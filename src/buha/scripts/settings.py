#!/usr/bin/env python
# -*- coding: utf-8 -*-
# settings.py
import datetime
import hashlib
import os
import sqlite3
from typing import Tuple
from .constants import settings_headline
from .helpers import clear_screen
from .helpers import create_headline
from .helpers import get_person_id
from .helpers import show_my_table
from .helpers import continue_
from .login import password_correct
from .person import pick_language


screen_cleared = False


def generate_table_settings(conn: sqlite3.Connection) -> None:
    """
    Settings with language and password. Except for the language nothing points
    back at the owner of the settings.
    """
    table_settings = """CREATE TABLE IF NOT EXISTS settings (
                        settings_id INTEGER PRIMARY KEY,
                        person_id INTEGER,
                        created_by TEXT,
                        timestamp TEXT,
                        language TEXT,
                        initials TEXT,
                        is_internal BOOL,
                        salt BLOB NOT NULL,
                        password_hash BLOB NOT NULL,
                        FOREIGN KEY (person_id)
                            REFERENCES persons(person_id)
                            ON DELETE CASCADE
                        )"""
    with conn:
        cur = conn.cursor()
        cur.execute(table_settings)
        conn.commit()
        return


def add_settings(conn: sqlite3.Connection, created_by: str, language: str,
                 person_id: int, initials: str, is_internal: bool = False) -> None:  # noqa
    add_settings = """INSERT INTO settings (
                      person_id, created_by, timestamp, language, initials,
                      is_internal, salt, password_hash)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    password = "asd"
    salt, password_hash = hash_password(password)
    if 0:
        print("person_id: ", person_id)
        if continue_():
            pass

    with conn:
        generate_table_settings(conn)
        cur = conn.cursor()
        cur.execute(add_settings, (person_id, created_by, timestamp, language,
                                   initials, is_internal, salt, password_hash))
        conn.commit()


def update_language(conn: sqlite3.Connection, language: str,
                    person_id: int) -> None:

    generate_table_settings(conn)
    update_language = """UPDATE settings
                         SET language = ?
                         WHERE person_id = ?"""

    with conn:
        cur = conn.cursor()
        cur.execute(update_language, (language, person_id))
        conn.commit()
        return


def update_password(conn: sqlite3.Connection, password: str, initials: str) -> None:  # noqa

    person_id = get_person_id(conn, initials)
    generate_table_settings(conn)
    salt, password_hash = hash_password(password)
    update_password = """UPDATE settings
                          SET salt = ?,
                          password_hash = ?
                          WHERE person_id = ?"""

    with conn:
        cur = conn.cursor()
        cur.execute(update_password, (person_id,
                                      sqlite3.Binary(salt),
                                      sqlite3.Binary(password_hash)
                                      ))
        conn.commit()
        return


def hash_password(password: str) -> Tuple[str, str]:
    salt = os.urandom(16)  # Generate a random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # noqa
    return salt, password_hash


class MenuSettings():
    """Menu options for adding a new entry."""

    def __init__(self):

        self.choices = {
            "1": self.change_language,
            "2": self.change_password,
            "3": show_my_table,
            "9": False
        }

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared
        headline = settings_headline[language]

        menu_settings_head = create_headline(company_name, headline)  # noqa
        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_settings_head)

        menu_change_settings = """
    1: Change language
    2: Change password
    3: Show my settings
    9: Back
    """

        print(menu_change_settings)

    def run(self, conn: sqlite3.Connection, initials: str,
            company_name: str, language: str) -> None:

        while True:
            self.display_menu(company_name, language)
            choice = input("    Enter an option: ")

            if not self.choices.get(choice):
                break
            elif choice == "1":
                self.change_language(conn, initials)

            elif choice == "2":
                password = self.change_password(conn, initials, language)
                update_password(conn, password, initials)
            elif choice == "3":
                person_id = get_person_id(conn, initials)
                show_my_table(conn, "settings", person_id)
            else:
                print(f"    {choice} is not a valid choice.")

        return None

    def change_language(self, conn: sqlite3.Connection, initials: str) -> None:
        person_id = get_person_id(conn, initials)
        language = pick_language()
        update_language(conn, language, person_id)

    def change_password(self, conn: sqlite3.Connection, initials: str,
                        language: str, counter: int = 1) -> str | None:

        password = input("    Enter old password: ")
        if password_correct(conn, initials, password):
            new_password = input("    Enter new password: ")
            return new_password
        else:
            counter = counter + 1
            if counter <= 3:
                print(f"    Password not correct. Try again ({counter} of 3): ")  # noqa
                return self.change_password(conn, initials, language, counter)
            else:
                print("    Password not correct. Too many tries.")
                return None
