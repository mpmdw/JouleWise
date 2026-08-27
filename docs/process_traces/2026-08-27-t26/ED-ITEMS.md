# Items that need Ed (running list, T26; batched so Ed sees ONE list)

Updated 2026-08-27. Nothing here blocks agent work; each blocks a specific
gate named beside it.

## Transaction gates (from the T25 checkpoint, unchanged)
1. Venv relock at `-20260813` (runbook §1.1; ~10 min).
2. Permission hygiene per `w6-prompt-inventory.md` NEEDS-ED.
3. Notification cadence: immediate (recommended) or batched.
4. Transaction night — now the first free night AFTER W-10 (D-157) and
   W-11 (D-158) merge and estate 11 is green; ~2026-08-29/30.

## BLOCKING THE MINT — one two-line edit only your hands can make (W-10, PR #209)
0. The reviewed pinset `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`
   row `d117_contrast_qwen25_1p5b_vs_7b_v3` pins the OLD pack bytes; W-10
   regenerated the `_v3` pack, so the mint refuses `histsem_pinset_mismatch`
   at `arm_readiness.py:6901` before the new admission check runs. The
   pinset has no update lane BY DESIGN (byte tripwires; the harness
   classifier refused both the agent and the magistrate). On branch
   `fix/d139-a2-gamma-families` (worktree `/Users/edr/code/JouleWise-wt-s8-d139-families`):
   (a) in that JSON, change that row's `current_pack_sha256` from
   `0d07194143702b266267f0faa7b051695ffb5e1c56dc7a69d0b2dca8aaa883ef` to
   `6986bb496aed2b2b0329f79e1c2877ff4cb0ab537ca1be26ff7b7d65bb121d0a`
   (recomputed independently by the magistrate with
   `committed_pack_tree_sha256` at head `2e49910e` — recompute again if
   any later commit touches that pack);
   (b) in `tests/test_receipt_histsem.py:33` set `PINSET_SHA256` to the
   SHA-256 of the edited JSON file (`shasum -a 256 <file>`).
   Then `python -m pytest -q tests/test_receipt_histsem.py`, commit, push.
   Everything else on #209 is done and gauntleted (head `9c8d5632`).
   HAZARD: the digest covers every committed blob under
   `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/`; NO commit may
   touch that directory before the pin lands (a stray `__pycache__` there
   also makes the digest refuse — clean it first). Recompute with
   `committed_pack_tree_sha256` if in doubt.

## New from the S9 ruled-not-installed sweep (PR #210, SHORTLIST.md)
5. **S9-05 (NEEDS-RULING, ruled number):** the live calibration screen
   constant is `0.009724` while D-125 rules a `0.010818` floor. Either
   the code moves to the ruled number or D-125 is amended — a ruled-number
   change is Ed's. Gates the mint.
6. **S9-03 (ED + CODE):** the gamma prefill prompt is a *candidate* where
   it is owned and *ratified* where it is consumed; Ed ratifies the prompt
   (one word) and the code then pins it. Gates the mint.

## From T0-UNATTENDED-01 (S2, PR #212) — five hands items, verbatim from the stream
Gate unattended WINDOWS, not the `_v4` mint night.
10. D-127 sudoers install/exercise — pre-existing; blocks every window
    regardless of design.
11. ~2 min privileged anchor positive control during the supervised
    rehearsal sitting (closes the detector-inertness risk).
12. Ratification: D-127.1 (scope closure — retire the operator
    `-getusingnetworktime` read; NO new privileged command) and the ruled
    6 h retention. Paste-ready text: `impl/d127-1-proposed-decision-log-delta.md`
    on the PR branch.
13. Exact `setUsingNetworkTime: Off` bytes bench-verified under sudo BEFORE
    the strengthened postcondition gates — a wrong byte refuses every window
    forever; the constant is one line.
14. The supervised rehearsal sitting itself (kernel acceptance item 2).

## Optional but valuable
7. **PIPELINE-SMOKE-LIVE-01 — now the ONLY end-to-end clean proof (D-160
   R-2):** ~20 minutes at the machine the evening before the night — a
   real, tiny, quarantined family generation (not smoke-scoped), real
   telemetry, its own two calibration brackets, `fixed_n = 1`, decode-only,
   one ABBA block, then finalize → analyze-claims at the desk. Zero new
   production seams. A synthetic desk version was ruled impossible without
   relaxing the floor rule; this is the honest path. Strongly recommended
   before the night; the runbook for it is drafted by S10 once the
   bracket-binding producer lands.
8. `~/.local/bin/codex-run-v3`: add `.pytest_cache` to
   `ignored_bytecode_paths` (false exit-77 on every pytest-running Sol run).

## Strategic (no deadline)
9. The +2–5-week model-ladder horizon (see the 2026-08-27 chat answer):
   say the horizon and the `_v5` ladder design consult launches.
