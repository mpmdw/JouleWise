# 03/00 — Design consult CLAIMGATE-WIRING-01: end-to-end wiring of claim gate v2

Assembled 2026-09-25 ≈04:33 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed. This is integration design, not new science. The science texts are already ruled: CLAIMGATE-01 and its addendum, final texts v2 at `docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md` (CG-1..CG-4). Treat those texts as fixed inputs. If wiring them faithfully is impossible, say so as a BLOCKER. Do not redesign them.

## Terms, as used here

- **Claim gate.** The code that decides whether a measured energy difference between two arms may be stated in the paper. It compares the difference Δ against a detection floor.
- **F_est.** The detection floor under v2: the smallest energy difference this instrument can attribute in this measurement epoch, estimated from the calibration record. An epoch is a fixed macOS build, machine and protocol.
- **v1 / v2.** The old gate, which uses a single shared floor, and the ruled new gate. `claim_rule_version` is frozen per contrast, where a contrast is one named arm-versus-arm comparison in a registry.
- **Manifest.** The analysis manifest (`joulewise/analysis_manifest.py`, `analysis_manifest_v3.py`), which validates the registered contrasts with exact-key checks.
- **Paper custody.** Receipts that bind the paper's numbers to the exact validator and fixture sources (`tests/test_paper_custody*`). Changing validator source changes the receipt digests.

## Where the implementation stopped

The WIP is on branch `origin/feat/2026-09-24-claimgate-v2`, head `3cd00c73`. Its seat reports are `93b-claimgate-impl-report.md` and `97b-claimgate-impl-resume-report.md` in the same trace directory. The focused suite passes 276 tests, and the desk simulations meet their checks. The magistrate stopped the work at four integration questions:
- **W1 — F_est provenance.** No authenticated same-epoch calibration wire supplies F_est, its unit and its artifact binding, so v2 admission refuses. The seat recommends recomputing F_est from an authenticated same-epoch calibration record, checking unit and artifact id at replay. The alternative is binding a separately authenticated calibration sidecar. Decide where F_est is minted, what authenticates it, which artifact carries it, and how replay re-derives it. Account for the acceptance lane: the 25G83 calibration acceptance is being re-decided now (council ACCEPTANCE-25G83-02), and the successor acceptance generation is the natural producer.
- **W2 — Manifest v2 schema.** The exact-key validators reject the v2 per-contrast fields: version, claim shape and envelope registration. Specify the schema change in the two validators and their tests, and keep v1 manifests byte-identical in behaviour.
- **W3 — Mixed v1/v2 registries.** Choose between per-contrast floor selectors and separate registries per version. Say what the existing claim-bearing registries (the paper's current contrasts) become.
- **W4 — Paper-custody receipts.** Nineteen tests hold stale receipt digests because validator source changed. Specify the reissue procedure: who mints the receipts, and what proves no paper number moved. Name the check that distinguishes a legitimate reissue from masking a real change.

## Answer

For W1–W4, give:
- the design, as executable text an implementation seat can follow without choosing;
- the files and tests it touches, as the WRITE_SCOPE;
- the failure it must refuse, as a named test;
- concerns tiered BLOCKER / MATERIAL / NIT.

Then give one ordering of the PRs, and say what would show the design wrong. Finish with at most 5 lines on where you expect the other seats to disagree.
