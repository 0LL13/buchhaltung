#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_entry.py
import re
import sqlite3
from .helpers import action_prompt
from .helpers import clear_screen
from .person import MenuNewPerson


"""
customer: first_name, last_name, company_name, customer_nr, currency, key
employee: first_name, last_name, job_title, division, account_nr, key
supplier: company_name, account_nr, currency, key
entity: company_name, street, street_nr, zip_code, city, country, key
bank_details: name_of_bank, IBAN, BLZ, BIC, account_nr, key
"""


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
        clear_screen()
        company_name = company_name[:-3]
        company_name = re.sub("_", " ", company_name)
        length_name = 76 - len(company_name)
        prompt = action_prompt[language]
        length_prompt = 76 - len(prompt)
        company_line = f"| {company_name}" + ' ' * length_name + "|"
        chose_action = "| " + prompt + ' ' * length_prompt + "|"

        menu_type_of_new_entry = f"""
        +{'-' * 77}+
        {company_line}
        +{'-' * 77}+
        {chose_action}
        +{'-' * 77}+

        1: New person
        2: New entity
        3: New object
        4: New project
        5: New service
        9: Back
        """

        print(menu_type_of_new_entry)

    def run(self, initial: str,
            conn: sqlite3.Connection,
            company_name: str,
            language: str) -> None:
        '''Display menu and respond to choices'''

        while True:
            self.display_menu(company_name, language)
            choice = input("        Enter an option: ")

            if not self.choices.get(choice):
                break
            elif choice in self.choices:
                action = self.choices.get(choice)
                print("action iin new_entry: ", action)
                if action:
                    action(initial, conn, company_name, language)
            else:
                print(f"{choice} is not a valid choice.")

    def new_person(self, initial: str,
                   conn: sqlite3.Connection,
                   company_name: str,
                   language: str) -> None:

        menu = MenuNewPerson()
        menu.run(initial, conn, company_name, language)

    def new_entity(self, initial) -> None:
        print(f"change entity by {initial}")

    def new_object(self, initial) -> None:
        # object: name, type (ware, product, material, tool, ...), supplier,
        # supplier_alternatives, key, bank details
        print(f"search object by {initial}")

    def new_project(self, initial) -> None:
        print(f"search project by {initial}")

    def new_service(self, initial) -> None:
        print(f"search service by {initial}")


def main():
    menu = MenuNewEntry()
    menu.run()


if __name__ == "__main__":
    main()
