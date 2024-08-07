#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Generic, Iterable, Sequence, Type

from sqlalchemy import Row, RowMapping, select
from sqlalchemy import delete as sa_delete
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus.errors import MultipleResultsError
from sqlalchemy_crud_plus.types import CreateSchema, Model, UpdateSchema
from sqlalchemy_crud_plus.utils import apply_sorting, count, parse_filters


class CRUDPlus(Generic[Model]):
    def __init__(self, model: Type[Model]):
        self.model = model

    async def create_model(self, session: AsyncSession, obj: CreateSchema, commit: bool = False, **kwargs) -> Model:
        """
        Create a new instance of a model

        :param session: The SQLAlchemy async session.
        :param obj: The Pydantic schema containing data to be saved.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Additional model data not included in the pydantic schema.
        :return:
        """
        if not kwargs:
            ins = self.model(**obj.model_dump())
        else:
            ins = self.model(**obj.model_dump(), **kwargs)
        session.add(ins)
        if commit:
            await session.commit()
        return ins

    async def create_models(
        self, session: AsyncSession, obj: Iterable[CreateSchema], commit: bool = False
    ) -> list[Model]:
        """
        Create new instances of a model

        :param session: The SQLAlchemy async session.
        :param obj: The Pydantic schema list containing data to be saved.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :return:
        """
        ins_list = []
        for ins in obj:
            ins_list.append(self.model(**ins.model_dump()))
        session.add_all(ins_list)
        if commit:
            await session.commit()
        return ins_list

    async def select_model(self, session: AsyncSession, pk: int) -> Model | None:
        """
        Query by ID

        :param session: The SQLAlchemy async session.
        :param pk: The database primary key value.
        :return:
        """
        stmt = select(self.model).where(self.model.id == pk)
        query = await session.execute(stmt)
        return query.scalars().first()

    async def select_model_by_column(self, session: AsyncSession, **kwargs) -> Model | None:
        """
        Query by column

        :param session: The SQLAlchemy async session.
        :param kwargs: Query expressions.
        :return:
        """
        filters = await parse_filters(self.model, **kwargs)
        stmt = select(self.model).where(*filters)
        query = await session.execute(stmt)
        return query.scalars().first()

    async def select_models(self, session: AsyncSession, **kwargs) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Query all rows

        :param session: The SQLAlchemy async session.
        :param kwargs: Query expressions.
        :return:
        """
        filters = await parse_filters(self.model, **kwargs)
        stmt = select(self.model).where(*filters)
        query = await session.execute(stmt)
        return query.scalars().all()

    async def select_models_order(
        self, session: AsyncSession, sort_columns: str | list[str], sort_orders: str | list[str] | None = None, **kwargs
    ) -> Sequence[Row | RowMapping | Any] | None:
        """
        Query all rows and sort by columns

        :param session: The SQLAlchemy async session.
        :param sort_columns: more details see apply_sorting
        :param sort_orders: more details see apply_sorting
        :return:
        """
        filters = await parse_filters(self.model, **kwargs)
        stmt = select(self.model).where(*filters)
        stmt_sort = await apply_sorting(self.model, stmt, sort_columns, sort_orders)
        query = await session.execute(stmt_sort)
        return query.scalars().all()

    async def update_model(
        self, session: AsyncSession, pk: int, obj: UpdateSchema | dict[str, Any], commit: bool = False
    ) -> int:
        """
        Update an instance by model's primary key

        :param session: The SQLAlchemy async session.
        :param pk: The database primary key value.
        :param obj: A pydantic schema or dictionary containing the update data
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :return:
        """
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        stmt = sa_update(self.model).where(self.model.id == pk).values(**instance_data)
        result = await session.execute(stmt)
        if commit:
            await session.commit()
        return result.rowcount  # type: ignore

    async def update_model_by_column(
        self,
        session: AsyncSession,
        obj: UpdateSchema | dict[str, Any],
        allow_multiple: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> int:
        """
        Update an instance by model column

        :param session: The SQLAlchemy async session.
        :param obj: A pydantic schema or dictionary containing the update data
        :param allow_multiple: If `True`, allows updating multiple records that match the filters.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Query expressions.
        :return:
        """
        filters = await parse_filters(self.model, **kwargs)
        total_count = await count(session, self.model, filters)
        if not allow_multiple and total_count > 1:
            raise MultipleResultsError(f'Only one record is expected to be update, found {total_count} records.')
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        stmt = sa_update(self.model).where(*filters).values(**instance_data)  # type: ignore
        result = await session.execute(stmt)
        if commit:
            await session.commit()
        return result.rowcount  # type: ignore

    async def delete_model(self, session: AsyncSession, pk: int, commit: bool = False) -> int:
        """
        Delete an instance by model's primary key

        :param session: The SQLAlchemy async session.
        :param pk: The database primary key value.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :return:
        """
        stmt = sa_delete(self.model).where(self.model.id == pk)
        result = await session.execute(stmt)
        if commit:
            await session.commit()
        return result.rowcount  # type: ignore

    async def delete_model_by_column(
        self,
        session: AsyncSession,
        allow_multiple: bool = False,
        logical_deletion: bool = False,
        deleted_flag_column: str = 'del_flag',
        commit: bool = False,
        **kwargs,
    ) -> int:
        """
        Delete

        :param session: The SQLAlchemy async session.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Query expressions.
        :param allow_multiple: If `True`, allows deleting multiple records that match the filters.
        :param logical_deletion: If `True`, enable logical deletion instead of physical deletion
        :param deleted_flag_column: Specify the flag column for logical deletion
        :return:
        """
        filters = await parse_filters(self.model, **kwargs)
        total_count = await count(session, self.model, filters)
        if not allow_multiple and total_count > 1:
            raise MultipleResultsError(f'Only one record is expected to be delete, found {total_count} records.')
        if logical_deletion:
            deleted_flag = {deleted_flag_column: True}
            stmt = sa_update(self.model).where(*filters).values(**deleted_flag)
        else:
            stmt = sa_delete(self.model).where(*filters)
        await session.execute(stmt)
        if commit:
            await session.commit()
        return total_count
