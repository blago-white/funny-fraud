from .base import DefaultApikeyRedisRepository


class CaptchaServiceApikeyRepository(DefaultApikeyRedisRepository):
    _APIKEY_KEY = "cap:cap-apikey"
