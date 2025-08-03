from functools import wraps

from aiogram.dispatcher.router import Router
from db.services.sessions import SessionsService

router = Router(name=__name__)


def db_service_provider(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        service = SessionsService()
        return await func(*args, **kwargs, service=service)

    return wrapped
