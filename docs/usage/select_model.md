通过主键查询单条记录

```py title="select_model" hl_lines="15"
from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import Mapped, mapped_column
from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession


class ModelIns(Base):
    # define your primary_key
    primary_key: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)


class CRUDIns(CRUDPlus[ModelIns]):
    async def select(self, db: AsyncSession, pk: int) -> ModelIns:
        return await self.select_model(db, pk)
```

## API

```py
async def select_model(
    self,
    session: AsyncSession,
    pk: Union[Any, Dict[str, Any]],
    *whereclause: ColumnExpressionArgument[bool],
) -> Model | None:
```

**Parameters:**

| Name         | Type                             | Description                                                                                          | Default |
|--------------|----------------------------------|------------------------------------------------------------------------------------------------------|---------|
| session      | AsyncSession                     | 数据库会话                                                                                                | 必填      |
| pk           | int                              | [主键](../advanced/primary_key.md)                                                                     | 必填      |
| *whereclause | `ColumnExpressionArgument[bool]` | 等同于 [SQLAlchemy where](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#the-where-clause) |         |

**Returns:**

| Type                | Description |
|---------------------|-------------|
| `TypeVar `\|` None` | 模型实例        |


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
    crud = CRUDPlus(UserComposite)
    
    # Create
    await crud.create_model(
        session, UserCreate(id="123", name="John", email="composite@example.com"), commit=True
    )
    
    # Select by composite primary key (dictionary)
    user = await crud.select_model(session, {"id": "123", "name": "John"})
    print(user.email)  # composite@example.com

    # Select by composite primary key (tuple)
    user = await crud.select_model(session, ("123", "John"))
    print(user.email)  # composite@example.com
    

```