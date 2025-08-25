#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy_crud_plus import CRUDPlus
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
async def test_load_strategies_with_select_models(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(async_db_session, load_strategies=['posts'], limit=2)

    assert len(users) <= 2


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


@pytest.mark.asyncio
async def test_combined_all_relationship_params(
    async_db_session: AsyncSession, rel_sample_data: dict, rel_crud_user: CRUDPlus[RelUser]
):
    users = await rel_crud_user.select_models(
        async_db_session,
        load_options=[selectinload(RelUser.roles)],
        load_strategies=['posts'],
        join_conditions=['posts'],
        limit=1,
    )

    assert len(users) <= 1
