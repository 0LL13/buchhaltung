# -*- coding: utf-8 -*-
# context.py
import os
import sys

PACKAGE_PARENT = "../src"
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)  # isort:skip # noqa # pylint: disable=wrong-import-position
sys.path.append(
    os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT))
)  # isort: skip # noqa # pylint: disable=wrong-import-position

from buchhaltung.resources.helpers import AttrDisplay  # type: ignore
from buchhaltung.resources.helpers import TooManyFirstNames
from buchhaltung.resources.constants import PEER_PREPOSITIONS
from buchhaltung.resources.constants import PEERTITLES

from buchhaltung import (  # type: ignore # isort:skip # noqa # pylint: disable=unused-import, wrong-import-position
    person,
)  # pylint: disable=unused-import  # noqa
