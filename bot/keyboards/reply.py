from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton


MAIN_MENU_KB = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔥Новый Сеанс")],
    [KeyboardButton(text="🟩 Gologin Apikey")],
    [KeyboardButton(text="☎ El-Sms Apikey"),
     KeyboardButton(text="☎ Helper-Sms Apikey")],
    [KeyboardButton(text="🔐 Изменить Прокси")],
    [KeyboardButton(text="👾 Captcha Apikey")],
    [KeyboardButton(text="📲 Donation Phone")],
    [KeyboardButton(text="📧 Почты")],
], resize_keyboard=True)
