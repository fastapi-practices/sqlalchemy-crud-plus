#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column, relationship


class RelationBase(MappedAsDataclass, DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


user_role = Table(
    'user_role',
    RelationBase.metadata,
    Column('user_id', Integer, ForeignKey('rel_user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('rel_role.id'), primary_key=True),
)


class RelUser(RelationBase):
    __tablename__ = 'rel_user'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    profile: Mapped[RelProfile | None] = relationship(init=False, back_populates='user', uselist=False)
    posts: Mapped[list[RelPost]] = relationship(init=False, back_populates='author')
    roles: Mapped[list[RelRole]] = relationship(init=False, secondary=user_role, back_populates='users')


class RelProfile(RelationBase):
    __tablename__ = 'rel_profile'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    bio: Mapped[str] = mapped_column(String(100))

    user_id: Mapped[int] = mapped_column(ForeignKey('rel_user.id'), unique=True)
    user: Mapped[RelUser] = relationship(init=False, back_populates='profile')


class RelCategory(RelationBase):
    __tablename__ = 'rel_category'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    parent_id: Mapped[int | None] = mapped_column(ForeignKey('rel_category.id'))
    parent: Mapped[RelCategory | None] = relationship(init=False, remote_side=[id], back_populates='children')
    children: Mapped[list[RelCategory]] = relationship(init=False, back_populates='parent')
    posts: Mapped[list[RelPost]] = relationship(init=False, back_populates='category')


class RelPost(RelationBase):
    __tablename__ = 'rel_post'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))

    author_id: Mapped[int] = mapped_column(ForeignKey('rel_user.id'))
    author: Mapped[RelUser] = relationship(init=False, back_populates='posts')

    category_id: Mapped[int | None] = mapped_column(ForeignKey('rel_category.id'))
    category: Mapped[RelCategory | None] = relationship(init=False, back_populates='posts')


class RelRole(RelationBase):
    __tablename__ = 'rel_role'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20))

    users: Mapped[list[RelUser]] = relationship(init=False, secondary=user_role, back_populates='roles')
