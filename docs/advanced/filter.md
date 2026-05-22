# 过滤条件

过滤条件通过关键字参数传入：`字段名__操作符=值`。没有操作符时表示等于，例如 `name='张三'`。

```python
users = await user_crud.select_models(
    session,
    name__like='%张%',
    age__ge=18,
    is_active=True
)
```

## 常用操作符

| 类型 | 操作符 | 示例 | 说明 |
| --- | --- | --- | --- |
| 等值 | 无 / `__eq` | `name='张三'`、`id__eq=1` | 等于 |
| 比较 | `__gt` / `__ge` | `age__gt=18` | 大于 / 大于等于 |
| 比较 | `__lt` / `__le` | `age__le=60` | 小于 / 小于等于 |
| 不等 | `__ne` | `status__ne=0` | 不等于 |
| 集合 | `__in` / `__not_in` | `id__in=[1, 2]` | 在 / 不在列表中 |
| 范围 | `__between` | `age__between=[18, 65]` | 闭区间范围 |
| 字符串 | `__like` / `__not_like` | `name__like='%张%'` | LIKE / NOT LIKE |
| 字符串 | `__ilike` / `__not_ilike` | `name__ilike='%admin%'` | 忽略大小写匹配 |
| 字符串 | `__startswith` | `email__startswith='admin'` | 前缀匹配 |
| 字符串 | `__endswith` | `email__endswith='@example.com'` | 后缀匹配 |
| 字符串 | `__contains` | `bio__contains='Python'` | 包含 |
| 空值 | `__is` / `__is_not` | `deleted_at__is=None` | IS / IS NOT |

## OR 条件

使用特殊键 `__or__` 表示 OR。外层其他条件仍然是 AND。

```python
# 名称包含“张”，或邮箱以 admin 开头。
users = await user_crud.select_models(
    session,
    __or__={
        'name__like': '%张%',
        'email__startswith': 'admin'
    }
)
```

同一个字段需要多个 OR 值时，传列表：

```python
users = await user_crud.select_models(
    session,
    is_active=True,
    __or__={
        'email__endswith': ['@gmail.com', '@qq.com']
    }
)
```

## 组合示例

```python
async def search_users(session: AsyncSession, keyword: str | None = None):
    filters = {'is_active': True}

    if keyword:
        filters['__or__'] = {
            'name__like': f'%{keyword}%',
            'email__like': f'%{keyword}%'
        }

    return await user_crud.select_models(
        session,
        **filters,
        limit=20
    )
```

```python
users = await user_crud.select_models_order(
    session,
    sort_columns='created_at',
    sort_orders='desc',
    created_at__ge='2024-01-01',
    age__between=[18, 65],
    status__not_in=['blocked', 'deleted']
)
```

## 复合主键

CRUDPlus 会自动识别单主键和复合主键。复合主键查询、更新、删除时用元组传入 `pk`。

```python
class UserRole(Base):
    __tablename__ = 'user_roles'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(primary_key=True)
```

```python
user_role = await user_role_crud.select_model(session, pk=(1, 2))

await user_role_crud.update_model(
    session,
    pk=(1, 2),
    obj={'role_name': 'admin'}
)

await user_role_crud.delete_model(session, pk=(1, 2))
```

## 性能建议

- 常用过滤字段应建立索引，例如 `email`、`status`、`created_at`。
- `exists()` 比查询整条记录更适合做存在性检查。
- 列表查询务必配合 `limit`，避免一次加载过多数据。
- `LIKE '%keyword%'` 通常无法有效利用普通索引；能用前缀匹配时优先 `LIKE 'keyword%'`。
- OR 条件过多时，建议评估 SQL 执行计划。
