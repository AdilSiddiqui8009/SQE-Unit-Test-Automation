"""Function-level unit tests for humanize.filesize.naturalsize.

Design basis: docs/test_design_notes.md section 2 (ECP + BVA + option coverage).
"""
import pytest

from humanize import naturalsize

pytestmark = pytest.mark.filesize


class TestNaturalsize:
    @pytest.mark.smoke
    @pytest.mark.case_order(10)
    def test_naturalsize_basic_decimal(self):
        assert naturalsize(3_000_000) == "3.0 MB"

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "value, expected",
        [(0, "0 Bytes"), (1, "1 Byte"), (2, "2 Bytes")],
    )
    def test_naturalsize_singular_plural_byte_boundary(self, value, expected):
        assert naturalsize(value) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "value, expected",
        [(999, "999 Bytes"), (1000, "1.0 kB"), (1001, "1.0 kB"),
         (999_999, "1.0 MB"), (1_000_000, "1.0 MB")],
    )
    def test_naturalsize_decimal_unit_boundaries(self, value, expected):
        assert naturalsize(value) == expected

    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "value, expected",
        [(1023, "1023 Bytes"), (1024, "1.0 KiB"), (1025, "1.0 KiB"),
         (1024**2, "1.0 MiB"), (1024**3, "1.0 GiB")],
    )
    def test_naturalsize_binary_unit_boundaries(self, value, expected):
        assert naturalsize(value, binary=True) == expected

    @pytest.mark.boundary
    def test_naturalsize_rounding_does_not_show_1000_of_smaller_unit(self):
        result = naturalsize(999_999)
        assert result == "1.0 MB"
        assert "1000.0" not in result

    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "value, expected",
        [(-1, "-1 Byte"), (-999, "-999 Bytes"), (-1000, "-1.0 kB"),
         (-4096, "-4.1 kB")],
    )
    def test_naturalsize_negative_sizes_keep_sign(self, value, expected):
        assert naturalsize(value) == expected

    @pytest.mark.ecp
    def test_naturalsize_numeric_string_and_float_inputs(self):
        assert naturalsize("2048") == "2.0 kB"
        assert naturalsize(1500.0) == "1.5 kB"

    @pytest.mark.ecp
    def test_naturalsize_huge_values_use_largest_suffix(self):
        assert naturalsize(10**30) == "1.0 QB"
        assert naturalsize(10**28) == "10.0 RB"

    @pytest.mark.ecp
    @pytest.mark.parametrize(
        "value, binary, gnu, fmt, expected",
        [(300, False, True, "%.1f", "300B"),
         (1024, False, True, "%.1f", "1.0K"),
         (3000, False, True, "%.3f", "2.930K"),
         (1536, True, False, "%.0f", "2 KiB"),
         (1024, True, True, "%.1f", "1.0K")],  # gnu overrides binary
    )
    def test_naturalsize_option_combinations(self, value, binary, gnu, fmt, expected):
        assert naturalsize(value, binary, gnu, fmt) == expected

    @pytest.mark.negative
    @pytest.mark.parametrize("bad_value, error", [("abc", ValueError), (None, TypeError)])
    def test_naturalsize_invalid_input_raises(self, bad_value, error):
        with pytest.raises(error):
            naturalsize(bad_value)
