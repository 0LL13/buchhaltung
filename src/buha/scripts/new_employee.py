#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_employee.py
import datetime
import getpass
import hashlib
import os
import sqlite3
from .mk_key import mk_key


name_new_employee = {
    "fr": "Entrez le nom de l'employé (prénom, nom): ",
    "en": "Enter name of employee (first name, last name): ",
    "de": "Name der/s Mitarbeiterin/s (Vorname, Name): ",
    "es": "Ingrese el nombre del empleado (nombre, apellido): ",
    "it": "Inserisci il nome del dipendente (nome, cognome): ",
    "tr": "Çalışanın adını girin (ad, soyad): ",
}


def generate_table_employees(conn) -> None:
    cur = conn.cursor()
    table_employees = """CREATE TABLE IF NOT EXISTS employees (
                         employee_id INTEGER PRIMARY KEY,
                         key TEXT,
                         employee TEXT NOT NULL,
                         initial TEXT,
                         language TEXT,
                         company TEXT,
                         salt BLOB NOT NULL,
                         password_hash BLOB NOT NULL,
                         created_by TEXT,
                         timestamp TEXT
                         )"""
    cur.execute(table_employees)
    conn.commit()
    return


def new_employee(language: str, company: str, conn: sqlite3.Connection,
                 initial_creator: str = None) -> None:
    generate_table_employees(conn)
    new_employee = input(name_new_employee[language])

    if not employee_in_table(conn, new_employee):
        new_key = mk_key(conn)
        # default password, should be changed by employee
        password = "asd"
        salt, password_hash = hash_password(password)
        if initial_creator is None:
            created_by = getpass.getuser()
        else:
            created_by = initial_creator
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        print(timestamp)
        initial_new_employee = mk_initial(conn, new_employee, 2)

        add_employee = """INSERT INTO employees (
                          key, employee, initial, language, company,
                          salt, password_hash,
                          created_by, timestamp)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cur = conn.cursor()
        cur.execute(add_employee, (new_key, new_employee, initial_new_employee,
                                   language, company,
                                   sqlite3.Binary(salt),
                                   sqlite3.Binary(password_hash),
                                   created_by, timestamp))
        conn.commit()
    else:
        print("There already is an entry with the same name.")

    if 1:
        show_employees(conn)

    return


def hash_password(password):
    salt = os.urandom(16)  # Generate a random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # noqa
    return salt, password_hash


def mk_initial(conn, name, length) -> str:
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