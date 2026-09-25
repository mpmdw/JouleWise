# Charge — cold gate A292-REDUCER-DESIGN-01: rule the sealed scored reducer's design before its harness is written

Assembled 2026-09-25 ≈05:25 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## Background in plain words

The scored reducer (lane A292) turns one sealed scored night into per-cell counts and energy. A cell is one model at one MATH level. The inputs are the packer's sealed roster (merged as PR #409), the scorer's per-item rows, and the per-block capture windows in joules. Every registered item must end as exactly one counted row or one typed terminal refusal.

The method is harness-first. A seat writes executable RED acceptance tests plus an independent oracle from ruled text, and a second seat then implements to GREEN. The harness cannot be written until the design points the rulings leave OPEN are decided.

A scout mapped the binding clauses (`ex-02-scout-report.md`). Three blind seats answered R1–R7 (`ex-03-seat-{sol,astra,opus}.md`). An Opus subagent compared the seats and verified each disputed fact, and the magistrate added proposals P-S1 to P-S13 (`ex-30-synthesis.md`: Terms; R1–R7 with 13 splits; §P proposals). The seats and the synthesis are arguments before you, not authorities.

## Questions

- **D1.** For each split S1–S13: AFFIRM the magistrate's proposal, or write a different ruling. Give the deciding evidence from your own reading of the cited rulings and code. The code is `joulewise/scored_packer.py`, `joulewise/scored_registration.py`, `joulewise/adapters/mlx_runtime.py`, `tests/scored_roster_checker.py` and `tests/scored_case_generator.py`. The rulings are the paths listed in ex-30's header.
- **D2.** The three "only one seat" defects (the per-item terminal energy repeated across items; INV-13's `retry_stage` into cells; K3's `stop_reason` check), Opus's `internal_disagreement` refusal, and the deferred list. AFFIRM or amend each. Say whether anything in the deferred list must be decided before A292 can be claim-bearing.
- **D3.** Anything the seats and the synthesis all missed. In particular, check every "Agreed by all three" item against its source.
- **D4.** Issue **"A292 reducer rulings (final texts)"**. It must contain:
  - the exact input schemas;
  - the output schema;
  - the refusal-code list, each code with its trigger;
  - the completeness rules;
  - the cap rules with their boundaries;
  - the executed-status presentation;
  - the harness seat's WRITE_SCOPE with its named tests (at least one per ruled clause);
  - the implementation seat's WRITE_SCOPE.
  All of it must be executable without choosing. Add a plain summary of at most 5 lines for Ed.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, `~/Library/LaunchAgents` or `/Users/edr/JouleWise-measurement-*`.
- Focused unit tests of named modules are allowed; the discovery suite is not.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory. Do not read any `docs/process_traces` file outside this packet directory, except the ruling files ex-30's header cites (the 2026-09-23-activation-d8cc9c0a/45-*, 08-*; 2026-09-24-activation-a65fb4fa/15-*, 07d-*; 2026-09-24-activation-278ebc9e/82-*, 89-*, 117-*, 52-* trees).

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
3725ccd01da0baf94551fdfe1703c22f876181a083fe523a960b428ead9b11cb  ex-00-question.md
518b99b156e00d1736fabd2a1ab6a8e0943e85ff405d85d692eadd6ae6023262  ex-02-scout-report.md
43be873b39092ea3e94eed24bc41c3dfe241643c40b987694b0d78850aa77021  ex-03-seat-astra.md
bf970d64d425a1d62c66397956ab9d8d9e9194f8065fdcc9bf8ca623f6ef7747  ex-03-seat-opus.md
429e74a877431db802d56c7529468712fa26207803e0e7bda1349bcb93b71a11  ex-03-seat-sol.md
65f6656622a39b01628c23153e26f367e1853cca54c3dc253f9b84c5433f901d  ex-30-synthesis.md
```
