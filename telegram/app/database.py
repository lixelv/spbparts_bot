import asyncpg
import json
from typing import Optional, List


class PostgresDB:
    def __init__(self, config: dict):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        if not self.pool:
            self.pool = await asyncpg.create_pool(**self.config)

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()

    def __del__(self):
        """
        Вызывается при удалении объекта. Закрывает пул соединений с базой данных.
        """
        try:
            import asyncio

            loop = asyncio.get_event_loop()

            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except Exception as e:
            print(f"Ошибка при закрытии пула соединений в __del__: {e}")

    async def create_tables(self) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id BIGINT PRIMARY KEY,
                        username VARCHAR(255),
                        full_name VARCHAR(255),
                        phone_number VARCHAR(255),
                        chatgpt_thread_id VARCHAR(255),
                        manager_level INT DEFAULT 0,
                        spec VARCHAR(255),
                        active_user BIGINT,
                        extra_info JSONB DEFAULT '{}',
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                await conn.execute(
                    """
                    DO $$ BEGIN
                        ALTER TABLE users
                        ADD CONSTRAINT fk_active_user
                        FOREIGN KEY (active_user) REFERENCES users (id) ON DELETE SET NULL;
                    EXCEPTION WHEN duplicate_object THEN NULL; END $$;
                    """
                )
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id BIGSERIAL PRIMARY KEY,
                        user_id BIGINT,
                        message TEXT NOT NULL,
                        sender INT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_user
                            FOREIGN KEY(user_id)
                            REFERENCES users(id)
                            ON DELETE CASCADE
                    )
                    """
                )

    async def do(self, sql: str, values=None) -> None:
        await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                if values:
                    await conn.execute(sql, *values)
                else:
                    await conn.execute(sql)

    async def read(self, sql: str, values=None, one=False):
        await self.connect()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *values) if values else await conn.fetch(sql)
            if one:
                return dict(rows[0]) if rows else None
            return [dict(r) for r in rows]

    async def get_or_create_user(
        self, user_id: int, username: str, full_name: str
    ) -> dict:
        sql = """
            WITH upsert AS (
                INSERT INTO users (id, username, full_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO NOTHING
                RETURNING *
            )
            SELECT * FROM upsert
            UNION
            SELECT * FROM users WHERE id=$1
            LIMIT 1
        """
        return await self.read(sql, (user_id, username, full_name), one=True)

    async def user_exists(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM users WHERE id=$1"
        return bool(await self.read(sql, (user_id,), one=True))

    async def add_user(self, user_id: int, username: str, full_name: str) -> None:
        sql = "INSERT INTO users (id, username, full_name) VALUES ($1, $2, $3)"
        await self.do(sql, (user_id, username, full_name))

    async def get_user(self, user_id: int) -> Optional[dict]:
        sql = "SELECT * FROM users WHERE id=$1"
        return await self.read(sql, (user_id,), one=True)

    async def set_chatgpt_thread_id(self, user_id: int, thread_id: str) -> None:
        sql = "UPDATE users SET chatgpt_thread_id=$1 WHERE id=$2"
        await self.do(sql, (thread_id, user_id))

    async def get_chatgpt_thread_id(self, user_id: int) -> Optional[str]:
        sql = "SELECT chatgpt_thread_id FROM users WHERE id=$1"
        row = await self.read(sql, (user_id,), one=True)
        return row["chatgpt_thread_id"] if row else None

    async def set_phone_number(self, user_id: int, phone_number: str) -> None:
        sql = "UPDATE users SET phone_number=$1 WHERE id=$2"
        await self.do(sql, (phone_number, user_id))

    async def set_manager(self, user_id: int, spec: str, manager_level: int) -> None:
        sql = "UPDATE users SET manager_level=$1, spec=$2 WHERE id=$3"
        await self.do(sql, (manager_level, spec, user_id))

    async def get_managers(self) -> List[dict]:
        sql = "SELECT * FROM users WHERE manager_level!=0 AND active_user IS NULL ORDER BY manager_level DESC"
        return await self.read(sql)

    async def add_message(self, user_id: int, message_text: str, sender: int) -> None:
        sql = "INSERT INTO messages (user_id, message, sender) VALUES ($1, $2, $3)"
        await self.do(sql, (user_id, message_text, sender))

    async def update_user_info(self, user_id: int, json_info: dict) -> None:
        sql = """
            UPDATE users
            SET extra_info = extra_info || $1::jsonb
            WHERE id=$2
        """
        await self.do(sql, (json.dumps(json_info), user_id))
