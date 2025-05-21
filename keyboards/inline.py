from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню с Inline-кнопками
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Диагностика 🩺", callback_data="diagnostics")],
        [InlineKeyboardButton(text="Сыграть со мной в квиз 🎮", callback_data="quiz"), InlineKeyboardButton(text="Расчет БЖУ 🍎", callback_data="bju_calc")],
        [InlineKeyboardButton(text="Напоминалка ⏰", callback_data="reminder"), InlineKeyboardButton(text="Помощь ❓", callback_data="help")],
        [InlineKeyboardButton(text="Записаться на консультацию 📞", callback_data="contact")]
    ])
    return keyboard

# Меню выбора модулей для диагностики
def get_diagnostics_modules():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ЖКТ 🍽", callback_data="diag_jkt")],
        [InlineKeyboardButton(text="Щитовидная железа 🧬", callback_data="diag_hormones")],
        [InlineKeyboardButton(text="Инсулин 🩸", callback_data="diag_insulin")],
        [InlineKeyboardButton(text="Дефициты 🛡", callback_data="diag_deficiencies")],
        [InlineKeyboardButton(text="Назад 🔙", callback_data="back_to_menu")]
    ])
    return keyboard

# Клавиатура для ответов "Да/Нет" в диагностике
def get_yes_no_keyboard(theme, question_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да ✅", callback_data=f"diag_answer_{theme}_{question_id}_yes"),
            InlineKeyboardButton(text="Нет ❌", callback_data=f"diag_answer_{theme}_{question_id}_no")
        ]
    ])
    return keyboard

# Клавиатура после завершения диагностики
def get_diagnostic_result_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записаться на консультацию 📅", callback_data="consultation")],
        [InlineKeyboardButton(text="Вернуться в главное меню 🔙", callback_data="back_to_menu")]
    ])
    return keyboard

# Клавиатура для квиза (выбор ответа)
def get_quiz_options(question_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вариант 1", callback_data=f"quiz_{question_id}_1")],
        [InlineKeyboardButton(text="Вариант 2", callback_data=f"quiz_{question_id}_2")],
        [InlineKeyboardButton(text="Назад 🔙", callback_data="back_to_menu")]
    ])
    return keyboard

# Клавиатура для выбора обратного звонка
def get_contact_choice():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, перезвоните 📞", callback_data="contact_yes")],
#       [InlineKeyboardButton(text="Нет, сам контакт ✉️", callback_data="contact_no")],
        [InlineKeyboardButton(text="Назад 🔙", callback_data="back_to_menu")]
    ])
    return keyboard

# Клавиатура для напоминаний и БЖУ (отмена)
def get_cancel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена 🚫", callback_data="cancel")]
    ])
    return keyboard

# Клавиатура для админ-панели
def get_admin_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Просмотреть логи 📝", callback_data="admin_logs")],
        [InlineKeyboardButton(text="Просмотреть напоминания ⏰", callback_data="admin_reminders")],
        [InlineKeyboardButton(text="Просмотреть контакты 📞", callback_data="admin_contacts")],
        [InlineKeyboardButton(text="Назад в меню 🔙", callback_data="back_to_menu")]
    ])
    return keyboard