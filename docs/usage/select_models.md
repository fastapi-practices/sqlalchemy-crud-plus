```py
async def select_models(self, session: AsyncSession, **kwargs) -> Sequence[Row[Any] | RowMapping | Any]:
```

此方法可结合 [高级过滤器](../advanced/filter.md) 使用

## 示例

```py title="select_models" hl_lines="18"
from typing import Sequence

from pydantic import BaseModel

from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def create(self, db: AsyncSession) -> Sequence[ModelIns]:
        return await self.select_models(db)
```
