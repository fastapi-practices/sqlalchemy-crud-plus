#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Literal, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.base import ExecutableOption

# Base type variables for generic CRUD operations
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

LoadStrategies = list[str] | dict[str, RelationshipLoadingStrategyType]

# https://docs.sqlalchemy.org/en/20/orm/queryguide/columns.html#column-loading-api
ColumnLoadingStrategyType = Literal[
    'defer', 'deferred', 'load_only', 'query_expression', 'undefer', 'undefer_group', 'with_expression'
]

JoinType = Literal[
    'inner',
    'left',
    'full',
]

JoinConditions = list[str] | dict[str, JoinType]

QueryOptions = list[ExecutableOption]

SortColumns = str | list[str]
SortOrders = str | list[str] | None
