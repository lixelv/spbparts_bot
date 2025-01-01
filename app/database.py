import aiomysql

from aiomysql import DictCursor
from typing import Optional, List


class MySQL:
    def __init__(self, config: dict):
        self.config = config
        self.connection: Optional[aiomysql.Connection] = None
        self.cursor: Optional[aiomysql.Cursor] = None

    async def connect(self, connect_instant=False) -> None:
        if not self.connection or self.connection.closed or connect_instant:
            self.connection = await aiomysql.connect(
                db=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                host=self.config["url"],
                port=self.config["port"],
            )

    async def create_tables(self):
        # Create tables one by one
        await self.do("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY, -- Telegram ID пользователя или уникальный ID
                username VARCHAR(255), -- Username пользователя
                full_name VARCHAR(255), -- Полное имя пользователя
                phone_number VARCHAR(255), -- Номер телефона пользователя
                chatgpt_thread_id VARCHAR(255), -- ID thread-а с ChatGPT API
                manager_level INT DEFAULT 0, -- Уровень менеджера, по умолчанию 0 (не менеджер)
                spec VARCHAR(255), -- Специализация менеджера
                active_user BIGINT DEFAULT NULL, -- ID активного пользователя для менеджера
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Время добавления пользователя в базу данных
                
                FOREIGN KEY (active_user) REFERENCES users (id) ON DELETE SET NULL
            )
        """)

        await self.do("""
            CREATE TABLE IF NOT EXISTS messages (
                id BIGINT PRIMARY KEY AUTO_INCREMENT, -- Уникальный идентификатор сообщения
                user_id BIGINT, -- ID пользователя, к которому относится сообщение
                message TEXT NOT NULL, -- Текст сообщения
                sender INT NOT NULL, -- Кто отправил сообщение: 0 - пользователь, 1 - чатбот, 2 - менеджер
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Время отправки сообщения
                
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

    async def do(self, sql, values=None):
        await self.connect()
        async with self.connection.cursor(DictCursor) as cursor:
            try:
                await cursor.execute(sql, values)
                await self.connection.commit()
            except aiomysql.OperationalError as e:
                if e.args[0] in (
                    2013,
                    2006,
                ):  # Lost connection to MySQL server during query
                    await self.connect(connect_instant=True)
                    async with self.connection.cursor(DictCursor) as cursor:
                        await cursor.execute(sql, values)
                        await self.connection.commit()
                else:
                    raise

    async def read(self, sql, values=None, one=False):
        await self.connect()
        async with self.connection.cursor(DictCursor) as cursor:
            try:
                await cursor.execute(sql, values)
                result = await cursor.fetchone() if one else await cursor.fetchall()
                return result
            except aiomysql.OperationalError as e:
                if e.args[0] in (
                    2013,
                    2006,
                ):  # Lost connection to MySQL server during query
                    await self.connect(connect_instant=True)
                    async with self.connection.cursor(DictCursor) as cursor:
                        await cursor.execute(sql, values)
                        result = (
                            await cursor.fetchone() if one else await cursor.fetchall()
                        )
                        return result
                else:
                    raise

    async def close(self) -> None:
        self.connection.close()

    async def user_exists(self, user_id: int) -> bool:
        sql = "SELECT * FROM users WHERE id = %s"
        return bool(await self.read(sql, (user_id,), one=True))

    async def add_user(self, user_id: int, username: str, full_name: str) -> None:
        sql = "INSERT INTO users (id, username, full_name) VALUES (%s, %s, %s)"
        await self.do(sql, (user_id, username, full_name))

    async def get_user(self, user_id: int) -> Optional[DictCursor]:
        sql = "SELECT * FROM users WHERE id = %s"
        return await self.read(sql, (user_id,), one=True)

    async def set_chatgpt_thread_id(self, user_id: int, thread_id: str) -> None:
        sql = "UPDATE users SET chatgpt_thread_id = %s WHERE id = %s"
        await self.do(sql, (thread_id, user_id))

    async def get_chatgpt_thread_id(self, user_id: int) -> Optional[str]:
        sql = "SELECT chatgpt_thread_id FROM users WHERE id = %s"
        return await self.read(sql, (user_id,), one=True)

    async def set_phone_number(self, user_id: int, phone_number: str) -> None:
        sql = "UPDATE users SET phone_number = %s WHERE id = %s"
        await self.do(sql, (phone_number, user_id))

    async def set_manager(self, user_id: int, spec: str, manager_level: int) -> None:
        sql = "UPDATE users SET manager_level = %s, spec = %s WHERE id = %s"
        await self.do(sql, (manager_level, spec, user_id))

    async def get_managers(self) -> List[DictCursor]:
        sql = "SELECT * FROM users WHERE manager_level != 0 AND active_user IS NULL ORDER BY manager_level DESC"
        return await self.read(sql)

    # sender: 0 - user, 1 - chatbot, 2 - manager
    async def add_message(self, user_id: int, message_text: str, sender: int) -> None:
        sql = "INSERT INTO messages (user_id, message, sender) VALUES (%s, %s, %s)"
        await self.do(sql, (user_id, message_text, sender))
