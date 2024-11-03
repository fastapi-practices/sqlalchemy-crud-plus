```py
 async def select_models_order(
     self,
     session: AsyncSession,
     sort_columns: str | list[str],
     sort_orders: str | list[str] | None = None,
     **kwargs,
) -> Sequence[Row | RowMapping | Any] | None:
```

此方法可结合 [高级过滤器](../advanced/filter.md) 使用

## 排序

对结果进行排序涉及此方法的两个字段

1. `sort_columns`：应用排序的单个列名或列名列表

2. `sort_orders`：单个排序顺序（`asc` 或 `desc`）或与 `sort_columns` 中的列相对应的排序顺序列表。
   如果未提供，则默认每列的排序顺序为 `asc`

## 示例

```py title="select_models_order" hl_lines="18"
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
        return await self.select_models_order(db, sort_columns=['name', 'age'], sort_orders=['asc', 'desc'])
```
