#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins, InsPks
from tests.schemas.basic import InsCreate, InsPksCreate, InsUpdate


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
        result = await crud_ins.update_model(async_db_session, item.id, update_data, is_deleted=True)

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
            async_db_session, update_data, allow_multiple=True, is_deleted=False
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
            await crud_ins.update_model_by_column(async_db_session, update_data, is_deleted=False)


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_true(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [
        InsCreate(name='update_test_1', is_deleted=False),
        InsCreate(name='update_test_2', is_deleted=False),
        InsCreate(name='update_test_3', is_deleted=False),
    ]

    async with async_db_session.begin():
        created_items = await crud_ins.create_models(async_db_session, create_data)

    update_data = [
        {'id': created_items[0].id, 'name': 'updated_test_1', 'is_deleted': True},
        {'id': created_items[1].id, 'name': 'updated_test_2', 'is_deleted': True},
        {'id': created_items[2].id, 'name': 'updated_test_3', 'is_deleted': True},
    ]

    async with async_db_session.begin():
        result = await crud_ins.bulk_update_models(async_db_session, update_data, pk_mode=True)

    assert result == 3

    async with async_db_session.begin():
        updated_item1 = await crud_ins.select_model(async_db_session, created_items[0].id)
        updated_item2 = await crud_ins.select_model(async_db_session, created_items[1].id)
        updated_item3 = await crud_ins.select_model(async_db_session, created_items[2].id)

    assert updated_item1.name == 'updated_test_1'
    assert updated_item1.is_deleted is True
    assert updated_item2.name == 'updated_test_2'
    assert updated_item2.is_deleted is True
    assert updated_item3.name == 'updated_test_3'
    assert updated_item3.is_deleted is True


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_false(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [
        InsCreate(name='filter_test_1', is_deleted=False),
        InsCreate(name='filter_test_2', is_deleted=False),
    ]

    async with async_db_session.begin():
        await crud_ins.create_models(async_db_session, create_data)

    update_data = [
        {'name': 'bulk_updated_1'},
        {'name': 'bulk_updated_2'},
    ]

    async with async_db_session.begin():
        result = await crud_ins.bulk_update_models(async_db_session, update_data, pk_mode=False, is_deleted=False)

    assert result == 2


@pytest.mark.asyncio
async def test_bulk_update_models_with_pydantic_schema(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [InsCreate(name='schema_test')]

    async with async_db_session.begin():
        created_items = await crud_ins.create_models(async_db_session, create_data)

    update_data = [InsUpdate(name='schema_updated')]

    async with async_db_session.begin():
        result = await crud_ins.bulk_update_models(async_db_session, update_data, pk_mode=False, id=created_items[0].id)

    assert result == 1


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_false_no_filters_error(
    async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
):
    """测试 bulk_update_models pk_mode=False 时没有过滤条件的错误"""
    update_data = [{'name': 'no_filters'}]

    with pytest.raises(ValueError, match='At least one filter condition must be provided'):
        async with async_db_session.begin():
            await crud_ins.bulk_update_models(async_db_session, update_data, pk_mode=False)


@pytest.mark.asyncio
async def test_bulk_update_models_composite_keys(async_db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    create_data = [
        InsPksCreate(id=2000, name='update_pks_1', sex='male'),
        InsPksCreate(id=2001, name='update_pks_2', sex='female'),
    ]

    async with async_db_session.begin():
        await crud_ins_pks.create_models(async_db_session, create_data)

    update_data = [
        {'id': 2000, 'sex': 'male', 'name': 'updated_pks_1'},
        {'id': 2001, 'sex': 'female', 'name': 'updated_pks_2'},
    ]

    async with async_db_session.begin():
        result = await crud_ins_pks.bulk_update_models(async_db_session, update_data, pk_mode=True)

    assert result == 2

    async with async_db_session.begin():
        updated_item1 = await crud_ins_pks.select_model(async_db_session, (2000, 'male'))
        updated_item2 = await crud_ins_pks.select_model(async_db_session, (2001, 'female'))

    assert updated_item1.name == 'updated_pks_1'
    assert updated_item2.name == 'updated_pks_2'


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_false_with_flush(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [
        InsCreate(name='bulk_update_flush_1'),
        InsCreate(name='bulk_update_flush_2'),
    ]

    async with async_db_session.begin():
        await crud_ins.create_models(async_db_session, create_data)

    update_data = [{'name': 'updated_flush_1'}, {'name': 'updated_flush_2'}]

    async with async_db_session.begin():
        result = await crud_ins.bulk_update_models(
            async_db_session, update_data, pk_mode=False, flush=True, name__like='bulk_update_flush_%'
        )

    assert result == 2


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_false_with_commit(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [
        InsCreate(name='bulk_update_commit_1'),
        InsCreate(name='bulk_update_commit_2'),
    ]

    async with async_db_session.begin():
        await crud_ins.create_models(async_db_session, create_data)

    update_data = [{'name': 'updated_commit_1'}, {'name': 'updated_commit_2'}]

    result = await crud_ins.bulk_update_models(
        async_db_session, update_data, pk_mode=False, commit=True, name__like='bulk_update_commit_%'
    )

    assert result == 2
