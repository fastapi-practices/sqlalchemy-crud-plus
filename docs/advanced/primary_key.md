!!! note 主键参数命名

    由于在 python 内部 `id` 为关键字，因此，我们设定默认主键入参为 `pk`。这仅用于函数入参，并不要求模型主键必须定义为 `pk`

!!! tip 自动主键

    我们在 SQLAlchemy CRUD Plus 内部通过 [inspect()](https://docs.sqlalchemy.org/en/20/core/inspection.html) 自动搜索表主键，
    而非强制绑定主键列必须命名为 `id`

## 单个主键

```py title="e.g."
class ModelIns(Base):
    # define primary_key
    primary_key: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)


class ModelIns2(Base):
    # define primary_key
    primary_key: Mapped[str] = mapped_column(primary_key=True, index=True)
```

## 复合主键

```python title="e.g."
class ModelIns(Base):
    primary_key: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    primary_key2: Mapped[str] = mapped_column(primary_key=True, index=True)
```
