# PACK_AUTHENTICATION consumption sites

This inventory separates semantic consumers from immutable artifacts and from
historical prose that merely names the kind. That distinction matters: an
“honest-limit everywhere” cure would have to change every current semantic
consumer and operator-facing claim, but it cannot rewrite frozen artifacts or
historical records.

## Production definition and derivation

| Site | Consumption |
|---|---|
| `joulewise/arm_readiness_evidence.py:99-119` | Admits the kind and assigns its execution-environment fingerprint policy. |
| `joulewise/arm_readiness_evidence.py:1052-1075` | Bare generator-check recorder: successful exit becomes the `pack_generator_check` check evidence. |
| `joulewise/arm_readiness_evidence.py:1078-1098`, `:1387-1634` | Defines and executes the projected-pack composed authentication. |
| `joulewise/arm_readiness_evidence.py:1647-1741` | `_derive_pack_authentication`; selects projected/bare mode and emits all six `desk.current_pack.v1` PASS keys, including `pack_generator_check_status`. |
| `joulewise/arm_readiness_evidence.py:2157-2169` | Dispatches the registry kind to the deriver. |
| `joulewise/arm_readiness_evidence.py:2960-2967`, `:2977-3055` | Existing-evidence predicate replay and new generic evidence authoring. |

## Production validation and gating

| Site | Consumption |
|---|---|
| `configs/arm_readiness/d117_row_registry_v1.json:183-190`; `configs/arm_readiness/d117_row_registry_v2.json:715-722` | Registry row `desk.current_pack` requires `PACK_AUTHENTICATION` with predicate `desk.current_pack.v1`. |
| `configs/arm_readiness/d117_row_registry_v2.json:128-132` | Assigns the kind its R1 execution-bound freshness policy. |
| `joulewise/arm_readiness.py:727-757` | Admits GIT/PACK/PROBE source kinds for PACK_AUTHENTICATION. |
| `joulewise/arm_readiness.py:764-794` | Classifies it `EXECUTION_BOUND`. |
| `joulewise/arm_readiness.py:801-840` | Requires the exact six `desk.current_pack.v1` values to be PASS. This is the main unqualified semantic consumer. |
| `joulewise/arm_readiness.py:984-1003` | Maps the predicate to `PACK_AUTHENTICATION`. |
| `joulewise/arm_readiness.py:5409-5465` | Authenticates a generic evidence item and its receipt/sidecar binding. |
| `joulewise/arm_readiness.py:5633-5871` | Discovers receipts, authenticates sidecars, source SHA values, freshness and identity. |
| `joulewise/arm_readiness.py:5902-5941` | `_predicate_passes` admits a PACK_AUTH receipt when its fact source and six values match. |
| `joulewise/arm_readiness.py:5998-6044` | `_evaluate_rows` converts that predicate result into the row verdict. |
| `joulewise/arm_readiness.py:6475-6555` | `_load_freeze_reference` replays freeze evidence and the current-pack row. |
| `joulewise/arm_readiness.py:6749-6784` | `generate_freeze_receipt`; histsem-gates a predecessor and then evaluates evidence for the new freeze. |
| `joulewise/arm_readiness.py:7525-7568` | `generate_arm_receipt`; histsem-gates the pack and loads/re-evaluates its freeze evidence. |
| `joulewise/arm_readiness.py:8016-8139` | Arm receipt verification recomputes rows/refusals; PACK_AUTH therefore reaches the launch-capability verdict. |
| `joulewise/arm_readiness.py:3481-3719`, `:3753-3817` | Receipt-historical-semantics verifier and pre-freeze/pre-arm gate authenticate the historical/current byte coordinates containing PACK_AUTH evidence. |
| `joulewise/arm_readiness.py:10868-10925` | Family-publication verification is a generic downstream admission boundary for the governed pack/freeze state. |
| `scripts/build_v4_histsem_pinset.py:146-235` | Authenticates the current plan/freeze and all eleven generic receipts, including PACK_AUTH, while building the v4 historical/current composition row. It checks generic bindings, not PACK_AUTH's derivation meaning. |
| `joulewise/scheduler_gates.py:1049-1077` | Scheduler construction calls `_pack_record`; invalid arm-readiness pack authentication cannot be represented as a scheduler PASS placeholder. |
| `scripts/launch_window.py:97-135` | Launch consumption re-verifies the ARM receipt, thereby transitively consuming the PACK_AUTH row. |

`configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json:1-1470` is also a
machine-readable consumer of the nine PACK_AUTH receipt/source/freeze bindings:
its nine pack rows store historical and current pack digests, exact receipt
inventory, and closed deltas. Direct PACK_AUTH inventory entries begin near
lines 114, 276, 438, 602, 765, 928, 1092, 1255, and 1418.

## Frozen verdict carriers

Each of the nine pack directories contains exactly these three direct carriers:

```text
configs/campaigns/<PACK>/arm_readiness.sources/pack-authentication.json
configs/campaigns/<PACK>/arm_readiness.evidence/evidence-pack-authentication.json
configs/campaigns/<PACK>/arm_readiness.freeze.receipts/freeze-000N.json
```

The source records the detailed checks and the six-key fact; the evidence
receipt repeats and SHA-binds that fact/source; the freeze receipt admits the
evidence item. There are 27 such files across the three families and three
ordinals. They are immutable historical evidence, not cure edit targets. A
consumer-side interpretation must remain backward compatible with all 27.

The three author transcripts at
`docs/process_traces/2026-08-19-refreeze-execution/s4/author-*.json` are further
historical outputs that list PACK_AUTHENTICATION as authored; they are records,
not runtime consumers.

## Current operator-facing and normative prose

These sites tell an operator or reviewer what the verdict means and therefore
are the edit targets if the cure chooses the honest-limit-only branch:

* `docs/phase_2/alpha_arm_readiness.md:92-110`, especially `:105`, calls
  `desk.current_pack` a prior PASS needing successor re-freeze.
* `docs/phase_2/beta_arm_readiness.md:25-42`, especially `:33`, says the
  generator check, validators, specification, policy and digest describe the
  same completed BETA pack.
* `docs/phase_2/gamma_arm_readiness.md:30-47`, especially `:38`, makes the same
  unqualified GAMMA claim.
* `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/
  coldgate-adjudicator-ruling.md:16-26`, especially `:21`, rules the kind
  content-bound over committed bytes without stating the echo limit.
* `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/consult.md:
  122-134`, especially `:130`, places all PACK_AUTH receipts in one
  CONTENT_BOUND bucket.
* `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/
  coldgate-opus-refuter-findings.md:12-17` describes the executed check and its
  environment weakness, but not echo semantics.
* `docs/process_traces/2026-08-19-prep-sprint/registry-packet/
  02-environment-comparison-semantics.md:116-144` and
  `03-execution-bound-horizons.md:95-144` define the current environment and
  horizon treatment.
* `docs/decision_log.md:9318-9334`, especially `:9325`, carries the current
  PACK_AUTH environment-fingerprint decision.
* `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r3.md:24-36`
  records its fail-closed environment consequence.
* `RUN_STATE.md:213`, `:256`, and `:274`; `TASK_QUEUE.md:649-650` and
  `:770-771`; `docs/process/state_kernel.json:1703` and `:3314-3331` are the
  live status/acceptance consumers for A93/A94.

## Runsheets and transaction manifests

These sites consume the kind as an exact expected member of the generic
receipt set; they do not inspect the six values themselves:

* `docs/process_traces/2026-08-22-t20/s0-runsheet-r1.md:263,535`
* `docs/process_traces/2026-08-22-t20/s0-runsheet-r2.md:429,819`
* `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1433,2559`
* `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:83`
* `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md:357`
* `docs/process_traces/2026-08-19-prep-sprint/ready-packet/
  10-ROW-L1-authority-plane.md:50` and its byte-identical
  `ready-packet-rows/10-ROW-L1-authority-plane.md:50`

An honest-limit-only cure must ensure these exact-kind censuses do not display
an unqualified PASS without an adjacent derivation-mode meaning. A real
historical derivation cure can leave their membership/count semantics intact.

## Historical incident/design records

These are evidence of past decisions or incidents rather than live contracts;
they should be cross-referenced, not rewritten:

* `docs/process_traces/2026-08-13-freeze-execution/freeze-log.md:14-25`
* `docs/run_reports/2026-08-13-t6-session.md:554-568`
* `docs/process_traces/2026-08-20-go-session/{cold-delta-verdicts.md,
  opus-reg-report.md,terra-reg-report.md,readiness-sitting/seat-L8.md,
  v4plan/opus-design.md,v4plan/sol-design.md}` at their PACK_AUTH matches
* `docs/process_traces/2026-08-24-p06-codesign/01-seat-a-design.md:203`
* `docs/process_traces/2026-08-24-pinset-refuter/refuter-envelope.md:41`

## Tests that consume or fixture the claim

Implementation blast-radius tests are
`tests/test_arm_readiness_evidence_packauth.py:1-485`,
`tests/test_arm_readiness_evidence.py:251,497-528`,
`tests/test_arm_readiness.py:1554,1631`,
`tests/test_arm_readiness_evidence_t0.py:834`, and
`tests/test_arm_readiness_schemas.py:246-257,464,664-676`. The schema and
registry fixtures currently assume the exact six-key object; a cure should not
add a seventh required fact key and thereby invalidate frozen receipts.

