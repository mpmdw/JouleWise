# Record 38 — Opus counter-review (gate-ledger row 6): B1 `fix/2026-09-19-generator-head-pin-semantic` @ `842e5b39` (base `b3abce08`)

**VERDICT: MERGE-WITH-FIXES — blocker 0, should_fix 1, nit 4.** The single
should_fix is a three-line wrap (below the bench-vs-session threshold; the lead
does it at the bench). Nothing in the diff threatens custody, emitted bytes, or
the adjudicated shape. Read-only worktree `JouleWise-wt-b1refc-d0b83820`.

## Answers to the six questions

**1. Acceptance resolution.** No cross-binding path exists. `verify_ledger_head_pin()`
calls `acceptance_pin()` itself, and the drift loop one statement earlier
(`…1p7b_v5/generate_configs.py:2539-2545`) byte-pins that same file, so the cutoff
the check reads is always the acceptance the pack binds. Executed: preserve mode
resolves `calibration_acceptance_d079_v2.json` (n19), successor mode
`…_v2_n17_r6.json`; **both carry `ledger_cutoff` = `{76, 08456d50…, …ledger.v1}`
today**. If they ever diverge, successor mode refuses with `acceptance ledger cutoff
drifted` — fail-closed in the right direction. Live packs today:
`PRESERVE_CURRENT_FROZEN_BYTES = False`, `target_is_successor_family = True` (executed).

**Escaping exception types.** `json.JSONDecodeError` is a `ValueError` subclass;
`FileNotFoundError` is an `OSError`; the `__main__` guard catches
`(OSError, ValueError, json.JSONDecodeError)`. Executed all four counterfactuals
through the real CLI (`--check --prefill-prompt-pin …`): rollback, corrupt JSON,
bad shape, deleted file → **rc=1, no traceback in any case**. `KeyError`/`TypeError`
are reachable only from the acceptance side, which the preceding drift row
byte-pins — unreachable. No bypass.

**2. Ordering.** Identical in both generators: drift loop `:2539-2545` →
`verify_ledger_head_pin()` `:2546` → first `write_bytes(...)` `:2548`. Nothing
between the two. `--check` **does** run the head check: `check_current()` `:3164`
calls `generate(temp_root, …)` `:3171`, the same `_generate` path. Preserve mode
returns at `:2518-2522`, before both the drift loop and the new call — exactly the
reachability the deleted byte-pin row had, so no regression (nit 3).

**3. Emitted bytes.** Independent of the pin's bytes **and** its sequence.
My own probe generated ALPHA three times against the real committed pin (176 /
`0f7609ae…`), a cutoff-equal pin (76 / `08456d50…`), and an advanced pin
(999 / `99…9`): identical `calibration_plan_sha256 = c245ac2d3020…`, identical
`plan_tree_sha256 = b0d4a8e1bcbf…`, identical whole-tree snapshot digest
`7c6d1f856518d3e2…`. This is strictly stronger than the in-repo regression, which
compares cutoff vs cutoff+100 and never exercises the real committed 176.
Also confirmed: the two live v5 packs have **no committed `plan_tree.json`** — they
are generated on demand — so dropping `file_sha256` cannot strand a committed pack.

**4. Vacuity.** Not vacuous. Executed the deletion counterfactual independently
(neutering `module.verify_ledger_head_pin`, equivalent to deleting the call since
the return value is discarded): **6 of 10 methods detect it** (28 sub-test
failures) — `rolled_back_pin`, `schema_mismatch`, `equal_sequence_with_different_digest`,
`non_integer_sequence`, `missing_or_extra_keys`, `acceptance_cutoff_digest_must_match`.
The 4 survivors are legitimately independent properties, not vacuous coverage:
acceptance-drift ordering, emitted-byte identity, manifest shape, and the real-pin
`--check` subprocess. Exactly reproduces refuter 37c's V3 by a different route.

**5. Prune.** Nothing dead or misleading beyond the nits below. `nullcontext` was
correctly dropped; `hashlib` and `GENERATION_LEDGER_HEAD_BYTES/_SHA256` remain
**live** in the retained frozen-path helper `tests/test_campaign_generator_core.generation_repository()`
(`:27-58`) — correctly kept per adjudication §2. AST scan of all three test files:
no unused imports. The two generator hunks are byte-identical (verified by diff of
the changed lines). Repo-wide, `LEDGER_HEAD_FILE_SHA256` survives only in process-trace
prose; digest `6bbe2625…` survives only in that fixture and in historical records.

## Findings

**F1 — should_fix. A corrupt head pin now refuses without naming the file.**
Before this diff, *any* corruption of `configs/calibration/calibration_ledger_head.json`
hit the byte-drift row and refused with `pinned input drifted: configs/calibration/calibration_ledger_head.json`.
The pin is now the one parsed input that is **not** byte-verified first, so a parse
failure surfaces raw. *Counterfactual executed:* write `{nope` to the pin, run
`generate_configs.py --check --prefill-prompt-pin <pin>` → stderr is
`generation failed: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)`
— no path, no hint which of a dozen JSON inputs failed. At 03:00 before an arm that
is a materially worse refusal. *Call site:* `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2484`
and the identical line in `…-8b_v5`. *Fix:* wrap the `json.loads` in
`try/except json.JSONDecodeError` → `raise ValueError(f"ledger head pin is not valid JSON: {pin_rel.as_posix()}")`.
Neither the seat nor refuter 37c ran the corrupt-pin counterfactual.

**F2 — nit. `"ledger head pin shape invalid"` names no path either** (`:2481`),
unlike the other four refusals. It is verbatim from ruling 10 / adjudication §1, so
changing it is the magistrate's call, not the seat's. Suggest appending `: {pin_rel.as_posix()}`
at the same time as F1.

**F3 — nit. Docstring under-describes the function.** `:2478` says only "the head
pin must be at or ahead of the acceptance cutoff"; the body also enforces object
shape and key set, schema equality, the acceptance-binding digest, and digest
equality at equal sequence. The why-comment below it is accurate and well built.

**F4 — nit. Preserve mode never reaches the check** (`_generate` returns at
`:2518-2522`). Unreachable today for both live packs and identical to the deleted
byte-pin row's reachability, so not a regression — but worth recording that freezing
these packs later silently retires the check by design.

**F5 — nit. Misleading local name in the new regression.**
`tests/test_generator_head_pin_relation.py:165-181`: `pin` holds the **cutoff** pin
while the file on disk holds the advanced one; line 179 asserts against
`pin["head_digest"]`. The assertion is correct; the name reads as if it asserts the
on-disk value. Rename to `cutoff` or add one comment.

**Informational, out of scope.** The armed n1-20260919 evidence
(`…-activation-d8ca3a36/21-arm-evidence-n1-20260919/night_probe_receipt.json`) records
`ledger_pin_sha256 = 6bbe2625…` (sequence 76) from the separate measurement checkout,
while this tree's pin is at 176. B1 does not touch that machinery; flagged only so the
magistrate confirms the arm path is not byte-pinning the head file the same way.

## Commands run (worktree `JouleWise-wt-b1refc-d0b83820`, venv `/Users/edr/code/JouleWise/.venv`)

| # | Command | Outcome |
|---|---|---|
| 1 | `git diff b3abce08 842e5b39` (+ `--stat`) | 5 files, +292/-56; generator hunks byte-identical between the two packs |
| 2 | `python -B -m unittest tests.test_campaign_generator_core tests.test_d117_floor_qwen3_v5_generate` | `Ran 20 tests … OK` (15.0 s) |
| 3 | `/tmp/magistrate-d0b83820/opus-counter-b1/probe.py` | 3-pin emitted-byte probe → identical digests; preserve/successor flags; exception-type probes |
| 4 | `/tmp/magistrate-d0b83820/opus-counter-b1/cli.py` | 4 CLI refusal counterfactuals → rc=1, no traceback; F1 message gap found |
| 5 | `/tmp/magistrate-d0b83820/opus-counter-b1/mutant.py` | deletion counterfactual → `tests=10 subfailures=28 detected_methods=6`; 4 independent survivors |
| 6 | `grep -rn LEDGER_HEAD_FILE_SHA256 / 6bbe2625… .` | no live stale reference; fixture + process traces only |
| 7 | AST unused-import scan over the three test files | clean (only `__future__.annotations`) |

No repository files were written; all scratch under `/tmp/magistrate-d0b83820/opus-counter-b1/`.
Not claimed here: full-suite replay, fixture orphan census (needs `ps`), hardware paths.
