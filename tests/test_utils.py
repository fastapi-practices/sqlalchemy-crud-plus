#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy import select
from sqlalchemy.orm import aliased

from sqlalchemy_crud_plus.errors import (
    ColumnSortError,
    JoinConditionError,
    LoadingStrategyError,
    ModelColumnError,
    SelectOperatorError,
)
from sqlalchemy_crud_plus.utils import (
    _create_and_filters,
    _create_arithmetic_filters,
    _create_or_filters,
    apply_join_conditions,
    apply_sorting,
    build_load_strategies,
    get_column,
    get_sqlalchemy_filter,
    parse_filters,
)
from tests.models.basic import Ins
from tests.models.relations import RelUser


def test_get_column_valid_field():
    column = get_column(Ins, 'name')

    assert column is not None


def test_get_column_invalid_field():
    with pytest.raises(ModelColumnError):
        get_column(Ins, 'nonexistent_column')


def test_get_column_with_aliased_model():
    aliased_ins = aliased(Ins)
    column = get_column(aliased_ins, 'name')

    assert column is not None


def test_get_sqlalchemy_filter_basic_operators():
    gt_filter = get_sqlalchemy_filter('gt', 5)
    like_filter = get_sqlalchemy_filter('like', 'test%')

    assert gt_filter is not None
    assert like_filter is not None


def test_get_sqlalchemy_filter_in_valid():
    in_filter = get_sqlalchemy_filter('in', [1, 2, 3])

    assert in_filter is not None


def test_get_sqlalchemy_filter_in_invalid_value():
    with pytest.raises(SelectOperatorError):
        get_sqlalchemy_filter('in', 'invalid')


def test_get_sqlalchemy_filter_between_valid():
    between_filter = get_sqlalchemy_filter('between', [1, 10])

    assert between_filter is not None


def test_get_sqlalchemy_filter_between_invalid_value():
    with pytest.raises(SelectOperatorError):
        get_sqlalchemy_filter('between', 'invalid')


def test_get_sqlalchemy_filter_not_in_valid():
    not_in_filter = get_sqlalchemy_filter('not_in', [1, 2, 3])

    assert not_in_filter is not None


def test_get_sqlalchemy_filter_not_in_invalid_value():
    with pytest.raises(SelectOperatorError):
        get_sqlalchemy_filter('not_in', 'invalid')


def test_get_sqlalchemy_filter_all_operators():
    operators = ['gt', 'lt', 'ge', 'le', 'eq', 'ne', 'like', 'ilike', 'startswith', 'endswith', 'contains']
    for op in operators:
        filter_func = get_sqlalchemy_filter(op, 'test')
        assert filter_func is not None


def test_get_sqlalchemy_filter_arithmetic_operators():
    arithmetic_ops = ['add', 'sub', 'mul', 'truediv', 'floordiv', 'mod']
    for op in arithmetic_ops:
        filter_func = get_sqlalchemy_filter(op, 5)
        assert filter_func is not None


def test_get_sqlalchemy_filter_arithmetic_not_allowed():
    arithmetic_ops = ['add', 'sub', 'mul', 'truediv', 'floordiv', 'mod']
    for op in arithmetic_ops:
        with pytest.raises(SelectOperatorError):
            get_sqlalchemy_filter(op, 5, allow_arithmetic=False)


def test_get_sqlalchemy_filter_unsupported_operator():
    with pytest.warns(SyntaxWarning):
        result = get_sqlalchemy_filter('unsupported', 'value')
        assert result is None


def test_create_or_filters():
    column = get_column(Ins, 'name')
    filters = _create_or_filters(column, 'or', {'like': 'test%', 'eq': 'exact'})

    assert len(filters) == 2


def test_create_or_filters_invalid_op():
    column = get_column(Ins, 'name')
    filters = _create_or_filters(column, 'invalid', {'like': 'test%'})

    assert len(filters) == 0


def test_create_and_filters():
    column = get_column(Ins, 'id')
    filters = _create_and_filters(column, 'gt', 5)

    assert len(filters) == 1


def test_create_and_filters_between():
    column = get_column(Ins, 'id')
    filters = _create_and_filters(column, 'between', [1, 10])

    assert len(filters) == 1


def test_create_and_filters_unsupported():
    column = get_column(Ins, 'id')
    with pytest.warns(SyntaxWarning):
        filters = _create_and_filters(column, 'unsupported', 5)
        assert len(filters) == 0


def test_create_arithmetic_filters():
    column = get_column(Ins, 'id')
    filters = _create_arithmetic_filters(column, 'add', {'value': 5, 'condition': {'gt': 10}})

    assert len(filters) == 1


def test_create_arithmetic_filters_invalid_value():
    column = get_column(Ins, 'id')
    filters = _create_arithmetic_filters(column, 'add', 'invalid')

    assert len(filters) == 0


def test_create_arithmetic_filters_missing_keys():
    column = get_column(Ins, 'id')
    filters = _create_arithmetic_filters(column, 'add', {'value': 5})

    assert len(filters) == 0


def test_parse_filters_simple_equality():
    filters = parse_filters(Ins, name='test')

    assert len(filters) == 1


def test_parse_filters_gt_operator():
    filters = parse_filters(Ins, id__gt=5)

    assert len(filters) == 1


def test_parse_filters_like_operator():
    filters = parse_filters(Ins, name__like='test%')

    assert len(filters) == 1


def test_parse_filters_in_operator():
    filters = parse_filters(Ins, id__in=[1, 2, 3])

    assert len(filters) == 1


def test_parse_filters_between_operator():
    filters = parse_filters(Ins, id__between=[1, 10])

    assert len(filters) == 1


def test_parse_filters_arithmetic_operator():
    filters = parse_filters(Ins, id__add={'value': 5, 'condition': {'gt': 10}})

    assert len(filters) == 1


def test_parse_filters_or_group_list_values():
    filters = parse_filters(Ins, __or__={'del_flag': [True, False]})

    assert len(filters) == 1


def test_parse_filters_or_group_different_fields():
    filters = parse_filters(Ins, __or__={'del_flag': True, 'name': 'test'})

    assert len(filters) == 1


def test_parse_filters_or_with_operators():
    filters = parse_filters(Ins, __or__={'name__like': 'test%', 'id__gt': 5})

    assert len(filters) == 1


def test_parse_filters_or_with_list_values():
    filters = parse_filters(Ins, __or__={'id__in': [1, 2, 3], 'name': 'test'})

    assert len(filters) == 1


def test_parse_filters_field_or_operator():
    filters = parse_filters(Ins, name__or={'like': 'test%', 'eq': 'exact'})

    assert len(filters) == 1


def test_parse_filters_multiple_conditions():
    filters = parse_filters(Ins, name='test', id__gt=5, del_flag=False)

    assert len(filters) == 3


def test_parse_filters_empty_kwargs():
    filters = parse_filters(Ins)

    assert len(filters) == 0


def test_apply_sorting_single_column_asc():
    stmt = select(Ins)
    sorted_stmt = apply_sorting(Ins, stmt, 'name', 'asc')

    assert sorted_stmt is not None


def test_apply_sorting_single_column_desc():
    stmt = select(Ins)
    sorted_stmt = apply_sorting(Ins, stmt, 'name', 'desc')

    assert sorted_stmt is not None


def test_apply_sorting_multiple_columns():
    stmt = select(Ins)
    sorted_stmt = apply_sorting(Ins, stmt, ['name', 'id'], ['asc', 'desc'])

    assert sorted_stmt is not None


def test_apply_sorting_default_order():
    stmt = select(Ins)
    sorted_stmt = apply_sorting(Ins, stmt, 'name')

    assert sorted_stmt is not None


def test_apply_sorting_string_to_list_conversion():
    stmt = select(Ins)
    sorted_stmt = apply_sorting(Ins, stmt, 'name', 'desc')

    assert sorted_stmt is not None


def test_apply_sorting_no_columns():
    stmt = select(Ins)
    sorted_stmt = apply_sorting(Ins, stmt, [])

    assert sorted_stmt is not None


def test_apply_sorting_invalid_order():
    stmt = select(Ins)
    with pytest.raises(SelectOperatorError):
        apply_sorting(Ins, stmt, 'name', 'invalid')


def test_apply_sorting_mismatched_lengths():
    stmt = select(Ins)
    with pytest.raises(ColumnSortError):
        apply_sorting(Ins, stmt, ['name', 'id'], ['asc'])


def test_apply_sorting_orders_without_columns():
    stmt = select(Ins)
    with pytest.raises(ValueError):
        apply_sorting(Ins, stmt, None, ['asc'])


def test_apply_sorting_invalid_column():
    stmt = select(Ins)
    with pytest.raises(ModelColumnError):
        apply_sorting(Ins, stmt, 'nonexistent_column')


def test_build_load_strategies_list():
    options = build_load_strategies(RelUser, ['posts', 'profile'])

    assert len(options) == 2


def test_build_load_strategies_dict():
    options = build_load_strategies(RelUser, {'posts': 'selectinload', 'profile': 'joinedload'})

    assert len(options) == 2


def test_build_load_strategies_empty_list():
    options = build_load_strategies(RelUser, [])

    assert len(options) == 0


def test_build_load_strategies_empty_dict():
    options = build_load_strategies(RelUser, {})

    assert len(options) == 0


def test_build_load_strategies_none():
    options = build_load_strategies(RelUser, None)

    assert len(options) == 0


def test_build_load_strategies_all_strategies():
    strategies = ['selectinload', 'joinedload', 'subqueryload', 'contains_eager', 'raiseload', 'noload']
    for strategy in strategies:
        options = build_load_strategies(RelUser, {'posts': strategy})
        assert len(options) == 1


def test_build_load_strategies_invalid_strategy():
    with pytest.raises(LoadingStrategyError):
        build_load_strategies(RelUser, {'posts': 'invalid_strategy'})


def test_build_load_strategies_invalid_relationship():
    options = build_load_strategies(RelUser, ['nonexistent'])

    assert len(options) == 0


def test_apply_join_conditions_list():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, ['posts'])

    assert joined_stmt is not None


def test_apply_join_conditions_dict_inner():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, {'posts': 'inner'})

    assert joined_stmt is not None


def test_apply_join_conditions_dict_left():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, {'posts': 'left'})

    assert joined_stmt is not None


def test_apply_join_conditions_right_join():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, {'posts': 'right'})

    assert joined_stmt is not None


def test_apply_join_conditions_full_join():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, {'posts': 'full'})

    assert joined_stmt is not None


def test_apply_join_conditions_empty_list():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, [])

    assert joined_stmt is not None


def test_apply_join_conditions_empty_dict():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, {})

    assert joined_stmt is not None


def test_apply_join_conditions_none():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, None)

    assert joined_stmt is not None


def test_apply_join_conditions_invalid_join_type():
    stmt = select(RelUser)
    with pytest.raises(JoinConditionError):
        apply_join_conditions(RelUser, stmt, {'posts': 'invalid'})


def test_apply_join_conditions_invalid_relationship():
    stmt = select(RelUser)
    joined_stmt = apply_join_conditions(RelUser, stmt, ['nonexistent'])

    assert joined_stmt is not None
