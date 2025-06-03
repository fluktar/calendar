import hashlib
from db import get_db_connection, ensure_db_schema

class UserManager:
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
