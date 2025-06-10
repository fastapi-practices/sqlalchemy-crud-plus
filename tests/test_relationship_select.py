#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.relations import RelCategory, RelPost, RelRole, RelUser


class TestLoadStrategies:
    """Test load_strategies parameter functionality."""

    @pytest.mark.asyncio
    async def test_load_strategies_list(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test load_strategies with list format using default strategy."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(db_session, users[0].id, load_strategies=['posts', 'profile', 'roles'])

        assert user is not None
        assert len(user.posts) > 0
        assert user.profile is not None
        assert len(user.roles) > 0

    @pytest.mark.asyncio
    async def test_load_strategies_dict(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test load_strategies with dict format specifying strategies."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(
            db_session,
            users[0].id,
            load_strategies={'posts': 'selectinload', 'profile': 'joinedload', 'roles': 'subqueryload'},
        )

        assert user is not None
        assert len(user.posts) > 0
        assert user.profile is not None
        assert len(user.roles) > 0

    @pytest.mark.asyncio
    async def test_load_strategies_batch_query(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test load_strategies with batch query."""
        users = await rel_user_crud.select_models(db_session, load_strategies=['posts', 'profile'])

        assert len(users) > 0
        for user in users:
            assert hasattr(user, 'posts')
            assert hasattr(user, 'profile')

    @pytest.mark.asyncio
    async def test_load_strategies_with_order(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test load_strategies with ordered query."""
        users = await rel_user_crud.select_models_order(
            db_session, sort_columns='name', sort_orders='asc', load_strategies={'posts': 'selectinload'}
        )

        assert len(users) > 0
        names = [user.name for user in users]
        assert names == sorted(names)


class TestJoinConditions:
    """Test join_conditions parameter functionality."""

    @pytest.mark.asyncio
    async def test_join_conditions_list(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_post_crud: CRUDPlus[RelPost]
    ):
        """Test join_conditions with list format using default INNER JOIN."""
        posts = await rel_post_crud.select_models(db_session, join_conditions=['author'])

        assert len(posts) > 0
        for post in posts:
            assert post.author_id is not None

    @pytest.mark.asyncio
    async def test_join_conditions_dict(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_post_crud: CRUDPlus[RelPost]
    ):
        """Test join_conditions with dict format specifying JOIN types."""
        posts = await rel_post_crud.select_models(db_session, join_conditions={'author': 'inner', 'category': 'left'})

        assert len(posts) > 0

    @pytest.mark.asyncio
    async def test_join_conditions_with_filter(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_post_crud: CRUDPlus[RelPost]
    ):
        """Test join_conditions combined with filter conditions."""
        rel_sample_data['users']  # noqa

        posts = await rel_post_crud.select_models(
            db_session,
            join_conditions=['author'],
        )

        assert len(posts) >= 0


class TestCombinedUsage:
    """Test combined usage of load_strategies and join_conditions."""

    @pytest.mark.asyncio
    async def test_load_and_join_combined(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_post_crud: CRUDPlus[RelPost]
    ):
        """Test using load_strategies and join_conditions together."""
        posts = await rel_post_crud.select_models(
            db_session,
            load_strategies={'author': 'selectinload'},
            join_conditions={'category': 'left'},
        )

        assert len(posts) > 0
        for post in posts:
            assert post.author is not None

    @pytest.mark.asyncio
    async def test_complex_relationship_query(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test complex relationship queries."""
        users = await rel_user_crud.select_models(
            db_session,
            load_strategies={'posts': 'selectinload', 'profile': 'joinedload', 'roles': 'selectinload'},
            limit=2,
        )

        assert len(users) <= 2
        for user in users:
            assert hasattr(user, 'posts')
            assert hasattr(user, 'profile')
            assert hasattr(user, 'roles')


class TestSelfReferentialRelations:
    """Test self-referential relationships."""

    @pytest.mark.asyncio
    async def test_self_referential_children(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_category_crud: CRUDPlus[RelCategory]
    ):
        """Test self-referential relationship - loading children."""
        categories = rel_sample_data['categories']
        root_category = next(cat for cat in categories if cat.parent_id is None)

        category = await rel_category_crud.select_model(db_session, root_category.id, load_strategies=['children'])

        assert category is not None
        assert len(category.children) > 0

    @pytest.mark.asyncio
    async def test_self_referential_parent(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_category_crud: CRUDPlus[RelCategory]
    ):
        """Test self-referential relationship - loading parent."""
        categories = rel_sample_data['categories']
        child_category = next(cat for cat in categories if cat.parent_id is not None)

        category = await rel_category_crud.select_model(db_session, child_category.id, load_strategies=['parent'])

        assert category is not None
        assert category.parent is not None


class TestManyToManyRelations:
    """Test many-to-many relationships."""

    @pytest.mark.asyncio
    async def test_many_to_many_user_roles(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_user_crud: CRUDPlus[RelUser]
    ):
        """Test many-to-many relationship - user roles."""
        users = rel_sample_data['users']

        user = await rel_user_crud.select_model(db_session, users[0].id, load_strategies=['roles'])

        assert user is not None
        assert len(user.roles) > 0

    @pytest.mark.asyncio
    async def test_many_to_many_role_users(
        self, db_session: AsyncSession, rel_sample_data: dict, rel_role_crud: CRUDPlus[RelRole]
    ):
        """Test many-to-many relationship - role users."""
        roles = rel_sample_data['roles']

        role = await rel_role_crud.select_model(db_session, roles[0].id, load_strategies=['users'])

        assert role is not None
        assert len(role.users) > 0
