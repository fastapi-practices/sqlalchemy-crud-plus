查询符合条件过滤的记录数

```py title="count" hl_lines="14"
from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def create(self, db: AsyncSession) -> int:
        return await self.count(db, name="foo")
```

## API

```python
async def count(
    self,
    session: AsyncSession,
    filters: ColumnElement | list[ColumnElement] | None = None,
    **kwargs,
) -> int:
```

**Parameters:**

| Name    | Type                                               | Description      | Default |
|---------|----------------------------------------------------|------------------|---------|
| session | AsyncSession                                       | 数据库会话            | 必填      |
| filters | `ColumnElement `\|` list[ColumnElement] `\|` None` | 要应用于查询的 WHERE 子句 | `None`  |

!!! note "**kwargs"

    [条件过滤](../advanced/filter.md)，将创建条件查询 SQL

**Returns:**

| Type | Description |
|------|-------------|
| int  | 记录数         |
