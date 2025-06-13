# 快速开始

本指南将帮助您在 5 分钟内上手 SQLAlchemy CRUD Plus。

## 安装

```bash
pip install sqlalchemy-crud-plus
```

## 基础设置

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

## 基础操作

### 创建记录

```python
# 创建单个用户
user_data = {"name": "张三", "email": "zhangsan@example.com"}
user = await user_crud.create_model(session, user_data)

# 批量创建
users_data = [
    {"name": "李四", "email": "lisi@example.com"},
    {"name": "王五", "email": "wangwu@example.com"}
]
users = await user_crud.create_models(session, users_data)
```

### 查询记录

```python
# 主键查询
user = await user_crud.select_model(session, 1)

# 条件查询
users = await user_crud.select_models(session, name__like="%张%", limit=10)

# 计数和存在检查
total = await user_crud.count(session)
exists = await user_crud.exists(session, email="test@example.com")
```

### 更新记录

```python
# 主键更新
await user_crud.update_model(session, 1, {"name": "张三丰"})

# 条件更新
count = await user_crud.update_model_by_column(
    session, {"is_active": True}, name__like="%李%"
)
```

### 删除记录

```python
# 主键删除
await user_crud.delete_model(session, 1)

# 条件删除
count = await user_crud.delete_model_by_column(session, is_active=False)
```

## 关系查询

### 预加载关系

```python
# 预加载用户的文章
user = await user_crud.select_model(
    session, 1,
    load_strategies=['posts']
)

# 指定加载策略
user = await user_crud.select_model(
    session, 1,
    load_strategies={'posts': 'selectinload'}
)
```

### JOIN 查询

```python
# 只返回有文章的用户
users = await user_crud.select_models(
    session,
    join_conditions=['posts']
)

# 指定 JOIN 类型
users = await user_crud.select_models(
    session,
    join_conditions={'posts': 'inner'}
)
```

## 下一步

- [基础用法](../usage/crud.md) - 详细的 CRUD 操作
- [关系查询](../relationships/overview.md) - 深入了解关系查询
- [高级功能](../advanced/filter.md) - 过滤条件和事务控制
