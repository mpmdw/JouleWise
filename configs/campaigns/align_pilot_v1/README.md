# ALIGN pilot 2: capability screen (non-claim)

Generate with `python3 scripts/align_pilot_kit.py`; check with `--check`.
Protocol: `docs/align/pilot_protocol_v1.md`. Prepare/desk:
`scripts/align_pilot_session.py`. No registration, loop.json entry or claim.

Three four-member blocks: 30B-A3B thinking on (4096 x 12), thinking off
(2048 x 20), Next-80B instruct (2048 x 20). Both judge-free task pairs,
both conditions, hint on, one repeat, cap 40960. ABBA / BAAB / ABBA.
Align idle 300 s from cooldown.cap_s. Scaffold unchanged; midpoint after A.

Models are contiguous in the roster. The current campaign still launches a
fresh process and loads/cleans up MLX for each member; grouping does not
implement one persistent load per block. That requires separate authority.

`registration/derive_identity_pins.py --runtime-python <measurement python>`
reads local model files without loading MLX. `derive_sizing.py` records the
pilot-1 member law/scaffold and BYTES rate evidence; long-context transfer,
tool allowance, model overhead transfer and disk remain planning flags.
