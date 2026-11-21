import uuid

import edge_tts
from openai import AsyncOpenAI

# ==========================================
# НАСТРОЙКИ AIAI.BY
# ==========================================

AIAI_API_KEY = "sk-aiai-9kQ9fw4BcaLfzBmJwoKXxSPYcuMFSbWZV2r6_biPdiE"

# Создаем клиент OpenAI, но направляем его на сервера aiai.by
client = AsyncOpenAI(
    api_key=AIAI_API_KEY,
    base_url="https://api.aiai.by/v1"
)


# ==========================================
# 1. ФУНКЦИЯ ПЕРЕВОДА (DeepSeek V4 Flash)
# ==========================================
async def get_translation(word: str) -> str | None:
    """Переводит слово через DeepSeek V4 Flash на aiai.by."""
    try:
        response = await client.chat.completions.create(
            model="deepseek-v4-flash",  # Самая быстрая и дешевая модель
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — профессиональный переводчик. Переведи английское слово на русский язык. "
                        "Верни ТОЛЬКО перевод, без пояснений, без кавычек, без точек. "
                        "Если слово многозначное, верни 1-2 самых частых значения через точку с запятой. "
                        "Если слова не существует или это бессмыслица, верни строго 'НЕ НАЙДЕНО'."
                    )
                },
                {
                    "role": "user",
                    "content": word
                }
            ],
            temperature=0.1,  # Низкая температура = точный и предсказуемый ответ
            max_tokens=100  # Ограничиваем ответ, чтобы не тратить лишние токены
        )

        # 1. Безопасно извлекаем текст (если content == None, вернется "")
        content = response.choices[0].message.content
        translated = (content or "").strip()

        # Логируем, сколько токенов мы потратили (полезно для контроля бюджета)
        usage = response.usage
        print(f"🔤 Слово: {word} | Токены: вход={usage.prompt_tokens}, выход={usage.completion_tokens}")

        # Если модель не нашла слово
        if "НЕ НАЙДЕНО" in translated.upper():
            return None

        # Убираем возможные кавычки, которые модель может добавить по привычке
        translated = translated.strip('"').strip("'").strip()

        return translated

    except Exception as e:
        print(f"❌ Ошибка DeepSeek (aiai.by): {e}")
        return None


# ==========================================
# 2. ФУНКЦИЯ ОЗВУЧКИ (Edge TTS)
# ==========================================
async def get_audio_file(word: str) -> str | None:
    """Генерирует MP3-файл с озвучкой слова через Edge TTS."""
    # Выбираем голос (en-US-AriaNeural - женский американский)
    voice = "en-US-AriaNeural"

    # Создаем уникальное имя файла, чтобы они не перезаписывали друг друга
    filename = f"audio_{uuid.uuid4().hex}.mp3"

    try:
        # Генерируем аудио и сохраняем в файл
        communicate = edge_tts.Communicate(word, voice)
        await communicate.save(filename)
        return filename
    except Exception as e:
        print(f"❌ Ошибка Edge TTS: {e}")
        return None
