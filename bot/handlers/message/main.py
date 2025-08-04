from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from .._labels import MAIN_MESSAGE

router = Router(name=__name__)


@router.message(CommandStart())
async def main(message: Message, state: FSMContext):
    menu_message = MAIN_MESSAGE.format(
        golog="✅",
        golog_count="1",
        elsms="❌",
        helpersms="✅",
        proxy="✅",
        captcha="2cfhdf23h...",
        number="9290007957",
        last_mail="dhdoebgf@gmail.com",
        count_mails="3"
    )

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=menu_message
    )
