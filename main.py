import asyncio
from aiogram import Bot, Dispatcher
from config.config import BOT_TOKEN
from database.db import init_db
from handlers import start, main_menu, diagnostics, quiz, reminder, bju_calc, contact, help

# Функция, выполняемая при запуске бота
async def on_startup():
    await init_db()
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
        help.router
    )
    # Запускаем бота в режиме polling (для локального тестирования)
    await dp.start_polling(bot, on_startup=on_startup)

if __name__ == "__main__":
    asyncio.run(main())