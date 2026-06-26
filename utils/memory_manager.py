import sqlite3
import json
import uuid
import os
from datetime import datetime
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chats.db")

def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            sources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(chat_id) REFERENCES chats(id)
        )
    """)
    conn.commit()
    conn.close()

def create_chat(title: str = "New Conversation") -> str:
    chat_id = str(uuid.uuid4())
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (chat_id, title, datetime.now(), datetime.now())
    )
    conn.commit()
    conn.close()
    return chat_id

def get_all_chats() -> List[Dict[str, Any]]:
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.* 
        FROM chats c
        WHERE EXISTS (SELECT 1 FROM messages m WHERE m.chat_id = c.id)
        ORDER BY c.updated_at DESC
    """)
    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return chats

def get_messages(chat_id: str) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at ASC", (chat_id,))
    messages = []
    for row in cursor.fetchall():
        msg = dict(row)
        msg['sources'] = json.loads(msg['sources']) if msg['sources'] else []
        messages.append(msg)
    conn.close()
    return messages

def add_message(chat_id: str, role: str, content: str, sources: List[Dict[str, Any]] = None):
    msg_id = str(uuid.uuid4())
    sources_json = json.dumps(sources) if sources else "[]"
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (id, chat_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (msg_id, chat_id, role, content, sources_json, datetime.now())
    )
    
    # Auto-update title if it's the first user message
    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,))
    count = cursor.fetchone()[0]
    
    if count == 1 and role == "user":
        title = content[:25] + "..." if len(content) > 25 else content
        cursor.execute("UPDATE chats SET title = ?, updated_at = ? WHERE id = ?", (title, datetime.now(), chat_id))
    else:
        cursor.execute(
            "UPDATE chats SET updated_at = ? WHERE id = ?",
            (datetime.now(), chat_id)
        )
        
    conn.commit()
    conn.close()

def delete_chat(chat_id: str):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()

def update_chat_title(chat_id: str, new_title: str):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title = ?, updated_at = ? WHERE id = ?", (new_title, datetime.now(), chat_id))
    conn.commit()
    conn.close()

# Initialize DB on load
init_db()
