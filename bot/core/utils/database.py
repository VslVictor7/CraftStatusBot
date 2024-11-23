import sqlite3
import os
import pytz
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'bot_database.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS server_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    player_left TEXT,
    players_online INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    server_status TEXT
)
''')
conn.commit()
conn.close()

def insert_server_data(player_name, server_online, players_online, player_left=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    br_tz = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(br_tz)

    cursor.execute('''
    INSERT INTO server_data (nome, players_online, server_status, player_left, timestamp)
    VALUES (?, ?, ?, ?, ?)
    ''', (player_name, players_online, 'online' if server_online else 'offline', player_left, current_time))

    conn.commit()
    conn.close()
