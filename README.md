# sqlalchemy-crud-plus

基于 SQLAlChemy2 模型的异步 CRUD 操作

## 下载

```shell
pip install sqlalchemy-crud-plus
```

## TODO

- [ ] ...

## Use

以下仅为简易示例

```python
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
ins_dao = CRUDIns(ModelIns)
```

## 互动

[WeChat / QQ](https://github.com/wu-clan)

## 赞助

如果此项目能够帮助到你，你可以赞助作者一些咖啡豆表示鼓励：[:coffee: Sponsor :coffee:](https://wu-clan.github.io/sponsor/)
