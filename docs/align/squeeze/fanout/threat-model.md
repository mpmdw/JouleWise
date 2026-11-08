# v5 threat-model fan-out handoff

Task date: 2026-11-08 brief. Branch: `align/2026-11-08-v5-threat-model`.
Base: `d600baba029f70592bb8e792098338e4cd6811d3` (the supplied W1/R10 lane).
Documentation only; NOT REGISTERED; no arm or native-validation claim.

## Delivered

- Reconciled the Sol prereg draft (`688d14b6e`) into
  [the v5 addendum](../../../registrations/align_v4_squeeze_addendum_DRAFT.md).
- Preserved reviewer2's A0–A13 numbering; every row maps meter, monitor and
  seeded rerun responsibilities, qualifications and scope. The source crosswalk
  preserves both reviewer2 seats, both squeeze-design seats and SOL's families,
  including prompt injection, misfit camouflage, smoothing, batching and PCs.
- Added the scoped D-139 A1 amendment and trusted-harness/readable-view boundary.
  Stripped ordinary runtime reasoning is a software benchmark; actual side
  generation/tool subprocess work is the distinct physical challenge.
- Stated the disguised-compute and cheap-decoy shared blind spots, battery and
  span limits, and escape per assigned sabotage attempt as the primary estimand.
- Recorded 28 reconciliation decisions, immutable source pins and admission
  blockers. Removed unadmitted SOL campaign/decision constants from the active
  proposal rather than treating them as lead rulings.

Changed files: the addendum and this report only. No code or permanent tests
changed. Coordination state, v4 protocol/energy documentation and R1 were not
edited. No kernel task was registered. No independent reviewer or subagent was
launched; the lead retains final review and registration authority.

## Assumed binding rulings

The supplied 2026-11-08 brief overrides the older design proposals: v4's same
model/settings/thermal policy, only meter capture and sealed full-reasoning
transcripts added; compatible v4 windows count toward m >= 39/pair; about seven
calibration windows plus separate T1–T3; per-channel maximum thresholds; frontier
API primary/off-box and local secondary; no v4 monitor scoring before
registration; unaccounted side-work PCs; strict all-cells survival descriptive.
ED items 204/210 supply Q6, the power path and the A1 amendment. No authority
was inferred to install a new numerical estimator, search budget or live kit.

## Verification

Ran one temporary unittest module, using document text and a tiny synthetic
table-parser fixture only; no measurement/model code or data were loaded:

```text
python3.13 -B /private/tmp/jwsol/fan/v5-threat-model/tmp/test_threat_model_docs.py
```

Failing first against the unchanged Sol draft: 8 tests, 7 expected failures,
1 synthetic-parser pass (0.004 s). After reconciliation: 8 tests passed
(0.001 s); final rerun also passed. Checks cover exact unique IDs, all three
channel columns, amendment/sealing text, shared limits, source aliases,
attempt-denominator/threshold requirements, frozen-v4 scope and decision ledger.
These are document-contract checks, not evidence that the science is valid.
The temporary harness is outside the commit; no permanent test module was added.

Also manually checked the source-to-taxonomy mapping, all 28 decisions and
the original Sol-to-reconciled diff. `git diff --cached --check` passed after
staging. A protected-path diff confirmed no changes to `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, `tests/test_gen_state.py`,
`docs/align/pilot_protocol_v4.md` or `docs/align/energy_residual.md`.
The full suite and compileall were not run: full-suite execution is forbidden
by the brief and this is documentation only. Total test time was below one
second, far below the 20-minute cap.

## Open questions and next exact step

The drafting deliverable is complete; registration remains pending. The lead
should review addendum §9 with the other fan-out lanes, then freeze M1/view/
sampling, the DC estimator and calibration/test construction, meter/battery/
reference qualification, PC criteria, red-team effort and manifests, and the
primary inference/decision bars. The main statistical uncertainty is whether
pooled LOTO calibration and full-fit test scores support the assumed rank
exchangeability; common configuration alone does not establish it. Imputed
off-Mac alarms and non-rejection of a distribution test are not physical proof.

No MLX implementation or MLX tests changed. Outside this sandbox, the lead
must qualify native readable-view/recount preservation, seeded determinism,
whole-member meter plus battery closure and executed side-work injections
before live claims; those gates were not run or cleared here.

All requested Git refs were cached, so no fetch was attempted under the
no-network rule. No external literature verification, data access, monitor
scoring, model download, measurement, process control, push or publication
occurred. Paths cited by source documents were treated as text only.

Local commit subject: `docs(align v5): unify squeeze threat model and attack taxonomy`.
The final handoff supplies its resulting hash; no push is authorized.
