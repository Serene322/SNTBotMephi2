from database import get_db_connection


class Vote:
    def __init__(self, id, creator_id, topic, description, is_in_person, is_closed, is_visible_in_progress, is_finished,
                 start_time, end_time):
        self.id = id
        self.creator_id = creator_id
        self.topic = topic
        self.description = description
        self.is_in_person = is_in_person
        self.is_closed = is_closed
        self.is_visible_in_progress = is_visible_in_progress
        self.is_finished = is_finished
        self.start_time = start_time
        self.end_time = end_time

    @classmethod
    def from_db_row(cls, row):
        return cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])

    @classmethod
    def get_by_id(cls, vote_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM votes WHERE id = ?', (vote_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls.from_db_row(row)
        return None

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO votes (creator_id, topic, description, is_in_person, is_closed, is_visible_in_progress, 
            is_finished, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.creator_id, self.topic, self.description, self.is_in_person, self.is_closed,
              self.is_visible_in_progress, self.is_finished, self.start_time, self.end_time))
        conn.commit()
        conn.close()
