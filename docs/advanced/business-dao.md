# 业务 DAO 封装

`CRUDPlus` 适合封装通用数据库操作。当一个模型出现租户隔离、状态流转、软删除或批量业务更新时，可以继承 `CRUDPlus`，创建一个面向业务的 DAO。

本页以博客关键词资产 `KeywordAsset` 为例，说明如何把通用 CRUD 和业务规则组合起来。

## 为什么要继承 CRUDPlus

直接使用 `CRUDPlus` 时，调用方需要自己重复传入租户、站点和软删除条件：

```python
await crud.select_models(
    db,
    tenant_id=tenant_id,
    site_url=site_url,
    deleted_at=None,
)
```

业务 DAO 可以统一封装这些约束，并在此基础上提供更有意义的方法，例如：

- 按租户和站点批量软删除
- 批量修改关键词品类
- `KEEP` 和 `REMOVE` 状态之间的流转
- 只允许删除已经移除的关键词
- 返回分页对象，而不是裸的 ORM 列表

## 定义业务 DAO

```python
from typing import Any, ClassVar, cast

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from app.archive.model.blog_keyword_asset import KeywordAsset
from utils.timezone import timezone


class CRUDBlogKeywords(CRUDPlus[KeywordAsset]):
    """博客关键词数据库操作类。"""

    # 所有业务查询默认排除软删除记录。
    default_filters: ClassVar[dict[str, Any]] = {"deleted_at": None}

    def _with_default_filters(self, **filters: Any) -> dict[str, Any]:
        # 默认条件放在后面，调用方不能覆盖 deleted_at。
        return {**filters, **self.default_filters}

    async def soft_delete_by_tenant_and_site_url(
        self,
        db: AsyncSession,
        *,
        tenant_id: int,
        site_url: str,
    ) -> int:
        stmt = (
            update(self.model)
            .where(
                self.model.tenant_id == tenant_id,
                self.model.site_url == site_url,
                self.model.deleted_at.is_(None),
            )
            .values(deleted_at=timezone.now())
        )
        result = await db.execute(stmt)
        return result.rowcount or 0


blog_keywords_dao = CRUDBlogKeywords(KeywordAsset)
```

`CRUDPlus` 实例只绑定模型，不绑定 `AsyncSession`。因此同一个 DAO 可以安全地在不同请求中复用，Session 仍由请求或任务负责创建和管理。

## 调用通用 CRUD

继承后可以直接使用父类方法：

```python
# 主键查询
item = await blog_keywords_dao.select_model(db, pk=keyword_id)

# 条件查询
items = await blog_keywords_dao.select_models(
    db,
    tenant_id=tenant_id,
    site_url=site_url,
    deleted_at=None,
)

# 统计和存在性检查
total = await blog_keywords_dao.count(db, tenant_id=tenant_id)
exists = await blog_keywords_dao.exists(db, site_url=site_url)
```

推荐通过 DAO 自己的 `_with_default_filters()` 生成条件，避免遗漏软删除过滤：

```python
filters = blog_keywords_dao._with_default_filters(
    tenant_id=tenant_id,
    site_url=site_url,
)
items = await blog_keywords_dao.select_models(db, **filters)
```

## 分页查询

业务查询通常需要把 Schema 参数转换为 CRUDPlus 的过滤、排序和分页参数：

```python
async def get_keywords(db: AsyncSession, query: KeywordAssetQueryInput):
    excluded = {"page", "page_size", "sort_field", "sort_order", "keyword_norm"}
    filters = query.model_dump(exclude_none=True, exclude=excluded)
    filters = blog_keywords_dao._with_default_filters(**filters)

    if query.keyword_norm:
        filters["keyword_norm__like"] = f"%{query.keyword_norm}%"

    total = await blog_keywords_dao.count(db, **filters)
    items = await blog_keywords_dao.select_models_order(
        db,
        query.sort_field,
        query.sort_order,
        limit=query.page_size,
        offset=(query.page - 1) * query.page_size,
        **filters,
    )

    return PageData(
        items=list(items),
        total=total,
        page=query.page,
        page_size=query.page_size,
    )
```

`count()` 和列表查询必须使用同一组过滤条件，否则 `total` 可能和实际列表不一致。

如果不需要自定义 `PageData`，也可以使用 CRUDPlus 自带的分页方法：

```python
result = await blog_keywords_dao.select_models_paginated(
    db,
    page=query.page,
    size=query.page_size,
    sort_columns=query.sort_field,
    sort_orders=query.sort_order,
    **filters,
)
```

## 批量更新

`bulk_update_models(..., pk_mode=False)` 表示使用一份更新数据，更新所有满足过滤条件的记录：

```python
await blog_keywords_dao.bulk_update_models(
    db,
    [{"category": "Technology", "category_normal": "technology"}],
    pk_mode=False,
    tenant_id=tenant_id,
    site_url=site_url,
    id__in=keyword_ids,
    deleted_at=None,
)
```

如果每条记录的更新内容不同，则使用默认的 `pk_mode=True`，每个字典都必须包含主键：

```python
await blog_keywords_dao.bulk_update_models(
    db,
    [
        {"id": 1, "category": "technology"},
        {"id": 2, "category": "news"},
    ],
)
```

批量 SQL 更新可能不会自动同步当前 Session 中已经加载的 ORM 实例。如果方法需要返回这些实例，应在更新后手动同步对象：

```python
for item in items:
    item.category = new_category
    item.category_normal = new_category.lower()
```

## 状态流转示例

关键词资产可以通过 DAO 固定状态变化规则：

```text
KEEP --remove_keywords--> REMOVE --delete_keywords--> deleted_at 有值
REMOVE --restore_keywords--> KEEP
```

移除关键词：

```python
items = await blog_keywords_dao.remove_keywords(db, query)
```

恢复关键词：

```python
items = await blog_keywords_dao.restore_keywords(db, query)
```

最终软删除：

```python
items = await blog_keywords_dao.delete_keywords(db, query)
```

`delete_keywords()` 只处理 `REMOVE` 状态的记录，不会执行物理 `DELETE`。

## 自定义 SQL 操作

当操作需要更新多个字段，或者需要避免先查询再逐条更新时，可以在 DAO 中直接使用 SQLAlchemy Core：

```python
async def clear_category_by_tenant_and_site_url(
    self,
    db: AsyncSession,
    *,
    tenant_id: int,
    site_url: str,
    category_normal: str,
) -> int:
    stmt = (
        update(self.model)
        .where(
            self.model.tenant_id == tenant_id,
            self.model.site_url == site_url,
            self.model.category_normal == category_normal,
            self.model.deleted_at.is_(None),
        )
        .values(category="-", category_normal="-")
    )
    result = await db.execute(stmt)
    return result.rowcount or 0
```

这仍然复用了 CRUDPlus 的模型绑定和 Session 调用方式，只是针对特殊业务直接构造 SQL。

## 事务控制

DAO 方法默认不提交事务。涉及多个 DAO 或级联删除时，应在外层统一管理：

```python
async with async_session.begin() as db:
    await brand_dao.soft_delete(db, tenant_id=tenant_id, site_url=site_url)
    await blog_keywords_dao.soft_delete_by_tenant_and_site_url(
        db,
        tenant_id=tenant_id,
        site_url=site_url,
    )
```

这样可以保证多个表的操作要么全部成功，要么全部回滚。

## 使用时的注意事项

- `ClassVar` 用于声明 DAO 的类级默认配置，不会被当作实例字段。
- `cast()` 只用于类型检查，不会在运行时转换对象；如需转换，应显式调用 `list(items)` 或执行数据转换。
- `rowcount` 可能因数据库驱动不同而有差异，业务上通常用 `result.rowcount or 0`。
- 查询和更新必须使用完全一致的租户、用户、站点和软删除条件。
- 如果 `user_id` 允许为空，应在查询和更新前统一归一化，不能一处使用 `0`、另一处使用 `None`。
- 批量更新绕过 ORM 属性事件和部分 Session 同步逻辑；需要返回最新对象时应手动同步或重新查询。
- 不建议在 DAO 内部调用 `commit()`，否则无法和其他业务操作组成一个原子事务。
