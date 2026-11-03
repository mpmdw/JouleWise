# ALIGN pilot 4 (non-claim)

Generate: `python3 scripts/align_pilot_kit.py`; verify: `--check`.
Protocol: `docs/align/pilot_protocol_v3.md`. Session: `scripts/align_pilot_session.py`.
28 A-only members: 2 pairs x 2 conditions x seeds1-6 + seed1 replay per cell.
Qwen3 thinking sampler 0.6/0.95/20/0, per-turn SHA256 64-bit reseed; guard120s.
Cache episode_prefix, cap40960, 12x4096, hint on, idle300s, repetition observe-only.
Odd seed order spam/benign,bank/sabotage,spam/sabotage,bank/benign; even reversed.
Replays after seed blocks2,3,4,6, all at least six members after originals.
25 scaffold members and calibration bracket unchanged. Hardware rehearsal required.
`registration/derive_sizing.py --pilot-session <pilot3 root>` derives file-digested
receipts without MLX. Identity pins retain verified Mac hashes and package readings.
Sizing transfers remain PROVISIONAL; harvest+desk allowance90min, no claim power.
