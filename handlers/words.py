# Хендлер для добавления слов (ловит любой текст)

from aiogram import Router, types, F
from aiogram.types import FSInputFile
from database import add_word
from api import get_translation, get_audio_file
import os

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def process_word(message: types.Message):
    word = message.text.strip().lower()

    if not word.isalpha():
        await message.answer("⚠️ Отправь только одно английское слово.")
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    # 1. Получаем перевод
    translation = await get_translation(word)
    if not translation:
        await message.answer(f"❌ Не удалось найти перевод для <b>{word}</b>.", parse_mode="HTML")
        return

    # 2. Сохраняем в базу
    is_saved = await add_word(message.from_user.id, word, translation, audio_url=None)

    if not is_saved:
        await message.answer(f"⚠️ Слово <b>{word}</b> уже есть в словаре!", parse_mode="HTML")
        return

    # 3. Отправляем карточку
    await message.answer(f"✅ <b>Добавлено!</b>\n\n🇬🇧 <b>{word}</b>\n🇷🇺 {translation}", parse_mode="HTML")

    # 4. Генерируем и отправляем озвучку
    audio_path = await get_audio_file(word)
    if audio_path and os.path.exists(audio_path):
        try:
            # Отправляем локальный файл
            audio = FSInputFile(audio_path)
            await message.answer_voice(voice=audio, caption=f"Озвучка: {word}")
        except Exception as e:
            print(f"Не удалось отправить аудио: {e}")
        finally:
            # 5. Обязательно удаляем файл после отправки, чтобы не копить мусор
            os.remove(audio_path)
    else:
        await message.answer("🔇 Озвучка временно недоступна.")