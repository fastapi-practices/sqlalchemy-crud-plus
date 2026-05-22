# SQLAlchemy CRUD Plus

基于 SQLAlchemy 2.0 的异步 CRUD 工具。它把常见的创建、查询、更新、删除、过滤、排序、关系加载和批量操作整理成一组稳定 API，适合 FastAPI 等异步项目使用。

## 适合什么场景

- 你已经在使用 SQLAlchemy 2.0 Async ORM
- 你希望用统一方法处理 CRUD、分页、过滤和排序
- 你需要 relationship 预加载、动态 JOIN 或字段加载控制
- 你想保留 SQLAlchemy 原生能力，而不是引入一套新 ORM

## 安装

=== "pip"

    ```bash
    pip install sqlalchemy-crud-plus
    ```

=== "uv"

    ```bash
    uv add sqlalchemy-crud-plus
    ```

## 最小示例

```python
from sqlalchemy_crud_plus import CRUDPlus

user_crud = CRUDPlus(User)

# 创建
user = await user_crud.create_model(session, user_data, commit=True)

# 查询
user = await user_crud.select_model(session, pk=1)
users = await user_crud.select_models(session, is_active=True, limit=20)

# 过滤和排序
users = await user_crud.select_models_order(
    session,
    sort_columns='created_at',
    sort_orders='desc',
    name__like='%admin%'
)

# 更新和删除
await user_crud.update_model(session, pk=1, obj={'name': 'new name'})
await user_crud.delete_model(session, pk=1)
```

## 主要能力

| 能力 | 用法入口 |
| --- | --- |
| 基础 CRUD | `create_model`、`select_model`、`update_model`、`delete_model` |
| 条件过滤 | `name__like`、`age__ge`、`__or__` 等 |
| 批量操作 | `create_models`、`bulk_create_models`、`bulk_update_models` |
| 关系查询 | `load_strategies`、`join_conditions`、`load_options` |
| 字段加载 | `load_only`、`defer`、`undefer` |
| 事务控制 | `flush=True`、`commit=True`、`session.begin()` |
| 复合主键 | `pk=(user_id, role_id)` |

## 下一步

- 新项目先看 [快速开始](getting-started/quick-start.md)
- 查 API 示例看 [CRUD 操作](usage/crud.md)
- 查过滤写法看 [过滤条件](advanced/filter.md)
- 查关系加载和 JOIN 看 [关系查询](advanced/relationship.md)
- 查事务建议看 [事务控制](advanced/transaction.md)
- 查完整签名看 [API 参考](api/crud-plus.md)
