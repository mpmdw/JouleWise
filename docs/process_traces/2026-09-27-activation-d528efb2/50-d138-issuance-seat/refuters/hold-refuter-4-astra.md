```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "HOLD OPEN: direct campaign invocation bypasses S3, and two unchecked helpers return held content or numbers; remaining execution coverage was interrupted by the immediate-report instruction.",
  "workspace": {
    "base_requested": "b953f4b0",
    "base_mode": "exact",
    "head_start": "b953f4b0119f0e05bf02cb9ac206eaf4498b08e3",
    "head_end": null,
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "hold": "OPEN",
    "open_route_count": 3,
    "approval": false,
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Direct run_campaign invocation reaches the child launcher without S3",
        "locations": [
          "scripts/run_campaign.py:8043",
          "scripts/run_campaign.py:1872",
          "scripts/run_campaign.py:8738",
          "scripts/run_campaign.py:1959",
          "scripts/run_campaign.py:8990"
        ]
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Unchecked authenticator and operative helper return held data outside the inspection function",
        "locations": [
          "joulewise/calibration_bracketing.py:1238",
          "joulewise/calibration_bracketing.py:1285",
          "joulewise/calibration_bracketing.py:604",
          "joulewise/calibration_bracketing.py:638"
        ]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-hold4-d528efb2/probe_campaign.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DIRECT_BUILD_READS 0",
          "MAIN_RETURN 2 CHILD_CALLS 0 BUILD_READS 1",
          "campaign_probe: PASS; direct runner reaches subprocess.run; main refuses; no child launched"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "campaign_probe: PASS; direct runner reaches subprocess.run; main refuses; no child launched"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-hold4-d528efb2/probe_core.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "ORDINARY_WRITER: refused before ledger write, sampler, MLX and battery",
          "DERIVATION_ENDPOINT derivation excluded",
          "DERIVATION_ENDPOINT unresolved-session excluded",
          "DERIVATION_BASIS d079_calibration_acceptance_v2_n17_r7",
          "TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'dict'"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "core_probe: PASS"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-hold4-d528efb2/probe_continuation.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "G2_HELD continued_identity_epoch_claim_held",
          "G2_CONTROL pass skipped_no_ledger_snapshot",
          "continuation_probe: PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "continuation_probe: PASS"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-hold4-d528efb2/probe_go.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "S2_CONSUME_REFUSED claim_hold: H1-25G83-CAP-CADENCE (SCI-25G83-CANDIDATE-01-A1 §5.3)",
          "S2_REPLAY_REFUSED claim_hold: H1-25G83-CAP-CADENCE (SCI-25G83-CANDIDATE-01-A1 §5.3)",
          "S2_HISTORICAL_REPLAY: accepted without live authority",
          "go_probe: PASS; fixture Git calls suppressed; no git command wrote"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "go_probe: PASS; fixture Git calls suppressed; no git command wrote"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-hold4-d528efb2/probe_readers.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "joulewise.analysis_engine.inputs.AnalysisInputError: runs root path_resolution_refused"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "readers_probe: PASS"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-hold4-d528efb2/census.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "C5_REFERENCES"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Demonstrated routes trigger HOLD-BY-CONSTRUCTION-01 §6.2. This report does not approve issuance or merge.",
      "needs": "Stop this issuing transaction and return the route evidence to the owner under the ruling's prescribed options."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The immediate-report instruction arrived before the complete execution charge was finished. Two scratch probes have harness failures; every C-5 reader and every launch entry were not fully executed.",
      "needs": "Preserve the demonstrated findings. Do not treat this report as completion of §7 step 7."
    },
    {
      "id": "G3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Campaign execution used patched build and environmental observations plus a child-launch sentinel. GO probes used synthetic fixtures with Git writes suppressed. No hardware validation is claimed.",
      "needs": ""
    },
    {
      "id": "G4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The checkout was clean at intake. Final HEAD/status verification and the full suite were not run.",
      "needs": ""
    }
  ]
}
```

HOLD: OPEN — 3 route(s)

The three counted routes are direct campaign invocation, direct unchecked byte authentication, and direct unchecked operative lookup. The latter two satisfy the supplied §6.1(4) definition: held content or numbers returned by a function other than the inspection function. No successful measurement, passed held-build bracket, or published claim is asserted.

The execution charge remains **partial**. Your immediate-report instruction interrupted the remaining work.

| Candidate path | Gate or result | File:line | Executed evidence |
|---|---|---|---|
| Direct `run_campaign(args)` → ordinary child | **OPEN:** skips S3; marker-free preflight returns without launch authentication | `scripts/run_campaign.py:8043`, `:1872`, `:8738`, `:1959` | V1 reached the real `subprocess.run` boundary; sentinel raised before launch; build-reader calls: **0** |
| Same campaign through `main()` | S3 refuses | `scripts/run_campaign.py:8990` | V1: return **2**, child calls **0**, build-reader calls **1** |
| Held bytes → `_authenticate_acceptance_bytes` | **OPEN:** returns the held artifact | `joulewise/calibration_bracketing.py:1238`, `:1285` | V2 asserted equality with the parsed, pinned committed bytes before its later harness error |
| Held ID → `_registered_operatives_unchecked` | **OPEN:** returns held operative numbers | `joulewise/calibration_bracketing.py:604`, `:638` | V2 returned and asserted bracket screen **`0.013701`** |
| Held path → public loader / guarded authenticator | G1 returns `None` | `joulewise/calibration_bracketing.py:1224`, `:1288` | V2 assertions passed |
| Held ID → public operative API | Build lookup returns `None` | `joulewise/calibration_bracketing.py:643` | V2 assertion passed |
| Inspection result → explicit authentication / allowance | Reauthentication through G1 refuses | `joulewise/calibration_bracketing.py:1304`, `:1320`, `:1387` | V2: labeled inspection succeeds; explicit authentication and allowance return `None` |
| Mixed nested/flat declarations → arm evidence | Single-identifier admission refuses; evidence author also refuses through G1 | `joulewise/arm_readiness.py:6204`; `joulewise/arm_readiness_evidence.py:341`, `:923` | V2 exercised both shapes using committed held bytes; neither certified |
| Ledger bootstrap → guarded authenticator | G1 refuses before issuance-cutoff processing | `scripts/calibration_ledger_bootstrap.py:158` | V2 exercised raw-byte and explicit-object inputs; both refused |
| Ordinary capture preflight at 25G83, all eight registered generations | Older generations fail freshness; R7 fails epoch matching; held generation fails authentication | `scripts/validate_powermetrics_fiducial.py:388` | V2 exercised all eight |
| Explicit bracket evaluation at 25G83, all eight generations | No bracket passed | `joulewise/calibration_bracketing.py:2148`, `:2325` | V2 exercised all eight |
| Ordinary capture writer → ledger | Preflight refuses before capture and ledger writing | `scripts/validate_powermetrics_fiducial.py:2136` | V2 invoked `main()` with patched truthful 25G83 identity, without a test sampler or identity-override argument; epoch mismatch refused |
| Derivation or unresolved-session row → bracket endpoint | Discovery excludes both | `joulewise/calibration_bracketing.py:1900`, `:1976` | V2: both returned no candidates; endpoint-reader tripwire untouched |
| Derivation-only provenance | Reads unheld R7 | `scripts/validate_powermetrics_fiducial.py:551` | V2 returned R7’s basis |
| R7 continuation into 25G83 | G2 refuses | `joulewise/calibration_epoch_continuation.py:213` | V3: held refusal; same registered synthetic continuation passes with hold table emptied; judged epochs retain only 25F84 |
| Claim-eligible GO, direct authentication | S2 refuses held/unreadable builds | `joulewise/arm_readiness.py:10127` | V4: held and unreadable refuse; old-build and non-claim controls pass |
| Launch capability consumption → GO authentication | S2 refuses | `joulewise/arm_readiness.py:10551` | V4 executed `_consume_launch_capability` through the fixture’s invocation helper |
| Live consumed-GO replay | S2 refuses | `joulewise/arm_readiness.py:10221` | V4: held live replay refused; explicit historical replay did not read machine build |
| Default analysis binding, whole-window construction, mint component/binding/main, campaign snapshot | Real loader returns R7 at each exercised call boundary | `analysis_engine/inputs.py:1625`; `whole_window.py:508`; `mint_floor_artifact.py:965`, `:1743`, `:2036`; `run_campaign.py:4819` | V5 traced actual callers, stopping after the real loader returned |
| Issuance check/predecessor, continuation derive/check, reissue, equivalence | Explicit held-path loader returns `None` | `issue_calibration_acceptance_generation.py:393`, `:1148`; `issue_epoch_continuation.py:75`, `:326`; `reissue_calibration_acceptance.py:579`; `epoch_equivalence_check.py:208` | V5 exercised these reader boundaries |
| Simulation reference | Explicit R7 reference loads | `scripts/sim_acc_25g83_rev5.py:227` | V5 exercised the reader boundary |
| Generalized v2 mint | Held acceptance fails authentication | `scripts/mint_floor_artifact_generalized.py:3596` | V5 exercised the real held-file read and received `v2 calibration acceptance evidence is not authenticated` |
| Full analysis-input loader | Probe stopped before calibration read | `joulewise/analysis_engine/inputs.py:3114`, `:3123` | V5 failed because its scratch runs directory did not exist |
| AXI child dispatch, complete night/launcher execution, remaining C-5 entries | **Coverage unfinished** | `scripts/run_campaign.py:7554`; `scripts/run_night.py:3218`; `scripts/launch_window.py:261` | Source census completed; full execution not completed |

## Findings

**F1 — BLOCKER: direct campaign invocation bypasses S3.**

The executed sequence was:

```text
parse_args(...)
→ run_campaign(args)
→ authenticate_campaign_writer_preflight(...)
→ run_authenticated_campaign_child(...)
→ subprocess.run(...)
```

Inputs included the checked-in production policy with `claim_bearing: true` and an unchanged copy of the checked-in `p2015-neg8-reference-end.json` configuration. The configuration uses production MLX/powermetrics backends.

The probe patched `machine_os_build` to `25G83`, supplied admissible environmental observations, and supplied process-identity observations because the initial sandboxed process observation was unavailable. These were prerequisite observations; no hold, loader, authenticator, admission, or campaign-control function was replaced. The child launcher raised a sentinel before creating any process.

Direct invocation reached the launcher with **zero build-reader calls**. Calling `main()` with the same arguments returned **2** at S3 without reaching the child.

The production Python call census found `main()` as the sole caller of `run_campaign`; it did **not** find `run_night` directly importing that function. That limits the demonstrated route to direct callable entry, which the charge expressly requested testing. It does not remove the route: S3 is outside the callable runner.

**F2 — BLOCKER: the unchecked helpers meet the ruling’s forbidden data-return endpoint.**

Without changing production code, registry pins, file bytes, or the hold table:

```python
bracket._authenticate_acceptance_bytes(held_path.read_bytes())
```

returned the full held artifact, including `identity_epoch.os_build == "25G83"`.

Separately:

```python
bracket._registered_operatives_unchecked(held_id)
```

returned its operative mapping, including `bracket_screen_s == "0.013701"`.

Their complete production caller census is:

| Helper | Production callers |
|---|---|
| `_authenticate_acceptance_bytes` | Guarded wrapper at `calibration_bracketing.py:1290`; inspection function at `:1310` |
| `_registered_operatives_unchecked` | Public operative function at `:650`; validator at `:868` |
| `inspect_acceptance_without_claim_authority` | No production caller outside its definition |

The public wrapper and operative API refused held input. The validator returned only a Boolean, and inspection output failed reauthentication when presented to claim consumers. Thus, **no enrolled production caller was demonstrated to carry these unchecked results through a successful claim path**.

Nevertheless, §6.1(4) expressly counts held content or numbers returned by *any function other than the inspection function*. Direct helper calls meet that endpoint. Their underscore names and the passing reference census do not prevent invocation.

**SHOULD-FIX:** None independently established.

**NIT:** None.

Under HOLD-BY-CONSTRUCTION-01 §6.2, the next step is to **stop this issuing transaction and return the route evidence to the owner**. This report proposes no fourth production repair round.

## Residual risk

- This is not completion of §7 step 7. All 24 C-5 files were enumerated, but execution of every listed reader and launch entry was unfinished when immediate reporting was requested.
- `probe_core.py` completed its route, authentication, capture, bracket, and endpoint assertions, then failed because its final input-writer call used the wrong argument shape.
- `probe_readers.py` completed the listed reader probes, then failed before `load_analysis_inputs` reached its calibration reader because the scratch runs directory was absent. Its subsequent G2A probe did not execute.
- An initial route/census run passed 28 tests and hit a safety-blocked Git initialization in the continuation fixture. The continuation and GO checks were subsequently exercised separately without Git writes. No complete passing route/census rerun is claimed.
- GO probes used synthetic fixtures and substituted fixture Git setup/hash handling. They establish execution of S2 and its two callers, not full real-pack launch authentication.
- No child was launched, no capture or powermetrics session ran, no laptop battery was read, and no `sudo`, system-setting change, Claude call, repository write, or Git write occurred. Scratch artifacts are under `/tmp/d138-hold4-d528efb2/`.
- The full suite and final workspace-state check were not run.