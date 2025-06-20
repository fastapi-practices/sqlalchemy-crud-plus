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
from typing import Literal

LoadingStrategy = Literal[
    'selectinload',  # SELECT IN loading (recommended for one-to-many)
    'joinedload',  # JOIN loading (recommended for one-to-one)
    'subqueryload',  # Subquery loading (for large datasets)
    'contains_eager',  # Use with explicit JOINs
    'raiseload',  # Prevent lazy loading
    'noload',  # Don't load relationship
]

# Configuration for relationship loading strategies
LoadStrategiesConfig = list[str] | dict[str, LoadingStrategy]

# Examples
load_strategies: LoadStrategiesConfig = ['posts', 'profile']
load_strategies: LoadStrategiesConfig = {
    'posts': 'selectinload',
    'profile': 'joinedload'
}
```

### JoinConditionsConfig

```python
from typing import Literal

JoinType = Literal[
    'inner',  # INNER JOIN
    'left',  # LEFT OUTER JOIN
    'right',  # RIGHT OUTER JOIN
    'full',  # FULL OUTER JOIN
]

# Configuration for JOIN conditions
JoinConditionsConfig = list[str] | dict[str, JoinType]

# Examples
join_conditions: JoinConditionsConfig = ['posts', 'profile']
join_conditions: JoinConditionsConfig = {
    'posts': 'inner',
    'profile': 'left'
}
```

### QueryOptions

```python
from sqlalchemy.sql.base import ExecutableOption

QueryOptions = list[ExecutableOption]

# Example
from sqlalchemy.orm import selectinload, joinedload

load_options: QueryOptions = [
    selectinload(User.posts),
    joinedload(User.profile)
]
```

## 工具类型

### 常用过滤器模式

```python
# Comparison operators
age__gt: int = 30
age__ge: int = 18
age__lt: int = 65
age__le: int = 60
status__ne: int = 0

# Range operators
id__in: list[int] = [1, 2, 3, 4, 5]
status__not_in: list[int] = [0, -1]
age__between: list[int] = [30, 40]

# String operators
name__like: str = '%张%'
name__ilike: str = '%ADMIN%'
email__startswith: str = 'admin'
email__endswith: str = '@qq.com'

# Null checks
deleted_at__is: None = None
profile_id__is_not: None = None

# OR conditions
__or__: dict[str, Any] = {
    'email__endswith': ['@gmail.com', '@qq.com']
}
```

### 排序配置

```python
SortColumns = str | list[str]
SortOrders = str | list[str] | None

# Examples
sort_columns: SortColumns = "created_time"
sort_columns: SortColumns = ["created_time", "name"]

sort_orders: SortOrders = "desc"
sort_orders: SortOrders = ["desc", "asc"]
```
