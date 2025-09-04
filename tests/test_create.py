#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins, InsPks
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
        result = await crud_ins.create_model(async_db_session, data, is_deleted=True)

    assert result.name == 'test_kwargs'
    assert result.is_deleted is True


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
        results = await crud_ins.create_models(async_db_session, data, is_deleted=True)

    assert len(results) == 2
    assert all(r.is_deleted is True for r in results)


@pytest.mark.asyncio
async def test_bulk_create_models_basic(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        data = [
            {'name': 'bulk_item_1', 'is_deleted': False, 'created_time': datetime.now()},
            {'name': 'bulk_item_2', 'is_deleted': True, 'created_time': datetime.now()},
            {'name': 'bulk_item_3', 'is_deleted': False, 'created_time': datetime.now()},
        ]
        results = await crud_ins.bulk_create_models(async_db_session, data)

    assert len(results) == 3
    assert results[0].name == 'bulk_item_1'
    assert results[1].name == 'bulk_item_2'
    assert results[2].name == 'bulk_item_3'
    assert results[0].is_deleted is False
    assert results[1].is_deleted is True
    assert results[2].is_deleted is False


@pytest.mark.asyncio
async def test_bulk_create_models_composite_keys(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = [
        {'id': 1000, 'name': 'bulk_pks_1', 'sex': 'male', 'created_time': datetime.now()},
        {'id': 1001, 'name': 'bulk_pks_2', 'sex': 'female', 'created_time': datetime.now()},
        {'id': 1002, 'name': 'bulk_pks_3', 'sex': 'male', 'created_time': datetime.now()},
    ]

    async with async_db_session.begin():
        results = await crud_ins_pks.bulk_create_models(async_db_session, data)

    assert len(results) == 3
    assert results[0].id == 1000
    assert results[0].name == 'bulk_pks_1'
    assert results[0].sex == 'male'


@pytest.mark.asyncio
async def test_bulk_create_models_with_flush(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = [
        {'name': 'bulk_flush_1', 'is_deleted': False, 'created_time': datetime.now()},
        {'name': 'bulk_flush_2', 'is_deleted': False, 'created_time': datetime.now()},
    ]

    async with async_db_session.begin():
        results = await crud_ins.bulk_create_models(async_db_session, data, flush=True)

    assert len(results) == 2
    assert results[0].name == 'bulk_flush_1'
    assert results[1].name == 'bulk_flush_2'


@pytest.mark.asyncio
async def test_bulk_create_models_with_commit(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = [
        {'name': 'bulk_commit_1', 'is_deleted': False, 'created_time': datetime.now()},
        {'name': 'bulk_commit_2', 'is_deleted': False, 'created_time': datetime.now()},
    ]

    results = await crud_ins.bulk_create_models(async_db_session, data, commit=True)

    assert len(results) == 2
    assert results[0].name == 'bulk_commit_1'
    assert results[1].name == 'bulk_commit_2'
