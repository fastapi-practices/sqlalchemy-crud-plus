#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from pydantic import BaseModel
from sqlalchemy import select

from sqlalchemy_crud_plus import CRUDPlus
from tests.conftest import async_db_session
from tests.model import Ins


class ModelSchema(BaseModel):
    name: str


async def create_test_model():
    async with async_db_session.begin() as session:
        for i in range(1, 10):
            data = Ins(name=f'test_name_{i}')
            session.add(data)


@pytest.mark.asyncio
async def test_create_model():
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            data = ModelSchema(name=f'test_name_{i}')
            await crud.create_model(session, data)
    async with async_db_session() as session:
        for i in range(1, 10):
            query = await session.scalar(select(Ins).where(Ins.id == i))
            assert query.name == f'test_name_{i}'


@pytest.mark.asyncio
async def test_create_models():
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = []
        for i in range(1, 10):
            data.append(ModelSchema(name=f'test_name_{i}'))
        await crud.create_models(session, data)
    async with async_db_session() as session:
        for i in range(1, 10):
            query = await session.scalar(select(Ins).where(Ins.id == i))
            assert query.name == f'test_name_{i}'


@pytest.mark.asyncio
async def test_select_model_by_id():
    await create_test_model()
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.select_model_by_id(session, i)
            assert result.name == f'test_name_{i}'


@pytest.mark.asyncio
async def test_select_model_by_column():
    await create_test_model()
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.select_model_by_column(session, 'name', f'test_name_{i}')
            assert result.name == f'test_name_{i}'


@pytest.mark.asyncio
async def test_select_model_by_columns():
    await create_test_model()
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.select_model_by_columns(session, id=f'{i}', name=f'test_name_{i}')
            assert result.name == f'test_name_{i}'
            result = await crud.select_model_by_columns(session, 'or', id=f'{i}', name='null')
            assert result.name == f'test_name_{i}'


@pytest.mark.asyncio
async def test_select_models():
    await create_test_model()
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_models(session)
        assert len(result) == 9


@pytest.mark.asyncio
async def test_select_models_order():
    await create_test_model()
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_models_order(session, 'id', 'name')
        assert result[0].id == 1
        result = await crud.select_models_order(session, 'id', model_sort='asc')
        assert result[0].id == 1
        result = await crud.select_models_order(session, 'id', model_sort='desc')
        assert result[0].id == 9


@pytest.mark.asyncio
async def test_update_model():
    await create_test_model()
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = ModelSchema(name='test_name_update_1')
        result = await crud.update_model(session, 1, data)
        assert result == 1
        result = await session.get(Ins, 1)
        assert result.name == 'test_name_update_1'


@pytest.mark.asyncio
async def test_update_model_by_column():
    await create_test_model()
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = ModelSchema(name='test_name_update_1')
        result = await crud.update_model_by_column(session, 'name', 'test_name_1', data)
        assert result == 1
        result = await session.get(Ins, 1)
        assert result.name == 'test_name_update_1'


@pytest.mark.asyncio
async def test_delete_model():
    await create_test_model()
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.delete_model(session, i)
            assert result == 1
