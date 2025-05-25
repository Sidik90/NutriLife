import logging
import os
import sys
from database.db import save_log_to_db

# Установите кодировку UTF-8 для стандартных потоков вывода
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Создаем папку для логов, если её нет
os.makedirs("logs", exist_ok=True)

# Настройка логгера
logger = logging.getLogger("NutriLifeBot")
logger.setLevel(logging.INFO)

# Формат сообщений логов
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

# Настройка файлового обработчика
file_handler = logging.FileHandler("logs/bot.log", encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Настройка консольного обработчика (закомментирована, чтобы избежать дублирования)
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setFormatter(formatter)
# console_handler.stream.reconfigure(encoding='utf-8')
# logger.addHandler(console_handler)

# Функция для логирования с сохранением в базу данных (для важных событий)
async def log_to_db(level, message, user_id=None):
    logger.log(getattr(logging, level.upper()), message)
    if level.upper() in ["WARNING", "ERROR"]:
        await save_log_to_db(level.upper(), message, user_id)