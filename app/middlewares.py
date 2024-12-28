from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import Message

from abc import abstractmethod
from database import SQLite
from typing import Any, Dict, Callable, Awaitable


class DatabaseRelatedMiddleware(BaseMiddleware):
    def __init__(self, db: SQLite):
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
        user = await self.db.get_user(event.from_user.id)

        if user is None:
            await self.db.add_user(
                event.from_user.id, event.from_user.username, event.from_user.full_name
            )

        data["user"] = user

        return await handler(event, data)


class AddMessagesMiddleware(DatabaseRelatedMiddleware):
    async def __call__(self, handler, event: Message, data):
        if isinstance(event, Message):
            await self.db.add_message(event.from_user.id, event.text, 0)

        result = await handler(event, data)

        if isinstance(event, Message):
            await self.db.add_message(
                event.from_user.id,
                result.text if result.text else "Handler returned non-Message result",
                1,
            )

        return result


def setup_middlewares(dp: Dispatcher, user_db):
    dp.message.middleware(UserCheckMiddleware(user_db))
    dp.message.middleware(AddMessagesMiddleware(user_db))
