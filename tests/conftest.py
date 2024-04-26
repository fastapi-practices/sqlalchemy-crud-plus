#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest_asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tests.model import Base

async_engine = create_async_engine('sqlite+aiosqlite:///:memory:', future=True, pool_pre_ping=True)
async_db_session = async_sessionmaker(async_engine, autoflush=False, expire_on_commit=False)


@pytest_asyncio.fixture(scope='function', autouse=True)
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)
