# 关系查询示例

本页面展示 SQLAlchemy CRUD Plus 的关系查询功能，包括预加载、JOIN 操作和性能优化。

## 模型关系定义

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# 多对多关系表
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

    # 一对一关系
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    
    # 一对多关系
    posts = relationship("Post", back_populates="author")
    
    # 多对多关系
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    bio = Column(String(500))
    avatar_url = Column(String(200))

    user = relationship("User", back_populates="profile")

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    content = Column(String(1000))
    author_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))

    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    posts = relationship("Post", back_populates="category")

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    content = Column(String(500))
    post_id = Column(Integer, ForeignKey('posts.id'))

    post = relationship("Post", back_populates="comments")

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    users = relationship("User", secondary=user_roles, back_populates="roles")
```

## 基础关系查询

### 简单预加载

```python
async def basic_relationship_loading():
    async with _async_db_session() as session:
        # 预加载用户的个人资料
        user = await user_crud.select_model(
            session, 1,
            load_strategies=['profile']
        )
        
        # 预加载用户的文章
        user = await user_crud.select_model(
            session, 1,
            load_strategies=['posts']
        )
        
        # 预加载多个关系
        user = await user_crud.select_model(
            session, 1,
            load_strategies=['profile', 'posts', 'roles']
        )
        
        return user
```

### 指定加载策略

```python
async def specific_loading_strategies():
    async with _async_db_session() as session:
        # 为不同关系指定不同的加载策略
        user = await user_crud.select_model(
            session, 1,
            load_strategies={
                'profile': 'joinedload',      # 一对一用 joinedload
                'posts': 'selectinload',      # 一对多用 selectinload
                'roles': 'subqueryload'       # 多对多用 subqueryload
            }
        )
        
        return user
```

## 嵌套关系查询

### 多层关系预加载

```python
async def nested_relationship_loading():
    async with _async_db_session() as session:
        # 预加载用户 -> 文章 -> 分类
        users = await user_crud.select_models(
            session,
            load_strategies={
                'posts': 'selectinload',
                'posts.category': 'joinedload'
            }
        )
        
        # 预加载用户 -> 文章 -> 评论
        users = await user_crud.select_models(
            session,
            load_strategies={
                'posts': 'selectinload',
                'posts.comments': 'selectinload'
            }
        )
        
        return users
```

### 复杂嵌套查询

```python
async def complex_nested_loading():
    async with _async_db_session() as session:
        # 预加载所有相关数据
        user = await user_crud.select_model(
            session, 1,
            load_strategies={
                'profile': 'joinedload',
                'posts': 'selectinload',
                'posts.category': 'joinedload',
                'posts.comments': 'selectinload',
                'roles': 'selectinload'
            }
        )
        
        return user
```

## JOIN 查询

### 基础 JOIN

```python
async def basic_join_queries():
    async with _async_db_session() as session:
        # 只返回有个人资料的用户
        users = await user_crud.select_models(
            session,
            join_conditions=['profile']
        )
        
        # 只返回有文章的用户
        users = await user_crud.select_models(
            session,
            join_conditions=['posts']
        )
        
        return users
```

### 指定 JOIN 类型

```python
async def specific_join_types():
    async with _async_db_session() as session:
        # 混合 JOIN 类型
        users = await user_crud.select_models(
            session,
            join_conditions={
                'posts': 'inner',      # 必须有文章
                'profile': 'left',     # 可能有个人资料
                'roles': 'left'        # 可能有角色
            }
        )
        
        return users
```

### JOIN 与预加载结合

```python
async def join_with_loading():
    async with _async_db_session() as session:
        # JOIN 用于过滤，预加载用于获取数据
        users = await user_crud.select_models(
            session,
            join_conditions=['posts'],           # 只要有文章的用户
            load_strategies=['posts', 'profile'] # 预加载文章和个人资料
        )
        
        return users
```

## 性能优化示例

### 避免 N+1 查询

```python
async def avoid_n_plus_1():
    async with _async_db_session() as session:
        # ❌ 错误：会产生 N+1 查询
        users = await user_crud.select_models(session, limit=10)
        for user in users:
            print(f"用户 {user.name} 有 {len(user.posts)} 篇文章")  # 每次都查询
        
        # ✅ 正确：预加载避免 N+1 查询
        users = await user_crud.select_models(
            session,
            load_strategies=['posts'],
            limit=10
        )
        for user in users:
            print(f"用户 {user.name} 有 {len(user.posts)} 篇文章")  # 无额外查询
```

### 选择合适的加载策略

```python
async def optimal_loading_strategies():
    async with _async_db_session() as session:
        # 一对一关系：使用 joinedload
        user = await user_crud.select_model(
            session, 1,
            load_strategies={'profile': 'joinedload'}
        )
        
        # 一对多关系：使用 selectinload
        user = await user_crud.select_model(
            session, 1,
            load_strategies={'posts': 'selectinload'}
        )
        
        # 多对多关系：使用 selectinload 或 subqueryload
        user = await user_crud.select_model(
            session, 1,
            load_strategies={'roles': 'selectinload'}
        )
        
        return user
```

## 计数和存在检查

### 关系计数

```python
async def relationship_counting():
    async with _async_db_session() as session:
        # 计算有文章的用户数量
        count = await user_crud.count(
            session,
            join_conditions=['posts']
        )
        
        # 计算有特定角色的用户数量
        count = await user_crud.count(
            session,
            join_conditions=['roles'],
            roles__name='admin'
        )
        
        return count
```

### 关系存在检查

```python
async def relationship_existence():
    async with _async_db_session() as session:
        # 检查是否有用户发布了文章
        has_posts = await user_crud.exists(
            session,
            join_conditions=['posts']
        )
        
        # 检查特定用户是否有特定角色
        is_admin = await user_crud.exists(
            session,
            join_conditions=['roles'],
            id=1,
            roles__name='admin'
        )
        
        return has_posts, is_admin
```

## 实际应用场景

### 用户仪表板数据

```python
async def user_dashboard_data(user_id: int):
    async with _async_db_session() as session:
        # 获取用户完整信息
        user = await user_crud.select_model(
            session, user_id,
            load_strategies={
                'profile': 'joinedload',
                'posts': 'selectinload',
                'posts.category': 'joinedload',
                'posts.comments': 'selectinload',
                'roles': 'selectinload'
            }
        )
        
        if not user:
            return None
        
        # 构建仪表板数据
        dashboard_data = {
            'user': user,
            'profile': user.profile,
            'posts_count': len(user.posts),
            'comments_count': sum(len(post.comments) for post in user.posts),
            'roles': [role.name for role in user.roles]
        }
        
        return dashboard_data
```

### 文章列表页面

```python
async def posts_list_page(page: int = 1, page_size: int = 20):
    async with _async_db_session() as session:
        offset = (page - 1) * page_size
        
        # 获取文章列表及相关数据
        posts = await post_crud.select_models_order(
            session,
            sort_columns='created_at',
            sort_orders='desc',
            limit=page_size,
            offset=offset,
            load_strategies={
                'author': 'joinedload',
                'category': 'joinedload',
                'comments': 'selectinload'
            }
        )
        
        # 获取总数
        total = await post_crud.count(session)
        
        return {
            'posts': posts,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
```

### 用户搜索功能

```python
async def search_users_with_posts(keyword: str):
    async with _async_db_session() as session:
        # 搜索用户名或邮箱包含关键词的用户
        users = await user_crud.select_models(
            session,
            __or__={
                'name__like': [f'%{keyword}%'],
                'email__like': [f'%{keyword}%']
            },
            join_conditions=['posts'],  # 只返回有文章的用户
            load_strategies={
                'posts': 'selectinload',
                'profile': 'joinedload'
            }
        )
        
        return users
```

## 最佳实践总结

1. **选择合适的加载策略**
   - 一对一：`joinedload`
   - 一对多：`selectinload`
   - 多对多：`selectinload` 或 `subqueryload`

2. **避免过度加载**
   - 只加载需要的关系数据
   - 根据使用场景选择加载深度

3. **合理使用 JOIN**
   - 用于过滤条件而非数据获取
   - 结合预加载策略使用

4. **性能监控**
   - 使用 `echo=True` 监控 SQL 查询
   - 避免 N+1 查询问题
   - 合理设置分页大小
