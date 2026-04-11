import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

PERSIST_DIR = "./storage"

def get_rag_engine(data_path="./data"):
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))

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