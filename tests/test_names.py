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
    headline = "NAMENSEINTRÄGE"  # 14
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
    menu_name = MenuName()
    menu_name.reset_entries()
    for key, value in menu_name.entries.items():
        assert value is None


def test_name_menu_class_init(reset_parent_class_menu):
    reset_parent_class_menu()
    menu_name = MenuName()
    if menu_name.last_caller_module == "names":
        assert False
    assert menu_name.current_caller_module == "src.buha.scripts.names"
    assert menu_name.navigation_stack == ["names"]


def test_name_menu_display_menu(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_name = MenuName()
    company_name = "Test & Co.   "
    language = "de"
    task = "names"
    expected = display_with_change

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu_name.display_menu(company_name, language, task)
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


@patch("builtins.input", side_effect=["1", "test_fn", "9"])
def test_name_menu_run_action_triggers_change_menu(mocker):
    menu = MenuName()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"

    with patch.object(helpers.Menu, "change_menu") as mock_super:
        menu.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


@patch("builtins.input", return_value="not valid")
def test_name_menu_run_get_choice_not_valid(mocker, capsys, display_wo_change):  # noqa
    menu = MenuName()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected_display = display_wo_change

    menu.run(mock_conn, created_by, company_name, language)
    actual_display, err = capsys.readouterr()

    assert actual_display == expected_display


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
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

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
    expected_row = ['1', '11', 'test_func', timestamp, 'test_fn', None,
                    'test_ln', None, None, None, None]
    assert columns == expected_row


def test_names_name_already_in_db_wo_middlename(mock_db_connection):
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_fn"
    menu.entries["ln"] = "test_ln"
    name_1 = menu.generate_name_instance()
    name_2 = menu.generate_name_instance()

    menu.generate_table_names(mock_db_connection)
    menu.add_name_to_db(mock_db_connection, created_by, name_1, person_id)

    assert isinstance(menu.name_already_in_db(mock_db_connection, name_2, language), bool)  # noqa
    assert menu.name_already_in_db(mock_db_connection, name_2, language)


def test_names_name_already_in_db_with_one_middlename(mock_db_connection):
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_fn"
    menu.entries["ln"] = "test_ln"
    name_1 = menu.generate_name_instance()
    menu.entries["mn"] = "test_mn"
    name_2 = menu.generate_name_instance()

    menu.generate_table_names(mock_db_connection)
    menu.add_name_to_db(mock_db_connection, created_by, name_1, person_id)

    if menu.name_already_in_db(mock_db_connection, name_2, language):
        assert False


def test_names_name_already_in_db_with_same_middlenames(mock_db_connection):
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_fn"
    menu.entries["ln"] = "test_ln"
    menu.entries["mn"] = "test_mn"
    name_1 = menu.generate_name_instance()
    name_2 = menu.generate_name_instance()

    menu.generate_table_names(mock_db_connection)
    menu.add_name_to_db(mock_db_connection, created_by, name_1, person_id)

    assert menu.name_already_in_db(mock_db_connection, name_2, language)


def test_names_name_already_in_db_wo_middlename_and_several_names(mock_db_connection):  # noqa
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_1_fn"
    menu.entries["ln"] = "test_1_ln"
    name_1 = menu.generate_name_instance()

    menu.entries["fn"] = "test_2_fn"
    menu.entries["ln"] = "test_2_ln"
    name_2 = menu.generate_name_instance()

    menu.entries["fn"] = "test_3_fn"
    menu.entries["ln"] = "test_3_ln"
    name_3 = menu.generate_name_instance()

    menu.generate_table_names(mock_db_connection)
    menu.add_name_to_db(mock_db_connection, created_by, name_1, person_id)
    menu.add_name_to_db(mock_db_connection, created_by, name_2, person_id)
    menu.add_name_to_db(mock_db_connection, created_by, name_3, person_id)

    assert menu.name_already_in_db(mock_db_connection, name_2, language)


def test_names_name_not_already_in_db_wo_middlename_and_several_names(mock_db_connection):  # noqa
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_1_fn"
    menu.entries["ln"] = "test_1_ln"
    name_1 = menu.generate_name_instance()

    menu.entries["fn"] = "test_2_fn"
    menu.entries["ln"] = "test_2_ln"
    name_2 = menu.generate_name_instance()

    menu.entries["fn"] = "test_3_fn"
    menu.entries["ln"] = "test_3_ln"
    name_3 = menu.generate_name_instance()

    menu.generate_table_names(mock_db_connection)
    menu.add_name_to_db(mock_db_connection, created_by, name_1, person_id)
    menu.add_name_to_db(mock_db_connection, created_by, name_2, person_id)

    if menu.name_already_in_db(mock_db_connection, name_3, language):
        assert False


def test_names_name_not_already_in_db_wo_middlename_and_several_names_and_same_fn(mock_db_connection):  # noqa
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_1_fn"
    menu.entries["ln"] = "test_1_ln"
    name_1 = menu.generate_name_instance()

    menu.entries["fn"] = "test_2_fn"
    menu.entries["ln"] = "test_2_ln"
    name_2 = menu.generate_name_instance()

    menu.entries["fn"] = "test_2_fn"
    menu.entries["ln"] = "test_3_ln"
    name_3 = menu.generate_name_instance()

    menu.generate_table_names(mock_db_connection)
    menu.add_name_to_db(mock_db_connection, created_by, name_1, person_id)
    menu.add_name_to_db(mock_db_connection, created_by, name_2, person_id)

    if menu.name_already_in_db(mock_db_connection, name_3, language):
        assert False


# ######## handle double entry ################################################

@patch("builtins.input", return_value="test_foo")
def test_names_handle_double_entry_true(mock_db_connection):
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_1_fn"
    menu.entries["ln"] = "test_1_ln"
    name_1 = menu.generate_name_instance()

    with patch.object(menu, "enter_middlenames", autospec=True) as mock_enter_middlenames:  # noqa
        with patch.object(menu, "name_already_in_db", return_value=True):
            menu.handle_double_entry(mock_conn, created_by, name_1, person_id, language)  # noqa
            mock_enter_middlenames.assert_called_once()


@patch("builtins.input", return_value="test_foo")
def test_names_handle_double_entry_false(mock_db_connection):
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_1_fn"
    menu.entries["ln"] = "test_1_ln"
    name_1 = menu.generate_name_instance()

    with patch.object(menu, "enter_middlenames", autospec=True) as mock_enter_middlenames:  # noqa
        with patch.object(menu, "name_already_in_db", return_value=False):
            with patch.object(menu, "add_name_to_db", autospec=True) as mock_add_name:  # noqa
                menu.handle_double_entry(mock_conn, created_by, name_1, person_id, language)  # noqa
                mock_enter_middlenames.assert_called_once()
                mock_add_name.assert_called_once_with(mock_conn, created_by, name_1, person_id)  # noqa


@patch("builtins.input", return_value="test_foo")
def test_names_commit_name_to_db_but_double(mock_db_connection):
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_1_fn"
    menu.entries["ln"] = "test_1_ln"
    name = menu.generate_name_instance()

    with patch.object(menu, "generate_table_names", autospec=True) as mock_generate_table_names:  # noqa
        with patch.object(menu, "name_already_in_db", return_value=True):
            with patch.object(menu, "handle_double_entry", autospec=True) as mock_handle_double:  # noqa
                menu.commit_name_to_db(mock_conn, created_by, name, person_id, language)  # noqa
                mock_generate_table_names.assert_called_once()
                mock_handle_double.assert_called_once_with(mock_conn, created_by, name, person_id, language)  # noqa


@patch("builtins.input", return_value="test_foo")
def test_names_commit_name_to_db_new_entry(mock_db_connection):
    person_id = "11"
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_1_fn"
    menu.entries["ln"] = "test_1_ln"
    name = menu.generate_name_instance()

    with patch.object(menu, "generate_table_names", autospec=True) as mock_generate_table_names:  # noqa
        with patch.object(menu, "name_already_in_db", return_value=False):
            with patch.object(menu, "add_name_to_db", autospec=True) as mock_add_name:  # noqa
                menu.commit_name_to_db(mock_conn, created_by, name, person_id, language)  # noqa
                mock_generate_table_names.assert_called_once()
                mock_add_name.assert_called_once_with(mock_conn, created_by, name, person_id)  # noqa
                for key, value in menu.entries.items():
                    assert value is None


# ######## commit #############################################################

def test_names_commit_type_fn_is_None():
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = None
    menu.entries["ln"] = "test_1_ln"
    name = menu.generate_name_instance()

    with patch.object(menu, "generate_name_instance", return_value=name):
        assert menu.commit(mock_conn, created_by, language) is None


def test_names_commit_type_ln_is_None():
    created_by = "test_func"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_fn"
    menu.entries["ln"] = None
    name = menu.generate_name_instance()

    with patch.object(menu, "generate_name_instance", return_value=name):
        assert menu.commit(mock_conn, created_by, language) is None


@patch("builtins.input", return_value="8")
def test_names_commit_input_is_8(mock_conn):
    created_by = "test_func"
    company_name = "test_company"
    language = "de"

    menu = MenuName()
    menu.entries["fn"] = "test_fn"
    menu.entries["ln"] = "test_ln"
    expected_name = menu.generate_name_instance()

    with patch.object(menu, "commit", return_value=expected_name):
        actual_name = menu.run(mock_conn, created_by, company_name, language)
        assert actual_name == expected_name
