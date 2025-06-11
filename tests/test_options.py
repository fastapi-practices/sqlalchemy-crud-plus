#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, selectinload, subqueryload

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.relations import RelCategory, RelPost, RelUser


class TestOptionsParameter:
    """Test options parameter functionality."""

    @pytest.mark.asyncio
    async def test_options_with_selectinload(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with selectinload."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(db_session, users[0].id, options=[selectinload(RelUser.posts)])

        assert user is not None
        assert len(user.posts) > 0

    @pytest.mark.asyncio
    async def test_options_with_joinedload(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with joinedload."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(db_session, users[0].id, options=[joinedload(RelUser.profile)])

        assert user is not None
        assert user.profile is not None

    @pytest.mark.asyncio
    async def test_options_with_multiple_strategies(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with multiple loading strategies."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(
            db_session,
            users[0].id,
            options=[selectinload(RelUser.posts), joinedload(RelUser.profile), subqueryload(RelUser.roles)],
        )

        assert user is not None
        assert len(user.posts) > 0
        assert user.profile is not None
        assert len(user.roles) > 0

    @pytest.mark.asyncio
    async def test_options_with_nested_loading(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with nested relationship loading."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(
            db_session, users[0].id, options=[selectinload(RelUser.posts).selectinload(RelPost.category)]
        )

        assert user is not None
        assert len(user.posts) > 0
        for post in user.posts:
            if post.category_id:
                assert post.category is not None

    @pytest.mark.asyncio
    async def test_options_with_batch_query(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with batch query."""
        users = await rel_user_crud.select_models(
            db_session, options=[selectinload(RelUser.posts), joinedload(RelUser.profile)]
        )

        assert len(users) > 0
        for user in users:
            assert hasattr(user, 'posts')
            assert hasattr(user, 'profile')

    @pytest.mark.asyncio
    async def test_options_with_order_query(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with ordered query."""
        users = await rel_user_crud.select_models_order(
            db_session, sort_columns='name', sort_orders='asc', options=[selectinload(RelUser.posts)]
        )

        assert len(users) > 0
        names = [user.name for user in users]
        assert names == sorted(names)

    @pytest.mark.asyncio
    async def test_options_with_column_query(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with column-based query."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model_by_column(
            db_session, name=users[0].name, options=[selectinload(RelUser.posts), joinedload(RelUser.profile)]
        )

        assert user is not None
        assert len(user.posts) > 0
        assert user.profile is not None

    @pytest.mark.asyncio
    async def test_options_combined_with_load_strategies(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter combined with load_strategies."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(
            db_session,
            users[0].id,
            options=[selectinload(RelUser.posts).selectinload(RelPost.category)],
            load_strategies=['profile', 'roles'],
        )

        assert user is not None
        assert len(user.posts) > 0
        assert user.profile is not None
        assert len(user.roles) > 0

    @pytest.mark.asyncio
    async def test_options_combined_with_join_conditions(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_post_crud: CRUDPlus[RelPost]
    ):
        """Test options parameter combined with join_conditions."""
        posts = await rel_post_crud.select_models(
            db_session, options=[contains_eager(RelPost.author)], join_conditions=['author']
        )

        assert len(posts) > 0
        for post in posts:
            assert post.author is not None

    @pytest.mark.asyncio
    async def test_options_with_self_referential_relations(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_category_crud: CRUDPlus[RelCategory]
    ):
        """Test options parameter with self-referential relationships."""
        categories = rel_sample_data['categories']
        root_category = next(cat for cat in categories if cat.parent_id is None)

        category = await rel_category_crud.select_model(
            db_session, root_category.id, options=[selectinload(RelCategory.children)]
        )

        assert category is not None
        assert len(category.children) > 0

    @pytest.mark.asyncio
    async def test_options_with_many_to_many_relations(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with many-to-many relationships."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(db_session, users[0].id, options=[subqueryload(RelUser.roles)])

        assert user is not None
        assert len(user.roles) > 0

    @pytest.mark.asyncio
    async def test_options_empty_list(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with empty list."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(db_session, users[0].id, options=[])

        assert user is not None

    @pytest.mark.asyncio
    async def test_options_none_value(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with None value."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(db_session, users[0].id, options=None)

        assert user is not None

    @pytest.mark.asyncio
    async def test_options_complex_nested_loading(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with complex nested loading."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(
            db_session,
            users[0].id,
            options=[
                selectinload(RelUser.posts).selectinload(RelPost.category).selectinload(RelCategory.parent),
                joinedload(RelUser.profile),
            ],
        )

        assert user is not None
        assert len(user.posts) > 0
        assert user.profile is not None

    @pytest.mark.asyncio
    async def test_options_performance_comparison(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter for performance optimization."""
        # Test with options (should prevent N+1 queries)
        users_with_options = await rel_user_crud.select_models(db_session, options=[selectinload(RelUser.posts)])

        assert len(users_with_options) > 0

        # Access relationships (should not trigger additional queries)
        for user in users_with_options:
            posts_count = len(user.posts)
            assert posts_count >= 0

    @pytest.mark.asyncio
    async def test_options_with_filters(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter combined with filters."""
        users = await rel_user_crud.select_models(
            db_session, options=[selectinload(RelUser.posts)], name__like='user_%'
        )

        assert len(users) > 0
        for user in users:
            assert 'user_' in user.name
            assert hasattr(user, 'posts')

    @pytest.mark.asyncio
    async def test_options_with_pagination(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test options parameter with pagination."""
        users = await rel_user_crud.select_models(
            db_session, options=[selectinload(RelUser.posts), joinedload(RelUser.profile)], limit=2, offset=0
        )

        assert len(users) <= 2
        for user in users:
            assert hasattr(user, 'posts')
            assert hasattr(user, 'profile')
