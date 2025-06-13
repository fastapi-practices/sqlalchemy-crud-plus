#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import CompositePrimaryKeysError
from tests.models.basic import InsPks
from tests.schemas.basic import InsPksCreate, InsPksUpdate


@pytest.mark.asyncio
async def test_composite_key_create_model(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = InsPksCreate(id=100, name='test_user', sex='test')
    result = await crud_ins_pks.create_model(async_db_session, data, commit=True)

    assert result.id == 100
    assert result.sex == 'test'
    assert result.name == 'test_user'


@pytest.mark.asyncio
async def test_composite_key_select_model(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = InsPksCreate(id=101, name='select_test', sex='test')
    await crud_ins_pks.create_model(async_db_session, data, commit=True)

    result = await crud_ins_pks.select_model(async_db_session, (101, 'test'))

    assert result is not None
    assert result.id == 101
    assert result.sex == 'test'
    assert result.name == 'select_test'


@pytest.mark.asyncio
async def test_composite_key_update_model(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = InsPksCreate(id=102, name='update_test', sex='test')
    await crud_ins_pks.create_model(async_db_session, data, commit=True)

    updated_count = await crud_ins_pks.update_model(
        async_db_session, (102, 'test'), InsPksUpdate(name='updated_name'), commit=True
    )

    assert updated_count == 1


@pytest.mark.asyncio
async def test_composite_key_delete_model(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = InsPksCreate(id=103, name='delete_test', sex='test')
    await crud_ins_pks.create_model(async_db_session, data, commit=True)

    deleted_count = await crud_ins_pks.delete_model(async_db_session, (103, 'test'), commit=True)

    assert deleted_count == 1


@pytest.mark.asyncio
async def test_composite_key_create_models(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = [InsPksCreate(id=200, name='batch_1', sex='test1'), InsPksCreate(id=201, name='batch_2', sex='test2')]

    results = await crud_ins_pks.create_models(async_db_session, data, commit=True)

    assert len(results) == 2
    assert results[0].id == 200
    assert results[1].id == 201


@pytest.mark.asyncio
async def test_composite_key_count(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = [
        InsPksCreate(id=300, name='count_1', sex='count_test'),
        InsPksCreate(id=301, name='count_2', sex='count_test'),
        InsPksCreate(id=302, name='count_3', sex='count_test'),
    ]
    await crud_ins_pks.create_models(async_db_session, data, commit=True)

    count = await crud_ins_pks.count(async_db_session, sex='count_test')

    assert count == 3


@pytest.mark.asyncio
async def test_composite_key_exists(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = InsPksCreate(id=400, name='exists_test', sex='exists')
    await crud_ins_pks.create_model(async_db_session, data, commit=True)

    exists = await crud_ins_pks.exists(async_db_session, id=400, sex='exists')

    assert exists is True


@pytest.mark.asyncio
async def test_composite_key_select_models(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = [
        InsPksCreate(id=500, name='select_1', sex='select_test'),
        InsPksCreate(id=501, name='select_2', sex='select_test'),
    ]
    await crud_ins_pks.create_models(async_db_session, data, commit=True)

    results = await crud_ins_pks.select_models(async_db_session, sex='select_test')

    assert len(results) == 2


@pytest.mark.asyncio
async def test_composite_key_error_insufficient_params(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    with pytest.raises(CompositePrimaryKeysError):
        await crud_ins_pks.select_model(async_db_session, (1,))


@pytest.mark.asyncio
async def test_composite_key_error_excessive_params(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    with pytest.raises(CompositePrimaryKeysError):
        await crud_ins_pks.select_model(async_db_session, (1, 'men', 'extra'))


@pytest.mark.asyncio
async def test_composite_key_error_update_insufficient_params(
    async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]
):
    with pytest.raises(CompositePrimaryKeysError):
        await crud_ins_pks.update_model(async_db_session, (1,), {'name': 'test'})


@pytest.mark.asyncio
async def test_composite_key_error_delete_excessive_params(
    async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]
):
    with pytest.raises(CompositePrimaryKeysError):
        await crud_ins_pks.delete_model(async_db_session, (1, 'men', 'extra'))
