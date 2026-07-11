from __future__ import annotations

import inspect

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Generic, Mapping, Sequence, TypeGuard, TypeVar, cast

from pydantic import BaseModel
from sqlalchemy import delete, func, insert, or_, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import Select
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import ClauseElement, ColumnElement

from sqlalchemy_crud_plus.errors import QueryBuilderError, UnsafeWriteError, UpsertError
from sqlalchemy_crud_plus.types import JoinConditions, LoadStrategies, Model, PaginatedResult
from sqlalchemy_crud_plus.utils import (
    apply_join_conditions,
    build_load_strategies,
    get_column,
    parse_filters,
    parse_update_values,
)

if TYPE_CHECKING:
    from sqlalchemy_crud_plus.crud import CRUDPlus


_JoinedModel = TypeVar('_JoinedModel')
ExpressionFactory = Callable[..., Any]


def _dump(value: BaseModel | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, BaseModel):
        return value.model_dump(exclude_unset=True)
    return dict(value)


def _dump_many(
    values: BaseModel | Mapping[str, Any] | Sequence[BaseModel | Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(values, BaseModel):
        return [_dump(values)]
    if isinstance(values, Mapping):
        return [dict(cast(Mapping[str, Any], values))]
    return [_dump(value) for value in values]


def _is_expression_factory(value: Any) -> TypeGuard[ExpressionFactory]:
    return callable(value) and not isinstance(value, (type, ClauseElement, InstrumentedAttribute))


def _factory_arity(factory: ExpressionFactory) -> tuple[int, bool]:
    try:
        parameters = inspect.signature(factory).parameters.values()
    except (TypeError, ValueError):
        return 1, False
    positional = [
        parameter
        for parameter in parameters
        if parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    has_varargs = any(parameter.kind is inspect.Parameter.VAR_POSITIONAL for parameter in parameters)
    return len(positional), has_varargs


def _call_expression_factory(factory: ExpressionFactory, models: tuple[Any, ...]) -> Any:
    arity, has_varargs = _factory_arity(factory)
    if arity > len(models) and not has_varargs:
        raise QueryBuilderError(
            f'Expression expects {arity} model arguments, but the query currently contains {len(models)} model(s)'
        )
    return factory(*models if has_varargs else models[:arity])


def _flatten_expression_result(value: Any, *, labels: bool = False) -> list[Any]:
    if isinstance(value, Mapping):
        expressions = []
        for label, expression in value.items():
            if labels and isinstance(label, str):
                if not hasattr(expression, 'label'):
                    raise QueryBuilderError(f'Projection value for {label!r} cannot be labelled')
                expression = expression.label(label)
            expressions.append(expression)
        return expressions
    if isinstance(value, (tuple, list)):
        return list(value)
    return [value]


def _resolve_expressions(
    values: Sequence[Any],
    models: tuple[Any, ...],
    *,
    labels: bool = False,
) -> list[Any]:
    expressions: list[Any] = []
    for value in values:
        if _is_expression_factory(value):
            value = _call_expression_factory(value, models)
        expressions.extend(_flatten_expression_result(value, labels=labels))
    return expressions


def _validate_predicates(expressions: Sequence[Any]) -> list[ColumnElement[bool]]:
    predicates: list[ColumnElement[bool]] = []
    for expression in expressions:
        if isinstance(expression, bool) or not (
            isinstance(expression, ClauseElement) or hasattr(expression, '__clause_element__')
        ):
            raise QueryBuilderError(
                'Where expressions must return SQLAlchemy boolean expressions; use &, |, where(), or where_or() '
                'instead of Python and/or'
            )
        predicates.append(cast(ColumnElement[bool], expression))
    return predicates


def _column_name(value: Any) -> str:
    if isinstance(value, str):
        return value
    name = getattr(value, 'key', None) or getattr(value, 'name', None)
    if not isinstance(name, str):
        raise QueryBuilderError(f'{value!r} is not a mapped column')
    return name


def _returns_model(returning: tuple[Any, ...], model: type[Any]) -> bool:
    return len(returning) == 1 and returning[0] is model


def _resolve_update_mapping(
    crud: CRUDPlus[Any],
    value: BaseModel | Mapping[Any, Any] | ExpressionFactory,
) -> dict[Any, Any]:
    if _is_expression_factory(value):
        value = _call_expression_factory(value, (crud.model,))
    if isinstance(value, BaseModel):
        value = value.model_dump(exclude_unset=True)
    if not isinstance(value, Mapping):
        raise QueryBuilderError('Update values must be a mapping, Pydantic model, or expression factory')

    string_values = {key: item for key, item in value.items() if isinstance(key, str)}
    column_values = {key: item for key, item in value.items() if not isinstance(key, str)}
    column_values.update(parse_update_values(crud.model, string_values))
    return column_values


@dataclass(frozen=True)
class QueryBuilder(Generic[Model]):
    """Immutable asynchronous query builder backed by a SQLAlchemy statement."""

    crud: CRUDPlus[Model]
    session: AsyncSession
    _statement: Any
    _models: tuple[Any, ...] = ()
    _criteria: tuple[ColumnElement[bool], ...] = ()
    _include_deleted: bool = False
    _model_result: bool = True
    _unique_result: bool = False
    _write_compatible: bool = True

    def _deleted_criteria(self) -> tuple[ColumnElement[bool], ...]:
        return cast(tuple[ColumnElement[bool], ...], tuple(self.crud._get_deleted_filters(self._include_deleted)))

    def _final_statement(self) -> Any:
        deleted = self._deleted_criteria()
        return self._statement.where(*deleted) if deleted else self._statement

    @property
    def statement(self) -> Any:
        """Return the final SQLAlchemy statement, including the soft-delete filter."""
        return self._final_statement()

    def where(
        self,
        expression: ColumnElement[bool] | Callable[[type[Model]], Any] | None = None,
        /,
        *expressions: ColumnElement[bool],
        **filters: Any,
    ) -> QueryBuilder[Model]:
        values = expressions if expression is None else (expression, *expressions)
        criteria = _validate_predicates(_resolve_expressions(values, self._models))
        criteria.extend(parse_filters(self.crud.model, **filters))
        if not criteria:
            return self
        stmt = self._statement.where(*criteria)
        return replace(self, _statement=stmt, _criteria=(*self._criteria, *criteria))

    def where_if(
        self,
        condition: bool,
        expression: ColumnElement[bool] | Callable[[type[Model]], Any],
        **filters: Any,
    ) -> QueryBuilder[Model]:
        return self.where(cast(Any, expression), **filters) if condition else self

    def where_or(
        self,
        *expressions: ColumnElement[bool] | Callable[[type[Model]], Any],
    ) -> QueryBuilder[Model]:
        criteria = _validate_predicates(_resolve_expressions(expressions, self._models))
        return self.where(or_(*criteria)) if criteria else self

    def or_if(
        self,
        condition: bool,
        expression: ColumnElement[bool] | Callable[[type[Model]], Any],
    ) -> QueryBuilder[Model]:
        return self.where_or(cast(Any, expression)) if condition else self

    def include_deleted(self, enabled: bool = True) -> QueryBuilder[Model]:
        return replace(self, _include_deleted=enabled)

    def select(
        self,
        *entities: ClauseElement | InstrumentedAttribute[Any] | type[Any] | Callable[[type[Model]], Any],
    ) -> QueryBuilder[Model]:
        entities = tuple(_resolve_expressions(entities, self._models, labels=True))
        if not entities:
            raise QueryBuilderError('At least one entity or expression must be selected')
        stmt = self._statement.with_only_columns(*entities, maintain_column_froms=True)
        model_result = len(entities) == 1 and entities[0] is self.crud.model
        return replace(self, _statement=stmt, _model_result=model_result, _write_compatible=False)

    def distinct(
        self,
        *expressions: ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> QueryBuilder[Model]:
        expressions = tuple(_resolve_expressions(expressions, self._models))
        return replace(
            self,
            _statement=self._statement.distinct(*expressions),
            _write_compatible=False,
        )

    def group_by(
        self,
        *expressions: ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> QueryBuilder[Model]:
        expressions = tuple(_resolve_expressions(expressions, self._models))
        return replace(
            self,
            _statement=self._statement.group_by(*expressions),
            _write_compatible=False,
        )

    def having(
        self,
        *expressions: ColumnElement[bool] | Callable[[type[Model]], Any],
    ) -> QueryBuilder[Model]:
        expressions = tuple(_validate_predicates(_resolve_expressions(expressions, self._models)))
        return replace(
            self,
            _statement=self._statement.having(*expressions),
            _write_compatible=False,
        )

    def join(
        self,
        target: type[_JoinedModel],
        onclause: Callable[[type[Model], type[_JoinedModel]], Any] | ColumnElement[bool] | None = None,
        *,
        join_type: str = 'inner',
        fill_result: bool = False,
    ) -> QueryBuilder[Model]:
        if join_type not in ('inner', 'left', 'full'):
            raise QueryBuilderError('join_type must be one of: inner, left, full')

        join_target: Any = target
        if _is_expression_factory(join_target):
            join_target = _call_expression_factory(join_target, self._models)

        if isinstance(join_target, str) and onclause is None:
            join_target = getattr(self.crud.model, join_target, None)
            if join_target is None:
                raise QueryBuilderError(f'Join target is not found on {self.crud.model}')

        target_model = join_target if isinstance(join_target, type) else None
        if target_model is None:
            target_model = getattr(getattr(getattr(join_target, 'property', None), 'mapper', None), 'class_', None)

        if _is_expression_factory(onclause):
            arity, _ = _factory_arity(onclause)
            join_models = (
                (self.crud.model, target_model)
                if target_model is not None and arity <= 2
                else (*self._models, target_model)
            )
            onclause = _call_expression_factory(onclause, tuple(model for model in join_models if model is not None))

        if join_type == 'inner':
            stmt = (
                self._statement.join(join_target, onclause)
                if onclause is not None
                else self._statement.join(join_target)
            )
        elif join_type == 'left':
            stmt = (
                self._statement.join(join_target, onclause, isouter=True)
                if onclause is not None
                else self._statement.join(join_target, isouter=True)
            )
        else:
            stmt = (
                self._statement.join(join_target, onclause, full=True)
                if onclause is not None
                else self._statement.join(join_target, full=True)
            )

        if fill_result:
            stmt = stmt.add_columns(target_model or join_target)

        models = self._models
        if target_model is not None and target_model not in models:
            models = (*models, target_model)

        return replace(
            self,
            _statement=stmt,
            _models=models,
            _model_result=self._model_result and not fill_result,
            _write_compatible=False,
        )

    def join_relationship(
        self,
        relationship: InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
        *,
        join_type: str = 'inner',
        fill_result: bool = False,
    ) -> QueryBuilder[Model]:
        return self.join(
            cast(Any, relationship),
            join_type=join_type,
            fill_result=fill_result,
        )

    def joins(self, conditions: JoinConditions) -> QueryBuilder[Model]:
        stmt = apply_join_conditions(self.crud.model, self._statement, conditions)
        from sqlalchemy_crud_plus.utils import has_join_fill_result

        return replace(
            self,
            _statement=stmt,
            _model_result=self._model_result and not has_join_fill_result(conditions),
            _write_compatible=False,
        )

    def options(self, *options: ExecutableOption) -> QueryBuilder[Model]:
        return replace(self, _statement=self._statement.options(*options))

    def load(
        self,
        strategies: LoadStrategies | Callable[[type[Model]], Any],
        strategy: str = 'selectinload',
    ) -> QueryBuilder[Model]:
        if _is_expression_factory(strategies):
            attributes = _resolve_expressions((strategies,), self._models)
            strategy_config = {_column_name(attribute): strategy for attribute in attributes}
            options = build_load_strategies(self.crud.model, cast(LoadStrategies, strategy_config))
        else:
            options = build_load_strategies(self.crud.model, cast(LoadStrategies, strategies))
        return self.options(*options)

    def order_by(
        self,
        *expressions: str | ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> QueryBuilder[Model]:
        clauses = []
        for expression in _resolve_expressions(expressions, self._models):
            if isinstance(expression, str):
                descending = expression.startswith('-')
                name = expression[1:] if expression[:1] in ('-', '+') else expression
                column = get_column(self.crud.model, name)
                clauses.append(column.desc() if descending else column.asc())
            else:
                clauses.append(expression)
        return replace(self, _statement=self._statement.order_by(*clauses))

    def take(self, value: int) -> QueryBuilder[Model]:
        return self.limit(value)

    def limit(self, value: int | None) -> QueryBuilder[Model]:
        if value is not None and value < 0:
            raise ValueError('Limit must be greater than or equal to 0')
        return replace(self, _statement=self._statement.limit(value), _write_compatible=False)

    def offset(self, value: int | None) -> QueryBuilder[Model]:
        if value is not None and value < 0:
            raise ValueError('Offset must be greater than or equal to 0')
        return replace(self, _statement=self._statement.offset(value), _write_compatible=False)

    def page(self, page: int, size: int) -> QueryBuilder[Model]:
        if page < 1 or size < 1:
            raise ValueError('Page and size must be greater than or equal to 1')
        return self.limit(size).offset((page - 1) * size)

    def for_update(self, **kwargs: Any) -> QueryBuilder[Model]:
        return replace(self, _statement=self._statement.with_for_update(**kwargs), _write_compatible=False)

    def add_cte(self, *ctes: Any, nest_here: bool = False) -> QueryBuilder[Model]:
        return replace(
            self,
            _statement=self._statement.add_cte(*ctes, nest_here=nest_here),
            _write_compatible=False,
        )

    def subquery(self, name: str | None = None) -> Any:
        return self._final_statement().subquery(name)

    def cte(self, name: str | None = None, recursive: bool = False, nesting: bool = False) -> Any:
        return self._final_statement().cte(name=name, recursive=recursive, nesting=nesting)

    def union(self, *others: QueryBuilder[Any] | Select[Any]) -> QueryBuilder[Model]:
        statements = [other.statement if isinstance(other, QueryBuilder) else other for other in others]
        return replace(
            self,
            _statement=self._final_statement().union(*statements),
            _include_deleted=True,
            _model_result=False,
            _write_compatible=False,
        )

    def union_all(self, *others: QueryBuilder[Any] | Select[Any]) -> QueryBuilder[Model]:
        statements = [other.statement if isinstance(other, QueryBuilder) else other for other in others]
        return replace(
            self,
            _statement=self._final_statement().union_all(*statements),
            _include_deleted=True,
            _model_result=False,
            _write_compatible=False,
        )

    def unique(self, enabled: bool = True) -> QueryBuilder[Model]:
        return replace(self, _unique_result=enabled)

    def to_sql(self, *, literal_binds: bool = False) -> str:
        bind = self.session.get_bind()
        return str(self._final_statement().compile(bind, compile_kwargs={'literal_binds': literal_binds}))

    async def _execute(self, statement: Any | None = None) -> Any:
        result = await self.session.execute(statement if statement is not None else self._final_statement())
        return result.unique() if self._unique_result else result

    async def all(self) -> Sequence[Any]:
        result = await self._execute()
        return result.scalars().all() if self._model_result else result.all()

    async def to_list(self) -> Sequence[Any]:
        return await self.all()

    async def first(
        self,
        predicate: ColumnElement[bool] | Callable[[type[Model]], Any] | None = None,
    ) -> Any | None:
        query = self.where(predicate) if predicate is not None else self
        result = await query._execute(query._final_statement().limit(1))
        return result.scalars().first() if self._model_result else result.first()

    async def one(self) -> Any:
        result = await self._execute()
        return result.scalars().one() if self._model_result else result.one()

    async def one_or_none(self) -> Any | None:
        result = await self._execute()
        return result.scalars().one_or_none() if self._model_result else result.one_or_none()

    async def single(
        self,
        predicate: ColumnElement[bool] | Callable[[type[Model]], Any] | None = None,
    ) -> Any | None:
        return await (self.where(predicate) if predicate is not None else self).one_or_none()

    async def scalars(self) -> Sequence[Any]:
        result = await self._execute()
        return result.scalars().all()

    async def scalar(self) -> Any | None:
        result = await self._execute()
        return result.scalar()

    async def scalar_one(self) -> Any:
        result = await self._execute()
        return result.scalar_one()

    async def count(
        self,
        selector: ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any] | None = None,
    ) -> int:
        if selector is not None:
            expressions = _resolve_expressions((selector,), self._models)
            if len(expressions) != 1:
                raise QueryBuilderError('count() accepts exactly one column expression')
            stmt = (
                self._final_statement()
                .with_only_columns(func.count(expressions[0]), maintain_column_froms=True)
                .order_by(None)
                .limit(None)
                .offset(None)
            )
            result = await self.session.execute(stmt)
            return int(result.scalar_one())
        stmt = self._final_statement().order_by(None).limit(None).offset(None)
        result = await self.session.execute(select(func.count()).select_from(stmt.subquery()))
        return int(result.scalar_one())

    async def exists(
        self,
        predicate: ColumnElement[bool] | Callable[[type[Model]], Any] | None = None,
    ) -> bool:
        query = self.where(predicate) if predicate is not None else self
        stmt = query._final_statement().order_by(None).limit(None).offset(None)
        result = await self.session.execute(select(stmt.exists()))
        return bool(result.scalar_one())

    async def any(
        self,
        predicate: ColumnElement[bool] | Callable[[type[Model]], Any] | None = None,
    ) -> bool:
        return await self.exists(predicate)

    async def _aggregate(
        self,
        function: Callable[[Any], Any],
        selector: ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> Any:
        expressions = _resolve_expressions((selector,), self._models)
        if len(expressions) != 1:
            raise QueryBuilderError('Aggregate methods accept exactly one column expression')
        stmt = (
            self._final_statement()
            .with_only_columns(function(expressions[0]), maintain_column_froms=True)
            .order_by(None)
            .limit(None)
            .offset(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def max(
        self,
        selector: ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> Any:
        return await self._aggregate(func.max, selector)

    async def min(
        self,
        selector: ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> Any:
        return await self._aggregate(func.min, selector)

    async def sum(
        self,
        selector: ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> Any:
        return await self._aggregate(func.sum, selector)

    async def avg(
        self,
        selector: ClauseElement | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> Any:
        return await self._aggregate(func.avg, selector)

    async def paginate(self, page: int = 1, size: int = 20) -> PaginatedResult[Any]:
        if page < 1 or size < 1:
            raise ValueError('Page and size must be greater than or equal to 1')
        total = await self.count()
        items = await self.page(page, size).all()
        return PaginatedResult(items=items, total=total, page=page, size=size)

    async def stream(self) -> AsyncResult[Any]:
        return await self.session.stream(self._final_statement())

    def _ensure_write_compatible(self) -> None:
        if not self._write_compatible:
            raise QueryBuilderError(
                'This query contains projection, join, grouping, pagination, or locking and cannot be converted '
                'to a portable update/delete statement'
            )

    async def update(
        self,
        values: BaseModel | Mapping[Any, Any] | Callable[[type[Model]], Mapping[Any, Any]],
        *,
        flush: bool = False,
        commit: bool = False,
    ) -> int:
        self._ensure_write_compatible()
        builder = UpdateBuilder(self.crud, self.session).where(*self._criteria)
        if self._include_deleted:
            builder = builder.include_deleted()
        return await builder.set(values).execute(flush=flush, commit=commit)

    async def delete(self, *, flush: bool = False, commit: bool = False) -> int:
        self._ensure_write_compatible()
        builder = DeleteBuilder(self.crud, self.session).where(*self._criteria)
        if self._include_deleted:
            builder = builder.include_deleted()
        return await builder.execute(flush=flush, commit=commit)

    async def soft_delete(
        self,
        *,
        deleted_flag_column: str | None = None,
        deleted_flag_value: Any | None = None,
        deleted_at_column: str | None = None,
        deleted_at_value: Any | None = None,
        flush: bool = False,
        commit: bool = False,
    ) -> int:
        self._ensure_write_compatible()
        values: dict[str, Any] = {
            deleted_flag_column or self.crud.deleted_flag_column: (
                self.crud.deleted_flag_value if deleted_flag_value is None else deleted_flag_value
            )
        }
        if deleted_at_column is not None:
            values[deleted_at_column] = deleted_at_value if deleted_at_value is not None else datetime.now(timezone.utc)
        builder = UpdateBuilder(self.crud, self.session).where(*self._criteria).set(values)
        return await builder.execute(flush=flush, commit=commit)


@dataclass(frozen=True)
class UpdateBuilder(Generic[Model]):
    crud: CRUDPlus[Model]
    session: AsyncSession
    _criteria: tuple[ColumnElement[bool], ...] = ()
    _values: Mapping[Any, Any] | None = None
    _allow_all: bool = False
    _include_deleted: bool = False
    _returning: tuple[Any, ...] = ()

    def where(
        self,
        *expressions: ColumnElement[bool] | Callable[[type[Model]], Any],
        **filters: Any,
    ) -> UpdateBuilder[Model]:
        criteria = _validate_predicates(_resolve_expressions(expressions, (self.crud.model,)))
        criteria.extend(parse_filters(self.crud.model, **filters))
        return replace(self, _criteria=(*self._criteria, *criteria))

    def where_if(
        self,
        condition: bool,
        *expressions: ColumnElement[bool] | Callable[[type[Model]], Any],
        **filters: Any,
    ) -> UpdateBuilder[Model]:
        return self.where(*expressions, **filters) if condition else self

    def set(
        self,
        values: BaseModel | Mapping[Any, Any] | Callable[[type[Model]], Mapping[Any, Any]],
        **kwargs: Any,
    ) -> UpdateBuilder[Model]:
        data = _resolve_update_mapping(self.crud, values)
        if kwargs:
            data.update(parse_update_values(self.crud.model, kwargs))
        return replace(self, _values=data)

    def returning(
        self,
        *entities: ClauseElement | InstrumentedAttribute[Any] | type[Any] | Callable[[type[Model]], Any],
    ) -> UpdateBuilder[Model]:
        entities = tuple(_resolve_expressions(entities, (self.crud.model,)))
        return replace(self, _returning=entities or (self.crud.model,))

    def allow_all(self, enabled: bool = True) -> UpdateBuilder[Model]:
        return replace(self, _allow_all=enabled)

    def include_deleted(self, enabled: bool = True) -> UpdateBuilder[Model]:
        return replace(self, _include_deleted=enabled)

    async def execute(self, *, flush: bool = False, commit: bool = False) -> Any:
        if not self._criteria and not self._allow_all:
            raise UnsafeWriteError('Update requires an explicit WHERE condition; call allow_all() to override')
        if self._values is None:
            raise QueryBuilderError('No update values were provided')
        criteria = [*self._criteria, *self.crud._get_deleted_filters(self._include_deleted)]
        stmt = update(self.crud.model).where(*criteria).values(self._values)
        if self._returning:
            stmt = stmt.returning(*self._returning)
        result = await self.session.execute(stmt)
        if flush:
            await self.session.flush()
        if commit:
            await self.session.commit()
        if self._returning:
            return result.scalars().all() if _returns_model(self._returning, self.crud.model) else result.all()
        return cast(CursorResult[Any], result).rowcount


@dataclass(frozen=True)
class DeleteBuilder(Generic[Model]):
    crud: CRUDPlus[Model]
    session: AsyncSession
    _criteria: tuple[ColumnElement[bool], ...] = ()
    _allow_all: bool = False
    _include_deleted: bool = False
    _returning: tuple[Any, ...] = ()

    def where(
        self,
        *expressions: ColumnElement[bool] | Callable[[type[Model]], Any],
        **filters: Any,
    ) -> DeleteBuilder[Model]:
        criteria = _validate_predicates(_resolve_expressions(expressions, (self.crud.model,)))
        criteria.extend(parse_filters(self.crud.model, **filters))
        return replace(self, _criteria=(*self._criteria, *criteria))

    def where_if(
        self,
        condition: bool,
        *expressions: ColumnElement[bool] | Callable[[type[Model]], Any],
        **filters: Any,
    ) -> DeleteBuilder[Model]:
        return self.where(*expressions, **filters) if condition else self

    def returning(
        self,
        *entities: ClauseElement | InstrumentedAttribute[Any] | type[Any] | Callable[[type[Model]], Any],
    ) -> DeleteBuilder[Model]:
        entities = tuple(_resolve_expressions(entities, (self.crud.model,)))
        return replace(self, _returning=entities or (self.crud.model,))

    def allow_all(self, enabled: bool = True) -> DeleteBuilder[Model]:
        return replace(self, _allow_all=enabled)

    def include_deleted(self, enabled: bool = True) -> DeleteBuilder[Model]:
        return replace(self, _include_deleted=enabled)

    async def execute(self, *, flush: bool = False, commit: bool = False) -> Any:
        if not self._criteria and not self._allow_all:
            raise UnsafeWriteError('Delete requires an explicit WHERE condition; call allow_all() to override')
        criteria = [*self._criteria, *self.crud._get_deleted_filters(self._include_deleted)]
        stmt = delete(self.crud.model).where(*criteria)
        if self._returning:
            stmt = stmt.returning(*self._returning)
        result = await self.session.execute(stmt)
        if flush:
            await self.session.flush()
        if commit:
            await self.session.commit()
        if self._returning:
            return result.scalars().all() if _returns_model(self._returning, self.crud.model) else result.all()
        return cast(CursorResult[Any], result).rowcount


@dataclass(frozen=True)
class InsertBuilder(Generic[Model]):
    crud: CRUDPlus[Model]
    session: AsyncSession
    _values: tuple[dict[str, Any], ...] = ()
    _returning: tuple[Any, ...] = ()

    def values(
        self,
        values: BaseModel | Mapping[str, Any] | Sequence[BaseModel | Mapping[str, Any]],
    ) -> InsertBuilder[Model]:
        return replace(self, _values=tuple(_dump_many(values)))

    def returning(
        self,
        *entities: ClauseElement | InstrumentedAttribute[Any] | type[Any] | Callable[[type[Model]], Any],
    ) -> InsertBuilder[Model]:
        entities = tuple(_resolve_expressions(entities, (self.crud.model,)))
        return replace(self, _returning=entities or (self.crud.model,))

    async def execute(self, *, flush: bool = False, commit: bool = False) -> Any:
        if not self._values:
            raise QueryBuilderError('No insert values were provided')
        payload: Any = self._values[0] if len(self._values) == 1 else list(self._values)
        stmt = insert(self.crud.model).values(payload)
        if self._returning:
            stmt = stmt.returning(*self._returning)
        result = await self.session.execute(stmt)
        if flush:
            await self.session.flush()
        if commit:
            await self.session.commit()
        if self._returning:
            return result.scalars().all() if _returns_model(self._returning, self.crud.model) else result.all()
        return cast(CursorResult[Any], result).rowcount


@dataclass(frozen=True)
class UpsertBuilder(Generic[Model]):
    crud: CRUDPlus[Model]
    session: AsyncSession
    _values: tuple[dict[str, Any], ...] = ()
    _conflict_columns: tuple[str, ...] | None = None
    _update_columns: tuple[str, ...] | None = None
    _do_nothing: bool = False
    _returning: tuple[Any, ...] = ()

    def values(
        self,
        values: BaseModel | Mapping[str, Any] | Sequence[BaseModel | Mapping[str, Any]],
    ) -> UpsertBuilder[Model]:
        return replace(self, _values=tuple(_dump_many(values)))

    def conflict_on(
        self,
        *columns: str | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> UpsertBuilder[Model]:
        resolved = _resolve_expressions(columns, (self.crud.model,))
        names = tuple(_column_name(column) for column in resolved)
        for column in names:
            get_column(self.crud.model, column)
        return replace(self, _conflict_columns=names)

    def update_columns(
        self,
        *columns: str | InstrumentedAttribute[Any] | Callable[[type[Model]], Any],
    ) -> UpsertBuilder[Model]:
        resolved = _resolve_expressions(columns, (self.crud.model,))
        names = tuple(_column_name(column) for column in resolved)
        for column in names:
            get_column(self.crud.model, column)
        return replace(self, _update_columns=names, _do_nothing=False)

    def do_nothing(self, enabled: bool = True) -> UpsertBuilder[Model]:
        return replace(self, _do_nothing=enabled)

    def returning(
        self,
        *entities: ClauseElement | InstrumentedAttribute[Any] | type[Any] | Callable[[type[Model]], Any],
    ) -> UpsertBuilder[Model]:
        entities = tuple(_resolve_expressions(entities, (self.crud.model,)))
        return replace(self, _returning=entities or (self.crud.model,))

    async def execute(self, *, flush: bool = False, commit: bool = False) -> Any:
        if not self._values:
            raise QueryBuilderError('No upsert values were provided')

        dialect_name = self.session.get_bind().dialect.name
        if dialect_name == 'postgresql':
            from sqlalchemy.dialects.postgresql import insert as dialect_insert
        elif dialect_name == 'sqlite':
            from sqlalchemy.dialects.sqlite import insert as dialect_insert
        elif dialect_name in ('mysql', 'mariadb'):
            from sqlalchemy.dialects.mysql import insert as dialect_insert
        else:
            raise UpsertError(f'Upsert is not supported for dialect: {dialect_name}')

        payload: Any = self._values[0] if len(self._values) == 1 else list(self._values)
        stmt: Any = dialect_insert(self.crud.model).values(payload)
        pks = self.crud.primary_key if isinstance(self.crud.primary_key, list) else [self.crud.primary_key]
        conflict_columns = self._conflict_columns or tuple(column.name for column in pks)
        all_columns = tuple(key for key in self._values[0] if key not in conflict_columns)
        update_columns = self._update_columns if self._update_columns is not None else all_columns

        if dialect_name in ('mysql', 'mariadb'):
            if self._do_nothing:
                raise UpsertError('MySQL / MariaDB does not support do_nothing in this builder')
            if not update_columns:
                raise UpsertError('MySQL / MariaDB upsert requires at least one update column')
            stmt = stmt.on_duplicate_key_update(**{column: stmt.inserted[column] for column in update_columns})
        elif self._do_nothing or not update_columns:
            stmt = stmt.on_conflict_do_nothing(index_elements=conflict_columns)
        else:
            stmt = stmt.on_conflict_do_update(
                index_elements=conflict_columns,
                set_={column: stmt.excluded[column] for column in update_columns},
            )

        if self._returning:
            stmt = stmt.returning(*self._returning)
        result = await self.session.execute(stmt, execution_options={'populate_existing': True})
        if flush:
            await self.session.flush()
        if commit:
            await self.session.commit()
        if self._returning:
            return result.scalars().all() if _returns_model(self._returning, self.crud.model) else result.all()
        return cast(CursorResult[Any], result).rowcount
