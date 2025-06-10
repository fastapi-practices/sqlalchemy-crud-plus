#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Base, Ins, InsPks

# Database configuration
_async_engine = create_async_engine(
    'sqlite+aiosqlite:///:memory:',
    future=True,
    echo=False,  # Set to True for SQL debugging
)
_async_session_factory = async_sessionmaker(_async_engine, autoflush=False, expire_on_commit=False)


@pytest_asyncio.fixture(scope='function', autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Setup and teardown database for each test function."""
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for testing."""
    async with _async_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def db_session_factory() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Provide a session factory for testing."""
    yield _async_session_factory


@pytest.fixture
def crud_ins() -> CRUDPlus[Ins]:
    """Provide CRUD instance for Ins model."""
    return CRUDPlus(Ins)


@pytest.fixture
def crud_ins_pks() -> CRUDPlus[InsPks]:
    """Provide CRUD instance for InsPks model."""
    return CRUDPlus(InsPks)


@pytest_asyncio.fixture
async def populated_db(db_session: AsyncSession, crud_ins: CRUDPlus[Ins]) -> list[Ins]:
    """Provide a database populated with test data."""
    async with db_session.begin():
        test_data = [Ins(name=f'item_{i}', del_flag=(i % 2 == 0)) for i in range(1, 11)]
        db_session.add_all(test_data)
        await db_session.flush()
        return test_data


@pytest_asyncio.fixture
async def populated_db_pks(db_session: AsyncSession) -> dict[str, list[InsPks]]:
    """Provide a database populated with composite key test data."""
    async with db_session.begin():
        men_data = [InsPks(id=i, name=f'man_{i}', sex='men') for i in range(1, 4)]
        women_data = [InsPks(id=i, name=f'woman_{i}', sex='women') for i in range(4, 7)]
        all_data = men_data + women_data

        db_session.add_all(all_data)
        await db_session.flush()

        return {'men': men_data, 'women': women_data, 'all': all_data}
