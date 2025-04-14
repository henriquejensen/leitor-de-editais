import streamlit as st
import os
from rag_pipeline import create_vector_store, load_qa
from fpdf import FPDF

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
        st.session_state.history = []

question = st.text_input("Digite sua pergunta sobre o edital:", key="question_input", placeholder="Digite sua pergunta...")

ask_clicked = st.button("🔍 Consultar")

if ask_clicked and question.strip():
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
if st.button("🧹 Limpar histórico", disabled=not st.session_state.history):
    st.session_state.history = []
    st.rerun()

# Função para exportar histórico em PDF
def export_history_to_pdf(history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Historico - Leitor de Editais", ln=True)

    for idx, (q, r) in enumerate(history, 1):
        pdf.ln(10)
        pdf.set_font("Arial", "B", size=12)
        pdf.multi_cell(0, 10, f"{idx}. Pergunta: {q}")
        pdf.set_font("Arial", "", size=12)
        pdf.multi_cell(0, 10, f"Resposta: {r}")

    output_path = "data/historico_sessao.pdf"
    pdf.output(output_path)
    return output_path

# Botão para exportar PDF
if st.session_state.history:
    pdf_path = export_history_to_pdf(st.session_state.history)
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="💾 Exportar histórico para PDF",
            file_name="historico_sessao.pdf",
            mime="application/pdf",
            data=pdf_file.read()
        )
