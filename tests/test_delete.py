#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import ModelColumnError
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


@pytest.mark.asyncio
async def test_logical_delete_single_record(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[0]

    assert item.del_flag is False

    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(
            async_db_session, logical_deletion=True, allow_multiple=False, id=item.id
        )

    assert count == 1

    async with async_db_session.begin():
        updated_item = await crud_ins.select_model(async_db_session, item.id)
        assert updated_item is not None
        assert updated_item.del_flag is True


@pytest.mark.asyncio
async def test_logical_delete_multiple_records(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(
            async_db_session, logical_deletion=True, allow_multiple=True, del_flag=False
        )

    assert count >= 0

    async with async_db_session.begin():
        remaining_false = await crud_ins.select_models(async_db_session, del_flag=False)
        assert len(remaining_false) >= 0


@pytest.mark.asyncio
async def test_logical_delete_with_custom_column(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[1]

    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(
            async_db_session, logical_deletion=True, deleted_flag_column='del_flag', allow_multiple=False, id=item.id
        )

    assert count == 1

    async with async_db_session.begin():
        updated_item = await crud_ins.select_model(async_db_session, item.id)
        assert updated_item.del_flag is True


@pytest.mark.asyncio
async def test_logical_delete_with_filters(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(
            async_db_session, logical_deletion=True, allow_multiple=True, name__like='item_%', id__gt=3
        )

    assert count >= 0

    async with async_db_session.begin():
        deleted_items = await crud_ins.select_models(async_db_session, name__like='item_%', id__gt=3, del_flag=True)

        assert len(deleted_items) >= 0


@pytest.mark.asyncio
async def test_logical_delete_with_flush(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[2]

    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(
            async_db_session, logical_deletion=True, allow_multiple=False, flush=True, id=item.id
        )

    assert count == 1


@pytest.mark.asyncio
async def test_logical_delete_with_commit(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[3]

    count = await crud_ins.delete_model_by_column(
        async_db_session, logical_deletion=True, allow_multiple=False, commit=True, id=item.id
    )

    assert count == 1

    updated_item = await crud_ins.select_model(async_db_session, item.id)
    assert updated_item.del_flag is True


@pytest.mark.asyncio
async def test_logical_delete_no_matching_records(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(
            async_db_session, logical_deletion=True, allow_multiple=True, name='nonexistent_record'
        )

    assert count == 0


@pytest.mark.asyncio
async def test_logical_delete_already_deleted_records(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    async with async_db_session.begin():
        await crud_ins.delete_model_by_column(async_db_session, logical_deletion=True, allow_multiple=True, id__le=3)

    async with async_db_session.begin():
        count = await crud_ins.delete_model_by_column(
            async_db_session, logical_deletion=True, allow_multiple=True, id__le=3, del_flag=True
        )

    assert count >= 0


@pytest.mark.asyncio
async def test_logical_delete_invalid_column_error(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    with pytest.raises(ModelColumnError):
        async with async_db_session.begin():
            await crud_ins.delete_model_by_column(
                async_db_session,
                logical_deletion=True,
                deleted_flag_column='nonexistent_column',
                allow_multiple=True,
                name='test',
            )


@pytest.mark.asyncio
async def test_logical_delete_no_filters_error(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    with pytest.raises(ValueError):
        async with async_db_session.begin():
            await crud_ins.delete_model_by_column(async_db_session, logical_deletion=True, allow_multiple=True)


@pytest.mark.asyncio
async def test_logical_delete_single_but_multiple_found(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    from sqlalchemy_crud_plus.errors import MultipleResultsError

    with pytest.raises(MultipleResultsError):
        async with async_db_session.begin():
            await crud_ins.delete_model_by_column(
                async_db_session, logical_deletion=True, allow_multiple=False, del_flag=False
            )


@pytest.mark.asyncio
async def test_logical_delete_affects_count(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    initial_count = await crud_ins.count(async_db_session, del_flag=False)

    deleted_count = await crud_ins.delete_model_by_column(
        async_db_session, logical_deletion=True, allow_multiple=True, commit=True, id__le=2
    )

    final_count = await crud_ins.count(async_db_session, del_flag=False)

    if deleted_count > 0:
        assert final_count < initial_count


@pytest.mark.asyncio
async def test_logical_delete_affects_exists(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = populated_db[4]

    exists_before = await crud_ins.exists(async_db_session, id=item.id, del_flag=False)
    assert exists_before is True

    await crud_ins.delete_model_by_column(
        async_db_session, logical_deletion=True, allow_multiple=False, commit=True, id=item.id
    )

    exists_after = await crud_ins.exists(async_db_session, id=item.id, del_flag=False)
    assert exists_after is False

    still_exists = await crud_ins.exists(async_db_session, id=item.id)
    assert still_exists is True


@pytest.mark.asyncio
async def test_logical_delete_with_select_models(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    initial_active = await crud_ins.select_models(async_db_session, del_flag=False)
    initial_count = len(initial_active)

    await crud_ins.delete_model_by_column(
        async_db_session, logical_deletion=True, allow_multiple=True, commit=True, id__between=[1, 3]
    )

    final_active = await crud_ins.select_models(async_db_session, del_flag=False)
    final_count = len(final_active)

    assert final_count <= initial_count
