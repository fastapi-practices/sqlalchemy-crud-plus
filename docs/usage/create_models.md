```python
async def create_models(
    self, 
    session: AsyncSession, 
    obj: Iterable[CreateSchema], 
    commit: bool = False
) -> list[Model]:
```

此方法提供 `commit` 参数，详见：[提交](./create_model.md/#_1)

## 示例

```py title="create_models" hl_lines="23"
from typing import Iterable

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
    async def creates(self, db: AsyncSession, obj: Iterable[CreateIns]) -> list[ModelIns]:  # (1)
        return await self.create_models(db, obj)
```

1. obj 必须是一个 schema 列表
