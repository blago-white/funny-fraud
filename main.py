import asyncio
import os

import dotenv

dotenv.load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.handlers.message import ROUTERS


async def main():
    dp = Dispatcher()

    bot = Bot(
        token=os.environ.get("BOT_TOKEN"),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp.include_routers(*ROUTERS)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
