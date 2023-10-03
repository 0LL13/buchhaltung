#!/usr/bin/env python
# -*- coding: utf-8 -*-
# login.py
import getpass
import hashlib
import os
import sqlite3
import sys
from typing import Tuple
from .new_employee import generate_table_employees


class LoginMenu():
    """Menu options for starting buha."""

    def display_menu(self) -> None:
        print("""
            1: Login
            2: Quit
            """)

    def run(self, conn) -> None:
        '''Display menu and respond to choices'''
        while True:
            self.display_menu()
            choice = input("Enter an option: ")
            if choice == "1":
                database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")  # noqa
                conn = sqlite3.connect(database_path)
                # table employees
                # key
                # employee (first name, last name)
                # initial
                # language
                # salt
                # password_hash
                # created_by (initial)
                # timestamp
                generate_table_employees(conn)
                authenticated, initial, language = login_employee(conn)
                conn.commit()
                conn.close()
                break
            else:
                authenticated = False
                initial = None
                language = None
                break

        return authenticated, initial, language


def login_employee(conn) -> Tuple[bool, str, str]:

    initial = input("Enter initials: ")

    if initial_in_table(conn, initial):
        password = getpass.getpass("Enter password: ")
        if password_correct(conn, initial, password):
            language = get_language(conn, initial)
            return True, initial, language
    else:
        print("Unknown initials.")

    # authenticated, initial, language
    return False, None, None


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
    for res_initial in initials:
        abbr = ''.join(str(c) for c in res_initial)
        if abbr == initial:
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


def main() -> None:
    database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")
    conn = sqlite3.connect(database_path)
    generate_table_employees(conn)

    menu = LoginMenu()
    authenticated, initial, language = menu.run(conn)
    if not authenticated:
        conn.close()
        sys.exit()
    print(authenticated, initial, language)
    conn.close()


if __name__ == "__main__":
    main()
