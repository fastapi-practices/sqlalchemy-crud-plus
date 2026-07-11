# 链式查询与写入

CRUDPlus 提供基于 SQLAlchemy 的不可变链式构建器。现有 CRUD 方法仍然可用，链式 API 更适合动态组合查询、投影、聚合及复杂 SQL。

## 基础查询

通过 `query(session)` 创建绑定当前异步 Session 的构建器：

```python
users = await (
    user_crud.query(session)
    .where(lambda user: user.is_active.is_(True))
    .where(lambda user: user.name.contains('张'))
    .order_by(lambda user: user.created_at.desc())
    .limit(20)
    .to_list()
)
```

构建器不可变，每一步都会返回新对象，因此可以安全地从一个基础查询派生多个查询：

```python
base = user_crud.query(session).where(lambda user: user.is_active.is_(True))

admins = await base.where(lambda user: user.role == 'admin').to_list()
members = await base.where(lambda user: user.role == 'member').to_list()
```

Lambda 参数会从 `CRUDPlus[User]` 推断为 `type[User]`，因此 IDE、重命名工具和类型检查器都能识别字段错误。`where()` 也接受 SQLAlchemy 原生表达式：

```python
users = await (
    user_crud.query(session)
    .where(lambda user: user.created_at >= start_time)
    .where(
        (User.age.between(18, 65))
        & User.email.endswith('@example.com')
    )
    .to_list()
)
```

多次 `where()` 之间是 AND。Python 的 `and/or` 不能生成 SQL 表达式，请使用 `&`、`|`，或者使用动态组合方法：

```python
query = (
    user_crud.query(session)
    .where_if(only_active, lambda user: user.is_active.is_(True))
    .where_or(
        lambda user: user.name.contains(keyword),
        lambda user: user.email.contains(keyword),
    )
    .or_if(include_system, lambda user: user.role == 'system')
)
```

旧的字符串过滤继续兼容，但不再是推荐写法：

```python
users = await user_crud.query(session).where(is_active=True, name__like='%张%').all()
```

## 排序与分页

字符串字段名前加 `-` 表示倒序，普通字段名或 `+` 表示正序：

```python
users = await (
    user_crud.query(session)
    .order_by(lambda user: (user.created_at.desc(), user.name.asc()))
    .page(1, 20)
    .to_list()
)
```

需要总数和分页元数据时，直接调用 `paginate()`：

```python
result = await (
    user_crud.query(session)
    .where(lambda user: user.is_active.is_(True))
    .order_by(lambda user: user.created_at.desc())
    .paginate(page=1, size=20)
)

print(result.items)
print(result.total)
print(result.total_pages)
```

分页统计保留过滤、JOIN、分组和 `distinct`，但忽略查询链中已有的排序、`limit` 和 `offset`。

## 投影和结果类型

默认选择主模型，`all()` 返回模型序列：

```python
users = await user_crud.query(session).all()
```

选择字段、多模型或聚合表达式后，`all()` 返回 SQLAlchemy `Row`：

```python
rows = await (
    user_crud.query(session)
    .select(lambda user: {'user_id': user.id, 'user_name': user.name})
    .order_by(lambda user: user.id)
    .to_list()
)

for row in rows:
    print(row.user_id, row.user_name)
```

只需要第一列时使用 `scalars()`，只需要一个值时使用 `scalar()` 或 `scalar_one()`：

```python
names = await user_crud.query(session).select(lambda user: user.name).scalars()
total = await user_crud.query(session).count(lambda user: user.id)
largest_id = await user_crud.query(session).max(lambda user: user.id)
```

其他终结方法包括：

- `first()`
- `one()` / `one_or_none()`
- `count()` / `exists()`
- `stream()`

## JOIN 和关系加载

```python
rows = await (
    user_crud.query(session)
    .join(Post, lambda user, post: user.id == post.author_id, join_type='left')
    .where(Post.status == 'published')
    .select(User.name, Post.title)
    .to_list()
)
```

JOIN 条件的两个 Lambda 参数会分别推断为主模型和目标模型。JOIN 后继续查询关联模型字段时，直接使用 `Post.status`、`Post.title` 等 SQLAlchemy 属性，可继续获得完整的字段检查。运行时也支持多参数 Lambda，但 Python 类型检查器无法从普通 `QueryBuilder[User]` 持续推导任意数量的后续 JOIN 模型。

也可以使用 relationship 名称：

```python
users = await user_crud.query(session).join_relationship(lambda user: user.posts).to_list()
```

关系预加载继续使用已有加载策略：

```python
users = await user_crud.query(session).load(lambda user: user.posts, strategy='selectinload').to_list()
```

复杂加载选项可以直接传入 SQLAlchemy option：

```python
users = await user_crud.query(session).options(selectinload(User.posts)).all()
```

集合 `joinedload` 需要结果去重时调用 `.unique()`。

## 分组和复杂查询

```python
rows = await (
    post_crud.query(session)
    .select(lambda post: (post.category_id, func.count(post.id).label('total')))
    .group_by(lambda post: post.category_id)
    .having(lambda post: func.count(post.id) > 5)
    .order_by(lambda post: func.count(post.id).desc())
    .to_list()
)
```

构建器支持 `distinct()`、`subquery()`、`cte()`、`add_cte()`、`union()` 和 `union_all()`：

```python
published = post_crud.query(session).where(lambda post: post.status == 'published').select(lambda post: post.id)
draft = post_crud.query(session).where(lambda post: post.status == 'draft').select(lambda post: post.id)

rows = await published.union_all(draft).all()
post_ids = published.cte('published_post_ids')
```

窗口函数直接作为 SQLAlchemy 表达式投影：

```python
rows = await (
    post_crud.query(session)
    .select(
        Post.id,
        func.row_number().over(
            partition_by=Post.category_id,
            order_by=Post.created_at.desc(),
        ).label('row_number'),
    )
    .all()
)
```

使用 `statement` 获取最终 SQLAlchemy 语句，使用 `to_sql()` 查看 SQL：

```python
query = post_crud.query(session).where(lambda post: post.status == 'published')
stmt = query.statement
sql = query.to_sql(literal_binds=True)
```

## 链式更新和删除

可以从查询链直接执行：

```python
affected = await (
    user_crud.query(session)
    .where(lambda user: user.status == 'inactive')
    .update(lambda user: {user.login_attempts: user.login_attempts + 1})
)

affected = await user_crud.query(session).where(lambda user: user.id == user_id).delete()
```

也可以使用独立构建器：

```python
affected = await (
    user_crud.update_query(session)
    .where(lambda user: user.status == 'inactive')
    .set(lambda user: {user.is_active: False})
    .execute()
)

deleted = await (
    user_crud.delete_query(session)
    .where(lambda user: user.id == user_id)
    .returning(lambda user: (user.id, user.name))
    .execute()
)
```

为了避免误操作，update/delete 必须包含调用方显式提供的 WHERE 条件。全表操作必须主动确认：

```python
await user_crud.update_query(session).set(lambda user: {user.is_active: False}).allow_all().execute()
```

软删除自动条件不算显式 WHERE，不能绕过这项保护。包含 JOIN、投影、分组、分页或锁的查询不能转换为可移植的 update/delete；这类操作应使用独立构建器或原生 SQLAlchemy。

## Insert 和 Upsert

```python
users = await (
    user_crud.insert_query(session)
    .values([
        {'name': '张三', 'email': 'a@example.com'},
        {'name': '李四', 'email': 'b@example.com'},
    ])
    .returning()
    .execute()
)
```

字典批量插入使用 SQLAlchemy Core，不会调用 ORM dataclass 的 `default_factory`。没有数据库端默认值的必填字段必须包含在字典中。

Upsert 支持 PostgreSQL、SQLite、MySQL 和 MariaDB：

```python
user = await (
    user_crud.upsert_query(session)
    .values({'email': 'a@example.com', 'name': '张三'})
    .conflict_on(lambda user: user.email)
    .update_columns(lambda user: user.name)
    .returning(lambda user: (user.id, user.name))
    .execute()
)
```

PostgreSQL 和 SQLite 支持 `.do_nothing()`。MySQL/MariaDB 使用 `ON DUPLICATE KEY UPDATE`，不支持该选项。

## 软删除和事务

当 CRUD 实例启用 `filter_deleted=True` 时，链式查询、更新和删除都会自动排除软删除记录：

```python
user_crud = CRUDPlus(User, filter_deleted=True)

active_users = await user_crud.query(session).all()
all_users = await user_crud.query(session).include_deleted().all()
```

逻辑删除使用 `soft_delete()`：

```python
await user_crud.query(session).where(lambda user: user.id == user_id).soft_delete()
```

链式写入默认不提交事务。推荐在外层统一管理：

```python
async with async_session.begin() as session:
    await (
        user_crud.query(session)
        .where(lambda user: user.id == user_id)
        .update(lambda user: {user.name: '新名称'})
    )
    await audit_crud.insert_query(session).values(audit_data).execute()
```
