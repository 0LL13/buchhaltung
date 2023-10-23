#!/usr/bin/env python
# -*- coding: utf-8 -*-
# settings.py
import hashlib
import os
import re
import sqlite3
from typing import Tuple
from .helpers import action_prompt
from .helpers import clear_screen
from .login import password_correct
from .person import pick_language


def generate_table_settings(conn: sqlite3.Connection) -> None:
    """
    Settings with language and password. Except for the language nothing points
    back at the owner of the settings.
    """
    table_settings = """CREATE TABLE IF NOT EXISTS settings (
                        key TEXT,
                        language TEXT,
                        salt BLOB NOT NULL,
                        password_hash BLOB NOT NULL
                        )"""
    with conn:
        cur = conn.cursor()
        cur.execute(table_settings)
        conn.commit()
        return


def update_language(conn: sqlite3.Connection, language: str, key: str) -> None:

    generate_table_settings(conn)
    update_language = f"""UPDATE settings
                          SET language = {language},
                          WHERE key = {key}"""

    with conn:
        cur = conn.cursor()
        cur.execute(update_language, (key, language))
        conn.commit()

    return


def update_password(conn: sqlite3.Connection, password: str, key: str) -> None:

    generate_table_settings(conn)
    salt, password_hash = hash_password(password)
    update_password = f"""UPDATE settings
                          SET salt = {salt},
                          password_hash = {password_hash}
                          WHERE key = {key}"""

    with conn:
        cur = conn.cursor()
        cur.execute(update_password, (key,
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
            "9": False
        }

    def display_menu(self, company_name: str, language: str) -> None:
        clear_screen()
        company_name = company_name[:-3]
        company_name = re.sub("_", " ", company_name)
        length_name = 76 - len(company_name)
        prompt = action_prompt[language]
        length_prompt = 76 - len(prompt)
        company_line = f"| {company_name}" + ' ' * length_name + "|"
        chose_action = "| " + prompt + ' ' * length_prompt + "|"

        menu_change_settings = f"""
        +{'-' * 77}+
        {company_line}
        +{'-' * 77}+
        {chose_action}
        +{'-' * 77}+

        1: Change language
        2: Change password
        9: Back
        """

        print(menu_change_settings)

    def run(self, conn: sqlite3.Connection,
            company_name: str,
            language_old: str,
            password_old: str,
            key: str) -> None:
        '''Display menu and respond to choices'''

        while True:
            self.display_menu(company_name, language_old)
            choice = input("        Enter an option: ")

            if not self.choices.get(choice):
                break
            elif choice == "1":
                language = self.change_language(conn)
                update_language(conn, language, key)

            elif choice == "2":
                password = self.change_password(conn, language, password_old, key)  # noqa
                update_password(conn, password, key)
            else:
                print(f"{choice} is not a valid choice.")

        return None

    def change_language(self, conn: sqlite3.Connection) -> str:

        language = pick_language()
        return language

    def change_password(self, conn: sqlite3.Connection, language: str,
                        password_old: str, initial: str,
                        counter: int = 1) -> str | None:

        password = input("Enter old password: ")
        if password_correct(conn, initial, password):
            new_password = input("Enter new password: ")
            return new_password
        else:
            counter = counter + 1
            if counter >= 3:
                print(f"Password not correct. Try again ({counter} of 3): ")
                return self.change_password(conn, language, password_old,
                                            initial, counter)
            else:
                print("Password not correct. Too many tries.")
                return None


if __name__ == "__main__":
    pass
