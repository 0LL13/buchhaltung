#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions: exceptions, print style, ..."""
from prettytable import PrettyTable
from .attr_dicts import german_attrs  # type: ignore # isort:skip # noqa


language = "german"


class TooManyFirstNames(Exception):
    """
    Currently only one first name and two middle names are supported.
    Example: Tom H. Paul last_name
    """

    def __init__(self, message):
        """Usage: raise TooManyFirstNames ("message")."""

        Exception.__init__(self, message)


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
        print(f"{self.__class__.__name__}")
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
