```py
async def select_models_order(
    self,
    session: AsyncSession,
    sort_columns: str | list[str],
    sort_orders: str | list[str] | None = None,
    **kwargs
) -> Sequence[Row | RowMapping | Any] | None:
```

此方法可结合 [高级过滤器](../advanced/filter.md) 使用

## 示例

```py title="select_models_order" hl_lines="23"
from typing import Sequence

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
    async def create(self, db: AsyncSession) -> Sequence[ModelIns]:
        return await self.select_models_order(db, sort_columns=['name', 'age'], sort_orders=['asc', 'desc'])
```
