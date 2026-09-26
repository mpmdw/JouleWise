```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend one mandatory end-to-end battery admission and window-confounding change, preserving sampler and estimator pins, plus a separately validated periodic-monitoring follow-up.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "c6814dd891db361156c45434490342a3e1dd9da3",
    "head_end": "c6814dd891db361156c45434490342a3e1dd9da3",
    "upstream_end": "c6814dd891db361156c45434490342a3e1dd9da3",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "mandatory_end_to_end_implementation", "action": "start_now"},
      {"row": "registration_addendum_and_replacement_policy", "action": "needs_ruling"},
      {"row": "W1_arm", "action": "wait_for"},
      {"row": "change_registered_powermetrics_samplers", "action": "do_not_start"},
      {"row": "periodic_in_capture_monitoring", "action": "wait_for"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse refs/remotes/origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "c6814dd891db361156c45434490342a3e1dd9da3",
          "c6814dd891db361156c45434490342a3e1dd9da3"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "c6814dd891db361156c45434490342a3e1dd9da3"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "gh issue view 421 --repo mpmdw/JouleWise",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "error connecting to api.github.com",
          "check your internet connection or https://githubstatus.com"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "battery"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "ioreg -r -c AppleSmartBattery",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["    }"]
      },
      "expected": {"exit_code": 0, "tail_regex": "\\}"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "pmset -g batt",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Now drawing from 'AC Power'",
          " -InternalBattery-0 (id=23003235)\t99%; finishing charge; 0:00 remaining present: true"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "present: true"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "GitHub CLI network access failed; directive 421 was successfully read through the GitHub fetch_issue connector.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Before W1 sealing, explicitly reconcile whole-window battery confounding with Revision 5 retention, stopping, and replacement rules. Directive 421 already requires refusal; it does not specify a replacement-window schedule.",
      "needs": "Record the prospective registration addendum and rule on disposition of a confounded W1/W2; do not silently substitute a window."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests or measurement jobs ran. The single live sample was charging at +1073 mA, so neither this machine's float distribution nor a live negative InstantAmperage representation was observed.",
      "needs": "Lead-controlled parser fixtures and subsequent float-state validation."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Boundary observations cannot rule out an intervening charging excursion; periodic observation requires observer-impact validation and cannot establish zero battery-energy error merely by passing 200 mA.",
      "needs": "Describe coverage honestly and validate any periodic observer before enabling it."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Mandatory parser, admission, slot evidence and consumers | start_now | Implementation authority for a subsequent seat | Night gate, installer, capture writers, custody readers |
| Prospective registration addendum | needs_ruling | Lead disposition of confounded-window replacement | Revision 5 stopping and retention |
| W1 arm | wait_for | Mandatory #421 observations passing; registration sealed; required evidence route available | Quiet-machine window |
| Add `battery` to `SAMPLERS` | do_not_start | — | Registered estimator-code digest |
| Periodic battery observer | wait_for | Boundary implementation and observer-impact validation | Measured energy, cadence, quiet-window contract |

## Critical path

**Recommendation:** implement a shared, fail-closed battery predicate; record observations inside each capture’s authenticated evidence; reject the **entire enclosing window** if any slot fails. A t0-only patch does not complete BATTERY-FLOAT-GATE-01.

**Verified baseline and corrections**

- The current C3 check records `ac_power_raw` and accepts the presence of `"AC Power"`: `joulewise/night_gate.py:1488–1505`.
- Correction to the supplied facts: `environment.py:215` declares `power.is_charging`, but **ioreg populates it**, through `environment.py:366–372` and `:868–885`. The pmset call at `:259` is not its source. There is no `InstantAmperage` parser there.
- Derivation slots invoke `validate_powermetrics_fiducial.py` at `scripts/night_chains/calibration_derivation_only.zsh:251–262`. That writer uses the imported `SAMPLERS` at `scripts/validate_powermetrics_fiducial.py:2275–2287`; its value lacks `battery` at `joulewise/adapters/powermetrics.py:58`. The inspected writer produces no battery observation.
- Revision 5 explicitly identifies W1/W2 as 12-slot derivation windows with 600-second settle/cadence: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:612`. The generator specifies `DIAGNOSTIC_NO_PACK` at `scripts/gen_derivation_night.py:81` and its example uses 9,000 seconds at `:666`. The preregistration recommends 9,000 seconds at `:110`. I verified the registered recipe, **not an actual staged W1 plan**, which was not supplied.

The binding [directive #421](https://github.com/mpmdw/JouleWise/issues/421) was read through the connector after the requested CLI failed.

**D1 — Admission and cheap postponement**

Add a small shared module, proposed `joulewise/battery_float.py`, owning capture, parsing, predicate evaluation and replay validation.

Use **C3**, not a new C6. C3 already owns machine state, while receipt validation fixes the condition IDs to C1–C5 (`night_gate.py:301`, `:2020–2027`).

The predicate is exactly:

```text
probe completed successfully
AND all three required properties parsed unambiguously
AND external_connected is true
AND is_charging is false
AND -200 <= instant_amperage_ma <= 200
```

Do not require 100% charge or `FullyCharged=Yes`; neither is in the directive. Missing, duplicate, malformed, timed-out or failed observations never pass.

Parser design:

- Execute `/usr/sbin/ioreg -r -c AppleSmartBattery` without a shell, with a bounded timeout.
- Parse exactly one AppleSmartBattery object and its top-level properties. Match complete property lines; do not accidentally consume nested adapter fields.
- Accept `Yes`/`No` as booleans and decimal integer current lexemes. Preserve the original integer as a **string**, avoiding JSON/JavaScript precision loss.
- For unsigned 64-bit rendering, compute `signed = n - 2**64` when `n >= 2**63`; otherwise retain `n`. Reject values outside the supported integer range. Do not mask arbitrary values down to 16 bits.
- An explicitly signed decimal can be supported with an int64 range check. Do not guess an alternative unsigned-32 encoding without a fixture establishing it.

Worked negative example:

```text
"InstantAmperage" = 18446744073709551566
18446744073709551566 - 18446744073709551616 = -50 mA
```

This is an illustrative negative encoding, **not a negative value observed today**. Apple’s `ioreg` implementation reads a signed `long long` and prints it after an unsigned cast; its boolean renderer prints `Yes`/`No`. [Apple ioreg source, `cfnumbershow` and `cfbooleanshow`](https://github.com/apple-oss-distributions/IOKitTools/blob/main/ioreg.tproj/ioreg.c#L1325).

Record `battery_float` with:

```text
schema, policy_id, limit_ma, phase
plan_id/window_id/session_id/slot/attempt_id where applicable
wall_time_s, monotonic_before_ns, monotonic_after_ns
argv, exit_code, timed_out, stderr
raw_stdout_sha256, raw_stdout reference
external_connected_raw, is_charging_raw, instant_amperage_raw
external_connected, is_charging, instant_amperage_ma
passed, reasons
```

Retain exact stdout bytes in an immutable artifact. Store the three original property values alongside parsed fields in the stage and arm record.

Required insertion points:

1. `night_gate._check_machine`, adjacent to the existing AC check at `:1488`, before load observations. This reaches both `evaluate_night` (`:1856`) and v4 `evaluate_dynamic_hard` (`:1811`).
2. `evidence_night.check`, beside the arm checks at `:1361`, **outside** the evidence-kind conditions at `:1372–1393`.
3. `evidence_night.publish_install`, after veto/successor checks and immediately before publication and successor-claim creation (`:1777–1782`). A cached arm check is insufficient.
4. The real installer’s shared admission path, `night_agent_install.validate_install` (`:1166`, invoked at `:1373`), to cover direct installation. Render-only work should remain non-measuring.
5. `arm_readiness_evidence_t0._derive_power` (`:1839`): incorporate the same observation into `t0.power_path`. This supplements the universal gate; it cannot replace it because W1 is not a transaction-pack night.

Use proposed refusal **`night_refused_battery_not_float`** for a successfully observed predicate failure, and **`night_battery_probe_error`** for unavailable/unparseable evidence. Add them to the explicit night/refusal registries; do not misclassify probe failure as proven charging.

For A212/D-182, add only the first code to `arm_retry.ZERO_CAPTURE_MACHINE_REFUSALS` (`arm_retry.py:21`) and its explicit code explanation. Preserve all existing custody, delivery, early-release and successor checks. `terminal_zero_capture_refusal` already rejects possible chain execution (`:204–244`); `run_night.py:3096–3122` already returns before launching the chain.

Thus:

- At arm/publication: preserve the stage and postpone before publishing or spending a successor.
- At t0: return REFUSED promptly, without captures/reservation.
- After capture: never use the zero-capture route.
- Do not turn this into repeated measurement attempts while waiting for charge completion. The licensed successor remains a fresh plan, not unlimited retries (`arm_retry.py:339`).

**D2 — Per-slot recording without changing registered samplers**

Do **not** add `battery` to `SAMPLERS`. The adapter file is in `ESTIMATOR_CODE_PATHS` (`calibration_bracketing.py:206–210`), and `_current_estimator_code_sha256` hashes its complete bytes (`:696–706`). The writer compares those pins (`validate_powermetrics_fiducial.py:396–398`).

That edit changes a registered **estimator-code digest**, although it does not by itself change `protocol_v3.json`’s digest. Also avoid editing `joulewise/reduce.py`, which is in the same pinned list.

Use the shared ioreg collector independently of powermetrics:

| Capture family | Exact insertion sites | Authenticated evidence |
|---|---|---|
| Derivation and calibration | Writer `main`: after raw-directory creation at `validate_powermetrics_fiducial.py:2228`, final pre-sampler check before `:2296`; post observation after teardown at `:2452`, including exceptional teardown | `raw/battery_float.pre.ioreg`, `raw/battery_float.post.ioreg`; parsed `battery_float` in `instrument_evidence.json` before `:2610`; raw hashes in both `artifact_sha256` at `:2572` and manifest artifacts at `:2620` |
| Ordinary campaign/transaction/scored capture using controller | `controller._run_lifecycle`: before idle baseline at `:859`; bracket the measured stage at `:1222`; final observation after post-idle sampling, before metadata/reduction at `:867` | Bundle raw artifacts plus `metadata.json.battery_float`, written through `_write_metadata` (`:2122` vicinity) |
| Quiet-predicate evidence envelopes | `sample_quiet_predicate_evidence.collect`: before recorder/round acquisition at `:1087–1098`, after acquisition teardown in `finally` | Envelope raw battery artifacts and `session.json.battery_float`; existing raw inventory/hashing at `:1200–1203` includes the files; envelope index records their references |

Use `battery_float.pre`, `.post`, `.observations`, `.status`, `.reasons`, `.policy_id`, and `.limit_ma` consistently. Proposed statuses: `pass`, `confounded`, `unverifiable`; none means “not applicable” for an actual Mac measurement.

A pre-slot failure stops before workload. A post-slot failure preserves captured bytes and records confounding. Exceptional exit without a post observation is `unverifiable`, never pass.

**Boundary checks are the least invasive first implementation.** During-slot polling should be a separate validated enhancement: an owned observer with fixed cadence, raw timestamps, bounded command duration, and complete cleanup. Buffer during measurements where necessary. The controller explicitly forbids file writes/logging within its measured interval (`controller.py:1262–1265`); do not slip a subprocess-and-disk polling loop into that interval under the description “just metadata.”

A proposed two-second cadence is reasonable to evaluate, but neither its overhead nor its ability to observe every excursion has been established here.

**Whole-window custody is essential.** Add a sealed battery window index, proposed `battery_float.window.json`, enumerating expected slots, terminal dispositions, observation artifacts and their hashes. Bind it to the plan/session and existing ledger or capture roster. Preserve invalid and aborted slots. An individual clean bundle must not license a claim if another slot in the same window charged.

Avoid a hash cycle: the terminal index hashes completed slot evidence; the enclosing harvest/acceptance/claim artifact pins the index. Each slot carries its window identity, not a forward hash of a file that does not yet exist.

**D3 — Consumers and bypass prevention**

Create one replay validator that authenticates raw observations, reparses them, checks completeness/identity, and evaluates the **whole window**. Do not trust a stored `passed=true` or caller-selected subset.

1. **Derivation harvest and issuance.**  
   Invoke the window validator in:
   - `scripts/calibration_cadence_report.report_window` (`:44`) before emitting a decision usable to proceed to W2.
   - `issue_calibration_acceptance_generation.registration_dry_run` (`:175`).
   - `_prepare_candidate`, before `_select_members` (`:1351`).
   
   Crucially, validate **all slots before disposition filtering**. The dry run skips non-valid slots at `:215–216`; `_select_members` does likewise at `:1076–1077`. A battery-confounded ordinary-invalid slot must invalidate its window rather than disappear from membership selection.

   Output `battery_float_confounded` or `battery_float_evidence_missing`; report counts and mechanisms, no B values. Do not quietly exclude one contaminated member and issue from the remainder.

2. **Calibration admission/acceptance use.**  
   Add local observation verification after authenticated evidence loading in `_load_calibration_candidate_unbounded` (`calibration_bracketing.py:1583–1633`), and whole-session validation before candidate/bracket use in `evaluate_calibration_bracket` (`:1965`). A consumer must establish that siblings are not confounded, not merely validate its two endpoints.

   Check equivalent ingress in acceptance reissuance; the issuing CLI alone is not a sufficient barrier. Preserve historical artifacts rather than rewriting them to manufacture missing observations. Historical replay and current scientific acceptance must have explicit, separate treatment.

3. **Ordinary bundle reducer.**  
   Enforce through `BundleReader.metadata()` (`bundle_read.py:272`) using the shared validator. `reduce_bundle` necessarily calls it at `reduce.py:2653` and already converts `BundleReadError` into a failed summary (`:2654–2666`). This avoids changing the pinned reducer file.

   Before the enclosing window closes, an online per-run result is provisional/unusable for claims. Final re-reduction requires authenticated terminal window evidence. Missing metadata must not disable the requirement; derive applicability from trusted capture identity, not an optional producer flag.

4. **Scored reducer.**  
   `scored_reduce.reduce` (`:145`) accepts caller-supplied `capture_windows`; `_check_window` only validates the digest’s syntax and joins at `:91–109`. It does **not** authenticate the bundle identified by `bundle_sha256`. Consequently, adding an optional boolean would leave a bypass.

   Require authenticated capture/window evidence at this public boundary, resolve it through the shared validator, and reject missing, incomplete or confounded enclosing windows before scoring. This needs a prospective input-contract change: `_check_window` currently demands an exact key set (`:92`). A trusted resolver or verified-evidence object must connect each scored window to its underlying bundle and complete window index.

   Repository search found no production producer of these scored-window records outside the reducer itself; tests construct them. Treat the production custody connection as work to build, not an existing integration to claim.

5. **Quiet-predicate evidence.**  
   Add whole-window validation at `quiet_predicate_campaign.pilot_summary` (`:1139`), reached by the harvest path at `:1674`, and at standalone `sample_quiet_predicate_evidence.summarize` (`:1462`). One charging envelope confounds the window; it is not merely another selectively excluded envelope.

The arm notice should state the mandatory predicate and whole-window consequence. Harvest records should pin the battery index and name the affected slots, raw hashes and refusal reasons.

**D4 — Registration**

**No change to `protocol_v3.json` is needed** for boundary admission/evidence recording. Its registered pulse workload, sampling interval, gates and estimator rules are at `protocol_v3.json:5–39`; this proposal changes none of them.

**An explicit prospective preregistration addendum is warranted before W1 sealing.** The arm check is an instrument-state admission requirement, but whole-window confounding changes which observations may contribute and potentially when capture stops:

- Registered exclusions are enumerated at preregistration `:165–171`.
- Revision 5 says every valid resolved member is retained and fixes W1/W2/W3 progression (`:612`).
- Earlier instrumentation amendments explicitly distinguish stops from tuning (`:569–575`).
- Revision 5 remains prospective and requires sealing before W1 (`:602`).

Recommended addendum: quote #421’s predicate; specify immutable evidence, whole-window non-use, fail-closed missing evidence, and that battery screening is independent of B. Preserve the pulse protocol, estimator pins, slot cadence and scientific thresholds.

**NEEDS_RULING:** what happens after a captured W1/W2 is confounded? Options are halt and return to council, or a prospectively specified replacement policy. Recommend **halt and return to council unless the lead installs a replacement rule before capture**. Do not infer that the existing count-triggered W3 permission licenses arbitrary replacement nights.

Keep the registered shell chain unchanged if possible. Its writer already stops on exit 2 (`calibration_derivation_only.zsh:273–278`), so new writer refusal can propagate without changing the Revision 3 chain digest retained by Revision 5 (`preregistration:604`).

**D5 — Defect-shaped tests**

Drive production entry points with injected probes/fixtures; do not launch hardware.

| Defect | Production path and required assertion |
|---|---|
| AC attached but charging | `night_gate.evaluate_night`, parameterized across measurement classes: exact battery refusal, C3 raw evidence, no GO |
| v4 bypass | `evaluate_dynamic_hard` through driver binding: charging never reaches chain launch |
| State changes after arm check | `evidence_night.publish_install`: fresh charging observation prevents publication and successor-claim creation |
| Direct installer bypass | Real-install validation path with fake actuator: no install side effect after battery refusal |
| Charging slot hidden as ordinary-invalid | `registration_dry_run` and `_prepare_candidate`: whole registration refuses before `_select_members` reads B |
| One bad sibling, clean requested endpoint | `evaluate_calibration_bracket`: refusal despite clean selected endpoints |
| Direct scored call | `scored_reduce.reduce`: missing evidence, forged pass, bad sibling and digest mismatch all refuse |
| Re-reduction bypass | `reduce_bundle`: authenticated charging evidence yields failed/non-claimable result without controller involvement |
| Evidence-envelope contamination | `pilot_summary` and standalone summary reject whole window |
| Crash or missing post observation | Writer/controller exceptional cleanup leaves unverifiable evidence, never a successful battery verdict |
| False cheap retry | A212 allows an otherwise eligible zero-capture battery refusal; rejects probe error, captured slot, or spent successor |

Parser fixtures should include today’s complete byte-form output, not only dictionaries; mutations cover `±200` passing, `±201` failing, zero, `IsCharging=Yes` with zero current, missing fields, duplicates, nested lookalikes and malformed/truncated output. Test the exact unsigned negative byte line shown above and integer boundaries; label negative fixtures synthetic until an actual negative capture is available.

Add pin-regression assertions that `SAMPLERS`, `protocol_v3.json`, all four `ESTIMATOR_CODE_PATHS`, and the registered shell chain remain byte-identical. This design-only session ran none of these tests.

**D6 — Size, split and physical interpretation**

Estimate: **roughly 1,200–2,000 changed lines across 15–20 production/test/document files**, dominated by custody validation, caller coverage and tests.

Recommend one mandatory vertical PR containing admission, pre/post recording, whole-window authentication, all consumers and the registration reconciliation. A t0-only PR must not close the lane. A second PR can introduce periodic monitoring after observer-impact validation.

The 200 mA threshold is a useful gross-flow screen, **not proof of negligible wall-energy error**. Today’s pack voltage was 12.953 V: 200 mA corresponds to approximately **2.59 W**, or **6.48 Wh over 9,000 seconds** if sustained. Passing the predicate does not establish an adequate wall-meter error bound.

At operational “float,” near-zero signed current is the expectation; zero or small discharge readings should pass. I cannot state this machine’s actual float distribution: today’s sole observation was still charging. The threshold also cannot establish that heat from earlier charging has dissipated; preserve settle/thermal gates.

**Executed evidence and handoff:** one ioreg read reported `ExternalConnected=Yes`, `IsCharging=Yes`, `InstantAmperage=1073`, `Voltage=12953`, and capacity 99%. One pmset read reported AC power and “finishing charge.” No launchctl, installer, powermetrics, tests, background jobs, subagents or repository writes occurred. HEAD and the clean worktree were unchanged.

**Next exact step:** the lead records the prospective whole-window/replacement ruling, then issues implementation scope for the mandatory vertical PR.