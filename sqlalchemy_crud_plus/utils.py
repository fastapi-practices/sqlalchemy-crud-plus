#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import warnings

from typing import Any, Callable, Type

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


def get_sqlalchemy_filter(operator: str, value: Any, allow_arithmetic: bool = True) -> Callable[[str], Callable] | None:
    if operator in ['in', 'not_in', 'between']:
        if not isinstance(value, (tuple, list, set)):
            raise SelectOperatorError(f'The value of the <{operator}> filter must be tuple, list or set')

    if (
        operator
        in ['add', 'radd', 'sub', 'rsub', 'mul', 'rmul', 'truediv', 'rtruediv', 'floordiv', 'rfloordiv', 'mod', 'rmod']
        and not allow_arithmetic
    ):
        raise SelectOperatorError(f'Nested arithmetic operations are not allowed: {operator}')

    sqlalchemy_filter = _SUPPORTED_FILTERS.get(operator)
    if sqlalchemy_filter is None and operator not in ['or', 'mor', '__gor']:
        warnings.warn(
            f'The operator <{operator}> is not yet supported, only {", ".join(_SUPPORTED_FILTERS.keys())}.',
            SyntaxWarning,
        )
        return None

    return sqlalchemy_filter


def get_column(model: Type[Model] | AliasedClass, field_name: str) -> InstrumentedAttribute | None:
    column = getattr(model, field_name, None)
    if column is None:
        raise ModelColumnError(f'Column {field_name} is not found in {model}')
    return column


def _create_or_filters(column: str, op: str, value: Any) -> list[ColumnElement | None]:
    or_filters = []
    if op == 'or':
        for or_op, or_value in value.items():
            sqlalchemy_filter = get_sqlalchemy_filter(or_op, or_value)
            if sqlalchemy_filter is not None:
                or_filters.append(sqlalchemy_filter(column)(or_value))
    elif op == 'mor':
        for or_op, or_values in value.items():
            for or_value in or_values:
                sqlalchemy_filter = get_sqlalchemy_filter(or_op, or_value)
                if sqlalchemy_filter is not None:
                    or_filters.append(sqlalchemy_filter(column)(or_value))
    return or_filters


def _create_arithmetic_filters(column: str, op: str, value: Any) -> list[ColumnElement | None]:
    arithmetic_filters = []
    if isinstance(value, dict) and {'value', 'condition'}.issubset(value):
        arithmetic_value = value['value']
        condition = value['condition']
        sqlalchemy_filter = get_sqlalchemy_filter(op, arithmetic_value)
        if sqlalchemy_filter is not None:
            for cond_op, cond_value in condition.items():
                arithmetic_filter = get_sqlalchemy_filter(cond_op, cond_value, allow_arithmetic=False)
                arithmetic_filters.append(
                    arithmetic_filter(sqlalchemy_filter(column)(arithmetic_value))(cond_value)
                    if cond_op != 'between'
                    else arithmetic_filter(sqlalchemy_filter(column)(arithmetic_value))(*cond_value)
                )
    return arithmetic_filters


def _create_and_filters(column: str, op: str, value: Any) -> list[ColumnElement | None]:
    and_filters = []
    sqlalchemy_filter = get_sqlalchemy_filter(op, value)
    if sqlalchemy_filter is not None:
        and_filters.append(sqlalchemy_filter(column)(value) if op != 'between' else sqlalchemy_filter(column)(*value))
    return and_filters


def parse_filters(model: Type[Model] | AliasedClass, **kwargs) -> list[ColumnElement]:
    filters = []

    def process_filters(target_column: str, target_op: str, target_value: Any):
        # OR / MOR
        or_filters = _create_or_filters(target_column, target_op, target_value)
        if or_filters:
            filters.append(or_(*or_filters))

        # ARITHMETIC
        arithmetic_filters = _create_arithmetic_filters(target_column, target_op, target_value)
        if arithmetic_filters:
            filters.append(and_(*arithmetic_filters))
        else:
            # AND
            and_filters = _create_and_filters(target_column, target_op, target_value)
            if and_filters:
                filters.append(*and_filters)

    for key, value in kwargs.items():
        if '__' in key:
            field_name, op = key.rsplit('__', 1)

            # OR GROUP
            if field_name == '__gor' and op == '':
                _or_filters = []
                for field_or in value:
                    for _key, _value in field_or.items():
                        _field_name, _op = _key.rsplit('__', 1)
                        _column = get_column(model, _field_name)
                        process_filters(_column, _op, _value)
                if _or_filters:
                    filters.append(or_(*_or_filters))
            else:
                column = get_column(model, field_name)
                process_filters(column, op, value)
        else:
            # NON FILTER
            column = get_column(model, key)
            filters.append(column == value)

    return filters


def apply_sorting(
    model: Type[Model] | AliasedClass,
    stmt: Select,
    sort_columns: str | list[str],
    sort_orders: str | list[str] | None = None,
) -> Select:
    """
    Apply sorting to a SQLAlchemy query based on specified column names and sort orders.

    :param model: The SQLAlchemy model.
    :param stmt: The SQLAlchemy `Select` statement to which sorting will be applied.
    :param sort_columns: A single column name or list of column names to sort the query results by.
    Must be used in conjunction with sort_orders.
    :param sort_orders: A single sort order ("asc" or "desc") or a list of sort orders, corresponding to each
    column in sort_columns. If not specified, defaults to ascending order for all sort_columns.
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
