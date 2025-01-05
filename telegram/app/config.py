import os

from openai_tools_decorator import OpenAIT
from dotenv import load_dotenv
from database import PostgresDB

# Load .env file
load_dotenv()

LOADING_STICKER_ID = (
    "CAACAgIAAxkBAAPaZ3K_UpoKOS2DU0xBfRF0b6v2j-oAArQjAAKYSylI3rm-zSpb5Nk2BA"
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
DATABASE_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT")),
    "user": os.getenv("POSTGRES_LOGIN"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DATABASE"),
}

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

sql = PostgresDB(DATABASE_CONFIG)
client = OpenAIT(
    api_key=OPENAI_API_KEY,
)
