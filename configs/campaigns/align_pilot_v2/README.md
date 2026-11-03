# ALIGN pilot 3 (non-claim)

Generate with `python3 scripts/align_pilot_kit.py`; verify with `--check`.
Protocol: `docs/align/pilot_protocol_v2.md`. Prepare/desk:
`scripts/align_pilot_session.py` (desk accepts `--compare-session <pilot2>`).

24 members: A thinking-on 12 x 4096, then C template-default 20 x 2048;
2 pairs x 2 conditions x 3 repeats, hint on, cap 40960, episode prefix cache
on throughout. Pair order alternates each repeat; condition order alternates
within each pair. Midpoint after A; idle 300 s. Fresh process per member.

Specs equal pilot2 A/C except prompt_cache; seed remains 1 in every repeat.
Repetition flags observe only. Thermal/contention eligibility is unchanged.
Sizing is a transferred planning bound, not hardware validation. Read its
conditional cache derivation before freezing a span. Rehearse first.

`registration/derive_sizing.py --pilot-session <pilot2 root>` derives receipts
without model work. `derive_identity_pins.py --runtime-python <measurement
python>` hashes local files without loading MLX. Generation preserves verified
Mac identity pins and refuses changed inputs instead of silently replacing them.
