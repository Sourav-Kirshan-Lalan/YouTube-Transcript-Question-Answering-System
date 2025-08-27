from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()
from urllib.parse import urlparse, parse_qs

def extract_youtube_id(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.path.startswith("/embed/"):
            return parsed_url.path.split("/")[2]
        elif parsed_url.path.startswith("/v/"):
            return parsed_url.path.split("/")[2]
    if parsed_url.hostname in ["youtu.be"]:
        return parsed_url.path[1:]
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = regex.search(url)
    if match:
        return match.group(1)
    return None

def build_rag(youtube_url: str):
    video_id = extract_youtube_id(youtube_url)
    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=["en"])
        transcript = " ".join([snippet.text for snippet in transcript_list])
    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")

    # Split transcript
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])

    # Create embeddings
    embeddings = AzureOpenAIEmbeddings(
        model="text-embedding-ada-002",
        api_version="2024-12-01-preview"
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    # Build QA chain
    llm = AzureChatOpenAI(
        deployment_name="gpt-5-nano", 
        api_version="2024-12-01-preview"
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    prompt = PromptTemplate(
    template="""
    You are a helpful assistant.
    Answer ONLY from the provided transcript context, and chat history.
    If the context is insufficient, just say you don't know.
    If the user greets you, respond with a friendly greeting.
    Be conversational and refer to previous parts of the conversation when relevant.

    Chat History:
    {chat_history}

    Transcript context:
    {context}

    Question: {question}
            
    Answer:""",
    input_variables = ['context', 'question', 'chat_history']
)
    def format_docs(retrieved_docs):
        context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
        return context_text
    
    def get_chat_history():
        return memory.chat_memory.messages
    
    parallel_chain = RunnableParallel({
    'context': retriever | RunnableLambda(format_docs),
    'question': RunnablePassthrough(),
    'chat_history': RunnableLambda(lambda x: get_chat_history())
})
    
    parser = StrOutputParser()

    main_chain = parallel_chain | prompt | llm | parser
    
    return main_chain, memory

def example_usage_function():
    youtube_url = "https://www.youtube.com/watch?v=ejGEddhynE0&t=2s"
    chain, memory = build_rag(youtube_url)

    # Function to ask questions with memory
    def ask_with_memory(question: str):
        response = chain.invoke(question)
        # Manually add to memory
        memory.chat_memory.add_user_message(question)
        memory.chat_memory.add_ai_message(response)
        return response
    # Ask questions
    response1 = ask_with_memory("What is this video about?")
    print("Response 1:", response1)
    
    response2 = ask_with_memory("Can you elaborate on that?")
    print("Response 2:", response2)



