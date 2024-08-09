#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Ins(Base):
    __tablename__ = 'ins'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    del_flag: Mapped[bool] = mapped_column(default=False)
    created_time: Mapped[datetime] = mapped_column(init=False, default_factory=datetime.now)
    updated_time: Mapped[datetime | None] = mapped_column(init=False, onupdate=datetime.now)
