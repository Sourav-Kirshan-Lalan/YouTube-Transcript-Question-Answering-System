from fastapi import FastAPI, HTTPException
from rag_pipeline import build_rag
from pydantic import BaseModel
import uuid

class CreateSessionRequest(BaseModel):
    youtube_url: str

class AskQuestionRequest(BaseModel):
    session_id: str
    question: str

# Store sessions
sessions = {}
def ask_question_with_memory(chain, memory, question: str) -> str:
    response = chain.invoke(question)
    memory.save_context(
        {"question": question}, 
        {"answer": response}
    )
    return response

app = FastAPI(title="YouTube RAG API")

@app.get("/")
def home():
    return {"message": "YouTube RAG API is running!", "active_sessions": len(sessions)}

@app.post("/create-session")
def create_session(request: CreateSessionRequest):
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())[:8]  # Short ID for easier testing
        
        # Build RAG system using your function
        chain, memory = build_rag(request.youtube_url)
        
        # Store session
        sessions[session_id] = {
            "chain": chain,
            "memory": memory,
            "url": request.youtube_url
        }
        
        return {
            "session_id": session_id,
            "message": "Session created successfully!",
            "youtube_url": request.youtube_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.post("/ask")
def ask_question(request: AskQuestionRequest):
    # Check if session exists
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get session
        session = sessions[request.session_id]
        chain = session["chain"]
        memory = session["memory"]
        
        # Get answer using your helper function logic
        answer = ask_question_with_memory(chain, memory, request.question)
        
        return {
            "session_id": request.session_id,
            "question": request.question,
            "answer": answer
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/sessions")
def list_sessions():
    session_info = []
    for session_id, data in sessions.items():
        session_info.append({
            "session_id": session_id,
            "youtube_url": data["url"]
        })
    return {"sessions": session_info, "total": len(sessions)}

@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}

