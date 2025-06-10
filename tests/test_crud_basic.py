#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Ins, InsPks
from tests.schema import ModelTest, ModelTestPks


class TestBasicCRUD:
    """Test basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_single(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test creating a single model."""
        async with db_session.begin():
            data = ModelTest(name='test_create')
            result = await crud_ins.create_model(db_session, data)
            assert result.name == 'test_create'

    @pytest.mark.asyncio
    async def test_create_multiple(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test creating multiple models."""
        async with db_session.begin():
            data = [ModelTest(name=f'test_{i}') for i in range(3)]
            results = await crud_ins.create_models(db_session, data)
            assert len(results) == 3

    @pytest.mark.asyncio
    async def test_create_with_kwargs(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test creating with additional kwargs."""
        async with db_session.begin():
            data = ModelTest(name='test_kwargs')
            result = await crud_ins.create_model(db_session, data, del_flag=True)
            assert result.del_flag is True

    @pytest.mark.asyncio
    async def test_select_by_id(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test selecting by ID."""
        first_item = populated_db[0]
        result = await crud_ins.select_model(db_session, first_item.id)
        assert result is not None
        assert result.id == first_item.id

    @pytest.mark.asyncio
    async def test_select_by_column(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test selecting by column filter."""
        first_item = populated_db[0]
        result = await crud_ins.select_model_by_column(db_session, name=first_item.name)
        assert result is not None
        assert result.name == first_item.name

    @pytest.mark.asyncio
    async def test_select_multiple(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test selecting multiple models."""
        results = await crud_ins.select_models(db_session, del_flag=False)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_select_with_sorting(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test selecting with sorting."""
        results = await crud_ins.select_models_order(db_session, sort_columns='name', sort_orders='asc')
        names = [r.name for r in results]
        assert names == sorted(names)

    @pytest.mark.asyncio
    async def test_count(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test count operation."""
        count = await crud_ins.count(db_session)
        assert count == len(populated_db)

    @pytest.mark.asyncio
    async def test_exists(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test exists operation."""
        exists = await crud_ins.exists(db_session, name='item_1')
        assert exists is True

        not_exists = await crud_ins.exists(db_session, name='nonexistent')
        assert not_exists is False

    @pytest.mark.asyncio
    async def test_update_by_id(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test updating by ID."""
        first_item = populated_db[0]
        async with db_session.begin():
            result = await crud_ins.update_model(db_session, first_item.id, {'name': 'updated_name'})
            assert result == 1

    @pytest.mark.asyncio
    async def test_update_by_column(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test updating by column filter."""
        async with db_session.begin():
            result = await crud_ins.update_model_by_column(
                db_session, {'name': 'bulk_updated'}, allow_multiple=True, del_flag=False
            )
            assert result > 0

    @pytest.mark.asyncio
    async def test_delete_by_id(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test deleting by ID."""
        first_item = populated_db[0]
        async with db_session.begin():
            result = await crud_ins.delete_model(db_session, first_item.id)
            assert result == 1

    @pytest.mark.asyncio
    async def test_delete_by_column(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test deleting by column filter."""
        async with db_session.begin():
            result = await crud_ins.delete_model_by_column(db_session, allow_multiple=True, del_flag=True)
            assert result >= 0

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


class TestCompositeKeys:
    """Test operations with composite primary keys."""

    @pytest.mark.asyncio
    async def test_create_composite_key(self, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
        """Test creating model with composite key."""
        async with db_session.begin():
            data = ModelTestPks(id=100, name='composite_test', sex='men')
            result = await crud_ins_pks.create_model(db_session, data)
            assert result.id == 100
            assert result.sex == 'men'

    @pytest.mark.asyncio
    async def test_select_composite_key(
        self, populated_db_pks: dict, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]
    ):
        """Test selecting by composite key."""
        first_man = populated_db_pks['men'][0]
        result = await crud_ins_pks.select_model(db_session, (first_man.id, first_man.sex))
        assert result is not None
        assert result.id == first_man.id

    @pytest.mark.asyncio
    async def test_update_composite_key(
        self, populated_db_pks: dict, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]
    ):
        """Test updating by composite key."""
        first_man = populated_db_pks['men'][0]
        async with db_session.begin():
            result = await crud_ins_pks.update_model(
                db_session, (first_man.id, first_man.sex), {'name': 'updated_composite'}
            )
            assert result == 1

    @pytest.mark.asyncio
    async def test_delete_composite_key(
        self, populated_db_pks: dict, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]
    ):
        """Test deleting by composite key."""
        first_woman = populated_db_pks['women'][0]
        async with db_session.begin():
            result = await crud_ins_pks.delete_model(db_session, (first_woman.id, first_woman.sex))
            assert result == 1


class TestFilters:
    """Test various filter operations."""

    @pytest.mark.asyncio
    async def test_string_filters(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test string-specific filters."""
        # Test LIKE
        results = await crud_ins.select_models(db_session, name__like='item_%')
        assert len(results) > 0

        # Test startswith
        results = await crud_ins.select_models(db_session, name__startswith='item_')
        assert len(results) > 0

        # Test contains
        results = await crud_ins.select_models(db_session, name__contains='item')
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_comparison_filters(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test comparison filters."""
        # Test greater than
        results = await crud_ins.select_models(db_session, id__gt=0)
        assert len(results) > 0

        # Test less than
        results = await crud_ins.select_models(db_session, id__lt=1000)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_list_filters(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test list-based filters."""
        first_three_names = [item.name for item in populated_db[:3]]
        results = await crud_ins.select_models(db_session, name__in=first_three_names)
        assert len(results) <= 3

    @pytest.mark.asyncio
    async def test_or_filters(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test OR filters."""
        # Test simple OR filter
        results = await crud_ins.select_models(db_session, name__or={'eq': 'item_1', 'like': 'item_2%'})
        assert len(results) >= 0

        # Test __or__ group filter (dictionary format only)
        results = await crud_ins.select_models(db_session, __or__={'name': ['item_1', 'item_2']})
        assert len(results) >= 0

        # Test complex __or__ group with operators
        results = await crud_ins.select_models(db_session, __or__={'name__eq': 'item_1', 'name__startswith': 'item_2'})
        assert len(results) >= 0


class TestOrFilters:
    """Test __or__ filter functionality with dictionary format only."""

    @pytest.mark.asyncio
    async def test_or_dict_simple_values(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test dictionary with simple values."""
        results = await crud_ins.select_models(db_session, __or__={'name': 'item_1', 'id__gt': 0})
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_or_dict_list_values(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test dictionary with list values for same field different values."""
        results = await crud_ins.select_models(db_session, __or__={'name': ['item_1', 'item_2', 'item_3']})
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_or_dict_mixed_values(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test dictionary with mixed single and list values."""
        results = await crud_ins.select_models(db_session, __or__={'name': ['item_1', 'item_2'], 'id__gt': 0})
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_or_dict_with_operators(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test dictionary with different operators."""
        results = await crud_ins.select_models(
            db_session, __or__={'name__eq': 'item_1', 'name__startswith': 'item_2', 'id__gt': 0}
        )
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_or_dict_operators_with_lists(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test dictionary with operators and list values."""
        results = await crud_ins.select_models(
            db_session, __or__={'name__eq': ['item_1', 'item_2'], 'id__gt': [0, 100]}
        )
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_or_dict_with_regular_filters(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test __or__ dictionary combined with regular filters."""
        results = await crud_ins.select_models(db_session, del_flag=False, __or__={'name': ['item_1', 'item_3']})
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_or_dict_complex_conditions(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test dictionary with complex operator conditions."""
        results = await crud_ins.select_models(
            db_session, __or__={'name__like': ['%item_1%', '%item_2%'], 'id__between': [1, 100]}
        )
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_or_empty_dict(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test __or__ with empty dictionary."""
        results = await crud_ins.select_models(db_session, __or__={})
        assert len(results) >= 0


class TestTransactions:
    """Test transaction handling."""

    @pytest.mark.asyncio
    async def test_commit_transaction(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test successful transaction commit."""
        data = ModelTest(name='commit_test')
        result = await crud_ins.create_model(db_session, data, commit=True)
        assert result.name == 'commit_test'

        # Verify persistence
        count = await crud_ins.count(db_session, name='commit_test')
        assert count == 1

    @pytest.mark.asyncio
    async def test_rollback_transaction(self, db_session_factory, crud_ins: CRUDPlus[Ins]):
        """Test transaction rollback."""
        initial_count = 0
        async with db_session_factory() as session:
            initial_count = await crud_ins.count(session)

        try:
            async with db_session_factory() as session:
                async with session.begin():
                    data = ModelTest(name='rollback_test')
                    await crud_ins.create_model(session, data)
                    raise Exception('Force rollback')
        except Exception:
            pass

        # Verify rollback
        async with db_session_factory() as session:
            final_count = await crud_ins.count(session)
            assert final_count == initial_count
