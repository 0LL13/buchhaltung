#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_person.py
"""Tests for `person` package."""

import pytest
from dataclasses import dataclass

from context import person

from context import AttrDisplay  # type: ignore # noqa
from context import TooManyFirstNames  # type: ignore # noqa
from context import (  # type: ignore # noqa
    PEER_PREPOSITIONS,
    PEERTITLES,
)


names = [
    ["Alfons-Reimund Horst Emil", "Boeselager"],
    ["Horatio R.", "Pimpernell"],
    ["Sven Jakob", "Große Brömer"],
]


def equivalent_names(n1, n2):
    fn = n2[0].split()[0]
    ln = n2[-1]
    try:
        mn_2 = n2[0].split()[2]
    except IndexError:
        mn_2 = None
    try:
        mn_1 = n2[0].split()[1]
    except IndexError:
        mn_1 = None

    return (
        (n1.first_name == fn)
        and ((n1.middle_names == f'{mn_1} {mn_2}')
             or (n1.middle_names == mn_1)
             or n1.middle_names is None)
        and (n1.last_name == ln)
    )


@pytest.mark.parametrize("n", names)
def test_person_Name_para(n):
    name = person.Name(*n)
    assert equivalent_names(name, n)  # nosec


def test_person_Name():
    # pylint: disable=W0612, W0613

    name = person.Name("Alfons-Reimund Horst Emil", "Boeselager")
    assert name.first_name == "Alfons-Reimund"  # nosec
    assert name.middle_names == "Horst Emil"  # nosec
    assert name.last_name == "Boeselager"  # nosec


def test_person_Academic():
    # pylint: disable=W0612, W0613

    academic = person.Academic(
        "Horatio",
        "Pimpernell",
        middle_names="R.",
        academic_title="Prof.Dr.   Dr",  # noqa
    )
    assert academic.first_name == "Horatio"  # nosec
    assert academic.middle_names == "R."  # nosec
    assert academic.last_name == "Pimpernell"  # nosec
    assert academic.academic_title == "Prof. Dr. Dr."  # nosec

    academic = person.Academic(
        "Horatio Rübennase D.", "Pimpernell", academic_title="Prof.Dr.Dr"
    )
    assert academic.first_name == "Horatio"  # nosec
    assert academic.middle_names == "Rübennase D."  # nosec
    assert academic.last_name == "Pimpernell"  # nosec
    assert academic.academic_title == "Prof. Dr. Dr."  # nosec

    academic = person.Academic("Horatio", "Pimpernell", academic_title="B.A.")
    assert academic.academic_title == "B. A."  # nosec


def test_person_Noble():
    # pylint: disable=W0612, W0613

    noble = person.Noble("Sepp Theo", "Müller", peer_title="von und zu")

    assert noble.first_name == "Sepp"  # nosec
    assert noble.middle_names == "Theo"  # nosec
    assert noble.last_name == "Müller"  # nosec
    assert noble.peer_preposition == "von und zu"  # nosec

    noble = person.Noble("Seppl", "Müller", peer_title="Junker van")

    assert noble.first_name == "Seppl"  # nosec
    assert noble.last_name == "Müller"  # nosec
    assert noble.peer_title == "Junker"  # nosec
    assert noble.peer_preposition == "van"  # nosec

    noble = person.Noble("Sven Oskar", "Müller", peer_title="Graf Eumel von")

    assert noble.first_name == "Sven"  # nosec
    assert noble.middle_names == "Oskar"  # nosec
    assert noble.last_name == "Müller"  # nosec
    assert noble.peer_title == "Graf"  # nosec
    assert noble.peer_preposition == "von"  # nosec


def test_person_Person():
    # pylint: disable=W0612, W0613

    pers = person.Person(
        "Hugo", "Berserker", academic_title="MBA", date_of_birth="2000"
    )  # noqa

    assert pers.gender == "male"  # nosec
    assert pers.academic_title == "MBA"  # nosec
    assert pers.age == "23"  # nosec

    pers = person.Person(
        "Siggi Mathilde", "Berserker", date_of_birth="1980-2010"
    )  # noqa

    assert pers.gender == "unknown"  # nosec
    assert pers.middle_names == "Mathilde"  # nosec
    assert pers.year_of_birth == "1980"  # nosec
    assert pers.deceased is True  # nosec
    assert pers.year_of_death == "2010"  # nosec

    pers = person.Person("Sigrid", "Berserker", date_of_birth="10.1.1979")  # noqa

    assert pers.gender == "female"  # nosec
    assert pers.year_of_birth == "1979"  # nosec

    pers = person.Person(
        "Sigrid", "Berserker", date_of_birth="10.1.1979 - 22.10.2019"
    )  # noqa

    assert pers.date_of_birth == "10.1.1979"  # nosec
    assert pers.date_of_death == "22.10.2019"  # nosec


def test_person_TooManyFirstNames():
    # pylint: disable=W0612, W0613

    name = person.Name
    with pytest.raises(TooManyFirstNames):
        name("Alfons-Reimund Horst Emil Pupsi", "Schulze")


def test_person_AttrDisplay(capsys):
    # pylint: disable=W0612, W0613

    @dataclass
    class MockClass(AttrDisplay):
        a: str
        b: str
        c: str

    var_1 = "späm"
    var_2 = "ham"
    var_3 = "ew"

    mock_instance = MockClass(var_1, var_2, var_3)
    print(mock_instance)
    captured = capsys.readouterr()

    expected = """\nMockClass\n+-----------+-------+\n| attribute | value |\n+-----------+-------+\n+-----------+-------+\n"""  # noqa

    assert expected == captured.out  # nosec
