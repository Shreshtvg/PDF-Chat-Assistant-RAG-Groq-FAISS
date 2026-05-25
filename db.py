import sqlite3

DB_NAME = "data.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        pdf_path TEXT,
        summary TEXT,
        questions TEXT
    )
    """
    )
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        content TEXT,
        FOREIGN KEY(chat_id)
        REFERENCES chats(id)
        ON DELETE CASCADE
    )
    """
    )
    conn.commit()
    conn.close()


def create_chat(title, pdf_path, summary, questions):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chats(
            title,
            pdf_path,
            summary,
            questions
        )
        VALUES(?,?,?,?)
        """,
        (title, pdf_path, summary, questions),
    )

    chat_id = cur.lastrowid
    conn.commit()
    conn.close()
    return chat_id


def get_chats():
    conn = get_connection()
    rows = conn.execute(
        """
    SELECT
        id,
        title,
        pdf_path,
        summary,
        questions
    FROM chats
    ORDER BY id DESC
    """
    ).fetchall()
    conn.close()
    return rows


def delete_chat(chat_id):
    conn = get_connection()
    conn.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    conn.execute("DELETE FROM chats WHERE id=?", (chat_id,))
    conn.commit()
    conn.close()


def save_message(chat_id, role, content):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO messages(
            chat_id,
            role,
            content
        )
        VALUES(?,?,?)
        """,
        (chat_id, role, content),
    )
    conn.commit()
    conn.close()


def load_messages(chat_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT role,content
        FROM messages
        WHERE chat_id=?
        ORDER BY id
        """,
        (chat_id,),
    ).fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]
