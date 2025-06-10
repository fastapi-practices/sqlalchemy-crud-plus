#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import warnings

from typing import Any, Callable

from sqlalchemy import ColumnElement, Select, and_, asc, desc, or_
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.util import AliasedClass

from sqlalchemy_crud_plus.errors import ColumnSortError, ModelColumnError, SelectOperatorError
from sqlalchemy_crud_plus.types import Model

_SUPPORTED_FILTERS = {
    # Comparison: https://docs.sqlalchemy.org/en/20/core/operators.html#comparison-operators
    'gt': lambda column: column.__gt__,
    'lt': lambda column: column.__lt__,
    'ge': lambda column: column.__ge__,
    'le': lambda column: column.__le__,
    'eq': lambda column: column.__eq__,
    'ne': lambda column: column.__ne__,
    'between': lambda column: column.between,
    # IN: https://docs.sqlalchemy.org/en/20/core/operators.html#in-comparisons
    'in': lambda column: column.in_,
    'not_in': lambda column: column.not_in,
    # Identity: https://docs.sqlalchemy.org/en/20/core/operators.html#identity-comparisons
    'is': lambda column: column.is_,
    'is_not': lambda column: column.is_not,
    'is_distinct_from': lambda column: column.is_distinct_from,
    'is_not_distinct_from': lambda column: column.is_not_distinct_from,
    # String: https://docs.sqlalchemy.org/en/20/core/operators.html#string-comparisons
    'like': lambda column: column.like,
    'not_like': lambda column: column.not_like,
    'ilike': lambda column: column.ilike,
    'not_ilike': lambda column: column.not_ilike,
    # String Containment: https://docs.sqlalchemy.org/en/20/core/operators.html#string-containment
    'startswith': lambda column: column.startswith,
    'endswith': lambda column: column.endswith,
    'contains': lambda column: column.contains,
    # String matching: https://docs.sqlalchemy.org/en/20/core/operators.html#string-matching
    'match': lambda column: column.match,
    # String Alteration: https://docs.sqlalchemy.org/en/20/core/operators.html#string-alteration
    'concat': lambda column: column.concat,
    # Arithmetic: https://docs.sqlalchemy.org/en/20/core/operators.html#arithmetic-operators
    'add': lambda column: column.__add__,
    'radd': lambda column: column.__radd__,
    'sub': lambda column: column.__sub__,
    'rsub': lambda column: column.__rsub__,
    'mul': lambda column: column.__mul__,
    'rmul': lambda column: column.__rmul__,
    'truediv': lambda column: column.__truediv__,
    'rtruediv': lambda column: column.__rtruediv__,
    'floordiv': lambda column: column.__floordiv__,
    'rfloordiv': lambda column: column.__rfloordiv__,
    'mod': lambda column: column.__mod__,
    'rmod': lambda column: column.__rmod__,
}

_DYNAMIC_OPERATORS = [
    'concat',
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


def get_sqlalchemy_filter(
    operator: str, value: Any, allow_arithmetic: bool = True
) -> Callable[[InstrumentedAttribute], Callable] | None:
    if operator in ['in', 'not_in', 'between']:
        if not isinstance(value, (tuple, list, set)):
            raise SelectOperatorError(f'The value of the <{operator}> filter must be tuple, list or set')

    if operator in _DYNAMIC_OPERATORS and not allow_arithmetic:
        raise SelectOperatorError(f'Nested arithmetic operations are not allowed: {operator}')

    sqlalchemy_filter = _SUPPORTED_FILTERS.get(operator)
    if sqlalchemy_filter is None and operator != 'or':
        warnings.warn(
            f'The operator <{operator}> is not yet supported, only {", ".join(_SUPPORTED_FILTERS.keys())}.',
            SyntaxWarning,
        )
        return None

    return sqlalchemy_filter


def get_column(model: type[Model] | AliasedClass, field_name: str) -> InstrumentedAttribute:
    """
    Get column from model with validation.

    :param model: The SQLAlchemy model class or aliased class
    :param field_name: The column name to retrieve
    :return:
    """
    column = getattr(model, field_name, None)
    if column is None:
        raise ModelColumnError(f'Column {field_name} is not found in {model}')

    if hasattr(model, '__table__') and hasattr(column, 'property'):
        if not hasattr(column.property, 'columns'):
            raise ModelColumnError(f'{field_name} is not a valid column in {model}')

    return column


def _create_or_filters(column: InstrumentedAttribute, op: str, value: dict[str, Any]) -> list[ColumnElement | None]:
    """
    Create OR filter expressions.

    :param column: The SQLAlchemy column
    :param op: The operator (should be 'or')
    :param value: Dictionary of operator-value pairs
    :return:
    """
    or_filters = []
    if op == 'or':
        for or_op, or_value in value.items():
            sqlalchemy_filter = get_sqlalchemy_filter(or_op, or_value)
            if sqlalchemy_filter is not None:
                or_filters.append(sqlalchemy_filter(column)(or_value))
    return or_filters


def _create_arithmetic_filters(
    column: InstrumentedAttribute, op: str, value: dict[str, Any]
) -> list[ColumnElement | None]:
    """
    Create arithmetic filter expressions.

    :param column: The SQLAlchemy column
    :param op: The arithmetic operator
    :param value: Dictionary containing 'value' and 'condition' keys
    :return:
    """
    arithmetic_filters = []
    if isinstance(value, dict) and {'value', 'condition'}.issubset(value):
        arithmetic_value = value['value']
        condition = value['condition']
        sqlalchemy_filter = get_sqlalchemy_filter(op, arithmetic_value)
        if sqlalchemy_filter is not None:
            for cond_op, cond_value in condition.items():
                arithmetic_filter = get_sqlalchemy_filter(cond_op, cond_value, allow_arithmetic=False)
                if arithmetic_filter is not None:
                    arithmetic_filters.append(
                        arithmetic_filter(sqlalchemy_filter(column)(arithmetic_value))(cond_value)
                        if cond_op != 'between'
                        else arithmetic_filter(sqlalchemy_filter(column)(arithmetic_value))(*cond_value)
                    )
    return arithmetic_filters


def _create_and_filters(column: InstrumentedAttribute, op: str, value: Any) -> list[ColumnElement | None]:
    """
    Create AND filter expressions.

    :param column: The SQLAlchemy column
    :param op: The filter operator
    :param value: The filter value
    :return:
    """
    and_filters = []
    sqlalchemy_filter = get_sqlalchemy_filter(op, value)
    if sqlalchemy_filter is not None:
        and_filters.append(sqlalchemy_filter(column)(value) if op != 'between' else sqlalchemy_filter(column)(*value))
    return and_filters


def parse_filters(model: type[Model] | AliasedClass, **kwargs) -> list[ColumnElement]:
    """
    Parse filter expressions from keyword arguments.

    :param model: The SQLAlchemy model class or aliased class
    :param kwargs: Filter expressions using field__operator=value syntax
    :return:
    """
    filters = []

    for key, value in kwargs.items():
        if '__' not in key:
            column = get_column(model, key)
            filters.append(column == value)
            continue

        field_name, op = key.rsplit('__', 1)

        # OR GROUP
        if field_name == '__or' and op == '':
            __or__filters = []

            for _key, _value in value.items():
                if '__' not in _key:
                    _column = get_column(model, _key)
                    if isinstance(_value, list):
                        for single_value in _value:
                            __or__filters.append(_column == single_value)
                    else:
                        __or__filters.append(_column == _value)
                else:
                    _field_name, _op = _key.rsplit('__', 1)
                    _column = get_column(model, _field_name)

                    if isinstance(_value, list) and _op not in ['in', 'not_in', 'between']:
                        for single_value in _value:
                            __or__filters.extend(_create_and_filters(_column, _op, single_value))
                    else:
                        if _op == 'or':
                            __or__filters.extend(_create_or_filters(_column, _op, _value))
                        elif _op in _DYNAMIC_OPERATORS:
                            __or__filters.extend(_create_arithmetic_filters(_column, _op, _value))
                        else:
                            __or__filters.extend(_create_and_filters(_column, _op, _value))

            if __or__filters:
                filters.append(or_(*__or__filters))
        else:
            column = get_column(model, field_name)

            if op == 'or':
                filters.append(or_(*_create_or_filters(column, op, value)))
            elif op in _DYNAMIC_OPERATORS:
                arithmetic_filters = _create_arithmetic_filters(column, op, value)
                if arithmetic_filters:
                    filters.append(and_(*arithmetic_filters))
            else:
                filters.extend(_create_and_filters(column, op, value))

    return filters


def apply_sorting(
    model: type[Model] | AliasedClass,
    stmt: Select,
    sort_columns: str | list[str],
    sort_orders: str | list[str] | None = None,
) -> Select:
    """
    Apply sorting to a SQLAlchemy query based on specified column names and sort orders.

    :param model: The SQLAlchemy model
    :param stmt: The SQLAlchemy Select statement to which sorting will be applied
    :param sort_columns: Column name or list of column names to sort by
    :param sort_orders: Sort order ("asc" or "desc") or list of sort orders
    :return:
    """
    if sort_orders and not sort_columns:
        raise ValueError('Sort orders provided without corresponding sort columns.')

    if sort_columns:
        if not isinstance(sort_columns, list):
            sort_columns = [sort_columns]

        if sort_orders:
            if not isinstance(sort_orders, list):
                sort_orders = [sort_orders] * len(sort_columns)

            if len(sort_columns) != len(sort_orders):
                raise ColumnSortError('The length of sort_columns and sort_orders must match.')

            for order in sort_orders:
                if order not in ['asc', 'desc']:
                    raise SelectOperatorError(
                        f'Select sort operator {order} is not supported, only supports `asc`, `desc`'
                    )

        validated_sort_orders = ['asc'] * len(sort_columns) if not sort_orders else sort_orders

        for idx, column_name in enumerate(sort_columns):
            column = get_column(model, column_name)
            order = validated_sort_orders[idx]
            stmt = stmt.order_by(asc(column) if order == 'asc' else desc(column))

    return stmt
