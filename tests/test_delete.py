#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Ins


@pytest.mark.asyncio
async def test_delete_model(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        result = await crud.delete_model(session, 1)
        assert result == 1


@pytest.mark.asyncio
async def test_delete_model_by_column(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        result = await crud.delete_model_by_column(session, name='name_1')
        assert result == 1


@pytest.mark.asyncio
async def test_delete_model_by_column_with_and(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        result = await crud.delete_model_by_column(session, id=1, name='name_1')
        assert result == 1


@pytest.mark.asyncio
async def test_delete_model_by_column_logical(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        result = await crud.delete_model_by_column(session, logical_deletion=True, name='name_1')
        assert result == 1


@pytest.mark.asyncio
async def test_delete_model_by_column_allow_multiple(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        result = await crud.delete_model_by_column(session, allow_multiple=True, name__startswith='name')
        assert result == 9


@pytest.mark.asyncio
async def test_delete_model_by_column_logical_with_multiple(create_test_model, async_db_session):
    async with async_db_session.begin() as session:
        crud = CRUDPlus(Ins)
        result = await crud.delete_model_by_column(
            session, allow_multiple=True, logical_deletion=True, name__startswith='name'
        )
        assert result == 9
