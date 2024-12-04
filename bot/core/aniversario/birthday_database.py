import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'postgres-db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'botdb')
DB_USER = os.getenv('DB_USER', 'myuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mypassword')

def connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

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