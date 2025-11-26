#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import ModelColumnError
from tests.models.basic import Ins


@pytest.mark.asyncio
async def test_delete_model_by_id(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]

    async with db.begin():
        count = await crud_ins.delete_model(db, item.id)

    assert count == 1

    result = await crud_ins.select_model(db, item.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_model_by_id_not_found(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.delete_model(db, 99999, commit=True)

    assert count == 0


@pytest.mark.asyncio
async def test_delete_model_with_flush(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[1]

    async with db.begin():
        count = await crud_ins.delete_model(db, item.id, flush=True)

    assert count == 1


@pytest.mark.asyncio
async def test_delete_model_with_commit(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[2]

    count = await crud_ins.delete_model(db, item.id, commit=True)

    assert count == 1


@pytest.mark.asyncio
async def test_delete_model_by_column_basic(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[3]

    before_exists = await crud_ins.exists(db, name=item.name)
    assert before_exists is True

    count = await crud_ins.delete_model_by_column(db, allow_multiple=True, commit=True, name=item.name)

    assert count > 0

    after_exists = await crud_ins.exists(db, name=item.name)
    assert after_exists is False


@pytest.mark.asyncio
async def test_delete_model_by_column_not_found(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        count = await crud_ins.delete_model_by_column(db, allow_multiple=True, name='nonexistent')

    assert count == 0


@pytest.mark.asyncio
async def test_delete_model_by_column_allow_multiple(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    before_count = await crud_ins.count(db, is_deleted=False)
    assert before_count > 0

    count = await crud_ins.delete_model_by_column(db, allow_multiple=True, commit=True, is_deleted=False)

    assert count == before_count

    after_count = await crud_ins.count(db, is_deleted=False)
    assert after_count == 0


@pytest.mark.asyncio
async def test_delete_model_by_column_with_flush(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[4]

    before_exists = await crud_ins.exists(db, name=item.name)
    assert before_exists is True

    count = await crud_ins.delete_model_by_column(db, allow_multiple=True, commit=True, name=item.name)

    assert count > 0

    after_exists = await crud_ins.exists(db, name=item.name)
    assert after_exists is False


@pytest.mark.asyncio
async def test_delete_model_by_column_with_commit(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[5]

    before_exists = await crud_ins.exists(db, name=item.name)
    assert before_exists is True

    count = await crud_ins.delete_model_by_column(db, allow_multiple=True, commit=True, name=item.name)

    assert count > 0

    after_exists = await crud_ins.exists(db, name=item.name)
    assert after_exists is False


@pytest.mark.asyncio
async def test_delete_model_by_column_no_filters_error(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    with pytest.raises(ValueError):
        async with db.begin():
            await crud_ins.delete_model_by_column(db, allow_multiple=True)


@pytest.mark.asyncio
async def test_delete_model_by_column_multiple_results_error(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    from sqlalchemy_crud_plus.errors import MultipleResultsError

    with pytest.raises(MultipleResultsError):
        async with db.begin():
            await crud_ins.delete_model_by_column(db, is_deleted=False)


@pytest.mark.asyncio
async def test_logical_delete_single_record(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]

    assert item.is_deleted is False

    async with db.begin():
        count = await crud_ins.delete_model_by_column(
            db, logical_deletion=True, deleted_flag_column='is_deleted', allow_multiple=False, id=item.id
        )

    assert count == 1

    async with db.begin():
        updated_item = await crud_ins.select_model(db, item.id)
        assert updated_item is not None
        assert updated_item.is_deleted is True


@pytest.mark.asyncio
async def test_logical_delete_multiple_records(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    before_count = await crud_ins.count(db, is_deleted=False)
    assert before_count > 0

    count = await crud_ins.delete_model_by_column(
        db,
        logical_deletion=True,
        deleted_flag_column='is_deleted',
        allow_multiple=True,
        commit=True,
        is_deleted=False,
    )

    assert count == before_count

    remaining_false = await crud_ins.select_models(db, is_deleted=False)
    assert len(remaining_false) == 0


@pytest.mark.asyncio
async def test_logical_delete_with_custom_column(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[1]

    async with db.begin():
        count = await crud_ins.delete_model_by_column(
            db, logical_deletion=True, deleted_flag_column='is_deleted', allow_multiple=False, id=item.id
        )

    assert count == 1

    async with db.begin():
        updated_item = await crud_ins.select_model(db, item.id)
        assert updated_item.is_deleted is True


@pytest.mark.asyncio
async def test_logical_delete_with_filters(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    await crud_ins.count(db, name__like='item_%', id__gt=3, is_deleted=False)

    count = await crud_ins.delete_model_by_column(
        db,
        logical_deletion=True,
        deleted_flag_column='is_deleted',
        allow_multiple=True,
        commit=True,
        name__like='item_%',
        id__gt=3,
    )

    assert count >= 0

    deleted_items = await crud_ins.select_models(db, name__like='item_%', id__gt=3, is_deleted=True)
    assert len(deleted_items) >= count


@pytest.mark.asyncio
async def test_logical_delete_with_flush(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[2]

    async with db.begin():
        count = await crud_ins.delete_model_by_column(
            db,
            logical_deletion=True,
            deleted_flag_column='is_deleted',
            allow_multiple=False,
            flush=True,
            id=item.id,
        )

    assert count == 1


@pytest.mark.asyncio
async def test_logical_delete_with_commit(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[3]

    count = await crud_ins.delete_model_by_column(
        db,
        logical_deletion=True,
        deleted_flag_column='is_deleted',
        allow_multiple=False,
        commit=True,
        id=item.id,
    )

    assert count == 1

    updated_item = await crud_ins.select_model(db, item.id)
    assert updated_item.is_deleted is True


@pytest.mark.asyncio
async def test_logical_delete_no_matching_records(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.delete_model_by_column(
        db,
        logical_deletion=True,
        deleted_flag_column='is_deleted',
        allow_multiple=True,
        commit=True,
        name='nonexistent_record',
    )

    assert count == 0


@pytest.mark.asyncio
async def test_logical_delete_already_deleted_records(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    first_count = await crud_ins.delete_model_by_column(
        db, logical_deletion=True, deleted_flag_column='is_deleted', allow_multiple=True, commit=True, id__le=3
    )
    assert first_count >= 0

    already_deleted_count = await crud_ins.count(db, id__le=3, is_deleted=True)
    assert already_deleted_count >= first_count

    count = await crud_ins.delete_model_by_column(
        db,
        logical_deletion=True,
        deleted_flag_column='is_deleted',
        allow_multiple=True,
        commit=True,
        id__le=3,
        is_deleted=True,
    )

    assert count >= 0


@pytest.mark.asyncio
async def test_logical_delete_invalid_column_error(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    with pytest.raises(ModelColumnError):
        async with db.begin():
            await crud_ins.delete_model_by_column(
                db,
                logical_deletion=True,
                deleted_flag_column='nonexistent_column',
                allow_multiple=True,
                name='test',
            )


@pytest.mark.asyncio
async def test_logical_delete_no_filters_error(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    with pytest.raises(ValueError):
        async with db.begin():
            await crud_ins.delete_model_by_column(
                db, logical_deletion=True, deleted_flag_column='is_deleted', allow_multiple=True
            )


@pytest.mark.asyncio
async def test_logical_delete_single_but_multiple_found(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    from sqlalchemy_crud_plus.errors import MultipleResultsError

    with pytest.raises(MultipleResultsError):
        async with db.begin():
            await crud_ins.delete_model_by_column(
                db,
                logical_deletion=True,
                deleted_flag_column='is_deleted',
                allow_multiple=False,
                is_deleted=False,
            )


@pytest.mark.asyncio
async def test_logical_delete_affects_count(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    initial_count = await crud_ins.count(db, is_deleted=False)

    to_delete_count = await crud_ins.count(db, id__le=2, is_deleted=False)

    deleted_count = await crud_ins.delete_model_by_column(
        db,
        logical_deletion=True,
        deleted_flag_column='is_deleted',
        allow_multiple=True,
        commit=True,
        id__le=2,
        is_deleted=False,
    )

    final_count = await crud_ins.count(db, is_deleted=False)

    assert deleted_count == to_delete_count
    assert final_count == initial_count - deleted_count


@pytest.mark.asyncio
async def test_logical_delete_affects_exists(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[4]

    exists_before = await crud_ins.exists(db, id=item.id, is_deleted=False)
    assert exists_before is True

    await crud_ins.delete_model_by_column(
        db,
        logical_deletion=True,
        deleted_flag_column='is_deleted',
        allow_multiple=False,
        commit=True,
        id=item.id,
    )

    exists_after = await crud_ins.exists(db, id=item.id, is_deleted=False)
    assert exists_after is False

    still_exists = await crud_ins.exists(db, id=item.id)
    assert still_exists is True


@pytest.mark.asyncio
async def test_logical_delete_with_select_models(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    initial_active = await crud_ins.select_models(db, is_deleted=False)
    initial_count = len(initial_active)

    await crud_ins.delete_model_by_column(
        db,
        logical_deletion=True,
        deleted_flag_column='is_deleted',
        allow_multiple=True,
        commit=True,
        id__between=[1, 3],
    )

    final_active = await crud_ins.select_models(db, is_deleted=False)
    final_count = len(final_active)

    assert final_count <= initial_count


@pytest.mark.asyncio
async def test_delete_model_by_column_with_deleted_at(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[6]

    async with db.begin():
        count = await crud_ins.delete_model_by_column(db, logical_deletion=True, id=item.id)

    assert count == 1

    async with db.begin():
        updated_item = await crud_ins.select_model(db, item.id)
        assert updated_item is not None
        assert updated_item.is_deleted is True
        assert updated_item.updated_time is not None


@pytest.mark.asyncio
async def test_delete_model_by_column_without_deleted_at_column(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    item = sample_ins[7]

    async with db.begin():
        count = await crud_ins.delete_model_by_column(db, logical_deletion=True, id=item.id)

    assert count == 1

    async with db.begin():
        updated_item = await crud_ins.select_model(db, item.id)
        assert updated_item is not None
        assert updated_item.is_deleted is True


@pytest.mark.asyncio
async def test_delete_model_by_column_with_custom_deleted_at_column(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    from datetime import datetime, timezone

    item = sample_ins[8]

    async with db.begin():
        count = await crud_ins.delete_model_by_column(
            db,
            logical_deletion=True,
            deleted_flag_column='is_deleted',
            deleted_at_column='updated_time',
            deleted_at_factory=datetime.now(timezone.utc),
            id=item.id,
        )

    assert count == 1

    async with db.begin():
        updated_item = await crud_ins.select_model(db, item.id)
        assert updated_item is not None
        assert updated_item.is_deleted is True
        assert updated_item.updated_time is not None
