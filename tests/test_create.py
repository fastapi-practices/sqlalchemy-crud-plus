from datetime import datetime

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins, InsPks
from tests.schemas.basic import CreateIns


@pytest.mark.asyncio
async def test_create_model_basic(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = CreateIns(name='test_item')
        result = await crud_ins.create_model(db, data)

    assert result.name == 'test_item'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_flush(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = CreateIns(name='test_flush')
        result = await crud_ins.create_model(db, data, flush=True)

    assert result.name == 'test_flush'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_commit(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = CreateIns(name='test_commit')
    result = await crud_ins.create_model(db, data, commit=True)

    assert result.name == 'test_commit'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_kwargs(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = CreateIns(name='test_kwargs')
        result = await crud_ins.create_model(db, data, is_deleted=True)

    assert result.name == 'test_kwargs'
    assert result.is_deleted is True


@pytest.mark.asyncio
async def test_create_models_basic(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = [CreateIns(name=f'item_{i}') for i in range(3)]
        results = await crud_ins.create_models(db, data)

    assert len(results) == 3
    assert all(r.name.startswith('item_') for r in results)
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_with_flush(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = [CreateIns(name=f'flush_item_{i}') for i in range(2)]
        results = await crud_ins.create_models(db, data, flush=True)

    assert len(results) == 2
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_with_commit(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = [CreateIns(name=f'commit_item_{i}') for i in range(2)]
    results = await crud_ins.create_models(db, data, commit=True)

    assert len(results) == 2
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_empty_list(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        results = await crud_ins.create_models(db, [])

    assert results == []


@pytest.mark.asyncio
async def test_create_models_with_kwargs(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = [CreateIns(name=f'kwargs_item_{i}') for i in range(2)]
        results = await crud_ins.create_models(db, data, is_deleted=True)

    assert len(results) == 2
    assert all(r.is_deleted is True for r in results)


@pytest.mark.asyncio
async def test_bulk_create_models_basic(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = [
            {'name': 'bulk_item_1', 'is_deleted': False, 'created_time': datetime.now()},
            {'name': 'bulk_item_2', 'is_deleted': True, 'created_time': datetime.now()},
            {'name': 'bulk_item_3', 'is_deleted': False, 'created_time': datetime.now()},
        ]
        results = await crud_ins.bulk_create_models(db, data)

    assert len(results) == 3
    assert results[0].name == 'bulk_item_1'
    assert results[1].name == 'bulk_item_2'
    assert results[2].name == 'bulk_item_3'
    assert results[0].is_deleted is False
    assert results[1].is_deleted is True
    assert results[2].is_deleted is False


@pytest.mark.asyncio
async def test_bulk_create_models_pkss(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    data = [
        {'id': 1000, 'name': 'bulk_pks_1', 'sex': 'male', 'created_time': datetime.now()},
        {'id': 1001, 'name': 'bulk_pks_2', 'sex': 'female', 'created_time': datetime.now()},
        {'id': 1002, 'name': 'bulk_pks_3', 'sex': 'male', 'created_time': datetime.now()},
    ]

    async with db.begin():
        results = await crud_ins_pks.bulk_create_models(db, data)

    assert len(results) == 3
    assert results[0].id == 1000
    assert results[0].name == 'bulk_pks_1'
    assert results[0].sex == 'male'


@pytest.mark.asyncio
async def test_bulk_create_models_with_flush(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = [
        {'name': 'bulk_flush_1', 'is_deleted': False, 'created_time': datetime.now()},
        {'name': 'bulk_flush_2', 'is_deleted': False, 'created_time': datetime.now()},
    ]

    async with db.begin():
        results = await crud_ins.bulk_create_models(db, data, flush=True)

    assert len(results) == 2
    assert results[0].name == 'bulk_flush_1'
    assert results[1].name == 'bulk_flush_2'


@pytest.mark.asyncio
async def test_bulk_create_models_with_commit(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = [
        {'name': 'bulk_commit_1', 'is_deleted': False, 'created_time': datetime.now()},
        {'name': 'bulk_commit_2', 'is_deleted': False, 'created_time': datetime.now()},
    ]

    results = await crud_ins.bulk_create_models(db, data, commit=True)

    assert len(results) == 2
    assert results[0].name == 'bulk_commit_1'
    assert results[1].name == 'bulk_commit_2'


@pytest.mark.asyncio
async def test_create_model_with_dict(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = {'name': 'dict_item'}
        result = await crud_ins.create_model(db, data)

    assert result.name == 'dict_item'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_dict_and_flush(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = {'name': 'dict_flush_item'}
        result = await crud_ins.create_model(db, data, flush=True)

    assert result.name == 'dict_flush_item'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_dict_and_commit(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = {'name': 'dict_commit_item'}
    result = await crud_ins.create_model(db, data, commit=True)

    assert result.name == 'dict_commit_item'
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_model_with_dict_and_kwargs(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = {'name': 'dict_kwargs_item'}
        result = await crud_ins.create_model(db, data, is_deleted=True)

    assert result.name == 'dict_kwargs_item'
    assert result.is_deleted is True


@pytest.mark.asyncio
async def test_create_models_with_dict(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = [{'name': f'dict_batch_{i}'} for i in range(3)]
        results = await crud_ins.create_models(db, data)

    assert len(results) == 3
    assert all(r.name.startswith('dict_batch_') for r in results)
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_with_dict_and_flush(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = [{'name': f'dict_flush_batch_{i}'} for i in range(2)]
        results = await crud_ins.create_models(db, data, flush=True)

    assert len(results) == 2
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_with_dict_and_commit(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    data = [{'name': f'dict_commit_batch_{i}'} for i in range(2)]
    results = await crud_ins.create_models(db, data, commit=True)

    assert len(results) == 2
    assert all(r.id is not None for r in results)


@pytest.mark.asyncio
async def test_create_models_with_dict_and_kwargs(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = [{'name': f'dict_kwargs_batch_{i}'} for i in range(2)]
        results = await crud_ins.create_models(db, data, is_deleted=True)

    assert len(results) == 2
    assert all(r.is_deleted is True for r in results)


@pytest.mark.asyncio
async def test_create_models_with_mixed_input(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    async with db.begin():
        data = [
            CreateIns(name='schema_item'),
            {'name': 'dict_item'},
            CreateIns(name='schema_item_2'),
        ]
        results = await crud_ins.create_models(db, data)

    assert len(results) == 3
    assert results[0].name == 'schema_item'
    assert results[1].name == 'dict_item'
    assert results[2].name == 'schema_item_2'
    assert all(r.id is not None for r in results)
