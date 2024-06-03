import asyncio
from aiogram import Bot, Dispatcher
from Config import TOKEN
from app.handlers import router
from app.database.models import async_main
from app.middleware import AuthMiddleware


async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Добавляем middleware для проверки авторизации
    dp.message.middleware(AuthMiddleware())

    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
