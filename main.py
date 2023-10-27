#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main.py
import getpass
import sqlite3
from typing import Tuple

from src.buha.scripts.helpers import check_databases  # looking for databases
from src.buha.scripts.helpers import state_company
from src.buha.scripts.helpers import path_to_database
from src.buha.scripts.helpers import create_headline
from src.buha.scripts.helpers import pick_language
from src.buha.scripts.helpers import continue_
from src.buha.scripts.helpers import show_table
from src.buha.scripts.helpers import check_for_matches
from src.buha.scripts.helpers import mk_initials
from src.buha.scripts.login import LoginMenu
from src.buha.scripts.new_entry import MenuNewEntry
from src.buha.scripts.person import MenuNewPerson as NewPerson
from src.buha.scripts.settings import add_settings
from src.buha.scripts.shared import clear_screen


"""
Entry point for buha. Get language first, then name of company. The name of the
company makes the name of the database. If no database of that name is there,
a new database will be created and a first employee can register. Once a
database is installed employees log in with initials and password after they
picked their language and company.
"""


screen_cleared = False


first_employee_pls_log_in = {
    "fr": "        Premier employé créé. Veuillez vous connecter.",
    "en": "        First employee created. Please log in.",
    "de": "        Erster Mitarbeiter angelegt. Bitte loggen Sie sich ein.",
    "es": "        Primer empleado creado. Por favor Iniciar sesión.",
    "it": "        Primo dipendente creato. Accedere prego.",
    "tr": "        İlk çalışan oluşturuldu. Lütfen giriş yapın.",
}


def initialize() -> Tuple[sqlite3.Connection, str, str]:
    """
    - check if database exists
    - if not exists:
        - start new db
        - create first employee
        - create settings (initials, password, language) for first employee
    - if exists:
        - login
        - language should be clear after login, but can be changed in settings
        - give option to not login and create new db instead
    """
    targets = check_databases()  # returns list with databases
    if targets == []:   # no database found
        conn, language, company_name = setup_new_db()
        return conn, language, company_name
    else:
        language = pick_language()
        company_name = state_company(language)
        match = check_for_matches(company_name, targets, language)
        conn = activate_database(match)
        return conn, language, match


def setup_new_db() -> Tuple[sqlite3.Connection, str, str]:
    language = pick_language()
    company_name = state_company(language)  # database will be named after company  # noqa
    created_by = getpass.getuser()
    conn = activate_database(company_name)
    new_person = NewPerson()
    name, person_id = new_person.enter_name(conn, created_by, company_name, language)  # noqa
    initials = mk_initials(conn, name, 2)
    add_settings(conn, created_by, language, person_id, initials)

    if 1:
        print("show_persons")
        show_table(conn, "persons")
        print("show_names")
        show_table(conn, "names")
        print("show_settings")
        show_table(conn, "settings")
        if continue_():
            pass
    return conn, language, company_name


def activate_database(company_name: str) -> sqlite3.Connection:
    path = path_to_database()
    db_path = path / company_name
    if 0:
        print("activate_database, path, company_name: ", path, company_name)
        print(db_path)
    conn = sqlite3.connect(db_path)
    return conn


class StartMenu():
    """
    The Start menu options: create/change/search new entry or settings or
    logout.
    """

    def __init__(self):
        self.choices = {
            "1": self.new_entry,
            "2": self.change_entry,
            "3": self.search_entry,
            "4": self.settings,
            "5": self.logout,
            "9": False
        }

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared
        prompt = "CHOSE ACTION"
        menu_main_head = create_headline(company_name, language, prompt=prompt)

        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_main_head)

        menu_first_action = """
        1: New Entry
        2: Change Entry
        3: Search Entry
        4: Settings
        5: Logout
        9: Quit
        """

        print(menu_first_action)

    def run(self, conn: sqlite3.Connection, created_by: str,
            company_name: str, language: str) -> None:
        '''
        Display start menu: create/change/show entries or settings or logout or
        quit.
        '''

        while True:
            self.display_menu(company_name, language)
            choice = input("        Enter an option: ")

            if not self.choices.get(choice):
                break
            elif choice in self.choices:
                action = self.choices.get(choice)
                if action:
                    action(conn, created_by, company_name, language)
            else:
                print(f"        {choice} is not a valid choice.")

        conn.close()

    def new_entry(self, conn: sqlite3.Connection, created_by: str,
                  company_name: str, language: str) -> None:
        print(f"new entry by {created_by}")
        menu = MenuNewEntry()
        menu.run(conn, created_by, company_name, language)

    def logout(self, conn: sqlite3.Connection, created_by: str,
               logged_out_company_name: str, language: str) -> None:
        conn.close()
        main()

    def change_entry(self, initial: str) -> None:
        print(f"change entry by {initial}")

    def search_entry(self, initial: str) -> None:
        print(f"search entry by {initial}")

    def settings(self, initial: str) -> None:
        print(f"change settings (password, language) by {initial}")


def main():
    conn, language, company_name = initialize()
    login_menu = LoginMenu()
    authenticated, created_by = login_menu.run(conn, language, company_name)  # noqa
    if authenticated:
        menu = StartMenu()
        menu.run(conn, created_by, company_name, language)


if __name__ == "__main__":
    main()
