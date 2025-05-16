import aiosqlite
from datetime import datetime

# Инициализация базы данных при старте бота
async def init_db():
    async with aiosqlite.connect("nutrilife.db") as db:
        # Создаем таблицу для хранения заявок на обратный звонок
        await db.execute('''CREATE TABLE IF NOT EXISTS contacts (
            user_id INTEGER,
            name TEXT,
            contact_info TEXT,
            timestamp TEXT
        )''')
        await db.commit()
    print("База данных инициализирована.")

# Сохранение данных пользователя в базу
async def save_contact(user_id, name, contact_info):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect("nutrilife.db") as db:
        await db.execute("INSERT INTO contacts (user_id, name, contact_info, timestamp) VALUES (?, ?, ?, ?)",
                         (user_id, name, contact_info, timestamp))
        await db.commit()