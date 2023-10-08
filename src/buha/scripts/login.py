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
from .new_employee import generate_table_employees


class LoginMenu():
    """Menu options for starting buha."""

    def display_menu(self, company_name) -> None:
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
        '''Display menu and respond to choices'''
        while True:
            self.display_menu(company_name)
            choice = input("        Enter an option: ")
            if choice == "1":
                generate_table_employees(conn)
                # table employees:
                # key
                # employee (first name, last name)
                # initial
                # language
                # company
                # salt
                # password_hash
                # created_by (initial)
                # timestamp
                authenticated, initial = login_employee(conn, language, company_name)  # noqa
                conn.commit()
                print("authenticated and initials: ", initial)
                break
            else:
                authenticated = False
                initial = None
                # make sure the program exits
                sys.exit()

        return authenticated, initial


def login_employee(conn, language, company_name) -> Tuple[bool, str]:

    initial = input("        Enter initials: ")

    if initial_in_table(conn, initial):
        password = getpass.getpass("        Enter password: ")
        if password_correct(conn, initial, password):
            return True, initial
    else:
        print("        Unknown initials.")

    # authenticated, initial
    return False, None


def get_language(conn, initial) -> str:
    cur = conn.cursor()
    get_language = "SELECT language FROM employees WHERE INITIAL = ?"
    cur.execute(get_language, (initial,))
    language_tuple = cur.fetchone()
    if language_tuple:
        language = language_tuple[0]
        print("language: ", language)
        return language
    else:
        print("Could not get language")
        print(language_tuple)


def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16)  # Generate a random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # noqa
    return salt, password_hash


def initial_in_table(conn, initial) -> bool:
    cur = conn.cursor()
    res = cur.execute("SELECT initial FROM employees")
    initials = res.fetchall()
    print("initials: ", initials)
    for res_initial in initials:
        abbr = ''.join(str(c) for c in res_initial)
        print("res_initial: ", res_initial)
        print("abbr: ", abbr)
        print("initial: ", initial)
        if abbr == initial:
            print("initial in table")
            return True
    return False


def password_correct(conn, initial, password) -> bool:
    cur = conn.cursor()

    # Retrieve salt from database
    get_salt = "SELECT salt FROM employees WHERE INITIAL = ?"
    cur.execute(get_salt, (initial,))
    salt_tuple = cur.fetchone()
    if salt_tuple:
        salt = salt_tuple[0]
    else:
        print("No salt_tuple")
        return False

    # Retrieve hashed password from database
    get_pw = "SELECT password_hash FROM employees WHERE INITIAL = ?"  # noqa
    cur.execute(get_pw, (initial,))
    hashed_pw_tuple = cur.fetchone()

    if hashed_pw_tuple:
        password_hash = hashed_pw_tuple[0]
    else:
        return False

    _, computed_password_hash = hash_password(password, salt)

    return computed_password_hash == password_hash
