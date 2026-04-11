import streamlit as st
import os

st.title("System Check")

# Check 1: Is the Data folder visible?
if os.path.exists("./data"):
    st.success("✅ 'data' folder found.")
else:
    st.error("❌ 'data' folder NOT found. Please create it in your root directory.")

# Check 2: Is the API Key loaded?
from dotenv import load_dotenv
load_dotenv()
if os.getenv("OPENAI_API_KEY"):
    st.success("✅ API Key loaded.")
else:
    st.warning("⚠️ API Key missing in .env file.")

# Check 3: Can we see our engine?
try:
    from rag_surveillance_demo.unused.paid_version_engine import get_rag_engine
    st.success("✅ Engine module imported correctly.")
except Exception as e:
    st.error(f"❌ Engine import failed: {e}")