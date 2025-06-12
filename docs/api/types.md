# 类型

本页面记录了 SQLAlchemy CRUD Plus 中使用的类型定义。

## Core Types

### Model Types

```python
from typing import TypeVar
from sqlalchemy.ext.declarative import DeclarativeMeta

# Generic model type
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)

# Schema types
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
```

### CRUDPlus Generic

```python
from typing import Generic, TypeVar
from sqlalchemy_crud_plus import CRUDPlus

# Usage with type hints
user_crud: CRUDPlus[User] = CRUDPlus(User)
post_crud: CRUDPlus[Post] = CRUDPlus(Post)
```

## Relationship Types

### LoadStrategiesConfig

```python
from typing import Union, Dict, List

LoadStrategiesConfig = Union[
    List[str],                          # Simple list format
    Dict[str, str],                     # Strategy mapping
    Dict[str, Dict[str, str]]           # Nested strategies
]

# Examples
load_strategies: LoadStrategiesConfig = ['posts', 'profile']
load_strategies: LoadStrategiesConfig = {
    'posts': 'selectinload',
    'profile': 'joinedload'
}
```

### JoinConditionsConfig

```python
from typing import Union, Dict, List

JoinConditionsConfig = Union[
    List[str],                          # Simple list format
    Dict[str, str]                      # JOIN type mapping
]

# Examples
join_conditions: JoinConditionsConfig = ['posts', 'profile']
join_conditions: JoinConditionsConfig = {
    'posts': 'inner',
    'profile': 'left'
}
```

### QueryOptions

```python
from typing import List, Any
from sqlalchemy.orm import Load

QueryOptions = List[Load]

# Example
from sqlalchemy.orm import selectinload, joinedload

load_options: QueryOptions = [
    selectinload(User.posts),
    joinedload(User.profile)
]
```

## Filter Types

### FilterOperators

```python
from typing import Any, Dict, List, Union

# Basic filter value
FilterValue = Union[str, int, float, bool, None, List[Any]]

# OR filter structure
OrFilter = Dict[str, List[Any]]

# Filter parameters
FilterParams = Dict[str, Union[FilterValue, OrFilter]]
```

### Common Filter Patterns

```python
# Comparison operators
age__gt: int = 30
age__ge: int = 18
age__lt: int = 65
age__le: int = 60
status__ne: int = 0

# Range operators
id__in: List[int] = [1, 2, 3, 4, 5]
status__not_in: List[int] = [0, -1]
age__between: List[int] = [30, 40]

# String operators
name__like: str = '%张%'
name__ilike: str = '%ADMIN%'
email__startswith: str = 'admin'
email__endswith: str = '@qq.com'

# Null checks
deleted_at__is: None = None
profile_id__is_not: None = None

# OR conditions
__or__: Dict[str, List[Any]] = {
    'email__endswith': ['@gmail.com', '@qq.com']
}
```

## Session Types

### AsyncSession

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Session factory type
AsyncSessionFactory = async_sessionmaker[AsyncSession]

# Usage
_async_db_session: AsyncSessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False
)
```

## Return Types

### CRUD Operation Returns

```python
from typing import Optional, List, Union

# Single model operations
async def select_model(...) -> Optional[ModelType]: ...
async def create_model(...) -> ModelType: ...
async def update_model(...) -> Optional[ModelType]: ...

# Multiple model operations
async def select_models(...) -> List[ModelType]: ...
async def create_models(...) -> List[ModelType]: ...

# Count and existence
async def count(...) -> int: ...
async def exists(...) -> bool: ...

# Delete operations
async def delete_model(...) -> int: ...
async def delete_model_by_column(...) -> int: ...
```

## Utility Types

### Primary Key Types

```python
from typing import Union, Tuple, Any

# Single or composite primary key
PrimaryKeyType = Union[Any, Tuple[Any, ...]]

# Examples
pk: PrimaryKeyType = 1                    # Single primary key
pk: PrimaryKeyType = (1, 2)               # Composite primary key
pk: PrimaryKeyType = "uuid-string"        # String primary key
```

### Sort Configuration

```python
from typing import Union, List

SortColumns = Union[str, List[str]]
SortOrders = Union[str, List[str]]

# Examples
sort_columns: SortColumns = "created_at"
sort_columns: SortColumns = ["created_at", "name"]

sort_orders: SortOrders = "desc"
sort_orders: SortOrders = ["desc", "asc"]
```

## Type Checking

### Runtime Type Validation

```python
from typing import get_type_hints
from sqlalchemy_crud_plus import CRUDPlus

def validate_crud_types(crud_instance: CRUDPlus) -> bool:
    """Validate CRUD instance types at runtime"""
    hints = get_type_hints(crud_instance.__class__)
    return all(hint for hint in hints.values())
```

### IDE Support

```python
# Full type hints for IDE support
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import User, Post
    from schemas import UserCreate, UserUpdate, PostCreate, PostUpdate

# Type-safe CRUD instances
user_crud: CRUDPlus[User] = CRUDPlus(User)
post_crud: CRUDPlus[Post] = CRUDPlus(Post)

# IDE will provide full autocomplete and type checking
async def typed_operations():
    async with _async_db_session() as session:
        # IDE knows the return type is Optional[User]
        user = await user_crud.select_model(session, 1)
        
        # IDE knows the return type is List[User]
        users = await user_crud.select_models(session, limit=10)
```
