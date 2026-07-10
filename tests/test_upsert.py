from datetime import datetime

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import ModelColumnError
from tests.models.basic import Ins, InsPks
from tests.schemas.basic import CreateIns


class TestUpsertInsert:
    @pytest.mark.asyncio
    async def test_upsert_inserts_new_record(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        result = await crud_ins.upsert_model(db, {'name': 'upsert_new', 'created_time': datetime.now()}, flush=True)

        assert result is not None
        assert result.name == 'upsert_new'
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_upsert_with_pydantic_schema(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        result = await crud_ins.upsert_model(
            db, CreateIns(name='upsert_schema'), flush=True, created_time=datetime.now()
        )

        assert result is not None
        assert result.name == 'upsert_schema'

    @pytest.mark.asyncio
    async def test_upsert_with_kwargs(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        result = await crud_ins.upsert_model(
            db, {'name': 'upsert_kwargs', 'created_time': datetime.now()}, flush=True, deleted=5
        )

        assert result is not None
        assert result.deleted == 5


class TestUpsertUpdate:
    @pytest.mark.asyncio
    async def test_upsert_updates_on_pk_conflict(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        created = await crud_ins.upsert_model(db, {'name': 'before_update', 'created_time': datetime.now()}, flush=True)
        assert created is not None

        result = await crud_ins.upsert_model(
            db, {'id': created.id, 'name': 'after_update', 'created_time': datetime.now()}, flush=True
        )

        assert result is not None
        assert result.id == created.id
        assert result.name == 'after_update'

        total = await crud_ins.count(db, name__in=['before_update', 'after_update'])
        assert total == 1

    @pytest.mark.asyncio
    async def test_upsert_with_composite_pk(self, db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
        created = await crud_ins_pks.upsert_model(
            db, {'id': 2000, 'sex': 'men', 'name': 'first', 'created_time': datetime.now()}, flush=True
        )
        assert created is not None

        result = await crud_ins_pks.upsert_model(
            db, {'id': 2000, 'sex': 'men', 'name': 'second', 'created_time': datetime.now()}, flush=True
        )

        assert result is not None
        assert result.name == 'second'

        total = await crud_ins_pks.count(db, id=2000, sex='men')
        assert total == 1

    @pytest.mark.asyncio
    async def test_upsert_with_update_columns(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        created = await crud_ins.upsert_model(
            db, {'name': 'partial', 'deleted': 1, 'created_time': datetime.now()}, flush=True
        )
        assert created is not None

        result = await crud_ins.upsert_model(
            db,
            {'id': created.id, 'name': 'partial_updated', 'deleted': 99, 'created_time': datetime.now()},
            update_columns=['name'],
            flush=True,
        )

        assert result is not None
        assert result.name == 'partial_updated'
        assert result.deleted == 1


class TestUpsertErrors:
    @pytest.mark.asyncio
    async def test_upsert_invalid_conflict_column(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        with pytest.raises(ModelColumnError):
            await crud_ins.upsert_model(db, {'name': 'x'}, conflict_columns=['not_a_column'])

    @pytest.mark.asyncio
    async def test_upsert_invalid_update_column(self, db: AsyncSession, crud_ins: CRUDPlus[Ins]):
        with pytest.raises(ModelColumnError):
            await crud_ins.upsert_model(db, {'name': 'x'}, update_columns=['not_a_column'])
