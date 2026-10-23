"""Module-level tests: public API, return-type contracts and cross-function properties.

Design basis: docs/test_design_notes.md sections 1.4, 2.1 and 3.4.
"""
import datetime as dt
import math

import pytest
from freezegun import freeze_time

import humanize
from humanize import filesize, number
from humanize import time as htime

TD = dt.timedelta


# ======================================================================== number.py
@pytest.mark.module_level
@pytest.mark.number
class TestNumberModule:
    FUNCS = (number.ordinal, number.intcomma, number.apnumber)

    @pytest.mark.smoke
    def test_package_reexports_are_the_module_functions(self):
        assert humanize.ordinal is number.ordinal
        assert humanize.intcomma is number.intcomma
        assert humanize.apnumber is number.apnumber

    def test_public_names_declared_in_package_all(self):
        # number.py has no __all__ of its own; the public API is humanize.__all__
        for name in ("ordinal", "intcomma", "apnumber", "intword"):
            assert name in humanize.__all__

    @pytest.mark.parametrize("value", [0, 7, 1234, -5, 3.5, "12", "abc", None])
    def test_every_function_returns_a_string(self, value):
        for func in self.FUNCS:
            assert isinstance(func(value), str)

    @pytest.mark.negative
    @pytest.mark.parametrize("junk", ["not a number", None, [1, 2]])
    def test_junk_in_junk_out_contract(self, junk):
        for func in self.FUNCS:
            assert func(junk) == str(junk)

    @pytest.mark.negative
    def test_nan_handled_consistently_across_functions(self):
        for func in self.FUNCS:
            assert func(math.nan) == "NaN"

    @pytest.mark.parametrize("n", [0, 1, 999, 1000, 123_456, 987_654_321, -42_000])
    def test_intcomma_round_trip_recovers_integer(self, n):
        assert int(number.intcomma(n).replace(",", "")) == n

    @pytest.mark.parametrize("n", [1, 12, 123, 1234, 12345, 123456, 1234567])
    def test_intcomma_comma_count_matches_digit_count(self, n):
        digits = len(str(n))
        assert number.intcomma(n).count(",") == (digits - 1) // 3

    def test_ordinal_keeps_the_original_number_as_prefix(self):
        for n in (5, 22, 313, 4004):
            assert number.ordinal(n).startswith(str(n))


# ====================================================================== filesize.py
@pytest.mark.module_level
@pytest.mark.filesize
class TestFilesizeModule:
    @pytest.mark.smoke
    def test_package_reexport_is_the_module_function(self):
        assert humanize.naturalsize is filesize.naturalsize

    def test_public_name_declared_in_package_all(self):
        # filesize.py has no __all__ of its own; the public API is humanize.__all__
        assert "naturalsize" in humanize.__all__

    @pytest.mark.parametrize("value", [0, 1, 1023, 1024, 10**6, -5, 1.5, "100"])
    @pytest.mark.parametrize("kwargs", [{}, {"binary": True}, {"gnu": True}])
    def test_always_returns_a_string(self, value, kwargs):
        assert isinstance(filesize.naturalsize(value, **kwargs), str)

    def test_decimal_suffix_progression_is_monotonic(self):
        expected = ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        got = [filesize.naturalsize(1000 ** i).split()[1] for i in range(1, 9)]
        assert got == expected

    def test_binary_family_always_uses_iB_and_decimal_never_does(self):
        for exp in range(1, 6):
            assert filesize.naturalsize(1024**exp, binary=True).endswith("iB")
            assert not filesize.naturalsize(1000**exp).endswith("iB")

    def test_gnu_mode_has_no_space_between_number_and_suffix(self):
        for value in (300, 3000, 10**6):
            assert " " not in filesize.naturalsize(value, gnu=True)

    @pytest.mark.parametrize("value", [500, 1500, 2_000_000])
    def test_int_and_float_inputs_give_same_result(self, value):
        assert filesize.naturalsize(value) == filesize.naturalsize(float(value))

    @pytest.mark.parametrize("value", [2, 999, 1000, 123_456, 10**9])
    def test_negative_is_mirror_of_positive(self, value):
        assert filesize.naturalsize(-value) == "-" + filesize.naturalsize(value)


# ========================================================================== time.py
@pytest.mark.module_level
@pytest.mark.time
class TestTimeModule:
    @pytest.mark.smoke
    def test_package_reexports_are_the_module_functions(self):
        assert humanize.naturaldelta is htime.naturaldelta
        assert humanize.naturalday is htime.naturalday
        assert humanize.precisedelta is htime.precisedelta

    def test_public_names_declared_in_all(self):
        for name in ("naturaldelta", "naturalday", "precisedelta", "naturaltime"):
            assert name in htime.__all__

    @pytest.mark.parametrize("seconds", [0, 1, 59, 3600, 86_400, 10**8])
    def test_delta_functions_return_strings(self, seconds):
        assert isinstance(htime.naturaldelta(seconds), str)
        assert isinstance(htime.precisedelta(TD(seconds=seconds)), str)

    @pytest.mark.parametrize("value", [TD(hours=2), TD(days=2), TD(days=10)])
    def test_naturaldelta_agrees_with_precisedelta_on_whole_units(self, value):
        assert htime.naturaldelta(value) == htime.precisedelta(value)

    @pytest.mark.parametrize("seconds", [1, 90, 7200, 172_800, 10**7])
    def test_sign_does_not_change_the_description(self, seconds):
        assert htime.naturaldelta(-seconds) == htime.naturaldelta(seconds)

    @pytest.mark.parametrize("seconds", [1, 61, 7200, 90_000, 10**7])
    def test_precisedelta_accepts_timedelta_and_seconds_equally(self, seconds):
        assert htime.precisedelta(seconds) == htime.precisedelta(TD(seconds=seconds))

    def test_unit_magnitude_never_decreases_as_duration_grows(self):
        rank = {"moment": 0, "second": 1, "minute": 2, "hour": 3,
                "day": 4, "month": 5, "year": 6}
        durations = [1, 5, 120, 7200, 2 * 86_400, 60 * 86_400, 3 * 365 * 86_400]
        ranks = [rank[htime.naturaldelta(s).split()[-1].rstrip("s")] for s in durations]
        assert ranks == sorted(ranks)

    @freeze_time("2026-06-15")
    def test_naturalday_only_special_words_within_one_day(self):
        base = dt.date(2026, 6, 15)
        words = {offset: htime.naturalday(base + TD(days=offset)) for offset in range(-3, 4)}
        assert words[-1] == "yesterday" and words[0] == "today" and words[1] == "tomorrow"
        assert all(words[o] not in ("yesterday", "today", "tomorrow") for o in (-3, -2, 2, 3))
