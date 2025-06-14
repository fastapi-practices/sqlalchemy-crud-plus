#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Generic, Iterable, Sequence

from sqlalchemy import (
    Column,
    ColumnExpressionArgument,
    Select,
    delete,
    func,
    inspect,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus.errors import CompositePrimaryKeysError, ModelColumnError, MultipleResultsError
from sqlalchemy_crud_plus.types import (
    CreateSchema,
    JoinConditionsConfig,
    LoadStrategiesConfig,
    Model,
    QueryOptions,
    SortColumns,
    SortOrders,
    UpdateSchema,
)
from sqlalchemy_crud_plus.utils import apply_join_conditions, apply_sorting, build_load_strategies, parse_filters


class CRUDPlus(Generic[Model]):
    def __init__(self, model: type[Model]):
        self.model = model
        self.primary_key = self._get_primary_key()

    def _get_primary_key(self) -> Column | list[Column]:
        """
        Dynamically retrieve the primary key column(s) for the model.
        """
        mapper = inspect(self.model)
        primary_key = mapper.primary_key
        if len(primary_key) == 1:
            return primary_key[0]
        else:
            return list(primary_key)

    def _get_pk_filter(self, pk: Any | Sequence[Any]) -> list[ColumnExpressionArgument[bool]]:
        """
        Get the primary key filter(s).

        :param pk: Single value for simple primary key, or tuple for composite primary key
        :return:
        """
        if isinstance(self.primary_key, list):
            if len(pk) != len(self.primary_key):
                raise CompositePrimaryKeysError(f'Expected {len(self.primary_key)} values for composite primary key')
            return [column == value for column, value in zip(self.primary_key, pk)]
        else:
            return [self.primary_key == pk]

    async def create_model(
        self,
        session: AsyncSession,
        obj: CreateSchema,
        flush: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> Model:
        """
        Create a new instance of a model.

        :param session: The SQLAlchemy async session
        :param obj: The Pydantic schema containing data to be saved
        :param flush: If `True`, flush all object changes to the database
        :param commit: If `True`, commits the transaction immediately
        :param kwargs: Additional model data not included in the pydantic schema
        :return:
        """
        obj_data = obj.model_dump()
        if kwargs:
            obj_data.update(kwargs)

        ins = self.model(**obj_data)
        session.add(ins)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return ins

    async def create_models(
        self,
        session: AsyncSession,
        objs: Iterable[CreateSchema],
        flush: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> list[Model]:
        """
        Create new instances of a model.

        :param session: The SQLAlchemy async session
        :param objs: The Pydantic schema list containing data to be saved
        :param flush: If `True`, flush all object changes to the database
        :param commit: If `True`, commits the transaction immediately
        :param kwargs: Additional model data not included in the pydantic schema
        :return:
        """
        ins_list = []
        for obj in objs:
            obj_data = obj.model_dump()
            if kwargs:
                obj_data.update(kwargs)
            ins = self.model(**obj_data)
            ins_list.append(ins)

        session.add_all(ins_list)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return ins_list

    async def count(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        join_conditions: JoinConditionsConfig | None = None,
        **kwargs,
    ) -> int:
        """
        Count records that match specified filters.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param join_conditions: JOIN conditions for relationships
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        filters = list(whereclause)

        if kwargs:
            filters.extend(parse_filters(self.model, **kwargs))

        stmt = select(func.count()).select_from(self.model)
        if filters:
            stmt = stmt.where(*filters)

        if join_conditions:
            stmt = apply_join_conditions(self.model, stmt, join_conditions)

        query = await session.execute(stmt)
        total_count = query.scalar()
        return total_count if total_count is not None else 0

    async def exists(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        join_conditions: JoinConditionsConfig | None = None,
        **kwargs,
    ) -> bool:
        """
        Check whether records that match the specified filters exist.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param join_conditions: JOIN conditions for relationships
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        filters = list(whereclause)

        if kwargs:
            filters.extend(parse_filters(self.model, **kwargs))

        stmt = select(self.model).where(*filters).limit(1)

        if join_conditions:
            stmt = apply_join_conditions(self.model, stmt, join_conditions)

        query = await session.execute(stmt)
        return query.scalars().first() is not None

    async def select_model(
        self,
        session: AsyncSession,
        pk: Any | Sequence[Any],
        *whereclause: ColumnExpressionArgument[bool],
        load_options: QueryOptions | None = None,
        load_strategies: LoadStrategiesConfig | None = None,
        join_conditions: JoinConditionsConfig | None = None,
        **kwargs: Any,
    ) -> Model | None:
        """
        Query by primary key(s) with optional relationship loading and joins.

        :param session: SQLAlchemy async session
        :param pk: Primary key value(s) - single value or tuple for composite keys
        :param whereclause: Additional WHERE clauses
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        filters = list(whereclause)
        filters.extend(self._get_pk_filter(pk))

        if kwargs:
            filters.extend(parse_filters(self.model, **kwargs))

        stmt = select(self.model).where(*filters)

        if load_options:
            stmt = stmt.options(*load_options)

        if join_conditions:
            stmt = apply_join_conditions(self.model, stmt, join_conditions)

        if load_strategies:
            rel_options = build_load_strategies(self.model, load_strategies)
            if rel_options:
                stmt = stmt.options(*rel_options)

        query = await session.execute(stmt)
        return query.scalars().first()

    async def select_model_by_column(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: QueryOptions | None = None,
        load_strategies: LoadStrategiesConfig | None = None,
        join_conditions: JoinConditionsConfig | None = None,
        **kwargs: Any,
    ) -> Model | None:
        """
        Query by column with optional relationship loading and joins.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        stmt = await self.select(
            *whereclause,
            load_options=load_options,
            load_strategies=load_strategies,
            join_conditions=join_conditions,
            **kwargs,
        )

        query = await session.execute(stmt)
        return query.scalars().first()

    async def select(
        self,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: QueryOptions | None = None,
        load_strategies: LoadStrategiesConfig | None = None,
        join_conditions: JoinConditionsConfig | None = None,
        **kwargs,
    ) -> Select:
        """
        Construct the SQLAlchemy selection.

        :param whereclause: WHERE clauses to apply to the query
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param kwargs: Query expressions
        :return:
        """
        filters = list(whereclause)
        filters.extend(parse_filters(self.model, **kwargs))
        stmt = select(self.model).where(*filters)

        if join_conditions:
            stmt = apply_join_conditions(self.model, stmt, join_conditions)

        if load_options:
            stmt = stmt.options(*load_options)

        if load_strategies:
            rel_options = build_load_strategies(self.model, load_strategies)
            if rel_options:
                stmt = stmt.options(*rel_options)

        return stmt

    async def select_order(
        self,
        sort_columns: SortColumns,
        sort_orders: SortOrders = None,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: QueryOptions | None = None,
        load_strategies: LoadStrategiesConfig | None = None,
        join_conditions: JoinConditionsConfig | None = None,
        **kwargs: Any,
    ) -> Select:
        """
        Construct SQLAlchemy selection with sorting.

        :param sort_columns: Column names to sort by
        :param sort_orders: Sort orders ('asc' or 'desc')
        :param whereclause: WHERE clauses to apply to the query
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param kwargs: Query expressions
        :return:
        """
        stmt = await self.select(
            *whereclause,
            load_options=load_options,
            load_strategies=load_strategies,
            join_conditions=join_conditions,
            **kwargs,
        )
        sorted_stmt = apply_sorting(self.model, stmt, sort_columns, sort_orders)
        return sorted_stmt

    async def select_models(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: QueryOptions | None = None,
        load_strategies: LoadStrategiesConfig | None = None,
        join_conditions: JoinConditionsConfig | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **kwargs: Any,
    ) -> Sequence[Model]:
        """
        Query all rows that match the specified filters with optional relationship loading and joins.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param limit: Maximum number of results to return
        :param offset: Number of results to skip
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        stmt = await self.select(
            *whereclause,
            load_options=load_options,
            load_strategies=load_strategies,
            join_conditions=join_conditions,
            **kwargs,
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        query = await session.execute(stmt)
        return query.scalars().all()

    async def select_models_order(
        self,
        session: AsyncSession,
        sort_columns: SortColumns,
        sort_orders: SortOrders = None,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: QueryOptions | None = None,
        load_strategies: LoadStrategiesConfig | None = None,
        join_conditions: JoinConditionsConfig | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **kwargs: Any,
    ) -> Sequence[Model]:
        """
        Query all rows that match the specified filters and sort by columns
        with optional relationship loading and joins.

        :param session: SQLAlchemy async session
        :param sort_columns: Column names to sort by
        :param sort_orders: Sort orders ('asc' or 'desc')
        :param whereclause: Additional WHERE clauses
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param limit: Maximum number of results to return
        :param offset: Number of results to skip
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        stmt = await self.select_order(
            sort_columns,
            sort_orders,
            *whereclause,
            load_options=load_options,
            load_strategies=load_strategies,
            join_conditions=join_conditions,
            **kwargs,
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        query = await session.execute(stmt)
        return query.scalars().all()

    async def update_model(
        self,
        session: AsyncSession,
        pk: Any | Sequence[Any],
        obj: UpdateSchema | dict[str, Any],
        flush: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> int:
        """
        Update an instance by model's primary key

        :param session: The SQLAlchemy async session.
        :param pk: Single value for simple primary key, or tuple for composite primary key.
        :param obj: A pydantic schema or dictionary containing the update data
        :param flush: If `True`, flush all object changes to the database. Default is `False`.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Additional model data not included in the pydantic schema.
        :return:
        """
        filters = self._get_pk_filter(pk)
        instance_data = obj if isinstance(obj, dict) else obj.model_dump(exclude_unset=True)
        instance_data.update(kwargs)
        stmt = update(self.model).where(*filters).values(**instance_data)
        result = await session.execute(stmt)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return result.rowcount

    async def update_model_by_column(
        self,
        session: AsyncSession,
        obj: UpdateSchema | dict[str, Any],
        allow_multiple: bool = False,
        flush: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> int:
        """
        Update records by model column filters.

        :param session: The SQLAlchemy async session
        :param obj: A Pydantic schema or dictionary containing the update data
        :param allow_multiple: If `True`, allows updating multiple records that match the filters
        :param flush: If `True`, flush all object changes to the database
        :param commit: If `True`, commits the transaction immediately
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        filters = parse_filters(self.model, **kwargs)

        if not filters:
            raise ValueError('At least one filter condition must be provided for update operation')

        if not allow_multiple:
            total_count = await self.count(session, *filters)
            if total_count > 1:
                raise MultipleResultsError(f'Only one record is expected to be updated, found {total_count} records.')

        instance_data = obj if isinstance(obj, dict) else obj.model_dump(exclude_unset=True)
        stmt = update(self.model).where(*filters).values(**instance_data)
        result = await session.execute(stmt)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return result.rowcount

    async def delete_model(
        self,
        session: AsyncSession,
        pk: Any | Sequence[Any],
        flush: bool = False,
        commit: bool = False,
    ) -> int:
        """
        Delete an instance by model's primary key

        :param session: The SQLAlchemy async session.
        :param pk: Single value for simple primary key, or tuple for composite primary key.
        :param flush: If `True`, flush all object changes to the database. Default is `False`.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :return:
        """
        filters = self._get_pk_filter(pk)

        stmt = delete(self.model).where(*filters)
        result = await session.execute(stmt)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return result.rowcount

    async def delete_model_by_column(
        self,
        session: AsyncSession,
        allow_multiple: bool = False,
        logical_deletion: bool = False,
        deleted_flag_column: str = 'del_flag',
        flush: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> int:
        """
        Delete records by model column filters.

        :param session: The SQLAlchemy async session
        :param allow_multiple: If `True`, allows deleting multiple records that match the filters
        :param logical_deletion: If `True`, enable logical deletion instead of physical deletion
        :param deleted_flag_column: Column name for logical deletion flag
        :param flush: If `True`, flush all object changes to the database
        :param commit: If `True`, commits the transaction immediately
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        if logical_deletion:
            if not hasattr(self.model, deleted_flag_column):
                raise ModelColumnError(f'Column {deleted_flag_column} is not found in {self.model}')

        filters = parse_filters(self.model, **kwargs)

        if not filters:
            raise ValueError('At least one filter condition must be provided for delete operation')

        if not allow_multiple:
            total_count = await self.count(session, *filters)
            if total_count > 1:
                raise MultipleResultsError(f'Only one record is expected to be deleted, found {total_count} records.')

        stmt = (
            update(self.model).where(*filters).values(**{deleted_flag_column: True})
            if logical_deletion
            else delete(self.model).where(*filters)
        )

        result = await session.execute(stmt)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return result.rowcount
