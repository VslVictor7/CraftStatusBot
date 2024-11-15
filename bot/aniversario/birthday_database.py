import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH')

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS birthday_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date_sent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

def has_sent_birthday_message(name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime('%m-%d')

    cursor.execute('''
    SELECT 1 FROM birthday_messages WHERE name = ? AND date_sent = ?
    ''', (name, today))

    result = cursor.fetchone()
    conn.close()

    return result is not None

def mark_birthday_sent(name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime('%m-%d')

    cursor.execute('''
    INSERT INTO birthday_messages (name, date_sent)
    VALUES (?, ?)
    ''', (name, today))

    conn.commit()
    conn.close()

conn.commit()
conn.close()
