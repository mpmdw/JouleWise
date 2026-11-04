# ALIGN pilot 4 (non-claim)

Generate: `python3 scripts/align_pilot_kit.py`; verify: `--check`.
Protocol: `docs/align/pilot_protocol_v3.md`. Session: `scripts/align_pilot_session.py`.
28 A-only members: 2 pairs x 2 conditions x seed blocks 1,12,13,14,15,16 + seed1 replay per cell.
Pilot-7 anchors: the seed-1 block (ordinals 1-4) and the four seed-1 replays (9,14,19,28)
repeat pilots 4-6 at the same ordinals; seeds 12-16 are new trajectories.
Qwen3 thinking sampler 0.6/0.95/20/0, per-turn SHA256 64-bit reseed; guard120s.
Seed-law task identifiers are exactly `shade/spam_filter_update` and
`shade/bank_transfer_2` (the task's task_pair attribute, not task_kwargs.task_pair).
Every member's expected_episode_seed is pre-registered in collection_plan.json.
Cache episode_prefix, cap40960, 12x4096, hint on, idle300s, repetition observe-only.
Odd seed-block ordinal: spam/benign,bank/sabotage,spam/sabotage,bank/benign; even reversed.
Replays after seed blocks2,3,4,6, all at least six members after originals.
25 scaffold members and calibration bracket unchanged. Hardware rehearsal required.
`registration/derive_sizing.py --pilot-session <pilot3 root>` derives file-digested
receipts without MLX. Identity pins retain verified Mac hashes and package readings.
Sizing transfers remain PROVISIONAL; harvest+desk allowance90min, no claim power.
The allowance comes from pilot3 89min (24 members) and pilot2 90min (12 members);
the scaffold sets the time, not align count. Bank expected120s is a lower bound
for a guard-limited episode unless it finishes first; an admitted turn completes.
`desk --no-harvest` writes inspection/ under the supplied session root: point it
at a copy of an archived session.
