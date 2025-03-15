from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config.setting import setting


class Database:
    def __init__(self):
        self.async_engine = create_async_engine(
            setting.get_db_url
        )

        self.session_factory = async_sessionmaker(
            self.async_engine,
            expire_on_commit=False
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator:
        session = self.session_factory()
        try:
            yield session
        except Exception as e:
            print(f"Session rollback because of exception: {e}")
            await session.rollback()
        finally:
            await session.close()


database = Database()