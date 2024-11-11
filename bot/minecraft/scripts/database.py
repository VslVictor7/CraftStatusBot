import sqlite3, os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH')

# Conectar ao banco de dados (ou criar um novo arquivo de banco de dados)
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Criar tabela de status e logs do servidor (se não existir)
cursor.execute('''
CREATE TABLE IF NOT EXISTS server_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    player_left TEXT,
    online_in_server INTEGER,
    players_online INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    server_status TEXT
)
''')
conn.commit()
conn.close()

def insert_server_data(player_name, server_online, players_online, player_left=None):

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO server_data (nome, online_in_server, players_online, server_status, player_left)
    VALUES (?, ?, ?, ?, ?)
    ''', (player_name, server_online, players_online, 'online' if server_online else 'offline', player_left))

    conn.commit()
    conn.close()