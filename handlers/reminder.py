from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu, get_cancel_keyboard
from database.db import save_reminder
from utils.logger import logger
from datetime import datetime

router = Router()

# Определение состояний для напоминаний
class ReminderStates(StatesGroup):
    TEXT = State()
    TIME = State()

# Обработчик выбора "Напоминалка"
@router.callback_query(F.data == "reminder")
async def start_reminder(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} начал создание напоминания")
    await callback_query.message.edit_text("Введите текст напоминания:", reply_markup=get_cancel_keyboard())
    await state.set_state(ReminderStates.TEXT)
    await callback_query.answer()

# Обработчик ввода текста напоминания
@router.callback_query(ReminderStates.TEXT, F.data == "cancel")
async def cancel_reminder(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} отменил создание напоминания")
    await state.clear()
    await callback_query.message.edit_text("Создание напоминания отменено.", reply_markup=get_main_menu())
    await callback_query.answer()

@router.message(ReminderStates.TEXT)
async def process_reminder_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    reminder_text = message.text
    logger.info(f"Пользователь {user_id} ввел текст напоминания: {reminder_text}")
    await state.update_data(reminder_text=reminder_text)
    await message.answer("Введите дату и время напоминания (в формате ДД.ММ.ГГГГ ЧЧ:ММ):", reply_markup=get_cancel_keyboard())
    await state.set_state(ReminderStates.TIME)

# Обработчик ввода времени напоминания
@router.callback_query(ReminderStates.TIME, F.data == "cancel")
async def cancel_reminder_time(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} отменил создание напоминания на этапе ввода времени")
    await state.clear()
    await callback_query.message.edit_text("Создание напоминания отменено.", reply_markup=get_main_menu())
    await callback_query.answer()

@router.message(ReminderStates.TIME)
async def process_reminder_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    reminder_time_input = message.text
    data = await state.get_data()
    reminder_text = data.get("reminder_text")
    try:
        # Конвертируем формат ДД.ММ.ГГГГ ЧЧ:ММ в ГГГГ-ММ-ДД ЧЧ:ММ
        reminder_time = datetime.strptime(reminder_time_input, "%d.%m.%Y %H:%M").strftime("%Y-%m-%d %H:%M")
        await save_reminder(user_id, reminder_text, reminder_time)
        await message.answer(f"Напоминание '{reminder_text}' установлено на {reminder_time_input} ⏰", reply_markup=get_main_menu())
        logger.info(f"Пользователь {user_id} установил напоминание на {reminder_time}")
    except ValueError:
        await message.answer("Ошибка: неверный формат даты и времени. Используйте формат ДД.ММ.ГГГГ ЧЧ:ММ (например, 20.10.2023 15:30). Попробуйте снова.", reply_markup=get_cancel_keyboard())
        logger.warning(f"Пользователь {user_id} ввел неверный формат времени: {reminder_time_input}")
    await state.clear()
