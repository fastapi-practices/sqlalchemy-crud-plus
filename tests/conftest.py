#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest_asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tests.model import Base, Ins

_async_engine = create_async_engine('sqlite+aiosqlite:///:memory:', future=True)
_async_session = async_sessionmaker(_async_engine, autoflush=False, expire_on_commit=False)


@pytest_asyncio.fixture(scope='function', autouse=True)
async def init_db():
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_db_session():
    yield _async_session


@pytest_asyncio.fixture
async def create_test_model():
    async with _async_session.begin() as session:
        data = [Ins(name=f'name_{i}') for i in range(1, 10)]
        session.add_all(data)
