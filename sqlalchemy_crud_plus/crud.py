#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Generic, Iterable, Sequence, Type

from sqlalchemy import (
    Column,
    ColumnExpressionArgument,
    Row,
    RowMapping,
    Select,
    delete,
    func,
    inspect,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus.errors import CompositePrimaryKeysError, MultipleResultsError
from sqlalchemy_crud_plus.types import CreateSchema, Model, UpdateSchema
from sqlalchemy_crud_plus.utils import apply_sorting, parse_filters


class CRUDPlus(Generic[Model]):
    def __init__(self, model: Type[Model]):
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

    def _get_pk_filter(self, pk: Any | Sequence[Any]) -> list[bool]:
        """
        Get the primary key filter(s).

        :param pk: Single value for simple primary key, or tuple for composite primary key.
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
        Create a new instance of a model

        :param session: The SQLAlchemy async session.
        :param obj: The Pydantic schema containing data to be saved.
        :param flush: If `True`, flush all object changes to the database. Default is `False`.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Additional model data not included in the pydantic schema.
        :return:
        """
        ins = self.model(**obj.model_dump()) if not kwargs else self.model(**obj.model_dump(), **kwargs)

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
        Create new instances of a model

        :param session: The SQLAlchemy async session.
        :param objs: The Pydantic schema list containing data to be saved.
        :param flush: If `True`, flush all object changes to the database. Default is `False`.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Additional model data not included in the pydantic schema.
        :return:
        """
        ins_list = []
        for obj in objs:
            ins = self.model(**obj.model_dump()) if not kwargs else self.model(**obj.model_dump(), **kwargs)
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
        **kwargs,
    ) -> int:
        """
        Counts records that match specified filters.

        :param session: The sqlalchemy session to use for the operation.
        :param whereclause: The WHERE clauses to apply to the query.
        :param kwargs: Query expressions.
        :return:
        """
        filters = list(whereclause)

        if kwargs:
            filters.extend(parse_filters(self.model, **kwargs))

        stmt = select(func.count()).select_from(self.model).where(*filters)
        query = await session.execute(stmt)
        total_count = query.scalar()
        return total_count if total_count is not None else 0

    async def exists(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        **kwargs,
    ) -> bool:
        """
        Whether the records that match the specified filter exist.

        :param session: The sqlalchemy session to use for the operation.
        :param whereclause: The WHERE clauses to apply to the query.
        :param kwargs: Query expressions.
        :return:
        """
        filter_list = list(whereclause)

        if kwargs:
            filter_list.extend(parse_filters(self.model, **kwargs))

        stmt = select(self.model).where(*filter_list).limit(1)
        query = await session.execute(stmt)
        return query.scalars().first() is not None

    async def select_model(
        self,
        session: AsyncSession,
        pk: Any | Sequence[Any],
        *whereclause: ColumnExpressionArgument[bool],
    ) -> Model | None:
        """
        Query by primary key(s)

        :param session: The SQLAlchemy async session.
        :param pk: Single value for simple primary key, or tuple for composite primary key.
        :param whereclause: The WHERE clauses to apply to the query.
        :return:
        """
        filters = self._get_pk_filter(pk)
        filters + list(whereclause)
        stmt = select(self.model).where(*filters)
        query = await session.execute(stmt)
        return query.scalars().first()

    async def select_model_by_column(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        **kwargs,
    ) -> Model | None:
        """
        Query by column

        :param session: The SQLAlchemy async session.
        :param whereclause: The WHERE clauses to apply to the query.
        :param kwargs: Query expressions.
        :return:
        """
        filters = parse_filters(self.model, **kwargs) + list(whereclause)
        stmt = select(self.model).where(*filters)
        query = await session.execute(stmt)
        return query.scalars().first()

    async def select(self, *whereclause: ColumnExpressionArgument[bool], **kwargs) -> Select:
        """
        Construct the SQLAlchemy selection

        :param whereclause: The WHERE clauses to apply to the query.
        :param kwargs: Query expressions.
        :return:
        """
        filters = parse_filters(self.model, **kwargs) + list(whereclause)
        stmt = select(self.model).where(*filters)
        return stmt

    async def select_order(
        self,
        sort_columns: str | list[str],
        sort_orders: str | list[str] | None = None,
        *whereclause: ColumnExpressionArgument[bool],
        **kwargs,
    ) -> Select:
        """
        Constructing SQLAlchemy selection with sorting

        :param sort_columns: more details see apply_sorting
        :param sort_orders: more details see apply_sorting
        :param whereclause: The WHERE clauses to apply to the query.
        :param kwargs: Query expressions.
        :return:
        """
        stmt = await self.select(*whereclause, **kwargs)
        sorted_stmt = apply_sorting(self.model, stmt, sort_columns, sort_orders)
        return sorted_stmt

    async def select_models(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        **kwargs,
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Query all rows

        :param session: The SQLAlchemy async session.
        :param whereclause: The WHERE clauses to apply to the query.
        :param kwargs: Query expressions.
        :return:
        """
        stmt = await self.select(*whereclause, **kwargs)
        query = await session.execute(stmt)
        return query.scalars().all()

    async def select_models_order(
        self,
        session: AsyncSession,
        sort_columns: str | list[str],
        sort_orders: str | list[str] | None = None,
        *whereclause: ColumnExpressionArgument[bool],
        **kwargs,
    ) -> Sequence[Row | RowMapping | Any] | None:
        """
        Query all rows and sort by columns

        :param session: The SQLAlchemy async session.
        :param sort_columns: more details see apply_sorting
        :param sort_orders: more details see apply_sorting
        :param whereclause: The WHERE clauses to apply to the query.
        :param kwargs: Query expressions.
        :return:
        """
        stmt = await self.select_order(sort_columns, sort_orders, *whereclause, **kwargs)
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

        return result.rowcount  # type: ignore

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
        Update an instance by model column

        :param session: The SQLAlchemy async session.
        :param obj: A pydantic schema or dictionary containing the update data
        :param allow_multiple: If `True`, allows updating multiple records that match the filters.
        :param flush: If `True`, flush all object changes to the database. Default is `False`.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Query expressions.
        :return:
        """
        filters = parse_filters(self.model, **kwargs)

        total_count = await self.count(session, *filters)
        if not allow_multiple and total_count > 1:
            raise MultipleResultsError(f'Only one record is expected to be update, found {total_count} records.')

        instance_data = obj if isinstance(obj, dict) else obj.model_dump(exclude_unset=True)
        stmt = update(self.model).where(*filters).values(**instance_data)
        result = await session.execute(stmt)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return result.rowcount  # type: ignore

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

        return result.rowcount  # type: ignore

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
        Delete an instance by model column

        :param session: The SQLAlchemy async session.
        :param allow_multiple: If `True`, allows deleting multiple records that match the filters.
        :param logical_deletion: If `True`, enable logical deletion instead of physical deletion
        :param deleted_flag_column: Specify the flag column for logical deletion
        :param flush: If `True`, flush all object changes to the database. Default is `False`.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Query expressions.
        :return:
        """
        filters = parse_filters(self.model, **kwargs)

        total_count = await self.count(session, *filters)
        if not allow_multiple and total_count > 1:
            raise MultipleResultsError(f'Only one record is expected to be delete, found {total_count} records.')

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

        return result.rowcount  # type: ignore
