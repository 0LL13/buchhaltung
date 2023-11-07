#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_helpers.py
"""Tests for "helpers" module."""

from context import path_to_database_dir

# ######## helpers.py #########################################################

abs_path_to_parent = "/home/sam/Programming/buha/src/buha/"
abs_path_to_data = "/home/sam/Programming/buha/src/buha/data"


def test_main_path_to_database():
    actual = str(path_to_database_dir())
    expected = abs_path_to_data
    assert actual == expected
