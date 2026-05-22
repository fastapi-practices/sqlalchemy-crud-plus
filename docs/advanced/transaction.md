# 事务控制

CRUDPlus 不接管事务，而是沿用 SQLAlchemy `AsyncSession` 的事务模型。你可以按业务场景选择 `session.begin()`、`flush=True` 或 `commit=True`。

## 推荐模式

多个数据库操作属于同一个业务动作时，使用 `async with async_session.begin()`：

```python
async with async_session.begin() as session:
    user = await user_crud.create_model(session, user_data, flush=True)
    profile = await profile_crud.create_model(
        session,
        ProfileCreate(user_id=user.id, bio='hello')
    )
```

如果代码块正常结束，事务自动提交；如果抛出异常，事务自动回滚。

## flush=True

`flush=True` 会把变更发送到数据库，但不提交事务。最常见用途是提前拿到自增主键。

```python
async with async_session.begin() as session:
    user = await user_crud.create_model(session, user_data, flush=True)

    await post_crud.create_model(
        session,
        PostCreate(title='第一篇文章', author_id=user.id)
    )
```

## commit=True

`commit=True` 会在方法内部立即提交，适合独立的单个操作。

```python
user = await user_crud.create_model(session, user_data, commit=True)
await user_crud.update_model(session, pk=user.id, obj={'name': '新名称'}, commit=True)
await user_crud.delete_model(session, pk=user.id, commit=True)
```

!!! warning

    不建议在 `async with session.begin()` 内再传 `commit=True`。事务块内一般使用默认值或 `flush=True`。

## 手动控制

需要完全手动处理时，可以直接调用 SQLAlchemy 的事务方法。

```python
async with async_session() as session:
    try:
        await session.begin()
        user = await user_crud.create_model(session, user_data)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

## 保存点

保存点适合“部分失败不影响主事务”的场景。

```python
async with async_session.begin() as session:
    user = await user_crud.create_model(session, user_data, flush=True)

    savepoint = await session.begin_nested()
    try:
        await profile_crud.create_model(session, profile_data)
        await savepoint.commit()
    except Exception:
        await savepoint.rollback()

    await log_crud.create_model(session, log_data)
```

## 批量处理

大量数据不要放进一个超长事务。按批次提交更容易控制锁和内存。

```python
async def batch_create_users(users_data: list[UserCreate], batch_size: int = 100):
    for start in range(0, len(users_data), batch_size):
        batch = users_data[start:start + batch_size]
        async with async_session.begin() as session:
            await user_crud.create_models(session, batch)
```

## 选择建议

| 场景 | 推荐方式 |
| --- | --- |
| 一个请求内有多个写操作 | `async with session.begin()` |
| 创建后需要主键继续写关联表 | `flush=True` |
| 独立单个操作 | `commit=True` |
| 部分失败允许继续 | `session.begin_nested()` |
| 大量数据导入 | 分批事务 |

## 注意事项

- 查询方法不会自动提交事务。
- `flush=True` 不是提交，事务回滚后数据仍会撤销。
- 事务中避免执行耗时外部 IO，例如发邮件、调用第三方 API。
- 异常需要向外抛出，才能让 `session.begin()` 自动回滚。
