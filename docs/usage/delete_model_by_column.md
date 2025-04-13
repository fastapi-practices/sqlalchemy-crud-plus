通过列删除单条/多条记录

```py title="delete_model_by_column" hl_lines="14"
from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def delete(self, db: AsyncSession) -> int:
        return await self.delete_model_by_column(db, name="foo")
```

## API
```py
async def delete_model_by_column(
    self,
    session: AsyncSession,
    allow_multiple: bool = False,
    logical_deletion: bool = False,
    deleted_flag_column: str = 'del_flag',
    flush: bool = False,
    commit: bool = False,
    **kwargs,
) -> int:
```

**Parameters:**

| Name                | Type         | Description                                          | Default    |
|---------------------|--------------|------------------------------------------------------|------------|
| session             | AsyncSession | 数据库会话                                                | 必填         |
| allow_multiple      | bool         | 设置为 `True`，将允许删除多条记录，删除的数量取决于过滤器过滤后的数据               | `False`    |
| logical_deletion    | bool         | 设置为 `True`，将不会从数据库中直接删除数据，而是通过更新的方式，将数据库删除标志字段的值进行更新 | `False`    |
| deleted_flag_column | str          | 设置指定逻辑删除的字段                                          | `del_flag` |
| flush               | bool         | [冲洗](../advanced/flush.md)                           | `False`    |
| commit              | bool         | [提交](../advanced/commit.md)                          | `False`    |

!!! note "**kwargs"

    [条件过滤](../advanced/filter.md)，将删除符合条件的数据

**Returns:**

| Type | Description |
|------|-------------|
| int  | 删除数量        |
