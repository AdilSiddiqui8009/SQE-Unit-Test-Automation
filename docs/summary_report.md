# Summary Report - Assignment 3: Unit Test Automation

**System under test:** [humanize](https://github.com/python-humanize/humanize) (Python library for human-readable numbers, sizes, dates, lists)  
**Team Contributors:**
- **Member 1:** Adil Siddiqui (`AdilSiddiqui8009`)
- **Member 2:** Ibadat Ali (`i.k.jamlera820@gmail.com`)

---

## 1. What was done
| Task | Status | Evidence |
|---|---|---|
| 1. Select project + setup | Done (cross-platform Linux/macOS + Windows native verified; setup video recorded) | `SETUP.md`, `docs/setup_video.mp4`, `docs/setup_video_script.md` |
| 2. Unit tests, 3 modules per member, ECP/BVA notes | Done (6 modules / extended sub-modules total) | `docs/test_design_notes.md`, `tests_assignment/unit/` |
| 3. Excel test cases + CSV external data | Done (10 total test cases, 91 CSV rows executed across M1 and M2) | `test_cases/Test_Cases.xlsx`, `tests_assignment/data/*.csv`, `tests_assignment/test_data_driven_csv.py`, `tests_assignment/test_data_driven_m2.py` |
| 4. Parallel, suites, groups, parametrization, order | Done (multi-core xdist, loadgroup per module, explicit marker ordering) | `pytest.ini`, `conftest.py`, `run_tests.py` |

---

## 2. Test Execution Numbers (Final Regression Run: `pytest`)
- **Total test cases collected:** **383 test cases**
- **Test results:** **381 passed, 2 expected failures (`xfail`), 0 failed, 0 errors.**
- **Member breakdown:**
  * **Member 1 (Adil Siddiqui):** 309 cases (243 unit + 66 CSV data-driven) $\rightarrow$ 308 passed, 1 `xfail`.
  * **Member 2 (Ibadat Ali):** 74 cases (49 unit + 25 CSV data-driven) $\rightarrow$ 73 passed, 1 `xfail`.
- **Functions tested per person (Assignment asks 5–10 tests per function):**
  * *Member 1:* `ordinal` (10), `intcomma` (9), `apnumber` (9), `naturalsize` (10), `naturaldelta` (10), `naturalday` (7), `precisedelta` (9).
  * *Member 2:* `natural_list` (7), `clamp` (11), `intword` (9), `naturaldate` (8).
- **Module-level contract tests:**
  * *Member 1:* 8 tests each for `number`, `filesize`, `time`.
  * *Member 2:* 5 tests each for `lists`, `number` extended, `time` extended.
- **Upstream regression:** Upstream `humanize` test suite executes cleanly in the local environment (744 passed).

---

## 3. Test Design Techniques Applied
1. **Equivalence Class Partitioning (ECP):** Partitioning valid interior inputs, negative domains, edge collections, and distinct data types.
2. **Boundary Value Analysis (BVA):** Testing exact on-boundary ($B$), immediately below ($B - 1$), and immediately above ($B + 1$) transitions for numerical thresholds, list lengths, and date deltas.
3. **Option / Decision Coverage:** Verifying optional parameters, formatting strings, and custom boundary tokens.
4. **Negative Testing / Error Guessing:** Verifying robust handling of `None`, non-numeric strings, NaN, Infinity, and invalid types.
5. **External Data-Driven Testing:** Separating test logic from test data using external CSV files and dynamic Pytest parameterization.

All boundaries, equivalence partitions, and rationale are documented in [`docs/test_design_notes.md`](test_design_notes.md).

---

## 4. SQA Findings & Defect Analysis

### Finding 1 (Suspected Defect - Member 1): `ordinal(-1)`
* **Module:** `humanize.number`
* **Behavior:** `ordinal(-1)` returns `"-1th"` instead of `"-1st"`.
* **Root Cause:** Negative numbers compute their suffix via `value % 10`, yielding `9` in Python (`-1 % 10 == 9`), which mistakenly assigns `"th"`.
* **Classification:** Defect captured with `@pytest.mark.xfail` in `test_number_functions.py::TestOrdinal::test_ordinal_negative_one_should_be_1st`.

### Finding 2 (Suspected Defect - Member 2): `intword(999_999)` Premature Scale Rollover
* **Module:** `humanize.number`
* **Behavior:** `intword(999_999)` returns `"1.0 million"`.
* **Root Cause:** `intword` divides by `1,000,000` (`0.999999`) and formats with `%.1f`. The string formatter rounds `0.999999` up to `1.0`, prematurely applying the "million" suffix before the boundary of 1,000,000 is reached.
* **Classification:** Defect captured with `@pytest.mark.xfail` in `test_number_m2.py::TestIntword::test_intword_below_one_million_should_not_claim_million`.

### Finding 3 (API Contract Observation - Member 2): `clamp` String Exception Type
* **Module:** `humanize.number`
* **Behavior:** Calling `clamp("invalid", floor=0, ceil=10)` raises `ValueError` rather than `TypeError`.
* **Root Cause:** The function attempts `int(value)` or `float(value)` internally instead of checking `isinstance(value, (int, float))`.
* **Classification:** Handled and verified in `test_number_m2.py::TestClamp::test_clamp_invalid_format_raises_value_error`.

### Finding 4 (Threshold Precision Observation - Member 2): `naturaldate` Leap Year Window
* **Module:** `humanize.time`
* **Behavior:** `naturaldate` transitions from relative days (`"yesterday"`, `"tomorrow"`) to month-day format (`"Apr 10"`) and finally to year format (`"Jan 01 2025"`) using a fixed threshold of `365.25 / 2.4` ($\approx 152.19$ days).
* **Classification:** Documented and verified across leap years in `test_time_m2.py::TestNaturalDate`.

### Finding 5 (Usability Issue - Shared): Unhandled `minimum_unit`
* **Module:** `humanize.time`
* **Behavior:** Passing an invalid unit string to `naturaldelta` raises an unhandled `KeyError` instead of a user-friendly `ValueError`.

---

## 5. How to Verify All Test Suites
From the repository root with virtual environment activated:

```powershell
# 1. Run Member 2 (Ibadat Ali) test suite (74 tests: 73 passed, 1 xfail):
python run_tests.py m2

# 2. Run Member 2 lists module suite:
python run_tests.py lists

# 3. Run Member 1 suites:
python run_tests.py number
python run_tests.py filesize
python run_tests.py time

# 4. Run multi-core parallel execution across 4 module workers:
python run_tests.py parallel-modules

# 5. Run full regression suite with HTML and JUnit report generation:
python run_tests.py full
```

Generated reports are stored in `reports/`:
* HTML Report: `reports/report.html`
* JUnit XML: `reports/junit.xml`

---

## 6. Team Contribution Matrix

| Member | Allocated Modules | Individual Deliverables & Evidence |
|---|---|---|
| **Member 1: Adil Siddiqui** (`AdilSiddiqui8009`) | `number.py`, `filesize.py`, `time.py` | • Linux/macOS setup documentation.<br>• 7 functions tested (67 unit tests).<br>• Module contract tests for 3 modules (24 tests).<br>• 6 CSV datasets in `tests_assignment/data/` (66 rows).<br>• `test_data_driven_csv.py` test runner.<br>• Base `Test_Cases.xlsx` (Sheets: Test Cases, Test Data, Summary).<br>• Found Defect 1 (`ordinal(-1)`). |
| **Member 2: Ibadat Ali** (`i.k.jamlera820@gmail.com`) | `lists.py`, `number.py` (extended), `time.py` (extended) | • Native Windows 10/11 PowerShell environment verification.<br>• Recorded setup demonstration video (`docs/setup_video.mp4`, 16.6 MB).<br>• 4 functions tested: `natural_list`, `clamp`, `intword`, `naturaldate` (34 unit tests).<br>• Module contract tests for `lists`, `number`, `time` (15 tests).<br>• 4 CSV datasets in `tests_assignment/data/` (25 rows).<br>• `tests_assignment/test_data_driven_m2.py` test runner.<br>• Excel workbook updates (`M2_TestCases`, `M2_TestData`, `M2_Summary`).<br>• Added M2 markers, module ordering (`lists`), and suites in `run_tests.py`.<br>• Found Defect 2 (`intword(999_999)` premature rollover). |

All contributions are tracked via distinct Git commit history on branch `test/m2-unit-tests`.
