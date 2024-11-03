```py
async def select(self, **kwargs) -> Select:
    ...
```

此方法用于构造 SQLAlchemy
Select，在一些特定场景将会很有用，比如，配合 [fastapi-pagination](https://github.com/uriyyo/fastapi-pagination) 使用

## 示例

```py hl_lines="28"
from typing import Any, Annotated

from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel

from sqlalchemy_crud_plus import CRUDPlus

from sqlalchemy import select, Select
from sqlalchemy import DeclarativeBase as Base
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate


class ModelIns(Base):
    # your sqlalchemy model
    pass


class UserOut(BaseModel):
    # your pydantic schema
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    async def get_list(self, name: str = None, method: str = None) -> Select:
        return await self.select(name__like=f'%{name}%', method=method)

    
crud_ins = CRUDIns(ModelIns)
    

app = FastAPI()
add_pagination(app)

    
@app.get("/users", response_model=Page[UserOut])
async def get_users(
    db: AsyncSession = Depends(get_db),
    name: Annotated[str | None, Query()] = None,
    method: Annotated[str | None, Query()] = None,
) -> Any:
    select = await crud_ins.get_list()
    return await paginate(db, select)
```
