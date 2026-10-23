"""Unit tests for humanize.time extended module (naturaldate).

Member 2 (m2) contribution for Task 2 and Task 4.
Design basis: docs/test_design_notes.md Section 6 (ECP + BVA).
Rule: Single scenario tests placed first; parametrized data-driven tests placed at the end.
"""
import datetime as dt

import pytest

import humanize
from humanize import time as htime
from humanize.time import naturaldate

pytestmark = [pytest.mark.m2, pytest.mark.time]


# ---------------------------------------------------------------------------
# Fixture: dynamic date reference
# ---------------------------------------------------------------------------
@pytest.fixture
def today_ref():
    """Provides a fresh reference date for testing relative date calculations."""
    return dt.date.today()


# ---------------------------------------------------------------------------
# Function Tests: naturaldate
# ---------------------------------------------------------------------------
class TestNaturalDate:
    """Function-level test cases for naturaldate using BVA and ECP."""

    # 1. BVA (Single): 5-month threshold: Within 150 days (no year appended)
    @pytest.mark.boundary
    @pytest.mark.case_order(10)
    def test_naturaldate_within_five_months_no_year(self, today_ref):
        target = today_ref + dt.timedelta(days=60)
        expected = target.strftime("%b %d")
        result = naturaldate(target)
        assert result == expected

    # 2. BVA (Single): 5-month threshold: Beyond 153 days (year appended)
    @pytest.mark.boundary
    def test_naturaldate_beyond_five_months_includes_year(self, today_ref):
        target = today_ref + dt.timedelta(days=180)
        expected = target.strftime("%b %d %Y")
        result = naturaldate(target)
        assert result == expected

    # 3. ECP (Single): Datetime object input equivalence partition
    @pytest.mark.ecp
    def test_naturaldate_accepts_datetime_object(self, today_ref):
        dt_today = dt.datetime(today_ref.year, today_ref.month, today_ref.day, 14, 30)
        result = naturaldate(dt_today)
        assert result == "today"

    # 4. ECP / Negative (Single): None input fallback partition
    @pytest.mark.negative
    def test_naturaldate_none_fallback(self):
        result = naturaldate(None)
        assert result == "None"

    # 5. BVA (Parametrized at end): Relative day threshold boundaries (today, yesterday, tomorrow)
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "offset_days,expected",
        [
            (0, "today"),
            (-1, "yesterday"),
            (1, "tomorrow"),
        ],
    )
    def test_naturaldate_relative_day_thresholds(self, today_ref, offset_days, expected):
        target = today_ref + dt.timedelta(days=offset_days)
        result = naturaldate(target)
        assert result == expected

    # 6. ECP / Negative (Parametrized at end): Non-date string and invalid fallback partition
    @pytest.mark.negative
    @pytest.mark.parametrize(
        "junk",
        [
            "not-a-date",
            "2026-99-99",
            12345,
        ],
    )
    def test_naturaldate_non_date_string_fallback(self, junk):
        result = naturaldate(junk)
        assert result == str(junk)


# ---------------------------------------------------------------------------
# Module-Level Contract Tests: time.py (extended)
# ---------------------------------------------------------------------------
@pytest.mark.module_level
class TestTimeModuleContract:
    """Module-level contract tests for extended time functions."""

    # 1. Package re-export of naturaldate (Single)
    def test_time_package_reexports_naturaldate(self):
        assert hasattr(humanize, "naturaldate")
        assert humanize.naturaldate is htime.naturaldate

    # 2. Datetime vs Date input contract equivalence (Single)
    def test_time_datetime_vs_date_contract(self, today_ref):
        date_obj = today_ref
        datetime_obj = dt.datetime(today_ref.year, today_ref.month, today_ref.day)
        assert naturaldate(date_obj) == naturaldate(datetime_obj)

    # 3. Timezone-aware datetime handling (Single)
    def test_time_timezone_awareness_does_not_crash(self):
        aware_dt = dt.datetime.now(dt.timezone.utc)
        result = naturaldate(aware_dt)
        assert isinstance(result, str)
        assert len(result) > 0

    # 4. Return type guarantee (Single)
    def test_time_return_type_is_always_str(self, today_ref):
        samples = [today_ref, today_ref + dt.timedelta(days=10), "junk", None]
        for s in samples:
            assert isinstance(naturaldate(s), str)

    # 5. Leap year date boundary handling (Parametrized at end)
    @pytest.mark.parametrize(
        "year,month,day",
        [
            (2024, 2, 29),  # Leap year leap day
            (2024, 2, 28),  # Leap year day before
            (2023, 2, 28),  # Common year end of Feb
        ],
    )
    def test_time_leap_year_boundary_handling(self, year, month, day):
        test_day = dt.date(year, month, day)
        result = naturaldate(test_day)
        assert isinstance(result, str)
        assert str(year) in result
