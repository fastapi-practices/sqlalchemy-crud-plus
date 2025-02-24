from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

async_engine = create_async_engine('数据库连接', future=True)
async_db_session = async_sessionmaker(async_engine, autoflush=False, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """
    session 生成器
    """
    session = async_db_session()
    try:
        yield session
    except Exception as se:
        await session.rollback()
        raise se
    finally:
        await session.close()
