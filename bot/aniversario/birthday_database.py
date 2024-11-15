import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH')

# Conectar ao banco de dados (ou criar um novo arquivo de banco de dados)
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Criar tabela para armazenar aniversariantes que já foram cumprimentados
cursor.execute('''
CREATE TABLE IF NOT EXISTS birthday_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date_sent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Função para verificar se a mensagem de aniversário já foi enviada
def has_sent_birthday_message(name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime('%m-%d')  # Formato de data 'MM-DD'

    cursor.execute('''
    SELECT 1 FROM birthday_messages WHERE name = ? AND date_sent = ?
    ''', (name, today))

    result = cursor.fetchone()
    conn.close()

    return result is not None

# Função para salvar um aniversariante que já foi cumprimentado
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
