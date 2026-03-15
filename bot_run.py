#БОТ для оли
import asyncio
import logging


from aiogram import Bot, Dispatcher


from App.handler import router
from bot_token import TOKEN




bot = Bot(token=TOKEN)
dp = Dispatcher()



async def main():
    print('Бот запущен')
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот отключён')