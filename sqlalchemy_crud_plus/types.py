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

# SQLAlchemy relationship loading strategies
LoadingStrategy = Literal[
    'selectinload',  # SELECT IN loading (recommended for one-to-many)
    'joinedload',  # JOIN loading (recommended for one-to-one)
    'subqueryload',  # Subquery loading (for large datasets)
    'contains_eager',  # Use with explicit JOINs
    'raiseload',  # Prevent lazy loading
    'noload',  # Don't load relationship
]

# SQL JOIN types
JoinType = Literal[
    'inner',  # INNER JOIN
    'left',  # LEFT OUTER JOIN
    'right',  # RIGHT OUTER JOIN
    'full',  # FULL OUTER JOIN
]

# Configuration for relationship loading strategies
LoadStrategiesConfig = list[str] | dict[str, LoadingStrategy]

# Configuration for JOIN conditions
JoinConditionsConfig = list[str] | dict[str, JoinType]

# Query configuration types
SortColumns = str | list[str]
SortOrders = str | list[str] | None
QueryOptions = list[ExecutableOption]
