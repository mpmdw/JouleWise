# Executing review: Erratum 3 trigger scope in the block-5 harvest program

Reviewer: Opus 5.5, independent seat (wrote none of the change). 2026-10-11.
Reviewed commit `e4b4145a071871c8a3cca85c976433b89b15befd` against pin `0699abbb0881ce64b39c46ba07de568cc3848260`,
read in the worktree `/Users/edr/code/JouleWise-wt-harvest-trigger-review` (left untouched; `git status` empty at
the end). Specification: `docs/process_traces/2026-10-block5/trigger-erratum/ERRATUM.md` sections 4 and 5.

Abbreviations: **BRK** = `joulewise/calibration_bracketing.py`, **H** = `joulewise/b5/harvest.py`, **T** =
`tests/test_harvest_b5_trigger_scope.py`; line numbers are those of the reviewed commit unless "pin" is written.
"Sealed scope" is `trigger_scope="sealed"` (the rule as registered); "window scope" is
`trigger_scope="window_evidence"` (the erratum's rule). "Bound" means the call carried a bracket binding that
`validate_calibration_bracket_binding` accepted.

Structure only: this report holds no energy, power, workload duration or member name. The millisecond values are
synthetic fixture bounds or the erratum's own.

## 0. Result

No BLOCKER. Three SHOULD-FIX, all test gaps (no production line needs to change). Sealed results are identical to
the pinned program's on 752 evaluator inputs and 28 wrapper inputs. 38 mutants: 33 killed, 5 survived (2 are
equivalent, 3 are the test gaps below).

One step of the brief was **not executed, on purpose**: `discover_calibration_candidates` over the real ledger.
It opens every valid capture's directory at the path the ledger records, and 12 of those 14 paths are under
`/Users/edr/night-b5/`, which my blinding instruction forbids me to open. I ran everything else of the pre-arm
shape with candidates rebuilt from ledger rows (section 3), and the snippet in section 3.3 carries the real
discovery call for the lead to run.

| id | class | title |
|---|---|---|
| S1 | SHOULD-FIX | No test has a systematic row that carries a content id (the real shape); the ascending sort of `other_session_systematic_sequences` is untested and its deletion survives |
| S2 | SHOULD-FIX | Item 7's flag condition ("status other than passed, OR any reason") has no test that separates `or` from `and` |
| S3 | SHOULD-FIX | The GAMMA-shaped gate cannot show a stale-state cause for the three removal codes its own control already carries; assert the removal flags' payloads equal the control's |
| N1 to N12 | NOTE | representation and gate-mechanics points, section 8 |

## 1. What was executed

All runs used `/opt/homebrew/bin/python3.13`, `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`, a scratch
`TMPDIR` under `/Users/edr/.jwtmp/review4/`, and a scratch clone of the reviewed commit at
`/Users/edr/.jwtmp/review4/copy` (`git clone --shared --no-checkout` of the worktree, then a checkout of
`e4b4145a0`; nothing was written to the worktree or the main repository). The machine was loaded by the whole
suite (load average 8 to 14).

| run | result |
|---|---|
| `-m unittest -v tests.test_harvest_b5_trigger_scope` | 26 tests, OK, 117 s |
| `-m unittest tests.test_calibration_bracketing` | 95 tests, OK (1 skipped) |
| `-m unittest tests.test_harvest_b5_window.HarvestCheckoutTests` | 4 tests, OK |
| `probes/differential.py` (mine) | 752 cases, 0 sealed differences |
| `probes/wrapper_diff.py` (mine) | 28 cases, 0 sealed differences |
| `probes/prearm_probe.py` (mine, real ledger, blinding guard) | section 3 |
| `probes/stale_fixtures.py` (mine) | section 5 |
| `probes/mutants.py` (mine), 38 mutants | section 4 |
| `probes/sort_gap.py`, `probes/bytechange_diff.py`, `probes/realcheck.py` (mine) | S1, section 2, section 3 |

The probes and their logs are copied to `review/probes/` and `review/logs/` beside this file. The implementer's
497-test targeted set was not rerun (the brief limits me to single modules); its three components above pass.
`BRK` at the pin hashes to `ddb7db11…4037`, equal to the measurement clone's copy and to the erratum's figure.

## 2. Item-by-item conformance

"Matches" means the code does what the admitted text says and I ran something that would have failed otherwise.

| item | where | matches | executed evidence |
|---|---|---|---|
| 0 constant | H 89 (`ERRATUM_3_ADMITTED_AT_EPOCH_S = 1791738000`) | yes | T `test_item0…` asserts the value; Addendum 4 on main (`SEAL_RECORD.md` 557, 560) reads the same epoch |
| 0 governed test | H 4012 to 4015: not bool, int or float, finite if float, `>` | yes; it is the exact negation of the pin's Erratum 2 test (pin H 5223 to 5227) | mutants H01 (`>=`) and H03 (finiteness) killed; H02 (bool) survives and is equivalent: a bool is 0 or 1 and can never exceed the constant |
| 1 argument, two values, other raises | BRK 2118, 2123 to 2124 (evaluator); 2855, 2860 to 2861 (wrapper) | yes | M12 killed. M13 (wrapper check deleted) survives and is equivalent: every wrapper path calls the evaluator, which raises |
| 1 pass-through in every call | BRK 2871, 2896, 2912, 2964, 2981 | yes | W01 to W04 and M14 each killed by `test_item1_wrapper_passes_scope_at_every_call_site` |
| 1 sealed identity | `finish()` BRK 2137 to 2158 touches the result only when `trigger_scope == "window_evidence"` | yes | section 2.1; M19 killed |
| 1 harvest's one call | H 4605 to 4610, scope from H 4018 | yes | H04, H05, H11 killed |
| 1 no other caller changed | diff touches BRK and H only; `whole_window.py` 707 and 5551, `run_campaign.py` 7370 unchanged | yes | `git diff --stat` |
| 2 own session | BRK 2497 (`bound_session_id` from the validated binding), compared at 2638 and 2663 | yes | M01, M04 killed; a row with no session is treated as another session (T `test_item2…`, both subtests) |
| 2 fallback when unbound | BRK 2515 to 2516 | yes for every decision; see N1 for the output keys | M10, M11, M20, M21 killed; real ledger, section 3.2 |
| 3(a) other-session systematic | BRK 2631 to 2650 (record), 2661 to 2673 (no early return), 2780 (not in the failing set) | yes | M02, M05, M09 killed; real ledger gives `[456]` |
| 3(a) own systematic takes the early return | BRK 2661 to 2665 | yes | M03 killed by `test_item3_own_systematic_event_keeps_the_early_return` |
| 3(b) valid capture outside the range | BRK 2620 to 2630 | yes | M08 killed; `test_item5_own_low_capture…`, `…rounding_gap…` |
| 3(c) doubling at or above 48 | BRK 2594 to 2601 | yes | M07 killed; counts 48 and 49 pass |
| 3 second-site failing set | BRK 2780 to 2785: exactly `{"protocol_or_estimator_byte_change"}` under window scope | yes | M05 (full set) and M06 (empty set) killed |
| 4 acceptance missing or unissued | BRK 2195 to 2222 | unchanged | differential `acceptance_none`, `acceptance_unissued` |
| 4 snapshot absent, refused, wrong baseline | BRK 2242 to 2258 | unchanged | differential `no_snapshot`, `refused_snapshot`, `baseline_bad` |
| 4 incomplete candidate list; custody not loaded | BRK 2397 to 2424; wrapper 2956 to 2967 | unchanged | differential `cand_short`, `cand_dup`, `cand_empty`; wrapper `custody` |
| 4 set-aside list unresolved | BRK 2580 to 2584 | unchanged | differential `disposed_none` |
| 4 `identity_field_change` | BRK 2296 to 2300, 2356 to 2359 | unchanged | differential `identity_change` |
| 4 binding missing or invalid | BRK 2461 to 2514 | unchanged | differential `binding_none`, `binding_empty`, `binding_tampered`, `plan_sha_wrong` |
| 4 unclassifiable class | BRK 2572 to 2577 | unchanged | differential, `abandoned` rows (30 cases) |
| 4 own post above the screen | H 4531 to 4535 (`calibration.capture_invalid`), H 4585 to 4593 (`calibration.binding_failed`, return before the call); builder BRK 1472 to 1488 | unchanged | T `test_item5_own_post_systematic…` (executed harvest, evaluator not called, `evaluated` false) |
| 4 endpoints missing or old; not of the bound session; not finite | BRK 2690 to 2696; 2714 to 2715; 2520 to 2523 and 2718 to 2724 | unchanged | differential `window_far`, `window_unbracketed`, `cand_nan` |
| 4 own pre above the screen | BRK 2768 to 2778 (does not read the failing set) | unchanged | differential, p = 37.0 ms fixtures |
| 4 byte change | BRK 2535 to 2540, then 2780 to 2800 | unchanged | M06 killed; `probes/bytechange_diff.py` |
| 4 own drift above the ceiling | BRK 2818 to 2819 | unchanged | T `test_item5_low_capture_drift_ceiling_still_fails` (20.5 and 36.4 ms) |
| 4 order | every `return` became `return finish(...)`; no check moved (read from the diff, hunk by hunk) | yes | differential: same reasons as sealed wherever the erratum does not change the decision |
| 5 p above the screen | harvest path unchanged; `calibration.no_bracket` | yes | T `test_item5_pre_systematic_abort…` (executed over an aborted synthetic session) |
| 5 q above the screen | as item 4 | yes | as item 4 |
| 5 p or q below 21.93 ms | 3(b); bracket passes; drift still applies | yes | both slots tested; operative bound below 36.46 ms observed in the fixture |
| 5 rounding gap | 3(b) | yes | T `test_item5_rounding_gap…` |
| 5 inside the range | no event | yes | T `test_item5_inside_range…` |
| 5 own captures count toward doubling | BRK 2585 to 2593 counts every valid row | yes | counts 48 and 49 include the bound pair |
| 6 four keys, order (c), (b), (a), ascending sequences | BRK 2130 to 2135, 2155; appends at 2599, 2624, 2644; sort at 2640 | yes, with test gap S1 | M07 to M09, M16 killed; M17 (sort deleted) **survived** |
| 6 `corpus_doubling.count` = largest per-epoch count | BRK 2594 to 2596; late copy in `finish()` 2142 to 2154 | yes | M18 (`max` to `min`) survived: one judged epoch in every fixture and on the real ledger (N4) |
| 6 freshness | `fresh` unless a reason exists (BRK 2156 to 2157) | yes (N2) | M15 killed |
| 6 status and reasons | unchanged tail, BRK 2838 to 2839 | yes | worked example: passed, 45.031 ms, 14.531 ms, 2.5 ms |
| 7 flag | H 4626 to 4628, the pin's condition, byte for byte | yes, with test gap S2 | H10 killed; H09 (`or` to `and`) **survived** |
| 8(i) `calibration_bracket` object | H 4016 to 4027 (initial), 4613 to 4623 (after the call), 8140 (written) | yes | H08 killed; governed, ungoverned and not-evaluated objects asserted whole |
| 8(ii) outputs digest | H 4624 | yes | H07 killed |
| 8(iii) `HARVEST_PROGRAM_FILES` | H 3888 | yes | H06 killed (also by the edited checkout test) |

### 2.1 Sealed identity (my differential, not the lane's)

The lane's own test rebinds the pinned functions' code onto the new module's globals. That is sound only because
the diff touches nothing but the two functions (true: every hunk of the BRK diff lies inside
`evaluate_calibration_bracket` or `calibration_bracket_for_bundles`). My probe does not rely on that: it executes
the whole pinned file (`git show 0699abbb0:joulewise/calibration_bracketing.py`, SHA-256 `ddb7db11…4037`) as a
second module with its own globals and compares three calls per input: pinned, new with `trigger_scope` omitted,
new with `"sealed"`. Comparison is `==` on `(result, reasons)` and on canonical JSON.

- 710 synthetic cases from the lane's fixture builder: 5 bound pairs x 4 doubling counts x 3 systematic lists x
  3 owners x 3 classes, each bound, plus on 14 base fixtures the early refusals: no snapshot, refused snapshot,
  bad baseline, no binding, empty binding, tampered binding, wrong plan digest, window bounds NaN, infinite,
  reversed, equal, far, unbracketed, `require_bracket` false, identity change, binding-field change, short,
  duplicated, NaN and empty candidate lists, acceptance missing, acceptance unissued, estimator byte change,
  set-aside unresolved, and the unbound variant.
- 42 real-ledger cases: for each of the 7 finalized two-slot sessions, the ledger as a byte prefix ending at that
  session's post capture and the full ledger (478 entries, stale by row 456), each bound, without a binding, and
  with a window starting now. Candidates were rebuilt from ledger rows (section 3.1).
- Sealed outcome classes covered: passed (22), not_required (20), and 12 distinct refusal reasons (all of
  item 4's except custody, which the wrapper probe covers).
- **Result: 0 differences.** No sealed result carries any of the four new keys. Wrapper: 28 cases, 0 differences.

`finish()` (BRK 2137 to 2158), read and exercised:

- *Can it change a sealed result?* No. Its only writes are inside `if trigger_scope == "window_evidence" and
  result["acceptance"] is not None`. With the guard removed (M19) three tests fail.
- *Can it raise?* Not on any path I could construct (752 inputs x window scope, none raised where sealed did
  not). Every place that sets `result["acceptance"]` to a dict gives it a `freshness` key (BRK 2196, 2208, 2224,
  2302), so `result["acceptance"]["freshness"]["status"] = "stale"` is safe; `prospective_rederivation` is
  created by `setdefault` when the early refusals have none. `artifact` and `ledger_snapshot` are read only when
  `scope_epochs` is set, which happens after both are authenticated (BRK 2287). With the acceptance-None guard
  removed (M22) it raises `TypeError`, and a test catches that.
- *One deviation from sealed evaluation order that is harmless:* the pin's systematic test is a short-circuiting
  `any(...)`; the new code builds the full list first (BRK 2631 to 2635). Same truth value; the differential
  confirms.

Where sealed and window scope return the same reason, the bodies are equal apart from the four keys and
`freshness.status`, except nine byte-change cases where both fail `calibration_acceptance_bound_stale` for
different registered causes (sealed: the systematic early return or a longer `stale_triggers`; window scope:
`stale_triggers` = byte change only). That is the erratum's item 3, not a defect (`probes/bytechange_diff.py`).

Where they differ (170 cases), sealed failed `calibration_acceptance_bound_stale` with
`prospective_rederivation_required` and `stale_triggers` drawn only from the three demoted names, and the call
was bound. No window-scope pass violated an own-evidence check: for all 124 passes I recomputed
max(p, q) + max(|p − q|, screen) and checked p against the pre screen, the drift against the ceiling, and that the
endpoints belong to the bound session.

## 3. Real-shape probe on the calibration ledger

### 3.1 What I opened, and what I did not

Opened: the measurement clone's `runs/calibration_observation_ledger.jsonl`, `configs/calibration/
calibration_ledger_head.json` and `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`
(read-only), and three keys of `/Users/edr/night-custody/v5-b5-beta-a5-20261011T0739Z/night_plan.json`
(`t0_epoch_s`, `hazard_window.bracket_session_id`, `plan_id`). Every probe that touched real data ran under a
Python audit hook that raises on `open`, `listdir` or `scandir` of anything under
`/Users/edr/night-custody/v5-b5-*` (other than that plan file), `/Users/edr/night-b5/` or
`/Users/edr/night-archive/harvest-v5-b5-*`. The hook never fired.

**Not executed: `discover_calibration_candidates` on the real snapshot.** For each valid row it calls
`_candidate_from_observation` (BRK 1807 to 1863), which opens the capture directory at the row's
`custody_locator`. On this ledger 12 of the 14 rows that discovery would load have a locator under
`/Users/edr/night-b5/<attempt>/<runs root>/…` (6 under ALPHA attempts, 6 under BETA; the other 2 are under
`/Users/edr/night-g2a/`; `probes/locators.py`). That tree is on my forbidden list with no exception, so I did
not run it. The snapshot loader with `verify_custody=False` and the
binding builder open no capture directory (confirmed by the hook).

In its place the probe builds each `CalibrationCandidate` from the ledger row itself (artifact digests, exact
bound lexeme, capture wall time, identity and T1 bindings, session fields). The evaluator compares exactly these
fields against the ledger rows, so every decision and every recorded key below is what the real run will give
**provided the 14 capture directories load**. What the stand-in cannot show is item 13(a)'s second "must": that
discovery returns 14.

### 3.2 Results (window starting now, one hour long; structure words only)

- Snapshot: head sequence 478; refusal reasons `[]`.
- Valid, live, non-derivation, current-capture-method observations of finalized sessions: **14**. (The erratum's
  17 valid post-cutoff captures less 3 valid pre captures of aborted sessions.) Candidates (stand-in): 14.
- One judged epoch. Post-cutoff live rows: 17 `valid`, 1 `systematic-invalid` (sequence 456; it carries a
  content id and a session id).
- The worktree's default acceptance is the clone's artifact (same authenticated digest).

| call | status | reasons | freshness | observed_triggers | trigger_scope | recorded_only_triggers | corpus_doubling | other_session_systematic_sequences |
|---|---|---|---|---|---|---|---|---|
| no binding, sealed | failed | `calibration_acceptance_bound_stale` | stale | systematic | absent | absent | absent | absent |
| no binding, window scope | failed | `calibration_acceptance_bound_stale` | stale | systematic | `window_evidence` | `[]` | `{count: 41, threshold: 48}` | `[]` |
| bound to the last finalized session, sealed | failed | `calibration_acceptance_bound_stale` | stale | systematic | absent | absent | absent | absent |
| bound to the last finalized session, window scope | failed | `instrument_calibration_bracket_missing` | stale | systematic | `window_evidence` | `[systematic]` | `{count: 41, threshold: 48}` | `[456]` |

("systematic" = `new_systematic_failure_challenges_preflight_screen`.)

Readings:

1. Without a binding the function falls back to the sealed decisions, as item 2 requires. In that fallback
   `other_session_systematic_sequences` is **empty although row 456 is on the ledger**. The pre-arm run must
   therefore pass the binding, as item 13(a) says; a run without it would record an empty list and hide the
   input to rules 13(b) and 13(c).
2. With the binding the three recorded keys match the erratum's worked example for today's ledger (41, `[456]`).
   The call fails `instrument_calibration_bracket_missing` because a window starting now has no post capture;
   that is expected of a hypothetical window and is not one of the two "must" conditions.
3. **A binding can be built from plan-time, unblinded inputs only.** `build_calibration_bracket_binding` needs
   the session's `window_id`, `plan_id`, `plan_sha256`, `evidence_root_id` and `runs_root`; all five are in the
   session's open receipt in the ledger, and the builder reads nothing else. The last finalized two-slot session
   is `v5-b5-beta-a5-20261011T0739Z-calibration` (post at sequence 478); the plan file names the same session
   id. `runs_root` is used as a string only.

Exploratory by-product (labelled as REG 4844 and item 12 require; it changes no verdict, `claim_usable`, cause
key or attempt history): the differential also evaluated, for each finalized session, a hypothetical window lying
between that session's two captures. On ledger prefixes ending at sequences 402 to 442 both scopes pass. On the
prefixes ending at 468 and 478 and on the full ledger, sealed fails `calibration_acceptance_bound_stale` and
window scope passes with `[456]` recorded and counts 39 and 41. These used stand-in candidates and no member
bundle; they are not the item-12 run over the archived ledger copy, which remains the lead's gate.

### 3.3 The pre-arm snippet (item 13(a))

Tested as written except the one marked line, which I replaced by the stand-in for the reason in 3.1. Run from
the pinned desk checkout with `PYTHONDONTWRITEBYTECODE=1`. `probes/prearm_probe.py <checkout> discover` is the
same code with the printing used above.

```python
import sys, time, json
from pathlib import Path
sys.path.insert(0, "/Users/edr/night-custody/desk/b5-harvest")          # the pinned desk checkout
from joulewise import calibration_bracketing as br
from joulewise import calibration_ledger as cl
from joulewise.schemas import CalibrationBracketingPolicy

CLONE = Path("/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18")
LEDGER = CLONE / "runs/calibration_observation_ledger.jsonl"
PIN = CLONE / "configs/calibration/calibration_ledger_head.json"
ACCEPT = CLONE / "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json"

acceptance = br.load_calibration_acceptance_bound(ACCEPT)
cutoff = acceptance["ledger_cutoff"]
snapshot = cl.load_calibration_ledger_snapshot(                          # as H 4488 to 4491
    LEDGER, PIN, require_committed_pin=False, verify_custody=False, mode="issuing",
    repo_root=CLONE, baseline_sequence=cutoff["sequence"], baseline_digest=cutoff["head_digest"])

# "must" 1: no refusal reasons
assert list(snapshot.refusal_reasons) == [], snapshot.refusal_reasons

# the universe the evaluator and the wrapper count (BRK 2366 to 2385, 2936 to 2955)
finalized = {s.session_id for s in snapshot.bracket_sessions if s.state == "finalized"}
registered = [o for o in snapshot.observations
              if o.disposition == "valid" and not o.is_historical_import
              and br._capture_pipeline_refusal_for_observation(o) is None
              and (o.bracket_session_id is None or o.bracket_session_id in finalized)
              and not br._is_derivation_kind_observation(o, snapshot)]

candidates = br.discover_calibration_candidates(snapshot, mode="issuing")   # NOT executed by the reviewer (3.1)

# "must" 2: every capture directory loaded
assert len(candidates) == len(registered), (len(candidates), len(registered))

# the last finalized session that has a pre and a post slot (derivation sessions have d01..d12 slots instead)
last = max((s for s in snapshot.bracket_sessions if s.state == "finalized" and "post" in s.finalized_slots),
           key=lambda s: s.finalized_slots["post"].sequence)
binding = br.build_calibration_bracket_binding(
    snapshot, session_id=last.session_id, window_id=last.window_id, plan_id=last.plan_id,
    plan_sha256=last.plan_sha256, evidence_root_id=last.evidence_root_id, runs_root=last.runs_root)
pre = last.finalized_slots["pre"]
now = time.time()
result, reasons = br.evaluate_calibration_bracket(
    candidates, window_start_s=now, window_end_s=now + 3600.0,
    bindings={**dict(pre.identity_epoch), **dict(pre.t1_bindings)},
    policy=CalibrationBracketingPolicy(require_bracket=True, calibration_bracket_max_drift_s=0.005),
    ledger_snapshot=snapshot, bracket_binding=binding, bracket_window_id=last.window_id,
    bracket_plan_id=last.plan_id, bracket_plan_sha256=last.plan_sha256,
    bracket_evidence_root_id=last.evidence_root_id, bracket_runs_root=last.runs_root,
    trigger_scope="window_evidence")
pro = result["acceptance"]["prospective_rederivation"]
assert result["bracket_binding"] is not None                              # the binding validated: not the fallback
print(json.dumps({
    "snapshot_refusal_reasons": list(snapshot.refusal_reasons), "head_sequence": snapshot.head_sequence,
    "candidates": len(candidates), "registered_valid": len(registered),
    "last_finalized_session": last.session_id,
    "status": result["status"], "reasons": list(reasons),                 # expected: failed, bracket missing/stale
    "observed_triggers": pro["observed_triggers"], "recorded_only_triggers": pro["recorded_only_triggers"],
    "corpus_doubling": pro["corpus_doubling"],
    "other_session_systematic_sequences": pro["other_session_systematic_sequences"]}, indent=1))
```

Notes for reuse. (a) `calibration_bracket_max_drift_s` is a legacy field the evaluator records as
`legacy_obsolete_not_an_acceptance_comparator`; any float works, or load the campaign policy as H 4600 does.
(b) The `assert result["bracket_binding"] is not None` matters: reading 1 of 3.2. (c) `corpus_doubling` can be
`None` if the call is refused before the count exists (section 7), so read `.get("count")` defensively.
(d) Expected values today, if discovery loads all 14: candidates 14, registered 14, observed and recorded-only
`[systematic]`, doubling `{count: 41, threshold: 48}`, sequences `[456]`.

## 4. Mutation probes

Each mutant is one deleted or inverted check, applied to a fresh copy of the tree and run against
`tests.test_harvest_b5_trigger_scope` (which also replays `tests.test_calibration_bracketing` through the lane's
identity test). H12 also ran `tests.test_harvest_b5_window.HarvestCheckoutTests`. Exact old and new text of
each: `probes/mutants.py`; first failing tests: `logs/mutants-summary.txt`.

| id | mutated line | outcome |
|---|---|---|
| M01 | BRK 2638 `!= bound_session_id` to `==` | killed (7 failures; `test_item2…`, worked example) |
| M02 | BRK 2661 to 2665 condition restored to the pin's `if observation_stale_triggers:` | killed (10) |
| M03 | BRK 2663 to 2664 own-session clause deleted | killed (`test_item3_own_systematic_event_keeps_the_early_return`) |
| M04 | BRK 2663 `==` to `!=` | killed (11) |
| M05 | BRK 2780 window scope gets the full sealed failing set | killed (18) |
| M06 | BRK 2780 window scope gets the empty set | killed (`test_item4_byte_change_remains…`) |
| M07 | BRK 2598 recorded-only append (c) deleted | killed |
| M08 | BRK 2623 recorded-only append (b) deleted | killed |
| M09 | BRK 2643 recorded-only append (a) deleted | killed |
| M10 | BRK 2598 `and window_evidence` deleted | killed (`test_item2_unbound…`) |
| M11 | BRK 2623 `and window_evidence` deleted | killed (`test_item2_unbound…`) |
| M12 | BRK 2123 to 2124 evaluator scope check deleted | killed |
| M13 | BRK 2860 to 2861 wrapper scope check deleted | **SURVIVED**, equivalent: the evaluator raises on every wrapper path; no outcome changes |
| M14 | BRK 2981 scope not passed in the wrapper's deciding call | killed |
| W01 to W04 | BRK 2871, 2896, 2912, 2964 scope not passed in each early call | killed (4 of 4) |
| M15 | BRK 2156 `finish()` no longer writes `stale` on a failure | killed |
| M16 | BRK 2142 `finish()` late doubling count deleted | killed |
| M17 | BRK 2640 `sorted(` to `list(` | **SURVIVED**: changes the order of a recorded list, no window outcome. Test gap S1 |
| M18 | BRK 2595 `max(` to `min(` | **SURVIVED**: changes a recorded count only when two judged epochs exist; there is one on the real ledger. N4 |
| M19 | BRK 2139 `finish()` scope guard deleted | killed (lane identity test and two others) |
| M20 | BRK 2515 `sealed_fallback` never set | killed |
| M21 | BRK 2516 `and not sealed_fallback` deleted | killed |
| M22 | BRK 2139 acceptance-None guard deleted | killed |
| H01 | H 4015 `>` to `>=` | killed (3) |
| H02 | H 4013 bool exclusion deleted | **SURVIVED**, equivalent: `True`/`False` compare as 1/0 and are never greater than the constant; no outcome changes |
| H03 | H 4014 finiteness deleted | killed (`inf` case) |
| H04 | H 4610 harvest always passes `"sealed"` | killed (both stale-state gates and the worked example) |
| H05 | H 4610 harvest always passes `"window_evidence"` | killed (ungoverned stale window) |
| H06 | H 3888 `calibration_bracketing.py` removed from `HARVEST_PROGRAM_FILES` | killed |
| H07 | H 4624 outputs digest not recorded | killed |
| H08 | H 8140 `calibration_bracket` object not written | killed |
| H09 | H 4626 flag condition `or` to `and` | **SURVIVED**: would keep a window whose status is not `passed` but has no reason (only `not_required`, unreachable under the sealed policy). Test gap S2 |
| H10 | H 4626 flag never emitted | killed |
| H11 | H 4018 scope chosen from `governed` inverted | killed (17) |
| H12 | H 3928 checkout `status_lines` off by one (sensitivity of the edited test) | killed by the edited test |

Tally: 38 mutants, 33 killed, 5 survived (M13 and H02 equivalent; M17, M18, H09 real gaps, none of which changes
a governed window's outcome on reachable inputs).

## 5. The two stale-state fixtures

Executed through `probes/stale_fixtures.py`, which runs each test as written, then variants.

**Erratum 2 recovery with a source-less stored verdict (`RecoveryStaleGateTests`).** It does what it claims, in
stages. Executed for real: the sealed evaluation of the stale fixture (no endpoints); `ww.build_evaluation_basis`
and `ww._validated_evaluation_basis` on that stale bracket (accepted; no `launch_lineage`; `pre` null); the
harvest's `calibration()`, `whole_window()` and the NEG-8 screen, which takes the `survivor_rescreen` route with
`claim_campaign_manifests_authenticated` references; the verdict's `source_campaign_manifests` is `[]`. Asserted:
window-removing codes `[]`, `whole_window.not_passed` present, scope passed `window_evidence`, bracket `passed`.
Counterfactual (mine): forcing the desk evaluation to the sealed scope makes the test fail, and mutant H04 fails
it too, so the fixture is sensitive to the thing it gates. Replaced by mocks, hence not proven here: the ledger
snapshot loader, the terminal pin, the binding builder and the wrapper's reading of member bundles (the wrapper
is replaced by an evaluator call over the synthetic fixture). Not run: every other harvest stage
(`neg8_bound`, G3, member-level collectors, the exclusion function, `harvest.json`).

**GAMMA-shaped window (`test_gate_gamma_shaped_stale_window_removing_codes`).** A whole harvest runs over a
hazard-pack window with an analysis manifest; the G3 handler builds its `--full-window` command and calls the
runner seam once. Result, stale and governed: removal list `calibration.capture_battery_unmeasured`,
`neg8.bound_not_derived`, `neg8.screen_failed`; identical in the fresh control. The stale state adds
`g3.recompute_failed` and `whole_window.not_passed`, both `DISCLOSE`. My variants of the seam:

| G3 seam returns | codes added over the fresh control | removal list equals the control's |
|---|---|---|
| report with F5-2 FAIL (the lane's case) | `g3.recompute_failed`, `whole_window.not_passed` | yes |
| report with seven assertions all FAIL | plus `g3.assertion_failed` | yes |
| exit code 2, no report | `g3.recompute_failed`, `whole_window.not_passed` | yes |
| `TimeoutExpired` | plus `records.collector_failed` | yes |
| (counterfactual) same window with t0 equal to ADMIT | plus `calibration.bracket_acceptance_failed` (`EXCLUDE_WINDOW`) | no, as it should not |

All added codes are `DISCLOSE` in the sealed catalog (`configs/campaigns/v5_claim_25g83/flag_catalog.json`,
`5d77c725…`), which I checked directly because the fixture uses the test catalog (`b34a420f…`, same effects for
these codes). The G3 handler (H 7507 to 7580) can emit only `g3.not_applicable`, `g3.assertion_failed` and
`g3.recompute_failed`, whatever the checker does; all three are `DISCLOSE`.

**No window-removing code arises from the stale state in either fixture.**

What the GAMMA fixture leaves unproven:

1. `scripts/check_window_provenance.py` itself is never executed in the stale state. Which assertions it fails,
   and whether it exits 0/1 or crashes, is unknown. By the handler's construction the harvest's response is
   bounded to the three `DISCLOSE` codes above (my four variants), so this cannot remove a window, but the record
   a governed GAMMA window will actually carry is not known until the real checker runs (the lead's gate).
2. The stored verdict in this fixture is not an authenticated one (`whole_window.verdict_unauthenticated` fires
   in both arms). The authenticated-basis path under a stale bracket is exercised only in the recovery fixture.
3. The three removal codes are present in both arms, for the same recorded cause (I compared the flags'
   `observed` and `expected` payloads: equal, 4 flags). So the NEG-8 bound and screen stages never reach a
   passing state here, and the list comparison alone could not see the stale state causing one of those same
   three codes. That is S3.

## 6. The one edited existing test

`tests/test_harvest_b5_window.py`, `HarvestCheckoutTests.test_both_records_name_the_commit_…` (2628 to 2657).
Two edits: the expected file list gains `joulewise/calibration_bracketing.py` (required by item 8(iii)); and the
independent `git status` is now taken at the moment the checkout record is read, through the `harvest_checkout`
seam, instead of after the harvest.

**Not a weakening.** The real `h.harvest_checkout()` still produces the record, and the comparison is still
against a separate `git status` call. Executed: the old form passes with scratch outside the tree and fails with
scratch inside it (`(False, 270) != (False, 448)`), which is the implementer's stated reason; the new form passes
both ways; and mutant H12 (record's `status_lines` off by one) fails the new form. One thing this test no longer
does is run the default `Seams.harvest_checkout` wiring; T `test_items1_7_8_governed…` runs a default-seam
harvest and checks the record's file digests, so the wiring stays covered.

## 7. The lead's ruling: `corpus_doubling: null` when no authenticated count can exist

**Confirmed.**

- Item 6 defines the count as "the largest per-epoch count of BRK 2544 to 2552". That count is defined over an
  authenticated snapshot, the judged epochs and the resolved set-aside list. When the acceptance is missing or
  unissued, the snapshot is absent, refused or of the wrong baseline, or the set-aside list cannot be resolved,
  none of those exists. A number there would be an invented one; `0` would read as "far from 48".
- Item 8 already types the harvest field `{"count": N, "threshold": 48}|null`, and `null` breaks no consumer
  equality under item 10(ii), since consumer and harvest call the same function.
- Every such refusal has a reason, so the window is removed by `calibration.bracket_acceptance_failed` whatever
  the field holds. No outcome depends on it.

What the code does, executed (T `test_item4_unchanged_refusals_and_order`, the differential): `null` for a
missing, refused or wrong-baseline snapshot, a missing or unissued acceptance, and an unresolved set-aside list;
the real count for refusals that come after the snapshot is authenticated (identity change, incomplete candidate
list, binding missing or invalid, unclassifiable class), computed afterwards in `finish()` without moving any
check. Two consequences to carry: the lead's attempt-history tooling (item 11) and the pre-arm run must tolerate
`null`; and when the window bounds are invalid or `require_bracket` is false the four keys are absent altogether,
because there is no `acceptance` object to hold them (N3).

## 8. Findings

### SHOULD-FIX

**S1. The systematic rows in every fixture have no content id; the real one has.** `fixture()` (T 179 to 184)
builds systematic rows with `content_id=None`. Such rows enter `new_observations` through the branch that is
already sorted by sequence (BRK 2560 to 2570). Row 456 of the live ledger has a content id and enters through
the other branch, which is ordered by content id (BRK 2555 to 2559). Hence deleting the sort (M17) survives, and
the real-shape path is exercised only by my real-ledger probe. Executed proof (`probes/sort_gap.py`): two
other-session systematic rows at sequences 456 and 458 with content ids `"f"*64` and `"0"*64` give `[456, 458]`
in production and `[458, 456]` in the mutant. Item 13(b) and (c) read this list.
*Test to add* in `WindowEvidenceTests`: build `self.fixture(systematics=(456, 458))`, replace the two systematic
rows (`o.sequence in (456, 458) and o.disposition == "systematic-invalid"`) with
`content_id="f"*64` and `"0"*64` respectively, evaluate with window scope, assert status `passed`,
`other_session_systematic_sequences == [456, 458]` and `recorded_only_triggers == [SYSTEMATIC]`.

**S2. Item 7's condition is not pinned by any test.** `calibration.bracket_acceptance_failed` appears in no test
outside T, and T's cases are (failed, with a reason) and (passed, no reason), which `and` satisfies as well as
`or` (H09 survived). The line is the pin's, unchanged, and the only reachable difference today is the status
`not_required`, which the sealed policy does not produce; still, this is the line that decides whether a
governed window is removed.
*Test to add* in `HarvestScopeTests`: patch `br.calibration_bracket_for_bundles` to return, in two subtests, a
copy of a passing assessment with `status` set to `"not_required"` and reasons `()`, and a passing assessment
with reasons `("instrument_calibration_mismatch",)`; assert `calibration.bracket_acceptance_failed` is in
`window.codes()` in both, and that `record["calibration_bracket"]["status"]` and `["reasons"]` carry the values.

**S3. The GAMMA gate's control shares all three removal codes.** Section 5, point 3. The erratum asks the
fixture to show "the window-removing codes that result" from the stale state; equality of two non-empty lists
shows it only for codes the control lacks.
*Test to add* (cheap form) at the end of `test_gate_gamma_shaped_stale_window_removing_codes`: for every flag in
`window.flags()` and `control.flags()` whose code is in `exclude_window_reasons`, assert the sorted
`(code, observed, expected)` triples are equal after replacing the two window directory names. I ran exactly
this comparison and it holds (4 flags). The complete form, a GAMMA fixture with a derived NEG-8 bound and
authenticated references so that the control's removal list is empty, and one run of the real provenance checker
over a stale synthetic window, belongs to the lead's GAMMA gate that the implementer's flag F2 already names.

### NOTE (representation or gate mechanics; none changes a window's outcome)

- **N1.** In the unbound fallback the function takes the sealed decisions (item 2) but still writes the four
  keys with `trigger_scope: "window_evidence"`, empty lists and the count. Item 6 says the keys are present
  "with `window_evidence` only", so this is within the letter; a reader of the record cannot tell the fallback
  from a bound evaluation except by `bracket_binding` being null. The harvest cannot reach the fallback with a
  session window (it always passes a binding). Operational consequence: reading 1 of section 3.2.
- **N2.** Under window scope, `freshness.status` is set to `stale` whenever a bound evaluation has a reason
  (BRK 2156 to 2157), including refusals where the sealed word is `fresh` (drift over the ceiling, endpoints
  missing, incomplete candidate list) and without a `reason` or `stale_triggers` key in those cases. This is the
  implementer's reading of item 6's "fresh when … no item-4 check failed" and is consistent between harvest and
  consumer; the same failure in an ungoverned window reads `fresh`. 235 of my cases show the word change.
- **N3.** With invalid window bounds or `require_bracket` false there is no `acceptance` object and the four
  keys are absent; the harvest reads them with `.get` and writes null and empty lists.
- **N4.** `corpus_doubling.count` uses `max` over judged epochs and `finish()` holds a second copy of the count
  formula (BRK 2142 to 2154). Both agree on every input I ran. `max` to `min` survives (M18) because every
  fixture and the real ledger have one judged epoch. If a continuation epoch is ever issued, add a two-epoch
  case.
- **N5.** `"threshold": 48` is a literal (BRK 2153, 2595) while the trigger itself uses `2 * corpus_n`. Equal
  for this acceptance, and 48 is what the erratum prints.
- **N6.** `_Harvest.__init__` reads `inputs.plan.get(...)` without the `isinstance(plan, Mapping)` guard that
  the Erratum 2 test has (H 4012 against pin H 5222 to 5223). Every constructor path passes a dict.
- **N7.** Section 5's rehearsal gate asks for byte-identical `derived/` output against pin `0699abbb0` under
  the sealed scope. `derived/exclusions.json` carries `harvest_checkout` (H 8099), whose `files` gains a key by
  item 8(iii) and whose `head` differs between any two pins. The gate must exempt that object, as pin 3's gate
  must already have done for `head`. The rehearsal comparison is opt-in (`B5_REHEARSAL_COMPARE=1`) and I did not
  run it.
- **N8.** If the window's own session and another session both held a systematic row, the other one would be
  recorded in `recorded_only_triggers` before the early return. Unreachable with a validated binding.
- **N9.** The lane's identity test proves the two function bodies against the new module's helpers. Sufficient
  because the diff changes no helper; section 2.1 does not depend on that.
- **N10.** The implementer's report header reads `status: blocked`, `acceptance: needs_ruling` for the item-6
  question; section 7 answers it. Its claims I checked by execution hold: item table, the two gate results, the
  single edited test, protected files untouched (diff stat: four files).
- **N11.** Item 13(a)'s "valid, non-derivation, finalized-session observations" is, in the code's universe, also
  restricted to live rows of the current capture method. The snippet counts the code's universe, so the two
  numbers it compares are computed alike.
- **N12.** Scratch left in place: `/Users/edr/.jwtmp/review4/` (about 0.5 GB: the clone `copy`, logs, probe
  scratch). A safety check refused my cleanup command; nothing there is needed once this report is read.

APPROVE WITH FIXES (S1, S2, S3)
