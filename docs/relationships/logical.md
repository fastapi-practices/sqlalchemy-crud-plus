# 纯逻辑关联查询

本文档介绍如何在**不使用外键约束和不定义 ORM relationship** 的情况下进行关联查询。这是中国市场最常见的数据库设计实践。

## 镜像对比设计

本文档中的示例与 [关系查询概览](overview.md) 使用**相同的业务场景**，但技术实现不同：

| 特性 | 关系查询（overview.md） | 纯逻辑关联（本文档） |
|------|---------------------|------------------|
| 模型命名 | `RelUser`, `RelPost` | `NoRelUser`, `NoRelPost` |
| 外键约束 | ✅ 有 `ForeignKey` | ❌ 无外键 |
| ORM关系 | ✅ 有 `relationship` | ❌ 无 relationship |
| 关联字段 | `author_id` (整数) | `author_email` (字符串) |
| 查询方式 | `user.posts` (自动) | 显式 JOIN |

**目的**：通过对比同一业务场景的两种实现，让开发者理解：
- 标准 ORM 方式（有外键 + relationship）
- 纯逻辑关联方式（无外键 + 无 relationship）

## 适用场景

- 🏢 数据库不允许物理外键约束（公司规范）
- 🔄 表之间完全解耦，不定义 ORM relationship
- 🇨🇳 中国市场的传统数据库设计规范
- 🔗 需要在查询时动态关联多个表
- 📧 通过业务字段（如 email、code）进行逻辑关联
- 🏗️ 遗留系统改造，无法添加外键约束

## 核心概念

### 什么是纯逻辑关联？

**纯逻辑关联**是指：
- ❌ 数据库层面：没有外键约束（`FOREIGN KEY`）
- ❌ ORM 层面：不定义 `relationship`
- ✅ 查询时：通过业务字段动态 JOIN

```python
# 标准 ORM 方式（有外键和 relationship）- 对应 RelUser, RelPost
class RelUser(Base):
    __tablename__ = 'rel_user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    posts: Mapped[list['RelPost']] = relationship()  # ✅ 定义了 relationship

class RelPost(Base):
    __tablename__ = 'rel_post'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey('rel_user.id'))  # ✅ 有外键


# 纯逻辑关联方式（无外键、无 relationship）- 对应 NoRelUser, NoRelPost
class NoRelUser(Base):
    __tablename__ = 'norel_user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String(100), index=True)
    # ❌ 没有定义任何 relationship

class NoRelPost(Base):
    __tablename__ = 'norel_post'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_email: Mapped[str] = mapped_column(String(100), index=True)  # ❌ 无外键约束
    # ❌ 没有定义任何 relationship
```

**关键区别**：
- 标准方式：`author_id` (整数) → 引用 `User.id` → 有外键
- 逻辑方式：`author_email` (字符串) → 引用 `User.email` → 无外键

## 字段命名规范

### 为什么不用 `xxx_id`？

在纯逻辑关联中，关联字段的命名应该**明确表达字段的实际含义**：

| 场景 | 推荐命名 | 不推荐 | 原因 |
|------|---------|--------|------|
| 通过 email 关联 | `user_email` | `user_id` | email 是字符串，用 `_id` 会误导为整数 |
| 通过业务代码关联 | `category_code` | `category_id` | 明确表示这是业务代码 |
| 通过手机号关联 | `user_phone` | `user_id` | 清晰表达关联字段类型 |

### 什么时候用 `xxx_id`？

✅ **适合使用 `xxx_id` 的情况**：

```python
# 场景1：引用业务编号（即使不是主键）
class Customer(Base):
    id: Mapped[int] = mapped_column(primary_key=True)  # 数据库主键
    customer_id: Mapped[str] = mapped_column(String(20), unique=True)  # 业务编号

class Contract(Base):
    customer_id: Mapped[str]  # ✅ 引用业务编号，使用 customer_id

# 场景2：引用数据库主键（即使没有外键约束）
class Order(Base):
    user_id: Mapped[int]  # ✅ 逻辑关联到 User.id（整数）
```

❌ **不适合使用 `xxx_id` 的情况**：

```python
# 通过非 ID 字段关联
class UserStats(Base):
    user_email: Mapped[str]  # ✅ 清晰
    # user_id: Mapped[str]   # ❌ 误导（看起来应该是整数）

class Product(Base):
    category_code: Mapped[str]  # ✅ 语义明确
    # category_id: Mapped[str]   # ❌ 混淆（code 和 id 的区别）
```

### 命名最佳实践

1. **字段名应反映实际内容**：`user_email` > `user_id`（当存储 email 时）
2. **保持一致性**：项目内统一命名风格
3. **添加注释**：说明关联逻辑
4. **总是加索引**：逻辑关联字段必须有索引

## 场景一：用户和个人资料（一对一）

这是最常见的场景，镜像 `RelUser` 和 `RelProfile` 的业务逻辑。

### 模型对比

```python
# 标准 ORM 方式（overview.md）
class RelUser(Base):
    __tablename__ = 'rel_user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    profile: Mapped['RelProfile'] = relationship(back_populates='user')

class RelProfile(Base):
    __tablename__ = 'rel_profile'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('rel_user.id'))  # 外键
    bio: Mapped[str]
    user: Mapped['RelUser'] = relationship(back_populates='profile')


# 纯逻辑关联方式（本文档）
class NoRelUser(Base):
    __tablename__ = 'norel_user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    # 无 relationship 定义

class NoRelProfile(Base):
    __tablename__ = 'norel_profile'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str] = mapped_column(String(100), index=True)  # 无外键
    bio: Mapped[str]
    # 无 relationship 定义
```

**关键差异**：
- 标准方式：通过 `user_id` (整数) 关联，有外键约束
- 逻辑方式：通过 `user_email` (字符串) 关联，无外键约束

### 查询方式

#### 方式 1：原生 SQLAlchemy 查询（推荐）

```python
from sqlalchemy import select

async def get_users_with_profiles(session: AsyncSession):
    """查询用户及其个人资料"""
    stmt = select(NoRelUser, NoRelProfile).join(
        NoRelProfile,
        NoRelUser.email == NoRelProfile.user_email,  # 动态 JOIN 条件
        isouter=True  # LEFT JOIN，保留没有资料的用户
    )
    
    result = await session.execute(stmt)
    rows = result.all()
    
    # 处理结果
    for user, profile in rows:
        print(f"用户: {user.name}")
        if profile:
            print(f"  简介: {profile.bio}")
```

**对比标准方式**：
```python
# 标准 ORM 方式 - 自动通过 relationship
user = await session.get(RelUser, 1, options=[selectinload(RelUser.profile)])
print(user.profile.bio)  # 直接访问

# 纯逻辑关联 - 需要显式 JOIN
stmt = select(NoRelUser, NoRelProfile).join(...)
result = await session.execute(stmt)
user, profile = result.first()
print(profile.bio)  # 需要手动处理
```

#### 方式 2：使用 JoinConfig 过滤

```python
from sqlalchemy_crud_plus import CRUDPlus, JoinConfig

user_crud = CRUDPlus(NoRelUser)

async def get_users_with_profiles(session: AsyncSession):
    """查询有个人资料的用户（用于过滤）"""
    users = await user_crud.select_models(
        session,
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.email == NoRelProfile.user_email,
                join_type='inner',  # INNER JOIN，只返回有资料的用户
            )
        ],
    )
    
    # 注意：这里只返回 User 对象，不包含 profile 数据
    return users
```

**重要**：`JoinConfig` 主要用于**过滤**，不返回关联表数据！

#### 方式 3：返回字典格式（实用）

```python
async def get_user_list_api(session: AsyncSession):
    """API 接口：返回用户列表（含资料）"""
    stmt = select(NoRelUser, NoRelProfile).join(
        NoRelProfile,
        NoRelUser.email == NoRelProfile.user_email,
        isouter=True,
    )
    
    result = await session.execute(stmt)
    rows = result.all()
    
    # 转换为 API 响应格式
    return [
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'bio': profile.bio if profile else None,
        }
        for user, profile in rows
    ]
```

## 场景二：用户和帖子（一对多）

镜像 `RelUser` 和 `RelPost` 的一对多关系。

### 模型对比

```python
# 标准 ORM 方式
class RelUser(Base):
    __tablename__ = 'rel_user'
    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[list['RelPost']] = relationship(back_populates='author')

class RelPost(Base):
    __tablename__ = 'rel_post'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey('rel_user.id'))
    author: Mapped['RelUser'] = relationship(back_populates='posts')


# 纯逻辑关联方式
class NoRelUser(Base):
    __tablename__ = 'norel_user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    # 无 posts relationship

class NoRelPost(Base):
    __tablename__ = 'norel_post'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_email: Mapped[str] = mapped_column(String(100), index=True)  # 无外键
    # 无 author relationship
```

### 查询示例

```python
async def get_users_with_posts(session: AsyncSession):
    """查询用户及其帖子"""
    stmt = select(NoRelUser, NoRelPost).join(
        NoRelPost,
        NoRelUser.email == NoRelPost.author_email,  # 通过 email JOIN
    )
    
    result = await session.execute(stmt)
    
    return [
        {
            'user_name': user.name,
            'post_title': post.title,
        }
        for user, post in result.all()
    ]
```

**对比标准方式**：
```python
# 标准方式 - 自动预加载
user = await session.get(RelUser, 1, options=[selectinload(RelUser.posts)])
for post in user.posts:  # 直接访问列表
    print(post.title)

# 逻辑方式 - 显式 JOIN
stmt = select(NoRelUser, NoRelPost).join(...)
for user, post in result.all():  # 手动遍历
    print(post.title)
```

## 场景三：多表关联

帖子关联作者和类别（多表 JOIN）。

```python
async def get_posts_with_details(session: AsyncSession):
    """查询帖子及作者、类别信息"""
    stmt = (
        select(NoRelPost, NoRelUser, NoRelCategory)
        .join(NoRelUser, NoRelPost.author_email == NoRelUser.email)
        .join(NoRelCategory, NoRelPost.category_code == NoRelCategory.code, isouter=True)
        .where(NoRelPost.title.like('%tutorial%'))
    )
    
    result = await session.execute(stmt)
    
    post_list = []
    for post, user, category in result.all():
        post_list.append({
            'title': post.title,
            'author_name': user.name,
            'category_name': category.name if category else 'Uncategorized',
        })
    
    return post_list
```

**对比标准方式**：
```python
# 标准方式 - 使用 relationship
posts = await session.execute(
    select(RelPost).options(
        selectinload(RelPost.author),
        selectinload(RelPost.category)
    )
)
for post in posts.scalars():
    print(post.author.name, post.category.name)

# 逻辑方式 - 显式多表 JOIN
stmt = select(NoRelPost, NoRelUser, NoRelCategory).join(...).join(...)
for post, user, category in result.all():
    print(user.name, category.name)
```

## 场景四：业务编号关联

通过业务编号（非数据库主键）进行关联，这种情况下使用 `xxx_id` 是合适的。

### 模型定义

```python
class Customer(Base):
    """客户表 - 使用业务编号"""
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)  # 数据库主键
    customer_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # 业务编号
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))

class Contract(Base):
    """合同表 - 通过 customer_id（业务编号）逻辑关联"""
    __tablename__ = 'contracts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    contract_number: Mapped[str] = mapped_column(String(50), unique=True)
    customer_id: Mapped[str] = mapped_column(String(20), index=True)  # 引用业务编号
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20))
```

### 查询示例

```python
async def get_contracts_with_customer(session: AsyncSession):
    """查询合同及客户信息"""
    stmt = select(Contract, Customer).join(
        Customer,
        Contract.customer_id == Customer.customer_id,  # 通过业务编号关联
    ).where(
        Contract.status == 'active'
    )
    
    result = await session.execute(stmt)
    
    return [
        {
            'contract_number': contract.contract_number,
            'amount': float(contract.amount),
            'customer_id': customer.customer_id,  # 业务编号
            'customer_name': customer.name,
            'customer_email': customer.email,
        }
        for contract, customer in result.all()
    ]
```

**说明**：这个场景中使用 `customer_id` 是合适的，因为：
- 它引用的是客户的**业务编号**（虽然不是数据库主键）
- 在业务逻辑中，`customer_id` 就是客户的唯一标识
- 与 `user_email`、`category_code` 等不同，这里的 `_id` 后缀有明确的业务含义

## 使用 JoinConfig 的场景

`JoinConfig` 主要用于**过滤条件**，而非返回关联数据。

### 何时使用 JoinConfig？

✅ **适合场景**：
- 需要根据关联表的条件过滤主表
- 统计符合条件的记录数
- 检查是否存在满足条件的记录

❌ **不适合场景**：
- 需要返回关联表的数据（应使用原生查询）
- 需要嵌套加载多层关系

### 示例：过滤和统计

```python
from sqlalchemy_crud_plus import CRUDPlus, JoinConfig

user_crud = CRUDPlus(User)

# 统计有统计数据的活跃用户数量
count = await user_crud.count(
    session,
    join_conditions=[
        JoinConfig(
            model=UserStats,
            join_on=User.email == UserStats.user_email,
            join_type='inner',
        )
    ],
    is_active=True,
)

# 检查是否存在登录次数超过 100 的用户
exists = await user_crud.exists(
    session,
    join_conditions=[
        JoinConfig(
            model=UserStats,
            join_on=User.email == UserStats.user_email,
            join_type='inner',
        )
    ],
    **{'UserStats.login_count__gt': 100}  # 关联表条件
)
```

## 实际业务示例

### 用户列表页面

```python
async def get_user_list_for_admin(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """管理后台：用户列表（含统计信息）"""
    offset = (page - 1) * page_size
    
    # 查询用户和统计
    stmt = (
        select(User, UserStats)
        .join(UserStats, User.email == UserStats.user_email, isouter=True)
        .where(User.is_active == True)
        .order_by(User.created_at.desc())
        .limit(page_size)
        .offset(offset)
    )
    
    result = await session.execute(stmt)
    rows = result.all()
    
    # 统计总数
    count_stmt = select(func.count(User.id)).where(User.is_active == True)
    total = await session.scalar(count_stmt)
    
    # 组装数据
    items = [
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'login_count': stats.login_count if stats else 0,
            'last_login': stats.last_login.isoformat() if stats and stats.last_login else None,
        }
        for user, stats in rows
    ]
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'pages': (total + page_size - 1) // page_size,
    }
```

### 订单详情页面

```python
async def get_order_detail(session: AsyncSession, order_id: int) -> dict:
    """订单详情（含客户信息）"""
    stmt = (
        select(Order, User)
        .join(User, Order.customer_email == User.email)
        .where(Order.id == order_id)
    )
    
    result = await session.execute(stmt)
    row = result.first()
    
    if not row:
        return None
    
    order, user = row
    
    return {
        'order': {
            'id': order.id,
            'order_number': order.order_number,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'created_at': order.created_at.isoformat(),
        },
        'customer': {
            'name': user.name,
            'email': user.email,
            'is_active': user.is_active,
        }
    }
```

## 性能优化建议

### 1. 添加索引

**务必**在逻辑关联字段上添加索引：

```python
class UserStats(Base):
    __tablename__ = 'user_stats'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str] = mapped_column(String(100), index=True)  # ✅ 添加索引
```

### 2. 选择合适的 JOIN 类型

```python
# INNER JOIN - 只返回两边都有数据的记录
stmt = select(User, UserStats).join(
    UserStats,
    User.email == UserStats.user_email,
    isouter=False  # INNER JOIN
)

# LEFT JOIN - 保留左表所有记录
stmt = select(User, UserStats).join(
    UserStats,
    User.email == UserStats.user_email,
    isouter=True  # LEFT JOIN
)
```

### 3. 避免 N+1 查询

```python
# ❌ 错误：N+1 查询
users = await user_crud.select_models(session, limit=10)
for user in users:
    # 每次都触发新查询
    stats = await session.execute(
        select(UserStats).where(UserStats.user_email == user.email)
    )

# ✅ 正确：一次 JOIN 查询
stmt = select(User, UserStats).join(
    UserStats, User.email == UserStats.user_email, isouter=True
).limit(10)
rows = await session.execute(stmt)
```

## 对比总结

| 特性 | 标准 ORM (RelXxx) | 纯逻辑关联 (NoRelXxx) |
|------|------------------|---------------------|
| 模型示例 | `RelUser`, `RelPost` | `NoRelUser`, `NoRelPost` |
| 数据库约束 | ✅ 有外键约束 | ❌ 无约束 |
| ORM 定义 | ✅ 定义 relationship | ❌ 无 relationship |
| 关联字段 | `author_id` (整数) | `author_email` (字符串) |
| 数据一致性 | 数据库保证 | 应用层保证 |
| 关联查询 | `user.posts` 自动 | 显式 JOIN |
| 学习曲线 | 较陡（需理解 ORM） | 较平（SQL JOIN） |
| 灵活性 | 较低 | 高 |
| 维护成本 | 低（自动维护） | 中（手动维护） |
| 适用场景 | 标准项目、新项目 | 中国市场、遗留系统 |

**选择建议**：
- 新项目、有控制权 → 使用标准 ORM 方式（RelXxx）
- 公司规范、遗留系统 → 使用纯逻辑关联（NoRelXxx）
- 两种方式可以在同一项目中混用（不同模块不同策略）

## 最佳实践

1. **总是添加索引**：在逻辑关联字段上添加索引
2. **使用原生查询返回关联数据**：不要依赖 CRUDPlus 返回关联表
3. **明确 JOIN 类型**：根据业务需求选择 INNER/LEFT JOIN
4. **封装通用查询**：将常用的关联查询封装成函数
5. **考虑数据一致性**：在应用层保证数据完整性

## 相关资源

- [关系查询概览](overview.md) - 标准 ORM 方式（RelXxx 模型）
- [测试对比](../../tests/test_non_fk_relationships.py) - 查看完整测试用例
- [模型定义](../../tests/models/non_fk_relations.py) - NoRelXxx 模型源码
- [命名规范指南](../../NAMING_CONVENTION.md) - 字段命名最佳实践
- [API 参考](../api/crud-plus.md) - CRUDPlus 完整 API

**学习路径**：
1. 先学习 [关系查询概览](overview.md) - 理解标准 ORM 方式
2. 再学习本文档 - 理解纯逻辑关联的差异
3. 对比两个测试文件 - 看同一场景的不同实现
