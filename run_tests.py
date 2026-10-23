#!/usr/bin/env python3
"""Named test suites for the assignment (Task 4).

    python run_tests.py <suite> [extra pytest args]

Suites
  smoke             fastest happy-path tests, one per function
  regression        everything (serial, ordered)
  ecp | boundary | negative | datadriven | module_level     one technique/group
  number | filesize | time | lists                           one module
  clamp | intword | naturaldate                             individual function suite
  m2                all tests authored by Member 2 (Ibadat Ali)
  parallel          everything, all CPU cores (xdist `load`)
  parallel-modules  4 workers, one per module suite (xdist `loadgroup`)
  ordered           everything, serial, verbose: shows the enforced group order
  full              parallel + JUnit XML + HTML report in reports/
"""
import subprocess
import sys

SUITES = {
    "smoke": ["-m", "smoke"],
    "regression": [],
    "ecp": ["-m", "ecp"],
    "boundary": ["-m", "boundary"],
    "negative": ["-m", "negative"],
    "datadriven": ["-m", "datadriven"],
    "module_level": ["-m", "module_level"],
    "number": ["-m", "number"],
    "filesize": ["-m", "filesize"],
    "time": ["-m", "time"],
    "lists": ["-m", "lists"],
    "clamp": ["-m", "clamp"],
    "intword": ["-m", "intword"],
    "naturaldate": ["-m", "naturaldate"],
    "m2": ["-m", "m2"],
    "parallel": ["-n", "auto", "--dist", "load"],
    "parallel-modules": ["-n", "4", "--dist", "loadgroup"],
    "ordered": ["-p", "no:xdist", "-v"],
    "full": [
        "-n",
        "auto",
        "--dist",
        "load",
        "--junitxml=reports/junit.xml",
        "--html=reports/report.html",
        "--self-contained-html",
    ],
}


def main(argv):
    if not argv or argv[0] not in SUITES:
        print(__doc__)
        return 2
    command = [sys.executable, "-m", "pytest", *SUITES[argv[0]], *argv[1:]]
    print("$", " ".join(command), flush=True)
    return subprocess.call(command)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
