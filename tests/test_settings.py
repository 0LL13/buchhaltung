#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_settings.py
"""Tests for "settings" module."""

import datetime
import pytest
import sqlite3

from unittest.mock import patch

from context import add_settings
from context import generate_table_settings
from context import helpers
from context import Menu
from context import MenuSettings
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
    headline = "MENÜ EINSTELLUNGEN"  # 18
    headline_final = f"| {headline}{' ' * 58}|"
    expected = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+

    1: Sprache wählen
    2: Passwort ändern
    3: Einstellungen anzeigen
    9: Zurück
\n"""

    return expected


@pytest.fixture
def display_wo_change():
    expected = """
    1: Sprache wählen
    2: Passwort ändern
    3: Einstellungen anzeigen
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

def test_settings_menu_reset(reset_parent_class_menu):
    menu = reset_parent_class_menu()
    assert menu.last_caller_module is None
    assert menu.current_caller_module is None
    assert menu.navigation_stack == []


# ######## MenuSettings class #################################################

def test_settings_menu_class_init(reset_parent_class_menu):
    reset_parent_class_menu()
    menu_settings = MenuSettings()
    if menu_settings.last_caller_module == "settings":
        assert False
    assert menu_settings.current_caller_module == "src.buha.scripts.settings"
    assert menu_settings.navigation_stack == ["settings"]


def test_settings_menu_display_menu(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_settings = MenuSettings()
    company_name = "Test & Co.   "
    language = "de"
    task = "settings"
    expected = display_with_change

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu_settings.display_menu(company_name, language, task)
        actual, err = capsys.readouterr()
        assert actual == expected


# ######## MenuSettings run ###################################################

def test_settings_menu_run(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_settings = MenuSettings()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected = display_with_change

    with patch("builtins.input", return_value=None):
        menu_settings.run(mock_conn, created_by, company_name, language)
        actual, err = capsys.readouterr()
        assert actual == expected


@patch("builtins.input", return_value="9")
def test_settings_menu_run_get_choice_to_go_back(mocker):
    menu_settings = MenuSettings()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu_settings.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


@patch("builtins.input", return_value="not valid")
def test_settings_menu_run_get_choice_not_valid(mocker, capsys, display_wo_change):  # noqa
    menu_settings = MenuSettings()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected_display = display_wo_change

    menu_settings.run(mock_conn, created_by, company_name, language)
    actual_display, err = capsys.readouterr()

    assert actual_display == expected_display

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu_settings.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


# change language
def test_settings_menu_run_choice_is_1(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    menu_settings = MenuSettings()

    choose_option_side_effect = ["1", "9"]

    with patch("buha.scripts.settings.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(menu_settings, "change_language", return_value=None) as mock_change_language:  # noqa
            menu_settings.run(mock_conn, created_by, company_name, language)  # noqa
            mock_change_language.assert_called_once()


# change password
def test_settings_menu_run_choice_is_2(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    menu_settings = MenuSettings()

    choose_option_side_effect = ["2", "9"]

    with patch("buha.scripts.settings.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(menu_settings, "change_password", return_value=None) as mock_change_password:  # noqa
            with patch("builtins.input", return_value="asd"):
                with patch.object(settings, "update_password", return_value="asdf"):  # noqa
                    result = menu_settings.run(mock_conn, created_by, company_name, language)  # noqa
                    mock_change_password.assert_called_once()


# show settings
def test_settings_menu_run_choice_is_3(mock_conn, capsys):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    menu_settings = MenuSettings()

    choose_option_side_effect = ["3", "9"]

    with patch("buha.scripts.settings.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(menu_settings, "show_settings", return_value=None) as mock_show_settings:  # noqa
            with patch.object(settings, "get_person_id", return_value="1"):
                menu_settings.run(mock_conn, created_by, company_name, language)  # noqa
                mock_show_settings.assert_called_once()


# ######## generate table #####################################################

def test_settings_generate_table_settings(mock_conn):

    with mock_conn:
        settings.generate_table_settings(mock_conn)
        cur = mock_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
        assert cur.fetchone() is not None, "Table 'settings' was not created"

        cur.execute("PRAGMA table_info('settings')")
        columns = [row[1] for row in cur.fetchall()]
        expected_columns = ['settings_id', 'person_id', 'created_by',
                            'timestamp', 'language', 'initials', 'is_internal',
                            'salt', 'password_hash']  # noqa
        assert columns == expected_columns, "Table schema for 'settings' does not match expected schema"  # noqa


# ######## add settings to table ##############################################

def test_settings_add_settings(mock_conn):
    created_by = "test_func"
    language = "de"
    person_id = 1
    initials = "tt"

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa
    assert cur.fetchone() is not None, "Table 'settings' was not created"

    with patch.object(settings, "check_if_internal", return_value="y"):
        with patch.object(settings, "hash_password", return_value=("mocked_salt", "mocked_hash")):  # noqa
            settings.add_settings(mock_conn, created_by, language, person_id, initials)  # noqa
            cur.execute("SELECT * FROM 'settings'")
            rows = cur.fetchall()
            assert len(rows) > 0, "No data found in the table"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    columns = [str(row) if row is not None else None for row in rows[0]]
    expected_row = ['1', '1', 'test_func', timestamp, 'de', 'tt', 'y', 'mocked_salt', 'mocked_hash']  # noqa
    assert columns == expected_row


# ######## update language ####################################################

def test_settings_change_language(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co.   "
    language = "de"
    menu_settings = MenuSettings()
    choose_option_side_effect = ["1", "9"]

    with patch("buha.scripts.settings.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch.object(settings, "get_person_id", return_value=1) as mock_get_person_id:  # noqa
            with patch.object(settings, "pick_language", return_value=language) as mock_pick_language:  # noqa
                with patch.object(settings, "update_language", return_value=None) as mock_update_language:  # noqa
                    menu_settings.run(mock_conn, created_by, company_name, language)  # noqa
                    mock_get_person_id.assert_called_once()
                    mock_pick_language.assert_called_once()
                    mock_update_language.assert_called_once()


# ######## update language ####################################################

def test_settings_update_language(mock_conn):
    created_by = "test_func"
    language = "de"
    person_id = 1
    initials = "tt"

    settings.generate_table_settings(mock_conn)
    cur = mock_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")  # noqa

    with patch.object(settings, "check_if_internal", return_value="y"):
        with patch.object(settings, "hash_password", return_value=("mocked_salt", "mocked_hash")):  # noqa
            settings.add_settings(mock_conn, created_by, language, person_id, initials)  # noqa
            cur.execute("SELECT * FROM 'settings'")
            rows = cur.fetchall()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        columns = [str(row) if row is not None else None for row in rows[0]]
        expected_row = ['1', '1', 'test_func', timestamp, 'de', 'tt', 'y', 'mocked_salt', 'mocked_hash']  # noqa
        assert columns == expected_row

    new_language = "test_language"
    with patch.object(settings, "check_if_internal", return_value="y"):
        with patch.object(settings, "hash_password", return_value=("mocked_salt", "mocked_hash")):  # noqa
            settings.update_language(mock_conn, new_language, person_id)  # noqa
            cur.execute("SELECT * FROM 'settings'")
            rows = cur.fetchall()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        columns = [str(row) if row is not None else None for row in rows[0]]
        expected_row = ['1', '1', 'test_func', timestamp, 'test_language', 'tt', 'y', 'mocked_salt', 'mocked_hash']  # noqa
        assert columns == expected_row


# ######## change password ####################################################

def test_settings_change_password(mock_conn, capsys):
    language = "de"
    initials = "tt"
    counter = 1
    menu_settings = MenuSettings()

    choose_option_side_effect = ["2", "9"]
    password_entry_side_effect = ["not", "correct", "password"]

    with patch("buha.scripts.settings.choose_option", side_effect=choose_option_side_effect):  # noqa
        with patch("builtins.input", side_effect=password_entry_side_effect):
            with patch.object(settings, "password_correct", side_effect=[False, False, False]):  # noqa
                result = menu_settings.change_password(mock_conn, initials, language, counter)  # noqa
                captured = capsys.readouterr()

                assert result is None

                assert "Password not correct. Try again (2 of 3): " in captured.out  # noqa
                assert "Password not correct. Try again (3 of 3): " in captured.out  # noqa
                assert "Password not correct. Too many tries." in captured.out


# ######## show my table ######################################################

def test_settings_show_my_table(mock_conn):
    person_id = 1
    menu_settings = MenuSettings()

    with patch.object(settings, "show_my_table", return_value=None) as mock_show_my_table:  # noqa
        menu_settings.show_settings(mock_conn, person_id)
        mock_show_my_table.assert_called_once()
