import logging
import os
from datetime import datetime
from database.db import save_log_to_db

# Создаем папку для логов, если её нет
os.makedirs("logs", exist_ok=True)

# Настройка логгера
logger = logging.getLogger("NutriLifeBot")
logger.setLevel(logging.INFO)

# Формат сообщений логов
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Настройка файлового обработчика
file_handler = logging.FileHandler("logs/bot.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Настройка консольного обработчика (для вывода в терминал)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Функция для логирования с сохранением в базу данных (для важных событий)
async def log_to_db(level, message, user_id=None):
    logger.log(getattr(logging, level.upper()), message)
    if level.upper() in ["WARNING", "ERROR"]:
        await save_log_to_db(level.upper(), message, user_id)