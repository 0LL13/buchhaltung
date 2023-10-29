#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_entry.py
import sqlite3
from .helpers import action_prompt
from .helpers import clear_screen
from .helpers import create_headline
from .helpers import is_internal
from .person import MenuNewPerson
from .settings import add_settings


"""
customer: first_name, last_name, company_name, customer_nr, currency, key
employee: first_name, last_name, job_title, division, account_nr, key
supplier: company_name, account_nr, currency, key
entity: company_name, street, street_nr, zip_code, city, country, key
bank_details: name_of_bank, IBAN, BLZ, BIC, account_nr, key
"""


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
            "9": False
        }

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared
        menu_newentry_head = create_headline(company_name, language, prompt=action_prompt)  # noqa

        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_newentry_head)

        menu_new_entry = """
        1: New person
        2: New entity
        3: New object
        4: New project
        5: New service
        9: Back
        """

        print(menu_new_entry)

    def run(self, conn: sqlite3.Connection, created_by: str,
            company_name: str, language: str) -> None:

        # "created_by" are the initials of the person working with the program
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
                print(f"{choice} is not a valid choice.")

    def new_person(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str, language: str) -> None:

        menu = MenuNewPerson()
        name, person_id, initials = menu.enter_name(conn, created_by, company_name, language)  # noqa
        internal = is_internal()
        add_settings(conn, created_by, language, person_id, initials, is_internal=internal)  # noqa

    def new_entity(self, conn, initials) -> None:
        print(f"change entity by {initials}")

    def new_object(self, conn, initials) -> None:
        # object: name, type (ware, product, material, tool, ...), supplier,
        # supplier_alternatives, key, bank details
        print(f"search object by {initials}")

    def new_project(self, conn, initials) -> None:
        print(f"search project by {initials}")

    def new_service(self, conn, initial) -> None:
        print(f"search service by {initial}")


def main():
    menu = MenuNewEntry()
    menu.run()


if __name__ == "__main__":
    main()
