"""Unit tests for humanize.lists module (natural_list).

Member 2 (m2) contribution for Task 2.
Design basis: docs/test_design_notes.md Section 4 (ECP + BVA).
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

    # 1. BVA: Lower boundary: empty collection (length = 0)
    @pytest.mark.boundary
    @pytest.mark.case_order(10)
    def test_natural_list_empty_collection_returns_empty_string(self):
        items = []
        result = natural_list(items)
        assert result == ""

    # 2. BVA: Single item boundary (length = 1)
    @pytest.mark.boundary
    def test_natural_list_single_item_no_delimiters(self):
        items = ["apple"]
        result = natural_list(items)
        assert result == "apple"

    # 3. BVA: Two items boundary (length = 2)
    @pytest.mark.boundary
    def test_natural_list_two_items_joined_with_and(self):
        items = ["apple", "banana"]
        result = natural_list(items)
        assert result == "apple and banana"

    # 4. BVA: Three items boundary (length = 3)
    @pytest.mark.boundary
    def test_natural_list_three_items_with_comma_and_conjunction(self):
        items = ["apple", "banana", "cherry"]
        result = natural_list(items)
        assert result == "apple, banana and cherry"

    # 5. ECP: Heterogeneous partition (numeric integers stringified)
    @pytest.mark.ecp
    def test_natural_list_heterogeneous_integer_items(self):
        items = [1, 2, 3]
        result = natural_list(items)
        assert result == "1, 2 and 3"

    # 6. ECP: Collection polymorphism (tuple input partition)
    @pytest.mark.ecp
    def test_natural_list_accepts_tuple_input(self):
        items = ("first", "second")
        result = natural_list(items)
        assert result == "first and second"

    # 7. ECP / Negative: Non-iterable partition (None raises TypeError)
    @pytest.mark.negative
    def test_natural_list_none_input_raises_type_error(self):
        with pytest.raises(TypeError):
            natural_list(None)


# ---------------------------------------------------------------------------
# Module-Level Contract Tests: lists.py
# ---------------------------------------------------------------------------
@pytest.mark.module_level
class TestListsModuleContract:
    """Module-level contract tests for humanize.lists component."""

    # 1. Public API exposure
    def test_lists_module_exports_all(self):
        assert hasattr(lists, "__all__")
        assert "natural_list" in lists.__all__

    # 2. Package re-export consistency
    def test_lists_package_reexport_identity(self):
        assert humanize.natural_list is lists.natural_list

    # 3. Return type contract across varied collections
    def test_lists_return_type_is_always_str(self):
        test_inputs = [[], ["a"], ["a", "b"], [1, 2, 3]]
        for sample in test_inputs:
            assert isinstance(natural_list(sample), str)

    # 4. Immutability guarantee (caller's list is never modified in place)
    def test_lists_input_list_immutability(self):
        original = ["cherry", "apple", "banana"]
        snapshot = list(original)
        _ = natural_list(original)
        assert original == snapshot

    # 5. Generator polymorphism contract
    def test_lists_accepts_generator_expression(self):
        gen = (item.upper() for item in ["cat", "dog"])
        result = natural_list(gen)
        assert result == "CAT and DOG"
