from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
DATABASE_CONFIG = {
    "url": os.getenv("MYSQL_URL"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_LOGIN"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}
