#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseModel


class CreateIns(BaseModel):
    name: str
    is_deleted: bool = False


class UpdateIns(BaseModel):
    name: str | None = None
    is_deleted: bool | None = None


class CreateInsPks(BaseModel):
    id: int
    name: str
    sex: str


class UpdateInsPks(BaseModel):
    name: str | None = None
