#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_person.py
"""Tests for "person" module."""

import datetime
import pytest
import sqlite3

from unittest.mock import patch

from context import helpers
from context import Menu
from context import MenuName
from context import Name
from context import NewPerson

from test_helpers import setup_db_persons  # noqa


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
    headline = "PERSONENEINTRAG"
    headline_final = f"| {headline}{' ' * 61}|"
    expected = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+

    1: Name
    2: Titel
    3: Zusätzliche persönliche Daten
    4: Personen zeigen
    9: Zurück
    \n"""

    return expected


@pytest.fixture
def display_wo_change():
    expected = """
    1: Name
    2: Titel
    3: Zusätzliche persönliche Daten
    4: Personen zeigen
    9: Zurück
    \n"""

    return expected


@pytest.fixture
def reset_parent_class_menu():
    Menu.last_caller_module = None
    Menu.current_caller_module = None
    Menu.navigation_stack = []

    return Menu


@pytest.fixture
def setup_db(mock_conn):
    created_by = "test_func"
    length = 2
    menu_person = NewPerson()
    name = Name("test_fn", "test_ln")

    menu_person.generate_table_persons(mock_conn)
    menu_person.add_person_to_db(mock_conn, created_by, name, length)
    mock_conn.commit()

    try:
        table_exists = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='persons'"  # noqa
        mock_conn.cursor().execute(table_exists)
        if mock_conn.cursor().fetchone()[0] == 1:
            print("table successfully created in fixture")
        else:
            print("table was not created in fixture")

    except sqlite3.Error as e:
        print(f"SQLite3 error: {e}")
        raise

    yield mock_conn

    mock_conn.close()


# ######## initialize Menu ####################################################

def test_start_menu_reset(reset_parent_class_menu):
    menu = reset_parent_class_menu()
    assert menu.last_caller_module is None
    assert menu.current_caller_module is None
    assert menu.navigation_stack == []


# ######## MenuName class #####################################################

def test_person_menu_class_init(reset_parent_class_menu):
    reset_parent_class_menu()
    menu = NewPerson()
    if menu.last_caller_module == "person":
        assert False
    assert menu.current_caller_module == "src.buha.scripts.person"
    assert menu.navigation_stack == ["person"]


def test_person_menu_display_menu(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu = NewPerson()
    company_name = "Test & Co.   "
    language = "de"
    task = "person"
    expected = display_with_change

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu.display_menu(company_name, language, task)
        actual, err = capsys.readouterr()
        assert actual == expected


# ######## MenuName run #######################################################

def test_person_menu_run(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu = NewPerson()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected = display_with_change

    with patch("builtins.input", return_value=None):
        menu.run(mock_conn, created_by, company_name, language)
        actual, err = capsys.readouterr()
        assert actual == expected


@patch("builtins.input", return_value="9")
def test_person_menu_run_get_choice_to_go_back(mocker):
    menu = NewPerson()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


@patch("builtins.input", return_value="not valid")
def test_person_menu_run_get_choice_not_valid(mocker, capsys, display_wo_change):  # noqa
    menu_person = NewPerson()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected_display = display_wo_change

    menu_person.run(mock_conn, created_by, company_name, language)
    actual_display, err = capsys.readouterr()

    assert actual_display == expected_display

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu_person.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


def test_person_menu_run_choice_is_1(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    menu_person = NewPerson()
    name = Name("test_fn", "test_ln")

    choose_option_side_effect = ["1", "9"]

    with patch("buha.scripts.person.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(menu_person, "enter_name", return_value=name) as mock_enter_name:  # noqa
            menu_person.run(mock_conn, created_by, company_name, language)  # noqa
            mock_enter_name.assert_called_once()


def test_person_menu_run_choice_is_2(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    menu_person = NewPerson()

    choose_option_side_effect = ["2", "9"]

    with patch("buha.scripts.person.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(menu_person, "enter_titles", return_value=None) as mock_enter_titles:  # noqa
            result = menu_person.run(mock_conn, created_by, company_name, language)  # noqa
            mock_enter_titles.assert_called_once()


def test_person_menu_run_choice_is_3(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    menu_person = NewPerson()

    choose_option_side_effect = ["3", "9"]

    with patch("buha.scripts.person.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(menu_person, "enter_particulars", return_value=None) as mock_enter_particulars:  # noqa
            menu_person.run(mock_conn, created_by, company_name, language)  # noqa
            mock_enter_particulars.assert_called_once()


def test_person_menu_run_choice_is_4(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    menu_person = NewPerson()

    choose_option_side_effect = ["4", "9"]

    with patch("buha.scripts.person.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(menu_person, "show_tables", return_value=None) as mock_show_tables:  # noqa
            menu_person.run(mock_conn, created_by, company_name, language)  # noqa
            mock_show_tables.assert_called_once()


# ######## generate table #####################################################

def test_person_generate_table_persons(mock_conn):
    menu = NewPerson()

    with mock_conn:
        menu.generate_table_persons(mock_conn)
        cur = mock_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persons'")  # noqa
        assert cur.fetchone() is not None, "Table 'persons' was not created"

        cur.execute("PRAGMA table_info('persons')")
        columns = [row[1] for row in cur.fetchall()]
        expected_columns = ['person_id', 'created_by', 'timestamp', 'first_name',  # noqa
                            'middle_names', 'last_name', 'initials']  # noqa
        assert columns == expected_columns, "Table schema for 'persons' does not match expected schema"  # noqa


# ######## add person to table ################################################

def test_person_add_person_to_db(mock_conn):
    created_by = "test_func"
    length = 2
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    name = Name("test_fn", "test_ln")

    menu = NewPerson()
    menu.generate_table_persons(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persons'")  # noqa
    assert cur.fetchone() is not None, "Table 'persons' was not created"

    menu.add_person_to_db(mock_conn, created_by, name, length)
    cur.execute("SELECT * FROM 'persons'")
    rows = cur.fetchall()
    assert len(rows) > 0, "No data found in the table"

    columns = [str(row) if row is not None else None for row in rows[0]]
    expected_row = ['1', 'test_func', timestamp, 'test_fn', 'None',
                    'test_ln', 'tt']
    assert columns == expected_row


# ######## get person_id from table ###########################################

def test_person_get_person_id(mock_conn):
    created_by = "test_func"
    length = 2

    name_1 = Name("test_fn", "test_ln")
    name_2 = Name("fn_test", "ln_test")

    menu = NewPerson()
    menu.generate_table_persons(mock_conn)
    menu.add_person_to_db(mock_conn, created_by, name_1, length)
    menu.add_person_to_db(mock_conn, created_by, name_2, length)

    expected_id = 1
    actual_id = menu.get_person_id(mock_conn, "tt")
    assert expected_id == actual_id

    expected_id = 2
    actual_id = menu.get_person_id(mock_conn, "fl")
    assert expected_id == actual_id


# ######## enter name #########################################################

def test_person_enter_name_None(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"

    menu = NewPerson()

    with patch.object(MenuName, "run", return_value=None):
        actual = menu.enter_name(mock_conn, created_by, company_name, language)
        assert actual is None


@patch("builtins.input", return_value="1")
def test_person_enter_name_fn_ln(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    name = Name(first_name="test_fn", last_name="test_ln")
    menu_person = NewPerson()

    with patch.object(menu_person, "generate_table_persons", autospec=True) as mock_generate_table:  # noqa
        with patch("buha.scripts.names.MenuName.run", return_value=name):
            menu_person.enter_name(mock_conn, created_by, company_name, language)  # noqa
            mock_generate_table.assert_called_once()


# ######## show table #########################################################

# took me two gorram weeks to get to this gorram function
@pytest.mark.usefixtures("setup_db_persons")
def test_person_show_tables(mock_conn, capsys):
    menu_person = NewPerson()
    expected = """(1, 'aa', 'today', 'Jon', 'D.', 'Outsh', 'jo')
(2, 'aa', 'today', 'Tom', 'D.', 'Pouch', 'tp')
(3, 'aa', 'today', 'Bob', 'D.', 'Vouch', 'bv')
(4, 'aa', 'today', 'Dob', 'D.', 'Grump', 'dg')
(5, 'aa', 'today', 'Sam', 'D.', 'Bump', 'sb')
(6, 'aa', 'today', 'Amy', 'D.', 'Hoot', 'ah')
"""

    with patch("builtins.input", return_value="y"):
        menu_person.show_tables(mock_conn, "persons")
        actual, err = capsys.readouterr()
        assert actual == expected
