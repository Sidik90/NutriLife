import asyncio
from aiogram import Bot, Dispatcher
from config.config import BOT_TOKEN
from database.db import init_db, insert_test_foods
from handlers import start, main_menu, diagnostics, quiz, reminder, bju_calc, contact, help, admin
from utils.reminder_scheduler import start_scheduler
from utils.logger import logger

# Функция, выполняемая при запуске бота
async def on_startup(bot: Bot):
    await init_db()
    await insert_test_foods()  # Добавляем тестовые данные о продуктах
    start_scheduler(bot)  # Запускаем планировщик напоминаний
    logger.info("Бот запущен!")
    print("Бот запущен!")

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
        admin.router
    )
    # Запускаем бота в режиме polling (для локального тестирования)
    await dp.start_polling(bot, skip_updates=True, on_startup=lambda _: on_startup(bot))

if __name__ == "__main__":
    asyncio.run(main())