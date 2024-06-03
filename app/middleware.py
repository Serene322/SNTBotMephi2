from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select
from app.database.models import async_session, User


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if event.text == '/start':
            return await handler(event, data)

        telegram_id = event.from_user.id

        async with async_session() as session:
            async with session.begin():
                user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if not user:
            await event.answer('Вы не авторизованы. Пожалуйста, используйте команду /start для авторизации.')
            return

        return await handler(event, data)
