import os

print("🚀 Iniciando o Chat do Edital...")

# Cria os vetores se ainda não existirem
if not os.path.exists("data/index.faiss"):
    from rag_pipeline import create_vector_store
    create_vector_store("docs/edital.pdf", "data")

# Abre a interface no navegador
os.system("streamlit run app.py")
