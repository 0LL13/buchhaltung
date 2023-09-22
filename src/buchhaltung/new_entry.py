#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_entry.py
import os
import sys
import sqlite3
from customer import Customer

PACKAGE_PARENT = ".."
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)  # isort:skip # noqa # pylint: disable=wrong-import-position
sys.path.append(
    os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT))
)  # isort: skip # noqa # pylint: disable=wrong-import-position

from resources.helpers import AttrDisplay  # type: ignore # noqa


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
        self.entry_dict = {
            "1": Customer,
            "employee": ["first_name", "last_name", "job_title", "division", "account_nr", "key"],  # noqa
            "supplier": ["company_name", "account_nr", "currency", "key"],
            "entity": ["company_name", "street", "street_nr", "zip_code", "city", "country", "key"],  # noqa
            "object": ["name", "type_", "supplier", "alternative_suppliers", "key"],  # noqa
            "bank_details": ["name_of_bank", "IBAN", "BLZ", "BIC", "account_nr", "key"],  # noqa
            "7": None
        }

        self.choices_type_of_entity = {
            "1": self.create_entity,
            "2": self.create_entity,
            "3": self.create_entity,
            "4": self.create_entity,
            "5": self.create_entity,
            "6": self.create_entity,
            "7": self.quit
        }

    def display_menu(self) -> None:
        print("""
            1: customer
            2: employee
            3: supplier
            4: entity
            5: object
            6: bank details
            7: quit
            """)

    def run(self) -> None:
        '''Display menu and respond to choices'''
        while True:
            self.display_menu()
            choice = input("Enter an option: ")
            type_of_entity = self.entry_dict[choice]

            if choice in ["1", 2, 3, 4, 5, 6]:
                self.create_entity(type_of_entity)
            elif choice == "7":
                self.quit()
            else:
                print(f"{choice} is not a valid choice.")

    def quit(self) -> None:
        sys.exit()

    def create_entity(self, type_of_entity) -> list:
        vals = []  # will be the values of company_name, first_name, ...
        attrs = vars(type_of_entity)
        args = attrs.get("__match_args__", None) # [company_name, first_name, ...]  # noqa
        print("args: ", args)
        print(f'more args: {args}')
        database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")  # noqa
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        new_table = f"""CREATE TABLE IF NOT EXISTS '{type_of_entity.__module__}'({", ".join(f'{arg} TEXT' for arg in args)})"""  # noqa
        cur.execute(new_table)
        for arg in args:
            val = input(f"{arg}: ")
            if not val:
                val = None
            vals.append(val)
        print("vals")
        print(vals)
        insert_val = f"""INSERT INTO {type_of_entity.__module__} ({args}) VALUES (? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ?)"""  # noqa
        for val in vals:
            cur.executemany(insert_val, (val,))
        conn.commit()
        conn.close()


def main():
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()
