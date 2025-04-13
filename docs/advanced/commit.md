SQLAlchemy CRUD Plus 内部为很多方法都提供了 `commit` 参数，默认值为 `False`，它既不会执行提交操作，也不包含 `flush`
等行为，要想真正写入到数据库，你可以通过以下几种方案

## `commit=True`

这通常适用于手动创建的 [session 生成器](https://fastapi.tiangolo.com/tutorial/sql-databases/?h=get_db#create-a-dependency),
SQLAlchemy CRUD Plus 将在内部自动执行提交

```py hl_lines="31"
from fastapi import FastAPI, Depends

from pydantic import BaseModel

--8<-- "docs/ext/get_db.py"

app = FastAPI()


class CreateIns(BaseModel):
    # your pydantic schema
    pass


@app.post('/api', summary='新增一条数据')
async def create(self, obj: CreateIns, db: AsyncSession = Depends(get_db)) -> None:
    await self.create_model(db, obj, commit=True)
```

## `begin()`

适用于自动提交，[这一切都由 sqlalchemy 在内部完成](https://docs.sqlalchemy.org.cn/en/20/orm/session_transaction.html)
，因此，用户无需重复调用 commit 方法

```py hl_lines="9"
--8<-- "docs/ext/async_db_session.py"

async def create(self, obj: CreateIns) -> None:
    async with async_db_session.begin() as db:
        await self.create_model(db, obj)
```
