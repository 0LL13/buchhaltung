#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A set of dataclasses concerning persons and their particulars."""
import sys
from operator import itemgetter
from dataclasses import dataclass, field
from typing import Optional
from resources.helpers import AttrDisplay


class MenuNewPerson():
    """Menu to enter name and particulars of a person."""

    def __init__(self):
        self.choices = {
            "1": self.enter_name,
            "2": self.enter_titles,
            "3": self.enter_particulars,
            "4": self.show_persons,
            "5": False,
        }

    def display_menu(self):
        menu_person_entry = (
            f"""
            +{'-' * 77}+
            | PERSON ENTRY{' ' * 64}|
            +{'-' * 77}+

            1: Name
            2: Titles
            3: Additional personal data
            4: Show persons
            5: Quit
            """)
        print(menu_person_entry)

    def run(self, initial) -> None:
        while True:
            self.display_menu()
            choice = input("Enter an option: ")
            if not self.choices.get(choice):
                break
            else:
                action = self.choices.get(choice)
                if action:
                    action(initial)
                else:
                    print(f"{choice} is not a valid choice.")

    def enter_name(self, initial) -> None:
        menu = MenuName()
        menu.run(initial)

    def enter_titles(self) -> None:
        pass

    def enter_particulars(self) -> None:
        pass

    def show_persons(self) -> None:
        pass


@dataclass
class _Name_default:
    middle_names: Optional[str] = field(default=None)
    nickname: Optional[str] = field(default=None)
    maiden_name: Optional[str] = field(default=None)
    suffix: Optional[str] = field(default=None)
    salutation: Optional[str] = field(default=None)


@dataclass
class _Name_base:
    first_name: str
    last_name: str


@dataclass
class Name(_Name_default, _Name_base, AttrDisplay):
    """A person's names: first, middle/s, last name."""

    def __post_init__(self):
        """
        Initializing the names of a person.

        In case a Name instance is initialized with all first names in one
        string, __post_init__ will take care of this and assign each first
        name its attribute. Also it will raise TooManyFirstNames if more than
        three first names are given.
        """
        first_names = self.first_name.split(" ")
        self.first_name = first_names[0]
        if len(first_names) > 1:
            self.middle_names = " ".join(name for name in first_names[1:])


class MenuName():
    """Menu to enter the names of a contact."""

    def __init__(self):
        self.entries = {
            "fn": False,
            "mn": None,
            "ln": False,
            "nn": None,
            "maiden": None,
            "suffix": None,
            "salutation": None,
        }

        self.choices = {
            "1": self.enter_firstname,
            "2": self.enter_middlenames,
            "3": self.enter_lastname,
            "4": self.enter_nickname,
            "5": self.enter_maidenname,
            "6": self.enter_generational_suffix,
            "7": self.salutation,
            "8": self.commit,
            "9": False,
        }

    def display_menu(self) -> None:
        menu_name_particulars = (
            f"""
            +{'-' * 77}+
            | BASIC NAME PARTICULARS{' ' * 54}|
            +{'-' * 77}+

            Fields with (*) are obligatory

            1: (*) First Name
            2: Middle Name(s)
            3: (*) Last Name
            4: Nickname
            5: Maiden Name
            6: Generational Suffix (Jr., Sr.)
            7: Salutation
            8: Commit
            9: Back
            """
        )
        print(menu_name_particulars)

    def run(self, initial, use_prepared_values=False, prepared_values=None) -> None:  # noqa
        """Display Menu, gather entries in dict "entries", and finally put
        the data in new instance of Name."""
        if not use_prepared_values:
            while True:
                self.display_menu()
                choice = input("Enter an option: ")
                if not self.choices.get(choice):
                    break
                else:
                    action = self.choices.get(choice)
                    if action:
                        action()
                    else:
                        print(f"{choice} is not a valid choice.")
        elif prepared_values is not None:
            self.entries.update(prepared_values)

    def commit(self) -> None:
        self.generate_name_instance()

    def enter_firstname(self):
        firstname = input("First Name: ")
        # check validity
        self.entries["fn"] = firstname

    def enter_middlenames(self):
        middlename = input("Middle Name(s): ")
        # check validity
        self.entries["mn"] = middlename

    def enter_lastname(self):
        lastname = input("Last Name: ")
        # check validity
        self.entries["ln"] = lastname

    def enter_nickname(self):
        nickname = input("Nickname: ")
        # check validity
        self.entries["nn"] = nickname

    def enter_maidenname(self):
        maidenname = input("Maiden Name: ")
        # check validity
        self.entries["maiden"] = maidenname

    def enter_generational_suffix(self):
        suffix = input("Generational Suffix: ")
        # check validity
        self.entries["suffix"] = suffix

    def salutation(self):
        salutation = input("Salutation: ")
        # check validity
        self.entries["salutation"] = salutation

    def get_entries(self):
        return self.entries

    def generate_name_instance(self) -> None:
        collected_entries = self.entries
        # see here: https://stackoverflow.com/a/17755259/6597765
        first_name, last_name = itemgetter("fn", "ln")(collected_entries)
        name_list = [first_name, last_name]
        mn, nn, maiden, suffix, salutation = \
            itemgetter("mn", "nn", "maiden", "suffix", "salutation")(collected_entries)  # noqa
        default_names_list = [mn, nn, maiden, suffix, salutation]

        name = Name(*name_list, *default_names_list)
        print(name)


def main():
    menu = MenuName()
    initial = "tb"
    prepared_values = {"fn": "Bodo", "mn": "Knuth H.", "ln": "Weibel",
                       "nn": "Knuti", "salutation": "Herr", "suffix": "Sr.",
                       }
    menu.run(initial, use_prepared_values=True, prepared_values=prepared_values)  # noqa
    menu.generate_name_instance()


if __name__ == "__main__":
    if 0:
        main()
        sys.exit()

    menu = MenuNewPerson()
    initial = "tb"
    menu.run(initial)
