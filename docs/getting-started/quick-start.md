# 快速开始

本指南帮助您在 5 分钟内快速上手 SQLAlchemy CRUD Plus。

## 基础配置

### 数据库配置

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# 数据库连接
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_session():
    async with async_session() as session:
        yield session
```

### 模型定义

```python
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(1000))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author: Mapped[User] = relationship(back_populates="posts")
```

### Pydantic 模式

```python
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    is_active: bool = True


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None


class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int
```

## 基本使用

!!! note "关于代码示例"
以下示例代码片段假设您已经配置好数据库连接和模型定义（参见上方"基础配置"部分），并且在异步函数中使用 `session`
对象。完整的可运行示例请参见本页底部的"完整示例"部分。

### 创建 CRUD 实例

```python
from sqlalchemy_crud_plus import CRUDPlus

user_crud = CRUDPlus(User)
post_crud = CRUDPlus(Post)
```

### 创建记录

```python
# 创建用户（需要手动提交事务）
user_data = UserCreate(name="张三", email="zhangsan@example.com")
user = await user_crud.create_model(session, user_data)
await session.commit()  # 提交事务

# 或者使用 commit 参数自动提交
user = await user_crud.create_model(session, user_data, commit=True)

# 批量创建
users_data = [
    UserCreate(name="李四", email="lisi@example.com"),
    UserCreate(name="王五", email="wangwu@example.com")
]
users = await user_crud.create_models(session, users_data)
await session.commit()

# 使用事务上下文自动管理
async with session.begin():
    user = await user_crud.create_model(session, user_data)
    # 退出 with 块时自动提交或回滚
```

### 查询记录

```python
# 根据主键查询
user = await user_crud.select_model(session, pk=1)

# 根据字段查询
user = await user_crud.select_model_by_column(session, email="zhangsan@example.com")

# 查询多个记录
users = await user_crud.select_models(session, is_active=True)

# 分页查询
users = await user_crud.select_models(session, limit=10, offset=0)

# 过滤查询
users = await user_crud.select_models(
    session,
    name__like="%张%",
    created_at__ge="2024-01-01"
)
```

### 更新记录

```python
# 根据主键更新
update_data = UserUpdate(name="新名称")
await user_crud.update_model(session, pk=1, obj=update_data)

# 使用字典更新
await user_crud.update_model(session, pk=1, obj={"is_active": False})

# 条件更新
await user_crud.update_model_by_column(
    session,
    obj={"is_active": True},
    name="李四"
)
```

### 删除记录

```python
# 根据主键删除
await user_crud.delete_model(session, pk=1)

# 条件删除
await user_crud.delete_model_by_column(session, is_active=False)

# 逻辑删除（推荐）
await user_crud.delete_model_by_column(
    session,
    logical_deletion=True,
    deleted_flag_column='is_deleted',
    allow_multiple=False,
    id=1
)
```

### 统计查询

```python
# 统计记录数
total = await user_crud.count(session)
active_count = await user_crud.count(session, is_active=True)

# 检查记录是否存在
exists = await user_crud.exists(session, email="test@example.com")
if not exists:
    user = await user_crud.create_model(session, user_data)
```

### 关系查询

```python
# 预加载关系数据
users = await user_crud.select_models(
    session,
    load_strategies=['posts']
)

# JOIN 查询
users = await user_crud.select_models(
    session,
    join_conditions=['posts']
)

# 指定加载策略
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies={
        'posts': 'selectinload'
    }
)

# 查询构建方法
stmt = await user_crud.select(
    User.is_active == True,
    load_strategies=['posts']
)

stmt = await user_crud.select_order(
    sort_columns='created_at',
    sort_orders='desc'
)
```

### 高性能批量操作

```python
# 高性能批量创建（使用字典）
users_dict = [
    {"name": "用户1", "email": "user1@example.com"},
    {"name": "用户2", "email": "user2@example.com"},
    {"name": "用户3", "email": "user3@example.com"}
]
users = await user_crud.bulk_create_models(session, users_dict)

# 批量更新不同数据
users_update = [
    {"id": 1, "name": "新名称1", "email": "new1@example.com"},
    {"id": 2, "name": "新名称2", "email": "new2@example.com"}
]
await user_crud.bulk_update_models(session, users_update)
```

## 完整示例

```python
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Boolean, ForeignKey, func
from pydantic import BaseModel
from sqlalchemy_crud_plus import CRUDPlus

# 数据库配置
DATABASE_URL = "sqlite+aiosqlite:///./example.db"
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


# 模型定义
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(1000))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author: Mapped[User] = relationship(back_populates="posts")


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int


async def main():
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建 CRUD 实例
    user_crud = CRUDPlus(User)
    post_crud = CRUDPlus(Post)

    async with async_session() as session:
        # 创建用户
        user_data = UserCreate(name="张三", email="zhangsan@example.com")
        user = await user_crud.create_model(session, user_data)
        await session.commit()
        print(f"创建用户: {user.name}")

        # 创建文章
        post_data = PostCreate(
            title="我的第一篇文章",
            content="这是文章内容",
            author_id=user.id
        )
        post = await post_crud.create_model(session, post_data)
        await session.commit()
        print(f"创建文章: {post.title}")

        # 查询用户及其文章
        user_with_posts = await user_crud.select_model(
            session,
            pk=user.id,
            load_strategies=['posts']
        )
        print(f"用户 {user_with_posts.name} 有 {len(user_with_posts.posts)} 篇文章")

        # 统计和检查
        total_users = await user_crud.count(session)
        print(f"总用户数: {total_users}")

        email_exists = await user_crud.exists(session, email="zhangsan@example.com")
        print(f"邮箱存在: {email_exists}")

        # 更新用户
        update_data = UserUpdate(name="张三改名")
        await user_crud.update_model(session, pk=user.id, obj=update_data)
        await session.commit()
        print("更新用户名")

        # 删除文章
        await post_crud.delete_model(session, pk=post.id, commit=True)
        print("删除文章")


if __name__ == "__main__":
    asyncio.run(main())
```
