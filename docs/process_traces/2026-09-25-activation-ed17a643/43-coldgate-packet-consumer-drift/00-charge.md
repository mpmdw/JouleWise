# Charge: cold gate CONSUMER-DRIFT-ESC-01. Rule the structural cure for battery-verdict consumer drift in BFG-D.

Assembled at about 00:50 PDT on 2026-09-26 by the resident magistrate (Opus 5.5, activation ed17a643). Nothing is armed.

**Why this gate is required.** Rule 11 makes a cold gate mandatory for a third fix round on the same defect. The standing escalation rule also applies: the same failure signature has now appeared in three consecutive rounds.

## Background

BFG-D is at `origin/feat/2026-09-25-bfg-d` `3e984ecc`. Its obligations come from three sources: final texts v1.1 (BATTERY-FLOAT-01), harvest-verdict obligations v1.1 (HARVEST-VERDICT-FINAL-01), and the BFG-D-PARSER-ESC-01 plan. All of them are on the branch under `docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/`.

Every consumer of a committed battery verdict must do three things: load the verdict with the registration digest, replay it from raw bytes, and compare the replay with the recorded verdict. Any failure is a refusal, never an exclusion.

The count-only dry run is the desk decision Revision 5 uses to stop or continue W1 and W2. In three consecutive rounds it handled unnamed computed sessions differently from the issuer (`_prepare_candidate`):
- **Round 1 (FX-6).** An omitted non-pass session was reported as admissible.
- **Round 2 (R2-3).** A `NoRecord` failure was swallowed.
- **Round 3 (ex-03 F1, executed).** A computed session's record is loaded but never replayed or compared. With W1's raw bytes altered and only W2 named, `check` returns 0 and "admissible", while `prepare-candidate` refuses.

Two blind consults both propose one sole authenticated-verdict API in `battery_float.py`, one shared computed-set collector, and a mechanical AST test that bans direct use of the primitives: ex-01 (Sol 6.0 high) and ex-02 (Astra 6 high). They differ in detail, for example on the order of replay and load. Treat both as arguments, not authorities.

The same deltas cleared the parser (no BLOCKER in either family) and all other closures.

## Questions

- **K1.** Verify F1 yourself at `3e984ecc`. Grep every caller of `load_committed_verdict`, `validate_window` and `compare_verdict`, and every place that derives the computed session set S. Is the drift real, and is it anywhere else?
- **K2.** Rule the cure as exact final text:
  - the function name and signature, its return type and its refusal type and codes;
  - the order of load, replay and compare. Note that obligations v1.1 §4.4 fixes an order; say whether that order stands;
  - the single collector for S, and exactly which consumers call it;
  - the AST or import-graph guard and its allowlist, where the producer `verdict_record` may call `validate_window`;
  - the tests, which must include regression tests for all three rounds' defects.
- **K3.** Say whether anything else in BFG-D should be held to this pattern before the final pass. Give a plain summary for Ed of at most 5 lines.

## Constraints

- Work in one foreground session. Start no background tasks and no subagents. Ending before the ruling file exists is a protocol failure. Budget about 25 minutes.
- Read-only apart from /tmp scratch space, which you must remove at the end. Never run sudo, launchctl, powermetrics, the installer or model inference. Focused unit tests only; no test discovery.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` or `~/Library/LaunchAgents`.
- Write only `20-coldgate-fable-consumer-drift-ruling.md` in this packet directory.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory. Do not read `docs/process_traces` files outside this packet, except the BFG-D directory on the branch and packets 10, 41 and 42 in this activation directory.
- Begin with a contamination disclosure.

Charter: `docs/process/coldgate_charter.md` sha256 `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.

## Exhibit manifest
```
d7ea3defb8b1551f03959bd868219fe904bf924e82f1fb1981f84b573332870f  ex-00-consult-brief.txt
a9f4dd351aa001d45dde34f885e9d65278df677f3add8a47e92244c91b2b9446  ex-01-seat-sol.md
ef9cab2d2a76e988bfcf1063b691269c28a4ec9b38f875b0f19d8dbda939067c  ex-02-seat-astra.md
0e561b913c5a18d53ccbf2c6381ad22f028e417368f85c802482c8d7e3953f8a  ex-03-sol-delta-r2.md
70e3175e00341b8a915ab17402393e0dfbe93644acfae6ffd3e2edce5723ac57  ex-04-astra-delta-r2.md
```
