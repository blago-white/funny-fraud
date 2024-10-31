from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards import APPROVE_KB, EMPTY_KB
from bot.states.forms import SessionForm
from db.services.banking import BotBankingStatusService
from db.services.sessions import SessionsService, Session
from parser.services import PlatformLeadsService
from .main import db_service_provider, router, start


@router.message(F.text == "🔥Новый Сеанс")
async def new_session(message: Message, state: FSMContext):
    await state.set_state(state=SessionForm.set_count_complete_requests)

    await message.reply(
        text="Какое колличество полных заявок\n<b>с закупом билета</b>"
             "\n\n<i>во время тестирования игнорируется</i>",
        reply_markup=EMPTY_KB
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
    await state.set_state(state=SessionForm.set_proxy)

    await message.reply(
        text="<b>Последний шаг.</b> Введите список прокси"
             "Формат: <i>login1:password1@host1:port1 "
             "login2:password2@host2:port2</i>"
    )


@router.message(SessionForm.set_proxy)
async def set_proxyies(message: Message, state: FSMContext):
    if not message.text.split():
        await message.reply(text="❌Прокси не добавлены либо неверный формат")
        return

    proxy_list = message.text.split()
    count_requests = int((await state.get_data()).get("count_requests"))
    
    if len(proxy_list) != count_requests:
        await message.reply(text="❌Неверное кол-во прокси:\n"
                                 f"Получено: {len(proxy_list)}\n"
                                 f"Нужно: {count_requests}")
        return

    await state.set_data(data=dict(await state.get_data()) | {
        "proxy": message.text
    })

    current_session_form = dict(await state.get_data())

    await state.set_state(SessionForm.approve_session)

    await message.reply(
        text="✅ Отлично, форма заполнена!\n"
             f"| Кол-во запросов: "
             f"{current_session_form.get("count_requests")}\n"
             f"| Реф. ссылка: <code>"
             f"{current_session_form.get("ref_link")}</code>\n"
             f"| Прокси добавлены",
        reply_markup=APPROVE_KB
    )


@router.message(SessionForm.approve_session)
@db_service_provider
async def approve_session(
        message: Message, state: FSMContext, service: SessionsService
):
    if message.text != "✅Начать сеанс":
        await message.reply("✅Отменен")
        await state.clear()
        return

    form = dict(await state.get_data())

    session = Session.from_dict(
        dict_=form | {"phone_number": BotBankingStatusService().get_number()}
    )

    proxy_list = form.get("proxy").split()

    session_id = service.add(passed_session=session)

    await state.clear()

    replyed = await message.reply(
        text=f"✅<b>Сессия начата, ожидайте, результаты будут ниже</b>\n\n"
             f"<i>около 5 мин. на лид</i>"
    )

    try:
        results = PlatformLeadsService().mass_generate(
            ref_link=session.ref_link,
            count=int(session.count_requests),
            proxy=proxy_list
        )

        print(results)

        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Results:\n"
                 "\n".join([
                f"{'✅' if i[0] else '❌'}-{i[1]}-{i[2]}" for i in results
            ])
        )
        # async for gen in PlatformLeadsService().mass_generate(
        #     ref_link=session.ref_link,
        #     count=int(session.count_requests),
        #     proxy=proxy_list
        # ):
        #     replyed = await replyed.edit_text(text=replyed.text + "\n" + gen)
    except BaseException as e:
        await replyed.edit_text(
            text="❌ <b>Сессия прервалась с ошибкой</b>\n\n"
                 f"<code>{e}</code>",
        )
    else:
        service.update_successed_count(session_id=session_id,
                                       count=session.count_successed)

        await start(message=message, state=state)


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
