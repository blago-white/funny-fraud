from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.states.forms import CaptchaSettingForm
from db.captcha import CaptchaServiceApikeyRepository
from ..common import captcha_repo_provider

router = Router(name=__name__)


@router.message(F.text == "👾 Captcha Apikey")
async def make_reset_apikey(message: Message, state: FSMContext):
    await state.set_state(state=CaptchaSettingForm.wait_apikey)

    await message.bot.send_message(
        chat_id=message.chat.id,
        text="🔄Укажите новый apikey:\n"
             "<i>Если нажали по ошибке отправьте любой символ</i>",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(CaptchaSettingForm.wait_apikey)
@captcha_repo_provider
async def set_apikey(
        message: Message, state: FSMContext,
        captcha_service: CaptchaServiceApikeyRepository):
    await state.clear()

    if not len(message.text) > 3:
        return await message.reply("✅Ввод отменен")

    captcha_service.set(new_apikey=message.text.replace(" ", ""))

    await message.reply(
        text=f"✅Ключ сохранен:\n\n <code>{captcha_service.get_current()}</code>"
    )
