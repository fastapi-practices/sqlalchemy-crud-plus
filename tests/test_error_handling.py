#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import (
    CompositePrimaryKeysError,
    ModelColumnError,
    MultipleResultsError,
    SelectOperatorError,
)
from tests.models.basic import Ins, InsPks
from tests.schemas.basic import ModelTest


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_composite_key_errors(self, db_session: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
        """Test composite primary key errors."""
        # Wrong number of key components
        with pytest.raises(CompositePrimaryKeysError):
            await crud_ins_pks.select_model(db_session, (1,))

        with pytest.raises(CompositePrimaryKeysError):
            await crud_ins_pks.select_model(db_session, (1, 'men', 'extra'))

    @pytest.mark.asyncio
    async def test_model_column_errors(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test model column validation errors."""
        # Non-existent column in filter
        with pytest.raises(ModelColumnError):
            await crud_ins.select_models(db_session, nonexistent_column='value')

        # Non-existent column in sorting
        with pytest.raises(ModelColumnError):
            await crud_ins.select_models_order(db_session, sort_columns='nonexistent_column')

    @pytest.mark.asyncio
    async def test_multiple_results_errors(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test multiple results error handling."""
        # Update multiple when not allowed
        async with db_session.begin():
            with pytest.raises(MultipleResultsError):
                await crud_ins.update_model_by_column(
                    db_session, {'name': 'should_fail'}, allow_multiple=False, name__startswith='item_'
                )

        # Delete multiple when not allowed
        async with db_session.begin():
            with pytest.raises(MultipleResultsError):
                await crud_ins.delete_model_by_column(db_session, allow_multiple=False, name__startswith='item_')

    @pytest.mark.asyncio
    async def test_validation_errors(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test input validation errors."""
        # Update without filters
        async with db_session.begin():
            with pytest.raises(ValueError, match='At least one filter condition'):
                await crud_ins.update_model_by_column(db_session, {'name': 'test'})

        # Delete without filters
        async with db_session.begin():
            with pytest.raises(ValueError, match='At least one filter condition'):
                await crud_ins.delete_model_by_column(db_session)

    @pytest.mark.asyncio
    async def test_sort_validation_errors(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test sorting validation errors."""
        # Invalid sort order
        with pytest.raises(SelectOperatorError):
            await crud_ins.select_models_order(db_session, sort_columns='name', sort_orders='invalid_order')

    @pytest.mark.asyncio
    async def test_logical_deletion_column_error(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test logical deletion with invalid column."""
        async with db_session.begin():
            with pytest.raises(ModelColumnError):
                await crud_ins.delete_model_by_column(
                    db_session, logical_deletion=True, deleted_flag_column='nonexistent_column', name='test'
                )

    @pytest.mark.asyncio
    async def test_nonexistent_record_operations(self, db_session_factory, crud_ins: CRUDPlus[Ins]):
        """Test operations on non-existent records."""
        # Select non-existent
        async with db_session_factory() as session:
            result = await crud_ins.select_model(session, 99999)
            assert result is None

        # Update non-existent
        async with db_session_factory() as session:
            async with session.begin():
                result = await crud_ins.update_model(session, 99999, {'name': 'test'})
                assert result == 0

        # Delete non-existent
        async with db_session_factory() as session:
            async with session.begin():
                result = await crud_ins.delete_model(session, 99999)
                assert result == 0

    @pytest.mark.asyncio
    async def test_empty_operations(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test operations with empty data."""
        # Create empty list
        async with db_session.begin():
            results = await crud_ins.create_models(db_session, [])
            assert len(results) == 0

        # Count with no matches
        count = await crud_ins.count(db_session, name='nonexistent')
        assert count == 0

        # Exists with no matches
        exists = await crud_ins.exists(db_session, name='nonexistent')
        assert exists is False

    @pytest.mark.asyncio
    async def test_special_character_handling(self, db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test handling of special characters."""
        special_names = ["test'quote", 'test"double', 'test\\backslash']

        # Create with special characters
        async with db_session.begin():
            for name in special_names:
                data = ModelTest(name=name)
                result = await crud_ins.create_model(db_session, data)
                assert result.name == name

        # Query with special characters
        for name in special_names:
            results = await crud_ins.select_models(db_session, name=name)
            assert len(results) == 1
            assert results[0].name == name
