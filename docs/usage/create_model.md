````py
async def create_model(
    self,
    session: AsyncSession,
    obj: CreateSchema,
    commit: bool = False,
    **kwargs
) -> Model:
````

!!! note "create_model 独特的关键字参数"

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

## 提交

此方法提供 `commit` 参数，默认值为 False，它既不会执行提交操作，也不包含 `flush` 等行为，要想真正写入到数据库，你可以通过以下几种方案

1. 设置 `commit=True` 手动提交

      ```py hl_lines="2"
      async def create(self, db: AsyncSession, obj: CreateIns) -> None:
          await self.create_model(db, obj, commit=True)
      ```

2. 使用 `begin()` 事务自动提交

      ```py hl_lines="9"
      --8<-- "docs/ext/async_db_session.py"
      
      async def create(self, obj: CreateIns) -> None:
          async with async_db_session.begin() as db:
              await self.create_model(db, obj)
      ```

## 示例

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
