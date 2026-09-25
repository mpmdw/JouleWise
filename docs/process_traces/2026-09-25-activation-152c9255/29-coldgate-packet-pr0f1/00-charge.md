# Charge — cold gate PR0-F1-01: a gated mutant masked by a known production defect

Assembled 2026-09-25 10:24 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## Background

PR-0 freezes a snapshot of every v1 claim-gate decision. Its acceptance v3 (`ex-02-acceptance-v3-ruling.md`) requires every gated mutant to be killed or listed with a proof. One mutant survives because a known production defect masks it (`ex-01-round4-seat-report.md` flag F1). The magistrate's proposal is `ex-03-magistrate-proposal.md`. It is argument before you, not authority.

## Questions

- **Q1.** Verify the masking claim on `origin/test/2026-09-25-claimgate-pr0-golden` at `1b8bae45` in a /tmp clone. Read the code at `paper_custody.py` ≈`:600-660` and `:1340-1350`. If your budget allows, run the single mutant through the golden comparison.
- **Q2.** Rule on the proposal: AFFIRM it (give the exact exception-entry format and the recertification text), take the alternative, or write another.
- A plain summary of at most 2 lines for Ed.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root) or `/Users/edr/night-custody`.
- The discovery suite and background tasks are not allowed; keep test runs light.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
bf305ccb933ec7bdecb76b02848322634a02d3b16e431c03cce8efaba18bafe5  ex-01-round4-seat-report.md
ddc1f1bf1ec5f7f8b1911062552227e1af2788af1c6892f09d2eaa539ca276a2  ex-02-acceptance-v3-ruling.md
ba6da91a2a58e7ce0486425ef4f00f9eb46bb9ff5c72343a3e7320a7ce1fe817  ex-03-magistrate-proposal.md
```
