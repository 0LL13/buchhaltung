#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mk_key.py
import os
import string
import secrets
import sqlite3


def generate_table(conn, name_of_table) -> None:
    cur = conn.cursor()
    new_table = f"CREATE TABLE IF NOT EXISTS '{name_of_table}'(key TEXT)"
    cur.execute(new_table)
    conn.commit()
    return


def generate_key(alphabet) -> str:
    database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")
    conn = sqlite3.connect(database_path)
    generate_table(conn, "keys")

    while True:
        key = ''.join(secrets.choice(alphabet) for i in range(8))
        if (any(c.islower() for c in key)
                and any(c.isupper() for c in key)
                and sum(c.isdigit() for c in key) >= 1):
            break

    if not key_in_db(conn, key):
        cur = conn.cursor()
        add_key = f"""INSERT INTO 'keys' VALUES ('{key}')"""
        cur.execute(add_key)
        conn.commit()

    return key


def key_in_db(conn, key) -> bool:
    cur = conn.cursor()
    res = cur.execute("SELECT key FROM keys")
    for res_key in res:
        if res_key == key:
            return True
    return False


def show_keys(conn) -> None:
    cur = conn.cursor()
    data = cur.execute("""SELECT key from keys""")
    res = data.fetchall()
    for res_key in res:
        print(res_key)


def mk_key():
    name_of_table = "keys"
    alphabet = string.ascii_letters + string.digits
    database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")
    conn = sqlite3.connect(database_path)
    generate_table(conn, name_of_table)
    key = generate_key(alphabet)
    if 0:
        show_keys(conn)
    conn.close()
    return key


if __name__ == "__main__":
    mk_key()
