import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from config import TELEGRAM_BOT_TOKEN
from utils import get_answer_async, client
from keyboards import keyboard, texts
from middlewares import setup_middlewares
from database import SQLite

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
sql = SQLite("db.sqlite")

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
    thread_id = user[3]

    if thread_id is not None:
        await sql.set_chatgpt_thread_id(message.from_user.id, None)

    return await message.reply(
        "Контекст очищен.",
        reply_markup=keyboard,
    )


@dp.message(Command("get_sqlite_database"))
async def get_sqlite_database(message: Message):
    input_file = FSInputFile("db.sqlite")
    return await message.reply_document(document=input_file, reply_markup=keyboard)


@dp.message()
async def chatgpt_reply(message: Message, user):
    thread_id = user[3]

    if thread_id is None:
        thread_id = client.beta.threads.create().id
        await sql.set_chatgpt_thread_id(message.from_user.id, thread_id)

    reply = await message.reply(
        "Подождите, идет обработка запроса...",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

    response = await get_answer_async(
        texts.get(message.text) or message.text,
        thread_id,
        {
            "name": message.from_user.full_name,
            "username": message.from_user.username,
            "id": message.from_user.id,
        },
    )

    await reply.delete()
    return await message.reply(response, parse_mode="Markdown", reply_markup=keyboard)


if __name__ == "__main__":
    asyncio.run(sql.connect())
    dp.run_polling(bot)
