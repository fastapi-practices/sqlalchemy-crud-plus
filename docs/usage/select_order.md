此方法与 [select](./select.md) 方法类似，但增加了排序功能

```py
async def select_order(
    self,
    sort_columns: str | list[str],
    sort_orders: str | list[str] | None = None,
    **kwargs,
) -> Select:
```

**Parameters:**

| Name         | Type                           | Description                                                            | Default |
|--------------|--------------------------------|------------------------------------------------------------------------|---------|
| sort_columns | `str `\|` list[str]`           | 应用排序的单个列名或列名列表                                                         | 必填      |
| sort_orders  | `str `\|` list[str] `\|` None` | 单个排序顺序（asc 或 desc）或与 sort_columns 中的列相对应的排序顺序列表。 如果未提供，则默认每列的排序顺序为 asc | `None`  |

!!! note "**kwargs"

    [条件过滤](../advanced/filter.md)，将创建条件查询 SQL

**Returns:**

| Type   | Description          |
|--------|----------------------|
| Select | SQLAlchemy Select 对象 |
