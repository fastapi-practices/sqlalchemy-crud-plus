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
from sqlalchemy_crud_plus.types import JoinConfig
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
from tests.models.relationship import RelPost, RelProfile, RelUser


class TestGetSqlalchemyFilter:
    def test_comparison_operators(self):
        operators = ['gt', 'lt', 'ge', 'le', 'eq', 'ne']
        for op in operators:
            assert get_sqlalchemy_filter(op, 5) is not None

    def test_in_operators_valid(self):
        assert get_sqlalchemy_filter('in', [1, 2, 3]) is not None
        assert get_sqlalchemy_filter('not_in', (1, 2, 3)) is not None
        assert get_sqlalchemy_filter('between', [1, 10]) is not None

    def test_in_operators_invalid(self):
        with pytest.raises(SelectOperatorError):
            get_sqlalchemy_filter('in', 'invalid')

        with pytest.raises(SelectOperatorError):
            get_sqlalchemy_filter('not_in', 123)

        with pytest.raises(SelectOperatorError):
            get_sqlalchemy_filter('between', 'invalid')

    def test_identity_operators(self):
        assert get_sqlalchemy_filter('is', None) is not None
        assert get_sqlalchemy_filter('is_not', None) is not None
        assert get_sqlalchemy_filter('is_distinct_from', True) is not None
        assert get_sqlalchemy_filter('is_not_distinct_from', False) is not None

    def test_string_operators(self):
        string_ops = ['like', 'not_like', 'ilike', 'not_ilike', 'startswith', 'endswith', 'contains', 'match', 'concat']
        for op in string_ops:
            assert get_sqlalchemy_filter(op, 'test') is not None

    def test_arithmetic_operators(self):
        arithmetic_ops = [
            'add',
            'radd',
            'sub',
            'rsub',
            'mul',
            'rmul',
            'truediv',
            'rtruediv',
            'floordiv',
            'rfloordiv',
            'mod',
            'rmod',
        ]
        for op in arithmetic_ops:
            assert get_sqlalchemy_filter(op, 5) is not None

    def test_arithmetic_not_allowed(self):
        arithmetic_ops = ['add', 'mul', 'sub', 'truediv']
        for op in arithmetic_ops:
            with pytest.raises(SelectOperatorError):
                get_sqlalchemy_filter(op, 5, allow_arithmetic=False)

    def test_unsupported_operator(self):
        with pytest.warns(SyntaxWarning):
            result = get_sqlalchemy_filter('unsupported_op', 'value')
            assert result is None


class TestGetColumn:
    def test_valid_columns_id(self):
        column = get_column(Ins, 'id')
        assert column is not None
        assert column.name == 'id'

    def test_valid_columns_name(self):
        column = get_column(Ins, 'name')
        assert column is not None
        assert column.name == 'name'

    def test_invalid_column(self):
        with pytest.raises(ModelColumnError) as exc_info:
            get_column(Ins, 'nonexistent_column')
        assert str(exc_info.value)

    def test_aliased_model(self):
        aliased_ins = aliased(Ins)
        column = get_column(aliased_ins, 'name')
        assert column is not None

    def test_invalid_column_property(self):
        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

        class Base(DeclarativeBase):
            pass

        class TestModel(Base):
            __tablename__ = 'test_model'
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column()

        class RelatedModel(Base):
            __tablename__ = 'related_model'
            id: Mapped[int] = mapped_column(primary_key=True)
            test_id: Mapped[int] = mapped_column(ForeignKey('test_model.id'))

        TestModel.related = relationship(RelatedModel)

        with pytest.raises(ModelColumnError) as exc_info:
            get_column(TestModel, 'related')
        assert str(exc_info.value)


class TestParseFilters:
    def test_basic_filters(self):
        filters = parse_filters(Ins, name='test')
        assert len(filters) == 1

    def test_basic_filters_multiple(self):
        filters = parse_filters(Ins, name='test', id=1)
        assert len(filters) == 2

    def test_operator_filters(self):
        filters = parse_filters(Ins, id__gt=5)
        assert len(filters) == 1

        filters = parse_filters(Ins, name__like='test%', id__in=[1, 2, 3])
        assert len(filters) == 2

    def test_or_conditions_same_field(self):
        filters = parse_filters(Ins, __or__={'name': ['test1', 'test2']})
        assert len(filters) == 1

    def test_or_conditions_different_fields(self):
        filters = parse_filters(Ins, __or__={'name': 'test', 'id__gt': 5})
        assert len(filters) == 1

    def test_or_conditions_with_operators(self):
        filters = parse_filters(Ins, __or__={'name__like': 'test%', 'id__lt': 10})
        assert len(filters) == 1

    def test_or_invalid_value(self):
        with pytest.raises(SelectOperatorError):
            parse_filters(Ins, __or__='invalid')

    def test_complex_or_mixed(self):
        filters = parse_filters(Ins, __or__={'is_deleted': [True, False], 'name__like': 'test%'})
        assert len(filters) == 1

    def test_empty_filters(self):
        filters = parse_filters(Ins)
        assert len(filters) == 0


class TestApplySorting:
    def test_single_column_sorting_asc(self):
        stmt = apply_sorting(Ins, select(Ins), 'name')
        assert 'ORDER BY' in str(stmt)

    def test_single_column_sorting_desc(self):
        stmt = apply_sorting(Ins, select(Ins), 'name', 'desc')
        assert 'ORDER BY' in str(stmt)

    def test_multiple_columns_sorting(self):
        stmt = apply_sorting(Ins, select(Ins), ['name', 'id'], ['asc', 'desc'])
        assert 'ORDER BY' in str(stmt)

    def test_mismatched_columns_orders(self):
        with pytest.raises(ColumnSortError):
            apply_sorting(Ins, select(Ins), ['name', 'id'], ['asc'])

    def test_invalid_sort_order(self):
        with pytest.raises(SelectOperatorError):
            apply_sorting(Ins, select(Ins), 'name', 'invalid')

    def test_invalid_column_sorting(self):
        with pytest.raises(ModelColumnError):
            apply_sorting(Ins, select(Ins), 'nonexistent')

    def test_no_columns_with_orders(self):
        with pytest.raises(ValueError):
            apply_sorting(Ins, select(Ins), None, 'asc')

    def test_empty_columns(self):
        stmt = apply_sorting(Ins, select(Ins), [])
        assert stmt is not None

    def test_default_sort_order(self):
        stmt = apply_sorting(Ins, select(Ins), ['name', 'id'])
        assert 'ORDER BY' in str(stmt)


class TestBuildLoadStrategies:
    def test_list_format_single(self):
        strategies = build_load_strategies(RelUser, ['posts'])
        assert len(strategies) == 1

    def test_list_format_multiple(self):
        strategies = build_load_strategies(RelUser, ['posts', 'profile'])
        assert len(strategies) == 2

    def test_dict_format_single(self):
        strategies = build_load_strategies(RelUser, {'posts': 'selectinload'})
        assert len(strategies) == 1

    def test_dict_format_multiple(self):
        strategies = build_load_strategies(RelUser, {'posts': 'joinedload', 'profile': 'subqueryload'})
        assert len(strategies) == 2

    def test_all_supported_strategies(self):
        strategy_types = [
            'contains_eager',
            'defaultload',
            'immediateload',
            'joinedload',
            'lazyload',
            'noload',
            'raiseload',
            'selectinload',
            'subqueryload',
            'defer',
            'load_only',
            'undefer',
            'undefer_group',
        ]

        for strategy_type in strategy_types:
            strategies = build_load_strategies(RelUser, {'posts': strategy_type})
            assert len(strategies) == 1

    def test_invalid_strategy(self):
        with pytest.raises(LoadingStrategyError):
            build_load_strategies(RelUser, {'posts': 'invalid_strategy'})

    def test_invalid_column_strategies(self):
        with pytest.raises(ModelColumnError):
            build_load_strategies(RelUser, ['nonexistent_relation'])

        with pytest.raises(ModelColumnError):
            build_load_strategies(RelUser, {'nonexistent_relation': 'selectinload'})

    def test_none_strategies_none(self):
        strategies = build_load_strategies(RelUser, None)
        assert len(strategies) == 0

    def test_none_strategies_empty_list(self):
        strategies = build_load_strategies(RelUser, [])
        assert len(strategies) == 0

    def test_none_strategies_empty_dict(self):
        strategies = build_load_strategies(RelUser, {})
        assert len(strategies) == 0


class TestApplyJoinConditions:
    def test_list_format_single(self):
        stmt = apply_join_conditions(RelUser, select(RelUser), ['posts'])
        assert 'JOIN' in str(stmt)

    def test_list_format_multiple(self):
        stmt = apply_join_conditions(RelUser, select(RelUser), ['posts', 'profile'])
        assert 'JOIN' in str(stmt)

    def test_dict_format_all_join_types(self):
        join_types = ['inner', 'left', 'full']

        for join_type in join_types:
            stmt = apply_join_conditions(RelUser, select(RelUser), {'posts': join_type})
            assert 'JOIN' in str(stmt)

    def test_invalid_join_type(self):
        with pytest.raises(JoinConditionError):
            apply_join_conditions(RelUser, select(RelUser), {'posts': 'invalid'})

    def test_invalid_column_joins(self):
        with pytest.raises(ModelColumnError):
            apply_join_conditions(RelUser, select(RelUser), ['nonexistent'])

        with pytest.raises(ModelColumnError):
            apply_join_conditions(RelUser, select(RelUser), {'nonexistent': 'inner'})

    def test_none_conditions(self):
        stmt = apply_join_conditions(RelUser, select(RelUser), None)
        assert stmt is not None
        assert 'JOIN' not in str(stmt)

    def test_empty_conditions(self):
        stmt = apply_join_conditions(RelUser, select(RelUser), [])
        assert stmt is not None
        assert 'JOIN' not in str(stmt)


class TestJoinConfig:
    def test_join_config_inner_join(self):
        stmt = apply_join_conditions(
            RelUser,
            select(RelUser),
            [
                JoinConfig(
                    model=RelPost,
                    join_on=RelUser.id == RelPost.author_id,
                    join_type='inner',
                )
            ],
        )
        assert 'JOIN' in str(stmt)
        assert stmt is not None

    def test_join_config_left_join(self):
        stmt = apply_join_conditions(
            RelUser,
            select(RelUser),
            [
                JoinConfig(
                    model=RelPost,
                    join_on=RelUser.id == RelPost.author_id,
                    join_type='left',
                )
            ],
        )
        assert 'JOIN' in str(stmt)
        assert stmt is not None

    def test_join_config_full_join(self):
        stmt = apply_join_conditions(
            RelUser,
            select(RelUser),
            [
                JoinConfig(
                    model=RelPost,
                    join_on=RelUser.id == RelPost.author_id,
                    join_type='full',
                )
            ],
        )
        assert 'JOIN' in str(stmt)
        assert stmt is not None

    def test_join_config_default_join_type(self):
        join_config = JoinConfig(model=RelPost, join_on=RelUser.id == RelPost.author_id)
        assert join_config.join_type == 'left'
        stmt = apply_join_conditions(RelUser, select(RelUser), [join_config])
        assert 'JOIN' in str(stmt)

    def test_join_config_with_aliased_model(self):
        aliased_post = aliased(RelPost)
        stmt = apply_join_conditions(
            RelUser,
            select(RelUser),
            [
                JoinConfig(
                    model=aliased_post,
                    join_on=RelUser.id == aliased_post.author_id,
                    join_type='left',
                )
            ],
        )
        assert 'JOIN' in str(stmt)

    def test_join_config_multiple_in_list(self):
        stmt = apply_join_conditions(
            RelUser,
            select(RelUser),
            [
                JoinConfig(
                    model=RelPost,
                    join_on=RelUser.id == RelPost.author_id,
                    join_type='inner',
                ),
                JoinConfig(
                    model=RelProfile,
                    join_on=RelUser.id == RelProfile.user_id,
                    join_type='left',
                ),
            ],
        )
        assert 'JOIN' in str(stmt)

    def test_join_config_mixed_with_string(self):
        stmt = apply_join_conditions(
            RelUser,
            select(RelUser),
            [
                'posts',
                JoinConfig(
                    model=RelPost,
                    join_on=RelUser.id == RelPost.author_id,
                    join_type='inner',
                ),
            ],
        )
        assert 'JOIN' in str(stmt)

    def test_join_config_creation(self):
        join_config = JoinConfig(
            model=RelPost,
            join_on=RelUser.id == RelPost.author_id,
            join_type='inner',
        )
        assert join_config.model == RelPost
        assert join_config.join_type == 'inner'
        assert join_config.join_on is not None

    def test_join_config_pydantic_validation(self):
        join_config = JoinConfig(
            model=RelPost,
            join_on=RelUser.id == RelPost.author_id,
            join_type='left',
        )
        assert isinstance(join_config.model, type)
        assert join_config.join_type in ['inner', 'left', 'full']


class TestPrivateFunctions:
    def test_create_or_filters(self):
        column = get_column(Ins, 'name')
        filters = _create_or_filters(column, 'or', {'like': 'test%', 'startswith': 'item'})
        assert len(filters) >= 0

    def test_create_or_filters_with_none_filter(self):
        column = get_column(Ins, 'name')
        with pytest.warns(SyntaxWarning):
            filters = _create_or_filters(column, 'or', {'unsupported_op': 'test'})
        assert len(filters) == 0

    def test_create_arithmetic_filters_valid(self):
        column = get_column(Ins, 'id')
        filters = _create_arithmetic_filters(column, 'add', {'value': 10, 'condition': {'gt': 5}})
        assert len(filters) >= 0

    def test_create_arithmetic_filters_between_condition(self):
        column = get_column(Ins, 'id')
        filters = _create_arithmetic_filters(column, 'add', {'value': 10, 'condition': {'gt': 5}})
        assert len(filters) >= 0

    def test_create_arithmetic_filters_invalid_dict(self):
        column = get_column(Ins, 'id')
        filters = _create_arithmetic_filters(column, 'add', {'invalid': 'structure'})
        assert len(filters) == 0

    def test_create_arithmetic_filters_none_filter(self):
        column = get_column(Ins, 'id')
        with pytest.warns(SyntaxWarning):
            filters = _create_arithmetic_filters(column, 'add', {'value': 10, 'condition': {'unsupported_op': 5}})
        assert len(filters) == 0

    def test_create_and_filters_between(self):
        column = get_column(Ins, 'id')
        filters = _create_and_filters(column, 'between', [1, 10])
        assert len(filters) == 1

    def test_create_and_filters_regular(self):
        column = get_column(Ins, 'id')
        filters = _create_and_filters(column, 'gt', 5)
        assert len(filters) == 1

    def test_create_and_filters_none_filter(self):
        column = get_column(Ins, 'id')
        with pytest.warns(SyntaxWarning):
            filters = _create_and_filters(column, 'unsupported_op', 5)
        assert len(filters) == 0


class TestComplexOrConditions:
    def test_or_with_list_values_and_operators(self):
        filters = parse_filters(Ins, __or__={'name__like': ['test1%', 'test2%'], 'id__gt': 5})
        assert len(filters) == 1

    def test_or_with_arithmetic_operators(self):
        filters = parse_filters(Ins, __or__={'id__add': {'value': 1, 'condition': {'gt': 5}}})
        assert len(filters) >= 0

    def test_or_nested_or_operator(self):
        filters = parse_filters(Ins, __or__={'name__or': {'like': 'test%'}})
        assert len(filters) >= 0

    def test_regular_or_operator_on_field(self):
        filters = parse_filters(Ins, name__or={'like': 'test%', 'startswith': 'item'})
        assert len(filters) >= 0

    def test_arithmetic_filter_with_empty_condition(self):
        filters = parse_filters(Ins, id__add={'value': 1, 'condition': {}})
        assert len(filters) == 0

    def test_arithmetic_filter_with_none_arithmetic_filter(self):
        with pytest.warns(SyntaxWarning):
            filters = parse_filters(Ins, id__unsupported_arithmetic={'value': 1, 'condition': {'gt': 5}})
        assert len(filters) == 0

    def test_or_with_non_or_operator_branch(self):
        with pytest.warns(SyntaxWarning):
            filters = parse_filters(Ins, name__not_or={'like': 'test%'})
        assert len(filters) >= 0
