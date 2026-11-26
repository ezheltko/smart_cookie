# Хендлеры команд: /start, /help, /mywords, /train

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup

from utils import texts
from database import add_user, get_words, get_translation_by_word, get_random_word, delete_word
from api import get_audio_file
import os

router = Router()


class DeleteWordStates(StatesGroup):
    waiting_for_word = State()


@router.message(Command(commands='start'))
async def start_command(message: Message):
    # 1. Сохраняем юзера в БД (передаем его Telegram ID)
    await add_user(message.from_user.id)
    # 2. Отправляем приветствие
    text = "\n".join(texts["start"])
    await message.answer(text, parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    # Берем текст по ключу "help"
    await message.answer('\n'.join(texts['help']), parse_mode='HTML')


@router.message(Command("mywords"))
async def cmd_mywords(message: Message):
    # 1. Получаем слова из базы
    words = await get_words(message.from_user.id)

    # 2. Если словарь пуст — сообщаем об этом
    if not words:
        await message.answer("📭 Твой словарь пока пуст. Отправь мне слово на английском, чтобы добавить его!")
        return

    # 3. Формируем красивый список
    # Берем первые 20 слов (чтобы сообщение не превысило лимит Telegram в 4096 символов)
    display_words = words[:20]

    response = f"📚 <b>Твой словарь ({len(words)} слов):</b>\n\n"

    for i, (english, russian) in enumerate(display_words, start=1):
        response += f"{i}. <b>{english}</b> — {russian}\n"

    # Если слов больше 20, добавляем приписку
    if len(words) > 20:
        response += f"\n<i>...и еще {len(words) - 20} слов. (Пока показаны первые 20).</i>"

    # 4. Отправляем результат
    await message.answer(response, parse_mode="HTML")

    # Создаем кнопку "Удалить слово"
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Удалить слово", callback_data="delete_word_prompt")

    await message.answer(response, parse_mode="HTML", reply_markup=builder.as_markup())


@router.message(Command("train"))
async def cmd_train(message: Message):
    # 1. Достаем случайное слово
    word_data = await get_random_word(message.from_user.id)

    if not word_data:
        await message.answer("📭 Твой словарь пуст. Добавь слова, чтобы начать тренировку!")
        return

    english, russian = word_data

    # 2. Создаем кнопку
    builder = InlineKeyboardBuilder()

    # ВАЖНО: передаем только само слово, без перевода.
    # Префикс "show_" нужен, чтобы отличить эту кнопку от других в будущем.
    builder.button(
        text="👀 Показать перевод",
        callback_data=f"show_{english}"
    )

    # 3. Отправляем сообщение
    await message.answer(
        f"🤔 Вспомни перевод:\n\n🇬🇧 <b>{english}</b>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data and c.data.startswith('show_'))
async def process_show_translation(callback: CallbackQuery):
    # 1. СРАЗУ отвечаем Telegram, чтобы убрать часики
    await callback.answer("Генерирую озвучку...")

    english_word = callback.data.replace('show_', '')
    translation = await get_translation_by_word(callback.from_user.id, english_word)

    if not translation:
        await callback.message.answer("Слово не найдено 😔")
        return

    # 2. Редактируем сообщение (показываем перевод)
    new_text = f"✅ <b>{english_word}</b>\n🇷🇺 {translation}"
    await callback.message.edit_text(new_text, parse_mode="HTML")

    # 3. Пытаемся сделать озвучку (в блоке try)
    try:
        audio_path = await get_audio_file(english_word)
        if audio_path and os.path.exists(audio_path):
            audio = FSInputFile(audio_path)
            await callback.message.answer_voice(voice=audio, caption=f"Озвучка: {english_word}")
            os.remove(audio_path)
    except Exception as e:
        # Если озвучка не удалась — просто логируем, бот не падает
        print(f"Ошибка озвучки: {e}")


@router.callback_query(F.data == "delete_word_prompt")
async def process_delete_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✍️ Введи английское слово, которое хочешь удалить:")
    # Устанавливаем состояние ожидания
    await state.set_state(DeleteWordStates.waiting_for_word)
    await callback.answer()


@router.message(DeleteWordStates.waiting_for_word)
async def process_delete_word(message: Message, state: FSMContext):
    word = message.text.strip().lower()

    # Пытаемся удалить
    is_deleted = await delete_word(message.from_user.id, word)

    if is_deleted:
        await message.answer(f"✅ Слово <b>{word}</b> удалено из словаря.", parse_mode="HTML")
    else:
        await message.answer(f"❌ Слово <b>{word}</b> не найдено в твоем словаре.", parse_mode="HTML")

    # Сбрасываем состояние (выходим из режима удаления)
    await state.clear()


@router.message(Command("delete"))
# функция удаления слов
async def cmd_delete(message: Message, state: FSMContext):
    # Проверяем, есть ли вообще слова в словаре
    words = await get_words(message.from_user.id)
    if not words:
        await message.answer("📭 Твой словарь пуст. Нечего удалять.")
        return

    await message.answer("✍️ Введи английское слово, которое хочешь удалить:")
    # Устанавливаем то же состояние, что и для кнопки в /mywords
    await state.set_state(DeleteWordStates.waiting_for_word)
