from db import get_db_connection
from PySide6.QtCore import QDate, QDateTime

class NoteManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.ensure_notes_schema()

    def ensure_notes_schema(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                content TEXT,
                color VARCHAR(20),
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            ''')
            conn.commit()
            cur.close()

    def get_notes(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, content, color, created FROM notes WHERE user_id=%s ORDER BY created DESC', (self.user_id,))
            notes = [
                {
                    'id': row[0],
                    'content': row[1],
                    'color': row[2],
                    'created': row[3]
                } for row in cur.fetchall()
            ]
            cur.close()
            return notes

    def add_note(self, content, color):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO notes (user_id, content, color) VALUES (%s, %s, %s)', (self.user_id, content, color))
            conn.commit()
            cur.close()

    def update_note(self, note_id, content, color):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('UPDATE notes SET content=%s, color=%s WHERE id=%s AND user_id=%s', (content, color, note_id, self.user_id))
            conn.commit()
            cur.close()

    def delete_note(self, note_id):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM notes WHERE id=%s AND user_id=%s', (note_id, self.user_id))
            conn.commit()
            cur.close()
