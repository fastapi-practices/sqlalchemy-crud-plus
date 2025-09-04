#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class InsCreate(BaseModel):
    name: str
    is_deleted: bool = False


class InsUpdate(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None


class InsPksCreate(BaseModel):
    id: int
    name: str
    sex: str


class InsPksUpdate(BaseModel):
    name: Optional[str] = None
