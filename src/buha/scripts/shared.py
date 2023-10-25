#!/usr/bin/env python
# -*- coding: utf-8 -*-
# helpers.py
"""Shared class definitions to avoid circular import issues."""
import os
import platform
from dataclasses import dataclass, field
from prettytable import PrettyTable
from typing import Optional
from .attr_dicts import german_attrs


language = "de"


def is_posix() -> bool:
    if platform.system() == "Windows":
        return False
    else:
        return True


def clear_screen() -> None:
    if is_posix():
        os.system("clear")
    else:
        os.system("cls")


# ############## class definitions ############################################

class AttrDisplay:
    """
    Mark Lutz, Programming Python
    Provides an inheritable display overload method that shows instances
    with their class names and a name=value pair for each attribute stored
    on the instance itself (but not attrs inherited from its classes). Can
    be mixed into any class, and will work on any instance.
    """

    def gather_attrs(self) -> dict:
        """
        Check if attributes have content and add them to a list called attrs.
        """
        attrs = {}
        for key in sorted(self.__dict__):
            if self.__dict__[key] and self.__dict__[key] not in [
                "unknown",
                "ew",
                None,
            ]:
                attrs[key] = getattr(self, key)

        return attrs

    def __str__(self) -> str:
        """
        Instances will printed like this:
        name of class
        +-----------+---------+
        | attribute | value   |
        +-----------+---------+
        | attr1     + value1  |
        | attr2     + value2  |
        | ...

        see also: https://zetcode.com/python/prettytable/
        """
        if language:
            attrs = self.translate()
        else:
            attrs = self.gather_attrs()
        # print(f"{self.__class__.__name__}")
        t = PrettyTable(["attribute", "value"])
        t.align["attribute"] = "l"
        t.align["value"] = "l"
        for k, v in attrs.items():
            t.add_row([k, v])

        return str(t)

    def translate(self) -> dict:
        """
        Select dict with attribute names of another language.
        """
        attrs = self.gather_attrs()
        new_attrs = {}
        for k, v in attrs.items():
            if k in german_attrs:
                german_key = german_attrs[k]
                new_attrs[german_key] = attrs[k]

        return new_attrs


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
    pass

#     def __post_init__(self):
#         """
#         Initializing the names of a person.
#
#         In case a Name instance is initialized with all first names in one
#         string, __post_init__ will take care of this and assign each first
#         name its attribute. Also it will raise TooManyFirstNames if more than
#         three first names are given.
#         """
#         print("post_init dataclass Name")
#         print(self.first_name)
#         first_names = self.first_name.split(" ")
#         self.first_name = first_names[0]
#         if len(first_names) > 1:
#             self.middle_names = " ".join(name for name in first_names[1:])
