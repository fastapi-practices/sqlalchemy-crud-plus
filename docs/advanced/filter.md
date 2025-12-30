# 过滤条件

SQLAlchemy CRUD Plus 支持 30+ 种过滤操作符，用于构建复杂的查询条件。

## 基础用法

```python
# 使用过滤条件查询
users = await user_crud.select_models(
    session,
    name="张三",  # 等于
    age__gt=18,  # 大于
    email__like="%@qq.com"  # 模糊匹配
)
```

## 比较操作符

```python
# 数值比较
users = await user_crud.select_models(
    session,
    age__gt=30,  # 大于 30
    age__ge=18,  # 大于等于 18
    age__lt=65,  # 小于 65
    age__le=60,  # 小于等于 60
    id__eq=1,  # 等于 1
    status__ne=0  # 不等于 0
)
```

## 范围操作符

```python
# 包含查询
users = await user_crud.select_models(
    session,
    id__in=[1, 2, 3, 4, 5],  # ID 在列表中
    status__not_in=[0, -1],  # 状态不在列表中
    age__between=[18, 65]  # 年龄在 18-65 之间
)
```

## 字符串操作符

```python
# 字符串匹配
users = await user_crud.select_models(
    session,
    name__like='%张%',  # 包含"张"
    name__not_like='%test%',  # 不包含"test"
    name__ilike='%ADMIN%',  # 不区分大小写包含
    email__startswith='admin',  # 以"admin"开头
    email__endswith='@qq.com',  # 以"@qq.com"结尾
    bio__contains='程序员',  # 包含"程序员"
)
```

## 空值检查

```python
# NULL 值处理
users = await user_crud.select_models(
    session,
    deleted_at__is=None,  # 为 NULL
    profile_id__is_not=None,  # 不为 NULL
)
```

## OR 条件查询

### 同字段多值

```python
# 邮箱域名为 gmail.com 或 qq.com 的用户
users = await user_crud.select_models(
    session,
    __or__={
        'email__endswith': ['@gmail.com', '@qq.com']
    }
)
```

### 不同字段条件

```python
# 名字包含"张"或邮箱以admin开头的用户
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
# 多种条件组合
users = await user_crud.select_models(
    session,
    is_active=True,  # 必须是活跃用户
    __or__={
        'level__ge': 5,  # 等级大于等于5
        'is_vip': True,  # 或者是VIP
        'total_spent__gt': 1000  # 或者消费大于1000
    }
)
```

## 操作符参考

### 比较操作符

| 操作符    | 说明   | 示例             |
|--------|------|----------------|
| `__gt` | 大于   | `age__gt=18`   |
| `__ge` | 大于等于 | `age__ge=18`   |
| `__lt` | 小于   | `age__lt=65`   |
| `__le` | 小于等于 | `age__le=65`   |
| `__eq` | 等于   | `id__eq=1`     |
| `__ne` | 不等于  | `status__ne=0` |

### 包含操作符

| 操作符         | 说明    | 示例                     |
|-------------|-------|------------------------|
| `__in`      | 在列表中  | `id__in=[1,2,3]`       |
| `__not_in`  | 不在列表中 | `id__not_in=[1,2,3]`   |
| `__between` | 在范围内  | `age__between=[18,65]` |

### 字符串操作符

| 操作符            | 说明          | 示例                          |
|----------------|-------------|-----------------------------|
| `__like`       | 模糊匹配        | `name__like='%张%'`          |
| `__not_like`   | 模糊不匹配       | `name__not_like='%test%'`   |
| `__ilike`      | 不区分大小写模糊匹配  | `name__ilike='%ZHANG%'`     |
| `__not_ilike`  | 不区分大小写模糊不匹配 | `name__not_ilike='%TEST%'`  |
| `__startswith` | 开头匹配        | `email__startswith='admin'` |
| `__endswith`   | 结尾匹配        | `email__endswith='@qq.com'` |
| `__contains`   | 包含          | `name__contains='张'`        |

### 空值操作符

| 操作符        | 说明    | 示例                        |
|------------|-------|---------------------------|
| `__is`     | 为空检查  | `deleted_at__is=None`     |
| `__is_not` | 不为空检查 | `deleted_at__is_not=None` |

## 实际应用示例

### 用户搜索功能

```python
async def search_users(
        session: AsyncSession,
        keyword: str = None,
        age_min: int = None,
        age_max: int = None,
        is_active: bool = None
):
    filters = {}

    # 关键词搜索（姓名或邮箱）
    if keyword:
        filters['__or__'] = {
            'name__like': f'%{keyword}%',
            'email__like': f'%{keyword}%'
        }

    # 年龄范围
    if age_min is not None:
        filters['age__ge'] = age_min
    if age_max is not None:
        filters['age__le'] = age_max

    # 状态筛选
    if is_active is not None:
        filters['is_active'] = is_active

    return await user_crud.select_models(session, **filters)
```

### 高级筛选

```python
# 查找活跃的高级用户
users = await user_crud.select_models(
    session,
    is_active=True,
    created_at__ge='2024-01-01',
    __or__={
        'level__ge': 5,
        'is_vip': True,
        'total_orders__gt': 10
    }
)
```

## 复合主键支持

SQLAlchemy CRUD Plus 自动检测模型主键，支持单个主键和复合主键。

### 复合主键模型

```python
class UserRole(Base):
    __tablename__ = 'user_roles'

    # 复合主键
    user_id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime)
```

### 复合主键操作

```python
# 创建
user_role_data = UserRoleCreate(user_id=1, role_id=2)
user_role = await user_role_crud.create_model(session, user_role_data)

# 查询（使用元组）
user_role = await user_role_crud.select_model(session, pk=(1, 2))

# 更新
await user_role_crud.update_model(
    session,
    pk=(1, 2),
    obj={"assigned_at": datetime.now()}
)

# 删除
await user_role_crud.delete_model(session, pk=(1, 2))

# 批量查询
user_roles = await user_role_crud.select_models(session, user_id=1)
```

## 性能建议

### 索引优化

```python
# 为常用查询字段创建索引
class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    # 复合索引
    __table_args__ = (
        Index('idx_user_active_created', 'is_active', 'created_at'),
    )
```

### 查询优化技巧

```python
# 使用 exists 检查存在性（更高效）
exists = await user_crud.exists(session, email="test@example.com")

# 使用 limit 限制结果集
recent_users = await user_crud.select_models(
    session,
    created_at__ge=datetime.now() - timedelta(days=7),
    limit=100
)

# 避免前缀通配符（低效）
# 不推荐: name__like='%张%'
# 推荐: name__like='张%'
```

## 注意事项

1. **参数命名**: 主键参数使用 `pk`，避免与 Python 关键字 `id` 冲突
2. **自动主键检测**: 支持各种主键类型，包括字符串主键和复合主键
3. **性能考虑**: 为常用过滤字段创建数据库索引
4. **OR 查询**: 过多 OR 条件可能影响性能，合理使用
5. **通配符**: 避免以通配符开头的 LIKE 查询
