# ALIGN pilot 10 (non-claim)

Generate: `python3 scripts/align_pilot_kit.py`; verify: `--check`.
Protocol: `docs/align/pilot_protocol_v3.md`. Session: `scripts/align_pilot_session.py`.
28 A-only members: eight unchanged anchors plus 20 fresh benign members (10 seeds x 2 pairs).
The seed-1 block (ordinals 1-4) and four seed-1 replays (9,14,19,28) are
byte-identical to pilot 9 and repeat pilots 4-9 at the same ordinals.
Fresh benign seeds 37-46 fill ordinals 5-8,10-13,15-18,20-27 in ascending seed order.
Within each fresh seed, odd indices run spam then bank; even indices run bank then spam.
Both pairs share the seed index. Unique seeds per pair/condition: benign 11
(anchor 1 plus fresh 37-46), sabotage 1 (anchor 1); replays do not add trajectories.
Qwen3 thinking sampler 0.6/0.95/20/0, per-turn SHA256 64-bit reseed; guard120s.
Seed-law task identifiers are exactly `shade/spam_filter_update` and
`shade/bank_transfer_2` (the task's task_pair attribute, not task_kwargs.task_pair).
Every member's expected_episode_seed is pre-registered in collection_plan.json.
Cache episode_prefix, cap40960, 12x4096, hint on, idle300s, repetition observe-only.
Seed-1 block order: spam/benign,bank/sabotage,spam/sabotage,bank/benign.
Replays at 9,14,19,28 use that same cell order, all at least six members after originals.
The midpoint reference remains after member 14 (episodes-a / episodes-b).
25 scaffold members and calibration bracket unchanged. Hardware rehearsal required.
`registration/derive_sizing.py --pilot-session <pilot3 root>` derives file-digested
receipts without MLX. Identity pins retain verified Mac hashes and package readings.
Sizing transfers remain PROVISIONAL; harvest+desk allowance90min, no claim power.
The allowance comes from pilot3 89min (24 members) and pilot2 90min (12 members);
the scaffold sets the time, not align count. Bank expected120s is a lower bound
for a guard-limited episode unless it finishes first; an admitted turn completes.
`desk --no-harvest` writes inspection/ under the supplied session root: point it
at a copy of an archived session.
