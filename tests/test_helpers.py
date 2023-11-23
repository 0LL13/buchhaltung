#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_helpers.py
"""Tests for "helpers" module."""

import os
import pytest
import sqlite3

from pathlib import Path
from unittest.mock import patch

from context import create_headline
from context import helpers
from context import mk_initials
from context import Menu
from context import Name
from context import path_to_database
from context import path_to_db_dir


@pytest.fixture
def mock_conn():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


# ######## basic Menu class ###################################################

def test_basic_menu_class_attributes():
    menu = Menu()
    assert menu.last_caller_module is None
    assert menu.current_caller_module is None
    assert menu.navigation_stack == []


def test_basic_menu_class_menu_changed_True_attr():
    menu = Menu()
    Menu.last_caller_module = "main"
    Menu.last_caller_module = "start"
    assert menu.menu_changed()


def test_basic_menu_class_menu_changed_True_modules():
    menu = Menu()
    Menu.last_caller_module = "start"
    Menu.last_caller_module = "start"
    Menu.navigation_stack = ["start", "settings"]
    assert menu.menu_changed()


def test_basic_menu_class_menu_changed_True_attr_False_modules():
    menu = Menu()
    Menu.last_caller_module = "start"
    Menu.last_caller_module = "settings"
    Menu.navigation_stack = ["settings", "settings"]
    assert menu.menu_changed()


def test_basic_menu_class_menu_changed_False():
    menu = Menu()
    Menu.last_caller_module = "person"
    Menu.current_caller_module = "person"
    Menu.navigation_stack = ["person", "person"]
    if menu.menu_changed():
        assert False


def test_basic_menu_class_menu_changed_False_index_error():
    menu = Menu()
    Menu.last_caller_module = "person"
    Menu.current_caller_module = "person"
    Menu.navigation_stack = ["person"]
    if menu.menu_changed():
        assert False


def test_basic_menu_class_menu_changed_False_no_stack():
    menu = Menu()
    Menu.last_caller_module = "person"
    Menu.current_caller_module = "person"
    Menu.navigation_stack = []
    if menu.menu_changed():
        assert False


def test_basic_menu_class_print_headline_clear_screen(mocker):
    mocker.patch("os.system")
    menu = Menu()
    company_name = "Test Ltd."
    language = "en"
    task = "person"
    menu.print_headline(company_name, language, task)
    os.system.assert_called_once()
    os.system.assert_called_with("clear")


def test_basic_menu_class_print_headline_task_headline(mocker, capsys):
    mocker.patch("os.system")
    menu = Menu()
    company_name = "Test_Ltd..db"
    language = "en"
    task = "main"
    company_line = f"| Test Ltd.{' ' * 67}|"
    headline = "A small-scale accounting program"
    headline_final = f"| A small-scale accounting program{' ' * 44}|"
    expected = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+\n"""

    menu.print_headline(company_name, language, task)
    actual, err = capsys.readouterr()
    assert actual == expected


# ######## path to database ###################################################

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


# ######## create headline ####################################################

def test_create_headline():
    company_name = "Test_Ltd..db"
    company_line = f"| Test Ltd.{' ' * 67}|"
    headline = "A small-scale accounting program"
    headline_final = f"| A small-scale accounting program{' ' * 44}|"
    expected = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+"""

    actual = create_headline(company_name, headline)
    assert actual == expected


# ######## mk initials ########################################################

def test_mk_initials_not_in_table(mock_conn):
    with patch.object(helpers, "initials_in_table", return_value=False):
        first_name = "Peter"
        last_name = "Pan"
        name = Name(first_name, last_name)
        length = 2
        expected = "pp"
        actual = mk_initials(mock_conn, name, length)
        assert actual == expected


def test_mk_initials_in_table(mock_conn):
    first_name = "Peter"
    last_name = "Pan"
    name = Name(first_name, last_name)
    length = 2

    def side_effect(module, func):
        if mock_func.call_count == 0:
            return True
        return False

    with patch.object(helpers, "initials_in_table") as mock_func:
        mock_func.side_effect = side_effect
        actual = mk_initials(mock_conn, name, length)
        assert mock_func.call_count == 1

        length = 3
        actual = mk_initials(mock_conn, name, length)
        expected = "pep"
        assert actual == expected
        assert mock_func.call_count == 2
