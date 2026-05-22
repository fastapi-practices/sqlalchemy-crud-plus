# 关系查询

关系查询主要解决三件事：预加载 relationship、动态 JOIN、控制查询字段。先选对参数，再写查询。

## 参数怎么选

| 需求 | 参数 | 说明 |
| --- | --- | --- |
| 避免 N+1，提前加载 relationship | `load_strategies` | 返回主模型实例 |
| JOIN 过滤或按关联表条件查询 | `join_conditions` | 默认仍返回主模型实例 |
| JOIN 后同时返回关联表数据 | `JoinConfig(fill_result=True)` | 返回 `Row` |
| SQLAlchemy 原生加载选项 | `load_options` | 适合嵌套加载或复杂字段控制 |
| 只查部分字段 / 延迟大字段 | `load_strategies` 或 `load_options` | 支持 `load_only`、`defer`、`undefer` |

## 预加载 relationship

模型中已经定义 `relationship` 时，最常用的是 `load_strategies`。

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    posts: Mapped[list['Post']] = relationship(back_populates='author')


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    author: Mapped[User] = relationship(back_populates='posts')
```

```python
# 列表格式默认使用 selectinload。
users = await user_crud.select_models(
    session,
    load_strategies=['posts']
)

# 字典格式可以指定策略。
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies={
        'posts': 'selectinload'
    }
)
```

常用策略：

| 策略 | 适合场景 |
| --- | --- |
| `selectinload` | 一对多、多对多，通常首选 |
| `joinedload` | 一对一或多对一，希望一次 JOIN 查出 |
| `subqueryload` | 某些复杂集合加载场景 |
| `noload` | 明确不加载关系 |
| `raiseload` | 防止意外懒加载 |

## 字段加载控制

字段加载策略用于减少 SELECT 字段或延迟大字段。

```python
# 只加载 id 和 name。主键会自动保留。
users = await user_crud.select_models(
    session,
    load_strategies={
        'id': 'load_only',
        'name': 'load_only'
    },
    limit=20
)

# 延迟加载大字段。
users = await user_crud.select_models(
    session,
    load_strategies={
        'content': 'defer',
        'extra_data': 'defer'
    }
)

# 恢复加载模型中默认 deferred 的字段。
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies={
        'profile_summary': 'undefer'
    }
)
```

!!! warning

    异步 ORM 中访问未加载字段可能触发额外 SQL。推荐在查询时一次声明需要的字段。

## JOIN 过滤

`join_conditions` 用来把关联表加入查询。默认返回主模型实例，适合“按关联条件筛选主表”的场景。

```python
# 使用 relationship 名称 JOIN。
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],
    is_active=True
)

# 指定 JOIN 类型。
users = await user_crud.select_models(
    session,
    join_conditions={
        'posts': 'inner',
        'profile': 'left'
    }
)
```

JOIN 类型：

| 类型 | 说明 |
| --- | --- |
| `inner` | 只返回两边都匹配的数据 |
| `left` | 保留主表数据，关联表可为空 |
| `full` | FULL OUTER JOIN，取决于数据库支持 |

## 自定义 JOIN：JoinConfig

没有 relationship、没有外键，或 JOIN 条件较复杂时，使用 `JoinConfig`。

```python
from sqlalchemy import and_
from sqlalchemy_crud_plus import JoinConfig

users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=and_(
                User.id == Post.author_id,
                Post.status == 'published'
            ),
            join_type='inner'
        )
    ]
)
```

如果只需要主表数据，保持默认 `fill_result=False` 即可。需要同时拿到关联表数据时，设置 `fill_result=True`：

```python
rows = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=User.id == Post.author_id,
            join_type='left',
            fill_result=True
        )
    ]
)

for user, post in rows:
    print(user.name, post.title if post else None)
```

!!! note

    `fill_result=True` 会让返回值变成 SQLAlchemy `Row`，不再是单纯的主模型实例列表。

## 原生 load_options

当 `load_strategies` 不够表达复杂加载需求时，可以直接传 SQLAlchemy 原生选项。

```python
from sqlalchemy.orm import defer, load_only, selectinload

user = await user_crud.select_model(
    session,
    pk=1,
    load_options=[
        selectinload(User.posts).selectinload(Post.comments)
    ]
)

users = await user_crud.select_models(
    session,
    load_options=[
        load_only(User.id, User.name, User.email),
        defer(User.bio)
    ]
)
```

## 常见组合

```python
users = await user_crud.select_models(
    session,
    join_conditions={'posts': 'inner'},
    load_strategies={
        'posts': 'selectinload',
        'id': 'load_only',
        'name': 'load_only'
    },
    name__like='%admin%',
    limit=20
)
```

## 实用建议

- 有标准外键和 relationship：优先 `load_strategies`。
- 只是筛选主表：用 `join_conditions`，不要设置 `fill_result=True`。
- 需要返回多表数据：用 `JoinConfig(fill_result=True)` 或原生 `select()`。
- 列表页：用 `load_only` 减少字段，用 `limit` 限制结果。
- 常用 JOIN 字段和过滤字段要加索引。
- 避免在异步环境中依赖隐式懒加载。

## 相关页面

- [过滤条件](filter.md)
- [CRUD 操作](../usage/crud.md)
- [API 参考](../api/crud-plus.md)
