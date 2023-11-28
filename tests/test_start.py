#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_start.py
"""Tests for "helpers" module."""

import pytest
import sqlite3

from unittest.mock import patch

from context import helpers
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
def test_start_menu_run_get_choice_9(mocker, capsys, display_with_change):
    mocker.patch("os.system")
    menu = MenuStart()
    company_name = "Test & Co.   "
    language = "de"
    created_by = "tb"

    with patch("sys.exit") as mock_exit:
        menu.run(mock_conn, created_by, company_name, language)
        mock_exit.assert_called_once()
