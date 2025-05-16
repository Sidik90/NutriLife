from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота, ID канала и ID администратора
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))