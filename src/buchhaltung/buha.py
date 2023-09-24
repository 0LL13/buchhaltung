#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_entry.py
import os
import sys
import sqlite3
from login import LoginMenu
from new_employee import new_employee


"""
New entry: customer, employee, supplier, entity, object (ware/product/tool/machine/material), bank details  # noqa
customer: first_name, last_name, company_name, customer_nr, currency, key
employee: first_name, last_name, job_title, division, account_nr, key
supplier: company_name, account_nr, currency, key
entity: company_name, street, street_nr, zip_code, city, country, key
object: name, type (ware, product, material, ...), supplier, supplier_alternatives, key
bank_details: name_of_bank, IBAN, BLZ, BIC, account_nr, key
"""


class Menu():
    """Menu options for adding a new entity."""

    def __init__(self):
        database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")  # noqa
        if not os.path.isfile(database_path):
            new_employee()
            print("First employee created. Please log in.")
            sys.exit()

        self.choices = {
            "1": self.new_entry,
            "2": self.change_entry,
            "3": self.search_entry,
            "4": False
        }

    def display_menu(self) -> None:
        print("""
            1: New Entry
            2: Change Entry
            3: Search Entry
            4: Quit
            """)

    def run(self) -> None:
        '''Display menu and respond to choices'''
        database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")  # noqa
        conn = sqlite3.connect(database_path)
        login = LoginMenu()
        authenticated, initial = login.run(conn)
        print(authenticated, initial)
        if not authenticated:
            conn.close()
            sys.exit()

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

    def quit(self) -> None:
        sys.exit()

    def new_entry(self, initial) -> None:
        print(f"new entry by {initial}")

    def change_entry(self, initial) -> None:
        print(f"change entry by {initial}")

    def search_entry(self, initial) -> None:
        print(f"search entry by {initial}")


def main():
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()
