"""Task 3 - External Data-Driven Tests for Member 2 (Ibadat Ali).

Every row of each CSV file in tests_assignment/data/ executes as an automated
test case. Each test maps to formal Test Cases documented in test_cases/Test_Cases.xlsx:
  * TC-M2-01: natural_list  (m2_lists.csv)
  * TC-M2-02: clamp         (m2_clamp.csv)
  * TC-M2-03: intword       (m2_intword.csv)
  * TC-M2-04: naturaldate   (m2_naturaldate.csv)
"""
import datetime as dt

import pytest
from freezegun import freeze_time

from humanize import clamp, intword, natural_list, naturaldate
from tests_assignment.csv_loader import load_params, optional, parse_value

pytestmark = [pytest.mark.datadriven, pytest.mark.m2]


# -----------------------------------------------------------------------------
# TC-M2-01: natural_list from CSV (humanize.lists)
# -----------------------------------------------------------------------------
@pytest.mark.lists
@pytest.mark.parametrize("row", load_params("m2_lists.csv"))
def test_natural_list_from_csv(row):
    """TC-M2-01: Verify natural_list formatting with items loaded from CSV."""
    raw_items = row["items"].strip()
    if not raw_items:
        items = []
    else:
        items = [parse_value(item) for item in raw_items.split("|")]

    result = natural_list(items)
    assert result == row["expected"]


# -----------------------------------------------------------------------------
# TC-M2-02: clamp from CSV (humanize.number)
# -----------------------------------------------------------------------------
@pytest.mark.number
@pytest.mark.clamp
@pytest.mark.parametrize("row", load_params("m2_clamp.csv"))
def test_clamp_from_csv(row):
    """TC-M2-02: Verify clamp boundaries and formatting loaded from CSV."""
    val = parse_value(row["value"])
    floor = parse_value(row["floor"]) if optional(row["floor"]) is not None else None
    ceil = parse_value(row["ceil"]) if optional(row["ceil"]) is not None else None
    floor_token = optional(row["floor_token"]) or "<"
    ceil_token = optional(row["ceil_token"]) or ">"
    fmt = optional(row["format"]) or "{:}"

    result = clamp(val, floor=floor, ceil=ceil, floor_token=floor_token, ceil_token=ceil_token, format=fmt)
    assert result == row["expected"]


# -----------------------------------------------------------------------------
# TC-M2-03: intword from CSV (humanize.number)
# -----------------------------------------------------------------------------
@pytest.mark.number
@pytest.mark.intword
@pytest.mark.parametrize("row", load_params("m2_intword.csv"))
def test_intword_from_csv(row):
    """TC-M2-03: Verify intword scales and custom formats loaded from CSV."""
    val = parse_value(row["value"])
    fmt = optional(row["format"]) or "%.1f"

    result = intword(val, format=fmt)
    assert result == row["expected"]


# -----------------------------------------------------------------------------
# TC-M2-04: naturaldate from CSV (humanize.time)
# -----------------------------------------------------------------------------
@pytest.mark.time
@pytest.mark.naturaldate
@pytest.mark.parametrize("row", load_params("m2_naturaldate.csv"))
def test_naturaldate_from_csv(row):
    """TC-M2-04: Verify naturaldate relative/exact thresholds loaded from CSV."""
    with freeze_time(row["reference_date"]):
        target = dt.date.fromisoformat(row["target_date"])
        result = naturaldate(target)
        assert result == row["expected"]
