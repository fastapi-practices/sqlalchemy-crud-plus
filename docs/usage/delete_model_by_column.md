```py
async def delete_model_by_column(
    self,
    session: AsyncSession,
    allow_multiple: bool = False,
    logical_deletion: bool = False,
    deleted_flag_column: str = 'del_flag',
    commit: bool = False,
    **kwargs,
) -> int:
```

- 此方法提供 `commit` 参数，详见：[提交](./create_model.md/#_1)

- 此方法可结合 [高级过滤器](../advanced/filter.md) 使用

## 删除多条

将参数 `allow_multiple` 设置为 True，将允许删除多条记录，删除的数量取决于过滤器过滤后的数据

## 软删除

此方法同时提供逻辑删除，将参数 `logical_deletion` 设置为 True，将不会从数据库中直接删除数据，而是通过更新的方式，
将数据库删除标志字段的值进行更新，你可以通过 `deleted_flag_column` 参数设置指定逻辑删除字段，默认为 `del_flag`

!!! warning "注意"

    逻辑删除也允许同时删除多条，同样由参数 `allow_multiple` 和过滤器控制

## 示例

```py title="delete_model_by_column" hl_lines="21"
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
    async def delete(self, db: AsyncSession) -> int:
        return await self.delete_model_by_column(db, name="foo")
```
