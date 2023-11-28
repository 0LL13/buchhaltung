#!/usr/bin/env python
# -*- coding: utf-8 -*-
# constants.py
"""All the language dictionaries to pick an option from."""

from typing import Callable


# ######### import -> all modules with menus - helpers.py #####################

def task_headline(task: str, language: str) -> str:
    headlines = {
        "main": main_headline,
        "login": login_headline,
        "settings": settings_headline,
        "new entry": new_entry_headline,
        "person": person_headline,
        "start": start_headline,
        "names": names_headline,
    }
    return headlines[task][language]


def task_menu(task: str, language: str) -> str:
    menu = {
        "login": login_menu,
        "settings": settings_menu,
        "new entry": new_entry_menu,
        "person": person_menu,
        "start": start_menu,
        "names": names_menu,
    }
    return menu[task][language]


def choose_option(language: str) -> Callable:
    prompt = {
        "en": "    Enter an option: ",
        "de": "    Eingabe wählen: "
    }
    return input(prompt[language])


# ######## import -> main.py ##################################################

main_headline = {
    "en": "A small-scale accounting program",
    "de": "Ein Buchhaltungsprogramm für kleine Unternehmen",
}


# ######## import -> login.py #################################################

def enter_initials(language: str) -> Callable:
    prompt = dict()
    prompt["en"] = "    Enter initials/nick: "
    prompt["de"] = "    Initialien oder Spitznamen eingeben: "
    return input(prompt[language])


login_headline = {
    "en": "LOGIN MENU",
    "de": "LOGIN MENÜ",
}

password_prompt = {
    "en": "    Enter password: ",
    "de": "    Passwort angeben: ",
}

login_menu = dict()
login_menu["de"] = """
    1. Einloggen
    2. Beenden
    """


# ######### import -> settings.py #############################################

settings_headline = {
    "en": "SETTINGS MENU",
    "de": "MENÜ EINSTELLUNGEN",
}

settings_menu = dict()
settings_menu["en"] = """
    1: Change language
    2: Change password
    3: Show my settings
    9: Back
    """

settings_menu["de"] = """
    1: Sprache wählen
    2: Passwort ändern
    3: Einstellungen anzeigen
    9: Zurück
"""


# ######### import -> names.py ################################################

names_headline = {
    "en": "NAME ENTRIES",
    "de": "NAMENSEINTRÄGE",
}

names_menu = dict()
names_menu["en"] = """
    Fields with (*) are obligatory

    1: (*) First Name
    2: Middle Name(s)
    3: (*) Last Name
    4: Nickname
    5: Maiden Name
    6: Generational Suffix (Jr., Sr.)
    7: Salutation
    8: Commit and back
    9: Back
    """

names_menu["de"] = """
    Felder mit (*) sind Pflichtfelder

    1: (*) Vorname
    2: Zweitname(n)
    3: (*) Nachname
    4: Spitzname
    5: Geburtsname
    6: Generationen-Suffix (Jr., Sr.)
    7: Anrede
    8: Speichern und zurück
    9: Zurück
    """

name_particulars_headline = {
    "en": "BASIC NAME PARTICULARS",
    "de": "ANGABEN ZUM NAMEN",
}

firstname_prompt = {
    "en": "    First name: ",
    "de": "    Vorname: ",
}

lastname_prompt = {
    "en": "    Last name: ",
    "de": "    Nachname: ",
}

middlenames_prompt = {
    "en": "    Middle names: ",
    "de": "    Weitere Vornamen: ",
}

salutation_prompt = {
    "en": "    Salutation: ",
    "de": "    Anrede: ",
}

maiden_prompt = {
    "en": "    Maiden name: ",
    "de": "    Geburtsname: ",
}

nickname_prompt = {
    "en": "    Nickname: ",
    "de": "    Spitzname: ",
}

suffix_prompt = {
    "en": "    Generational suffix (Jr., Sr.): ",
    "de": "    Generations-Suffix (Jr., Sr.): ",
}


def enter_prompt(prompt: dict, language: str) -> Callable:
    return input(prompt[language])


# ######## import -> new_entry.py #############################################

new_entry_headline = {
    "en": "NEW ENTRY",
    "de": "NEUER EINTRAG",
}

new_entry_menu = dict()
new_entry_menu["en"] = """
    1: Person
    2: Entity (company, bank, ...)
    3: Object (tools, wares, ...)
    4: Project (paint room, fix bicycle, ...)
    5: Service (inspection, consulting, ...)
    6: Account (job title, department, SKR number, ...)
    7: Settings (language, password, level of access)
    9: Back
    """

new_entry_menu["de"] = """
    1: Person
    2: Unternehmen (Firma, Bank, ...)
    3: Objekt (Werkzeuge, Waren, ...)
    4: Projekt (Zimmer streichen, Fahrradreperatur, ...)
    5: Dienstleistung (Inspektion, Beratung, ...)
    6: Konto (Jobtitel, Abteilung, SKR-Nummer, ...)
    7: Einstellungen (Sprache, Passwort, Zugangsberechtigungen)
    9: Zurück
    """

# ######## import -> person.py ################################################

person_headline = {
    "de": "PERSONENEINTRAG",
    "it": "INGRESSO DELLA PERSONA",
    "es": "ENTRADA DE PERSONA",
    "tr": "KIŞI GIRIŞI",
    "fr": "ENTRÉE DE PERSONNE",
    "en": "PERSON ENTRY",
}

languages = ["de", "en", "fr", "es", "it", "tr"]

person_menu = dict()
person_menu["de"] = """
    1: Name
    2: Titel
    3: Zusätzliche persönliche Daten
    4: Personen zeigen
    9: Zurück
    """
person_menu["en"] = """
    1: Name
    2: Titles
    3: Additional particulars
    4: Show persons
    9: Back
    """


# ######## import -> headline generator in helpers.py #########################

action_prompt = {
    "de": "WÄHLEN SIE EINE AKTION",
    "it": "SCEGLI UN'AZIONE",
    "es": "ELIGE ACCIÓN",
    "tr": "EYLEM SEÇIN",
    "en": "CHOOSE ACTION",
    "fr": "CHOISIR UNE ACTION",
}


state_company_prompt = {
    "fr": "    Indiquez votre entreprise: ",
    "en": "    State your company: ",
    "de": "    Name Ihres Unternehmens: ",
    "es": "    Indique su empresa: ",
    "it": "    Dichiara la tua azienda: ",
    "tr": "    Şirketinizi belirtin: ",
}


# ######## import -> start.py #################################################

start_menu = dict()
start_menu["de"] = """
    1: Neuer Eintrag
    2: Eintrag ändern
    3: Eintrag suchen
    4: Einstellungen
    5: Logout
    9: Beenden
    """

start_menu["en"] = """
    1: New entry
    2: Change entry
    3: Search entry
    4: Settings
    5: Logout
    9: Quit
    """

start_headline = {
    "de": "STARTMENÜ",
    "en": "START MENU",
}


# ######## import -> shared.py ################################################

german_attrs = {
    "academic_title": "Akademischer Titel",
    "age": "Alter",
    "alternative_address": "Alternative Adresse",
    "appartment_number": "Wohnungsnummer",
    "company_name": "Unternehmen",
    "date_of_birth": "Geburtsdatum",
    "date_of_death": "Todesdatum",
    "deceased": "gestorben",
    "delivery_address": "Lieferadresse",
    "delivery_instruction": "Lieferanweisung",
    "district": "Stadtteil",
    "division": "Abteilung",
    "divorcée": "geschieden",
    "first_name": "Vorname",
    "gender": "Geschlecht",
    "generational_suffix": "Generations-Suffix (z.B. 'Jr.')",
    "job_title": "Stellenbezeichnung",
    "last_name": "Nachname",
    "maiden_name": "Geburtsname",
    "main_phone_number": "Haupttelefonnummer",
    "middle_names": "weitere Vornamen",
    "name_of_building": "Gebäudenamen",
    "name_of_company": "Unternehmensname",
    "name_of_institution": "Institutionsname",
    "name_of_public_authority": "Behördenname",
    "province": "Bundesland",
    "nickname": "Spitzname",
    "peer_preposition": "Adelsprädikat",
    "peer_title": "Adelstitel",
    "phone_extension": "Durchwahl",
    "profession": "Beruf",
    "room_number": "Zimmernummer",
    "salutation": "Anrede",
    "stairs": "Stiegen",
    "state": "Land",
    "street": "Straße",
    "street_number": "Hausnummer",
    "sublodging": "c/o",
    "ward": "Wahlkreis",
    "year_of_birth": "Geburtsjahr",
    "year_of_death": "Todesjahr",
    "zip_code": "Postleitzahl",
}
