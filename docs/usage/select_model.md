```py
async def select_model(
    self,
    session: AsyncSession,
    pk: int
) -> Model | None:
```

## 示例

```py title="select_model" hl_lines="21"
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
    async def create(self, db: AsyncSession, pk: int) -> ModelIns:
        return await self.select_model(db, pk)
```
