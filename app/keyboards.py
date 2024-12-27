from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Iterable


def box(iteable: Iterable, pack_size: int):
    it = iter(iteable)

    while True:
        try:
            box = []

            for _ in range(pack_size):
                box.append(next(it))

            yield box
        except StopIteration:
            if box:
                yield box

            break


texts = {
    "👨‍💼 Связь с менеджером": "...",
    "🛠 Диагностика форсунок": "...",
    "🔧 Ремонт форсунок": "...",
    "💰 Купить форсунки": "...",
    "📦 Мои форсунки": "...",
    "📜 Гарантия и условия": "...",
    "📍 Контакты и расположение": "...",
    "❓ FAQ (Частые вопросы)": "...",
    "📞 Обратный звонок/Задать вопрос": "...",
}


keyboard = ReplyKeyboardMarkup(
    keyboard=box([KeyboardButton(text=row) for row in texts.keys()], 2),
    resize_keyboard=True,
)
