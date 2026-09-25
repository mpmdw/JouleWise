```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "partial",
  "summary": "The battery-float gate needs a universal arm/t0 probe, capture-specific slot records, and fail-closed harvest checks before W1.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "c6814dd891db361156c45434490342a3e1dd9da3",
    "head_end": "c6814dd891db361156c45434490342a3e1dd9da3",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "BATTERY-FLOAT-GATE-01A: parser and arm/t0 refusal",
        "action": "start_now"
      },
      {
        "row": "BATTERY-FLOAT-GATE-01B: slot evidence and harvest barriers",
        "action": "wait_for"
      },
      {
        "row": "W1 arm",
        "action": "wait_for"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "gh issue view 421 --repo mpmdw/JouleWise",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["error connecting to api.github.com", "check your internet connection or https://githubstatus.com"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "battery"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "ioreg -r -c AppleSmartBattery",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["\"ExternalConnected\" = Yes", "\"IsCharging\" = Yes"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "IsCharging.*Yes"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "pmset -g batt",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Now drawing from 'AC Power'", "99%; finishing charge; 0:00 remaining present: true"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AC Power"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "python3 -B -c 'n=18446744073709551458; print(n-(1<<64), abs(n-(1<<64))<=200); print(200*12.953/1000)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["-158 True", "2.5906"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "-158 True"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Issue #421 could not be fetched through gh or the web cache; its exact wording was not independently verified. The supplied directive was used.",
      "needs": "Lead should compare this design with issue #421."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Revision 5 currently retains every valid resolved member; a battery-confounded whole-window exclusion changes corpus admission and needs a prospective written addendum before W1.",
      "needs": "Lead to install the addendum and pin its digest before W1 arm."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The live ioreg output was truncated in the tool response, so this pass did not establish this machine's exact InstantAmperage value or its update cadence.",
      "needs": "Capture a bounded raw ioreg fixture during implementation."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| 01A: common probe and admission | start_now | none | Night gate, evidence-night arm path, pack readiness |
| 01B: slot evidence and consumption | wait_for | 01A’s parser and record schema | Derivation writer, quiet-envelope collector, scored bundle controller, harvesters |
| W1 | wait_for | both PRs, prospective registration addendum, focused verification | Sealed registration and arm digests |

### D1 — Arm and t0 refusal

Put the authoritative t0 predicate in **existing C3**, immediately after its AC observation, using a new exact reason code such as `night_refused_battery_float`. C3 already stores `pmset -g batt` as `ac_power_raw` but accepts any successful “AC Power” result ([night_gate.py:1486](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/night_gate.py:1486>)). Its row and reason registries are fixed lists, so add the code there and to receipt/retry policy; do not create C6 ([night_gate.py:203](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/night_gate.py:203>), [night_gate.py:301](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/night_gate.py:301>), [night_gate.py:609](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/night_gate.py:609>)). `night_probe_error` remains the result for a failed or malformed probe; parsed charging, disconnection, or excess current gets the new refusal code.

Use one shared parser over raw `/usr/sbin/ioreg -r -c AppleSmartBattery -w0` output. Require exactly one battery object and exactly one top-level occurrence each of `ExternalConnected = Yes`, `IsCharging = No`, and `InstantAmperage`. Parse the current as an integer in mA; for an unsigned 64-bit decimal at or above `2^63`, subtract `2^64`. For example, ioreg-form text `"InstantAmperage" = 18446744073709551458` means **−158 mA**, which passes the current bound. Accept signed negative decimal if emitted; reject absent, duplicate, malformed, or out-of-range values. Do not substitute the distinct `Amperage` field. Store the complete probe result, raw current token, normalized signed mA, three predicate outcomes, threshold, and capture time in C3 evidence/measured fields. The existing environment parser reads the two booleans but does not parse current ([environment.py:868](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/environment.py:868>)).

Run the same predicate at the arm check **and again immediately before publication**: the existing check writes `check.json`, while `publish_install` later reaches `os.replace` after other work ([evidence_night.py:1325](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/evidence_night.py:1325>), [evidence_night.py:1757](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/evidence_night.py:1757>)). Record the final raw probe in the attempt journal before that rename. For transaction packs, add the predicate to the existing `t0.power_path` authoring probe rather than adding a sixteenth row ([arm_readiness_evidence_t0.py:103](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/arm_readiness_evidence_t0.py:103>), [arm_readiness_evidence_t0.py:1839](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/arm_readiness_evidence_t0.py:1839>)).

A pre-capture battery refusal should join D-182’s **one new-plan, delivered, zero-capture successor** set, with its disk-fact checks and ≥60 s spacing; it is never a same-plan retry or a waiver. The eligible set is explicit ([arm_retry.py:21](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/arm_retry.py:21>), [arm_retry.py:280](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/arm_retry.py:280>)). A refusal after any capture remains ineligible for that route.

### D2 — Per-slot record

Use a common `battery_float` record with `before`, `after`, and optional `during` samples. Each sample contains raw ioreg bytes or a raw-text artifact reference, probe exit code, wall and monotonic stamps, `external_connected`, `is_charging`, `instant_amperage_raw`, `instant_amperage_ma`, and parse error. Missing or failed samples make the slot **unknown/confounded**. Take `before` immediately before sampler start and `after` immediately after sampler teardown, including error paths.

Place producer hooks where slot boundaries actually exist:

- **Derivation/calibration:** in `validate_powermetrics_fiducial.py` around its sampler lifetime and before its artifact write. Add `raw/battery_float.jsonl` to both `instrument_evidence.json.artifact_sha256` and `manifest.json.artifacts`; ledger finalization hashes the complete artifact inventory ([validate_powermetrics_fiducial.py:2275](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/validate_powermetrics_fiducial.py:2275>), [validate_powermetrics_fiducial.py:2568](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/validate_powermetrics_fiducial.py:2568>), [validate_powermetrics_fiducial.py:2615](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/validate_powermetrics_fiducial.py:2615>), [validate_powermetrics_fiducial.py:1715](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/validate_powermetrics_fiducial.py:1715>)). This avoids changing the sealed derivation shell chain, whose 12-slot loop invokes that writer ([calibration_derivation_only.zsh:243](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/night_chains/calibration_derivation_only.zsh:243>)).
- **Quiet-predicate envelopes:** bracket each `collect()` call and preserve the record under `evidence/envelope-NN/`, with its digest in the envelope’s archived inventory. `session.json` already supplies the envelope identity and start/end stamps ([sample_quiet_predicate_evidence.py:1028](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/sample_quiet_predicate_evidence.py:1028>), [sample_quiet_predicate_evidence.py:1066](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/sample_quiet_predicate_evidence.py:1066>), [sample_quiet_predicate_evidence.py:1163](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/sample_quiet_predicate_evidence.py:1163>)).
- **Scored bundles:** bracket the controller’s measured-run boundary and persist raw samples plus a digest in the bundle’s authenticated artifact inventory; include the digest in the sealed capture roster consumed by the forthcoming headline reducer. The controller already has exact sampling start/stop markers and writes metadata before reduction ([controller.py:1222](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/controller.py:1222>), [controller.py:1277](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/controller.py:1277>), [controller.py:2065](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/controller.py:2065>)). Merely adding a key to `metadata.json` does **not**, by itself, establish the requested digest coverage.

Do **not** add `battery` to `SAMPLERS`. The registered invocation currently requests `cpu_power,gpu_power,ane_power,thermal` ([powermetrics.py:58](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/adapters/powermetrics.py:58>), [validate_powermetrics_fiducial.py:2275](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/validate_powermetrics_fiducial.py:2275>)). Editing that adapter changes a pinned estimator-code digest, even though it need not change the separate `protocol_v3.json` digest ([calibration_bracketing.py:206](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/calibration_bracketing.py:206>), [calibration_bracketing.py:696](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/calibration_bracketing.py:696>)); it also changes the captured stream. A 2 s independent ioreg observer would improve transient detection, but must be characterized before use in scored captures: the controller’s measured interval is deliberately quiescent, with no controller I/O between its markers ([controller.py:1245](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/controller.py:1245>), [controller.py:1262](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/controller.py:1262>)). Before/after samples alone cannot prove that no charging occurred between them.

### D3 — Harvest and acceptance

Make a single fail-closed `require_battery_float_clean` reader authenticate each slot’s record and return `battery_float_confounded` for any `is_charging=true`, `ExternalConnected!=Yes`, `|current|>200`, missing bracket, failed parse, or digest mismatch. Apply it to **all recorded slots in the window**, including ordinary-invalid slots; one hit bars the *whole window* from claims and acceptance.

For derivation, call it before the count-only dry run reports `valid`, before `_select_members` reads any `b_fiducial_s`, and in the lower calibration candidate loader so a separate acceptance caller cannot bypass it ([issue_calibration_acceptance_generation.py:175](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/issue_calibration_acceptance_generation.py:175>), [issue_calibration_acceptance_generation.py:1061](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/issue_calibration_acceptance_generation.py:1061>), [calibration_bracketing.py:1542](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/calibration_bracketing.py:1542>)). The existing issuer authenticates manifest/evidence hashes but currently has no battery predicate ([issue_calibration_acceptance_generation.py:902](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/issue_calibration_acceptance_generation.py:902>)). The older continuation reader is another consumer and should use the same barrier if it remains callable for new nights ([issue_epoch_continuation.py:95](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/issue_epoch_continuation.py:95>)).

For quiet envelopes, the collector’s `summarize()` must report confounded status from authenticated envelope records ([sample_quiet_predicate_evidence.py:1462](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/sample_quiet_predicate_evidence.py:1462>)). For scored work, consume the record in the existing post-run environment refusal seam **before** campaign collection verdict and claim reduction, and require the forthcoming A292 reducer to verify the sealed roster’s battery digest ([environment_admission.py:48](</Users/edr/code/JouleWise-wt-817355d2-w1scout/joulewise/environment_admission.py:48>), [run_campaign.py:5070](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/run_campaign.py:5070>), [run_campaign.py:4372](</Users/edr/code/JouleWise-wt-817355d2-w1scout/scripts/run_campaign.py:4372>)). A scored reducer that accepts only a caller-supplied “clean” boolean leaves a bypass.

### D4 — Registration

The arm/t0 predicate is an instrument-state admission check and does not change the pulse estimator. **The proposed whole-window harvest exclusion does change W1’s registered membership rule.** Revision 5 says every valid resolved member is retained and fixes the W1 count-only stops ([preregistration_d079_epoch_25g83_rev1.md:610](</Users/edr/code/JouleWise-wt-817355d2-w1scout/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:610>)); the earlier text lists the named exclusion mechanisms ([same file:156](</Users/edr/code/JouleWise-wt-817355d2-w1scout/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:156>), [same file:165](</Users/edr/code/JouleWise-wt-817355d2-w1scout/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:165>)). Install a **prospective Revision 5 addendum before W1**, naming battery-confounded whole-window disposition, count handling, and the no-top-up consequence. Pin the amended text at arm. The v3 pulse-protocol JSON need not change if sampler arguments and pulse logic stay fixed; the existing registration explicitly calls for an unmodified protocol ([same file:143](</Users/edr/code/JouleWise-wt-817355d2-w1scout/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:143>)).

### D5 — Defect-shaped checks

1. Feed a real-format `ioreg` fixture with `ExternalConnected = Yes`, `IsCharging = Yes`, and low current through the **production** `night_gate.evaluate_*` C3 path: assert `night_refused_battery_float`, raw probe custody, no GO, and D-182 eligibility only with proven zero-capture facts. Repeat through arm `check()` and the final `publish_install()` pre-rename check.
2. Feed `InstantAmperage = 18446744073709551458` and assert −158 mA; test +200, −200, +201, a negative over-limit value, missing field, duplicate field, and the presence of `Amperage` without `InstantAmperage`. Drive the shared production parser, not a test-only copy.
3. Produce a derivation slot with `is_charging=true` in its hashed battery record, finalize its ledger row, then drive **both** `registration_dry_run()` and `prepare_candidate()`; neither may count or issue it. Tamper with the sidecar and assert the lower candidate loader rejects its digest. Drive quiet `summarize()` and scored `run_campaign`/A292 with analogous records. These checks verify consumption, not just writer output.

### D6 — Size and physical limit

Recommend **two PRs**, roughly **250–400 changed lines** for parser/admission/tests and **600–1,000** for the three producers, authenticated inventories, harvest readers, and tests. W1 waits for both and the registration addendum. This split keeps the immediately useful cheap refusal reviewable while preventing an admission-only change from being mistaken for complete protection.

The 200 mA threshold is useful as a **gross-flow screen**, not an energy-error bound. At the observed roughly 12.953 V battery voltage, 200 mA is about **2.59 W**; sustained for a 480 s capture it represents about **1.24 kJ**, far above the project’s joule-scale attribution target. The live `pmset`/`ioreg` combination confirms AC power can coexist with active charging. I did not obtain a readable live `InstantAmperage` value or establish its refresh interval, so “float reads near zero on this machine” remains unverified.

## Critical path

01A establishes one parser and refusal vocabulary. 01B uses that schema for every producer and every harvest path. The lead then installs the prospective Revision 5 addendum and pins its digest; only after all three are verified should W1 be armed.