from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton


MAIN_MENU_KB = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📑Сеансы"), KeyboardButton(text="🔥Новый Сеанс")],
])

EMPTY_KB = ReplyKeyboardMarkup()
