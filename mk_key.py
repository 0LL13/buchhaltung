#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import secrets
import sqlite3


def table_in_db(con) -> bool:
    cur = con.cursor()
    # https://stackoverflow.com/a/1604121/6597765
    list_of_tables = cur.execute("""SELECT name FROM sqlite_master
                                 WHERE type='table'
                                 AND name='keys'; """).fetchall()
    if not list_of_tables:
        return False
    return True


def generate_table(con) -> None:
    cur = con.cursor()
    cur.execute("CREATE TABLE keys(last_name, first_name, key)")
    return


def generate_key(alphabet) -> str:
    while True:
        key = ''.join(secrets.choice(alphabet) for i in range(8))
        if (any(c.islower() for c in key)
                and any(c.isupper() for c in key)
                and sum(c.isdigit() for c in key) >= 1):
            break
    return key


def key_in_db(key, cur) -> bool:
    res = cur.execute("SELECT key FROM keys")
    for res_key in res:
        if res_key == key:
            return True
    return False


def main():
    alphabet = string.ascii_letters + string.digits
    con = sqlite3.connect("keys.db")
    if not table_in_db(con):
        generate_table(con)
    cur = con.cursor()
    key = generate_key(alphabet)
    if not key_in_db(key, cur):
        return key
    else:
        main()
    con.close()


if __name__ == "__main__":
    main()
