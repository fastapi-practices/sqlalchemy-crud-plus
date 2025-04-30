通过主键删除单条记录

```py title="delete_model" hl_lines="15"
from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import Mapped, mapped_column
from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # define your primary_key
    primary_key: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)


class CRUDIns(CRUDPlus[ModelIns]):
    async def delete(self, db: AsyncSession, pk: int) -> int:
        return await self.delete_model(db, pk)
```

## API

```py
async def delete_model(
    self,
    session: AsyncSession,
    pk: Union[Any, Dict[str, Any]],
    flush: bool = False,
    commit: bool = False,
) -> int:
```

**Parameters:**

| Name    | Type         | Description                      | Default |
|---------|--------------|----------------------------------|---------|
| session | AsyncSession | 数据库会话                            | 必填      |
| pk      | int          | [主键](../advanced/primary_key.md) | 必填      |
| flush   | bool         | [冲洗](../advanced/flush.md)       | `False` |
| commit  | bool         | [提交](../advanced/commit.md)      | `False` |

**Returns:**

| Type | Description |
|------|-------------|
| int  | 删除数量        |


## example

```python
# Model with composite primary key
class UserComposite(Base):
    __tablename__ = "users_composite"
    id = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    email = Column(String)
    
class UserCreate(BaseModel):
    id: str
    name: str | None
    email: str

async def example(session: AsyncSession):
    # Composite primary key model
    crud_composite = CRUDPlus(UserComposite)
    
    # Create
    await crud_composite.create_model(
        session, UserCreate(id="123", name="John", email="composite@example.com"), commit=True
    )
    
    
    # Delete by composite primary key (dictionary)
    await crud_composite.delete_model(session, {"id": "123", "name": "John"}, commit=True)

```