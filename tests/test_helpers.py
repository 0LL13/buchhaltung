#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_helpers.py
"""Tests for "helpers" module."""

from pathlib import Path

from context import path_to_db_dir
from context import path_to_database

# ######## helpers.py #########################################################

abs_path_to_parent = "/home/sam/Programming/buha/src/buha/"
abs_path_to_data = "/home/sam/Programming/buha/src/buha/data"


def test_main_path_to_database():
    actual = str(path_to_db_dir())
    expected = abs_path_to_data
    assert actual == expected


def test_path_to_db_dir_type_Path():
    result = path_to_db_dir()
    assert isinstance(result, Path)


def test_path_to_database_type_Path():
    db_name = "test.db"
    result = path_to_database(db_name)
    assert isinstance(result, Path)
