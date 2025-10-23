#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus, JoinConfig
from tests.models.no_relationship import NoRelCategory, NoRelPost, NoRelProfile, NoRelUser


@pytest.mark.asyncio
async def test_user_profile_join_raw_query(db: AsyncSession, no_rel_sample_data: dict):
    """Test joining user and profile using raw SQLAlchemy query."""
    stmt = select(NoRelUser, NoRelProfile).join(
        NoRelProfile,
        NoRelUser.id == NoRelProfile.user_id,
        isouter=True,
    )

    result = await db.execute(stmt)
    rows = result.all()

    assert len(rows) >= 3
    for user, profile in rows:
        assert user is not None
        if profile:
            assert profile.user_id == user.id


@pytest.mark.asyncio
async def test_user_profile_join_with_filter(db: AsyncSession, no_rel_sample_data: dict):
    """Test joining with filter - only users with profiles."""
    stmt = (
        select(NoRelUser, NoRelProfile)
        .join(
            NoRelProfile,
            NoRelUser.id == NoRelProfile.user_id,
        )
        .where(NoRelUser.name.like('%User%'))
    )

    result = await db.execute(stmt)
    rows = result.all()

    assert len(rows) >= 2
    for user, profile in rows:
        assert profile.user_id == user.id


# ==================== User and Posts (One-to-Many) ====================


@pytest.mark.asyncio
async def test_user_posts_join_raw_query(db: AsyncSession, no_rel_sample_data: dict):
    """Test joining user and posts."""
    stmt = select(NoRelUser, NoRelPost).join(
        NoRelPost,
        NoRelUser.id == NoRelPost.author_id,
    )

    result = await db.execute(stmt)
    rows = result.all()

    assert len(rows) >= 1
    for user, post in rows:
        assert post.author_id == user.id


@pytest.mark.asyncio
async def test_user_posts_join_using_join_config(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    """Test using JoinConfig for filtering (JOIN is used for filter only)."""
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


# ==================== Category and Posts (One-to-Many) ====================


@pytest.mark.asyncio
async def test_category_posts_join_raw_query(db: AsyncSession, no_rel_sample_data: dict):
    """Test joining category and posts."""
    stmt = select(NoRelCategory, NoRelPost).join(
        NoRelPost,
        NoRelCategory.id == NoRelPost.category_id,
    )

    result = await db.execute(stmt)
    rows = result.all()

    assert len(rows) >= 1
    for category, post in rows:
        assert post.category_id == category.id


@pytest.mark.asyncio
async def test_category_posts_join_using_join_config(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_category: CRUDPlus[NoRelCategory]
):
    """Test using JoinConfig to filter categories with posts."""
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

    assert len(categories) >= 1
    assert all(isinstance(category, NoRelCategory) for category in categories)


# ==================== Multiple JOINs ====================


@pytest.mark.asyncio
async def test_post_with_author_and_category(db: AsyncSession, no_rel_sample_data: dict):
    """Test multiple JOINs: post -> user -> category."""
    stmt = (
        select(NoRelPost, NoRelUser, NoRelCategory)
        .join(NoRelUser, NoRelPost.author_id == NoRelUser.id)
        .join(NoRelCategory, NoRelPost.category_id == NoRelCategory.id, isouter=True)
    )

    result = await db.execute(stmt)
    rows = result.all()

    assert len(rows) >= 1
    for post, user, category in rows:
        assert post.author_id == user.id
        if category:
            assert post.category_id == category.id


# ==================== Practical Business Scenarios ====================


@pytest.mark.asyncio
async def test_get_user_list_with_profiles_dict(db: AsyncSession, no_rel_sample_data: dict):
    """Practical example: Get user list with profiles as dict (API response)."""
    stmt = select(NoRelUser, NoRelProfile).join(
        NoRelProfile,
        NoRelUser.id == NoRelProfile.user_id,
        isouter=True,
    )

    result = await db.execute(stmt)
    rows = result.all()

    user_list = [
        {
            'id': user.id,
            'name': user.name,
            'bio': profile.bio if profile else None,
        }
        for user, profile in rows
    ]

    assert len(user_list) >= 1
    assert all('name' in item for item in user_list)


@pytest.mark.asyncio
async def test_get_posts_with_full_details(db: AsyncSession, no_rel_sample_data: dict):
    """Practical example: Get posts with author and category details."""
    stmt = (
        select(NoRelPost, NoRelUser, NoRelCategory)
        .join(NoRelUser, NoRelPost.author_id == NoRelUser.id)
        .join(NoRelCategory, NoRelPost.category_id == NoRelCategory.id, isouter=True)
    )

    result = await db.execute(stmt)
    rows = result.all()

    post_list = [
        {
            'title': post.title,
            'author_name': user.name,
            'category_name': category.name if category else None,
        }
        for post, user, category in rows
    ]

    assert len(post_list) >= 1
    assert all('author_name' in item for item in post_list)


# ==================== CRUD Operations with JOINs ====================


@pytest.mark.asyncio
async def test_count_with_join_condition(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    """Test count with JOIN condition."""
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


@pytest.mark.asyncio
async def test_exists_with_join_condition(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    """Test exists with JOIN condition."""
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


@pytest.mark.asyncio
async def test_select_models_with_join_filter(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    """Test select_models with JOIN filter."""
    posts = await no_rel_crud_post.select_models(
        db,
        join_conditions=[
            JoinConfig(
                model=NoRelCategory,
                join_on=NoRelPost.category_id == NoRelCategory.id,
                join_type='inner',
            )
        ],
    )

    assert len(posts) >= 1
    assert all(isinstance(post, NoRelPost) for post in posts)
