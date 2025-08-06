from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.states.forms import ProxySettingForm
from db.proxy import ProxyRepository
from ..common import proxy_repo_provider

router = Router(name=__name__)


@router.message(F.text == "🔐 Изменить Прокси")
async def make_reset_apikey(message: Message, state: FSMContext):
    await state.set_state(state=ProxySettingForm.wait_base_proxy)

    await message.bot.send_message(
        chat_id=message.chat.id,
        text="🔄Укажите паттерн прокси:\n"
             "<i>Если нажали по ошибке отправьте любой символ</i>",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(ProxySettingForm.wait_base_proxy)
@proxy_repo_provider
async def set_apikey(
        message: Message, state: FSMContext,
        proxydb: ProxyRepository):
    await state.clear()

    print("START")

    if (not len(message.text) > 3) or (len(message.text.split(":")) != 3):
        print("OTM")
        return await message.reply("✅Ввод отменен")

    try:
        proxy = proxydb.add(proxy=message.text.replace(
            " ", ""
        ).replace("\n", ""))
    except Exception as e:
        return await message.reply(
            text=f"Ошибка добавления прокси: {e!r}"
        )

    print("OK")

    await message.reply(
        text=f"✅Прокси сохранен:\n\n <code>{proxy}</code>"
    )
