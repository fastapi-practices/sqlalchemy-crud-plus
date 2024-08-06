# sqlalchemy-crud-plus

Asynchronous CRUD operations based on SQLAlChemy 2.0

## Download

```shell
pip install sqlalchemy-crud-plus
```

## Use

```python
# example:
from sqlalchemy.orm import declarative_base
from sqlalchemy_crud_plus import CRUDPlus

Base = declarative_base()


class ModelIns(Base):
    # your sqlalchemy model
    pass


class CRUDIns(CRUDPlus[ModelIns]):
    # your controller service
    pass


# singleton
ins_dao: CRUDIns = CRUDIns(ModelIns)
```

## 互动

[WeChat / QQ](https://github.com/wu-clan)

## 赞助

如果此项目能够帮助到你，你可以赞助作者一些咖啡豆表示鼓励：[:coffee: Sponsor :coffee:](https://wu-clan.github.io/sponsor/)
