#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A set of dataclasses concerning customer data."""
import os
import sys
from person import Person
from dataclasses import dataclass, field
from typing import Optional


PACKAGE_PARENT = ".."
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)  # isort:skip # noqa # pylint: disable=wrong-import-position
sys.path.append(
    os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT))
)  # isort: skip # noqa # pylint: disable=wrong-import-position

from resources.constants import (  # type: ignore # noqa
    PEER_PREPOSITIONS,
    PEERTITLES,
)
from resources.helpers import AttrDisplay  # type: ignore # noqa


@dataclass
class _Customer_base:
    company: Optional[str] = field(default=None)
    main_phone_number: Optional[str] = field(default=None)
    phone_extension: Optional[str] = field(default=None)
    job_title: Optional[str] = field(default=None)
    division: Optional[str] = field(default=None)  # Abteilung


@dataclass
class Customer(_Customer_base, Person, AttrDisplay):
    """Customer data: name, address, contracts."""

    def __post_init__(self):
        """
        Initializing a customer, and translating to a different language, if
        specified.
        """


if __name__ == "__main__":

    customer_1 = Customer(
        "Sven", "Rübennase", academic_title="MBA", date_of_birth="1990")  # noqa
    print(
        'customer_1 = Customer("Sven", "Rübennase", academic_title="MBA", date_of_birth="1990")'  # noqa
    )  # noqa
    print(customer_1)

    customer_2 = Customer("Paul Heiner D.", "Wiekeiner", academic_title="Dr.",
                          phone_extension="243")  # noqa
    print(
        'customer_2 = Customer("Pauley Heiner D.", "Wiekeiner", academic_title="Dr.", phone_extension="243")')  # noqa
    print(customer_2)

    customer_3 = Customer("Dagmara", "Bodelschwingh", peer_title="Gräfin",
                          company="Luftschloss GmbH", main_phone_number="+492345678-0")  #noqa
    print('customer_3 = Customer("Dagmara", "Bodelschwingh", peer_title="Gräfin", company="Luftschloss GmbH", main_phone_number="+492345678-0")')  #noqa
    print(customer_3)
