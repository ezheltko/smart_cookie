# Работа с SQLite

import aiosqlite
import os

# Путь к базе данных
# __file__ — это встроенная переменная Python, которая содержит путь к исполняемому файлу модуля
base_dir = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.join(base_dir, 'bot.db')


async def init_db():
    """Создает таблицы, если их еще нет."""
    # Создаем соединение с файлом базы данных
    async with aiosqlite.connect(base_path) as db:
        # Включаем поддержку внешних ключей (важно для SQLite)
        await db.execute("PRAGMA foreign_keys = ON;")

        # 1. Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Таблица слов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                english TEXT NOT NULL,
                russian TEXT,
                transcription TEXT,
                audio_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(tg_id) ON DELETE CASCADE
            )
        """)

        # 3. Уникальный индекс (защита от дублей у одного пользователя)
        # Создаем уникальный указатель, если его ещё нет с индексом idx_user_word для таблицы words
        # на основе колонок user_id, english
        # База автоматически вызывает индекс, когда выполняется INSERT

        await db.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_user_word 
            ON words(user_id, english)
        """)

        await db.commit()
        print("✅ База данных инициализирована.")


async def add_user(tg_id: int):
    """Добавляет нового пользователя в базу, если его там еще нет."""
    async with aiosqlite.connect(base_path) as db:
        # Включаем проверку связей
        await db.execute("PRAGMA foreign_keys = ON;")

        # INSERT OR IGNORE: "вставь, но если такой ID уже есть — ничего не делай"
        await db.execute(
            "INSERT OR IGNORE INTO users (tg_id) VALUES (?)",
            (tg_id,)
        )
        await db.commit()


async def add_word(user_id: int, english: str, russian: str, audio_url: str = None):
    """Сохраняет слово в словарь. Возвращает True, если добавлено, False — если дубль."""
    async with aiosqlite.connect(base_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        try:
            await db.execute(
                "INSERT INTO words (user_id, english, russian, audio_url) VALUES (?, ?, ?, ?)",
                (user_id, english, russian, audio_url)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False  # Слово уже есть (сработал уникальный индекс)


async def get_words(user_id: int) -> list:
    """Возвращает список всех слов пользователя."""
    async with aiosqlite.connect(base_path) as db:
        # Создаем курсор и выполняем запрос
        cursor = await db.execute(
            "SELECT english, russian FROM words WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,)
        )
        # fetchall() возвращает список кортежей: [('apple', 'яблоко'), ('cat', 'кот')]
        rows = await cursor.fetchall()
        await cursor.close()
        return rows


async def get_random_word(user_id: int):
    """Возвращает одно случайное слово пользователя."""
    async with aiosqlite.connect(base_path) as db:
        # ORDER BY RANDOM() — заставляет SQLite выбрать случайную строку
        cursor = await db.execute(
            "SELECT english, russian FROM words WHERE user_id = ? ORDER BY RANDOM() LIMIT 1",
            (user_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row  # Вернет кортеж ('apple', 'яблоко') или None, если словарь пуст


async def get_translation_by_word(user_id: int, english: str) -> str | None:
    """Ищет перевод конкретного слова для пользователя."""
    async with aiosqlite.connect(base_path) as db:
        cursor = await db.execute(
            "SELECT russian FROM words WHERE user_id = ? AND english = ?",
            (user_id, english)
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row[0] if row else None


async def delete_word(user_id: int, english: str) -> bool:
    """Удаляет слово. Возвращает True, если удалено, False — если не найдено."""
    async with aiosqlite.connect(base_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")

        # Проверяем, существует ли слово у этого пользователя
        cursor = await db.execute(
            "SELECT id FROM words WHERE user_id = ? AND english = ?",
            (user_id, english)
        )
        row = await cursor.fetchone()
        await cursor.close()

        if not row:
            return False  # Слово не найдено

        # Удаляем
        await db.execute(
            "DELETE FROM words WHERE user_id = ? AND english = ?",
            (user_id, english)
        )
        await db.commit()
        return True
