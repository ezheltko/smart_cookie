# Загрузка текстов из texts.json

import json
import os


def load_texts() -> dict:
    """Возвращает заготовленные тексты для сообщений пользователю """
    # Возвращает путь к папке со скриптом
    # __file__ — это встроенная переменная Python, которая содержит путь к исполняемому файлу модуля
    # os.path.abspath(...) — функция из стандартной библиотеки, которая принимает любой путь и превращает
    # его в абсолютный нормализованный путь, отталкиваясь от текущей рабочей директории (os.getcwd()),
    # если передан относительный путь.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, "texts.json")

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


# Загружаем один раз при старте бота
texts = load_texts()
