#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_start.py
"""Tests for "start" module."""

import pytest
import sqlite3

from unittest.mock import patch

from context import helpers
from context import Menu
from context import MenuStart


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
    headline = "STARTMENÜ"  # 9
    headline_final = f"| {headline}{' ' * 67}|"
    expected = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+

    1: Neuer Eintrag
    2: Eintrag ändern
    3: Eintrag suchen
    4: Einstellungen
    5: Logout
    9: Beenden
    \n"""

    return expected


@pytest.fixture
def display_wo_change():
    expected = """
    1: Neuer Eintrag
    2: Eintrag ändern
    3: Eintrag suchen
    4: Einstellungen
    5: Logout
    9: Beenden
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

def test_start_menu_class_init(reset_parent_class_menu):
    reset_parent_class_menu()
    menu_start = MenuStart()
    if menu_start.last_caller_module == "start":
        assert False
    assert menu_start.current_caller_module == "src.buha.scripts.start"
    assert menu_start.navigation_stack == ["start"]


def test_start_menu_display_menu(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_start = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    task = "start"
    expected = display_with_change

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu_start.display_menu(company_name, language, task)
        actual, err = capsys.readouterr()
        assert actual == expected


def test_start_menu_run(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_start = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected = display_with_change

    with patch("builtins.input", return_value=None):
        menu_start.run(mock_conn, created_by, company_name, language)
        actual, err = capsys.readouterr()
        assert actual == expected


@patch("builtins.input", return_value="9")
def test_start_menu_run_get_choice_to_go_back(mocker):
    menu_start = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu_start.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


@patch("builtins.input", side_effect=["1", "9", "9"])
def test_start_menu_run_action_triggers_change_menu(mocker):
    menu_start = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"

    with patch.object(helpers.Menu, "change_menu") as mock_super:
        menu_start.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


@patch("builtins.input", return_value="not valid")
def test_start_menu_run_get_choice_not_valid(mocker, capsys, display_wo_change):  # noqa
    menu_start = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected_display = display_wo_change

    menu_start.run(mock_conn, created_by, company_name, language)
    actual_display, err = capsys.readouterr()

    assert actual_display == expected_display


def test_start_menu_run_choice_is_1(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co."
    language = "de"
    menu_start = MenuStart()

    with patch("builtins.input", side_effect=["1", "3", "9", "9"]) as mock_input:  # noqa
        menu_start.run(mock_conn, created_by, company_name, language)

        assert mock_input.call_count == 4


def test_start_menu_run_choice_is_4(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co."
    language = "de"
    menu_start = MenuStart()

    with patch("builtins.input", side_effect=["4", "1", "9", "9"]) as mock_input:  # noqa
        with patch("buha.scripts.start.MenuSettings.run", autoinspec=True) as mock_settings:  # noqa
            menu_start.run(mock_conn, created_by, company_name, language)

            assert mock_input.call_count == 4
            mock_settings.assert_called_once()


def test_start_menu_run_choice_is_5(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co."
    language = "de"
    menu_start = MenuStart()

    with patch("builtins.input", side_effect=["5", "1", "9", "9"]) as mock_input:  # noqa
        with patch("buha.scripts.start.LoginMenu.run", return_value=(False, None)) as mock_login:  # noqa
            menu_start.run(mock_conn, created_by, company_name, language)

            assert mock_input.call_count == 4
            mock_login.assert_called_once()
