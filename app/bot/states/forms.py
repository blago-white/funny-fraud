from aiogram.fsm.state import StatesGroup, State


class SessionForm(StatesGroup):
    set_count_complete_requests = State()
    set_ref_link = State()
    approve_session = State()


class BankAccountLogin(StatesGroup):
    enter_phone = State()
    enter_otp = State()
    enter_card = State()
