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

from buha.scripts import (  # type: ignore # isort:skip # noqa # pylint: disable=unused-import, wrong-import-position
    helpers
)  # pylint: disable=unused-import  # noqa

from buha.scripts.helpers import (  # type: ignore # isort:skip # noqa # pylint: disable=unused-import, wrong-import-position
    check_databases,
    create_headline,
    Menu,
    mk_initials,
    path_to_database,
    path_to_db_dir,
    state_company,
    state_company_prompt,
)  # pylint: disable=unused-import  # noqa


from buha.scripts.constants import (  # type: ignore # isort:skip # noqa # pylint: disable=unused-import, wrong-import-position
    languages,
)  # pylint: disable=unused-import  # noqa


from buha.scripts.person import (  # type: ignore # isort:skip # noqa # pylint: disable=unused-import, wrong-import-position
    MenuNewPerson as NewPerson,
)  # pylint: disable=unused-import  # noqa


from buha.scripts.login import (  # type: ignore # isort:skip # noqa # pylint: disable=unused-import, wrong-import-position
    LoginMenu,
)  # pylint: disable=unused-import  # noqa


from buha.scripts.shared import (  # type: ignore # isort:skip # noqa # pylint: disable=unused-import, wrong-import-position
    clear_screen,
    Name,
)  # pylint: disable=unused-import  # noqa


PACKAGE_ROOT = ".."
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)  # isort:skip # noqa # pylint: disable=wrong-import-position
sys.path.append(
    os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_ROOT))
)  # isort: skip # noqa # pylint: disable=wrong-import-position


from main import (  # type: ignore # isort:skip # noqa # pylint: disable=unused-import, wrong-import-position
    activate_database,
    initialize,
    setup_new_company,
)  # pylint: disable=unused-import  # noqa
