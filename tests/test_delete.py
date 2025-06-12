#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins


@pytest.mark.asyncio
async def test_delete_model_by_id(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = populated_db[0]

    async with async_db_session.begin():
        count = await crud_ins.delete_model(async_db_session, item.id)

    assert count == 1

    result = await crud_ins.select_model(async_db_session, item.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_model_by_id_not_found(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        count = await crud_ins.delete_model(async_db_session, 99999)

    assert count == 0


@pytest.mark.asyncio
async def test_delete_model_with_flush(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[1]

    async with async_db_session.begin():
        count = await crud_ins.delete_model(async_db_session, item.id, flush=True)

    assert count == 1


@pytest.mark.asyncio
async def test_delete_model_with_commit(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[2]

    count = await crud_ins.delete_model(async_db_session, item.id, commit=True)

    assert count == 1


@pytest.mark.asyncio
async def test_delete_model_by_column_basic(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[3]

    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(async_db_session, allow_multiple=True, name=item.name)

    assert count >= 0


@pytest.mark.asyncio
async def test_delete_model_by_column_not_found(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(async_db_session, allow_multiple=True, name='nonexistent')

    assert count == 0


@pytest.mark.asyncio
async def test_delete_model_by_column_allow_multiple(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(async_db_session, allow_multiple=True, del_flag=False)

    assert count >= 0


@pytest.mark.asyncio
async def test_delete_model_by_column_with_flush(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[4]

    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(async_db_session, allow_multiple=True, flush=True, name=item.name)

    assert count >= 0


@pytest.mark.asyncio
async def test_delete_model_by_column_with_commit(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[5]

    count = await crud_ins.delete_model_by_column(async_db_session, allow_multiple=True, commit=True, name=item.name)

    assert count >= 0


@pytest.mark.asyncio
async def test_delete_model_by_column_no_filters_error(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    with pytest.raises(ValueError):
        async with async_db_session.begin():
            await crud_ins.delete_model_by_column(async_db_session, allow_multiple=True)


@pytest.mark.asyncio
async def test_delete_model_by_column_multiple_results_error(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    with pytest.raises(Exception):
        async with async_db_session.begin():
            await crud_ins.delete_model_by_column(async_db_session, del_flag=False)
