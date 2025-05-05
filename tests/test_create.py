#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import choice

import pytest

from sqlalchemy import select

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Ins, InsPks
from tests.schema import ModelTest, ModelTestPks


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


@pytest.mark.asyncio
async def test_create_model_pks(async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(InsPks)
        for i in range(1, 10):
            data = ModelTestPks(id=i, name=f'name_{i}', sex=choice(['men', 'women']))
            await crud.create_model(session, data)
    async with async_db_session() as session:
        for i in range(1, 10):
            query = await session.scalar(select(InsPks).where(InsPks.id == i))
            assert query.name == f'name_{i}'


@pytest.mark.asyncio
async def test_create_models_pks(async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(InsPks)
        data = []
        for i in range(1, 10):
            data.append(ModelTestPks(id=i, name=f'name_{i}', sex=choice(['men', 'women'])))
        await crud.create_models(session, data)
    async with async_db_session() as session:
        for i in range(1, 10):
            query = await session.scalar(select(InsPks).where(InsPks.id == i))
            assert query.name == f'name_{i}'
