# Block-4 lane X13 (Sol 6.1 high): test changes that must land before the freeze (joined replay D1 and P1)

Worktree: /Users/edr/code/JouleWise-wt-dd5-x13 (branch `lane/2026-10-05-b4-x13` at 013265f6, the integration head with X12a). Scratch /tmp/dd5-x13/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics, systemsetup or Metal.

Background: the joined-replay seat's report is `/Users/edr/night-archive/desk-day-v5/joined-replay/REPORT.md`, with findings D1, D2 and P1. Once the `_v5` packs are frozen, any change to a relevant path, tests included, makes every writer and ARM refuse (`joulewise/arm_readiness.py:5168`). So every test change must be in the head that gets frozen.

1. **D1.** `tests/test_v5_pack_regen.py:24-36` always generates with `--no-preserve-current-frozen-bytes`. Once a pack is frozen, the generators correctly refuse that. Make the test correct in both states:
   - for an unfrozen pack, the current check;
   - for a FROZEN pack, check the 75 s idle from preserve-mode output, or from the committed member configs.

   Never weaken the generator guard. Prove both branches: the unfrozen branch at this head; the frozen branch in a throwaway clone frozen by the joined-replay procedure (REPORT.md step table, or reuse `/tmp/dd5-joined/frozen-suite` read-only: copy it, do not write in it).
2. **P1 and D2.** Land the joined-replay test file `/Users/edr/night-archive/desk-day-v5/joined-replay/test_v5_block4_replay.py` as `tests/test_v5_block4_replay.py`. It replaces the committed version, which breaks once GAMMA is frozen (D2).
   - Adapt it to this head: X12a changed the history, harvest and OFF-receipt code since 6796b8e0, and X12b is changing G1 and G10 in parallel. Keep every stop assertion exact.
   - It must pass in two states:
     - unfrozen at this head: the joined cases skip at the freeze FLAG;
     - frozen, in a throwaway clone with the test landed before the freeze: the joined cases skip at the F1 FLAG `scripts/capture_t0_step.py:491`.
   - The seam list stays the eight physical seams the file names. Do not widen it.

Run `tests.test_v5_pack_regen tests.test_v5_block4_replay` in both states, and report both outputs. Finish in this turn.

WRITE_SCOPE: ["tests/test_v5_pack_regen.py", "tests/test_v5_block4_replay.py"]
