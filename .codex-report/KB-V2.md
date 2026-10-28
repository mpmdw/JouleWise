# KB-V2 — activation 39206674, 2026-10-28

Status: in progress; reconciled rule awaiting the lead's admission. No hardware measurements.

## Authority and inputs

User brief: base `ci/2026-10-27-bytes-enddate` at `e624d67c7ca154c67df77f105b6aa8adcad047a4`; branch `codex/2026-10-28-kb-v2`.
Write scope is exactly the registration draft, probe, new probe test module and this report.
The brief overrides local broad-suite and bookkeeping defaults: run only the touched test module; preserve every other file.
Environment: `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, `/workspace/.joulewise-env/bin/python3.13` (3.13.5).

Inputs fetched successfully from mpmdw/JouleWise-data:
- Fable `39398e572ea0943edc77f0981d82e3be32311a32`, `kb-cold/REPORT.md`.
- Opus `ecd46c1124000dbfbc51b475068661ceefb62a1f`, `kb-cold/REPORT.md`.
- Reconciler `0609bcc0caf941fd68c36fccea323f34c3951730`, `kb-revise/`.
- Current draft: JouleWise main `8b39d4846de168ab3fb83b21084238e3491ade21`.

## Decisions I made

- Adopt the lead's Fable 1 ruling (a): retain the disclosed remainder, ε_flip and per-arm GPU frequency/residency. No new kernel or leverage model.
- This is bounded [AGENT] implementation/documentation work; no quiet-Mac collection, unblinding, admission or merge.

## NEEDS_RULING

None at intake. The access exception does not apply: all inputs are reachable.

## Correction table, execution, receipt and CI

Pending audit and implementation. This early checkpoint establishes the branch and input pins.
