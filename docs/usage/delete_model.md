```py
async def delete_model(
    self, session: 
    AsyncSession, 
    pk: int, 
    commit: bool = False
) -> int:
```

## 示例

```py title="delete_model" hl_lines="21"
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
    async def delete(self, db: AsyncSession, pk: int) -> int:
        return await self.delete_model(db, pk)
```
