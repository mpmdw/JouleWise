# Fix seat: the N3 test passes locally but errors on hosted CI (Linux, stdlib core only)

Worktree: /Users/edr/code/JouleWise-wt-adae-tests (branch tests/2026-10-03-g2a-attach-guard-tests, head 7f7cbec6, PR #469). Commit if your sandbox allows; otherwise leave changes uncommitted. Do not push.

`tests/test_harvest_g2a_window.py::G2aHarvestTests::test_real_passed_bracket_after_nonzero_acceptance_cutoff_selects` (added in 93b84dae) passes on this Mac but on GitHub Actions (ubuntu, Python 3.13, the "Unit tests (stdlib core only, per D-009/D-017)" step of `.github/workflows/ci.yml`) it errors at line ~386: `FileNotFoundError: .../archive/derived/bracket.json` — the harvest ran but never wrote `bracket.json`, so it must have ended REFUSED/NULL earlier on CI.

Find the cause without guessing: list every file the test and the harvest path it drives read (fixture inputs, "retained import receipts", acceptance artifacts, estimator pins, anything under `runs/`, `configs/`, `tests/fixtures/`) and check each with `git ls-files --error-unmatch` (an untracked or gitignored file exists here but not on CI) and for platform dependence (macOS-only paths, `os.uname`, `platform`, Metal/MLX, `plistlib` behaviour, case-sensitive paths, `/private/tmp` vs `/tmp` symlinks, `os.sched_*`, missing non-stdlib modules such as numpy). Reproduce the CI condition locally where possible (e.g. run with `PYTHONPATH` stripped of site-packages, or a copy of the repo made by `git archive HEAD | tar -x -C /tmp/dd5-n3ci/repo` so untracked files are absent, and the system `/usr/bin/python3` or the venv python with `-I -S` if numpy is the issue).

Then fix the TEST (not production code): make it hermetic from tracked bytes, or, if it genuinely needs inputs that CI cannot have, skip with an explicit `skipUnless` reason exactly like the existing D-079-import-input skip in this file (find it) — but only if the same skip condition also identifies the local environment correctly. In either case make the test assert the harvest verdict and print `record.get('fault')`/cause codes BEFORE reading `bracket.json`, so a future failure says why. Run the test from the `git archive` copy to show it passes or skips there, and in the worktree.

WRITE_SCOPE: ["tests/test_harvest_g2a_window.py", "tests/fixtures/**"]
Scratch: /tmp/dd5-n3ci/ only. No production code. Finish in this turn.
