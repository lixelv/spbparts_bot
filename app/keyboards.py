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
    "ℹ️ Подробнее": "Расскажи об этом подробнее.",
    "👨‍💼 Связь с менеджером": "Как связаться с менеджером? Уточните, пожалуйста, ваш запрос.",
    "🛠 Диагностика форсунок": "Какие форсунки ремонтируете? Сколько времени занимает диагностика?",
    "🔧 Ремонт форсунок": "Какие форсунки ремонтируете? Сколько по времени займёт ремонт? Какие гарантии предоставляете?",
    "💰 Купить форсунки": "Совместимость: Подойдут ли форсунки для моей модели двигателя? Есть ли в наличии, и какая цена?",
    "📦 Мои форсунки": "Могу ли я проверить статус ремонта или заказа форсунок?",
    "📜 Гарантия и условия": "Какая гарантия предоставляется на форсунки и услуги? Какие условия работы?",
    "📍 Контакты и расположение": "Где вы находитесь? Есть ли филиалы или пункты выдачи?",
    "❓ FAQ (Частые вопросы)": "Часто задаваемые вопросы по ремонту, диагностике и покупке форсунок.",
    "📞 Обратный звонок/Задать вопрос": "Какой ваш вопрос? Мы свяжемся с вами в ближайшее время.",
}


keyboard = ReplyKeyboardMarkup(
    keyboard=box([KeyboardButton(text=row) for row in texts.keys()], 2),
    resize_keyboard=True,
)
