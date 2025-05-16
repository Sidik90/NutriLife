from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для ответов "Да/Нет" и возврата в меню
def get_yes_no_back():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
        [KeyboardButton(text="Назад в меню")]
    ], resize_keyboard=True)
    return keyboard

# Клавиатура для записи на консультацию
def get_consultation_back():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Записаться на консультацию")],
        [KeyboardButton(text="Назад в меню")]
    ], resize_keyboard=True)
    return keyboard

# Клавиатура для отмены ввода
def get_cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Отмена")]
    ], resize_keyboard=True)
    return keyboard