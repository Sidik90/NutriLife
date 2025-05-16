from aiogram import Router, F
from aiogram import types
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu
from keyboards.reply import get_cancel_keyboard
import asyncio

router = Router()

# Определение состояний для напоминаний
class ReminderStates(StatesGroup):
    TEXT = State()
    TIME = State()

# Обработчик выбора "Напоминалка"
@router.callback_query(lambda c: c.data == "reminder")
async def start_reminder(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите текст напоминания:", reply_markup=get_cancel_keyboard())
    await state.set_state(ReminderStates.TEXT)
    await callback_query.message.delete()
    await callback_query.answer()

# Обработчик ввода текста напоминания
@router.message(ReminderStates.TEXT, F.text == ["Отмена"])
async def cancel_reminder(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Напоминание отменено.", reply_markup=get_main_menu())

@router.message(ReminderStates.TEXT)
async def process_reminder_text(message: Message, state: FSMContext):
    await state.update_data(reminder_text=message.text)
    await message.answer("Введите дату и время напоминания (формат: ДД.ММ.ГГГГ ЧЧ:ММ):", reply_markup=get_cancel_keyboard())
    await state.set_state(ReminderStates.TIME)

# Обработчик ввода времени напоминания
@router.message(ReminderStates.TIME, F.text == ["Отмена"])
async def cancel_reminder_time(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Напоминание отменено.", reply_markup=get_main_menu())

@router.message(ReminderStates.TIME)
async def process_reminder_time(message: Message, state: FSMContext):
    await state.update_data(reminder_time=message.text)
    user_data = await state.get_data()
    await message.answer(f"Напоминание установлено: {user_data['reminder_text']} на {user_data['reminder_time']}.", reply_markup=get_main_menu())
    await state.clear()
    # Здесь можно добавить логику для отправки напоминания в указанное время (например, через asyncio.sleep)