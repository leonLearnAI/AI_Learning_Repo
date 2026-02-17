# import streamlit as st

# st.set_page_config(page_title="Book Intelligence Assistant", layout="wide")

# st.title("Book Intelligence Assistant")
# st.caption("RAG + Knowledge Graph + Traceable Citations (Local-first)")

# with st.sidebar:
#     st.header("Settings")
#     spoiler = st.toggle("Spoiler Model", value=False)
#     top_k = st.slider("TOP-K", 1, 10, 5)

# st.write("Demo UI placeholder. next chapters will connect this to FastApi")
# st.write({"spoiler_mode": spoiler, "top_k": top_k})

import time
import streamlit as st
import requests

st.set_page_config(page_title="Book Intelligence Assistant", layout="wide")

st.title("📚 Book Intelligence Assistant")
st.write("✅ Streamlit is running and rendering this page.")

st.divider()
st.subheader("FastAPI health check")

try:
    r = requests.get("http://127.0.0.1:8000/health", timeout=2)
    st.json(r.json())
except Exception as e:
    st.error(f"Cannot reach FastAPI /health: {e}")
# verify the streamlit app can reach FastAPI
st.divider()
st.subheader("Ask")

question = st.text_input("Enter your question")
spoiler_mode = st.toggle("Spoiler Model", value=False)
top_k = st.slider("TOP-K", 1, 10, 5)

if st.button("Ask"):
    payload = {
        "question" : question,
        "top_k": top_k,
        "spoiler_model": spoiler_mode
    }
    r = requests.post("http://127.0.0.1:8000/ask", json=payload, timeout=5)
    st.json(r.json())