# ALIGN v4 series after W1 (Opus build) — PROVISIONAL, NON-CLAIM

Build: `python3.13 -B scripts/align_v4_series.py`. Check: add `--check` (drift only).
Generated from `registration/inputs.json` and `r1_slots.json` of the W1 kit and the
frozen manifest `series_manifest.json` (`joulewise.align.apple.v4_series`).

Order: W1 (existing kit), C1-C8 (calibration; aliases D1-D8, so D1-D3 are C1-C3),
then T1-T3 (locked test). Every C/T window has the default D shape (22 members):
anchors 1-4 (original bytes), early sentinel 5 (replay of W1 ordinal 5; captures R),
16 fresh held-out D members alternating pair by pair (7 benign + 1 sabotage per
pair; sabotage at 9 and 18), late sentinel 22; midpoint after 11. Odd windows start
with spam, even with bank. Held-out seeds per pair start at 2 in kit order and skip
the development indices 1 and 91-99: C1-C8 use 2-65, T1-T3 66-89.

Arm a window: `align_v4_session.py prepare --window C1 ...`, then `install` with a
`--next-arm-triage` packet from `align_v4_series.py packet --ledger L --checks C`.
The arm refuses unless the packet's series binding names this window as the next
frozen window of the ledger it carries (`v4_series.check_arm_binding`), on top of the
R12 triage (`v4_cadence.next_arm_triage`, fixed-8 `calibration_stop`).
`prepare` refuses until R1 has filled the W1 plan and this window's sizing_b5.json
is regenerated from it. Open lead rulings: docs/align/v4/DCT-SERIES-opus.md.
