#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy import select

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Ins
from tests.schema import ModelTest


@pytest.mark.asyncio
async def test_create_model(async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            data = ModelTest(name=f'name_{i}')
            await crud.create_model(session, data)
    async with async_db_session() as session:
        for i in range(1, 10):
            query = await session.scalar(select(Ins).where(Ins.id == i))
            assert query.name == f'name_{i}'


@pytest.mark.asyncio
async def test_create_models(async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = []
        for i in range(1, 10):
            data.append(ModelTest(name=f'name_{i}'))
        await crud.create_models(session, data)
    async with async_db_session() as session:
        for i in range(1, 10):
            query = await session.scalar(select(Ins).where(Ins.id == i))
            assert query.name == f'name_{i}'
