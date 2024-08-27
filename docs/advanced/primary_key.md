!!! note 主键参数命名

    由于在 python 内部 id 的特殊性，我们设定 pk (参考 Django) 作为模型主键命名，所以在 crud 方法中，任何涉及到主键的地方，入参都为 `pk`

```py title="e.g." hl_lines="2"
async def delete(self, db: AsyncSession, primary_key: int) -> int:
    return self.delete_model(db, pk=primary_key)
```

## 主键定义

!!! warning 自动主键

    我们在 SQLAlchemy CRUD Plus 内部通过 [inspect()](https://docs.sqlalchemy.org/en/20/core/inspection.html) 自动搜索表主键，
    而非强制绑定主键列必须命名为 id，感谢 [@DavidSche](https://github.com/DavidSche) 提供帮助 

```py title="e.g." hl_lines="4"
class ModelIns(Base):
    # your sqlalchemy model
    # define your primary_key
    custom_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
```
