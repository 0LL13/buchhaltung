#!/usr/bin/env python
# -*- coding: utf-8 -*-
# login.py
import getpass
import hashlib
import os
import sqlite3
import sys

from typing import Tuple

from .constants import enter_initials
from .constants import choose_option
from .constants import password_prompt
from .helpers import Menu


debug = False


class LoginMenu(Menu):
    """Menu options for starting buha."""
    def __init__(self):
        super().__init__()
        super().change_menu("login")

    def display_menu(self, company_name: str, language: str,
                     task: str = "login") -> None:
        super().display_menu(company_name, language, task=task)

    def run(self, conn: sqlite3.Connection, language: str,
            company_name: str) -> Tuple[bool, str]:

        while True:
            self.display_menu(company_name, language, task="login")
            choice = choose_option(language)
            if choice == "1":
                authenticated, initials = login_employee(conn, language, company_name)  # noqa
                break
            else:
                authenticated = False
                initials = None
                conn.close()
                sys.exit()

        super().go_back()
        return authenticated, initials


def login_employee(conn: sqlite3.Connection, language: str,
                   company_name: str) -> Tuple[bool, str]:
    """Returns authenticated, initials."""
    global debug
    debug = True

    initials = enter_initials(language)
    if initials_in_table(conn, initials):
        if is_internal(conn, initials):
            if debug:
                password = input(password_prompt[language])
            else:
                password = getpass.getpass(password_prompt[language])
            if password_correct(conn, initials, password):
                return True, initials
    return False, None


def is_internal(conn: sqlite3.Connection, initials: str) -> bool:
    with conn:
        cur = conn.cursor()
        query = "SELECT is_internal FROM settings WHERE initials = ?"
        res = cur.execute(query, (initials,))
        res_query = res.fetchone()
        if res_query:
            return res_query[0]
        return False


def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16)  # Generate a random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # noqa
    return salt, password_hash


def initials_in_table(conn: sqlite3.Connection, initials: str) -> bool:
    with conn:
        cur = conn.cursor()
        res = cur.execute("SELECT initials FROM persons")
        res_initials = res.fetchall()
        for res in res_initials:
            abbr = ''.join(str(c) for c in res)
            if 1:
                print("res_initials: ", res_initials)
                print("abbr: ", abbr)
                print("initials: ", initials)
            if abbr == initials:
                return True
    return False


def password_correct(conn: sqlite3.Connection, initials: str, password: str) -> bool:  # noqa

    with conn:
        cur = conn.cursor()

        # Retrieve salt from database
        get_salt = "SELECT salt FROM settings WHERE initials = ?"
        cur.execute(get_salt, (initials,))
        salt_tuple = cur.fetchone()
        if salt_tuple:
            salt = salt_tuple[0]
        else:
            return False

        # Retrieve hashed password from database
        get_pw = "SELECT password_hash FROM settings WHERE initials = ?"
        cur.execute(get_pw, (initials,))
        hashed_pw_tuple = cur.fetchone()

        if hashed_pw_tuple:
            password_hash = hashed_pw_tuple[0]
        else:
            return False

        _, computed_password_hash = hash_password(password, salt)

        return computed_password_hash == password_hash
