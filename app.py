# app.py

import streamlit as st
from rag_pipeline import create_vector_store, load_qa
import os

st.title("🤖 Chat do Edital - Mestrado USP")

pdf_path = "docs/edital.pdf"
vector_path = "data"

if "qa" not in st.session_state:
    with st.spinner("Carregando modelo e indexando documento..."):
        if not os.path.exists(os.path.join(vector_path, "index.faiss")):
            create_vector_store(pdf_path, vector_path)
        st.session_state.qa = load_qa(vector_path)

question = st.text_input("Digite sua pergunta sobre o edital:")

if question:
    with st.spinner("Consultando..."):
        response = st.session_state.qa.run(question)
        st.write(response)
