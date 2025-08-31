# 关系查询

SQLAlchemy CRUD Plus 提供强大的关系查询功能，支持预加载策略和 JOIN 查询，有效避免 N+1 查询问题。

## 基础用法

```python
# 预加载关系数据
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies=['posts', 'profile']
)

# JOIN 查询
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],
    is_active=True
)
```

## 核心参数

SQLAlchemy CRUD Plus 提供三个关键参数控制关系查询：

- **load_strategies** - 关系数据加载策略
- **join_conditions** - JOIN 条件控制  
- **load_options** - 原生 SQLAlchemy 选项

## load_strategies 参数

### 列表格式

```python
# 使用默认加载策略
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies=['posts', 'profile']
)
```

### 字典格式

```python
# 指定具体策略
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies={
        'posts': 'selectinload',    # 一对多关系
        'profile': 'joinedload',    # 一对一关系
        'roles': 'subqueryload'     # 多对多关系
    }
)
```

## join_conditions 参数

### 基础 JOIN

```python
# 默认使用 INNER JOIN
users = await user_crud.select_models(
    session,
    join_conditions=['posts']
)
```

### 指定 JOIN 类型

```python
# 指定不同的 JOIN 类型
users = await user_crud.select_models(
    session,
    join_conditions={
        'posts': 'inner',      # INNER JOIN
        'profile': 'left'      # LEFT JOIN
    }
)
```

### 自定义 JOIN ON 条件

当需要更复杂的 JOIN 条件时，可以使用 `JoinConfig` 类：

```python
from sqlalchemy_crud_plus import JoinConfig

# 自定义 JOIN ON 条件
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=User.id == Post.author_id,
            join_type='inner'
        )
    ]
)
```

### 复杂 JOIN ON 示例

```python
# 带条件的 JOIN
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=and_(
                User.id == Post.author_id,
                Post.is_published == True,
                Post.created_at >= datetime(2024, 1, 1)
            ),
            join_type='left'
        )
    ]
)

# 多表 JOIN
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=User.id == Post.author_id,
            join_type='inner'
        ),
        JoinConfig(
            model=Category,
            join_on=Post.category_id == Category.id,
            join_type='left'
        )
    ]
)
```

### 混合使用关系和自定义 JOIN

```python
# 关系 JOIN 与自定义 JOIN 结合
users = await user_crud.select_models(
    session,
    join_conditions=[
        'profile',  # 基于关系的 JOIN
        JoinConfig(
            model=Post,
            join_on=and_(
                User.id == Post.author_id,
                Post.status == 'published'
            ),
            join_type='left'
        )
    ]
)
```

### JOIN 与过滤结合

```python
# JOIN 用于过滤条件
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],
    name__like='%admin%',       # 用户名过滤
    is_active=True              # 活跃用户
)

# 自定义 JOIN 与过滤结合
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=and_(
                User.id == Post.author_id,
                Post.view_count > 100
            ),
            join_type='inner'
        )
    ],
    is_active=True,
    created_at__gt=datetime(2024, 1, 1)
)
```

## 加载策略详解

### selectinload - 一对多关系

适用于一对多关系，避免笛卡尔积问题。

```python
# 用户的多篇文章
users = await user_crud.select_models(
    session,
    load_strategies={'posts': 'selectinload'}
)

# 文章的多条评论
posts = await post_crud.select_models(
    session,
    load_strategies={'comments': 'selectinload'}
)
```

**特点:**
- 使用 SELECT IN 查询
- 避免重复数据
- 适合大量子记录

### joinedload - 一对一关系

适用于一对一关系，单次查询获取所有数据。

```python
# 用户的个人资料
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies={'profile': 'joinedload'}
)

# 文章的分类信息
posts = await post_crud.select_models(
    session,
    load_strategies={'category': 'joinedload'}
)
```

**特点:**
- 使用 LEFT OUTER JOIN
- 单个查询获取所有数据
- 适合少量关联数据

### subqueryload - 多对多关系

适用于复杂关系，使用子查询加载。

```python
# 用户的多个角色
users = await user_crud.select_models(
    session,
    load_strategies={'roles': 'subqueryload'}
)
```

**特点:**
- 使用子查询
- 适合复杂多对多关系
- 避免笛卡尔积

## load_options 参数

使用原生 SQLAlchemy 选项进行精确控制：

```python
from sqlalchemy.orm import selectinload, joinedload

# 原生选项
user = await user_crud.select_model(
    session,
    pk=1,
    load_options=[
        selectinload(User.posts),
        joinedload(User.profile)
    ]
)

# 嵌套关系
user = await user_crud.select_model(
    session,
    pk=1,
    load_options=[
        selectinload(User.posts).selectinload(Post.comments)
    ]
)
```

## 组合使用

### 预加载 + JOIN

```python
# JOIN 用于过滤，预加载用于获取数据
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],              # 只要有文章的用户
    load_strategies=['posts', 'profile'],   # 预加载数据
    is_active=True
)
```

### 复杂组合

```python
# 组合所有参数
users = await user_crud.select_models(
    session,
    # 预加载策略
    load_strategies={
        'posts': 'selectinload',
        'profile': 'joinedload'
    },
    # JOIN 条件
    join_conditions={'posts': 'inner'},
    # 过滤条件
    is_active=True,
    name__like='%admin%'
)
```

## 实际应用示例

### 用户详情页面

```python
async def get_user_detail(session: AsyncSession, user_id: int):
    """获取用户详细信息"""
    return await user_crud.select_model(
        session,
        pk=user_id,
        load_strategies={
            'posts': 'selectinload',        # 用户文章
            'profile': 'joinedload',        # 用户资料
            'roles': 'selectinload'         # 用户角色
        }
    )
```

### 文章列表页面

```python
async def get_posts_with_author(session: AsyncSession, page: int = 1):
    """获取文章列表及作者信息"""
    offset = (page - 1) * 20
    
    return await post_crud.select_models(
        session,
        load_strategies={
            'author': 'joinedload',         # 作者信息
            'category': 'joinedload',       # 分类信息
            'comments': 'selectinload'      # 评论列表
        },
        is_published=True,
        limit=20,
        offset=offset
    )
```

### 活跃用户统计

```python
async def get_active_users_with_posts(session: AsyncSession):
    """获取有文章的活跃用户"""
    return await user_crud.select_models(
        session,
        join_conditions=['posts'],      # 只要有文章的用户
        load_strategies=['posts'],      # 预加载文章
        is_active=True,
        posts_count__gt=0
    )
```

## 性能优化

### 避免 N+1 查询

```python
# 错误：N+1 查询
users = await user_crud.select_models(session, limit=10)
for user in users:
    print(len(user.posts))  # 每次访问都触发查询

# 正确：预加载
users = await user_crud.select_models(
    session,
    load_strategies=['posts'],
    limit=10
)
for user in users:
    print(len(user.posts))  # 无额外查询
```

### 策略选择指南

| 关系类型 | 推荐策略 | 说明 |
|---------|----------|------|
| 一对一 | joinedload | 单次查询，数据量小 |
| 一对多 | selectinload | 避免笛卡尔积 |
| 多对多 | selectinload | 处理复杂关系 |
| 大数据量 | subqueryload | 适合复杂场景 |

### 监控查询

```python
# 开启 SQL 日志查看生成的查询
engine = create_async_engine(DATABASE_URL, echo=True)

# 查看执行的 SQL 语句
users = await user_crud.select_models(
    session,
    load_strategies=['posts']
)
```

## 常见错误

### 错误的策略选择

```python
# 错误：对一对多关系使用 joinedload
users = await user_crud.select_models(
    session,
    load_strategies={'posts': 'joinedload'}  # 会产生笛卡尔积
)

# 正确：使用 selectinload
users = await user_crud.select_models(
    session,
    load_strategies={'posts': 'selectinload'}
)
```

### 嵌套关系

```python
# 当前不支持嵌套关系
users = await user_crud.select_models(
    session,
    load_strategies={
        'posts': 'selectinload',
        'posts.comments': 'selectinload',  # error
        'posts.comments.author': 'selectinload',  # error
    }
)
```

## 最佳实践

1. **选择合适的加载策略**
   - 一对一关系使用 `joinedload`
   - 一对多关系使用 `selectinload`
   - 多对多关系使用 `selectinload` 或 `subqueryload`

2. **合理使用 JOIN**
   - 用于过滤条件而非数据获取
   - 结合预加载策略使用
   - 避免过多的 INNER JOIN

3. **性能监控**
   - 使用 `echo=True` 监控 SQL 查询
   - 避免 N+1 查询问题
   - 合理设置查询限制

4. **错误处理**
   - 检查关系是否正确定义
   - 验证预加载策略是否生效
   - 处理关系数据为空的情况

## JOIN ON 条件的高级用法

### 使用 SQLAlchemy 函数

```python
from sqlalchemy import func, case

# 使用函数的 JOIN 条件
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=and_(
                User.id == Post.author_id,
                func.date(Post.created_at) == func.current_date()
            ),
            join_type='left'
        )
    ]
)

# 条件表达式 JOIN
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=and_(
                User.id == Post.author_id,
                case(
                    (User.role == 'admin', Post.status.in_(['draft', 'published'])),
                    else_=Post.status == 'published'
                )
            ),
            join_type='inner'
        )
    ]
)
```

### 外键关系以外的 JOIN

```python
# 基于非外键字段的 JOIN
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=UserStats,
            join_on=User.email == UserStats.user_email,
            join_type='left'
        )
    ]
)

# 基于计算字段的 JOIN
orders = await order_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Discount,
            join_on=and_(
                Order.total_amount >= Discount.min_amount,
                Order.total_amount <= Discount.max_amount,
                Discount.is_active == True
            ),
            join_type='left'
        )
    ]
)
```

## 性能优化建议

### JOIN ON 的最佳实践

1. **索引优化**: 确保 JOIN 条件中的字段都有适当的索引
2. **条件顺序**: 将最具选择性的条件放在前面
3. **避免函数**: 在 JOIN 条件中避免使用函数，除非必要
4. **类型匹配**: 确保 JOIN 的字段类型匹配

```python
# 好的做法 - 基于索引字段
JoinConfig(
    model=Post,
    join_on=User.id == Post.author_id,  # 两个字段都有索引
    join_type='inner'
)

# 避免的做法 - 函数调用可能影响性能
JoinConfig(
    model=Post,
    join_on=func.lower(User.email) == func.lower(Post.author_email),
    join_type='inner'
)
```

## 下一步

- [事务控制](../advanced/transaction.md) - 学习事务管理
- [过滤条件](../advanced/filter.md) - 高级过滤技术
- [API 参考](../api/crud-plus.md) - 完整 API 文档
