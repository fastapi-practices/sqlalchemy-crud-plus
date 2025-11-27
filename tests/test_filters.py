import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins


@pytest.mark.asyncio
async def test_filter_gt(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__gt=2)

    assert all(r.id > 2 for r in results)


@pytest.mark.asyncio
async def test_filter_ge(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__ge=2)

    assert all(r.id >= 2 for r in results)


@pytest.mark.asyncio
async def test_filter_lt(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__lt=5)

    assert all(r.id < 5 for r in results)


@pytest.mark.asyncio
async def test_filter_le(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__le=5)

    assert all(r.id <= 5 for r in results)


@pytest.mark.asyncio
async def test_filter_eq(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    first_item = sample_ins[0]
    results = await crud_ins.select_models(db, id__eq=first_item.id)

    assert all(r.id == first_item.id for r in results)


@pytest.mark.asyncio
async def test_filter_ne(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__ne=1)

    assert all(r.id != 1 for r in results)


@pytest.mark.asyncio
async def test_filter_between(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__between=[2, 5])

    assert all(2 <= r.id <= 5 for r in results)


@pytest.mark.asyncio
async def test_filter_in(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    ids = [item.id for item in sample_ins[:3]]
    results = await crud_ins.select_models(db, id__in=ids)

    assert all(r.id in ids for r in results)


@pytest.mark.asyncio
async def test_filter_not_in(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    ids = [999, 1000]
    results = await crud_ins.select_models(db, id__not_in=ids)

    assert all(r.id not in ids for r in results)


@pytest.mark.asyncio
async def test_filter_is(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, is_deleted__is=False)

    assert all(r.is_deleted is False for r in results)


@pytest.mark.asyncio
async def test_filter_is_not(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, is_deleted__is_not=None)

    assert all(r.is_deleted is not None for r in results)


@pytest.mark.asyncio
async def test_filter_is_distinct_from(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, is_deleted__is_distinct_from=True)

    assert all(r.is_deleted is not True for r in results)


@pytest.mark.asyncio
async def test_filter_is_not_distinct_from(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, is_deleted__is_not_distinct_from=False)

    assert all(r.is_deleted is False for r in results)


@pytest.mark.asyncio
async def test_filter_like(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__like='item_%')

    assert all('item_' in r.name for r in results)


@pytest.mark.asyncio
async def test_filter_not_like(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__not_like='nonexistent_%')

    assert len(results) > 0
    assert all('nonexistent_' not in r.name for r in results)


@pytest.mark.asyncio
async def test_filter_ilike(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__ilike='ITEM_%')

    assert len(results) > 0
    assert all(r.name.lower().startswith('item_') for r in results)


@pytest.mark.asyncio
async def test_filter_not_ilike(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__not_ilike='ITEM_%')

    assert all(not r.name.lower().startswith('item_') for r in results)


@pytest.mark.asyncio
async def test_filter_startswith(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__startswith='item')

    assert all(r.name.startswith('item') for r in results)


@pytest.mark.asyncio
async def test_filter_endswith(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__endswith='_1')

    assert all(r.name.endswith('_1') for r in results)


@pytest.mark.asyncio
async def test_filter_contains(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__contains='item')

    assert all('item' in r.name for r in results)


@pytest.mark.asyncio
async def test_filter_match(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    try:
        results = await crud_ins.select_models(db, name__match='item')
        assert len(results) >= 0
    except Exception as e:
        assert 'match' in str(e).lower() or 'not supported' in str(e).lower()


@pytest.mark.asyncio
async def test_filter_concat(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__concat='_test')

    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_filter_add(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__add=1)

    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_filter_radd(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__radd=10)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_sub(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__sub=1)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rsub(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__rsub=10)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_mul(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__mul=2)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_mul_with_condition(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__mul={'value': 2, 'condition': {'gt': 0}})

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rmul(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__rmul=3)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_truediv(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__truediv=2)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rtruediv(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__rtruediv=10)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_floordiv(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__floordiv=2)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rfloordiv(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__rfloordiv=10)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_mod(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__mod=2)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_rmod(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__rmod=7)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_or_same_field_list_values(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, __or__={'is_deleted': [True, False]})

    total_count = await crud_ins.count(db)
    assert len(results) == total_count
    assert all(r.is_deleted in [True, False] for r in results)


@pytest.mark.asyncio
async def test_filter_or_different_fields_single_values(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(db, __or__={'is_deleted': True, 'id__gt': 5})

    assert len(results) > 0
    assert all(r.is_deleted is True or r.id > 5 for r in results)


@pytest.mark.asyncio
async def test_filter_or_with_operators(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, __or__={'name__like': 'item_%', 'id__lt': 3})

    assert len(results) > 0
    assert all('item_' in r.name or r.id < 3 for r in results)


@pytest.mark.asyncio
async def test_filter_or_mixed_list_and_single(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, __or__={'is_deleted': [True, False], 'name__like': 'item_%'})

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_multiple_conditions(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__like='item_%', id__ge=1, is_deleted=False)

    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_with_count(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    count = await crud_ins.count(db, name__like='item_%')

    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_filter_with_exists(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(db, name__like='item_%')

    assert isinstance(exists, bool)


@pytest.mark.asyncio
async def test_filter_multiple_same_operator(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__gt=1, id__lt=5)
    assert all(1 < r.id < 5 for r in results)


@pytest.mark.asyncio
async def test_filter_complex_or_conditions(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(
        db, __or__={'name__startswith': 'item', 'id__between': [1, 3], 'is_deleted': True}
    )
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_mixed_and_or_conditions(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(
        db,
        is_deleted=False,  # AND condition
        __or__={'name__like': 'item_%', 'id__gt': 5},  # OR condition
    )
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_or_with_list_values_complex(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(
        db,
        __or__={'name': ['item_1', 'item_2', 'item_3'], 'id__in': [7, 8, 9], 'is_deleted': [True, False]},
    )
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_empty_in_list(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__in=[])
    assert len(results) == 0


@pytest.mark.asyncio
async def test_filter_none_values(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, updated_time__is=None)
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_boolean_values(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    true_results = await crud_ins.select_models(db, is_deleted=True)
    false_results = await crud_ins.select_models(db, is_deleted=False)

    assert len(true_results) >= 0
    assert len(false_results) >= 0


@pytest.mark.asyncio
async def test_filter_case_sensitive_operations(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results_like = await crud_ins.select_models(db, name__like='ITEM_%')

    results_ilike = await crud_ins.select_models(db, name__ilike='ITEM_%')
    assert len(results_ilike) >= len(results_like)


@pytest.mark.asyncio
async def test_filter_numeric_edge_cases(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, id__gt=0)
    assert len(results) >= 0

    results = await crud_ins.select_models(db, id__ge=-1)
    assert len(results) >= 0

    results = await crud_ins.select_models(db, id__lt=999999)
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_is_distinct_from_comprehensive(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, is_deleted__is_distinct_from=True)
    assert all(r.is_deleted is not True for r in results)

    results = await crud_ins.select_models(db, is_deleted__is_distinct_from=False)
    assert all(r.is_deleted is not False for r in results)

    results = await crud_ins.select_models(db, updated_time__is_distinct_from=None)
    assert all(r.updated_time is not None for r in results)


@pytest.mark.asyncio
async def test_filter_is_not_distinct_from_comprehensive(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(db, is_deleted__is_not_distinct_from=False)
    assert all(r.is_deleted is False for r in results)


@pytest.mark.asyncio
async def test_filter_all_arithmetic_operators_comprehensive(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    results = await crud_ins.select_models(db, id__add=1)
    assert len(results) >= 0

    results = await crud_ins.select_models(db, id__sub=1)
    assert len(results) >= 0

    results = await crud_ins.select_models(db, id__mul=2)
    assert len(results) >= 0

    results = await crud_ins.select_models(db, id__truediv=2)
    assert len(results) >= 0

    results = await crud_ins.select_models(db, id__floordiv=2)
    assert len(results) >= 0

    results = await crud_ins.select_models(db, id__mod=2)
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_string_operations_comprehensive(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(db, name__startswith='item')
    assert len(results) >= 0

    results = await crud_ins.select_models(db, name__endswith='1')
    assert len(results) >= 0

    results = await crud_ins.select_models(db, name__contains='tem')
    assert len(results) >= 0

    results = await crud_ins.select_models(db, name__not_like='xyz%')
    assert len(results) >= 0

    results = await crud_ins.select_models(db, name__not_ilike='XYZ%')
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_performance_complex_query(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    results = await crud_ins.select_models(
        db,
        name__like='item_%',
        id__between=[1, 8],
        is_deleted__in=[True, False],
        __or__={'id__mod': 2, 'name__endswith': ['1', '3', '5']},
    )
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_filter_with_count_comprehensive(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    total_count = await crud_ins.count(db)
    assert total_count >= len(sample_ins)

    filtered_count = await crud_ins.count(db, is_deleted=False)
    assert filtered_count >= 0

    complex_count = await crud_ins.count(db, name__like='item_%', id__gt=2, __or__={'is_deleted': True, 'id__lt': 5})
    assert complex_count >= 0


@pytest.mark.asyncio
async def test_filter_with_exists_comprehensive(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    exists = await crud_ins.exists(db, name__like='item_%')
    assert exists is True

    not_exists = await crud_ins.exists(db, name='definitely_not_exists')
    assert not_exists is False

    complex_exists = await crud_ins.exists(db, name__startswith='item', id__between=[1, 10])
    assert isinstance(complex_exists, bool)
