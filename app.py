import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- UTILITY: Logging Queries ---
def log_query(question, response):
    log_file = "query_logs.csv"
    new_data = pd.DataFrame([[datetime.now(), question]], columns=['Timestamp', 'Query'])
    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False)
    else:
        new_data.to_csv(log_file, mode='a', header=False, index=False)

# --- APP CONFIG ---
st.set_page_config(page_title="STI Surveillance AI", page_icon="⚖️", layout="wide")

# Initialize Chat Engine in session state so it persists
if "chat_engine" not in st.session_state:
    from src.engine import get_rag_engine
    st.session_state.chat_engine = get_rag_engine()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("⚖️ STI Surveillance Program Assistant")

# --- SIDEBAR ---
# --- SIDEBAR ---
with st.sidebar:
    st.title("📂 Control Panel")
    
    # 1. File Management
    st.subheader("Upload Manuals/Memos")
    uploaded_files = st.file_uploader("Drop CDC PDFs or Memos here", type=['pdf', 'txt'], accept_multiple_files=True)
    if uploaded_files:
        if not os.path.exists("data"):
            os.makedirs("data")
        for f in uploaded_files:
            with open(os.path.join("data", f.name), "wb") as file:
                file.write(f.getbuffer())
        st.success(f"Saved {len(uploaded_files)} files.")

    st.markdown("---")

    # 2. THE RESOURCE LIST (The part that went missing)
    st.subheader("📚 Current Knowledge")
    data_dir = "data"
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        # Filter out hidden files like .gitkeep or .DS_Store
        clean_files = [f for f in files if not f.startswith('.')]
        
        if clean_files:
            for f in clean_files:
                st.caption(f"📄 {f}")
        else:
            st.info("No documents found in /data.")
    else:
        st.error("Data directory not found!")

    st.markdown("---")

    # 3. Maintenance
    if st.button("🔄 Clear Memory & Re-index", use_container_width=True):
        import shutil
        with st.spinner("Resetting..."):
            if os.path.exists("./storage"):
                shutil.rmtree("./storage")
            if "chat_engine" in st.session_state:
                del st.session_state.chat_engine
            st.rerun()

    # 4. Admin View: Download Logs
    if os.path.exists("query_logs.csv"):
        st.markdown("---")
        st.subheader("Admin: Usage Logs")
        df = pd.read_csv("query_logs.csv")
        st.download_button("Download Query Logs", df.to_csv(index=False), "logs_csv", "text/csv")
# --- MAIN CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a follow-up question..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status = st.status("Thinking...", expanded=False)
        
        # Use chat engine (it automatically handles session history)
        response = st.session_state.chat_engine.chat(prompt)
        
        st.markdown(response.response)
        log_query(prompt, response.response)
        
        # Professional Source Attribution
        if response.source_nodes:
            with st.expander("🔍 Verified Sources"):
                for node in response.source_nodes:
                    # Get filename from metadata if available
                    source_name = node.metadata.get('file_name', 'Unknown Source')
                    st.caption(f"Source: **{source_name}** (Relevance: {node.score:.2f})")
                    st.info(node.get_content()[:500] + "...")
        
        status.update(label="Response Generated", state="complete")
        st.session_state.messages.append({"role": "assistant", "content": response.response})