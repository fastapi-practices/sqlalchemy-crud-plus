#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseModel, ConfigDict


class RelUserCreate(BaseModel):
    name: str


class RelProfileCreate(BaseModel):
    bio: str


class RelCategoryCreate(BaseModel):
    name: str
    parent_id: int | None = None


class RelPostCreate(BaseModel):
    title: str
    category_id: int | None = None


class RelRoleCreate(BaseModel):
    name: str


class RelUserUpdate(BaseModel):
    name: str | None = None


class RelProfileUpdate(BaseModel):
    bio: str | None = None


class RelCategoryUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None


class RelPostUpdate(BaseModel):
    title: str | None = None
    category_id: int | None = None


class RelRoleUpdate(BaseModel):
    name: str | None = None


class RelUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class RelProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    bio: str


class RelCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None


class RelPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author_id: int
    category_id: int | None


class RelRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
