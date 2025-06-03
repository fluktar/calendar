import os
import psycopg2
from sshtunnel import SSHTunnelForwarder
from contextlib import contextmanager
from dotenv import load_dotenv
from PySide6.QtCore import QDate
from datetime import datetime
import hashlib

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
                # Połącz do domyślnej bazy i utwórz calendar_db
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
                # Spróbuj ponownie połączyć się do właściwej bazy
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
        # Dodaję kolumnę user_id jeśli nie istnieje
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

class TaskManager:
    def __init__(self):
        ensure_db_schema()
        self.user_id = None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        with get_db_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute('INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id',
                            (username, self.hash_password(password)))
                user_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return user_id
            except Exception:
                cur.close()
                return None

    def login_user(self, username, password):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, hashed_password FROM users WHERE username=%s', (username,))
            row = cur.fetchone()
            cur.close()
            if row and row[1] == self.hash_password(password):
                self.user_id = row[0]
                return True
            return False

    def load_tasks(self):
        if self.user_id is None:
            return {}
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, date, title, description, status, priority, repeat, deadline, history FROM tasks WHERE user_id=%s', (self.user_id,))
            rows = cur.fetchall()
            tasks = {}
            for row in rows:
                date_str = row[1].strftime('%Y-%m-%d')
                task = {
                    'id': row[0],
                    'text': row[2],
                    'description': row[3],
                    'status': row[4],
                    'priority': row[5],
                    'repeat': row[6],
                    'deadline': row[7].strftime('%Y-%m-%d') if row[7] else '',
                    'history': row[8] or []
                }
                if date_str not in tasks:
                    tasks[date_str] = []
                tasks[date_str].append(task)
            cur.close()
            return tasks

    def save_task(self, date, text, description='', status='nowe', priority='średni', repeat='brak', deadline=None, history=None):
        if self.user_id is None:
            return
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO tasks (user_id, date, title, description, status, priority, repeat, deadline, history)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (self.user_id, date, text, description, status, priority, repeat, deadline, history or []))
            conn.commit()
            cur.close()

    def update_task(self, task_id, new_text=None, status=None, description=None, priority=None, repeat=None, deadline=None):
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Pobierz aktualną historię
            cur.execute('SELECT history, status FROM tasks WHERE id=%s', (task_id,))
            row = cur.fetchone()
            history = row[0] or []
            old_status = row[1]
            # Dodaj wpis do historii jeśli status się zmienia
            if status is not None and status != old_status:
                from datetime import datetime
                history.append([status, datetime.now().isoformat()])
            fields = []
            values = []
            if new_text is not None:
                fields.append("title=%s")
                values.append(new_text)
            if status is not None:
                fields.append("status=%s")
                values.append(status)
            if description is not None:
                fields.append("description=%s")
                values.append(description)
            if priority is not None:
                fields.append("priority=%s")
                values.append(priority)
            if repeat is not None:
                fields.append("repeat=%s")
                values.append(repeat)
            if deadline is not None:
                fields.append("deadline=%s")
                values.append(deadline)
            # Aktualizuj historię
            fields.append("history=%s")
            values.append(history)
            if not fields:
                return
            values.append(task_id)
            cur.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id=%s", values)
            conn.commit()
            cur.close()

    def remove_task(self, task_id):
        if self.user_id is None:
            return
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM tasks WHERE id=%s AND user_id=%s', (task_id, self.user_id))
            conn.commit()
            cur.close()

    def get_all_dates_with_tasks(self):
        if self.user_id is None:
            return []
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT DISTINCT date FROM tasks WHERE user_id=%s', (self.user_id,))
            rows = cur.fetchall()
            cur.close()
            return [row[0].strftime('%Y-%m-%d') for row in rows]

    def get_tasks_for_date(self, date: QDate):
        if self.user_id is None:
            return []
        date_str = date.toString('yyyy-MM-dd')
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, title, description, status, priority, repeat, deadline, history FROM tasks WHERE date=%s AND user_id=%s', (date_str, self.user_id))
            rows = cur.fetchall()
            cur.close()
            return [
                {
                    'id': row[0],
                    'text': row[1],
                    'description': row[2],
                    'status': row[3],
                    'priority': row[4],
                    'repeat': row[5],
                    'deadline': row[6].strftime('%Y-%m-%d') if row[6] else '',
                    'history': row[7] or []
                } for row in rows
            ]

    def get_tasks_for_today(self):
        today = QDate.currentDate().toString('yyyy-MM-dd')
        return self.get_tasks_for_date(QDate.fromString(today, 'yyyy-MM-dd'))
