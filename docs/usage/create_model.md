添加单条新纪录

```py title="create_model" hl_lines="21"
from pydantic import BaseModel

from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    pass


class CreateIns(BaseModel):
    # your pydantic schema
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def create(self, db: AsyncSession, obj: CreateIns) -> ModelIns:
        return await self.create_model(db, obj)
```

## API

```py
async def create_model(
    self,
    session: AsyncSession,
    obj: CreateSchema,
    flush: bool = False,
    commit: bool = False,
    **kwargs,
) -> Model:
```

**Parameters:**

| Name    | Type         | Description                 | Default |
|---------|--------------|-----------------------------|---------|
| session | AsyncSession | 数据库会话                       | 必填      |
| obj     | TypeVar      | 创建新数据参数                     | 必填      |
| flush   | bool         | [冲洗](../advanced/flush.md)  | `False` |
| commit  | bool         | [提交](../advanced/commit.md) | `False` |

!!! note "**kwargs"

    除了必须传入 obj schema 外，还可以通过关键字入参，传入非 schema
    参数，比如，对于某些特定场景，其中一个字段并不是通用的，也不需要进行输入控制，只需在写入时赋予指定值，那么你可以使用关键字入参即可
   
    e.g.
   
    ```PY
    async def create(self, obj: CreateIns) -> None:
        async with async_db_session.begin() as db:
            await self.create_model(db, obj, status=1)  # (1)
    ```
   
    1. 在数据被最终写入前，所有入参（schema 和关键字参数）都会赋值给 SQLAlchemy 模型，即便你传入了非模型数据，
       这也是安全的，因为它不会被模型所引用

**Returns:**

| Type    | Description |
|---------|-------------|
| TypeVar | 模型实例        |
