#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_login.py
"""Tests for "login" module."""

import pytest
import sqlite3

from unittest.mock import MagicMock
from unittest.mock import patch

from context import add_settings
from context import generate_table_settings
from context import helpers
from context import LoginMenu
from context import login
from context import Menu
from context import Name
from context import NewPerson
from context import settings


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
    headline = "LOGIN MENÜ"  # 10
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

    return expected


@pytest.fixture
def display_wo_change():
    expected = """
    1: Einloggen
    9: Beenden
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
    language = "de"
    person_id = 1
    initials = "fl"

    generate_table_settings(mock_conn)
    add_settings(mock_conn, created_by, language, person_id, initials)  # noqa
    mock_conn.commit()

    try:
        table_exists = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='settings'"  # noqa
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

def test_login_menu_reset(reset_parent_class_menu):
    menu = reset_parent_class_menu()
    assert menu.last_caller_module is None
    assert menu.current_caller_module is None
    assert menu.navigation_stack == []


# ######## LoginMenu class ####################################################

def test_login_menu_class_init(reset_parent_class_menu):
    reset_parent_class_menu()
    menu_login = LoginMenu()
    if menu_login.last_caller_module == "login":
        assert False
    assert menu_login.current_caller_module == "src.buha.scripts.login"
    assert menu_login.navigation_stack == ["login"]


def test_login_menu_display_menu(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_login = LoginMenu()
    company_name = "Test & Co.   "
    language = "de"
    task = "login"
    expected = display_with_change

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu_login.display_menu(company_name, language, task)
        actual, err = capsys.readouterr()
        assert actual == expected


# ######## LoginMenu run ######################################################

def test_login_menu_run(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_login = LoginMenu()
    company_name = "Test & Co.   "
    language = "de"

    with patch("builtins.input", return_value=None):
        with patch.object(menu_login, "display_menu", return_value=None) as mock_display_menu:  # noqa
            menu_login.run(mock_conn, language, company_name)
            mock_display_menu.assert_called_once()


@patch("builtins.input", return_value="9")
def test_login_menu_run_get_choice_to_go_back(mocker):
    menu_login = LoginMenu()
    company_name = "Test & Co.   "
    language = "de"

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu_login.run(mock_conn, language, company_name)
        mock_super.assert_called_once()


@patch("builtins.input", return_value="not valid")
def test_login_menu_run_get_choice_not_valid(mocker, capsys, display_wo_change):  # noqa
    menu_login = LoginMenu()
    company_name = "Test & Co.   "
    language = "de"
    expected_display = display_wo_change

    menu_login.run(mock_conn, language, company_name)
    actual_display, err = capsys.readouterr()

    assert actual_display == expected_display

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu_login.run(mock_conn, language, company_name)
        mock_super.assert_called_once()


# login
def test_login_menu_run_choice_is_1(mock_conn):
    company_name = "Test & Co.   "
    language = "de"
    menu_login = LoginMenu()
    expected_auth, expected_initials = True, "tt"

    choose_option_side_effect = ["1", "9"]

    with patch("buha.scripts.login.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(menu_login, "login_employee", return_value=(expected_auth, expected_initials)) as mock_login:  # noqa
            auth, initials = menu_login.run(mock_conn, language, company_name)  # noqa
            mock_login.assert_called_once()
            assert (auth, initials) == (expected_auth, expected_initials)


# ######## password ###########################################################

@patch("builtins.input", return_value="y")
def test_login_password_correct(mock_conn):
    created_by = "test_func"
    initials = "tt"
    password = "mock_password"
    language = "de"
    person_id = 1

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
    settings.add_settings(mock_conn, created_by, language, person_id, initials)

    with patch.object(login, "hash_password", return_value=("mock_salt", "mock_password")) as mock_hash_password:  # noqa
        with patch.object(settings, "generate_table_settings", return_value=None) as mock_generate_table_settings:  # noqa
            login.password_correct(mock_conn, initials, password)
            mock_hash_password.assert_called_once()


def test_password_not_correct_salt_is_None(mock_conn):
    # written by ChatGPT

    initials = "test_initials"
    password = "test_password"
    fake_salt = b"fake_salt"
    fake_hash = b"fake_hashed_password"

    # Mock cursor and connection
    mock_cursor = MagicMock()
    mock_conn = MagicMock()

    # Set up the cursor's behavior
    mock_conn.cursor.return_value = mock_cursor

    # Test when both salt and password hash are present
    mock_cursor.fetchone.side_effect = [(fake_salt,), (fake_hash,)]
    with patch('sqlite3.connect', return_value=mock_conn):
        assert login.password_correct(mock_conn, initials, password) == (fake_hash == login.hash_password(password, fake_salt)[1])  # noqa

    # Test when salt is not present
    mock_cursor.fetchone.side_effect = [None, fake_hash]
    with patch('sqlite3.connect', return_value=mock_conn):
        assert not login.password_correct(mock_conn, initials, password)


def test_password_not_correct_hashed_pw_is_None(mock_conn):
    # written by ChatGPT

    initials = "test_initials"
    password = "test_password"
    fake_salt = b"fake_salt"
    fake_hash = b"fake_hashed_password"

    # Mock cursor and connection
    mock_cursor = MagicMock()
    mock_conn = MagicMock()

    # Set up the cursor's behavior
    mock_conn.cursor.return_value = mock_cursor

    # Test when both salt and password hash are present
    mock_cursor.fetchone.side_effect = [(fake_salt,), (fake_hash,)]
    with patch('sqlite3.connect', return_value=mock_conn):
        assert login.password_correct(mock_conn, initials, password) == (fake_hash == login.hash_password(password, fake_salt)[1])  # noqa

    # Test when password hash is not present
    mock_cursor.fetchone.side_effect = [fake_salt, None]
    with patch('sqlite3.connect', return_value=mock_conn):
        assert not login.password_correct(mock_conn, initials, password)


def test_password_hash(mock_conn):
    password = "test_password"
    mock_salt = b"mock_salt"

    with patch("os.urandom", return_value=mock_salt) as mock_urandom:
        login.hash_password(password)
        mock_urandom.assert_called_once()


# ######## internal ###########################################################

def test_login_is_internal_True(mock_conn):
    created_by = "test_func"
    initials = "tt"
    language = "de"
    person_id = 1

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
    with patch("builtins.input", return_value="y"):
        settings.add_settings(mock_conn, created_by, language, person_id, initials)  # noqa

    res = login.is_internal(mock_conn, initials)
    assert res


def test_login_is_internal_False(mock_conn):
    created_by = "test_func"
    initials = "tt"
    language = "de"
    person_id = 1

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
    with patch("builtins.input", return_value="N"):
        settings.add_settings(mock_conn, created_by, language, person_id, initials)  # noqa

    res = login.is_internal(mock_conn, initials)
    if res:
        assert False


def test_login_is_internal_no_entry(mock_conn):
    created_by = "test_func"
    initials = "tt"
    test_initials = "not_in_table"
    language = "de"
    person_id = 1

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
    with patch("builtins.input", return_value="y"):
        settings.add_settings(mock_conn, created_by, language, person_id, initials)  # noqa

    res = login.is_internal(mock_conn, initials)
    assert res

    res = login.is_internal(mock_conn, test_initials)
    if res:
        assert False


# ######## initials ###########################################################

def test_login_initials_in_table(mock_conn):
    created_by = "test_func"
    length = 2

    name = Name("test_fn", "test_ln")
    initials = "tt"

    menu = NewPerson()
    menu.generate_table_persons(mock_conn)
    menu.add_person_to_db(mock_conn, created_by, name, length)

    res = login.initials_in_table(mock_conn, initials)
    assert res


def test_login_initials_not_in_table(mock_conn):
    created_by = "test_func"
    length = 2

    name = Name("test_fn", "test_ln")
    initials = "not_in_table"

    menu = NewPerson()
    menu.generate_table_persons(mock_conn)
    menu.add_person_to_db(mock_conn, created_by, name, length)

    res = login.initials_in_table(mock_conn, initials)
    if res:
        assert False


# ######## login ##############################################################

def test_login_login_employee_initials_not_in_table(mock_conn):
    menu_login = LoginMenu()
    created_by = "test_func"
    length = 2
    language = "de"
    company_name = "Test & Co."

    name = Name("test_fn", "test_ln")

    menu = NewPerson()
    menu.generate_table_persons(mock_conn)
    menu.add_person_to_db(mock_conn, created_by, name, length)

    with patch("builtins.input", return_value="no no"):
        with patch("buha.scripts.login.enter_initials") as mock_enter_initials:
            res = menu_login.login_employee(mock_conn, language, company_name)

            mock_enter_initials.assert_called_once()
            assert res == (False, None)


def test_login_login_employee_initials_in_table_pw_correct(mock_conn):
    menu_login = LoginMenu()
    created_by = "test_func"
    length = 2
    language = "de"
    company_name = "Test & Co."
    initials = "tt"
    person_id = 1

    name = Name("test_fn", "test_ln")

    menu = NewPerson()
    menu.generate_table_persons(mock_conn)
    menu.add_person_to_db(mock_conn, created_by, name, length)

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
    with patch("builtins.input", return_value="y"):
        settings.add_settings(mock_conn, created_by, language, person_id, initials)  # noqa

    with patch("getpass.getpass", return_value="asd"):
        with patch("buha.scripts.login.initials_in_table", return_value=True):
            with patch("buha.scripts.login.enter_initials", return_value="tt"):
                res = menu_login.login_employee(mock_conn, language, company_name)  # noqa

                assert res == (True, "tt")


def test_login_login_employee_initials_in_table_pw_not_correct(mock_conn):
    menu_login = LoginMenu()
    created_by = "test_func"
    length = 2
    language = "de"
    company_name = "Test & Co."
    initials = "tt"
    person_id = 1

    name = Name("test_fn", "test_ln")

    menu = NewPerson()
    menu.generate_table_persons(mock_conn)
    menu.add_person_to_db(mock_conn, created_by, name, length)

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
    with patch("builtins.input", return_value="y"):
        settings.add_settings(mock_conn, created_by, language, person_id, initials)  # noqa

    with patch("getpass.getpass", return_value="not correct"):
        with patch("buha.scripts.login.initials_in_table", return_value=True):
            with patch("buha.scripts.login.enter_initials", return_value="tt"):
                res = menu_login.login_employee(mock_conn, language, company_name)  # noqa

                if res == (True, "tt"):
                    assert False


def test_login_login_employee_is_not_internal(mock_conn):
    menu_login = LoginMenu()
    created_by = "test_func"
    length = 2
    language = "de"
    company_name = "Test & Co."
    initials = "tt"
    person_id = 1

    name = Name("test_fn", "test_ln")

    menu = NewPerson()
    menu.generate_table_persons(mock_conn)
    menu.add_person_to_db(mock_conn, created_by, name, length)

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
    with patch("builtins.input", return_value="N"):
        settings.add_settings(mock_conn, created_by, language, person_id, initials)  # noqa

    with patch("getpass.getpass", return_value="not correct"):
        with patch("buha.scripts.login.initials_in_table", return_value=True):
            with patch("buha.scripts.login.enter_initials", return_value="tt"):
                res = menu_login.login_employee(mock_conn, language, company_name)  # noqa

                if res == (True, "tt"):
                    assert False
