import dotenv
import redis
from db.services.sessions import SessionsService

dotenv.load_dotenv()


if __name__ == "__main__":
    SessionsService(conn=redis.Redis.from_url("redis://localhost:6379/0"))

    from bot.main import startup

    startup()
