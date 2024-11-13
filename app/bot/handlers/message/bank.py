from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states.forms import BankAccountLogin
from db.services.banking import BotBankingStatusService
from parser.banking import exceptions
from parser.banking.parser import BaseBankingParser
from .main import bank_service_provider, router


@router.message(F.text == "💳Добавить банк")
@bank_service_provider
async def authenticate_bank(
        message: Message,
        state: FSMContext,
        bank: BaseBankingParser):
    await state.set_state(BankAccountLogin.enter_phone)

    bank.reset()

    await message.reply(text="☎ Введите телефон обладателя карты\n\n"
                             "<i>формат: 9952481751</i>")


@router.message(BankAccountLogin.enter_phone)
@bank_service_provider
async def enter_bank_phone(
        message: Message,
        state: FSMContext,
        bank: BaseBankingParser):
    phone = message.text.replace(" ", "")

    if not phone.isdigit():
        await message.reply(text="❌Неверный формат")

    bank.add_phone(owner_phone=phone)

    await state.set_state(BankAccountLogin.enter_otp)

    reply = await message.reply("✅Отлично, теперь код из смс")

    await state.set_data(data={"phone": phone})

    try:
        bank.send_login_request()
    except Exception as e:
        await reply.edit_text(f"❌ОШИБКА: {e}")
        await state.clear()


@router.message(BankAccountLogin.enter_otp)
@bank_service_provider
async def enter_otp_bank_code(
        message: Message,
        state: FSMContext,
        bank: BaseBankingParser):
    reply = await message.reply("✅Принято, ожидайте")

    try:
        bank.enter_otp_code(code=message.text.replace(" ", ""))
    except exceptions.ReEnterOtp:
        await message.reply("🔄Ввведите новый код")
        return
    except exceptions.CardNumberEnterRequired:
        pass
    except exceptions.PasswordEnterRequired:
        try:
            bank.no_password_way()
        except exceptions.CardNumberEnterRequired:
            pass
    except (Exception, BaseException) as e:
        await reply.edit_text(f"❌ОШИБКА: {e}")
    else:
        await message.reply("✅Осуществлен быстрый вход по пинкоду!")
        return await state.clear()

    await message.reply("💳Введите номер любой карты т-банка без пробелов")

    await state.set_state(state=BankAccountLogin.enter_card)


@router.message(BankAccountLogin.enter_card)
@bank_service_provider
async def enter_bank_card(
        message: Message,
        state: FSMContext,
        bank: BaseBankingParser):
    reply = await message.reply("✅Принято, ожидайте")

    try:
        bank.enter_card_number(number=message.text.replace(" ", ""))
    except Exception as e:
        await reply.edit_text(f"❌ОШИБКА: {e}")

    phone = dict(await state.get_data()).get("phone")

    await state.clear()

    await message.reply("✅Номер карты принят, ожидайте")

    if await bank.authenticated:
        await message.reply("🔗Банк подключен\n\n"
                            "<i>информация об аккаунта будет "
                            "добавлена для просмотра позже</i>")

        BotBankingStatusService().authenticated(
            phone=phone
        )
    else:
        await message.reply(f"❌Ошибка входа в банкинг, попробуйте еще раз")
