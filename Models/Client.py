import sqlite3
from database import get_db_connection


class Client:
    def __init__(self, id, first_name, second_name, patronymic, phone_number, email, password, access_level, telegram_id):
        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.patronymic = patronymic
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.access_level = access_level
        self.telegram_id = telegram_id

    @classmethod
    def from_db_row(cls, row):
        return cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

    @classmethod
    def get_by_id(cls, client_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls.from_db_row(row)
        return None

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (first_name, second_name, patronymic, phone_number, email, password, access_level, telegram_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.first_name, self.second_name, self.patronymic, self.phone_number, self.email, self.password, self.access_level, self.telegram_id))
        conn.commit()
        conn.close()

