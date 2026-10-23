"""Unit tests for humanize.time extended module (naturaldate).

Member 2 (m2) contribution for Task 2.
Design basis: docs/test_design_notes.md Section 6 (ECP + BVA).
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

    # 1. BVA: Exact day boundary: Today (Delta = 0)
    @pytest.mark.boundary
    @pytest.mark.case_order(10)
    def test_naturaldate_today_boundary(self, today_ref):
        result = naturaldate(today_ref)
        assert result == "today"

    # 2. BVA: Exact day boundary: Yesterday (Delta = -1)
    @pytest.mark.boundary
    def test_naturaldate_yesterday_boundary(self, today_ref):
        yesterday = today_ref - dt.timedelta(days=1)
        result = naturaldate(yesterday)
        assert result == "yesterday"

    # 3. BVA: Exact day boundary: Tomorrow (Delta = +1)
    @pytest.mark.boundary
    def test_naturaldate_tomorrow_boundary(self, today_ref):
        tomorrow = today_ref + dt.timedelta(days=1)
        result = naturaldate(tomorrow)
        assert result == "tomorrow"

    # 4. BVA: 5-month threshold: Within 150 days (no year appended)
    @pytest.mark.boundary
    def test_naturaldate_within_five_months_no_year(self, today_ref):
        target = today_ref + dt.timedelta(days=60)
        expected = target.strftime("%b %d")
        result = naturaldate(target)
        assert result == expected

    # 5. BVA: 5-month threshold: Beyond 153 days (year appended)
    @pytest.mark.boundary
    def test_naturaldate_beyond_five_months_includes_year(self, today_ref):
        target = today_ref + dt.timedelta(days=180)
        expected = target.strftime("%b %d %Y")
        result = naturaldate(target)
        assert result == expected

    # 6. ECP: Datetime object input equivalence partition
    @pytest.mark.ecp
    def test_naturaldate_accepts_datetime_object(self, today_ref):
        dt_today = dt.datetime(today_ref.year, today_ref.month, today_ref.day, 14, 30)
        result = naturaldate(dt_today)
        assert result == "today"

    # 7. ECP / Negative: Non-date string fallback partition
    @pytest.mark.negative
    def test_naturaldate_non_date_string_fallback(self):
        result = naturaldate("not-a-date")
        assert result == "not-a-date"

    # 8. ECP / Negative: None input fallback partition
    @pytest.mark.negative
    def test_naturaldate_none_fallback(self):
        result = naturaldate(None)
        assert result == "None"


# ---------------------------------------------------------------------------
# Module-Level Contract Tests: time.py (extended)
# ---------------------------------------------------------------------------
@pytest.mark.module_level
class TestTimeModuleContract:
    """Module-level contract tests for extended time functions."""

    # 1. Package re-export of naturaldate
    def test_time_package_reexports_naturaldate(self):
        assert hasattr(humanize, "naturaldate")
        assert humanize.naturaldate is htime.naturaldate

    # 2. Datetime vs Date input contract equivalence
    def test_time_datetime_vs_date_contract(self, today_ref):
        date_obj = today_ref
        datetime_obj = dt.datetime(today_ref.year, today_ref.month, today_ref.day)
        assert naturaldate(date_obj) == naturaldate(datetime_obj)

    # 3. Timezone-aware datetime handling
    def test_time_timezone_awareness_does_not_crash(self):
        aware_dt = dt.datetime.now(dt.timezone.utc)
        result = naturaldate(aware_dt)
        assert isinstance(result, str)
        assert len(result) > 0

    # 4. Return type guarantee
    def test_time_return_type_is_always_str(self, today_ref):
        samples = [today_ref, today_ref + dt.timedelta(days=10), "junk", None]
        for s in samples:
            assert isinstance(naturaldate(s), str)

    # 5. Leap year date boundary handling
    def test_time_leap_year_boundary_handling(self):
        leap_day = dt.date(2024, 2, 29)
        result = naturaldate(leap_day)
        assert isinstance(result, str)
        assert "2024" in result
