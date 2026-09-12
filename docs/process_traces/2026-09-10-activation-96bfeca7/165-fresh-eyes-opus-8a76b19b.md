# 165 — Fresh-eyes review (gate row 10), post-review commits 07995051 + 8a76b19b

Reviewer: Opus 5 (1M), read-only. Checkout `/Users/edr/code/JouleWise-wt-eq-ruling`
at `8a76b19b` (branch `feat/2026-09-10-equivalence-ruling-316`), working tree clean,
nothing modified. Scope: the two diffs only, whole files read as context.

## Verdict

**CLEAN — no blocker, no should-fix.** Four nits (N-1 is the only one with any
operational bite; it is documentation drift, not behaviour).

## 1. Did either commit introduce a defect? — No

Script commit `8a76b19b` (`scripts/epoch_equivalence_check.py`), each named risk checked:

- **`registry_row` identity and ordering.** `registry_row = _D102_GENERATION_DERIVATIONS.get(acceptance_id, {})`
  is assigned at `scripts/epoch_equivalence_check.py:263` and is the same variable
  read at `:278` for `screen_rule`; assignment precedes use in straight-line code
  with no rebinding between (`:263`–`:278`). **Missing/non-string `screen_rule`
  refuses, does not crash**: `.get` on the `{}` default yields `None`, the
  `isinstance(..., str)` guard at `:279` raises `EquivalenceRefusal` → refusal
  exit 3, and nothing is written (the `--out` write at `:636` is downstream of
  `reference_envelope`). Defence in depth: a wholly absent registry row would
  already have refused earlier — `registered is None` at `:244` and the
  `corpus_n` cross-check at `:266`.
- **`relative_to(REPO_ROOT)` fallback.** `:284`–`:287` wraps it in
  `try/except ValueError` with `resolved_path.name` as the fallback, which is the
  only exception `Path.relative_to` raises for a non-subpath. The paired
  `acceptance_file_sha256` keeps the record unambiguous even in the fallback case.
- **`hashlib`** imported at `:84` (module scope, top of the import block); the
  `read_bytes()` at `:293` runs only after the production loader has already
  authenticated that exact file, so a missing/unreadable artifact cannot reach it.
- **Floored-generation NOTE reachability.** `envelope_lines` `:333`–`:337`:
  `" and the never-zero floor of that rule"` is selected only when
  `envelope["screen_rule"] != "range_equals_screen"`; r6's registered rule *is*
  `range_equals_screen`, and `:219` refuses any `acceptance_id` other than r6, so
  the floor clause is unreachable in production and the printed run says
  `no floor is in force under this screen rule` (see §3 output). Dead-but-correct
  defensive text, consistent with the runbook's §2.5 fact 3 and the decision-log
  addendum, both of which already attribute the gap to quantization alone.
- **Byte-for-byte claim actually holds.** The written record (`evaluate_session`
  `:463`ff) carries `reference_envelope` (now repo-relative path + digest +
  screen rule), `session`, `slot_outcomes`, `m`, the extrema and the two
  comparisons — **no other absolute path anywhere**. The absolute `--out` path is
  printed to stdout (`:637`), never into the record. So the runbook's new
  parenthetical is true as written.

Docs commit `07995051`: no factual defect found. The one claim it adds about
runtime behaviour — `docs/phase_2/derivation_night_runbook.md:2018`, "The session
is terminal and §2.5 judges its finalized rows (… fewer than six retained values
is INCONCLUSIVE)" — is code-correct:
`TERMINAL_SESSION_STATES = frozenset({"finalized", "aborted"})`
(`scripts/issue_calibration_acceptance_generation.py:966`), the
`aborted` + `abort_reason == "window_exhausted"` case is handled explicitly at
`scripts/epoch_equivalence_check.py:362`–`375`, and `MINIMUM_RETAINED_M = 6`
(`:127`) matches "fewer than six".

Runbook `§2.5` shell block (`:1713`–`:1720`): `$MEASUREMENT_ROOT`, `$PY`,
`$SESSION_ID`, `$NIGHT_ROOT`, `$CALIBRATION_LEDGER`, `$LEDGER_HEAD_PIN` are all
exported upstream of §2.5 — the harvest-desk block at
`docs/phase_2/derivation_night_runbook.md:1401`–`1407` (and the arm block at
`:269`–`:334`), with `CALIBRATION_LEDGER` under `runs/` matching
`DEFAULT_LEDGER_PATH`. Fence changed to ` ```zsh `, which is the file's
convention (20 zsh fences).

## 2. Docs verification

All against `gh issue view 316 --repo mpmdw/JouleWise --json body --jq .body`
(rc 0, 4850 bytes, fetched this session):

| Claimed quote | Where | Result |
|---|---|---|
| `lands it through the normal PR gate as the smallest possible change` | `docs/decision_log.md:6764` | **VERBATIM** (issue: "the magistrate lands it through the normal PR gate as the smallest possible change and reports the diff") |
| `the m values` | `docs/phase_2/derivation_night_runbook.md:1692` | **VERBATIM** |
| `if the validator's operative screen differs from the raw range (the never-zero floor), the operative value is the one used` | runbook `:1628`, dlog `:6739` (context, not in these diffs) | **VERBATIM** |

**Revision 1 byte-identity: CONFIRMED.** `git show 6c581738:configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
(the last state before revision 2 landed in `12162263`) vs lines 1–287 of the file
at HEAD: `diff` reports only `284a285,287` — a blank line, `---`, blank line, i.e.
the revision-2 separator. Not one revision-1 byte changed; the `07995051` edit sits
at `:492`–`:497`, inside revision 2 (which starts at `:288`).

**The blindness quote is genuinely revision 1's own words.** The new text quotes
"every rule that could otherwise be chosen after seeing values is fixed here first",
which is verbatim revision 1 at `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:30`–`31`
("…why it is written before any data: every rule that could otherwise be chosen
after seeing values is fixed here first."). The superseded wording
("so that nothing can be chosen after seeing values") appears nowhere in revision 1
— review 159's S-1 was correct and the fix is correct.

**D-102 clause 2: the addendum states it correctly.** `docs/decision_log.md:6474`–`6484`
reads: "the artifact binds {os_build, hardware_model, power_policy,
sampling_interval_ms, estimator_revision, pulse_protocol_id}; any change →
`calibration_acceptance_bound_stale`. Mandatory prospective re-derivation triggers:
**any identity-field change**; protocol/estimator byte change; …". So both halves of
the addendum's new paragraph check out: "any identity-field change" is indeed among
the MANDATORY prospective triggers, and `os_build` is one of the six bound identity
fields, so the os_build change alone would have voided r6 absent the carve-out. The
addendum's preserved half (trigger observation judged under the PRIOR artifact,
never incorporated into a threshold judging itself) is likewise clause 2's text
verbatim in substance. "Clause 2 above" resolves: the addendum heading is at
`docs/decision_log.md:6700`, inside D-102 (`:6449` → next section D-103 at `:6798`).

## 3. Commanded runs (pasted)

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_equivalence_check \
    tests.test_docs_freshness tests.test_custody_mode_inventory \
    tests.test_mint_policy_resolver_guard tests.test_d078_reason_registry 2>&1 | tail -3
Ran 78 tests in 87.971s

OK
```

```
$ PYTHONDONTWRITEBYTECODE=1 python3 scripts/epoch_equivalence_check.py --print-envelope-only
Reference envelope (the acceptance in force; issue 316)
  acceptance_id: d079_calibration_acceptance_v2_n17_r6
  artifact: configs/calibration/calibration_acceptance_d079_v2_n17_r6.json  sha256 0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d
    loaded by joulewise.calibration_bracketing.load_calibration_acceptance_bound
  screen rule registered for this generation: range_equals_screen
  corpus n = 17 (artifact derivation_corpus.n; registry corpus_n; they agree)
  raw corpus maximum_s = 0.03289849371536248  [artifact decimal_derivation.source_statistics]
  raw corpus range_s   = 0.00972358928879385  [artifact decimal_derivation.source_statistics]
  OPERATIVE level screen   preflight_level_screen_s   = 0.032898493715362  [validator registry _D102_GENERATION_DERIVATIONS operatives]
  OPERATIVE bracket screen bracket_screen_s           = 0.009724  [validator registry _D102_GENERATION_DERIVATIONS operatives]
  budget ceiling           maximum_budgetable_drift_s = 0.010164834757777545  [validator registry _D102_GENERATION_DERIVATIONS operatives]
    artifact decimal_derivation.ratified_operatives agrees with the registry on all three, or this tool refuses
    NOTE: the operative comparators differ from the raw statistics by quantization; no floor is in force under this screen rule; issue 316 rules the OPERATIVE value is the one compared against.
rc=0
```

The printed path is repo-relative and the digest matches the artifact's bytes
(`shasum -a 256` of the file agrees, per the regression test at
`tests/test_epoch_equivalence_check.py:451`–`469`).

## Nits

- **N-1 (nit, documentation drift, introduced by 8a76b19b).**
  `tests/fixtures/custody_read_replay_allowlist.json:62` refreshes `"line"` to
  `596`, but 596 was the call site in the **parent** commit's file; the same
  commit added 25 lines above it, so the actual `load_calibration_ledger_snapshot`
  read-replay call is now `scripts/epoch_equivalence_check.py:621`, and line 596
  is `return lines` inside `record_lines` — a different function from the row's
  `"function": "run"`. Harmless to the gate: `tests/test_custody_mode_inventory.py:224`–`232`
  keys the census on `(file, function, ordinal)` and only asserts `line` is a
  positive int, which is why the suite is green. Cost is to a human auditor
  navigating by that number. One-character-class fix (596 → 621) if a doc commit
  is still open; not worth a round on its own.
- **N-2 (nit, style).** `docs/phase_2/derivation_night_runbook.md:1599` is a
  119-column prose line ("instrument. Its rule was fixed in writing before the
  night was armed, by the owner's directive issue 316 of 2026-09-10,") where the
  surrounding prose wraps at 76–77. Table rows in this file are long by
  convention; body prose is not.
- **N-3 (nit, precision — writing standard).**
  `docs/phase_2/derivation_night_runbook.md:1722`–`1723`: "`--acceptance` … resolves
  against the checkout the SCRIPT lives in (here the clone, because `$PY` runs the
  clone's copy)". The conclusion is right (both are the clone's), but the named
  mechanism is not: `$PY` selects the *interpreter*; what selects the script copy
  is `cd "$MEASUREMENT_ROOT"` plus the relative `scripts/epoch_equivalence_check.py`.
  "because the block `cd`s into the clone and runs the clone's copy of the script"
  would be replicable from the text. ("Clone" = `$MEASUREMENT_ROOT` per §Terms
  `:362`, so the sentence is consistent with the runbook's vocabulary.)
- **N-4 (nit, prose).** `docs/decision_log.md:6763`–`6765`: "If continuation needs a
  code change (…) it \"lands it through the normal PR gate as the smallest possible
  change\"…" — the quote is verbatim and the fix is correct, but the leading "it"
  (the code change) collides with the quoted "it" (the change, landed by the
  magistrate), so the sentence has two different referents one word apart. The
  issue's own subject was "the magistrate".

Nothing here rises to should-fix; none of the four blocks landing `8a76b19b`.
