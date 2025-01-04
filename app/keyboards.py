from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Iterable
from config import texts


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


keyboard = ReplyKeyboardMarkup(
    keyboard=box([KeyboardButton(text=row) for row in texts.keys()], 2),
    resize_keyboard=True,
)
