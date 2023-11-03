#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_entry.py
import sqlite3
from .constants import menu_new_entry_options
from .constants import new_entry_headline
from .constants import choose_option
from .helpers import clear_screen
from .helpers import create_headline
# from .helpers import is_internal
from .person import MenuNewPerson
# from .settings import add_settings


screen_cleared = False


class MenuNewEntry():
    """Menu options for adding a new entry."""

    def __init__(self):

        self.choices = {
            "1": self.new_person,
            "2": self.new_entity,
            "3": self.new_object,
            "4": self.new_project,
            "5": self.new_service,
            "6": self.new_account,
            "7": self.settings,
            "9": False
        }

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared
        headline = new_entry_headline[language]
        menu_new_entry_head = create_headline(company_name, headline)

        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_new_entry_head)

        print(menu_new_entry_options[language])

    def run(self, conn: sqlite3.Connection, created_by: str,
            company_name: str, language: str) -> None:

        # "created_by" are the initials of the person working with the program
        while True:
            self.display_menu(company_name, language)
            choice = choose_option(language)

            if not self.choices.get(choice):
                break
            elif choice in self.choices:
                action = self.choices.get(choice)
                if action:
                    action(conn, created_by, company_name, language)
            else:
                print(f"    {choice} is not a valid choice.")

    def new_person(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str, language: str) -> None:

        menu = MenuNewPerson()
        menu.run(conn, created_by, company_name, language)
#         name, person_id, initials = menu.enter_name(conn, created_by, company_name, language)  # noqa
#         if (name, person_id, initials) != (None, None, None):
#             internal = is_internal()
#             add_settings(conn, created_by, language, person_id, initials, is_internal=internal)  # noqa

    def new_entity(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str, language: str) -> None:
        print("ToDo")

    def new_object(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str, language: str) -> None:
        print("ToDo")

    def new_project(self, conn: sqlite3.Connection, created_by: str,
                    company_name: str, language: str) -> None:
        print("ToDo")

    def new_service(self, conn: sqlite3.Connection, created_by: str,
                    company_name: str, language: str) -> None:
        print("ToDo")

    def new_account(self, conn: sqlite3.Connection, created_by: str,
                    company_name: str, language: str) -> None:
        print("ToDo")

    def settings(self, conn: sqlite3.Connection, created_by: str,
                 company_name: str, language: str) -> None:
        print("ToDo")
