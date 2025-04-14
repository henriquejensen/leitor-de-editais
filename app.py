import streamlit as st
import os
from rag_pipeline import create_vector_store
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

st.title("🤖 Leitor de Editais")

# 🧠 Seletor de modelo
model_choice = st.selectbox("Escolha o modelo:", ["Gemini", "OpenAI"], key="model_choice")

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

# 🔄 Função para carregar o modelo LLM + embeddings
def load_qa_model(model_choice: str, vector_path: str):
    if model_choice == "OpenAI":
        embeddings = OpenAIEmbeddings()
        llm = ChatOpenAI(temperature=0.2)
    else:  # Gemini
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.2)

    vectorstore = FAISS.load_local(
        vector_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# Carrega modelo + vetor se necessário
model_key = f"{selected_pdf}_{model_choice}"
if "qa" not in st.session_state or st.session_state.get("qa_key") != model_key:
    with st.spinner("Carregando modelo..."):
        if not os.path.exists(os.path.join(vector_path, "index.faiss")):
            create_vector_store(pdf_path, vector_path)
        st.session_state.qa = load_qa_model(model_choice, vector_path)
        st.session_state.qa_key = model_key
        st.session_state.history = []

# Campo de pergunta e botão separado
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
    st.session_state.question_input = ""
    st.rerun()

# Exportação para PDF
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

if st.session_state.history:
    pdf_path = export_history_to_pdf(st.session_state.history)
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="💾 Exportar histórico para PDF",
            file_name="historico_sessao.pdf",
            mime="application/pdf",
            data=pdf_file.read()
        )
