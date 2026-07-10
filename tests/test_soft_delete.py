import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import ModelColumnError
from tests.models.basic import Ins


@pytest.fixture
def crud_ins_soft() -> CRUDPlus[Ins]:
    """Provide CRUD instance for Ins model with soft deletion filtering enabled."""
    return CRUDPlus(Ins, filter_deleted=True)


class TestSoftDeleteInit:
    def test_invalid_deleted_flag_column(self):
        with pytest.raises(ModelColumnError):
            CRUDPlus(Ins, filter_deleted=True, deleted_flag_column='not_a_column')

    def test_disabled_by_default(self, crud_ins: CRUDPlus[Ins]):
        assert crud_ins.filter_deleted is False


class TestSoftDeleteQueries:
    @pytest.mark.asyncio
    async def test_select_models_excludes_deleted(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins_soft: CRUDPlus[Ins]
    ):
        results = await crud_ins_soft.select_models(db)
        assert all(item.is_deleted is False for item in results)

    @pytest.mark.asyncio
    async def test_select_models_include_deleted(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins_soft: CRUDPlus[Ins], crud_ins: CRUDPlus[Ins]
    ):
        all_results = await crud_ins_soft.select_models(db, include_deleted=True)
        unfiltered = await crud_ins.select_models(db)
        assert len(all_results) == len(unfiltered)

    @pytest.mark.asyncio
    async def test_select_model_by_pk_excludes_deleted(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins_soft: CRUDPlus[Ins]
    ):
        deleted_item = next(item for item in sample_ins if item.is_deleted)

        result = await crud_ins_soft.select_model(db, deleted_item.id)
        assert result is None

        result = await crud_ins_soft.select_model(db, deleted_item.id, include_deleted=True)
        assert result is not None

    @pytest.mark.asyncio
    async def test_select_model_by_column_excludes_deleted(self, db: AsyncSession, crud_ins_soft: CRUDPlus[Ins]):
        item = Ins(name='soft_delete_by_column', is_deleted=True)
        db.add(item)
        await db.commit()

        result = await crud_ins_soft.select_model_by_column(db, name='soft_delete_by_column')
        assert result is None

        result = await crud_ins_soft.select_model_by_column(db, name='soft_delete_by_column', include_deleted=True)
        assert result is not None

    @pytest.mark.asyncio
    async def test_count_excludes_deleted(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins_soft: CRUDPlus[Ins], crud_ins: CRUDPlus[Ins]
    ):
        filtered = await crud_ins_soft.count(db)
        total = await crud_ins_soft.count(db, include_deleted=True)

        expected_active = await crud_ins.count(db, is_deleted=False)
        assert filtered == expected_active
        assert total == await crud_ins.count(db)
        assert filtered < total

    @pytest.mark.asyncio
    async def test_exists_excludes_deleted(self, db: AsyncSession, crud_ins_soft: CRUDPlus[Ins]):
        item = Ins(name='soft_delete_exists', is_deleted=True)
        db.add(item)
        await db.commit()

        assert await crud_ins_soft.exists(db, name='soft_delete_exists') is False
        assert await crud_ins_soft.exists(db, name='soft_delete_exists', include_deleted=True) is True

    @pytest.mark.asyncio
    async def test_select_models_order_excludes_deleted(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins_soft: CRUDPlus[Ins]
    ):
        results = await crud_ins_soft.select_models_order(db, 'id', 'asc')
        assert all(item.is_deleted is False for item in results)

    @pytest.mark.asyncio
    async def test_paginated_excludes_deleted(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins_soft: CRUDPlus[Ins], crud_ins: CRUDPlus[Ins]
    ):
        result = await crud_ins_soft.select_models_paginated(db, page=1, size=10000)

        expected_active = await crud_ins.count(db, is_deleted=False)
        assert result.total == expected_active
        assert all(item.is_deleted is False for item in result.items)


class TestSoftDeleteCustomFlag:
    @pytest.mark.asyncio
    async def test_custom_flag_column_and_value(self, db: AsyncSession, sample_ins: list[Ins]):
        crud = CRUDPlus(Ins, filter_deleted=True, deleted_flag_column='deleted', deleted_flag_value=1)

        target = sample_ins[0]
        await crud.update_model(db, target.id, {'deleted': 1}, commit=True)

        result = await crud.select_model(db, target.id)
        assert result is None

        result = await crud.select_model(db, target.id, include_deleted=True)
        assert result is not None
