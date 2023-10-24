#!/usr/bin/env python
# -*- coding: utf-8 -*-
# helpers.py
"""Helper functions: exceptions, print style, ..."""
import os
import re
import sqlite3
import sys
from fuzzywuzzy import fuzz
from prettytable import PrettyTable
from pathlib import Path
from .attr_dicts import german_attrs
from .shared import Name
from .shared import clear_screen


action_prompt = {
    "de": "WÄHLEN SIE EINE AKTION",
    "it": "SCEGLI UN'AZIONE",
    "es": "ELIGE ACCIÓN",
    "tr": "EYLEM SEÇIN",
    "en": "CHOOSE ACTION",
    "fr": "CHOISIR UNE ACTION",
}


state_company_prompt = {
    "fr": "        Indiquez votre entreprise: ",
    "en": "        State your company: ",
    "de": "        Name Ihres Unternehmens: ",
    "es": "        Indique su empresa: ",
    "it": "        Dichiara la tua azienda: ",
    "tr": "        Şirketinizi belirtin: ",
}


def mk_initials(conn: sqlite3.Connection, name: Name, length: int) -> str:
    fn = name.first_name
    ln = name.last_name

    if length == 2:
        initials = ''.join(fn[0].lower() + ln[0].lower())
    elif not length % 2:
        li = ri = length // 2
        initials = ''.join(fn[:li].lower() + ln[:ri].lower())
    else:
        li = length // 2 + 1
        ri = length // 2
        initials = ''.join(fn[:li].lower() + ln[:ri].lower())

    if initials_in_table(conn, initials):
        length = length + 1
        initials = mk_initials(conn, name, length)

    return initials


def initials_in_table(conn: sqlite3.Connection, initials: str) -> bool:
    with conn:
        cur = conn.cursor()
        res = cur.execute("SELECT initials FROM persons")
        initials = res.fetchall()
        for res_initials in initials:
            abbr = ''.join(str(c) for c in res_initials)
            if abbr == initials:
                return True
        return False


def path_to_database() -> Path:
    cwd = Path(__file__).resolve().parent
    db_dir = cwd.parent / "data"
    db_path = db_dir.resolve()
    print(str(db_path))
    return db_path


def state_company(language: str) -> str:
    company_name = input(state_company_prompt[language])
    company_name = re.sub(' +', '_', company_name) + ".db"
    company_name = company_name.strip()
    return company_name


def create_headline(company_name: str, language: str,
                    prompt: str = action_prompt) -> str:
    company_name = company_name[:-3]
    company_name = re.sub("_", " ", company_name)
    length_name = 76 - len(company_name)
    prompt = action_prompt[language]
    length_prompt = 76 - len(prompt)
    company_line = f"| {company_name}" + ' ' * length_name + "|"
    final_action_prompt = "| " + prompt + ' ' * length_prompt + "|"

    menu_xxxxx_head = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {final_action_prompt}
    +{'-' * 77}+"""

    return menu_xxxxx_head


# type hint best practice for v3.10 or above
# https://stackoverflow.com/a/69440627/6597765
def check_for_matches(company_name: str, language: str) -> str | None:
    """
    Check if a name resembles that of the names found in the database folder.
    """

    targets = check_databases()
    if targets == []:
        return None
    threshold = 50
    scores = [fuzz.ratio(target, company_name) for target in targets]
    if scores:
        best_match_index = scores.index(max(scores))
        best_match = targets[best_match_index]

        if max(scores) > threshold:
            choice = input(f"Did you mean {best_match}? y/N: ")
            if choice == "y":
                print("best_match: ", best_match)
                return best_match

    repeat = input("Check again? y/N ")
    if repeat == "y":
        company_name = state_company(language)
        return check_for_matches(company_name, language)

    match = None
    return match


def check_databases() -> list:
    """
    Check if there are any databases inside the directory.
    """
    targets = []

    print("inside check_databases")
    path_to_db = path_to_database()
    for (dirpath, dirnames, filenames) in os.walk(path_to_db):
        for filename in filenames:
            print(filename)
            if filename.endswith(".db"):
                targets.append(filename)
    print("check_databases, targets: ", targets)

    return targets


def database_exists(company_name: str) -> bool:
    path = path_to_database()
    database_path = os.path.join(os.path.dirname(__file__), path + company_name)  # noqa
    if not os.path.isfile(database_path):
        print("inside database_exists: no file found")
        return False
    print("inside database_exists: file exists")
    return True


def pick_language() -> str:
    clear_screen()

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


class AttrDisplay:
    """
    Mark Lutz, Programming Python
    Provides an inheritable display overload method that shows instances
    with their class names and a name=value pair for each attribute stored
    on the instance itself (but not attrs inherited from its classes). Can
    be mixed into any class, and will work on any instance.
    """

    def gather_attrs(self) -> dict:
        """
        Check if attributes have content and add them to a list called attrs.
        """
        attrs = {}
        for key in sorted(self.__dict__):
            if self.__dict__[key] and self.__dict__[key] not in [
                "unknown",
                "ew",
                None,
            ]:
                attrs[key] = getattr(self, key)

        return attrs

    def __str__(self) -> str:
        """
        Instances will printed like this:
        name of class
        +-----------+---------+
        | attribute | value   |
        +-----------+---------+
        | attr1     + value1  |
        | attr2     + value2  |
        | ...

        see also: https://zetcode.com/python/prettytable/
        """
        language = "de"
        if language:
            attrs = self.translate()
        else:
            attrs = self.gather_attrs()
        print(f"{self.__class__.__name__}")
        t = PrettyTable(["attribute", "value"])
        t.align["attribute"] = "l"
        t.align["value"] = "l"
        for k, v in attrs.items():
            t.add_row([k, v])

        return str(t)

    def translate(self) -> dict:
        """
        Select dict with attribute names of another language.
        """
        attrs = self.gather_attrs()
        new_attrs = {}
        for k, v in attrs.items():
            if k in german_attrs:
                german_key = german_attrs[k]
                new_attrs[german_key] = attrs[k]

        return new_attrs
