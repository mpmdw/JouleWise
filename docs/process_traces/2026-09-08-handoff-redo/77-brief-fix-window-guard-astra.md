WRITE_SCOPE: ["scripts/window_status.sh","tests/test_window_status_guard.py"]

# Fix-round brief — WINDOW-STATUS-GUARD-CENSUS-01, Astra refuter findings F1-F4 (gpt-6-astra, medium)
HEAD = a37de2ec (your landing). Refuter (trace 76) found, verbatim:
F1 BLOCKER `scripts/window_status.sh:74` — the exact `window-chain` basename restriction misses valid run_night
chains with other filenames: `run_night.py:1237` launches `plan.chain_path`, and the G2-a generator accepts an
arbitrary output path. A census containing `run_night`, `/bin/zsh /tmp/.../chain`, `/bin/sleep 600` wrote status
(must refuse). Cure: treat a live `scripts/run_night.py` process (any interpreter) as a measurement in progress
regardless of the chain filename, AND any child of it; keep the campaign entry-point rule.
F2 BLOCKER `:57` — whitespace tokenization of flattened `ps` text misses interpreters, campaign scripts, or chain
paths containing spaces (`python3 /repo with space/scripts/run_campaign.py …` wrote status). Cure: match on the
`run_campaign.py` / `run_night.py` path COMPONENT anywhere in the command string (regex on the basename preceded by
`/` or start, followed by whitespace or end), not on split tokens; keep the `--dry-run` and `unittest` exclusions
working on the whole string.
F3 should-fix `:61` — the interpreter-option parser omits Python's `--` separator (`python3 -- scripts/run_campaign.py`
passes). Cure follows from F2 if matching is by path component.
F4 should-fix `:44` — a census command that exits 0 but prints garbage or nothing FAILS OPEN (status written). Cure:
require at least one `ps`-shaped header/row (e.g. the injected census must contain a PID column / the header line
the real `ps aux` prints); otherwise refuse with a named reason before writing.
Add a regression for each (F1: run_night with a custom chain path → refuse; F2: paths with spaces → refuse; F3: `--`
→ refuse; F4: garbage and empty census → refuse, nothing written), keep the sibling-process regression (unittest /
--dry-run / grep / codex prompt text must NOT refuse), and prove each new regression fails against a37de2ec in a
$TMPDIR copy. Acceptance = tests.test_window_status_guard to a log with rc + `bash -n`. Never the repository-wide
suite; no `git commit`; header < 8192 bytes; genre implementation verdict keys.
