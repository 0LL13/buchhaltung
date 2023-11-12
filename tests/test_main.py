#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_main.py
"""Tests for "main" module."""

import pytest
import os
import sqlite3
import main
from unittest.mock import patch, MagicMock

from context import check_databases
from context import activate_database
from context import clear_screen
from context import state_company
from context import setup_new_company
# from context import helpers


# ######## initialize #########################################################

def test_global_screen_cleared():
    if main.screen_cleared is True:
        assert False


def test_clear_screen(mocker):
    mocker.patch("os.system")
    clear_screen()
    os.system.assert_called_with("clear")
    clear_screen()
    os.system.assert_called_once()


def test_state_company():
    with patch("builtins.input", return_value="Test Inc."):
        language = "de"
        assert state_company(language) == 'Test_Inc..db'


def test_check_databases_return_type():
    assert type(check_databases()) == list


def test_check_databases(tmp_path, mocker):
    mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
    mocker.patch("os.walk", return_value=[
        (str(tmp_path),
         [],
         ["check_db.db"])
    ])
    expected = ["check_db.db"]
    actual = check_databases()
    assert actual == expected


def test_check_databases_empty(tmp_path, mocker):
    mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
    mocker.patch("os.walk", return_value=[
        (str(tmp_path),
         [],
         [])
    ])
    expected = []
    actual = check_databases()
    assert actual == expected


def test_check_databases_other_than_db(tmp_path, mocker):
    mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
    mocker.patch("os.walk", return_value=[
        (str(tmp_path),
         [],
         ["check_db.db", "__init__.py"])
    ])
    expected = ["check_db.db"]
    actual = check_databases()
    assert actual == expected


def test_check_databases_more_than_one(tmp_path, mocker):
    mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
    mocker.patch("os.walk", return_value=[
        (str(tmp_path),
         [],
         ["check_db_1.db", "check_db_2.db"])
    ])
    expected = ["check_db_1.db", "check_db_2.db"]
    actual = check_databases()
    assert actual == expected


@pytest.fixture
def mock_conn():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


# fork to activate_database if there is a company database already
def test_connects_with_existing_db(tmp_path, mocker, monkeypatch, mock_conn):
    with patch.object(main, "activate_database", return_value=mock_conn) as mock_method:  # noqa
        monkeypatch.setattr("builtins.input", lambda _: "existing db")
        mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
        mocker.patch("os.walk", return_value=[
            (str(tmp_path), [], ["existing_db.db"])
        ])
        monkeypatch.setattr("os.system", lambda _: None)
        conn, language, company_name = main.initialize()
        assert company_name == "existing_db.db"
        mock_method.assert_called_once_with("existing_db.db")
        assert conn is mock_conn
        # assert return types match
        assert isinstance(conn, sqlite3.Connection)
        assert isinstance(language, str)
        assert isinstance(company_name, str)


# fork to setup_new_db if there is no database
def test_setup_new_db(tmp_path, mocker, monkeypatch, mock_conn):
    with patch.object(main, "setup_new_company", return_value=(mock_conn, "de", "new_company.db")) as mock_method:  # noqa
        monkeypatch.setattr("builtins.input", lambda _: "new company")
        mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
        mocker.patch("os.walk", return_value=[
            (str(tmp_path), [], [])
        ])
        monkeypatch.setattr("os.system", lambda _: None)
        conn, language, company_name = main.initialize()
        assert company_name == "new_company.db"
        mock_method.assert_called_once_with("new_company.db", "de")
        assert conn is mock_conn


# fork to check_for_matches if there is a database but the input has a typo
def test_connect_with_best_match(tmp_path, mocker, monkeypatch, mock_conn):
    with patch.object(main, "activate_database", return_value=mock_conn) as mock_method:  # noqa
        monkeypatch.setattr("builtins.input", lambda _: "existing compa")
        mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
        mocker.patch("os.walk", return_value=[
            (str(tmp_path), [], ["existing_company.db"])
        ])
        monkeypatch.setattr("os.system", lambda _: None)
        conn, language, match = main.initialize()
        assert match == "existing_company.db"
        mock_method.assert_called_once_with("existing_company.db")  # noqa
        assert conn is mock_conn


# fork to check_for_matches if there is a database but the input does not match
def test_check_for_matches(tmp_path, mocker, monkeypatch, mock_conn):
    with patch.object(main, "check_for_matches", return_value=None) as mock_method:  # noqa
        monkeypatch.setattr("builtins.input", lambda _: "different company")
        mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
        mocker.patch("os.walk", return_value=[
            (str(tmp_path), [], ["existing_db.db"])
        ])
        monkeypatch.setattr("os.system", lambda _: None)
        conn, language, match = main.initialize()
        mock_method.assert_called_once_with("different_company.db", ["existing_db.db"], "de")  # noqa


# fork to setup_new_company if there is a database but the input does not match
def test_existing_db_but_setup_new_db(tmp_path, mocker, monkeypatch, mock_conn):  # noqa
    with patch.object(main, "setup_new_company", return_value=(mock_conn, "de", "different_company.db")) as mock_method:  # noqa
        monkeypatch.setattr("builtins.input", lambda _: "different company")
        mocker.patch("src.buha.scripts.helpers.path_to_db_dir", return_value=tmp_path)  # noqa
        mocker.patch("os.walk", return_value=[
            (str(tmp_path), [], ["existing_db.db"])
        ])
        monkeypatch.setattr("os.system", lambda _: None)
        conn, language, match = main.initialize()
        # assert match is None
        mock_method.assert_called_once_with("different_company.db", "de")  # noqa


# ######## setup_new_company ##################################################

def test_setup_new_company(tmp_path, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "test company")
    monkeypatch.setattr("src.buha.scripts.helpers.path_to_db_dir", lambda: tmp_path)  # noqa
    conn, language, company_name = setup_new_company("test_company.db", "de")

    assert isinstance(conn, sqlite3.Connection)
    assert language == "de"
    assert company_name == "test_company.db"


# ######## activate_database ##################################################

def test_activate_database(tmp_path, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "test company")
    company_name = "test_activate_db.db"
    db_path = tmp_path / company_name
    monkeypatch.setattr("src.buha.scripts.helpers.path_to_db_dir", lambda: tmp_path)  # noqa
    if os.path.exists(db_path):
        assert False
    conn = activate_database(company_name)
    assert os.path.exists(db_path)
    conn.close()


# ######## main ###############################################################


def test_main_authenticated():
    with patch.object(main, "initialize", return_value=("mock_conn",
         "mock_language", "mock_company_name")) as mock_initialize, \
         patch("main.LoginMenu") as mock_login_menu, \
         patch("main.MenuStart") as mock_menu_start:

        # Mock the LoginMenu's run method to return authenticated user
        login_menu_instance = MagicMock()
        login_menu_instance.run.return_value = (True, "mock_initials")
        mock_login_menu.return_value = login_menu_instance

        menu_start_instance = MagicMock()
        mock_menu_start.return_value = menu_start_instance

        main.main()

        mock_initialize.assert_called_once()
        login_menu_instance.run.assert_called_once_with("mock_conn", "mock_language", "mock_company_name")  # noqa
        menu_start_instance.run.assert_called_once_with("mock_conn", "mock_initials", "mock_company_name", "mock_language")  # noqa


def test_main_unauthenticated(monkeypatch):
    counter = [0]

    def counted_main():
        counter[0] += 1
        if counter[0] <= 1:
            return main.main()

    with patch.object(main, "initialize", return_value=("mock_conn",
         "mock_language", "mock_company_name")) as mock_initialize, \
         patch('main.LoginMenu') as mock_login_menu, \
         patch("main.main", return_value=counted_main) as mock_main:

        # Mock the LoginMenu's run method to return unauthenticated user
        login_menu_instance = MagicMock()
        login_menu_instance.run.return_value = (False, None)
        mock_login_menu.return_value = login_menu_instance

        # Run the main function and expect it to call itself once more
        main.main()

        mock_initialize.assert_called_once()
        # assert counter[0] == 2
