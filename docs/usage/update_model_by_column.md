通过列更新单条/多条记录

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

## API

```py
async def update_model_by_column(
    self,
    session: AsyncSession,
    obj: UpdateSchema | dict[str, Any],
    allow_multiple: bool = False,
    flush: bool = False,
    commit: bool = False,
    **kwargs,
) -> int:
```

**Parameters:**

| Name           | Type                          | Description                            | Default |
|----------------|-------------------------------|----------------------------------------|---------|
| session        | AsyncSession                  | 数据库会话                                  | 必填      |
| obj            | `TypeVar `\|` dict[str, Any]` | 更新数据参数                                 | 必填      |
| allow_multiple | bool                          | 设置为 `True`，将允许更新多条记录，更新的数量取决于过滤器过滤后的数据 | `False` |
| flush          | bool                          | [冲洗](../advanced/flush.md)             | `False` |
| commit         | bool                          | [提交](../advanced/commit.md)            | `False` |

!!! note "**kwargs"

    [条件过滤](../advanced/filter.md)，将更新符合条件的数据

**Returns:**

| Type | Description |
|------|-------------|
| int  | 更新数量        |
