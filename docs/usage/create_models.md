```python
async def create_models(
    self,
    session: AsyncSession,
    objs: Iterable[CreateSchema],
    flush: bool = False,
    commit: bool = False,
    **kwargs,
) -> list[Model]:
```

- 此方法提供 `flush` 参数，详见：[冲洗](../advanced/flush.md)
- 此方法提供 `commit` 参数，详见：[提交](../advanced/commit.md)
- 此方法还提供与 `create_model()` 相同用法的关键字参数，需要额外注意的是，`create_models()` 会将关键字参数写入每个实例中

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
    async def creates(self, db: AsyncSession, objs: Iterable[CreateIns]) -> list[ModelIns]:  # (1)
        return await self.create_models(db, objs)
```

1. objs 必须是一个 schema 列表
