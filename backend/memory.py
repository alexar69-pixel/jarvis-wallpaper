import sqlite3
import os
import json

DB_FILE = 'jarvis_memory.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_message(role, content):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat_history (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

def get_recent_history(limit=5):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    # Return chronologically (oldest first within the limit window)
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def clear_memory():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history')
    conn.commit()
    conn.close()

# Initialize on import
init_db()
