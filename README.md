# 🎥 YouTube Chat Assistant

A powerful AI-powered application that allows you to chat with any YouTube video using RAG (Retrieval-Augmented Generation) technology. Ask questions about video content and get intelligent answers based on the video's transcript.

## ✨ Features

- 🎬 **Chat with YouTube Videos**: Ask questions about any YouTube video with English subtitles
- 💬 **Conversational AI**: Maintains context across multiple questions
- 🔄 **Multi-Session Support**: Switch between different video conversations
- 📱 **Clean Web Interface**: Easy-to-use Streamlit frontend
- 🚀 **Fast API Backend**: RESTful API for scalability
- 💾 **Session Management**: Persistent chat history for each video
- 🔍 **Smart Retrieval**: Uses vector similarity search for relevant context

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌──────────────────┐
│                 │ ◄──────────────► │                  │
│  Streamlit UI   │                  │   FastAPI Server │
│                 │                  │                  │
└─────────────────┘                  └──────────────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │   RAG Pipeline   │
                                     │                  │
                                     │ • YouTube API    │
                                     │ • Text Splitter  │
                                     │ • Embeddings     │
                                     │ • Vector Store   │
                                     │ • LLM Chain      │
                                     │ • Memory         │
                                     └──────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance web framework
- **LangChain** - LLM application framework
- **Azure OpenAI** - GPT models and embeddings
- **FAISS** - Vector similarity search
- **YouTube Transcript API** - Extract video transcripts

### Frontend
- **Streamlit** - Interactive web application
- **Requests** - HTTP client for API communication

## 📖 Usage

### Getting Started

1. **Enter YouTube URL**: Paste any YouTube video URL in the sidebar
2. **Create Session**: Click "Start New Session" to process the video
3. **Start Chatting**: Ask questions about the video content
4. **Switch Sessions**: Use the dropdown to switch between different videos

### Example Questions

- "What is the main topic of this video?"
- "Can you summarize the key points?"
- "What did the speaker say about [specific topic]?"
- "How does this relate to what we discussed earlier?"
- "Can you elaborate on the first point?"

### Session Management

- **Create Multiple Sessions**: Chat with different videos simultaneously
- **Switch Between Sessions**: Use the session dropdown to navigate
- **Persistent History**: Each session maintains its own chat history
- **Delete Sessions**: Remove sessions when no longer needed

## 🔧 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API status and health check |
| `POST` | `/create-session` | Create new video session |
| `POST` | `/ask` | Ask question in session |
| `GET` | `/sessions` | List all active sessions |
| `DELETE` | `/session/{id}` | Delete session |
