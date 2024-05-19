import sqlite3
from database import get_db_connection
from Models.Option import Option

class Point:
    def __init__(self, id, body, vote_id):
        self.id = id
        self.body = body
        self.vote_id = vote_id

    @classmethod
    def from_db_row(cls, row):
        return cls(row[0], row[1], row[2])

    @classmethod
    def get_by_vote_id(cls, vote_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Points WHERE vote_id = ?', (vote_id,))
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_db_row(row) for row in rows]

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Points (body, vote_id)
            VALUES (?, ?)
        ''', (self.body, self.vote_id))
        conn.commit()
        conn.close()

    def get_options(self):
        return Option.get_by_point_id(self.id)
