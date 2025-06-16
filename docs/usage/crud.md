# 基础用法

SQLAlchemy CRUD Plus 提供完整的 CRUD（创建、读取、更新、删除）操作。

## 创建记录

### 单条记录

```python
# 使用 Pydantic 模型创建
user_data = UserCreate(name="张三", email="zhangsan@example.com")
user = await user_crud.create_model(session, user_data)
```

### 批量创建

```python
# 批量创建多条记录
users_data = [
    UserCreate(name="用户1", email="user1@example.com"),
    UserCreate(name="用户2", email="user2@example.com"),
    UserCreate(name="用户3", email="user3@example.com")
]
users = await user_crud.create_models(session, users_data)
```

## 查询记录

### 主键查询

```python
# 基础查询
user = await user_crud.select_model(session, pk=1)

# 结合 whereclause 位置参数
user = await user_crud.select_model(session, pk=1, user_crud.model.is_active == True)

# 结合 kwargs 关键字参数
user = await user_crud.select_model(session, pk=1, is_active=True)
```

### 条件查询

```python
# 基础查询
user = await user_crud.select_model_by_column(session, email="zhangsan@example.com")

# 复杂查询
user = await user_crud.select_model_by_column(
    session,
    user_crud.model.is_active == True,
    email="zhangsan@example.com"
)
```

### 批量查询

```python
# 基础查询
users = await user_crud.select_models(session)

# 使用 whereclause 位置参数
users = await user_crud.select_models(
    session,
    user_crud.model.created_time > datetime.now() - timedelta(days=7)
)

# 使用 kwargs 关键字参数
users = await user_crud.select_models(session, is_active=True, name__like="%张%")

# 分页查询
users = await user_crud.select_models(session, limit=10, offset=20)
```

### 排序查询

```python
# 基础排序
users = await user_crud.select_models_order(session, sort_columns="created_time", sort_orders="desc")

# 多列排序
users = await user_crud.select_models_order(
    session,
    sort_columns=["name", "created_time"],
    sort_orders=["asc", "desc"]
)

# 结合过滤和分页
users = await user_crud.select_models_order(
    session,
    sort_columns="created_time",
    sort_orders="desc",
    user_crud.model.is_active == True,
    limit=10,
    name__like="%张%"
)
```

### 计数和存在检查

```python
# 基础计数
total = await user_crud.count(session)

# 使用 whereclause 位置参数
count = await user_crud.count(session, user_crud.model.created_time > datetime.now() - timedelta(days=30))

# 使用 kwargs 关键字参数
active_count = await user_crud.count(session, is_active=True)

# 存在检查
exists = await user_crud.exists(session, email="test@example.com")
```

## 更新记录

### 主键更新

```python
# 使用字典更新
updated_count = await user_crud.update_model(session, pk=1, obj={"name": "新名称"})

# 使用 Pydantic 模型
user_update = UserUpdate(name="新名称", email="new@example.com")
updated_count = await user_crud.update_model(session, pk=1, obj=user_update)

# 使用 whereclause 位置参数（额外条件）
updated_count = await user_crud.update_model(
    session,
    pk=1,
    obj={"name": "新名称"},
    user_crud.model.is_active == True
)
```

### 条件更新

```python
# 根据条件更新单条记录
updated_count = await user_crud.update_model_by_column(
    session,
    obj={"is_active": False},
    email="user@example.com"
)

# 使用 whereclause 位置参数（额外条件）
updated_count = await user_crud.update_model_by_column(
    session,
    obj={"name": "新名称"},
    user_crud.model.is_active == True,
    email="user@example.com"
)
```

## 删除记录

### 主键删除

```python
# 根据主键删除
deleted_count = await user_crud.delete_model(session, pk=1)

# 使用 whereclause 位置参数（额外条件）
deleted_count = await user_crud.delete_model(
    session,
    pk=1,
    user_crud.model.is_active == False
)
```

### 条件删除

```python
# 根据条件删除
deleted_count = await user_crud.delete_model_by_column(
    session,
    is_active=False
)

# 使用 whereclause 位置参数（额外条件）
deleted_count = await user_crud.delete_model_by_column(
    session,
    user_crud.model.created_time < datetime.now() - timedelta(days=30),
    is_active=False
)
```

## 分页查询

```python
# 基础分页
def paginated_users(page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size

    users = await user_crud.select_models_order(
        session,
        sort_columns="created_time",
        sort_orders="desc",
        limit=page_size,
        offset=offset
    )

    total = await user_crud.count(session)

    return {
        'users': users,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }
```
