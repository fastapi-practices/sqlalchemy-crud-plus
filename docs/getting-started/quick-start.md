# 快速开始

本指南将帮助您在 5 分钟内上手 SQLAlchemy CRUD Plus。

## 前置条件

- Python 3.10+
- SQLAlchemy 2.0+
- Pydantic 2.0+

## 安装

```bash
pip install sqlalchemy-crud-plus
```

## 基础设置

### 定义模型

```python
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    posts: Mapped[list[Post]] = relationship(back_populates="author")
    profile: Mapped[UserProfile | None] = relationship(back_populates="user", uselist=False)


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(1000))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    author: Mapped[User] = relationship(back_populates="posts")


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    bio: Mapped[str] = mapped_column(String(500))
    avatar_url: Mapped[str | None] = mapped_column(String(200))

    user: Mapped[User] = relationship(back_populates="profile")
```

### 定义 Pydantic 模式

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime


class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class ProfileCreate(BaseModel):
    user_id: int
    bio: str
    avatar_url: str | None = None
```

### 数据库配置

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False
)

# 创建表
async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

### 创建 CRUD 实例

```python
from sqlalchemy_crud_plus import CRUDPlus

user_crud = CRUDPlus(User)
post_crud = CRUDPlus(Post)
profile_crud = CRUDPlus(UserProfile)
```

## 基础操作

### 创建记录

```python
async def create_user_example():
    async with _async_db_session() as session:
        async with session.begin():
            # 创建单个用户
            user_data = UserCreate(name="张三", email="zhangsan@example.com")
            user = await user_crud.create_model(session, user_data)
            
            # 批量创建
            users_data = [
                UserCreate(name="李四", email="lisi@example.com"),
                UserCreate(name="王五", email="wangwu@example.com")
            ]
            users = await user_crud.create_models(session, users_data)
            
        return user
```

### 查询记录

```python
async def read_user_examples():
    async with _async_db_session() as session:
        # 主键查询
        user = await user_crud.select_model(session, 1)
        
        # 条件查询
        user = await user_crud.select_model_by_column(
            session, email="zhangsan@example.com"
        )
        
        # 批量查询
        users = await user_crud.select_models(
            session,
            is_active=True,
            name__like="%张%",
            limit=10
        )
        
        # 计数和存在检查
        total = await user_crud.count(session)
        exists = await user_crud.exists(session, email="test@example.com")
```

### 更新记录

```python
async def update_user_examples():
    async with _async_db_session() as session:
        async with session.begin():
            # 主键更新
            user_update = UserUpdate(name="张三丰")
            updated_user = await user_crud.update_model(session, 1, user_update)
            
            # 条件更新
            update_data = UserUpdate(is_active=True)
            count = await user_crud.update_model_by_column(
                session, update_data, name__like="%李%"
            )
```

### 删除记录

```python
async def delete_user_examples():
    async with _async_db_session() as session:
        async with session.begin():
            # 主键删除
            await user_crud.delete_model(session, 1)
            
            # 条件删除
            count = await user_crud.delete_model_by_column(
                session, is_active=False
            )
            
            # 逻辑删除
            await user_crud.delete_model(
                session, 1, logical_deletion=True
            )
```

## 关系查询

### 预加载关系

```python
async def relationship_examples():
    async with _async_db_session() as session:
        # 预加载用户的文章
        user = await user_crud.select_model(
            session, 1,
            load_strategies=['posts']
        )
        
        # 预加载多个关系
        user = await user_crud.select_model(
            session, 1,
            load_strategies=['posts', 'profile']
        )
        
        # 指定加载策略
        user = await user_crud.select_model(
            session, 1,
            load_strategies={
                'posts': 'selectinload',
                'profile': 'joinedload'
            }
        )
```

### JOIN 查询

```python
async def join_examples():
    async with _async_db_session() as session:
        # 只返回有文章的用户
        users = await user_crud.select_models(
            session,
            join_conditions=['posts']
        )
        
        # 指定 JOIN 类型
        users = await user_crud.select_models(
            session,
            join_conditions={
                'posts': 'inner',
                'profile': 'left'
            }
        )
```

## 高级查询

### 过滤操作符

```python
async def advanced_filtering():
    async with _async_db_session() as session:
        # 比较操作符
        users = await user_crud.select_models(
            session,
            age__gt=18,              # 年龄大于 18
            age__le=65,              # 年龄小于等于 65
            status__ne=0             # 状态不等于 0
        )
        
        # 字符串操作符
        users = await user_crud.select_models(
            session,
            name__like='%张%',           # 名字包含"张"
            email__endswith='@qq.com'    # 邮箱以@qq.com结尾
        )
        
        # OR 条件
        users = await user_crud.select_models(
            session,
            __or__={
                'email__endswith': ['@gmail.com', '@qq.com']
            }
        )
```

### 排序和分页

```python
async def sorting_and_pagination():
    async with _async_db_session() as session:
        # 排序查询
        users = await user_crud.select_models_order(
            session,
            sort_columns='created_at',
            sort_orders='desc',
            limit=10
        )
        
        # 分页查询
        users = await user_crud.select_models(
            session,
            limit=20,
            offset=40,  # 第3页，每页20条
            is_active=True
        )
```

### 计数和存在检查

```python
async def count_and_exists():
    async with _async_db_session() as session:
        # 计数
        total_users = await user_crud.count(session)
        active_users = await user_crud.count(session, is_active=True)
        
        # 存在检查
        user_exists = await user_crud.exists(session, email="test@example.com")
        has_posts = await user_crud.exists(
            session,
            join_conditions=['posts']
        )
```

## 完整示例

```python
import asyncio

async def main():
    async with _async_db_session() as session:
        async with session.begin():
            # 创建用户
            user_data = UserCreate(name="示例用户", email="example@test.com")
            user = await user_crud.create_model(session, user_data, flush=True)
            
            # 创建文章
            post_data = PostCreate(
                title="我的第一篇文章",
                content="这是文章内容...",
                author_id=user.id
            )
            post = await post_crud.create_model(session, post_data)
        
        # 查询用户及其文章
        user_with_posts = await user_crud.select_model(
            session, user.id,
            load_strategies=['posts']
        )
        
        print(f"用户 {user_with_posts.name} 有 {len(user_with_posts.posts)} 篇文章")

if __name__ == "__main__":
    asyncio.run(main())
```

## 下一步

- [基础用法](../usage/create.md) - 详细的 CRUD 操作
- [关系查询](../relationships/overview.md) - 深入了解关系查询
- [高级功能](../advanced/filter.md) - 过滤条件和事务控制
- [API 参考](../api/crud-plus.md) - 完整的 API 文档
