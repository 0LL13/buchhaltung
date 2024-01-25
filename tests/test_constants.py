#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_constants.py
"""Tests for "constants" module."""


from context import enter_initials
from unittest.mock import patch


def test_constants_enter_initials(capsys):
    language_de = "de"
    language_en = "en"

    expected_de = "    Initialien oder Spitznamen eingeben: "
    expected_en = "    Enter initials/nick: "

    with patch("builtins.input", return_value=None) as mock_input:
        enter_initials(language_de)
        mock_input.assert_called_with(expected_de)

    with patch("builtins.input", return_value=None) as mock_input:
        enter_initials(language_en)
        mock_input.assert_called_with(expected_en)
