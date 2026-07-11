"""Static typing examples for the fluent query API.

This module is checked directly with ``ty`` and is not a pytest test module.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_crud_plus import CRUDPlus
from tests.models.basic import Ins
from tests.models.relationship import RelPost, RelUser


async def typed_single_model_query(crud: CRUDPlus[Ins], session: AsyncSession) -> None:
    query = (
        crud.query(session)
        .where(lambda item: item.id > 0)
        .where(lambda item: item.name.contains('item'))
        .select(lambda item: (item.id, item.name))
        .order_by(lambda item: item.id.desc())
    )
    await query.to_list()
    await (
        crud.update_query(session)
        .where(lambda item: item.id > 0)
        .set(lambda item: {item.name: 'updated', item.deleted: item.deleted + 1})
        .execute()
    )


async def typed_join_query(crud: CRUDPlus[RelUser], session: AsyncSession) -> None:
    query = crud.query(session).join(RelPost, lambda user, post: user.id == post.author_id)
    await query.to_list()
