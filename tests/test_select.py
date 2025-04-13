#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy import Select

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Ins


@pytest.mark.asyncio
async def test_count(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.count(session, id=i)
            assert result == 1


@pytest.mark.asyncio
async def test_count_filters(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.count(session, [Ins.id == i])
            assert result == 1


@pytest.mark.asyncio
async def test_exists(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.exists(session, id=i)
            assert result is True


@pytest.mark.asyncio
async def test_exists_filters(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.exists(session, [Ins.id == i])
            assert result is True


@pytest.mark.asyncio
async def test_select_model(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.select_model(session, i)
            assert result.name == f'name_{i}'


@pytest.mark.asyncio
async def test_select_model_by_column(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.select_model_by_column(session, name=f'name_{i}')
            assert result.name == f'name_{i}'


@pytest.mark.asyncio
async def test_select_model_by_column_with_and(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        for i in range(1, 10):
            result = await crud.select_model_by_column(session, id=i, name=f'name_{i}')
            assert result.name == f'name_{i}'


@pytest.mark.asyncio
async def test_select_model_by_column_with_gt(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__gt=1)
        assert result.id == 2


@pytest.mark.asyncio
async def test_select_model_by_column_with_lt(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__lt=1)
        assert result is None


@pytest.mark.asyncio
async def test_select_model_by_column_with_gte(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__ge=1)
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_lte(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__le=1)
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_eq(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__eq=1)
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_ne(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__ne=1)
        assert result.id == 2


@pytest.mark.asyncio
async def test_select_model_by_column_with_between(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__between=(0, 10))
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_is(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, del_flag__is=False)
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_is_not(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, del_flag__is_not=True)
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_is_distinct_from(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, del_flag__is_distinct_from=True)
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_is_not_distinct_from(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, del_flag__is_not_distinct_from=True)
        assert result is None


@pytest.mark.asyncio
async def test_select_model_by_column_with_like(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, name__like='name%')
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_not_like(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, name__not_like='name%')
        assert result is None


@pytest.mark.asyncio
async def test_select_model_by_column_with_ilike(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, name__ilike='NAME%')
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_not_ilike(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, name__not_ilike='NAME%')
        assert result is None


@pytest.mark.asyncio
async def test_select_model_by_column_with_startwith(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, name__startswith='name')
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_endwith(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, name__endswith='1')
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_contains(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, name__contains='name')
        assert result.id == 1


@pytest.mark.asyncio
@pytest.mark.skip(reason='match not available in sqlite')
async def test_select_model_by_column_with_match(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, name__match='name')
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_concat(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(
            session, name__concat={'value': '_concat', 'condition': {'eq': 'name_1_concat'}}
        )
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_add_string(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(
            session, name__add={'value': '_add', 'condition': {'eq': 'name_1_add'}}
        )
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_radd_string(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(
            session, name__radd={'value': 'radd_', 'condition': {'eq': 'radd_name_1'}}
        )
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_add_number(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__add={'value': 1, 'condition': {'eq': 2}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_radd_number(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__radd={'value': 1, 'condition': {'eq': 2}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_sub(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__sub={'value': 1, 'condition': {'eq': 0}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_rsub(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__rsub={'value': 2, 'condition': {'eq': 1}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_mul(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__mul={'value': 1, 'condition': {'eq': 1}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_rmul(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__rmul={'value': 1, 'condition': {'eq': 1}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_truediv(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__truediv={'value': 1, 'condition': {'eq': 1}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_rtruediv(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__rtruediv={'value': 1, 'condition': {'eq': 1}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_floordiv(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__floordiv={'value': 1, 'condition': {'eq': 1}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_rfloordiv(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__rfloordiv={'value': 1, 'condition': {'eq': 1}})
        assert result is not None


@pytest.mark.asyncio
async def test_select_model_by_column_with_mod(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__mod={'value': 1, 'condition': {'eq': 0}})
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_rmod(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__rmod={'value': 1, 'condition': {'eq': 0}})
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_in(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__in=(1, 2, 3, 4, 5, 6, 7, 8, 9))
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_not_in(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__not_in=(1, 2, 3, 4, 5, 6, 7, 8, 9))
        assert result is None


@pytest.mark.asyncio
async def test_select_model_by_column_with_or(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__or={'le': 1, 'eq': 1})
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with_mor(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(session, id__mor={'eq': [1, 2, 3, 4, 5, 6, 7, 8, 9]})
        assert result.id == 1


@pytest.mark.asyncio
async def test_select_model_by_column_with___gor__(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_model_by_column(
            session,
            __gor__=[
                {'id__eq': 1},
                {'name__mor': {'endswith': ['1', '2']}},
                {'id__mul': {'value': 1, 'condition': {'eq': 1}}},
            ],
        )
        assert result.id == 1


@pytest.mark.asyncio
async def test_select(create_test_model):
    crud = CRUDPlus(Ins)
    result = await crud.select()
    assert isinstance(result, Select)


@pytest.mark.asyncio
async def test_select_models(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_models(session)
        assert len(result) == 9


@pytest.mark.asyncio
async def test_select_order(create_test_model):
    crud = CRUDPlus(Ins)
    result = await crud.select_order(sort_columns='name')
    assert isinstance(result, Select)


@pytest.mark.asyncio
async def test_select_models_order_default_asc(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_models_order(session, ['id', 'name'])
        assert result[0].id == 1


@pytest.mark.asyncio
async def test_select_models_order_desc(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_models_order(session, ['id', 'name'], ['desc', 'desc'])
        assert result[0].id == 9


@pytest.mark.asyncio
async def test_select_models_order_asc_and_desc(create_test_model, async_db_session):
    async with async_db_session() as session:
        crud = CRUDPlus(Ins)
        result = await crud.select_models_order(session, ['id', 'name'], ['asc', 'desc'])
        assert result[0].id == 1
