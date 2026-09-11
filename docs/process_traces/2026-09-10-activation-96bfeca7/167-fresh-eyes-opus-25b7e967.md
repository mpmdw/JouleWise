# Fresh-eyes review — 25b7e967 (gate row 10)

Reviewer: Opus 5 (1M), read-only. Checkout: /Users/edr/code/JouleWise-wt-eq-ruling,
branch feat/2026-09-10-equivalence-ruling-316, HEAD 25b7e9670d2eea21389681f722d5aa28698ef3cd.
Nothing modified; worktree `git status --porcelain` empty at start and at finish.

## Verdict: CLEAN

All three edits check out. Two non-blocking observations (N1, N2) recorded below;
neither is a defect in this commit.

## (1) Allowlist `line` — 621 is the real call site: CONFIRMED

```
$ grep -n "load_calibration_ledger_snapshot(" scripts/epoch_equivalence_check.py
621:    snapshot = load_calibration_ledger_snapshot(
```

Only one call site in the file (line 106 is the import). Its enclosing def is
`def run(args: argparse.Namespace) -> int:` at line 606, so the fixture row's
`"function": "run", "ordinal": 1, "line": 621` matches the source exactly. The
old 596 was stale.

## (2) Runbook §2.5 mechanism sentence: TRUE as written

Sentence under review (docs/phase_2/derivation_night_runbook.md, just below the
`cd "$MEASUREMENT_ROOT"` / `"$PY" scripts/epoch_equivalence_check.py ...` block):

> `--acceptance` is left at its default, which resolves against the checkout
> the SCRIPT lives in (here the clone, because the `cd` and the relative script
> path select the clone's copy; `$PY` only selects the interpreter); …

Verified chain, each link read in this session:

- `scripts/epoch_equivalence_check.py:151` `REPO_ROOT = Path(__file__).resolve().parents[1]`,
  then `sys.path.insert(0, str(REPO_ROOT))` (line 153, guarded by `if str(REPO_ROOT) not in sys.path`),
  then `from joulewise.calibration_bracketing import … DEFAULT_ACCEPTANCE_BOUND_PATH`.
- `joulewise/calibration_bracketing.py:57-59` `_CALIBRATION_CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs" / "calibration"`;
  line 178 `DEFAULT_ACCEPTANCE_BOUND_PATH = ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH`, which is built from
  `_CALIBRATION_CONFIG_DIR`. So the default is derived from the MODULE's own file location.
- Empirical check from an unrelated cwd (/tmp) with a bare `python3`:
  module `/Users/edr/code/JouleWise-wt-eq-ruling/joulewise/calibration_bracketing.py`,
  default `/Users/edr/code/JouleWise-wt-eq-ruling/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`
  — i.e. neither cwd nor interpreter identity moved it; the imported package's location did.
- Runbook §0.2: `MEASUREMENT_ROOT` IS the clone (`git clone … "$MEASUREMENT_ROOT"`), and
  `PY="$MEASUREMENT_ROOT/.venv/bin/python"`. So the corrected attribution is right on the
  merits too: `cd` + the relative path `scripts/epoch_equivalence_check.py` pick WHICH script
  file runs; that script then forces its own checkout to the front of `sys.path`, so the
  `joulewise` copy imported — and hence the acceptance default — is the clone's. The old
  "`$PY` runs the clone's copy" phrasing attributed the selection to the interpreter, which is
  wrong in mechanism even though it happened to name the right checkout (the venv lives inside
  the clone). The replacement is the correct one. No correction needed.

N1 (nit, non-blocking, pedagogy not fact): the sentence states the conclusion
("resolves against the checkout the SCRIPT lives in") but omits the one link that
makes the conclusion true — the script prepends its own `REPO_ROOT` to `sys.path`,
so the *module* `joulewise.calibration_bracketing` is loaded from the script's
checkout, and the default is that module's `parents[1]/configs/calibration/…`.
A reader replicating from the text alone cannot derive why the script's location,
rather than the cwd or the venv, wins. If another pass touches this sentence, one
clause ("…because the script puts its own checkout first on `sys.path`, and the
default is built from the imported module's own location") would close it. Not
worth a commit on its own.

N2 (edge case, not reachable under this runbook): the `sys.path` insert is guarded
by `if str(REPO_ROOT) not in sys.path`. If an environment already had the repo root
on `sys.path` BEHIND a different checkout (e.g. a hand-set `PYTHONPATH`), no insert
would happen and another checkout's `joulewise` could be imported, moving the
default. `grep -rn PYTHONPATH docs/phase_2/derivation_night_runbook.md scripts/night_chains/`
finds nothing, and the runbook builds the venv from the lock in the clone, so the
documented path is unaffected.

## (3) Decision-log quote still verbatim: CONFIRMED

`gh issue view 316 --repo mpmdw/JouleWise --json body --jq .body`, clause 3:

> If continuation needs a code change (the epoch-freshness refusal in the loader or
> issuer), **the magistrate lands it through the normal PR gate as the smallest
> possible change** and reports the diff; it does not work around a refusal by hand.

docs/decision_log.md:6763-6766 now reads `… the magistrate "lands it through the normal
PR gate as the smallest possible change" with its diff reported; …`. Whitespace-normalized
comparison (markdown line wrap only) of the span inside the quotation marks against the
issue body: exact string match, 1 occurrence in the issue. The added subject
"the magistrate" sits OUTSIDE the quote marks and is also the issue's own subject for
that clause, so the attribution is faithful as well as grammatical.

## (4) Tests

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_custody_mode_inventory tests.test_docs_freshness tests.test_epoch_equivalence_check 2>&1 | tail -2

OK
```

Fuller tail from the same command re-run (for the count):

```
----------------------------------------------------------------------
Ran 64 tests in 80.541s

OK
```

Exit code 0 both runs.

## Context worth the magistrate knowing (not a finding against this commit)

The allowlist `line` field is documentary only. `tests/test_custody_mode_inventory.py`
validates it as "a positive int" (lines 226-232) and nothing more; the census matches on
`(file, function, ordinal)`, and `test_line_shift_does_not_require_allowlist_edit`
(line 330) pins that a shifted call line must NOT force a fixture edit. That is a
deliberate design property, so correcting 596 → 621 is accuracy housekeeping, not a gate
repair — and by the same design the field can silently go stale again after any future
edit above line 621. Adding an assertion that `line` equals the censused call's `lineno`
would fix the rot but would contradict the pinned line-shift property; flagging the
tension rather than recommending a change.
