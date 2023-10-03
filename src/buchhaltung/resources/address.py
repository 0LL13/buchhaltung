#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A set of dataclasses concerning the elements of an address."""
import os
import sys
from dataclasses import dataclass, field
from typing import Optional


from resources.constants import (  # type: ignore # noqa
    PEER_PREPOSITIONS,
    PEERTITLES,
)
from resources.helpers import AttrDisplay  # type: ignore # noqa


@dataclass
class _Address_default:
    street: Optional[str] = field(default=None)
    appartment_number: Optional[str] = field(default=None)  # Wohnungsnummer
    room_number: Optional[str] = field(default=None)  # Zimmernummer
    district: Optional[str] = field(default=None)  # Stadtteil
    ward: Optional[str] = field(default=None)  # Wahlkreis
    province: Optional[str] = field(default=None)  # Bundesland
    stairs: Optional[str] = field(default=None)  # "Stiegen"
    sublodging: Optional[str] = field(default=None)  # "c/o", "bei"
    name_of_building: Optional[str] = field(default=None)
    name_of_company: Optional[str] = field(default=None)
    name_of_institution: Optional[str] = field(default=None)
    name_of_public_authority: Optional[str] = field(default=None)
    state: Optional[str] = field(default=None)


@dataclass
class _Address_base:
    street_number: str
    zip_code: str
    city: str


@dataclass
class _Address_additions:
    delivery_instruction: Optional[str] = field(default=None)
    delivery_address: Optional[dataclass] = field(default=None)
    alternative_address: Optional[dataclass] = field(default=None)
    room_number: Optional[str] = field(default=None)
    district: Optional[str] = field(default=None)
    province: Optional[str] = field(default=None)
    stairs: Optional[str] = field(default=None)  # "Stiegen"
    sublodging: Optional[str] = field(default=None)  # "c/o", "bei"


@dataclass
class Address(_Address_default, _Address_additions, _Address_base, AttrDisplay):  # noqa
    """An address with streetnumber, zip-code, city, and other elements that
    are optional."""


if __name__ == "__main__":
    adresse_1 = Address("22", "12345", "Neustadt", street="Boboweg")
    print(
        'adresse_1 = Address("22", "12345", "Neustadt", street="Boboweg")')
    print(adresse_1)

    adresse_2 = Address("5a", "12345", "Piratenschiff",
                        street="Hooks Planke",
                        state="Nimmerland",
                        name_of_institution="Insel der Kinder")
    print(
        """adresse_2 = Address("5a", "12345", "Piratenschiff",
        street="Hooks Planke", state="Nimmerland",
        name_of_institution="Insel der Kinder")"""
    )
    print(adresse_2)
    print()
    print(dir(adresse_2))
