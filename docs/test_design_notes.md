# Test Design Notes (Task 2) - ECP and BVA

**System under test:** `humanize` (vendored in `humanize/`).
**Authors:** Adil Siddiqui (Member 1) & Ibadat Ali (Member 2 / m2).

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
Public API exposure (`humanize.__all__` and package re-exports; `number.py`/`filesize.py` define no `__all__` of their own), every function returns `str`,
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

## Module 4 - `humanize/lists.py` (Member 2: Ibadat Ali)

Function under test: `natural_list(items)`.

### 4.1 `natural_list(items)`
Rule: converts an iterable into a natural language list with commas and 'and'. Empty iterable returns `""`, single item returns the stringified item, two items separated by `' and '`, three or more separated by `', '` and `' and '`.

| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | empty collection (len = 0) | `[]` -> `""` |
| BVA | single item (len = 1) | `["apple"]` -> `"apple"` |
| BVA | two items (len = 2) | `["apple", "banana"]` -> `"apple and banana"` |
| BVA | three items (len = 3) | `["apple", "banana", "cherry"]` -> `"apple, banana and cherry"` |
| ECP | heterogeneous iterable / stringification | `[1, 2, 3]` -> `"1, 2 and 3"` |
| ECP | tuple polymorphism | `("x", "y")` -> `"x and y"` |
| ECP (invalid) | non-iterable (None) | `None` -> raises `TypeError` |

### 4.2 Module-level contract tests (lists.py)
Public API exposure (`__all__ = ["natural_list"]`), top-level package re-export (`humanize.natural_list is humanize.lists.natural_list`), string return type guarantee across inputs, caller input immutability (passing list does not mutate it), and generator comprehension support.

---------------------------------------------------------------------------------------

## Module 5 - `humanize/number.py` (Extended - Member 2: Ibadat Ali)

Functions under test: `clamp`, `intword`.

### 5.1 `clamp(value, format="{:}", floor=None, ceil=None, floor_token="<", ceil_token=">")`
Rule: clamps value between floor and ceil. If below floor, returns `floor_token + formatted floor`. If above ceil, returns `ceil_token + formatted ceil`. If inside, returns formatted value.

| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | exact lower boundary (Floor) | `clamp(10, floor=10, ceil=100)` -> `"10"` |
| BVA | just below lower boundary (Floor - ε) | `clamp(9.99, floor=10, ceil=100)` -> `"<10"` |
| BVA | exact upper boundary (Ceiling) | `clamp(100, floor=10, ceil=100)` -> `"100"` |
| BVA | just above upper boundary (Ceiling + ε) | `clamp(100.01, floor=10, ceil=100)` -> `">100"` |
| BVA | custom boundary tokens | `clamp(5, floor=10, floor_token="under ")` -> `"under 10"` |
| ECP | interior valid partition | `clamp(50, floor=10, ceil=100)` -> `"50"` |
| ECP | None passthrough | `clamp(None)` -> `None` |
| ECP (invalid) | invalid format parameter | `clamp(50, format=123)` -> raises `ValueError` |

### 5.2 `intword(value, format="%.1f")`
Rule: converts large integers into friendly text (starting at 1,000 thousand up to googol).

| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | below thousand boundary | 999 -> `"999"` |
| BVA | exact thousand boundary | 1_000 -> `"1.0 thousand"` |
| BVA | million scale transition | 1_000_000 -> `"1.0 million"` |
| BVA | billion scale transition | 1_000_000_000 -> `"1.0 billion"` |
| BVA | trillion scale transition | 1_000_000_000_000 -> `"1.0 trillion"` |
| BVA | negative scale boundary | -1_000 -> `"-1.0 thousand"` |
| ECP | interior fractional partition | (1_250_000, "%.2f") -> `"1.25 million"` |
| ECP (invalid) | non-numeric string fallback | `"not-a-number"` -> `"not-a-number"` |

### 5.3 Module-level contract tests (number.py - extended)
Package re-export of `clamp` and `intword` at top-level `humanize`, inter-function integration (`clamp(1, format=intword, floor=1e6)` -> `"under 1.0 million"`), non-finite handling (`nan`, `inf`), and string return-type guarantees.

---------------------------------------------------------------------------------------

## Module 6 - `humanize/time.py` (Extended - Member 2: Ibadat Ali)

Function under test: `naturaldate(value)`.

### 6.1 `naturaldate(value)`
Rule: returns natural relative day within 152 days (`today`, `yesterday`, `tomorrow`, or `%b %d`), and appends year `%b %d %Y` beyond 153 days (~5 months).

| Technique | Class / boundary | Input -> Expected |
|---|---|---|
| BVA | exact day boundary: Today (Δ = 0) | `today` -> `"today"` |
| BVA | exact day boundary: Yesterday (Δ = -1) | `today - 1 day` -> `"yesterday"` |
| BVA | exact day boundary: Tomorrow (Δ = +1) | `today + 1 day` -> `"tomorrow"` |
| BVA | 5-month threshold: within 150 days | `today + 60 days` -> formatted `%b %d` (no year) |
| BVA | 5-month threshold: beyond 153 days | `today + 180 days` -> formatted `%b %d %Y` (with year) |
| ECP | datetime vs date input equivalence | `datetime(today.year, today.month, today.day)` -> `"today"` |
| ECP (invalid) | non-date input fallback | `"not-a-date"` -> `"not-a-date"`, `None` -> `"None"` |

### 6.2 Module-level contract tests (time.py - extended)
Top-level re-export of `naturaldate`, datetime vs date contract consistency, timezone-aware datetime handling, return-type guarantee (`str`), and leap-year boundary handling.

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
| `m2` | test suite authored by Member 2 (Ibadat Ali) |
| `lists` | tests for humanize.lists module |
| `clamp` | tests for number.clamp function |
| `intword` | tests for number.intword function |
| `naturaldate` | tests for time.naturaldate function |

## Observations / possible defects found during design
1. `ordinal(-1)` returns `-1th` - negative numbers use the wrong suffix (suffix chosen from
   `value % 10` on a negative number). Captured as an `xfail` test so the suite stays green
   but the finding is on record.
2. `naturaldelta(3599)` -> `an hour`: rounding up is by design (nearest unit), noted so
   the boundary tests encode intended behaviour, not a bug.
3. Invalid `minimum_unit` raises a bare `KeyError('BOGUS')` rather than a descriptive
   `ValueError` - low severity usability issue.
4. `intword(999_999)` returns `'1.0 million'` - with format `'%.1f'`, 999,999 prematurely
   rounds up and claims to be a million before reaching 1,000,000. Captured as an `xfail`
   test so the finding is on record with code proof.
