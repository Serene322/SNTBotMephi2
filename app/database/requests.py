from app.database.models import async_session
from app.database.models import User, Area, Vote, Point, Option, Result
from sqlalchemy import select, update, delete, join

async def set_user (telegram_id):
    async with async_session() as session:
        user = await session.scalar((select(User).where(User.telegram_id == telegram_id)))
        
        if not user:
            session.add(User(telegram_id = telegram_id))
            await session.commit()
            
async def registration (email, password):
    async with async_session() as session:
        user_info = await session.scalar((select(User).where(User.email == email)))
        
        if user_info.password == password:
            return True
        else:
            return False