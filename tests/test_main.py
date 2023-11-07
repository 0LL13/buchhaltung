#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_main.py
"""Tests for "main" module."""

import unittest.mock
import os

from pathlib import Path

from context import check_databases
from context import activate_database
from context import clear_screen
from context import state_company


# ######## main.py ############################################################

# @pytest.fixture
# def create_database_test_1(tmp_path):
#     db_name = Path("test_1.db")
#     db_path = Path(tmp_path) / db_name
#     conn = sqlite3.connect(db_path)
#     yield conn, db_path


def test_check_databases_return_type():
    assert type(check_databases()) == list


def test_check_databases(mocker, tmp_path):
    mocker.patch("src.buha.scripts.helpers.path_to_database_dir", return_value=tmp_path)  # noqa
    mocker.patch("os.walk", return_value=[
        (str(tmp_path),
         [],
         ["test.db"])
    ])
    expected = ["test.db"]
    actual = check_databases()
    assert actual == expected


def test_activate_database(tmp_path, monkeypatch):

    # monkeypatch.setattr("src.buha.scripts.helpers.path_to_database",
    # mock_path_to_database)
    company_name = "test_2.db"
    monkeypatch.setattr("src.buha.scripts.helpers.path_to_database_dir", tmp_path)  # noqa
    conn = activate_database(company_name)
    db_path = str(Path(tmp_path) / Path(company_name))
    print("activate: ", db_path)
    assert os.path.exists(db_path)
    conn.close()


def test_clear_screen(mocker):
    mocker.patch("os.system")
    clear_screen()
    os.system.assert_called_with("clear")
    clear_screen()
    os.system.assert_called_once()


def test_state_company():
    with unittest.mock.patch("builtins.input", return_value="Test Inc."):  # noqa
        language = "de"
        assert state_company(language) == 'Test_Inc..db'


def test_setup_new_db(tmp_path, mocker):
    pass
