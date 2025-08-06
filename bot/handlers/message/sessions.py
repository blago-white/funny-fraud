from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from bot.states.forms import SessionForm

from .. import common
from .._labels import MAIN_MESSAGE

router = Router(name=__name__)


@router.message(F.text == "🔥Новый Сеанс")
@common.gologin_repo_provider
@common.mails_db_provider
@common.helpersms_repo_provider
@common.proxy_repo_provider
@common.captcha_repo_provider
@common.donation_phone_repo_provider
async def new_session(
        message: Message,
        state: FSMContext,
        mails_service: common.MailCredsRepository,
        gologin_service: common.GologinApikeysRepository,
        helper_service: common.HelperSmsServiceApikeyRepository,
        proxy_service: common.ProxyRepository,
        captcha_service: common.CaptchaServiceApikeyRepository,
        donation_phone_service: common.DonationPhoneNumberRepository):
    if not (gologin_service.exists
            and helper_service.exists
            and donation_phone_service.exists
            and captcha_service.exists
            and mails_service.get_mail_storage_params()[0]):
        return await message.reply(
            "⭕Сначала добавьте <b>Gologin apikey</b>, один из"
            "<b>Sms-Service apikey</b>, <b>Captcha apikey</b>, почту, и телефон для дарения"
        )

    can_use_proxy, proxy = proxy_service.can_use

    if not can_use_proxy:
        return await message.reply(
            f"⭕Обновите прокси! <code>[{proxy}]</code>"
        )

    await state.set_state(state=SessionForm.set_count_complete_requests)

    await message.reply(
        text="Какое колличество полных заявок",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(SessionForm.set_count_complete_requests)
async def set_count_requests(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply(text="Неверное значение\n\n<i>должно быть "
                                 "целым числом</i>")
        return

    count = abs(int(message.text))

    await state.set_data(data={"count_requests": count})
    await state.set_state(SessionForm.set_ref_link)

    await message.reply(
        text="<b>Отлично</b>, теперь реф. ссылка:"
    )


@router.message(SessionForm.set_ref_link)
async def process_ref_link(message: Message, state: FSMContext):
    ref_links = message.text.split("\n")

    for link in ref_links:
        if (not link.startswith("https://")) or (" " in link):
            await message.reply("Неверный формат\n\n<i>нужна ссылка</i>")
            return

    current_session_form = dict(await state.get_data())

    await state.set_data(data=current_session_form | {
        "ref_links": ref_links
    })

    await state.set_state(state=SessionForm.approve_session)

    current_session_form = dict(await state.get_data())

    await message.reply(text="✅ Отлично, форма заполнена!\n",
                        reply_markup=APPROVE_KB)

    await message.reply(
        text=f"| Кол-во запросов: "
             f"{current_session_form.get("count_requests")}\n"
             f"| Реф. ссылки: <code>"
             f"{', '.join(current_session_form.get("ref_links"))}"
             f"</code>\n",
        reply_markup=get_session_presets_kb(),
    )
