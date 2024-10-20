from functools import wraps

from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from db.services.sessions import SessionsService, Session
from ..keyboards import MAIN_MENU_KB, APPROVE_KB
from ..states.forms import SessionForm

router = Router(name=__name__)


def db_service_provider(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        service = SessionsService()
        return await func(*args, **kwargs, service=service)

    return wrapped


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.reply(text="🏠Меню Парсера", reply_markup=MAIN_MENU_KB)


@router.message(F.text == "🔥Новый Сеанс")
async def new_session(message: Message, state: FSMContext):
    await state.set_state(state=SessionForm.set_count_complete_requests)

    await message.reply(
        text="Какое колличество полных заявок\n<b>с закупом билета</b>",
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
    ref_link = message.text

    if (not ref_link.startswith("https://")) or (" " in ref_link):
        await message.reply("Неверный формат\n\n<i>нужна ссылка</i>")
        return

    current_session_form = dict(await state.get_data())
    await state.set_data(data=current_session_form | {"ref_link": ref_link})
    await state.set_state(state=SessionForm.set_bank_number)

    await message.reply(
        text="Отлично, теперь введи номер телефона от банковского аккаунта:"
    )


@router.message(SessionForm.set_bank_number)
async def set_phone(message: Message, state: FSMContext):
    number = message.text.replace(" ", "")

    if len(number) not in (11, 12, 10):
        await message.reply("Неверный формат номера телефона")

    current_session_form = dict(await state.get_data())

    await state.set_data(
        data=current_session_form | {"phone_number": number[-10:]}
    )

    await state.set_state(state=SessionForm.approve_session)

    await message.reply(
        text="✅ Отлично, форма заполнена!\n"
             f"| Кол-во запросов: "
             f"{current_session_form.get("count_requests")}\n"
             f"| Реф. ссылка: <code>"
             f"{current_session_form.get("ref_link")}</code>\n"
             f"| Номер: <code>{number[-10:]}</code>\n",
        reply_markup=APPROVE_KB
    )


@router.message(SessionForm.approve_session)
@db_service_provider
async def approve_session(
        message: Message, state: FSMContext, service: SessionsService):
    if message.text != "✅Начать сеанс":
        await message.reply("✅Отменен")
        await state.clear()
        return

    form = dict(await state.get_data())

    session = Session.from_dict(
        dict_=form
    )

    service.add(passed_session=session)

    await state.clear()

    replyed = await message.reply(
        text=f"✅ <b>Сессия начата</b>\n"
        "\n".join(
            [f"#{i} - ?" for i in range(session.count_requests)]
        )
    )


@router.message(F.text == "📑Сеансы")
@db_service_provider
async def get_all_sessions(message: Message, service: SessionsService):
    sessions: list[bytes] = service.get_all()

    if not sessions:
        await message.reply("❌ Сессий еще не было!")
        return

    sessions = [i.decode().split("@") for i in sessions]
    header = "<b>Проведенные сессии:</b>\n"
    table = "\n".join(
        ["\n".join((f"| <b>✅{s[0]} ❌{s[1]}</b>",
                    f"| 🌐{s[2]}",
                    f"| 📞<code>{s[-1]}</code>",
                    "— — — — — — — — —")) for s in sessions]
    )

    await message.reply(
        text=header + table
    )
