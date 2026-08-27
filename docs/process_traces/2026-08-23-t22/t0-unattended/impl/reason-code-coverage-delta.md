# T0-UNATTENDED-01 — enumerated refusal-code delta

## 0. Contract header

- **Row:** `T0-UNATTENDED-01`.
- **Authority:** `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`, read in full before every other design source.
- **Measured HEAD:** `2fd7c920314333535ea2631bec887a19b964f834` on `impl/t0-unattended-01`.
- **Census date:** 2026-08-26.
- **Purpose:** this pre-implementation contract enumerates the refusal-code
  consequences of the ruled design. `NEEDS-RULING` means an exact authority
  question that implementation cannot answer. Both questions this document
  raised were answered on 2026-08-26: §6.2 is RULED (the production consumer is
  `UNATTENDED-LAUNCH-01`'s, not this row's) and §6.3 is COLD-GATE-PENDING (the
  conflict is a defect in the magistrate's own prior ruling, so a cold instance
  rules, and the implementation is frozen exactly as landed meanwhile).

A **refusal code** is the exact string carried by a failed producer or receipt.
A code is **registered** when it belongs to the code-owned set that authorizes
that namespace. A code is **produced** when the current scanner finds its exact
runtime literal. `REASON_CODE_COVERAGE` is the evidence kind whose current
deriver proves the registered `readiness_*` set relations and runs the named
focused test (`joulewise/arm_readiness_evidence.py:1999-2079`). A **fresh census**
means re-running the printed command at the current HEAD instead of copying an
earlier total.

Disposition words have one meaning throughout this document:

- `ADDED` means a spelling absent at HEAD would be introduced.
- `RETIRED` means a spelling present in the stated HEAD census would disappear
  from that census.
- `REUSED-UNCHANGED` means the spelling remains in its registered set and gains
  no new refusal meaning; an obsolete emission site may still be removed.
- `RE-TARGETED` means an existing spelling remains and gains a newly ruled
  physical cause.

The **author** is `joulewise/arm_readiness_evidence_t0.py`, which derives and
validates T-0 PASS receipts before publishing them.

An **ARM receipt** is the `joulewise.arm_readiness_receipt.v1` GO/NO-GO record
validated at `joulewise/arm_readiness.py:2404-2454`. A **freeze receipt** is the
non-authorizing frozen-row record validated at `arm_readiness.py:2328-2375`. A
**PASS evidence namespace** is the complete source-and-receipt directory pair
whose receipts have `status: PASS`; the T-0 publisher makes incompleteness
detectable before it writes the final marker
(`arm_readiness_evidence_t0.py:1796-1811`). A **successor rehearsal** is the
final supervised rehearsal at the implementation HEAD required by
`docs/phase_2/alpha_arm_readiness.md:72,111`.

**Rehearsal-observable** means a ruled rehearsal row deliberately triggers and
records the exact refusal code. **Unit-level only** means a deterministic test
may observe the code but the ruled rehearsal has no negative injection for it.

A **production consumer** is an executable production entry point authorized
to accept a receipt, not the process that performs the supervised rehearsal.
The **R1 lifecycle
registry** is the current v2 table whose roles select lifecycle refusal codes
and types. The **R0 clock reference** is the pre-disable SNTP batch; the **R1
clock reference** is the authoring-time SNTP batch. Those clock labels are
unrelated to the lifecycle-registry label. **Role-resolved** means
that a lifecycle-registry role selects the refusal code and type at runtime
(`arm_readiness.py:1888-1946`). A **round-trip** means constructing a refusal
and validating it under the same registered spelling
(`arm_readiness_evidence.py:2055-2058`). The **mirror test** is the independent
test-side repetition of the production census
(`tests/test_arm_readiness_integration.py:583-639`). **Archival row wiring** is
the immutable v1 registry row that names the evidence kind; **SHA-pinned** means
its expected file digest is fixed by a test
(`tests/test_arm_readiness_schemas.py:500-502`).

The two vocabularies are separate. A **readiness refusal** is a `readiness_*`
code which an ARM or freeze receipt may carry. A **T-0 evidence-author
refusal** is an `evidence_author_t0_*` code returned when the T-0 producer or
author fails before it can publish a PASS evidence namespace. The currently
enforced `desk.reason_code_plumbing` row checks only the first vocabulary; its
registry definition requires `REASON_CODE_COVERAGE`
(`configs/arm_readiness/d117_row_registry_v1.json:237-244`).

The read head was measured with:

```text
$ git rev-parse HEAD
2fd7c920314333535ea2631bec887a19b964f834
$ git rev-parse --abbrev-ref HEAD
impl/t0-unattended-01
$ git rev-parse origin/main
954328078194b557af967505ef88edea6aa56d27
$ git merge-base HEAD origin/main
2fd7c920314333535ea2631bec887a19b964f834
```

`origin/main` advanced after this worktree was cut; the contract therefore
describes the exact HEAD above, not the later upstream commit. Rebase or merge
is a mandatory re-census trigger.

## 1. Baseline census

### 1.1 Vocabulary A — ARM-readiness `readiness_*` codes

Here **registered** means membership in `READINESS_REASON_CODES`. Here
**produced** means a double-quoted `readiness_[a-z0-9_]+` literal in
`joulewise/arm_readiness.py` after the `class ArmReadinessError` split point;
that is the exact scan performed by the currently enforced deriver at
`joulewise/arm_readiness_evidence.py:2018-2025`. Here **dynamic** means a
registered code which is intentionally not such a literal and is enumerated
in the deriver's set at `joulewise/arm_readiness_evidence.py:2031-2049`.

The family sets are declared at `joulewise/arm_readiness.py:123-204`, united
at `:216-229`, and typed through `REASON_TYPE_BY_CODE` at `:230-243`. The
following command imports those exact objects, repeats the deriver's literal
scan, and AST-reads the deriver's `dynamic` assignment:

```text
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'import ast, inspect, re; import joulewise.arm_readiness as a; import joulewise.arm_readiness_evidence as e; src=inspect.getsource(a).split("class ArmReadinessError",1)[1]; produced=set(re.findall(r"\"(readiness_[a-z0-9_]+)\"",src)); tree=ast.parse(inspect.getsource(e._derive_reason_code_coverage)); dynamic=ast.literal_eval(next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="dynamic" for t in n.targets))); registered=set(a.READINESS_REASON_CODES); print("registered_count",len(registered)); print("registered",*sorted(registered),sep="\n"); print("produced_count",len(produced)); print("produced",*sorted(produced),sep="\n"); print("dynamic_count",len(dynamic)); print("dynamic",*sorted(dynamic),sep="\n"); print("produced_minus_registered",sorted(produced-registered)); print("registered_minus_produced",sorted(registered-produced)); print("registered_minus_produced_equals_dynamic",registered-produced==dynamic)'
registered_count 55
registered
readiness_backup_preflight_refused
readiness_clock_preflight_refused
readiness_dependency_refused
readiness_dry_run_missing
readiness_dry_run_refused
readiness_dry_run_stale
readiness_dry_run_used_as_arm_record
readiness_evidence_digest_mismatch
readiness_evidence_reference_invalid
readiness_evidence_unreadable
readiness_freeze_receipt_mismatch
readiness_freeze_receipt_unreadable
readiness_git_tree_dirty
readiness_identity_artifact_unreadable
readiness_identity_environment_dirty
readiness_identity_pinset_frozen_mismatch
readiness_identity_projection_mint_divergence
readiness_identity_receipt_namespace_anomalous
readiness_internal_error
readiness_io_error
readiness_launch_capability_unavailable
readiness_ledger_preflight_refused
readiness_lock_unavailable
readiness_machine_preflight_refused
readiness_output_collision
readiness_pack_digest_mismatch
readiness_pack_namespace_anomalous
readiness_pack_not_committed
readiness_pack_unreadable
readiness_r1_class_mismatch
readiness_r1_dependency_changed_set
readiness_r1_dependency_manifest
readiness_r1_family_publication
readiness_r1_successor_chain
readiness_r1_temporal_budget
readiness_r1_unknown_policy
readiness_r1_v1_grandfathering
readiness_receipt_kind_invalid
readiness_receipt_namespace_anomalous
readiness_receipt_superseded
readiness_record_consumed
readiness_record_expired
readiness_reviewed_main_mismatch
readiness_root_binding_invalid
readiness_root_not_fresh
readiness_row_applicability_invalid
readiness_row_registry_mismatch
readiness_row_set_incomplete
readiness_schema_invalid
readiness_successor_chain_invalid
readiness_terminal_review_missing
readiness_unknown_key
readiness_usage_invalid
readiness_waiver_set_nonempty
readiness_waiver_source_invalid
produced_count 45
produced
readiness_backup_preflight_refused
readiness_clock_preflight_refused
readiness_dependency_refused
readiness_dry_run_missing
readiness_dry_run_refused
readiness_dry_run_stale
readiness_dry_run_used_as_arm_record
readiness_evidence_digest_mismatch
readiness_evidence_reference_invalid
readiness_evidence_unreadable
readiness_freeze_receipt_mismatch
readiness_freeze_receipt_unreadable
readiness_git_tree_dirty
readiness_identity_artifact_unreadable
readiness_identity_environment_dirty
readiness_identity_pinset_frozen_mismatch
readiness_internal_error
readiness_io_error
readiness_launch_capability_unavailable
readiness_ledger_preflight_refused
readiness_machine_preflight_refused
readiness_output_collision
readiness_pack_digest_mismatch
readiness_pack_namespace_anomalous
readiness_pack_not_committed
readiness_pack_unreadable
readiness_r1_family_publication
readiness_receipt_kind_invalid
readiness_receipt_namespace_anomalous
readiness_receipt_superseded
readiness_record_consumed
readiness_record_expired
readiness_reviewed_main_mismatch
readiness_root_binding_invalid
readiness_root_not_fresh
readiness_row_applicability_invalid
readiness_row_registry_mismatch
readiness_row_set_incomplete
readiness_schema_invalid
readiness_successor_chain_invalid
readiness_terminal_review_missing
readiness_unknown_key
readiness_usage_invalid
readiness_waiver_set_nonempty
readiness_waiver_source_invalid
dynamic_count 10
dynamic
readiness_identity_projection_mint_divergence
readiness_identity_receipt_namespace_anomalous
readiness_lock_unavailable
readiness_r1_class_mismatch
readiness_r1_dependency_changed_set
readiness_r1_dependency_manifest
readiness_r1_successor_chain
readiness_r1_temporal_budget
readiness_r1_unknown_policy
readiness_r1_v1_grandfathering
produced_minus_registered []
registered_minus_produced ['readiness_identity_projection_mint_divergence', 'readiness_identity_receipt_namespace_anomalous', 'readiness_lock_unavailable', 'readiness_r1_class_mismatch', 'readiness_r1_dependency_changed_set', 'readiness_r1_dependency_manifest', 'readiness_r1_successor_chain', 'readiness_r1_temporal_budget', 'readiness_r1_unknown_policy', 'readiness_r1_v1_grandfathering']
registered_minus_produced_equals_dynamic True
```

Thus the measured relation is:

```text
produced (45) is a subset of registered (55)
produced - registered = empty
registered - produced = dynamic (10), exactly
registered = produced disjoint-union dynamic
```

The row is currently enforced because registry v1 maps
`desk.reason_code_plumbing.v1` to `REASON_CODE_COVERAGE` at
`configs/arm_readiness/d117_row_registry_v1.json:237-244`. The current
obligation is also stated twice in
`docs/phase_2/alpha_arm_readiness.md:72` and `:111`: the prior row passed,
PR #152 added T-0 acquisition refusals, and the final successor rehearsal
must verify registry coverage and the refusal code/type/row/evidence fields.

### 1.2 Vocabulary B — T-0 evidence-author `evidence_author_t0_*` codes

The module has two ways to spell a code. Thirty codes are string literals.
Fourteen `*_underivable` codes are generated at
`joulewise/arm_readiness_evidence_t0.py:301-306` from the thirteen distinct
row kinds in `_ROW_KIND` (`:85-101`) plus `AUTHORING_SET`. The following AST
census counts both forms and reports every literal's mapping or raise-site
line:

```text
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'import ast,re; from pathlib import Path; import joulewise.arm_readiness_evidence_t0 as t; p=Path("joulewise/arm_readiness_evidence_t0.py"); tree=ast.parse(p.read_text()); literals={}; [literals.setdefault(n.value,[]).append(n.lineno) for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str) and re.fullmatch(r"evidence_author_t0_[a-z0-9_]+",n.value)]; generated={f"evidence_author_t0_{kind.lower()}_underivable" for kind in set(t._ROW_KIND.values())|{"AUTHORING_SET"}}; codes=set(literals)|generated; print("literal_distinct_count",len(literals)); [print(code,"literal_lines="+",".join(map(str,sorted(literals[code])))) for code in sorted(literals)]; print("generated_underivable_count",len(generated)); [print(code,"generator_line=304") for code in sorted(generated)]; print("all_distinct_count",len(codes)); print("all_codes"); [print(code) for code in sorted(codes)]'
literal_distinct_count 30
evidence_author_t0_arm_context_missing literal_lines=149,570
evidence_author_t0_clock_attestation_missing literal_lines=150,521
evidence_author_t0_clock_disable_missing literal_lines=152
evidence_author_t0_clock_prior_state_missing literal_lines=151
evidence_author_t0_existing_invalid literal_lines=1864,1867
evidence_author_t0_existing_stale literal_lines=1894,1898,1902
evidence_author_t0_identity_epoch_missing literal_lines=161
evidence_author_t0_input_changed literal_lines=1759,1764,2023,2026
evidence_author_t0_internal_error literal_lines=1774,1989,2058
evidence_author_t0_launch_manifest_missing literal_lines=157,616
evidence_author_t0_ledger_readiness_missing literal_lines=155
evidence_author_t0_ledger_reservation_missing literal_lines=156
evidence_author_t0_output_collision literal_lines=1821,1829,2053
evidence_author_t0_pack_uncommitted literal_lines=1951
evidence_author_t0_predicate_refused literal_lines=2015
evidence_author_t0_prewindow_check_missing literal_lines=154
evidence_author_t0_production_ledger_missing literal_lines=163
evidence_author_t0_publication_incomplete literal_lines=1974
evidence_author_t0_publication_interrupted literal_lines=2074
evidence_author_t0_quiet_mac_prep_missing literal_lines=153
evidence_author_t0_repository_mismatch literal_lines=1924
evidence_author_t0_reviewed_tree_mismatch literal_lines=1934
evidence_author_t0_row_census_mismatch literal_lines=747,753
evidence_author_t0_t1_bindings_missing literal_lines=162
evidence_author_t0_tap_sequence_invalid literal_lines=1644
evidence_author_t0_terminal_review_record_missing literal_lines=951
evidence_author_t0_validation_failed literal_lines=2049
evidence_author_t0_waiver_record_missing literal_lines=160
evidence_author_t0_window_chain_missing literal_lines=159
evidence_author_t0_window_environment_missing literal_lines=158
generated_underivable_count 14
evidence_author_t0_authoring_set_underivable generator_line=304
evidence_author_t0_backup_preflight_underivable generator_line=304
evidence_author_t0_clock_attestation_underivable generator_line=304
evidence_author_t0_clock_probe_underivable generator_line=304
evidence_author_t0_launch_recipe_underivable generator_line=304
evidence_author_t0_ledger_reservation_underivable generator_line=304
evidence_author_t0_machine_preflight_underivable generator_line=304
evidence_author_t0_maintenance_census_underivable generator_line=304
evidence_author_t0_offline_input_inventory_underivable generator_line=304
evidence_author_t0_power_preflight_underivable generator_line=304
evidence_author_t0_powermetrics_probe_underivable generator_line=304
evidence_author_t0_process_census_underivable generator_line=304
evidence_author_t0_root_preflight_underivable generator_line=304
evidence_author_t0_terminal_review_underivable generator_line=304
all_distinct_count 44
all_codes
evidence_author_t0_arm_context_missing
evidence_author_t0_authoring_set_underivable
evidence_author_t0_backup_preflight_underivable
evidence_author_t0_clock_attestation_missing
evidence_author_t0_clock_attestation_underivable
evidence_author_t0_clock_disable_missing
evidence_author_t0_clock_prior_state_missing
evidence_author_t0_clock_probe_underivable
evidence_author_t0_existing_invalid
evidence_author_t0_existing_stale
evidence_author_t0_identity_epoch_missing
evidence_author_t0_input_changed
evidence_author_t0_internal_error
evidence_author_t0_launch_manifest_missing
evidence_author_t0_launch_recipe_underivable
evidence_author_t0_ledger_readiness_missing
evidence_author_t0_ledger_reservation_missing
evidence_author_t0_ledger_reservation_underivable
evidence_author_t0_machine_preflight_underivable
evidence_author_t0_maintenance_census_underivable
evidence_author_t0_offline_input_inventory_underivable
evidence_author_t0_output_collision
evidence_author_t0_pack_uncommitted
evidence_author_t0_power_preflight_underivable
evidence_author_t0_powermetrics_probe_underivable
evidence_author_t0_predicate_refused
evidence_author_t0_prewindow_check_missing
evidence_author_t0_process_census_underivable
evidence_author_t0_production_ledger_missing
evidence_author_t0_publication_incomplete
evidence_author_t0_publication_interrupted
evidence_author_t0_quiet_mac_prep_missing
evidence_author_t0_repository_mismatch
evidence_author_t0_reviewed_tree_mismatch
evidence_author_t0_root_preflight_underivable
evidence_author_t0_row_census_mismatch
evidence_author_t0_t1_bindings_missing
evidence_author_t0_tap_sequence_invalid
evidence_author_t0_terminal_review_record_missing
evidence_author_t0_terminal_review_underivable
evidence_author_t0_validation_failed
evidence_author_t0_waiver_record_missing
evidence_author_t0_window_chain_missing
evidence_author_t0_window_environment_missing
```

The missing-artifact mapping is the local table at
`joulewise/arm_readiness_evidence_t0.py:148-164`; the generic underivable
generator is at `:301-306`. The command below measures every mapping key and
value. No production check compares every author-module spelling to that
mapping; the author namespace therefore has no exact produced-versus-registered
set check.

```text
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'import joulewise.arm_readiness_evidence_t0 as t; m=dict(t._RUNBOOK_ARTIFACT_REASON_CODES); print("mapping_entry_count",len(m)); print("mapping_distinct_value_count",len(set(m.values()))); [print(k,"->",m[k]) for k in sorted(m)]'
mapping_entry_count 15
mapping_distinct_value_count 15
arm_context -> evidence_author_t0_arm_context_missing
clock_attestation -> evidence_author_t0_clock_attestation_missing
clock_disable_capture -> evidence_author_t0_clock_disable_missing
clock_prior_state_capture -> evidence_author_t0_clock_prior_state_missing
identity_epoch -> evidence_author_t0_identity_epoch_missing
launch_manifest -> evidence_author_t0_launch_manifest_missing
ledger_readiness_capture -> evidence_author_t0_ledger_readiness_missing
ledger_reservation_capture -> evidence_author_t0_ledger_reservation_missing
prewindow_check_capture -> evidence_author_t0_prewindow_check_missing
production_ledger -> evidence_author_t0_production_ledger_missing
quiet_mac_prep_capture -> evidence_author_t0_quiet_mac_prep_missing
t1_bindings -> evidence_author_t0_t1_bindings_missing
waiver_record -> evidence_author_t0_waiver_record_missing
window_chain -> evidence_author_t0_window_chain_missing
window_environment -> evidence_author_t0_window_environment_missing
```

The capture producer has a related, separately listed 12-code subset in
`scripts/capture_t0_step.py:83-100`. It matters to the ruled exact-Off and
noninteractive behaviors, so its affected entries are included in the
Vocabulary-B delta below, but it is not part of the module's measured count
of 44.

```text
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'from scripts.capture_t0_step import CAPTURE_REASON_CODES; print("capture_registered_count",len(CAPTURE_REASON_CODES)); [print(code) for code in sorted(CAPTURE_REASON_CODES)]'
capture_registered_count 12
evidence_author_t0_capture_boot_probe_failed
evidence_author_t0_capture_clock_observation_invalid
evidence_author_t0_capture_command_failed
evidence_author_t0_capture_environment_invalid
evidence_author_t0_capture_internal_error
evidence_author_t0_capture_io_error
evidence_author_t0_capture_output_collision
evidence_author_t0_capture_plan_invalid
evidence_author_t0_capture_result_invalid
evidence_author_t0_capture_sequence_invalid
evidence_author_t0_capture_terminal_review_missing
evidence_author_t0_capture_usage_invalid
```

That capture set has an exact-count-and-membership test at
`tests/test_capture_t0_step.py:624-631` and D-078 lists the same twelve
spellings at `docs/decision_log.md:9571-9588`. The test proves registration
membership; it does not require every retained spelling to keep an emission
site.

The following registry/gate search produced no match:

```text
$ rg -n 'evidence_author_t0_' configs/arm_readiness/d117_row_registry_v1.json configs/arm_readiness/d117_row_registry_v2.json joulewise/arm_readiness.py joulewise/arm_readiness_evidence.py tests/test_arm_readiness_integration.py
(no output; rg exit 1)
```

Therefore Vocabulary B has no R1 registry entry and is not scanned by
`REASON_CODE_COVERAGE`. The all-member missing-artifact test at
`tests/test_arm_readiness_evidence_t0.py:1574-1626` covers the mapping table,
and the named-refusal matrix at `:1278-1322` samples row kinds, but neither
compares all 44 author-module spellings to a registry. This fact creates no
new-code problem here because §3.2 adds zero spellings.

## 2. The ruled implementation surface

**Governed** means fixed by the cited policy and required to match its exact
command, roster, order, or numeric limit. The **capture script** is
`scripts/capture_t0_step.py`, which executes and records governed T-0 steps. A
result is **parseable** when the fixed parser accepts its exact output shape.
**Read skew** is the elapsed RAW counter time between the two RAW reads that
bracket one REALTIME read.
The **arm-side predicate** is `_predicate_passes` in
`joulewise/arm_readiness.py:5902-5975`; it rechecks receipt facts instead of
trusting stored booleans. The **rehearsal harness** is the still-to-be-built
mechanical evaluator for the ruled ten-gate supervised rehearsal.

A **RAW anchor** is `CLOCK_REALTIME - CLOCK_MONOTONIC_RAW`: wall time minus a
sleep-inclusive hardware counter. A changed anchor shows that wall time moved
relative to that counter. An **agreement interval** is the common intersection
of every successful parseable SNTP leg's `[offset - uncertainty, offset +
uncertainty]` interval. The **validity origin** is the monotonic timestamp from
which the receipt's six-hour deadline is calculated. These definitions are
the physical quantities the refusals below check.

The ARM-side source branch and the author's producer route are different
surfaces. The ruling preserves the ARM predicate's `OPERATOR_ATTESTATION`
branch and adds a `PROBE` branch (`MAGISTRATE-RULING-T0-UNATTENDED.md:35-40`).
The adopted seat implements that preservation in `_predicate_passes`
(`seat-opus-design.md:272-300`) while separately deleting the author's operator
inputs and capture prompts (`seat-opus-design.md:304-340`). “Historical and
attended receipts authenticate unchanged” therefore describes ARM consumption;
it does not require the new author to reproduce an operator receipt.

The rehearsal labels are defined here before use. `G1` is noninteractive
execution; `G2` is the receipt/source census; `G3` is the local-input witness;
`G4` is clock-mechanics recomputation; `G5` is D-149 C1–C5 evaluation; `G6` is
rehearsal separation; `G7` is production rejection; `G8` is zero-agent
capture; `G9` is the full lifecycle; and `G10` is the falsifier-control row.
These are local labels for the ten rows at `debate-sol-critique.md:63-74`,
adopted by the ruling at `MAGISTRATE-RULING-T0-UNATTENDED.md:91-105`.
**Custody overlaps production** when a rehearsal artifact is placed in a root,
ledger, or namespace that a production consumer may accept; G6 forbids that.
**Launch/exit lineage** is the recorded process ancestry and start/exit timing
used by G8 to prove the agent exited before capture.

The ruled refusal-bearing behaviors are:

| ID | Refusing component | Physical condition that must refuse |
|---|---|---|
| RF-01 | Author | R0 does not prove the fixed versioned `time.apple.com`, `pool.ntp.org`, `time.nist.gov` roster under `sample_policy_id`; does not record exactly one governed `/usr/bin/sntp -t 2` invocation per hostname; substitutes, falls back, or adds an attempt; omits a successful parseable leg from the intersection; performs best-result selection; or omits that leg's resolved peer address or raw line. |
| RF-02 | Author | Fewer than two R0 legs exit zero with a parseable line; spawn failure, nonzero exit, timeout, or malformed output counts that leg as unsuccessful and no extra attempt is launched. |
| RF-03 | Author | The agreement intervals of all successful parseable R0 legs have an empty common intersection. |
| RF-04 | Author | R0's `abs(intersection midpoint) + intersection halfwidth` exceeds 0.5 seconds. |
| RF-05 | Author | R0's RAW→REALTIME→RAW anchor read skew exceeds 1,000,000 ns. |
| RF-06 | Author | Fewer than two fixed-roster R1 legs exit zero with a parseable line; one failed leg is tolerated but never retried or replaced. |
| RF-07 | Author | The agreement intervals of all successful parseable R1 legs have an empty common intersection. |
| RF-08 | Author | R1's `abs(intersection midpoint) + intersection halfwidth` exceeds 0.5 seconds. |
| RF-36 | Author | R1 does not prove the same fixed versioned `sample_policy_id` roster as R0; does not record exactly one governed `/usr/bin/sntp -t 2` invocation per hostname; substitutes, falls back, or adds an attempt; omits a successful parseable leg from the intersection; performs best-result selection; or omits that leg's resolved peer address or raw line. |
| RF-09 | Author and arm-side predicate | `author_anchor_raw_ns - R0_anchor_raw_ns` is below 600,000,000,000 ns, so the falsifier lacks the ruled minimum observation span. |
| RF-10 | Author and arm-side predicate | That same RAW-anchor span exceeds 3,600,000,000,000 ns. |
| RF-11 | Author | The absolute R0-to-author RAW-anchor delta exceeds 5,000,000 ns; this is separate from, and never added to, the 0.5-second SNTP bound. |
| RF-12 | Author | The author's RAW→REALTIME→RAW read skew exceeds 1,000,000 ns. |
| RF-13 | Capture script and author | The boot-session UUID changes during a capture, differs between R0 and authoring, or changes before publication. |
| RF-14 | Author and capture script | R0 is not completed before the first clock-disable action, the first disable is not completed before R1 or the author-side RAW→REALTIME→RAW anchor sample, or R1 is not completed before the author's fresh maintenance and process censuses. |
| RF-15 | Author | `clock-reference.json` is absent, non-regular, non-canonical, wrong-schema, or otherwise not a usable governed command capture. |
| RF-16 | Author and arm-side predicate | The R1 batch's last completion minus first start exceeds 30,000,000,000 ns. |
| RF-17 | Author and arm-side predicate | R1 completion to the recorded validity origin exceeds 5,000,000,000 ns. |
| RF-18 | Author and arm-side predicate | `valid_until_monotonic_ns` is not exactly `validity_origin_monotonic_ns + 21_600_000_000_000`. |
| RF-37 | Author and arm-side predicate | Any endpoint used by RF-09/RF-10/RF-16/RF-17/RF-18 is not an integer, is boolean-typed, or reverses the ordered endpoints. |
| RF-19 | Capture script | The first active `sudo -n systemsetup -setusingnetworktime off` invocation exits nonzero. |
| RF-20 | Capture script | The first active Off invocation exits zero but stdout is not exactly the Ed-bench-verified `setUsingNetworkTime: Off` line. |
| RF-21 | Author | The second, fresh active Off invocation exits nonzero. |
| RF-22 | Author | The second, fresh active Off invocation exits zero but stdout is not exactly the Ed-bench-verified `setUsingNetworkTime: Off` line. |
| RF-23 | Arm-side predicate | A historical `OPERATOR_ATTESTATION` fact lacks `prior_systemsetup_state_captured: true`; preserving this refusal preserves the attended branch's strictness. |
| RF-24 | Author and arm-side predicate | A `PROBE` fact lacks the ruled reference, anchor, numeric-timestamp, or deadline inputs, carries a false gate value, or fails any recomputed RF-09/RF-10/RF-16/RF-17/RF-18/RF-37 relation. |
| RF-25 | Arm-side predicate | A fresh arm-side anchor sample differs from the published T-0 anchor by more than 5,000,000 ns. |
| RF-26 | Rehearsal gate G1, noninteractive execution | The top-level T-0 process or any governed subprocess does not complete with stdin bound to `/dev/null`; any surviving prompt, EOF refusal, or hang fails the rehearsal. |
| RF-27 | Rehearsal gate G2, receipt/source census | Any T-0 receipt has an `OPERATOR_ATTESTATION` fact, any capture uses `operator-interactive`, or the clock fact is not `PROBE`. |
| RF-28 | Rehearsal gate G3, local-input witness | `IOHIDSystem/HIDIdleTime` is absent, ambiguous, unparsable, or less than the measured T-0 span. |
| RF-29 | Rehearsal gate G4, clock mechanics | The recorded R0/R1 quorum, intersection, 0.5-second bounds, exact-Off results, RAW endpoints, 600–3600-second span, or 5-ms delta does not mechanically recompute to PASS. |
| RF-30 | Rehearsal gate G5, D-149 evaluation | Any one of ordinary D-149 conditions C1–C5 lacks its evidence or is not mechanically green, so no GO may issue. |
| RF-31 | Rehearsal gate G6, rehearsal separation | The receipt class is not `T0_UNATTENDED_SUPERVISED_REHEARSAL`, `claim_eligible` is not false, the window ID lacks the rehearsal prefix, or custody overlaps production. |
| RF-32 | Production consumer and rehearsal gate G7 | A production consumer is presented with an otherwise valid rehearsal receipt and does not mechanically refuse it specifically for lacking production authority. |
| RF-33 | Rehearsal gate G8, zero-agent capture | The agent has not exited before capture, or process and launch/exit lineage show any agent process during capture. |
| RF-34 | Rehearsal gate G9, full lifecycle | Launch, capability consumption, capture, backups, close-out, or restore is incomplete, or any human intervention occurs even if it would have made the run succeed. |
| RF-35 | Rehearsal gate G10, falsifier controls | The arm predicate does not refuse at 5 ms + 1 ns, does not pass at 5 ms - 1 ns, the adjacent out-of-T-0 privileged positive control fails to move the RAW anchor visibly, or either added code-observation case in §5 is absent. |

RF-36 and RF-37 extend the table without renumbering existing rows, so the
outstanding G7 mapping remains RF-32. RF-36 makes the complete R1 policy
symmetrical with RF-01, as required by the fixed roster, one-attempt,
all-successful-leg, and evidence-bearing-peer ruling
(`MAGISTRATE-RULING-T0-UNATTENDED.md:47-57`).

The issuance-time relations are ordered, integer-only numeric relations:

```text
0 <= R1_last_completion_ns - R1_first_start_ns <= 30_000_000_000
0 <= validity_origin_ns - R1_last_completion_ns <= 5_000_000_000
600_000_000_000 <= author_anchor_raw_ns - R0_anchor_raw_ns <= 3_600_000_000_000
valid_until_monotonic_ns == validity_origin_ns + 21_600_000_000_000
```

`_predicate_passes` must recompute these relations numerically. They are never
stored booleans, and no unstated capture-order check may substitute for either
non-negative lower bound. This is the ruling's issuance-time requirement
(`MAGISTRATE-RULING-T0-UNATTENDED.md:73-83`) and the adopted numeric shape
(`debate-sol-critique.md:110-119`). Section 6.3 records the unresolved execution
conflict in the second relation and the lead-ordered interim relation; it does
not alter the ruled target. A green G-row proves only its stated positive
outcome unless it explicitly injects and records a refusal; §5 does not count a
green-only outcome as a code observation.

## 3. The enumerated delta

### 3.1 Vocabulary A — ARM-readiness delta

This portion adds no `readiness_*` spelling. `_evaluate_rows` calls the
predicate and, on a false clock row, obtains its refusal from
`_missing_row_code` (`joulewise/arm_readiness.py:6031-6064`). That mapping
returns the already registered `readiness_clock_preflight_refused` literal for
every `clock.*` row (`arm_readiness.py:5978-5986`; family registration at
`:168-181`). Those mechanics prove that the new numeric and arm-anchor causes
do not require a new readiness code.

| code | disposition | RF IDs served | family frozenset + registry entry | exact implementation/coverage places | exercise |
|---|---|---|---|---|---|
| `readiness_clock_preflight_refused` | RE-TARGETED | RF-09, RF-10, RF-16–RF-18, RF-23–RF-25, RF-37 | Existing `POLICY_REASON_CODES` at `joulewise/arm_readiness.py:168-181`; type supplied by `REASON_TYPE_BY_CODE` at `:235`; no R1 `refusal_vocabulary` entry is needed because this is not an R1 lifecycle-role error. | Extend `_predicate_passes` at `joulewise/arm_readiness.py:5902-5975`; keep the literal mapping at `:5978-5986`; keep the family, union, type map, deriver `dynamic` set (`arm_readiness_evidence.py:2038-2049`), and mirror test (`test_arm_readiness_integration.py:583-639`) unchanged. Add numeric-type/order, operator-branch, PROBE-minimal-content, and arm-anchor boundary tests. | G10 must use the real arm evaluator and record this code for its arm-side >5 ms case; G4's successful arithmetic is not a code observation. |
| **NOT THIS ROW'S — production rejection code for RF-32** | **RULED to `UNATTENDED-LAUNCH-01` (§6.2); not an addition here** | RF-32 | Recommendation: reuse existing `readiness_usage_invalid` in `STRUCTURE_REASON_CODES` (`arm_readiness.py:123-134`) if the production consumer is an ARM entry point. If the magistrate instead orders a new spelling, it must use the ruled R1 family/role/registry procedure in §4.5. | The ruling gives fields but HEAD has no `T0_UNATTENDED_SUPERVISED_REHEARSAL` parser or production-rejection call site; `docs/process/d149-go-receipt-template.md:1-66` is a prose template and explicitly says a mechanical evaluator merely “MAY” be built. No code or test location can be named honestly until the consumer is ruled. | G7, after the consumer and code are ruled. |

Known Vocabulary-A count: **0 ADDED, 0 RETIRED, 0 REUSED-UNCHANGED, 1
RE-TARGETED**. RF-32 is unresolved and excluded from the count.

#### Arm-only anchor plumbing

At HEAD `_predicate_passes` is pure receipt logic and has no clock parameter
(`arm_readiness.py:5902-5975`). The implementation must make RF-25 reachable as
follows:

1. At ARM evaluation, take one governed RAW→REALTIME→RAW sample and refuse the
   clock row when read skew exceeds 1,000,000 ns. ARM evaluation currently
   fixes its evaluation time and boot before discovery at
   `arm_readiness.py:7588-7606` and evaluates rows at `:7683-7691`; that is the
   insertion surface.
2. Deliver the sample through an injectable keyword parameter threaded from
   ARM evaluation through `_evaluate_rows` into `_predicate_passes`. Tests must
   supply deterministic samples. `_predicate_passes` must never perform an
   unconditional clock read.
3. Apply the sample only when the predicate is
   `clock.correct_and_prior_state.v1` and the matching fact's source is
   `PROBE`. The `OPERATOR_ATTESTATION` branch remains receipt-only.
4. Recompute the published T-0 anchor as
   `anchor_realtime_ns - anchor_monotonic_raw_ns`, recompute the injected ARM
   anchor from its bracketed sample, and compare their absolute difference.
5. Return false above 5,000,000 ns or on an invalid/missing required ARM sample.
   `_evaluate_rows` then emits the existing code through
   `arm_readiness.py:6039-6064` and `:5978-5986`.

The complete production caller census was re-derived against HEAD with:

```text
$ git grep -n '_predicate_passes(' HEAD -- 'joulewise/*.py'
HEAD:joulewise/arm_readiness.py:5902:def _predicate_passes(
HEAD:joulewise/arm_readiness.py:6039:            if _predicate_passes(
HEAD:joulewise/arm_readiness.py:8427:            if _predicate_passes(
HEAD:joulewise/arm_readiness_evidence.py:2819:                _readiness._predicate_passes(item, row["predicate_id"])
HEAD:joulewise/arm_readiness_evidence.py:2961:                _readiness._predicate_passes(item, row["predicate_id"])
HEAD:joulewise/arm_readiness_evidence.py:3128:                _readiness._predicate_passes(item, row["predicate_id"])
HEAD:joulewise/arm_readiness_evidence_t0.py:1890:            or not _readiness._predicate_passes(
HEAD:joulewise/arm_readiness_evidence_t0.py:2010:        if not _readiness._predicate_passes(
$ git grep -n '_evaluate_rows(' HEAD -- 'joulewise/arm_readiness.py'
HEAD:joulewise/arm_readiness.py:5998:def _evaluate_rows(
HEAD:joulewise/arm_readiness.py:6652:    expected_rows, expected_refusals = _evaluate_rows(
HEAD:joulewise/arm_readiness.py:6966:    rows, refusals = _evaluate_rows(
HEAD:joulewise/arm_readiness.py:7683:    rows, row_refusals = _evaluate_rows(
HEAD:joulewise/arm_readiness.py:7946:    rows, row_refusals = _evaluate_rows(
```

| Direct call | What the caller is doing | Can it select `clock.correct_and_prior_state.v1` today? | Live-anchor parameter state |
|---|---|---|---|
| `arm_readiness.py:6039` | `_evaluate_rows` checks each matching evidence receipt against the row definition being evaluated. | Yes for ARM-phase definitions; no for freeze-phase definitions. | Forward the state chosen by the entry context in the next table; this layer must not invent a sample. |
| `arm_readiness.py:8427` | Launch-consumption binding authenticates exactly one `t0.single_launch_capability.v1` receipt. | No; the predicate ID is hard-coded to the launch-capability predicate. | Omit/default to receipt-only static evaluation. |
| `arm_readiness_evidence.py:2819` | The generic legacy author re-authenticates an existing evidence namespace against its freeze rows. | No; `_required_generic_rows` selects `FREEZE_AND_ARM` rows, while the clock row is `ARM_ONLY` (`arm_readiness_evidence.py:2307-2329`; registry v1 `:129-136`). | Omit/default to receipt-only static evaluation. |
| `arm_readiness_evidence.py:2961` | The generic R1 author re-authenticates existing lifecycle-governed evidence against the same freeze rows. | No, for the same phase-selection reason. | Omit/default to receipt-only static evaluation. |
| `arm_readiness_evidence.py:3128` | The generic author self-checks newly assembled evidence before publication. | No, for the same phase-selection reason. | Omit/default to receipt-only static evaluation. |
| `arm_readiness_evidence_t0.py:1890` | The T-0 author re-derives and semantically re-authenticates an existing fifteen-row namespace. | Yes; the preserved ARM_ONLY census contains the clock row first (`arm_readiness_evidence_t0.py:68-84,731-756`). | Omit/default to receipt-only static evaluation; re-authentication must not sample a later instant. |
| `arm_readiness_evidence_t0.py:2010` | The T-0 author self-checks each newly assembled receipt before publication. | Yes; it iterates the same fifteen ARM_ONLY definitions. | Omit/default to receipt-only static evaluation; ARM evaluation has not occurred. |

Every `_evaluate_rows` entry context reaches the direct call at
`arm_readiness.py:6039`:

| `_evaluate_rows` entry | What the caller is doing | Can it select `clock.correct_and_prior_state.v1` today? | Live-anchor parameter state |
|---|---|---|---|
| Freeze replay (`arm_readiness.py:6652`) | It proves recorded freeze conclusions still derive from authenticated evidence bytes. | No; `_profile_rows(..., phase="freeze")` keeps only `FREEZE_AND_ARM` rows (`arm_readiness.py:5054-5066`). | Omit/default to receipt-only static evaluation. |
| Freeze-receipt issuance (`arm_readiness.py:6966`) | It derives the rows and refusals written into a new freeze receipt. | No; it uses the same freeze-only profile selection. | Omit/default to receipt-only static evaluation. |
| Original ARM evaluation (`arm_readiness.py:7683`) | It evaluates the live ARM-phase evidence and creates the original GO/NO-GO conclusion. | Yes. | Supply the governed live anchor sample and enter live-required mode; a missing or invalid sample for a PROBE clock fact fails closed. |
| ARM-receipt verification (`arm_readiness.py:7946`) | It replays row semantics from authenticated bytes and compares them with the already-recorded ARM conclusion. | Yes. | Omit/default to receipt-only static evaluation; a second sample would adjudicate a later instant and could change recorded history. |

The new parameter therefore defaults explicitly to receipt-only (static)
evaluation. Only the original ARM evaluation supplies a live sample, and only
the `PROBE` branch of `clock.correct_and_prior_state.v1` consumes it; the
historical `OPERATOR_ATTESTATION` branch remains receipt-only. The original ARM
path must not rely on the default: a PROBE fact reaching original ARM
evaluation without a valid live sample returns false. `_predicate_passes`
never reads a clock itself.

A caller that cannot select the clock predicate today still matters because it
shares the function signature: changing the parameter default reaches that
caller too. Receipt-only is consequently the safe default for every direct and
transitive caller except the explicitly live original ARM path.

### 3.2 Vocabulary B — T-0 author and capture-producer delta

The following table applies the adopted Opus convention from
`seat-opus-design.md:348-354`: numbered refusal rules share the existing
`evidence_author_t0_clock_attestation_underivable` spelling. The missing
`clock-reference` capture reuses
`evidence_author_t0_clock_attestation_missing`, so this table adds no spelling.

| code | disposition | RF IDs served | family frozenset + registry entry | exact implementation/coverage places | exercise |
|---|---|---|---|---|---|
| `evidence_author_t0_clock_attestation_missing` | RE-TARGETED | RF-15 | Replace mapping keys `clock_attestation` and `clock_prior_state_capture` with `clock_reference_capture`, whose value is this existing spelling. No R1 entry changes because no spelling is added. | Update `_CAPTURE_FILES` and `_RUNBOOK_ARTIFACT_REASON_CODES` at `joulewise/arm_readiness_evidence_t0.py:135-164`; the forced derived lookup key is `f"{step_id.replace('-','_')}_capture"` at `:469-471`. Update the exact map/path test at `tests/test_arm_readiness_evidence_t0.py:1574-1626` from 15 distinct entries to 14 distinct entries. | Unit-level only: removing or corrupting `clock-reference.json` prevents the complete rehearsal, and no ruled G-row deletes that required artifact. |
| `evidence_author_t0_clock_prior_state_missing` | RETIRED | Predecessor of RF-15; serves no ruled behavior after the `clock-prior-state` step is removed. | Stop listing mapping key `clock_prior_state_capture` and this value at `arm_readiness_evidence_t0.py:151`; no registry entry exists. | Remove the mapping at `:151`; remove the expected entry/path at `tests/test_arm_readiness_evidence_t0.py:1578,1606`; replace all step-order fixtures which expect `clock-prior-state`. No readiness gate/mirror change. | Not rehearsal-observable after retirement; a source/AST absence assertion proves no new refusal can emit it. Historical refusal transcripts remain immutable. |
| `evidence_author_t0_clock_attestation_underivable` | RE-TARGETED | RF-01–RF-14, RF-16–RF-18, RF-36, RF-37 when derivation identifies the violation before receipt assembly | Generated by `_underivable("CLOCK_ATTESTATION", ...)` at `arm_readiness_evidence_t0.py:301-306`; no frozenset or registry entry. | Rewrite `_derive_clock_attestation` at `:855-888` and its parser/helper surface at `:455-554`; add one defect-shaped regression for every R0/R1 policy, numeric, ordering, type, and boundary rule. Each regression asserts kind `CLOCK_ATTESTATION`, this code, a distinct detail, and no published namespace. | G10 must add one real-author >5 ms case that records this code and no published namespace. Other limbs remain unit-level because G4 is a successful clock-mechanics gate. |
| `evidence_author_t0_clock_probe_underivable` | RE-TARGETED | RF-21, RF-22 | Generated by `_underivable("CLOCK_PROBE", ...)` at `arm_readiness_evidence_t0.py:301-306`; no frozenset or registry entry. | Strengthen `_derive_clock_probe` at `:891-916` from exit-only to exit plus exact-line checking; add `test_fresh_clock_disable_nonzero_refuses_underivable` and `test_fresh_clock_disable_wrong_exact_stdout_refuses_underivable`. No readiness gate/mirror change. | Unit-level only, not rehearsal-observable: G4 proves the exact line passed; it does not inject a false exit-zero stdout. |
| `evidence_author_t0_predicate_refused` | RE-TARGETED | RF-16–RF-18, RF-24, RF-37 | Inline author self-check at `arm_readiness_evidence_t0.py:2010-2015`; no frozenset or registry entry. | Make `_predicate_passes` recompute the ordered integer relations in `arm_readiness.py:5902-5975`; carry every numeric endpoint in the derived value/source; add per-relation, reversed-endpoint, boolean, and PROBE-minimal-content regressions. | Unit-level only. RF-25 is deliberately absent from the author self-check; G10's ARM-side case emits the readiness code. |
| `evidence_author_t0_existing_stale` | RE-TARGETED | RF-16–RF-18, RF-24, RF-37 during re-authentication of an already-published PROBE receipt | Inline at `arm_readiness_evidence_t0.py:1894,1898,1902`; no frozenset or registry entry. | The existing-receipt predicate call at `:1889-1894` applies recorded numeric relations but receives no ARM anchor sample; add exact-deadline/type/order mutation coverage. | Unit-level only; the successful one-shot rehearsal does not deliberately re-authenticate a stale namespace. |
| `evidence_author_t0_clock_disable_missing` | REUSED-UNCHANGED | RF-19, RF-20 when the governed capture itself is unavailable | Existing local mapping at `arm_readiness_evidence_t0.py:152`; no registry entry. | Keep the mapping and all-member artifact test at `tests/test_arm_readiness_evidence_t0.py:1579,1607`; no readiness-gate or mirror change. | Unit-level only; G4 requires the artifact to exist. |
| `evidence_author_t0_capture_command_failed` | REUSED-UNCHANGED | RF-19 | Existing `CAPTURE_REASON_CODES` member at `scripts/capture_t0_step.py:94`, registered historically at `docs/decision_log.md:9584`; not an R1 entry. | Keep the nonzero command refusal at `scripts/capture_t0_step.py:946-950`; add a clock-disable-specific assertion if the existing generic test does not name the step. No readiness gate/mirror change. | Unit-level only; G4's successful command is not negative evidence. |
| `evidence_author_t0_capture_result_invalid` | RE-TARGETED | RF-20 | Existing `CAPTURE_REASON_CODES` member at `scripts/capture_t0_step.py:95`, D-078 entry at `docs/decision_log.md:9585`; not an R1 entry. | Add the `clock-disable` exact stdout branch to `_validate_result` at `scripts/capture_t0_step.py:796-887`; add `test_clock_disable_zero_exit_wrong_exact_stdout_refuses_result_invalid`. No readiness gate/mirror change. | Unit-level only; G4 proves the exact output passed. |
| `evidence_author_t0_capture_sequence_invalid` | RE-TARGETED | RF-14 | Existing `CAPTURE_REASON_CODES` member at `scripts/capture_t0_step.py:92`, D-078 entry at `docs/decision_log.md:9582`; not an R1 entry. | Replace `clock-prior-state` with `clock-reference` in `STEP_ORDER`/filenames and predecessor checks; update `tests/test_capture_t0_step.py:451-464` and add `test_clock_reference_must_precede_clock_disable`. No readiness gate/mirror change. | Unit-level only; G1 demonstrates a passing order, not this refusal. |
| `evidence_author_t0_capture_boot_probe_failed` | REUSED-UNCHANGED | RF-13 | Existing `CAPTURE_REASON_CODES` member at `scripts/capture_t0_step.py:89`, D-078 entry at `docs/decision_log.md:9579`; not an R1 entry. | Preserve pre/post command boot checks at `scripts/capture_t0_step.py:913-931`; extend the same fixture to the renamed reference step. No readiness gate/mirror change. | Unit-level only; a successful full rehearsal stays on one boot. |
| `evidence_author_t0_capture_clock_observation_invalid` | REUSED-UNCHANGED | No new RF; its prompt emission is removed | Keep the spelling in the exact D-078 twelve-code `CAPTURE_REASON_CODES` set at `scripts/capture_t0_step.py:83-100` and in the decision record at `docs/decision_log.md:9571-9588`. | Delete the old `_clock_attestation` prompt emission sites at `scripts/capture_t0_step.py:545-608`; leave the set and its exact-count test at `tests/test_capture_t0_step.py:624-631` unchanged. | No new rehearsal emission is required. A registered-but-unemitted spelling is permitted; changing D-078's registered vocabulary requires a magistrate decision. |

Vocabulary-B counts, including the separately enumerated capture subset because
the ruled behaviors change it:

| scope | ADDED | RETIRED | REUSED-UNCHANGED | RE-TARGETED |
|---|---:|---:|---:|---:|
| Author module | 0 | 1 | 1 | 5 |
| Capture subset | 0 | 0 | 3 | 2 |
| **Vocabulary B total** | **0** | **1** | **4** | **7** |

The author-module census becomes 43 because only
`evidence_author_t0_clock_prior_state_missing` disappears: `44 - 1 = 43`.
The capture registered set remains 12 because its spelling remains while its
prompt emission sites disappear. The missing-artifact mapping becomes 14
entries because two keys disappear and one is added: `15 - 2 + 1 = 14`.
Those post-change totals are command-produced predictions, not HEAD
measurements; the command below prints both bases and transforms.

```text
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'import ast,inspect,re; from pathlib import Path; from collections import Counter; import joulewise.arm_readiness as a; import joulewise.arm_readiness_evidence as e; import joulewise.arm_readiness_evidence_t0 as t; from scripts.capture_t0_step import CAPTURE_REASON_CODES; doc=Path("docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md").read_text(encoding="utf-8"); cats=("ADDED","RETIRED","REUSED-UNCHANGED","RE-TARGETED"); asec=doc.split("### 3.1",1)[1].split("### 3.2",1)[0]; bsec=doc.split("### 3.2",1)[1].split("### 3.3",1)[0]; ar=Counter(re.findall(r"^\| `[^`]+` \| (ADDED|RETIRED|REUSED-UNCHANGED|RE-TARGETED) \|",asec,re.M)); brows=re.findall(r"^\| `(evidence_author_t0_[^`]+)` \| (ADDED|RETIRED|REUSED-UNCHANGED|RE-TARGETED) \|",bsec,re.M); br={scope:Counter(d for code,d in brows if ("Capture subset" if code.startswith("evidence_author_t0_capture_") else "Author module")==scope) for scope in ("Author module","Capture subset")}; bt=Counter(d for _,d in brows); src=inspect.getsource(a).split("class ArmReadinessError",1)[1]; produced=set(re.findall(r"\"(readiness_[a-z0-9_]+)\"",src)); tree=ast.parse(inspect.getsource(e._derive_reason_code_coverage)); dynamic=ast.literal_eval(next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=="dynamic" for x in n.targets))); registered=set(a.READINESS_REASON_CODES); ptree=ast.parse(Path("joulewise/arm_readiness_evidence_t0.py").read_text(encoding="utf-8")); literals={n.value for n in ast.walk(ptree) if isinstance(n,ast.Constant) and isinstance(n.value,str) and re.fullmatch(r"evidence_author_t0_[a-z0-9_]+",n.value)}; generated={f"evidence_author_t0_{kind.lower()}_underivable" for kind in set(t._ROW_KIND.values())|{"AUTHORING_SET"}}; author=literals|generated; mapping=dict(t._RUNBOOK_ARTIFACT_REASON_CODES); projected_author=author-{"evidence_author_t0_clock_prior_state_missing"}; projected_mapping=(set(mapping)-{"clock_attestation","clock_prior_state_capture"})|{"clock_reference_capture"}; projected_mapping_values=set(mapping.values())-{"evidence_author_t0_clock_prior_state_missing"}; print("vocab_a_dispositions",*(f"{c}={ar[c]}" for c in cats)); [print(scope.replace(" ","_").lower()+"_dispositions",*(f"{c}={br[scope][c]}" for c in cats)) for scope in br]; print("vocab_b_dispositions",*(f"{c}={bt[c]}" for c in cats)); print("baseline",f"readiness_registered={len(registered)}",f"readiness_produced={len(produced)}",f"readiness_dynamic={len(dynamic)}",f"author={len(author)}",f"capture={len(CAPTURE_REASON_CODES)}",f"mapping={len(mapping)}"); print("predicted",f"readiness_registered={len(registered)}",f"readiness_produced={len(produced)}",f"readiness_dynamic={len(dynamic)}",f"author={len(projected_author)}",f"capture={len(CAPTURE_REASON_CODES)}",f"mapping={len(projected_mapping)}"); print("predicted_mapping_distinct_values",len(projected_mapping_values)); print("nothing_new",ar["ADDED"]==0 and bt["ADDED"]==0)'
vocab_a_dispositions ADDED=0 RETIRED=0 REUSED-UNCHANGED=0 RE-TARGETED=1
author_module_dispositions ADDED=0 RETIRED=1 REUSED-UNCHANGED=1 RE-TARGETED=5
capture_subset_dispositions ADDED=0 RETIRED=0 REUSED-UNCHANGED=3 RE-TARGETED=2
vocab_b_dispositions ADDED=0 RETIRED=1 REUSED-UNCHANGED=4 RE-TARGETED=7
baseline readiness_registered=55 readiness_produced=45 readiness_dynamic=10 author=44 capture=12 mapping=15
predicted readiness_registered=55 readiness_produced=45 readiness_dynamic=10 author=43 capture=12 mapping=14
predicted_mapping_distinct_values 14
nothing_new True
```

“Nothing ships unregistered” is satisfied without a registration edit because
the disposition census proves zero added spellings: Vocabulary A remains the
same registered 55-code set, the author census only shrinks from 44 to 43, and
the D-078 capture set remains its registered twelve.

### 3.3 Registration and historical-record consequences

No numbered clock rule gets a per-rule code. RF-01–RF-14, RF-16–RF-18,
RF-36, and RF-37 use the existing
`evidence_author_t0_clock_attestation_underivable` spelling when derivation
identifies the failure; RF-15 uses the existing
`evidence_author_t0_clock_attestation_missing` spelling. That applies the
adopted no-proliferation convention at `seat-opus-design.md:348-354` without
creating a registration question.

The current all-member mapping test requires exactly 15 keys and 15 distinct
values (`tests/test_arm_readiness_evidence_t0.py:1574-1593`). It must change to
14 keys and 14 distinct values. This is not a mechanical obstacle to reuse:
`clock_attestation` is removed before its value is assigned to
`clock_reference_capture`, so the post-change mapping contains no duplicate
value. The producing command in §3.2 prints
`predicted_mapping_distinct_values 14`.

#### Existing operator namespace under the new author

The new author's sole `clock.correct_and_prior_state` deriver returns `PROBE`.
If it is asked to re-authenticate an existing namespace whose clock receipt is
`OPERATOR_ATTESTATION`, and the new derivation inputs are otherwise available,
the freshly derived source cannot equal the old source at
`arm_readiness_evidence_t0.py:1886`; the reconstructed receipt also cannot
equal the old receipt at `:1889`. The combined condition raises
`evidence_author_t0_existing_stale` at `:1894`. The result is **REFUSE**, not
PASS. If the required new `clock-reference` capture is absent, derivation
refuses earlier with the reused
`evidence_author_t0_clock_attestation_missing`; that does not turn the old
namespace into a PASS.

No post-change production author can create the problematic same-head
namespace: it emits only `PROBE`, while re-authentication requires the receipt
and source to match the current HEAD, tree, pack, and boot at
`arm_readiness_evidence_t0.py:1875-1892`. A pre-change operator namespace may
remain on disk, but its capture must also be no more than
`_MAX_T0_SEQUENCE_AGE_NS` (3,600,000,000,000 ns) old and on the current boot
(`arm_readiness_evidence_t0.py:52,493-501`); changing to the post-change HEAD
then breaks the exact identity comparison. ARM consumption is different: the
preserved `OPERATOR_ATTESTATION` predicate branch continues to authenticate a
still-valid historical or attended receipt. This asymmetry is the ruled design
consequence described by `MAGISTRATE-RULING-T0-UNATTENDED.md:35-45` and the
separate author deletions at `seat-opus-design.md:304-340`, not an unruled
deviation. It creates no additional `NEEDS-RULING` item.

A successful T-0 evidence receipt always has `status: PASS` and
`reason_codes: []` (`joulewise/arm_readiness_evidence_t0.py:1682-1706`).
Therefore historical PASS receipts do not carry the one retired Vocabulary-B
code. Historical REFUSE transcripts which already carry it remain immutable
diagnostics; they are never rewritten or translated. Preserving the
`OPERATOR_ATTESTATION` ARM branch means a historical attended PASS receipt
still authenticates against `prior_systemsetup_state_captured: true` (RF-23);
it does not preserve the deleted author prompts.

## 4. Gate impact analysis

The account includes the gate's execution mechanics, not only its set
arithmetic:

- `_derive_reason_code_coverage` passes the fully qualified focused test name
  to `_run_suite` at `joulewise/arm_readiness_evidence.py:1999-2008`.
  `_run_suite` requires the requested test module to appear in executed-module
  evidence and requires a passing result at `:746-787`; therefore the named
  test must execute successfully.
- The subprocess uses the target repository as `cwd`, resets its import root to
  that repository, and reports both identities
  (`arm_readiness_evidence.py:548-570,628-693`). It hashes every repository
  module actually executed at `:587-605`; `_run_suite` then requires each
  executed file to be byte-identical to the target HEAD through
  `_committed_artifact` at `:755-769`. `_committed_artifact` performs the
  readable-file and HEAD-byte comparison at `:262-275`.
- The deriver separately requires readable, HEAD-identical bytes for
  `joulewise/arm_readiness.py`, `joulewise/identity_pins.py`, and
  `tests/test_arm_readiness_integration.py` at
  `arm_readiness_evidence.py:2009-2017`.
- It decodes `arm_readiness.py` as strict UTF-8 and requires the
  `class ArmReadinessError` split point at
  `arm_readiness_evidence.py:2018-2023`. The current split point is
  `joulewise/arm_readiness.py:1023`.

These checks require the test to run from the intended repository, bind
imported project modules to committed bytes, and bind the three named primary
artifacts to HEAD. A green test from another checkout cannot satisfy the
evidence kind.

```text
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'import subprocess; from pathlib import Path; paths=("joulewise/arm_readiness.py","joulewise/identity_pins.py","tests/test_arm_readiness_integration.py"); print("repository",Path.cwd().resolve());
for path in paths:
 raw=Path(path).read_bytes(); head=subprocess.check_output(["git","show",f"HEAD:{path}"]); print(path,"readable",True,"byte_identical_to_HEAD",raw==head)
runtime=Path(paths[0]).read_bytes().decode("utf-8",errors="strict"); print("arm_readiness_utf8",True); print("arm_readiness_split_count",runtime.count("class ArmReadinessError")); print("arm_readiness_has_split_point",runtime.count("class ArmReadinessError")==1)'
repository /Users/edr/code/JouleWise-wt-s2-t0-unattended
joulewise/arm_readiness.py readable True byte_identical_to_HEAD True
joulewise/identity_pins.py readable True byte_identical_to_HEAD True
tests/test_arm_readiness_integration.py readable True byte_identical_to_HEAD True
arm_readiness_utf8 True
arm_readiness_split_count 1
arm_readiness_has_split_point True
```

### 4.1 Check 1 — every produced readiness literal is registered

The deriver extracts runtime literals at
`arm_readiness_evidence.py:2018-2025` and rejects
`produced - registered` at `:2026-2030`. The enumerated delta adds no readiness
literal and retains the already produced
`readiness_clock_preflight_refused` literal at
`arm_readiness.py:5985-5986`. Therefore the predicted post-change relation
remains `produced = 45`, `registered = 55`, and
`produced - registered = empty`.

Vocabulary-B additions and retirements do not enter this scan: the regex is
applied only to committed `joulewise/arm_readiness.py` bytes after the class
split, not to the author or capture script.

### 4.2 Check 2 — registered minus produced exactly equals `dynamic`

The equality is enforced at `arm_readiness_evidence.py:2031-2054`. Since the
known delta changes neither `READINESS_REASON_CODES` nor the readiness literal
set, `registered - produced` remains the exact ten-code `dynamic` set measured
in §1.1. The deriver's `dynamic` assignment must not change for the enumerated
delta.

### 4.3 Check 3 — every registered readiness code round-trips

The deriver calls `_receipt_refusal` and `_validate_refusal` for every sorted
registered code at `arm_readiness_evidence.py:2055-2058`. The receipt builder
rejects an unregistered code and obtains its type from `REASON_TYPE_BY_CODE`
at `arm_readiness.py:4869-4881`. Reusing the existing policy code keeps all 55
round-trips unchanged.

### 4.4 Mirror test

The mirror at `tests/test_arm_readiness_integration.py:583-639` repeats the
literal subset check (`:584-589`), round-trips every code (`:590-594`),
AST-reads the single `dynamic` assignment (`:595-610`), loads the R1 registry
role-to-code map (`:611-615`), builds a nonempty justification per dynamic
code (`:616-634`), and asserts exact set equality (`:635-639`). The enumerated
delta leaves all of those inputs unchanged, so no mirror edit is required.
The focused test must still run after implementation because a stray quoted
`readiness_*` detail string would change the literal scan even if it were not
an emission site.

Registry v1's `desk.reason_code_plumbing` row at
`d117_row_registry_v1.json:237-244` is archival row wiring and must not change;
its SHA is pinned by `tests/test_arm_readiness_schemas.py:500-502`. Registry
v2 carries the same row at `d117_row_registry_v2.json:769-776` and the current R1
role/code/type entries at `:326-366`.

### 4.5 Complete path if the RF-32 ruling adds a readiness code

No such addition is authorized by this document. If the magistrate orders
one, the implementation must change all of the following together. This path
is complete for the current mechanism because code families and types are
united at `arm_readiness.py:192-243`, registry roles are checked at
`:1888-1946`, the produced/dynamic sets are checked at
`arm_readiness_evidence.py:2018-2054`, and the mirror repeats the relations at
`tests/test_arm_readiness_integration.py:583-639`:

1. Add the exact spelling to the ruled `R1_POLICY_REASON_CODES`,
   `R1_LIFECYCLE_REASON_CODES`, `R1_CUSTODY_REASON_CODES`, or
   `R1_GIT_REASON_CODES` family at `arm_readiness.py:192-204`; the magistrate
   must rule the type.
2. Let `REASON_TYPE_BY_CODE` acquire the same type through the corresponding
   family expansion at `arm_readiness.py:239-242`.
3. Add a ruled role to `R1_REFUSAL_ROLES` at `arm_readiness.py:520-530` if the
   code is registry-role-resolved. The registry validator requires every role
   exactly once at `:1888-1946`.
4. Add the matching `{role, code, type}` object to
   `configs/arm_readiness/d117_row_registry_v2.json:326-366`. Do not edit the
   SHA-pinned v1 registry.
5. Add an actual runtime emission site. If it appears as a quoted literal
   after `class ArmReadinessError`, the produced scan sees it and it must not
   enter `dynamic`.
6. If and only if it is registered but never appears as a runtime literal,
   add it to the deriver's `dynamic` set at
   `arm_readiness_evidence.py:2038-2049` and make the mirror's role map cover
   it. For an R1 role-resolved code, the exact justification produced by the
   mirror is:

   ```text
   resolved by role <ROLE> from the R1 registry refusal_vocabulary
   ```

   That string shape is fixed by
   `tests/test_arm_readiness_integration.py:628-633`.
7. Extend registry-load and refusal-emission regressions, including
   `tests/test_arm_readiness_schemas.py:504-515` and the mirror test.

Adding a registered code without a runtime literal and without both dynamic
and mirror justification breaks check 2. Adding a literal without family and
type registration breaks check 1. Adding a registry entry without the same
code/type authority breaks registry loading at `arm_readiness.py:1930-1940`.

## 5. Rehearsal coverage evidence per changed code

**Rehearsal-observable** means a ruled G-row deliberately triggers and records
the exact refusal. **Unit-level only** means a deterministic test may observe
the code but the ruled rehearsal has no negative injection for it. A successful
gate which merely avoids a refusal does not count. The ruled G-rows specify
trigger outcomes, not emitted codes (`debate-sol-critique.md:63-74`; adoption at
`MAGISTRATE-RULING-T0-UNATTENDED.md:91-105`).

The author and ARM observations must be separate. An author-side anchor delta
above 5 ms aborts before a receipt is published
(`seat-opus-design.md:384-400`), so ARM has no receipt to consume. The
implementation must add two cases to **G10's observation set**:

1. Run the real author with an injected R0-to-author delta above 5 ms; record
   `evidence_author_t0_clock_attestation_underivable` and prove that no PASS
   evidence namespace was published.
2. Give the real ARM evaluator a valid published `PROBE` receipt and an
   injected ARM-evaluation anchor more than 5 ms from the published T-0 anchor;
   record `readiness_clock_preflight_refused`. The 5 ms - 1 ns ARM case passes.

These are additions to the ruled G10 row's observations, not new rehearsal
gates and not changes to the ruled ten-row count.

| code | disposition | supervised-rehearsal evidence |
|---|---|---|
| `readiness_clock_preflight_refused` | RE-TARGETED | **G10 addition 2** records the real ARM evaluator's code above 5 ms and a pass at 5 ms - 1 ns. G4's successful arithmetic is not refusal evidence. |
| RF-32 production-rejection code | RULED ELSEWHERE (§6.2) | **G7 ships UNRULED in this row.** It must feed an otherwise valid rehearsal receipt to the ruled production consumer and record the ruled code. The ruling requires production-side rejection (`MAGISTRATE-RULING-T0-UNATTENDED.md:97-100`), while HEAD only permits a future evaluator (`docs/process/d149-go-receipt-template.md:58-66`); §6.2 therefore must be answered before G7 can be recorded. |
| `evidence_author_t0_clock_attestation_missing` | RE-TARGETED | **Unit-level only:** the ruled ten rows have no missing-artifact injection, and removing `clock-reference.json` prevents the full lifecycle. |
| `evidence_author_t0_clock_prior_state_missing` | RETIRED | **Unit-level/source-absence only, not rehearsal-observable**: the retired step cannot be invoked in the new rehearsal; preserve old REFUSE transcripts without replay. |
| `evidence_author_t0_clock_attestation_underivable` | RE-TARGETED | **G10 addition 1** records the real author's >5 ms code and absence of a published namespace. Other RF-01–RF-14, RF-16–RF-18, RF-36 and RF-37 limbs remain unit-level because G4 injects none of them. |
| `evidence_author_t0_clock_probe_underivable` | RE-TARGETED | **Unit-level only, not rehearsal-observable**: G4 records a successful second exact-Off action but does not inject wrong stdout or nonzero exit. |
| `evidence_author_t0_predicate_refused` | RE-TARGETED | **Unit-level only, not rehearsal-observable**: a real arm-side G10 failure emits the readiness code, while this author self-check code requires a derived-value mutation or author-time relation failure. |
| `evidence_author_t0_existing_stale` | RE-TARGETED | **Unit-level only, not rehearsal-observable**: the ruled rehearsal does not deliberately re-authenticate a stale existing namespace. |
| `evidence_author_t0_clock_disable_missing` | REUSED-UNCHANGED | **Unit-level only:** G4 requires the capture to exist and therefore cannot emit its missing-artifact code. |
| `evidence_author_t0_capture_command_failed` | REUSED-UNCHANGED | **Unit-level only:** G4 records a successful first exact-Off action, not a nonzero command result. |
| `evidence_author_t0_capture_result_invalid` | RE-TARGETED | **Unit-level only, not rehearsal-observable**: G4 proves the first exact-Off stdout passed but never substitutes a wrong exit-zero string. |
| `evidence_author_t0_capture_sequence_invalid` | RE-TARGETED | **Unit-level only, not rehearsal-observable**: G1 proves the governed order passed but does not deliberately reorder steps. |
| `evidence_author_t0_capture_boot_probe_failed` | REUSED-UNCHANGED | **Unit-level only:** the full rehearsal stays on one boot and does not inject a boot-probe failure. |
| `evidence_author_t0_capture_clock_observation_invalid` | REUSED-UNCHANGED | **No new observation:** G1's closed stdin proves no prompt survived. The old prompt emission is removed, but the D-078 spelling remains registered and need not emit. |

The final successor rehearsal must also re-derive the ordinary
`REASON_CODE_COVERAGE` evidence row against the exact final head, satisfying
the successor-replay obligation at `alpha_arm_readiness.md:72,111`. That
re-derivation proves the readiness exact-set relations; it does not extend
the exact-set check to Vocabulary B.

## 6. Decision record: both authority questions answered 2026-08-26

### 6.1 Resolved reuse choice for the missing reference capture

`clock_reference_capture` reuses
`evidence_author_t0_clock_attestation_missing`, the existing missing-input
spelling at `joulewise/arm_readiness_evidence_t0.py:150,521`; the derived key
shape at `:469-471` requires that mapping key. The rejected alternative was a
new `evidence_author_t0_clock_reference_missing` spelling, which would have
raised an unruled registration question. The residual legibility cost is that
the retained name says “attestation” although the missing input is now the
clock-reference capture. The ruled row and evidence kind are unchanged, so
that naming debt is accepted here.

### 6.2 RULED — the production rehearsal-rejection consumer is UNATTENDED-LAUNCH-01's

**Question:** Which production entry point consumes the rehearsal receipt for
G7, and which refusal code must it emit?

**Options considered:**

1. Route it through an ARM production entry point and reuse the registered
   `readiness_usage_invalid` code for a receipt explicitly marked as having no
   production authority.
2. Add a new readiness code and R1 role using every step in §4.5.
3. Let the rehearsal harness reject its own receipt. This does not satisfy the
   ruling's stronger “production-side mechanical REJECTION” language.

**Recommendation:** option 1 if the magistrate confirms the ARM entry point;
the code's existing meaning is invalid use, and reuse avoids vocabulary
proliferation. The consumer choice remains an authority decision.

**MAGISTRATE RULING (2026-08-26).** The consumer is named, and it is not an
ARM entry point: a window launches only against a valid, non-rehearsal D-149 GO
receipt, and `scripts/launch_window.py`'s launch-capability consumption is the
production entry point that must refuse a receipt **by class**. That refusal
therefore belongs to `UNATTENDED-LAUNCH-01` by this row's own scope fence
(`MAGISTRATE-RULING-T0-UNATTENDED.md:114-118`: this row removes the T-0
*evidence* blocker only, and the *launch* blocker is a separate row). Option 1
above — reusing `readiness_usage_invalid` at an ARM entry point — is therefore
NOT adopted; the recommendation is superseded by the ruling and is retained
only as the record of what was considered.

The same ruling closes the separately-raised question of a window launching
with no T-0 GO receipt at all: it is the *same missing mechanism* seen from the
other end. Nothing in `scripts/` or `joulewise/` consumes a D-149 GO receipt at
HEAD, so there is no launch precondition to weaken — the mechanism was never
built.

**Disposition for THIS row:** G7 ships as a first-class `UNRULED` gate that can
never count as a pass, and RF-32 adds no code to either vocabulary here. The
consumer requirement is written into `UNATTENDED-LAUNCH-01`'s kernel row and is
deliberately NOT implemented in this row.

**Blocked work:** none remaining in this row. RF-32's production-side refusal
code is selected by `UNATTENDED-LAUNCH-01` when it builds the consumer.

### 6.3 COLD-GATE-PENDING — R1 ordering conflicts with the five-second validity-origin bound

**Question:** Which reconciliation must govern the ruled
R1-completion-to-validity-origin upper relation: move the stamp, reorder
derivation, relax the five-second bound, or drop its upper half?

**The conflict:** The ruling requires both that R1 complete before the author's
fresh maintenance and process censuses and that
`0 <= validity_origin_ns - R1_last_completion_ns <= 5_000_000_000`. At HEAD the
clock row is first in `_EXPECTED_ROWS` (`arm_readiness_evidence_t0.py:68-84`),
`_required_rows` preserves that order (`:731-756`), the author derives the full
fifteen-row census in one ordered loop (`:1979-1990`), and `issued_at` and
`validity_origin` are stamped only after the loop (`:1992-1993`). Thus R1 is
followed by fourteen intervening derivers before the stamp.

The order and subprocess census were re-derived against HEAD with these
commands:

```text
$ git show HEAD:joulewise/arm_readiness_evidence_t0.py | nl -ba | sed -n -e '68,84p' -e '731,756p' -e '1979,1993p'
    68  _EXPECTED_ROWS = (
    69      "clock.correct_and_prior_state",
    70      "clock.network_time_off",
    ...
    83      "t0.storage_backup_capacity",
    84  )
   731  def _required_rows(context: _Context) -> list[_Mapping[str, _Any]]:
   ...
   744      if tuple(row["row_id"] for row in selected) != _EXPECTED_ROWS:
   ...
   756      return selected
  1979      derived: list[_DerivedRow] = []
  1980      for row in rows:
  1983              item = _DERIVERS[row_id](context)
  ...
  1990          derived.append(item)
  1991      _validate_capture_order(context)
  1992      issued_at = context.clock.utc_now()
  1993      validity_origin = context.clock.monotonic_ns()
$ git show HEAD:joulewise/arm_readiness_evidence_t0.py | /Users/edr/code/JouleWise/.venv/bin/python -c 'import ast,sys; tree=ast.parse(sys.stdin.read()); assigns={t.id:n.value for n in tree.body if isinstance(n,(ast.Assign,ast.AnnAssign)) for t in ((n.targets if isinstance(n,ast.Assign) else [n.target])) if isinstance(t,ast.Name)}; rows=ast.literal_eval(assigns["_EXPECTED_ROWS"]); timeout=ast.literal_eval(assigns["_PROBE_TIMEOUT_SECONDS"]); calls=[]; [(calls.append((fn.name,node.lineno,ast.literal_eval(node.args[3])))) for fn in tree.body if isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef)) for node in ast.walk(fn) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=="_fresh_probe"]; print("expected_row_count",len(rows)); print("intervening_deriver_count",len(rows)-1); print("fresh_probe_call_count",len(calls)); [print(f"{fn}:{line}",*argv) for fn,line,argv in sorted(calls,key=lambda x:x[1])]; print("timeout_each_seconds",timeout); print("fresh_probe_elapsed_lower_seconds",0); print("fresh_probe_elapsed_upper_seconds",len(calls)*timeout)'
expected_row_count 15
intervening_deriver_count 14
fresh_probe_call_count 11
_derive_clock_probe:895 /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off
_maintenance_probe:991 /usr/bin/pgrep -lf XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd
_thermal_probe:1038 /usr/bin/pmset -g therm
_derive_process_census:1396 /usr/bin/pgrep -x caffeinate
_derive_process_census:1397 /usr/bin/pgrep -lf codex|claude|t3
_derive_process_census:1398 /usr/bin/pgrep -lf Safari|Google Chrome|Chromium|Firefox|browser automation
_derive_process_census:1399 /usr/bin/pgrep -lf powermetrics|window-chain|run_campaign|tail -f|watch
_derive_powermetrics:1474 /usr/bin/sudo -n /usr/bin/powermetrics -i 200 -n 1
_derive_power:1509 /usr/bin/pmset -g batt
_derive_power:1510 /usr/bin/pmset -g custom
_derive_power:1511 /usr/sbin/system_profiler SPPowerDataType -json
timeout_each_seconds 45
fresh_probe_elapsed_lower_seconds 0
fresh_probe_elapsed_upper_seconds 495
```

Every `_fresh_probe` subprocess in the intervening derivers is therefore:

| Deriver row | Exact argv | Governing timeout |
|---|---|---:|
| `clock.network_time_off` | `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` | 45 s |
| `t0.background_quiet` | `/usr/bin/pgrep -lf 'XProtect\|mds_stores\|mdworker\|mdbulkimport\|backupd\|photoanalysisd\|softwareupdated\|Spotlight\|mediaanalysisd'` | 45 s |
| `t0.display_thermal_idle` | `/usr/bin/pmset -g therm` | 45 s |
| `t0.no_stray_keepawake` | `/usr/bin/pgrep -x caffeinate` | 45 s |
| `t0.no_stray_keepawake` | `/usr/bin/pgrep -lf 'codex\|claude\|t3'` | 45 s |
| `t0.no_stray_keepawake` | `/usr/bin/pgrep -lf 'Safari\|Google Chrome\|Chromium\|Firefox\|browser automation'` | 45 s |
| `t0.no_stray_keepawake` | `/usr/bin/pgrep -lf 'powermetrics\|window-chain\|run_campaign\|tail -f\|watch'` | 45 s |
| `t0.passwordless_powermetrics` | `/usr/bin/sudo -n /usr/bin/powermetrics -i 200 -n 1` | 45 s |
| `t0.power_path` | `/usr/bin/pmset -g batt` | 45 s |
| `t0.power_path` | `/usr/bin/pmset -g custom` | 45 s |
| `t0.power_path` | `/usr/sbin/system_profiler SPPowerDataType -json` | 45 s |

The remaining intervening derivers—terminal review, campaign-lock absence,
fresh roots/waivers, ledger reservation, machine readiness, offline inputs,
single-launch capability, and backup capacity—execute no `_fresh_probe`, but
their filesystem, parsing, Git, and custody work has no declared aggregate
timeout.

**The arithmetic:** for the governed fresh-probe waits alone,
`0 s <= elapsed <= 11 * 45 s = 495 s` (a successful path is strictly below
the timeout ceiling). For the complete interval,
`elapsed_R1_to_validity_origin = elapsed_fresh_probes + elapsed_other_work`,
where `elapsed_other_work >= 0` and HEAD declares no finite upper bound.
Consequently five seconds is reachable in the best case, but it is not
guaranteed in any case: one permitted probe can itself take more than five
seconds, and the full path has no aggregate deadline.

**A second, independent defect:** `validity_origin` is
`context.clock.monotonic_ns()` (`arm_readiness_evidence_t0.py:1992-1993`), and
the production clock binds that callable to `time.monotonic_ns()` (`:241-253`).
On Darwin the bench measurement in `debate-opus-critique.md:59-65` identifies
that Python clock as `CLOCK_UPTIME_RAW`, while the ruling requires the R1
endpoints to use `CLOCK_MONOTONIC_RAW`. The critique measured
`MONOTONIC_RAW - UPTIME_RAW = 812,998 s` on this machine. Subtracting endpoints
read from two different clocks is not a duration at all, so the five-second
relation is not merely tight; it is currently ill-typed.

The minimal clock-domain cure is to publish an ordinary-monotonic R1 completion
endpoint alongside the RAW endpoint. The lead has already pinned that field
into the implementation contract as `r1_batch_finished_monotonic_ns`; the RAW
endpoint remains evidence for the ruled anchor physics.

**Options considered:**

1. Move the validity-origin stamp to immediately after R1. This preserves the
   ruled order and five-second constant, at the cost of starting the six-hour
   receipt horizon before the remaining derivation work and changing the stamp
   from near-publication time to reference-completion time.
2. Reorder derivation so the clock row derives immediately before the fresh
   maintenance and process censuses and the stamp follows those censuses. This
   keeps the censuses after R1, at the cost of departing from the registry-
   preserved row order or adding a separate scheduling layer and moving the
   stamp ahead of the other derivations.
3. Relax the five-second bound to a value the current derivation order can
   honor. This preserves the one-loop order, at the cost of changing a ruled
   number; the 495-second probe envelope is still insufficient as a guarantee
   unless the currently unbounded other work also receives an aggregate
   deadline.
4. Drop the upper bound and retain only the ruled six-hour lower relation. This
   is the smallest implementation surface, at the cost of losing the ruled
   maximum R1 age at issuance.

**Recommendation:** option 1, because it simultaneously honors the explicit R1
ordering and unchanged five-second constant, makes the six-hour validity period
conservatively shorter after publication, and avoids registry-order churn. This
recommendation is not a decision; only the magistrate can select among these
costs.

**Interim disposition:** The lead has ordered this round to implement

```text
valid_until_monotonic_ns - r1_batch_finished_monotonic_ns >= 21_600_000_000_000
```

and to publish `r1_batch_finished_monotonic_ns` on the same ordinary-monotonic
clock as `valid_until_monotonic_ns`. This enforces the six-hour lower relation
now and makes the upper bound a one-constant change once ruled. No inert or
always-true gate is added in its place.

**MAGISTRATE DISPOSITION (2026-08-26): COLD-GATE-PENDING.** The magistrate
accepts the finding as a defect in its own prior ruling rather than an
implementation problem, and declines to patch it from the seat that wrote it:
reinterpreting a prior verdict is a cold-gate trigger, not a magistrate's own
call. The stop recorded here is therefore CORRECT and stands. The four options
above go to a cold instance; the recommendation is not a decision and remains
one.

Until that cold gate rules, this row's disposition is frozen exactly as
implemented: `r1_batch_finished_monotonic_ns` published on the ordinary-
monotonic clock so the endpoints are of one type, the six-hour lower relation
enforced and non-tautological, **no upper bound, and no inert or always-true
substitute**. Nothing about this may be reinterpreted as "predicate recency" or
quietly relaxed in a later round.

**Blocked work:** the five-second upper half of RF-17 is COLD-GATE-PENDING. The
implemented interim work is not blocked and is not provisional.

### 6.4 D-078 capture-code disposition

`evidence_author_t0_capture_clock_observation_invalid` is REUSED-UNCHANGED: its prompt emission sites are removed, but its registered spelling, D-078 entry, exact twelve-code set, and exact-count test remain untouched (`scripts/capture_t0_step.py:83-100`; `docs/decision_log.md:9571-9588`; `tests/test_capture_t0_step.py:624-631`).

### 6.5 Ed-owned physical prerequisites already named by the ruling

Only the four ruled Ed-hands items bear on this vocabulary:

1. Install/exercise the existing D-127 exact `off`/`on` sudoers capability;
   failure manifests as RF-19/RF-21 and their existing author/capture codes.
2. Run the adjacent, out-of-T-0 privileged anchor positive control; it is the
   only supervised physical demonstration that RF-11/RF-25 is coupled to a
   real wall-clock adjustment.
3. Ratify D-127.1's scope reduction and the unchanged six-hour horizon; the
   retirement and RF-18 exact-deadline relation depend on that authority.
4. Bench-verify the exact `setUsingNetworkTime: Off` stdout under sudo before
   RF-20/RF-22 may gate; an unverified wrong byte would refuse every window.

## 7. Acceptance contract for the implementation round

The code round satisfies this document only when all of the following are
true:

- [x] Both authority questions have recorded answers (2026-08-26) and the
  implementer selected neither. §6.2 is RULED: the production consumer is
  `scripts/launch_window.py`'s launch-capability consumption, which belongs to
  `UNATTENDED-LAUNCH-01` by this row's scope fence, so RF-32 adds no code here
  and G7 ships as a first-class `UNRULED` gate. §6.3 is COLD-GATE-PENDING: a
  cold instance rules on the conflict, and until it does this row's disposition
  is frozen exactly as landed — six-hour lower relation enforced, no upper
  bound, no inert substitute.
- [ ] Vocabulary A has 0 ADDED, 0 RETIRED, 0 REUSED-UNCHANGED, and 1
  RE-TARGETED spelling before any later RF-32 ruling. Numeric and ARM-anchor
  failures emit `readiness_clock_preflight_refused` through
  `arm_readiness.py:6039-6064,5978-5986`.
- [ ] Vocabulary B has 0 ADDED, 1 RETIRED, 4 REUSED-UNCHANGED, and 7
  RE-TARGETED spellings. The author census is predicted to be 43, the D-078
  capture set remains 12, and the missing-artifact mapping is predicted to be
  14 entries with 14 distinct values; the code round reruns the §3.2 command.
- [ ] `_RUNBOOK_ARTIFACT_REASON_CODES` removes `clock_attestation` and
  `clock_prior_state_capture`, adds `clock_reference_capture`, and maps the new
  key to existing `evidence_author_t0_clock_attestation_missing`, as forced by
  `arm_readiness_evidence_t0.py:469-471`.
- [ ] The author retires only
  `evidence_author_t0_clock_prior_state_missing`. The capture producer keeps
  `evidence_author_t0_capture_clock_observation_invalid` in D-078's exact
  twelve-code set while removing its prompt emission sites.
- [ ] RF-01–RF-14, RF-16–RF-18, RF-36, and RF-37 share
  `evidence_author_t0_clock_attestation_underivable` when derivation identifies
  the failure; RF-15 reuses
  `evidence_author_t0_clock_attestation_missing`. No per-rule SNTP or anchor
  code is added.
- [ ] The first exact-Off zero/nonzero paths use
  `evidence_author_t0_capture_result_invalid` /
  `evidence_author_t0_capture_command_failed`; the second exact-Off paths use
  `evidence_author_t0_clock_probe_underivable`.
- [ ] The source-discriminated predicate preserves
  `prior_systemsetup_state_captured: true` for `OPERATOR_ATTESTATION`, requires
  every PROBE input, rejects non-integer/boolean/reversed endpoints, and
  recomputes the ruled §2 relations numerically rather than trusting booleans.
  While §6.3 is COLD-GATE-PENDING, it implements the active six-hour lower
  relation with published ordinary-monotonic `r1_batch_finished_monotonic_ns`;
  it does not substitute an inert or always-true gate for the frozen upper
  bound.
- [ ] ARM evaluation takes one RAW→REALTIME→RAW sample, rejects read skew above
  1 ms, injects the sample into the predicate only for the PROBE clock branch,
  and maps a delta above 5 ms to the existing readiness code. Author
  self-check, existing-namespace re-authentication, freeze replay, and ARM
  receipt verification perform no unconditional clock read.
- [ ] The readiness census replays at the final head with `produced = 45`,
  `registered = 55`, `dynamic = 10`, empty `produced - registered`, and
  `registered - produced == dynamic`, unless the later RF-32 ruling explicitly
  authorizes and fully registers a new code.
- [ ] `_run_suite` executes the named focused test successfully in the target
  repository; every executed project module is bound to committed bytes; the
  three §4 primary artifacts are readable and HEAD-identical; and
  `arm_readiness.py` is strict UTF-8 with exactly one
  `class ArmReadinessError` split point.
- [ ] The SHA-pinned v1 registry is unchanged. Any RF-32 ruling that adds a
  readiness code follows every cited family, type, role, registry-v2,
  literal/dynamic, and mirror-test step in §4.5.
- [ ] Each numbered author clock rule has a defect-shaped test with a distinct
  detail, `kind == "CLOCK_ATTESTATION"`, the shared underivable code where
  applicable, and proof that no partial PASS evidence namespace was published.
- [ ] G10 records separate real-author and real-ARM >5 ms cases with their
  exact codes; these are observation additions to G10, not new gates. G7 stays
  `UNRULED` in this row and is recorded by `UNATTENDED-LAUNCH-01` when that row
  builds the consumer §6.2 names. No successful-only
  G-row is reported as refusal-code evidence.
- [ ] Historical/attended receipts remain consumable through the unchanged
  ARM `OPERATOR_ATTESTATION` branch. New-author re-authentication of an old
  operator namespace refuses as described in §3.3 and is not reported as
  historical ARM-consumption failure.
- [ ] The final successor rehearsal re-derives and binds
  `REASON_CODE_COVERAGE` at the exact final head, discharging
  `alpha_arm_readiness.md:72,111`.

### Source conflicts and their disposition

These are source conflicts, not implementation choices:

1. `seat-sol-design.md:120-140,180-188` proposes a new predicate row, a
   20-minute horizon, Apple-only sampling, and SNTP failures under
   `evidence_author_t0_capture_clock_observation_invalid`. The ruling adopts
   the Opus single-row skeleton, keeps six hours, and chooses three providers
   (`MAGISTRATE-RULING-T0-UNATTENDED.md:35-59,73-83`); the adopted refusal
   convention assigns derivation failures to
   `evidence_author_t0_clock_attestation_underivable`
   (`seat-opus-design.md:348-354`). The Sol assignments do not survive.
2. `seat-opus-design.md:276-295,311-330` shows only three stored PROBE
   booleans and no issuance timestamp relations or arm-side re-sample. The
   later ruling adds numeric RF-09/RF-10/RF-16/RF-17/RF-18 recomputation and
   RF-25 (`MAGISTRATE-RULING-T0-UNATTENDED.md:61-83`). The ruling expands the
   adopted skeleton; implementing the seat's short illustrative snippet
   verbatim would be incomplete.
3. `seat-opus-design.md:268-270` says “No registry change,” while the ruling
   says any new code must register under the R1 tables
   (`MAGISTRATE-RULING-T0-UNATTENDED.md:107-111`). There is no implementation
   conflict because the §3 census proves zero new spellings in either
   vocabulary.

The ruling records no surviving dissent at
`MAGISTRATE-RULING-T0-UNATTENDED.md:133-139`; this document therefore carries
only the three cited source differences above into implementation.
