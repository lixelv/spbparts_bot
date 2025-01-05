import logging
import json

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType, FSInputFile

from config import TELEGRAM_BOT_TOKEN, LOADING_STICKER_ID, sql
from utils import get_answer_async
from functions import client
from keyboards import keyboard
from middlewares import setup_middlewares

# Configure logging
logging.basicConfig(level=logging.INFO)
logs_path = "/logs/telegram-bot.txt"
file_handler = logging.FileHandler(logs_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

setup_middlewares(dp, sql)


@dp.message(Command("start"))
async def start(message: Message, user):
    return await message.reply(
        "Привет!\nЯ ваш бот!\nРаботаю на ЕвроПром. \nЗадавайте вопросы.",
        reply_markup=keyboard,
    )


# user[3] is chatgpt_token
@dp.message(Command("clear"))
async def clear(message: Message, user):
    thread_id = user["chatgpt_thread_id"]

    if thread_id is not None:
        await sql.set_chatgpt_thread_id(message.from_user.id, None)

    return await message.reply(
        "Контекст очищен.",
        reply_markup=keyboard,
    )


@dp.message(Command("logs"))
async def logs(message: Message):
    return await message.reply_document(
        FSInputFile(logs_path, filename="logs.txt"), reply_markup=keyboard
    )


@dp.message(F.content_type == ContentType.TEXT)
async def chatgpt_reply(message: Message, user, text=None):
    metadata = json.loads(message.from_user.model_dump_json())
    metadata = {
        i: str(metadata[i])
        for i in metadata
        if i in ("id", "username", "first_name", "last_name", "language_code")
    }
    metadata.update(
        {"phone_number": user.get("phone_number")} if user.get("phone_number") else {}
    )

    text = text or message.text
    thread_id = user["chatgpt_thread_id"]

    if thread_id is None:
        thread_id = client.beta.threads.create(metadata=metadata).id
        await sql.set_chatgpt_thread_id(message.from_user.id, thread_id)

    loading = await message.answer_sticker(
        LOADING_STICKER_ID,
        reply_markup=keyboard,
    )

    try:
        response = await get_answer_async(text, thread_id, metadata)
    except Exception:
        thread_id = client.beta.threads.create(metadata=metadata).id
        await sql.set_chatgpt_thread_id(message.from_user.id, thread_id)
        response = await get_answer_async(text, thread_id, metadata)

    await loading.delete()
    return await message.reply(response, reply_markup=keyboard)


@dp.message()
async def other_type(message: Message):
    return await message.reply(
        "Я понимаю только текстовые сообщения.", reply_markup=keyboard
    )


if __name__ == "__main__":
    dp.run_polling(bot)
