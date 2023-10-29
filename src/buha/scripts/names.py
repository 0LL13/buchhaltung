#!/usr/bin/env python
# -*- coding: utf-8 -*-
# names.py
"""Dataclass Name and menu to enter names. Check if entry with given names
already exists. If not, create one entry in sqlite3 table "persons" and one
entry in "names", with names referencing to persons via foreign key."""
import datetime
import re
import sqlite3
from operator import itemgetter
from typing import Tuple
from .helpers import clear_screen
from .helpers import create_headline
from .shared import Name


screen_cleared = False


class MenuName():
    """Menu to enter the names of a contact."""

    def __init__(self):
        self.entries = {
            "fn": None,
            "mn": None,
            "ln": None,
            "nn": None,
            "maiden": None,
            "suffix": None,
            "salutation": None,
        }

        self.choices = {
            "1": self.enter_firstname,
            "2": self.enter_middlenames,
            "3": self.enter_lastname,
            "4": self.enter_nickname,
            "5": self.enter_maidenname,
            "6": self.enter_generational_suffix,
            "7": self.enter_salutation,
            "8": self.commit,
            "9": False,
        }

    def reset_entries(self):
        self.entries = {key: None for key in self.entries}

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared
        prompt = "BASIC NAME PARTICULARS"

        menu_names_head = create_headline(company_name, language, prompt=prompt)  # noqa
        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_names_head)

        menu_names_entry = """
        Fields with (*) are obligatory

        1: (*) First Name
        2: Middle Name(s)
        3: (*) Last Name
        4: Nickname
        5: Maiden Name
        6: Generational Suffix (Jr., Sr.)
        7: Salutation
        8: Commit and back
        9: Back
        """

        print(menu_names_entry)

    def run(self, conn: sqlite3.Connection, created_by: str, company_name: str,
            language: str) -> Tuple[str | None, str | None]:

        """Display Menu, gather entries in dict "entries", and finally put
        the data in new instance of Name."""

        while True:
            self.display_menu(company_name, language)
            choice = input("        Enter an option: ")
            if not self.choices.get(choice):
                break
            else:
                action = self.choices.get(choice)
                if action and choice == "8":
                    name = action(created_by, conn)
                    return name
                elif action:
                    action()
                else:
                    print(f"{choice} is not a valid choice.")

        return None, None

    def commit(self, conn: sqlite3.Connection, created_by: str) -> Tuple:

        name = self.generate_name_instance()
        return name

    def enter_firstname(self) -> None:
        firstname = input("First Name: ")
        if not firstname.isalpha():
            firstname = self.enter_firstname()
        self.entries["fn"] = firstname

    def enter_middlenames(self) -> None:
        middlename = input("Middle Name(s): ")
        middlename = re.sub(" +", " ", middlename)
        if " " in middlename:
            for mn in middlename.split(" "):
                if not mn.isalpha():
                    print("Input must contain alphabetic characters only.")
                    choice = input("Try again? y/N: ")
                    if choice == "y":
                        middlename = self.enter_middlename()
                    else:
                        middlename = None
        elif not middlename.isalpha():
            print("Input must contain alphabetic characters only.")
            middlename = self.enter_middlename()
        self.entries["mn"] = middlename

    def enter_lastname(self) -> None:
        lastname = input("Last Name: ")
        if not lastname.isalpha():
            lastname = self.enter_lastname()
        self.entries["ln"] = lastname

    def enter_nickname(self) -> None:
        nickname = input("Nickname: ")
        if not nickname.isalnum():
            choice = input("Try again? y/N: ")
            if choice == "y":
                nickname = self.enter_nickname()
            else:
                nickname = None
        self.entries["nn"] = nickname

    def enter_maidenname(self) -> None:
        maidenname = input("Maiden Name: ")
        maidenname = re.sub(" +", " ", maidenname)
        if " " in maidenname:
            for mn in maidenname.split(" "):
                if not mn.isalpha():
                    print("Input must contain alphabetic characters only.")
                    maidenname = self.enter_maidenname()
        elif not maidenname.isalpha():
            print("Input must contain alphabetic characters only.")
            maidenname = self.enter_maidenname()

        self.entries["maiden"] = maidenname

    def enter_generational_suffix(self) -> None:
        suffix = input("Generational Suffix: ")
        if suffix not in ["Jr.", "Sr.", "Jr", "Sr", "Jnr", "Snr", "I", "II", "III"]:  # noqa
            choice = input("Try again? y/N: ")
            if choice == "y":
                suffix = input("Generational Suffix: ")
            else:
                suffix = None
        self.entries["suffix"] = suffix

    def enter_salutation(self) -> None:
        salutation = input("Salutation: ")
        if salutation not in ["Herr", "Frau", "Fr.", "Hr."]:
            choice = input("Try again? y/N: ")
            if choice == "y":
                salutation = self.enter_salutation()
            else:
                salutation = None
        self.entries["salutation"] = salutation

    def generate_name_instance(self) -> Tuple:
        collected_entries = self.entries
        # see here about use of itemgetter:
        # https://stackoverflow.com/a/17755259/6597765
        first_name, last_name = itemgetter("fn", "ln")(collected_entries)
        name_list = [first_name, last_name]
        mn, nn, maiden, suffix, salutation = \
            itemgetter("mn", "nn", "maiden", "suffix", "salutation")(collected_entries)  # noqa
        default_names_list = [mn, nn, maiden, suffix, salutation]

        name = Name(*name_list, *default_names_list)
        if 0:
            print(name)
        return name

    def generate_table_names(self, conn: sqlite3.Connection) -> None:
        table_names = """CREATE TABLE IF NOT EXISTS names (
                         name_id INTEGER PRIMARY KEY,
                         person_id INTEGER,
                         created_by TEXT,
                         timestamp TEXT,
                         first_name TEXT NOT NULL,
                         middle_names TEXT,
                         last_name TEXT NOT NULL,
                         nickname TEXT,
                         maiden_name TEXT,
                         suffix TEXT,
                         salutation TEXT,
                         FOREIGN KEY (person_id)
                            REFERENCES persons(person_id)
                            ON DELETE CASCADE
                         )"""
        with conn:
            cur = conn.cursor()
            cur.execute(table_names)
            conn.commit()

    def commit_name_to_db(self, conn: sqlite3.Connection, created_by: str,
                          name: Name, person_id: int) -> None:
        self.generate_table_names(conn)
        if not self.name_already_in_db(conn, name):
            self.add_name_to_db(conn, created_by, name, person_id)
            self.reset_entries()
        else:
            message_name_exists = "Name already exists. Create entry anyway? y/N: "  # noqa
            choice = input(message_name_exists)
            if choice == "y":
                self.add_name_to_db(conn, created_by, name)
                self.reset_entries()

        return

    def add_name_to_db(self, conn: sqlite3.Connection, created_by: str,
                       name: Name, person_id: int) -> None:
        add_name = """INSERT INTO names (
                      person_id, created_by, timestamp, first_name,
                      middle_names, last_name, nickname, maiden_name, suffix,
                      salutation)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        with conn:
            cur = conn.cursor()
            cur.execute(add_name, (person_id, created_by, timestamp,
                                   name.first_name, name.middle_names,
                                   name.last_name, name.nickname,
                                   name.maiden_name, name.suffix,
                                   name.salutation))
            conn.commit()

    def name_already_in_db(self, conn: sqlite3.Connection, name: Name) -> bool:
        select_names = "SELECT first_name, middle_names, last_name FROM names"
        with conn:
            cur = conn.cursor()
            res = cur.execute(select_names)
            names = res.fetchall()

        for name_tuple in names:
            fn, mn, ln = name_tuple[0], name_tuple[1], name_tuple[2]
            if fn.lower() == name.first_name.lower():
                if ln.lower() == name.last_name.lower():
                    double = "Entry with these first and last names already exists. Please add a middle name!"  # noqa
                    if mn is None:
                        print(double)
                        self.enter_middlenames()
                        self.generate_name_instance()
                        return self.name_already_in_db(conn, name)
                    else:
                        return mn.lower() == name.middle_names.lower()
