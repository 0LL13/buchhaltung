#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_shared.py
"""Tests for "shared" module."""


from unittest.mock import patch

from context import AttrDisplay
from context import is_posix
from context import Name
from context import shared


# ######## is posix ###########################################################

def test_shared_is_posix_on_posix_system():
    with patch('platform.system', return_value='Linux'):
        assert is_posix()


def test_shared_is_posix_on_windows_system():
    with patch('platform.system', return_value='Windows'):
        if is_posix():
            assert False


# ######## class AttrDisplay ##################################################

def test_shared_gather_attrs_filter_unwanted():

    class TestAttrDisplay(AttrDisplay):
        def __init__(self):
            self.wanted = "wanted"
            self.unwanted_ew = "ew"
            self.unwanted_unknown = "unknown"
            self.unwanted_None = None

    test_dict = TestAttrDisplay()
    attrs = test_dict.gather_attrs()
    if "ew" in attrs:
        assert False
    if "unknown" in attrs:
        assert False
    if None in attrs:
        assert False
    if "wanted" not in attrs:
        assert False


# ######## class AttrDisplay ##################################################

def test_shared_translate(capsys):
    test_name = Name("test_fn", "test_ln")

    expected = """+-----------+---------+
| attribute | value   |
+-----------+---------+
| Vorname   | test_fn |
| Nachname  | test_ln |
+-----------+---------+
"""

    print(test_name)

    actual, _ = capsys.readouterr()

    assert actual == expected


def test_shared_translate_missing_attr(capsys):
    test_name = Name("test_fn", "test_ln")
    test_name.nexa = "non-existing attribute"

    expected = """nexa missing
+-----------+---------+
| attribute | value   |
+-----------+---------+
| Vorname   | test_fn |
| Nachname  | test_ln |
+-----------+---------+
"""

    print(test_name)

    actual, _ = capsys.readouterr()

    assert actual == expected


def test_shared_no_language(capsys):
    shared.language = None

    test_name = Name("test_fn", "test_ln")

    expected = """+------------+---------+
| attribute  | value   |
+------------+---------+
| first_name | test_fn |
| last_name  | test_ln |
+------------+---------+
"""

    print(test_name)

    actual, _ = capsys.readouterr()

    assert actual == expected


def test_shared_language_not_de(capsys):
    shared.language = "not de"

    test_name = Name("test_fn", "test_ln")

    expected = """+------------+---------+
| attribute  | value   |
+------------+---------+
| first_name | test_fn |
| last_name  | test_ln |
+------------+---------+
"""

    print(test_name)

    actual, _ = capsys.readouterr()

    assert actual == expected
