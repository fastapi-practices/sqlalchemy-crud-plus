查询符合条件过滤的记录是否存在

```py title="exists" hl_lines="14"
from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def create(self, db: AsyncSession) -> bool:
        return await self.exists(db, name="foo")
```

## API 

```python
async def exists(
    self,
    session: AsyncSession,
    *whereclause: ColumnExpressionArgument[bool],
    **kwargs,
) -> bool:
```

**Parameters:**

| Name         | Type                             | Description                                                                                          | Default |
|--------------|----------------------------------|------------------------------------------------------------------------------------------------------|---------|
| session      | AsyncSession                     | 数据库会话                                                                                                | 必填      |
| *whereclause | `ColumnExpressionArgument[bool]` | 等同于 [SQLAlchemy where](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#the-where-clause) |         |
| **kwargs     |                                  | [条件过滤](../advanced/filter.md)，将创建条件查询 SQL                                                            |         |


**Returns:**

| Type | Description |
|------|-------------|
| bool | 记录是否存在      |
