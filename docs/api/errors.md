# 错误类型

本页面记录了 SQLAlchemy CRUD Plus 中定义的错误类型和异常。

## 库内置异常

SQLAlchemy CRUD Plus 定义了以下自定义异常类型：

::: sqlalchemy_crud_plus.errors.SelectOperatorError

::: sqlalchemy_crud_plus.errors.ColumnSortError

::: sqlalchemy_crud_plus.errors.ModelColumnError

::: sqlalchemy_crud_plus.errors.JoinConditionError

::: sqlalchemy_crud_plus.errors.LoadingStrategyError

::: sqlalchemy_crud_plus.errors.MultipleResultsError

## 异常层次结构

```
Exception
├── SelectOperatorError          # 选择操作符错误
├── ColumnSortError             # 列排序错误
├── ModelColumnError            # 模型列错误
├── JoinConditionError          # JOIN 条件错误
├── LoadingStrategyError        # 加载策略错误
└── MultipleResultsFoundError   # 多结果发现错误
```

## 常见异常场景

### SelectOperatorError

当使用不支持的过滤操作符时抛出。

```python
from sqlalchemy_crud_plus.errors import SelectOperatorError

try:
    users = await user_crud.select_models(session, name__invalid_op='test')
except SelectOperatorError as e:
    print(f"不支持的操作符: {e}")
```

### ModelColumnError

当访问模型中不存在的列时抛出。

```python
from sqlalchemy_crud_plus.errors import ModelColumnError

try:
    users = await user_crud.select_models(session, nonexistent_column='value')
except ModelColumnError as e:
    print(f"列不存在: {e}")
```

### MultipleResultsFoundError

当期望单个结果但找到多个结果时抛出。

```python
from sqlalchemy_crud_plus.errors import MultipleResultsFoundError

try:
    count = await user_crud.update_model_by_column(
        session,
        obj={"name": "新名称"},
        name__like='%张%'  # 可能匹配多条记录
    )
except MultipleResultsFoundError as e:
    print(f"找到多条记录: {e}")
```
