# 快速开始

本页用一个最小模型演示如何创建 CRUD 实例，并完成创建、查询、更新、删除。更多参数请继续阅读 [CRUD 操作](../usage/crud.md)。

## 1. 准备数据库会话

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = 'sqlite+aiosqlite:///./app.db'

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
```

## 2. 定义模型和 Schema

```python
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserCreate(BaseModel):
    name: str
    email: str
    is_active: bool = True


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None
```

## 3. 创建 CRUD 实例

```python
from sqlalchemy_crud_plus import CRUDPlus

user_crud = CRUDPlus(User)
```

`CRUDPlus(User)` 只绑定模型，不绑定 session。每次调用时传入当前请求或任务中的 `AsyncSession`。

## 4. 常用操作

```python
async with async_session.begin() as session:
    # 创建
    user = await user_crud.create_model(
        session,
        UserCreate(name='张三', email='zhangsan@example.com'),
        flush=True
    )

    # 主键查询
    user = await user_crud.select_model(session, pk=user.id)

    # 条件查询、分页
    users = await user_crud.select_models(
        session,
        is_active=True,
        limit=20,
        offset=0
    )

    # 更新
    await user_crud.update_model(
        session,
        pk=user.id,
        obj=UserUpdate(name='张三改名')
    )

    # 删除
    await user_crud.delete_model(session, pk=user.id)
```

!!! tip

    推荐用 `async with async_session.begin()` 管理事务。需要立即拿到自增主键时使用 `flush=True`；只有独立操作才考虑 `commit=True`。

## 5. 过滤、排序和字段加载

```python
# 模糊过滤 + 排序
users = await user_crud.select_models_order(
    session,
    sort_columns='id',
    sort_orders='desc',
    name__like='%张%',
    limit=10
)

# 只加载列表页需要的字段
users = await user_crud.select_models(
    session,
    load_strategies={
        'id': 'load_only',
        'name': 'load_only'
    },
    is_active=True
)
```

常见过滤写法：`field=value` 表示等于，`field__gt=value` 表示大于，`field__like=value` 表示模糊匹配。完整列表见 [过滤条件](../advanced/filter.md)。

## 6. 关系查询速览

如果模型定义了 `relationship`，可以使用 `load_strategies` 预加载关系，避免 N+1 查询。

```python
users = await user_crud.select_models(
    session,
    load_strategies=['posts']
)
```

如果没有 relationship，或需要复杂 JOIN，请使用 `JoinConfig`。完整说明见 [关系查询](../advanced/relationship.md)。

## 完整可运行示例

```python
import asyncio

from pydantic import BaseModel
from sqlalchemy import Boolean, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_crud_plus import CRUDPlus

DATABASE_URL = 'sqlite+aiosqlite:///./example.db'
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserCreate(BaseModel):
    name: str
    email: str
    is_active: bool = True


class UserUpdate(BaseModel):
    name: str | None = None


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    user_crud = CRUDPlus(User)

    async with async_session.begin() as session:
        user = await user_crud.create_model(
            session,
            UserCreate(name='张三', email='zhangsan@example.com'),
            flush=True
        )
        await user_crud.update_model(session, pk=user.id, obj=UserUpdate(name='张三改名'))
        users = await user_crud.select_models(session, is_active=True)
        print(users)


if __name__ == '__main__':
    asyncio.run(main())
```
