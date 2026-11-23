"""Tests for the public exports of `autoresume.bank` (Q-export-load-bank).

Goal: callers can write `from autoresume.bank import load_bank, BankLoadError` without knowing
that the loader lives in `autoresume.bank.loader`.
"""

import autoresume.bank as bank_pkg
from autoresume.bank import BankLoadError, load_bank
from autoresume.bank.loader import BankLoadError as LoaderBankLoadError
from autoresume.bank.loader import load_bank as loader_load_bank


def test_load_bank_and_bank_load_error_are_exported_from_package():
    """The names import from the package and are the same objects as in the loader module."""
    assert load_bank is loader_load_bank
    assert BankLoadError is LoaderBankLoadError
    assert "load_bank" in bank_pkg.__all__
    assert "BankLoadError" in bank_pkg.__all__
