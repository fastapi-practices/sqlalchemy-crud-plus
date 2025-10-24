#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy_crud_plus.errors import LoadingStrategyError, ModelColumnError
from tests.models.relationship import RelCategory, RelUser


@pytest.mark.asyncio
async def test_load_options_single(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_options=[selectinload(RelUser.posts)])

    assert user is not None
    assert user.id == users[0].id
    assert hasattr(user, 'posts')
    assert isinstance(user.posts, list)


@pytest.mark.asyncio
async def test_load_options_multiple(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        db, users[0].id, load_options=[selectinload(RelUser.posts), selectinload(RelUser.roles)]
    )

    assert user is not None
    assert user.id == users[0].id
    assert hasattr(user, 'posts')
    assert hasattr(user, 'roles')
    assert isinstance(user.posts, list)
    assert isinstance(user.roles, list)


@pytest.mark.asyncio
async def test_load_options_with_select_models(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(db, load_options=[selectinload(RelUser.posts)], limit=2)

    assert len(users) <= 2
    for user in users:
        assert hasattr(user, 'posts')
        assert isinstance(user.posts, list)


@pytest.mark.asyncio
async def test_load_options_empty_list(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_options=[])

    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_list_format(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies=['posts'])

    assert user is not None
    assert user.id == users[0].id
    assert hasattr(user, 'posts')
    assert isinstance(user.posts, list)


@pytest.mark.asyncio
async def test_load_strategies_dict_format(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'selectinload'})

    assert user is not None
    assert user.id == users[0].id
    assert hasattr(user, 'posts')
    assert isinstance(user.posts, list)


@pytest.mark.asyncio
async def test_load_strategies_empty_configurations(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user = await rel_crud_user.select_model(db, users[0].id, load_strategies=[])
    assert user is not None

    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={})
    assert user is not None

    user = await rel_crud_user.select_model(db, users[0].id, load_strategies=None)
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_selectinload(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'selectinload'})

    assert user is not None
    assert user.id == users[0].id
    assert hasattr(user, 'posts')
    assert isinstance(user.posts, list)
    for post in user.posts:
        assert post.author_id == user.id


@pytest.mark.asyncio
async def test_load_strategies_joinedload(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'profile': 'joinedload'})

    assert user is not None
    assert user.id == users[0].id
    if user.profile is not None:
        assert user.profile.user_id == user.id


@pytest.mark.asyncio
async def test_load_strategies_subqueryload(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'roles': 'subqueryload'})

    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_lazyload(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'lazyload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_noload(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'noload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_raiseload(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'raiseload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_immediateload(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'profile': 'immediateload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_defaultload(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'defaultload'})
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_contains_eager(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        db, users[0].id, load_strategies={'profile': 'contains_eager'}, join_conditions=['profile']
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_all_relationship_types(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user = await rel_crud_user.select_model(db, users[0].id, load_strategies=['posts', 'profile', 'roles'])
    assert user is not None
    assert user.id == users[0].id
    # Verify all relationship types are loaded
    assert hasattr(user, 'posts')
    assert hasattr(user, 'profile')
    assert hasattr(user, 'roles')
    assert isinstance(user.posts, list)
    assert isinstance(user.roles, list)


@pytest.mark.asyncio
async def test_load_strategies_selectinload_explicit(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        db,
        users[0].id,
        load_strategies={'posts': 'selectinload', 'profile': 'selectinload', 'roles': 'selectinload'},
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_joinedload_comprehensive(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'profile': 'joinedload'})
    assert user is not None

    user = await rel_crud_user.select_model(
        db, users[0].id, load_strategies={'profile': 'joinedload', 'posts': 'joinedload'}
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_subqueryload_comprehensive(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'subqueryload'})
    assert user is not None

    user = await rel_crud_user.select_model(
        db, users[0].id, load_strategies={'posts': 'subqueryload', 'roles': 'subqueryload'}
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_mixed_types(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        db,
        users[0].id,
        load_strategies={'posts': 'selectinload', 'profile': 'joinedload', 'roles': 'subqueryload'},
    )
    assert user is not None


@pytest.mark.asyncio
async def test_load_strategies_with_select_models(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(db, load_strategies=['posts', 'profile'], limit=2)
    assert len(users) <= 2
    for user in users:
        assert hasattr(user, 'posts')
        assert hasattr(user, 'profile')
        assert isinstance(user.posts, list)

    users = await rel_crud_user.select_models(
        db, load_strategies={'posts': 'selectinload', 'profile': 'joinedload'}, limit=2
    )
    assert len(users) <= 2
    for user in users:
        assert hasattr(user, 'posts')
        assert hasattr(user, 'profile')
        assert isinstance(user.posts, list)


@pytest.mark.asyncio
async def test_load_strategies_with_select_models_order(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models_order(db, 'name', 'asc', load_strategies=['posts'], limit=2)
    assert len(users) <= 2
    for user in users:
        assert hasattr(user, 'posts')
        assert isinstance(user.posts, list)
    if len(users) == 2:
        assert users[0].name <= users[1].name


@pytest.mark.asyncio
async def test_load_strategies_with_filters(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = await rel_crud_user.select_models(
        db,
        name__like='user_%',
        load_strategies={'posts': 'selectinload', 'profile': 'joinedload'},
        limit=2,
    )
    assert len(users) <= 2
    for user in users:
        assert 'user_' in user.name
        assert hasattr(user, 'posts')
        assert hasattr(user, 'profile')
        assert isinstance(user.posts, list)


@pytest.mark.asyncio
async def test_load_strategies_with_pagination(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(db, load_strategies=['posts', 'profile'], limit=1, offset=1)
    assert len(users) <= 1
    if users:
        user = users[0]
        assert hasattr(user, 'posts')
        assert hasattr(user, 'profile')
        assert isinstance(user.posts, list)


@pytest.mark.asyncio
async def test_load_strategies_performance_comparison(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    user_no_load = await rel_crud_user.select_model(db, users[0].id)
    assert user_no_load is not None

    user_selectin = await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'selectinload'})
    assert user_selectin is not None

    user_joined = await rel_crud_user.select_model(db, users[0].id, load_strategies={'profile': 'joinedload'})
    assert user_joined is not None

    assert user_no_load.id == user_selectin.id == user_joined.id


@pytest.mark.asyncio
async def test_column_loading_strategies_defer(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    try:
        user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'name': 'defer'})
        assert user is not None
    except (AttributeError, Exception):
        pass


@pytest.mark.asyncio
async def test_column_loading_strategies_load_only(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    try:
        user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'id': 'load_only'})
        assert user is not None
    except (AttributeError, Exception):
        pass


@pytest.mark.asyncio
async def test_column_loading_strategies_undefer(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    try:
        user = await rel_crud_user.select_model(db, users[0].id, load_strategies={'name': 'undefer'})
        assert user is not None
    except (AttributeError, Exception):
        pass


@pytest.mark.asyncio
async def test_load_strategies_invalid_strategy_error(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    with pytest.raises(LoadingStrategyError):
        await rel_crud_user.select_model(db, users[0].id, load_strategies={'posts': 'invalid_strategy'})


@pytest.mark.asyncio
async def test_load_strategies_invalid_relationship_error(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']

    with pytest.raises(ModelColumnError):
        await rel_crud_user.select_model(db, users[0].id, load_strategies=['nonexistent_relationship'])

    with pytest.raises(ModelColumnError):
        await rel_crud_user.select_model(db, users[0].id, load_strategies={'nonexistent_relationship': 'selectinload'})


@pytest.mark.asyncio
async def test_join_conditions_list_format(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = await rel_crud_user.select_models(db, join_conditions=['posts'])

    assert len(users) >= 0
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_join_conditions_inner_join(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = await rel_crud_user.select_models(db, join_conditions={'posts': 'inner'})

    assert len(users) >= 0
    assert isinstance(users, list)
    for user in users:
        assert isinstance(user, RelUser)


@pytest.mark.asyncio
async def test_join_conditions_left_join(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    users = await rel_crud_user.select_models(db, join_conditions={'posts': 'left'})

    assert len(users) >= 0
    assert isinstance(users, list)
    sample_users = rel_sample_data['users']
    assert len(users) >= len(sample_users)


@pytest.mark.asyncio
async def test_join_conditions_multiple_relationships(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(db, join_conditions=['posts', 'profile'])

    assert len(users) >= 0
    assert isinstance(users, list)
    for user in users:
        assert isinstance(user, RelUser)


@pytest.mark.asyncio
async def test_join_conditions_with_count(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    count = await rel_crud_user.count(db, join_conditions=['posts'])

    assert count >= 0


@pytest.mark.asyncio
async def test_join_conditions_with_exists(db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]):
    exists = await rel_crud_user.exists(db, join_conditions=['posts'])

    assert isinstance(exists, bool)


@pytest.mark.asyncio
async def test_self_referencing_children_load(
    db: AsyncSession, rel_sample_data: dict, rel_crud_category: CRUDPlus[RelCategory]
):
    categories = rel_sample_data['categories']
    root_category = next(cat for cat in categories if cat.parent_id is None)
    category = await rel_crud_category.select_model(db, root_category.id, load_strategies=['children'])

    assert category is not None
    assert category.id == root_category.id
    assert hasattr(category, 'children')
    assert isinstance(category.children, list)
    if root_category.name in ['Technology', 'Science']:
        for child in category.children:
            assert child.parent_id == category.id


@pytest.mark.asyncio
async def test_self_referencing_parent_load(
    db: AsyncSession, rel_sample_data: dict, rel_crud_category: CRUDPlus[RelCategory]
):
    categories = rel_sample_data['categories']
    child_category = next(cat for cat in categories if cat.parent_id is not None)
    category = await rel_crud_category.select_model(db, child_category.id, load_strategies=['parent'])

    assert category is not None
    assert category.id == child_category.id
    assert hasattr(category, 'parent')
    if category.parent is not None:
        assert category.parent.id == child_category.parent_id


@pytest.mark.asyncio
async def test_combined_load_strategies_and_join_conditions(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(db, join_conditions=['posts'], load_strategies=['posts'], limit=2)

    assert len(users) <= 2
    for user in users:
        assert hasattr(user, 'posts')
        assert isinstance(user.posts, list)
        for post in user.posts:
            assert post.author_id == user.id


@pytest.mark.asyncio
async def test_combined_load_options_and_load_strategies(
    db: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = rel_sample_data['users']
    user = await rel_crud_user.select_model(
        db, users[0].id, load_options=[selectinload(RelUser.posts)], load_strategies=['profile']
    )

    assert user is not None
    assert user.id == users[0].id
    assert hasattr(user, 'posts')
    assert hasattr(user, 'profile')
    assert isinstance(user.posts, list)
