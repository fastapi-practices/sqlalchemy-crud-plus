# CRUDPlus API 参考

`CRUDPlus` 类是执行 CRUD 操作和关系查询的主要接口。

## 类定义

::: sqlalchemy_crud_plus.CRUDPlus

## 构造函数

```python
from sqlalchemy_crud_plus import CRUDPlus
from myapp.models import User

user_crud = CRUDPlus(User)
```

## 查询方法

### select_model

::: sqlalchemy_crud_plus.CRUDPlus.select_model

### select_model_by_column

::: sqlalchemy_crud_plus.CRUDPlus.select_model_by_column

### select_models

::: sqlalchemy_crud_plus.CRUDPlus.select_models

### select_models_order

::: sqlalchemy_crud_plus.CRUDPlus.select_models_order

### count

::: sqlalchemy_crud_plus.CRUDPlus.count

### exists

::: sqlalchemy_crud_plus.CRUDPlus.exists

## 创建方法

### create_model

::: sqlalchemy_crud_plus.CRUDPlus.create_model

### create_models

::: sqlalchemy_crud_plus.CRUDPlus.create_models

## 更新方法

### update_model

::: sqlalchemy_crud_plus.CRUDPlus.update_model

### update_model_by_column

::: sqlalchemy_crud_plus.CRUDPlus.update_model_by_column

## 删除方法

### delete_model

::: sqlalchemy_crud_plus.CRUDPlus.delete_model

### delete_model_by_column

::: sqlalchemy_crud_plus.CRUDPlus.delete_model_by_column

## 底层方法

### select

::: sqlalchemy_crud_plus.CRUDPlus.select

### select_order

::: sqlalchemy_crud_plus.CRUDPlus.select_order


