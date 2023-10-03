#!/usr/bin/env python
# -*- coding: utf-8 -*-
# buha.py
import os
import platform
import sys
import sqlite3
from resources.login import LoginMenu
from resources.new_employee import new_employee, pick_language
from resources.new_entry import MenuNewEntry

"""
Entry menu when calling buha. If there is no employee registered, a first
employee will be registered. After that employees log in and choose what they
need to do.
"""


first_employee_pls_log_in = {
    "fr": "Premier employé créé. Veuillez vous connecter.",
    "en": "First employee created. Please log in.",
    "de": "Erster Mitarbeiter angelegt. Bitte loggen Sie sich ein.",
    "es": "Ingrese el nombre de la/del empleada/o (nombre, apellido): ",
    "it": "Inserisci il nome del dipendente (nome, cognome): ",
    "tr": "Çalışanın adını girin (ad, soyad): ",
}


class Menu():
    """Menu options for adding a new entity."""

    def __init__(self):
        if platform.system() == "Windows":
            database_path = os.path.join(os.path.dirname(__file__), "resources" + "\\" + "buchhaltung.db")  # noqa
        else:
            database_path = os.path.join(os.path.dirname(__file__), "resources" + "/" + "buchhaltung.db")  # noqa
        if not os.path.isfile(database_path):
            language = pick_language()
            new_employee(language)
            print(first_employee_pls_log_in[language])
            sys.exit()

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

    def run(self) -> None:
        '''Display menu and respond to choices'''
        database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")  # noqa
        conn = sqlite3.connect(database_path)
        login = LoginMenu()
        authenticated, initial, language = login.run(conn)
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

    def new_entry(self, initial) -> None:
        print(f"new entry by {initial}")
        menu = MenuNewEntry()
        menu.run(initial)

    def change_entry(self, initial) -> None:
        print(f"change entry by {initial}")

    def search_entry(self, initial) -> None:
        print(f"search entry by {initial}")

    def settings(self, initial) -> None:
        print(f"change settings (password, language) by {initial}")


def main():
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()
