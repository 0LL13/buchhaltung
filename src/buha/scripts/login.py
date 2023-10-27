#!/usr/bin/env python
# -*- coding: utf-8 -*-
# login.py
import getpass
import hashlib
import os
import sqlite3
import sys
from typing import Tuple
from .helpers import clear_screen
from .helpers import create_headline
from .new_employee import generate_table_employees


screen_cleared = False


class LoginMenu():
    """Menu options for starting buha."""

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared
        prompt = "LOGIN MENU"
        menu_login_head = create_headline(company_name, language, prompt=prompt)  # noqa

        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_login_head)

        login_menu = """
        1: Login
        2: Quit
        """

        print(login_menu)

    def run(self, conn: sqlite3.Connection, language: str,
            company_name: str) -> Tuple[bool, str]:
        """
        Display login menu: login or quit.
        Needs "company_name" for the head of menu, "language" for its language,
        and "conn".
        Activates table "employees" in order to check password and initial.
        Returns authenticated and initial.
        Logout closes connection and exits.
        """
        while True:
            self.display_menu(company_name, language)
            choice = input("Enter an option: ")
            if choice == "1":
                generate_table_employees(conn)
                """
                table employees:
                #
                # employee (first name, last name)
                # initial
                # language
                # company
                # salt
                # password_hash
                # created_by (initial)
                # timestamp
                """
                authenticated, initial = login_employee(conn, language,
                                                        company_name)
                conn.commit()
                print("authenticated and initials: ", initial)
                break
            else:
                authenticated = False
                initial = None
                conn.close()
                sys.exit()

        return authenticated, initial


def login_employee(conn: sqlite3.Connection,
                   language: str,
                   company_name: str) -> Tuple[bool, str]:
    """Returns authenticated, initial."""

    initials = input("Enter initials: ")
    initials_validated = initials_in_table(conn, initials)
    if initials_validated:
        password = getpass.getpass("Enter password: ")
        password_validated = password_correct(conn, initials, password)
        if password_validated:
            return True, initials
    else:
        print("Unknown initials.")

    return False, None


def get_language(conn: sqlite3.Connection, initials: str) -> str | None:
    language = None
    try:
        with conn:
            cur = conn.cursor()
            get_language = "SELECT language FROM employees WHERE initials = ?"
            cur.execute(get_language, (initials,))
            language_tuple = cur.fetchone()
            if language_tuple:
                language = language_tuple[0]
                # print("language: ", language)
            else:
                # print("Could not get language")
                # print(language_tuple)
                return
    finally:
        return language


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
        print("initials: ", initials)
        for res in res_initials:
            abbr = ''.join(str(c) for c in res)
            # print("res_initial: ", res_initial)
            print("abbr: ", abbr)
            print("initial: ", initials)
    return abbr == initials


# currently not necessary
def is_intern(conn: sqlite3.Connection,
              initial: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT relation FROM employees WHERE initial = ?", (initial,))
    res = cur.fetchone()
    if res:
        return res[0] == "intern"
    return False


def password_correct(conn: sqlite3.Connection,
                     initials: str,
                     password: str) -> bool:

    with conn:
        cur = conn.cursor()

        # Retrieve salt from database
        get_salt = "SELECT salt FROM settings WHERE initials = ?"
        cur.execute(get_salt, (initials,))
        salt_tuple = cur.fetchone()
        if salt_tuple:
            salt = salt_tuple[0]
        else:
            print("No salt_tuple")
            return False

        # Retrieve hashed password from database
        get_pw = "SELECT password_hash FROM settings WHERE initials = ?"
        cur.execute(get_pw, (initials,))
        hashed_pw_tuple = cur.fetchone()

        if hashed_pw_tuple:
            password_hash = hashed_pw_tuple[0]
        else:
            print("No password_hash")
            return False

        _, computed_password_hash = hash_password(password, salt)

        return computed_password_hash == password_hash
