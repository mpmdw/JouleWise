# Magistrate terminal review — NIGHT-GATE-STUB-CHAIN-01 (PR #309), merge candidate `5db38b5816bce05b67cabfe3eb621bf2b22aa3e6`

Reviewer: headless magistrate, activation 2145630c (Fable), full session context, not delegated. Read at the bench in the linked
worktree `/Users/edr/code/JouleWise-wt-night-gate-stub` (branch `fix/2026-09-09-night-gate-stub-chain`, HEAD 5db38b58).
Diff read in full: `git diff 83ab38ed..5db38b58 -- joulewise/night_gate.py scripts/run_night.py` (+78/−64 gate, +6/−1 driver);
test additions listed by name from `git diff 83ab38ed..5db38b58 -- tests`.

## Forcing defect (primary evidence)

Harvest record 21i: rehearsal-20260909 `receipt.json` verdict REFUSED, reason `night_probe_error`, because `evaluate_night` read
`plan.chain_path` for every receipt class while the driver (`scripts/run_night.py:1573–1575`) substitutes the built-in stub
`sleep 2; echo REHEARSAL` whenever `rehearsal_effective` (i.e. `receipt_class == "REHEARSAL_STUB"`), and the stub arm never
writes `chain.zsh`. NIGHT_HANDBACK names `night_refused_agent_present` as the only acceptable stub refusal, so this was a finding.

## Design-level questions (row 7)

1. **One truth with the driver?** Yes. The driver's own branch (`run_night.py:1571–1575`) already ignores the plan's chain for the
   stub class (`chain_path = /dev/null`, `chain_sha256 = None`, built-in command). The gate now mirrors exactly that predicate
   (`plan.receipt_class == "REHEARSAL_STUB"`), so gate and driver agree on what the stub night executes. No second source of truth
   was introduced (no new plan key, no flag).
2. **Does any other class lose the check?** No. The non-stub path is the previous code re-indented under `else:`; the delta
   refuter (23b) confirmed the non-stub detail string and the whole sidecar/digest ladder byte-identical to bb7090e2, and the
   `DIAGNOSTIC_NO_PACK` regression (`test_diagnostic_still_refuses_missing_chain_or_sidecar`) pins that a missing chain still
   refuses `night_probe_error` for a real class.
3. **Does the receipt say only true things?** Yes after fix round 1: stub C5 records `chain_sha256: null`,
   `expected_chain_sha256: null`, `chain_stub: built_in_stub_by_design`, the plan's two paths, and a detail sentence that states the
   chain identity was NOT evaluated. The C5 evidence list carries no `chain:`/`chain_sha256:` citations for the stub (23b N1).
   The class table (`REHEARSAL_STUB` C5 = PASS, basis None) and `validate_receipt` basis rules are untouched, so this is not a
   ruling change; it removes a false claim from a receipt.
4. **Consumers of the nulls?** Bench sweep this session: `grep -rn chain_sha256 joulewise scripts` outside `night_gate.py` hits only
   `arm_readiness.py` `window_chain_sha256` (the TRANSACTION_PACK GO-receipt path, which never takes the stub branch). No consumer
   reads a stub receipt's C5 `chain_sha256` as a string. Opus review 10's consumer sweep reached the same conclusion.
5. **Driver log line.** `night gate verdict=REFUSED reason=… detail=…` is one line, detail newline-joined and capped at 200 chars;
   the non-refused form is byte-identical (`test_non_refused_gate_log_keeps_exact_verdict_form`). This is what would have let the
   courier's finding note be written from `night.log` alone.
6. **What this PR does NOT decide.** Whether the cure needs a second stub night before G2-a, and whether the stub class should ever
   carry a chain-identity check (Opus review 10 S4, recorded in 21i as a note), stay with the cold gate or Ed. Nothing here arms,
   re-arms, or touches a plan.

## Overbuild / merge-ability prune (row 8)

Nothing to prune. Four files, one predicate, six defect-shaped tests, contract §9 pins repinned mechanically (139 occurrences,
63 repinned, 0 unresolved; 101/101 symbol pins on definition lines per 23b). No new module, no new plan key, no doc rewrite.

## Bench execution this session

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate tests.test_run_night` in the branch worktree:
`Ran 136 tests in 8.492s / OK` (rc 0). Full-suite replay alone on the integration tree is recorded separately (row 9).

## Review lineage

seat 02 (Astra, implementation) → execution refuter 09 (Astra) + contract refuter 10 (Opus, fresh non-author) → fix brief 16 /
seat 17 (S1 detail sentence, N1 paths, S3 present-but-mismatched regression, S2 repin) → delta re-audit 23b (Astra, read-only):
S1/N1/S3/S2 PASS, mutation harness kills the inverted predicate, **same signature: none**. First delta attempt 23 died with
activation 628c2eed's exit; 23b is the record.

## Verdict

CLEAN for merge at 5db38b58 once CI is green on that head and the full-suite replay alone on the integration tree records rc 0.

## Addendum (2026-09-09 ~06:10 PDT, ruling 44 A6)

The verdict sentence above required "the full-suite replay alone on the integration tree records rc 0". Cold-gate ruling
`44-coldgate-ruling-replay-verdict.md` (Q2) amends the acceptance for this PR: the replay alone on the integration tree (main + this
branch) may record exactly the four pre-existing `IdleAdmissionCoreVerdictTests` failures (by name, each at
`tests/test_run_campaign.py:9581`, `AssertionError: False is not True`) and nothing else, provided A2 (pathspec and import independence
recorded), A3 (same four on the merge base, same session), A4 (`tests.test_night_gate tests.test_run_night` green on the integration
tree, not the branch), A5 (CI green on the final head) and A6 (class re-run green after powermode 0, recorded as a dated addendum) hold.
Any other failure or error is a hold. Recorded, not decided here.

## Addendum 2 (2026-09-09 ~08:55 PDT, cold gate 56 W8)

Two replays on successive integration trees each recorded the ruling-44 four plus one different extra failure (53: a docs-freshness
literal check broken by a main commit, cured at a3da3463; 54: `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`,
a 30 s thread-join timeout under four-shard concurrency, green alone 4/4). Cold gate 56 rules that attempt 2 does NOT satisfy 44 A1 as
written, refuses a general "passes alone + registered lane" clause, and grants a named structural waiver for THIS head (6d76f964) only,
under W1–W8, on the ground that the PR's only code hunk (`evaluate_night`, night_gate.py 1040–1104) is unreachable from the race test's
launch path (which reaches night_gate only through the function-local `NightPlan`/`PlanError` import at arm_readiness.py:9933, untouched).
The first addendum's "any other failure or error is a hold" is superseded for that one named failure on that one head; no precedent.
Record: `59-pr309-row9-waiver-record.md`.
