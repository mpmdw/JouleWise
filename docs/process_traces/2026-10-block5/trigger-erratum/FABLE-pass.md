Contamination disclosure: before this charge, in this session, I read nothing about this project by my own choice; the harness injected the global and project CLAUDE.md instruction files and the one-line memory index (MEMORY.md, whose entries include the 10-11 note that BETA a4 and a5 were lost to a stale calibration acceptance). I opened no RUN_STATE.md, docs/orchestration.md, decision log, memory body, or anything under the blinded paths.

# Cold pass 4 (Fable 5.1), harvest lane change for Erratum 3 (trigger scope)

Reviewed: `git diff 0699abbb0..e4b4145a0` in `/Users/edr/code/JouleWise-wt-harvest-trigger-cold` (BRK = `joulewise/calibration_bracketing.py`, H = `joulewise/b5/harvest.py`, the new `tests/test_harvest_b5_trigger_scope.py`, the one edit in `tests/test_harvest_b5_window.py`), against ERRATUM.md sections 4 and 5. Line numbers below are those of e4b4145a0 unless marked "pinned". Structure only: no energy, no power, no workload duration, no member name.

Executed in the foreground (all with `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/Users/edr/.jwtmp/fable-pass4`, python 3.13):

- baseline `tests.test_harvest_b5_trigger_scope` in the working directory: 26 tests, OK, 117 s.
- `tests.test_harvest_b5_window.HarvestCheckoutTests` in the working directory: 4 tests, OK.
- 17 mutation probes on copies under `/Users/edr/.jwtmp/fable-pass4/p1..p8` (tree exported with `git archive e4b4145a0`); the sealed-identity probe reads the pinned source from a saved copy of `git show 0699abbb0:joulewise/calibration_bracketing.py`, SHA-256 `ddb7db11c8d04946c8d3c6d7660822e442b4dee3ac77f3e1be6a23f683974037`, which equals the digest the erratum cites for BRK at the pin.
- the pinned text of the checkout test (file list updated to four files) against the new program, in a scratch git copy.
- the live calibration ledger: 478 rows; row 456 is a `bracket-session-slot-finalization` with `disposition` `systematic-invalid` and a `session_id` of attempt 3's session; rows 464 and 474 carry attempt 4's and attempt 5's session ids. So the snapshot's `bracket_session_id` is populated from the ledger's `session_id`, and item 2's comparison has real data on both sides.

NOT EXECUTED (not mine or not runnable here): the item 12 exploratory run over BETA attempt 5's archived ledger copy (blinded path); the before/after comparison on the rehearsal copy (`tests.test_harvest_b5_rehearsal_compare`, skipped under `JW_B5_SYNTHETIC_ONLY`); the real `scripts/check_window_provenance.py` subprocess and the sealed verdict writer in the stale state (see F3); `unittest discover` and the repository suite (forbidden; another process runs it).

## Summary

No BLOCKER. No SHOULD-FIX before the pin. One SHOULD-FIX (F3) scoped to before a governed GAMMA attempt is armed, which the erratum itself already schedules there. Four NOTEs. The null ruling on `corpus_doubling` is confirmed (F2).

## Answers to the seven charges

### 1. Can a governed bracket pass that the admitted text would fail?

Not by any path I found. Each check of item 4 is in place, unweakened and in the sealed order; the diff wraps every `return result, reasons` in `finish(...)` and touches no condition except the three the text amends:

| Item 4 line | Where (BRK) | Changed? | Probe |
|---|---|---|---|
| acceptance missing / unissued | 2192-2222 | no | item4 test (mocked loader, both cases) |
| snapshot absent / refused / baseline | 2242-2258 | no | item4 test |
| identity change | 2341-2359 | no | P13 |
| incomplete candidate list | 2397-2398, 2423-2424 | no | item4 test (`candidates[:-1]`) |
| custody did not load | wrapper 2961-2967 | no | wrapper test `custody` case |
| binding missing / invalid | 2461-2485, 2500-2514 | no | item4 test |
| unclassifiable (`abandoned`) | 2573-2577 | no | P16 |
| set-aside unresolvable | 2580-2583 | no | item4 test (mocked resolver) |
| own post above screen | H 4530-4533, 4569-4577 | no | harvest test, evaluator asserted not called |
| endpoints missing / old / not of the bound session / not finite | 2687-2724 | no | item4 test (`instrument_calibration_stale`, NaN bound) |
| own pre above screen | 2768-2778 | no | P7 |
| byte change at the second site | 2780-2800 | set narrowed to the one name under `window_evidence` only | P5 |
| own drift above ceiling | 2818-2819 | no | P6 |

Item 2, how the own session is obtained: `bound_session_id = str(bracket_binding["session_id"])` at BRK 2497, assigned only after `validate_calibration_bracket_binding` returned non-None (2477-2485; a None returns `calibration_bracket_binding_invalid` first). It is compared at 2638 (recording site) and 2663 (first failure site). An observation with no session has `bracket_session_id` None, which is `!=` the bound id, so it is another session's, as item 2 says; tested with `session=None` (test_item2, both sites). The fallback of item 2: `sealed_fallback = bound_observations is None` and `window_evidence = ... and not sealed_fallback` (2515-2516); with the fallback every decision is the sealed one (test_item2_unbound compares the two results with the four keys popped; probe P12 removes the fallback and the test errors). In the harvest the fallback is unreachable because the harvest returns before the call when the binding cannot be built (H 4569-4577) and `has_session_candidates` is true whenever a binding is passed (2455-2458).

Item 3(a): the first failure site (2661-2671) now returns stale only when `not window_evidence` or some systematic observation of the judged epoch carries the bound session id; probe P2 (`or True`) and P1 (treat every systematic as another session's) both fail tests. The recording side appends the name once and the sequences ascending (2634-2651; P14 reverses the order, detected).

The operative bound, the allowance (`max(drift, screen)`), the drift arithmetic and the preflight comparison (2729-2835) are untouched by the diff except for the return wrapping; I read the hunks line by line.

### 2. Does anything differ with `trigger_scope="sealed"` or omitted?

No. `finish` (BRK 2135-2158) returns `(result, reasons)` untouched unless `trigger_scope == "window_evidence"` and `result["acceptance"]` is not None. On every early refusal with an acceptance record, that record carries a `freshness` dict (2196-2203, 2224-2241, 2303-2322), so the `freshness["status"]` write cannot raise; with `acceptance` None (`not_required`, invalid window) the guard skips. The count fallback runs only when `scope_epochs` is set (after 2289), when `artifact` and `ledger_snapshot` both exist.

The sealed-identity test is real, not vacuous: it loads the pinned function bodies from `git show 0699abbb0:joulewise/calibration_bracketing.py`, rebinds them to the current module's globals (no helper changed in the diff), replays every call the existing bracket test module makes with the argument omitted and with `"sealed"`, compares both to the pinned result by equality and by canonical JSON, asserts the four new keys are absent, and requires more than 50 evaluator calls and more than 5 wrapper calls with both `passed` and `failed` statuses seen. Probe P17 (make `finish` attach the keys under `sealed` too) fails it; the unmutated control passes (15 s). Two limits: it covers the fixtures of `tests/test_calibration_bracketing.py` only, so the rehearsal-copy comparison the gates also require is a separate, not-executed item; and it needs 0699abbb0 reachable from the checkout it runs in (F6).

### 3. The governing test

`ERRATUM_3_ADMITTED_AT_EPOCH_S = 1791738000` (H 89) is 2026-10-11T17:00:00Z (computed). The test at H 4012-4015: not a bool, int or float, finite if float, and strictly `>` the constant. BETA attempts 4 and 5 (1791671820, 1791704340) are not governed (test item0 subtests; probe P8 makes the comparison `>=` and the equality subtest plus the ungoverned harvest test fail; probe P9 drops the finite guard and the `inf` subtest fails). `inputs.plan` is always a Mapping (`resolve_inputs`, H 1735-1737, raises `plan_not_an_object` otherwise), so the `__init__` read cannot crash on a missing plan. The value reaches the function only through `self.calibration_bracket["trigger_scope"]` at H 4610; probe P11 hard-codes `"window_evidence"` there and the ungoverned test fails. `grep` of `joulewise/`, `scripts/`, `analysis/` finds no other use of `trigger_scope`; the other wrapper callers (`joulewise/whole_window.py:707, 5551`, `scripts/run_campaign.py:7370`, `scripts/harvest_g2a_window.py:216`, `scripts/harvest_v5_g2b_window.py:735`) are unchanged and take the default `"sealed"`.

### 4. Items 6 and 8

Four keys under `acceptance.prospective_rederivation` with `"window_evidence"` only (BRK 2126-2131, attached at 2155). `recorded_only_triggers` is appended in code order doubling (2597), range (2621), systematic (2645): (c), (b), (a); probe P10 reorders and two tests fail. `freshness.status` is `fresh` when only recorded-only names were observed and no item-4 check failed (worked example, test_item6, test_item2); see F1 for the failed cases. `harvest.json.calibration_bracket` has exactly the ten keys of item 8(i), initialised with `evaluated` false, nulls and empty lists (H 4016-4027), and filled after the call (H 4611-4622) with sorted reasons; tested governed, ungoverned and not-evaluated (both governed states). `outputs["withheld/bracket-evaluation.json"]` is the SHA-256 `write_json_once` returns (H 4623; `write_once` returns `sha256_bytes(raw)`, H 1275-1283), recorded as the `derived/` entries are; probe P15 drops it and the governed test errors. `HARVEST_PROGRAM_FILES` has the four files (H 3888) and `harvest_checkout` is its only consumer.

Ruling on `corpus_doubling: null`: confirmed. Item 6's count is defined as "the largest per-epoch count of BRK 2544 to 2552", which exists only once the acceptance, the snapshot, its baseline and the set-aside list have all been authenticated; before that there is no such count, item 8 types the field `{...}|null`, no decision reads it (the flag condition is H 4626-4628; item 10's consumer compares its own evaluation with the same function), and a zero would be a number for a state that has no evidence. The implementation returns the count on refusals after `judged_epochs` exists (identity stale, off-ledger, binding, invalid bound, unclassifiable) using the same arithmetic as 2583-2591 (same `distinct` set keyed by `content_id`, same set-aside ids, same epoch test; read side by side), and null before (test item4 asserts `{"count": 43, ...}` for the binding cases and null for the ledger cases).

### 5. Mutation probes

Each row: mutated line (BRK unless marked H), module or test run, result. Every probe was restored before the next; every probe was detected.

| id | mutation | run | result |
|---|---|---|---|
| P1 | 2638 `if window_evidence and observation.bracket_session_id != bound_session_id` → `if window_evidence` | WindowEvidenceTests | FAIL test_item3_own_systematic_event_keeps_the_early_return |
| P2 | 2663-2664 own-session `any(...)` → `True` | WindowEvidenceTests | 7 FAIL (item1 wrapper success, item2 both subtests, item4 byte change, item4 refusals, item6, worked example) |
| P3 | 2780 failing set under window_evidence + range name | WindowEvidenceTests | 8 FAIL + 1 ERROR (item5 low capture ×3, rounding gap ×2, drift ceiling, item4 byte change, item6) |
| P4 | 2780 failing set + doubling name | WindowEvidenceTests | 4 FAIL (item3 doubling 48 and 49, item4 byte change, item6) |
| P5 | 2780 failing set → `set()` | WindowEvidenceTests | FAIL test_item4_byte_change_remains_the_only_failing_name_at_second_site |
| P6 | 2818 drift ceiling `and not window_evidence` | WindowEvidenceTests | FAIL test_item5_low_capture_drift_ceiling_still_fails |
| P7 | 2768 pre-screen `and not window_evidence` | WindowEvidenceTests | FAIL test_item5_own_preflight_failure_branch_stays_as_sealed |
| P8 | H 4015 `t0 >` → `t0 >=` | item0 + ungoverned harvest test | 2 FAIL (equality subtest; ungoverned flag) |
| P9 | H 4014 finite guard → `True` | item0 | FAIL (t0=inf) |
| P10 | 2621 range appended → inserted at 0 | WindowEvidenceTests | 2 FAIL (item4 byte change, item6 order) |
| P11 | H 4610 scope hard-coded `"window_evidence"` | ungoverned harvest test | FAIL |
| P12 | 2516 drop `and not sealed_fallback` | WindowEvidenceTests | ERROR test_item2_unbound_uses_sealed_decisions_whatever_scope |
| P13 | 2341 `if stale_fields` → `and trigger_scope == "sealed"` | WindowEvidenceTests | FAIL test_item4_identity_change_still_fails_first |
| P14 | 2641 sequences sorted descending | WindowEvidenceTests | FAIL test_item6_keys_fixed_order_and_ascending_sequences |
| P15 | H 4623 digest not stored in `outputs` | governed worked-example harvest test | ERROR (KeyError) |
| P16 | 2576 unclassifiable return `and not window_evidence` | WindowEvidenceTests | FAIL test_item4_unchanged_refusals_and_order |
| P17 | 2137 `finish` attaches keys under `sealed` too | SealedIdentityTests (pinned source from saved file) | FAIL; unmutated control OK |

Tests that assert too little: none of the checks named in the charge survived deletion or inversion. One vacuous case, F4 (the `True` subtest of item 0).

### 6. The two stale-state fixtures

Erratum 2 recovery (`RecoveryStaleGateTests.test_gate_governed_stale_bracket_and_source_less_recovery`): executes what it claims within its seams. It builds a stored verdict whose bracket is the sealed stale result (no `pre`, no `launch_lineage`, `calibration_bracket_set.pre` None), validates it with `ww._validated_evaluation_basis`, sets `row_provenance.source_campaign_manifests` to `[]`, a governed t0, then runs the real `calibration()`, `whole_window()` and screen stages with the snapshot, acceptance, binding and wrapper mocked to the synthetic fixture, and asserts: scope `window_evidence`, bracket passed, survivor rescreen with authenticated manifests, `whole_window.not_passed` present, no `calibration.bracket_acceptance_failed`, and no `EXCLUDE_WINDOW` code among the flags of those stages. The ledger, acceptance and binding loaders are mocked, so it proves the stage logic, not the file path; the file path is the sealed one and unchanged.

GAMMA-shaped (`HarvestScopeTests.test_gate_gamma_shaped_stale_window_removing_codes`): a full `window.harvest()` over the GAMMA-shaped helper window with an analysis manifest, a hand-built stale stored verdict, `bracket-binding.json` = `{}`, the wrapper seamed to the synthetic evaluator, and `seams.runner` replaced by a function that runs a sealed evaluation (asserting stale) and writes a report with F5-2 FAIL, exit 1. It pins the full window-removing list (three codes from fixture gaps) and shows a fresh control gives the same list, with `g3.recompute_failed` and `whole_window.not_passed` added by the stale state only. What remains unproven, and my ruling, is F3.

### 7. Outside the admitted text

No new flag code, exclusion or refusal. Two representations the text does not state: F1 (freshness forced to `stale` on item-4 failures) and the `"threshold": 48` literal (F7). The edit to the checkout test is not a weakening (F5).

## Findings

**F1. NOTE (representation).** BRK 2156-2157: under `"window_evidence"` with a validated binding, `finish` sets `acceptance.freshness.status = "stale"` on every non-empty reason, including drift above the ceiling, pre above the screen, missing or old endpoints, an invalid bound, an unclassifiable observation, an incomplete candidate list and a bad binding, where the sealed function leaves `fresh`. The erratum defines `stale` as the word written "for an acceptance on which a trigger has been seen" (section 1) and item 6 gives only the `fresh` condition; the implementer read item 6 as a biconditional and pinned it (test_item5_low_capture_drift_ceiling_still_fails and test_item4_unchanged_refusals assert `stale`). `harvest.json.calibration_bracket.freshness` will therefore read `stale` for a governed window removed for drift with no trigger on record. No decision reads the field (flag: H 4626-4628; item 10's consumer evaluates with the same function). Disposition: flag, not refuse. If the lead wants the sealed representation instead, the minimal change is deleting BRK 2156-2157 and the two assertions.

**F2. NOTE (ruling confirmed).** `corpus_doubling: null` on refusals before an authenticated count exists is right, for the reasons in charge 4. The count on the later refusal paths is the item-6 arithmetic reproduced in `finish` (BRK 2139-2152); descriptive only.

**F3. SHOULD-FIX, before a governed GAMMA attempt is armed; not before the pin.** The GAMMA gate's seam replaces `scripts/check_window_provenance.py`, and both fixtures hand-build the stored verdict instead of running the sealed writer in the stale state. What the seams leave unproven: (a) the real checker's behaviour over a stale basis with no calibration pair and no `launch_lineage`, and over the real `bracket-binding.json`; by reading H 7507-7580 every outcome of that subprocess (spawn failure, timeout, exit code outside {0, 1}, report absent, F5-2 FAIL or SKIP, other FAIL rows) maps to `g3.recompute_failed` or `g3.assertion_failed`, both `DISCLOSE` in the sealed catalog, so no window-removing code can come from the checker; (b) the sealed writer's row shape in the stale state: the only `EXCLUDE_WINDOW` code reachable from the stored verdict is `whole_window.member_failures_unreadable` (H 4913-4919), which needs the `member_failures` key absent or the list malformed; the writer always writes the key as a list (`scripts/run_campaign.py` 8572 and 10161), but no run of it in the stale state was executed. Minimal closure: on the rehearsal copy, with the live ledger (row 456 present), run the sealed writer and the real checker over a GAMMA-shaped archive and print `exclude_window_reasons`; the erratum's gate text asks for exactly that list. BETA's arm does not wait on this: the G3 step runs only on a pack whose root holds `analysis_manifest_v3.json` (H 7517), and the harvest stages BETA exercises are the ones the recovery fixture executes. Whether the BETA pack carries that manifest I did not verify (pack trees are not in this checkout).

**F4. NOTE (vacuous subtest).** test_item0's `(True, False)` case cannot detect removal of the bool guard at H 4013: `True == 1`, which is below the constant either way. The guard itself is correct per item 0; no bool value above the constant exists, so no fix is possible or needed.

**F5. NOTE (the edited checkout test is not a weakening).** tests/test_harvest_b5_window.py 2627-2651: the edit (i) adds `joulewise/calibration_bracketing.py` to the expected file list, which item 8(iii) requires, and (ii) passes seams: the three defaults the helper would pass anyway (tests/test_harvest_b5_window.py 779-781) plus `harvest_checkout=checkout_reader`, which calls the real `h.harvest_checkout()` and snapshots `git status` at the moment of the read, replacing the pinned comparison against the status after the harvest. The program's obligation is unchanged. The edit accommodates the implementer's in-tree `TMPDIR`; with `TMPDIR` outside the tree the pinned text (file list updated) passes against the new program (4 tests OK, 47.8 s, in my scratch git copy). 0699abbb0's own message records this test being "restored to the pinned text" once before; the lead may prefer the pinned text again. No fix required.

**F6. NOTE.** `SealedIdentityTests` runs `git show 0699abbb0:...` in the checkout the tests run from; in a checkout where that commit is not reachable it errors rather than skips. Fine for the desk checkout; never run in the measurement clone.

**F7. NOTE.** `"threshold": 48` is a literal (BRK 2592, 2148) while the decision uses `2 * corpus_n` of the artifact (BRK 2531); equal for the issued acceptance; the text says 48.

No BLOCKER was found. No finding requires a code change before the pin.

PASS
