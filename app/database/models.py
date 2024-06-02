from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column()
    second_name: Mapped[str] = mapped_column()
    patronymic: Mapped[str] = mapped_column()
    phone_number: Mapped[int] = mapped_column()
    email: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    access_level: Mapped[str] = mapped_column()
    telegram_id = mapped_column(BigInteger)    

class Area(Base):
    __tablename__ = 'Areas'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    adress: Mapped[str] = mapped_column()
    cadastral_number: Mapped[int] = mapped_column()
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    
    
class Vote(Base):
    __tablename__ = 'votes'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    creater_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    closed: Mapped[bool] = mapped_column()
    start_dttm = mapped_column(DateTime)
    end_dttm = mapped_column(DateTime)
    
class Point(Base):
    __tablename__ = 'points'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column()
    vote_id: Mapped[int] = mapped_column(ForeignKey('votes.id'))
    
class Option(Base):
    __tablename__ = 'options'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column()
    point_id: Mapped[int] = mapped_column(ForeignKey('points.id'))
    
class Result(Base):
    __tablename__ = 'results'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    point_id: Mapped[int] = mapped_column(ForeignKey('points.id'))
    option_id: Mapped[int] = mapped_column(ForeignKey('options.id'))
    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    
