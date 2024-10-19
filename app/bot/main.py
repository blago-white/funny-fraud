import asyncio
import os

from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram import Bot

from .handlers import messages_router


async def main(token: str):
    bot = Bot(token=token)

    dp = Dispatcher()

    dp.include_router(router=messages_router)

    await dp.start_polling(bot)


asyncio.run(main(os.environ.get("TOKEN")))
