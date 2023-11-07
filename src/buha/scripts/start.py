#!/usr/bin/env python
# -*- coding: utf-8 -*-
# start.py
import sqlite3
from .constants import menu_start_options
from .constants import start_headline
from .constants import choose_option
from .helpers import clear_screen
from .helpers import create_headline
from .login import LoginMenu
from .new_entry import MenuNewEntry
from .settings import MenuSettings


"""
customer: first_name, last_name, company_name, customer_nr, currency, key
employee: first_name, last_name, job_title, division, account_nr, key
supplier: company_name, account_nr, currency, key
entity: company_name, street, street_nr, zip_code, city, country, key
bank_details: name_of_bank, IBAN, BLZ, BIC, account_nr, key
"""


screen_cleared = False


class MenuStart():
    """Menu options for adding a new entry."""

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
        headline = start_headline[language]
        menu_start_head = create_headline(company_name, headline)  # noqa

        if not screen_cleared:
            clear_screen()
            print(menu_start_head)

        print(menu_start_options[language])

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

    def new_entry(self, conn: sqlite3.Connection, created_by: str,
                  company_name: str, language: str) -> None:
        menu = MenuNewEntry()
        menu.run(conn, created_by, company_name, language)

    def change_entry(self, conn, initials) -> None:
        pass

    def search_entry(self, conn, initials) -> None:
        pass

    def settings(self, conn: sqlite3.Connection, initials: str,
                 company_name: str, language: str) -> None:
        menu = MenuSettings()
        menu.run(conn, initials, company_name, language)

    def logout(self, conn: sqlite3.Connection, initials: str,
               company_name: str, language: str) -> None:
        login_menu = LoginMenu()
        authenticated, initials = login_menu.run(conn, language, company_name)
