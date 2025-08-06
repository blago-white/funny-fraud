from functools import wraps

from db.mails.mails import MailCredsRepository
from db.gologin import GologinApikeysRepository
from db.sms import HelperSmsServiceApikeyRepository
from db.proxy import ProxyRepository
from db.captcha import CaptchaServiceApikeyRepository
from db.number import DonationPhoneNumberRepository


def mails_db_provider(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, mails_service=MailCredsRepository(), **kwargs)

    return wrapper


def gologin_repo_provider(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, gologin_service=GologinApikeysRepository(), **kwargs)

    return wrapper


def helpersms_repo_provider(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, helper_service=HelperSmsServiceApikeyRepository(), **kwargs)

    return wrapper


def proxy_repo_provider(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, proxy_service=ProxyRepository(), **kwargs)

    return wrapper


def captcha_repo_provider(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, captcha_service=CaptchaServiceApikeyRepository(), **kwargs)

    return wrapper


def donation_phone_repo_provider(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, donation_phone_service=DonationPhoneNumberRepository(), **kwargs)

    return wrapper
