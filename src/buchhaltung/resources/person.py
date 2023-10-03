#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A set of dataclasses concerning persons and their particulars."""
import datetime
import os
import sqlite3
from dataclasses import dataclass, field
from typing import Optional
from .mk_key import mk_key
from .name import MenuName
from .new_employee import pick_language


@dataclass
class Person():
    key: str
    initial: str
    timestamp: str
    first_name: str
    last_name: str
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

    def display_menu(self):
        menu_person_entry_en = (
            f"""
            +{'-' * 77}+
            | PERSON ENTRY{' ' * 64}|
            +{'-' * 77}+

            1: Name
            2: Titles
            3: Additional personal data
            4: Show persons
            9: Back
            """)
        print(menu_person_entry_en)

    def run(self, initial) -> None:
        while True:
            self.display_menu()
            choice = input("Enter an option: ")
            if not self.choices.get(choice):
                break
            else:
                action = self.choices.get(choice)
                if action and choice == "4":
                    action()
                elif action:
                    name, names_key = action(initial)
                else:
                    print(f"{choice} is not a valid choice.")

    def enter_name(self, initial) -> None:
        menu = MenuName()
        res = menu.run(initial)
        if not res:
            print("No values for menu.run(initial)")
        else:
            print("res from enter_name")
            print(res)
            name = res[0]
            names_key = res[1]
            print("name: ", name)
            print("names_key: ", names_key)
            first_name = f"{name.first_name}"
            last_name = f"{name.last_name}"
            language = pick_language()
            if names_key is not None:
                database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")  # noqa
                conn = sqlite3.connect(database_path)
                self.generate_table_persons(conn)
                self.add_person_to_db(conn, initial, first_name, last_name, language, names_key)  # noqa
                self.show_persons()
            return name, names_key

    def enter_titles(self) -> None:
        pass

    def enter_particulars(self) -> None:
        pass

    def enter_relation(self) -> None:
        relation = input("intern/extern? ")
        if relation not in ["intern", "extern"]:
            print("Either intern or extern. Can be changed later.")
            relation = self.enter_relation()
        return relation

    def show_persons(self) -> None:
        database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")  # noqa
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        show_persons = "SELECT * FROM persons"
        res = cur.execute(show_persons)
        res_persons = res.fetchall()
        for person in res_persons:
            print(person)
        conn.close()
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
        new_key = mk_key()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        relation = self.enter_relation()
        add_person = """INSERT INTO persons (
                        key, initial, timestamp, first_name, last_name,
                        language, names_key, relation, titles_key,
                        particulars_key)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cur = conn.cursor()
#        person_list = [new_key, initial, timestamp, first_name, last_name,
#                       language, names_key, titles_key, particulars_key]
        cur.execute(add_person, (new_key, initial, timestamp, first_name,
                                 last_name, language, names_key, relation,
                                 titles_key, particulars_key))
        conn.commit()
        conn.close()
        return


if __name__ == "__main__":

    menu = MenuNewPerson()
    initial = "tb"
    menu.run(initial)
