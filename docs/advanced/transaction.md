# 事务控制

SQLAlchemy CRUD Plus 基于 SQLAlchemy 2.0 的现代事务管理模式，提供了简洁而强大的事务控制功能。

## 基础事务模式

### 自动事务管理

```python
# 推荐的事务模式
async with async_db_session.begin() as session:
    # 在这个块中的所有操作都在同一个事务中
    user_data = UserCreate(name="张三", email="zhangsan@example.com")
    user = await user_crud.create_model(session, user_data)

    # 如果没有异常，事务会自动提交
    # 如果有异常，事务会自动回滚
```

### 手动事务控制

```python
async with async_db_session() as session:
    try:
        # 开始事务
        await session.begin()

        user_data = UserCreate(name="李四", email="lisi@example.com")
        user = await user_crud.create_model(session, user_data)

        # 手动提交
        await session.commit()

    except Exception as e:
        # 手动回滚
        await session.rollback()
        raise e
```

### 使用 flush 和 commit 参数

**flush**：将更改刷新到数据库但不提交事务，用于获取自动生成的主键或在同一事务中使用新创建的记录。

**commit**：立即提交事务，适用于独立的单个操作。

```python
# 使用 flush 获取自动生成的主键
user_data = UserCreate(name="张三", email="zhangsan@example.com")
user = await user_crud.create_model(session, user_data, flush=True)
# 此时 user.id 已可用，但事务未提交

# 自动提交单个操作
user_data = UserCreate(name="李四", email="lisi@example.com")
user = await user_crud.create_model(session, user_data, commit=True)

# 自动提交更新操作
await user_crud.update_model(session, pk=user_id, obj=update_data, commit=True)

# 自动提交删除操作
await user_crud.delete_model(session, pk=user_id, commit=True)
```

## 复杂事务场景

### 多表操作事务

```python
async with async_db_session.begin() as session:
    # 创建用户（使用 flush 获取主键）
    user_data = UserCreate(name="王五", email="wangwu@example.com")
    user = await user_crud.create_model(session, user_data, flush=True)

    # 创建个人资料（使用获取到的用户主键）
    profile_data = ProfileCreate(user_id=user.id, bio="个人简介")
    profile = await profile_crud.create_model(session, profile_data)

    # 创建文章
    post_data = PostCreate(
        title="我的第一篇文章",
        content="文章内容...",
        author_id=user.id
    )
    post = await post_crud.create_model(session, post_data)

    # 所有操作要么全部成功，要么全部回滚
```

### 条件事务

```python
async with async_db_session.begin() as session:
    # 检查用户是否存在
    existing_user = await user_crud.select_model_by_column(
        session, email="test@example.com"
    )

    if existing_user:
        # 更新现有用户
        user_update = UserUpdate(last_login=datetime.now())
        await user_crud.update_model(
            session, pk=existing_user.id, obj=user_update
        )
        user = existing_user
    else:
        # 创建新用户
        user_data = UserCreate(
            name="新用户",
            email="test@example.com"
        )
        user = await user_crud.create_model(session, user_data)

    return user
```

### 批量操作事务

```python
async with async_db_session.begin() as session:
    # 批量创建用户
    users_data = [
        UserCreate(name=f"用户{i}", email=f"user{i}@example.com")
        for i in range(100)
    ]
    users = await user_crud.create_models(session, users_data)

    # 批量更新
    for user in users:
        await user_crud.update_model(
            session, pk=user.id, obj={"is_active": True}
        )
```

## 嵌套事务

### 保存点（Savepoint）

```python
async with async_db_session.begin() as session:
    # 主事务
    user_data = UserCreate(name="主用户", email="main@example.com")
    user = await user_crud.create_model(session, user_data, flush=True)

    # 创建保存点
    savepoint = await session.begin_nested()

    try:
        # 嵌套事务
        profile_data = ProfileCreate(user_id=user.id, bio="可能失败的操作")
        profile = await profile_crud.create_model(session, profile_data)

        # 提交保存点
        await savepoint.commit()

    except Exception as e:
        # 回滚到保存点
        await savepoint.rollback()
        print(f"嵌套事务失败，已回滚: {e}")

    # 主事务继续
    return user
```

## 长事务处理

### 分批处理

```python
def batch_processing(data_list: list, batch_size: int = 100):
    """分批处理大量数据，避免长事务"""

    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]

        async with async_db_session.begin() as session:
            # 处理一批数据
            for item in batch:
                user_data = item
                await user_crud.create_model(session, user_data)

            print(f"已处理 {i + len(batch)}/{len(data_list)} 条记录")
```

### 异步处理

```python
import asyncio


async def concurrent_transactions():
    """并发执行多个独立事务"""

    async def process_user(user_data):
        async with async_db_session.begin() as session:
            user = await user_crud.create_model(session, user_data)
            return user

    # 并发处理
    tasks = []
    for i in range(10):
        user_data = UserCreate(name=f"用户{i}", email=f"user{i}@example.com")
        task = process_user(user_data)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## flush 和 commit 参数详解

### flush 参数

`flush=True` 将更改发送到数据库但不提交事务：

```python
async with async_db_session.begin() as session:
    # 创建用户并立即获取主键
    user_data = UserCreate(name="张三", email="zhangsan@example.com")
    user = await user_crud.create_model(session, user_data, flush=True)

    # 此时 user.id 已可用，可用于关联操作
    profile_data = ProfileCreate(user_id=user.id, bio="用户简介")
    profile = await profile_crud.create_model(session, profile_data)

    # 事务在 with 块结束时自动提交
```

**使用场景：**

- 需要获取自动生成的主键
- 在同一事务中创建关联记录
- 确保数据一致性检查

### commit 参数

`commit=True` 立即提交事务：

```python
# 独立操作，立即提交
user_data = UserCreate(name="李四", email="lisi@example.com")
user = await user_crud.create_model(session, user_data, commit=True)

# 适用于单个操作
await user_crud.update_model(session, pk=1, obj={"name": "新名称"}, commit=True)
await user_crud.delete_model(session, pk=1, commit=True)
```

**使用场景：**

- 独立的单个操作
- 不需要与其他操作组合
- 简化代码结构

### 参数组合使用

```python
# ❌ 错误：不要同时使用 flush 和 commit
user = await user_crud.create_model(session, user_data, flush=True, commit=True)

# ✅ 正确：根据需要选择其一
user = await user_crud.create_model(session, user_data, flush=True)  # 获取主键
user = await user_crud.create_model(session, user_data, commit=True)  # 立即提交
```

## 最佳实践

1. **优先使用自动事务管理**
    - 使用 `async with session.begin()` 模式
    - 让异常自然传播以触发回滚
    - 避免手动管理事务状态

2. **合理使用 flush 和 commit**
    - 需要主键时使用 `flush=True`
    - 独立操作时使用 `commit=True`
    - 避免在事务块中使用 `commit=True`

3. **合理控制事务范围**
    - 保持事务尽可能短小
    - 避免在事务中执行耗时操作
    - 考虑使用分批处理

4. **错误处理**
    - 在事务外部处理业务逻辑错误
    - 使用保存点处理部分失败场景
    - 记录事务失败的详细信息

5. **性能优化**
    - 合理设置事务隔离级别
    - 使用并发处理独立事务
    - 避免不必要的事务嵌套
