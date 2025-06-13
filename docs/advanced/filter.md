# 过滤条件

SQLAlchemy CRUD Plus 支持 34+ 种过滤操作符，允许构建复杂的查询条件。

## 比较操作符

```python
# 数值比较
users = await user_crud.select_models(
    session,
    age__gt=30,         # 大于
    age__ge=18,         # 大于等于
    age__lt=65,         # 小于
    age__le=60,         # 小于等于
    id__eq=1,           # 等于
    status__ne=0        # 不等于
)
```

## 范围操作符

```python
# 范围查询
users = await user_crud.select_models(
    session,
    id__in=[1, 2, 3, 4, 5],     # 包含在列表中
    status__not_in=[0, -1],     # 不包含在列表中
    age__between=[30, 40]       # 在范围内
)
```

## 字符串操作符

```python
# 字符串匹配
users = await user_crud.select_models(
    session,
    name__like='%张%',              # 包含"张"
    name__not_like='%test%',        # 不包含"test"
    name__ilike='%ADMIN%',          # 不区分大小写包含
    name__not_ilike='%TEST%',       # 不区分大小写不包含
    email__startswith='admin',      # 以"admin"开头
    email__endswith='@qq.com',      # 以"@qq.com"结尾
    bio__contains='程序员',          # 包含"程序员"
    name__match='pattern'           # 正则匹配（依赖数据库支持）
)
```

## 身份比较操作符

```python
# NULL 值检查
users = await user_crud.select_models(
    session,
    deleted_at__is=None,                    # 为 NULL
    profile_id__is_not=None,                # 不为 NULL
    status__is_distinct_from=0,             # 与 0 不同（包括 NULL）
    status__is_not_distinct_from=1          # 与 1 相同（不包括 NULL）
)
```

## 字符串变换操作符

```python
# 字符串连接
users = await user_crud.select_models(
    session,
    name__concat='_suffix'          # 连接后缀
)
```

## 算术操作符

```python
# 算术运算
users = await user_crud.select_models(
    session,
    age__add=5,                     # age + 5
    age__radd=10,                   # 10 + age
    score__sub=10,                  # score - 10
    score__rsub=100,                # 100 - score
    price__mul=2,                   # price * 2
    price__rmul=3,                  # 3 * price
    price__truediv=2,               # price / 2
    price__rtruediv=100,            # 100 / price
    count__floordiv=10,             # count // 10
    count__rfloordiv=100,           # 100 // count
    number__mod=3,                  # number % 3
    number__rmod=10                 # 10 % number
)
```

## OR 条件

### 同字段多值

```python
# 邮箱域名为 gmail.com 或 qq.com
users = await user_crud.select_models(
    session,
    __or__={
        'email__endswith': ['@gmail.com', '@qq.com']
    }
)
```

### 不同字段条件

```python
# 名字包含"张"或邮箱以admin开头
users = await user_crud.select_models(
    session,
    __or__={
        'name__like': '%张%',
        'email__startswith': 'admin'
    }
)
```

### 复杂 OR 条件

```python
# 混合使用
users = await user_crud.select_models(
    session,
    __or__={
        'status': [1, 2, 3],           # status 等于 1 或 2 或 3
        'is_vip': True,                # 或者是 VIP
        'created_time__gt': '2023-01-01' # 或者创建时间大于指定日期
    }
)
```

### 字段级 OR 操作

```python
# 单个字段的多种条件
users = await user_crud.select_models(
    session,
    name__or={
        'like': '%张%',
        'startswith': 'admin'
    }
)
```

## 组合条件

```python
# AND 条件（默认）
users = await user_crud.select_models(
    session,
    age__gt=30,                 # 年龄大于 30
    is_active=True,             # 并且是活跃用户
    name__like='%张%'           # 并且名字包含"张"
)

# AND + OR 组合
users = await user_crud.select_models(
    session,
    is_active=True,             # 必须是活跃用户
    __or__={                    # 并且满足以下任一条件
        'age__gt': 40,
        'is_vip': True
    }
)
```

## 支持的操作符

### 比较操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `__gt` | 大于 | `age__gt=18` |
| `__ge` | 大于等于 | `age__ge=18` |
| `__lt` | 小于 | `age__lt=65` |
| `__le` | 小于等于 | `age__le=65` |
| `__eq` | 等于 | `id__eq=1` |
| `__ne` | 不等于 | `status__ne=0` |
| `__between` | 在范围内 | `age__between=[18,65]` |

### 包含操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `__in` | 在列表中 | `id__in=[1,2,3]` |
| `__not_in` | 不在列表中 | `id__not_in=[1,2,3]` |

### 身份比较操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `__is` | 为空检查 | `deleted_at__is=None` |
| `__is_not` | 不为空检查 | `deleted_at__is_not=None` |
| `__is_distinct_from` | 身份不同 | `status__is_distinct_from=0` |
| `__is_not_distinct_from` | 身份相同 | `status__is_not_distinct_from=1` |

### 字符串操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `__like` | 模糊匹配 | `name__like='%张%'` |
| `__not_like` | 模糊不匹配 | `name__not_like='%test%'` |
| `__ilike` | 不区分大小写模糊匹配 | `name__ilike='%ZHANG%'` |
| `__not_ilike` | 不区分大小写模糊不匹配 | `name__not_ilike='%TEST%'` |
| `__startswith` | 开头匹配 | `email__startswith='admin'` |
| `__endswith` | 结尾匹配 | `email__endswith='@qq.com'` |
| `__contains` | 包含 | `name__contains='张'` |
| `__match` | 正则匹配 | `name__match='pattern'` |
| `__concat` | 字符串连接 | `name__concat='_suffix'` |

### 算术操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `__add` | 加法 | `age__add=5` |
| `__radd` | 反向加法 | `age__radd=10` |
| `__sub` | 减法 | `score__sub=10` |
| `__rsub` | 反向减法 | `score__rsub=100` |
| `__mul` | 乘法 | `price__mul=2` |
| `__rmul` | 反向乘法 | `price__rmul=3` |
| `__truediv` | 除法 | `price__truediv=2` |
| `__rtruediv` | 反向除法 | `price__rtruediv=100` |
| `__floordiv` | 整除 | `count__floordiv=10` |
| `__rfloordiv` | 反向整除 | `count__rfloordiv=100` |
| `__mod` | 取模 | `number__mod=3` |
| `__rmod` | 反向取模 | `number__rmod=10` |

## 实际应用

### 用户搜索

```python
def search_users(
    keyword: str = None,
    age_min: int = None,
    age_max: int = None,
    email_domain: str = None,
    is_active: bool = None
):
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

### 复杂查询

```python
# 查找活跃的高级用户
users = await user_crud.select_models(
    session,
    is_active=True,
    __or__={
        'level__ge': 5,
        'is_vip': True,
        'total_spent__gt': 1000
    },
    created_time__gt='2023-01-01'
)
```

## 性能建议

1. **索引优化**：为常用的过滤字段创建数据库索引
2. **避免前缀通配符**：`name__like='张%'` 比 `name__like='%张%'` 更高效
3. **使用 IN 查询**：对于多个值的查询，使用 `__in` 而不是多个 OR 条件
4. **限制结果集**：使用 `limit` 参数限制返回的记录数
5. **合理使用 OR**：过多的 OR 条件可能影响性能
