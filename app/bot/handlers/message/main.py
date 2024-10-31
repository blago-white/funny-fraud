from functools import wraps

from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards import MAIN_MENU_KB
from db.services.banking import BotBankingStatusService
from db.services.sessions import SessionsService
from parser.banking.parser import BaseBankingParser

router = Router(name=__name__)


def db_service_provider(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        service = SessionsService()
        return await func(*args, **kwargs, service=service)

    return wrapped


def bank_service_provider(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        service = BaseBankingParser()
        return await func(*args, **kwargs, bank=service)

    return wrapped


@router.message(CommandStart())
@bank_service_provider
async def start(message: Message, state: FSMContext, bank: BaseBankingParser):
    await state.clear()

    reply = await message.reply(
        text=f"🔄<b>Обновление...</b>\n<i>Ожидайте</i>",
        reply_markup=MAIN_MENU_KB
    )

    await _update_status(bank=bank)

    _, status = BotBankingStatusService().status()

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=f"🏠<b>Меню Парсера</b>\n\n<b>{status}</b>",
        reply_markup=MAIN_MENU_KB
    )

    await reply.delete()


async def _update_status(bank: BaseBankingParser):
    authenticated = await bank.authenticated
    bin_status, _ = BotBankingStatusService().status()

    if bin_status == authenticated:
        pass

    if authenticated:
        BotBankingStatusService().authenticated(bank.phone)

    else:
        BotBankingStatusService().unauthenticated()
