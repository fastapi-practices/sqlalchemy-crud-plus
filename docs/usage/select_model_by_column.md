```py
async def select_model_by_column(
    self,
    session: AsyncSession, 
    **kwargs
) -> Model | None:
```

此方法可结合 [高级过滤器](../advanced/filter.md) 使用

## 示例

```py title="select_model_by_cloumn" hl_lines="16"
from pydantic import BaseModel

from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def create(self, db: AsyncSession) -> ModelIns:
        return await self.select_model_by_column(db, name="foo")
```
