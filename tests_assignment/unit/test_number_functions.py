"""Function-level unit tests for humanize.number (ordinal, intcomma, apnumber).

Design basis: docs/test_design_notes.md section 1 (ECP + BVA + error guessing).
"""
import math

import pytest

from humanize import apnumber, intcomma, ordinal

pytestmark = pytest.mark.number


# --------------------------------------------------------------------------- ordinal
class TestOrdinal:
    @pytest.mark.smoke
    @pytest.mark.case_order(10)
    def test_ordinal_basic_first_second_third(self):
        assert [ordinal(n) for n in (1, 2, 3)] == ["1st", "2nd", "3rd"]

    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "value, expected",
        [(1, "1st"), (21, "21st"), (101, "101st"), (1001, "1001st"),
         (2, "2nd"), (22, "22nd"), (3, "3rd"), (23, "23rd"),
         (0, "0th"), (4, "4th"), (9, "9th"), (10, "10th")],
    )
    def test_ordinal_equivalence_classes_by_last_digit(self, value, expected):
        assert ordinal(value) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "value, expected",
        [(10, "10th"), (11, "11th"), (12, "12th"), (13, "13th"), (14, "14th")],
    )
    def test_ordinal_teen_band_boundaries(self, value, expected):
        assert ordinal(value) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize("value", [111, 112, 113, 211, 912])
    def test_ordinal_hundreds_teens_use_th(self, value):
        assert ordinal(value) == f"{value}th"

    @pytest.mark.ecp
    def test_ordinal_numeric_string_input(self):
        assert ordinal("7") == "7th"
        assert ordinal("22") == "22nd"

    @pytest.mark.ecp
    def test_ordinal_float_is_truncated(self):
        assert ordinal(7.9) == "7th"
        assert ordinal(1.2) == "1st"

    @pytest.mark.negative
    @pytest.mark.parametrize("junk", ["abc", None, [1], {}, ""])
    def test_ordinal_non_numeric_returns_str_of_input(self, junk):
        assert ordinal(junk) == str(junk)

    @pytest.mark.negative
    def test_ordinal_non_finite_values(self):
        assert ordinal(math.inf) == "+Inf"
        assert ordinal(math.nan) == "NaN"

    @pytest.mark.ecp
    def test_ordinal_gender_option_english_is_same(self):
        assert ordinal(1, "female") == ordinal(1, "male") == "1st"
        assert ordinal(1, gender="unknown") == "1st"

    @pytest.mark.negative
    @pytest.mark.case_order(99)
    @pytest.mark.xfail(reason="Suspected defect: negative numbers get 'th' (-1 -> '-1th')",
                       strict=False)
    def test_ordinal_negative_one_should_be_1st(self):
        assert ordinal(-1) == "-1st"


# ------------------------------------------------------------------------- intcomma
class TestIntcomma:
    @pytest.mark.smoke
    @pytest.mark.case_order(10)
    def test_intcomma_basic(self):
        assert intcomma(1234567) == "1,234,567"

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "value, expected",
        [(0, "0"), (1, "1"), (999, "999"), (1000, "1,000"), (1001, "1,001")],
    )
    def test_intcomma_three_to_four_digit_boundary(self, value, expected):
        assert intcomma(value) == expected

    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "value, expected",
        [(-1, "-1"), (-999, "-999"), (-1000, "-1,000"), (-1234567, "-1,234,567")],
    )
    def test_intcomma_negative_numbers(self, value, expected):
        assert intcomma(value) == expected

    @pytest.mark.ecp
    def test_intcomma_large_integers_group_every_three_digits(self):
        assert intcomma(10**9) == "1,000,000,000"
        assert intcomma(10**15) == "1,000,000,000,000,000"

    @pytest.mark.ecp
    def test_intcomma_float_keeps_fraction(self):
        assert intcomma(1234.5) == "1,234.5"
        assert intcomma(1_234_567.25) == "1,234,567.25"

    @pytest.mark.ecp
    def test_intcomma_numeric_strings(self):
        assert intcomma("1000") == "1,000"
        assert intcomma("1,000") == "1,000"

    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "value, ndigits, expected",
        [(1234.5678, 2, "1,234.57"), (1000, 0, "1,000"), (14308.40, 1, "14,308.4"),
         (0.5, 3, "0.500")],
    )
    def test_intcomma_ndigits_rounding(self, value, ndigits, expected):
        assert intcomma(value, ndigits) == expected

    @pytest.mark.negative
    @pytest.mark.parametrize("junk", ["abc", None, [], "12abc"])
    def test_intcomma_non_numeric_returns_str_of_input(self, junk):
        assert intcomma(junk) == str(junk)

    @pytest.mark.negative
    def test_intcomma_infinity(self):
        assert intcomma(math.inf) == "+Inf"
        assert intcomma(-math.inf) == "-Inf"


# -------------------------------------------------------------------------- apnumber
class TestApnumber:
    @pytest.mark.smoke
    @pytest.mark.case_order(10)
    def test_apnumber_basic(self):
        assert apnumber(1) == "one"

    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "value, word",
        list(enumerate(["zero", "one", "two", "three", "four",
                        "five", "six", "seven", "eight", "nine"])),
    )
    def test_apnumber_spells_out_zero_to_nine(self, value, word):
        assert apnumber(value) == word

    @pytest.mark.boundary
    def test_apnumber_upper_boundary_nine_vs_ten(self):
        assert apnumber(9) == "nine"
        assert apnumber(10) == "10"

    @pytest.mark.boundary
    def test_apnumber_lower_boundary_zero_vs_minus_one(self):
        assert apnumber(0) == "zero"
        assert apnumber(-1) == "-1"

    @pytest.mark.ecp
    def test_apnumber_large_numbers_stay_digits(self):
        assert apnumber(100) == "100"
        assert apnumber(1_000_000) == "1000000"

    @pytest.mark.ecp
    def test_apnumber_numeric_string(self):
        assert apnumber("3") == "three"
        assert apnumber("10") == "10"

    @pytest.mark.ecp
    def test_apnumber_float_is_truncated(self):
        assert apnumber(9.5) == "nine"
        assert apnumber(0.9) == "zero"

    @pytest.mark.negative
    @pytest.mark.parametrize("junk", ["abc", None, [], ""])
    def test_apnumber_non_numeric_returns_str_of_input(self, junk):
        assert apnumber(junk) == str(junk)

    @pytest.mark.negative
    def test_apnumber_nan(self):
        assert apnumber(math.nan) == "NaN"
