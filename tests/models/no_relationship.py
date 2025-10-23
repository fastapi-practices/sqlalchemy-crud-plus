#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column


class NoRelBase(MappedAsDataclass, DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class NoRelUser(NoRelBase):
    __tablename__ = 'no_rel_user'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))


class NoRelProfile(NoRelBase):
    __tablename__ = 'no_rel_profile'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    bio: Mapped[str] = mapped_column(String(100))

    user_id: Mapped[int] = mapped_column(unique=True)


class NoRelCategory(NoRelBase):
    __tablename__ = 'no_rel_category'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    parent_id: Mapped[int | None] = mapped_column(default=None)


class NoRelPost(NoRelBase):
    __tablename__ = 'no_rel_post'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))

    author_id: Mapped[int] = mapped_column()
    category_id: Mapped[int | None] = mapped_column(default=None)


class NoRelRole(NoRelBase):
    __tablename__ = 'no_rel_role'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20))
