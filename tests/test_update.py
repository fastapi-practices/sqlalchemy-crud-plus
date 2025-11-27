import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins, InsPks
from tests.schemas.basic import CreateIns, CreateInsPks, UpdateIns


@pytest.mark.asyncio
async def test_update_model_by_id(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = UpdateIns(name='updated_item')

    async with db.begin():
        result = await crud_ins.update_model(db, item.id, update_data)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_id_not_found(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    update_data = UpdateIns(name='not_found')

    async with db.begin():
        result = await crud_ins.update_model(db, 99999, update_data)

    assert result == 0


@pytest.mark.asyncio
async def test_update_model_with_flush(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = UpdateIns(name='flush_update')

    result = await crud_ins.update_model(db, item.id, update_data, flush=True)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_with_commit(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = UpdateIns(name='commit_update')

    result = await crud_ins.update_model(db, item.id, update_data, commit=True)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_with_kwargs(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = UpdateIns(name='kwargs_update')

    async with db.begin():
        result = await crud_ins.update_model(db, item.id, update_data, is_deleted=True)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_with_dict(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = {'name': 'dict_update'}

    async with db.begin():
        result = await crud_ins.update_model(db, item.id, update_data)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_basic(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = UpdateIns(name='updated_by_column')

    async with db.begin():
        result = await crud_ins.update_model_by_column(db, update_data, id=item.id)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_not_found(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    update_data = UpdateIns(name='not_found')

    async with db.begin():
        result = await crud_ins.update_model_by_column(db, update_data, name='nonexistent')

    assert result == 0


@pytest.mark.asyncio
async def test_update_model_by_column_allow_multiple(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    update_data = UpdateIns(name='multiple_update')

    before_count = await crud_ins.count(db, is_deleted=False)
    assert before_count > 0

    result = await crud_ins.update_model_by_column(db, update_data, allow_multiple=True, commit=True, is_deleted=False)

    assert result == before_count

    updated_records = await crud_ins.select_models(db, name='multiple_update')
    assert len(updated_records) == before_count


@pytest.mark.asyncio
async def test_update_model_by_column_with_flush(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = UpdateIns(name='flush_column_update')

    result = await crud_ins.update_model_by_column(db, update_data, flush=True, id=item.id)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_with_commit(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = UpdateIns(name='commit_column_update')

    result = await crud_ins.update_model_by_column(db, update_data, commit=True, id=item.id)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_with_dict(db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]):
    item = sample_ins[0]
    update_data = {'name': 'dict_column_update'}

    async with db.begin():
        result = await crud_ins.update_model_by_column(db, update_data, id=item.id)

    assert result == 1


@pytest.mark.asyncio
async def test_update_model_by_column_no_filters_error(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    update_data = UpdateIns(name='no_filters')

    with pytest.raises(ValueError):
        async with db.begin():
            await crud_ins.update_model_by_column(db, update_data)


@pytest.mark.asyncio
async def test_update_model_by_column_multiple_results_error(
    db: AsyncSession, sample_ins: list[Ins], crud_ins: CRUDPlus[Ins]
):
    from sqlalchemy_crud_plus.errors import MultipleResultsError

    update_data = UpdateIns(name='multiple_error')

    with pytest.raises(MultipleResultsError):
        async with db.begin():
            await crud_ins.update_model_by_column(db, update_data, is_deleted=False)


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_true(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [
        CreateIns(name='update_test_1', is_deleted=False),
        CreateIns(name='update_test_2', is_deleted=False),
        CreateIns(name='update_test_3', is_deleted=False),
    ]

    async with db.begin():
        created_items = await crud_ins.create_models(db, create_data)

    update_data = [
        {'id': created_items[0].id, 'name': 'updated_test_1', 'is_deleted': True},
        {'id': created_items[1].id, 'name': 'updated_test_2', 'is_deleted': True},
        {'id': created_items[2].id, 'name': 'updated_test_3', 'is_deleted': True},
    ]

    async with db.begin():
        result = await crud_ins.bulk_update_models(db, update_data, pk_mode=True)

    assert result == 3

    async with db.begin():
        updated_item1 = await crud_ins.select_model(db, created_items[0].id)
        updated_item2 = await crud_ins.select_model(db, created_items[1].id)
        updated_item3 = await crud_ins.select_model(db, created_items[2].id)

    assert updated_item1.name == 'updated_test_1'
    assert updated_item1.is_deleted is True
    assert updated_item2.name == 'updated_test_2'
    assert updated_item2.is_deleted is True
    assert updated_item3.name == 'updated_test_3'
    assert updated_item3.is_deleted is True


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_false(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [
        CreateIns(name='filter_test_1', is_deleted=False),
        CreateIns(name='filter_test_2', is_deleted=False),
    ]

    async with db.begin():
        await crud_ins.create_models(db, create_data)

    update_data = [
        {'name': 'bulk_updated_1'},
        {'name': 'bulk_updated_2'},
    ]

    async with db.begin():
        result = await crud_ins.bulk_update_models(db, update_data, pk_mode=False, is_deleted=False)

    assert result == 2


@pytest.mark.asyncio
async def test_bulk_update_models_with_pydantic_schema(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [CreateIns(name='schema_test')]

    async with db.begin():
        created_items = await crud_ins.create_models(db, create_data)

    update_data = [UpdateIns(name='schema_updated')]

    async with db.begin():
        result = await crud_ins.bulk_update_models(db, update_data, pk_mode=False, id=created_items[0].id)

    assert result == 1


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_false_no_filters_error(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    update_data = [{'name': 'no_filters'}]

    with pytest.raises(ValueError, match='At least one filter condition must be provided'):
        async with db.begin():
            await crud_ins.bulk_update_models(db, update_data, pk_mode=False)


@pytest.mark.asyncio
async def test_bulk_update_models_pkss(db: AsyncSession, crud_ins_pks: CRUDPlus[InsPks]):
    create_data = [
        CreateInsPks(id=2000, name='update_pks_1', sex='male'),
        CreateInsPks(id=2001, name='update_pks_2', sex='female'),
    ]

    async with db.begin():
        await crud_ins_pks.create_models(db, create_data)

    update_data = [
        {'id': 2000, 'sex': 'male', 'name': 'updated_pks_1'},
        {'id': 2001, 'sex': 'female', 'name': 'updated_pks_2'},
    ]

    async with db.begin():
        result = await crud_ins_pks.bulk_update_models(db, update_data, pk_mode=True)

    assert result == 2

    async with db.begin():
        updated_item1 = await crud_ins_pks.select_model(db, (2000, 'male'))
        updated_item2 = await crud_ins_pks.select_model(db, (2001, 'female'))

    assert updated_item1.name == 'updated_pks_1'
    assert updated_item2.name == 'updated_pks_2'


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_false_with_flush(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [
        CreateIns(name='bulk_update_flush_1'),
        CreateIns(name='bulk_update_flush_2'),
    ]

    async with db.begin():
        await crud_ins.create_models(db, create_data)

    update_data = [{'name': 'updated_flush_1'}, {'name': 'updated_flush_2'}]

    result = await crud_ins.bulk_update_models(
        db, update_data, pk_mode=False, flush=True, name__like='bulk_update_flush_%'
    )

    assert result == 2


@pytest.mark.asyncio
async def test_bulk_update_models_pk_mode_false_with_commit(db: AsyncSession, crud_ins: CRUDPlus[Ins]):
    create_data = [
        CreateIns(name='bulk_update_commit_1'),
        CreateIns(name='bulk_update_commit_2'),
    ]

    async with db.begin():
        await crud_ins.create_models(db, create_data)

    update_data = [{'name': 'updated_commit_1'}, {'name': 'updated_commit_2'}]

    result = await crud_ins.bulk_update_models(
        db, update_data, pk_mode=False, commit=True, name__like='bulk_update_commit_%'
    )

    assert result == 2
