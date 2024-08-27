```py
async def select_model(
    self,
    session: AsyncSession,
    pk: int
) -> Model | None:
```

此方法使用主键 pk 参数，详见：[主键](../advanced/primary_key.md)

## 示例

```py title="select_model" hl_lines="21"
from pydantic import BaseModel

from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import Mapped, mapped_column
from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    # define your primary_key
    custom_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)


class CreateIns(BaseModel):
    # your pydantic schema
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def select(self, db: AsyncSession, pk: int) -> ModelIns:
        return await self.select_model(db, pk)
```
