#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins
from tests.schemas.basic import InsCreate


@pytest.mark.asyncio
async def test_create_model_basic(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        data = InsCreate(name='test_item')
        result = await crud_ins.create_model(async_db_session, data)

    assert result.name == 'test_item'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_flush(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        data = InsCreate(name='test_flush')
        result = await crud_ins.create_model(async_db_session, data, flush=True)

    assert result.name == 'test_flush'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_commit(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = InsCreate(name='test_commit')
    result = await crud_ins.create_model(async_db_session, data, commit=True)

    assert result.name == 'test_commit'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_kwargs(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        data = InsCreate(name='test_kwargs')
        result = await crud_ins.create_model(async_db_session, data, del_flag=True)

    assert result.name == 'test_kwargs'
    assert result.del_flag is True


@pytest.mark.asyncio
async def test_create_models_basic(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        data = [InsCreate(name=f'item_{i}') for i in range(3)]
        results = await crud_ins.create_models(async_db_session, data)

    assert len(results) == 3
    assert all(r.name.startswith('item_') for r in results)
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_with_flush(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        data = [InsCreate(name=f'flush_item_{i}') for i in range(2)]
        results = await crud_ins.create_models(async_db_session, data, flush=True)

    assert len(results) == 2
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_with_commit(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = [InsCreate(name=f'commit_item_{i}') for i in range(2)]
    results = await crud_ins.create_models(async_db_session, data, commit=True)

    assert len(results) == 2
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_empty_list(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        results = await crud_ins.create_models(async_db_session, [])

    assert results == []


@pytest.mark.asyncio
async def test_create_models_with_kwargs(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        data = [InsCreate(name=f'kwargs_item_{i}') for i in range(2)]
        results = await crud_ins.create_models(async_db_session, data, del_flag=True)

    assert len(results) == 2
    assert all(r.del_flag is True for r in results)
