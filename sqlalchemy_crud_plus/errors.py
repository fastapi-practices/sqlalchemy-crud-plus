#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class SQLAlchemyCRUDPlusException(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class ModelColumnError(SQLAlchemyCRUDPlusException):
    """Error raised when an SCP column is invalid."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
