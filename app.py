import streamlit as st
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

# Set page config
st.set_page_config(
    page_title="YouTube Chat Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "youtube_url" not in st.session_state:
    st.session_state.youtube_url = ""
if "all_sessions" not in st.session_state:
    st.session_state.all_sessions = []

# Helper functions
def create_session(youtube_url):
    """Create a new RAG session"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/create-session",
            json={"youtube_url": youtube_url},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error creating session: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def ask_question(session_id, question):
    """Ask a question to the RAG system"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json={"session_id": session_id, "question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error asking question: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        response = requests.get(f"{API_BASE_URL}/session/{session_id}/history")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def get_all_sessions():
    """Get all active sessions"""
    try:
        response = requests.get(f"{API_BASE_URL}/sessions")
        if response.status_code == 200:
            return response.json().get("sessions", [])
        else:
            return []
    except:
        return []

def delete_session(session_id):
    """Delete a session"""
    try:
        response = requests.delete(f"{API_BASE_URL}/session/{session_id}")
        return response.status_code == 200
    except:
        return False

# Main app
def main():
    st.title("🎥 YouTube Chat Assistant")
    st.markdown("Chat with any YouTube video using AI!")

    # Sidebar for session management
    with st.sidebar:
        st.header("📹 Video Setup")
        
        # Get all sessions for switching
        all_sessions = get_all_sessions()
        st.session_state.all_sessions = all_sessions
        
        # Session switcher
        if all_sessions:
            st.subheader("🔄 Switch Sessions")
            
            # Create a list of session options
            session_options = ["Create New Session"] + [
                f"{session['session_id'][:8]} - {session['youtube_url'][:30]}..." 
                if len(session['youtube_url']) > 30 
                else f"{session['session_id'][:8]} - {session['youtube_url']}"
                for session in all_sessions
            ]
            
            # Current selection index
            current_index = 0
            if st.session_state.session_id:
                for i, session in enumerate(all_sessions):
                    if session["session_id"] == st.session_state.session_id:
                        current_index = i + 1
                        break
            
            selected_option = st.selectbox(
                "Select Session:",
                options=session_options,
                index=current_index,
                key="session_selector"
            )
            
            # Handle session switching
            if selected_option != "Create New Session":
                selected_session_id = selected_option.split(" - ")[0]
                
                # Find the full session data
                selected_session = None
                for session in all_sessions:
                    if session["session_id"].startswith(selected_session_id):
                        selected_session = session
                        break
                
                # Switch to selected session if different from current
                if selected_session and selected_session["session_id"] != st.session_state.session_id:
                    st.session_state.session_id = selected_session["session_id"]
                    st.session_state.youtube_url = selected_session["youtube_url"]
                    
                    # Load chat history for this session
                    history_data = get_chat_history(selected_session["session_id"])
                    if history_data and history_data.get("conversation"):
                        st.session_state.chat_history = history_data["conversation"]
                    else:
                        st.session_state.chat_history = []
                    
                    st.success(f"Switched to session: {selected_session_id}")
                    st.rerun()
            
            st.divider()
        
        # YouTube URL input (only for new sessions)
        if not all_sessions or st.session_state.get("session_selector", "").startswith("Create New Session"):
            youtube_url = st.text_input(
                "YouTube URL:",
                value="" if not st.session_state.session_id else st.session_state.youtube_url,
                placeholder="https://www.youtube.com/watch?v=...",
                key="youtube_url_input"
            )
            
            # Create session button
            if st.button("🚀 Start New Session", type="primary"):
                if youtube_url:
                    with st.spinner("Processing video... This may take a moment."):
                        result = create_session(youtube_url)
                        if result:
                            st.session_state.session_id = result["session_id"]
                            st.session_state.youtube_url = youtube_url
                            st.session_state.chat_history = []
                            st.success(f"Session created! ID: {result['session_id'][:8]}")
                            st.rerun()
                else:
                    st.error("Please enter a YouTube URL")
        
        # Current session info
        if st.session_state.session_id:
            st.subheader("✅ Active Session")
            st.info(f"**ID:** {st.session_state.session_id[:8]}...")
            
            # Show video URL with click to view
            if st.session_state.youtube_url:
                st.caption("**Video:**")
                if st.button("🔗 View Video", help=st.session_state.youtube_url):
                    st.write(f"[Open Video]({st.session_state.youtube_url})")
            
            # Session management buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Delete", type="secondary", help="Delete this session"):
                    if delete_session(st.session_state.session_id):
                        st.session_state.session_id = None
                        st.session_state.chat_history = []
                        st.session_state.youtube_url = ""
                        st.success("Session deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete session")
            
            with col2:
                if st.button("🔄 Refresh", help="Refresh session list"):
                    st.rerun()
        
        # API Status check
        st.divider()
        st.subheader("🔧 API Status")
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if response.status_code == 200:
                st.success("✅ API Connected")
                data = response.json()
                st.caption(f"Total sessions: {data.get('active_sessions', 0)}")
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ API Disconnected")
            st.error("Make sure your FastAPI server is running on port 8000")

    # Main chat interface
    if st.session_state.session_id:
        st.header("💬 Chat with Video")
        
        # Load chat history on first load
        if not st.session_state.chat_history:
            history_data = get_chat_history(st.session_state.session_id)
            if history_data and history_data.get("conversation"):
                st.session_state.chat_history = history_data["conversation"]
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["type"] == "human":
                    with st.chat_message("user"):
                        st.write(message["message"])
                else:
                    with st.chat_message("assistant"):
                        st.write(message["message"])
        
        # Chat input
        question = st.chat_input("Ask a question about the video...")
        
        if question:
            # Add user message to history
            st.session_state.chat_history.append({
                "type": "human", 
                "message": question
            })
            
            # Display user message immediately
            with st.chat_message("user"):
                st.write(question)
            
            # Get response from API
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = ask_question(st.session_state.session_id, question)
                    
                    if response:
                        answer = response["answer"]
                        st.write(answer)
                        
                        # Add assistant response to history
                        st.session_state.chat_history.append({
                            "type": "assistant",
                            "message": answer
                        })
                    else:
                        st.error("Sorry, I couldn't process your question. Please try again.")
        
        # Clear chat history button
        if st.session_state.chat_history:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🧹 Clear Chat", type="secondary"):
                    st.session_state.chat_history = []
                    st.rerun()
            with col3:
                st.caption(f"{len(st.session_state.chat_history)} messages")
    
    else:
        # Welcome screen
        st.header("👋 Welcome!")
        st.markdown("""
        **Get started in 2 easy steps:**
        
        1. **Enter a YouTube URL** in the sidebar
        2. **Click "Start New Session"** to begin chatting
        
        You can then ask questions about the video content, and the AI will answer based on the video transcript!
        
        ### 📋 Example URLs to try:
        - Educational videos
        - Tutorials  
        - Podcasts
        - Interviews
        - Any video with English subtitles/captions
        """)
        
        # Sample questions
        st.header("💡 Sample Questions You Can Ask:")
        sample_questions = [
            "What is the main topic of this video?",
            "Can you summarize the key points?",
            "What did the speaker say about [specific topic]?",
            "What are the main takeaways?",
            "Can you explain the first point in more detail?"
        ]
        
        for q in sample_questions:
            st.markdown(f"• {q}")

if __name__ == "__main__":
    main()