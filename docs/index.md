# SQLAlchemy CRUD Plus

强大的 SQLAlchemy CRUD 库，支持高级关系查询功能。

## 核心特性

**完整的 CRUD 操作**
- 创建、查询、更新、删除操作
- 支持单条和批量操作
- 丰富的过滤操作符

**强大的关系查询**
- 三参数系统：`load_options`、`load_strategies`、`join_conditions`
- 预防 N+1 查询问题
- 多种加载策略支持

**类型安全**
- 完整的类型提示
- 泛型支持 `CRUDPlus[Model]`
- Pydantic 模式验证

**高性能**
- 基于 SQLAlchemy 2.0 异步引擎
- 智能查询优化
- 高效的批量操作

## 安装

```bash
pip install sqlalchemy-crud-plus
```

## 快速开始

### 定义模型

```python
from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))

    posts: Mapped[list[Post]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(1000))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    author: Mapped[User] = relationship(back_populates="posts")
```

### 创建 CRUD 实例

```python
from sqlalchemy_crud_plus import CRUDPlus

user_crud = CRUDPlus(User)
post_crud = CRUDPlus(Post)
```

### 基础操作

```python
from sqlalchemy.ext.asyncio import AsyncSession

# 创建用户
async with async_session.begin():
    user_data = UserCreate(name="张三", email="zhangsan@example.com")
    user = await user_crud.create_model(async_session, user_data)

# 查询用户
user = await user_crud.select_model(async_session, user.id)

# 更新用户
async with async_session.begin():
    user_update = UserUpdate(name="张三丰")
    result = await user_crud.update_model(async_session, user.id, user_update)

# 删除用户
async with async_session.begin():
    count = await user_crud.delete_model(async_session, user.id)
```

### 关系查询

```python
# 查询用户及其文章
user = await user_crud.select_model(
    async_session, user_id,
    load_strategies=['posts']  # 预加载文章，防止 N+1 查询
)

# 高级关系查询
user = await user_crud.select_model(
    async_session, user_id,
    load_strategies={
        'posts': 'selectinload',    # 一对多使用 selectinload
        'profile': 'joinedload'     # 一对一使用 joinedload
    },
    join_conditions={
        'posts': 'left'             # LEFT JOIN posts
    }
)
```

### 高级查询

```python
# 条件查询
users = await user_crud.select_models(
    async_session,
    name__like='%张%',           # name LIKE '%张%'
    email__endswith='@qq.com',   # email LIKE '%@qq.com'
    limit=10
)

# 计数和存在检查
count = await user_crud.count(async_session, is_active=True)
exists = await user_crud.exists(async_session, email='test@example.com')
```

## 对比传统方式

**传统 SQLAlchemy 查询**
```python
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select

stmt = (
    select(User)
    .options(
        selectinload(User.posts),
        joinedload(User.profile)
    )
    .join(User.posts)
    .where(User.id == user_id)
)
result = await async_session.execute(stmt)
user = result.scalar_one_or_none()
```

**SQLAlchemy CRUD Plus**
```python
user = await user_crud.select_model(
    async_session, user_id,
    load_strategies=['posts', 'profile'],
    join_conditions=['posts']
)
```

## 文档导航

- [安装指南](installing.md) - 安装和配置
- [快速开始](getting-started/quick-start.md) - 5分钟上手
- [基础用法](usage/create.md) - CRUD 操作
- [关系查询](relationships/overview.md) - 关系查询指南
- [API 参考](api/crud-plus.md) - 完整 API 文档

## 社区

- [GitHub](https://github.com/wu-clan/sqlalchemy-crud-plus) - 源代码和问题反馈
- [Discord](https://wu-clan.github.io/homepage/) - 社区讨论
