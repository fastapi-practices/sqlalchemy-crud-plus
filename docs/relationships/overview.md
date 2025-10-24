# 关系查询

SQLAlchemy CRUD Plus 提供强大的关系查询功能，支持 ORM 关系预加载和动态 JOIN 查询。

## 核心参数

- **load_strategies** - 关系数据预加载策略（需要 ORM relationship）
- **join_conditions** - JOIN 条件控制（支持有无 relationship）
- **load_options** - 原生 SQLAlchemy 选项

## 两种关联方式

### 方式一：ORM 关系（有 relationship）

使用 SQLAlchemy 的 `relationship` 定义关系，适合标准的外键关联。

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    posts: Mapped[list['Post']] = relationship(back_populates='author')


class Post(Base):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    author: Mapped['User'] = relationship(back_populates='posts')
```

**查询示例**：

```python
# 预加载关系数据
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies=['posts', 'profile']
)
print(user.posts)  # 直接访问关系

# JOIN 查询（用于过滤）
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],  # 只查询有文章的用户
    is_active=True
)
```

### 方式二：纯逻辑关联（无 relationship）

不定义 `relationship`，在查询时通过 `JoinConfig` 动态关联。适合无外键约束的场景。

```python
class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String(100), index=True)


class Post(Base):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_email: Mapped[str] = mapped_column(String(100), index=True)
```

**查询示例**：

```python
from sqlalchemy_crud_plus import JoinConfig

# 使用 JoinConfig 动态关联
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=User.email == Post.author_email,
            join_type='inner'
        )
    ]
)
```

## join_conditions 参数详解

`join_conditions` 用于关联查询多表数据，支持三种格式。

### 格式一：列表格式（有 relationship）

```python
# 使用关系名称
users = await user_crud.select_models(
    session,
    join_conditions=['posts', 'profile']
)
```

### 格式二：字典格式（有 relationship）

```python
# 指定 JOIN 类型
users = await user_crud.select_models(
    session,
    join_conditions={
        'posts': 'inner',  # INNER JOIN
        'profile': 'left'  # LEFT JOIN
    }
)
```

### 格式三：JoinConfig（无 relationship 或复杂条件）

这是最灵活的方式，支持自定义 JOIN 条件。

#### 基础用法

```python
from sqlalchemy_crud_plus import JoinConfig

# 简单关联
result = await user_crud.select_models(
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

#### join_on 参数说明

**join_on** 定义表之间的关联条件，支持：

**1. 简单等值条件**

```python
JoinConfig(
    model=Post,
    join_on=User.id == Post.author_id,
    join_type='left'
)
```

**2. 复合条件**

```python
from sqlalchemy import and_, or_

JoinConfig(
    model=Post,
    join_on=and_(
        User.id == Post.author_id,
        Post.is_published == True,
        Post.created_at >= datetime(2024, 1, 1)
    ),
    join_type='inner'
)
```

**3. 多种条件组合**

```python
JoinConfig(
    model=Post,
    join_on=and_(
        User.id == Post.author_id,
        or_(
            Post.status == 'published',
            Post.status == 'featured'
        ),
        Post.view_count > 100
    ),
    join_type='left'
)
```

**4. 使用函数**

```python
from sqlalchemy import func

JoinConfig(
    model=Post,
    join_on=and_(
        User.id == Post.author_id,
        func.date(Post.created_at) == func.current_date()
    ),
    join_type='inner'
)
```

**5. 非主键关联**

```python
# 通过 email 关联
JoinConfig(
    model=Profile,
    join_on=User.email == Profile.user_email,
    join_type='left'
)

# 通过业务编号关联
JoinConfig(
    model=Order,
    join_on=Customer.customer_code == Order.customer_code,
    join_type='inner'
)
```

**6. 范围条件**

```python
# 查询符合折扣区间的订单
JoinConfig(
    model=Discount,
    join_on=and_(
        Order.total_amount >= Discount.min_amount,
        Order.total_amount <= Discount.max_amount,
        Discount.is_active == True
    ),
    join_type='left'
)
```

#### 多表关联

```python
# 关联多个表
posts = await post_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=User,
            join_on=Post.author_id == User.id,
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

#### 获取关联表数据

**重要**：使用 `join_conditions` 的目的是获取多个表的数据，而不只是主表数据。

```python
from sqlalchemy import select

# 方式1：使用原生 select 获取多表数据
stmt = select(User, Post).join(
    Post, User.id == Post.author_id
)
result = await session.execute(stmt)
for user, post in result.all():
    print(f"{user.name}: {post.title}")

# 方式2：使用 JoinConfig 过滤 + 原生查询获取数据
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
# users 只包含主表数据，需要再次查询获取关联数据

# 方式3：构建字典结果（推荐用于 API 返回）
stmt = select(User.name, User.email, Post.title, Post.created_at).join(
    Post, User.id == Post.author_id
)
result = await session.execute(stmt)
data = [
    {
        'user_name': row.name,
        'user_email': row.email,
        'post_title': row.title,
        'post_created': row.created_at
    }
    for row in result.all()
]
```

#### 实际应用示例

```python
# 查询用户和文章数据
async def get_users_with_posts(session: AsyncSession):
    stmt = select(User, Post).join(
        Post,
        User.id == Post.author_id,
        isouter=True
    ).where(User.is_active == True)

    result = await session.execute(stmt)
    rows = result.all()

    # 组织数据
    user_posts = {}
    for user, post in rows:
        if user.id not in user_posts:
            user_posts[user.id] = {
                'user': user,
                'posts': []
            }
        if post:
            user_posts[user.id]['posts'].append(post)

    return list(user_posts.values())


# 查询多表数据用于 API
async def get_post_list_api(session: AsyncSession, page: int = 1):
    stmt = (
        select(
            Post.id,
            Post.title,
            Post.created_at,
            User.name.label('author_name'),
            Category.name.label('category_name')
        )
        .join(User, Post.author_id == User.id)
        .join(Category, Post.category_id == Category.id, isouter=True)
        .where(Post.is_published == True)
        .limit(20)
        .offset((page - 1) * 20)
    )

    result = await session.execute(stmt)
    return [
        {
            'id': row.id,
            'title': row.title,
            'created_at': row.created_at,
            'author': row.author_name,
            'category': row.category_name
        }
        for row in result.all()
    ]
```

### JOIN 类型说明

| 类型      | 说明              | 使用场景           |
|---------|-----------------|----------------|
| `inner` | INNER JOIN      | 只返回两表都匹配的记录    |
| `left`  | LEFT JOIN       | 返回左表所有记录，右表可为空 |
| `right` | RIGHT JOIN      | 返回右表所有记录，左表可为空 |
| `outer` | FULL OUTER JOIN | 返回两表所有记录       |

## load_strategies 参数

**仅用于有 relationship 的模型**，预加载关系数据以避免 N+1 查询。

### 列表格式（使用默认策略）

```python
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies=['posts', 'profile']
)
```

### 字典格式（指定策略）

```python
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies={
        'posts': 'selectinload',  # 一对多
        'profile': 'joinedload',  # 一对一
        'roles': 'subqueryload'  # 多对多
    }
)
```

### 策略选择

| 策略           | 适用关系 | 特点                  |
|--------------|------|---------------------|
| selectinload | 一对多  | SELECT IN 查询，避免笛卡尔积 |
| joinedload   | 一对一  | LEFT JOIN，单次查询      |
| subqueryload | 多对多  | 子查询，适合复杂关系          |

### 避免 N+1 查询

```python
# 错误：N+1 查询
users = await user_crud.select_models(session, limit=10)
for user in users:
    print(len(user.posts))  # 每次都触发查询

# 正确：预加载
users = await user_crud.select_models(
    session,
    load_strategies=['posts'],
    limit=10
)
for user in users:
    print(len(user.posts))  # 无额外查询
```

## 组合使用

### JOIN 过滤 + 预加载数据

```python
# 查询有文章的用户，并预加载其数据
users = await user_crud.select_models(
    session,
    join_conditions=['posts'],  # 过滤：只要有文章的用户
    load_strategies=['posts', 'profile'],  # 预加载数据
    is_active=True
)
```

### 复杂组合

```python
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
    load_strategies={
        'posts': 'selectinload',
        'profile': 'joinedload'
    },
    is_active=True,
    name__like='%admin%',
    limit=20
)
```

## 实际应用示例

### 用户详情页面

```python
async def get_user_detail(session: AsyncSession, user_id: int):
    return await user_crud.select_model(
        session,
        pk=user_id,
        load_strategies={
            'posts': 'selectinload',
            'profile': 'joinedload',
            'roles': 'selectinload'
        }
    )
```

### 文章列表（多表数据）

```python
async def get_posts_with_details(session: AsyncSession):
    stmt = (
        select(Post, User, Category)
        .join(User, Post.author_id == User.id)
        .join(Category, Post.category_id == Category.id, isouter=True)
        .where(Post.is_published == True)
    )

    result = await session.execute(stmt)
    return [
        {
            'post': post,
            'author': user,
            'category': category
        }
        for post, user, category in result.all()
    ]
```

### 统计查询

```python
async def get_active_authors(session: AsyncSession):
    # 查询有已发布文章的作者
    authors = await user_crud.select_models(
        session,
        join_conditions=[
            JoinConfig(
                model=Post,
                join_on=and_(
                    User.id == Post.author_id,
                    Post.is_published == True
                ),
                join_type='inner'
            )
        ],
        is_active=True
    )
    return authors
```

## 性能优化

### 索引优化

```python
# 为关联字段添加索引
class Post(Base):
    __tablename__ = 'post'
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(index=True)  # 添加索引
    author_email: Mapped[str] = mapped_column(String(100), index=True)  # 添加索引
```

### 选择合适的 JOIN 类型

```python
# INNER JOIN - 只要匹配的
users = await user_crud.select_models(
    session,
    join_conditions={'posts': 'inner'}  # 只返回有文章的用户
)

# LEFT JOIN - 保留主表所有记录
users = await user_crud.select_models(
    session,
    join_conditions={'posts': 'left'}  # 返回所有用户，包括没文章的
)
```

### 监控查询

```python
# 开启 SQL 日志
engine = create_async_engine(DATABASE_URL, echo=True)

# 查看生成的 SQL
users = await user_crud.select_models(
    session,
    load_strategies=['posts']
)
```

## 最佳实践

1. **根据场景选择方式**
    - 有外键 + 标准关系 → 使用 `load_strategies`
    - 无外键或复杂条件 → 使用 `JoinConfig`

2. **关联查询获取多表数据**
    - 使用原生 `select(Model1, Model2).join()` 获取多表数据
    - 构建字典结果用于 API 返回
    - `JoinConfig` 主要用于过滤，不直接返回关联表数据

3. **性能优化**
    - 为关联字段添加索引
    - 预加载避免 N+1 查询
    - 合理选择 JOIN 类型

4. **字段命名**
    - 主键关联：`user_id`（整数）
    - 业务字段关联：`user_email`、`customer_code`（语义化）

5. **错误处理**
    - 检查关联字段是否有索引
    - 验证 JOIN 条件的正确性
    - 处理关联数据为空的情况

## load_options 参数

使用原生 SQLAlchemy 选项进行精确控制：

```python
from sqlalchemy.orm import selectinload, joinedload

# 嵌套关系
user = await user_crud.select_model(
    session,
    pk=1,
    load_options=[
        selectinload(User.posts).selectinload(Post.comments)
    ]
)
```

## 常见问题

### 如何获取关联表的数据？

```python
# 方法1：原生 select（推荐）
stmt = select(User, Post).join(Post, User.id == Post.author_id)
result = await session.execute(stmt)
for user, post in result.all():
    print(user, post)

# 方法2：使用 relationship + load_strategies
user = await user_crud.select_model(
    session,
    pk=1,
    load_strategies=['posts']
)
for post in user.posts:
    print(post)
```

### JoinConfig 返回什么数据？

`JoinConfig` 用于过滤和关联，但 `select_models` 只返回主表数据。要获取关联表数据，需使用原生 `select()`。

```python
# 这只返回 User 数据
users = await user_crud.select_models(
    session,
    join_conditions=[JoinConfig(model=Post, join_on=...)]
)

# 要获取 User 和 Post，使用原生查询
stmt = select(User, Post).join(...)
result = await session.execute(stmt)
```

### 何时使用哪种方式？

| 场景                 | 推荐方式                         |
|--------------------|------------------------------|
| 有外键 + relationship | `load_strategies`            |
| 无外键或复杂条件           | `JoinConfig` + 原生 `select()` |
| 需要多表数据             | 原生 `select(Model1, Model2)`  |
| API 返回             | 原生 `select()` + 构建字典         |

## 相关资源

- [过滤条件](../advanced/filter.md) - 高级过滤技术
- [事务控制](../advanced/transaction.md) - 事务管理
- [API 参考](../api/crud-plus.md) - 完整 API 文档
