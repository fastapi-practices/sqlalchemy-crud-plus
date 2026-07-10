from __future__ import annotations

import math

from dataclasses import dataclass
from typing import Any, Generic, Literal, Sequence, TypeVar

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
    'undefer',
    'undefer_group',
]

# https://docs.sqlalchemy.org/en/20/orm/queryguide/columns.html#column-loading-api
ColumnLoadingStrategyType = Literal[
    'defer',
    'load_only',
    'undefer',
    'undefer_group',
]

LoadStrategies = list[str] | dict[str, RelationshipLoadingStrategyType] | dict[str, ColumnLoadingStrategyType]

JoinType = Literal[
    'inner',
    'left',
    'full',
]


class JoinConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: type[DeclarativeBase] | AliasedClass | Alias | Table = Field(
        description='The target model, aliased class, alias, or table to join with'
    )
    join_on: Any = Field(description='The join condition expression (e.g., model.id == other_model.id)')
    join_type: JoinType = Field(default='left', description='The type of join to perform')
    fill_result: bool = Field(default=False, description='Whether to populate this model to the query result')


JoinConditions = list[str | JoinConfig] | dict[str, JoinType]

LoadOptions = list[ExecutableOption]

SortColumns = str | list[str]
SortOrders = str | list[str] | None

_T = TypeVar('_T')


@dataclass
class PaginatedResult(Generic[_T]):
    """Paginated query result with items and pagination metadata."""

    items: Sequence[_T]
    total: int
    page: int
    size: int

    @property
    def total_pages(self) -> int:
        if self.size <= 0:
            return 0
        return math.ceil(self.total / self.size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
