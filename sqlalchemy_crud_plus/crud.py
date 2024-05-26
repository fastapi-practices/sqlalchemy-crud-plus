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

    async def create_model(self, session: AsyncSession, obj: _CreateSchema, **kwargs) -> None:
        """
        Create a new instance of a model

        :param session:
        :param obj:
        :param kwargs:
        :return:
        """
        if kwargs:
            instance = self.model(**obj.model_dump(), **kwargs)
        else:
            instance = self.model(**obj.model_dump())
        session.add(instance)

    async def create_models(self, session: AsyncSession, obj: Iterable[_CreateSchema]) -> None:
        """
        Create new instances of a model

        :param session:
        :param obj:
        :return:
        """
        instance_list = []
        for i in obj:
            instance_list.append(self.model(**i.model_dump()))
        session.add_all(instance_list)

    async def select_model_by_id(self, session: AsyncSession, pk: int) -> _Model | None:
        """
        Query by ID

        :param session:
        :param pk:
        :return:
        """
        query = await session.execute(select(self.model).where(self.model.id == pk))
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
            query = await session.execute(select(self.model).where(model_column == column_value))  # type: ignore
            return query.scalars().first()
        else:
            raise ModelColumnError(f'Model column {column} is not found')

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
                raise ModelColumnError(f'Model column {column} is not found')
        match expression:
            case 'and':
                query = await session.execute(select(self.model).where(and_(*where_list)))
            case 'or':
                query = await session.execute(select(self.model).where(or_(*where_list)))
            case _:
                raise SelectExpressionError(f'select expression {expression} is not supported')
        return query.scalars().first()

    async def select_models(self, session: AsyncSession) -> Sequence[Row | RowMapping | Any] | None:
        """
        Query all rows

        :param session:
        :return:
        """
        query = await session.execute(select(self.model))
        return query.scalars().all()

    async def select_models_order(
        self,
        session: AsyncSession,
        *columns,
        model_sort: Literal['default', 'asc', 'desc'] = 'default',
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
                raise ModelColumnError(f'Model column {column} is not found')
        match model_sort:
            case 'default':
                query = await session.execute(select(self.model).order_by(*sort_list))
            case 'asc':
                query = await session.execute(select(self.model).order_by(asc(*sort_list)))
            case 'desc':
                query = await session.execute(select(self.model).order_by(desc(*sort_list)))
            case _:
                raise SelectExpressionError(f'select sort expression {model_sort} is not supported')
        return query.scalars().all()

    async def update_model(self, session: AsyncSession, pk: int, obj: _UpdateSchema | dict[str, Any], **kwargs) -> int:
        """
        Update an instance of model's primary key

        :param session:
        :param pk:
        :param obj:
        :param kwargs:
        :return:
        """
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        if kwargs:
            instance_data.update(kwargs)
        result = await session.execute(sa_update(self.model).where(self.model.id == pk).values(**instance_data))
        return result.rowcount  # type: ignore

    async def update_model_by_column(
        self, session: AsyncSession, column: str, column_value: Any, obj: _UpdateSchema | dict[str, Any], **kwargs
    ) -> int:
        """
        Update an instance of model column

        :param session:
        :param column:
        :param column_value:
        :param obj:
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
            raise ModelColumnError(f'Model column {column} is not found')
        result = await session.execute(
            sa_update(self.model).where(model_column == column_value).values(**instance_data)
        )
        return result.rowcount  # type: ignore

    async def delete_model(self, session: AsyncSession, pk: int, **kwargs) -> int:
        """
        Delete an instance of a model

        :param session:
        :param pk:
        :param kwargs: for soft deletion only
        :return:
        """
        if not kwargs:
            result = await session.execute(sa_delete(self.model).where(self.model.id == pk))
        else:
            result = await session.execute(sa_update(self.model).where(self.model.id == pk).values(**kwargs))
        return result.rowcount  # type: ignore
