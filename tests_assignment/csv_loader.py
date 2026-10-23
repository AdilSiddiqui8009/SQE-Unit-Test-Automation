"""Helpers that turn rows of the CSV data files into pytest parameters.

CSV conventions
  * an empty cell  -> "use the function's default"
  * value cells    -> int, else float (so inf/nan/1e30 work), else the literal text;
                      the token `None` means Python None
  * technique col  -> ECP | BVA | Negative | Option  (mapped to pytest markers)
"""
import csv
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"
TECHNIQUE_MARKER = {"ECP": "ecp", "BVA": "boundary", "Negative": "negative", "Option": "ecp"}


def parse_value(text):
    if text == "None":
        return None
    for caster in (int, float):
        try:
            return caster(text)
        except ValueError:
            pass
    return text


def parse_bool(text, default=False):
    return default if text == "" else text.strip().lower() == "true"


def optional(text):
    """Return None for an empty cell so the caller can fall back to a default."""
    return None if text == "" else text


def load_params(csv_name):
    """Return one pytest.param per CSV row, id = value of the `id` column."""
    params = []
    with open(DATA_DIR / csv_name, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            marker = getattr(pytest.mark, TECHNIQUE_MARKER[row["technique"]])
            params.append(pytest.param(row, id=row["id"], marks=marker))
    return params
