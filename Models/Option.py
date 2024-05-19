import sqlite3
from database import get_db_connection


class Option:
    def __init__(self, id, body, point_id):
        self.id = id
        self.body = body
        self.point_id = point_id

    @classmethod
    def from_db_row(cls, row):
        return cls(row[0], row[1], row[2])

    @classmethod
    def get_by_point_id(cls, point_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM options WHERE point_id = ?', (point_id,))
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_db_row(row) for row in rows]

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO options (body, point_id)
            VALUES (?, ?)
        ''', (self.body, self.point_id))
        conn.commit()
        conn.close()
