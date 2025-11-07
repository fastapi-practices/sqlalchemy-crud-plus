# 事务控制

SQLAlchemy CRUD Plus 基于 SQLAlchemy 2.0 的现代事务管理模式，提供简洁而强大的事务控制功能。

## 基础事务模式

### 自动事务管理（推荐）

```python
# 推荐的事务模式
async with async_session.begin() as session:
    # 在这个块中的所有操作都在同一个事务中
    user_data = UserCreate(name="张三", email="zhangsan@example.com")
    user = await user_crud.create_model(session, user_data)
    
    # 如果没有异常，事务会自动提交
    # 如果有异常，事务会自动回滚
```

### 手动事务控制

```python
async with async_session() as session:
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

## flush 和 commit

### flush 参数

`flush=True` 将更改发送到数据库但不提交事务，主要用于获取自动生成的主键。

```python
async with async_session.begin() as session:
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

`commit=True` 立即提交事务，适用于独立的单个操作。

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

## 复杂事务场景

### 多表操作事务

```python
async with async_session.begin() as session:
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
async with async_session.begin() as session:
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

## 嵌套事务（保存点）

```python
async with async_session.begin() as session:
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

## 批量操作事务

### 分批处理

```python
async def batch_create_users(users_data: list, batch_size: int = 100):
    """分批处理大量数据，避免长事务"""
    
    for i in range(0, len(users_data), batch_size):
        batch = users_data[i:i + batch_size]
        
        async with async_session.begin() as session:
            # 处理一批数据
            await user_crud.create_models(session, batch)
            print(f"已处理 {i + len(batch)}/{len(users_data)} 条记录")
```

### 事务内批量操作

```python
async with async_session.begin() as session:
    # 批量创建用户
    users_data = [
        UserCreate(name=f"用户{i}", email=f"user{i}@example.com")
        for i in range(100)
    ]
    users = await user_crud.create_models(session, users_data)
    
    # 批量更新
    await user_crud.update_model_by_column(
        session,
        obj={"is_active": True},
        created_at__ge=datetime.now() - timedelta(days=1)
    )
```

## 实际应用示例

### 用户注册流程

```python
async def register_user(
    session: AsyncSession,
    user_data: UserCreate,
    profile_data: ProfileCreate = None
):
    """用户注册，包含用户和资料创建"""
    async with session.begin():
        # 检查邮箱是否已存在
        existing = await user_crud.exists(session, email=user_data.email)
        if existing:
            raise ValueError("邮箱已存在")
        
        # 创建用户
        user = await user_crud.create_model(session, user_data, flush=True)
        
        # 创建用户资料（可选）
        if profile_data:
            profile_data.user_id = user.id
            await profile_crud.create_model(session, profile_data)
        
        return user
```

### 订单处理

```python
async def process_order(
    session: AsyncSession,
    order_data: OrderCreate,
    order_items: list[OrderItemCreate]
):
    """处理订单和订单项"""
    async with session.begin():
        # 创建订单
        order = await order_crud.create_model(session, order_data, flush=True)
        
        # 创建订单项
        for item_data in order_items:
            item_data.order_id = order.id
            await order_item_crud.create_model(session, item_data)
        
        # 更新库存
        for item_data in order_items:
            await product_crud.update_model_by_column(
                session,
                obj={"stock": Product.stock - item_data.quantity},
                id=item_data.product_id
            )
        
        return order
```

## 错误处理

### 异常回滚

```python
async def safe_user_operation(session: AsyncSession, user_data: dict):
    """安全的用户操作，包含错误处理"""
    async with session.begin():
        try:
            # 执行操作
            user = await user_crud.create_model(session, user_data)
            
            # 可能失败的操作
            await send_welcome_email(user.email)
            
            return user
            
        except EmailError:
            # 特定异常处理
            print("邮件发送失败，但用户创建成功")
            return user
            
        except Exception as e:
            # 其他异常会自动回滚事务
            print(f"操作失败: {e}")
            raise
```

### 部分失败处理

```python
async def bulk_process_with_savepoints(session: AsyncSession, items: list):
    """批量处理，部分失败不影响其他"""
    results = []
    
    async with session.begin():
        for item in items:
            savepoint = await session.begin_nested()
            
            try:
                result = await process_single_item(session, item)
                await savepoint.commit()
                results.append(result)
                
            except Exception as e:
                await savepoint.rollback()
                print(f"项目 {item.id} 处理失败: {e}")
                results.append(None)
    
    return results
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

3. **控制事务范围**
   - 保持事务尽可能短小
   - 避免在事务中执行耗时操作
   - 考虑使用分批处理

4. **错误处理**
   - 在事务外部处理业务逻辑错误
   - 使用保存点处理部分失败场景
   - 记录事务失败的详细信息

## 注意事项

1. **参数冲突**: 不要同时使用 `flush=True` 和 `commit=True`
2. **事务嵌套**: 合理使用保存点，避免过深嵌套
3. **长事务**: 避免长时间持有事务，影响数据库性能
4. **异常处理**: 确保异常能够正确触发事务回滚

## 下一步

- [关系查询](relationship.md) - 学习关系查询和 JOIN
- [过滤条件](filter.md) - 高级过滤技术  
- [API 参考](../api/crud-plus.md) - 完整 API 文档
