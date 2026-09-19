```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two should-fix findings: census evidence is lost or pooled, and summary JSON drops PROVISIONAL provenance; 31 offline tests pass.",
  "workspace": {
    "base_requested": "7faaf2d0",
    "base_mode": "exact",
    "head_start": "d066d271b37849c3fcaf67807044d5b5b326e81e",
    "head_end": "d066d271b37849c3fcaf67807044d5b5b326e81e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 2,
      "nit": 0
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "text": "Concurrent round censuses are not retained, and summaries pool clean, contaminated, and census-unknown evidence without labels."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "text": "summary.json drops the PROVISIONAL label and conditional alignment provenance."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 0.124s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/quiet-contract-review-d066d271.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "summary_unchanged_after_reference_census_flip=True",
          "contaminated_reference_complete_rounds=1",
          "summary_json_has_PROVISIONAL=False",
          "partial_observation=None",
          "partial_row_has_separate_census=False",
          "OFFLINE_COUNTEREXAMPLES_CONFIRMED"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OFFLINE_COUNTEREXAMPLES_CONFIRMED$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check 7faaf2d0 d066d271 && git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "d066d271b37849c3fcaf67807044d5b5b326e81e"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "d066d271b37849c3fcaf67807044d5b5b326e81e$"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The supplied brief defines D1 through D7 only; no D8 definition exists at this head.",
      "needs": "Supply D8 if an eighth deliverable was intended."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Review used source inspection and offline fixtures only; no live collection, load, network, sudo, powermetrics, or canonical discovery suite.",
      "needs": "Lead retains live verification."
    }
  ]
}
```

## Findings

**F1 — should_fix: Census evidence does not reliably distinguish clean rounds from contaminated rounds.**

There are two connected losses:

- The production sampler includes `observation.census` (`joulewise/quiet_admission.py:267–277`), and the harness retains that observation (`scripts/sample_quiet_predicate_evidence.py:537–547`). However, the smoke round’s separate concurrent censuses go into a temporary journal (`scripts/run_night.py:2612`, `:2673`), and its return contains only the sample observation and cost (`:2701`). The harness saves worker identities and lifecycle state, not census results (`scripts/sample_quiet_predicate_evidence.py:405–418`). A partial round without a completed sample has `observation: null` and no separate census result.
- `aggregate()` selects solely by `status == "complete"` (`:909–934`). `summarize()` groups solely by state/repeat and pools the reference state (`:945–965`). Neither output labels census cleanliness.

**Counterfactual:** An agent is detected by a concurrent census but exits before the sampler’s final census. The persisted sample can look census-clean while the earlier hit disappears. Production admission instead stops on concurrent census refusal (`scripts/run_night.py:2470–2476`) and sampler census hits (`:2515–2517`).

**Offline reproduction:** V2 changes only an idle reference row’s census from empty/exit 1 to `123 claude -p`/exit 0, then calls `summarize(root, "idle")`. The entire summary remains identical, and the contaminated reference remains counted as complete. This exercises the implementation behind:

```sh
python3 -B scripts/sample_quiet_predicate_evidence.py summarize --in DIR --reference-state idle
```

Record 14 decision 3 requires census-clean evidence (`14-magistrate-adjudication-consult-06.md:9`); decision 5 requires a census-clean reference (`:11`). Preserve available concurrent results, explicitly represent unknown census coverage, and group or label summaries by census condition.

**F2 — should_fix: Machine-readable summaries lose the PROVISIONAL qualification.**

Collection records `evidence_status: "PROVISIONAL"` and unknown network-time provenance in `session.json` (`scripts/sample_quiet_predicate_evidence.py:583–584`), and round alignment carries a PROVISIONAL model label (`:684–686`). Markdown summaries also carry the label (`:988`).

But the JSON summary constructed at `:963–966` retains neither the label nor the alignment model/network-time qualification. This matters because the imported anchor explicitly treats unknown network-time provenance as validation-only and requires that provenance to accompany derived records (`joulewise/uncertainty_evidence.py:826–844`). Repository instructions also require PROVISIONAL labels without live validation (`docs/orchestration.md:88–90`).

**Counterfactual:** Summarize otherwise complete, bounded rows collected with unknown network-time provenance, then consume only `summary.json`. It contains numerical ΔJ and alignment bounds without the qualification attached to its inputs.

**Reproduction:** V2 executes the same `summarize` entry point and reports `summary_json_has_PROVISIONAL=False`. Carry the evidence status and relevant bound conditions into JSON summaries.

**C1 — Deliverable coverage**

References below use `scripts/sample_quiet_predicate_evidence.py` unless stated otherwise.

| Deliverable | Assessment | Implementation/evidence |
|---|---|---|
| D1 | MET by inspection/offline tests | `collect`, CLI flags `:1016–1024`; production round `:343–418`; one recorder `:594–598`; deadline signaling and cleanup `:448–534`; partial clipping `:615–622`; session metadata `:569–586`, `:624–626`. Live cleanup remains unverified. |
| D2 | MET | Bracketed `Clock.stamp()` `:102–107`; production anchor call `:195–212`; overlap integration `:219–271`; per-row bound `:667–686`. |
| D3 | MET | Native power conversion and residency parsing `:142–192`; support-weighted rail/entity reduction `:219–271`. |
| D4 | MET for brief’s requested outputs | `load` flags `:1025–1032`; separate OS processes and preallocation `:701–717`, `:830–850`; thread-CPU budgets/calibration/freeze `:720–777`; stationarity statistics `:780–795`. Native behavior unverified. |
| D5 | PARTIAL | Quantiles, coverage-weighted powers, ΔJ480, propagated bounds, disagreement counts and JSON/Markdown exist `:896–990`; census handling and JSON qualification fail F1/F2. |
| D6 | MET for listed fields; PARTIAL with C6 requirement | All listed keys initialized `:65–71`, `:537–547`; recursive null reasons `:74–84`; census limitations are F1. |
| D7 | MET for brief’s enumerated tests | Tests cover argv/units `tests/test_sample_quiet_predicate_evidence.py:105–139`, alignment/integration `:156–231`, partial/schema `:236–254`, duty/stationarity `:445–484`, summary ΔJ `:499–518`. V1 passes all 31 tests. Census fixtures are insufficient to catch F1. |
| D8 | MISSING definition | Brief 11 lists D1–D7 at `:20–26`, then Rules at `:28–30`. No D8 was silently dropped by the implementation. |

**C2 — Production reuse and cited ranges**

Production symbols used include:

- `quiet_admission.sample_interval`, `publish_observation`, `parse_ps`, `top_argv`, `PS_ARGV`, `BOOT_ARGV`.
- `run_night.smoke_observation_round`, `_BindTask`, `_bind_argv`.
- `pm.PowermetricsTelemetryAdapter._command`, `POWER_METRICS`, `_powermetrics_documents`, `_timestamp_epoch_ns_utc`.
- `ClockStamp`, `NativeAnchorRecord`, `derive_powermetrics_anchor_v3`.

Call sites are harness `:134–139`, `:163–172`, `:195–202`, `:312–335`, `:343–377`, `:467–470`, `:571`, `:1056`.

The cited production ranges resolve as follows:

- `run_night.py:2603–2712`: smoke function starts at 2603 and ends at 2701; the cited range extends into `run_night`.
- `quiet_admission.py:231–278`: actual sampler, including interval metrics and sampler census. **Framed publication is at `:298–316`**, and the harness calls it.
- `powermetrics.py:1775–1785`: endpoint advancement using elapsed durations.
- `powermetrics.py:2009–2025`: interval supports ending at each record’s timestamp.
- The rate-aware anchor itself lives at `uncertainty_evidence.py:814`, imported directly by the harness.

The harness independently implements rail conversion/summing, anchor-record projection, and endpoint/support construction (`:174–211`), corresponding to adapter `:1791–1799`, `:1837–1860`, `:1775–1785`, and `:2009–2025`. Thus production telemetry transformations are re-expressed, although the anchor solver is imported.

**No reimplemented quiet-predicate or admission decision logic found.** The sampler still computes production `busy_cores`; the harness never calls or duplicates the cutoff decision. Its local overlap reducer and load controller are new harness functions.

**C3 — Authority boundary**

No production import of the harness or fixed write into plans/source was found.

Commands run:

```sh
rg -n 'sample_quiet_predicate_evidence' joulewise scripts --glob '*.py'
rg -n 'write_text|write_bytes|open\(|mkdir|write_json|cutoff|is_quiet' scripts/sample_quiet_predicate_evidence.py
```

The first returned only the harness’s own documentation examples. Inspected writes target collection output/raw files, load log, internal worker paths supplied from collection output, or the D5-authorized `summary.json`/`summary.md` under `--in`. Imported smoke journaling uses a temporary directory (`run_night.py:2612`). No cutoff authoring or admission coupling found.

**C4 — Actual schema and units**

All brief-listed top-level fields are emitted:

`schema, session, state, repeat, round, status, error, epoch_s, boot_id, load_setting, round_wall_start_s, round_wall_end_s, round_mono_start_s, round_mono_end_s, observation, observer_cpu_s, power, clusters, cpus, alignment, raw`.

All requested rail, cluster, CPU, alignment and raw-path/hash fields are present when their enclosing evidence exists; unavailable enclosing values are null with sibling reasons. Additional fields include rail coverage/energy/bounds, clock stamps, support descriptions and mismatch diagnostics (`:250–270`, `:553–555`, `:627–640`, `:677–692`).

Conversions read: mW→W and mJ→J divide by 1000 (`:179`, `:183`); ns→s divides by 1e9 (`:186–187`); overlap seconds×W produces joules (`:241`). No requested unit mismatch found.

Production top-consumer entries carry the boolean `observer` label (`quiet_admission.py:154–162`), retained inside the observation. PROVISIONAL labels exist in session metadata, row alignment and Markdown; JSON summary omission is F2.

**C5 — Alignment failure behavior**

No arrival-time or linear fallback found. `align_frames()` returns no aligned frames when the production anchor is unbounded (`:202–204`).

For emitted rows:

- Disabled power supplies `"power disabled"` (`:593`).
- Finalization exceptions supply their exception text (`:657–659`).
- Production anchor failures preserve production `detail`, falling back to `reason` (`:669`, `:681–683`).
- Incomplete rail coverage supplies an explicit unbounded-energy reason (`:679–680`).
- Recursive serialization supplies reasons for other null fields (`:74–84`, `:696`).

The row uses the production detail string; the full production anchor, including its standardized reason, remains in recorder metadata (`:532–533`; production unresolved shape at `uncertainty_evidence.py:704–718`). A null alignment bound in the inspected emitted-row branches carries a reason.

**C6 — Census-clean condition**

**PARTIAL:** completed sample observations retain their census. Every-round census coverage and census-aware summary labeling are absent; see F1.

## Residual risk

No hardware claims were tested. Native QoS, actual recorder descendant termination, and live clock/coverage behavior remain lead-owned verification.

Only `/tmp/quiet-contract-review-d066d271.py` and temporary fixture artifacts were written. The repository remained clean at the requested head. Next step: lead adjudicates F1/F2 and supplies D8 only if an additional requirement exists.