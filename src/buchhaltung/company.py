#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A set of dataclasses concerning company data."""
import os
import sys
from address import Address
from dataclasses import dataclass


PACKAGE_PARENT = ".."
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)  # isort:skip # noqa # pylint: disable=wrong-import-position
sys.path.append(
    os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT))
)  # isort: skip # noqa # pylint: disable=wrong-import-position


from resources.helpers import AttrDisplay  # type: ignore # noqa


# check out inheritance for dataclasses here:
# https://www.slingacademy.com/article/how-to-use-inheritance-with-dataclass-in-python/


@dataclass
class _Company_base:
    company_name: str
    main_phone_number: str


@dataclass
class Company(Address, _Company_base, AttrDisplay):
    """Company data: name, address, contracts."""

    def __post_init__(self):
        """Initializing a company."""


if __name__ == "__main__":
    pass
