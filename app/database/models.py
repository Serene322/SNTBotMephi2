from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

DATABASE_URL = 'sqlite+aiosqlite:///db.sqlite3'

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String)
    second_name: Mapped[str] = mapped_column(String)
    patronymic: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    access_level: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    areas = relationship("Area", back_populates="client")
    votes_created = relationship("Vote", back_populates="creator")


class Area(Base):
    __tablename__ = 'areas'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String, unique=True)
    cadastral_number: Mapped[str] = mapped_column(String, unique=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    client = relationship("User", back_populates="areas")


class Vote(Base):
    __tablename__ = 'votes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    topic: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)
    is_in_person: Mapped[bool] = mapped_column(Boolean)
    is_closed: Mapped[bool] = mapped_column(Boolean)
    is_visible_in_progress: Mapped[bool] = mapped_column(Boolean)
    is_finished: Mapped[bool] = mapped_column(Boolean)
    start_time = mapped_column(DateTime)
    end_time = mapped_column(DateTime)

    creator = relationship("User", back_populates="votes_created")
    points = relationship("Point", back_populates="vote")


class Point(Base):
    __tablename__ = 'points'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    body: Mapped[str] = mapped_column(String)
    vote_id: Mapped[int] = mapped_column(ForeignKey('votes.id'))

    vote = relationship("Vote", back_populates="points")
    options = relationship("Option", back_populates="point")


class Option(Base):
    __tablename__ = 'options'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    body: Mapped[str] = mapped_column(String)
    point_id: Mapped[int] = mapped_column(ForeignKey('points.id'))

    point = relationship("Point", back_populates="options")


class Result(Base):
    __tablename__ = 'results'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    point_id: Mapped[int] = mapped_column(ForeignKey('points.id'))
    option_id: Mapped[int] = mapped_column(ForeignKey('options.id'))

    client = relationship("User")
    point = relationship("Point")
    option = relationship("Option")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
