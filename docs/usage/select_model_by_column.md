通过列查询单条记录

```py title="select_model_by_cloumn" hl_lines="14"
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

## API

```py
async def select_model_by_column(self, session: AsyncSession, **kwargs) -> Model | None:
```

**Parameters:**

| Name    | Type         | Description                      | Default |
|---------|--------------|----------------------------------|---------|
| session | AsyncSession | 数据库会话                            | 必填      |

!!! note "**kwargs"

    [条件过滤](../advanced/filter.md)，将创建条件查询 SQL

**Returns:**

| Type                | Description |
|---------------------|-------------|
| `TypeVar `\|` None` | 模型实例        |
