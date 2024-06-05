from app.database.models import async_session
from app.database.models import User, Vote, Point, Option, Result
from sqlalchemy import select, update


async def set_telegram_id(email: str, telegram_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.email == email))
        if user:
            user.telegram_id = telegram_id
            await session.commit()


async def registration(email: str, password: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.email == email))
        if user and user.password == password:
            return True
        return False


async def create_vote(vote_data, telegram_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            return None

        creator_id = user.id

        vote = Vote(
            creator_id=creator_id,
            topic=vote_data['topic'],
            description=vote_data['description'],
            is_in_person=vote_data['is_in_person'],
            is_closed=vote_data['is_closed'],
            is_visible_in_progress=vote_data['is_visible_in_progress'],
            is_finished=vote_data['is_finished'],
            start_time=vote_data['start_time'],
            end_time=vote_data['end_time']
        )
        session.add(vote)
        await session.commit()
        return vote.id


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
        existing_vote = await session.scalar(select(Vote).where(Vote.topic == data['topic']).where(Vote.creator_id == creator_id))
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
            existing_point = await session.scalar(select(Point).where(Point.vote_id == vote_id).where(Point.body == point_data['body']))
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

        vote = await session.scalar(select(Vote).where(Vote.creator_id == creator_id).where(Vote.topic == data['topic']))
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

#Запрос для получения незавершённых голосований
async def get_unfinished_votes(telegram_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            return []

        votes = await session.scalars(select(Vote).where(Vote.creator_id == user.id, Vote.is_finished == False))
        return [{'id': vote.id, 'topic': vote.topic} for vote in votes]

#Запрос для получения информации голосования
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
            'is_visible_in_progress': vote.is_visible_in_progress
        }


#Запросы для обновления полей голосования
async def update_vote_topic(vote_id: int, new_topic: str):
    async with async_session() as session:
        await session.execute(update(Vote).where(Vote.id == vote_id).values(topic=new_topic))
        await session.commit()

async def update_vote_description(vote_id: int, new_description: str):
    async with async_session() as session:
        await session.execute(update(Vote).where(Vote.id == vote_id).values(description=new_description))
        await session.commit()

async def update_vote_is_in_person(vote_id: int, new_is_in_person: bool):
    async with async_session() as session:
        await session.execute(update(Vote).where(Vote.id == vote_id).values(is_in_person=new_is_in_person))
        await session.commit()

async def update_vote_is_closed(vote_id: int, new_is_closed: bool):
     async with async_session() as session:
        await session.execute(update(Vote).where(Vote.id == vote_id).values(is_closed=new_is_closed))
        await session.commit()

async def update_vote_is_visible_in_progress(vote_id: int, new_is_visible_in_progress: bool):
    async with async_session() as session:
        await session.execute(update(Vote).where(Vote.id == vote_id).values(is_visible_in_progress=new_is_visible_in_progress))
        await session.commit()

async def update_vote_is_finished(vote_id: int, new_is_finished: bool):
    async with async_session() as session:
        await session.execute(update(Vote).where(Vote.id == vote_id).values(is_finished=new_is_finished))
        await session.commit()






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
