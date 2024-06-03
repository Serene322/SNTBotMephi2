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
        # Получаем creator_id из базы данных по telegram_id
        user = await session.scalar(select(User.id).where(User.telegram_id == telegram_id))
        if user:
            creator_id = user.id
        else:
            # Обработка ситуации, когда пользователь с указанным telegram_id не найден
            return None

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


# async def create_vote(vote_data):
#     async with async_session() as session:
#         vote = Vote(
#             creator_id=vote_data['creator_id'],
#             topic=vote_data['topic'],
#             description=vote_data['description'],
#             is_in_person=vote_data['is_in_person'],
#             is_closed=vote_data['is_closed'],
#             is_visible_in_progress=vote_data['is_visible_in_progress'],
#             is_finished=vote_data['is_finished'],
#             start_time=vote_data['start_time'],
#             end_time=vote_data['end_time']
#         )
#         session.add(vote)
#         await session.commit()
#         return vote.id


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


async def save_incomplete_vote(data):
    async with async_session() as session:
        vote = Vote(
            creator_id=data['creator_id'],
            topic=data['topic'],
            description=data.get('description', None),
            start_dttm=data['start_date'],
            end_dttm=data['end_date'],
            is_in_person=data['is_in_person'],
            is_closed=data['is_closed'],
            is_visible_in_progress=data['is_visible_in_progress'],
            is_finished=False
        )
        session.add(vote)
        await session.commit()


async def save_vote(vote_data):
    async with async_session() as session:
        vote = Vote(
            creator_id=vote_data['creator_id'],
            topic=vote_data['topic'],
            description=vote_data.get('description', None),
            is_in_person=vote_data['is_in_person'],
            is_closed=vote_data['is_closed'],
            is_visible_in_progress=vote_data['is_visible_in_progress'],
            is_finished=vote_data['is_finished'],
            start_time=vote_data['start_time'],
            end_time=vote_data['end_time']
        )
        session.add(vote)
        await session.commit()

        # Создаем пункты голосования и их варианты ответов
        for point_data in vote_data['points']:
            point = Point(body=point_data['body'], vote_id=vote.id)
            session.add(point)
            await session.commit()

            for option_data in point_data['options']:
                option = Option(body=option_data['body'], point_id=point.id)
                session.add(option)
                await session.commit()
