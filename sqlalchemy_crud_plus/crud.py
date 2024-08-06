#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Generic, Iterable, Literal, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import Row, RowMapping, and_, asc, desc, or_, select
from sqlalchemy import delete as sa_delete
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus.errors import ModelColumnError, SelectExpressionError

_Model = TypeVar('_Model')
_CreateSchema = TypeVar('_CreateSchema', bound=BaseModel)
_UpdateSchema = TypeVar('_UpdateSchema', bound=BaseModel)


class CRUDPlus(Generic[_Model]):
    def __init__(self, model: Type[_Model]):
        self.model = model

    async def create_model(self, session: AsyncSession, obj: _CreateSchema, commit: bool = False, **kwargs) -> _Model:
        """
        Create a new instance of a model

        :param session:
        :param obj:
        :param commit:
        :param kwargs:
        :return:
        """
        if kwargs:
            ins = self.model(**obj.model_dump(), **kwargs)
        else:
            ins = self.model(**obj.model_dump())
        session.add(ins)
        if commit:
            await session.commit()
        return ins

    async def create_models(
        self, session: AsyncSession, obj: Iterable[_CreateSchema], commit: bool = False
    ) -> list[_Model]:
        """
        Create new instances of a model

        :param session:
        :param obj:
        :param commit:
        :return:
        """
        ins_list = []
        for i in obj:
            ins_list.append(self.model(**i.model_dump()))
        session.add_all(ins_list)
        if commit:
            await session.commit()
        return ins_list

    async def select_model_by_id(self, session: AsyncSession, pk: int) -> _Model | None:
        """
        Query by ID

        :param session:
        :param pk:
        :return:
        """
        stmt = select(self.model).where(self.model.id == pk)
        query = await session.execute(stmt)
        return query.scalars().first()

    async def select_model_by_column(self, session: AsyncSession, column: str, column_value: Any) -> _Model | None:
        """
        Query by column

        :param session:
        :param column:
        :param column_value:
        :return:
        """
        if hasattr(self.model, column):
            model_column = getattr(self.model, column)
            stmt = select(self.model).where(model_column == column_value)  # type: ignore
            query = await session.execute(stmt)
            return query.scalars().first()
        else:
            raise ModelColumnError(f'Column {column} is not found in {self.model}')

    async def select_model_by_columns(
        self, session: AsyncSession, expression: Literal['and', 'or'] = 'and', **conditions
    ) -> _Model | None:
        """
        Query by columns

        :param session:
        :param expression:
        :param conditions: Query conditions, format：column1=value1, column2=value2
        :return:
        """
        where_list = []
        for column, value in conditions.items():
            if hasattr(self.model, column):
                model_column = getattr(self.model, column)
                where_list.append(model_column == value)
            else:
                raise ModelColumnError(f'Column {column} is not found in {self.model}')
        match expression:
            case 'and':
                stmt = select(self.model).where(and_(*where_list))
                query = await session.execute(stmt)
            case 'or':
                stmt = select(self.model).where(or_(*where_list))
                query = await session.execute(stmt)
            case _:
                raise SelectExpressionError(
                    f'Select expression {expression} is not supported, only supports `and`, `or`'
                )
        return query.scalars().first()

    async def select_models(self, session: AsyncSession) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Query all rows

        :param session:
        :return:
        """
        stmt = select(self.model)
        query = await session.execute(stmt)
        return query.scalars().all()

    async def select_models_order(
        self,
        session: AsyncSession,
        *columns,
        model_sort: Literal['asc', 'desc'] = 'desc',
    ) -> Sequence[Row | RowMapping | Any] | None:
        """
        Query all rows asc or desc

        :param session:
        :param columns:
        :param model_sort:
        :return:
        """
        sort_list = []
        for column in columns:
            if hasattr(self.model, column):
                model_column = getattr(self.model, column)
                sort_list.append(model_column)
            else:
                raise ModelColumnError(f'Column {column} is not found in {self.model}')
        match model_sort:
            case 'asc':
                query = await session.execute(select(self.model).order_by(asc(*sort_list)))
            case 'desc':
                query = await session.execute(select(self.model).order_by(desc(*sort_list)))
            case _:
                raise SelectExpressionError(
                    f'Select sort expression {model_sort} is not supported, only supports `asc`, `desc`'
                )
        return query.scalars().all()

    async def update_model(
        self, session: AsyncSession, pk: int, obj: _UpdateSchema | dict[str, Any], commit: bool = False, **kwargs
    ) -> int:
        """
        Update an instance of model's primary key

        :param session:
        :param pk:
        :param obj:
        :param commit:
        :param kwargs:
        :return:
        """
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        if kwargs:
            instance_data.update(kwargs)
        stmt = sa_update(self.model).where(self.model.id == pk).values(**instance_data)
        result = await session.execute(stmt)
        if commit:
            await session.commit()
        return result.rowcount  # type: ignore

    async def update_model_by_column(
        self,
        session: AsyncSession,
        column: str,
        column_value: Any,
        obj: _UpdateSchema | dict[str, Any],
        commit: bool = False,
        **kwargs,
    ) -> int:
        """
        Update an instance of model column

        :param session:
        :param column:
        :param column_value:
        :param obj:
        :param commit:
        :param kwargs:
        :return:
        """
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        if kwargs:
            instance_data.update(kwargs)
        if hasattr(self.model, column):
            model_column = getattr(self.model, column)
        else:
            raise ModelColumnError(f'Column {column} is not found in {self.model}')
        stmt = sa_update(self.model).where(model_column == column_value).values(**instance_data)  # type: ignore
        result = await session.execute(stmt)
        if commit:
            await session.commit()
        return result.rowcount  # type: ignore

    async def delete_model(self, session: AsyncSession, pk: int, commit: bool = False, **kwargs) -> int:
        """
        Delete an instance of a model

        :param session:
        :param pk:
        :param commit:
        :param kwargs: for soft deletion only
        :return:
        """
        if not kwargs:
            stmt = sa_delete(self.model).where(self.model.id == pk)
            result = await session.execute(stmt)
        else:
            stmt = sa_update(self.model).where(self.model.id == pk).values(**kwargs)
            result = await session.execute(stmt)
        if commit:
            await session.commit()
        return result.rowcount  # type: ignore
