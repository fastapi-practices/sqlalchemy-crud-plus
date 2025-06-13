# 关系查询

SQLAlchemy CRUD Plus 提供强大的关系查询功能，通过 `load_options`、`load_strategies` 和 `join_conditions` 参数实现灵活的数据加载和连接控制。

## 关系查询参数

**核心参数**

- `load_options` - 原生 SQLAlchemy 选项
- `load_strategies` - 简化的加载策略
- `join_conditions` - JOIN 条件控制

## load_options 参数

使用原生 SQLAlchemy 选项进行精确控制：

```python
from sqlalchemy.orm import selectinload, joinedload

# 使用原生 SQLAlchemy 选项
user = await user_crud.select_model(
    session, user_id,
    load_options=[
        selectinload(User.posts),
        joinedload(User.profile)
    ]
)

# 嵌套关系
user = await user_crud.select_model(
    session, user_id,
    load_options=[
        selectinload(User.posts).selectinload(Post.comments),
        joinedload(User.profile)
    ]
)
```

## load_strategies 参数

使用字符串或字典指定加载策略：

```python
# 列表格式（使用默认策略）
user = await user_crud.select_model(
    session, user_id,
    load_strategies=['posts', 'profile']
)

# 字典格式（指定具体策略）
user = await user_crud.select_model(
    session, user_id,
    load_strategies={
        'posts': 'selectinload',
        'profile': 'joinedload',
        'roles': 'subqueryload'
    }
)

# 嵌套关系
user = await user_crud.select_model(
    session, user_id,
    load_strategies={
        'posts': 'selectinload',
        'posts.category': 'joinedload',
        'posts.comments': 'selectinload'
    }
)
```

## join_conditions 参数

控制表连接行为：

```python
# 列表格式（使用默认 INNER JOIN）
users = await user_crud.select_models(
    session,
    join_conditions=['posts']
)

# 字典格式（指定 JOIN 类型）
users = await user_crud.select_models(
    session,
    join_conditions={
        'posts': 'inner',
        'profile': 'left',
        'roles': 'right'
    }
)

# 与过滤条件结合
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],
    name__like='%admin%'
)
```

## 加载策略类型

### selectinload

**适用场景：一对多关系**

```python
# 用户的多篇文章
user = await user_crud.select_model(
    session, user_id,
    load_strategies={'posts': 'selectinload'}
)

# 文章的多条评论
post = await post_crud.select_model(
    session, post_id,
    load_strategies={'comments': 'selectinload'}
)
```

**特点：**

- 使用单独的 SELECT 查询
- 避免笛卡尔积问题
- 适合大量子记录

### joinedload

**适用场景：一对一关系**

```python
# 用户的个人资料
user = await user_crud.select_model(
    session, user_id,
    load_strategies={'profile': 'joinedload'}
)

# 文章的分类
post = await post_crud.select_model(
    session, post_id,
    load_strategies={'category': 'joinedload'}
)
```

**特点：**

- 使用 LEFT OUTER JOIN
- 单个查询获取所有数据
- 适合少量关联数据

### subqueryload

**适用场景：多对多关系**

```python
# 用户的多个角色
user = await user_crud.select_model(
    session, user_id,
    load_strategies={'roles': 'subqueryload'}
)

# 文章的多个标签
post = await post_crud.select_model(
    session, post_id,
    load_strategies={'tags': 'subqueryload'}
)
```

**特点：**

- 使用子查询加载
- 适合复杂关系
- 避免重复数据

### contains_eager

**适用场景：已经 JOIN 的关系**

```python
# 与 join_conditions 结合使用
users = await user_crud.select_models(
    session,
    join_conditions={'posts': 'inner'},
    load_strategies={'posts': 'contains_eager'}
)
```

### raiseload 和 noload

**适用场景：禁止加载**

```python
# 禁止访问关系（抛出异常）
user = await user_crud.select_model(
    session, user_id,
    load_strategies={'posts': 'raiseload'}
)

# 禁止加载关系（返回 None）
user = await user_crud.select_model(
    session, user_id,
    load_strategies={'posts': 'noload'}
)
```

## 组合使用

### 预加载 + JOIN

```python
# JOIN 用于过滤，预加载用于获取数据
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],  # 只要有文章的用户
    load_strategies=['posts', 'profile']  # 预加载数据
)
```

### 嵌套关系

```python
# 多层关系预加载
users = await user_crud.select_models(
    session,
    load_strategies={
        'posts': 'selectinload',
        'posts.category': 'joinedload',
        'posts.comments': 'selectinload'
    }
)
```

### 复杂查询

```python
# 组合所有参数
users = await user_crud.select_models(
    session,
    # 原生选项
    load_options=[selectinload(User.posts)],
    # 简化策略
    load_strategies={'profile': 'joinedload'},
    # JOIN 条件
    join_conditions={'posts': 'inner'},
    # 过滤条件
    is_active=True,
    name__like='%admin%'
)
```

## 性能优化

### 避免 N+1 查询

```python
# ❌ 错误：N+1 查询
users = await user_crud.select_models(session, limit=10)
for user in users:
    print(len(user.posts))  # 每次访问都触发查询

# ✅ 正确：预加载
users = await user_crud.select_models(
    session,
    load_strategies=['posts'],
    limit=10
)
for user in users:
    print(len(user.posts))  # 无额外查询
```

## 最佳实践

1. **选择合适的加载策略**
    - 一对一关系：使用 `joinedload`
    - 一对多关系：使用 `selectinload`
    - 多对多关系：使用 `selectinload` 或 `subqueryload`

2. **合理使用 JOIN**
    - 用于过滤条件而非数据获取
    - 结合预加载策略使用
    - 避免过多的 INNER JOIN

3. **性能监控**
    - 使用 `echo=True` 监控 SQL 查询
    - 避免 N+1 查询问题
    - 合理设置查询限制
