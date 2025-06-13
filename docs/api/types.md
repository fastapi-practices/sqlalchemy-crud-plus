# 类型定义

本页面记录了 SQLAlchemy CRUD Plus 中使用的类型定义。

## 核心类型

### 模型类型

```python
from typing import TypeVar
from sqlalchemy.ext.declarative import DeclarativeMeta

# Generic model type
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)

# Schema types
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
```

### CRUDPlus 泛型

```python
from typing import Generic, TypeVar
from sqlalchemy_crud_plus import CRUDPlus

# Usage with type hints
user_crud: CRUDPlus[User] = CRUDPlus(User)
post_crud: CRUDPlus[Post] = CRUDPlus(Post)
```

## 关系类型

### LoadStrategiesConfig

```python
from typing import Union, Dict, List

LoadStrategiesConfig = Union[
    List[str],  # Simple list format
    Dict[str, str],  # Strategy mapping
    Dict[str, Dict[str, str]]  # Nested strategies
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
    List[str],  # Simple list format
    Dict[str, str]  # JOIN type mapping
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

### 常用过滤器模式

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

## 会话类型

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

## 工具类型

### 主键类型

```python
from typing import Union, Tuple, Any

# Single or composite primary key
PrimaryKeyType = Union[Any, Tuple[Any, ...]]

# Examples
pk: PrimaryKeyType = 1  # Single primary key
pk: PrimaryKeyType = (1, 2)  # Composite primary key
pk: PrimaryKeyType = "uuid-string"  # String primary key
```

### 排序配置

```python
from typing import Union, List

SortColumns = Union[str, List[str]]
SortOrders = Union[str, List[str]]

# Examples
sort_columns: SortColumns = "created_time"
sort_columns: SortColumns = ["created_time", "name"]

sort_orders: SortOrders = "desc"
sort_orders: SortOrders = ["desc", "asc"]
```
