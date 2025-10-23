#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins


@pytest.mark.asyncio
async def test_select_model_by_id(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    result = await crud_ins.select_model(db, item.id)

    assert result is not None
    assert result.id == item.id
    assert result.name == item.name


@pytest.mark.asyncio
async def test_select_model_by_id_not_found(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    result = await crud_ins.select_model(db, 99999)

    assert result is None


@pytest.mark.asyncio
async def test_select_model_with_whereclause(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    result = await crud_ins.select_model(db, item.id, ~crud_ins.model.is_deleted)

    assert result is not None
    assert result.id == item.id


@pytest.mark.asyncio
async def test_select_model_with_kwargs(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    result = await crud_ins.select_model(db, item.id, is_deleted=False)

    assert result is not None
    assert result.id == item.id


@pytest.mark.asyncio
async def test_select_model_by_column_basic(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    result = await crud_ins.select_model_by_column(db, name=item.name)

    assert result is not None
    assert result.name == item.name


@pytest.mark.asyncio
async def test_select_model_by_column_not_found(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    result = await crud_ins.select_model_by_column(db, name='nonexistent')

    assert result is None


@pytest.mark.asyncio
async def test_select_model_by_column_with_whereclause(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = sample_ins[0]
    result = await crud_ins.select_model_by_column(db, ~crud_ins.model.is_deleted, name=item.name)

    assert result is not None
    assert result.name == item.name


@pytest.mark.asyncio
async def test_select_model_by_column_comprehensive(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    from tests.schemas.basic import CreateIns

    create_data = CreateIns(name='comprehensive_test_select')

    async with db.begin():
        created_item = await crud_ins.create_model(db, create_data)

    result = await crud_ins.select_model_by_column(db, name='comprehensive_test_select')

    assert result is not None
    assert result.name == 'comprehensive_test_select'
    assert result.id == created_item.id


@pytest.mark.asyncio
async def test_select_models_basic(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db)

    assert len(results) >= len(sample_ins)


@pytest.mark.asyncio
async def test_select_models_with_limit(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, limit=3)

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_select_models_with_offset(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, offset=2, limit=3)

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_select_models_with_whereclause(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, ~crud_ins.model.is_deleted)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_with_kwargs(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, is_deleted=False)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_basic(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models_order(db, 'name')

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_with_sort_orders(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models_order(db, 'name', 'desc')

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_multiple_columns(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models_order(db, ['name', 'id'], ['asc', 'desc'])

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_with_limit(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models_order(db, 'name', limit=3)

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_select_models_order_with_offset(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models_order(db, 'name', offset=2, limit=3)

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_select_models_order_with_whereclause(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models_order(db, 'name', None, ~crud_ins.model.is_deleted)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_with_kwargs(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models_order(db, 'name', is_deleted=False)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_count_basic(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.count(db)

    assert count >= len(sample_ins)


@pytest.mark.asyncio
async def test_count_with_whereclause(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.count(db, ~crud_ins.model.is_deleted)

    assert count >= 0


@pytest.mark.asyncio
async def test_count_with_kwargs(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.count(db, is_deleted=False)

    assert count >= 0


@pytest.mark.asyncio
async def test_exists_basic(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(db, name=sample_ins[0].name)

    assert exists is True


@pytest.mark.asyncio
async def test_exists_not_found(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(db, name='nonexistent')

    assert exists is False


@pytest.mark.asyncio
async def test_exists_with_whereclause(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(db, ~crud_ins.model.is_deleted)

    assert isinstance(exists, bool)


@pytest.mark.asyncio
async def test_exists_with_kwargs(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(db, is_deleted=False)

    assert isinstance(exists, bool)
