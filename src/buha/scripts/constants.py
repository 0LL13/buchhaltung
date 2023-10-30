#!/usr/bin/env python
# -*- coding: utf-8 -*-
# constants.py
"""All the language dictionaries to pick an option from."""


# ######### import -> all modules with menus ##################################

def choose_option(language: str) -> str:
    prompt = {
        "en": "    Enter an option: ",
        "de": "    Eingabe wählen: "
    }
    return input(prompt[language])


# ######## import -> login.py #################################################

def enter_initials(language: str) -> str:
    prompt = dict()
    prompt["en"] = "    Enter initials/nick: "
    prompt["de"] = "    Initialien oder Spitznamen eingeben: "
    return input(prompt[language])


login_prompt = dict()
login_prompt["en"] = "LOGIN MENU"
login_prompt["de"] = "LOGIN MENÜ"


# ######### import -> names.py ################################################

menu_names_entry = dict()
menu_names_entry["en"] = """
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

menu_names_entry["de"] = """
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

name_particulars_prompt = dict()
name_particulars_prompt["en"] = "BASIC NAME PARTICULARS"
name_particulars_prompt["de"] = "ANGABEN ZUM NAMEN"


# ######## import -> new_entry.py #############################################

new_entry_prompt = dict()
new_entry_prompt["en"] = "NEW ENTRY"
new_entry_prompt["de"] = "NEUER EINTRAG"


# ######## import -> person.py ################################################

enter_person_prompt = {
    "de": "PERSONENEINTRAG",
    "it": "INGRESSO DELLA PERSONA",
    "es": "ENTRADA DE PERSONA",
    "tr": "KIŞI GIRIŞI",
    "fr": "ENTRÉE DE PERSONNE",
    "en": "PERSON ENTRY",
}

languages = ["de", "en", "fr", "es", "it", "tr"]

menu_person_entry = dict()
menu_person_entry["de"] = """
    1: Name
    2: Titel
    3: Zusätzliche persönliche Daten
    4: Personen zeigen
    9: Zurück
    """
menu_person_entry["en"] = """
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
