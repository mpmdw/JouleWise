# Design consult — a governed bootstrap route for a new calibration identity epoch (blind three-seat consult: Astra xhigh, Opus, cold Fable)

## The problem (read `38-consult-acceptance-epoch-astra-report.md` and `39-lead-record-os-build-epoch-blocker.md` in this directory first)

The instrument's calibration acceptance (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`, D-079/D-102) binds an identity epoch
{os_build, hardware_model, power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id}. The machine's OS build changed on 2026-09-02
(25F84 → 25G83; the `/usr/bin/powermetrics` binary changed too). Every consumer on the G2-a path refuses (`acceptance_artifact_epoch_mismatch`), by
design (D-102 cl.2; D-161 fail-closed for physics/evidence). There is NO installed way to capture calibration observations under the new epoch:
`scripts/validate_powermetrics_fiducial.py --allow-live` requires a matching issued acceptance BEFORE it captures (lines ~1701–1720); the issuer
`scripts/reissue_calibration_acceptance.py` only re-derives the predecessor's members; historical import into the ledger is genesis-only
(`docs/contracts/calibration_ledger.md:15, :253`); the issued-artifact validator requires exactly one epoch equal to the acceptance's
(`joulewise/calibration_bracketing.py:522, :562, :1349–1385`).

## What you must design (a proposal for a cold-gate ruling; the resident magistrate cannot make rules)

D1. **Derivation-only capture route.** How a `[QUIET-MAC]` agent-free night captures fiducial calibration observations under a NEW epoch when no
    acceptance for that epoch exists: which script/mode (a new `--derivation-only` mode of the writer? a new night class or a `DIAGNOSTIC_NO_PACK`
    chain variant?), what it records (the full raw evidence, the identity epoch actually measured, the powermetrics binary hash, reservation
    receipts?), what it explicitly does NOT license (no G2-a, no floors, no claims; every observation `non-claim-bearing`), and how the fail-closed
    refusal stays intact for every other consumer. Cite the exact functions to change and the smallest change set.
D2. **Ledger representation.** Canonical ledger carrying both epochs (per-row `identity_epoch` already exists) with an epoch-pure derivation corpus
    selected by preregistered rule, versus a separately anchored new-epoch ledger. Give the pros/cons against the contracts (`calibration_ledger.md`
    rollback/prefix rules, D-124 single-sourcing, the bootstrap script's one-epoch-per-artifact refusal at `scripts/calibration_ledger_bootstrap.py:289`)
    and recommend one.
D3. **Corpus design and stopping rule (prospective, pre-registered BEFORE the first capture).** Sample size (r6 has 17 retained of 19; the reasoning at
    `docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md:68`), schedule (how many nights; within-night spacing;
    the existing 600 s settle; the 59-pulse census per observation; 4–8 min per observation), exclusion rules (the r6 clock-anchor exclusion),
    stopping rule, and what "a new systematic failure challenging the pre-flight screen" (D-102 cl.2) means for a fresh epoch where no screen exists
    yet. Give the arithmetic for one-night vs two-night designs. Name what is Ed's to decide (scientific rules) versus the magistrate's.
D4. **Successor issuance.** From the captured corpus to an issued `calibration_acceptance_d079_v2_n<N>_<gen>.json` under 25G83: the derivation
    (decimal statistics, quantiles, screen, budget — D-102 cl.4 semantics), the generation registration in `tests/verify_calibration_acceptance_corpus.py`,
    what the D-138 atomic transaction must carry (successor bytes + default + registry + pack/extraction pins + T1 projections + regenerated chains +
    the staged R2 patch `15-r2-coverage-ulp-staged-for-d138.patch`), and the cold science gate. Estimate the desk time honestly.
D5. **Recurrence.** The epoch will change again at the next macOS update. Propose the standing rule shape (NOT ruled here): a "new-epoch bootstrap"
    lane template so the next update costs one night, not a design round; and an arm-time check that surfaces an epoch mismatch at the DESK
    (bind-window at the dry run) rather than inside the night — already true today; say whether anything else should move earlier.

Output: a markdown design memo ≤ 250 lines: recommendation per D1–D5, the exact minimal code/contract change list (file:function), the pre-registration
text for D3, the calendar (earliest corpus night, earliest issuance, earliest G2-a) under one-night and two-night designs, risks, and the questions for
Ed. Cite file:line for every mechanism claim. Read-only; do not edit anything.
