#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy import select
from sqlalchemy.orm import aliased

from sqlalchemy_crud_plus.errors import (
    ColumnSortError,
    ModelColumnError,
    SelectOperatorError,
)
from sqlalchemy_crud_plus.utils import (
    apply_sorting,
    get_column,
    get_sqlalchemy_filter,
    parse_filters,
)
from tests.model import Ins


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_column_valid(self):
        """Test getting valid columns."""
        name_column = get_column(Ins, 'name')
        assert name_column is not None

        id_column = get_column(Ins, 'id')
        assert id_column is not None

    def test_get_column_invalid(self):
        """Test getting invalid columns."""
        with pytest.raises(ModelColumnError):
            get_column(Ins, 'nonexistent_column')

    def test_get_column_with_aliased_model(self):
        """Test getting columns from aliased model."""
        aliased_ins = aliased(Ins)
        name_column = get_column(aliased_ins, 'name')
        assert name_column is not None

    def test_get_sqlalchemy_filter_basic(self):
        """Test basic filter operators."""
        # Test equality
        filter_func = get_sqlalchemy_filter('eq', 'test')
        assert filter_func is not None

        # Test inequality
        filter_func = get_sqlalchemy_filter('ne', 'test')
        assert filter_func is not None

        # Test greater than
        filter_func = get_sqlalchemy_filter('gt', 5)
        assert filter_func is not None

    def test_get_sqlalchemy_filter_string_ops(self):
        """Test string operators."""
        # Test LIKE
        filter_func = get_sqlalchemy_filter('like', '%test%')
        assert filter_func is not None

        # Test startswith
        filter_func = get_sqlalchemy_filter('startswith', 'test')
        assert filter_func is not None

    def test_get_sqlalchemy_filter_list_ops(self):
        """Test list operators."""
        # Test IN
        filter_func = get_sqlalchemy_filter('in', [1, 2, 3])
        assert filter_func is not None

        # Test BETWEEN
        filter_func = get_sqlalchemy_filter('between', [1, 10])
        assert filter_func is not None

    def test_get_sqlalchemy_filter_unsupported(self):
        """Test unsupported operators."""
        with pytest.warns(SyntaxWarning):
            filter_func = get_sqlalchemy_filter('unsupported_op', 'value')
            assert filter_func is None

    def test_parse_filters_simple(self):
        """Test parsing simple filters."""
        filters = parse_filters(Ins, name='test', id=1)
        assert len(filters) == 2

        filters = parse_filters(Ins, name__eq='test')
        assert len(filters) == 1

    def test_parse_filters_complex(self):
        """Test parsing complex filters."""
        filters = parse_filters(Ins, name__like='%test%', id__gt=5, del_flag=True)
        assert len(filters) == 3

    def test_parse_filters_empty(self):
        """Test parsing empty filters."""
        filters = parse_filters(Ins)
        assert len(filters) == 0

    def test_apply_sorting_single_column(self):
        """Test applying single column sorting."""
        stmt = select(Ins)

        # Test ascending sort
        sorted_stmt = apply_sorting(Ins, stmt, 'name', 'asc')
        assert sorted_stmt is not None

        # Test descending sort
        sorted_stmt = apply_sorting(Ins, stmt, 'name', 'desc')
        assert sorted_stmt is not None

    def test_apply_sorting_multiple_columns(self):
        """Test applying multiple column sorting."""
        stmt = select(Ins)

        sorted_stmt = apply_sorting(Ins, stmt, ['name', 'id'], ['asc', 'desc'])
        assert sorted_stmt is not None

    def test_apply_sorting_validation_errors(self):
        """Test sorting validation errors."""
        stmt = select(Ins)

        # Test mismatched columns and orders
        with pytest.raises(ColumnSortError):
            apply_sorting(
                Ins,
                stmt,
                ['name', 'id'],
                ['asc'],  # Only one order for two columns
            )

        # Test invalid sort order
        with pytest.raises(SelectOperatorError):
            apply_sorting(Ins, stmt, 'name', 'invalid_order')

        # Test invalid column
        with pytest.raises(ModelColumnError):
            apply_sorting(Ins, stmt, 'nonexistent_column')

    def test_apply_sorting_edge_cases(self):
        """Test sorting edge cases."""
        stmt = select(Ins)

        # Test with None columns
        result_stmt = apply_sorting(Ins, stmt, None)
        assert result_stmt is stmt

        # Test with empty string
        result_stmt = apply_sorting(Ins, stmt, '')
        assert result_stmt is stmt

    def test_filter_edge_cases(self):
        """Test filter edge cases."""
        # Test with None value
        filter_func = get_sqlalchemy_filter('eq', None)
        assert filter_func is not None

        # Test with empty string
        filter_func = get_sqlalchemy_filter('eq', '')
        assert filter_func is not None

        # Test with boolean value
        filter_func = get_sqlalchemy_filter('eq', True)
        assert filter_func is not None

    def test_or_filter_parsing(self):
        """Test OR filter parsing."""
        # Test simple OR filter
        filters = parse_filters(Ins, name__or={'eq': 'test1', 'like': '%test2%'})
        assert len(filters) == 1

        # Test __or__ dictionary format
        filters = parse_filters(Ins, __or__={'name': 'test1', 'id__gt': 5})
        assert len(filters) == 1

        # Test __or__ with list values
        filters = parse_filters(Ins, __or__={'name': ['test1', 'test2'], 'id__gt': [5, 10]})
        assert len(filters) == 1

    def test_or_filter_edge_cases(self):
        """Test OR filter edge cases."""
        # Test empty dict
        filters = parse_filters(Ins, __or__={})
        assert len(filters) == 0

        # Test single field with list
        filters = parse_filters(Ins, __or__={'name': ['test1', 'test2']})
        assert len(filters) == 1

        # Test operators with lists
        filters = parse_filters(Ins, __or__={'name__eq': ['test1', 'test2'], 'id__gt': [5, 10]})
        assert len(filters) == 1

    def test_arithmetic_filter_parsing(self):
        """Test arithmetic filter parsing."""
        filters = parse_filters(Ins, id__add={'value': 5, 'condition': {'gt': 10}})
        assert len(filters) == 1
