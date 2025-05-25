import aiosqlite
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu, get_cancel_keyboard
from database.db import save_reminder
from utils.logger import logger
from datetime import datetime

from project.Bots.NutriLifeBot.database.db import get_all_reminders

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

# Обработчик отмены на этапе ввода текста
@router.callback_query(ReminderStates.TEXT, F.data == "cancel")
async def cancel_reminder(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} отменил создание напоминания")
    await state.clear()
    await callback_query.message.edit_text("Создание напоминания отменено.", reply_markup=get_main_menu())
    await callback_query.answer()

# Обработчик ввода текста напоминания
@router.message(ReminderStates.TEXT)
async def process_reminder_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    reminder_text = message.text
    logger.info(f"Пользователь {user_id} ввел текст напоминания: {reminder_text}")
    await state.update_data(reminder_text=reminder_text)
    await message.answer("Введите дату и время напоминания (в формате ДД.ММ.ГГГГ ЧЧ:ММ):", reply_markup=get_cancel_keyboard())
    await state.set_state(ReminderStates.TIME)

# Обработчик отмены на этапе ввода времени
@router.callback_query(ReminderStates.TIME, F.data == "cancel")
async def cancel_reminder_time(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} отменил создание напоминания на этапе ввода времени")
    await state.clear()
    await callback_query.message.edit_text("Создание напоминания отменено.", reply_markup=get_main_menu())
    await callback_query.answer()

# Обработчик ввода времени напоминания
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
    except Exception as e:
        await message.answer("Произошла ошибка при сохранении напоминания. Попробуйте снова.", reply_markup=get_cancel_keyboard())
        logger.error(f"Ошибка при сохранении напоминания для пользователя {user_id}: {str(e)}")
    finally:
        await state.clear()


# Команда для проверки всех напоминаний
@router.message(lambda message: message.text == "/check_reminders")
async def check_reminders_command(message: Message):
    user_id = message.from_user.id
    reminders = await get_all_reminders()
    user_reminders = [r for r in reminders if r[0] == user_id]

    if not user_reminders:
        await message.answer("У вас нет сохраненных напоминаний.")
        logger.info(f"Пользователь {user_id} запросил список напоминаний: список пуст")
        return

    response = "⏰ Ваши напоминания:\n\n"
    for i, (uid, text, time, sent) in enumerate(user_reminders, 1):
        status = "Отправлено" if sent else "Ожидает"
        response += f"{i}. Текст: {text}\n"
        response += f"   Время: {time}\n"
        response += f"   Статус: {status}\n"
        response += "---\n"
    await message.answer(response)
    logger.info(f"Пользователь {user_id} запросил список напоминаний: найдено {len(user_reminders)} напоминаний")

@router.message(lambda message: message.text == "/clear_invalid_reminders")
async def clear_invalid_reminders(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("nutrilife.db") as db:
        cursor = await db.execute("SELECT reminder_text, reminder_time FROM reminders WHERE user_id = ? AND is_sent = 0", (user_id,))
        reminders = await cursor.fetchall()
        invalid_count = 0
        for reminder_text, reminder_time_str in reminders:
            try:
                if reminder_time_str.count('.') == 2:
                    datetime.strptime(reminder_time_str, "%d.%m.%Y %H:%M")
                else:
                    datetime.strptime(reminder_time_str, "%Y-%m-%d %H:%M")
            except ValueError:
                await db.execute("DELETE FROM reminders WHERE user_id = ? AND reminder_time = ?", (user_id, reminder_time_str))
                invalid_count += 1
        await db.commit()
    await message.answer(f"Удалено {invalid_count} напоминаний с некорректным форматом времени.")
    logger.info(f"Пользователь {user_id} удалил {invalid_count} некорректных напоминаний")

@router.message(lambda message: message.text == "/force_send_reminders")
async def force_send_reminders(message: Message, bot):
    user_id = message.from_user.id
    current_time = datetime.now()
    async with aiosqlite.connect("nutrilife.db") as db:
        cursor = await db.execute("SELECT user_id, reminder_text, reminder_time FROM reminders WHERE is_sent = 0 AND user_id = ?", (user_id,))
        reminders = await cursor.fetchall()
        sent_count = 0
        for reminder in reminders:
            uid, reminder_text, reminder_time_str = reminder
            try:
                reminder_time = None
                possible_formats = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M", "%d.%m.%Y %H:%M:%S"]
                for date_format in possible_formats:
                    try:
                        reminder_time = datetime.strptime(reminder_time_str, date_format)
                        break
                    except ValueError:
                        continue
                if reminder_time and reminder_time <= current_time:
                    await bot.send_message(chat_id=user_id, text=f"Напоминание (принудительная отправка): {reminder_text} ⏰")
                    await db.execute("UPDATE reminders SET is_sent = 1 WHERE user_id = ? AND reminder_time = ?", (user_id, reminder_time_str))
                    sent_count += 1
            except Exception as e:
                logger.error(f"Ошибка при принудительной отправке напоминания {reminder_text} на {reminder_time_str}: {str(e)}")
        await db.commit()
    await message.answer(f"Принудительно отправлено {sent_count} напоминаний.")
    logger.info(f"Пользователь {user_id} принудительно отправил {sent_count} напоминаний")