import aiosqlite
from datetime import datetime, timedelta
from config.config import DATABASE_FILE


async def init_db():
    async with aiosqlite.connect(DATABASE_FILE) as db:
        # Таблица для контактов (заявки на обратный звонок)
        await db.execute(
            """CREATE TABLE IF NOT EXISTS contacts (
            user_id INTEGER,
            name TEXT,
            contact_info TEXT,
            timestamp TEXT
        )"""
        )
        # Таблица для напоминаний
        await db.execute(
            """CREATE TABLE IF NOT EXISTS reminders (
            user_id INTEGER,
            reminder_text TEXT,
            reminder_time TEXT,
            is_sent INTEGER DEFAULT 0
        )"""
        )
        # Таблица для данных о продуктах (БЖУ) с добавленным полем weight
        await db.execute(
            """CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            protein REAL DEFAULT 0.0,
            fat REAL DEFAULT 0.0,
            carbs REAL DEFAULT 0.0,
            calories REAL DEFAULT 0.0,
            weight REAL DEFAULT 100.0
        )"""
        )
        # Таблица для логов
        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_level TEXT NOT NULL,
            message TEXT NOT NULL,
            user_id INTEGER,
            timestamp TEXT NOT NULL
        )"""
        )
        await db.commit()
    print("База данных инициализирована.")


async def save_contact(user_id, name, contact_info):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "INSERT INTO contacts (user_id, name, contact_info, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, name, contact_info, timestamp),
        )
        await db.commit()


async def save_reminder(user_id, reminder_text, reminder_time):
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "INSERT INTO reminders (user_id, reminder_text, reminder_time, is_sent) VALUES (?, ?, ?, 0)",
            (user_id, reminder_text, reminder_time),
        )
        await db.commit()


async def get_due_reminders():
    current_time = datetime.now()
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            "SELECT user_id, reminder_text, reminder_time FROM reminders WHERE is_sent = 0"
        )
        reminders = await cursor.fetchall()
        due_reminders = []
        print(f"Текущее время: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Все напоминания из базы (неотправленные): {reminders}")
        for reminder in reminders:
            user_id, reminder_text, reminder_time_str = reminder
            try:
                # Пробуем разные форматы времени
                reminder_time = None
                possible_formats = [
                    "%Y-%m-%d %H:%M",  # 2025-05-25 17:30
                    "%Y-%m-%d %H:%M:%S",  # 2025-05-25 17:30:00
                    "%d.%m.%Y %H:%M",  # 25.05.2025 17:30
                    "%d.%m.%Y %H:%M:%S",  # 25.05.2025 17:30:00
                ]
                for date_format in possible_formats:
                    try:
                        reminder_time = datetime.strptime(
                            reminder_time_str, date_format
                        )
                        break
                    except ValueError:
                        continue
                if reminder_time and reminder_time <= current_time:
                    due_reminders.append(reminder)
                    print(
                        f"Напоминание добавлено в очередь на отправку: {reminder_text} на {reminder_time_str}"
                    )
                elif reminder_time:
                    print(
                        f"Напоминание еще не наступило: {reminder_text} на {reminder_time_str}"
                    )
                else:
                    print(
                        f"Не удалось распознать формат времени для напоминания: {reminder_text} на {reminder_time_str}"
                    )
            except Exception as e:
                print(
                    f"Ошибка при обработке напоминания {reminder_text} на {reminder_time_str}: {str(e)}"
                )
        print(f"Найденные напоминания для отправки: {due_reminders}")
        return due_reminders


async def mark_reminder_sent(user_id, reminder_time):
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "UPDATE reminders SET is_sent = 1 WHERE user_id = ? AND reminder_time = ?",
            (user_id, reminder_time),
        )
        await db.commit()


async def get_bju_from_local_db(product_name):
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            "SELECT name, protein, fat, carbs, calories, weight FROM foods WHERE name LIKE ? LIMIT 5",
            (f"%{product_name}%",),
        )
        results = await cursor.fetchall()
        if results:
            # Возвращаем список продуктов с их характеристиками
            return [
                {
                    "name": result[0],
                    "b": result[1],
                    "j": result[2],
                    "u": result[3],
                    "kcal": result[4],
                    "weight": result[5],
                }
                for result in results
            ]
        return None


async def save_log_to_db(log_level, message, user_id=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "INSERT INTO logs (log_level, message, user_id, timestamp) VALUES (?, ?, ?, ?)",
            (log_level, message, user_id, timestamp),
        )
        await db.commit()


async def get_all_logs(limit=50):
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            "SELECT id, log_level, message, user_id, timestamp FROM logs ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        logs = await cursor.fetchall()
        return logs


async def get_all_reminders():
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            "SELECT user_id, reminder_text, reminder_time, is_sent FROM reminders ORDER BY reminder_time"
        )
        reminders = await cursor.fetchall()
        return reminders


async def get_all_contacts():
    async with aiosqlite.connect(DATABASE_FILE) as db:
        cursor = await db.execute(
            "SELECT user_id, name, contact_info, timestamp FROM contacts ORDER BY timestamp DESC"
        )
        contacts = await cursor.fetchall()
        return contacts


async def clean_old_reminders(days=7):
    """Удаление старых напоминаний, отправленных более 'days' дней назад."""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        threshold_time = (datetime.now() - timedelta(days=days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        cursor = await db.execute(
            "DELETE FROM reminders WHERE reminder_time < ? AND is_sent = 1",
            (threshold_time,),
        )
        deleted_count = cursor.rowcount
        await db.commit()
        return deleted_count


def recalculate_bju(data, input_weight):
    base_weight = data["weight"]
    multiplier = input_weight / base_weight if base_weight > 0 else 1
    return {
        "name": data["name"],
        "b": round(data["b"] * multiplier, 1),
        "j": round(data["j"] * multiplier, 1),
        "u": round(data["u"] * multiplier, 1),
        "kcal": round(data["kcal"] * multiplier, 1),
        "weight": input_weight,
    }
