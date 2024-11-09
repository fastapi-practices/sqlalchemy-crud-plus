```py
async def update_model(
    self,
    session: AsyncSession,
    pk: int,
    obj: UpdateSchema | dict[str, Any],
    flush: bool = False,
    commit: bool = False,
    **kwargs,
) -> int:
```

- 此方法提供 `flush` 参数，详见：[冲洗](../advanced/flush.md)
- 此方法使用主键 `pk` 参数，详见：[主键](../advanced/primary_key.md)
- 此方法提供 `commit` 参数，详见：[提交](../advanced/commit.md)
- 此方法还提供与 `create_model()` 相同用法的关键字参数

## 示例

```py title="update_model" hl_lines="23"
from pydantic import BaseModel

from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import Mapped, mapped_column
from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # your sqlalchemy model
    # define your primary_key
    custom_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)


class UpdateIns(BaseModel):
    # your pydantic schema
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def create(self, db: AsyncSession, pk: int, obj: UpdateIns) -> int:
        return await self.update_model(db, pk, obj)
```
