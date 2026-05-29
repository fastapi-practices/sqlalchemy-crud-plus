# CRUD 操作

本页按“创建、查询、更新、删除”的顺序说明常用 API。示例默认已有 `user_crud = CRUDPlus(User)` 和可用的 `AsyncSession`。

## 方法速查

| 场景 | 方法 | 返回值 |
| --- | --- | --- |
| 创建单条 | `create_model` | ORM 实例 |
| 创建多条 | `create_models` | ORM 实例列表 |
| 高性能批量插入 | `bulk_create_models` | 实例列表或 `None` |
| 主键查询 | `select_model` | ORM 实例或 `None` |
| 条件查询单条 | `select_model_by_column` | ORM 实例或 `None` |
| 条件查询多条 | `select_models` | ORM 实例列表 |
| 排序查询 | `select_models_order` | ORM 实例列表 |
| 主键更新 | `update_model` | 影响行数 |
| 条件更新 | `update_model_by_column` | 影响行数 |
| 批量更新不同数据 | `bulk_update_models` | 影响行数 |
| 主键删除 | `delete_model` | 影响行数 |
| 条件删除 | `delete_model_by_column` | 影响行数 |
| 统计 / 存在 | `count` / `exists` | `int` / `bool` |

## 创建

```python
# 单条创建。默认不提交事务。
user = await user_crud.create_model(session, UserCreate(name='张三', email='a@example.com'))

# 需要立即获得自增主键时使用 flush=True。
user = await user_crud.create_model(session, user_data, flush=True)
print(user.id)

# 独立操作可以直接提交。
user = await user_crud.create_model(session, user_data, commit=True)
```

批量创建有两种方式：

```python
# 返回 ORM 实例，适合普通批量创建。
users = await user_crud.create_models(session, [
    UserCreate(name='用户1', email='u1@example.com'),
    UserCreate(name='用户2', email='u2@example.com')
])

# 更接近 SQLAlchemy bulk insert，适合大量字典数据。
users = await user_crud.bulk_create_models(session, [
    {'name': '用户3', 'email': 'u3@example.com'},
    {'name': '用户4', 'email': 'u4@example.com'}
])

# 部分数据库方言不支持 executemany RETURNING，此时数据已写入但不返回实例。
if users is None:
    print('inserted without returned ORM instances')
```

## 查询

```python
# 主键查询。
user = await user_crud.select_model(session, pk=1)

# 复合主键使用元组。
user_role = await user_role_crud.select_model(session, pk=(1, 2))

# 字段查询单条。
user = await user_crud.select_model_by_column(session, email='a@example.com')

# 条件查询多条 + 分页。
users = await user_crud.select_models(
    session,
    is_active=True,
    limit=20,
    offset=0
)
```

过滤条件直接写在关键字参数中：

```python
users = await user_crud.select_models(
    session,
    name__like='%张%',
    age__ge=18,
    email__endswith='@example.com'
)
```

完整过滤操作符见 [过滤条件](../advanced/filter.md)。

## 排序和分页

```python
# 单字段排序。
users = await user_crud.select_models_order(
    session,
    sort_columns='created_at',
    sort_orders='desc',
    limit=20
)

# 多字段排序。
users = await user_crud.select_models_order(
    session,
    sort_columns=['name', 'created_at'],
    sort_orders=['asc', 'desc']
)
```

## 字段加载控制

字段加载适合列表页或大字段模型。它不会改变返回类型，只会影响 SQL 查询的列。

```python
# 只加载列表页需要的字段。
users = await user_crud.select_models(
    session,
    load_strategies={
        'id': 'load_only',
        'name': 'load_only',
        'email': 'load_only'
    }
)

# 延迟加载大字段。
users = await user_crud.select_models(
    session,
    load_strategies={
        'bio': 'defer',
        'extra_data': 'defer'
    }
)
```

!!! warning

    异步场景中访问未加载字段可能触发额外 IO。列表页建议显式使用 `load_only` 或 `defer`，详情页则一次加载需要的字段。

## 更新

```python
# 主键更新，obj 支持 dict 或 Pydantic 模型。
count = await user_crud.update_model(
    session,
    pk=1,
    obj={'name': '新名称'}
)

# 条件更新单条。默认不允许命中多条。
count = await user_crud.update_model_by_column(
    session,
    obj={'is_active': False},
    email='a@example.com'
)

# 条件更新多条，需要 allow_multiple=True。
count = await user_crud.update_model_by_column(
    session,
    obj={'is_active': False},
    allow_multiple=True,
    created_at__lt='2024-01-01'
)
```

批量更新不同记录时，默认按主键匹配：

```python
count = await user_crud.bulk_update_models(session, [
    {'id': 1, 'name': '张三'},
    {'id': 2, 'name': '李四'}
])
```

如果要用过滤条件更新相同数据，优先使用 `update_model_by_column`。`bulk_update_models(pk_mode=False)` 只接受一个更新 payload，并返回实际影响行数：

```python
count = await user_crud.bulk_update_models(
    session,
    [{'is_active': False}],
    pk_mode=False,
    last_login__lt='2024-01-01'
)
```

## 删除

```python
# 主键删除。
count = await user_crud.delete_model(session, pk=1)

# 复合主键删除。
count = await user_role_crud.delete_model(session, pk=(1, 2))

# 条件删除。默认只允许命中一条。
count = await user_crud.delete_model_by_column(session, email='a@example.com')

# 删除多条需要 allow_multiple=True。
count = await user_crud.delete_model_by_column(
    session,
    allow_multiple=True,
    is_active=False
)
```

逻辑删除默认会把标记字段设为 `True`。如果模型包含删除时间字段，也会写入当前时间。

```python
count = await user_crud.delete_model_by_column(
    session,
    logical_deletion=True,
    deleted_flag_column='is_deleted',
    deleted_at_column='deleted_at',
    id=1
)
```

如果逻辑删除标记需要写入自定义值，可以使用 `deleted_flag_value`。该参数也支持 SQLAlchemy 表达式，例如把 `deleted` 字段写成当前行的 `id`。

```python
count = await user_crud.delete_model_by_column(
    session,
    logical_deletion=True,
    deleted_flag_column='deleted',
    deleted_flag_value=User.id,
    deleted_at_column='deleted_time',
    id=1,
    deleted=0
)
```

## 统计和存在性

```python
total = await user_crud.count(session)
active_total = await user_crud.count(session, is_active=True)

exists = await user_crud.exists(session, email='a@example.com')
if not exists:
    await user_crud.create_model(session, user_data)
```

## 构建原生 Select

需要继续追加 SQLAlchemy 原生条件时，可以先构建 `Select`。

```python
stmt = await user_crud.select(
    User.is_active.is_(True),
    name__like='%张%'
)

stmt = await user_crud.select_order(
    sort_columns='created_at',
    sort_orders='desc',
    is_active=True
)
```

## 事务建议

- 多个操作组成一个业务动作时，使用 `async with async_session.begin()`。
- 只需要拿到主键时用 `flush=True`，不要提前提交。
- 独立的单个操作可以用 `commit=True`。
- 查询不存在返回 `None`，更新或删除不存在返回 `0`。
