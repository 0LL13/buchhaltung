#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_employee.py
import hashlib
import os
import sqlite3
from mk_key import mk_key


def generate_table(conn, name_of_table) -> None:
    cur = conn.cursor()
    new_table = f"""CREATE TABLE IF NOT EXISTS '{name_of_table}'(
                    employee_id INTEGER PRIMARY KEY,
                    key TEXT,
                    employee TEXT NOT NULL,
                    initial TEXT,
                    salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL
                    )"""
    cur.execute(new_table)
    conn.commit()
    return


def new_employee() -> None:
    database_path = os.path.join(os.path.dirname(__file__), "buchhaltung.db")
    conn = sqlite3.connect(database_path)
    generate_table(conn, "employees")

    new_employee = input("Enter name of employee (first name, last name): ")

    if not employee_in_table(conn, new_employee):
        cur = conn.cursor()
        new_key = mk_key()
        initial = mk_initial(conn, new_employee, 2)
        password = "asdfgh"
        salt, password_hash = hash_password(password)
        add_employee = """INSERT INTO employees (
                           key, employee, initial, salt, password_hash)
                           VALUES (?, ?, ?, ?, ?)"""
        cur.execute(add_employee, (new_key, new_employee, initial,
                    sqlite3.Binary(salt), sqlite3.Binary(password_hash)))
        conn.commit()
    else:
        print("Employee already exists.")

    if 1:
        show_employees(conn)

    conn.close()


def hash_password(password):
    salt = os.urandom(16)  # Generate a random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # noqa
    return salt, password_hash


def mk_initial(conn, name, length) -> str:
    fn = name.split()[0]
    ln = name.split()[1]

    print("length: ", length)

    if length == 2:
        initial = ''.join(fn[0].lower() + ln[0].lower())
    elif not length % 2:
        li = ri = length // 2
        initial = ''.join(fn[:li].lower() + ln[:ri].lower())
    else:
        li = length // 2 + 1
        ri = length // 2
        initial = ''.join(fn[:li].lower() + ln[:ri].lower())

    if initial_in_table(conn, initial):
        length = length + 1
        initial = mk_initial(conn, name, length)

    return initial


def initial_in_table(conn, initial) -> bool:
    cur = conn.cursor()
    res = cur.execute("SELECT initial FROM employees")
    initials = res.fetchall()
    for res_initial in initials:
        abbr = ''.join(str(c) for c in res_initial)
        if abbr == initial:
            return True
    return False


def employee_in_table(conn, employee) -> bool:
    cur = conn.cursor()
    res = cur.execute("SELECT employee FROM employees")
    employees = res.fetchall()
    for res_employee in employees:
        name = " ".join(str(c) for c in res_employee)
        if name == employee:
            return True
    return False


def show_employees(conn) -> None:
    cur = conn.cursor()
    data = cur.execute("""SELECT * from employees""")
    res = data.fetchall()
    for res_employee in res:
        print(res_employee)


if __name__ == "__main__":
    new_employee()
