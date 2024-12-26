import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import TELEGRAM_BOT_TOKEN
from utils import get_answer_async, client

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

context = {}


@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply(
        "Привет!\nЯ ваш бот!\nРаботаю на ЕвроПром."
    )


@dp.message(Command("clear"))
async def clear_context(message: Message):
    if context.get(message.chat.id) is not None:
        del context[message.chat.id]

    await message.reply("Контекст очищен.")


@dp.message()
async def echo(message: Message):
    if context.get(message.chat.id) is None:
        context[message.chat.id] = client.beta.threads.create()

    response = await get_answer_async(message.text, context[message.chat.id])
    await message.reply(response, parse_mode="Markdown")


if __name__ == "__main__":
    dp.run_polling(bot)
