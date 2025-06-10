#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class RelationBase(DeclarativeBase):
    pass


# Association table for Many-to-Many relationship between User and Role
user_role = Table(
    'user_role',
    RelationBase.metadata,
    Column('user_id', Integer, ForeignKey('rel_user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('rel_role.id'), primary_key=True),
)


class RelUser(RelationBase):
    __tablename__ = 'rel_user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # One-to-One relationship: User has one profile
    profile: Mapped[RelProfile | None] = relationship(back_populates='user', uselist=False)

    # One-to-Many relationship: User has many posts
    posts: Mapped[list[RelPost]] = relationship(back_populates='author')

    # Many-to-Many relationship: User has many roles, Role has many users
    roles: Mapped[list[RelRole]] = relationship(secondary=user_role, back_populates='users')


class RelProfile(RelationBase):
    __tablename__ = 'rel_profile'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('rel_user.id'), unique=True)
    bio: Mapped[str] = mapped_column(String(200))

    # One-to-One relationship: Profile belongs to one user
    user: Mapped[RelUser] = relationship(back_populates='profile')


class RelCategory(RelationBase):
    __tablename__ = 'rel_category'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('rel_category.id'))

    # Self-referential relationship: Category belongs to parent category
    parent: Mapped[RelCategory | None] = relationship('RelCategory', remote_side=[id], back_populates='children')

    # Self-referential relationship: Category has many child categories
    children: Mapped[list[RelCategory]] = relationship('RelCategory', back_populates='parent')

    # One-to-Many relationship: Category has many posts
    posts: Mapped[list[RelPost]] = relationship(back_populates='category')


class RelPost(RelationBase):
    __tablename__ = 'rel_post'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    author_id: Mapped[int] = mapped_column(ForeignKey('rel_user.id'))
    category_id: Mapped[int | None] = mapped_column(ForeignKey('rel_category.id'))

    # Many-to-One relationship: Post belongs to one author (user)
    author: Mapped[RelUser] = relationship(back_populates='posts')

    # Many-to-One relationship: Post belongs to one category (optional)
    category: Mapped[RelCategory | None] = relationship(back_populates='posts')


class RelRole(RelationBase):
    __tablename__ = 'rel_role'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # Many-to-Many relationship: Role has many users, User has many roles
    users: Mapped[list[RelUser]] = relationship(secondary=user_role, back_populates='roles')
