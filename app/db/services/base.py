from abc import ABCMeta

from redis import Redis


class BaseService(metaclass=ABCMeta):
    _conn: Redis

    def __init__(self, conn: Redis = None):
        if conn:
            self._conn = conn

    def __new__(cls, conn: Redis = None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(BaseService, cls).__new__(cls)
            cls.instance._conn = conn
        return cls.instance
