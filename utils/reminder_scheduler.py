import asyncio
from datetime import datetime
from database.db import get_due_reminders, mark_reminder_sent
from utils.logger import logger

async def check_reminders(bot):
    logger.info("Запуск цикла проверки напоминаний.")
    while True:
        try:
            current_time = datetime.now()
            logger.info(f"Проверка напоминаний на время: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
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
            logger.error(f"Критическая ошибка в планировщике напоминаний: {str(e)}")
            # Небольшая пауза перед повторной попыткой, чтобы избежать спама ошибок
            await asyncio.sleep(5)
        # Проверяем каждые 10 секунд
        await asyncio.sleep(10)

def start_scheduler(bot):
    try:
        asyncio.create_task(check_reminders(bot))
        logger.info("Планировщик напоминаний успешно запущен.")
    except Exception as e:
        logger.error(f"Ошибка при запуске планировщика напоминаний: {str(e)}")