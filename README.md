# SQE Assignment 3 - Unit Test Automation (Python)

Project Phase 2: Testing and Test Automation of Unit Testing.
System under test: **[humanize](https://github.com/python-humanize/humanize)** (vendored in `humanize/`).

| Task | Deliverable | Where |
|---|---|---|
| 1 | Environment setup + setup video | `SETUP.md`, `docs/setup_video_script.md`, `docs/setup_video.mp4` |
| 2 | ECP/BVA design notes + unit tests for 3 modules | `docs/test_design_notes.md`, `tests_assignment/unit/` |
| 3 | Excel test cases + CSV-driven tests | `test_cases/Test_Cases.xlsx`, `tests_assignment/data/*.csv`, `tests_assignment/test_data_driven_csv.py`, `tests_assignment/test_data_driven_m2.py` |
| 4 | Parallel / suites / groups / parametrization / order | `pytest.ini`, `conftest.py`, `run_tests.py` |
| - | Summary report | `docs/summary_report.md` |

## Team Contributors
- **Member 1: Adil Siddiqui** — Linux/macOS Environment Setup, Task 2: Number, Filesize, Time
- **Member 2: Ibadat Ali** — Windows Environment Setup & Video Verification, Task 2: Lists, Number Extended (`clamp`, `intword`), Time Extended (`naturaldate`), Task 3: M2 External CSV Suites & Excel Sheets

## Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_tests.py regression                          # runs all tests across all modules
python run_tests.py m2                                  # runs Member 2 (Ibadat Ali) test suite
```
Details: [SETUP.md](SETUP.md).

## Modules under test
| Module | Functions Tested | Test file(s) | Contributor |
|---|---|---|---|
| `humanize/number.py` | `ordinal`, `intcomma`, `apnumber` | `unit/test_number_functions.py`, `unit/test_module_level.py` | Adil Siddiqui |
| `humanize/filesize.py` | `naturalsize` | `unit/test_filesize_functions.py`, `unit/test_module_level.py` | Adil Siddiqui |
| `humanize/time.py` | `naturaldelta`, `naturalday`, `precisedelta` | `unit/test_time_functions.py`, `unit/test_module_level.py` | Adil Siddiqui |
| `humanize/lists.py` | `natural_list` | `unit/test_lists_m2.py` | Ibadat Ali |
| `humanize/number.py` | `clamp`, `intword` | `unit/test_number_m2.py` | Ibadat Ali |
| `humanize/time.py` | `naturaldate` | `unit/test_time_m2.py` | Ibadat Ali |

## Running tests (Task 4)
`python run_tests.py <suite> [extra pytest args]`

| Suite | What runs | Equivalent pytest command |
|---|---|---|
| `smoke` | 1 fast happy-path test per function | `pytest -m smoke` |
| `regression` | everything, serial, ordered | `pytest` |
| `ecp` / `boundary` / `negative` | one test-design technique | `pytest -m boundary` |
| `datadriven` | CSV-fed tests (all members) | `pytest -m datadriven` |
| `module_level` | module-level contract tests | `pytest -m module_level` |
| `number` / `filesize` / `time` / `lists` | one module suite | `pytest -m lists` |
| `clamp` / `intword` / `naturaldate` | individual function suite | `pytest -m clamp` |
| `m2` | Member 2 (Ibadat Ali) complete suite | `pytest -m m2` |
| `parallel` | all tests, all CPU cores | `pytest -n auto --dist load` |
| `parallel-modules` | 4 workers, one pinned per module suite | `pytest -n 4 --dist loadgroup` |
| `ordered` | serial + verbose to see the enforced order | `pytest -p no:xdist -v` |
| `full` | parallel + JUnit XML + HTML report | writes `reports/junit.xml`, `reports/report.html` |

Markers can be combined: `pytest -m "boundary and lists"`, `pytest -m "m2 and not negative"`.

### Common Verification Commands
```powershell
# 1. Run Member 2 (Ibadat Ali) complete test suite (87 tests: 86 passed, 1 xfail):
python run_tests.py m2

# 2. Run Member 2 external data-driven tests (25 automated test cases):
pytest tests_assignment/test_data_driven_m2.py -v

# 3. Run Member 2 lists module suite:
python run_tests.py lists

# 4. Run parallel execution across all 4 module suites (one worker per module):
python run_tests.py parallel-modules

# 5. Run the entire repository regression suite (396 test cases: 394 passed, 2 xfailed):
python run_tests.py regression
```

### Groups
`smoke`, `ecp`, `boundary`, `negative`, `datadriven`, `module_level` (by technique/level)
and `number`, `filesize`, `time`, `lists`, `m2` (by module / author).

### Execution order
Enforced in `conftest.py`:
1. Group: `smoke` -> `datadriven` -> `module_level` -> `ecp` -> `boundary` -> `negative`
2. Module inside a group: `number` -> `filesize` -> `time` -> `lists`
3. Test case inside that: optional `@pytest.mark.case_order(n)` (lower first, default 50), e.g.
   function-level smoke tests (10) run before module-level smoke tests (20); known-defect
   `xfail` tests (99) run last in their group.

Order is exact for serial runs. Under `-n N`, tests are handed to workers in this order but
complete concurrently.

### Parameterization
`@pytest.mark.parametrize` is used throughout:
* Member 1 CSV files in `tests_assignment/data/` drive 66 cases (`TC-DD-001` ... `TC-DD-006`).
* Member 2 CSV files in `tests_assignment/data/` drive 25 cases (`TC-M2-01` ... `TC-M2-04`).

### Regenerating the Excel sheet
```bash
# Member 1 test cases:
pytest tests_assignment/test_data_driven_csv.py --junitxml=reports/data_driven.xml -q
python scripts/build_excel.py

# Member 2 test cases:
python scripts/add_m2_to_excel.py
```

## Known findings
1. `ordinal(-1)` returns `-1th` (expected `-1st`). Recorded as an `xfail` test (Adil Siddiqui) - see `docs/test_design_notes.md`.
2. `intword(999_999)` returns `"1.0 million"` (premature scale transition before reaching 1,000,000). Recorded as an `xfail` test (Ibadat Ali) - see `docs/test_design_notes.md`.
