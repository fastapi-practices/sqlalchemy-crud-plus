#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import (
    CompositePrimaryKeysError,
    ModelColumnError,
    MultipleResultsError,
    SelectOperatorError,
)
from tests.model import Ins, InsPks
from tests.schema import ModelTest


class ErrorTestBase(DeclarativeBase):
    """Base class for error test models."""

    pass


class ModelWithoutDelFlag(ErrorTestBase):
    """Test model without del_flag column."""

    __tablename__ = 'model_without_del_flag'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class TestErrorHandling:
    """Test error handling and exception scenarios."""

    @pytest.mark.asyncio
    async def test_composite_primary_key_errors(self, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
        """Test composite primary key error handling."""
        # Test with wrong number of key components
        with pytest.raises(CompositePrimaryKeysError):
            await crud_ins_pks.select_model(db_session, (1,))  # Missing second key

        with pytest.raises(CompositePrimaryKeysError):
            await crud_ins_pks.select_model(db_session, (1, 'men', 'extra'))  # Too many keys

    @pytest.mark.asyncio
    async def test_model_column_errors(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test model column validation errors."""
        # Test with non-existent column in filter
        with pytest.raises(ModelColumnError):
            await crud_ins.select_models(db_session, nonexistent_column='value')

        # Test with non-existent column in sorting
        with pytest.raises(ModelColumnError):
            await crud_ins.select_models_order(db_session, sort_columns='nonexistent_column')

    @pytest.mark.asyncio
    async def test_multiple_results_errors(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test multiple results error handling."""
        # Test update with multiple matches when not allowed
        with pytest.raises(MultipleResultsError):
            await crud_ins.update_model_by_column(
                db_session, {'name': 'updated'}, allow_multiple=False, name__startswith='item_'
            )

        # Test delete with multiple matches when not allowed
        with pytest.raises(MultipleResultsError):
            await crud_ins.delete_model_by_column(db_session, allow_multiple=False, name__startswith='item_')

    @pytest.mark.asyncio
    async def test_logical_deletion_column_errors(self, db_session: AsyncSession):
        """Test logical deletion with non-existent column."""
        crud_without_del_flag = CRUDPlus(ModelWithoutDelFlag)

        with pytest.raises(ModelColumnError):
            await crud_without_del_flag.delete_model_by_column(
                db_session, logical_deletion=True, deleted_flag_column='del_flag', name='test'
            )

    @pytest.mark.asyncio
    async def test_select_operator_errors(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test invalid operator errors."""
        # Test invalid sort order
        with pytest.raises(SelectOperatorError):
            await crud_ins.select_models_order(db_session, sort_columns='name', sort_orders='invalid_order')

        # Test invalid operator in filter (this should trigger a warning, not an error)
        # The function should return None for unsupported operators
        results = await crud_ins.select_models(db_session, name__invalid_op='test')
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_validation_errors(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test input validation errors."""
        # Test update without filters
        with pytest.raises(ValueError, match='At least one filter condition'):
            await crud_ins.update_model_by_column(db_session, {'name': 'test'})

        # Test delete without filters
        with pytest.raises(ValueError, match='At least one filter condition'):
            await crud_ins.delete_model_by_column(db_session)

    @pytest.mark.asyncio
    async def test_sorting_validation_errors(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test sorting validation errors."""
        from sqlalchemy_crud_plus.errors import ColumnSortError

        # Test mismatched columns and orders count
        with pytest.raises(ColumnSortError):
            await crud_ins.select_models_order(
                db_session,
                sort_columns=['name', 'id'],
                sort_orders=['asc'],  # Only one order for two columns
            )

        # Test providing sort orders without columns
        with pytest.raises(ValueError):
            from sqlalchemy import select

            from sqlalchemy_crud_plus.utils import apply_sorting

            apply_sorting(Ins, select(Ins), None, ['asc'])

    @pytest.mark.asyncio
    async def test_create_with_invalid_data(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test creation with invalid data."""
        # Test with valid data first
        valid_data = ModelTest(name='valid_test')
        result = await crud_ins.create_model(db_session, valid_data)
        assert result.name == 'valid_test'

        # Test with additional kwargs
        result_with_kwargs = await crud_ins.create_model(db_session, valid_data, del_flag=True)
        assert result_with_kwargs.del_flag is True

    @pytest.mark.asyncio
    async def test_update_with_different_data_types(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test update with different data types."""
        first_item = populated_db[0]

        # Test update with dictionary
        dict_update = {'name': 'updated_via_dict'}
        result = await crud_ins.update_model(db_session, first_item.id, dict_update)
        assert result == 1

        # Test update with Pydantic model
        pydantic_update = ModelTest(name='updated_via_pydantic')
        result = await crud_ins.update_model(db_session, first_item.id, pydantic_update)
        assert result == 1

    @pytest.mark.asyncio
    async def test_filter_edge_cases(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test filter edge cases."""
        # Test empty string filter
        results = await crud_ins.select_models(db_session, name='')
        assert isinstance(results, list)

        # Test None value filter
        results = await crud_ins.select_models(db_session, name__is=None)
        assert isinstance(results, list)

        # Test complex OR filter
        results = await crud_ins.select_models(db_session, name__or={'eq': 'item_1', 'like': 'item_2%'})
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_arithmetic_filter_errors(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test arithmetic filter error handling."""
        # Test invalid arithmetic operation structure
        results = await crud_ins.select_models(db_session, id__add={'invalid_structure': 'test'})
        assert isinstance(results, list)

        # Test valid arithmetic operation
        results = await crud_ins.select_models(db_session, id__add={'value': 1, 'condition': {'gt': 0}})
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_list_operator_validation(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test validation for operators that require lists."""
        # These should work without errors
        results = await crud_ins.select_models(db_session, id__in=[1, 2, 3])
        assert isinstance(results, list)

        results = await crud_ins.select_models(db_session, id__between=[1, 10])
        assert isinstance(results, list)

        # Test with invalid input types (should raise error)
        from sqlalchemy_crud_plus.errors import SelectOperatorError

        with pytest.raises(SelectOperatorError):
            await crud_ins.select_models(db_session, id__in='not_a_list')

    @pytest.mark.asyncio
    async def test_exists_edge_cases(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test exists method edge cases."""
        # Test exists with valid filter
        exists = await crud_ins.exists(db_session, name='item_1')
        assert exists is True

        # Test exists with non-matching filter
        exists = await crud_ins.exists(db_session, name='nonexistent')
        assert exists is False

        # Test exists without any filters
        exists = await crud_ins.exists(db_session)
        assert exists is True  # Should return True as table has data

    @pytest.mark.asyncio
    async def test_count_edge_cases(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test count method edge cases."""
        # Test count with filter
        count = await crud_ins.count(db_session, name__startswith='item_')
        assert count == len(populated_db)

        # Test count with non-matching filter
        count = await crud_ins.count(db_session, name='nonexistent')
        assert count == 0

        # Test count without filters
        total_count = await crud_ins.count(db_session)
        assert total_count == len(populated_db)

    @pytest.mark.asyncio
    async def test_transaction_rollback_scenarios(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test transaction rollback scenarios."""
        initial_count = await crud_ins.count(db_session)

        # Test rollback on exception
        try:
            async with db_session.begin():
                data = ModelTest(name='rollback_test')
                await crud_ins.create_model(db_session, data)
                # Force an exception
                raise Exception('Intentional rollback')
        except Exception:
            pass

        # Verify rollback worked
        final_count = await crud_ins.count(db_session)
        assert final_count == initial_count
