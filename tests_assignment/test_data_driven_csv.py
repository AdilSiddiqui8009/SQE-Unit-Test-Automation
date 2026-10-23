"""Task 3 - data-driven tests: every row of a CSV file is one test case.

Data files live in tests_assignment/data/. Each test is documented in
test_cases/Test_Cases.xlsx (TC-DD-001 ... TC-DD-006).
"""
import datetime as dt

import pytest

from humanize import apnumber, intcomma, naturaldelta, naturalsize, ordinal, precisedelta
from tests_assignment.csv_loader import load_params, optional, parse_bool, parse_value

pytestmark = pytest.mark.datadriven


@pytest.mark.number
@pytest.mark.parametrize("row", load_params("ordinal_cases.csv"))
def test_ordinal_from_csv(row):  # TC-DD-001
    assert ordinal(parse_value(row["value"])) == row["expected"]


@pytest.mark.number
@pytest.mark.parametrize("row", load_params("intcomma_cases.csv"))
def test_intcomma_from_csv(row):  # TC-DD-002
    ndigits = optional(row["ndigits"])
    value = parse_value(row["value"])
    result = intcomma(value) if ndigits is None else intcomma(value, int(ndigits))
    assert result == row["expected"]


@pytest.mark.number
@pytest.mark.parametrize("row", load_params("apnumber_cases.csv"))
def test_apnumber_from_csv(row):  # TC-DD-003
    assert apnumber(parse_value(row["value"])) == row["expected"]


@pytest.mark.filesize
@pytest.mark.parametrize("row", load_params("naturalsize_cases.csv"))
def test_naturalsize_from_csv(row):  # TC-DD-004
    result = naturalsize(
        parse_value(row["value"]),
        binary=parse_bool(row["binary"]),
        gnu=parse_bool(row["gnu"]),
        format=optional(row["format"]) or "%.1f",
    )
    assert result == row["expected"]


@pytest.mark.time
@pytest.mark.parametrize("row", load_params("naturaldelta_cases.csv"))
def test_naturaldelta_from_csv(row):  # TC-DD-005
    result = naturaldelta(
        dt.timedelta(seconds=parse_value(row["seconds"])),
        months=parse_bool(row["months"], default=True),
        minimum_unit=optional(row["minimum_unit"]) or "seconds",
    )
    assert result == row["expected"]


@pytest.mark.time
@pytest.mark.parametrize("row", load_params("precisedelta_cases.csv"))
def test_precisedelta_from_csv(row):  # TC-DD-006
    result = precisedelta(
        dt.timedelta(seconds=parse_value(row["seconds"])),
        minimum_unit=optional(row["minimum_unit"]) or "seconds",
        format=optional(row["format"]) or "%0.2f",
    )
    assert result == row["expected"]
