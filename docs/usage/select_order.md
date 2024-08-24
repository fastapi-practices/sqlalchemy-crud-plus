```py
async def select_order(
    self,
    sort_columns: str | list[str],
    sort_orders: str | list[str] | None = None,
    **kwargs,
) -> Select:
```

此方法与 [select](./select.md) 方法类似，但增加了 [排序](./select_models_order.md/#_1) 功能
