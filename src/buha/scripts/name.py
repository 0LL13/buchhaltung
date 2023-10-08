#!/usr/bin/env python
# -*- coding: utf-8 -*-
# name.py
"""A set of dataclasses concerning persons and their particulars."""
import datetime
import re
import sqlite3
import sys
from operator import itemgetter
from dataclasses import dataclass, field
from typing import Optional, Tuple
from .mk_key import mk_key
from .helpers import AttrDisplay


@dataclass
class _Name_default:
    middle_names: Optional[str] = field(default=None)
    nickname: Optional[str] = field(default=None)
    maiden_name: Optional[str] = field(default=None)
    suffix: Optional[str] = field(default=None)
    salutation: Optional[str] = field(default=None)


@dataclass
class _Name_base:
    first_name: str
    last_name: str


@dataclass
class Name(_Name_default, _Name_base, AttrDisplay):
    """A person's names: first, middle/s, last name."""

    def __post_init__(self):
        """
        Initializing the names of a person.

        In case a Name instance is initialized with all first names in one
        string, __post_init__ will take care of this and assign each first
        name its attribute. Also it will raise TooManyFirstNames if more than
        three first names are given.
        """
        print("post_init dataclass Name")
        print(self.first_name)
        first_names = self.first_name.split(" ")
        self.first_name = first_names[0]
        if len(first_names) > 1:
            self.middle_names = " ".join(name for name in first_names[1:])


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

    def display_menu(self, company_name) -> None:
        company_name = company_name[:-3]
        company_name = re.sub("_", " ", company_name)
        length_name = 76 - len(company_name)
        prompt = "BASIC NAME PARTICULARS"
        length_prompt = 76 - len(prompt)
        company_line = f"| {company_name}" + ' ' * length_name + "|"
        action_prompt = "| " + prompt + ' ' * length_prompt + "|"
        menu_name_particulars = f"""
        +{'-' * 77}+
        {company_line}
        +{'-' * 77}+
        {action_prompt}
        +{'-' * 77}+

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

        print(menu_name_particulars)

    def run(self, initial: str,
            conn: sqlite3.Connection,
            company_name: str,
            use_prepared_values: bool = False,
            prepared_values: dict = None) -> Tuple[str | None, str | None]:

        """Display Menu, gather entries in dict "entries", and finally put
        the data in new instance of Name."""

        if not use_prepared_values:
            while True:
                self.display_menu(company_name)
                choice = input("        Enter an option: ")
                if not self.choices.get(choice):
                    break
                else:
                    action = self.choices.get(choice)
                    if action and choice == "8":
                        name, key = action(initial, conn)
                        return name, key
                    elif action:
                        action()
                    else:
                        print(f"{choice} is not a valid choice.")
        elif prepared_values is not None:
            self.entries.update(prepared_values)

        return None, None

    def commit(self, initial, conn) -> Tuple:
        name = self.generate_name_instance()
        key = self.commit_name_to_db(initial, name, conn)
        return name, key

    def enter_firstname(self):
        firstname = input("First Name: ")
        if not firstname.isalpha():
            firstname = self.enter_firstname()
        self.entries["fn"] = firstname

    def enter_middlenames(self):
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

    def enter_lastname(self):
        lastname = input("Last Name: ")
        if not lastname.isalpha():
            lastname = self.enter_lastname()
        self.entries["ln"] = lastname

    def enter_nickname(self):
        nickname = input("Nickname: ")
        if not nickname.isalnum():
            choice = input("Try again? y/N: ")
            if choice == "y":
                nickname = self.enter_nickname()
            else:
                nickname = None
        self.entries["nn"] = nickname

    def enter_maidenname(self):
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

    def enter_generational_suffix(self):
        suffix = input("Generational Suffix: ")
        if suffix not in ["Jr.", "Sr.", "Jr", "Sr", "Jnr", "Snr", "I", "II", "III"]:  # noqa
            choice = input("Try again? y/N: ")
            if choice == "y":
                suffix = input("Generational Suffix: ")
            else:
                suffix = None
        self.entries["suffix"] = suffix

    def enter_salutation(self):
        salutation = input("Salutation: ")
        if salutation not in ["Herr", "Frau", "Fr.", "Hr."]:
            choice = input("Try again? y/N: ")
            if choice == "y":
                salutation = self.enter_salutation()
            else:
                salutation = None
        self.entries["salutation"] = salutation

    def get_entries(self):
        return self.entries

    def generate_name_instance(self) -> None:
        collected_entries = self.entries
        # see here: https://stackoverflow.com/a/17755259/6597765
        first_name, last_name = itemgetter("fn", "ln")(collected_entries)
        name_list = [first_name, last_name]
        mn, nn, maiden, suffix, salutation = \
            itemgetter("mn", "nn", "maiden", "suffix", "salutation")(collected_entries)  # noqa
        default_names_list = [mn, nn, maiden, suffix, salutation]

        name = Name(*name_list, *default_names_list)
        print(name)
        return name

    def generate_table_names(self, conn) -> None:
        cur = conn.cursor()
        table_names = """CREATE TABLE IF NOT EXISTS names (
                         key TEXT,
                         initial TEXT,
                         timestamp TEXT,
                         first_name TEXT NOT NULL,
                         middle_names TEXT,
                         last_name TEXT NOT NULL,
                         nickname TEXT,
                         maiden_name TEXT,
                         suffix TEXT,
                         salutation TEXT
                         )"""
        cur.execute(table_names)
        conn.commit()
        return

    def commit_name_to_db(self, initial, name, conn) -> str:
        self.generate_table_names(conn)
        if not self.name_already_in_db(conn, name):
            key = self.add_name_to_db(conn, initial, name)
            conn.commit()
            return key
        else:
            message_name_exists_en = "Name already exists. Create entry anyway? y/N: "  # noqa
            choice = input(message_name_exists_en)
            if choice == "y":
                key = self.add_name_to_db(conn, initial, name)
                conn.commit()
                return key
        self.show_names(conn)
        return

    def add_name_to_db(self, conn, initial, name) -> str:
        add_name = """INSERT INTO names (
                      key, initial, timestamp, first_name, middle_names,
                      last_name, nickname, maiden_name, suffix, salutation)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        new_key = mk_key(conn)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        cur = conn.cursor()
        cur.execute(add_name, (new_key, initial, timestamp,
                               name.first_name, name.middle_names,
                               name.last_name, name.nickname, name.maiden_name,
                               name.suffix, name.salutation))
        conn.commit()
        return new_key

    def name_already_in_db(self, conn, name) -> bool:
        cur = conn.cursor()
        res = cur.execute("SELECT first_name, last_name FROM names")
        names = res.fetchall()
        print(names)
        for name_tuple in names:
            fn, ln = name_tuple[0], name_tuple[1]
            if fn.lower() == name.first_name.lower():
                if ln.lower() == name.last_name.lower():
                    return True
        return False

    def show_names(self, conn) -> None:
        cur = conn.cursor()
        data = cur.execute("""SELECT * from names""")
        res = data.fetchall()
        for res_name in res:
            print(res_name)


def main():
    menu = MenuName()
    initial = "tb"
    prepared_values = {"fn": "Bodo", "mn": "Knuth H.", "ln": "Weibel",
                       "nn": "Knuti", "salutation": "Herr", "suffix": "Sr.",
                       }
    menu.run(initial, use_prepared_values=True, prepared_values=prepared_values)  # noqa
    menu.generate_name_instance()


if __name__ == "__main__":
    if 0:
        main()
        sys.exit()
