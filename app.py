import streamlit as st
from rag_pipeline import create_vector_store, load_qa
import os

st.title("🤖 Leitor de Editais")

# 📤 Upload de novo edital
with st.expander("📥 Fazer upload de um novo edital (.pdf)"):
    uploaded_file = st.file_uploader("Selecione um arquivo PDF", type=["pdf"])
    if uploaded_file:
        save_path = f"docs/{uploaded_file.name}"
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Arquivo '{uploaded_file.name}' salvo com sucesso!")
        st.rerun()

# 🔽 Lista de PDFs disponíveis na pasta docs/
pdf_list = [f for f in os.listdir("docs") if f.endswith(".pdf")]
selected_pdf = st.selectbox("Selecione o edital:", pdf_list)

pdf_path = f"docs/{selected_pdf}"
vector_path = f"data/{selected_pdf.replace('.pdf', '')}"

# Carregando modelo com base no PDF escolhido
if "qa" not in st.session_state or st.session_state.get("loaded_pdf") != selected_pdf:
    with st.spinner("Carregando modelo..."):
        if not os.path.exists(os.path.join(vector_path, "index.faiss")):
            create_vector_store(pdf_path, vector_path)
        st.session_state.qa = load_qa(vector_path)
        st.session_state.loaded_pdf = selected_pdf
        st.session_state.history = []  # inicializa o histórico para novo PDF

# Caixa de pergunta
question = st.text_input("Digite sua pergunta sobre o edital:")

# Consulta e grava histórico
if question:
    with st.spinner("Consultando..."):
        response = st.session_state.qa.run(question)
        st.session_state.history.append((question, response))
        st.write(response)

# Histórico de perguntas
st.markdown("---")
st.subheader("🕘 Histórico da sessão")

if st.session_state.history:
    for idx, (q, r) in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"{idx}. {q}"):
            st.markdown(r)
else:
    st.info("Nenhuma pergunta registrada ainda.")

# Botão para limpar histórico
if st.button("🧹 Limpar histórico"):
    st.session_state.history = []
    st.rerun()
