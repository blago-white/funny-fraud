from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton


MAIN_MENU_KB = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📑Сеансы"),
     KeyboardButton(text="🔥Новый Сеанс"),
     KeyboardButton(text="💳Добавить банк")],
], resize_keyboard=True)

APPROVE_KB = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅Начать сеанс"), KeyboardButton(text="⛔️Отмена")]
], resize_keyboard=True)

EMPTY_KB = ReplyKeyboardMarkup(keyboard=[])
