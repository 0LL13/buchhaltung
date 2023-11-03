#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mk_key.py
import string
import secrets


def generate_table_keys(conn) -> None:
    cur = conn.cursor()
    new_table = "CREATE TABLE IF NOT EXISTS keys (key TEXT)"
    cur.execute(new_table)
    conn.commit()
    return


def generate_key(conn) -> str:
    generate_table_keys(conn)
    alphanumeric = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(alphanumeric) for _ in range(10))

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


def mk_key(conn):
    generate_table_keys(conn)
    key = generate_key(conn)
    if 0:
        show_keys(conn)
    conn.commit()
    return key


if __name__ == "__main__":
    mk_key()
