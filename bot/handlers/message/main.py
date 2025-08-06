from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from bot.keyboards.reply import MAIN_MENU_KB

from .. import common
from .._labels import MAIN_MESSAGE

router = Router(name=__name__)


@router.message(CommandStart())
@common.gologin_repo_provider
@common.mails_db_provider
@common.helpersms_repo_provider
@common.proxy_repo_provider
@common.captcha_repo_provider
@common.donation_phone_repo_provider
async def main(message: Message,
               mails_service: common.MailCredsRepository,
               gologin_service: common.GologinApikeysRepository,
               helper_service: common.HelperSmsServiceApikeyRepository,
               proxy_service: common.ProxyRepository,
               captcha_service: common.CaptchaServiceApikeyRepository,
               donation_phone_service: common.DonationPhoneNumberRepository,
               state: FSMContext):
    mail_storage_params = mails_service.get_mail_storage_params()
    gologins_params = gologin_service.get_current(), gologin_service.get_count()
    captcha_apikey = captcha_service.get_current()

    menu_message = MAIN_MESSAGE.format(
        golog=f"✅ {gologins_params[0]}" if gologins_params[0] else "❌ Не добавлено",
        golog_count=gologins_params[1],
        elsms="❌",
        helpersms="✅" if helper_service.get_current() else "❌",
        proxy="✅" if proxy_service.can_use else "❌",
        captcha=f"✅ {captcha_apikey[:7]}..." if captcha_apikey else "❌",
        number=donation_phone_service.get_current() or "❌",
        last_mail=mail_storage_params[0] or "Не добавлено",
        count_mails=mail_storage_params[1]
    )

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=menu_message,
        reply_markup=MAIN_MENU_KB
    )
