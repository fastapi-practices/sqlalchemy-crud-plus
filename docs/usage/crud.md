# 基础用法

SQLAlchemy CRUD Plus 提供完整的 CRUD（创建、读取、更新、删除）操作。

## 创建操作

### 创建单条记录

```python
# 使用 Pydantic 模型
user_data = UserCreate(name="张三", email="zhangsan@example.com")
user = await user_crud.create_model(session, user_data)

# 使用 kwargs 传递额外数据
user = await user_crud.create_model(session, user_data, is_verified=True)

# 立即提交
user = await user_crud.create_model(session, user_data, commit=True)

# 获取主键（不提交事务）
user = await user_crud.create_model(session, user_data, flush=True)
print(f"用户ID: {user.id}")  # 可以立即获取主键
```

### 批量创建

```python
# 批量创建
users_data = [
    UserCreate(name="用户1", email="user1@example.com"),
    UserCreate(name="用户2", email="user2@example.com"),
    UserCreate(name="用户3", email="user3@example.com")
]
users = await user_crud.create_models(session, users_data)

# 使用字典批量创建（高性能方式）
users_dict = [
    {"name": "用户4", "email": "user4@example.com"},
    {"name": "用户5", "email": "user5@example.com"}
]
users = await user_crud.bulk_create_models(session, users_dict)
```

## 查询操作

### 主键查询

```python
# 根据主键查询
user = await user_crud.select_model(session, pk=1)

# 复合主键查询
user_role = await user_role_crud.select_model(session, pk=(1, 2))

# 结合条件查询
user = await user_crud.select_model(
    session,
    pk=1,
    is_active=True  # 额外条件
)
```

### 条件查询

```python
# 根据字段查询单条记录
user = await user_crud.select_model_by_column(session, email="zhangsan@example.com")

# 查询多条记录
users = await user_crud.select_models(session, is_active=True)

# 分页查询
users = await user_crud.select_models(session, limit=10, offset=20)
```

### 排序查询

```python
# 单列排序
users = await user_crud.select_models_order(
    session,
    sort_columns="created_at",
    sort_orders="desc"
)

# 多列排序
users = await user_crud.select_models_order(
    session,
    sort_columns=["name", "created_at"],
    sort_orders=["asc", "desc"]
)

# 结合条件和分页
users = await user_crud.select_models_order(
    session,
    sort_columns="created_at",
    sort_orders="desc",
    is_active=True,
    limit=10
)
```

### 统计查询

```python
# 统计总数
total = await user_crud.count(session)

# 条件统计
active_count = await user_crud.count(session, is_active=True)

# 检查是否存在
exists = await user_crud.exists(session, email="test@example.com")
if not exists:
    # 不存在则创建
    user = await user_crud.create_model(session, user_data)
```

## 更新操作

### 主键更新

```python
# 使用字典更新
await user_crud.update_model(session, pk=1, obj={"name": "新名称"})

# 使用 Pydantic 模型更新
user_update = UserUpdate(name="新名称", email="new@example.com")
await user_crud.update_model(session, pk=1, obj=user_update)

# 立即提交
await user_crud.update_model(session, pk=1, obj={"name": "新名称"}, commit=True)

# 复合主键更新
await user_role_crud.update_model(
    session,
    pk=(1, 2),
    obj={"assigned_at": datetime.now()}
)
```

### 批量更新（不同数据）

```python
# 使用 bulk_update_models 批量更新不同的数据
users_update = [
    {"id": 1, "name": "张三三", "email": "zhangsan_new@example.com"},
    {"id": 2, "name": "李四四", "email": "lisi_new@example.com"}
]
await user_crud.bulk_update_models(session, users_update)
```

### 条件更新（相同数据）

```python
# 根据条件更新单条记录
await user_crud.update_model_by_column(
    session,
    obj={"is_active": False},
    email="user@example.com"
)

# 批量更新相同数据
await user_crud.update_model_by_column(
    session,
    obj={"last_login": datetime.now()},
    allow_multiple=True,
    is_active=True
)
```

## 删除操作

### 主键删除

```python
# 根据主键删除
deleted_count = await user_crud.delete_model(session, pk=1)

# 复合主键删除
deleted_count = await user_role_crud.delete_model(session, pk=(1, 2))

# 立即提交
await user_crud.delete_model(session, pk=1, commit=True)
```

### 条件删除

```python
# 根据条件删除
deleted_count = await user_crud.delete_model_by_column(
    session,
    name='张三'
)

# 批量删除
deleted_count = await user_crud.delete_model_by_column(
    session,
    allow_multiple=True,
    created_at__lt=datetime.now() - timedelta(days=30)
)

# 逻辑删除（软删除）
deleted_count = await user_crud.delete_model_by_column(
    session,
    logical_deletion=True,  # 启用逻辑删除
    allow_multiple=False,
    id=1
)
```

## 事务控制

### 自动事务管理

```python
# 推荐的事务模式
async with async_session.begin() as session:
    # 所有操作在同一事务中
    user = await user_crud.create_model(session, user_data)
    profile = await profile_crud.create_model(session, profile_data)
    # 自动提交或回滚
```

### 使用 flush 和 commit

```python
async with async_session() as session:
    # 创建用户并立即获取主键
    user = await user_crud.create_model(session, user_data, flush=True)

    # 使用获取到的主键创建关联记录
    profile_data.user_id = user.id
    profile = await profile_crud.create_model(session, profile_data)

    # 手动提交
    await session.commit()
```

## 实用示例

### 分页查询实现

```python
async def get_users_paginated(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        **filters
):
    offset = (page - 1) * page_size

    # 查询数据
    users = await user_crud.select_models(
        session,
        **filters,
        limit=page_size,
        offset=offset
    )

    # 统计总数
    total = await user_crud.count(session, **filters)

    return {
        'items': users,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }
```

### 安全的查询操作

```python
async def get_user_safely(session: AsyncSession, user_id: int):
    """安全获取用户，处理不存在的情况"""
    user = await user_crud.select_model(session, pk=user_id)
    if not user:
        raise ValueError(f"用户 {user_id} 不存在")
    return user


async def get_or_create_user(session: AsyncSession, email: str, name: str):
    """获取用户，不存在则创建"""
    user = await user_crud.select_model_by_column(session, email=email)
    if not user:
        user_data = UserCreate(name=name, email=email)
        user = await user_crud.create_model(session, user_data)
    return user
```

### 查询构建方法

```python
# 使用 select 方法构建查询
stmt = await user_crud.select(
    User.is_active == True,
    load_strategies=['posts'],
    name__like='%张%'
)

# 使用 select_order 方法构建排序查询  
stmt = await user_crud.select_order(
    sort_columns=['name', 'created_at'],
    sort_orders=['asc', 'desc'],
    is_active=True
)
```

### 批量操作示例

```python
async def batch_update_users(session: AsyncSession, user_updates: list[dict]):
    """批量更新用户（使用高性能批量更新）"""
    # 方式1：批量更新不同数据
    return await user_crud.bulk_update_models(session, user_updates)


async def batch_update_same_data(session: AsyncSession, update_data: dict, **filters):
    """批量更新相同数据"""
    # 方式2：条件更新相同数据
    return await user_crud.update_model_by_column(
        session,
        obj=update_data,
        **filters
    )
```

## 注意事项

1. **主键参数**: 由于 `id` 是 Python 关键字，主键参数使用 `pk`
2. **事务管理**: 推荐使用 `async with session.begin()` 自动管理事务
3. **flush vs commit**: `flush` 用于获取主键，`commit` 用于立即提交
4. **复合主键**: 使用元组格式，如 `pk=(1, 2)`
5. **错误处理**: 查询不存在的记录返回 `None`，删除不存在的记录返回 `0`
6. **批量操作**: 大量数据操作时优先使用 `bulk_*` 方法
