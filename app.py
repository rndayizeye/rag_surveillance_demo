import streamlit as st
import os
from src.engine import get_rag_engine

# Page Configuration
st.set_page_config(page_title="STI Surveillance AI", layout="wide")
st.title("🔍 STI Surveillance Program Assistant")

# Ensure the data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# --- SIDEBAR: Document Management ---
with st.sidebar:
    st.header("📂 Document Management")
    st.info("Upload internal manuals, CDC guidelines, or memos to build the knowledge base.")
    
    uploaded_files = st.file_uploader(
        "Upload PDF Manuals", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if st.button("🚀 Process Documents"):
        if uploaded_files:
            with st.spinner("Saving and indexing files..."):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join("data", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # Clear existing chat engine from state to force a re-index
                if "chat_engine" in st.session_state:
                    del st.session_state["chat_engine"]
                
                st.success("Documents processed successfully!")
                st.rerun() # Refresh app to move past the safety check
        else:
            st.error("Please select files first.")

    if st.button("🧹 Clear All Data"):
        for f in os.listdir("data"):
            if not f.startswith('.'):
                os.remove(os.path.join("data", f))
        if "chat_engine" in st.session_state:
            del st.session_state["chat_engine"]
        st.rerun()

# --- MAIN UI: Chat Interface ---

# 1. Safety Check: Check if we have any 'real' files (ignoring hidden files like .gitkeep)
real_files = [f for f in os.listdir("data") if not f.startswith('.')]

if not real_files:
    st.warning("⚠️ No documents found in the system.")
    st.markdown("""
    ### How to get started:
    1. Open the **sidebar** on the left.
    2. Upload one or more **STI Surveillance manuals** (PDF).
    3. Click **Process Documents**.
    
    *Note: This demo uses local indexing. Your documents are processed within this container and are not used to train global models.*
    """)
else:
    # 2. Initialize the Engine
    if "chat_engine" not in st.session_state:
        try:
            with st.spinner("Building vector index... This may take a moment for large files."):
                st.session_state.chat_engine = get_rag_engine()
        except Exception as e:
            st.error(f"Error initializing engine: {e}")
            st.stop()

    # 3. Chat History Management
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I have indexed your surveillance manuals. How can I assist with STI protocols today?"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about STI protocols..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_container = st.empty()
            with st.spinner("Analyzing manuals..."):
                # Query the RAG engine
                response = st.session_state.chat_engine.chat(prompt)
                
                # Format full response with citations if available
                full_response = response.response
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    with st.expander("📝 Verified Sources"):
                        for node in response.source_nodes:
                            st.write(f"**Source:** {node.metadata.get('file_name', 'Unknown')}")
                            st.caption(f"**Text Snippet:** {node.get_text()[:200]}...")

                response_container.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})