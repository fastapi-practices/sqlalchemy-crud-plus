# 过滤条件

SQLAlchemy CRUD Plus 支持丰富的过滤操作符，允许构建复杂的查询条件。

## 比较操作符

```python
async def compare_filters():
    async with _async_db_session() as session:
        # 数值比较
        users = await user_crud.select_models(
            session,
            age__gt=30,         # 大于
            age__ge=18,         # 大于等于
            age__lt=65,         # 小于
            age__le=60,         # 小于等于
            status__ne=0        # 不等于
        )
        return users
```

## 范围操作符

```python
async def range_filters():
    async with _async_db_session() as session:
        # 范围查询
        users = await user_crud.select_models(
            session,
            id__in=[1, 2, 3, 4, 5],     # 包含在列表中
            status__not_in=[0, -1],     # 不包含在列表中
            age__between=[30, 40]       # 在范围内
        )
        return users
```

## 字符串操作符

```python
async def string_filters():
    async with _async_db_session() as session:
        # 字符串匹配
        users = await user_crud.select_models(
            session,
            name__like='%张%',              # 包含"张"
            name__ilike='%ADMIN%',          # 不区分大小写包含
            email__startswith='admin',      # 以"admin"开头
            email__endswith='@qq.com',      # 以"@qq.com"结尾
            bio__contains='程序员'           # 包含"程序员"
        )
        return users
```

## 空值检查

```python
async def null_checks():
    async with _async_db_session() as session:
        # NULL 值检查
        users = await user_crud.select_models(
            session,
            deleted_at__is=None,        # 为 NULL
            profile_id__is_not=None     # 不为 NULL
        )
        return users
```

## 组合条件

```python
async def combined_conditions():
    async with _async_db_session() as session:
        # AND 条件（默认）
        users = await user_crud.select_models(
            session,
            age__gt=30,                 # 年龄大于 30
            is_active=True              # 并且是活跃用户
        )
        
        # OR 条件
        users = await user_crud.select_models(
            session,
            __or__={'age__gt': [40], 'age__lt': [30]}    # 年龄大于 40 或小于 30
        )
        return users
```

## OR 条件详解

### 同字段多值

```python
async def or_same_field():
    async with _async_db_session() as session:
        # 邮箱域名为 gmail.com 或 qq.com
        users = await user_crud.select_models(
            session,
            __or__={
                'email__endswith': ['@gmail.com', '@qq.com']
            }
        )
        return users
```

### 不同字段条件

```python
async def or_different_fields():
    async with _async_db_session() as session:
        # 名字包含"张"或邮箱以admin开头
        users = await user_crud.select_models(
            session,
            __or__={
                'name__like': '%张%',
                'email__startswith': 'admin'
            }
        )
        return users
```

### 复杂 OR 条件

```python
async def complex_or():
    async with _async_db_session() as session:
        # 混合使用
        users = await user_crud.select_models(
            session,
            __or__={
                'status': [1, 2, 3],           # status 在 [1,2,3] 中
                'is_vip': True,                # 或者是 VIP
                'created_at__gt': '2023-01-01' # 或者创建时间大于指定日期
            }
        )
        return users
```

## 支持的操作符

| 操作符 | 说明 | 示例 |
|--------|------|------|
| `__gt` | 大于 | `age__gt=18` |
| `__ge` | 大于等于 | `age__ge=18` |
| `__lt` | 小于 | `age__lt=65` |
| `__le` | 小于等于 | `age__le=65` |
| `__ne` | 不等于 | `status__ne=0` |
| `__like` | 模糊匹配 | `name__like='%张%'` |
| `__ilike` | 不区分大小写模糊匹配 | `name__ilike='%ZHANG%'` |
| `__startswith` | 开头匹配 | `email__startswith='admin'` |
| `__endswith` | 结尾匹配 | `email__endswith='@qq.com'` |
| `__contains` | 包含 | `name__contains='张'` |
| `__in` | 在列表中 | `id__in=[1,2,3]` |
| `__not_in` | 不在列表中 | `id__not_in=[1,2,3]` |
| `__between` | 在范围内 | `age__between=[18,65]` |
| `__is` | 为空检查 | `deleted_at__is=None` |
| `__is_not` | 不为空检查 | `deleted_at__is_not=None` |

## 实际应用示例

### 用户搜索

```python
async def search_users(
    keyword: str = None,
    age_min: int = None,
    age_max: int = None,
    email_domain: str = None,
    is_active: bool = None
):
    async with _async_db_session() as session:
        filters = {}

        if keyword:
            filters['__or__'] = {
                'name__like': f'%{keyword}%',
                'email__like': f'%{keyword}%'
            }

        if age_min is not None:
            filters['age__ge'] = age_min

        if age_max is not None:
            filters['age__le'] = age_max

        if email_domain:
            filters['email__endswith'] = f'@{email_domain}'

        if is_active is not None:
            filters['is_active'] = is_active

        users = await user_crud.select_models(session, **filters)
        return users
```

## 性能建议

1. **索引优化**：为常用的过滤字段创建数据库索引
2. **避免前缀通配符**：`name__like='张%'` 比 `name__like='%张%'` 更高效
3. **使用 IN 查询**：对于多个值的查询，使用 `__in` 而不是多个 OR 条件
4. **限制结果集**：使用 `limit` 参数限制返回的记录数
5. **合理使用 OR**：过多的 OR 条件可能影响性能
