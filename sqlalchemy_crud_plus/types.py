#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import TypeVar

from pydantic import BaseModel

Model = TypeVar('Model')

CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
