#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_employee.py
import datetime
import getpass
import hashlib
import os
import sqlite3
from typing import Tuple
from .mk_key import mk_key


name_new_employee = {
    "fr": "Entrez le nom de l'employé (prénom, nom): ",
    "en": "Enter name of employee (first name, last name): ",
    "de": "Name der/s Mitarbeiterin/s (Vorname, Name): ",
    "es": "Ingrese el nombre del empleado (nombre, apellido): ",
    "it": "Inserisci il nome del dipendente (nome, cognome): ",
    "tr": "Çalışanın adını girin (ad, soyad): ",
}


def generate_table_employees(conn: sqlite3.Connection) -> None:
    """
    key: unique identifier
    initial: the employee's initials
    created_by: the initials of who created the entry
    account: key to account (? - necessary??)
    """
    table_employees = """CREATE TABLE IF NOT EXISTS employees (
                         key TEXT,
                         employee TEXT NOT NULL,
                         initial TEXT,
                         created_by TEXT,
                         timestamp TEXT
                         )"""
    with conn:
        cur = conn.cursor()
        cur.execute(table_employees)
        conn.commit()

    return None


def new_employee(language: str,
                 conn: sqlite3.Connection,
                 created_by: str = None) -> None:

    if created_by is None:
        created_by = getpass.getuser()
    new_employee = input(name_new_employee[language])
    add_employee_to_db(conn, new_employee, language, created_by)

    return None


def add_employee_to_db(conn: sqlite3.Connection,
                       new_employee: str,
                       language: str,
                       created_by: str) -> None:

    add_employee = """INSERT INTO employees (
                        key, employee, initial, created_by, timestamp)
                        VALUES (?, ?, ?, ?, ?)"""

    generate_table_employees(conn)
    account = None
    if not employee_in_table(conn, new_employee):
        mk_new_entry_employee(conn, new_employee)
    else:
        print("There already is an entry with the same name.")
        choice = input("Create anyway? y/N: ")
        if choice == "y":
            mk_new_entry_employee(conn, new_employee)
        else:
            print("Abort creation of new employee.")
            return None

    if 1:
        show_employees(conn)

    return None


def mk_new_entry_employee(conn: sqlite3.Connection, new_employee: str) -> None:
    new_key = mk_key(conn)
    # default password, should be changed by employee
    password = "asd"
    salt, password_hash = hash_password(password)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(timestamp)
    initial_new_employee = mk_initial(conn, new_employee, 2)

    with conn:
        cur = conn.cursor()
        cur.execute(add_employee, (new_key, new_employee,
                                   initial_new_employee,
                                   created_by,
                                   timestamp))
        conn.commit()

    return None


def hash_password(password: str) -> Tuple[str, str]:
    salt = os.urandom(16)  # Generate a random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # noqa
    return salt, password_hash


def mk_initial(conn: sqlite3.Connection, name: list, length: int) -> str:
    fn = name.split()[0]
    ln = name.split()[1]

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


def initial_in_table(conn: sqlite3.Connection, initial: str) -> bool:
    with conn:
        cur = conn.cursor()
        res = cur.execute("SELECT initial FROM employees")
        initials = res.fetchall()
        for res_initial in initials:
            abbr = ''.join(str(c) for c in res_initial)
            if abbr == initial:
                return True
        return False


def employee_in_table(conn: sqlite3.Connection, employee: str) -> bool:
    with conn:
        cur = conn.cursor()
        res = cur.execute("SELECT employee FROM employees")
        employees = res.fetchall()
        for res_employee in employees:
            name = " ".join(str(c) for c in res_employee)
            if name == employee:
                return True
        return False


def show_employees(conn: sqlite3.Connection) -> None:
    with conn:
        cur = conn.cursor()
        data = cur.execute("""SELECT * from employees""")
        res = data.fetchall()
        for res_employee in res:
            print(res_employee)


if __name__ == "__main__":
    new_employee()
