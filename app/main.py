import logging
import json

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType
import re


from config import TELEGRAM_BOT_TOKEN, DATABASE_CONFIG, LOADING_STICKER_ID
from utils import get_answer_async, client
from keyboards import keyboard
from middlewares import setup_middlewares
from database import MySQL

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
sql = MySQL(DATABASE_CONFIG)

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

    reply = await message.answer_sticker(
        LOADING_STICKER_ID,
        reply_markup=keyboard,
    )

    response = await get_answer_async(text, thread_id, metadata)
    set_phone_regex = r"SET_PHONE_NUMBER:\s*(\+?\d+)"
    phone_number = ([None] or re.findall(set_phone_regex, response))[0]
    response = re.sub(set_phone_regex, "", response)

    if phone_number is not None:
        await sql.set_phone_number(message.from_user.id, phone_number)

    await reply.delete()
    return await message.reply(response, parse_mode="Markdown", reply_markup=keyboard)


@dp.message()
async def other_type(message: Message):
    return await message.reply(
        "Я понимаю только текстовые сообщения.", reply_markup=keyboard
    )


if __name__ == "__main__":
    dp.run_polling(bot)
