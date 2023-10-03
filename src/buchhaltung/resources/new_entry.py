#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_entry.py
# import os
# import sqlite3
from .person import MenuNewPerson


"""
New entry: customer, employee, supplier, entity, object (ware/product/tool/machine/material), bank details  # noqa
customer: first_name, last_name, company_name, customer_nr, currency, key
employee: first_name, last_name, job_title, division, account_nr, key
supplier: company_name, account_nr, currency, key
entity: company_name, street, street_nr, zip_code, city, country, key
object: name, type (ware, product, material, ...), supplier, supplier_alternatives, key
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

    def display_menu(self) -> None:
        menu_type_of_new_entry_en = (
            f"""
            +{'-' * 77}+
            | CHOSE WHICH KIND OF NEW ENTRY{' ' * 47}|
            +{'-' * 77}+

            1: New person
            2: New entity
            3: New object
            4: New project
            5: New service
            9: Back
            """)
        print(menu_type_of_new_entry_en)

    def run(self, initial) -> None:
        '''Display menu and respond to choices'''

        while True:
            self.display_menu()
            choice = input("Enter an option: ")

            if not self.choices.get(choice):
                break
            elif choice in self.choices:
                action = self.choices.get(choice)
                if action:
                    action(initial)
            else:
                print(f"{choice} is not a valid choice.")

    def new_person(self, initial) -> None:
        print(f"new person by {initial}")
        menu = MenuNewPerson()
        menu.run(initial)

    def new_entity(self, initial) -> None:
        print(f"change entity by {initial}")

    def new_object(self, initial) -> None:
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
