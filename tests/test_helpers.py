#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_helpers.py
"""Tests for "helpers" module."""

import os
import pytest
import sqlite3

from pathlib import Path
from pyfakefs.fake_filesystem_unittest import Patcher
from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import create_autospec

from context import check_databases
from context import check_for_matches
from context import check_if_internal
from context import continue_
from context import create_headline
from context import get_person_id
from context import helpers
from context import initials_in_table
from context import mk_initials
from context import Menu
from context import Name
from context import path_to_database
from context import path_to_db_dir
from context import pick_language
from context import show_all
from context import show_my_table
from context import show_table
from context import state_company


@pytest.fixture
def mock_conn():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def no_clear_screen():
    with patch("os.system") as mock_system:
        yield mock_system


# ######## basic Menu class ###################################################

def test_basic_menu_class_attributes():
    menu = Menu()
    assert menu.last_caller_module is None
    assert menu.current_caller_module is None
    assert menu.navigation_stack == []


def test_basic_menu_class_menu_changed_True_attr():
    menu = Menu()
    Menu.last_caller_module = "main"
    Menu.current_caller_module = "start"
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
    os.system.assert_called_with("clear")


def test_basic_menu_class_change_menu(mocker):
    menu = Menu()
    Menu.navigation_stack = ["person"]
    task = "names"
    menu.change_menu(task)
    assert Menu.navigation_stack == ["person", "names"]

    with patch.object(helpers.Menu, "get_caller_module_name", return_value="names"):  # noqa
        menu.change_menu(task)
        assert Menu.current_caller_module == "names"


def test_basic_menu_class_change_menu_no_change(mocker):
    menu = Menu()
    Menu.navigation_stack = ["person"]
    Menu.last_caller_module = "person"
    task = "person"
    menu.change_menu(task)
    assert Menu.navigation_stack == ["person", "person"]

    with patch.object(helpers.Menu, "get_caller_module_name", return_value="src.buha.scripts.helpers"):  # noqa
        menu.change_menu(task)
        assert Menu.current_caller_module != "src.buha.scripts.helpers"


def test_basic_menu_class_go_back():
    menu = Menu()
    Menu.last_caller_module = "start"
    Menu.current_caller_module = "new entry"
    Menu.navigation_stack = ["start", "new entry"]

    with patch.object(helpers.Menu, "get_caller_module_name", return_value="start"):  # noqa
        menu.go_back()
        assert Menu.last_caller_module == "start"
        assert len(Menu.navigation_stack) == 1


def test_basic_menu_class_go_back_no_stack():
    menu = Menu()
    Menu.last_caller_module = "start"
    Menu.current_caller_module = "new entry"
    Menu.navigation_stack = []

    with patch.object(helpers.Menu, "get_caller_module_name", return_value="start"):  # noqa
        menu.go_back()
        assert Menu.last_caller_module == "start"


def test_basic_menu_class_get_caller_module_name_type_str():
    menu = Menu()
    assert isinstance(menu.get_caller_module_name(), str)


def test_basic_menu_class_display_menu_wo_headline(mocker, capsys):
    mocker.patch("os.system")
    menu = Menu()

    expected_task_menu = """
    1: Einloggen
    9: Beenden
    \n"""

    with patch.object(helpers.Menu, "menu_changed", return_value=False):
        menu.display_menu("Test Ltd.", "de", "login")
        actual_task_menu, err = capsys.readouterr()
        assert actual_task_menu == expected_task_menu


def test_basic_menu_class_display_menu_with_headline(mocker, capsys):
    mocker.patch("os.system")
    menu = Menu()
    company_name = "Test Ltd."
    company_line = f"| {company_name}{' ' * 67}|"
    headline = "LOGIN MENÜ"
    headline_final = f"| {headline}{' ' * 66}|"
    expected = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+

    1: Einloggen
    9: Beenden
    \n"""

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu.display_menu("Test_Ltd..db", "de", "login")
        actual, err = capsys.readouterr()
        assert actual == expected


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

def test_mk_initials_not_in_table_length2(mock_conn):
    with patch.object(helpers, "initials_in_table", return_value=False):
        first_name = "Peter"
        last_name = "Pan"
        name = Name(first_name, last_name)
        length = 2
        expected = "pp"
        actual = mk_initials(mock_conn, name, length)
        assert actual == expected


def test_mk_initials_not_in_table_length_modulo2(mock_conn):
    with patch.object(helpers, "initials_in_table", return_value=False):
        first_name = "Peter"
        last_name = "Pan"
        name = Name(first_name, last_name)
        length = 4
        expected = "pepa"
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


def test_mk_initials_with_recursion(mock_conn):
    first_name = "Peter"
    last_name = "Pan"
    name = Name(first_name, last_name)
    length = 2
    call_count = 0

    def side_effect(*args):
        nonlocal call_count
        call_count += 1
        return call_count == 1

    with patch("buha.scripts.helpers.initials_in_table", side_effect=side_effect) as mock_func:  # noqa
        actual = mk_initials(mock_conn, name, length)
        expected = "pep"  # Expecting length to increase to 3
        assert actual == expected
        assert mock_func.call_count == 2


# ######## initials in table ##################################################


def test_print_output():
    print("This is a test print statement.")
    assert True


def test_initials_in_table(mocker):
    mock_cursor = create_autospec(sqlite3.Cursor)
    mock_cursor.fetchall.return_value = [('jd',), ('js',)]

    mock_conn = create_autospec(sqlite3.Connection)
    mock_conn.cursor.return_value = mock_cursor

    def execute_side_effect(query):
        print(f"Executing query: {query}")
        return mock_cursor

    mock_cursor.execute.side_effect = execute_side_effect

    in_table = initials_in_table(mock_conn, 'jd')
    print(f"Test result for 'jd': {in_table}")
    assert in_table

    in_table = initials_in_table(mock_conn, 'ab')
    print(f"Test result for 'ab': {in_table}")
    if in_table:
        assert False


# ######## state company ######################################################

def test_state_company():
    with patch("builtins.input", return_value="2nd Test Ltd."):
        language = "en"
        actual = state_company(language)
        expected = "2nd_Test_Ltd..db"
        assert isinstance(actual, str)
        assert actual == expected


# ######## check for matches ##################################################

def test_check_for_matches_80_percent():
    eighty = "abcdefgh"
    company_name = "abcdefghij"
    targets = [company_name]
    expected = company_name
    actual = check_for_matches(eighty, targets, "de")
    assert actual == expected


def test_check_for_matches_50_percent():
    fifty = "abcde"
    company_name = "abcdefghij"
    targets = [company_name]
    expected = company_name
    with patch("builtins.input", return_value="y"):
        actual = check_for_matches(fifty, targets, "de")
        assert actual == expected


def test_check_for_matches_80_percent_several_targets():
    eighty = "abcdefgh"
    company_name = "abcdefghij"
    targets = ["abcdefghijklm", "acdeghij", company_name]
    expected = company_name
    actual = check_for_matches(eighty, targets, "de")
    assert actual == expected


def test_check_for_matches_no_match():
    no_match = "edcba"
    company_name = "abcdefghij"
    targets = [company_name]
    expected = None
    actual = check_for_matches(no_match, targets, "de")
    assert actual == expected


def test_check_for_matches_fifty_no_match():
    no_match = "abcdef"
    company_name = "abcdefghij"
    targets = [company_name]
    expected = None
    with patch("builtins.input", return_value="N"):
        actual = check_for_matches(no_match, targets, "de")
        assert actual == expected


# ######## pick language ######################################################

def test_pick_language_type():
    with patch("builtins.input", return_value="de"):
        ret_val = pick_language()
        assert isinstance(ret_val, str)


def test_pick_language_clear_screen_called(mocker):
    mocker.patch("os.system")
    with patch("builtins.input", return_value="de"):
        pick_language()
        os.system.assert_called_once()
        os.system.assert_called_with("clear")


@patch("builtins.input", return_value="de")
@patch("sys.exit")
def test_pick_language_valid_input(mock_exit, mock_input):
    assert pick_language() == "de"
    mock_exit.assert_not_called()


@patch("builtins.input", return_value="xx")
@patch("sys.exit", Mock(side_effect=SystemExit))
def test_pick_language_invalid_input_calls_sys_exit(mock_exit):
    with pytest.raises(SystemExit):
        pick_language()
    mock_exit.assert_called()


# ######## continue_ ##########################################################

def test_continue_yes():
    with patch("builtins.input", return_value="y"):
        assert continue_()


def test_continue_no():
    with patch("builtins.input", return_value="N"):
        if continue_():
            assert False


# ######## get person id from table persons ###################################

@pytest.fixture
def setup_db_persons(mock_conn):
    table_persons = """CREATE TABLE IF NOT EXISTS persons (
                    person_id INTEGER PRIMARY KEY,
                    created_by TEXT,
                    timestamp TEXT,
                    first_name TEXT NOT NULL,
                    middle_names TEXT,
                    last_name TEXT NOT NULL,
                    initials TEXT NOT NULL
                    )"""

    add_person = """INSERT INTO persons (
                created_by, timestamp, first_name,
                middle_names, last_name, initials)
                VALUES (?, ?, ?, ?, ?, ?)"""

    pers_jo = ("aa", "today", "Jon", "D.", "Outsh", "jo")
    pers_tp = ("aa", "today", "Tom", "D.", "Pouch", "tp")
    pers_bv = ("aa", "today", "Bob", "D.", "Vouch", "bv")
    pers_dg = ("aa", "today", "Dob", "D.", "Grump", "dg")
    pers_sb = ("aa", "today", "Sam", "D.", "Bump", "sb")
    pers_ah = ("aa", "today", "Amy", "D.", "Hoot", "ah")

    with mock_conn:
        session = mock_conn.cursor()
        session.execute(table_persons)
        for pers in [pers_jo, pers_tp, pers_bv, pers_dg, pers_sb, pers_ah]:
            session.execute(add_person, pers)
        session.connection.commit()


@pytest.mark.usefixtures("setup_db_persons")
def test_get_person_id_jo(mock_conn):
    person_id = get_person_id(mock_conn, "jo")
    assert person_id == 1


@pytest.mark.usefixtures("setup_db_persons")
def test_get_person_id_tp(mock_conn):
    person_id = get_person_id(mock_conn, "tp")
    assert person_id == 2


@pytest.mark.usefixtures("setup_db_persons")
def test_get_person_id_dg(mock_conn):
    person_id = get_person_id(mock_conn, "dg")
    assert person_id == 4


@pytest.mark.usefixtures("setup_db_persons")
def test_get_person_id_ah(mock_conn):
    person_id = get_person_id(mock_conn, "ah")
    assert person_id == 6


@pytest.mark.usefixtures("setup_db_persons")
def test_get_person_id_type_int(mock_conn):
    person_id = get_person_id(mock_conn, "sb")
    assert isinstance(person_id, int)


# ######## check if internal ##################################################

def test_check_if_internal_type():
    with patch("builtins.input", return_value="y"):
        assert isinstance(check_if_internal(), bool)


def test_check_if_internal_type_True():
    with patch("builtins.input", return_value="y"):
        assert check_if_internal()


def test_check_if_internal_type_False():
    with patch("builtins.input", return_value="N"):
        if check_if_internal():
            assert False


# ######## show tables persons ################################################

@pytest.mark.usefixtures("setup_db_persons")
def test_show_table(mock_conn, capsys):
    expected = """(1, 'aa', 'today', 'Jon', 'D.', 'Outsh', 'jo')
(2, 'aa', 'today', 'Tom', 'D.', 'Pouch', 'tp')
(3, 'aa', 'today', 'Bob', 'D.', 'Vouch', 'bv')
(4, 'aa', 'today', 'Dob', 'D.', 'Grump', 'dg')
(5, 'aa', 'today', 'Sam', 'D.', 'Bump', 'sb')
(6, 'aa', 'today', 'Amy', 'D.', 'Hoot', 'ah')
"""

    with patch("builtins.input", return_value="y"):
        show_table(mock_conn, "persons")
        actual, err = capsys.readouterr()
        assert actual == expected


# ######## show my table persons ##############################################

@pytest.mark.usefixtures("setup_db_persons")
def test_show_my_table(mock_conn, capsys):
    expected = """(1, 'aa', 'today', 'Jon', 'D.', 'Outsh', 'jo')
"""

    with patch("builtins.input", return_value="y"):
        show_my_table(mock_conn, "persons", 1)
        actual, err = capsys.readouterr()
        assert actual == expected


@pytest.mark.usefixtures("setup_db_persons")
def test_show_my_table_no_output(mock_conn, capsys):
    expected = ''

    with patch("builtins.input", return_value="y"):
        show_my_table(mock_conn, "persons", 9)
        actual, err = capsys.readouterr()
        assert actual == expected


# ######## show tables all ####################################################

@pytest.fixture
def setup_db_names(mock_conn):
    table_names = """CREATE TABLE IF NOT EXISTS names (
                        name_id INTEGER PRIMARY KEY,
                        person_id INTEGER,
                        created_by TEXT,
                        timestamp TEXT,
                        first_name TEXT NOT NULL,
                        middle_names TEXT,
                        last_name TEXT NOT NULL,
                        nickname TEXT,
                        maiden_name TEXT,
                        suffix TEXT,
                        salutation TEXT,
                        FOREIGN KEY (person_id)
                        REFERENCES persons(person_id)
                        ON DELETE CASCADE
                        )"""

    add_name = """INSERT INTO names (
                    person_id, created_by, timestamp, first_name,
                    middle_names, last_name, nickname, maiden_name, suffix,
                    salutation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    name_jo = (1, "aa", "today", "Jon", "D.", "Outsh", "", "", "", "Hr.")
    name_tp = (2, "aa", "today", "Tom", "D.", "Pouch", "", "", "Jr.", "")
    name_bv = (3, "aa", "today", "Bob", "D.", "Vouch", "", "", "", "")
    name_dg = (4, "aa", "today", "Dob", "D.", "Grump", "", "", "", "Hr.")
    name_sb = (5, "aa", "today", "Sam", "D.", "Bump", "", "", "Sr.", "Mr.")
    name_ah = (6, "aa", "today", "Amy", "D.", "Hoot", "", "", "", "Fr.")

    with mock_conn:
        session = mock_conn.cursor()
        session.execute(table_names)
        for name in [name_jo, name_tp, name_bv, name_dg, name_sb, name_ah]:
            session.execute(add_name, name)
        session.connection.commit()


@pytest.fixture
def setup_db_settings(mock_conn):
    table_settings = """CREATE TABLE IF NOT EXISTS settings (
                        settings_id INTEGER PRIMARY KEY,
                        person_id INTEGER,
                        created_by TEXT,
                        timestamp TEXT,
                        language TEXT,
                        initials TEXT,
                        is_internal BOOL,
                        salt BLOB NOT NULL,
                        password_hash BLOB NOT NULL,
                        FOREIGN KEY (person_id)
                            REFERENCES persons(person_id)
                            ON DELETE CASCADE
                        )"""

    add_settings = """INSERT INTO settings (
                      person_id, created_by, timestamp, language, initials,
                      is_internal, salt, password_hash)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

    settings_jo = (1, "aa", "today", "de", "jo", 1, b"a", b"abc")
    settings_tp = (2, "aa", "today", "en", "tp", 1, b"b", b"abc")
    settings_bv = (3, "aa", "today", "en", "bv", 0, b"c", b"abc")
    settings_dg = (4, "aa", "today", "de", "dg", 0, b"d", b"abc")
    settings_sb = (5, "aa", "today", "en", "sb", 1, b"e", b"abc")
    settings_ah = (6, "aa", "today", "de", "ah", 1, b"f", b"abc")

    with mock_conn:
        session = mock_conn.cursor()
        session.execute(table_settings)
        for setting in [settings_jo, settings_tp, settings_bv, settings_dg,
                        settings_sb, settings_ah]:
            session.execute(add_settings, setting)
        session.connection.commit()


@pytest.mark.usefixtures("setup_db_persons")
@pytest.mark.usefixtures("setup_db_names")
@pytest.mark.usefixtures("setup_db_settings")
def test_show_all(mock_conn, capsys):
    expected = """(1, 'aa', 'today', 'Jon', 'D.', 'Outsh', 'jo')
(1, 1, 'aa', 'today', 'Jon', 'D.', 'Outsh', '', '', '', 'Hr.')
(1, 1, 'aa', 'today', 'de', 'jo', 1, b'a', b'abc')
"""

    with patch("builtins.input", return_value="y"):
        show_all(mock_conn, 1)
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


# ######## check databases ####################################################

def test_check_databases_2_targets():
    with Patcher() as patcher:
        patcher.fs.create_dir(abs_path_to_data)
        patcher.fs.create_file(f"{abs_path_to_data}/__init__.bye")
        patcher.fs.create_file(f"{abs_path_to_data}/test_1.db")
        patcher.fs.create_file(f"{abs_path_to_data}/nononono.txt")
        patcher.fs.create_file(f"{abs_path_to_data}/test_2.db")
        patcher.fs.create_file(f"{abs_path_to_data}/terrible_idea.bd")

        expected_targets = ["test_1.db", "test_2.db"]
        actual_targets = check_databases()
        assert actual_targets == expected_targets


def test_check_databases_no_target():
    with Patcher() as patcher:
        patcher.fs.create_dir(abs_path_to_data)
        patcher.fs.create_file(f"{abs_path_to_data}/__init__.bye")
        patcher.fs.create_file(f"{abs_path_to_data}/test_1.dbb")
        patcher.fs.create_file(f"{abs_path_to_data}/nononono.txt")
        patcher.fs.create_file(f"{abs_path_to_data}/test_2.ddb")
        patcher.fs.create_file(f"{abs_path_to_data}/terrible_idea.bd")

        expected_targets = []
        actual_targets = check_databases()
        assert actual_targets == expected_targets
