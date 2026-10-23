"""Function-level unit tests for humanize.time (naturaldelta, naturalday, precisedelta).

Design basis: docs/test_design_notes.md section 3 (ECP + BVA + option coverage).
The clock is frozen with freezegun so naturalday results are deterministic.
"""
import datetime as dt

import pytest
from freezegun import freeze_time

from humanize import naturaldelta, naturalday, precisedelta

pytestmark = pytest.mark.time

TD = dt.timedelta
FROZEN_TODAY = "2026-06-15"


# ------------------------------------------------------------------------ naturaldelta
class TestNaturaldelta:
    @pytest.mark.smoke
    def test_naturaldelta_basic(self):
        assert naturaldelta(TD(seconds=90)) == "2 minutes"

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "seconds, expected",
        [(0, "a moment"), (0.5, "a moment"), (1, "a second"), (2, "2 seconds")],
    )
    def test_naturaldelta_moment_second_boundary(self, seconds, expected):
        assert naturaldelta(seconds) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "seconds, expected",
        [(59, "59 seconds"), (60, "a minute"), (89, "a minute"), (90, "2 minutes")],
    )
    def test_naturaldelta_seconds_to_minutes_boundary(self, seconds, expected):
        assert naturaldelta(seconds) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "seconds, expected",
        [(3540, "59 minutes"), (3599, "an hour"), (3600, "an hour"), (5400, "2 hours")],
    )
    def test_naturaldelta_minutes_to_hours_boundary(self, seconds, expected):
        assert naturaldelta(seconds) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "seconds, expected",
        [(43_200, "12 hours"), (86_399, "a day"), (86_400, "a day"), (172_800, "2 days")],
    )
    def test_naturaldelta_hours_to_days_boundary(self, seconds, expected):
        assert naturaldelta(seconds) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "days, expected",
        [(365, "a year"), (366, "1 year, 1 day"), (730, "2 years"), (1095, "3 years")],
    )
    def test_naturaldelta_year_boundaries(self, days, expected):
        assert naturaldelta(TD(days=days)) == expected

    @pytest.mark.ecp
    def test_naturaldelta_timedelta_and_seconds_are_equivalent(self):
        for seconds in (1, 59, 90, 3600, 86_400):
            assert naturaldelta(TD(seconds=seconds)) == naturaldelta(seconds)

    @pytest.mark.ecp
    def test_naturaldelta_negative_uses_absolute_value(self):
        assert naturaldelta(-60) == naturaldelta(60) == "a minute"
        assert naturaldelta(TD(days=-2)) == "2 days"

    @pytest.mark.ecp
    def test_naturaldelta_months_option(self):
        assert naturaldelta(TD(days=60)) == "2 months"
        assert naturaldelta(TD(days=45), months=False) == "45 days"

    @pytest.mark.ecp
    def test_naturaldelta_minimum_unit_milliseconds(self):
        assert naturaldelta(TD(milliseconds=500), minimum_unit="milliseconds") == "500 milliseconds"

    @pytest.mark.negative
    @pytest.mark.parametrize("junk", ["abc", None])
    def test_naturaldelta_non_numeric_returned_unchanged(self, junk):
        assert naturaldelta(junk) == str(junk)

    @pytest.mark.negative
    def test_naturaldelta_invalid_minimum_unit_raises_keyerror(self):
        with pytest.raises(KeyError):
            naturaldelta(TD(seconds=5), minimum_unit="bogus")


# ------------------------------------------------------------------------- naturalday
@freeze_time(FROZEN_TODAY)
class TestNaturalday:
    TODAY = dt.date(2026, 6, 15)

    @pytest.mark.smoke
    def test_naturalday_today(self):
        assert naturalday(self.TODAY) == "today"

    @pytest.mark.ecp
    def test_naturalday_tomorrow(self):
        assert naturalday(self.TODAY + TD(days=1)) == "tomorrow"

    @pytest.mark.ecp
    def test_naturalday_yesterday(self):
        assert naturalday(self.TODAY - TD(days=1)) == "yesterday"

    @pytest.mark.boundary
    @pytest.mark.parametrize("offset", [-2, 2])
    def test_naturalday_two_days_away_is_formatted_date(self, offset):
        value = self.TODAY + TD(days=offset)
        assert naturalday(value) == value.strftime("%b %d")

    @pytest.mark.ecp
    def test_naturalday_far_past_and_future_dates(self):
        assert naturalday(dt.date(2020, 1, 5)) == "Jan 05"
        assert naturalday(dt.date(2030, 12, 25)) == "Dec 25"

    @pytest.mark.ecp
    def test_naturalday_custom_format(self):
        assert naturalday(dt.date(2020, 1, 5), "%Y-%m-%d") == "2020-01-05"

    @pytest.mark.ecp
    def test_naturalday_datetime_input_uses_its_date(self):
        assert naturalday(dt.datetime(2026, 6, 15, 23, 59)) == "today"
        assert naturalday(dt.datetime(2026, 6, 16, 0, 1)) == "tomorrow"


# ----------------------------------------------------------------------- precisedelta
class TestPrecisedelta:
    @pytest.mark.smoke
    def test_precisedelta_basic(self):
        assert precisedelta(TD(seconds=90)) == "1 minute and 30 seconds"

    @pytest.mark.boundary
    def test_precisedelta_zero(self):
        assert precisedelta(0) == "0 seconds"

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "seconds, expected",
        [(1, "1 second"), (59, "59 seconds"), (60, "1 minute"),
         (61, "1 minute and 1 second")],
    )
    def test_precisedelta_unit_rollover(self, seconds, expected):
        assert precisedelta(TD(seconds=seconds)) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "seconds, expected",
        [(3600, "1 hour"), (86_400, "1 day"), (31_536_000, "1 year")],
    )
    def test_precisedelta_exact_unit_values(self, seconds, expected):
        assert precisedelta(TD(seconds=seconds)) == expected

    @pytest.mark.ecp
    def test_precisedelta_multiple_units(self):
        value = TD(days=2, seconds=3633, microseconds=123_000)
        assert precisedelta(value) == "2 days, 1 hour and 33.12 seconds"

    @pytest.mark.ecp
    def test_precisedelta_minimum_unit_hours(self):
        assert precisedelta(TD(seconds=3660), minimum_unit="hours") == "1.02 hours"

    @pytest.mark.ecp
    def test_precisedelta_suppress_days_moves_into_hours(self):
        assert precisedelta(TD(days=2, hours=3), suppress=["days"]) == "51 hours"

    @pytest.mark.ecp
    def test_precisedelta_custom_format(self):
        value = TD(seconds=1, microseconds=500_000)
        assert precisedelta(value, minimum_unit="seconds", format="%0.1f") == "1.5 seconds"

    @pytest.mark.ecp
    def test_precisedelta_months_and_days(self):
        assert precisedelta(TD(days=400)) == "1 year, 1 month and 4 days"
