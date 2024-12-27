import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import TELEGRAM_BOT_TOKEN
from utils import get_answer_async, client
from keyboards import keyboard, texts

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

context = {}


@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply(
        "Привет!\nЯ ваш бот!\nРаботаю на ЕвроПром. \nЗадавайте вопросы."
    )


@dp.message(Command("clear"))
async def clear_context(message: Message):
    if context.get(message.chat.id) is not None:
        del context[message.chat.id]

    await message.reply(
        "Контекст очищен.",
        reply_markup=keyboard,
    )


@dp.message()
async def echo(message: Message):
    if context.get(message.chat.id) is None:
        context[message.chat.id] = client.beta.threads.create()

    reply = await message.reply(
        "Подождите, идет обработка запроса...",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

    response = await get_answer_async(
        texts.get(message.text) or message.text, context[message.chat.id]
    )

    await reply.delete()
    await message.reply(response, parse_mode="Markdown", reply_markup=keyboard)


if __name__ == "__main__":
    dp.run_polling(bot)
