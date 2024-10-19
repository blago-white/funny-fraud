from aiogram.fsm.state import StatesGroup, State


class SessionForm(StatesGroup):
    set_count_complete_requests = State()
    set_ref_link = State()
    set_bank_number = State()
    approve_session = State()
    enter_bank_code = State()
