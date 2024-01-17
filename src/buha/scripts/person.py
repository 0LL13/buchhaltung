#!/usr/bin/env python
# -*- coding: utf-8 -*-
# person.py
"""Menu to add the names and particulars of a person. Will be added to the
company's database of the same name as company."""
import datetime
import sqlite3
from dataclasses import dataclass
from .constants import choose_option
from .helpers import continue_
from .helpers import Menu
from .helpers import mk_initials
from .helpers import show_table
from .names import MenuName
from .settings import add_settings
from .shared import Name


@dataclass
class Person():
    created_by: str  # the initials of the person who created entry
    timestamp: str
    first_name: str
    middle_names: str
    last_name: str


class MenuNewPerson(Menu):
    """Menu to enter name and particulars of a person."""

    def __init__(self):
        super().__init__()
        super().change_menu("person")

        self.choices = {
            "1": self.enter_name,
            "2": self.enter_titles,
            "3": self.enter_particulars,
            "4": self.show_tables,
            "9": False,
        }

    def display_menu(self, company_name: str, language: str,
                     task: str = "person") -> None:
        super().display_menu(company_name, language, task=task)

    def run(self, conn: sqlite3.Connection, created_by: str, company_name: str,
            language: str) -> str | None:

        while True:
            self.display_menu(company_name, language, task="person")
            choice = choose_option(language)
            if choice == "1":
                name = self.enter_name(conn, created_by, company_name, language)  # noqa
            elif choice == "2":
                return self.enter_titles()
            elif choice == "3":
                self.enter_particulars()
            elif choice == "4":
                self.show_tables(conn, "persons")
            else:
                name = None
                break

        super().go_back()
        return name

    def enter_name(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str, language: str) -> None:

        # "company_name" is needed to display the company's name in MenuName
        menu = MenuName()
        name = menu.run(conn, created_by, company_name, language)  # format dataclass "Name"  # noqa
        if name is None:
            super().go_back()
            return None
        else:
            self.generate_table_persons(conn)
            initials = self.add_person_to_db(conn, created_by, name, 2)  # unique identifier  # noqa
            person_id = self.get_person_id(conn, initials)  # foreign key
            menu.commit_name_to_db(conn, created_by, name, person_id, language)  # needs foreign key  # noqa
            add_settings(conn, created_by, language, person_id, initials)
            super().change_menu("person")

    def enter_titles(self) -> None:  # pragma: no cover
        return None  # pragma: no cover

    def enter_particulars(self) -> None:
        print("enter_particulars - to do")  # pragma: no cover

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
                         created_by: str, name: Name, length: int) -> str | None:  # noqa
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

    def show_tables(self, conn: sqlite3.Connection, table: str) -> None:
        show_table(conn, table)
        continue_()
