import aiosqlite

from aiosqlite import Row
from typing import Iterable, Optional, List


class SQLite:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection: Optional[aiosqlite.Connection] = None
        self.cursor: Optional[aiosqlite.Cursor] = None

    async def connect(self) -> None:
        self.connection = await aiosqlite.connect(self.db_name)
        self.cursor = await self.connection.cursor()
        await self.create_tables()

    async def create_tables(self):
        # Create tables one by one
        await self.do("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, -- Telegram ID пользователя или уникальный ID
                username TEXT, -- Username пользователя
                full_name TEXT, -- Полное имя пользователя
                chatgpt_thread_id TEXT, -- ID thread-а с ChatGPT API
                manager_level INTEGER DEFAULT 0, -- Уровень менеджера, по умолчанию 0 (не менеджер)
                spec TEXT, -- Специализация менеджера
                active_user INTEGER DEFAULT NULL, -- ID активного пользователя для менеджера
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, -- Время добавления пользователя в базу данных

                FOREIGN KEY (active_user) REFERENCES users (id) ON DELETE SET NULL
            )
        """)

        await self.do("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор сообщения
                user_id INTEGER, -- ID пользователя, к которому относится сообщение
                message TEXT NOT NULL, -- Текст сообщения
                sender INTEGER NOT NULL, -- Кто отправил сообщение: 0 - пользователь, 1 - чатбот, 2 - менеджер
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, -- Время отправки сообщения
                
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

    async def do(self, sql: str, values: tuple = ()) -> None:
        await self.cursor.execute(sql, values)
        await self.connection.commit()

    async def read(
        self, sql: str, values: tuple = (), one: bool = False
    ) -> Iterable[Row]:
        await self.cursor.execute(sql, values)

        if one:
            return await self.cursor.fetchone()
        else:
            return await self.cursor.fetchall()

    async def close(self) -> None:
        await self.cursor.close()
        await self.connection.close()

    async def user_exists(self, user_id: int) -> bool:
        sql = "SELECT * FROM users WHERE id = ?"
        return bool(await self.read(sql, (user_id,), one=True))

    async def add_user(self, user_id: int, username: str, full_name: str) -> None:
        sql = "INSERT INTO users (id, username, full_name) VALUES (?, ?, ?)"
        await self.do(sql, (user_id, username, full_name))

    async def get_user(self, user_id: int) -> Optional[Row]:
        sql = "SELECT * FROM users WHERE id = ?"
        return await self.read(sql, (user_id,), one=True)

    async def set_chatgpt_thread_id(self, user_id: int, thread_id: str) -> None:
        sql = "UPDATE users SET chatgpt_thread_id = ? WHERE id = ?"
        await self.do(sql, (thread_id, user_id))

    async def get_chatgpt_thread_id(self, user_id: int) -> Optional[str]:
        sql = "SELECT chatgpt_thread_id FROM users WHERE id = ?"
        return await self.read(sql, (user_id,), one=True)

    async def set_manager(self, user_id: int, spec: str, manager_level: int) -> None:
        sql = "UPDATE users SET manager_level = ?, spec = ? WHERE id = ?"
        await self.do(sql, (manager_level, spec, user_id))

    async def get_managers(self) -> List[Row]:
        sql = "SELECT * FROM users WHERE manager_level != 0 AND active_user IS NULL ORDER BY manager_level DESC"
        return await self.read(sql)

    # sender: 0 - user, 1 - chatbot, 2 - manager
    async def add_message(self, user_id: int, message_text: str, sender: int) -> None:
        sql = "INSERT INTO messages (user_id, message, sender) VALUES (?, ?, ?)"
        await self.do(sql, (user_id, message_text, sender))
