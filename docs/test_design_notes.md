# Test Design Notes (Task 2) - ECP and BVA

**System under test:** `humanize` (vendored in `humanize/`).
**Author:** AdilSiddiqui8009 (add your group members' sections below in the same format).

Techniques applied: **Equivalence Class Partitioning (ECP)**, **Boundary Value Analysis (BVA)**,
plus **error guessing** (odd types, `None`, `inf`, `nan`) and **decision/option coverage** for
flag parameters (`binary`, `gnu`, `format`, `months`, `minimum_unit`).

Expected values below were confirmed by running the real functions first (exploratory
probing), then frozen into automated tests.

---------------------------------------------------------------------------------------

## Module 1 - `humanize/number.py`

Functions under test: `ordinal`, `intcomma`, `apnumber`.

### 1.1 `ordinal(value, gender="male")`
Rule: suffix is `st/nd/rd/th` by last digit, except 11/12/13 (and 111/112/113...) -> `th`.

| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| ECP | ends in 1 (not 11) | 1 -> `1st`, 21 -> `21st`, 101 -> `101st` |
| ECP | ends in 2 (not 12) | 2 -> `2nd`, 22 -> `22nd` |
| ECP | ends in 3 (not 13) | 3 -> `3rd`, 23 -> `23rd` |
| ECP | ends in 0, 4-9 | 0 -> `0th`, 4 -> `4th`, 10 -> `10th` |
| BVA | teen exceptions (the "11-13" band) | 10 -> `10th`, 11 -> `11th`, 12 -> `12th`, 13 -> `13th`, 14 -> `14th` |
| BVA | hundreds teens | 111 -> `111th`, 112 -> `112th`, 113 -> `113th` |
| ECP | numeric string / float | "7" -> `7th`, 7.9 -> `7th` (truncated) |
| ECP (invalid) | non-numeric | "abc" -> `abc`, None -> `None`, [1] -> `[1]` |
| Error guessing | non-finite | inf -> `+Inf`, nan -> `NaN` |
| Option coverage | gender param | "female" and unknown gender both give `1st` in English |
| Suspected defect | negative numbers | -1 -> `-1th` (expected `-1st`) - documented with `xfail` |

### 1.2 `intcomma(value, ndigits=None)`
| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | 3-digit vs 4-digit boundary | 999 -> `999`, 1000 -> `1,000`, 0 -> `0` |
| ECP | negative | -1000 -> `-1,000` |
| ECP | large int | 1234567 -> `1,234,567` |
| ECP | float | 1234.5 -> `1,234.5` |
| ECP | numeric strings | "1000" -> `1,000`, "1,000" -> `1,000` |
| ECP (invalid) | non-numeric | "abc" -> `abc`, None -> `None` |
| Error guessing | inf | inf -> `+Inf` |
| Option coverage | `ndigits` | (1234.5678, 2) -> `1,234.57`; (1000, 0) -> `1,000` |

### 1.3 `apnumber(value)` (AP style: spell out 0-9)
| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | lower boundary | 0 -> `zero`, -1 -> `-1` |
| BVA | upper boundary | 9 -> `nine`, 10 -> `10` |
| ECP | inside range | 1 -> `one`, 5 -> `five` |
| ECP | numeric string | "3" -> `three` |
| ECP | float inside range | 9.5 -> `nine` (truncated) |
| ECP (invalid) | non-numeric | "abc" -> `abc`, None -> `None` |
| Error guessing | nan | nan -> `NaN` |

### 1.4 Module-level tests (number.py)
Public API exposure (`__all__`/package imports), every function returns `str`,
"junk in -> junk out" contract shared by all functions, function composition
(`intcomma(int(...))` round-trip), and non-finite handling consistency.

---------------------------------------------------------------------------------------

## Module 2 - `humanize/filesize.py`

Function under test: `naturalsize(value, binary=False, gnu=False, format="%.1f")`.

| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | singular/plural byte | 0 -> `0 Bytes`, 1 -> `1 Byte`, 2 -> `2 Bytes` |
| BVA | decimal unit boundary (base 1000) | 999 -> `999 Bytes`, 1000 -> `1.0 kB`, 1001 -> `1.0 kB` |
| BVA | binary unit boundary (base 1024) | 1023 -> `1023 Bytes`, 1024 -> `1.0 KiB`, 1048576 -> `1.0 MiB` |
| BVA | rounding carry-over | 999999 -> `1.0 MB` (not `1000.0 kB`) |
| ECP | negative sizes | -1 -> `-1 Byte`, -1000 -> `-1.0 kB` |
| ECP | numeric string | "2048" -> `2.0 kB` |
| ECP | huge values | 1e30 -> `1.0 QB` (largest suffix) |
| Option coverage | `gnu=True` | 300 -> `300B`, 1024 -> `1.0K`; `gnu` overrides `binary` |
| Option coverage | `format` | (3000, gnu, "%.3f") -> `2.930K`; (1536, binary, "%.0f") -> `2 KiB` |
| ECP (invalid) | non-numeric | "abc" -> `ValueError`, None -> `TypeError` |

### 2.1 Module-level tests (filesize.py)
Public export, always returns `str`, monotonic suffix growth, decimal vs binary
suffix families never mixed, GNU mode has no space, results independent of int vs float input.

---------------------------------------------------------------------------------------

## Module 3 - `humanize/time.py`

Functions under test: `naturaldelta`, `naturalday`, `precisedelta`.

### 3.1 `naturaldelta(value, months=True, minimum_unit="seconds")`
| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | "a moment" / "a second" boundary | 0 -> `a moment`, 0.5 -> `a moment`, 1 -> `a second` |
| BVA | seconds / minutes boundary | 59 -> `59 seconds`, 60 -> `a minute`, 89 -> `a minute`, 90 -> `2 minutes` |
| BVA | minutes / hours boundary | 3540 -> `59 minutes`, 3599 -> `an hour`, 3600 -> `an hour` |
| BVA | hours / days boundary | 43200 -> `12 hours`, 86399 -> `a day`, 172800 -> `2 days` |
| BVA | months / years | 365 days -> `a year`, 366 days -> `1 year, 1 day`, 730 days -> `2 years` |
| ECP | timedelta vs numeric input | `timedelta(seconds=1)` and `1` -> `a second` |
| ECP | negative (abs value used) | -60 -> `a minute` |
| ECP (invalid) | non-numeric | "abc" -> `abc`, None -> `None` |
| Option coverage | `months=False` | 45 days -> `45 days` |
| Option coverage | `minimum_unit` | 0.5 s with `milliseconds` -> `500 milliseconds`; bogus unit -> `KeyError` |

### 3.2 `naturalday(value, format="%b %d")` (clock frozen with `freezegun`)
| Technique | Class | Input -> Expected |
|---|---|---|
| ECP | today / tomorrow / yesterday | -> `today`, `tomorrow`, `yesterday` |
| BVA | +-2 days from today (first non-special day) | -> formatted date |
| ECP | far past / far future | -> `Jan 05` style |
| Option coverage | custom `format` | `%Y-%m-%d` -> `2020-01-05` |
| ECP | `datetime` input | datetime treated like its date |

### 3.3 `precisedelta(value, minimum_unit="seconds", suppress=(), format="%0.2f")`
| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | zero | 0 -> `0 seconds` |
| BVA | unit rollovers | 59 s -> `59 seconds`, 60 s -> `1 minute`, 61 s -> `1 minute and 1 second` |
| ECP | multi-unit | 2d 1h 33.12s -> `2 days, 1 hour and 33.12 seconds` |
| BVA | exact units | 3600 -> `1 hour`, 86400 -> `1 day` |
| Option coverage | `minimum_unit="hours"` | 3660 s -> `1.02 hours` |
| Option coverage | `suppress=["days"]` | 2d 3h -> `51 hours` |
| Option coverage | `format` | 1.5 s with `%0.1f` -> `1.5 seconds` |

### 3.4 Module-level tests (time.py)
Public exports, string return type, `naturaldelta` agrees with `precisedelta` on whole
units, sign-insensitivity, timedelta/seconds equivalence, monotonic ordering of magnitudes.

---------------------------------------------------------------------------------------

## Test groups (used by Task 4)
| Marker | Meaning |
|---|---|
| `smoke` | one fast happy-path test per function |
| `ecp` | equivalence-class tests |
| `boundary` | BVA tests |
| `negative` | invalid input / error-guessing tests |
| `datadriven` | tests fed from CSV files (Task 3) |
| `number`, `filesize`, `time` | module suites |
| `module_level` | module/class-level tests |

## Observations / possible defects found during design
1. `ordinal(-1)` returns `-1th` - negative numbers use the wrong suffix (suffix chosen from
   `value % 10` on a negative number). Captured as an `xfail` test so the suite stays green
   but the finding is on record.
2. `naturaldelta(3599)` -> `an hour`: rounding up is by design (nearest unit), noted so
   the boundary tests encode intended behaviour, not a bug.
3. Invalid `minimum_unit` raises a bare `KeyError('BOGUS')` rather than a descriptive
   `ValueError` - low severity usability issue.
