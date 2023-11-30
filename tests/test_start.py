#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_start.py
"""Tests for "helpers" module."""

import pytest
import sqlite3

from unittest.mock import Mock
from unittest.mock import patch

# from context import choose_option
from context import helpers
from context import NewEntry
from context import MenuStart
from context import start


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
    headline = "STARTMENÜ"
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


# ######## MenuStart class ####################################################

def test_start_menu_class_init():
    menu = MenuStart()
    assert menu.last_caller_module == "start"
    assert menu.current_caller_module == "src.buha.scripts.start"
    assert menu.navigation_stack == ["start"]


def test_start_menu_display_menu(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    task = "start"
    expected = display_with_change

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu.display_menu(company_name, language, task)
        actual, err = capsys.readouterr()
        assert actual == expected


def test_start_menu_run(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tb"
    expected = display_with_change

    with patch("builtins.input", return_value=None):
        menu.run(mock_conn, created_by, company_name, language)
        actual, err = capsys.readouterr()
        assert actual == expected


@patch("builtins.input", return_value="9")
def test_start_menu_run_get_choice_9(mocker):
    menu = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tb"

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


@patch("builtins.input", return_value="not valid")
def test_start_menu_run_get_choice_not_valid(mocker, capsys, display_wo_change):  # noqa
    menu = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tb"
    expected = display_wo_change

    menu.run(mock_conn, created_by, company_name, language)
    actual, err = capsys.readouterr()
    assert actual == expected


@patch("builtins.input", side_effect=["1"])
def test_start_menu_run_get_choice_1(mocker):
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tb"

    mock_menu_start = Mock(spec=MenuStart)
    mock_menu_start.new_entry = Mock()

    mock_menu_newentry = Mock(spec=NewEntry)
    mock_menu_newentry.run = Mock()

    def mock_run(*args):
        user_input = input()
        if user_input == "1":
            mock_menu_start.new_entry()
            mock_menu_newentry.run()

    mock_menu_start.run = mock_run

    mock_menu_start.run(mock_conn, created_by, company_name, language)

    mock_menu_start.new_entry.assert_called_once()
    mock_menu_newentry.run.assert_called_once()


def test_start_menu_input_in_choices():
    menu = MenuStart()
    for i in ["1", "2", "3", "4", "5", "9"]:
        assert i in menu.choices


def test_start_menu_input_not_in_choices():
    menu = MenuStart()
    for i in ["a", "100", "not valid"]:
        assert i not in menu.choices


def test_start_menu_input_get_choice():
    mock_menu_start = Mock(spec=MenuStart)

    mock_menu_start.new_entry = Mock(return_value=True)
    mock_menu_start.change_entry = Mock(return_value=True)
    mock_menu_start.search_entry = Mock(return_value=True)
    mock_menu_start.settings = Mock(return_value=True)
    mock_menu_start.logout = Mock(return_value=True)

    mock_menu_start.choices = {
            "1": mock_menu_start.new_entry,
            "2": mock_menu_start.change_entry,
            "3": mock_menu_start.search_entry,
            "4": mock_menu_start.settings,
            "5": mock_menu_start.logout,
            "9": False
        }

    with patch.object(start, "choose_option", side_effect=["1", "2", "3", "4", "5"]) as mock_choice:  # noqa
        assert mock_menu_start.choices.get(mock_choice())


def test_start_menu_input_get_choice_that_is_not_valid():
    mock_menu_start = Mock(spec=MenuStart)

    mock_menu_start.new_entry = Mock(return_value=True)
    mock_menu_start.change_entry = Mock(return_value=True)
    mock_menu_start.search_entry = Mock(return_value=True)
    mock_menu_start.settings = Mock(return_value=True)
    mock_menu_start.logout = Mock(return_value=True)

    mock_menu_start.choices = {
            "1": mock_menu_start.new_entry,
            "2": mock_menu_start.change_entry,
            "3": mock_menu_start.search_entry,
            "4": mock_menu_start.settings,
            "5": mock_menu_start.logout,
            "9": False
        }

    with patch.object(start, "choose_option", side_effect=["not valid"]) as mock_choice:  # noqa
        if mock_menu_start.choices.get(mock_choice()):
            assert False


def test_start_menu_input_get_choice_that_should_return_False():
    mock_menu_start = Mock(spec=MenuStart)

    mock_menu_start.choices = {
            "9": False
        }

    with patch.object(start, "choose_option", side_effect=["9"]) as mock_choice:  # noqa
        if mock_menu_start.choices.get(mock_choice()):
            assert False
