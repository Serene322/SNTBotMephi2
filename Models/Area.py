import sqlite3
from database import get_db_connection


class Area:
    def __init__(self, id, client_id, address, cadastral_number, number):
        self.id = id
        self.client_id = client_id
        self.address = address
        self.cadastral_number = cadastral_number
        self.number = number

    @classmethod
    def from_db_row(cls, row):
        return cls(row[0], row[1], row[2], row[3], row[4])

    @classmethod
    def get_by_client_id(cls, client_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM areas WHERE client_id = ?', (client_id,))
        rows = cursor.fetchall()
        conn.close()
        return [cls.from_db_row(row) for row in rows]

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO areas (client_id, address, cadastral_number, number)
            VALUES (?, ?, ?, ?)
        ''', (self.client_id, self.address, self.cadastral_number, self.number))
        conn.commit()
        conn.close()
