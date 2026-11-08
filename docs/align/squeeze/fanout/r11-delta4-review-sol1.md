# R11 delta4 review — Sol1

2026-11-08. Candidate: `48a4d1d76`, reviewed as `git diff 9891d679b..HEAD`.
Review branch: `align/2026-11-08-v4-r11-delta4-sol1` (the provisioned local branch).
Authority: the task brief, `docs/align/pilot_protocol_v4.md`, the packet contract,
R0-L3, W1-BLOCKERS merged rulings, and the Opus triage-packet review at
`origin/align/2026-11-08-triage-packet-opus-review:docs/align/v4/triage-packet-opus-review.md`.

## Verdict: HOLD for one bounded arm-validity fix

The packet rebuild and delta3 repairs are admitted on the synthetic evidence below.
I could not make an edited packet bypass the rebuilt evidence. However, the new
battery-source merger can manufacture a completed-charge transition by sorting a
source whose clock went backwards, and the **product arm admits it**. F1 needs a
small repair before a real arm. This is a demonstrated admission defect, not a
request for another design round or a new scientific threshold.

Two additional failures are stale R0-pending test fixtures. They need test repair,
not restoration of the old production guards. L1 below is a non-blocking extra
refusal with a packet-refresh workaround.

## F1 — MEDIUM, required: source sorting defeats the top-up raw-order refusal

Locations: `joulewise/align/apple/v4_topup.py:175-205` and
`scripts/align_v4_session.py:419`.

`derive` correctly refuses non-increasing timestamps, and requires consecutive raw
charging→floating observations. The new `derive_from_sources` first calls
`merge_in_time_order`, which sorts **inside each source**, even when there is only
one source. It silently repairs the very chronology that `derive` is supposed to
reject. Before this change the arm used `derive_from_file`, which preserves order.

The new witness
`test_arm_does_not_sort_away_a_battery_source_clock_regression` supplies this one
battery log, in its written order, at arm time 111:

1. Floating on AC at time 61, SoC 100%.
2. Charging on AC at time 11, SoC 97%.

`derive(rows, 111)` refuses. Through the real arm's new source loader the rows are
sorted into time 11 charging→time 61 floating. The retained evidence says:

```json
{"admissible": true, "basis": "completed_charge", "completed_at_epoch_s": 61.0,
 "completed_charge_epoch_s": 61.0, "latest_observation_epoch_s": 61.0,
 "observations": 2, "sources": {"between_window_logs": 1, "window_journals": 0}}
```

The arm returns `admitted: true`. The packet is honest and matches its rebuild;
current hardware probes are synthetic passing observations. The witness does not
replace the packet builder, record-binding check, commit check, battery derivation
or arm predicate. This bypasses the completed-top-up evidence requirement with an
ordinary clock/log-order fault; it does not require changing trusted code.

Recommended repair: validate strictly increasing finite timestamps **within each
source in raw order before merging**, including converted window-journal rows;
return a structured refusal on regression or duplication. Merge only validated
sources, preserving invalid/untimed rows as evidence. Keep the existing recent
completed-charge basis and continuous-float basis; add no new continuity rule or
threshold. Make the red arm witness pass and cover a regressed window journal too.

## L1 — LOW, non-blocking: the emitted pushed tip is not actually ignored

`canonical` drops only a top-level `pushed_tip`, but `build_packet` emits the tip
inside `checks.record_committed.pushed_tip`. Advancing only the remote-tracking ref
to an unrelated descendant therefore changes canonical equality, although the
window ledger and artifact digest are unchanged. The old packet refuses; a fresh
build immediately admits. No invalid arm is opened.

Passing witness: `test_remote_ref_advance_conservatively_requires_a_packet_refresh`.
It proves that this nested tip is the only canonical difference and that G1 still
reports `record_bound: true`. The packet contract's exception should cover the
actual emitted field, or the builder should put this informational field at the
documented top level. Refreshing after the last ref update is sufficient for W1;
this note does not extend the hold.

## Packet, delta3 and merge findings

- The arm rebuilds from the five named identities with its own time and current
  artifact digest. Added fields, removed battery rows, edited basis text, typed
  hardware passes, fabricated eight-window counts/test role, changed expiry and
  changed ruling digests refuse. A forged `packet_preflight.ready` cannot override
  a failed committed quiet observation. The arm retains its own packet and digest.
- Expiry is mandatory; a fresh packet stays canonically equal as arm time advances
  within its quiet receipt's validity. Missing, non-numeric, boolean, infinite and
  extended expiry values refuse. The lead-entered preparation timestamp does not
  supply the arm clock. Live meter failure and a charging battery observation
  refuse despite a ready packet. Quiet evidence remains committed-observation
  based until the separately owned R16 evaluator lands, as the current contract
  explicitly permits.
- Hash-linked history, `C3#1`/`C3#2`, committed ruling text SHA-256 and zero-capture
  accounting work together through the actual arm. Two zeros escalate; a committed
  ruling resets the trailing escalation without adding counted windows or changing
  eligible totals. Omitting the `#1` link refuses.
- G1 works independently of equality: rebuilding an old record's packet after a
  new window at a new path still produces a matching packet, but the canonical
  ledger binding refuses it. An unrelated commit with the same ledger is allowed;
  the new record's packet admits.
- The amendment allowlist is empty. The builder and four launchd templates are
  bound strict. Static and dynamic closure tests pass, the production
  `night_driver_hazard_pack` scenario is present and successful, and the production
  night-driver path is covered. Both delta3 witness modules pass.
- G3's listed + supervised + recorded matching-digest requirements remain intact.
  Tests cover stray/unlisted streams, missing supervision/digest, hash mismatch,
  and salvage only for covered members of an authenticated unclosed stream. No
  real meter journal was read.
- All four integration commits are ancestors of the candidate:
  `5d9b66dd4`, `d9d1098c6`, `9c40e4e5d`, `6d20e787a` (`merge-base --is-ancestor`
  returned 0 for each). R0 effort is `medium`; sensors are TV0h/Tf08 with F0Ac/F1Ac
  and the committed R0 digest. Pure configuration validators accept the fill.
  The original capture was not opened or revalidated.
- R0-L3 has not regressed: CPU contention in `QuietGuard` records flags without
  latching a refusal; SMC uses one `redo` attempt followed by `flag`; sustained
  largest-process contention, aggregate-only load, kernel_task, display wakes and
  classifier invariance have passing focused coverage. The generic SMC CLI's
  default `refuse` policy is deliberately retained for other callers; R0 explicitly
  selects the L3 policies. Armed-window/agent/custody/census faults still refuse.
- The merged U3/B tests pass: frozen N=16, source/gate binding, missing/refuted D
  screen local to D, charging-only desk exemptions, battery missing evidence,
  assist retention and escalation. The packet emits all **16 entries**, 15 gating;
  only meter coverage is non-gating. A first B non-pass resumes, a second refuses
  until the exact-window battery ruling's committed text is bound. Live arm checks
  remain required after that ruling.

## R0 integration test debt — two stale expectations

`tests.align.test_r1_runtime` runs 33 tests with two failures:

- `test_pending_inputs_refuse_before_work_with_a_terminal_record` still feeds the
  now-filled production `r1_runtime.json` and expects `PENDING R0`. It reaches
  native load-journal startup instead. The sandbox refuses `/bin/ps`, so it returns
  runtime-failure exit 3 rather than expected refusal exit 2. `start_journals` calls
  that snapshot before battery sampling, ticker startup or sensor capture; no
  measurement capture occurred. **Do not run this stale test unchanged outside the
  sandbox.** Make a temporary pending-sensors config for its negative case.
- `test_production_templates_refuse_pending_r0_effort_and_wp18_turns` still expects
  the filled D templates to have pending effort. Use an explicit temporary pending
  template for the negative assertion and accept `medium` in the shipped template.

These are test assumptions invalidated by the requested R0 fill, not a reason to
put pending-input guards back on this line. The new witness
`test_r0_filled_config_and_templates_validate_without_a_native_backend` exercises
the filled config/template validators without constructing a native backend.

## Verification

Python 3.13, one unittest module per process, sequentially. Every test process used
a realpath'd `TMPDIR=/private/tmp/jw-r11-delta4-sol1`; global Git config and user
Python site packages were disabled. The focused batch also set
`JOULEWISE_HOST_STATE_DIR` inside that temporary tree. Standard command form:

```sh
TMPDIR="$(realpath /private/tmp/jw-r11-delta4-sol1)" \
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 PYTHONNOUSERSITE=1 \
python3.13 -B -m unittest MODULE
```

The following **25 touched modules / 581 tests** returned success:

| Module (`tests.align.` unless otherwise stated) | Tests | Result |
|---|---:|---|
| test_v4_next_arm_packet | 27 | OK |
| test_v4_next_arm_packet_opus_witnesses | 5 | OK |
| test_v4_cadence | 30 | OK |
| test_v4_registration | 22 | OK |
| test_v4_receipt_tiers | 8 | OK |
| test_v4_record_binding | 6 | OK |
| test_v4_dynamic_closure | 10 | OK |
| test_r11_delta3_sol1 | 18 | OK |
| test_r11_delta3_sol2 | 13 | OK |
| test_r11_delta_sol1 | 8 | OK |
| test_r11_delta_sol2 | 6 | OK |
| test_km003c | 23 | OK |
| test_v4_topup | 19 | OK |
| test_v4_kit | 116 | OK |
| test_v4_powermode_record | 9 | OK |
| test_v4_r11 | 27 | OK |
| test_r0_checks | 33 | OK |
| test_r0_host | 59 | OK, 1 real-capture test suppressed before its import-time stat |
| test_smc_classifier_v4 | 27 | OK |
| test_smc_quiet | 34 | OK |
| test_v4_w1_blockers | 16 | OK |
| test_w1bm_sol1 | 12 | OK |
| test_w1bm_sol2 | 12 | OK |
| tests.hazards.test_smc_enumeration | 19 | OK |
| JW_WP22_FULL=1 test_v4_w1_synthetic | 22 | OK, 1 previously documented expected failure |

Additional integration checks, also individually:

| Module (`tests.align.`) | Tests | Result |
|---|---:|---|
| test_r1_runtime | 33 | FAIL: 2 stale R0-pending assumptions described above |
| test_r1_runtime_e2e | 2 | OK, synthetic backend in real subprocesses |
| test_r1_runtime_contract | 11 | OK |
| test_r1_to_w1_chain | 6 | OK |
| test_r1_turn_counts_export | 11 | OK |
| test_v4_executed_closure | 4 | OK |
| test_protocol_v4_doc | 6 | OK |
| test_thermal_desk | 25 | OK |

New review witnesses: `python3.13 -B -m unittest tests.align.test_r11_delta4_sol1`:
**11 tests; 10 pass, 1 intentionally red (F1)**. No `expectedFailure` masks F1.
The L1 behavior is a passing witness documenting a conservative refusal.

`test_r0_host` was imported under this narrow patch, then run normally, so its
optional real-capture decorator never even stats a forbidden path:

```python
original = pathlib.Path.is_file
def synthetic_only(path):
    return False if str(path).startswith('/Users/edr/') else original(path)
with patch.object(pathlib.Path, 'is_file', synthetic_only):
    module = importlib.import_module('tests.align.test_r0_host')
unittest.main(module=module, argv=['review'])
```

Cheap syntax check:

```sh
PYTHONPYCACHEPREFIX=/private/tmp/jw-r11-delta4-sol1/pycache \
python3.13 -B -m compileall -q joulewise tests
```

Exit 0. `git diff --check` — clean.
Test subprocess time, including witness iterations, was about seven minutes,
below the brief's 20-minute ceiling. No full-suite discovery, pytest, network,
model weights, MLX execution, block-5 analysis, actual launch/arm, or real custody
read was used. No coordination-state file was edited.

## Handoff and remaining limits

Changed files are only `tests/align/test_r11_delta4_sol1.py` and this report. The
local review commit contains both; no product fixes, push, merge or registration
were performed. This report is the run/handoff record under the brief's explicit
coordination-state prohibition; no further agents or cross-model consults were
launched by this seat.

Next exact step: lead fixes F1's per-source chronology refusal and the two stale
R0 test fixtures, then runs the new witness module, `test_v4_topup`,
`test_r1_runtime`, and the full synthetic W1 module, individually. L1 can be handled
by packet refresh at the final pushed ref or by the small schema normalization.

This review does not establish native readiness. After R1 closes, the lead still
owns its real slots/thermometry evidence, the U3 export and independent gate,
signed B policy, exact receipt/gates, and current quiet/meter/battery observations.
The candidate still has null R1 fields, a PENDING battery policy and a PENDING
registration receipt; those prospective fills are not review defects. Native
MLX/Metal, KM003C/IOKit and launchd checks belong to the clean measurement session
outside this sandbox. I cannot infer their results from these synthetic tests or
from the committed R0 selection metadata.
