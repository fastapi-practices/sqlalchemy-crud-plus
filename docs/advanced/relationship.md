# 关系查询

SQLAlchemy CRUD Plus 提供强大的关系查询功能，支持 ORM 关系预加载和动态 JOIN 查询。

## 核心参数

- **load_strategies** - 关系数据预加载策略（需要 ORM relationship）
- **join_conditions** - JOIN 条件控制（支持有无 relationship）
- **load_options** - 原生 SQLAlchemy 选项

## ORM 关系（有 relationship）

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

## 纯逻辑关联（无 relationship）

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

## join_conditions

`join_conditions` 用于关联查询多表数据，支持三种格式

### 列表格式（有 relationship）

```python
# 使用关系名称
users = await user_crud.select_models(
    session,
    join_conditions=['posts', 'profile']
)
```

### 字典格式（有 relationship）

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

### JoinConfig（无 relationship 或复杂条件）

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

#### join_on 参数

**join_on** 定义表之间的关联条件，支持：

1. 简单等值条件
   ```python
   JoinConfig(
       model=Post,
       join_on=User.id == Post.author_id,
       join_type='left'
   )
   ```

2. 复合条件
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

3. 多种条件组合
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

4. 使用函数
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

5. 非主键关联
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

6. 范围条件
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

#### fill_result 参数

当设置 `fill_result=True` 时，查询结果会包含关联表的数据。

```python
# 基础用法
results = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=User.id == Post.author_id,
            join_type='left',
            fill_result=True  # 包含关联表数据
        )
    ]
)

# 当 fill_result=True 时，results 是 Row 对象（行为类似元组）
for result in results:
    user, post = result  # (User, Post)
    print(f"{user.name}: {post.title if post else 'No post'}")
```

**多表关联**：

```python
# 关联多个表，都包含在结果中
results = await post_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=User,
            join_on=Post.author_id == User.id,
            join_type='inner',
            fill_result=True
        ),
        JoinConfig(
            model=Category,
            join_on=Post.category_id == Category.id,
            join_type='left',
            fill_result=True
        )
    ]
)

# 结果是三元组 (Post, User, Category) - Row 对象
for post, user, category in results:
    print(f"{post.title} by {user.name} in {category.name if category else 'Uncategorized'}")
```

**fill_result 默认行为**：

```python
# fill_result=False (默认) - 只返回主表数据
users = await user_crud.select_models(
    session,
    join_conditions=[
        JoinConfig(
            model=Post,
            join_on=User.id == Post.author_id,
            join_type='left',
            fill_result=False  # 默认值
        )
    ]
)
# users 只包含 User 实例
```

**选择正确的使用方式**：

- **只需要主表数据**：使用 `fill_result=False` (默认)
- **需要关联表数据**：使用 `fill_result=True`
- **复杂查询/自定义字段**：使用原生 `select()`

### JOIN 类型说明

| 类型      | 说明              | 使用场景           |
|---------|-----------------|----------------|
| `inner` | INNER JOIN      | 只返回两表都匹配的记录    |
| `left`  | LEFT JOIN       | 返回左表所有记录，右表可为空 |
| `outer` | FULL OUTER JOIN | 返回两表所有记录       |

## load_strategies

!!! note

    仅用于有 relationship 的模型，预加载关系数据以避免 N+1 查询

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
        'posts': 'selectinload',
        'profile': 'joinedload',
        'roles': 'subqueryload'
    }
)
```

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

## load_options

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

## 相关资源

- [过滤条件](filter.md) - 高级过滤技术
- [事务控制](transaction.md) - 事务管理
- [API 参考](../api/crud-plus.md) - 完整 API 文档
