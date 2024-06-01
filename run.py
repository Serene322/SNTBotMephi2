import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from Config import TOKEN
from app.handlers import router

bot = Bot(token='6858455476:AAH4rBu3-cQvhYOJR5hPqMDiDdIbpiRRHXI')
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
