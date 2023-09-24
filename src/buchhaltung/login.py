#!/usr/bin/env python
# -*- coding: utf-8 -*-
# login.py
import getpass
import hashlib
import os
import sqlite3
import sys
from typing import Tuple, Optional


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
                authenticated, initial = login_employee(conn)
                break
            else:
                authenticated = False
                initial = None
                break

        return authenticated, initial


def generate_table(conn, name_of_table) -> None:
    cur = conn.cursor()
    new_table = f"""CREATE TABLE IF NOT EXISTS '{name_of_table}'(
                    employee_id INTEGER PRIMARY KEY,
                    key TEXT,
                    employee TEXT NOT NULL,
                    initial TEXT,
                    salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL
                    )"""
    cur.execute(new_table)
    conn.commit()
    return


def login_employee(conn) -> Tuple[bool, Optional[str]]:

    initial = input("Enter initials: ")

    if initial_in_table(conn, initial):
        password = getpass.getpass("Enter password: ")
        if password_correct(conn, initial, password):
            return True, initial
    else:
        print("Unknown initials.")

    return False, None


def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16)  # Generate a random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # noqa
    return salt, password_hash


def initial_in_table(conn, initial) -> bool:
    cur = conn.cursor()
    res = cur.execute("SELECT initial_new_employee FROM employees")
    initials = res.fetchall()
    for res_initial in initials:
        abbr = ''.join(str(c) for c in res_initial)
        if abbr == initial:
            return True
    return False


def password_correct(conn, initial, password) -> bool:
    cur = conn.cursor()

    # Retrieve salt from database
    get_salt = "SELECT salt FROM employees WHERE INITIAL_NEW_EMPLOYEE = ?"
    cur.execute(get_salt, (initial,))
    salt_tuple = cur.fetchone()
    if salt_tuple:
        salt = salt_tuple[0]
    else:
        return False

    # Retrieve hashed password from database
    get_pw = "SELECT password_hash FROM employees WHERE INITIAL_NEW_EMPLOYEE = ?"  # noqa
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
    generate_table(conn, "employees")

    menu = LoginMenu()
    authenticated, initial = menu.run(conn)
    if not authenticated:
        conn.close()
        sys.exit()
    print(authenticated, initial)
    conn.close()


if __name__ == "__main__":
    main()
