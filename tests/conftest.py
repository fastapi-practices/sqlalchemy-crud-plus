#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Base, Ins, InsPks
from tests.models.no_relationship import NoRelBase, NoRelCategory, NoRelPost, NoRelProfile, NoRelUser
from tests.models.relationship import RelationBase, RelCategory, RelPost, RelProfile, RelRole, RelUser, user_role
from tests.schemas.relationship import CreateRelPost, CreateRelProfile, CreateRelRole, CreateRelUser

_async_engine = create_async_engine('sqlite+aiosqlite:///:memory:', future=True, echo=False)
_async_db_session = async_sessionmaker(_async_engine, autoflush=False, expire_on_commit=False)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_database():
    """Set up the test database."""
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(RelationBase.metadata.create_all)
        await conn.run_sync(NoRelBase.metadata.create_all)


@pytest.fixture
def crud_ins() -> CRUDPlus[Ins]:
    """Provide CRUD instance for Ins model."""
    return CRUDPlus(Ins)


@pytest.fixture
def crud_ins_pks() -> CRUDPlus[InsPks]:
    """Provide CRUD instance for InsPks model."""
    return CRUDPlus(InsPks)


@pytest_asyncio.fixture(scope='module')
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for testing."""
    async with _async_db_session() as session:
        yield session


@pytest_asyncio.fixture
async def sample_ins(db: AsyncSession) -> list[Ins]:
    """Provide a database populated with test data."""
    test_data = [Ins(name=f'item_{i}', is_deleted=(i % 2 == 0)) for i in range(1, 11)]
    db.add_all(test_data)
    await db.commit()
    return test_data


@pytest_asyncio.fixture
async def sample_ins_pks(db: AsyncSession) -> dict[str, list[InsPks]]:
    """Provide a database populated with composite key test data."""
    men_data = [InsPks(id=i, name=f'man_{i}', sex='men') for i in range(1, 4)]
    women_data = [InsPks(id=i, name=f'woman_{i}', sex='women') for i in range(1, 4)]
    all_data = men_data + women_data
    db.add_all(all_data)
    await db.commit()
    return {'men': men_data, 'women': women_data, 'all': all_data}


@pytest.fixture
def rel_crud_user() -> CRUDPlus[RelUser]:
    """Provide CRUD instance for RelUser model."""
    return CRUDPlus(RelUser)


@pytest.fixture
def rel_crud_post() -> CRUDPlus[RelPost]:
    """Provide CRUD instance for RelPost model."""
    return CRUDPlus(RelPost)


@pytest.fixture
def rel_crud_profile() -> CRUDPlus[RelProfile]:
    """Provide CRUD instance for RelProfile model."""
    return CRUDPlus(RelProfile)


@pytest.fixture
def rel_crud_category() -> CRUDPlus[RelCategory]:
    """Provide CRUD instance for RelCategory model."""
    return CRUDPlus(RelCategory)


@pytest.fixture
def rel_crud_role() -> CRUDPlus[RelRole]:
    """Provide CRUD instance for RelRole model."""
    return CRUDPlus(RelRole)


@pytest_asyncio.fixture
async def rel_sample_users(db: AsyncSession) -> list[RelUser]:
    """Create sample relation users."""
    users = []
    for i in range(1, 4):
        user_data = CreateRelUser(name=f'user_{i}')
        user = RelUser(**user_data.model_dump())
        db.add(user)
        users.append(user)
    await db.commit()
    return users


@pytest_asyncio.fixture
async def rel_sample_profiles(db: AsyncSession, rel_sample_users: list[RelUser]) -> list[RelProfile]:
    """Create sample relation profiles."""
    profiles = []
    for i, user in enumerate(rel_sample_users[:2]):
        profile_data = CreateRelProfile(bio=f'Bio for {user.name}')
        profile = RelProfile(user_id=user.id, **profile_data.model_dump())
        db.add(profile)
        profiles.append(profile)
    await db.commit()
    return profiles


@pytest_asyncio.fixture
async def rel_sample_categories(db: AsyncSession) -> list[RelCategory]:
    """Create sample relation categories."""
    tech = RelCategory(name='Technology', parent_id=None)
    science = RelCategory(name='Science', parent_id=None)
    db.add_all([tech, science])
    await db.flush()
    programming = RelCategory(name='Programming', parent_id=tech.id)
    ai = RelCategory(name='AI', parent_id=tech.id)
    db.add_all([programming, ai])
    await db.commit()
    return [tech, science, programming, ai]


@pytest_asyncio.fixture
async def rel_sample_posts(
    db: AsyncSession, rel_sample_users: list[RelUser], rel_sample_categories: list[RelCategory]
) -> list[RelPost]:
    """Create sample relation posts."""
    posts = []
    for i in range(6):
        post_data = CreateRelPost(
            title=f'Post {i + 1}',
            category_id=rel_sample_categories[i % len(rel_sample_categories)].id if i < 4 else None,
        )
        post = RelPost(author_id=rel_sample_users[i % len(rel_sample_users)].id, **post_data.model_dump())
        db.add(post)
        posts.append(post)
    await db.commit()
    return posts


@pytest_asyncio.fixture
async def rel_sample_roles(db: AsyncSession) -> list[RelRole]:
    """Create sample relation roles."""
    roles = []
    for role_name in ['admin', 'editor']:
        role_data = CreateRelRole(name=role_name)
        role = RelRole(**role_data.model_dump())
        db.add(role)
        roles.append(role)
    await db.commit()
    return roles


@pytest_asyncio.fixture
async def rel_sample_data(
    db: AsyncSession,
    rel_sample_users: list[RelUser],
    rel_sample_profiles: list[RelProfile],
    rel_sample_categories: list[RelCategory],
    rel_sample_posts: list[RelPost],
    rel_sample_roles: list[RelRole],
) -> dict:
    """Create complete relation sample data with relationships."""
    await db.execute(
        insert(user_role).values(
            [
                {'user_id': rel_sample_users[0].id, 'role_id': rel_sample_roles[0].id},
                {'user_id': rel_sample_users[1].id, 'role_id': rel_sample_roles[1].id},
            ]
        )
    )
    await db.commit()
    return {
        'users': rel_sample_users,
        'profiles': rel_sample_profiles,
        'categories': rel_sample_categories,
        'posts': rel_sample_posts,
        'roles': rel_sample_roles,
    }


@pytest.fixture
def no_rel_crud_user() -> CRUDPlus[NoRelUser]:
    """Provide CRUD instance for NoRelUser model."""
    return CRUDPlus(NoRelUser)


@pytest.fixture
def no_rel_crud_profile() -> CRUDPlus[NoRelProfile]:
    """Provide CRUD instance for NoRelProfile model."""
    return CRUDPlus(NoRelProfile)


@pytest.fixture
def no_rel_crud_post() -> CRUDPlus[NoRelPost]:
    """Provide CRUD instance for NoRelPost model."""
    return CRUDPlus(NoRelPost)


@pytest.fixture
def no_rel_crud_category() -> CRUDPlus[NoRelCategory]:
    """Provide CRUD instance for NoRelCategory model."""
    return CRUDPlus(NoRelCategory)


@pytest_asyncio.fixture(scope='module')
async def no_rel_sample_users(db: AsyncSession) -> list[NoRelUser]:
    """Create sample users without relationships."""
    users = []
    for i in range(1, 4):
        user = NoRelUser(name=f'User {i}')
        db.add(user)
        users.append(user)
    await db.commit()
    for user in users:
        await db.refresh(user)
    return users


@pytest_asyncio.fixture(scope='module')
async def no_rel_sample_profiles(db: AsyncSession, no_rel_sample_users: list[NoRelUser]) -> list[NoRelProfile]:
    """Create sample profiles without relationships."""
    profiles = []
    for i, user in enumerate(no_rel_sample_users[:2], 1):
        profile = NoRelProfile(
            user_id=user.id,
            bio=f'Bio for user {i}',
        )
        db.add(profile)
        profiles.append(profile)
    await db.commit()
    return profiles


@pytest_asyncio.fixture(scope='module')
async def no_rel_sample_categories(db: AsyncSession) -> list[NoRelCategory]:
    """Create sample categories without relationships."""
    categories = [
        NoRelCategory(name='Technology'),
        NoRelCategory(name='Science'),
    ]
    db.add_all(categories)
    await db.commit()
    for cat in categories:
        await db.refresh(cat)
    return categories


@pytest_asyncio.fixture(scope='module')
async def no_rel_sample_posts(
    db: AsyncSession, no_rel_sample_users: list[NoRelUser], no_rel_sample_categories: list[NoRelCategory]
) -> list[NoRelPost]:
    """Create sample posts without relationships."""
    posts = []
    for i in range(4):
        post = NoRelPost(
            title=f'Post {i + 1}',
            author_id=no_rel_sample_users[i % len(no_rel_sample_users)].id,
            category_id=no_rel_sample_categories[i % len(no_rel_sample_categories)].id if i < 3 else None,
        )
        db.add(post)
        posts.append(post)
    await db.commit()
    return posts


@pytest_asyncio.fixture(scope='module')
async def no_rel_sample_data(
    db: AsyncSession,
    no_rel_sample_users: list[NoRelUser],
    no_rel_sample_profiles: list[NoRelProfile],
    no_rel_sample_categories: list[NoRelCategory],
    no_rel_sample_posts: list[NoRelPost],
) -> dict:
    """Create complete sample data without relationships."""
    return {
        'users': no_rel_sample_users,
        'profiles': no_rel_sample_profiles,
        'categories': no_rel_sample_categories,
        'posts': no_rel_sample_posts,
    }
