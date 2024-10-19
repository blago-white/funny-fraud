from aiogram.fsm.state import StatesGroup, State


class SessionForm(StatesGroup):
    set_count_complete_requests = State()
    set_ref_link = State()
    set_proxies = State()
    enter_bank_code = State()
