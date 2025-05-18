import asyncio
from datetime import datetime
from database.db import get_due_reminders, mark_reminder_sent
from utils.logger import logger

async def check_reminders(bot):
    while True:
        try:
            reminders = await get_due_reminders()
            for user_id, reminder_text, reminder_time in reminders:
                try:
                    await bot.send_message(chat_id=user_id, text=f"Напоминание: {reminder_text} ⏰")
                    await mark_reminder_sent(user_id, reminder_time)
                    logger.info(f"Напоминание отправлено пользователю {user_id}: {reminder_text} на {reminder_time}")
                except Exception as e:
                    logger.error(f"Ошибка при отправке напоминания пользователю {user_id}: {str(e)}")
            await asyncio.sleep(10)  # Проверяем каждые 10 секунд для более частого обновления
        except Exception as e:
            logger.error(f"Ошибка в планировщике напоминаний: {str(e)}")
            await asyncio.sleep(60)  # Если ошибка, ждем минуту перед следующей попыткой

def start_scheduler(bot):
    asyncio.create_task(check_reminders(bot))
    logger.info("Планировщик напоминаний запущен")