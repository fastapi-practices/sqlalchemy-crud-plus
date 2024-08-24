```py
async def update_model(
    self, 
    session: AsyncSession,
    pk: int,
    obj: UpdateSchema | dict[str, Any],
    commit: bool = False
) -> int:
```

此方法提供 `commit` 参数，详见：[提交](./create_model.md/#_1)

`obj` 参数还可以是字典数据，通常情况下，传入的 schema 数据将通过 `model_dump(exclude_unset=True)` 序列化之后传入更新

## 示例

```py title="update_model" hl_lines="21"
from pydantic import BaseModel

from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    pass


class UpdateIns(BaseModel):
    # your pydantic schema
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def create(self, db: AsyncSession, pk: int, obj: UpdateIns) -> int:
        return await self.update_model(db, pk, obj)
```
