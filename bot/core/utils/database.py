import psycopg2
import os
import pytz
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'postgres-db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'botdb')
DB_USER = os.getenv('DB_USER', 'myuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mypassword')

# Conexão com o banco de dados

def connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Criação da tabela 'server_data' e inserção de dados

def create_server_data():
    conn = connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_data (
                id SERIAL PRIMARY KEY,
                nome TEXT,
                player_left TEXT,
                players_online INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                server_status TEXT
            )
        ''')
        conn.commit()
        print("[DATABASE] Tabela 'server_data' criada com sucesso.")
    except Exception as e:
        print(f"[DATABASE ERROR] Erro ao criar a tabela: {e}")
    finally:
        cursor.close()
        conn.close()

def insert_server_data(player_name, server_online, players_online, player_left=None):
    conn = connection()
    cursor = conn.cursor()

    br_tz = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(br_tz)

    cursor.execute('''
    INSERT INTO server_data (nome, players_online, server_status, player_left, timestamp)
    VALUES (%s, %s, %s, %s, %s)
    ''', (player_name, players_online, 'online' if server_online else 'offline', player_left, current_time))

    conn.commit()
    conn.close()

# Criação da tabela 'check_birthdays' e inserção de dados

def create_birthday_data():
    conn = connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS birthday_messages (
            id SERIAL PRIMARY KEY,
            name TEXT,
            date_sent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        print("[DATABASE] Tabela 'birthday_messages' criada com sucesso.")
    except Exception as e:
        print(f"[DATABASE ERROR] Erro ao criar a tabela: {e}")
    finally:
        cursor.close()
        conn.close()


def has_sent_birthday_message(name):
    conn = connection()
    cursor = conn.cursor()

    today = datetime.now().strftime('%m-%d')

    cursor.execute('''
    SELECT 1 FROM birthday_messages WHERE name = %s AND date_sent = %s
    ''', (name, today))

    result = cursor.fetchone()
    conn.close()

    return result is not None

def mark_birthday_sent(name):
    conn = connection()
    cursor = conn.cursor()

    today = datetime.now().strftime('%m-%d')

    cursor.execute('''
    INSERT INTO birthday_messages (name, date_sent)
    VALUES (%s, %s)
    ''', (name, today))

    conn.commit()
    conn.close()