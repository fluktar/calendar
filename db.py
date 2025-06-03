import os
from sshtunnel import SSHTunnelForwarder
from contextlib import contextmanager
from dotenv import load_dotenv
import psycopg2

# Ładowanie zmiennych środowiskowych
load_dotenv(os.path.join(os.path.dirname(__file__), 'calendar.env'))

@contextmanager
def get_db_connection():
    server = SSHTunnelForwarder(
        (os.getenv('SSH_HOST'), int(os.getenv('SSH_PORT'))),
        ssh_username=os.getenv('SSH_USER'),
        ssh_password=os.getenv('SSH_PASSWORD'),
        remote_bind_address=(os.getenv('DB_HOST'), int(os.getenv('DB_PORT')))
    )
    server.start()
    conn = None
    try:
        try:
            conn = psycopg2.connect(
                host='127.0.0.1',
                port=server.local_bind_port,
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                dbname=os.getenv('DB_NAME')
            )
        except psycopg2.OperationalError as e:
            if 'does not exist' in str(e):
                tmp_conn = psycopg2.connect(
                    host='127.0.0.1',
                    port=server.local_bind_port,
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    dbname='postgres'
                )
                tmp_conn.autocommit = True
                tmp_cur = tmp_conn.cursor()
                tmp_cur.execute(f"CREATE DATABASE {os.getenv('DB_NAME')}")
                tmp_cur.close()
                tmp_conn.close()
                conn = psycopg2.connect(
                    host='127.0.0.1',
                    port=server.local_bind_port,
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    dbname=os.getenv('DB_NAME')
                )
            else:
                server.stop()
                raise
        yield conn
    finally:
        if conn:
            conn.close()
        server.stop()

def ensure_db_schema():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tasks' AND column_name='user_id') THEN
                ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
            END IF;
        END$$;
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        );
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'nowe',
            priority VARCHAR(10) DEFAULT 'średni',
            repeat VARCHAR(20) DEFAULT 'brak',
            deadline DATE,
            history JSONB DEFAULT '[]'
        );
        ''')
        conn.commit()
        cur.close()
