通过列查询多条记录

```py title="select_models" hl_lines="16"
from typing import Sequence

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

## API

```py
async def select_models(self, session: AsyncSession, **kwargs) -> Sequence[Row[Any] | RowMapping | Any]:
```

**Parameters:**

| Name    | Type         | Description                      | Default |
|---------|--------------|----------------------------------|---------|
| session | AsyncSession | 数据库会话                            | 必填      |

!!! note "**kwargs"

    [条件过滤](../advanced/filter.md)，将创建条件查询 SQL

**Returns:**

| Type                                           | Description |
|------------------------------------------------|-------------|
| `Sequence[Row[Any] `\|` RowMapping  `\|` Any]` | 模型实例序列      |
