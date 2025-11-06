#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Alias, Table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.base import ExecutableOption

Model = TypeVar('Model', bound=DeclarativeBase)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)

# https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#relationship-loader-api
RelationshipLoadingStrategyType = Literal[
    'contains_eager',
    'defaultload',
    'immediateload',
    'joinedload',
    'lazyload',
    'noload',
    'raiseload',
    'selectinload',
    'subqueryload',
    # Load
    'defer',
    'load_only',
    'selectin_polymorphic',
    'undefer',
    'undefer_group',
    'with_expression',
]

# https://docs.sqlalchemy.org/en/20/orm/queryguide/columns.html#column-loading-api
ColumnLoadingStrategyType = Literal[
    'defer',
    'deferred',
    'load_only',
    'query_expression',
    'undefer',
    'undefer_group',
    'with_expression',
]

LoadStrategies = list[str] | dict[str, RelationshipLoadingStrategyType] | dict[str, ColumnLoadingStrategyType]

JoinType = Literal[
    'inner',
    'left',
    'full',
]


class JoinConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: type[Model] | AliasedClass | Alias | Table = Field(
        description='The target model, aliased class, alias, or table to join with'
    )
    join_on: Any = Field(description='The join condition expression (e.g., model.id == other_model.id)')
    join_type: JoinType = Field(default='left', description='The type of join to perform')
    fill_result: bool = Field(default=False, description='Whether to populate this model to the query result')


JoinConditions = list[str | JoinConfig] | dict[str, JoinType]

LoadOptions = list[ExecutableOption]

SortColumns = str | list[str]
SortOrders = str | list[str] | None
