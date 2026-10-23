"""Unit tests for humanize.lists module (natural_list).

Member 2 (m2) contribution for Task 2 and Task 4.
Design basis: docs/test_design_notes.md Section 4 (ECP + BVA).
Rule: Single scenario tests placed first; parametrized data-driven tests placed at the end.
"""
import pytest

import humanize
from humanize import lists
from humanize.lists import natural_list

pytestmark = [pytest.mark.m2, pytest.mark.lists]


# ---------------------------------------------------------------------------
# Function Tests: natural_list
# ---------------------------------------------------------------------------
class TestNaturalList:
    """Function-level test cases for natural_list using BVA and ECP."""

    # 1. BVA (Single): Lower boundary - empty collection (length = 0)
    @pytest.mark.boundary
    @pytest.mark.case_order(10)
    def test_natural_list_empty_collection_returns_empty_string(self):
        items = []
        result = natural_list(items)
        assert result == ""

    # 2. BVA (Single): Single item boundary (length = 1)
    @pytest.mark.boundary
    def test_natural_list_single_item_no_delimiters(self):
        items = ["apple"]
        result = natural_list(items)
        assert result == "apple"

    # 3. ECP (Single): Numeric integer items stringified
    @pytest.mark.ecp
    def test_natural_list_heterogeneous_integer_items(self):
        items = [1, 2, 3]
        result = natural_list(items)
        assert result == "1, 2 and 3"

    # 4. ECP (Single): Collection polymorphism with tuple input
    @pytest.mark.ecp
    def test_natural_list_accepts_tuple_input(self):
        items = ("first", "second")
        result = natural_list(items)
        assert result == "first and second"

    # 5. ECP / Negative (Single): Non-iterable input raises TypeError
    @pytest.mark.negative
    def test_natural_list_none_input_raises_type_error(self):
        with pytest.raises(TypeError):
            natural_list(None)

    # 6. BVA (Parametrized at end): Delimiter and conjunction progression (2, 3, 4 items)
    @pytest.mark.boundary
    @pytest.mark.parametrize(
        "items,expected",
        [
            (["apple", "banana"], "apple and banana"),
            (["apple", "banana", "cherry"], "apple, banana and cherry"),
            (["red", "blue", "green", "yellow"], "red, blue, green and yellow"),
            (["a", "b", "c", "d", "e"], "a, b, c, d and e"),
        ],
    )
    def test_natural_list_conjunction_progression(self, items, expected):
        assert natural_list(items) == expected


# ---------------------------------------------------------------------------
# Module-Level Contract Tests: lists.py
# ---------------------------------------------------------------------------
@pytest.mark.module_level
class TestListsModuleContract:
    """Module-level contract tests for humanize.lists component."""

    # 1. Public API exposure (Single)
    def test_lists_module_exports_all(self):
        assert hasattr(lists, "__all__")
        assert "natural_list" in lists.__all__

    # 2. Package re-export consistency (Single)
    def test_lists_package_reexport_identity(self):
        assert humanize.natural_list is lists.natural_list

    # 3. Immutability guarantee (Single: caller's list is never modified in place)
    def test_lists_input_list_immutability(self):
        original = ["cherry", "apple", "banana"]
        snapshot = list(original)
        _ = natural_list(original)
        assert original == snapshot

    # 4. Generator polymorphism contract (Single)
    def test_lists_accepts_generator_expression(self):
        gen = (item.upper() for item in ["cat", "dog"])
        result = natural_list(gen)
        assert result == "CAT and DOG"

    # 5. Return type contract across varied container types (Parametrized at end)
    @pytest.mark.parametrize(
        "container",
        [
            [],
            ["single"],
            ("a", "b"),
            {"x", "y"},
        ],
    )
    def test_lists_return_type_is_always_str(self, container):
        assert isinstance(natural_list(container), str)
