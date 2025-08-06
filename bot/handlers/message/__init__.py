from .main import router as main_router
from .captcha import router as captcha_router
from .donations import router as donations_router
from .gologin import router as gologin_router
from .mails import router as mails_router
from .proxy import router as proxy_router
from .sessions import router as sessions_router
from .sms import router as sms_router

ROUTERS = [sms_router,
           sessions_router,
           proxy_router,
           gologin_router,
           donations_router,
           main_router,
           captcha_router,
           mails_router]
