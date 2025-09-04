#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseModel, ConfigDict


class CreateRelUser(BaseModel):
    name: str


class CreateRelProfile(BaseModel):
    bio: str


class CreateRelCategory(BaseModel):
    name: str
    parent_id: int | None = None


class CreateRelPost(BaseModel):
    title: str
    category_id: int | None = None


class CreateRelRole(BaseModel):
    name: str


class UpdateRelUser(BaseModel):
    name: str | None = None


class UpdateRelProfile(BaseModel):
    bio: str | None = None


class UpdateRelCategory(BaseModel):
    name: str | None = None
    parent_id: int | None = None


class UpdateRelPost(BaseModel):
    title: str | None = None
    category_id: int | None = None


class UpdateRelRole(BaseModel):
    name: str | None = None


class RelUserDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class RelProfileDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    bio: str


class RelCategoryDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None


class RelPostDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author_id: int
    category_id: int | None


class RelRoleDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
