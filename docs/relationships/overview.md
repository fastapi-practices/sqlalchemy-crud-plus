# 关系查询概览

SQLAlchemy CRUD Plus 提供强大的关系查询功能，通过三参数系统实现灵活的数据加载和连接控制。

## 三参数系统

**核心参数**
- `load_options` - 原生 SQLAlchemy 选项
- `load_strategies` - 简化的加载策略
- `join_conditions` - JOIN 条件控制

## load_options - 原生选项

使用原生 SQLAlchemy 选项进行精确控制：

```python
from sqlalchemy.orm import selectinload, joinedload

user = await user_crud.select_model(
    session, user_id,
    load_options=[
        selectinload(User.posts),
        joinedload(User.profile)
    ]
)
```

## load_strategies - 简化策略

使用字符串或字典指定加载策略：

```python
# 简单列表格式
user = await user_crud.select_model(
    session, user_id,
    load_strategies=['posts', 'profile']
)

# 字典格式指定策略
user = await user_crud.select_model(
    session, user_id,
    load_strategies={
        'posts': 'selectinload',
        'profile': 'joinedload'
    }
)
```

## join_conditions - JOIN 控制

控制表连接行为：

```python
# 简单 JOIN
users = await user_crud.select_models(
    session,
    join_conditions=['posts']
)

# 指定 JOIN 类型
users = await user_crud.select_models(
    session,
    join_conditions={
        'posts': 'inner',
        'profile': 'left'
    }
)
```

## 加载策略类型

### selectinload
**最适合：一对多关系**

```python
user = await user_crud.select_model(
    session, user_id,
    load_strategies={'posts': 'selectinload'}
)
```

- 使用单独的 SELECT 查询
- 避免笛卡尔积问题
- 适合大量子记录

### joinedload
**最适合：一对一关系**

```python
user = await user_crud.select_model(
    session, user_id,
    load_strategies={'profile': 'joinedload'}
)
```

- 使用 LEFT OUTER JOIN
- 单个查询获取所有数据
- 适合少量关联数据

### subqueryload
**最适合：多对多关系**

```python
user = await user_crud.select_model(
    session, user_id,
    load_strategies={'roles': 'subqueryload'}
)
```

- 使用子查询加载
- 适合复杂关系
- 避免重复数据

## 方法支持

| 方法 | load_options | load_strategies | join_conditions |
|------|-------------|----------------|----------------|
| `select_model` | ✅ | ✅ | ✅ |
| `select_model_by_column` | ✅ | ✅ | ✅ |
| `select_models` | ✅ | ✅ | ✅ |
| `select_models_order` | ✅ | ✅ | ✅ |
| `count` | ❌ | ❌ | ✅ |
| `exists` | ❌ | ❌ | ✅ |

## 组合使用

### 预加载 + JOIN

```python
# JOIN 用于过滤，预加载用于获取数据
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],           # 只要有文章的用户
    load_strategies=['posts', 'profile'] # 预加载数据
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

### 选择合适的策略

```python
# 推荐的策略组合
load_strategies = {
    'profile': 'joinedload',        # 一对一
    'posts': 'selectinload',        # 一对多
    'roles': 'selectinload',        # 多对多
    'posts.category': 'joinedload'  # 嵌套一对一
}
```

## 实际应用

### 用户详情页面

```python
async def get_user_detail(user_id: int):
    async with _async_db_session() as session:
        user = await user_crud.select_model(
            session, user_id,
            load_strategies={
                'profile': 'joinedload',
                'posts': 'selectinload',
                'posts.category': 'joinedload',
                'roles': 'selectinload'
            }
        )
        return user
```

### 文章列表

```python
async def get_posts_with_authors():
    async with _async_db_session() as session:
        posts = await post_crud.select_models(
            session,
            join_conditions=['author'],  # 只要有作者的文章
            load_strategies={
                'author': 'joinedload',
                'category': 'joinedload'
            },
            limit=20
        )
        return posts
```

### 统计查询

```python
async def get_statistics():
    async with _async_db_session() as session:
        # 有文章的用户数量
        users_with_posts = await user_crud.count(
            session,
            join_conditions=['posts']
        )
        
        # 有评论的文章数量
        posts_with_comments = await post_crud.count(
            session,
            join_conditions=['comments']
        )
        
        return {
            'users_with_posts': users_with_posts,
            'posts_with_comments': posts_with_comments
        }
```

## 最佳实践

1. **选择合适的加载策略**
   - 一对一：使用 `joinedload`
   - 一对多：使用 `selectinload`
   - 多对多：使用 `selectinload` 或 `subqueryload`

2. **合理使用 JOIN**
   - 用于过滤条件而非数据获取
   - 结合预加载策略使用
   - 避免过多的 INNER JOIN

3. **性能监控**
   - 使用 `echo=True` 监控 SQL 查询
   - 避免 N+1 查询问题
   - 合理设置查询限制

4. **代码组织**
   - 将复杂的关系查询封装成函数
   - 使用常量定义常用的策略组合
   - 根据业务场景选择合适的参数
