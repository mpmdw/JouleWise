# ALIGN v4 adversarial-review remediation

Date: 2026-11-06. This change is code/test remediation only; it authorizes no
measurement and changes no registered or frozen v3 configuration bytes.

## Disposition

- HIGH-1 was already resolved at lane entry: `EpisodeSpec.hybrid_checkpoint_limit`
  defaults to `None`. The new pilot-10 regression invokes `build_files()` without
  a compatibility replacement and compares every generated v3 stage plus every
  retained v0-v2 stage byte to the `83e2dac59` Git oracle.
- A single `primary_stop` classifier now owns workload and diagnostics precedence:
  deadman, runtime fault, thermal timeout/incomplete, decode budget, ordinary
  stops. All flags remain retained, and any runtime fault causes `AdapterFailure`.
- Counterbalance cells consume `EpisodeSpec.execution_policy_projection()` and
  distinguish omitted (`None`), explicit zero, and positive hybrid checkpoint
  limits.
- The binding #666/F10 contract was followed: unobserved G1/H proceeds as a valid
  X4-flagged episode. Workload classification is recorded once and diagnostics no
  longer promotes unobserved intervals to `thermal.incomplete`.

## Verification

Focused remediation suite: 86 tests passed, one optional native test skipped.
The complete `tests/align` discovery and `test_align*.py` discovery were both
started, but their repository-wide imported Monte Carlo / reachability suites ran
for many minutes and were interrupted after progressing well beyond the ALIGN
integration modules. Focused affected modules completed green. `git diff --check`
passed, and the frozen config directories have no diff from `83e2dac59`.
