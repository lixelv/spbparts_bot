import os
from dotenv import load_dotenv
from avito import Avito

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_ID = os.getenv("USER_ID")
API_URL = os.getenv("API_URL")
SLEEP_SEC = int(os.getenv("SLEEP_SEC"))

prepared_texts = [
    """Здравствуйте!
Спасибо за ваше сообщение. Для консультации по вопросам ремонта напишите в наш Telegram-бот:""",
    "@europromsupport_bot.",
]

avito = Avito(CLIENT_ID, CLIENT_SECRET, USER_ID)
