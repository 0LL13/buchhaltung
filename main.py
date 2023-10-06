#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main.py
import os
import platform
import re
import sqlite3
import sys
from fuzzywuzzy import fuzz
from typing import Tuple
from src.buha.scripts.login import LoginMenu
from src.buha.scripts.new_employee import new_employee
from src.buha.scripts.new_entry import MenuNewEntry

"""
Entry point for buha. Get language first, then name of company. The name of the
company makes the name of the database. If no database of that name is there,
a new database will be created and a first employee can register. Once a
database is installed employees log in with initials and password after they
picked their language and company.
"""


first_employee_pls_log_in = {
    "fr": "Premier employé créé. Veuillez vous connecter.",
    "en": "First employee created. Please log in.",
    "de": "Erster Mitarbeiter angelegt. Bitte loggen Sie sich ein.",
    "es": "Primer empleado creado. Por favor Iniciar sesión.",
    "it": "Primo dipendente creato. Accedere prego.",
    "tr": "İlk çalışan oluşturuldu. Lütfen giriş yapın.",
}


state_company_prompt = {
    "fr": "Indiquez votre entreprise: ",
    "en": "State your company: ",
    "de": "Name Ihres Unternehmens: ",
    "es": "Indique su empresa: ",
    "it": "Dichiara la tua azienda: ",
    "tr": "Şirketinizi belirtin: ",
}


def initialize() -> Tuple[sqlite3.Connection, str]:
    language = pick_language()
    company_name = state_company(language)
    print("initialize, company_name: ", company_name)

    if database_exists(company_name):
        conn = activate_database(company_name)
        return conn, language

    # check if it was a misspelling
    match = check_for_matches(company_name)
    if match is not None:
        print("initialize, match: ", match)
        conn = activate_database(match)

        return conn, language

    # check if a new database is wanted
    else:
        print("initialize, no match: ", company_name)
        choice = input("Do you want to start a new database? y/N ")
        if choice == "y":
            conn = activate_database(company_name)
            new_employee(language, company_name, conn)
            print(first_employee_pls_log_in[language])
            conn = activate_database(company_name)

            return conn, language
        else:
            sys.exit()


def pick_language() -> str:
    pick_language_prompt = """
        Welche Sprache? de
        Which language? en
        Quelle langue? fr
        Que lenguaje? es
        Quale lingua? it
        Hangi dil? tr

        --> """
    language = input(pick_language_prompt)
    if language not in ["de", "en", "fr", "es", "it", "tr"]:
        language = pick_language()

    return language


def state_company(language: str) -> str:
    company_name = input(state_company_prompt[language])
    company_name = re.sub(' +', '_', company_name) + ".db"
    company_name = company_name.strip()
    return company_name


# def check_database(company_name: str) -> str:
#     """To offer close matches in case of misspelling."""
#     path = path_to_database()
#     database_path = os.path.join(os.path.dirname(__file__), path + company_name)  # noqa
#     print("inside check_database")
#     print("database_path: ", database_path)
#     print("company_name: ", company_name)
#
#     match = check_for_matches(company_name)
#     print("match: ", match)
#     if match is not None:
#         return match, database_path
#
#     return company_name, database_path


def database_exists(company_name: str) -> bool:
    path = path_to_database()
    database_path = os.path.join(os.path.dirname(__file__), path + company_name)  # noqa
    if not os.path.isfile(database_path):
        print("inside database_exists: no file found")
        return False
    print("inside database_exists: file exists")
    return True


def path_to_database() -> str:
    path_to_database = {
        "windows": "src" + "\\" + "buha" + "\\" + "data" + "\\",
        "posix": "src" + "/" + "buha" + "/" + "data" + "/",
    }

    if platform.system() == "Windows":
        path = path_to_database["windows"]
    else:
        path = path_to_database["posix"]

    print("path_to_database: ", path)
    return path


def activate_database(company_name: str) -> sqlite3.Connection:
    path = path_to_database()
    print("activate_database, path, company_name: ", path, company_name)
    database_path = os.path.join(os.path.dirname(__file__), path + company_name)  # noqa
    conn = sqlite3.connect(database_path)
    return conn


# type hint best practice for v3.10 or above
# https://stackoverflow.com/a/69440627/6597765
def check_for_matches(company_name: str) -> str | None:
    targets = []

    threshold = 50
    print("inside check_for_matches")
    path = path_to_database()
    database_path = os.path.join(os.path.dirname(__file__), path)
    print("database_path: ", database_path)
    for (dirpath, dirnames, filenames) in os.walk(database_path):
        targets.extend(filenames)
    print("check_for_matches, targets: ", targets)

    scores = [fuzz.ratio(target, company_name) for target in targets]
    if scores:
        best_match_index = scores.index(max(scores))
        best_match = targets[best_match_index]

        if max(scores) > threshold:
            choice = input(f"Did you mean {best_match}? y/N: ")
            if choice == "y":
                print("best_match: ", best_match)
                return best_match

    repeat = input("Check again? y/N ")
    if repeat == "y":
        return check_for_matches(company_name)

    match = None
    return match


class Menu():
    """Menu options for adding a new entity."""

    def __init__(self):
        self.choices = {
            "1": self.new_entry,
            "2": self.change_entry,
            "3": self.search_entry,
            "4": self.settings,
            "9": False
        }

    def display_menu(self) -> None:
        menu_buha_en = (
            f"""
            +{'-' * 77}+
            | BUHA START MENU{' ' * 61}|
            +{'-' * 77}+
            1: New Entry
            2: Change Entry
            3: Search Entry
            4: Settings
            9: Quit
            """
        )
        print(menu_buha_en)

    def run(self, conn: sqlite3.Connection, language: str, initial: str) -> None:  # noqa
        '''Display menu and respond to choices'''

        while True:
            self.display_menu()
            choice = input("Enter an option: ")

            if not self.choices.get(choice):
                break
            elif choice in self.choices:
                action = self.choices.get(choice)
                if action:
                    action(initial, conn)
            else:
                print(f"{choice} is not a valid choice.")

        conn.close()

    def new_entry(self, initial, conn) -> None:
        print(f"new entry by {initial}")
        menu = MenuNewEntry()
        menu.run(initial, conn)

    def change_entry(self, initial) -> None:
        print(f"change entry by {initial}")

    def search_entry(self, initial) -> None:
        print(f"search entry by {initial}")

    def settings(self, initial) -> None:
        print(f"change settings (password, language) by {initial}")


def main():
    conn, language = initialize()
    login_menu = LoginMenu()
    authenticated, initial = login_menu.run(conn, language)
    if authenticated:
        menu = Menu()
        menu.run(conn, language, initial)


if __name__ == "__main__":
    main()
