import json
import os
import faiss
import numpy as np
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def save_chunks(chunks, chat_id):
    os.makedirs("indexes", exist_ok=True)
    with open(f"indexes/{chat_id}.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)

def load_chunks(chat_id):
    path = f"indexes/{chat_id}.json"
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def load_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def chunk_text(text, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start+= chunk_size - overlap
    return chunks

def build_vector_store(chunks):
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
    embeddings = np.asarray(embeddings, dtype=np.float32)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def save_index(index, chat_id):
    os.makedirs("indexes", exist_ok=True)
    faiss.write_index(index, f"indexes/{chat_id}.index")

def load_index(chat_id):
    path = f"indexes/{chat_id}.index"
    if not os.path.exists(path):
        return None
    return faiss.read_index(path)

def retrieve_context(query, index, chunks, top_k=8):
    if not chunks:
        return ""
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    query_embedding = np.asarray(query_embedding, dtype=np.float32)
    top_k = min(top_k, len(chunks))
    distances, indices = index.search(query_embedding, top_k)
    contexts = []
    for idx in indices[0]:
        if idx < len(chunks):
            contexts.append(chunks[idx])
    return "\n\n".join(contexts)


def save_uploaded_pdf(pdf):
    os.makedirs("uploads", exist_ok=True)
    pdf_path = os.path.join("uploads", pdf.name)
    with open(pdf_path, "wb") as f:
        f.write(pdf.getbuffer())
    return pdf_path
