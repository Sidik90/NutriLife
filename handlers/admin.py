from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from config.config import ADMIN_ID
from keyboards.inline import get_admin_menu, get_main_menu
from database.db import get_all_logs, get_all_reminders, get_all_contacts
from utils.logger import logger

router = Router()

# Обработчик команды /admin для входа в админ-панель
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        logger.warning(f"Пользователь {user_id} попытался получить доступ к админ-панели")
        await message.answer("У вас нет доступа к админ-панели. 🚫")
        return
    logger.info(f"Администратор {user_id} вошел в админ-панель")
    await message.answer("Добро пожаловать в админ-панель:", reply_markup=get_admin_menu())

# Обработчик выбора "Просмотреть логи"
@router.callback_query(F.data == "admin_logs")
async def view_logs(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id != ADMIN_ID:
        logger.warning(f"Пользователь {user_id} попытался просмотреть логи")
        await callback_query.message.edit_text("У вас нет доступа к логам. 🚫")
        await callback_query.answer()
        return
    logger.info(f"Администратор {user_id} запросил просмотр логов")
    logs = await get_all_logs(limit=50)
    if not logs:
        await callback_query.message.edit_text("Логи отсутствуют.", reply_markup=get_admin_menu())
        await callback_query.answer()
        return
    log_text = "📝 **Последние 50 логов:**\n\n"
    for log in logs:
        log_id, log_level, msg, uid, timestamp = log
        log_text += f"ID: {log_id} | Уровень: {log_level} | Время: {timestamp}\nСообщение: {msg}\nПользователь: {uid if uid else 'N/A'}\n---\n"
        if len(log_text) > 4000:  # Ограничение на длину сообщения в Telegram
            await callback_query.message.bot.send_message(chat_id=user_id, text=log_text, parse_mode="Markdown")
            log_text = ""
    if log_text:
        await callback_query.message.edit_text(log_text, parse_mode="Markdown", reply_markup=get_admin_menu())
    await callback_query.answer()

# Обработчик выбора "Просмотреть напоминания"
@router.callback_query(F.data == "admin_reminders")
async def view_reminders(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id != ADMIN_ID:
        logger.warning(f"Пользователь {user_id} попытался просмотреть напоминания")
        await callback_query.message.edit_text("У вас нет доступа к напоминаниям. 🚫")
        await callback_query.answer()
        return
    logger.info(f"Администратор {user_id} запросил просмотр напоминаний")
    reminders = await get_all_reminders()
    if not reminders:
        await callback_query.message.edit_text("Напоминания отсутствуют.", reply_markup=get_admin_menu())
        await callback_query.answer()
        return
    reminder_text = "⏰ **Список напоминаний:**\n\n"
    for reminder in reminders:
        user_id, text, time, is_sent = reminder
        status = "Отправлено" if is_sent else "Ожидает"
        reminder_text += f"Пользователь: {user_id}\nТекст: {text}\nВремя: {time}\nСтатус: {status}\n---\n"
        if len(reminder_text) > 4000:
            await callback_query.message.bot.send_message(chat_id=user_id, text=reminder_text, parse_mode="Markdown")
            reminder_text = ""
    if reminder_text:
        await callback_query.message.edit_text(reminder_text, parse_mode="Markdown", reply_markup=get_admin_menu())
    await callback_query.answer()

# Обработчик выбора "Просмотреть контакты"
@router.callback_query(F.data == "admin_contacts")
async def view_contacts(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id != ADMIN_ID:
        logger.warning(f"Пользователь {user_id} попытался просмотреть контакты")
        await callback_query.message.edit_text("У вас нет доступа к контактам. 🚫")
        await callback_query.answer()
        return
    logger.info(f"Администратор {user_id} запросил просмотр контактов")
    contacts = await get_all_contacts()
    if not contacts:
        await callback_query.message.edit_text("Контакты отсутствуют.", reply_markup=get_admin_menu())
        await callback_query.answer()
        return
    contact_text = "📞 **Список контактов:**\n\n"
    for contact in contacts:
        user_id, name, contact_info, timestamp = contact
        contact_text += f"Пользователь: {user_id}\nИмя: {name}\nКонтакт: {contact_info}\nВремя: {timestamp}\n---\n"
        if len(contact_text) > 4000:
            await callback_query.message.bot.send_message(chat_id=user_id, text=contact_text, parse_mode="Markdown")
            contact_text = ""
    if contact_text:
        await callback_query.message.edit_text(contact_text, parse_mode="Markdown", reply_markup=get_admin_menu())
    await callback_query.answer()
