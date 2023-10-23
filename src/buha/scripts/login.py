#!/usr/bin/env python
# -*- coding: utf-8 -*-
# login.py
import getpass
import hashlib
import os
import re
import sqlite3
import sys
from typing import Tuple
from .helpers import clear_screen
from .new_employee import generate_table_employees


class LoginMenu():
    """Menu options for starting buha."""

    def display_menu(self, company_name) -> None:
        clear_screen()
        company_name = company_name[:-3]
        company_name = re.sub("_", " ", company_name)
        length_name = 76 - len(company_name)
        prompt = "LOGIN MENU"
        length_prompt = 76 - len(prompt)
        company_line = f"| {company_name}" + ' ' * length_name + "|"
        action_prompt = "| " + prompt + ' ' * length_prompt + "|"
        login_menu = f"""
        +{'-' * 77}+
        {company_line}
        +{'-' * 77}+
        {action_prompt}
        +{'-' * 77}+

        1: Login
        2: Quit

        """

        print(login_menu)

    def run(self, conn: sqlite3.Connection,
            language: str,
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
            self.display_menu(company_name)
            choice = input("Enter an option: ")
            if choice == "1":
                generate_table_employees(conn)
                """
                table employees:
                # key
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

    initial = input("Enter initials: ")
    initial_validated = initial_in_table(conn, initial)
    if initial_validated:
        password = getpass.getpass("Enter password: ")
        password_validated = password_correct(conn, initial, password)
        if password_validated:
            return True, initial
    else:
        print("Unknown initials.")

    return False, None


def get_language(conn: sqlite3.Connection, initial: str) -> str | None:
    language = None
    try:
        with conn:
            cur = conn.cursor()
            get_language = "SELECT language FROM employees WHERE INITIAL = ?"
            cur.execute(get_language, (initial,))
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


def initial_in_table(conn: sqlite3.Connection,
                     initial: str) -> bool:
    try:
        with conn:
            cur = conn.cursor()
            res = cur.execute("SELECT initial FROM employees")
            initials = res.fetchall()
            # print("initials: ", initials)
            for res_initial in initials:
                abbr = ''.join(str(c) for c in res_initial)
                # print("res_initial: ", res_initial)
                # print("abbr: ", abbr)
                # print("initial: ", initial)
    finally:
        return abbr == initial


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
                     initial: str,
                     password: str) -> bool:
    correct = False

    try:
        with conn:
            cur = conn.cursor()

            # Retrieve salt from database
            get_salt = "SELECT salt FROM employees WHERE INITIAL = ?"
            cur.execute(get_salt, (initial,))
            salt_tuple = cur.fetchone()
            if salt_tuple:
                salt = salt_tuple[0]
            else:
                print("No salt_tuple")
                return

            # Retrieve hashed password from database
            get_pw = "SELECT password_hash FROM employees WHERE INITIAL = ?"  # noqa
            cur.execute(get_pw, (initial,))
            hashed_pw_tuple = cur.fetchone()

            if hashed_pw_tuple:
                password_hash = hashed_pw_tuple[0]
            else:
                print("No password_hash")
                return

            _, computed_password_hash = hash_password(password, salt)

            correct = computed_password_hash == password_hash
    finally:
        return correct
