#!/usr/bin/env python
# -*- coding: utf-8 -*-
# person.py
"""Menu to add the names and particulars of a person. Will be added to the
company's database of the same name as company."""
import datetime
import sqlite3
from dataclasses import dataclass
from .helpers import clear_screen
from .helpers import create_headline
from .helpers import mk_initials
from .helpers import show_persons
from .shared import Name
from .names import MenuName


screen_cleared = False


prompt = {
    "de": "PERSONENEINTRAG",
    "it": "INGRESSO DELLA PERSONA",
    "es": "ENTRADA DE PERSONA",
    "tr": "KIŞI GIRIŞI",
    "fr": "ENTRÉE DE PERSONNE",
    "en": "PERSON ENTRY",
}

languages = ["de", "en", "fr", "es", "it", "tr"]


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
    if language not in languages:
        print(f"Should be {languages}")
        language = pick_language()

    return language


@dataclass
class Person():
    created_by: str  # the initials of the person who created entry
    timestamp: str
    first_name: str
    middle_names: str
    last_name: str


class MenuNewPerson():
    """Menu to enter name and particulars of a person."""

    def __init__(self):
        self.choices = {
            "1": self.enter_name,
            "2": self.enter_titles,
            "3": self.enter_particulars,
            "4": show_persons,
            "9": False,
        }

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared

        menu_person_head = create_headline(company_name, language, prompt=prompt)  # noqa
        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_person_head)

        menu_person_entry = """
        1: Name
        2: Titles
        3: Additional personal data
        4: Show persons
        9: Back
        """

        print(menu_person_entry)

    def run(self, conn: sqlite3.Connection, created_by: str, company_name: str,
            language: str) -> str | None:
        """
        "company_name" is only needed for the display of the company's name.
        """
        while True:
            self.display_menu(company_name, language)
            choice = input("        Enter an option: ")
            if not self.choices.get(choice):
                name = None
                break
            else:
                action = self.choices.get(choice)
                if action and choice == "4":
                    action(conn)
                elif action:
                    name = action(conn, created_by, company_name, language)
                    # commit_to_db(name, names_key)
                else:
                    print(f"        {choice} is not a valid choice.")

        return name

    def enter_name(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str,
                   language: str) -> Name:
        # "company_name" is needed to display the company's name in MenuName

        menu = MenuName()
        name = menu.run(conn, created_by, company_name, language)  # format dataclass "Name"  # noqa
        if name is None:
            print("No entries for enter_name)")
        else:
            self.generate_table_persons(conn)
            person_id = self.add_person_to_db(conn, created_by, name, 2)
            menu.commit_name_to_db(conn, created_by, name, person_id)
        return name

    def enter_titles(self) -> None:
        pass

    def enter_particulars(self) -> None:
        pass

    def enter_relation(self) -> None:
        relation = input(f"{'intern/extern? ' : <8}")
        if relation not in ["intern", "extern"]:
            print("        Either intern or extern. Can be changed later.")
            relation = self.enter_relation()
        return relation

    def generate_table_persons(self, conn: sqlite3.Connection) -> None:
        """
        "created_by" refers to the initials of the person who created this
        entry.
        "middle_name" is a fallback entry in case there are more than one
        persons with the same name.
        "initials" is the unique identifier to find related tables.
        """
        with conn:
            cur = conn.cursor()
            table_persons = """CREATE TABLE IF NOT EXISTS persons (
                            person_id INTEGER PRIMARY KEY,
                            created_by TEXT,
                            timestamp TEXT,
                            first_name TEXT NOT NULL,
                            middle_names TEXT,
                            last_name TEXT NOT NULL,
                            initials TEXT NOT NULL
                            )"""
            cur.execute(table_persons)
            conn.commit()
        return

    def add_person_to_db(self, conn: sqlite3.Connection,
                         created_by: str, name: Name, length: int) -> str:
        """
        Adding the basic data about a person and who created it. "initials"
        serves as the unique identifier.
        """
        initials = mk_initials(conn, name, length)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        first_name = f"{name.first_name}"
        last_name = f"{name.last_name}"
        middle_names = f"{name.middle_names}"

        add_person = """INSERT INTO persons (
                        created_by, timestamp, first_name,
                        middle_names, last_name, initials)
                        VALUES (?, ?, ?, ?, ?, ?)"""
        with conn:
            cur = conn.cursor()
            cur.execute(add_person, (created_by, timestamp, first_name,
                                     middle_names, last_name, initials))
            conn.commit()
        return initials


if __name__ == "__main__":

    menu = MenuNewPerson()
    initial = "tb"
    menu.run(initial)
