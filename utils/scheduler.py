import asyncio
from datetime import datetime
from aiogram import Bot
from database.db import get_due_reminders, mark_reminder_sent, clean_old_reminders
from utils.logger import logger

async def check_and_send_reminders(bot: Bot):
    logger.info("Запуск цикла проверки напоминаний (asyncio).")
    while True:
        try:
            current_time = datetime.now()
            logger.info(f"Проверка напоминаний на время (asyncio): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            reminders = await get_due_reminders()
            if not reminders:
                logger.info("Нет напоминаний для отправки на данный момент.")
            else:
                logger.info(f"Найдено {len(reminders)} напоминаний для отправки.")
                for user_id, reminder_text, reminder_time in reminders:
                    try:
                        logger.info(f"Обработка напоминания для пользователя {user_id}: {reminder_text} на {reminder_time}")
                        await bot.send_message(chat_id=user_id, text=f"Напоминание: {reminder_text} ⏰")
                        await mark_reminder_sent(user_id, reminder_time)
                        logger.info(f"Напоминание отправлено пользователю {user_id}: {reminder_text} на {reminder_time}")
                    except Exception as e:
                        logger.error(f"Ошибка при отправке напоминания пользователю {user_id} на {reminder_time}: {str(e)}")
        except Exception as e:
            logger.error(f"Критическая ошибка в проверке напоминаний (asyncio): {str(e)}")
        await asyncio.sleep(30)  # Проверяем каждые 30 секунд

async def clean_old_reminders_task():
    logger.info("Запуск цикла очистки старых напоминаний.")
    while True:
        try:
            current_time = datetime.now()
            logger.info(f"Очистка старых напоминаний на время: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            deleted_count = await clean_old_reminders(days=7)
            logger.info(f"Удалено {deleted_count} старых напоминаний.")
        except Exception as e:
            logger.error(f"Ошибка при очистке старых напоминаний: {str(e)}")
        await asyncio.sleep(86400)  # Проверяем раз в день (86400 секунд)