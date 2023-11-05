#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_main.py
"""Tests for "main" module."""

import os
import pytest
import sqlite3

from pathlib import Path

from context import path_to_database
from context import check_databases
from context import database_exists

from context import activate_database


abs_path_to_parent = "/home/sam/Programming/buha/src/buha/"
abs_path_to_data = "/home/sam/Programming/buha/src/buha/data"


def test_main_path_to_database():
    actual = str(path_to_database())
    expected = abs_path_to_data
    assert actual == expected


@pytest.fixture
def create_database_test_1():
    db_name = Path("test_1.db")
    path = Path(abs_path_to_data) / db_name
    conn = sqlite3.connect(path)
    yield conn
    conn.close()
    if os.path.isfile(path):
        os.remove(path)


def test_main_database_exists_True(create_database_test_1, mocker):
    conn = create_database_test_1
    with conn:
        mocker.patch("os.path.dirname", return_value=abs_path_to_parent)  # noqa
        company_name = "test_1.db"
        expected = os.path.join(abs_path_to_data + "/", company_name)
        print(expected)
        if os.path.exists(expected):
            print("exists")
        assert database_exists(company_name)


def test_main_database_exists_False(create_database_test_1, mocker):
    conn = create_database_test_1
    with conn:
        mocker.patch("os.path.dirname", return_value=abs_path_to_parent)  # noqa
        company_name = "does_not_exist.db"
        expected = os.path.join(abs_path_to_data + "/", company_name)
        print("expected: ", expected)
        if os.path.exists(expected):
            print("exists")
        if database_exists(company_name):
            assert False


def test_main_check_databases_return_type():
    assert type(check_databases()) == list


def test_main_check_databases(create_database_test_1, mocker):
    conn = create_database_test_1
    with conn:
        mocker.patch("os.path.dirname", return_value=abs_path_to_parent)  # noqa
        expected = ["test_1.db"]
        actual = check_databases()
        assert actual == expected


def test_main_activate_database(tmp_path, monkeypatch):

    def mock_path_to_database(db_name):
        return Path(tmp_path / db_name)

    # monkeypatch.setattr("src.buha.scripts.helpers.path_to_database", mock_path_to_database)
    company_name = "test_2.db"
    monkeypatch.setattr("main.path_to_database", mock_path_to_database)
    conn = activate_database(company_name)
    db_path = str(tmp_path / company_name)
    print(db_path)
    assert os.path.exists(db_path)
    conn.close
    os.remove(db_path)
