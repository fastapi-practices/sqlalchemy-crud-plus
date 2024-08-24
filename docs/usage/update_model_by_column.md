```py
async def update_model_by_column(
    self,
    session: AsyncSession,
    obj: UpdateSchema | dict[str, Any],
    allow_multiple: bool = False,
    commit: bool = False,
    **kwargs,
) -> int:
```

此方法可结合 [高级过滤器](../advanced/filter.md) 使用

## 示例

```py title="update_model_by_columnn" hl_lines="21"
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
    async def create(self, db: AsyncSession, obj: UpdateIns) -> int:
        return await self.update_model_by_column(db, obj, name="foo")
```
