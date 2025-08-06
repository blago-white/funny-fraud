from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.states.forms import MailCredentialsSettingForm

from ..common import mails_db_provider, MailCredsRepository


router = Router(name=__file__)


@router.message(F.text == "📧 Почты")
async def make_update_mails(message: Message, state: FSMContext):
    await state.set_state(state=MailCredentialsSettingForm.wait_emails)

    await message.bot.send_message(
        chat_id=message.chat.id,
        text="🔄Отправьте новые почты:\n"
             "<i>Если нажали по ошибке отправьте любой символ</i>",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(MailCredentialsSettingForm.wait_emails)
@mails_db_provider
async def set_mails(
        message: Message, state: FSMContext,
        mails_service: MailCredsRepository):
    await state.clear()

    if not len(message.text) > 3:
        return await message.reply("✅Ввод отменен")

    mails_service.add(data_set=message.text)

    await message.reply(
        text=f"✅Почты сохранены"
    )
