import aiosqlite
from datetime import datetime

async def init_db():
    async with aiosqlite.connect("nutrilife.db") as db:
        # Таблица для контактов (заявки на обратный звонок)
        await db.execute('''CREATE TABLE IF NOT EXISTS contacts (
            user_id INTEGER,
            name TEXT,
            contact_info TEXT,
            timestamp TEXT
        )''')
        # Таблица для напоминаний
        await db.execute('''CREATE TABLE IF NOT EXISTS reminders (
            user_id INTEGER,
            reminder_text TEXT,
            reminder_time TEXT,
            is_sent INTEGER DEFAULT 0
        )''')
        # Таблица для данных о продуктах (БЖУ)
        await db.execute('''CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            protein REAL DEFAULT 0.0,
            fat REAL DEFAULT 0.0,
            carbs REAL DEFAULT 0.0,
            calories REAL DEFAULT 0.0
        )''')
        # Таблица для логов
        await db.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_level TEXT NOT NULL,
            message TEXT NOT NULL,
            user_id INTEGER,
            timestamp TEXT NOT NULL
        )''')
        await db.commit()
    print("База данных инициализирована.")

async def save_contact(user_id, name, contact_info):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect("nutrilife.db") as db:
        await db.execute("INSERT INTO contacts (user_id, name, contact_info, timestamp) VALUES (?, ?, ?, ?)",
                         (user_id, name, contact_info, timestamp))
        await db.commit()

async def save_reminder(user_id, reminder_text, reminder_time):
    async with aiosqlite.connect("nutrilife.db") as db:
        await db.execute("INSERT INTO reminders (user_id, reminder_text, reminder_time, is_sent) VALUES (?, ?, ?, 0)",
                         (user_id, reminder_text, reminder_time))
        await db.commit()

async def get_due_reminders():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    async with aiosqlite.connect("nutrilife.db") as db:
        cursor = await db.execute("SELECT user_id, reminder_text, reminder_time FROM reminders WHERE is_sent = 0 AND reminder_time <= ?",
                                  (current_time,))
        reminders = await cursor.fetchall()
        return reminders

async def mark_reminder_sent(user_id, reminder_time):
    async with aiosqlite.connect("nutrilife.db") as db:
        await db.execute("UPDATE reminders SET is_sent = 1 WHERE user_id = ? AND reminder_time = ?",
                         (user_id, reminder_time))
        await db.commit()

async def get_bju_from_local_db(product_name):
    async with aiosqlite.connect("nutrilife.db") as db:
        cursor = await db.execute("SELECT protein, fat, carbs, calories FROM foods WHERE name LIKE ? LIMIT 1",
                                  (f"%{product_name}%",))
        result = await cursor.fetchone()
        if result:
            return {"b": result[0], "j": result[1], "u": result[2], "kcal": result[3]}
        return None

async def insert_test_foods():
    test_data = [
        ("яблоко", 0.4, 0.4, 9.8, 47),
        ("банан", 1.5, 0.2, 21.8, 95),
        ("курица", 23.1, 1.9, 0, 110)
    ]
    async with aiosqlite.connect("nutrilife.db") as db:
        for data in test_data:
            await db.execute("INSERT OR IGNORE INTO foods (name, protein, fat, carbs, calories) VALUES (?, ?, ?, ?, ?)", data)
        await db.commit()
    print("Тестовые данные о продуктах добавлены.")

async def save_log_to_db(log_level, message, user_id=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect("nutrilife.db") as db:
        await db.execute("INSERT INTO logs (log_level, message, user_id, timestamp) VALUES (?, ?, ?, ?)",
                         (log_level, message, user_id, timestamp))
        await db.commit()

async def get_all_logs(limit=50):
    async with aiosqlite.connect("nutrilife.db") as db:
        cursor = await db.execute("SELECT id, log_level, message, user_id, timestamp FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        logs = await cursor.fetchall()
        return logs

async def get_all_reminders():
    async with aiosqlite.connect("nutrilife.db") as db:
        cursor = await db.execute("SELECT user_id, reminder_text, reminder_time, is_sent FROM reminders ORDER BY reminder_time")
        reminders = await cursor.fetchall()
        return reminders

async def get_all_contacts():
    async with aiosqlite.connect("nutrilife.db") as db:
        cursor = await db.execute("SELECT user_id, name, contact_info, timestamp FROM contacts ORDER BY timestamp DESC")
        contacts = await cursor.fetchall()
        return contacts