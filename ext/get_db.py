from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

async_engine = create_async_engine('数据库连接', future=True)
async_db_session = async_sessionmaker(async_engine, autoflush=False, expire_on_commit=False)


async def get_db() -> AsyncGenerator:
    """
    session 生成器
    """
    async with async_db_session() as session:
        yield session
