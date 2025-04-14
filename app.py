# app.py (versão mais enxuta)

import streamlit as st
from rag_pipeline import load_qa

st.title("🤖 Chat do Edital - Mestrado")

if "qa" not in st.session_state:
    with st.spinner("Carregando modelo..."):
        st.session_state.qa = load_qa("data")

question = st.text_input("Digite sua pergunta sobre o edital:")

if question:
    with st.spinner("Consultando..."):
        response = st.session_state.qa.run(question)
        st.write(response)
