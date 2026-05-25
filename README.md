# 📚 PDF Chat Assistant (RAG + Groq + FAISS)

Ask questions about any PDF using Retrieval-Augmented Generation (RAG).

Upload a PDF, generate intelligent document-specific questions, and chat with the document using Groq LLMs.

---

# 🌐 Live Demo

**Render Deployment URL**

👉 https://your-render-url.onrender.com


---

# ✨ Features

- Upload PDF documents
- AI-generated document summary
- AI-generated suggested questions
- Chat with uploaded PDFs
- Retrieval-Augmented Generation (RAG)
- FAISS vector search
- Persistent chat history
- Delete chats and associated data
- Groq LLM integration
- Streamlit UI

---

# 🛠 Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### AI / RAG
- Groq
- Sentence Transformers
- FAISS

### Database
- SQLite

### PDF Processing
- PyPDF2

---

# 📂 Project Structure

```text
PDF-reader-with-FAISS/
│
├── app.py
├── db.py
├── rag.py
├── requirements.txt
├── render.yaml
├── .gitignore
│
├── uploads/
├── indexes/
│
└── data.db
```

---

# 🚀 Run Locally

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git

cd YOUR_REPO
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a file named:

```text
.env
```

Add:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Get your API key from:

https://console.groq.com/keys

---

## 5. Run Application

```bash
streamlit run app.py
```

or

```bash
python -m streamlit run app.py
```

---

# ☁️ Deploy on Render

## Create Web Service

1. Push project to GitHub
2. Login to Render
3. Create a New Web Service
4. Connect GitHub repository

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Environment Variables

Add:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

---

# 🧠 How It Works

1. User uploads PDF
2. PDF text is extracted
3. Text is split into chunks
4. Embeddings are generated
5. Embeddings are stored in FAISS
6. User asks a question
7. Relevant chunks are retrieved
8. Context is sent to Groq LLM
9. AI generates answer

---

# 📸 Screenshots

Add screenshots here after deployment.

---

# ⚠️ Notes

This project currently stores:

- Uploaded PDFs
- FAISS indexes
- SQLite database

locally on disk.

On free hosting services these files may not persist after restarts.

For production deployment consider:

- PostgreSQL
- AWS S3
- Supabase Storage
- Qdrant / Pinecone

---

# 👨‍💻 Author

Shresht VG

GitHub:
https://github.com/YOUR_USERNAME
