import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import json

from db import init_db, create_chat, get_chats, delete_chat, save_message, load_messages

from rag import (
    extract_text,
    load_chunks,
    chunk_text,
    build_vector_store,
    retrieve_context,
    save_chunks,
    save_uploaded_pdf,
    save_index,
    load_index,
)

# folders creation
os.makedirs("uploads", exist_ok=True)
os.makedirs("indexes", exist_ok=True)

# model caching
@st.cache_data
def cached_document_insights(text):
    return generate_document_insights(text)

# INITIALIZATION
load_dotenv()
init_db()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
st.set_page_config(page_title="PDF Chat", page_icon="📚", layout="wide")

# SESSION STATE
if "current_chat" not in st.session_state:
    chats = get_chats()
    if chats:
        st.session_state.current_chat = chats[0][0]
    else:
        st.session_state.current_chat = None
if "chat_cache" not in st.session_state:
    st.session_state.chat_cache = {}

# STYLING
st.markdown(
    """
<style>

[data-testid="stSidebar"]{
    background-color:#111827;
}

.block-container{
    padding-top:1rem;
}

[data-testid="stFileUploaderFile"]{
    display:none !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# helpers
def remove_chat_everywhere(chat_id, pdf_path):
    delete_chat(chat_id)
    index_path = f"indexes/{chat_id}.index"
    if os.path.exists(index_path):
        os.remove(index_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if chat_id in st.session_state.chat_cache:
        del st.session_state.chat_cache[chat_id]
    remaining = get_chats()
    if remaining:
        st.session_state.current_chat = remaining[0][0]
    else:
        st.session_state.current_chat = None

def generate_document_insights(text):
    preview_text = text[:4000]
    prompt = f"""
You are analyzing a document.

Generate questions that can be answered DIRECTLY from the document.

The questions must be factual and based on information present in the document.

Do NOT generate interview questions, opinion questions,
or questions requiring outside knowledge.

Good examples for a resume:

- Who is this person?
- Where did this person study?
- What is the person's work experience?
- What programming languages does the person know?
- What projects has the person worked on?

Good examples for a job description:

- What role is being offered?
- What skills are required?
- What technologies are mentioned?
- What are the responsibilities?
- What qualifications are needed?

Good examples for an insurance policy:

- What is the policy number?
- Who is insured?
- What is the policy period?
- What is the premium amount?
- What vehicle is covered?

Return ONLY valid JSON.

{{
    "summary":"...",
    "questions":[
        "...",
        "...",
        "...",
        "...",
        "..."
    ]
}}

Document:

{preview_text}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    content = response.choices[0].message.content
    try:
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        return (data.get("summary", ""), json.dumps(data.get("questions", [])))
    except:
        return (
            "Unable to generate summary.",
            json.dumps(
                [
                    "Summarize this document",
                    "What are the key topics?",
                    "Explain this document",
                    "List important details",
                    "What should I know?",
                ]
            ),
        )

# SIDEBAR
with st.sidebar:
    st.title("💬 Chats")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_upload")
    if uploaded_file:
        existing_titles = [chat[1] for chat in get_chats()]
        if uploaded_file.name not in existing_titles:
            with st.spinner("Processing PDF..."):
                pdf_path = save_uploaded_pdf(uploaded_file)
                text = extract_text(uploaded_file)
                summary, questions = cached_document_insights(text)
                chat_id = create_chat(uploaded_file.name, pdf_path, summary, questions)
                chunks = chunk_text(text)
                save_chunks(chunks, chat_id)
                index = build_vector_store(chunks)
                save_index(index, chat_id)
                st.session_state.chat_cache[chat_id] = {
                    "index": index,
                    "chunks": chunks,
                }
                st.session_state.current_chat = chat_id
            st.rerun()
    st.divider()
    chats = get_chats()

    for chat_id, title, pdf_path, summary, questions in chats:
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(f"📄 {title}", key=f"open_{chat_id}", use_container_width=True):
                st.session_state.current_chat = chat_id
                st.rerun()
        with col2:
            if st.button("🗑", key=f"delete_{chat_id}"):
                remove_chat_everywhere(chat_id, pdf_path)
                st.rerun()

# NO CHAT SELECTED
if st.session_state.current_chat is None:
    st.title("📚 PDF Chat Assistant")
    st.markdown(
        """
### Upload a PDF and start chatting

Supported:

- Resumes
- Research Papers
- Books
- Notes
- Documentation
- Reports
"""
    )

    st.stop()

# LOAD CHAT INFO
# cleanup orphaned chats
for chat in get_chats():
    pdf_path = chat[2]
    index_path = f"indexes/{chat[0]}.index"
    if not os.path.exists(index_path):
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        delete_chat(chat[0])

# find current chat
chat_info = None
for chat in get_chats():
    if chat[0] == st.session_state.current_chat:
        chat_info = chat
        break

# current chat no longer exists
if chat_info is None:
    remaining = get_chats()
    if remaining:
        st.session_state.current_chat = remaining[0][0]
        st.rerun()
    else:
        st.session_state.current_chat = None
        st.title("📚 PDF Chat Assistant")
        st.markdown(
            """
### Upload a PDF and start chatting

Supported:

- Resumes
- Research Papers
- Books
- Notes
- Documentation
- Reports
"""
        )

        st.stop()

chat_id = chat_info[0]
chat_title = chat_info[1]
pdf_path = chat_info[2]
chat_summary = chat_info[3] or ""
chat_questions = json.loads(
    chat_info[4] if len(chat_info) > 4 and chat_info[4] else "[]"
)

# LOAD CACHE
if chat_id not in st.session_state.chat_cache:
    chunks = load_chunks(chat_id)
    index = load_index(chat_id)
    st.session_state.chat_cache[chat_id] = {"index": index, "chunks": chunks}
chat_data = st.session_state.chat_cache[chat_id]

# HEADER
col1, col2 = st.columns([10, 1])
with col1:
    st.title(chat_title)
with col2:
    if st.button("🗑", key="delete_current_chat"):
        remove_chat_everywhere(chat_id, pdf_path)
        st.rerun()

# CHAT HISTORY
messages = load_messages(chat_id)
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if len(messages) == 0:

    st.markdown(
        f"""
    <div style="
    padding:30px;
    border-radius:15px;
    border:1px solid #333;
    margin-top:20px;
    ">

    <h2>📄 {chat_title}</h2>

    <p>{chat_summary}</p>

    </div>
    """,
        unsafe_allow_html=True,
    )

    st.subheader("Suggested Questions")
    cols = st.columns(3)

    for i, q in enumerate(chat_questions):
        with cols[i % 3]:
            if st.button(q, key=f"suggestion_{i}", use_container_width=True):
                st.session_state["pending_question"] = q
                st.rerun()

# USER INPUT
if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")
else:
    question = st.chat_input(f"Ask about {chat_title}...")
if question:
    save_message(chat_id, "user", question)
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                context = retrieve_context(question, chat_data["index"], chat_data["chunks"], top_k=8)
                prompt = f"""
You are a helpful document assistant.

Answer the question using the supplied context.

If relevant information exists,
provide a complete answer.

Only say:

'I could not find that information in the document.'

when no relevant information exists.

Context:
{context}

Question:
{question}

Answer:
"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": "Answer questions using the document context.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                )

                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"Error:\n\n{str(e)}"
        st.markdown(answer)
    save_message(chat_id, "assistant", answer)
    print("Saving answer:", answer)
    st.rerun()
