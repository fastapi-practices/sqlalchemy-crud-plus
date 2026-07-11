from collections.abc import Callable
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Generic, Sequence, cast, overload

from sqlalchemy import (
    Column,
    ColumnExpressionArgument,
    CursorResult,
    Row,
    Select,
    delete,
    func,
    insert,
    inspect,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus.errors import (
    CompositePrimaryKeysError,
    ModelColumnError,
    MultipleResultsError,
    UpsertError,
)
from sqlalchemy_crud_plus.types import (
    CreateSchema,
    JoinConditions,
    LoadOptions,
    LoadStrategies,
    Model,
    PaginatedResult,
    SortColumns,
    SortOrders,
    UpdateSchema,
)
from sqlalchemy_crud_plus.utils import (
    apply_join_conditions,
    apply_sorting,
    build_load_strategies,
    get_column,
    has_join_fill_result,
    parse_filters,
    parse_update_values,
)

if TYPE_CHECKING:
    from sqlalchemy_crud_plus.query import DeleteBuilder, InsertBuilder, QueryBuilder, UpdateBuilder, UpsertBuilder


class CRUDPlus(Generic[Model]):
    def __init__(
        self,
        model: type[Model],
        filter_deleted: bool = False,
        deleted_flag_column: str = 'is_deleted',
        deleted_flag_value: Any = True,
    ):
        """
        :param model: The SQLAlchemy model class
        :param filter_deleted: If `True`, automatically exclude soft-deleted records from all
            query operations (select / count / exists), unless `include_deleted=True` is passed
        :param deleted_flag_column: Column name for the logical deletion flag
        :param deleted_flag_value: Value that marks a record as deleted
        """
        self.model = model
        self.model_column_names = [column.key for column in model.__table__.columns]
        self.primary_key = self._get_primary_key()
        self.filter_deleted = filter_deleted
        self.deleted_flag_column = deleted_flag_column
        self.deleted_flag_value = deleted_flag_value

        if filter_deleted and deleted_flag_column not in self.model_column_names:
            raise ModelColumnError(f'Column {deleted_flag_column} is not found in {model}')

    def _get_deleted_filters(self, include_deleted: bool) -> list[ColumnExpressionArgument[bool]]:
        """
        Get the soft deletion filter(s) when global soft deletion filtering is enabled.

        :param include_deleted: If `True`, soft-deleted records are not filtered out
        :return:
        """
        if not self.filter_deleted or include_deleted:
            return []
        column = get_column(self.model, self.deleted_flag_column)
        return [column != self.deleted_flag_value]

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

    def query(self, session: AsyncSession) -> 'QueryBuilder[Model]':
        """Create an immutable fluent query builder bound to ``session``."""
        from sqlalchemy_crud_plus.query import QueryBuilder

        return QueryBuilder(self, session, select(self.model), _models=(self.model,))

    def update_query(self, session: AsyncSession) -> 'UpdateBuilder[Model]':
        """Create a fluent update builder bound to ``session``."""
        from sqlalchemy_crud_plus.query import UpdateBuilder

        return UpdateBuilder(self, session)

    def delete_query(self, session: AsyncSession) -> 'DeleteBuilder[Model]':
        """Create a fluent delete builder bound to ``session``."""
        from sqlalchemy_crud_plus.query import DeleteBuilder

        return DeleteBuilder(self, session)

    def insert_query(self, session: AsyncSession) -> 'InsertBuilder[Model]':
        """Create a fluent insert builder bound to ``session``."""
        from sqlalchemy_crud_plus.query import InsertBuilder

        return InsertBuilder(self, session)

    def upsert_query(self, session: AsyncSession) -> 'UpsertBuilder[Model]':
        """Create a fluent upsert builder bound to ``session``."""
        from sqlalchemy_crud_plus.query import UpsertBuilder

        return UpsertBuilder(self, session)

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
        objs: Sequence[CreateSchema],
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

    async def bulk_create_models(
        self,
        session: AsyncSession,
        objs: Sequence[dict[str, Any]],
        render_nulls: bool = False,
        flush: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> Sequence[Model] | None:
        """
        Create new instances of a model.

        :param session: The SQLAlchemy async session
        :param objs: The dict list containing data to be saved，The dict data should be aligned with the model column
        :param render_nulls: render null values instead of ignoring them
        :param flush: If `True`, flush all object changes to the database
        :param commit: If `True`, commits the transaction immediately
        :param kwargs: Additional model data not included in the dict
        :return:
        """
        stmt = insert(self.model).values(**kwargs).execution_options(render_nulls=render_nulls)
        dialect = session.get_bind().dialect
        use_returning = getattr(dialect, 'insert_returning', False) and getattr(
            dialect, 'insert_executemany_returning', False
        )
        if use_returning:
            stmt = stmt.returning(self.model)
        result = await session.execute(stmt, objs)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        if use_returning:
            return result.scalars().all()

        return None

    async def upsert_model(
        self,
        session: AsyncSession,
        obj: CreateSchema | dict[str, Any],
        conflict_columns: list[str] | None = None,
        update_columns: list[str] | None = None,
        flush: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> Model | None:
        """
        Insert a new record or update the existing one on conflict (upsert).

        Supported dialects: PostgreSQL, SQLite (ON CONFLICT DO UPDATE) and MySQL / MariaDB
        (ON DUPLICATE KEY UPDATE).

        :param session: The SQLAlchemy async session
        :param obj: The Pydantic schema or dictionary containing data to be saved
        :param conflict_columns: Columns that determine the conflict, defaults to the primary key(s);
            ignored on MySQL / MariaDB, which always uses the primary key and unique indexes
        :param update_columns: Columns to update on conflict, defaults to all data columns
            except the conflict columns
        :param flush: If `True`, flush all object changes to the database
        :param commit: If `True`, commits the transaction immediately
        :param kwargs: Additional model data not included in the pydantic schema
        :return: The upserted model instance on dialects supporting RETURNING, otherwise `None`
        """
        obj_data = obj if isinstance(obj, dict) else obj.model_dump()
        if kwargs:
            obj_data = {**obj_data, **kwargs}

        if conflict_columns is None:
            pks = self.primary_key if isinstance(self.primary_key, list) else [self.primary_key]
            conflict_columns = [column.name for column in pks]
        else:
            for column in conflict_columns:
                if column not in self.model_column_names:
                    raise ModelColumnError(f'Column {column} is not found in {self.model}')

        if update_columns is None:
            update_columns = [key for key in obj_data if key not in conflict_columns]
        else:
            for column in update_columns:
                if column not in self.model_column_names:
                    raise ModelColumnError(f'Column {column} is not found in {self.model}')

        dialect = session.get_bind().dialect
        dialect_name = dialect.name

        if dialect_name == 'postgresql':
            from sqlalchemy.dialects.postgresql import insert as dialect_insert
        elif dialect_name == 'sqlite':
            from sqlalchemy.dialects.sqlite import insert as dialect_insert
        elif dialect_name in ('mysql', 'mariadb'):
            from sqlalchemy.dialects.mysql import insert as dialect_insert
        else:
            raise UpsertError(f'Upsert is not supported for dialect: {dialect_name}')

        stmt = dialect_insert(self.model).values(**obj_data)

        if dialect_name in ('mysql', 'mariadb'):
            if not update_columns:
                raise UpsertError('MySQL / MariaDB upsert requires at least one update column')
            stmt = stmt.on_duplicate_key_update(**{column: stmt.inserted[column] for column in update_columns})
        else:
            if update_columns:
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_columns,
                    set_={column: stmt.excluded[column] for column in update_columns},
                )
            else:
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_columns)

        # MySQL / MariaDB do not support RETURNING combined with ON DUPLICATE KEY UPDATE
        use_returning = dialect_name in ('postgresql', 'sqlite') and getattr(dialect, 'insert_returning', False)
        if use_returning:
            stmt = stmt.returning(self.model)

        # populate_existing refreshes identity-mapped instances with the RETURNING row
        result = await session.execute(stmt, execution_options={'populate_existing': True})

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        if use_returning:
            return result.scalars().first()

        return None

    async def count(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        join_conditions: JoinConditions | None = None,
        include_deleted: bool = False,
        **kwargs,
    ) -> int:
        """
        Count records that match specified filters.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param join_conditions: JOIN conditions for relationships
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        filters = list(whereclause)
        filters.extend(self._get_deleted_filters(include_deleted))

        if kwargs:
            filters.extend(parse_filters(self.model, **kwargs))

        if isinstance(self.primary_key, list):
            stmt = select(func.count()).select_from(self.model)
        else:
            stmt = select(func.count(self.primary_key)).select_from(self.model)

        if filters:
            stmt = stmt.where(*filters)

        if join_conditions:
            stmt = apply_join_conditions(self.model, stmt.select_from(self.model), join_conditions)

        query = await session.execute(stmt)
        total_count = query.scalar()
        return total_count if total_count is not None else 0

    async def exists(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        join_conditions: JoinConditions | None = None,
        include_deleted: bool = False,
        **kwargs,
    ) -> bool:
        """
        Check whether records that match the specified filters exist.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param join_conditions: JOIN conditions for relationships
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        filters = list(whereclause)
        filters.extend(self._get_deleted_filters(include_deleted))

        if kwargs:
            filters.extend(parse_filters(self.model, **kwargs))

        stmt = select(self.model).where(*filters).limit(1)

        if join_conditions:
            stmt = apply_join_conditions(self.model, stmt.select_from(self.model), join_conditions)

        query = await session.execute(stmt)
        return query.scalars().first() is not None

    @overload
    async def select_model(
        self,
        session: AsyncSession,
        pk: Any | Sequence[Any],
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Model | None: ...

    @overload
    async def select_model(
        self,
        session: AsyncSession,
        pk: Any | Sequence[Any],
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions = ...,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Row[Any] | Model | None: ...

    async def select_model(
        self,
        session: AsyncSession,
        pk: Any | Sequence[Any],
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Row[Any] | Model | None:
        """
        Query by primary key(s) with optional relationship loading and joins.

        :param session: SQLAlchemy async session
        :param pk: Primary key value(s) - single value or tuple for composite keys
        :param whereclause: Additional WHERE clauses
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        filters = list(whereclause)
        filters.extend(self._get_pk_filter(pk))
        filters.extend(self._get_deleted_filters(include_deleted))

        if kwargs:
            filters.extend(parse_filters(self.model, **kwargs))

        stmt = select(self.model).where(*filters)

        if load_options:
            stmt = stmt.options(*load_options)

        if join_conditions:
            stmt = apply_join_conditions(self.model, stmt.select_from(self.model), join_conditions)

        if load_strategies:
            rel_options = build_load_strategies(self.model, load_strategies)
            if rel_options:
                stmt = stmt.options(*rel_options)

        query = await session.execute(stmt)

        if join_conditions:
            if has_join_fill_result(join_conditions):
                return query.first()

        return query.scalars().first()

    @overload
    async def select_model_by_column(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Model | None: ...

    @overload
    async def select_model_by_column(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions = ...,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Row[Any] | Model | None: ...

    async def select_model_by_column(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Row[Any] | Model | None:
        """
        Query by column with optional relationship loading and joins.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        stmt = await self.select(
            *whereclause,
            load_options=load_options,
            load_strategies=load_strategies,
            join_conditions=join_conditions,
            include_deleted=include_deleted,
            **kwargs,
        )

        query = await session.execute(stmt)

        if join_conditions:
            if has_join_fill_result(join_conditions):
                return query.first()

        return query.scalars().first()

    async def select(
        self,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions | None = None,
        include_deleted: bool = False,
        **kwargs,
    ) -> Select:
        """
        Construct the SQLAlchemy selection.

        :param whereclause: WHERE clauses to apply to the query
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
        :param kwargs: Query expressions
        :return:
        """
        filters = list(whereclause)
        filters.extend(self._get_deleted_filters(include_deleted))
        filters.extend(parse_filters(self.model, **kwargs))
        stmt = select(self.model).where(*filters)

        if join_conditions:
            stmt = apply_join_conditions(self.model, stmt.select_from(self.model), join_conditions)

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
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions | None = None,
        include_deleted: bool = False,
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
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
        :param kwargs: Query expressions
        :return:
        """
        stmt = await self.select(
            *whereclause,
            load_options=load_options,
            load_strategies=load_strategies,
            join_conditions=join_conditions,
            include_deleted=include_deleted,
            **kwargs,
        )
        sorted_stmt = apply_sorting(self.model, stmt, sort_columns, sort_orders)
        return sorted_stmt

    @overload
    async def select_models(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Sequence[Model]: ...

    @overload
    async def select_models(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions = ...,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Sequence[Row[Any] | Model]: ...

    async def select_models(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Sequence[Row[Any] | Model]:
        """
        Query all rows that match the specified filters with optional relationship loading and joins.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param join_conditions: JOIN conditions for relationships
        :param limit: Maximum number of results to return
        :param offset: Number of results to skip
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        stmt = await self.select(
            *whereclause,
            load_options=load_options,
            load_strategies=load_strategies,
            join_conditions=join_conditions,
            include_deleted=include_deleted,
            **kwargs,
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        query = await session.execute(stmt)

        if join_conditions:
            if has_join_fill_result(join_conditions):
                return query.all()

        return query.scalars().all()

    @overload
    async def select_models_order(
        self,
        session: AsyncSession,
        sort_columns: SortColumns,
        sort_orders: SortOrders = None,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Sequence[Model]: ...

    @overload
    async def select_models_order(
        self,
        session: AsyncSession,
        sort_columns: SortColumns,
        sort_orders: SortOrders = None,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions = ...,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Sequence[Row[Any] | Model]: ...

    async def select_models_order(
        self,
        session: AsyncSession,
        sort_columns: SortColumns,
        sort_orders: SortOrders = None,
        *whereclause: ColumnExpressionArgument[bool],
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        join_conditions: JoinConditions | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Sequence[Row[Any] | Model]:
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
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
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
            include_deleted=include_deleted,
            **kwargs,
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        query = await session.execute(stmt)

        if join_conditions:
            if has_join_fill_result(join_conditions):
                return query.all()

        return query.scalars().all()

    async def select_models_paginated(
        self,
        session: AsyncSession,
        *whereclause: ColumnExpressionArgument[bool],
        page: int = 1,
        size: int = 20,
        sort_columns: SortColumns | None = None,
        sort_orders: SortOrders = None,
        load_options: LoadOptions | None = None,
        load_strategies: LoadStrategies | None = None,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> PaginatedResult[Model]:
        """
        Query a page of rows that match the specified filters, together with the total count.

        :param session: SQLAlchemy async session
        :param whereclause: Additional WHERE clauses
        :param page: Page number, starting from 1
        :param size: Page size, must be greater than 0
        :param sort_columns: Column names to sort by
        :param sort_orders: Sort orders ('asc' or 'desc')
        :param load_options: SQLAlchemy loading options
        :param load_strategies: Relationship loading strategies
        :param include_deleted: If `True`, include soft-deleted records when `filter_deleted` is enabled
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        if page < 1:
            raise ValueError('Page number must be greater than or equal to 1')
        if size < 1:
            raise ValueError('Page size must be greater than or equal to 1')

        total = await self.count(session, *whereclause, include_deleted=include_deleted, **kwargs)

        stmt = await self.select(
            *whereclause,
            load_options=load_options,
            load_strategies=load_strategies,
            include_deleted=include_deleted,
            **kwargs,
        )

        if sort_columns:
            stmt = apply_sorting(self.model, stmt, sort_columns, sort_orders)

        stmt = stmt.limit(size).offset((page - 1) * size)

        query = await session.execute(stmt)
        items = query.scalars().all()

        return PaginatedResult(items=items, total=total, page=page, size=size)

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

        Dictionary data supports atomic expression updates using the field__operator=value
        syntax, e.g. `{'clicks__add': 1}` generates `clicks = clicks + 1`.

        :param session: The SQLAlchemy async session.
        :param pk: Single value for simple primary key, or tuple for composite primary key.
        :param obj: A pydantic schema or dictionary containing the update data
        :param flush: If `True`, flush all object changes to the database. Default is `False`.
        :param commit: If `True`, commits the transaction immediately. Default is `False`.
        :param kwargs: Additional model data not included in the pydantic schema.
        :return:
        """
        filters = self._get_pk_filter(pk)
        data = dict(obj) if isinstance(obj, dict) else obj.model_dump(exclude_unset=True)
        data.update(kwargs)
        data = parse_update_values(self.model, data)
        stmt = update(self.model).where(*filters).values(**data)
        result = cast(CursorResult[Any], await session.execute(stmt))

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

        Dictionary data supports atomic expression updates using the field__operator=value
        syntax, e.g. `{'clicks__add': 1}` generates `clicks = clicks + 1`.

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
            total_count = await self.count(session, *filters, include_deleted=True)
            if total_count > 1:
                raise MultipleResultsError(f'Only one record is expected to be updated, found {total_count} records.')

        data = dict(obj) if isinstance(obj, dict) else obj.model_dump(exclude_unset=True)
        data = parse_update_values(self.model, data)
        stmt = update(self.model).where(*filters).values(**data)
        result = cast(CursorResult[Any], await session.execute(stmt))

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return result.rowcount

    async def bulk_update_models(
        self,
        session: AsyncSession,
        objs: Sequence[UpdateSchema | dict[str, Any]],
        pk_mode: bool = True,
        flush: bool = False,
        commit: bool = False,
        **kwargs,
    ) -> int:
        """
        Bulk update multiple instances with different data for each record.

        :param session: The SQLAlchemy async session
        :param objs: To save a list of Pydantic schemas or dict for data
        :param pk_mode: Primary key mode, when enabled, the data must contain the primary key data
        :param flush: If `True`, flush all object changes to the database
        :param commit: If `True`, commits the transaction immediately
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        datas = [obj if isinstance(obj, dict) else obj.model_dump(exclude_unset=True) for obj in objs]

        if not pk_mode:
            filters = parse_filters(self.model, **kwargs)

            if not filters:
                raise ValueError('At least one filter condition must be provided for update operation')

            if not datas:
                return 0
            if len(datas) > 1:
                raise ValueError(
                    'pk_mode=False supports exactly one update payload; use pk_mode=True for per-row updates'
                )

            stmt = update(self.model).where(*filters)
            conn = await session.connection()
            result = await conn.execute(stmt, datas)
            affected_count = result.rowcount
        else:
            if not datas:
                return 0

            await session.execute(update(self.model), datas)
            affected_count = len(datas)

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return affected_count

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
        result = cast(CursorResult[Any], await session.execute(stmt))

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
        deleted_flag_column: str = 'is_deleted',
        deleted_flag_value: Any = True,
        deleted_at_column: str = 'deleted_at',
        deleted_at_factory: datetime | Callable[[], datetime] | None = None,
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
        :param deleted_flag_value: Value written to logical deletion flag column
        :param deleted_at_column: Column name for delete time，automatic judgment
        :param deleted_at_factory: The delete time value or factory function
        :param flush: If `True`, flush all object changes to the database
        :param commit: If `True`, commits the transaction immediately
        :param kwargs: Filter expressions using field__operator=value syntax
        :return:
        """
        if logical_deletion:
            if deleted_flag_column not in self.model_column_names:
                raise ModelColumnError(f'Column {deleted_flag_column} is not found in {self.model}')

        filters = parse_filters(self.model, **kwargs)

        if not filters:
            raise ValueError('At least one filter condition must be provided for delete operation')

        if not allow_multiple:
            total_count = await self.count(session, *filters, include_deleted=True)
            if total_count > 1:
                raise MultipleResultsError(f'Only one record is expected to be deleted, found {total_count} records.')

        data: dict[str, Any] = {deleted_flag_column: deleted_flag_value}

        if deleted_at_column in self.model_column_names:
            if deleted_at_factory is None:
                data[deleted_at_column] = datetime.now(timezone.utc)
            elif isinstance(deleted_at_factory, datetime):
                data[deleted_at_column] = deleted_at_factory
            else:
                data[deleted_at_column] = deleted_at_factory()

        stmt = (
            update(self.model).where(*filters).values(**data)
            if logical_deletion
            else delete(self.model).where(*filters)
        )

        result = cast(CursorResult[Any], await session.execute(stmt))

        if flush:
            await session.flush()
        if commit:
            await session.commit()

        return result.rowcount
