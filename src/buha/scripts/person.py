#!/usr/bin/env python
# -*- coding: utf-8 -*-
# person.py
"""A set of dataclasses concerning persons and their particulars."""
import datetime
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from typing import Optional, Tuple
from .helpers import clear_screen
from .mk_key import mk_key
from .name import MenuName


def pick_language() -> str:
    pick_language_prompt = f"""
        +{'-' * 77}+
        | BUHA START MENU{' ' * 61}|
        +{'-' * 77}+

        Welche Sprache? de
        Which language? en
        Quelle langue? fr
        Que lenguaje? es
        Quale lingua? it
        Hangi dil? tr

        Exit? x

        --> """

    language = input(pick_language_prompt)
    if language == "x":
        sys.exit()
    elif language not in ["de", "en", "fr", "es", "it", "tr"]:
        language = pick_language()

    return language


@dataclass
class Person():
    key: str
    initial: str
    timestamp: str
    first_name: str
    last_name: str
    relation: str
    names_key: str
    title_key: Optional[str] = field(default=None)
    particulars_key: Optional[str] = field(default=None)


class MenuNewPerson():
    """Menu to enter name and particulars of a person."""

    def __init__(self):
        self.choices = {
            "1": self.enter_name,
            "2": self.enter_titles,
            "3": self.enter_particulars,
            "4": self.show_persons,
            "9": False,
        }

    def display_menu(self, company_name):
        clear_screen()
        company_name = company_name[:-3]
        company_name = re.sub("_", " ", company_name)
        length_name = 76 - len(company_name)
        prompt = "PERSON ENTRY"
        length_prompt = 76 - len(prompt)
        company_line = f"| {company_name}" + ' ' * length_name + "|"
        action_prompt = "| " + prompt + ' ' * length_prompt + "|"
        menu_person_entry = f"""
        +{'-' * 77}+
        {company_line}
        +{'-' * 77}+
        {action_prompt}
        +{'-' * 77}+

        1: Name
        2: Titles
        3: Additional personal data
        4: Show persons
        9: Back

        """
        print(menu_person_entry)

    def run(self, initial: str,
            conn: sqlite3.Connection,
            company_name: str) -> Tuple[str | None, str | None]:
        while True:
            self.display_menu(company_name)
            choice = input("        Enter an option: ")
            if not self.choices.get(choice):
                name, names_key = None, None
                break
            else:
                action = self.choices.get(choice)
                if action and choice == "4":
                    action(initial, conn)
                elif action:
                    name, names_key = action(initial, conn, company_name)
                else:
                    print(f"        {choice} is not a valid choice.")

        return name, names_key

    def enter_name(self, initial: str,
                   conn: sqlite3.Connection,
                   company_name: str) -> Tuple[str | None, str | None]:
        menu = MenuName()
        res = menu.run(initial, conn, company_name)
        if res == (None, None):
            print("No values for menu.run(initial)")
            name, names_key = None, None
        else:
            print("res from enter_name")
            print(res)
            name = res[0]
            names_key = res[1]
            print("name: ", name)
            print("names_key: ", names_key)
            first_name = f"{name.first_name}"
            last_name = f"{name.last_name}"
            print("        Chose language for newly created person.")
            language = pick_language()
            if names_key is not None:
                self.generate_table_persons(conn)
                self.add_person_to_db(conn, initial, first_name, last_name, language, names_key)  # noqa
                self.show_persons(initial, conn)

        return name, names_key

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

    def show_persons(self, initial, conn) -> None:
        cur = conn.cursor()
        res = cur.execute("SELECT * FROM persons")
        res_persons = res.fetchall()
        for person in res_persons:
            print(person)
        return

    def generate_table_persons(self, conn) -> None:
        cur = conn.cursor()
        table_persons = """CREATE TABLE IF NOT EXISTS persons (
                         key TEXT,
                         initial TEXT,
                         timestamp TEXT,
                         first_name TEXT,
                         last_name TEXT,
                         language TEXT,
                         names_key TEXT,
                         relation TEXT,
                         titles_key TEXT,
                         particulars_key TEXT
                         )"""
        cur.execute(table_persons)
        conn.commit()
        return

    def add_person_to_db(self, conn, initial, first_name, last_name, language,
                         names_key, titles_key=None,
                         particulars_key=None) -> None:  # noqa
        new_key = mk_key(conn)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        relation = self.enter_relation()
        add_person = """INSERT INTO persons (
                        key, initial, timestamp, first_name, last_name,
                        language, names_key, relation, titles_key,
                        particulars_key)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cur = conn.cursor()
        cur.execute(add_person, (new_key, initial, timestamp, first_name,
                                 last_name, language, names_key, relation,
                                 titles_key, particulars_key))
        conn.commit()
        return


if __name__ == "__main__":

    menu = MenuNewPerson()
    initial = "tb"
    menu.run(initial)
