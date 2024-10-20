import asyncio
import os
import time

import dotenv
import redis
from db.services.sessions import SessionsService

dotenv.load_dotenv()


async def main():
    pass


if __name__ == "__main__":
    # SessionsService(conn=redis.Redis.from_url("redis://localhost:6379/0"))

    asyncio.run(main())

    # from bot.main import startup
    #
    # startup()
