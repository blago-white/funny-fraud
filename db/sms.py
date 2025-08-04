from base import D


class ElSmsServiceApikeyRepository(DefaultApikeyRedisRepository):
    _APIKEY_KEY = "sms:el-sms-apikey"


class HelperSmsServiceApikeyRepository(DefaultApikeyRedisRepository):
    _APIKEY_KEY = "sms:helper-sms-apikey"
