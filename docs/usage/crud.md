# CRUD 操作

SQLAlchemy CRUD Plus 提供完整的 CRUD（创建、读取、更新、删除）操作。

## 创建记录

### 单条记录

```python
async def create_user():
    async with _async_db_session() as session:
        async with session.begin():
            user_data = UserCreate(name="张三", email="zhangsan@example.com")
            user = await user_crud.create_model(session, user_data)
        return user
```

### 批量创建

```python
async def create_multiple_users():
    async with _async_db_session() as session:
        async with session.begin():
            users_data = [
                UserCreate(name="用户1", email="user1@example.com"),
                UserCreate(name="用户2", email="user2@example.com"),
                UserCreate(name="用户3", email="user3@example.com")
            ]
            users = await user_crud.create_models(session, users_data)
        return users
```

## 查询记录

### 主键查询

```python
async def get_user_by_id():
    async with _async_db_session() as session:
        user = await user_crud.select_model(session, 1)
        return user
```

### 条件查询

```python
async def get_user_by_email():
    async with _async_db_session() as session:
        user = await user_crud.select_model_by_column(
            session, 
            email="zhangsan@example.com"
        )
        return user
```

### 批量查询

```python
async def get_users():
    async with _async_db_session() as session:
        users = await user_crud.select_models(
            session,
            is_active=True,
            name__like="%张%",
            limit=10
        )
        return users
```

### 排序查询

```python
async def get_users_ordered():
    async with _async_db_session() as session:
        users = await user_crud.select_models_order(
            session,
            sort_columns="created_at",
            sort_orders="desc",
            limit=10
        )
        return users
```

## 更新记录

### 主键更新

```python
async def update_user():
    async with _async_db_session() as session:
        async with session.begin():
            user_update = UserUpdate(name="新名称", email="new@example.com")
            updated_user = await user_crud.update_model(session, 1, user_update)
        return updated_user
```

### 条件更新

```python
async def update_by_conditions():
    async with _async_db_session() as session:
        async with session.begin():
            user_update = UserUpdate(is_active=False)
            updated_user = await user_crud.update_model_by_column(
                session,
                user_update,
                email="user@example.com"
            )
        return updated_user
```

## 删除记录

### 主键删除

```python
async def delete_user():
    async with _async_db_session() as session:
        async with session.begin():
            deleted_count = await user_crud.delete_model(session, 1)
        return deleted_count
```

### 条件删除

```python
async def delete_by_conditions():
    async with _async_db_session() as session:
        async with session.begin():
            deleted_count = await user_crud.delete_model_by_column(
                session,
                is_active=False
            )
        return deleted_count
```

### 逻辑删除

```python
async def logical_delete():
    async with _async_db_session() as session:
        async with session.begin():
            deleted_count = await user_crud.delete_model(
                session,
                1,
                logical_deletion=True,
                deleted_flag_column="is_deleted"
            )
        return deleted_count
```

## 计数和存在检查

### 计数查询

```python
async def count_users():
    async with _async_db_session() as session:
        total = await user_crud.count(session)
        active_count = await user_crud.count(session, is_active=True)
        return total, active_count
```

### 存在检查

```python
async def check_user_exists():
    async with _async_db_session() as session:
        exists = await user_crud.exists(session, email="test@example.com")
        return exists
```

## 过滤操作符

### 比较操作符

```python
async def comparison_filters():
    async with _async_db_session() as session:
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

### 字符串操作符

```python
async def string_filters():
    async with _async_db_session() as session:
        users = await user_crud.select_models(
            session,
            name__like='%张%',              # 包含"张"
            email__startswith='admin',      # 以"admin"开头
            email__endswith='@qq.com'       # 以"@qq.com"结尾
        )
        return users
```

### OR 条件

```python
async def or_conditions():
    async with _async_db_session() as session:
        users = await user_crud.select_models(
            session,
            __or__={
                'email__endswith': ['@gmail.com', '@qq.com']
            }
        )
        return users
```

## 关系查询

### 预加载关系

```python
async def load_relationships():
    async with _async_db_session() as session:
        # 预加载用户的文章
        user = await user_crud.select_model(
            session, 1,
            load_strategies=['posts']
        )
        
        # 指定加载策略
        user = await user_crud.select_model(
            session, 1,
            load_strategies={
                'posts': 'selectinload',
                'profile': 'joinedload'
            }
        )
        return user
```

### JOIN 查询

```python
async def join_queries():
    async with _async_db_session() as session:
        # 只返回有文章的用户
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
        return users
```

## 分页查询

```python
async def paginated_users(page: int = 1, page_size: int = 20):
    async with _async_db_session() as session:
        offset = (page - 1) * page_size
        
        users = await user_crud.select_models_order(
            session,
            sort_columns="created_at",
            sort_orders="desc",
            limit=page_size,
            offset=offset
        )
        
        total = await user_crud.count(session)
        
        return {
            'users': users,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
```
