#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Base as BasicBase
from tests.models.basic import Ins, InsPks
from tests.models.relations import RelationBase, RelCategory, RelPost, RelProfile, RelRole, RelUser, user_role
from tests.schemas.relations import RelPostCreate, RelProfileCreate, RelRoleCreate, RelUserCreate

# Database configuration
_async_engine = create_async_engine('sqlite+aiosqlite:///:memory:', future=True, echo=False)
_async_session_factory = async_sessionmaker(_async_engine, autoflush=False, expire_on_commit=False)


@pytest_asyncio.fixture(scope='function', autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Setup and teardown database for each test function."""
    async with _async_engine.begin() as conn:
        await conn.run_sync(BasicBase.metadata.create_all)
        await conn.run_sync(RelationBase.metadata.create_all)

    yield

    async with _async_engine.begin() as conn:
        await conn.run_sync(BasicBase.metadata.drop_all)
        await conn.run_sync(RelationBase.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for testing."""
    async with _async_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def db_session_factory() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Provide a session factory for testing."""
    yield _async_session_factory


@pytest.fixture
def crud_ins() -> CRUDPlus[Ins]:
    """Provide CRUD instance for Ins model."""
    return CRUDPlus(Ins)


@pytest.fixture
def crud_ins_pks() -> CRUDPlus[InsPks]:
    """Provide CRUD instance for InsPks model."""
    return CRUDPlus(InsPks)


@pytest_asyncio.fixture
async def populated_db(db_session: AsyncSession, crud_ins: CRUDPlus[Ins]) -> list[Ins]:
    """Provide a database populated with test data."""
    async with db_session.begin():
        test_data = [Ins(name=f'item_{i}', del_flag=(i % 2 == 0)) for i in range(1, 11)]
        db_session.add_all(test_data)
        await db_session.flush()
        return test_data


@pytest_asyncio.fixture
async def populated_db_pks(db_session: AsyncSession) -> dict[str, list[InsPks]]:
    """Provide a database populated with composite key test data."""
    async with db_session.begin():
        men_data = [InsPks(id=i, name=f'man_{i}', sex='men') for i in range(1, 4)]
        women_data = [InsPks(id=i, name=f'woman_{i}', sex='women') for i in range(4, 7)]
        all_data = men_data + women_data

        db_session.add_all(all_data)
        await db_session.flush()

        return {'men': men_data, 'women': women_data, 'all': all_data}


@pytest.fixture
def rel_user_crud() -> CRUDPlus[RelUser]:
    """Provide CRUD instance for RelUser model."""
    return CRUDPlus(RelUser)


@pytest.fixture
def rel_post_crud() -> CRUDPlus[RelPost]:
    """Provide CRUD instance for RelPost model."""
    return CRUDPlus(RelPost)


@pytest.fixture
def rel_profile_crud() -> CRUDPlus[RelProfile]:
    """Provide CRUD instance for RelProfile model."""
    return CRUDPlus(RelProfile)


@pytest.fixture
def rel_category_crud() -> CRUDPlus[RelCategory]:
    """Provide CRUD instance for RelCategory model."""
    return CRUDPlus(RelCategory)


@pytest.fixture
def rel_role_crud() -> CRUDPlus[RelRole]:
    """Provide CRUD instance for RelRole model."""
    return CRUDPlus(RelRole)


@pytest_asyncio.fixture
async def rel_sample_users(db_session: AsyncSession) -> list[RelUser]:
    """Create sample relation users."""
    async with db_session.begin():
        users = []
        for i in range(1, 4):
            user_data = RelUserCreate(name=f'user_{i}')
            user = RelUser(**user_data.model_dump())
            db_session.add(user)
            users.append(user)
        await db_session.flush()
        return users


@pytest_asyncio.fixture
async def rel_sample_profiles(db_session: AsyncSession, rel_sample_users: list[RelUser]) -> list[RelProfile]:
    """Create sample relation profiles."""
    async with db_session.begin():
        profiles = []
        for i, user in enumerate(rel_sample_users[:2]):  # Only first 2 users get profiles
            profile_data = RelProfileCreate(bio=f'Bio for {user.name}')
            profile = RelProfile(user_id=user.id, **profile_data.model_dump())
            db_session.add(profile)
            profiles.append(profile)
        await db_session.flush()
        return profiles


@pytest_asyncio.fixture
async def rel_sample_categories(db_session: AsyncSession) -> list[RelCategory]:
    """Create sample relation categories."""
    async with db_session.begin():
        categories = []
        # Root categories
        tech = RelCategory(name='Technology')
        science = RelCategory(name='Science')
        db_session.add_all([tech, science])
        await db_session.flush()

        # Sub categories
        programming = RelCategory(name='Programming', parent_id=tech.id)
        ai = RelCategory(name='AI', parent_id=tech.id)
        db_session.add_all([programming, ai])
        await db_session.flush()

        categories = [tech, science, programming, ai]
        return categories


@pytest_asyncio.fixture
async def rel_sample_posts(
    db_session: AsyncSession, rel_sample_users: list[RelUser], rel_sample_categories: list[RelCategory]
) -> list[RelPost]:
    """Create sample relation posts."""
    async with db_session.begin():
        posts = []
        for i in range(6):
            post_data = RelPostCreate(
                title=f'Post {i + 1}',
                category_id=rel_sample_categories[i % len(rel_sample_categories)].id if i < 4 else None,
            )
            post = RelPost(author_id=rel_sample_users[i % len(rel_sample_users)].id, **post_data.model_dump())
            db_session.add(post)
            posts.append(post)
        await db_session.flush()
        return posts


@pytest_asyncio.fixture
async def rel_sample_roles(db_session: AsyncSession) -> list[RelRole]:
    """Create sample relation roles."""
    async with db_session.begin():
        roles = []
        for role_name in ['admin', 'editor', 'viewer']:
            role_data = RelRoleCreate(name=role_name)
            role = RelRole(**role_data.model_dump())
            db_session.add(role)
            roles.append(role)
        await db_session.flush()
        return roles


@pytest_asyncio.fixture
async def rel_sample_data(
    db_session: AsyncSession,
    rel_sample_users: list[RelUser],
    rel_sample_profiles: list[RelProfile],
    rel_sample_categories: list[RelCategory],
    rel_sample_posts: list[RelPost],
    rel_sample_roles: list[RelRole],
) -> dict:
    """Create complete relation sample data with relationships."""
    async with db_session.begin():
        # Create user-role relationships
        await db_session.execute(
            user_role.insert().values(
                [
                    {'user_id': rel_sample_users[0].id, 'role_id': rel_sample_roles[0].id},  # user_1 is admin
                    {'user_id': rel_sample_users[1].id, 'role_id': rel_sample_roles[1].id},  # user_2 is editor
                    {'user_id': rel_sample_users[0].id, 'role_id': rel_sample_roles[1].id},  # user_1 is also editor
                ]
            )
        )

        await db_session.flush()
        await db_session.commit()

    return {
        'users': rel_sample_users,
        'profiles': rel_sample_profiles,
        'categories': rel_sample_categories,
        'posts': rel_sample_posts,
        'roles': rel_sample_roles,
    }
