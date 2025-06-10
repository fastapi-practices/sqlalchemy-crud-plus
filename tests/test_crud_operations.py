#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Ins, InsPks
from tests.schema import ModelTest, ModelTestPks


class TestCRUDOperations:
    """Test all CRUD operations comprehensively."""

    # CREATE OPERATIONS
    @pytest.mark.asyncio
    async def test_create_single_model(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test creating a single model instance."""
        async with db_session.begin():
            data = ModelTest(name='single_test_item')
            result = await crud_ins.create_model(db_session, data)
            await db_session.flush()  # Ensure ID is generated

            assert result.name == 'single_test_item'
            assert result.id is not None
            assert result.del_flag is False

    @pytest.mark.asyncio
    async def test_create_multiple_models(
        self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins], sample_schemas: list[ModelTest]
    ):
        """Test creating multiple model instances."""
        async with db_session.begin():
            results = await crud_ins.create_models(db_session, sample_schemas)

            assert len(results) == len(sample_schemas)
            for i, result in enumerate(results):
                assert result.name == f'test_item_{i + 1}'

    @pytest.mark.asyncio
    async def test_create_with_kwargs(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test creating with additional kwargs."""
        async with db_session.begin():
            data = ModelTest(name='kwargs_test')
            result = await crud_ins.create_model(db_session, data, del_flag=True)

            assert result.name == 'kwargs_test'
            assert result.del_flag is True

    @pytest.mark.asyncio
    async def test_create_composite_key(self, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
        """Test creating model with composite primary key."""
        async with db_session.begin():
            data = ModelTestPks(id=100, name='composite_test', sex='men')
            result = await crud_ins_pks.create_model(db_session, data)

            assert result.name == 'composite_test'
            assert result.id == 100
            assert result.sex == 'men'

    # READ OPERATIONS
    @pytest.mark.asyncio
    async def test_select_by_id(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test selecting model by ID."""
        first_item = populated_db[0]
        result = await crud_ins.select_model(db_session, first_item.id)

        assert result is not None
        assert result.id == first_item.id
        assert result.name == first_item.name

    @pytest.mark.asyncio
    async def test_select_by_composite_key(
        self, populated_db_pks: dict, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]
    ):
        """Test selecting model by composite key."""
        first_man = populated_db_pks['men'][0]
        result = await crud_ins_pks.select_model(db_session, (first_man.id, first_man.sex))

        assert result is not None
        assert result.id == first_man.id
        assert result.sex == first_man.sex

    @pytest.mark.asyncio
    async def test_select_models_with_filters(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test selecting multiple models with filters."""
        results = await crud_ins.select_models(db_session, del_flag=False)
        assert len(results) > 0

        results = await crud_ins.select_models(db_session, name__startswith='item_')
        assert len(results) == len(populated_db)

    @pytest.mark.asyncio
    async def test_select_models_with_sorting(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test selecting models with sorting."""
        results = await crud_ins.select_models_order(db_session, sort_columns='name', sort_orders='asc')

        names = [r.name for r in results]
        assert names == sorted(names)

    @pytest.mark.asyncio
    async def test_select_model_by_column(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test selecting single model by column filter."""
        first_item = populated_db[0]
        result = await crud_ins.select_model_by_column(db_session, name=first_item.name)

        assert result is not None
        assert result.name == first_item.name

    @pytest.mark.asyncio
    async def test_count_operations(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test count operations."""
        total_count = await crud_ins.count(db_session)
        assert total_count == len(populated_db)

        filtered_count = await crud_ins.count(db_session, del_flag=False)
        assert filtered_count > 0

    @pytest.mark.asyncio
    async def test_exists_operations(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test exists operations."""
        exists = await crud_ins.exists(db_session, name='item_1')
        assert exists is True

        not_exists = await crud_ins.exists(db_session, name='nonexistent')
        assert not_exists is False

    # UPDATE OPERATIONS
    @pytest.mark.asyncio
    async def test_update_by_id(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test updating model by ID."""
        first_item = populated_db[0]
        update_data = ModelTest(name='updated_item')

        async with db_session.begin():
            result = await crud_ins.update_model(db_session, first_item.id, update_data)
            assert result == 1

        updated_item = await crud_ins.select_model(db_session, first_item.id)
        assert updated_item.name == 'updated_item'

    @pytest.mark.asyncio
    async def test_update_by_column(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test updating models by column filter."""
        async with db_session.begin():
            result = await crud_ins.update_model_by_column(
                db_session, {'name': 'bulk_updated'}, allow_multiple=True, del_flag=False
            )
            assert result > 0

        updated_items = await crud_ins.select_models(db_session, name='bulk_updated')
        assert len(updated_items) > 0

    @pytest.mark.asyncio
    async def test_update_with_dict(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test updating with dictionary data."""
        first_item = populated_db[0]

        async with db_session.begin():
            result = await crud_ins.update_model(db_session, first_item.id, {'name': 'dict_updated', 'del_flag': True})
            assert result == 1

        updated_item = await crud_ins.select_model(db_session, first_item.id)
        assert updated_item.name == 'dict_updated'
        assert updated_item.del_flag is True

    @pytest.mark.asyncio
    async def test_update_composite_key(
        self, populated_db_pks: dict, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]
    ):
        """Test updating model with composite key."""
        first_man = populated_db_pks['men'][0]
        update_data = {'name': 'updated_composite'}  # Use dict instead of Pydantic model

        async with db_session.begin():
            result = await crud_ins_pks.update_model(db_session, (first_man.id, first_man.sex), update_data)
            assert result == 1

        updated_item = await crud_ins_pks.select_model(db_session, (first_man.id, first_man.sex))
        assert updated_item.name == 'updated_composite'

    # DELETE OPERATIONS
    @pytest.mark.asyncio
    async def test_delete_by_id(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test deleting model by ID."""
        first_item = populated_db[0]

        async with db_session.begin():
            result = await crud_ins.delete_model(db_session, first_item.id)
            assert result == 1

        deleted_item = await crud_ins.select_model(db_session, first_item.id)
        assert deleted_item is None

    @pytest.mark.asyncio
    async def test_delete_by_column(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test deleting models by column filter."""
        async with db_session.begin():
            result = await crud_ins.delete_model_by_column(db_session, allow_multiple=True, del_flag=True)
            assert result > 0

        remaining_items = await crud_ins.select_models(db_session, del_flag=True)
        assert len(remaining_items) == 0

    @pytest.mark.asyncio
    async def test_logical_deletion(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test logical deletion."""
        first_item = populated_db[0]

        async with db_session.begin():
            result = await crud_ins.delete_model_by_column(db_session, logical_deletion=True, name=first_item.name)
            assert result == 1

        # Item should still exist but marked as deleted
        item = await crud_ins.select_model(db_session, first_item.id)
        assert item is not None
        assert item.del_flag is True

    @pytest.mark.asyncio
    async def test_delete_composite_key(
        self, populated_db_pks: dict, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]
    ):
        """Test deleting model with composite key."""
        first_woman = populated_db_pks['women'][0]

        async with db_session.begin():
            result = await crud_ins_pks.delete_model(db_session, (first_woman.id, first_woman.sex))
            assert result == 1

        deleted_item = await crud_ins_pks.select_model(db_session, (first_woman.id, first_woman.sex))
        assert deleted_item is None

    # COMPLEX FILTER OPERATIONS
    @pytest.mark.asyncio
    async def test_complex_filters(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test complex filter combinations."""
        # Test OR filters
        results = await crud_ins.select_models(db_session, name__or={'eq': 'item_1', 'like': 'item_2%'})
        assert len(results) >= 1

        # Test arithmetic filters
        results = await crud_ins.select_models(db_session, id__add={'value': 1, 'condition': {'gt': 1}})
        assert isinstance(results, list)

        # Test IN filter
        results = await crud_ins.select_models(db_session, name__in=['item_1', 'item_2', 'item_3'])
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_string_operations(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test string-specific operations."""
        # Test LIKE
        results = await crud_ins.select_models(db_session, name__like='item_%')
        assert len(results) == len(populated_db)

        # Test startswith
        results = await crud_ins.select_models(db_session, name__startswith='item_')
        assert len(results) == len(populated_db)

        # Test endswith
        results = await crud_ins.select_models(db_session, name__endswith='_1')
        assert len(results) >= 1

        # Test contains
        results = await crud_ins.select_models(db_session, name__contains='item')
        assert len(results) == len(populated_db)

    @pytest.mark.asyncio
    async def test_comparison_operations(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test comparison operations."""
        # Test greater than
        results = await crud_ins.select_models(db_session, id__gt=5)
        assert isinstance(results, list)

        # Test less than
        results = await crud_ins.select_models(db_session, id__lt=100)
        assert len(results) >= len(populated_db)

        # Test between
        results = await crud_ins.select_models(db_session, id__between=[1, 100])
        assert len(results) >= len(populated_db)

        # Test not equal
        results = await crud_ins.select_models(db_session, name__ne='nonexistent')
        assert len(results) == len(populated_db)

    @pytest.mark.asyncio
    async def test_null_operations(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test NULL-related operations."""
        # Test IS NULL
        results = await crud_ins.select_models(db_session, name__is=None)
        assert isinstance(results, list)

        # Test IS NOT NULL
        results = await crud_ins.select_models(db_session, name__is_not=None)
        assert len(results) == len(populated_db)

    @pytest.mark.asyncio
    async def test_transaction_operations(self, db_session_factory, crud_ins: CRUDPlus[Ins]):
        """Test transaction handling."""
        # Use separate sessions for each operation
        async with db_session_factory() as session:
            initial_count = await crud_ins.count(session)

        # Test successful transaction
        async with db_session_factory() as session:
            async with session.begin():
                data = ModelTest(name='transaction_test')
                await crud_ins.create_model(session, data)

        async with db_session_factory() as session:
            final_count = await crud_ins.count(session)
            assert final_count == initial_count + 1

        # Test rollback
        try:
            async with db_session_factory() as session:
                async with session.begin():
                    data = ModelTest(name='rollback_test')
                    await crud_ins.create_model(session, data)
                    raise Exception('Force rollback')
        except Exception:
            pass

        async with db_session_factory() as session:
            rollback_count = await crud_ins.count(session)
            assert rollback_count == final_count
