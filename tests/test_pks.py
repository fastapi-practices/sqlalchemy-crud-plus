#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import CompositePrimaryKeysError
from tests.models.basic import InsPks
from tests.schemas.basic import CreateInsPks, UpdateInsPks


@pytest.mark.asyncio
async def test_pks_create_model(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = CreateInsPks(id=100, name='test_user', sex='test')
    result = await crud_ins_pks.create_model(db, data, commit=True)

    assert result.id == 100
    assert result.sex == 'test'
    assert result.name == 'test_user'


@pytest.mark.asyncio
async def test_pks_select_model(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = CreateInsPks(id=101, name='select_test', sex='test')
    await crud_ins_pks.create_model(db, data, commit=True)

    result = await crud_ins_pks.select_model(db, (101, 'test'))

    assert result is not None
    assert result.id == 101
    assert result.sex == 'test'
    assert result.name == 'select_test'


@pytest.mark.asyncio
async def test_pks_update_model(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = CreateInsPks(id=102, name='update_test', sex='test')
    await crud_ins_pks.create_model(db, data, commit=True)

    updated_count = await crud_ins_pks.update_model(db, (102, 'test'), UpdateInsPks(name='updated_name'), commit=True)

    assert updated_count == 1


@pytest.mark.asyncio
async def test_pks_delete_model(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = CreateInsPks(id=103, name='delete_test', sex='test')
    await crud_ins_pks.create_model(db, data, commit=True)

    deleted_count = await crud_ins_pks.delete_model(db, (103, 'test'), commit=True)

    assert deleted_count == 1


@pytest.mark.asyncio
async def test_pks_create_models(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = [CreateInsPks(id=200, name='batch_1', sex='test1'), CreateInsPks(id=201, name='batch_2', sex='test2')]

    results = await crud_ins_pks.create_models(db, data, commit=True)

    assert len(results) == 2
    assert results[0].id == 200
    assert results[1].id == 201


@pytest.mark.asyncio
async def test_pks_count(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = [
        CreateInsPks(id=300, name='count_1', sex='count_test'),
        CreateInsPks(id=301, name='count_2', sex='count_test'),
        CreateInsPks(id=302, name='count_3', sex='count_test'),
    ]
    await crud_ins_pks.create_models(db, data, commit=True)

    count = await crud_ins_pks.count(db, sex='count_test')

    assert count == 3


@pytest.mark.asyncio
async def test_pks_exists(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = CreateInsPks(id=400, name='exists_test', sex='exists')
    await crud_ins_pks.create_model(db, data, commit=True)

    exists = await crud_ins_pks.exists(db, id=400, sex='exists')

    assert exists is True


@pytest.mark.asyncio
async def test_pks_select_models(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = [
        CreateInsPks(id=500, name='select_1', sex='select_test'),
        CreateInsPks(id=501, name='select_2', sex='select_test'),
    ]
    await crud_ins_pks.create_models(db, data, commit=True)

    results = await crud_ins_pks.select_models(db, sex='select_test')

    assert len(results) == 2


@pytest.mark.asyncio
async def test_pks_error_insufficient_params(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    with pytest.raises(CompositePrimaryKeysError):
        await crud_ins_pks.select_model(db, (1,))


@pytest.mark.asyncio
async def test_pks_error_excessive_params(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    with pytest.raises(CompositePrimaryKeysError):
        await crud_ins_pks.select_model(db, (1, 'men', 'extra'))


@pytest.mark.asyncio
async def test_pks_error_update_insufficient_params(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    with pytest.raises(CompositePrimaryKeysError):
        await crud_ins_pks.update_model(db, (1,), {'name': 'test'})


@pytest.mark.asyncio
async def test_pks_error_delete_excessive_params(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    with pytest.raises(CompositePrimaryKeysError):
        await crud_ins_pks.delete_model(db, (1, 'men', 'extra'))
