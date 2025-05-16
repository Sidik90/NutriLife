from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню с инлайн-кнопками
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Диагностика", callback_data="diagnostics")],
        [InlineKeyboardButton(text="Сыграть со мной в квиз", callback_data="quiz")],
        [InlineKeyboardButton(text="Напоминалка", callback_data="reminder")],
        [InlineKeyboardButton(text="Расчет БЖУ", callback_data="bju_calc")],
        [InlineKeyboardButton(text="Связаться с нами", callback_data="contact")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ])
    return keyboard

# Меню выбора модулей для диагностики
def get_diagnostics_modules():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Модуль 1: Питание", callback_data="module_1")],
        [InlineKeyboardButton(text="Модуль 2: Сон", callback_data="module_2")],
        [InlineKeyboardButton(text="Модуль 3: Стресс", callback_data="module_3")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ])
    return keyboard

# Клавиатура для квиза (выбор ответа)
def get_quiz_options(question_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вариант 1", callback_data=f"quiz_{question_id}_1")],
        [InlineKeyboardButton(text="Вариант 2", callback_data=f"quiz_{question_id}_2")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ])
    return keyboard

# Клавиатура для выбора обратного звонка
def get_contact_choice():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, перезвоните", callback_data="contact_yes")],
        [InlineKeyboardButton(text="Нет, просто контакт", callback_data="contact_no")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ])
    return keyboard