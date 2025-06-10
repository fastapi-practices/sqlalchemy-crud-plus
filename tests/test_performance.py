#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import time

import pytest

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from sqlalchemy_crud_plus import CRUDPlus
from tests.model import Ins
from tests.schema import ModelTest


class TestPerformance:
    """Test performance of CRUD operations."""

    @pytest.mark.asyncio
    async def test_bulk_create_performance(
        self, db_session_factory: async_sessionmaker[AsyncSession], crud_ins: CRUDPlus[Ins]
    ):
        """Test bulk creation performance."""
        batch_size = 100
        test_data = [ModelTest(name=f'bulk_item_{i}') for i in range(batch_size)]

        start_time = time.perf_counter()
        async with db_session_factory() as session:
            async with session.begin():
                results = await crud_ins.create_models(session, test_data)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        assert len(results) == batch_size
        assert execution_time < 3.0, f'Batch creation took {execution_time:.3f}s'

    @pytest.mark.asyncio
    async def test_query_performance(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test query performance with filters."""
        start_time = time.perf_counter()
        results = await crud_ins.select_models(db_session, name__startswith='item_')
        query_time = time.perf_counter() - start_time

        assert len(results) > 0
        assert query_time < 1.0, f'Query took {query_time:.3f}s'

    @pytest.mark.asyncio
    async def test_count_vs_exists_performance(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test count vs exists performance."""
        start_time = time.perf_counter()
        count_result = await crud_ins.count(db_session, name__startswith='item_')
        count_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        exists_result = await crud_ins.exists(db_session, name__startswith='item_')
        exists_time = time.perf_counter() - start_time

        assert count_result > 0
        assert exists_result is True
        assert count_time >= 0 and exists_time >= 0

    @pytest.mark.asyncio
    async def test_concurrent_operations(
        self, db_session_factory: async_sessionmaker[AsyncSession], crud_ins: CRUDPlus[Ins]
    ):
        """Test concurrent read operations."""
        # Setup test data
        async with db_session_factory() as session:
            async with session.begin():
                test_data = [ModelTest(name=f'concurrent_{i}') for i in range(20)]
                await crud_ins.create_models(session, test_data)

        async def read_operation(item_id: int):
            """Perform a read operation."""
            async with db_session_factory() as session:
                return await crud_ins.select_models(session, name=f'concurrent_{item_id}')

        # Test concurrent reads
        start_time = time.perf_counter()
        tasks = [read_operation(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        concurrent_time = time.perf_counter() - start_time

        assert len(results) == 5
        assert concurrent_time < 2.0

    @pytest.mark.asyncio
    async def test_sorting_performance(
        self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]
    ):
        """Test sorting performance."""
        start_time = time.perf_counter()
        results = await crud_ins.select_models_order(db_session, sort_columns='name', sort_orders='asc')
        sort_time = time.perf_counter() - start_time

        assert len(results) > 0
        names = [r.name for r in results]
        assert names == sorted(names)
        assert sort_time < 1.0

    @pytest.mark.asyncio
    async def test_update_performance(self, populated_db: list[Ins], db_session: AsyncSession, crud_ins: CRUDPlus[Ins]):
        """Test update performance."""
        start_time = time.perf_counter()
        async with db_session.begin():
            result = await crud_ins.update_model_by_column(
                db_session, {'name': 'bulk_updated'}, allow_multiple=True, del_flag=False
            )
        update_time = time.perf_counter() - start_time

        assert result > 0
        assert update_time < 2.0

    @pytest.mark.asyncio
    async def test_transaction_performance(
        self, db_session_factory: async_sessionmaker[AsyncSession], crud_ins: CRUDPlus[Ins]
    ):
        """Test transaction performance."""
        start_time = time.perf_counter()
        async with db_session_factory() as session:
            async with session.begin():
                test_data = [ModelTest(name=f'tx_test_{i}') for i in range(20)]
                await crud_ins.create_models(session, test_data)
        commit_time = time.perf_counter() - start_time

        # Test rollback
        start_time = time.perf_counter()
        try:
            async with db_session_factory() as session:
                async with session.begin():
                    test_data = [ModelTest(name=f'rollback_test_{i}') for i in range(20)]
                    await crud_ins.create_models(session, test_data)
                    raise Exception('Force rollback')
        except Exception:
            pass
        rollback_time = time.perf_counter() - start_time

        assert commit_time < 2.0
        assert rollback_time < 1.5
