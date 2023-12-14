#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_names.py
"""Tests for "names" module."""

import datetime
import pytest
import sqlite3

# from unittest.mock import Mock
from unittest.mock import patch

from context import helpers
from context import Menu
from context import MenuName


@pytest.fixture
def mock_conn():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def no_clear_screen():
    with patch("os.system") as mock_system:
        yield mock_system


@pytest.fixture
def display_with_change():
    company_name = "Test & Co.   "
    company_line = f"| {company_name}{' ' * 63}|"
    headline = "NAMENSEINTRÄGE"
    headline_final = f"| {headline}{' ' * 62}|"
    expected = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+

    Felder mit (*) sind Pflichtfelder

    1: (*) Vorname / Rufname
    2: Zweitname(n)
    3: (*) Nachname / Familienname
    4: Spitzname
    5: Geburtsname
    6: Generationen-Suffix (Jr., Sr.)
    7: Anrede
    8: Speichern und zurück
    9: Zurück
    \n"""

    return expected


@pytest.fixture
def display_wo_change():
    expected = """
    Felder mit (*) sind Pflichtfelder

    1: (*) Vorname / Rufname
    2: Zweitname(n)
    3: (*) Nachname / Familienname
    4: Spitzname
    5: Geburtsname
    6: Generationen-Suffix (Jr., Sr.)
    7: Anrede
    8: Speichern und zurück
    9: Zurück
    \n"""

    return expected


@pytest.fixture
def reset_parent_class_menu():
    Menu.last_caller_module = None
    Menu.current_caller_module = None
    Menu.navigation_stack = []

    return Menu


# ######## initialize Menu ####################################################

def test_start_menu_reset(reset_parent_class_menu):
    menu = reset_parent_class_menu()
    assert menu.last_caller_module is None
    assert menu.current_caller_module is None
    assert menu.navigation_stack == []


# ######## MenuName class #####################################################

def test_name_menu_reset_entries():
    menu = MenuName()
    menu.reset_entries()
    for key, value in menu.entries.items():
        assert value is None


def test_name_menu_class_init(reset_parent_class_menu):
    reset_parent_class_menu()
    menu = MenuName()
    if menu.last_caller_module == "names":
        assert False
    assert menu.current_caller_module == "src.buha.scripts.names"
    assert menu.navigation_stack == ["names"]


def test_name_menu_display_menu(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu = MenuName()
    company_name = "Test & Co.   "
    language = "de"
    task = "names"
    expected = display_with_change

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu.display_menu(company_name, language, task)
        actual, err = capsys.readouterr()
        assert actual == expected


def test_name_menu_run(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu = MenuName()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected = display_with_change

    with patch("builtins.input", return_value=None):
        menu.run(mock_conn, created_by, company_name, language)
        actual, err = capsys.readouterr()
        assert actual == expected


@patch("builtins.input", return_value="9")
def test_name_menu_run_get_choice_to_go_back(mocker):
    menu = MenuName()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


@patch("builtins.input", return_value="not valid")
def test_name_menu_run_get_choice_not_valid(mocker, capsys, display_wo_change):  # noqa
    menu = MenuName()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected = display_wo_change

    menu.run(mock_conn, created_by, company_name, language)
    actual, err = capsys.readouterr()
    assert actual == expected


# ######## MenuName class methods #############################################

@patch("builtins.input", return_value="first_name")
def test_name_menu_enter_firstname(mocker):
    language = "de"
    menu = MenuName()
    menu.enter_firstname(language)
    assert menu.entries["fn"] == "first_name"


@patch("builtins.input", return_value="middle_name_1 middle_name_2")
def test_name_menu_enter_middlename(mocker):
    language = "de"
    menu = MenuName()
    menu.enter_middlenames(language)
    assert menu.entries["mn"] == "middle_name_1 middle_name_2"


@patch("builtins.input", return_value="family_name")
def test_name_menu_enter_familyname(mocker):
    language = "de"
    menu = MenuName()
    menu.enter_lastname(language)
    assert menu.entries["ln"] == "family_name"


@patch("builtins.input", return_value="nick_name")
def test_name_menu_enter_nickname(mocker):
    language = "de"
    menu = MenuName()
    menu.enter_nickname(language)
    assert menu.entries["nn"] == "nick_name"


@patch("builtins.input", return_value="previous_name")
def test_name_menu_enter_previousname(mocker):
    language = "de"
    menu = MenuName()
    menu.enter_previousname(language)
    assert menu.entries["pn"] == "previous_name"


@patch("builtins.input", return_value="Jr.")
def test_name_menu_enter_suffix(mocker):
    language = "de"
    menu = MenuName()
    menu.enter_generational_suffix(language)
    assert menu.entries["suffix"] == "Jr."


@patch("builtins.input", return_value="Hr.")
def test_name_menu_enter_salutation(mocker):
    language = "de"
    menu = MenuName()
    menu.enter_salutation(language)
    assert menu.entries["salutation"] == "Hr."


# ######## name instance ######################################################

def test_name_generate_name_instance():
    menu = MenuName()
    menu.entries["fn"] = "test_fn"
    menu.entries["ln"] = "test_ln"
    name = menu.generate_name_instance()
    assert name.first_name == "test_fn"
    assert name.last_name == "test_ln"


# ######## generate table #####################################################

def test_name_generate_table_names():
    mock_conn = sqlite3.connect(":memory:")
    menu = MenuName()

    with mock_conn:
        menu.generate_table_names(mock_conn)
        cur = mock_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='names'")  # noqa
        assert cur.fetchone() is not None, "Table 'names' was not created"

        cur.execute("PRAGMA table_info('names')")
        columns = [row[1] for row in cur.fetchall()]
        expected_columns = ['name_id', 'person_id', 'created_by', 'timestamp', 'first_name',  # noqa
                            'middle_names', 'last_name', 'nickname', 'previous_name', 'suffix', 'salutation']  # noqa
        assert columns == expected_columns, "Table schema for 'names' does not match expected schema"  # noqa


# ######## add name to table ##################################################


@pytest.fixture
def mock_db_connection():
    """Fixture to provide an in-memory SQLite database."""
    conn = sqlite3.connect(':memory:')
    yield conn
    conn.close()


def test_names_add_name_to_db(mock_db_connection):
    person_id = "11"
    created_by = "test_func"
    today = str(datetime.date.today())

    menu = MenuName()
    menu.entries["fn"] = "test_fn"
    menu.entries["ln"] = "test_ln"
    name = menu.generate_name_instance()

    menu.generate_table_names(mock_db_connection)
    cur = mock_db_connection.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='names'")  # noqa
    assert cur.fetchone() is not None, "Table 'names' was not created"

    menu.add_name_to_db(mock_db_connection, created_by, name, person_id)
    cur.execute("SELECT * FROM 'names'")
    rows = cur.fetchall()
    assert len(rows) > 0, "No data found in the table"

    columns = [str(row) if row is not None else None for row in rows[0]]
    expected_row = ['1', '11', 'test_func', today, 'test_fn', None, 'test_ln',
                    None, None, None, None]
    assert columns == expected_row
