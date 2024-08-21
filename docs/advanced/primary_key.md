!!! note 主键参数命名

    由于在 python 内部 id 的特殊性，我们设定 pk (参考 Django) 作为模型主键命名，
    所以在 crud 方法中，任何涉及到主键的地方，入参都为 `pk`
    
    ```py title="example"
    async def delete(self, db: AsyncSession, primary_key: int)
        return self.delete_model(db, pk=primary_key)
    ```
