import sqlite3


def CreateDataBase():
    # Создаем соединение с базой данных
    conn = sqlite3.connect('your_database.sql')

    # Создаем курсор для выполнения SQL-запросов
    cursor = conn.cursor()

    # Создаем таблицу clients
    cursor.execute('''CREATE TABLE clients
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        second_name TEXT,
                        patronymic TEXT NULL,
                        phone_number INTEGER UNIQUE,
                        email TEXT UNIQUE NULL,
                        password TEXT,
                        access_level BOOLEAN,
                        telegram_id TEXT UNIQUE)''')

    # Создаем таблицу votes
    cursor.execute('''CREATE TABLE votes
                        (id INTEGER PRIMARY KEY,
                        creator_id INTEGER REFERENCES clients(id),
                        topic TEXT,
                        description TEXT NULL,
                        is_in_person BOOLEAN,
                        is_closed BOOLEAN,
                        is_visible_in_progress BOOLEAN,
                        is_finished BOOLEAN,
                        start_time DATETIME,
                        end_time DATETIME)''')

    # Создаем таблицу user_types
    cursor.execute('''CREATE TABLE user_types
                        (id INTEGER PRIMARY KEY,
                        type TEXT)''')

    # Создаем таблицу areas
    cursor.execute('''CREATE TABLE areas
                        (id INTEGER PRIMARY KEY,
                        client_id INTEGER REFERENCES clients(id),
                        address TEXT UNIQUE,
                        cadastral_number INTEGER UNIQUE,
                        number INTEGER UNIQUE)''')

    # Создаем таблицу Points
    cursor.execute('''CREATE TABLE Points
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         body TEXT,
                         vote_id INTEGER REFERENCES votes(id))''')

    # Создаем таблицу options
    cursor.execute('''CREATE TABLE options
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         body TEXT,
                         point_id INTEGER REFERENCES Points(id))''')

    # Создаем таблицу votes_results
    cursor.execute('''CREATE TABLE votes_results
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         client_id INTEGER REFERENCES clients(id),
                         point_id INTEGER REFERENCES Points(id),
                         option_id INTEGER REFERENCES options(id))''')

    # Пример инструкции INSERT для создания клиента
    client_data = (
        'Иван', 'Иванов', 'Иванович', 123456789, 'vanya.doe@example.com', 'password123', 1, 'ivan_telegram_id')
    cursor.execute('''INSERT INTO clients
                           (first_name, second_name, patronymic, phone_number, email, password, access_level, telegram_id)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', client_data)

    # Пример инструкции INSERT для создания области
    area_data = (1, '123 Main St', 1234567890, 1)
    cursor.execute('''INSERT INTO areas
                           (client_id, address, cadastral_number, number)
                           VALUES (?, ?, ?, ?)''', area_data)

    # Выполняем запрос SELECT для получения информации о пользователе с id = 1
    cursor.execute('''SELECT * FROM clients WHERE id = ?''', (1,))
    user_data = cursor.fetchone()  # Получаем одну строку с данными

    # Если пользователь найден, выводим информацию
    if user_data:
        print("Информация о пользователе:")
        print(f"ID: {user_data[0]}")
        print(f"Имя: {user_data[1]}")
        print(f"Фамилия: {user_data[2]}")
        print(f"Отчество: {user_data[3]}")
        print(f"Номер телефона: {user_data[4]}")
        print(f"Email: {user_data[5]}")
        print(f"Уровень доступа: {user_data[7]}")
        print(f"Telegram ID: {user_data[8]}")
    else:
        print("Пользователь с ID = 1 не найден.")

    # Сохраняем изменения
    conn.commit()

    # Закрываем соединение
    conn.close()


def get_db_connection():
    with sqlite3.connect('your_database.sql') as conn:
        return conn


#CreateDataBase()
