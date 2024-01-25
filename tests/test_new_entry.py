#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_new_entry.py
"""Tests for "new_entry" module."""

import pytest
import sqlite3

from unittest.mock import patch

from context import helpers
from context import Menu
from context import NewEntry


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
    headline = "NEUER EINTRAG"  # 13
    headline_final = f"| {headline}{' ' * 63}|"
    expected = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+

    1: Person
    2: Unternehmen (Firma, Bank, ...)
    3: Objekt (Werkzeuge, Waren, ...)
    4: Projekt (Zimmer streichen, Fahrradreperatur, ...)
    5: Dienstleistung (Inspektion, Beratung, ...)
    6: Konto (Jobtitel, Abteilung, SKR-Nummer, ...)
    7: Einstellungen (Sprache, Passwort, Zugangsberechtigungen)
    9: Zurück
    \n"""

    return expected


@pytest.fixture
def display_wo_change():
    expected = """
    1: Person
    2: Unternehmen (Firma, Bank, ...)
    3: Objekt (Werkzeuge, Waren, ...)
    4: Projekt (Zimmer streichen, Fahrradreperatur, ...)
    5: Dienstleistung (Inspektion, Beratung, ...)
    6: Konto (Jobtitel, Abteilung, SKR-Nummer, ...)
    7: Einstellungen (Sprache, Passwort, Zugangsberechtigungen)
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

def test_new_entry_menu_reset(reset_parent_class_menu):
    menu = reset_parent_class_menu()
    assert menu.last_caller_module is None
    assert menu.current_caller_module is None
    assert menu.navigation_stack == []


# ######## MenuName class #####################################################

def test_new_entry_menu_class_init(reset_parent_class_menu):
    reset_parent_class_menu()
    menu_newentry = NewEntry()
    if menu_newentry.last_caller_module == "new entry":
        assert False
    assert menu_newentry.current_caller_module == "src.buha.scripts.new_entry"
    assert menu_newentry.navigation_stack == ["new entry"]


def test_new_entry_menu_display_menu(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_newentry = NewEntry()
    company_name = "Test & Co.   "
    language = "de"
    task = "new entry"
    expected = display_with_change

    with patch.object(helpers.Menu, "menu_changed", return_value=True):
        menu_newentry.display_menu(company_name, language, task)
        actual, err = capsys.readouterr()
        assert actual == expected


# ######## NewEntry run #######################################################

def test_new_entry_menu_run(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu_newentry = NewEntry()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected = display_with_change

    with patch("builtins.input", return_value=None):
        menu_newentry.run(mock_conn, created_by, company_name, language)
        actual, err = capsys.readouterr()
        assert actual == expected


@patch("builtins.input", return_value="9")
def test_new_entry_menu_run_get_choice_to_go_back(mocker):
    menu_newentry = NewEntry()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu_newentry.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


@patch("builtins.input", return_value="not valid")
def test_new_entry_menu_run_get_choice_not_valid(mocker, capsys, display_wo_change):  # noqa
    menu_newentry = NewEntry()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tester"
    expected_display = display_wo_change

    menu_newentry.run(mock_conn, created_by, company_name, language)
    actual_display, err = capsys.readouterr()

    assert actual_display == expected_display

    with patch.object(helpers.Menu, "go_back") as mock_super:
        menu_newentry.run(mock_conn, created_by, company_name, language)
        mock_super.assert_called_once()


def test_new_entry_menu_run_choice_is_1(mock_conn):
    created_by = "test_func"
    company_name = "Test & Co."
    language = "de"
    menu_newentry = NewEntry()

    with patch("builtins.input", side_effect=["1", "1", "3", "9", "9"]) as mock_input:  # noqa
        menu_newentry.run(mock_conn, created_by, company_name, language)

        assert mock_input.call_count == 5
