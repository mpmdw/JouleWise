# Charge — addendum to cold gate ACCEPTANCE-25G83-01: the R-ACC-1(b) desk replay failed its literal criterion

Assembled 2026-09-24 ≈06:20 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## Background in plain words

The ruling (`ex-20-acceptance-ruling.md`, §3 item 1(b)) made a desk replay the gate for protocol v4 (a 2.0 s calibration pulse). The replay applies the production detector's interior rule at the commanded pulse times over the 24 archived 09-19 captures. PASS required two things:
- under v3 geometry (1.0 s pulse, 0.5 s interior), it reproduces every recorded `no_plateau_interior_intervals` miss and no other;
- under v4 geometry (1.5 s interior), it produces zero misses in 24 × 59 pulses.
"If the deterministic replay fails, stop and return to the council."

A Sol seat ran it (`ex-34-replay.py`, `ex-34-replay-results.json`, `ex-34-replay-README.md`, report `ex-33b-replay-seat-report.md`):
- **v4: zero misses in 1,416 pulses.**
- **v3: exact match on 22 of 24 captures.** The two mismatches, n1-d07 and n1-d10, have `recorded_fit_count` 0 and recorded reasons `clock_anchor_unresolved`, `not_all_pulses_detected` and `pulse_count_below_protocol:0!=59`. The production detector bypassed pulse fitting after the anchor failure, so their recorded miss lists are empty because nothing was recorded, not because no miss occurred. The replay finds v3 misses 13, 52 (d07) and 24, 56 (d10) there.

The seat stopped, as ruled. The magistrate bench-checked the two captures' recorded fields in `results.json` and takes no position.

## Questions

- **J1.** Does the gate PASS, FAIL, or need a different text given the two anchor-bypassed captures? If it needs a different text, give the exact criterion and apply it to the exhibits.
- **J2.** Does the replay show anything else about the mechanism or about v4, for example the anchor failures as a separate yield factor (2/24), that R-ACC-2's futility or window counts should reflect?
- **J3.** Should the jittered r6 diagnostic (ex-26 D1; ruled diagnostic-only) still run?
- **J4.** Anything else.

Give final exact texts. Tier BLOCKER / MATERIAL / NIT.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Reading the archived captures under `/Users/edr/night-archive` is allowed, and so is re-running `ex-34-replay.py` against them in a `/tmp` copy of your worktree.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
b8e5a98de55f8622f4fe5754e3368cbc2955b3de410b3ac77450734034ee1e8f  ex-20-acceptance-ruling.md
5cf73974c28b76823f34f2c1fbb1e2b225549e395ef8f1784750838a8a0fbb3a  ex-33b-replay-seat-report.md
d9573d1ff6a2d64bdb6ea6ab1bac3230d3f2205e9d87de9a6239ffeba30dc724  ex-34-replay-README.md
64404f6b93f6bd8b55c99efbd9c31592ddc8a33175ae3eaf82228f5da039c677  ex-34-replay-results.json
1c41fa89e9c771360a640ec93aa345f6d598ad0d9765d1407b0c292f14ccb700  ex-34-replay.py
```
