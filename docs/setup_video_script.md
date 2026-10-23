# Setup video - what to show (target 2-3 minutes)

Record screen + terminal (OBS / Win+G / QuickTime). Save as `docs/setup_video.mp4`.

1. Show the GitHub repo page (name, public, commit history).
2. `git clone <repo-url>` and `cd` into it.
3. `python3 -m venv .venv` then activate it.
4. `pip install -r requirements.txt` (let it finish).
5. `pytest humanize/tests -q` -> show the green summary.
6. `python -c "import humanize; print(humanize.naturalsize(3000000), humanize.ordinal(3))"`.
7. `pytest` (our assignment suite) -> show it runs.
8. Say your name and which modules you tested.
