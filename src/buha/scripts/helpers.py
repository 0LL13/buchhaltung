#!/usr/bin/env python
# -*- coding: utf-8 -*-
# helpers.py
"""Helper functions: exceptions, print style, ..."""
import os
import re
import sqlite3
import sys
from fuzzywuzzy import fuzz
from pathlib import Path
from .constants import state_company_prompt
from .shared import Name
from .shared import clear_screen


# ############## headline generator ###########################################

def create_headline(company_name: str, headline: str) -> str:
    company_name = company_name[:-3]
    company_name = re.sub("_", " ", company_name)
    length_name = 76 - len(company_name)
    length_headline = 76 - len(headline)
    company_line = f"| {company_name}" + ' ' * length_name + "|"
    headline_final = "| " + headline + ' ' * length_headline + "|"

    menu_xxxxx_head = f"""
    +{'-' * 77}+
    {company_line}
    +{'-' * 77}+
    {headline_final}
    +{'-' * 77}+"""

    return menu_xxxxx_head


# ############## initials #####################################################

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


def initials_in_table(conn: sqlite3.Connection, new_initials: str) -> bool:
    with conn:
        cur = conn.cursor()
        res = cur.execute("SELECT initials FROM persons")
        res_initials = res.fetchall()
        for initials_in_db in res_initials:
            existing_initials = ''.join(str(c) for c in initials_in_db)
            if existing_initials == new_initials:
                return True
        return False


# ############## initialize database and activate #############################

def path_to_database() -> Path:
    cwd = Path(__file__).resolve().parent
    db_dir = cwd.parent / "data"
    db_path = db_dir.resolve()
    if 0:
        print(str(db_path))
    return db_path


def state_company(language: str) -> str:
    company_name = input(state_company_prompt[language])
    company_name = re.sub(' +', '_', company_name) + ".db"
    company_name = company_name.strip()
    return company_name


# type hint best practice for v3.10 or above
# https://stackoverflow.com/a/69440627/6597765
def check_for_matches(company_name: str, targets: list, language: str) -> str | None:  # noqa
    """
    Check if a name resembles that of the names found in the database folder.
    "targets" will be a non-empty list bc it's in an if-else condition.
    """

    threshold = 80
    scores = [fuzz.ratio(target, company_name) for target in targets]
    best_match_index = scores.index(max(scores))
    best_match = targets[best_match_index]

    if max(scores) > threshold:
        return best_match
    elif max(scores) > 50:
        choice = input(f"Did you mean {best_match}? y/N: ")
        if choice == "y":
            if 0:
                print("best_match: ", best_match)
            return best_match
    else:
        return None


def check_databases() -> list:
    """
    Check if there are any databases inside the directory.
    """
    targets = []

    # print("inside check_databases")
    path_to_db = path_to_database()
    for (dirpath, dirnames, filenames) in os.walk(path_to_db):
        for filename in filenames:
            # print(filename)
            if filename.endswith(".db"):
                targets.append(filename)
    # print("check_databases, targets: ", targets)

    return targets


def database_exists(company_name: str) -> bool:
    path = path_to_database()
    database_path = os.path.join(os.path.dirname(__file__), path + company_name)  # noqa
    if not os.path.isfile(database_path):
        return False
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


# ############## stand alone helpers ##########################################

def continue_() -> bool:
    check = input("Continue? y/N").strip().lower()
    return check == "y"


def get_person_id(conn: sqlite3.Connection, initials: str) -> int:
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT person_id FROM persons WHERE initials = ?", (initials,))  # noqa
        row = cur.fetchone()
        person_id = row[0]
        return person_id


def is_internal() -> bool:
    relation = input("    internal? y/N : ")
    if relation == "y":
        return True
    return False


# ############## show tables ##################################################

def show_table(conn: sqlite3.Connection, table: str) -> None:
    with conn:
        cur = conn.cursor()
        res = cur.execute(f"SELECT * FROM {table}")
        res_table = res.fetchall()
        for row in res_table:
            print(row)


def show_all(conn: sqlite3.Connection, person_id: int) -> None:
    tables = ["persons", "names", "settings"]
    with conn:
        cur = conn.cursor()
        for table in tables:
            query = f"SELECT * FROM {table} WHERE person_id = ?"
            cur.execute(query, (person_id,))
            res = cur.fetchone()
            print(res[0])


def show_my_table(conn: sqlite3.Connection, table: str, person_id: int) -> None:  # noqa
    with conn:
        cur = conn.cursor()
        query = f"SELECT * FROM {table} WHERE person_id = ?"
        cur.execute(query, (person_id,))
        res = cur.fetchall()
        if res:
            res_value = res[0]
            print(res_value)
