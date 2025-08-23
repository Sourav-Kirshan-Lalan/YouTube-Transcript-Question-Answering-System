# 🎥 YouTube Transcript Question-Answering System (RAG with LangChain + Azure OpenAI)

This project implements a **Retrieval-Augmented Generation (RAG) pipeline** that enables users to ask natural language questions about a YouTube video, and receive **context-aware answers** derived directly from the transcript.  

The system combines **YouTube Transcript API**, **LangChain**, **Azure OpenAI embeddings + LLMs**, and **FAISS vector store** for efficient transcript retrieval and response generation.  

---

## 🚀 Features
- Extracts transcripts from YouTube videos using **YouTube Transcript API**  
- Splits long transcripts into **semantic chunks** with LangChain  
- Creates **vector embeddings** using Azure OpenAI  
- Stores embeddings in **FAISS vector database** for efficient retrieval  
- Uses **AzureChatOpenAI** (LLMs) for context-aware question answering  
- End-to-end **RAG pipeline** for querying YouTube video content  

---

## 🛠️ Tech Stack
- **Python 3.9+**  
- **LangChain** (Text splitters, prompts, RAG orchestration)  
- **Azure OpenAI** (Embeddings + Chat Models)  
- **FAISS** (Vector database for retrieval)  
- **YouTube Transcript API** (Transcript ingestion)  

---

## 💡 Usage
1. Provide a YouTube `video_id` in the notebook.  
2. The pipeline will:
   - Fetch the transcript  
   - Split text into chunks  
   - Generate embeddings and store them in FAISS  
   - Allow natural language Q&A over the video  

Example:
```python
Q: "What is the main topic of this video?"
A: "The video discusses farmers preparing soil and planting seeds..."
```

