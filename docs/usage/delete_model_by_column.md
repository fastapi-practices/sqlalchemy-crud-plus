```py
async def delete_model_by_column(
    self,
    session: AsyncSession,
    allow_multiple: bool = False,
    logical_deletion: bool = False,
    deleted_flag_column: str = 'del_flag',
    commit: bool = False,
    **kwargs,
) -> int:
```

此方法可结合 [高级过滤器](../advanced/filter.md) 使用

## 示例

```py title="delete_model_by_column" hl_lines="21"
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
    async def delete(self, db: AsyncSession) -> int:
        return await self.delete_model_by_column(db, name="foo")
```
