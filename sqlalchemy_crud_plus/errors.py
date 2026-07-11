class SQLAlchemyCRUDPlusException(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class ModelColumnError(SQLAlchemyCRUDPlusException):
    """Error raised when an SCP column is invalid."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class SelectOperatorError(SQLAlchemyCRUDPlusException):
    """Error raised when a select expression is invalid."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class ColumnSortError(SQLAlchemyCRUDPlusException):
    """Error raised when a column sorting is invalid."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class MultipleResultsError(SQLAlchemyCRUDPlusException):
    """Error raised when multiple results are invalid."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class CompositePrimaryKeysError(SQLAlchemyCRUDPlusException):
    """Error raised when a table have Composite primary keys."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class LoadingStrategyError(SQLAlchemyCRUDPlusException):
    """Error raised when a loading strategy is invalid."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class JoinConditionError(SQLAlchemyCRUDPlusException):
    """Error raised when a join operation is invalid."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class UpsertError(SQLAlchemyCRUDPlusException):
    """Error raised when an upsert operation is invalid."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class QueryBuilderError(SQLAlchemyCRUDPlusException):
    """Error raised when a fluent query cannot be constructed or executed."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class UnsafeWriteError(QueryBuilderError):
    """Error raised for an update or delete without an explicit user filter."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
