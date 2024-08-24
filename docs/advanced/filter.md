## 允许多次更新和删除

SQLAchemy CRUD Plus 的高级功能之一是可以根据指定条件一次性更新或删除多条记录。
条件一次性更新或删除多条记录。这对于需要修改或删除符合特定条件的多条记录的批量操作特别有用。
符合特定条件的记录。

### 更新多条记录

要更新多条记录，您可以在 `update` 方法中设置 `allow_multiple=True` 参数。这样，SQLAchemy CRUD Plus
将更新应用于所有匹配给定过滤器的记录。

```python

```

### 删除多条记录

同样，您可以通过在 `delete` 或 `db_delete` 方法中使用 `allow_multiple=True` 参数来删除多条记录。
方法中使用`allow_multiple=True`参数，就可以删除多条记录，具体取决于执行的是软删除还是硬删除。

```python

```

## 高级过滤器

SQLAchemy CRUD Plus 支持高级过滤选项，允许使用运算符查询记录，如 greater
大于 (`__gt`)、小于 (`__lt`)，以及它们的包容性对应运算符 (`__gte`, `__lte`)。这些过滤器可用于任何
方法中使用，包括 `get`, `get_multi`, `exists`, `count`, `update` 和 `delete`。

### 单参数过滤器

大多数过滤器操作符需要一个字符串或整数值。

```python

```

目前支持的单参数过滤器有

- `__gt`：大于
- `__lt`：小于
- `__gte`：大于或等于
- `__lte`：小于或等于
- `__ne`：不等于
- `__is`：用于测试 “真”、“假” 和 “无”。
- `__is_not`：“is” 的否定
- `__like`：针对特定文本模式的 SQL “like” 搜索
- `__not_like`：“like” 的否定
- `__ilike`：大小写不敏感的 “like”
- `__not_ilike`：大小写不敏感的 “not_like”
- `__startswith`：文本以给定字符串开始
- `__endswith`：文本以给定字符串结束
- `__contains`：文本包含给定字符串
- `__match`：特定于数据库的匹配表达式

### 复杂参数过滤器

某些运算符需要多个值。它们必须以 python 元组、列表或集合的形式传递。

```python

```

- `__between`：在两个数值之间
- `__in`：包含在
- `__not_in`：不包含在

### OR 子句

支持更复杂的 OR 过滤器。它们必须以字典形式传递，其中每个键都是库支持的运算符
值作为参数传递。

```python

```

### AND 子句

AND 子句可以通过连锁多个过滤器来实现。

```python

```

### 计算记录

```python

```
