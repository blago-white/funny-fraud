from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton


MAIN_MENU_KB = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📑Сеансы"), KeyboardButton(text="🔥Новый Сеанс")],
])

APPROVE_KB = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅Начать сеанс"), KeyboardButton(text="⛔️Отмена")]
])

EMPTY_KB = ReplyKeyboardMarkup(keyboard=[])
