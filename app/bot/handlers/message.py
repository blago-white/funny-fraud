from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart, Command
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..keyboards import MAIN_MENU_KB, EMPTY_KB
from ..states.forms import SessionForm

router = Router(name=__name__)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.reply(text="🏠Меню Парсера", reply_markup=MAIN_MENU_KB)


@router.message(F.text == "🔥Новый Сеанс")
async def new_session(message: Message, state: FSMContext):
    await state.set_state(state=SessionForm.set_count_complete_requests)

    await message.reply(
        text="Какое колличество полных запросов\n*[с закупом билета]*",
        parse_mode="MarkdownV2",
        reply_markup=EMPTY_KB
    )
