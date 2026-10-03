```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "SCOUT: 8 blocking items, 5 non-blocking",
  "workspace": {
    "base_requested": "b317866d",
    "base_mode": "exact",
    "head_start": "b317866d04b4b2af1eaf4522df6563d87e8bafe3",
    "head_end": "b317866d04b4b2af1eaf4522df6563d87e8bafe3",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "blocking_items": 8,
    "nonblocking_items": 5,
    "rows": [
      {"row": "Desk authentication", "action": "start_now", "wait_for": "", "collision_surface": "Read-only checkout and scratch outputs"},
      {"row": "G2-a arm", "action": "do_not_start", "wait_for": "B1-B8 resolved and desk replay completed", "collision_surface": "Ledger, installer inspection, driver admission"},
      {"row": "Admission scope", "action": "needs_ruling", "wait_for": "Lead disposition of Revision 6 admission on G2-a", "collision_surface": "Start manifest semantics and duration budget"},
      {"row": "Acquisition", "action": "wait_for", "wait_for": "Reviewed arm and agent-free machine-state gates", "collision_surface": "QUIET-MAC"},
      {"row": "Harvest", "action": "wait_for", "wait_for": "Completion boundary, delivery and process clearance", "collision_surface": "Separate G2-a probe custody"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/gen_g2_phase_d.py --emit-chain /tmp/g2a-scout/chain.zsh --night-date 20261004",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["emitted /tmp/g2a-scout/chain.zsh"]},
      "expected": {"exit_code": 0, "tail_regex": "emitted /tmp/g2a-scout/chain.zsh"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS generated Phase D matches pinned runbook bytes"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS generated Phase D"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "/bin/zsh -n /tmp/g2a-scout/chain.zsh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-scout/desk.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "harvest_coordinates REFUSED wrapper coordinates incomplete",
          "installer_literal_paths REFUSED CALIBRATION_LEDGER is not an absolute literal path",
          "fixed_chain_subtotal_s 7947.40625"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "fixed_chain_subtotal_s 7947[.]40625"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise /Users/edr/code/JouleWise/.venv/bin/python -B /Users/edr/code/JouleWise/scripts/recover_calibration_ledger.py --ledger /Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl --head-pin /Users/edr/code/JouleWise/configs/calibration/calibration_ledger_head.json audit",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 2, "tail": ["calibration_ledger_rollback"]},
      "expected": {"exit_code": 0, "tail_regex": "audit_clean"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise /Users/edr/code/JouleWise/.venv/bin/python -B /Users/edr/code/JouleWise/scripts/recover_calibration_ledger.py --ledger /Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/runs/calibration_observation_ledger.jsonl --head-pin /Users/edr/code/JouleWise/configs/calibration/calibration_ledger_head.json audit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["{\"head_digest\": \"a5b825b7dd77856be8d612be759be84f925a32f6e671481c2662bb03cbf57014\", \"head_sequence\": 376, \"status\": \"audit_clean\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "audit_clean"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /Users/edr/code/JouleWise/scripts/issue_calibration_acceptance_generation.py verify-members --artifact /Users/edr/code/JouleWise/configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json --corpus-root /Users/edr/night-custody",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["member \"d079-epoch-25g83-r6-20261001T2252Z-d12\": PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "d12.*PASS"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /Users/edr/code/JouleWise/scripts/recover_calibration_ledger.py --ledger /Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/runs/calibration_observation_ledger.jsonl --head-pin /Users/edr/code/JouleWise/configs/calibration/calibration_ledger_head.json audit-observations --baseline-sequence 376 --baseline-digest a5b825b7dd77856be8d612be759be84f925a32f6e671481c2662bb03cbf57014",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\": \"observations_classified\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "observations_classified"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Revision 6 manifest semantics and its fixed 7680-second budget currently apply to G2-a. A syntactically accepted null-prior manifest does not establish that the first-Revision-6-window assertion is scientifically applicable.",
      "needs": "Decide admission scope; recommendation: isolate Revision 6 bookkeeping while preserving G2-a OFF, clean-dwell and machine-state admission."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The sandbox denies sysctl kern.osversion and hw.model. Actual bind-window refused before publishing its inventory; check then refused the absent inventory. No full live-vector bind/check success is claimed.",
      "needs": "Replay canonical bind-window and check in the permitted operator environment after the fixes."
    }
  ]
}
```

SCOUT: 8 blocking items, 5 non-blocking

The former 25F84 acceptance blocker is cleared. The new acceptance authenticates, its declared epoch passes the estimator/protocol preflight, and all 24 derivation corpus members verify. G2-a still cannot safely traverse today’s installer and driver unchanged.

“Blocking” below means a readiness defect to resolve before arming. Some manifest only during unattended startup. The installer findings share a repair; the eight items are failure surfaces, not eight independent patches. No repository files changed.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Desk authentication | start_now | — | Read-only inputs; `/tmp/g2a-scout/` |
| Ledger restoration | wait_for | Authenticated source copied into the prospective clone | Clone’s ignored ledger |
| Installer compatibility | do_not_start | B4/B5 repaired and verified | Reservation inspection and launchd probe |
| Admission policy | needs_ruling | Disposition of B6–B8 | Revision 6 semantics applied to G2-a |
| Arm | do_not_start | Blocking findings resolved; fresh desk proof | Published plan and installed jobs |
| Acquisition | wait_for | Agent-free window; machine-state gates pass | `[QUIET-MAC]` |
| Harvest | wait_for | `t0 + window_max_s + 300`, delivery, process clearance | Night custody plus separate probe root |

## Critical path

Ledger restoration precedes binding and reservation verification. Installer compatibility precedes render/probe/install. Admission scope determines the manifest, session export and duration-budget repair. The resulting chain must be regenerated and hashed before plan publication. Harvest follows acquisition and must preserve the separate G2-a root.

**1. Chain generation passes, but generation does not establish current readiness.**

Executed:

```sh
python3 -B scripts/gen_g2_phase_d.py \
  --emit-chain /tmp/g2a-scout/chain.zsh --night-date 20261004
python3 -B scripts/gen_g2_phase_d.py --check
/bin/zsh -n /tmp/g2a-scout/chain.zsh
```

Results: emitted chain; generated-region check PASS; shell syntax exit 0.

[Generator:118](/Users/edr/code/JouleWise-scout-block2/scripts/gen_g2_phase_d.py:118) extracts the fixed runsheet fences and substitutes the G2-a date. The chain’s executable G2-a paths and tool references exist at this head. Its common prefix retains old G2-b/shakedown coordinates, but the G2-a stages use the fresh `G2A_*` coordinates.

`night_gate.probe_payload_kind(chain)` returns **`calibration`**, because there is no `NIGHT_PAYLOAD_KIND` declaration ([discriminant:161](/Users/edr/code/JouleWise-scout-block2/joulewise/night_gate.py:161)). Consequently it receives calibration installer handling and the broad diagnostic derivation admission.

**2. B1 — Runbook 68 restores the wrong ledger today.**

Runbook 68’s source remains the canonical checkout’s physical ledger ([runbook:177](/Users/edr/code/JouleWise-scout-block2/docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md:177)).

Observed metadata:

| Input | Rows | SHA-256 / head |
|---|---:|---|
| Canonical physical ledger | 76 | File `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f` |
| Current committed pin | 376 | Head `a5b825b7dd77856be8d612be759be84f925a32f6e671481c2662bb03cbf57014` |
| Acceptance baseline | 376 | Same head |
| Retained C2 physical ledger | 376 | File `3c9b6844e22958a6ba0eaee28cfab63642f3d0310f15b9bbc9e82363a2d772fb` |

Canonical `recover_calibration_ledger.py … audit` exits 2 with **`calibration_ledger_rollback`**. Loading against the acceptance baseline additionally reports **`calibration_ledger_baseline_missing`**. The refusal originates at [ledger:2610](/Users/edr/code/JouleWise-scout-block2/joulewise/calibration_ledger.py:2610).

The retained C2 source is:

```text
/Users/edr/night-custody/measurement/
JouleWise-measurement-20261001T2252Z-r6-c2/
runs/calibration_observation_ledger.jsonl
```

Its custody audit returns `audit_clean`, head sequence 376. `audit-observations` against the acceptance cutoff returns `observations_classified`.

**Smallest fix:** change `LEDGER_SOURCE` and its expected file digest, then restore those authenticated bytes into the new clone. Preserve the committed pin.

**3. B2 — The producer ignores ledger authentication refusals.**

[Producer:684](/Users/edr/code/JouleWise-scout-block2/scripts/generate_g2a_probe_inputs.py:684) loads a snapshot with the acceptance cutoff and committed-pin requirement, but [line 695](/Users/edr/code/JouleWise-scout-block2/scripts/generate_g2a_probe_inputs.py:695) returns bindings without examining `snapshot.refusal_reasons`.

Desk reproduction:

```text
snapshot refusals:
  calibration_ledger_baseline_missing
  calibration_ledger_rollback
producer_ledger_auth PASS
```

The same helper also returns PASS for the valid 376-row source. The defect is its failure to distinguish those cases. The enforcing reservation path subsequently checks readiness and refuses ([reservation:281](/Users/edr/code/JouleWise-scout-block2/scripts/reserve_calibration_window_bracket.py:281)); this is a false desk-authentication success, not a successful reservation bypass.

**Smallest fix:** reject nonempty `snapshot.refusal_reasons` before returning bindings; approximately 3–6 lines.

**4. Acceptance and producer checks: the new artifact works; full binding remains an environment gap.**

The default acceptance authenticates to:

```text
acceptance_id: d079_calibration_acceptance_v2_n24_25g83_r2
sha256: f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660
epoch: 25G83 / Mac15,9 / ac_high_power / 100 ms
protocol: powermetrics_pulse_fiducial_v3
estimator: joint_loss_sublevel_interval_branch_v2
```

The live default is selected at [calibration_bracketing:231](/Users/edr/code/JouleWise-scout-block2/joulewise/calibration_bracketing.py:231). Authentication and declared-epoch preflight passed. `verify-members` returned **24 PASS, exit 0**.

`build-probes` succeeded with the locally pinned tokenizer, producing four stages with five small members each and four stages with one large member each. It loads tokenizer resources, not model weights ([tokenizer loader:364](/Users/edr/code/JouleWise-scout-block2/scripts/generate_g2a_probe_inputs.py:364)).

Actual canonical `bind-window`, using the valid current ledger, refused:

```text
calibration_vector_derivation_refused: CalledProcessError:
Command '['/usr/sbin/sysctl', '-n', 'kern.osversion']'
returned non-zero exit status 1.
```

Direct observation was `Operation not permitted`; `sw_vers -buildVersion` returned `25G83`. The subsequent actual `check` refused the absent inventory. These are **N1**, an environment-limited verification gap—not evidence of a remaining 25F84 epoch mismatch.

With the valid ledger, the issuer’s desk `check` matched the powermetrics binary SHA and MLX version; OS/hardware observations were unavailable in this sandbox.

**5. B3 — The rendered pre-calibration screen is stale.**

The chain retains two frozen assignments from the old acceptance, including the operative comparator at [runsheet:453](/Users/edr/code/JouleWise-scout-block2/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:453). The pre-slot result is tested against that comparator at [runsheet:467](/Users/edr/code/JouleWise-scout-block2/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:467).

A boolean-only desk comparison returned:

```text
chain_screen_matches_active_acceptance False assignments 2
```

Thus a chain regenerated today still carries an obsolete acceptance screen. Depending on the future capture, it can wrongly accept or reject the pre-slot. No measured bound was inspected or reported.

**Smallest fix:** derive the frozen comparator from the authenticated active acceptance during chain generation, replace both assignments and regenerate the chain/sidecar. Approximately 10–20 lines plus generated text.

**6. N2 — G2-a still uses a v2 plan; there is no integrated G2-a plan-author command.**

[NightPlan.from_mapping:396](/Users/edr/code/JouleWise-scout-block2/joulewise/night_gate.py:396) accepts the exact v2 field set:

```text
schema, schema_version, plan_id, receipt_class,
t0_epoch_s, window_max_s, authored_epoch_s,
repo_head, measurement_root, measurement_head,
chain_path, chain_sha256_path, custody_root, registration_path
```

Use `joulewise.night_plan.v2`, integer `2`, `DIAGNOSTIC_NO_PACK`. No start-manifest field belongs in that closed schema. A v4 plan additionally requires a valid `quiet_admission` policy; changing version is not necessary to repair G2-a.

The existing G2-a authoring route is the runbook’s draft resolver plus `write_night_plan`, not `gen_derivation_night.py --new-plan`. The latter authors derivation windows. The retained G2-a draft still pins September coordinates, heads and registration location; reauthor those explicit fields rather than reuse its bytes.

The current D-166 registration remains armable:

```text
configs/campaigns/d117_contrast_v5/
d166_dominance_criterion_registration.json
sha256 dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265
```

[Registration table:95](/Users/edr/code/JouleWise-scout-block2/joulewise/night_gate.py:95) accepts it. No registration-table addition is needed.

Scratch v2 parsing, driver `preflight`, and `schedule` passed. These checks do not validate arm readiness.

**7. B4 — Installer render-only now executes the G2-a chain instead of inspecting reservation argv.**

[Installer:1295](/Users/edr/code/JouleWise-scout-block2/joulewise/night_agent_install.py:1295) sees the current derivation source’s inspection capability and calls `reservation_input_digests` for any calibration-class chain.

[Driver:661](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:661) executes the supplied chain with:

```text
NIGHT_VERIFY_ONLY=1
NIGHT_RESERVATION_ARGV_ONLY=1
```

The rendered G2-a chain checks neither switch. It instead creates directories, checks inputs, and reaches a reservation with **`--execute`**. If those steps succeed, its 600-second settle exceeds the inspection subprocess’s 10-second timeout. Render-only therefore can mutate prospective reservation state and fails to produce the expected NUL-delimited argv.

I did not execute this path.

**Smallest fix:** add a G2-a reservation-argv inspection branch before all mutation, plus a verify-only reservation branch. Do not rely on the installer flag alone.

**8. B5 — Mandatory launchd probe bindings assume the derivation wrapper.**

Three incompatible requirements occur before a usable probe receipt:

- [Installer:750](/Users/edr/code/JouleWise-scout-block2/joulewise/night_agent_install.py:750) requires absolute literal ledger exports. G2-a exports shell expansions. Actual parser result: **`CALIBRATION_LEDGER is not an absolute literal path`**.
- [Installer:801](/Users/edr/code/JouleWise-scout-block2/joulewise/night_agent_install.py:801) requires the wrapper to reference `calibration_derivation_only.zsh`.
- G2-a lacks the verify-only/argv-only behavior required by the probe.

Runbook 68’s install command without `--launchd-probe` no longer suffices: [installer:1307](/Users/edr/code/JouleWise-scout-block2/joulewise/night_agent_install.py:1307) requires a valid existing probe receipt. Adding `--launchd-probe` alone encounters the incompatibilities above.

**Smallest fix:** make probe bindings recognize the G2-a inspection surface, emit literal clone-specific ledger/pin coordinates, and reuse B4’s safe branches. Approximately 50–90 lines combined with B4, excluding tests.

Also, reservation `--verify-only` acquires a writer lease ([reservation:280](/Users/edr/code/JouleWise-scout-block2/scripts/reserve_calibration_window_bracket.py:280)); it is not strictly filesystem-read-only. I did not run it against canonical custody.

**9. B6 — Missing start manifest refuses before OFF admission.**

The broad branch at [driver:3363](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3363) includes G2-a. It first reads:

```text
<night custody>/start_conditions_manifest.json
```

Runbook 68 and the G2-a producer do not author that file.

[Validator:3024](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3024) requires either:

- `schema`, matching `plan_id`, null `prior_revision6_session`, nonempty `reason`; or
- `schema`, matching `plan_id`, and prior-session fields `session_id`, absolute `harvest_file`, `harvest_sha256`, `started_epoch_s`, `terminal_epoch_s`, `decision_sha256`.

The prior harvest must authenticate **`NEXT_WINDOW`** ([driver:3069](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3069)).

A null-prior G2-a explanation passed the syntax validator. That does not resolve whether Revision 6’s first-window assertion applies to G2-a after the completed derivation block.

**Smallest mechanical fix:** one manifest file. **Recommended fix requiring lead disposition:** limit Revision 6 bookkeeping to Revision 6 windows, while preserving generic G2-a quiet admission.

**10. N3 — OFF, clean dwell, battery and census are actual start gates.**

After the manifest, [driver:3370](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3370) creates the OFF receipt and runs clean dwell during the OFF settle. It does not accept “network time was already OFF” as a substitute.

The code requires successful exact OFF enforcement, current boot identity, and 600 seconds on both clocks ([network_time_off:87](/Users/edr/code/JouleWise-scout-block2/joulewise/network_time_off.py:87)). No privileged command was run in this scout.

Clean dwell requires ten continuous clean minutes; timeout is capped at 2700 seconds and the remaining start budget ([driver:3227](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3227)). The **current** prewindow script examines executable names, not every argument substring ([prewindow:163](/Users/edr/code/JouleWise-scout-block2/scripts/prewindow_check.sh:163)); the older C1 recipe’s argument-substring description is stale.

The v2 G2-a gate still requires census clearance, AC power, battery float, display configuration, acceptable load and thermal state. Installer battery float is also mandatory. The newer per-process observation predicate is selected for QPE payloads, not this calibration-class G2-a chain ([night_gate:1668](/Users/edr/code/JouleWise-scout-block2/joulewise/night_gate.py:1668)).

These are operator prerequisites, not demonstrated machine-state failures here.

**11. B7 — Start-condition recording requires a missing literal `SESSION_ID`.**

Even after manifest, OFF, dwell and gate success, [driver:3136](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3136) requires one literal `export SESSION_ID=…`.

G2-a provides `G2A_BRACKET_SESSION_ID`, not `SESSION_ID`. Actual parser result:

```text
SESSION_ID must be one literal export in the pinned chain
```

The recorder accumulates that error and refuses before chain claim at [driver:3207](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3207).

**Smallest fix if retaining this admission:** emit one literal `SESSION_ID` equal to the G2-a calibration session. Shell expansion is insufficient. Isolating Revision 6 bookkeeping under B6 also removes this coupling.

**12. B8 — The borrowed programmed-span budget is too short.**

The driver reserves **7680 seconds**:

```text
600 + 11 × 600 + 480 = 7680
13500 − 7680 = 5820 seconds available before latest chain start
```

That constant is Revision 6’s twelve-slot shape ([driver:3021](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3021)), not G2-a.

For the generated default G2-a chain:

| Component | Arithmetic | Seconds |
|---|---|---:|
| Pre-slot settle plus eight stage settles | `(1 + 2 × 4) × 600` | 5400 |
| Eight campaign arm countdowns | `8 × 20` | 160 |
| Members | `4 × 5 + 4 × 1` | 24 members |
| Idle, post-warmup settle, post-run sampling dwell | `24 × (75 + 5 + 1)` | 1944 |
| Each calibration capture | Three 5-second baselines + three `(1 + 1.5)` warmups + deterministic 59-pulse schedule | 196.703125 |
| Two calibration countdown/display pauses | `2 × (20 + 5)` | 50 |
| **Chain fixed-duration subtotal** | `5400 + 160 + 1944 + 2 × 196.703125 + 50` | **7947.40625** |
| Driver OFF/clean dwell, earliest overlap | `600` | **600** |
| **Earliest total fixed subtotal** | `7947.40625 + 600` | **8547.40625** |

Sources: [producer:507](/Users/edr/code/JouleWise-scout-block2/scripts/generate_g2a_probe_inputs.py:507), [pulse schedule:383](/Users/edr/code/JouleWise-scout-block2/joulewise/powermetrics_fiducial.py:383), [controller:1221](/Users/edr/code/JouleWise-scout-block2/joulewise/controller.py:1221), [controller:1295](/Users/edr/code/JouleWise-scout-block2/joulewise/controller.py:1295), and the emitted chain.

This excludes model loading, actual warmup/prefill/decode work, cooldown/admission work, sampler readiness, reductions and custody operations. Code does **not** provide one exact total wall duration.

Consequences:

- `13500` leaves **4952.59375 seconds** beyond the earliest fixed subtotal.
- A chain admitted at the current latest-start deadline has only 7680 seconds remaining—**267.40625 seconds less than its fixed subtotal**, before variable work.
- Required integer allocation is at least **`8548 + variable-work allowance + admission overhead`**.
- No duration proof establishes that 13500 is sufficient for every run.

**Smallest fix:** use a G2-a-specific reserved chain budget in admission, rather than increasing `window_max_s` while retaining 7680. Approximately 15–30 lines. Raising only the window preserves the late-admission defect.

**13. N4 — G2-a calibration refusals lack typed night transport.**

[Driver:681](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:681) recognizes `night/calibration-refusal.json`. The writer/reservation emitters publish it only when `JOULEWISE_CALIBRATION_REFUSAL_PATH` is set ([emitter:641](/Users/edr/code/JouleWise-scout-block2/joulewise/calibration_exits.py:641)).

The derivation chain sets that export; G2-a does not. A failed G2-a calibration can therefore produce a nonzero chain exit and stderr without the driver’s typed calibration-refusal result. The result may retain verdict `GO` with nonzero `chain_exit_code` ([driver:3624](/Users/edr/code/JouleWise-scout-block2/scripts/run_night.py:3624)).

**Smallest fix:** one export to `$NIGHT_DIR/calibration-refusal.json`. Harvest must independently require exit 0 and no abort/refusal. The courier remains generic and reports driver artifacts; it does not authenticate or back up the separate probe corpus.

**14. N5 — `harvest_window.py` is not a G2-a harvester.**

There are three independent incompatibilities:

- [Coordinates:117](/Users/edr/code/JouleWise-scout-block2/scripts/harvest_window.py:117) requires derivation-style literal exports. Actual G2-a result: **`wrapper coordinates incomplete`**.
- [Archive check:315](/Users/edr/code/JouleWise-scout-block2/scripts/harvest_window.py:315) archives night custody and checkout `runs/`; G2-a captures live under the separate `G2A_ROOT`.
- [Capture check:206](/Users/edr/code/JouleWise-scout-block2/scripts/harvest_window.py:206) explicitly refuses a session whose kind is not `derivation`.

Adding aliases alone cannot make this harvester support G2-a.

The minimal automated G2-a harvest should:

1. Enforce the closed completion boundary, delivery marker and actual process clearance.
2. Archive and hash **both night custody and the complete `G2A_ROOT`**, plus the physical ledger and pin.
3. Authenticate frozen inputs and the expected 24-member roster.
4. Authenticate pre/post primary custody and the recorded finalized/physical-ahead terminal boundary; advance the pin only through the governed terminal-pin procedure.
5. Strictly validate all expected member bundles from raw evidence and verify bracket verdicts. The existing [strict bundle validator:392](/Users/edr/code/JouleWise-scout-block2/joulewise/cli.py:392) re-reduces raw artifacts.
6. Verify or produce counts receipt and four-rung summary, then pass the authenticated summary to `select_g2a_prefill_length.py`.

The existing summarizer authenticates configs, manifests and prompt provenance, but reads stored summaries/metadata and skips absent summaries ([summarizer:474](/Users/edr/code/JouleWise-scout-block2/scripts/summarize_g2a_prefill_probe.py:474)). It is not complete raw-byte authentication. Its outputs are exclusive-create, so the chain’s existing outputs must be verified or compared with scratch regeneration rather than overwritten.

A small dedicated harvest wrapper is the narrower repair than adapting the Revision 6 harvester: approximately 100–180 lines using existing validation/authentication seams, plus focused tests.

**15. Watchdog and schedule have no G2-a-specific schema blocker.**

Current schedule differs from runbook 68:

- Install closes at **t0 − 10 minutes**.
- Watchdog REQUEST/TERM/KILL occur at **−8/−6/−5 minutes**.
- Dead-man is completion plus 3600-second recovery grace, rounded to a minute—not fixed at 07:00.
- Protected completion remains `t0 + window_max_s + 300`.

For the scratch October 4, 02:56/13500 plan, `schedule` returned a **07:46 dead-man**. The runbook’s old 07:00 arithmetic and hardcoded timestamps must be replaced. This is included in N2’s reauthoring work, not a new code blocker.

Next exact step: adjudicate admission scope, repair the producer/chain/installer seams, then replay binding, checking, safe reservation inspection and probe validation against a fresh clone restored from the authenticated 376-row ledger.

| Item | Blocks arm | Smallest fix | Estimated size |
|---|---|---|---|
| B1 — Stale canonical ledger seed | yes | Change ledger source and digest; restore current bytes | 2 settings |
| B2 — Producer ignores snapshot refusals | yes | Reject nonempty `refusal_reasons` | 3–6 lines |
| B3 — Obsolete frozen pre-cal screen | yes | Derive/freeze active comparator; regenerate | 10–20 lines + generated text |
| B4 — Render-only executes reservation | yes | Add side-effect-free argv inspection | Shared B4/B5 repair |
| B5 — Derivation-only probe bindings | yes | G2-a probe support, literal coordinates, verify-only branch | 50–90 lines combined |
| B6 — Missing/inapplicable start manifest | yes | Rule admission scope; author applicable manifest or isolate Revision 6 | 1 file or 15–25 lines |
| B7 — Missing literal `SESSION_ID` | yes | Emit literal session export, if retaining recorder | 1 export |
| B8 — Wrong reserved chain duration | yes | G2-a-specific admission budget | 15–30 lines |
| N1 — Sandbox prevents full live-vector proof | no | Operator-environment bind/check replay | 0 code |
| N2 — Stale plan/schedule; manual authoring | no | Reauthor current v2 coordinates and schedule | Existing writer; field substitutions |
| N3 — OFF/dwell/battery/census prerequisites | no | Satisfy existing gates in agent-free window | 0 code |
| N4 — Missing typed calibration-refusal path | no | Export refusal destination | 1 export |
| N5 — Derivation harvest cannot handle G2-a | no | Dedicated archive/authenticate/validate/summarize wrapper | 100–180 lines + tests |