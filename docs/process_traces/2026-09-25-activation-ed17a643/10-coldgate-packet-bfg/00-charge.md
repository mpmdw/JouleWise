# Charge — cold gate BATTERY-FLOAT-01: rule the design, split and registration addendum for Ed's binding battery-float directive (#421)

Assembled 2026-09-25 ≈14:55 PDT by the resident magistrate (Opus 5.5, activation ed17a643). Nothing is armed. The next window (W1, derivation window one of registration Revision 5) is held on this ruling.

## Background in plain words

Ed changed the laptop's charge limit from 80 % to 100 % today, and the battery has been charging on AC all afternoon. Ed's directive #421 (ex-00; binding) makes a battery-float check mandatory for every measurement window. It must pass at arm and immediately before publication/t0, and at harvest a window with any charging slot is confounded and not used. More generally, anything germane to the truth of a number is mandatory. Today no slot records charge state (ex-03, F2), so the harvest half cannot be discharged, and W1 waits.

Two blind seats designed the lane from one brief (ex-01): Sol 6.0 xhigh (ex-02-seat-sol) and Astra 6 high (ex-02-seat-astra). The magistrate's synthesis and proposals P1–P5 are ex-30. All of these are arguments before you, not authorities. Ed's standard: "preventing bad science, not progress on the paper when models agree".

## Questions

- **B1 (design).** Verify the seats' load-bearing code claims yourself at `origin/main` (`c6814dd8`): the C3 site and its reason registries; that `SAMPLERS` sits in a pinned estimator-code path; the derivation writer's sampler lifetime and artifact hashing; the issuer's dry run and `_select_members` skipping of non-valid slots; and the scored reducer's `_check_window`. Then AFFIRM or amend A1–A8 in ex-30. Name anything wrong or missing, especially any caller that could bypass the consumer, and any way a battery check could itself perturb a measurement.
- **B2 (split).** Rule S1 against the magistrate's P1: one PR, two PRs by layer, or two PRs by window kind. State exactly what must be merged before W1 may arm, and what must be merged before any non-derivation window may arm.
- **B3 (registration).** Is an addendum needed before W1? If so, issue its exact text, amending P2 or replacing it. Rule S2, the fate of a confounded window: halt, or one replacement with a bound. Rule the count handling, and whether the addendum lands as its own labelled amendment after the seal PR #418 merges as ruled.
- **B4 (threshold physics).** Rule P3. Is ≤ 200 mA an adequate screen for powermetrics-only derivation windows? What must hold before a wall-meter window?
- **B5 (W1 frozen calibration plan).** Rule P4.
- **B6.** Anything the seats and the synthesis all missed.
- **B7.** Issue **"Battery-float rulings (final texts)"**, executable without choosing: the predicate and parser rules; the refusal codes; the insertion sites per PR; the record schema field names; the consumers; the test obligations (defect-shaped, production call sites); the addendum text; the W1 arm prerequisites in order. Add a plain summary of at most 8 lines for Ed.

## Constraints on the judge

- Work as one non-interactive session in the foreground. Start no background tasks, watchers or subagents. Ending before the ruling file exists is a protocol failure. Budget about 30 minutes of wall time; anything you could not run is marked NOT EXECUTED.
- Read-only. Never run `sudo`, `launchctl`, `powermetrics`, the installer or any model inference. You MAY run `ioreg -r -c AppleSmartBattery` and `pmset -g batt`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, `~/Library/LaunchAgents` or `/Users/edr/night-custody/measurement`.
- Desk Python and focused unit tests are allowed; the discovery suite is not.
- Write only the ruling file `20-coldgate-fable-bfg-ruling.md` in this packet directory.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory. Do not read any `docs/process_traces` file outside this packet, except those the exhibits cite by path.
- Start the ruling with a contamination disclosure: everything loaded besides this packet.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`, sha256 `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.

## Exhibit manifest

```
3b03310a691e86859b8ac097dd6c5a0f5768e0c2ff701ad3fa965f64be256617  ex-00-directive.md
95ae7189adace6b87bc092ccb9f315620216de866893b576acf1c299a4cf70cb  ex-01-seat-brief.txt
2dc90dd32272efc14f5df9818d308c8feaa2793606b8e8c51ef0d89717250aeb  ex-02-seat-astra.md
39e63e8f3e231d617b99959a9a9116807bad9a151ce8676c354a4ec27aa4d835  ex-02-seat-sol.md
1927fbe98d7240d27de1156ca8931d25257080cf3cb328dad49e713970ca2e3f  ex-03-w1-arm-scripts-report.md
9497c832606d5cdd12b5ca816ed1ddbee6264771d98d8d642f9bf6fa1d96a0c6  ex-30-synthesis.md
```
