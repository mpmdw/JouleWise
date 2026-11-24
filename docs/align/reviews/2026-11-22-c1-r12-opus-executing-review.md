# Executing review — PR #896 C1 round 12 (c5b8b8047..3daea0447)

- **Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), Claude Code agent session, 2026-11-22. One of the two executing seats under gate_policy rule 3 (the other is Fable 5.2, working independently; the Sol seat cannot run on this machine).
- **Non-author:** I did not write, co-write or prompt any reviewed commit. This session first saw them through `git show`. **Process note:** all three commits carry `Co-Authored-By: Claude Opus 5.5`, the same model as this seat. My independence is per session, not per model family; Fable 5.2 is the cross-family seat.
- **Repository:** `/Volumes/JW-EXT/scratch/mythos-build-896/repo` at `3daea0447f571683a97ae8579c3a7436a0fc32c7`. I did not modify it. At the start, `git status --short` showed only a pre-existing ` M docs/align/next_arm_packet.md`, not mine.
- **The repository moved during this review, not by me.** Between 06:45 and 06:49 (local time) another session committed 48b50958c, ddd369dc6 and fcfc0dee4 (author Edr, `Co-Authored-By: Claude Opus 5.5`), whose titles address a head-pin agreement, capture slots and the session-status probe. It also left uncommitted edits in v4_registration.py, reserve_calibration_window_bracket.py, validate_powermetrics_fiducial.py and a run report (mtime 06:49:17). Every command I ran in the repository finished before 06:45, on 3daea0447: focused tests 05:38–05:48, census 06:01–06:03, HAZARD module 06:14–06:20. Probes and mutants used my `git archive 3daea0447` copy, which I confirmed byte-identical (blob hashes) after the last mutant. **This paper covers c5b8b8047..3daea0447 only; I did not review those later commits.**
- **Execution:** focused tests in the repository. Probes and mutants in a `git archive 3daea0447` copy at `$TMPDIR/opus-r12/tree`, tools in `$TMPDIR/opus-r12/tools`. Python 3.13.18. Synthetic inputs only: the frozen suite's invented history bundle through `adapter.Attempt`, plus temp-directory ledgers I built with the ledger's own append functions. One test process at a time; no background process left.

## Coverage

| Commit | Path | Blob after commit |
|---|---|---|
| c5b8b8047 (base) | joulewise/calibration_ledger.py | e1ef407f57da4613aa72ee0976878c3ebc0a144c |
| c5b8b8047 (base) | joulewise/align/apple/v4_registration.py | 985461864a50879e761694bcd29cc5c38505c3d5 |
| c5b8b8047 (base) | scripts/reserve_calibration_window_bracket.py | 613383c27b82959828e41dbdbc83b389e27354fd |
| c5b8b8047 (base) | scripts/validate_powermetrics_fiducial.py | 4f7e4d9004c39ab1123e1305f4114ac22a9a2551 |
| c5b8b8047 (base) | configs/gates/hazard_refusals.json | c77f5c9087270363bac40c34caa95e7e5dfbc105 |
| c5b8b8047 (base) | tests/align/c1_closure_lite/adapter.py | 17c4b22ab99088d1f8d4c80022667fb85df3fee1 |
| c5b8b8047 (base) | tests/align/test_c1_closure.py | d7c29ae84ef4b05aed43b7c3780e2cf06c56210d |
| 7f2155750528ce6e0469ec226857356a8aa1a22b | tests/align/c1_closure_lite/adapter.py | 1cf4cc2326fe9a826df43a04f118b641515e2da1 |
| 7f2155750528ce6e0469ec226857356a8aa1a22b | tests/align/test_c1_closure.py | ce38b4653537daff4a1f887e1a254c4bfcbdc076 |
| bc224942e83b4833a860d0824f297709fa69c727 | joulewise/calibration_ledger.py (NUMBER-BEARING, F8) | 37fa093f0a2b8f7e62b94f770e43a3abb4effcb3 |
| 3daea0447f571683a97ae8579c3a7436a0fc32c7 | joulewise/align/apple/v4_registration.py | 8fdb4db7a32e684d3b69c8555e7f2ca181b839d9 |
| 3daea0447f571683a97ae8579c3a7436a0fc32c7 | scripts/reserve_calibration_window_bracket.py | 81418de78c39e3c6db64a0c3424a829a05a3eb9a |
| 3daea0447f571683a97ae8579c3a7436a0fc32c7 | scripts/validate_powermetrics_fiducial.py | 5bf434e92005b408a9996386c9b3ecfa26ed0f76 |
| 3daea0447f571683a97ae8579c3a7436a0fc32c7 | configs/gates/hazard_refusals.json | abcad516da893a145f58cfa2b1983b7f5468e947 |

The test files are unchanged by bc224942e and 3daea0447 (same blobs as at 7f2155750), and calibration_ledger.py is unchanged by 3daea0447. So the spec commit precedes both fix commits (PIPELINE §3). `git diff c5b8b8047..3daea0447 -- tests/align/c1_closure_lite/suite tests/align/c1_closure_lite/SUITE.sha256` is empty, so the frozen 94 cases and their manifest are byte-identical. The adapter.py hook defaults to the old `b'{}\n'` literal, so the frozen tape's desk files keep the same bytes.

## Verdict: ADMIT-WITH-FIXES

No HIGH. I found no honest-mistake input that preflight admits and a consumer then consumes. bc224942e is correct for what it changes: the default and every existing caller behave as before, and only the C1 preflight passes `probe_live_writer=False`. The four named regressions and `tests.test_calibration_ledger` pass. On seven synthetic ledger states, the read-only pre-reserve decision equals the reservation's lease-held decision in every case.

Two MED remain. MED-1 is in the fix itself: on the reservation's resumable-session route the shared pre-reserve function still takes a writer lease. The `.lock` file it leaves in S makes the attempt unarmable, against the ruling's "Preflight must neither acquire a writer lease nor append". MED-2 is the ruling's general clause: four more capture/reservation agreements are decidable from prepared inputs, and preflight admits each of them while the capture refuses before hardware capture. LOW items are test gaps found by surviving mutants. Mutation: 18 mutants, 12 killed. Of the 6 survivors, 5 are LOW-1 to LOW-4 and 1 changes nothing on C1 inputs. Both MEDs should be fixed, with named regressions, before C1 is armed.

## Findings

### MED-1: On the resumable-session route the read-only pre-reserve call takes a writer lease and leaves `<ledger>.lock` in S; install and arm then refuse

`pre_reserve_readiness` (reserve_calibration_window_bracket.py:420–444) calls `calibration_session_status` whenever readiness is blocked, the call is not strict, and the code is not `LEDGER_CUSTODY_INVALID`. `calibration_session_status` always probes for a live writer (calibration_ledger.py:5723, `writer_lease_is_live`). That probe acquires a nonblocking writer lease, and the acquisition creates the lock sidecar beside the ledger. bc224942e's flag reaches only `calibration_readiness`, so `probe_live_writer=False` does not cover this call. Under `main`'s lease the same probe returns early, because the current lease is held, so `main` is unaffected. The route is taken when the starting ledger already holds an open session whose id is the reservation's `--session-id` (the reservation's resumable route). If the session is absent, `SESSION_NOT_FOUND` is raised before the probe, so the rollback and other negative cases do not reach it. The committed `configs/campaigns/align_v4/plan_tree.json` reservation template has no `--pre-reserve-strict`, so C1 uses the non-strict route.

Reproduction, executed:
- `readiness_equivalence.py` (temp ledger, one open session with the reservation's id, HAZARD arguments, non-strict). The read-only call returns `blocked`, the same as the lease-held call. Before the call the ledger directory held `calibration_observation_ledger.jsonl`; after it, also `calibration_observation_ledger.jsonl.lock` (size 0). A trace at `_open_slot_sidecar` gives `pre_reserve_readiness:429 → calibration_session_status:5723 → writer_lease_is_live:4010 → CalibrationWriterLease.acquire:3721`. With `--pre-reserve-strict` the call raises `calibration_pre_reserve_not_ready` and the directory is unchanged.
- `probe_r12.py ...test_p7_resumable_session_preflight_side_effects`. The fixture attempt's starting ledger is one open `fixture-session` receipt, built with `append_bracket_session_receipt` using the C1 plan id and SHA-256. The packet builder exits 0 (admitted), and afterwards `S/runs/` holds `calibration_observation_ledger.jsonl.lock`. Then `c1_arm_preflight`, install and direct arm all refuse: `packet_kit_mismatch: unlisted staged file: runs/calibration_observation_ledger.jsonl.lock`. Observed `(cli, arm, host_cli, host_arm) = (2, 'refuse', 0, 0)`. Ledger bytes unchanged.

Severity MED. It fails an explicit ruling requirement. `pre_reserve_readiness`'s docstring ("take no lease and append nothing") is wrong on this route. bc224942e's own change is correct for `calibration_readiness`, but its flag does not reach the session-status call that the shared function makes. A state that the reservation's pre-reserve decision accepts becomes a refused arm, through a file that preflight created. No number is admitted. Reachability needs a prepared starting ledger that already holds this attempt's open session. At launch the reservation's append then either replays an identical receipt or refuses `RESERVATION_IDENTITY_CONFLICT`, depending on identity vectors measured at launch; neither outcome is decidable at preflight.

Fix: let the read-only caller suppress the session-status liveness probe too. For example, add a `probe_live_writer` parameter to `calibration_session_status` (calibration_ledger.py, so number-bearing) and have `pre_reserve_readiness` pass it through. Add a named regression: a starting ledger with the attempt's own open session leaves `S/runs/` unchanged at build, install and arm.

### MED-2: Preflight still admits captures whose session, attempt, custody locator or head pin cannot match the reservation

The capture refuses before its writer lease, sampler launch and any hardware capture when its prepared slot binding differs from the reservation's open receipt (`_validate_slot(ledger_snapshot=preflight_snapshot)` at validate_powermetrics_fiducial.py:1733 → `_validate_reserved_bracket_slot` 1507–1577). The capture's values come from argv: `--session-id`, `--attempt-id`, custody locator `normalize_calibration_custody_path(--output-root / --attempt-id)` (2538–2539), and `--head-pin`. The reservation's come from its own argv. `_check_consumers` compares none of these: v4_registration.py contains no reference to session_id, attempt_id or custody_locator, and the capture's `--head-pin` is only `view.locate`d (1277). Ruling item 1 asks for "every consumer refusal that can be decided from prepared inputs, including agreements between consumers", and 3daea0447's message claims it.

Reproduction, executed (`probe_r12.py`). Each probe edits only the pre capture in the fixture tree, runs the production builder, delivers the packet, and runs install and direct arm. The reservation's own `reservation_inputs` + `append_bracket_session_receipt` then reserve on a private copy of the starting ledger, and the capture's `_validate_reserved_bracket_slot` runs on the rendered capture arguments:

| Probe | Edit (pre capture) | build, cli, arm, host_cli, host_arm | Capture's own slot check |
|---|---|---|---|
| p0 control | none | 0, 0, admit, 1, 1 | admit |
| p1 | `--attempt-id fixture-other` (reservation `--pre-attempt-id fixture-pre`) | 0, 0, admit, 1, 1 | `calibration_reserved_slot_mismatch` |
| p2 | `--session-id fixture-other-session` | 0, 0, admit, 1, 1 | `calibration_reserved_slot_mismatch` |
| p3 | `--output-root` relative `other_validation` (locator `…/other_validation/fixture-pre` vs reserved `…/instrument_validation/fixture-pre`) | 0, 0, admit, 1, 1 | `calibration_reserved_slot_mismatch` |
| p4 | `--head-pin` = the r11 retired pin `{sequence 7, head_digest 7…7}` (reservation keeps the default) | 0, 0, admit, 1, 1 | `calibration_reserved_slot_mismatch` |

The last step is the consumer's own function on a ledger that the reservation's own functions reserved. I did not run the capture CLI. For p2 the CLI may refuse earlier, at `declared_session_shape` (`SESSION_NOT_FOUND`), still before the lease. These seams predate this diff. The committed align_v4 template binds the session, attempt and output root from the same bindings as the reservation, and it gives the capture no `--head-pin`, so the reservation's pin is the default. A mismatch therefore needs an edited tree or a hand-edited binding, which is the same vector the round-11 regressions use.

Severity MED under the brief's rule: preflight admits, and the consumer refuses before host measurement. Fix: in the capture branch, compare `--session-id` with the reservation's `--session-id`, `--attempt-id` with `--{slot}-attempt-id`, and the capture's normalized locator with `--{slot}-custody-locator`, using `normalize_calibration_custody_path`. Require the capture's `--head-pin` to select the reservation's pin (same `view.locate` result), or judge it with the consumer's pin relation. Add one named regression per field and slot.

### LOW-1: No C1 regression pins the HAZARD pin relation at preflight (mutant R3 survives)

Preflight passes `hazard=True`, so a head pin that the physical chain contains but that lags it (the erratum's back-to-back state) admits, as the HAZARD reservation does. Changing it to `hazard=False` refuses that state with `calibration_reservation_head_mismatch` (executed in `readiness_equivalence.py`). Yet R3 survives the rollback regression, whose only control uses an exact pin. The ruling asks to "preserve the consumer's existing pin-relation semantics". Fix: add a control whose starting ledger is ahead of a contained pin (for example, an aborted earlier session), and which must admit on both routes.

### LOW-2: Desk policy precedence (epoch, then T1) has no repository test (R10 and R11 survive)

Swapping the desk files at the preflight call site (R10), or swapping the precedence in the shared `_desk_power_policy` (R11, which also changes what `main` records), survives `test_r11_capture_power_policy…`. R11 also survives `tests.test_reserve_calibration_hazard.DeskIdentityTests`. Both test fixtures give the two desk files the same policy, or only one file names one. At head the precedence is right: my `p6` (epoch `ac_high_power`, T1 `ac_low_power`) admits matching captures and refuses `ac_low_power`. By reading, it would kill both mutants; I did not run `p6` against them. Fix: add `p6` as a named control.

### LOW-3: The strict/non-strict distinction at preflight is untested (R4 survives)

Preflight passes `pre_reserve_strict=args.pre_reserve_strict`. Forcing `True` survives, because only the resumable route (MED-1) separates the two, and no test reaches it. The MED-1 regression would close this.

### LOW-4: The default live-writer probe in `calibration_readiness` has no killing test in `tests.test_calibration_ledger` (B3 survives)

Changing the new parameter's default to `False` turns off the contention probe for every non-enforcing default caller (`recover_calibration_ledger.py` readiness), and the 95 tests stay green. This gap predates the diff: no test there exercised the non-enforcing probe before either. Now that the probe can be turned off, one assertion that the default still reports `calibration_live_writer_contention` while another owner holds the lease would pin bc224942e's "default unchanged". My equivalence run shows the behavior is correct at head.

### Checks that found nothing

- **bc224942e default and callers.** With the default `probe_live_writer=True`, the new condition `enforcing_under_lease or not probe_live_writer` reduces to the old `enforcing_under_lease`. Production callers of `calibration_readiness`: reservation `main` (enforcing, via `pre_reserve_readiness`), capture `_begin_once` (enforcing, validate_powermetrics_fiducial.py:1814), and `recover_calibration_ledger.py` readiness (non-enforcing, default probe). None of them changes. The only `probe_live_writer=False` in the tree is v4_registration.py:1265, the C1 preflight. No test passes it.
- **Read-only vs lease-held decision** (`readiness_equivalence.py`, synthetic temp ledgers, no `JOULEWISE_C1_INPUTS`). States: exact pin, rollback pin (sequence 7), lagging pin (an aborted earlier session past a genesis pin), divergent pin, another open session, this session open, torn ledger. Each state ran with HAZARD on and off and with strict on and off, 28 cases. The preflight call (`enforcing_under_lease=False, probe_live_writer=False`) returned the same outcome as `pre_reserve_readiness` under a held `CalibrationWriterLease` in all 28. On HAZARD: exact → ready; rollback → `calibration_ledger_rollback`; lagging → ready (`calibration_reservation_head_mismatch` with HAZARD off); divergent → `calibration_reservation_head_mismatch`; other session open → `calibration_pre_reserve_not_ready`; own session open → `blocked` (returned, non-strict) or `calibration_pre_reserve_not_ready` (strict); torn → `calibration_ledger_recovery_required`. The read-only call left the ledger directory and bytes unchanged in 26 of 28; the two exceptions are MED-1. As a positive control, the same call with the default probe created `<ledger>.lock` in all 28. With a lease held by another owner, preflight returns ready, while the default probe and `main`'s own lease acquisition both give `calibration_live_writer_contention`. That is host state at launch, not a prepared input, so the ruling (no lease at preflight) puts it at use.
- **Reservation `main`.** The moved block is verbatim. A dedented `difflib` comparison of base `main`'s block (from `readiness = calibration_readiness(` to its `else:`) with the new function body shows only three changed lines. `enforcing_under_lease=True` becomes a parameter, `probe_live_writer=probe_live_writer` is added, and `if hazard is None` becomes `if not hazard`. `main` passes `hazard=hazard is not None`, so that is the old test. The old `else:` branch is now `if readiness.status == "ready":`, which is equivalent because the function returns a non-ready readiness only through the resumable route, where the old code also skipped that branch. `main` still passes `enforcing_under_lease=True`, so the new probe parameter is inert there. `_hazard_measured_identity` now calls `reserved_sampler()` and `reserved_power_policy()`, which compute the same expressions. `main` uses `args.pre_reserve_strict or args.verify_only`, and preflight uses `args.pre_reserve_strict`. These are equal on every C1 reservation preflight admits, because preflight requires `--execute`, which argparse makes exclusive with `--verify-only`. `tests.test_reserve_calibration_hazard` exercises HAZARD and legacy reservation `main` on stale, rollback, divergent, malformed, open-session and desk-identity cases. In the repository 16 of its 18 tests pass, and the 2 failures are wall-clock assertions (see Commands). On the scratch copy `DeskIdentityTests` (5) and the two non-timing HistoricalCustody tests pass, and mutant R14 shows that `main`'s lease-held flag is tested. I did not run a byte-level base-vs-head `main` diff this round.
- **Policy and sampler agreement.** The capture compares `dict(reserved["identity_epoch"]) != dict(identity_epoch)` with no normalization (`_normalized_vector` only selects fields), so exact equality of `--power-policy` is the consumer's own rule. Preflight reads the desk files with the reservation's own `_hazard_desk_object` and `reserved_power_policy`, from the same pinned paths and working directory the chain uses. Executed controls: desk epoch policy matched by both captures admits (named test); desk T1 only, `ac_low_power`, captures `ac_low_power` → admit on both routes (`p5`); desk epoch `ac_high_power` and desk T1 `ac_low_power`: captures `ac_high_power` → `(0, 0, admit, 1, 1)`, captures `ac_low_power` → `(2, 2, refuse, 0, 0)` with `C1 capture refuses: calibration_reserved_slot_mismatch {"capture": "ac_low_power", "field": "power_policy", "reservation": "ac_high_power"}` (`p6`). So the epoch, then T1, then plan precedence holds at preflight. Sampler, executed on `reserved_identity_refusal` with synthetic files: same path, `..` spelling, trailing slash and a symlink pass. A hard link and a byte-identical copy refuse, although the capture compares digests and would admit them. This is stricter than the consumer. The ruling asks for it ("a different executable refuses"), and a hard link to `/usr/bin/powermetrics` cannot be made from another volume, so it is not a finding. `--power-policy` absent refuses (`capture: null`); the capture's own `_live_capture_refusal` already refuses that case with `POWER_POLICY_REQUIRED`.
- **CALIBRATION_LEDGER.** `'CALIBRATION_LEDGER' in os.environ` now catches the empty value, and every non-empty value goes through `view.locate` (the R/S fence) before `check_ledger`. `check_ledger` compares resolved paths, then digests at start. The ruling's other cases are covered by the named test (unset, canonical, alias, empty, missing, outside with identical bytes and mode 0) and by round 9's `test_o2a_separate_same_byte_ledger_refuses_in_a_fully_pinned_stage` (same-byte copy inside S). Inside `consumer_environment` the chain's own exported value is used (v4_registration.py:1178). No other caller variable was given a veto by this diff.
- **Frozen suite.** Untouched (see Coverage). I did not run it, per the brief.

## Commands executed

Repository commands ran from `/Volumes/JW-EXT/scratch/mythos-build-896/repo`; `$S` is the scratch copy `$TMPDIR/opus-r12/tree`; `$T` is `$TMPDIR/opus-r12/tools`. Environment: no `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN`, `JOULEWISE_*` or `PYTHON*` set.

| Command | Result |
|---|---|
| `PYTHONPATH=tests:. python3.13 -B -m unittest -v align.test_c1_closure.C1ClosureTests.test_r11_capture_power_policy_must_equal_the_reserved_policy` | OK, 1 test, 111.3 s |
| `… C1ClosureTests.test_r11_capture_sampler_must_be_the_reserved_sampler` | OK, 1 test, 173.6 s |
| `… C1ClosureTests.test_r11_sole_rollback_head_pin_refuses_before_host` | OK, 1 test, 84.9 s |
| `… C1ClosureTests.test_r11_caller_ledger_pointer_is_refusal_only` | OK, 1 test, 114.2 s |
| `PYTHONPATH=tests:. python3.13 -B scripts/quick_suite.py --module tests.test_calibration_ledger` | PASS, 95 tests (1 skipped), 64.1 s |
| `PYTHONPATH=tests:. python3.13 -B scripts/quick_suite.py --module tests.hazards.test_refusal_allowlist` (census for the moved hazard_refusals.json rows) | PASS, 24 tests (1 skipped), 96.0 s |
| `PYTHONPATH=tests:. python3.13 -B scripts/quick_suite.py --module tests.test_reserve_calibration_hazard` | FAIL, 2 of 18 (319.9 s). Both failures are the fixture's wall-clock assertion ("custody refusal exceeded 3.0s budget + 2.0s cleanup tolerance"), and the expected refusal code is in the captured stderr (`calibration_pre_reserve_not_ready` for the open-session case). On the scratch copy the module failed 10 of 18 once. The class runs then failed a different single test each (StalePin passed 6/6 on rerun), so I treat it as timing-flaky on this machine. The diff adds no work to `main`'s path (verbatim move). I did not run it at base, so the attribution is by reading. I used named non-timing tests as mutation targets instead. |
| `git status --short` at start, after the focused tests (05:58) and at the end; `git log 3daea0447..HEAD`; `find . -name '*.pyc' -newer <start marker>` | unchanged at 05:58. At the end: three new commits and edits by another session (see header). No bytecode written by my runs |
| `git diff --stat c5b8b8047..3daea0447 -- …/suite …/SUITE.sha256`; `git rev-parse <commit>:<path>`; `git hash-object` on the scratch files | empty; blobs above; scratch pristine after mutants |
| `difflib` comparison of base `main`'s readiness block with the `pre_reserve_readiness` body | 3 changed lines (see "Reservation `main`") |
| (in `$S`) `PYTHONPATH=. python3.13 -B $T/readiness_equivalence.py <tmp>` | 28/28 agree; 2 directory changes (MED-1); see above |
| (in `$S`) inline trace of `_open_slot_sidecar` on the own-session state | stack in MED-1 |
| (in `$S`) inline `reserved_identity_refusal` on synthetic sampler paths | see "Policy and sampler agreement" |
| (in `$S`) `PYTHONPATH=$T:tests:. python3.13 -B -m unittest probe_r12.Probe.<p0…p7>`, one at a time | rows in MED-1 and MED-2; p5 and p6 under "Policy and sampler agreement" |
| (in `$S`) `$T/run_mutants.sh <ids>` → `$T/mutate_r12.py $S <id>`: apply one textual replacement (exactly one site), run its targets, restore the file | Mutants table. A first background chain was stopped with TaskStop during its census step, before any mutant was applied, and was rerun in foreground batches |

## Mutants

Scratch baselines with no mutation, all OK: power-policy test 57.4 s, sampler test 92.1 s, rollback test 69.4 s, ledger-pointer test 97.3 s, `tests.test_calibration_ledger` 95 tests 48.5 s, `DeskIdentityTests` 5 tests 152.8 s, and the two HistoricalCustody tests used for R14 (26.8 s). Each mutant is one textual replacement at exactly one site, then its target runs, then the file is restored. All four production files matched their 3daea0447 blobs after the last mutant.

| ID | Site (3daea0447 line) | Mutation | Target | Result |
|---|---|---|---|---|
| B1 | calibration_ledger.py:5841 (**bc224942e**) | `if enforcing_under_lease or not probe_live_writer` → `if enforcing_under_lease` | rollback test | **killed** (31.7 s). The retired-pin case lost its rollback detail. The default-pin control gave `(0, 2, refuse, 0, 0)`: the builder admitted, then install refused. That is consistent with the builder's probe leaving the lock file in S, as in MED-1; I did not capture the refusal text for this mutant |
| B3 | calibration_ledger.py:5791 (**bc224942e**) | default `probe_live_writer=True` → `False` | tests.test_calibration_ledger | **survived** (95 OK): LOW-4 |
| R1 | v4_registration.py:1262–1265 | delete the preflight `pre_reserve_readiness` call | rollback test | **killed**: retired pin admitted `(0, 0, admit, 1, 1)` |
| R2 | v4_registration.py:1265 | `probe_live_writer=False` → `True` | rollback test | **killed**, as B1 |
| R3 | v4_registration.py:1263 | `hazard=True` → `False` | rollback test | **survived**: LOW-1 |
| R4 | v4_registration.py:1264 | `pre_reserve_strict=args.pre_reserve_strict` → `True` | rollback test | **survived**: LOW-3 |
| R5 | v4_registration.py:1263 | `require_committed_pin=False` → `True` | rollback test | **survived**. In C1 the pin is read from R, and the fixture pin is committed at the execution commit, so this mutant changes nothing on these inputs. Not a finding |
| R6 | v4_registration.py:1292–1293 | delete the `reserved_identity_refusal` call | power-policy test | **killed**: pre and post mismatches admitted |
| R7 | v4_registration.py:1153–1156 | back to `if launch_ledger := os.environ.get('CALIBRATION_LEDGER')` | ledger-pointer test | **killed**: empty value not refused |
| R8 | v4_registration.py:1156 | drop `check_ledger(view.locate(…))` (no veto) | ledger-pointer test | **killed**: missing and outside admitted |
| R10 | v4_registration.py:1267–1269 | swap desk epoch / desk T1 arguments | power-policy test | **survived**: LOW-2 |
| R11 | reserve_calibration_window_bracket.py:60 | `_desk_power_policy` takes T1 before epoch (shared with `main`) | power-policy test; DeskIdentityTests | **survived** both: LOW-2 |
| R12 | reserve_calibration_window_bracket.py:72 | `reserved_power_policy` → `POWER_POLICY` | power-policy test | **killed**: desk-policy control `(2, 2, refuse, 0, 0)` |
| R13 | reserve_calibration_window_bracket.py:411 | drop `probe_live_writer=probe_live_writer` | rollback test | **killed**, as B1 |
| R14 | reserve_calibration_window_bracket.py:565 | `main`'s `enforcing_under_lease=True` → `False` | HistoricalCustody evicted + uncommitted-pin tests | **killed**: the legacy evicted-capture reservation succeeded (`0 == 0`) |
| F1 | validate_powermetrics_fiducial.py:2225 | drop the power-policy comparison | power-policy test | **killed** |
| F2 | validate_powermetrics_fiducial.py:2228 | `os.path.realpath(...)` → `str(...)` comparison | sampler test | **killed**: explicit equivalent spelling refused |
| F3 | validate_powermetrics_fiducial.py:2228 | drop the sampler comparison | sampler test | **killed**: pre and post mismatches admitted |

18 mutants: 12 killed, 6 survived (B3, R3, R4, R5, R10, R11). Of bc224942e's lines, the behavior line (B1) is killed and the default (B3) survives.

## Fix-round delta (2026-11-22): 3daea0447..062698aff

- **Scope:** delta review of the fix diff only (gate_policy rule 4), requested by the coordinator. Same reviewer and seat as above. All four commits carry `Co-Authored-By: Claude Opus 5.5`. I did not write, co-write or prompt them; I first saw them land during the original review (see header).
- **Execution:** a fresh `git archive 062698aff` copy at `$TMPDIR/opus-r12d/tree`, tools in `$TMPDIR/opus-r12d/tools`. Nothing was written to the repository. HEAD stayed at 062698aff48cebec883137cf08e9a25a08d26ef9, and `git status --short` stayed the same from start to end of the delta: only another session's two doc edits (` M docs/align/next_arm_packet.md`, ` M docs/run_reports/2026-11-19-c1-packet-rebuild-handoff.md`). One test process at a time. Per the coordinator, I did not run the frozen suite, `tests.test_reserve_calibration_hazard` or the p2_vpf module. The machine was heavily loaded for part of this round (another reviewer's probes were running), so some C1 tests took 3–5× their earlier time.

| Commit | Path | Blob after commit |
|---|---|---|
| 48b50958c | tests/align/test_c1_closure.py | 79f0f7fa52e6b607c49bca4a01d0c81f5ece5da5 |
| ddd369dc6 | tests/align/test_c1_closure.py | e32aa159e4ff7e36205f6d49abd5fbe49d228642 |
| fcfc0dee489e649d641ac34793eeed1a5000ddaa | joulewise/calibration_ledger.py (NUMBER-BEARING, F8) | fcd1bbdcca032c86d8d889f7fa2e3790bffeb33b |
| 062698aff48cebec883137cf08e9a25a08d26ef9 | joulewise/align/apple/v4_registration.py | 5cd823e6bf16890ac8d9d160febcba0d0417b9a6 |
| 062698aff48cebec883137cf08e9a25a08d26ef9 | scripts/reserve_calibration_window_bracket.py | a76cb6cf9c50c2c9bebc75e9f36ede837b751bd2 |
| 062698aff48cebec883137cf08e9a25a08d26ef9 | scripts/validate_powermetrics_fiducial.py | 26b836495b0e6d72442a9288f8e852aa60c778c2 |

Both test commits precede both production commits, and the test file does not change after ddd369dc6. adapter.py, the frozen suite and its `SUITE.sha256`, and `configs/gates/hazard_refusals.json` are unchanged across 3daea0447..062698aff (empty `git diff --stat`).

### Delta verdict: ADMIT

Both MEDs are closed, each is killed by its new named regression, and I found no new false refusal of an input the consumer would accept, apart from one deliberate tightening (D-INFO). fcfc0dee4's default and every existing caller are unchanged. Capture `main`'s custody locator is unchanged. Four LOW test gaps remain. None of them admits anything the consumer refuses, and none blocks.

### Status of the original findings

| Finding | Status at 062698aff | Evidence |
|---|---|---|
| MED-1 (resumable route takes a lease) | **Closed** | `test_r11_resumable_session_preflight_takes_no_lease` OK: admitted on both routes, ledger bytes and `runs/` listing unchanged. `readiness_equivalence.py` rerun: 28/28 read-only = lease-held decisions, and 0 read-only directory changes, where 3daea0447 had 2. Own-session state, non-strict: `blocked` (admit) with the directory unchanged. D1 (fcfc0dee4's line) and D3 (the pass-through) are each killed by that test: `(0, 2, refuse, 0, 0)`, i.e. the builder admitted and install refused, the old symptom. |
| MED-2 (capture/reservation agreement) | **Closed** | `test_r11_capture_slot_binding_must_match_the_reservation` and `test_r11_every_consumer_reads_the_reserved_head_pin` OK. D4, D6 and D8 are killed. D7 survives (D-LOW-1). Probe p14 at head: attempt differs while the locator matches → `(2, 2, refuse, 0, 0)` with `{"field": "attempt_id", "capture": "fixture-other", "reservation": "fixture-pre"}`, and the capture's own slot check also refuses. |
| LOW-1 (HAZARD lagging pin at preflight) | Open | The new resumable case has a lagging pin, but its open session refuses first (`open_sessions` precedes the pin-relation branch), so it cannot separate `hazard=True` from `False`. I did not rerun R3; this is by reading. |
| LOW-2 (desk policy precedence) | Mostly closed | R11 (shared `_desk_power_policy`) is now killed by `ReservedIdentityTests` (`'t1' != 'epoch'`). R10 swaps the arguments at the preflight call site; I did not rerun it. By reading it still survives, because the unit test calls the function directly and `DeskPolicyAttempt` names a policy only in the epoch file. |
| LOW-3 (strict vs non-strict untested) | **Closed** | R4 is killed by the resumable test: `(2, 2, refuse, 0, 0)`. |
| LOW-4 (default live-writer probe untested) | Open, and now two sites | D2 (`calibration_session_status` default `probe_live_writer=False`) survives `tests.test_calibration_ledger` (95 OK). No test anywhere asserts session status's `live_writer` field (grep). The `resume-live` exit witness drives `resume-finalize`, not session-status. |

### New findings

**D-LOW-1: The attempt-id comparison in `reserved_slot_refusal` has no killing test (D7 survives).** Every named case that changes `--attempt-id` also changes the custody locator, because the capture's locator is `--output-root / --attempt-id`. So the locator check refuses and the attempt check is never the deciding one. The attempt check matters when the reservation's `--{slot}-custody-locator` basename differs from its `--{slot}-attempt-id`. The validator allows that, and the capture refuses it at launch. Probe p14 shows the check refusing that case at head. Fix: add p14 as a subcase of the slot regression.

**D-INFO: The head-pin agreement compares pin files, not pin content (by design).** `same_head_pin` requires `view.locate(capture or campaign --head-pin)` to equal the reservation's located pin. Probe p13: a byte-identical copy of the genesis pin at another repo path, given to the pre capture, gives `(2, 2, refuse, 0, 0)` with `C1 capture head pin differs from the reservation's head pin`. The capture's own slot check on the reserved ledger admits it. This is stricter than the consumer, but it is a refusal, not an admission, and it matches the stated rule that every later stage locates the reservation's pin file. No change suggested.

### Checks that found nothing

- **fcfc0dee4 default and callers.** The new line is `writer_lease_is_live(ledger_path) if probe_live_writer else False`, and with the default `True` it is the old line. Production callers at 062698aff: `joulewise/b5/plan.py:663`, `calibration_ledger.py:6393`, `joulewise/controller.py:963`, `scripts/recover_calibration_ledger.py:427/438/511`, and `pre_reserve_readiness` (reserve…py:429). Only the last passes the flag. It passes `probe_live_writer=probe_live_writer`, which is `False` only from v4_registration.py:1273 (preflight); `main` keeps the default under its own lease, where the probe returns early. `tests.test_calibration_ledger` PASS (95, 1 skipped).
- **Capture `main` custody locator.** 3daea0447 had `custody_locator = normalize_calibration_custody_path(out_dir)` with `out_dir = args.output_root / validation_id`. 062698aff has `bracket_custody_locator(args.output_root, validation_id)`, which is `normalize_calibration_custody_path(Path(output_root) / attempt_id)`, and `args.output_root` is already a `Path`. `locator_equivalence.py` compared the two expressions on 30 cases (absolute, relative, `.` and `..` segments, trailing slash, spaces, ids containing `/` and `..`): 0 mismatches. In the run of `test_validate_powermetrics_fiducial_hazard.DisplaySleepTests.test_failed_display_action_flags_and_capture_finalizes` at head, the writer printed `calibration_writer_arm_authorized`, so the reserved-slot check, which compares this locator, passed. That test then failed for an unrelated reason: `detection_nonconvergent`, `trigger: wall_deadline` (wall budget 120 s under load). I did not use it as a mutation target.
- **Reserved slot source.** Preflight compares against `reservation_inputs(...)[3]`, the reservation's own normalized slots. `validate_bracket_session_reservation_inputs` normalizes `custody_locator` with `normalize_calibration_custody_path` and passes `attempt_id` through unchanged. `append_bracket_session_receipt` writes those same normalized slots, so preflight compares the values the open receipt will carry. Preflight runs in the chain's working directory, so the relative-path normalization matches launch.
- **No new false refusals (probes p9–p12, each with the capture's own slot check):** `--output-root` given as a literal absolute path with a trailing slash → admit on both routes, consumer admits. `--output-root …/instrument_validation/../instrument_validation` → refuse `custody_locator`, and the consumer also refuses (lexical locator), so this is consistent. Capture `--head-pin` given as an explicit literal equal to the default → admit. Collection `--head-pin` given explicitly as the reservation's pin → admit. Named controls also pass: explicit default pin in a capture, desk-epoch policy matched, omitted and equivalent sampler, default pin.
- **Renamed function.** No caller of `reserved_identity_refusal` remains at 062698aff (`git grep`). The round-11 policy, sampler and rollback tests pass against `reserved_slot_refusal`.
- **Census.** `tests.hazards.test_refusal_allowlist` PASS (24 tests, 1 skipped) on the 062698aff copy. v4_registration.py is a listed census exclusion, so `same_head_pin`'s new `ValueError` needs no row.

### Commands executed (delta; all in `$TMPDIR/opus-r12d/tree` unless noted)

| Command | Result |
|---|---|
| `git log/diff/rev-parse/status` in the repository (read-only) | commit order, blobs, unchanged suite/adapter/census, status unchanged |
| `mutate_r12d.py BASE_A`: resumable, head-pin and slot-binding tests | OK ×3 (153.6, 250.9, 146.5 s) |
| `mutate_r12d.py BASE_B`: ledger-pointer test, `ReservedIdentityTests`, `tests.test_calibration_ledger`, capture-finalize test | OK, OK, PASS 95; the capture-finalize test FAILED on `wall_deadline` (above) |
| `mutate_r12d.py BASE_C`: round-11 policy, sampler and rollback tests | OK ×3 (320.1, 490.3, 319.8 s under load) |
| Capture-finalize test rerun with full output | same `wall_deadline` failure; `calibration_writer_arm_authorized` present |
| `PYTHONPATH=. python3.13 -B locator_equivalence.py` | 30 cases, 0 mismatches |
| `PYTHONPATH=. python3.13 -B readiness_equivalence.py` (from round 12) | 28/28 agree, 0 read-only directory changes |
| `probes.sh` p9–p14 (`probe_r12d.DeltaProbe`, one at a time) | as above |
| `quick_suite.py --module tests.hazards.test_refusal_allowlist` | PASS 24 (1 skipped), 95.8 s |
| `git hash-object` on the four production files after the last mutant | match 062698aff blobs |

### Delta mutants (062698aff copy; one site each, restored after)

| ID | Site | Mutation | Target | Result |
|---|---|---|---|---|
| D1 | calibration_ledger.py:5728 (**fcfc0dee4**) | `… if probe_live_writer else False` → always `writer_lease_is_live(...)` | resumable test | **killed**: `(0, 2, refuse, 0, 0)` |
| D2 | calibration_ledger.py:5639 (**fcfc0dee4**) | session-status default `True` → `False` | tests.test_calibration_ledger | **survived** (95 OK): LOW-4 |
| D3 | reserve_calibration_window_bracket.py:437 | drop `probe_live_writer=probe_live_writer` to session status | resumable test | **killed**: `(0, 2, refuse, 0, 0)` |
| D4 | v4_registration.py:1186 | `same_head_pin` never refuses | head-pin test | **killed**: pre capture, post capture and collection admitted |
| D6 | validate_powermetrics_fiducial.py:2234 | drop the session comparison | slot-binding test | **killed** (pre `--session-id` admitted) |
| D7 | validate_powermetrics_fiducial.py:2239 | drop the attempt comparison | slot-binding test | **survived**: D-LOW-1 |
| D8 | validate_powermetrics_fiducial.py:2244 | drop the locator comparison | slot-binding test | **killed** (pre `--output-root` admitted) |
| R4 | v4_registration.py (preflight call) | `pre_reserve_strict=True` | resumable test | **killed**: `(2, 2, refuse, 0, 0)`; LOW-3 closed |
| R11 | reserve_calibration_window_bracket.py:60 | T1 before epoch in `_desk_power_policy` | ReservedIdentityTests | **killed**: `'t1' != 'epoch'` |

Not run this round: D5 (campaign call site only; D4 kills the shared function through the collection subcase), D9 (capture `main` locator; covered by the expression comparison above), R3 and R10 (stated by reading above). 9 mutants: 7 killed, 2 survived (D2, D7).
