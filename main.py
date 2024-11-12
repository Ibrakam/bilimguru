import logging

from aiogram import Bot, Dispatcher
from dotenv import dotenv_values
from db import Base, engine
from bot import router

config = dotenv_values(".env")

BOT_TOKEN = config["BOT_TOKEN"]


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    Base.metadata.create_all(bind=engine)
    asyncio.run(main())
