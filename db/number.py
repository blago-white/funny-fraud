from .base import DefaultApikeyRedisRepository


class DonationPhoneNumberRepository(DefaultApikeyRedisRepository):
    _APIKEY_KEY = "phn:number"
