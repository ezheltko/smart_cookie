# ТОЧКА ВХОДА. Запуск бота, инициализация БД, подключение роутеров.

import asyncio
from aiogram import Bot, Dispatcher
from handlers.commands import router as command_router
from handlers.words import router as words_router
from database import init_db
from environs import Env
from aiogram.types import BotCommand

env = Env()
env.read_env()

bot = Bot(token=env('bot_token'))

dp = Dispatcher()
# Подключение роутеров
dp.include_router(command_router)
dp.include_router(words_router)

async def set_bot_commands(bot: Bot):
    """Устанавливает меню команд для бота."""
    commands = [
        BotCommand(command="start", description="👋 Запустить бота / Главное меню"),
        BotCommand(command="help", description="📖 Справка по командам"),
        BotCommand(command="mywords", description="📚 Мой словарь (просмотр и удаление)"),
        BotCommand(command="train", description="🧠 Тренировка (повторение слов)"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Инициализация БД до запуска бота
    await init_db()
    # Устанавливаем меню команд ПЕРЕД запуском polling
    await set_bot_commands(bot)

    print("🚀 Бот запущен! База готова.")
    # Запуск асинхронного polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
