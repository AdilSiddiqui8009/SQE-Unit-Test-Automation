"""Unit tests for humanize.number extended module (clamp, intword).

Member 2 (m2) contribution for Task 2.
Design basis: docs/test_design_notes.md Section 5 (ECP + BVA).
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

    # 1. BVA: Exact lower boundary (Floor)
    @pytest.mark.boundary
    @pytest.mark.case_order(10)
    def test_clamp_exact_floor_boundary(self):
        result = clamp(10, floor=10, ceil=100)
        assert result == "10"

    # 2. BVA: Just below lower boundary (Floor - epsilon)
    @pytest.mark.boundary
    def test_clamp_below_floor_boundary_returns_floor_token(self):
        result = clamp(9.99, floor=10, ceil=100)
        assert result == "<10"

    # 3. BVA: Exact upper boundary (Ceiling)
    @pytest.mark.boundary
    def test_clamp_exact_ceil_boundary(self):
        result = clamp(100, floor=10, ceil=100)
        assert result == "100"

    # 4. BVA: Just above upper boundary (Ceiling + epsilon)
    @pytest.mark.boundary
    def test_clamp_above_ceil_boundary_returns_ceil_token(self):
        result = clamp(100.01, floor=10, ceil=100)
        assert result == ">100"

    # 5. BVA: Custom boundary tokens
    @pytest.mark.boundary
    def test_clamp_custom_floor_token(self):
        result = clamp(5, floor=10, floor_token="under ")
        assert result == "under 10"

    # 6. ECP: Interior valid partition
    @pytest.mark.ecp
    def test_clamp_interior_valid_range(self):
        result = clamp(50, floor=10, ceil=100)
        assert result == "50"

    # 7. ECP: Null passthrough partition
    @pytest.mark.ecp
    def test_clamp_none_passthrough(self):
        result = clamp(None)
        assert result is None

    # 8. ECP / Negative: Invalid format type partition
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

    # 1. BVA: Below thousand boundary (999 remains unformatted plain number)
    @pytest.mark.boundary
    @pytest.mark.case_order(15)
    def test_intword_below_thousand_boundary(self):
        result = intword(999)
        assert result == "999"

    # 2. BVA: Exact thousand threshold boundary (1,000)
    @pytest.mark.boundary
    def test_intword_exact_thousand_boundary(self):
        result = intword(1_000)
        assert result == "1.0 thousand"

    # 3. BVA: Million scale transition boundary
    @pytest.mark.boundary
    def test_intword_million_scale_boundary(self):
        result = intword(1_000_000)
        assert result == "1.0 million"

    # 4. BVA: Billion scale transition boundary
    @pytest.mark.boundary
    def test_intword_billion_scale_boundary(self):
        result = intword(1_000_000_000)
        assert result == "1.0 billion"

    # 5. BVA: Trillion scale transition boundary
    @pytest.mark.boundary
    def test_intword_trillion_scale_boundary(self):
        result = intword(1_000_000_000_000)
        assert result == "1.0 trillion"

    # 6. BVA: Negative scale boundary (-1,000)
    @pytest.mark.boundary
    def test_intword_negative_thousand_boundary(self):
        result = intword(-1_000)
        assert result == "-1.0 thousand"

    # 7. ECP: Custom precision format partition
    @pytest.mark.ecp
    def test_intword_custom_float_format(self):
        result = intword(1_250_000, format="%.2f")
        assert result == "1.25 million"

    # 8. ECP / Negative: Non-numeric string fallback
    @pytest.mark.negative
    def test_intword_non_numeric_fallback(self):
        result = intword("not-a-number")
        assert result == "not-a-number"

    # 9. Suspected Defect: Premature scale transition (Code Proof for SQA Finding)
    @pytest.mark.negative
    @pytest.mark.case_order(99)
    @pytest.mark.xfail(
        reason="Suspected defect: 999,999 prematurely rounds up to '1.0 million' before reaching 1,000,000",
        strict=False,
    )
    def test_intword_below_one_million_should_not_claim_million(self):
        result = intword(999_999)
        assert "million" not in result


# ---------------------------------------------------------------------------
# Module-Level Contract Tests: number.py (extended)
# ---------------------------------------------------------------------------
@pytest.mark.module_level
class TestNumberModuleContract:
    """Module-level contract tests for extended number functions."""

    # 1. Package re-export of clamp and intword
    def test_number_package_reexports_m2_functions(self):
        assert humanize.clamp is number.clamp
        assert humanize.intword is number.intword

    # 2. Inter-function integration: clamp calling intword as a formatter
    def test_clamp_intword_inter_function_integration(self):
        result = clamp(1, format=intword, floor=1e6, floor_token="under ")
        assert result == "under 1.0 million"

    # 3. Non-finite NaN handling
    def test_number_extended_nan_handling(self):
        assert clamp(float("nan")) == "NaN"
        assert intword(float("nan")) == "NaN"

    # 4. Non-finite Inf handling
    def test_number_extended_inf_handling(self):
        assert clamp(float("inf")) == "+Inf"
        assert intword(float("inf")) == "+Inf"

    # 5. Return type contract
    def test_number_extended_return_type_contract(self):
        assert isinstance(clamp(42), str)
        assert isinstance(intword(5000), str)
