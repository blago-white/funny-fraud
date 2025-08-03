import asyncio

import dotenv
import redis

dotenv.load_dotenv()

from db.services.sessions import SessionsService
from db.services.banking import BotBankingStatusService
from parser.drivers import WebDriversService
from parser.banking.parser import BaseBankingParser


async def main():
    from bot.main import startup

    conn = redis.Redis.from_url("redis://localhost:6379/0")  # TODO: Make os env param

    await startup()


def repl_task():
    asyncio.run(main())


if __name__ == "__main__":
    repl_task()
