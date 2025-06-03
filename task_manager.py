import os
import hashlib
from db import get_db_connection, ensure_db_schema
from PySide6.QtCore import QDate

class TaskManager:
    def __init__(self, user_id):
        ensure_db_schema()
        self.user_id = user_id

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
