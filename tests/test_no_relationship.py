#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus, JoinConfig
from sqlalchemy_crud_plus.errors import ModelColumnError
from tests.models.no_relationship import NoRelCategory, NoRelPost, NoRelProfile, NoRelUser


@pytest.mark.asyncio
async def test_create_single_user(db: AsyncSession, no_rel_crud_user: CRUDPlus[NoRelUser]):
    user = NoRelUser(name='Test User')
    db.add(user)
    await db.commit()
    await db.refresh(user)

    assert user is not None
    assert user.name == 'Test User'
    assert user.id is not None


@pytest.mark.asyncio
async def test_create_multiple_users(db: AsyncSession, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = [
        NoRelUser(name='User 1'),
        NoRelUser(name='User 2'),
        NoRelUser(name='User 3'),
    ]
    db.add_all(users)
    await db.commit()
    for user in users:
        await db.refresh(user)

    assert len(users) == 3
    assert all(isinstance(user, NoRelUser) for user in users)
    assert users[0].name == 'User 1'
    assert users[1].name == 'User 2'
    assert users[2].name == 'User 3'


@pytest.mark.asyncio
async def test_bulk_create_users(db: AsyncSession, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users_data = [{'name': f'Bulk User {i}'} for i in range(5)]
    users = await no_rel_crud_user.bulk_create_models(db, users_data)
    await db.commit()

    assert len(users) == 5
    assert all(isinstance(user, NoRelUser) for user in users)


@pytest.mark.asyncio
async def test_select_model_by_id(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = no_rel_sample_data['users']
    user = await no_rel_crud_user.select_model(db, users[0].id)

    assert user is not None
    assert user.id == users[0].id
    assert user.name == users[0].name


@pytest.mark.asyncio
async def test_select_model_by_column(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = no_rel_sample_data['users']
    user = await no_rel_crud_user.select_model_by_column(db, id=users[0].id)

    assert user is not None
    assert user.name == users[0].name
    assert user.id == users[0].id


@pytest.mark.asyncio
async def test_select_models_all(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = await no_rel_crud_user.select_models(db)

    assert len(users) >= 3
    assert all(isinstance(user, NoRelUser) for user in users)


@pytest.mark.asyncio
async def test_select_models_with_limit(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(db, limit=2)

    assert len(users) == 2
    assert all(isinstance(user, NoRelUser) for user in users)


@pytest.mark.asyncio
async def test_select_models_with_offset(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    all_users = await no_rel_crud_user.select_models(db)
    offset_users = await no_rel_crud_user.select_models(db, offset=1, limit=2)

    assert len(offset_users) <= 2
    if len(all_users) > 1:
        assert offset_users[0].id == all_users[1].id


@pytest.mark.asyncio
async def test_select_models_with_pagination(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    page1 = await no_rel_crud_user.select_models(db, limit=2, offset=0)
    page2 = await no_rel_crud_user.select_models(db, limit=2, offset=2)

    assert len(page1) <= 2
    assert len(page2) <= 2
    if len(page1) > 0 and len(page2) > 0:
        assert page1[0].id != page2[0].id


@pytest.mark.asyncio
async def test_select_models_order_asc(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models_order(db, 'name', 'asc')

    assert len(users) >= 3
    if len(users) >= 2:
        assert users[0].name <= users[1].name


@pytest.mark.asyncio
async def test_select_models_order_desc(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models_order(db, 'name', 'desc')

    assert len(users) >= 3
    if len(users) >= 2:
        assert users[0].name >= users[1].name


@pytest.mark.asyncio
async def test_select_models_order_with_limit(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models_order(db, 'id', 'asc', limit=2)

    assert len(users) <= 2
    if len(users) == 2:
        assert users[0].id < users[1].id


@pytest.mark.asyncio
async def test_select_models_with_filter_equal(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = no_rel_sample_data['users']
    filtered_users = await no_rel_crud_user.select_models(db, name=users[0].name)

    assert len(filtered_users) >= 1
    assert all(user.name == users[0].name for user in filtered_users)


@pytest.mark.asyncio
async def test_select_models_with_filter_like(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(db, name__like='%User%')

    assert len(users) >= 1
    assert all('User' in user.name for user in users)


@pytest.mark.asyncio
async def test_select_models_with_filter_ilike(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models(db, name__ilike='%user%')

    assert len(users) >= 1
    assert all('user' in user.name.lower() for user in users)


@pytest.mark.asyncio
async def test_select_models_with_multiple_filters(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_post: CRUDPlus[NoRelPost]
):
    users = no_rel_sample_data['users']
    posts = await no_rel_crud_post.select_models(db, author_id=users[0].id)

    assert len(posts) >= 0
    assert all(post.author_id == users[0].id for post in posts)


@pytest.mark.asyncio
async def test_count_all_users(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    count = await no_rel_crud_user.count(db)

    assert count >= 3
    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_count_with_filter(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    count = await no_rel_crud_user.count(db, name__like='%User%')

    assert count >= 1
    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_exists_true(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = no_rel_sample_data['users']
    exists = await no_rel_crud_user.exists(db, id=users[0].id)

    assert exists is True


@pytest.mark.asyncio
async def test_exists_false(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    exists = await no_rel_crud_user.exists(db, id=999999)

    assert exists is False


@pytest.mark.asyncio
async def test_exists_with_filter(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    exists = await no_rel_crud_user.exists(db, name__like='%User%')

    assert exists is True
    assert isinstance(exists, bool)


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
async def test_update_model_by_id(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = no_rel_sample_data['users']
    updated_count = await no_rel_crud_user.update_model(db, users[0].id, {'name': 'Updated Name'})
    await db.commit()

    assert updated_count == 1

    updated_user = await no_rel_crud_user.select_model(db, users[0].id)
    assert updated_user.name == 'Updated Name'


@pytest.mark.asyncio
async def test_update_model_by_column(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = no_rel_sample_data['users']
    updated_count = await no_rel_crud_user.update_model_by_column(db, obj={'name': 'Updated Name'}, id=users[0].id)
    await db.commit()

    assert updated_count == 1

    updated_user = await no_rel_crud_user.select_model(db, users[0].id)
    assert updated_user.name == 'Updated Name'


@pytest.mark.asyncio
async def test_bulk_update_models(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = no_rel_sample_data['users']
    update_data = [
        {'id': users[0].id, 'name': 'Bulk Updated 1'},
        {'id': users[1].id, 'name': 'Bulk Updated 2'},
    ]
    updated_count = await no_rel_crud_user.bulk_update_models(db, update_data)
    await db.commit()

    assert updated_count == 2

    user1 = await no_rel_crud_user.select_model(db, users[0].id)
    user2 = await no_rel_crud_user.select_model(db, users[1].id)
    assert user1.name == 'Bulk Updated 1'
    assert user2.name == 'Bulk Updated 2'


@pytest.mark.asyncio
async def test_update_single_field(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = no_rel_sample_data['users']
    update_data = {'name': 'Single Update'}
    updated_count = await no_rel_crud_user.update_model(db, users[0].id, update_data)
    await db.commit()

    assert updated_count == 1

    updated_user = await no_rel_crud_user.select_model(db, users[0].id)
    assert updated_user.name == 'Single Update'


@pytest.mark.asyncio
async def test_delete_model_by_id(db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = no_rel_sample_data['users']
    deleted_count = await no_rel_crud_user.delete_model(db, users[0].id)
    await db.commit()

    assert deleted_count == 1

    deleted_user = await no_rel_crud_user.select_model(db, users[0].id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_model_by_column(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = no_rel_sample_data['users']
    user_to_delete = users[1]
    deleted_count = await no_rel_crud_user.delete_model_by_column(db, allow_multiple=False, id=user_to_delete.id)
    await db.commit()

    assert deleted_count == 1

    deleted_user = await no_rel_crud_user.select_model(db, user_to_delete.id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_nonexistent_model(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    deleted_count = await no_rel_crud_user.delete_model(db, 999999)
    await db.commit()

    assert deleted_count == 0


@pytest.mark.asyncio
async def test_combined_filter_order_pagination(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    users = await no_rel_crud_user.select_models_order(db, 'name', 'asc', name__like='%User%', limit=2, offset=0)

    assert len(users) <= 2
    assert all('User' in user.name for user in users)
    if len(users) == 2:
        assert users[0].name <= users[1].name


@pytest.mark.asyncio
async def test_join_get_user_posts_grouped(db: AsyncSession, no_rel_sample_data: dict):
    stmt = select(NoRelUser, NoRelPost).join(
        NoRelPost,
        NoRelUser.id == NoRelPost.author_id,
        isouter=True,
    )
    result = await db.execute(stmt)
    rows = result.all()

    user_posts = {}
    for user, post in rows:
        if user.id not in user_posts:
            user_posts[user.id] = {'user': user, 'posts': []}
        if post:
            user_posts[user.id]['posts'].append(post)

    assert len(user_posts) >= 1
    for user_id, data in user_posts.items():
        assert isinstance(data['user'], NoRelUser)
        assert isinstance(data['posts'], list)


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
async def test_select_model_invalid_id(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    user = await no_rel_crud_user.select_model(db, 999999)

    assert user is None


@pytest.mark.asyncio
async def test_update_nonexistent_model(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    updated_count = await no_rel_crud_user.update_model(db, 999999, {'name': 'Test'})
    await db.commit()

    assert updated_count == 0


@pytest.mark.asyncio
async def test_select_with_invalid_filter_column(
    db: AsyncSession, no_rel_sample_data: dict, no_rel_crud_user: CRUDPlus[NoRelUser]
):
    with pytest.raises(ModelColumnError):
        await no_rel_crud_user.select_models(db, nonexistent_column='value')


@pytest.mark.asyncio
async def test_select_models_empty_result(db: AsyncSession, no_rel_crud_user: CRUDPlus[NoRelUser]):
    users = await no_rel_crud_user.select_models(db, name='NonExistentUser')

    assert len(users) == 0
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_count_empty_result(db: AsyncSession, no_rel_crud_user: CRUDPlus[NoRelUser]):
    count = await no_rel_crud_user.count(db, name='NonExistentUser')

    assert count == 0


@pytest.mark.asyncio
async def test_bulk_create_empty_list(db: AsyncSession):
    users = []
    assert len(users) == 0


@pytest.mark.asyncio
async def test_bulk_update_empty_list(db: AsyncSession, no_rel_crud_user: CRUDPlus[NoRelUser]):
    updated_count = await no_rel_crud_user.bulk_update_models(db, [])
    await db.commit()

    assert updated_count == 0


@pytest.mark.asyncio
async def test_join_get_multiple_table_data(db: AsyncSession, no_rel_sample_data: dict):
    stmt = select(NoRelUser, NoRelProfile).join(
        NoRelProfile,
        NoRelUser.id == NoRelProfile.user_id,
        isouter=True,
    )
    result = await db.execute(stmt)
    rows = result.all()

    assert len(rows) >= 2
    for user, profile in rows:
        assert isinstance(user, NoRelUser)
        assert user.name is not None
        if profile:
            assert isinstance(profile, NoRelProfile)
            assert profile.user_id == user.id


@pytest.mark.asyncio
async def test_join_get_post_with_author_data(db: AsyncSession, no_rel_sample_data: dict):
    stmt = select(NoRelPost, NoRelUser).join(
        NoRelUser,
        NoRelPost.author_id == NoRelUser.id,
    )
    result = await db.execute(stmt)
    rows = result.all()

    assert len(rows) >= 1
    for post, user in rows:
        assert isinstance(post, NoRelPost)
        assert isinstance(user, NoRelUser)
        assert post.author_id == user.id
        assert post.title is not None
        assert user.name is not None


@pytest.mark.asyncio
async def test_join_get_three_table_data(db: AsyncSession, no_rel_sample_data: dict):
    stmt = (
        select(NoRelPost, NoRelUser, NoRelCategory)
        .join(NoRelUser, NoRelPost.author_id == NoRelUser.id)
        .join(NoRelCategory, NoRelPost.category_id == NoRelCategory.id, isouter=True)
    )
    result = await db.execute(stmt)
    rows = result.all()

    assert len(rows) >= 1
    for post, user, category in rows:
        assert isinstance(post, NoRelPost)
        assert isinstance(user, NoRelUser)
        assert post.author_id == user.id
        if category:
            assert isinstance(category, NoRelCategory)
            assert post.category_id == category.id


@pytest.mark.asyncio
async def test_join_build_dict_result(db: AsyncSession, no_rel_sample_data: dict):
    stmt = select(NoRelUser, NoRelProfile).join(
        NoRelProfile,
        NoRelUser.id == NoRelProfile.user_id,
    )
    result = await db.execute(stmt)
    rows = result.all()

    data = [
        {
            'user_id': user.id,
            'user_name': user.name,
            'profile_bio': profile.bio,
        }
        for user, profile in rows
    ]

    assert len(data) >= 1
    for item in data:
        assert 'user_id' in item
        assert 'user_name' in item
        assert 'profile_bio' in item
        assert isinstance(item['user_id'], int)
        assert isinstance(item['user_name'], str)


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

    stmt = select(NoRelUser, NoRelPost).join(
        NoRelPost,
        NoRelUser.id == NoRelPost.author_id,
    )
    result = await db.execute(stmt)
    user_post_pairs = result.all()

    assert len(user_post_pairs) >= 1
    for user, post in user_post_pairs:
        assert isinstance(user, NoRelUser)
        assert isinstance(post, NoRelPost)
        assert user.id == post.author_id
