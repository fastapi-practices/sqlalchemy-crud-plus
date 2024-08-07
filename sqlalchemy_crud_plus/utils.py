#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import warnings

from typing import Any, Callable, Type

from sqlalchemy import ColumnElement, Select, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.util import AliasedClass

from sqlalchemy_crud_plus.errors import ColumnSortError, ModelColumnError, SelectOperatorError
from sqlalchemy_crud_plus.types import Model

# filters for select
_SUPPORTED_FILTERS = {
    'gt': lambda column: column.__gt__,
    'lt': lambda column: column.__lt__,
    'ge': lambda column: column.__ge__,
    'le': lambda column: column.__le__,
    'eq': lambda column: column.__eq__,
    'ne': lambda column: column.__ne__,
    'is': lambda column: column.is_,
    'is_not': lambda column: column.is_not,
    'like': lambda column: column.like,
    'not_like': lambda column: column.not_like,
    'ilike': lambda column: column.ilike,
    'not_ilike': lambda column: column.not_ilike,
    'startswith': lambda column: column.startswith,
    'endswith': lambda column: column.endswith,
    'contains': lambda column: column.contains,
    'match': lambda column: column.match,
    'between': lambda column: column.between,
    'in': lambda column: column.in_,
    'not_in': lambda column: column.not_in,
}


async def get_sqlalchemy_filter(operator: str, value: Any) -> Callable[[str], Callable] | None:
    if operator in {'in', 'not_in', 'between'}:
        if not isinstance(value, (tuple, list, set)):
            raise SelectOperatorError(f'The value of the <{operator}> filter must be tuple, list or set')
    sqlalchemy_filter = _SUPPORTED_FILTERS.get(operator)
    if sqlalchemy_filter is None:
        warnings.warn(
            f'The operator <{operator}> is not yet supported, only {", ".join(_SUPPORTED_FILTERS.keys())}.',
            SyntaxWarning,
        )
        return None
    return sqlalchemy_filter


async def get_column(model: Type[Model] | AliasedClass, field_name: str):
    column = getattr(model, field_name, None)
    if column is None:
        raise ModelColumnError(f'Column {field_name} is not found in {model}')
    return column


async def parse_filters(model: Type[Model] | AliasedClass, **kwargs) -> list[ColumnElement]:
    filters = []

    for key, value in kwargs.items():
        if '__' in key:
            field_name, op = key.rsplit('__', 1)
            column = await get_column(model, field_name)
            if op == 'or':
                or_filters = []
                for or_op, or_value in value.items():
                    sqlalchemy_filter = await get_sqlalchemy_filter(or_op, or_value)
                    if sqlalchemy_filter is not None:
                        if op != 'between':
                            or_filters.append(sqlalchemy_filter(column)(or_value))
                        else:
                            or_filters.append(sqlalchemy_filter(column)(*or_value))
                filters.append(or_(*or_filters))
            else:
                sqlalchemy_filter = await get_sqlalchemy_filter(op, value)
                if sqlalchemy_filter is not None:
                    if op != 'between':
                        filters.append(sqlalchemy_filter(column)(value))
                    else:
                        filters.append(sqlalchemy_filter(column)(*value))
        else:
            column = await get_column(model, key)
            filters.append(column == value)

    return filters


async def apply_sorting(
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
            column = await get_column(model, column_name)
            order = validated_sort_orders[idx]
            stmt = stmt.order_by(asc(column) if order == 'asc' else desc(column))

    return stmt


async def count(
    session: AsyncSession,
    model: Type[Model] | AliasedClass,
    filters: list[ColumnElement],
) -> int:
    """
    Counts records that match specified filters.

    :param session: The sqlalchemy session to use for the operation.
    :param model: The SQLAlchemy model.
    :param filters: Filters to apply for the count.
    :return:
    """
    stmt = select(func.count()).select_from(model)
    if filters:
        stmt = stmt.where(*filters)
    query = await session.execute(stmt)
    total_count = query.scalar()
    return total_count if total_count is not None else 0
