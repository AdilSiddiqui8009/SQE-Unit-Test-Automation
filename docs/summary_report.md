# Summary Report - Assignment 3: Unit Test Automation

**Repository author:** AdilSiddiqui8009
**System under test:** humanize (Python library for human-readable numbers, sizes, dates, lists)

## 1. What was done
| Task | Status | Evidence |
|---|---|---|
| 1. Select project + setup | Done (video to be recorded - script provided) | `SETUP.md`, `docs/setup_video_script.md` |
| 2. Unit tests, 3 modules, ECP/BVA notes | Done | `docs/test_design_notes.md`, `tests_assignment/unit/` |
| 3. Excel test cases + CSV data | Done (6 test cases, 66 CSV rows) | `test_cases/Test_Cases.xlsx`, `tests_assignment/data/` |
| 4. Parallel, suites, groups, parametrization, order | Done | `pytest.ini`, `conftest.py`, `run_tests.py` |

## 2. Numbers (final run: `python run_tests.py full`)
- **309 test cases collected: 308 passed, 1 expected failure (xfail), 0 failed.**
- 243 hand-written cases + 66 CSV-driven cases.
- Modules: `number.py` (ordinal, intcomma, apnumber), `filesize.py` (naturalsize),
  `time.py` (naturaldelta, naturalday, precisedelta).
- Test methods per function (assignment asks 5-10): ordinal 10, intcomma 9, apnumber 9,
  naturalsize 10, naturaldelta 10, naturalday 7, precisedelta 9.
- Module-level tests: 8 each for number, filesize and time.
- Upstream project's own suite also passes in our environment (744 passed).

## 3. Techniques
ECP, BVA, option/decision coverage (flag parameters) and error guessing (None, inf, nan,
wrong types). Every boundary value in the tests is listed in the design notes.

## 4. Findings
1. **Suspected defect:** `ordinal(-1)` -> `-1th` (expected `-1st`); negative numbers pick the
   suffix from `value % 10`. Captured as `xfail`.
2. Low-severity usability issue: invalid `minimum_unit` raises a bare `KeyError`.
3. Setup issue: upstream computes its version from git tags, so a snapshot without git
   history cannot be pip-installed; we pinned a static version (documented in `SETUP.md`).
4. Test-tooling lesson: xdist reads `xdist_group` before `conftest` modifyitems hooks run,
   so tagging moved to `pytest_itemcollected`; verified each module is pinned to one worker.

## 5. How to verify
```bash
pip install -r requirements.txt
python run_tests.py ordered     # shows enforced group/module order
python run_tests.py parallel-modules -v   # shows one worker per module
```

## 6. Team contribution
| Member | Module(s) | Notes |
|---|---|---|
| AdilSiddiqui8009 | number, filesize, time (this repo's initial work) | see `git log` |
| (add teammate) | | |
| (add teammate) | | |

Each teammate should add their own module/tests and commit under their own Git identity so
the history shows individual activity (rubric: task distribution, 2 marks).
