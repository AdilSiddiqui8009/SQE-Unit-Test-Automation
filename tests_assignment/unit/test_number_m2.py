"""Unit tests for humanize.number extended module (clamp, intword).

Member 2 (m2) contribution for Task 2 and Task 4.
Design basis: docs/test_design_notes.md Section 5 (ECP + BVA).
Rule: Single scenario tests placed first; parametrized data-driven tests placed at the end.
"""
import math

import pytest

import humanize
from humanize import number
from humanize.number import clamp, intword

pytestmark = [pytest.mark.m2, pytest.mark.number]


# ---------------------------------------------------------------------------
# Function Tests: clamp
# ---------------------------------------------------------------------------
class TestClamp:
    """Function-level test cases for clamp using BVA and ECP."""

    # 1. BVA (Single): Custom floor boundary token option
    @pytest.mark.boundary
    @pytest.mark.case_order(10)
    def test_clamp_custom_floor_token(self):
        result = clamp(5, floor=10, floor_token="under ")
        assert result == "under 10"

    # 2. ECP (Single): Null passthrough partition
    @pytest.mark.ecp
    def test_clamp_none_passthrough(self):
        result = clamp(None)
        assert result is None

    # 3. ECP (Single): Interior valid partition
    @pytest.mark.ecp
    def test_clamp_interior_valid_range(self):
        result = clamp(50, floor=10, ceil=100)
        assert result == "50"

    # 4. ECP / Option (Single): Floating-point precision formatting
    @pytest.mark.ecp
    def test_clamp_float_precision_format(self):
        result = clamp(12.3456, floor=0, ceil=100, format="{:.2f}")
        assert result == "12.35"

    # 5. BVA (Parametrized at end): Boundary transitions matrix (floor, ceil, exterior)
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "val,expected",
        [
            (10, "10"),        # On lower boundary
            (9.99, "<10"),     # Below lower boundary
            (100, "100"),      # On upper boundary
            (100.01, ">100"),  # Above upper boundary
        ],
    )
    def test_clamp_boundary_matrix(self, val, expected):
        result = clamp(val, floor=10, ceil=100)
        assert result == expected

    # 6. ECP / Negative (Parametrized at end): Invalid format type raises ValueError
    @pytest.mark.negative
    @pytest.mark.parametrize("invalid_format", [123, [1, 2], {"fmt": "str"}])
    def test_clamp_invalid_format_raises_value_error(self, invalid_format):
        with pytest.raises(ValueError):
            clamp(50, format=invalid_format)


# ---------------------------------------------------------------------------
# Function Tests: intword
# ---------------------------------------------------------------------------
class TestIntword:
    """Function-level test cases for intword using BVA and ECP."""

    # 1. BVA (Single): Below thousand boundary (999 remains plain number)
    @pytest.mark.boundary
    @pytest.mark.case_order(15)
    def test_intword_below_thousand_boundary(self):
        result = intword(999)
        assert result == "999"

    # 2. BVA (Single): Negative scale boundary (-1,000)
    @pytest.mark.boundary
    def test_intword_negative_thousand_boundary(self):
        result = intword(-1_000)
        assert result == "-1.0 thousand"

    # 3. ECP (Single): Custom precision format partition
    @pytest.mark.ecp
    def test_intword_custom_float_format(self):
        result = intword(1_250_000, format="%.2f")
        assert result == "1.25 million"

    # 4. Suspected Defect (Single): Premature scale transition (Code Proof for SQA Finding)
    @pytest.mark.negative
    @pytest.mark.case_order(99)
    @pytest.mark.xfail(
        reason="Suspected defect: 999,999 prematurely rounds up to '1.0 million' before reaching 1,000,000",
        strict=False,
    )
    def test_intword_below_one_million_should_not_claim_million(self):
        result = intword(999_999)
        assert "million" not in result

    # 5. BVA (Parametrized at end): Scale transition magnitudes (thousand, million, billion, trillion)
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "val,expected_word",
        [
            (1_000, "1.0 thousand"),
            (1_000_000, "1.0 million"),
            (1_000_000_000, "1.0 billion"),
            (1_000_000_000_000, "1.0 trillion"),
        ],
    )
    def test_intword_scale_magnitudes(self, val, expected_word):
        assert intword(val) == expected_word

    # 6. ECP / Negative (Parametrized at end): Non-numeric string fallback
    @pytest.mark.negative
    @pytest.mark.parametrize("junk", ["not-a-number", "abc", None])
    def test_intword_non_numeric_fallback(self, junk):
        assert intword(junk) == str(junk)


# ---------------------------------------------------------------------------
# Module-Level Contract Tests: number.py (extended)
# ---------------------------------------------------------------------------
@pytest.mark.module_level
class TestNumberModuleContract:
    """Module-level contract tests for extended number functions."""

    # 1. Package re-export of clamp and intword (Single)
    def test_number_package_reexports_m2_functions(self):
        assert humanize.clamp is number.clamp
        assert humanize.intword is number.intword

    # 2. Inter-function integration: clamp calling intword as a formatter (Single)
    def test_clamp_intword_inter_function_integration(self):
        result = clamp(1, format=intword, floor=1e6, floor_token="under ")
        assert result == "under 1.0 million"

    # 3. Non-finite Inf handling (Single)
    def test_number_extended_inf_handling(self):
        assert clamp(float("inf")) == "+Inf"
        assert intword(float("inf")) == "+Inf"

    # 4. Return type contract (Single)
    def test_number_extended_return_type_contract(self):
        assert isinstance(clamp(42), str)
        assert isinstance(intword(5000), str)

    # 5. Non-finite NaN handling (Parametrized at end)
    @pytest.mark.parametrize("nan_val", [float("nan"), math.nan])
    def test_number_extended_nan_handling(self, nan_val):
        assert clamp(nan_val) == "NaN"
        assert intword(nan_val) == "NaN"
