#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus, JoinConfig
from tests.models.no_relationship import NoRelCategory, NoRelPost, NoRelProfile, NoRelUser


@pytest.mark.asyncio
async def test_join_conditions_list_format(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelPost,
                join_on=NoRelUser.id == NoRelPost.author_id,
                join_type='inner',
            )
        ],
    )

    assert len(users) >= 0
    assert all(isinstance(user, NoRelUser) for user in users)


@pytest.mark.asyncio
async def test_join_conditions_inner_join(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.id == NoRelProfile.user_id,
                join_type='inner',
            )
        ],
    )

    assert len(users) >= 1
    assert all(isinstance(user, NoRelUser) for user in users)


@pytest.mark.asyncio
async def test_join_conditions_left_join(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.id == NoRelProfile.user_id,
                join_type='left',
            )
        ],
    )

    sample_users = no_rel_sample_data['users']
    assert len(users) >= len(sample_users)
    assert all(isinstance(user, NoRelUser) for user in users)


@pytest.mark.asyncio
async def test_join_conditions_multiple(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    posts = await no_rel_crud_post.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelUser,
                join_on=NoRelPost.author_id == NoRelUser.id,
                join_type='inner',
            ),
            JoinConfig(
                model=NoRelCategory,
                join_on=NoRelPost.category_id == NoRelCategory.id,
                join_type='left',
            ),
        ],
    )

    assert len(posts) >= 0
    assert all(isinstance(post, NoRelPost) for post in posts)


@pytest.mark.asyncio
async def test_join_with_filter(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]):
    posts = await no_rel_crud_post.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelCategory,
                join_on=NoRelPost.category_id == NoRelCategory.id,
                join_type='inner',
            )
        ],
        title__like='%Post%',
    )

    assert len(posts) >= 0
    assert all(isinstance(post, NoRelPost) for post in posts)
    assert all('Post' in post.title for post in posts)


@pytest.mark.asyncio
async def test_join_with_order(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = await no_rel_crud_user.select_models_order(
        db,
        'name',
        'asc',
        join_conditions=[
            JoinConfig(
                model=NoRelPost,
                join_on=NoRelUser.id == NoRelPost.author_id,
                join_type='inner',
            )
        ],
    )

    assert len(users) >= 0
    if len(users) >= 2:
        assert users[0].name <= users[1].name


@pytest.mark.asyncio
async def test_join_with_pagination(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = await no_rel_crud_user.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelPost,
                join_on=NoRelUser.id == NoRelPost.author_id,
                join_type='inner',
            )
        ],
        limit=2,
        offset=0,
    )

    assert len(users) <= 2
    assert all(isinstance(user, NoRelUser) for user in users)


@pytest.mark.asyncio
async def test_count_with_join_condition(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    count = await no_rel_crud_user.count(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.id == NoRelProfile.user_id,
                join_type='inner',
            )
        ],
    )

    assert count >= 1
    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_exists_with_join_condition(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    exists = await no_rel_crud_post.exists(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelCategory,
                join_on=NoRelPost.category_id == NoRelCategory.id,
                join_type='inner',
            )
        ],
    )

    assert exists is True
    assert isinstance(exists, bool)


@pytest.mark.asyncio
async def test_combined_join_filter_order(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    posts = await no_rel_crud_post.select_models_order(
        db,
        'title',
        'asc',
        join_conditions=[
            JoinConfig(
                model=NoRelUser,
                join_on=NoRelPost.author_id == NoRelUser.id,
                join_type='inner',
            )
        ],
        title__like='%Post%',
    )

    assert len(posts) >= 0
    assert all('Post' in post.title for post in posts)
    if len(posts) >= 2:
        assert posts[0].title <= posts[1].title


@pytest.mark.asyncio
async def test_combined_join_count_filter(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    count = await no_rel_crud_post.count(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelCategory,
                join_on=NoRelPost.category_id == NoRelCategory.id,
                join_type='inner',
            )
        ],
    )

    assert count >= 0
    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_category_posts_join(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_category: CRUDPlus[NoRelCategory]
):
    categories = await no_rel_crud_category.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelPost,
                join_on=NoRelCategory.id == NoRelPost.category_id,
                join_type='inner',
            )
        ],
    )

    assert len(categories) >= 0
    assert all(isinstance(category, NoRelCategory) for category in categories)


@pytest.mark.asyncio
async def test_post_with_author_and_category_join(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    posts = await no_rel_crud_post.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelUser,
                join_on=NoRelPost.author_id == NoRelUser.id,
                join_type='inner',
            ),
            JoinConfig(
                model=NoRelCategory,
                join_on=NoRelPost.category_id == NoRelCategory.id,
                join_type='left',
            ),
        ],
    )

    assert len(posts) >= 0
    assert all(isinstance(post, NoRelPost) for post in posts)


@pytest.mark.asyncio
async def test_user_profile_join_with_filter(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.id == NoRelProfile.user_id,
                join_type='inner',
            )
        ],
        name__like='%User%',
    )

    assert len(users) >= 0
    assert all('User' in user.name for user in users)


@pytest.mark.asyncio
async def test_join_filter_with_join_conditions(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelPost,
                join_on=NoRelUser.id == NoRelPost.author_id,
                join_type='inner',
            )
        ],
    )

    assert len(users) >= 1
    assert all(isinstance(user, NoRelUser) for user in users)


@pytest.mark.asyncio
async def test_join_with_fill_result_true(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    results = await no_rel_crud_user.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.id == NoRelProfile.user_id,
                join_type='left',
                fill_result=True,
            )
        ],
    )

    assert len(results) >= 1
    for result in results:
        assert isinstance(result, (tuple, Row))
        assert len(result) == 2
        assert isinstance(result[0], NoRelUser)
        if result[1]:
            assert isinstance(result[1], NoRelProfile)


@pytest.mark.asyncio
async def test_join_with_fill_result_false(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.id == NoRelProfile.user_id,
                join_type='left',
                fill_result=False,
            )
        ],
    )

    assert len(users) >= 1
    for user in users:
        assert isinstance(user, NoRelUser)
        assert not isinstance(user, tuple)


@pytest.mark.asyncio
async def test_join_multiple_with_fill_result(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    results = await no_rel_crud_post.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelUser,
                join_on=NoRelPost.author_id == NoRelUser.id,
                join_type='inner',
                fill_result=True,
            ),
            JoinConfig(
                model=NoRelCategory,
                join_on=NoRelPost.category_id == NoRelCategory.id,
                join_type='left',
                fill_result=True,
            ),
        ],
    )

    assert len(results) >= 1
    for result in results:
        assert isinstance(result, (tuple, Row))
        assert len(result) == 3
        assert isinstance(result[0], NoRelPost)
        assert isinstance(result[1], NoRelUser)
        if result[2]:
            assert isinstance(result[2], NoRelCategory)


@pytest.mark.asyncio
async def test_join_fill_result_single_model(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    user_id = no_rel_sample_data['users'][0].id
    result = await no_rel_crud_user.select_model(
        db,
        user_id,
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.id == NoRelProfile.user_id,
                join_type='left',
                fill_result=True,
            )
        ],
    )

    if result is not None:
        assert isinstance(result, (tuple, Row))
        assert isinstance(result[0], NoRelUser)
        if result[1]:
            assert isinstance(result[1], NoRelProfile)


@pytest.mark.asyncio
async def test_join_fill_result_with_order(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    results = await no_rel_crud_user.select_models_order(
        db,
        'name',
        'asc',
        join_conditions=[
            JoinConfig(
                model=NoRelProfile,
                join_on=NoRelUser.id == NoRelProfile.user_id,
                join_type='left',
                fill_result=True,
            )
        ],
    )

    assert len(results) >= 1
    for result in results:
        assert isinstance(result, (tuple, Row))
        assert isinstance(result[0], NoRelUser)

    if len(results) >= 2:
        assert results[0][0].name <= results[1][0].name
