# CRUDPlus API 参考

`CRUDPlus` 类是执行 CRUD 操作和关系查询的主要接口。

## 类定义

::: sqlalchemy_crud_plus.CRUDPlus

## 构造函数

```python
from sqlalchemy_crud_plus import CRUDPlus
from myapp.models import User

user_crud = CRUDPlus(User)
```

## Query Methods

### select_model

::: sqlalchemy_crud_plus.CRUDPlus.select_model

### select_model_by_column

::: sqlalchemy_crud_plus.CRUDPlus.select_model_by_column

### select_models

::: sqlalchemy_crud_plus.CRUDPlus.select_models

### select_models_order

::: sqlalchemy_crud_plus.CRUDPlus.select_models_order

### count

::: sqlalchemy_crud_plus.CRUDPlus.count

### exists

::: sqlalchemy_crud_plus.CRUDPlus.exists

## Create Methods

### create_model

::: sqlalchemy_crud_plus.CRUDPlus.create_model

### create_models

::: sqlalchemy_crud_plus.CRUDPlus.create_models

## Update Methods

### update_model

::: sqlalchemy_crud_plus.CRUDPlus.update_model

### update_model_by_column

::: sqlalchemy_crud_plus.CRUDPlus.update_model_by_column

## Delete Methods

### delete_model

::: sqlalchemy_crud_plus.CRUDPlus.delete_model

### delete_model_by_column

::: sqlalchemy_crud_plus.CRUDPlus.delete_model_by_column

## Low-level Methods

### select

::: sqlalchemy_crud_plus.CRUDPlus.select

### select_order

::: sqlalchemy_crud_plus.CRUDPlus.select_order

## Usage Examples

### Basic CRUD

```python
from sqlalchemy_crud_plus import CRUDPlus
from myapp.models import User
from myapp.schemas import UserCreate, UserUpdate

user_crud = CRUDPlus(User)

# Create
user_data = UserCreate(name="Alice", email="alice@example.com")
user = await user_crud.create_model(session, user_data)

# Read
user = await user_crud.select_model(session, user.id)

# Update
user_update = UserUpdate(name="Alice Smith")
updated_user = await user_crud.update_model(session, user.id, user_update)

# Delete
await user_crud.delete_model(session, user.id)
```

### Relationship Queries

```python
# Load with relationships
user = await user_crud.select_model(
    session, user_id,
    load_strategies=['posts', 'profile'],
    join_conditions={'posts': 'inner'}
)

# Count with relationships
count = await user_crud.count(
    session,
    join_conditions=['posts']
)

# Check existence with relationships
exists = await user_crud.exists(
    session,
    join_conditions={'posts': 'inner'},
    name='Alice'
)
```

### Advanced Filtering

```python
# Complex filters
users = await user_crud.select_models(
    session,
    name__like='%smith%',
    age__gte=18,
    is_active=True,
    __or__={'email__like': ['%@gmail.com', '%@yahoo.com']}
)

# With relationships
users = await user_crud.select_models(
    session,
    load_strategies={'posts': 'selectinload'},
    join_conditions={'profile': 'left'},
    name__ilike='alice%'
)
```
