#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Ins
from tests.schema import ModelTest


@pytest.mark.asyncio
async def test_update_model(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = ModelTest(name='name_update_1')
        result = await crud.update_model(session, 1, data)
        assert result == 1
        result = await session.get(Ins, 1)
        assert result.name == 'name_update_1'


@pytest.mark.asyncio
async def test_update_model_by_column(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = ModelTest(name='name_update_1')
        result = await crud.update_model_by_column(session, data, name='name_1')
        assert result == 1
        result = await session.get(Ins, 1)
        assert result.name == 'name_update_1'


@pytest.mark.asyncio
async def test_update_model_by_column_with_and(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = ModelTest(name='name_update_1')
        result = await crud.update_model_by_column(session, data, id=1, name='name_1')
        assert result == 1
        result = await session.get(Ins, 1)
        assert result.name == 'name_update_1'


@pytest.mark.asyncio
async def test_update_model_by_column_with_filter(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = ModelTest(name='name_update_1')
        result = await crud.update_model_by_column(session, data, id__eq=1)
        assert result == 1
        result = await session.get(Ins, 1)
        assert result.name == 'name_update_1'


@pytest.mark.asyncio
async def test_update_model_by_column_allow_multiple(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        data = ModelTest(name='name_update_1')
        result = await crud.update_model_by_column(session, data, allow_multiple=True, name__startswith='name')
        assert result == 9
        result = await session.get(Ins, 1)
        assert result.name == 'name_update_1'
