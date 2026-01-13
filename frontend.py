import streamlit as st
import uuid
import shutil
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from main import graph, retrieve_all_threads, load_conversation

# --- Page Configuration ---
st.set_page_config(
    page_title="MultiRAG Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for ChatGPT-like UI ---
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #ffffff;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2f2f2f;
    }
    
    section[data-testid="stSidebar"] * {
        color: #ececec !important;
    }
    
    /* Thread list container */
    .thread-list {
        max-height: 500px;
        overflow-y: auto;
        padding: 0.5rem 0;
    }
    
    /* Individual thread item */
    .thread-item {
        padding: 0.75rem;
        margin: 0.25rem 0;
        border-radius: 0.5rem;
        cursor: pointer;
        background-color: #2f2f2f;
        transition: background-color 0.2s;
        border: 1px solid transparent;
    }
    
    .thread-item:hover {
        background-color: #3f3f3f;
    }
    
    .thread-item.active {
        background-color: #4a4a4a;
        border: 1px solid #565869;
    }
    
    .thread-title {
        font-size: 0.875rem;
        color: #ececec;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .thread-id {
        font-size: 0.75rem;
        color: #8e8ea0;
        margin-top: 0.25rem;
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* User message specific */
    div[data-testid="stChatMessage"]:has(div[aria-label="user"]) {
        background-color: #f7f7f8;
    }
    
    /* Assistant message specific */
    div[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) {
        background-color: #ffffff;
    }
    
    /* Headers */
    h1 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 2rem;
        margin-bottom: 0;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 0.5rem;
        font-weight: 500;
        width: 100%;
        background-color: #2f2f2f;
        border: 1px solid #4a4a4a;
        color: #ececec;
    }
    
    .stButton button:hover {
        background-color: #3f3f3f;
        border-color: #565869;
    }
    
    /* File uploader styling */
    .uploadedFile {
        background-color: #2f2f2f;
        border: 1px solid #4a4a4a;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1f1f1f;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4a4a4a;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #565869;
    }
    
    /* Divider */
    hr {
        border-color: #4a4a4a;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# --- Sidebar: Thread Management & File Upload ---
with st.sidebar:
    st.markdown("### 💬 MultiRAG Chat")
    
    # New Chat Button
    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    
    # Thread History with scrollable list
    st.markdown("### 📜 Conversations")
    
    try:
        threads = retrieve_all_threads()
        threads = list(threads)
        
        if threads:
            # Create scrollable thread list
            for thread in threads:
                is_active = thread == st.session_state.thread_id
                
                # Create a button for each thread
                button_label = f"{'📌 ' if is_active else '💬 '}Thread {thread[:8]}..."
                
                if st.button(
                    button_label,
                    key=f"thread_{thread}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    if thread != st.session_state.thread_id:
                        st.session_state.thread_id = thread
                        st.rerun()
        else:
            st.info("No conversations yet")
            
    except Exception as e:
        st.error(f"Could not load threads: {e}")

    st.divider()
    
    # File Upload Section
    st.markdown("### 📂 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload documents", 
        accept_multiple_files=True,
        type=['pdf', 'txt'],
        help="Upload PDF or TXT files",
        label_visibility="collapsed"
    )
    
if uploaded_files:
    if not os.path.exists("docs"):
        os.makedirs("docs")
    
    saved_count = 0
    for uploaded_file in uploaded_files:
        file_path = os.path.join("docs", uploaded_file.name)
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_count += 1
    
    if saved_count > 0:
        st.success(f"✅ {saved_count} file(s) saved to knowledge base")

    if os.path.exists("db"):
        shutil.rmtree("db")    

# Load and Display Conversation History
try:
    history = load_conversation(st.session_state.thread_id)
    
    if not history:
        st.info("👋 Start a new conversation by typing below!")
    
    for msg in history:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            if msg.content:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg.content)
            
except Exception as e:
    st.error(f"Error loading conversation: {e}")

# Chat Input
if prompt := st.chat_input("Ask me anything..."):
    # 1. Display User Message Immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # 2. Prepare Config
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    # 3. Stream Response Token by Token
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream the response
            for event in graph.stream({"messages": [HumanMessage(content=prompt)]}, config=config, stream_mode="values"):
                # Extract the last message from the event
                if "messages" in event and event["messages"]:
                    last_msg = event["messages"][-1]
                    
                    # Check if it's an AI message with content
                    if isinstance(last_msg, AIMessage) and last_msg.content:
                        # Update the full response and display it
                        full_response = last_msg.content
                        message_placeholder.markdown(full_response)
            
            # If no response was captured
            if not full_response:
                message_placeholder.markdown("*[No response content]*")
                
        except Exception as e:
            message_placeholder.error(f"An error occurred: {e}")