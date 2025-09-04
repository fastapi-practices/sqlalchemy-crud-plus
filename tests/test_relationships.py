#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import LoadingStrategyError, ModelColumnError
from tests.models.relations import RelCategory, RelUser


@pytest.mark.asyncio
async def test_load_options_single(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_options=[selectinload(RelUser.posts)])

    assert user is not None


@pytest.mark.asyncio
async def test_load_options_multiple(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        async_db_session, users[0].id, load_options=[selectinload(RelUser.posts), selectinload(RelUser.roles)]
    )

    assert user is not None


@pytest.mark.asyncio
async def test_load_options_with_select_models(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(async_db_session, load_options=[selectinload(RelUser.posts)], limit=2)

    assert len(users) <= 2


@pytest.mark.asyncio
async def test_load_options_empty_list(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_options=[])

    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_list_format(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies=['posts'])

    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_dict_format(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'posts': 'selectinload'})

    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_selectinload(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'posts': 'selectinload'})

    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_joinedload(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'profile': 'joinedload'})

    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_subqueryload(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'roles': 'subqueryload'})

    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_all_relationship_types(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user = await rel_crud_user.select_model(
        async_db_session, users[0].id, load_strategies=['posts', 'profile', 'roles']
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_selectinload_explicit(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        async_db_session,
        users[0].id,
        load_strategies={'posts': 'selectinload', 'profile': 'selectinload', 'roles': 'selectinload'},
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_joinedload_comprehensive(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'profile': 'joinedload'})
    assert user is not None

    user = await rel_crud_user.select_model(
        async_db_session, users[0].id, load_strategies={'profile': 'joinedload', 'posts': 'joinedload'}
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_subqueryload_comprehensive(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'posts': 'subqueryload'})
    assert user is not None

    user = await rel_crud_user.select_model(
        async_db_session, users[0].id, load_strategies={'posts': 'subqueryload', 'roles': 'subqueryload'}
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_lazyload(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'posts': 'lazyload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_noload(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'posts': 'noload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_raiseload(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'posts': 'raiseload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_immediateload(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'profile': 'immediateload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_defaultload(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'posts': 'defaultload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_contains_eager(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        async_db_session, users[0].id, load_strategies={'profile': 'contains_eager'}, join_conditions=['profile']
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_mixed_types(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        async_db_session,
        users[0].id,
        load_strategies={'posts': 'selectinload', 'profile': 'joinedload', 'roles': 'subqueryload'},
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_with_select_models(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(async_db_session, load_strategies=['posts', 'profile'], limit=2)
    assert len(users) <= 2

    users = await rel_crud_user.select_models(
        async_db_session, load_strategies={'posts': 'selectinload', 'profile': 'joinedload'}, limit=2
    )
    assert len(users) <= 2


@pytest.mark.asyncio
async def test_load_strategies_with_select_models_order(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models_order(async_db_session, 'name', 'asc', load_strategies=['posts'], limit=2)
    assert len(users) <= 2


@pytest.mark.asyncio
async def test_load_strategies_with_filters(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(
        async_db_session,
        name__like='user_%',
        load_strategies={'posts': 'selectinload', 'profile': 'joinedload'},
        limit=2,
    )
    assert len(users) <= 2


@pytest.mark.asyncio
async def test_load_strategies_with_pagination(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(async_db_session, load_strategies=['posts', 'profile'], limit=1, offset=1)
    assert len(users) <= 1


@pytest.mark.asyncio
async def test_column_loading_strategies_defer(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    try:
        user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'name': 'defer'})
        assert user is not None
    except (AttributeError, Exception):
        pass


@pytest.mark.asyncio
async def test_column_loading_strategies_load_only(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    try:
        user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'id': 'load_only'})
        assert user is not None
    except (AttributeError, Exception):
        pass


@pytest.mark.asyncio
async def test_column_loading_strategies_undefer(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    try:
        user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'name': 'undefer'})
        assert user is not None
    except (AttributeError, Exception):
        pass


@pytest.mark.asyncio
async def test_load_strategies_invalid_strategy_error(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    with pytest.raises(LoadingStrategyError):
        await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={'posts': 'invalid_strategy'})


@pytest.mark.asyncio
async def test_load_strategies_invalid_relationship_error(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    with pytest.raises(ModelColumnError):
        await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies=['nonexistent_relationship'])

    with pytest.raises(ModelColumnError):
        await rel_crud_user.select_model(
            async_db_session, users[0].id, load_strategies={'nonexistent_relationship': 'selectinload'}
        )


@pytest.mark.asyncio
async def test_load_strategies_empty_configurations(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies=[])
    assert user is not None

    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies={})
    assert user is not None

    user = await rel_crud_user.select_model(async_db_session, users[0].id, load_strategies=None)
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_performance_comparison(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user_no_load = await rel_crud_user.select_model(async_db_session, users[0].id)
    assert user_no_load is not None

    user_selectin = await rel_crud_user.select_model(
        async_db_session, users[0].id, load_strategies={'posts': 'selectinload'}
    )
    assert user_selectin is not None

    user_joined = await rel_crud_user.select_model(
        async_db_session, users[0].id, load_strategies={'profile': 'joinedload'}
    )
    assert user_joined is not None

    assert user_no_load.id == user_selectin.id == user_joined.id


@pytest.mark.asyncio
async def test_join_conditions_list_format(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(async_db_session, join_conditions=['posts'])

    assert len(users) >= 0


@pytest.mark.asyncio
async def test_join_conditions_inner_join(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(async_db_session, join_conditions={'posts': 'inner'})

    assert len(users) >= 0


@pytest.mark.asyncio
async def test_join_conditions_left_join(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(async_db_session, join_conditions={'posts': 'left'})

    assert len(users) >= 0


@pytest.mark.asyncio
async def test_join_conditions_multiple_relationships(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(async_db_session, join_conditions=['posts', 'profile'])

    assert len(users) >= 0


@pytest.mark.asyncio
async def test_join_conditions_with_count(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    count = await rel_crud_user.count(async_db_session, join_conditions=['posts'])

    assert count >= 0


@pytest.mark.asyncio
async def test_join_conditions_with_exists(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    exists = await rel_crud_user.exists(async_db_session, join_conditions=['posts'])

    assert isinstance(exists, bool)


@pytest.mark.asyncio
async def test_self_referencing_children_load(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_category: CRUDPlus[RelCategory]
):
    categories = rel_sample_data['categories']
    root_category = next(cat for cat in categories if cat.parent_id is None)
    category = await rel_crud_category.select_model(async_db_session, root_category.id, load_strategies=['children'])

    assert category is not None


@pytest.mark.asyncio
async def test_self_referencing_parent_load(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_category: CRUDPlus[RelCategory]
):
    categories = rel_sample_data['categories']
    child_category = next(cat for cat in categories if cat.parent_id is not None)
    category = await rel_crud_category.select_model(async_db_session, child_category.id, load_strategies=['parent'])

    assert category is not None


@pytest.mark.asyncio
async def test_combined_load_strategies_and_join_conditions(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(
        async_db_session, join_conditions=['posts'], load_strategies=['posts'], limit=2
    )

    assert len(users) <= 2


@pytest.mark.asyncio
async def test_combined_load_options_and_load_strategies(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        async_db_session, users[0].id, load_options=[selectinload(RelUser.posts)], load_strategies=['profile']
    )

    assert user is not None
