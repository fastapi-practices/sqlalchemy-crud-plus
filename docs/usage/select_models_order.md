此方法与 [select_models()](./select_models.md) 方法类似，但增加了排序功能

```py title="select_models_order" hl_lines="16"
from typing import Sequence

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

## API

```py
 async def select_models_order(
     self,
     session: AsyncSession,
     sort_columns: str | list[str],
     sort_orders: str | list[str] | None = None,
     **kwargs,
) -> Sequence[Row | RowMapping | Any] | None:
```

**Parameters:**

| Name         | Type                           | Description                                                            | Default |
|--------------|--------------------------------|------------------------------------------------------------------------|---------|
| session      | AsyncSession                   | 数据库会话                                                                  | 必填      |
| sort_columns | `str `\|` list[str]`           | 应用排序的单个列名或列名列表                                                         | 必填      |
| sort_orders  | `str `\|` list[str] `\|` None` | 单个排序顺序（asc 或 desc）或与 sort_columns 中的列相对应的排序顺序列表。 如果未提供，则默认每列的排序顺序为 asc | `None`  |

!!! note "**kwargs"

    [条件过滤](../advanced/filter.md)，将创建条件查询 SQL

**Returns:**

| Type                                           | Description |
|------------------------------------------------|-------------|
| `Sequence[Row[Any] `\|` RowMapping  `\|` Any]` | 模型实例序列      |
