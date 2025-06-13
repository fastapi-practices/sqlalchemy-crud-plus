#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins
from tests.schemas.basic import InsUpdate


@pytest.mark.asyncio
async def test_update_model_by_id(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = populated_db[0]
    update_data = InsUpdate(name='updated_item')

    async with async_db_session.begin():
        result = await crud_ins.update_model(async_db_session, item.id, update_data)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_id_not_found(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    update_data = InsUpdate(name='not_found')

    async with async_db_session.begin():
        result = await crud_ins.update_model(async_db_session, 99999, update_data)

    assert result == 0


@pytest.mark.asyncio
async def test_update_model_with_flush(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    update_data = InsUpdate(name='flush_update')

    async with async_db_session.begin():
        result = await crud_ins.update_model(async_db_session, item.id, update_data, flush=True)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_with_commit(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    update_data = InsUpdate(name='commit_update')

    result = await crud_ins.update_model(async_db_session, item.id, update_data, commit=True)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_with_kwargs(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    update_data = InsUpdate(name='kwargs_update')

    async with async_db_session.begin():
        result = await crud_ins.update_model(async_db_session, item.id, update_data, del_flag=True)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_with_dict(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = populated_db[0]
    update_data = {'name': 'dict_update'}

    async with async_db_session.begin():
        result = await crud_ins.update_model(async_db_session, item.id, update_data)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_basic(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    update_data = InsUpdate(name='updated_by_column')

    async with async_db_session.begin():
        result = await crud_ins.update_model_by_column(async_db_session, update_data, id=item.id)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_not_found(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    update_data = InsUpdate(name='not_found')

    async with async_db_session.begin():
        result = await crud_ins.update_model_by_column(async_db_session, update_data, name='nonexistent')

    assert result == 0


@pytest.mark.asyncio
async def test_update_model_by_column_allow_multiple(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    update_data = InsUpdate(name='multiple_update')

    async with async_db_session.begin():
        result = await crud_ins.update_model_by_column(
            async_db_session, update_data, allow_multiple=True, del_flag=False
        )

    assert result >= 0


@pytest.mark.asyncio
async def test_update_model_by_column_with_flush(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    update_data = InsUpdate(name='flush_column_update')

    async with async_db_session.begin():
        result = await crud_ins.update_model_by_column(async_db_session, update_data, flush=True, id=item.id)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_with_commit(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    update_data = InsUpdate(name='commit_column_update')

    result = await crud_ins.update_model_by_column(async_db_session, update_data, commit=True, id=item.id)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_with_dict(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]
    update_data = {'name': 'dict_column_update'}

    async with async_db_session.begin():
        result = await crud_ins.update_model_by_column(async_db_session, update_data, id=item.id)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_no_filters_error(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    update_data = InsUpdate(name='no_filters')

    with pytest.raises(ValueError):
        async with async_db_session.begin():
            await crud_ins.update_model_by_column(async_db_session, update_data)


@pytest.mark.asyncio
async def test_update_model_by_column_multiple_results_error(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    update_data = InsUpdate(name='multiple_error')

    with pytest.raises(Exception):
        async with async_db_session.begin():
            await crud_ins.update_model_by_column(async_db_session, update_data, del_flag=False)
