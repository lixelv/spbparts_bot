from aiogram.types import Message, ContentType
from typing import Any, Dict, Callable, Awaitable
from database import PostgresDB
from aiogram import BaseMiddleware, Dispatcher
from abc import abstractmethod

from keyboards import texts


class HandleKeyboardMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if event.text in texts:
            data["text"] = texts[event.text]

        return await handler(event, data)


class DatabaseRelatedMiddleware(BaseMiddleware):
    def __init__(self, db: PostgresDB):
        super().__init__()
        self.db = db

    @abstractmethod
    async def __call__(self, handler, event, data):
        pass


class UserCheckMiddleware(DatabaseRelatedMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = await self.db.get_or_create_user(
            event.from_user.id, event.from_user.username, event.from_user.full_name
        )

        data["user"] = user

        return await handler(event, data)


class AddMessagesMiddleware(DatabaseRelatedMiddleware):
    async def __call__(self, handler, event: Message, data):
        if event.content_type == ContentType.TEXT:
            await self.db.add_message(event.from_user.id, event.text, 0)

        result = await handler(event, data)

        if event.content_type == ContentType.TEXT:
            await self.db.add_message(
                event.from_user.id,
                result.text
                if result.content_type == ContentType.TEXT
                else "Handler returned non-Message result",
                1,
            )

        return result


def setup_middlewares(dp: Dispatcher, user_db):
    dp.message.middleware(HandleKeyboardMiddleware())
    dp.message.middleware(UserCheckMiddleware(user_db))
    dp.message.middleware(AddMessagesMiddleware(user_db))
