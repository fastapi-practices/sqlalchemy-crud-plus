添加多条新纪录

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
    async def creates(self, db: AsyncSession, objs: Iterable[CreateIns]) -> list[ModelIns]:
        return await self.create_models(db, objs)  # objs 必须是一个 schema 列表
```

## API

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

**Parameters:**

| Name    | Type         | Description                 | Default |
|---------|--------------|-----------------------------|---------|
| session | AsyncSession | 数据库会话                       | 必填      |
| obj     | Iterable     | 创建新数据参数                     | 必填      |
| flush   | bool         | [冲洗](../advanced/flush.md)  | `False` |
| commit  | bool         | [提交](../advanced/commit.md) | `False` |

!!! note "**kwargs"

    提供与 `create_model()` 相同用法的关键字参数，需要额外注意的是，`create_models()` 会将关键字参数写入每条新数据中

**Returns:**

| Type | Description |
|------|-------------|
| list | 模型实例        |
