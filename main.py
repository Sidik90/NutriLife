import asyncio
from aiogram import Bot, Dispatcher
from config.config import BOT_TOKEN
from database.db import init_db
from handlers import (
    start,
    main_menu,
    diagnostics,
    quiz,
    reminder,
    bju_calc,
    contact,
    help,
    admin,
)
from utils.logger import logger
from utils.scheduler import check_and_send_reminders, clean_old_reminders_task


# Основная функция для запуска бота
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    # Подключаем все обработчики
    dp.include_routers(
        start.router,
        main_menu.router,
        diagnostics.router,
        quiz.router,
        reminder.router,
        bju_calc.router,
        contact.router,
        help.router,
        admin.router,
    )

    # Инициализируем базу данных
    await init_db()
    logger.info("Бот запущен!")

    # Запускаем цикл проверки напоминаний как отдельную задачу
    asyncio.create_task(check_and_send_reminders(bot))
    logger.info("Цикл проверки напоминаний (asyncio) запущен с интервалом 30 секунд.")

    # Запускаем цикл очистки старых напоминаний как отдельную задачу
    asyncio.create_task(clean_old_reminders_task())
    logger.info("Цикл очистки старых напоминаний запущен с интервалом 1 день.")

    # Запускаем бота в режиме polling
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
