from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.states.forms import DonationPhoneSettingForm
from db.number import DonationPhoneNumberRepository

from ..common import donation_phone_repo_provider

router = Router(name=__name__)


@router.message(F.text == "📲 Donation Phone")
async def make_reset_number(message: Message, state: FSMContext):
    await state.set_state(state=DonationPhoneSettingForm.wait_phone)

    await message.bot.send_message(
        chat_id=message.chat.id,
        text="🔄Укажите новый номер телефона:\n"
             "<i>Если нажали по ошибке отправьте любой символ</i>",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(DonationPhoneSettingForm.wait_phone)
@donation_phone_repo_provider
async def set_number(
        message: Message, state: FSMContext,
        donation_phone_service: DonationPhoneNumberRepository):
    await state.clear()

    if not len(message.text) > 3:
        return await message.reply("✅Ввод отменен")

    donation_phone_service.set(new_apikey=message.text.replace(" ", ""))

    await message.reply(
        text=f"✅Номер сохранен:\n\n <code>{donation_phone_service.get_current()}</code>"
    )
