# Charge — cold gate CLAIMGATE-WIRING-01: rule the design consult on end-to-end wiring of claim gate v2

Assembled 2026-09-25 ≈04:55 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed. No claim-bearing data can exist before the 25G83 instrument acceptance, so nothing here is urgent. Correctness is the only criterion.

## Background in plain words

The claim gate decides whether a measured energy difference may be stated in the paper. Its v2 science texts (CG-1..CG-4) are already ruled: `ex-91-claimgate-final-texts-v2.md`, from ruling `ex-66-20-claimgate-ruling.md` and addendum `ex-66-21-claimgate-addendum.md`. Treat those texts as fixed.

The implementation was stopped at four integration questions. Its seat report is `ex-97b-impl-resume-report.md`, and the WIP is `origin/feat/2026-09-24-claimgate-v2` at `3cd00c73`. The four questions are W1 (F_est provenance), W2 (the manifest v2 schema), W3 (mixed v1/v2 registries) and W4 (paper-custody receipt reissue).

Three blind seats answered: Sol `ex-04-seat-sol.md`, Astra `ex-04-seat-astra.md` and Opus `ex-04-seat-opus.md`. The magistrate's synthesis is `ex-30-synthesis.md`. It contains unanimous items A1–A4; a BLOCKER on the WIP (B-W2: block-level v2 admission treats blocks as replicates); splits S-W1, S-W3, S-W4 and S-PR; and new science questions Q-B1 and Q-M3. The seats and the synthesis are arguments before you, not authorities.

## Questions (for each: AFFIRM / write a different ruling; give the final text; tier BLOCKER / MATERIAL / NIT)

- **K1.** A1–A4. Verify A1 against `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` and the issuer.
- **K2.** B-W2 and the envelope-set layer. Verify WIP `joulewise/analysis_engine/__init__.py:779-799,1016-1020` via `git show origin/feat/2026-09-24-claimgate-v2:<path>`, and verify Opus's claim that one finalized v3 manifest carries exactly one window (`joulewise/analysis_manifest_v3.py` ≈`:1160-1165,3656-3659`). Rule whether Astra's in-manifest envelope design is possible.
- **K3.** S-W1: the source of the F_est null envelopes (the P2-015 comparative component versus a new registered null calibration); M-1 (freeze before data for every shape); M-2 (`n_cal`). Rule Q-M3, or route it, stating exactly what must be verified in `joulewise/detection_floor.py` and the D-124/D-125 entries of `docs/decision_log.md`.
- **K4.** S-W3: version-pure registrations plus a closed v1 allowlist, versus per-contrast selectors in one family.
- **K5.** S-W4 and S-PR: the golden PR-0, the reissue check, and the PR shape against CG-4's "one PR" text.
- **K6.** Q-B1: the J/correct F_est producer gap. Rule whether the CG-4 PR may land with J/correct refusing `not_resolvable` while the science choice goes to the four-model council, or whether the choice must precede the PR. Also rule magnitude (refuse versus build).

Finish with **"Wiring rulings (final texts)"**: one numbered paragraph per ruling, executable by an implementation seat without choosing, each with its WRITE_SCOPE and named refusal tests. Add a plain-language summary of at most 6 lines for Ed, with no project shorthand.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, any `/Users/edr/JouleWise-measurement-*` directory, or `~/Library/LaunchAgents`.
- Repository evidence may be read in your worktree, including `git show origin/feat/2026-09-24-claimgate-v2:<path>`. Focused unit tests of named modules may be run; the full discovery suite may not.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory, or any `docs/process_traces` file outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
67bbbe167ae87b80c2bddf10e2b84ab022e559a81eaa2ed0593b70da2f6fe7a6  ex-00-question.md
30cb2c8f05af8d0d590c96bf73dabab4fe31fc5faf6818b10fd9217dec86edb0  ex-04-seat-astra.md
161a6c3701231896c6d62f1864eff3c336dbc297c41185673c9ede9c8f6ded54  ex-04-seat-opus.md
8e6020d6a49af5f58f5a1b12c3f377e947bc80f2f471e66ce01e192e922676c3  ex-04-seat-sol.md
ed1dd262753a737f998b97499f5684ed8186e768b9fd1e63cd960a2eaef2227f  ex-30-synthesis.md
71b5ad892314e78e9d1b7c4ce161b674f8e855296c4f961e6456feddb2c9b5e6  ex-66-20-claimgate-ruling.md
6aceb70fe78e37cfd6f7927f11d36085f814e5b7df997745c45b35cba494fd04  ex-66-21-claimgate-addendum.md
c13171f5d04099943e4ffd7dbd68a960df4d850e41f4a7717dad9b0365eca64a  ex-91-claimgate-final-texts-v2.md
5b674c273fac04f977b38876a174bfd3c4ccca08377799c3247cd3eb668d32bd  ex-97b-impl-resume-report.md
```
