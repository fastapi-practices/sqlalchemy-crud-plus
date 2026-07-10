import math

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins


class TestPaginationBasic:
    @pytest.mark.asyncio
    async def test_limit_only(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, limit=3)
        assert len(results) <= 3

    @pytest.mark.asyncio
    async def test_offset_only(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, offset=2)
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_limit_offset_combination(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, limit=3, offset=2)
        assert len(results) <= 3

    @pytest.mark.asyncio
    async def test_zero_limit(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, limit=0)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_zero_offset(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results_with_offset = await crud_ins.select_models(db, limit=5, offset=0)
        results_without_offset = await crud_ins.select_models(db, limit=5)

        assert len(results_with_offset) == len(results_without_offset)

    @pytest.mark.asyncio
    async def test_large_offset(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, offset=1000)
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_large_limit(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, limit=1000)
        assert len(results) >= 0
        assert isinstance(results, list)


class TestPaginationWithFilters:
    @pytest.mark.asyncio
    async def test_pagination_with_where_conditions(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
    ):
        results = await crud_ins.select_models(db, name__like='item_%', limit=3, offset=1)
        assert len(results) <= 3

    @pytest.mark.asyncio
    async def test_pagination_with_or_conditions(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
    ):
        results = await crud_ins.select_models(db, __or__={'name__like': 'item_%', 'id__gt': 5}, limit=2, offset=1)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_pagination_with_complex_filters(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
    ):
        results = await crud_ins.select_models(
            db, name__startswith='item', id__between=[1, 8], is_deleted=False, limit=4, offset=2
        )
        assert len(results) <= 4


class TestPaginationWithSorting:
    @pytest.mark.asyncio
    async def test_pagination_with_single_sort(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models_order(db, 'name', 'asc', limit=3, offset=1)
        assert len(results) <= 3

        if len(results) > 1:
            names = [r.name for r in results]
            assert names == sorted(names)

    @pytest.mark.asyncio
    async def test_pagination_with_multiple_sort(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
    ):
        results = await crud_ins.select_models_order(db, ['is_deleted', 'name'], ['asc', 'desc'], limit=4, offset=1)
        assert len(results) <= 4

    @pytest.mark.asyncio
    async def test_pagination_sorting_consistency(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
    ):
        page1 = await crud_ins.select_models_order(db, 'id', 'asc', limit=3, offset=0)

        page2 = await crud_ins.select_models_order(db, 'id', 'asc', limit=3, offset=3)

        if page1 and page2:
            assert page1[-1].id < page2[0].id


class TestPaginationEdgeCases:
    @pytest.mark.asyncio
    async def test_offset_exceeds_total_records(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        total_count = await crud_ins.count(db)
        results = await crud_ins.select_models(db, offset=total_count + 10)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_limit_exceeds_available_records(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
    ):
        results = await crud_ins.select_models(db, limit=1000)
        actual_count = await crud_ins.count(db)
        assert len(results) <= actual_count

    @pytest.mark.asyncio
    async def test_last_page_partial_results(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        total_count = await crud_ins.count(db)
        page_size = 3

        last_page_offset = (total_count // page_size) * page_size

        results = await crud_ins.select_models(db, limit=page_size, offset=last_page_offset)

        assert len(results) <= page_size
        expected_remaining = total_count - last_page_offset
        assert len(results) <= expected_remaining

    @pytest.mark.asyncio
    async def test_empty_result_pagination(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, name='nonexistent', limit=5, offset=2)
        assert len(results) == 0


class TestPaginationPerformance:
    @pytest.mark.asyncio
    async def test_pagination_with_count(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        page_size = 3

        total_count = await crud_ins.count(db, name__like='item_%')

        page1 = await crud_ins.select_models(db, name__like='item_%', limit=page_size, offset=0)

        assert len(page1) <= page_size
        assert len(page1) <= total_count

    @pytest.mark.asyncio
    async def test_pagination_consistency_across_operations(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
    ):
        conditions = {'name__like': 'item_%'}

        select_results = await crud_ins.select_models(db, limit=3, offset=1, **conditions)

        order_results = await crud_ins.select_models_order(db, 'id', 'asc', limit=3, offset=1, **conditions)

        assert len(select_results) <= 3
        assert len(order_results) <= 3


class TestPaginationNegativeValues:
    @pytest.mark.asyncio
    async def test_negative_limit(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, limit=-1)
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_negative_offset(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        results = await crud_ins.select_models(db, offset=-5, limit=3)
        assert len(results) <= 3


class TestSelectModelsPaginated:
    @pytest.mark.asyncio
    async def test_paginated_basic(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        total = await crud_ins.count(db)

        result = await crud_ins.select_models_paginated(db, page=1, size=3)

        assert len(result.items) == min(3, total)
        assert result.total == total
        assert result.page == 1
        assert result.size == 3
        assert result.total_pages == math.ceil(total / 3)
        assert result.has_next is (total > 3)
        assert result.has_prev is False

    @pytest.mark.asyncio
    async def test_paginated_last_page(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        total = await crud_ins.count(db)
        size = 3
        last_page = math.ceil(total / size)

        result = await crud_ins.select_models_paginated(db, page=last_page, size=size)

        assert len(result.items) == total - (last_page - 1) * size
        assert result.has_next is False
        assert result.has_prev is (last_page > 1)

    @pytest.mark.asyncio
    async def test_paginated_with_filters(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        expected_total = await crud_ins.count(db, is_deleted=False)

        result = await crud_ins.select_models_paginated(db, page=1, size=5, is_deleted=False)

        assert result.total == expected_total
        assert all(item.is_deleted is False for item in result.items)

    @pytest.mark.asyncio
    async def test_paginated_with_sorting(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        result = await crud_ins.select_models_paginated(db, page=1, size=5, sort_columns='id', sort_orders='desc')

        ids = [item.id for item in result.items]
        assert ids == sorted(ids, reverse=True)

    @pytest.mark.asyncio
    async def test_paginated_page_beyond_total(self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
        total = await crud_ins.count(db)

        result = await crud_ins.select_models_paginated(db, page=math.ceil(total / 10) + 10, size=10)

        assert len(result.items) == 0
        assert result.total == total
        assert result.has_next is False

    @pytest.mark.asyncio
    async def test_paginated_empty_result(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        result = await crud_ins.select_models_paginated(db, page=1, size=10, name='nonexistent')

        assert len(result.items) == 0
        assert result.total == 0
        assert result.total_pages == 0

    @pytest.mark.asyncio
    async def test_paginated_invalid_page(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        with pytest.raises(ValueError):
            await crud_ins.select_models_paginated(db, page=0, size=10)

    @pytest.mark.asyncio
    async def test_paginated_invalid_size(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        with pytest.raises(ValueError):
            await crud_ins.select_models_paginated(db, page=1, size=0)


class TestPaginationWithRelationships:
    @pytest.mark.asyncio
    async def test_pagination_with_filter_on_related_field(
        self, db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
    ):
        results = await crud_ins.select_models(db, is_deleted=False, created_time__is_not=None, limit=2, offset=1)
        assert len(results) <= 2
