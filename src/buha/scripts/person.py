#!/usr/bin/env python
# -*- coding: utf-8 -*-
# person.py
"""Menu to add the names and particulars of a person. Will be added to the
company's database of the same name as company."""
import datetime
import sqlite3
from dataclasses import dataclass
from typing import Tuple
from .constants import enter_person_prompt
from .constants import menu_person_entry
from .constants import languages
from .helpers import clear_screen
from .helpers import create_headline
from .helpers import mk_initials
from .helpers import show_table
from .shared import Name
from .names import MenuName


screen_cleared = False


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
            "4": show_table,
            "9": False,
        }

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared

        menu_person_head = create_headline(company_name, language, prompt=enter_person_prompt)  # noqa
        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_person_head)

        print(menu_person_entry[language])

    def run(self, conn: sqlite3.Connection, created_by: str, company_name: str,
            language: str) -> str | None:
        """
        "company_name" is only needed for the display of the company's name.
        """
        while True:
            self.display_menu(company_name, language)
            choice = input("    Option wählen: ")
            if not self.choices.get(choice):
                name = None
                break
            else:
                action = self.choices.get(choice)
                if action and choice == "4":
                    action(conn, "persons")
                elif action:
                    name = action(conn, created_by, company_name, language)
                    # commit_to_db(name, names_key)
                else:
                    print(f"    {choice} ist keine zulässige Eingabe.")

        return name

    def enter_name(self, conn: sqlite3.Connection,
                   created_by: str,
                   company_name: str,
                   language: str) -> Tuple[Name | None, int | None, str | None]:  # noqa

        # "company_name" is needed to display the company's name in MenuName
        menu = MenuName()
        name = menu.run(conn, created_by, company_name, language)  # format dataclass "Name"  # noqa
        if name == (None, None):
            # print("    No entries for enter_name")
            return None, None, None
        else:
            self.generate_table_persons(conn)
            initials = self.add_person_to_db(conn, created_by, name, 2)
            person_id = self.get_person_id(conn, initials)
            menu.commit_name_to_db(conn, created_by, name, person_id)
            return name, person_id, initials

    def enter_titles(self) -> None:
        pass

    def enter_particulars(self) -> None:
        pass

    def generate_table_persons(self, conn: sqlite3.Connection) -> None:
        table_persons = """CREATE TABLE IF NOT EXISTS persons (
                        person_id INTEGER PRIMARY KEY,
                        created_by TEXT,
                        timestamp TEXT,
                        first_name TEXT NOT NULL,
                        middle_names TEXT,
                        last_name TEXT NOT NULL,
                        initials TEXT NOT NULL
                        )"""
        with conn:
            cur = conn.cursor()
            cur.execute(table_persons)
            conn.commit()

    def add_person_to_db(self, conn: sqlite3.Connection,
                         created_by: str, name: Name, length: int) -> str:
        """
        Adding the basic data about a person and who created it. "initials"
        serves as the unique identifier.
        """
        initials = mk_initials(conn, name, length)
        if 0:
            print("initials in person.py add_person_to_db: ", initials)
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

    def get_person_id(self, conn: sqlite3.Connection, initials: str) -> int:
        query = """SELECT person_id FROM persons WHERE initials = ?"""
        with conn:
            cur = conn.cursor()
            cur.execute(query, (initials,))
            res = cur.fetchone()
            if 0:
                print("res in get_person_id: ", res)
                print("res[0]: ", res[0])
            return res[0]
