from Models.Area import Area
from Models.Client import Client
from Models.Option import Option
from Models.Point import Point
from Models.Vote import Vote
import sqlite3


def input_client_data():
    first_name = input("Введите имя: ")
    second_name = input("Введите фамилию: ")
    patronymic = input("Введите отчество (можно оставить пустым): ")
    phone_number = input("Введите номер телефона: ")
    email = input("Введите email (можно оставить пустым): ")
    password = input("Введите пароль: ")
    access_level = (input("Введите уровень доступа: "))
    telegram_id = input("Введите Telegram ID: ")

    client = Client(
        id=None,
        first_name=first_name,
        second_name=second_name,
        patronymic=patronymic if patronymic else None,
        phone_number=phone_number,
        email=email if email else None,
        password=password,
        access_level=access_level,
        telegram_id=telegram_id
    )
    client.save()


def display_client_data(client_id):
    client = Client.get_by_id(client_id)
    if client:
        print("Информация о пользователе:")
        print(f"ID: {client.id}")
        print(f"Имя: {client.first_name}")
        print(f"Фамилия: {client.second_name}")
        print(f"Отчество: {client.patronymic}")
        print(f"Номер телефона: {client.phone_number}")
        print(f"Email: {client.email}")
        print(f"Уровень доступа: {client.access_level}")
        print(f"Telegram ID: {client.telegram_id}")
    else:
        print(f"Пользователь с ID = {client_id} не найден.")


def input_area_data():
    client_id = int(input("Введите ID клиента: "))
    address = input("Введите адрес: ")
    cadastral_number = int(input("Введите кадастровый номер: "))
    number = int(input("Введите номер: "))

    area = Area(
        id=None,
        client_id=client_id,
        address=address,
        cadastral_number=cadastral_number,
        number=number
    )
    area.save()


def display_area_data(client_id):
    areas = Area.get_by_client_id(client_id)
    if areas:
        for area in areas:
            print("Информация о области:")
            print(f"ID: {area.id}")
            print(f"ID клиента: {area.client_id}")
            print(f"Адрес: {area.address}")
            print(f"Кадастровый номер: {area.cadastral_number}")
            print(f"Номер: {area.number}")
    else:
        print(f"Области для клиента с ID = {client_id} не найдены.")


def input_vote_data():
    creator_id = int(input("Введите ID создателя: "))
    topic = input("Введите тему голосования: ")
    description = input("Введите описание (можно оставить пустым): ")
    is_in_person = input("Голосование в очном формате? (True/False): ").lower() == 'true'
    is_closed = input("Голосование закрыто? (True/False): ").lower() == 'true'
    is_visible_in_progress = input("Голосование видно в процессе? (True/False): ").lower() == 'true'
    is_finished = input("Голосование завершено? (True/False): ").lower() == 'true'
    start_time = input("Введите время начала (YYYY-MM-DD HH:MM:SS): ")
    end_time = input("Введите время окончания (YYYY-MM-DD HH:MM:SS): ")

    vote = Vote(
        id=None,
        creator_id=creator_id,
        topic=topic,
        description=description if description else None,
        is_in_person=is_in_person,
        is_closed=is_closed,
        is_visible_in_progress=is_visible_in_progress,
        is_finished=is_finished,
        start_time=start_time,
        end_time=end_time
    )
    vote.save()


def display_vote_data(vote_id):
    vote = Vote.get_by_id(vote_id)
    if vote:
        print("Информация о голосовании:")
        print(f"ID: {vote.id}")
        print(f"ID создателя: {vote.creator_id}")
        print(f"Тема: {vote.topic}")
        print(f"Описание: {vote.description}")
        print(f"Очное голосование: {vote.is_in_person}")
        print(f"Закрытое голосование: {vote.is_closed}")
        print(f"Видно в процессе: {vote.is_visible_in_progress}")
        print(f"Завершено: {vote.is_finished}")
        print(f"Время начала: {vote.start_time}")
        print(f"Время окончания: {vote.end_time}")
    else:
        print(f"Голосование с ID = {vote_id} не найдено.")


def input_point_data():
    body = input("Введите текст пункта: ")
    vote_id = int(input("Введите ID голосования: "))

    point = Point(
        id=None,
        body=body,
        vote_id=vote_id
    )
    point.save()


def display_point_data(vote_id):
    points = Point.get_by_vote_id(vote_id)
    if points:
        for point in points:
            print("Информация о пункте:")
            print(f"ID: {point.id}")
            print(f"Текст пункта: {point.body}")
            print(f"ID голосования: {point.vote_id}")
            options = Option.get_by_point_id(point.id)
            for option in options:
                print(f"    Опция ID: {option.id}")
                print(f"    Текст опции: {option.body}")
    else:
        print(f"Пункты для голосования с ID = {vote_id} не найдены.")


def input_option_data():
    body = input("Введите текст опции: ")
    point_id = int(input("Введите ID пункта: "))

    option = Option(
        id=None,
        body=body,
        point_id=point_id
    )
    option.save()


def input_option_data():
    body = input("Введите текст опции: ")
    point_id = int(input("Введите ID пункта: "))

    option = Option(
        id=None,
        body=body,
        point_id=point_id
    )
    option.save()

def display_option_data(point_id):
    options = Option.get_by_point_id(point_id)
    if options:
        for option in options:
            print("Информация об опции:")
            print(f"ID: {option.id}")
            print(f"Текст опции: {option.body}")
            print(f"ID пункта: {option.point_id}")
    else:
        print(f"Опции для пункта с ID = {point_id} не найдены.")


def main():
    while True:
        print("\nМеню:")
        print("1. Добавить клиента")
        print("2. Показать данные клиента")
        print("3. Добавить область")
        print("4. Показать данные области")
        print("5. Добавить голосование")
        print("6. Показать данные голосования")
        print("7. Добавить пункт голосования")
        print("8. Показать данные пункта голосования")
        print("9. Добавить опцию")
        print("10. Показать данные опции")
        print("11. Выйти")

        choice = input("Выберите действие: ")

        if choice == '1':
            input_client_data()
        elif choice == '2':
            client_id = int(input("Введите ID клиента: "))
            display_client_data(client_id)
        elif choice == '3':
            input_area_data()
        elif choice == '4':
            client_id = int(input("Введите ID клиента: "))
            display_area_data(client_id)
        elif choice == '5':
            input_vote_data()
        elif choice == '6':
            vote_id = int(input("Введите ID голосования: "))
            display_vote_data(vote_id)
        elif choice == '7':
            input_point_data()
        elif choice == '8':
            vote_id = int(input("Введите ID голосования: "))
            display_point_data(vote_id)
        elif choice == '9':
            input_option_data()
        elif choice == '10':
            point_id = int(input("Введите ID пункта: "))
            display_option_data(point_id)
        elif choice == '11':
            break
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")


if __name__ == "__main__":
    main()
