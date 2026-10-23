"""Project-wide pytest configuration (Task 4).

1. EXECUTION ORDER
   Tests run group by group, then module by module, then by an optional explicit
   per-test `@pytest.mark.case_order(n)` (lower runs first, default 50), then in
   definition order:

       group  : smoke -> datadriven -> module_level -> ecp -> boundary -> negative
       module : number -> filesize -> time -> lists

   A test with several group markers belongs to the FIRST group in the list above.
   Ordering is exact for serial runs (`-p no:xdist` or `-n0`). Under `-n N` the
   tests are *handed out* in this order, but finish concurrently.

2. PARALLEL EXECUTION (pytest-xdist)
   Every test is tagged `xdist_group(<module>)`. Use `-n auto --dist load` for
   maximum parallelism, or `-n 4 --dist loadgroup` to run the number / filesize /
   time / lists suites side by side, one worker per suite.
"""
import pytest

GROUP_ORDER = ["smoke", "datadriven", "module_level", "ecp", "boundary", "negative"]
MODULE_ORDER = ["number", "filesize", "time", "lists"]
DEFAULT_CASE_ORDER = 50


def _first_marker(item, names):
    for rank, name in enumerate(names):
        if item.get_closest_marker(name):
            return rank, name
    return len(names), "other"


def _case_order(item):
    marker = item.get_closest_marker("case_order")
    return marker.args[0] if marker and marker.args else DEFAULT_CASE_ORDER


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "case_order(n): explicit run position inside a group/module (lower first)"
    )


def pytest_itemcollected(item):
    # Must happen here, not in pytest_collection_modifyitems: pytest-xdist reads the
    # xdist_group marker in its own early modifyitems hook (for --dist loadgroup).
    _, module = _first_marker(item, MODULE_ORDER)
    item.add_marker(pytest.mark.xdist_group(name=module))


def pytest_collection_modifyitems(config, items):
    def sort_key(item):
        group_rank, _ = _first_marker(item, GROUP_ORDER)
        module_rank, _ = _first_marker(item, MODULE_ORDER)
        return (group_rank, module_rank, _case_order(item))

    items.sort(key=sort_key)  # list.sort is stable: definition order breaks ties
