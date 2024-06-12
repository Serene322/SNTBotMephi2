from app.database.models import async_session
from app.database.models import Area, User, Vote, Point, Option, Result
from sqlalchemy.future import select
from datetime import datetime


async def set_telegram_id(email: str, telegram_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.email == email))
        if user:
            user.telegram_id = telegram_id
            await session.commit()


async def registration(email: str, password: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.email == email))
        return user and user.password == password


async def create_vote(vote_data, telegram_id):
    async with async_session() as session:
        user = await fetch_user_by_telegram_id(telegram_id)
        if not user:
            return None

        vote = Vote(
            creator_id=user.id,
            **vote_data
        )
        session.add(vote)
        await session.commit()
        return vote.id


async def fetch_user_by_telegram_id(telegram_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id))


async def fetch_vote_by_id(vote_id: int):
    async with async_session() as session:
        return await session.scalar(select(Vote).where(Vote.id == vote_id))


async def add_point(vote_id: int, point_body: str):
    async with async_session() as session:
        point = Point(body=point_body, vote_id=vote_id)
        session.add(point)
        await session.commit()
        return point.id


async def add_option(point_id: int, option_body: str):
    async with async_session() as session:
        option = Option(body=option_body, point_id=point_id)
        session.add(option)
        await session.commit()


async def save_incomplete_vote(data, telegram_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            return None

        creator_id = user.id

        # Проверяем, существует ли уже голосование с такой же темой
        existing_vote = await session.scalar(
            select(Vote).where(Vote.topic == data['topic']).where(Vote.creator_id == creator_id))
        if existing_vote:
            vote_id = existing_vote.id
        else:
            # Создаем новое голосование, если его еще нет
            vote = Vote(
                creator_id=creator_id,
                topic=data['topic'],
                description=data.get('description', None),
                start_time=data['start_time'],
                end_time=data['end_time'],
                is_in_person=data['is_in_person'],
                is_closed=data['is_closed'],
                is_visible_in_progress=data['is_visible_in_progress'],
                is_finished=False
            )
            session.add(vote)
            await session.commit()
            vote_id = vote.id

        for point_data in data['points']:
            # Проверяем, существует ли уже пункт с таким текстом в базе данных
            existing_point = await session.scalar(
                select(Point).where(Point.vote_id == vote_id).where(Point.body == point_data['body']))
            if not existing_point:
                point = Point(body=point_data['body'], vote_id=vote_id)
                session.add(point)
                await session.commit()

                options = point_data.get('options', [])
                for option_data in options:
                    option = Option(body=option_data['body'], point_id=point.id)
                    session.add(option)
                    await session.commit()


async def save_vote(data, telegram_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            return None

        creator_id = user.id

        vote = await session.scalar(
            select(Vote).where(Vote.creator_id == creator_id).where(Vote.topic == data['topic']))
        if vote:
            vote.description = data.get('description', vote.description)
            vote.is_in_person = data['is_in_person']
            vote.is_closed = data['is_closed']
            vote.is_visible_in_progress = data['is_visible_in_progress']
            vote.is_finished = data['is_finished']
            vote.start_time = data['start_time']
            vote.end_time = data['end_time']
        else:
            vote = Vote(
                creator_id=creator_id,
                topic=data['topic'],
                description=data.get('description', None),
                is_in_person=data['is_in_person'],
                is_closed=data['is_closed'],
                is_visible_in_progress=data['is_visible_in_progress'],
                is_finished=data['is_finished'],
                start_time=data['start_time'],
                end_time=data['end_time']
            )
            session.add(vote)

        await session.commit()

        if not vote.is_finished:
            for point_data in data['points']:
                point = Point(body=point_data['body'], vote_id=vote.id)
                session.add(point)
                await session.commit()

                options = point_data.get('options', [])
                for option_data in options:
                    option = Option(body=option_data['body'], point_id=point.id)
                    session.add(option)
                    await session.commit()


# Запрос для получения незавершённых голосований
async def get_unfinished_votes(telegram_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            return []

        votes = await session.scalars(select(Vote).where(Vote.creator_id == user.id, Vote.is_finished == False))
        return [{'id': vote.id, 'topic': vote.topic} for vote in votes]


# Запрос для получения информации голосования
async def get_vote_details(vote_id: int):
    async with async_session() as session:
        vote = await session.scalar(select(Vote).where(Vote.id == vote_id))
        if not vote:
            return None

        return {
            'id': vote.id,
            'topic': vote.topic,
            'description': vote.description,
            'start_time': vote.start_time.strftime('%Y-%m-%d'),
            'end_time': vote.end_time.strftime('%Y-%m-%d'),
            'is_in_person': vote.is_in_person,
            'is_closed': vote.is_closed,
            'is_visible_in_progress': vote.is_visible_in_progress,
            'is_finished': vote.is_finished
        }


async def update_vote_field(vote_id: int, field: str, value):
    async with async_session() as session:
        vote = await session.get(Vote, vote_id)
        if vote:
            setattr(vote, field, value)
            await session.commit()
            return True
        return False


# Запросы для обновления полей голосования

async def update_vote_topic(vote_id: int, new_topic: str):
    return await update_vote_field(vote_id, 'topic', new_topic)


async def update_vote_description(vote_id: int, new_description: str):
    return await update_vote_field(vote_id, 'description', new_description)


async def update_vote_visibility(vote_id, new_value):
    return await update_vote_field(vote_id, 'is_visible_in_progress', new_value)


async def update_vote_is_closed(vote_id, new_value):
    return await update_vote_field(vote_id, 'is_closed', new_value)


async def update_vote_is_in_person(vote_id, new_value):
    return await update_vote_field(vote_id, 'is_in_person', new_value)


async def update_vote_is_finished(vote_id: int, new_value):
    return await update_vote_field(vote_id, 'is_finished', new_value)


# ГОЛОСОВАНИЕ.

async def get_active_votes(user_id):
    async with async_session() as session:
        current_time = datetime.now()
        votes = await session.scalars(
            select(Vote)
            .where(
                (Vote.is_finished == True) &
                (Vote.start_time < current_time) &
                (Vote.end_time > current_time) &
                (Vote.is_in_person == False)
            )
        )
        active_votes = []
        for vote in votes:
            if not await has_user_completed_vote(user_id, vote.id):
                active_votes.append({
                    'id': vote.id,
                    'topic': vote.topic,
                    'start_time': vote.start_time,
                    'end_time': vote.end_time
                })
        return active_votes



async def get_vote_details_with_points(vote_id):
    async with async_session() as session:
        async with session.begin():
            # Получаем данные о голосовании
            vote_result = await session.execute(select(Vote).where(Vote.id == vote_id))
            vote = vote_result.fetchone()

            if not vote:
                return None, None  # Возвращаем None, если голосование не найдено

            # Получаем связанные с голосованием точки
            points_result = await session.execute(select(Point).where(Point.vote_id == vote_id))
            points = points_result.all()

            print("Vote:", vote)
            print("Points:", points)

            return vote, points


# Функция для сохранения результата голосования в базе данных
async def save_result(client_id: int, point_id: int, option_id: int):
    async with async_session() as session:
        result = Result(client_id=client_id, point_id=point_id, option_id=option_id)
        session.add(result)
        await session.commit()


# Функция проверки, выполнил ли пользователь голосование
async def has_user_completed_vote(user_id, vote_id):
    async with async_session() as session:
        result = await session.execute(
            select(Result).join(Point).where(Result.client_id == user_id, Point.vote_id == vote_id)
        )
        return result.scalar() is not None


#Личный кабинет


async def fetch_user_info_and_areas(telegram_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            return None, []

        user_info = {
            "first_name": user.first_name,
            "second_name": user.second_name,
            "patronymic": user.patronymic,
            "phone_number": user.phone_number,
            "email": user.email,
            "access_level": user.access_level,
        }

        areas = await session.scalars(select(Area).where(Area.client_id == user.id))
        area_list = [{
            "address": area.address,
            "cadastral_number": area.cadastral_number
        } for area in areas]

        return user_info, area_list


from  aiogram import types
async def send_user_info(message_or_query, user_info_text, areas_info=None):
    if areas_info:
        reply_markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Главное меню", callback_data="to_inline_menu")]
        ])
        if isinstance(message_or_query, types.Message):
            await message_or_query.answer(user_info_text + "\nУчастки:\n" + areas_info, reply_markup=reply_markup)
        elif isinstance(message_or_query, types.CallbackQuery):
            await message_or_query.message.edit_text(user_info_text + "\nУчастки:\n" + areas_info, reply_markup=reply_markup)
    else:
        if isinstance(message_or_query, types.Message):
            await message_or_query.answer(user_info_text)
        elif isinstance(message_or_query, types.CallbackQuery):
            await message_or_query.message.edit_text(user_info_text)

'''Добавление смены времени не понял как должно работать
async def update_vote_start_time(vote_id: int, new_start_time: DateTime):
    async with async_session() as session:
        await session.execute(update(Vote).where(Vote.id == vote_id).values(start_time=new_start_time))
        await session.commit()

async def update_vote_end_time(vote_id: int, new_end_time: date):
    async with async_session() as session:
        await session.execute(update(Vote).where(Vote.id == vote_id).values(end_time=new_end_time))
        await session.commit()
'''