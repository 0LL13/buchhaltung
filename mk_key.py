#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mk_key.py
import string
import secrets
import sqlite3


def table_in_db(con, name_of_table) -> bool:
    cur = con.cursor()
    # https://stackoverflow.com/a/1604121/6597765
    select_table = f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{name_of_table}'; """  # noqa
    list_of_tables = cur.execute(select_table).fetchall()
    if not list_of_tables:
        return False
    return True


def generate_table(con, name_of_table) -> None:
    cur = con.cursor()
    new_table = f"CREATE TABLE '{name_of_table}'(last_name, first_name, key)"
    cur.execute(new_table)
    return


def generate_key(alphabet) -> str:
    while True:
        key = ''.join(secrets.choice(alphabet) for i in range(8))
        if (any(c.islower() for c in key)
                and any(c.isupper() for c in key)
                and sum(c.isdigit() for c in key) >= 1):
            break
    return key


def key_in_db(key, con) -> bool:
    cur = con.cursor()
    res = cur.execute("SELECT key FROM keys")
    for res_key in res:
        if res_key == key:
            return True
    return False


def show_keys(con, name_of_table) -> None:
    cur = con.cursor()
    data = cur.execute(f"""SELECT * from '{name_of_table}'""")
    res = data.fetchall()
    for res_key in res:
        print(res_key)


def connect_entry_with_key(con, name_of_table, person) -> None:
    cur = con.cursor()
    add_key = f"INSERT INTO '{name_of_table}' VALUES ('Max', 'Mustermann', '{key}')"  # noqa
    cur.execute(add_key)
    con.commit()


def main():
    person = "employee"
    name_of_table = "keys"
    alphabet = string.ascii_letters + string.digits
    con = sqlite3.connect("buchhaltung.db")
    if not table_in_db(con, name_of_table):
        generate_table(con, name_of_table)
    key = generate_key(alphabet)
    if not key_in_db(key, con):
        connect_entry_with_key(con, person)
    else:
        main()
    show_keys(con, name_of_table)
    con.close()


if __name__ == "__main__":
    main()
