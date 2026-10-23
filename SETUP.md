# Task 1 - Local Development Environment Setup

**Project under test:** [humanize](https://github.com/python-humanize/humanize) - a Python
library that turns numbers, sizes, dates and lists into human-readable text
(`naturalsize(3000000) -> '3.0 MB'`, `ordinal(3) -> '3rd'`, ...).

Why this project: pure Python, no external services, small and well-defined public API,
deterministic outputs -> ideal for unit testing with ECP/BVA.

## Prerequisites
- Python 3.11+ (tested with 3.13)
- git

## Steps
```bash
# 1. Clone the group repository
git clone https://github.com/AdilSiddiqui8009/sqe-assignment-3-unit-test-automation.git
cd sqe-assignment-3-unit-test-automation

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# 3. Install the project (editable) and all test tooling
pip install -r requirements.txt

# 4. Smoke test - upstream project's own tests must pass
pytest humanize/tests -q
```

Expected result of step 4: `744 passed, 134 skipped` (skips are locale tests that
need compiled translations on some platforms).

## Verify the install
```bash
python -c "import humanize; print(humanize.naturalsize(3000000), humanize.ordinal(3))"
# 3.0 MB 3rd
```

## Troubleshooting seen during our own setup
| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'freezegun'` while collecting `test_time.py` | upstream test dependency not in runtime deps | `pip install freezegun` (already in requirements.txt) |
| `fixture 'benchmark' not found` in `test_benchmarks.py` | missing plugin | `pip install pytest-benchmark` (already in requirements.txt) |

## Local change to the vendored upstream project
Upstream computes its version from git tags (`hatch-vcs`), which does not work in a
snapshot without upstream's git history (`pip install` fails while generating metadata).
We therefore pinned a static version: `humanize/pyproject.toml` (`version = "0.0.0"`, vcs hook
removed) and added `humanize/src/humanize/_version.py`. No library behaviour was changed.

## Setup video
Recording is in `docs/setup_video.mp4` (see `docs/setup_video_script.md` for the exact
command sequence demonstrated).
