# SQE Assignment 3 - Unit Test Automation (Python)

Project Phase 2: Testing and Test Automation of Unit Testing.
System under test: **[humanize](https://github.com/python-humanize/humanize)** (vendored in `humanize/`).

| Task | Deliverable | Where |
|---|---|---|
| 1 | Environment setup + setup video | `SETUP.md`, `docs/setup_video_script.md`, `docs/setup_video.mp4` |
| 2 | ECP/BVA design notes + unit tests for 3 modules | `docs/test_design_notes.md`, `tests_assignment/unit/` |
| 3 | Excel test cases + CSV-driven tests | `test_cases/Test_Cases.xlsx`, `tests_assignment/data/*.csv`, `tests_assignment/test_data_driven_csv.py` |
| 4 | Parallel / suites / groups / parametrization / order | `pytest.ini`, `conftest.py`, `run_tests.py` |
| - | Summary report | `docs/summary_report.md` |

## Team Contributors
- **Member 1: Adil Siddiqui** — Linux/macOS Environment Setup, Task 2: Number, Filesize, Time
- **Member 2: Ibadat Ali** — Windows Environment Setup & Verification, Task 2: Lists, Number Extended, Time Extended

## Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_tests.py regression                          # everything
```
Details: [SETUP.md](SETUP.md).

## Modules under test
| Module | Functions | Test file(s) |
|---|---|---|
| `humanize/number.py` | `ordinal`, `intcomma`, `apnumber` | `unit/test_number_functions.py`, `unit/test_module_level.py` |
| `humanize/filesize.py` | `naturalsize` | `unit/test_filesize_functions.py`, `unit/test_module_level.py` |
| `humanize/time.py` | `naturaldelta`, `naturalday`, `precisedelta` | `unit/test_time_functions.py`, `unit/test_module_level.py` |

## Running tests (Task 4)
`python run_tests.py <suite> [extra pytest args]`

| Suite | What runs | Equivalent pytest command |
|---|---|---|
| `smoke` | 1 fast happy-path test per function | `pytest -m smoke` |
| `regression` | everything, serial, ordered | `pytest` |
| `ecp` / `boundary` / `negative` | one test-design technique | `pytest -m boundary` |
| `datadriven` | CSV-fed tests | `pytest -m datadriven` |
| `module_level` | module-level tests | `pytest -m module_level` |
| `number` / `filesize` / `time` | one module suite | `pytest -m time` |
| `parallel` | all tests, all CPU cores | `pytest -n auto --dist load` |
| `parallel-modules` | 3 workers, one pinned per module suite | `pytest -n 3 --dist loadgroup` |
| `ordered` | serial + verbose to see the enforced order | `pytest -p no:xdist -v` |
| `full` | parallel + JUnit XML + HTML report | writes `reports/junit.xml`, `reports/report.html` |

Markers can be combined: `pytest -m "boundary and time"`, `pytest -m "number and not negative"`.

### Groups
`smoke`, `ecp`, `boundary`, `negative`, `datadriven`, `module_level` (by technique/level)
and `number`, `filesize`, `time` (by module).

### Execution order
Enforced in `conftest.py`:
1. Group: `smoke` -> `datadriven` -> `module_level` -> `ecp` -> `boundary` -> `negative`
2. Module inside a group: `number` -> `filesize` -> `time`
3. Test case inside that: optional `@pytest.mark.case_order(n)` (lower first, default 50), e.g.
   function-level smoke tests (10) run before module-level smoke tests (20); the known-defect
   `xfail` test (99) runs last in its group.

Order is exact for serial runs. Under `-n N`, tests are handed to workers in this order but
complete concurrently.

### Parameterization
`@pytest.mark.parametrize` is used throughout; the CSV files in `tests_assignment/data/`
drive 66 additional cases (one CSV row = one test case, id shown in the report).

### Regenerating the Excel sheet
```bash
pytest tests_assignment/test_data_driven_csv.py --junitxml=reports/data_driven.xml -q
python scripts/build_excel.py
```

## Known finding
`ordinal(-1)` returns `-1th` (expected `-1st`). Recorded as an `xfail` test - see
`docs/test_design_notes.md`.
