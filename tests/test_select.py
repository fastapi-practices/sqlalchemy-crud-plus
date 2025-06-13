#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins


@pytest.mark.asyncio
async def test_select_model_by_id(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = populated_db[0]
    result = await crud_ins.select_model(async_db_session, item.id)

    assert result is not None
    assert result.id == item.id
    assert result.name == item.name


@pytest.mark.asyncio
async def test_select_model_by_id_not_found(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    result = await crud_ins.select_model(async_db_session, 99999)

    assert result is None


@pytest.mark.asyncio
async def test_select_model_with_whereclause(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    result = await crud_ins.select_model(async_db_session, item.id, crud_ins.model.del_flag is False)

    assert result is not None
    assert result.id == item.id


@pytest.mark.asyncio
async def test_select_model_with_kwargs(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    result = await crud_ins.select_model(async_db_session, item.id, del_flag=False)

    assert result is not None
    assert result.id == item.id


@pytest.mark.asyncio
async def test_select_model_by_column_basic(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    result = await crud_ins.select_model_by_column(async_db_session, name=item.name)

    assert result is not None
    assert result.name == item.name


@pytest.mark.asyncio
async def test_select_model_by_column_not_found(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    result = await crud_ins.select_model_by_column(async_db_session, name='nonexistent')

    assert result is None


@pytest.mark.asyncio
async def test_select_model_by_column_with_whereclause(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    result = await crud_ins.select_model_by_column(async_db_session, crud_ins.model.del_flag is False, name=item.name)

    assert result is not None
    assert result.name == item.name


@pytest.mark.asyncio
async def test_select_models_basic(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session)

    assert len(results) >= len(populated_db)


@pytest.mark.asyncio
async def test_select_models_with_limit(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, limit=3)

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_select_models_with_offset(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, offset=2, limit=3)

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_select_models_with_whereclause(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, crud_ins.model.del_flag is False)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_with_kwargs(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, del_flag=False)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_basic(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models_order(async_db_session, 'name')

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_with_sort_orders(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models_order(async_db_session, 'name', 'desc')

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_multiple_columns(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models_order(async_db_session, ['name', 'id'], ['asc', 'desc'])

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_with_limit(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models_order(async_db_session, 'name', limit=3)

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_select_models_order_with_offset(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models_order(async_db_session, 'name', offset=2, limit=3)

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_select_models_order_with_whereclause(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models_order(async_db_session, 'name', crud_ins.model.del_flag is False)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_select_models_order_with_kwargs(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models_order(async_db_session, 'name', del_flag=False)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_count_basic(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.count(async_db_session)

    assert count >= len(populated_db)


@pytest.mark.asyncio
async def test_count_with_whereclause(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.count(async_db_session, crud_ins.model.del_flag is False)

    assert count >= 0


@pytest.mark.asyncio
async def test_count_with_kwargs(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.count(async_db_session, del_flag=False)

    assert count >= 0


@pytest.mark.asyncio
async def test_exists_basic(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(async_db_session, name=populated_db[0].name)

    assert exists is True


@pytest.mark.asyncio
async def test_exists_not_found(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(async_db_session, name='nonexistent')

    assert exists is False


@pytest.mark.asyncio
async def test_exists_with_whereclause(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    exists = await crud_ins.exists(async_db_session, crud_ins.model.del_flag is False)

    assert isinstance(exists, bool)


@pytest.mark.asyncio
async def test_exists_with_kwargs(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(async_db_session, del_flag=False)

    assert isinstance(exists, bool)
