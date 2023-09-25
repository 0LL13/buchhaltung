#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A set of dataclasses concerning persons and their particulars."""
import datetime
import os
import sys
from operator import itemgetter
from dataclasses import dataclass, field
from typing import Optional, Tuple
from gender_guesser import detector as sex  # type: ignore

PACKAGE_PARENT = ".."
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)  # isort:skip # noqa # pylint: disable=wrong-import-position
sys.path.append(
    os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT))
)  # isort: skip # noqa # pylint: disable=wrong-import-position

try:
    from buchhaltung.resources.helpers import AttrDisplay  # type: ignore # isort:skip # noqa
except ModuleNotFoundError:
    print(os.path)
    print(sys.path)
    print()
from buchhaltung.resources.helpers import TooManyFirstNames # type: ignore # isort:skip # noqa
from buchhaltung.resources.constants import PEER_PREPOSITIONS # type: ignore # isort:skip # noqa
from buchhaltung.resources.constants import PEERTITLES # type: ignore # isort:skip # noqa


@dataclass
class _Peertitle_default:
    peer_title: Optional[str] = field(default=None)
    peer_preposition: Optional[str] = field(default=None)

    def nobility_title(self) -> None:
        if self.peer_title is not None:
            title = self.peer_title
            self.peer_title, self.peer_preposition = self.title_fix(title)

    def title_fix(self, title) -> Tuple[str, str]:
        titles = title.split(" ")
        title_tmp = ""
        preposition_tmp = ""
        for prep in titles:
            if prep.lower() in PEER_PREPOSITIONS:
                preposition_tmp = preposition_tmp + prep.lower() + " "
            elif prep in PEERTITLES:
                title_tmp = title_tmp + prep + " "
        peer_preposition = preposition_tmp.strip()
        peer_title = title_tmp.strip()

        return peer_title, peer_preposition


@dataclass
class Noble(_Peertitle_default, Name, AttrDisplay):
    def __post_init__(self):
        """Initialize names and titles."""
        Name.__post_init__(self)
        self.nobility_title()


@dataclass
class _Academic_title_default:
    academic_title: Optional[str] = field(default=None)

    def degree_title(self) -> None:
        if self.academic_title is not None:
            title = self.academic_title
            self.academic_title = self.title_repair(title)

    def title_repair(self, title) -> str:
        if ".D" in title:
            title = ". ".join(c for c in title.split("."))
        if ".A" in title:
            title = ". ".join(c for c in title.split("."))
        if title.endswith("Dr"):
            title = title[:-2] + "Dr."
        while "  " in title:
            title = title.replace("  ", " ")
        title = title.strip()

        return title


@dataclass
class Academic(_Academic_title_default, Name, AttrDisplay):
    def __post_init__(self):
        """Initialize names of Name and degree."""
        Name.__post_init__(self)
        self.degree_title()


@dataclass
class _Person_default:
    gender: str = field(default="unknown")
    year_of_birth: str = field(default="unknown")
    date_of_birth: str = field(default="unknown")
    divorcée: Optional[str] = field(default=None)
    age: str = field(default="unknown")
    deceased: bool = field(default=False)
    year_of_death: str = field(default="unknown")
    date_of_death: str = field(default="unknown")
    profession: str = field(default="unknown")


@dataclass
class Person(
    _Peertitle_default,
    _Academic_title_default,
    _Person_default,
    Name,
    AttrDisplay,  # noqa
):
    def __post_init__(self):
        """
        Initializing names, titles (academic and peer), age, sex, and year of
        birth."""
        Name.__post_init__(self)
        Noble.__post_init__(self)
        Academic.__post_init__(self)
        self.get_sex()
        self.get_age()
        self.get_year_of_birth()

    def get_sex(self) -> None:
        if "-" in self.first_name:
            first_name = self.first_name.split("-")[0]
        else:
            first_name = self.first_name
        d = sex.Detector()
        gender = d.get_gender(f"{first_name}")
        if "female" in gender:
            self.gender = "female"
        elif "male" in gender:
            self.gender = "male"

    def get_year_of_birth(self) -> None:
        if "." in self.date_of_birth:
            self.year_of_birth = self.date_of_birth.split(".")[-1]
        elif len(self.date_of_birth.strip()) == 4:
            self.year_of_birth = self.date_of_birth
            self.date_of_birth = "unknown"

    def get_age(self) -> None:
        today = datetime.date.today()
        if self.date_of_birth != "unknown":
            born = str(self.date_of_birth)
            if len(born) > 4 and len(born) < 12 and "-" in born:
                self.get_yob_and_yod(born)
            elif len(born) > 8 and "-" in born:
                self.get_dob_and_dod(born)
            elif "." in born:
                born = born.split(".")[-1]
                self.age = str(int(today.year) - int(born.strip()))
            else:
                self.age = str(int(today.year) - int(born.strip()))

    def get_yob_and_yod(self, born) -> None:
        self.year_of_death = born.strip()[5:]
        self.year_of_birth = born[:4]
        self.deceased = True

    def get_dob_and_dod(self, born) -> None:
        self.date_of_death = born.split("-")[-1].strip()
        self.date_of_birth = born.split("-")[0].strip()
        self.deceased = True


@dataclass
class TestClass(AttrDisplay):
    a: str
    b: str
    c: str


class MenuNewPerson():
    """Menu to enter name and particulars of a person."""

    def __init__(self):
        self.choices = {
            "1": self.enter_name,
            "2": self.enter_titles,
            "3": self.enter_particulars,
            "4": False,
        }

    def display_menu(self):
        print("""
              1: Name
              2: Titles
              3: Additional personal data
              4: Quit
              """)

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

    def display_menu(self):
        print("""
                Fields with (*) are obligatory

                1: (*) First Name
                2: Middle Name(s)
                3: (*) Last Name
                4: Nickname
                5: Maiden Name
                6: Generational Suffix (Jr., Sr.)
                7: Salutation
                8: Commit
                9: Quit
                """)

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
    prepared_values = {"fn": "Bodo", "mn": "Knuth H.", "ln": "Weibel",
                       "nn": "Knuti", "salutation": "Herr", "suffix": "Sr.",
                       }
    menu.run(use_prepared_values=True, prepared_values=prepared_values)
    generate_name_instance(menu)


def generate_name_instance(menu) -> None:
    collected_entries = menu.get_entries()
    # see here: https://stackoverflow.com/a/17755259/6597765
    first_name, last_name = itemgetter("fn", "ln")(collected_entries)
    name_list = [first_name, last_name]
    mn, nn, maiden, suffix, salutation = \
        itemgetter("mn", "nn", "maiden", "suffix", "salutation")(collected_entries)  # noqa
    default_names_list = [mn, nn, maiden, suffix, salutation]

    name = Name(*name_list, *default_names_list)
    print(name)


if __name__ == "__main__":

    menu = MenuNewPerson()
    menu.run()
    sys.exit()

    main()
    sys.exit()

    name = Name("Hans-Peter Hermann Klaus", "Werner")
    print('name = Name("Hans-Peter Hermann Klaus", "Werner")')
    print(name)

    name = Name("Bodo Knuth H.", "Weibel", salutation="Herr", nickname="Knuti")  # noqa
    print("""name = 'Name("Bodo Knuth H.", "Weibel", salutation="Herr", nickname="Knuti")'""")  # noqa
    print(name)

    name = Name("Tom", "Bombadil", middle_names="None", maiden_name="None", generational_suffix="None", salutation="Mr.")  # noqa
    print("""name = Name("Tom", "Bombadil", middle_names="None", maiden_name="None", generational_suffix="None", salutation='Mr.'""")  # noqa
    print(name)

    noble = Noble("Dagmara", "Bodelschwingh", peer_title="Gräfin von")
    print('noble = Noble("Dagmara", "Bodelschwingh", peer_title="Gräfin von")')  # noqa
    print(noble)

    academic = Academic("Horst Heiner D.", "Wiekeiner", academic_title="Dr.")  # noqa
    print(
        'academic = Academic("Horst Heiner D.", "Wiekeiner", academic_title="Dr.")'  # noqa
    )  # noqa
    print(academic)

    person_1 = Person(
        "Sven", "Rübennase", academic_title="MBA", date_of_birth="1990"
    )  # noqa
    print(
        'person_1 = Person("Sven", "Rübennase", academic_title="MBA", date_of_birth="1990")'  # noqa
    )  # noqa
    print(person_1)

    person_2 = Person("Pauley Heiner D.", "Wiekeiner", academic_title="Dr.")  # noqa
    print(
        'person_2 = Person("Pauley Heiner D.", "Wiekeiner", academic_title="Dr.")'  # noqa
    )  # noqa
    print(person_2)

    person_3 = Person("Dagmara", "Bodelschwingh", peer_title="Gräfin von")
    print('person_3 = Person("Dagmara", "Bodelschwingh", peer_title="Gräfin von")')  #noqa
    print(person_3)

    person_4 = Person("Rainer-Maria", "Brandauer", academic_title="Prof.")  # noqa
    print(
        'person_4 = Person("Rainer-Maria", "Brandauer", academic_title="Prof.")'  # noqa
    )  # noqa
    print(person_4)

    person_5 = Person("Rainer-Maria", "Brandauer", academic_title="Prof.",
                      peer_title="Fürst von")  # noqa
    print(
        'person_5 = Person("Rainer-Maria", "Brandauer", academic_title="Prof.", peer_title="Fürst von")')  # noqa
    print(person_5)

    person_6 = Person("Horatio", "Pimpernell", academic_title="Prof. Dr.   Dr.", # noqa
                      middle_names="R.")  # noqa
    print(
        'person_6 = Person("Horatio", "Pimpernell", academic_title="Prof. Dr.   Dr.", middle_names="R.",'  # noqa
    )
    print(person_6)

    test = TestClass("späm", "ham", "ew")
    print(
        'test = TestClass("späm", "ham", "ew")'
    )
    print(test)
