**Verdict: FIX FIRST.** The CONTRACT lens found two blockers, both executed against the base tree (`2ea6a7ec`) and the head (`7647bb2e`). In each, a routing change also changes idle behaviour, which §2 forbids. I did not re-run the full V1 suite; I executed only the probes listed at the end.

## Findings

| # | Sev | Where | Finding | Witness | Cure |
|---|---|---|---|---|---|
| B1 | **BLOCKER** | `scripts/run_night.py:1005-1029` (`_custody_row`), `:1033`, `:1644` (`_write_result`) | `_write_result` now calls `_artifact_list(…, plan)`, which reads the wrapper's kind. `_custody_row` catches only a missing file or a directory. An idle wrapper that is unreadable, not UTF-8 or ambiguous now raises (ValueError or UnicodeDecodeError) out of `_write_standard_refusal_result`. The chain-digest-mismatch refusal (`run_night.py:3177`) is exactly this case. Consequences: no `result.json`, `run_night` exits with a traceback before `_finish_reporting`, and the courier falls to dead-man. With no readable result, `zero_capture_facts` reports the night not clean, so the refusal fast-retry cannot release a successor. A calibration plan whose wrapper is missing and that has no C5 receipt also raises. The base wrote the result in all four cases. The same read now fails inside `_evidence_cleanup_error` (`:1382`); `optional()` swallows that, so idle cleanup repair is silently skipped where the base ran it. | w1: base `RESULT_WRITTEN` ×4; head `RAISED ValueError probe payload kind ambiguous` / `UnicodeDecodeError` / `night payload kind unavailable`, `result.json exists: False` | Reporting paths must never raise on kind. In `_write_result`, `_durable_record` and `_courier_argv`, catch `(OSError, UnicodeError, ValueError)` from `_custody_row`. Fall back to the historical inventory (the calibration and idle rows have identical `artifact_names`) and log the kind error as a diagnostic. Keep typed refusals for dispatch only: cleanup, probe and installer. |
| B2 | **BLOCKER** | `joulewise/evidence_night.py:645-646`, called via `selected_candidate_row` at `:306-334` | `candidate_state` now reads the custody `chain.zsh`, its sidecar, and the chain source in the measurement clone. `uninstall` (`:1893`, comment: "Cleanup deliberately does not validate plan bytes … accepts malformed/retired published plans"), `veto` (`:1591`) and `verify` (`:1533`) all enter through `candidate_state`. Idle candidates the base accepted now refuse, with **new refusal texts**. Result: an installed idle agent cannot be uninstalled through the tool once its measurement clone is archived (iCloud offload) or its custody wrapper is removed. Arm-time tamper refusals also change text: from sealed-state "sealed-byte drift: …" to the new messages. | w2: base `ACCEPTED` ×4; head `REFUSED candidate chain source unreadable` / `candidate payload kind unreadable` / `candidate chain digest mismatch` (clone_archived, chain_removed, chain_tampered) | Restore the base `candidate_state` check (`prepare.json` kind must equal the row), as it was. Do the wrapper/source binding check in the paths that already validate sealed bytes: `sealed_state`, `render_notice`, `notice_subject`, `clone_census`. `uninstall` must keep working without the wrapper. |
| S1 | should_fix | `tests/test_night_kinds.py:~452-457` vs `joulewise/zero_capture_facts.py:104-106` | The handler/`successor_release` refusal in `zero_capture_facts` is untested. T3 writes `chain.started` before asserting `.clean` is False, so the assertion holds whatever the dispatch does. | Mutant M3 (handler check deleted; `evidence` decided by kind or `envelope_index_name`): T3 **OK**, mutant survives | Remove `chain.started` before that assertion, or assert `scan_complete is False`. Re-run M3. |
| S2 | should_fix | `scripts/run_night.py:1014-1027` | `_custody_row` adds two kind sources that are not the chain source. (1) A C5 receipt with `payload_kind` None is mapped to `"calibration"`. (2) Idle is inferred from plan fields: `plan_id` prefix, `receipt_class`, `registration_path`. Both are limited to reporting and cleanup, and the idle and calibration inventories are identical, so the impact is small today. But the plan-field rule is an unreviewed classification that B1+ will inherit. | reasoning | Keep it reporting-only (see B1 cure) and name it in the ALLOW reason. Never let this path feed cleanup or successor dispatch. |
| N1 | nit | `scripts/gen_evidence_night.py:21-27` | The chain-template refusal moved ahead of plan parsing and the receipt-class check. For a plan with the wrong receipt class **and** an alternate template, the refusal text changes from "evidence requires v2 DIAGNOSTIC_NO_PACK" to "…alternate chain refused". A malformed plan with an alternate template now gets a GenerationRefusal instead of a parse error. Idle default-template refusals are unchanged. | reasoning | Put the matching after `NightPlan.from_mapping` and the receipt-class check. |
| N2 | nit | `tests/test_kind_dispatch_literals.py` | The token scan cannot see symbolic idle branches: `evidence_night.py:590` (`if kind != KIND:`) and the `KIND` default arguments at `:158` and `:219`. | reasoning | Add `\bKIND\b` to the tokens, with ALLOW reasons. |
| N3 | nit | `joulewise/zero_capture_facts.py:1-5, 101` | The "standard library only" docstring was quietly rewritten. The new lazy `night_gate` import can raise ImportError, which is outside the except tuple. | reasoning | Add ImportError to the tuple, or state the dependency plainly. |
| N4 | nit | `run_night.py:1132` | `_durable_record` re-reads and re-probes the wrapper once per artifact, which is redundant and lets the kind change partway through the copy loop. | reasoning | Select the row once before the loop. |

## Accepted clauses
- 1(a): all ten T1 sites take their row from the candidate. No bare `state["kind"]` authority was added; the `prepare.json` kind that already existed is now cross-checked. The `prepare` CLI keeps idle as the default. The damage in B2 is where the check runs, not a second authority.
- 1(b): subject label and notice clauses come from the row; the corecaptured sentence is gated on `corecaptured_at_arm_and_t0`. `GOLDENS` and the `test_refusal_parity` expected values were not edited (0 changed golden lines in the diff).
- 1(c): manifest, executor and wrapper prefix come from the row; two rows sharing one chain source refuse; `quiet_predicate_campaign` is untouched.
- 1(d): installer receipt, installer render, driver probe, artifact inventory, courier and cleanup each refuse typed for a row with no handler. None falls into calibration: the installer uses `elif`/`else` and raises, and the probe returns 2 with a refusal code.
- 1(e): gate change is routing only, with no registration payload-kind comparison. Existing gate refusals are intact, and mutant M2 (gate handler check deleted) is killed.
- 1(f): the test-only third row is injected by patching the table, not added to the module. The literal guard pins exact lines, catches duplicates, and gives each entry a one-line reason (N2 is its blind spot).
- §2: no scored row, no scored manifest, no new entry in `RULED_REGISTRATIONS`, no armable kind.

## Probes (all under /tmp)
```
git archive 2ea6a7ec | tar -x -C /tmp/b0lens-opus/base
# w1: _write_standard_refusal_result(chain_digest_mismatch), idle plan, wrapper = ambiguous / non-UTF-8 / unknown kind; calibration plan with no wrapper and no receipt
python3 -B /tmp/b0lens-opus/w1.py {base|worktree} {ambiguous|nonutf8|unknown|cal}
[base] ambiguous RESULT_WRITTEN artifacts= 1
[head] ambiguous RAISED ValueError probe payload kind ambiguous result.json exists: False
[head] nonutf8 RAISED UnicodeDecodeError 'utf-8' codec can't decode byte 0xff …
[head] unknown RAISED ValueError probe payload kind ambiguous …
[head] cal RAISED ValueError night payload kind unavailable …   (base: RESULT_WRITTEN ×4)
# w2: candidate_state on a completed idle stage (the entry to uninstall, veto and verify)
python3 -B /tmp/b0lens-opus/w2.py {base|worktree} {intact|clone_archived|chain_removed|chain_tampered}
[base] * ACCEPTED ×4 ; [head] intact ACCEPTED
[head] clone_archived REFUSED Refused candidate chain source unreadable
[head] chain_removed REFUSED Refused candidate payload kind unreadable
[head] chain_tampered REFUSED Refused candidate chain digest mismatch
# M2 (/tmp/b0lens-opus/m2: gate handler check deleted): T3 + gate-literal test
FAIL: test_unhandled_third_row_routes_or_refuses_across_shared_entries
AssertionError: 'night_probe_error' != 'night_chain_digest_mismatch'   -> KILLED
# M3 (/tmp/b0lens-opus/m3: zero_capture_facts handler check deleted): T3
Ran 1 test in 8.910s  OK   -> SURVIVES (S1)
```
The mutation trees are `git archive 7647bb2e` copies. For the fixture's `git archive`, `cdc05e9b` was fetched into a throwaway `/tmp` repo. Nothing was written to the worktree, the canonical checkout, custody or LaunchAgents.
