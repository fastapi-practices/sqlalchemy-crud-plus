````py
async def create_model(
    self,
    session: AsyncSession,
    obj: CreateSchema,
    commit: bool = False,
    **kwargs,
) -> Model:
````

此方法提供 `commit` 参数，详见：[提交](../advanced/commit.md)

!!! note "关键字参数"

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
