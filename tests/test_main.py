#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_main.py
"""Tests for "main" module."""

import pytest
import unittest.mock
import os
import sqlite3

from pathlib import Path
# from typing import Tuple

from context import check_databases
from context import activate_database
from context import clear_screen
from context import state_company
# from context import initialize
from context import setup_new_company
# from context import NewPerson


# ######## main.py ############################################################

# def test_initialize(tmp_path, mocker, monkeypatch):
#     mocker.patch("src.buha.scripts.helpers.path_to_database_dir", return_value=tmp_path)  # noqa
#     mocker.patch("os.walk", return_value=[
#         (str(tmp_path),
#          [],
#          [])
#     ])
#     company_name = "Init ltd."
#     monkeypatch.setattr("src.buha.scripts.helpers.path_to_database_dir", tmp_path)  # noqa
#     conn = activate_database(company_name)
#     assert type(initialize()) == Tuple[sqlite3.Connection, str, str]


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
    assert isinstance(tmp_path, Path)


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


def test_activate_database(tmp_path, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "test company")
    company_name = "test_activate_db.db"
    db_path = tmp_path / company_name
    monkeypatch.setattr("src.buha.scripts.helpers.path_to_db_dir", lambda: tmp_path)
    if os.path.exists(db_path):
        assert False
    conn = activate_database(company_name)
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


@pytest.fixture
def setup_database():
    company_name = "test company"
    conn = sqlite3.connect(":memory:")
    yield conn, company_name
    conn.close()


def test_setup_new_company(tmp_path, monkeypatch):

    monkeypatch.setattr("builtins.input", lambda _: "test company")
    monkeypatch.setattr("src.buha.scripts.helpers.path_to_db_dir", lambda: tmp_path)
    conn, language, company_name = setup_new_company("test_company.db", "de")

    assert isinstance(conn, sqlite3.Connection)
    assert language == "de"
    assert company_name == "test_company.db"
