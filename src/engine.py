import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler # for debugging, trace and log all LLM calls and embedding calls. Useful for development, but can be verbose!
import streamlit as st

PERSIST_DIR = "./storage"

def get_rag_engine(data_path="./data"):
    # Initialize the debugger
    debug_handler = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([debug_handler])
    
    Settings.callback_manager = callback_manager
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
    
    # Check if the folder is empty or doesn't exist
    if not os.path.exists(data_path) or not os.listdir(data_path):
        # Return a "Mock" engine or handle the empty state
        # For a Streamlit app, it's often better to just 
        # let the UI handle the 'No files' state.
        st.warning("⚠️ No documents found. Please upload files in the sidebar.")
        st.stop() # Stops execution so the app doesn't crash

    if not os.path.exists(PERSIST_DIR):
        os.makedirs(data_path, exist_ok=True)
        documents = SimpleDirectoryReader(data_path).load_data()
        index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    # CHANGE: Switched from as_query_engine to as_chat_engine
    # 'condense_plus_context' remembers the chat history AND looks at your docs
    return index.as_chat_engine(
        chat_mode="condense_plus_context",
        llm=Settings.llm,
        system_prompt="You are an STI Surveillance Assistant. Answer based strictly on the provided manuals and memos."
    )