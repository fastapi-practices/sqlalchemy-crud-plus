from datetime import datetime

import pytest

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus, QueryBuilderError, UnsafeWriteError
from tests.models.basic import Ins
from tests.models.relationship import RelPost, RelUser


@pytest.mark.asyncio
async def test_query_builder_filters_order_and_is_immutable(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    base = crud_ins.query(db).where(is_deleted=False)
    limited = base.order_by('-id').limit(2)

    all_items = await base.all()
    limited_items = await limited.all()

    assert len(all_items) >= len(limited_items)
    assert len(limited_items) == 2
    assert [item.id for item in limited_items] == sorted((item.id for item in limited_items), reverse=True)
    assert 'LIMIT' not in base.to_sql()


@pytest.mark.asyncio
async def test_query_builder_typed_lambda_filter_sort_and_aliases(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    base = (
        crud_ins.query(db)
        .where(lambda item: item.is_deleted.is_(False))
        .where(lambda item: item.name.contains('item_'))
        .where_if(False, lambda item: item.id < 0)
        .order_by(lambda item: item.id.desc())
    )
    items = await base.take(3).to_list()

    assert len(items) == 3
    assert all(item.is_deleted is False for item in items)
    assert [item.id for item in items] == sorted((item.id for item in items), reverse=True)
    assert await base.any(lambda item: item.id == items[0].id) is True
    assert (await base.single(lambda item: item.id == items[0].id)).id == items[0].id


@pytest.mark.asyncio
async def test_query_builder_typed_lambda_or_and_validation(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    selected_ids = [sample_ins[0].id, sample_ins[1].id]
    items = await (
        crud_ins.query(db)
        .where_or(
            lambda item: item.id == selected_ids[0],
            lambda item: item.id == selected_ids[1],
        )
        .or_if(False, lambda item: item.name == 'not-added')
        .to_list()
    )

    assert {item.id for item in items} == set(selected_ids)
    deleted_items = await crud_ins.query(db).where(lambda item: item.is_deleted).to_list()
    assert deleted_items and all(item.is_deleted is True for item in deleted_items)
    with pytest.raises(QueryBuilderError, match='instead of Python and/or'):
        crud_ins.query(db).where(lambda item: True)


@pytest.mark.asyncio
async def test_query_builder_projection_scalar_and_aggregate(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    rows = await crud_ins.query(db).where(is_deleted=False).select(Ins.id, Ins.name).order_by('id').all()
    names = await crud_ins.query(db).where(is_deleted=False).select(Ins.name).scalars()
    count = await crud_ins.query(db).where(is_deleted=False).select(func.count(Ins.id)).scalar_one()

    assert rows
    assert rows[0].id is not None
    assert rows[0].name.startswith('item_')
    assert all(name.startswith('item_') for name in names)
    assert count == len(rows)


@pytest.mark.asyncio
async def test_query_builder_typed_projection_and_aggregate_aliases(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    rows = await (
        crud_ins.query(db)
        .where(lambda item: item.is_deleted.is_(False))
        .select(lambda item: {'item_id': item.id, 'item_name': item.name})
        .order_by(lambda item: item.id)
        .to_list()
    )
    query = crud_ins.query(db).where(lambda item: item.is_deleted.is_(False))

    assert rows[0].item_id is not None
    assert rows[0].item_name.startswith('item_')
    assert await query.count(lambda item: item.id) == len(rows)
    assert await query.max(lambda item: item.id) >= await query.min(lambda item: item.id)
    assert await query.sum(lambda item: item.id) > 0
    assert await query.avg(lambda item: item.id) > 0


@pytest.mark.asyncio
async def test_query_builder_group_having_distinct(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    rows = await (
        crud_ins.query(db)
        .select(Ins.is_deleted, func.count(Ins.id).label('total'))
        .group_by(Ins.is_deleted)
        .having(func.count(Ins.id) > 0)
        .order_by(Ins.is_deleted)
        .all()
    )

    assert {row.is_deleted for row in rows} == {False, True}
    assert sum(row.total for row in rows) >= len(sample_ins)


@pytest.mark.asyncio
async def test_query_builder_paginate_count_and_exists(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    query = crud_ins.query(db).where(name__like='item_%').order_by('id').limit(1)
    page = await query.paginate(page=1, size=3)

    assert page.total >= len(sample_ins)
    assert len(page.items) == 3
    assert await query.exists() is True
    assert await crud_ins.query(db).where(name='missing-query-builder-name').exists() is False


@pytest.mark.asyncio
async def test_query_builder_join_and_projection(
    db: AsyncSession,
    rel_sample_data: dict,
    rel_crud_user: CRUDPlus[RelUser],
):
    rows = await (
        rel_crud_user.query(db)
        .join(RelPost, RelUser.id == RelPost.author_id)
        .select(RelUser.name, RelPost.title)
        .order_by(RelPost.id)
        .all()
    )

    assert len(rows) >= len(rel_sample_data['posts'])
    assert rows[0].name.startswith('user_')
    assert rows[0].title.startswith('Post ')


@pytest.mark.asyncio
async def test_query_builder_typed_join_and_relationship_load(
    db: AsyncSession,
    rel_sample_data: dict,
    rel_crud_user: CRUDPlus[RelUser],
):
    rows = await (
        rel_crud_user.query(db)
        .join(RelPost, lambda user, post: user.id == post.author_id)
        .where(lambda user, post: post.title.contains('Post'))
        .select(lambda user, post: (user.name, post.title))
        .order_by(lambda user, post: post.id)
        .to_list()
    )
    users = await rel_crud_user.query(db).load(lambda user: user.posts).unique().to_list()

    assert len(rows) >= len(rel_sample_data['posts'])
    assert all(row.title.startswith('Post ') for row in rows)
    assert any(user.posts for user in users)


@pytest.mark.asyncio
async def test_query_builder_cte_subquery_union_and_sql(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    left = crud_ins.query(db).where(Ins.id <= sample_ins[1].id).select(Ins.id)
    right = crud_ins.query(db).where(Ins.id > sample_ins[1].id).select(Ins.id)
    cte = left.cte('small_ids')
    subquery = right.subquery('large_ids')
    union_rows = await left.union_all(right).all()
    stmt = select(cte.c.id).where(cte.c.id.not_in(select(subquery.c.id)))

    assert union_rows
    assert 'UNION ALL' in left.union_all(right).to_sql()
    assert (await db.execute(stmt)).scalars().all()


@pytest.mark.asyncio
async def test_query_builder_query_terminal_update(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    item = Ins(name='chain-update-before', is_deleted=False)
    db.add(item)
    await db.flush()

    affected = await crud_ins.query(db).where(id=item.id).update({'name': 'chain-update-after'})

    assert affected == 1
    await db.refresh(item)
    assert item.name == 'chain-update-after'


@pytest.mark.asyncio
async def test_update_builder_atomic_returning_and_safety(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    item = Ins(name='chain-atomic', is_deleted=False, deleted=1)
    db.add(item)
    await db.flush()

    with pytest.raises(UnsafeWriteError):
        await crud_ins.update_query(db).set({'deleted__add': 1}).execute()

    returned = await crud_ins.update_query(db).where(id=item.id).set({'deleted__add': 1}).returning().execute()

    assert returned[0].id == item.id
    assert returned[0].deleted == 2


@pytest.mark.asyncio
async def test_typed_lambda_update_and_returning(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    item = Ins(name='typed-chain-update', is_deleted=False, deleted=2)
    db.add(item)
    await db.flush()

    returned = await (
        crud_ins.update_query(db)
        .where(lambda model: model.id == item.id)
        .set(lambda model: {model.name: 'typed-chain-updated', model.deleted: model.deleted + 3})
        .returning(lambda model: (model.id, model.name, model.deleted))
        .execute()
    )

    assert returned[0].id == item.id
    assert returned[0].name == 'typed-chain-updated'
    assert returned[0].deleted == 5


@pytest.mark.asyncio
async def test_query_builder_rejects_complex_write(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    with pytest.raises(QueryBuilderError):
        await crud_ins.query(db).where(is_deleted=False).limit(1).update({'name': 'unsafe-complex-write'})


@pytest.mark.asyncio
async def test_delete_builder_safety_and_returning(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    item = Ins(name='chain-delete', is_deleted=False)
    db.add(item)
    await db.flush()

    with pytest.raises(UnsafeWriteError):
        await crud_ins.delete_query(db).execute()

    returned = await crud_ins.delete_query(db).where(id=item.id).returning().execute()

    assert returned[0].id == item.id
    assert await crud_ins.query(db).where(id=item.id).exists() is False


@pytest.mark.asyncio
async def test_insert_builder_single_batch_and_returning(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    inserted = await (
        crud_ins.insert_query(db)
        .values(
            [
                {'name': 'chain-insert-1', 'is_deleted': False, 'created_time': datetime.now()},
                {'name': 'chain-insert-2', 'is_deleted': False, 'created_time': datetime.now()},
            ]
        )
        .returning()
        .execute()
    )

    assert [item.name for item in inserted] == ['chain-insert-1', 'chain-insert-2']


@pytest.mark.asyncio
async def test_upsert_builder_update_and_do_nothing(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    item = Ins(name='chain-upsert-before', is_deleted=False)
    db.add(item)
    await db.flush()

    updated = await (
        crud_ins.upsert_query(db)
        .values(
            {
                'id': item.id,
                'name': 'chain-upsert-after',
                'is_deleted': False,
                'created_time': item.created_time,
            }
        )
        .conflict_on('id')
        .update_columns('name')
        .returning()
        .execute()
    )
    ignored = await (
        crud_ins.upsert_query(db)
        .values(
            {
                'id': item.id,
                'name': 'must-not-win',
                'is_deleted': False,
                'created_time': item.created_time,
            }
        )
        .conflict_on('id')
        .do_nothing()
        .returning()
        .execute()
    )

    assert updated[0].name == 'chain-upsert-after'
    assert ignored == []


@pytest.mark.asyncio
async def test_typed_lambda_upsert_columns(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    item = Ins(name='typed-upsert-before', is_deleted=False)
    db.add(item)
    await db.flush()

    rows = await (
        crud_ins.upsert_query(db)
        .values(
            {
                'id': item.id,
                'name': 'typed-upsert-after',
                'is_deleted': False,
                'created_time': item.created_time,
            }
        )
        .conflict_on(lambda model: model.id)
        .update_columns(lambda model: model.name)
        .returning(lambda model: (model.id, model.name))
        .execute()
    )

    assert rows[0].id == item.id
    assert rows[0].name == 'typed-upsert-after'


@pytest.mark.asyncio
async def test_soft_delete_filter_applies_to_chain_reads_and_writes(db: AsyncSession, sample_ins: list[Ins]):
    crud = CRUDPlus(Ins, filter_deleted=True)
    deleted_item = next(item for item in sample_ins if item.is_deleted)
    visible = await crud.query(db).all()

    affected = await crud.update_query(db).where(id=deleted_item.id).set({'name': 'must-not-change'}).execute()
    included = await crud.query(db).include_deleted().where(id=deleted_item.id).one()

    assert all(item.is_deleted is False for item in visible)
    assert affected == 0
    assert included.name != 'must-not-change'


@pytest.mark.asyncio
async def test_soft_delete_filter_does_not_satisfy_write_safety(db: AsyncSession):
    crud = CRUDPlus(Ins, filter_deleted=True)

    with pytest.raises(UnsafeWriteError):
        await crud.update_query(db).set({'name': 'unsafe'}).execute()
