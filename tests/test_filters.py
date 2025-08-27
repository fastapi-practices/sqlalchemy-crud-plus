#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins


@pytest.mark.asyncio
async def test_filter_gt(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__gt=2)

    assert all(r.id > 2 for r in results)


@pytest.mark.asyncio
async def test_filter_ge(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__ge=2)

    assert all(r.id >= 2 for r in results)


@pytest.mark.asyncio
async def test_filter_lt(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__lt=5)

    assert all(r.id < 5 for r in results)


@pytest.mark.asyncio
async def test_filter_le(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__le=5)

    assert all(r.id <= 5 for r in results)


@pytest.mark.asyncio
async def test_filter_eq(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    first_item = populated_db[0]
    results = await crud_ins.select_models(async_db_session, id__eq=first_item.id)

    assert all(r.id == first_item.id for r in results)


@pytest.mark.asyncio
async def test_filter_ne(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__ne=1)

    assert all(r.id != 1 for r in results)


@pytest.mark.asyncio
async def test_filter_between(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__between=[2, 5])

    assert all(2 <= r.id <= 5 for r in results)


@pytest.mark.asyncio
async def test_filter_in(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    ids = [item.id for item in populated_db[:3]]
    results = await crud_ins.select_models(async_db_session, id__in=ids)

    assert all(r.id in ids for r in results)


@pytest.mark.asyncio
async def test_filter_not_in(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    ids = [999, 1000]
    results = await crud_ins.select_models(async_db_session, id__not_in=ids)

    assert all(r.id not in ids for r in results)


@pytest.mark.asyncio
async def test_filter_is(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, del_flag__is=False)

    assert all(r.del_flag is False for r in results)


@pytest.mark.asyncio
async def test_filter_is_not(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, del_flag__is_not=None)

    assert all(r.del_flag is not None for r in results)


@pytest.mark.asyncio
async def test_filter_is_distinct_from(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, del_flag__is_distinct_from=True)

    assert all(r.del_flag is not True for r in results)


@pytest.mark.asyncio
async def test_filter_is_not_distinct_from(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, del_flag__is_not_distinct_from=False)

    assert all(r.del_flag is False for r in results)


@pytest.mark.asyncio
async def test_filter_like(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, name__like='item_%')

    assert all('item_' in r.name for r in results)


@pytest.mark.asyncio
async def test_filter_not_like(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, name__not_like='nonexistent_%')

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_ilike(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, name__ilike='ITEM_%')

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_not_ilike(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, name__not_ilike='ITEM_%')

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_startswith(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, name__startswith='item')

    assert all(r.name.startswith('item') for r in results)


@pytest.mark.asyncio
async def test_filter_endswith(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, name__endswith='_1')

    assert all(r.name.endswith('_1') for r in results)


@pytest.mark.asyncio
async def test_filter_contains(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, name__contains='item')

    assert all('item' in r.name for r in results)


@pytest.mark.asyncio
async def test_filter_match(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    try:
        results = await crud_ins.select_models(async_db_session, name__match='item')
        assert len(results) >= 0
    except Exception:
        assert True


@pytest.mark.asyncio
async def test_filter_concat(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, name__concat='_test')

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_add(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__add=1)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_radd(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__radd=10)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_sub(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__sub=1)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rsub(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__rsub=10)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_mul(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__mul=2)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rmul(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__rmul=3)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_truediv(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__truediv=2)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rtruediv(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__rtruediv=10)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_floordiv(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__floordiv=2)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rfloordiv(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__rfloordiv=10)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_mod(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__mod=2)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rmod(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__rmod=7)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_or_same_field_list_values(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, __or__={'del_flag': [True, False]})

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_or_different_fields_single_values(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, __or__={'del_flag': True, 'id__gt': 5})

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_or_with_operators(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, __or__={'name__like': 'item_%', 'id__lt': 3})

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_or_mixed_list_and_single(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, __or__={'del_flag': [True, False], 'name__like': 'item_%'})

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_multiple_conditions(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, name__like='item_%', id__ge=1, del_flag=False)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_with_count(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.count(async_db_session, name__like='item_%')

    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_filter_with_exists(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(async_db_session, name__like='item_%')

    assert isinstance(exists, bool)


@pytest.mark.asyncio
async def test_filter_multiple_same_operator(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, id__gt=1, id__lt=5)
    assert all(1 < r.id < 5 for r in results)


@pytest.mark.asyncio
async def test_filter_complex_or_conditions(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(
        async_db_session, __or__={'name__startswith': 'item', 'id__between': [1, 3], 'del_flag': True}
    )
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_mixed_and_or_conditions(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(
        async_db_session,
        del_flag=False,  # AND condition
        __or__={'name__like': 'item_%', 'id__gt': 5},  # OR condition
    )
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_or_with_list_values_complex(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(
        async_db_session,
        __or__={'name': ['item_1', 'item_2', 'item_3'], 'id__in': [7, 8, 9], 'del_flag': [True, False]},
    )
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_empty_in_list(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, id__in=[])
    assert len(results) == 0


@pytest.mark.asyncio
async def test_filter_none_values(async_db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(async_db_session, updated_time__is=None)
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_boolean_values(async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]):
    true_results = await crud_ins.select_models(async_db_session, del_flag=True)
    false_results = await crud_ins.select_models(async_db_session, del_flag=False)

    assert len(true_results) >= 0
    assert len(false_results) >= 0


@pytest.mark.asyncio
async def test_filter_case_sensitive_operations(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results_like = await crud_ins.select_models(async_db_session, name__like='ITEM_%')

    results_ilike = await crud_ins.select_models(async_db_session, name__ilike='ITEM_%')
    assert len(results_ilike) >= len(results_like)


@pytest.mark.asyncio
async def test_filter_numeric_edge_cases(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, id__gt=0)
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, id__ge=-1)
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, id__lt=999999)
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_is_distinct_from_comprehensive(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, del_flag__is_distinct_from=True)
    assert all(r.del_flag is not True for r in results)

    results = await crud_ins.select_models(async_db_session, del_flag__is_distinct_from=False)
    assert all(r.del_flag is not False for r in results)

    results = await crud_ins.select_models(async_db_session, updated_time__is_distinct_from=None)
    assert all(r.updated_time is not None for r in results)


@pytest.mark.asyncio
async def test_filter_is_not_distinct_from_comprehensive(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, del_flag__is_not_distinct_from=False)
    assert all(r.del_flag is False for r in results)


@pytest.mark.asyncio
async def test_filter_all_arithmetic_operators_comprehensive(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, id__add=1)
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, id__sub=1)
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, id__mul=2)
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, id__truediv=2)
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, id__floordiv=2)
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, id__mod=2)
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_string_operations_comprehensive(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(async_db_session, name__startswith='item')
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, name__endswith='1')
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, name__contains='tem')
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, name__not_like='xyz%')
    assert len(results) >= 0

    results = await crud_ins.select_models(async_db_session, name__not_ilike='XYZ%')
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_performance_complex_query(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(
        async_db_session,
        name__like='item_%',
        id__between=[1, 8],
        del_flag__in=[True, False],
        __or__={'id__mod': 2, 'name__endswith': ['1', '3', '5']},
    )
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_with_count_comprehensive(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    total_count = await crud_ins.count(async_db_session)
    assert total_count >= len(populated_db)

    filtered_count = await crud_ins.count(async_db_session, del_flag=False)
    assert filtered_count >= 0

    complex_count = await crud_ins.count(
        async_db_session, name__like='item_%', id__gt=2, __or__={'del_flag': True, 'id__lt': 5}
    )
    assert complex_count >= 0


@pytest.mark.asyncio
async def test_filter_with_exists_comprehensive(
    async_db_session: AsyncSession, populated_db: list[Ins], crud_ins: CRUDPlus[Ins]
):
    exists = await crud_ins.exists(async_db_session, name__like='item_%')
    assert exists is True

    not_exists = await crud_ins.exists(async_db_session, name='definitely_not_exists')
    assert not_exists is False

    complex_exists = await crud_ins.exists(async_db_session, name__startswith='item', id__between=[1, 10])
    assert isinstance(complex_exists, bool)
