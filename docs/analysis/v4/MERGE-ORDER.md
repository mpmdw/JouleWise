# v4 merge order: r11 first, engine second

2026-11-08. This is a lead ruling on R23j item 4, option (c).

## The rule

1. `align/2026-11-08-v4-r11` lands on `main` FIRST.
2. The engine line (`engine-r23*`) lands later. On every conflict, r11's versions win for:
   - `joulewise/align/apple/v4_cadence.py`;
   - the whole v4 arm stack, including `scripts/align_v4_session.py`, `scripts/align_v4_kit.py`, `joulewise/align/apple/v4_registration.py`, `docs/align/pilot_protocol_v4.md` and their tests.

   The engine's copies of those files are never merged over r11's.

## Why

The engine runs offline analysis from its own pinned commit and never arms. Its older arm stack is therefore inert. Making r11's `v4_cadence.py` byte-identical here was not possible: that file needs r11's arm clock, meter-reader wiring and `joulewise.timing_receipts`. Only the calibration predicate is shared.

## Guard

`tests/align/test_v4_calibration_port_pin.py` pins, by sha256, the source of:
- `calibration_stop`;
- every helper it calls (`slot_of`, `_validated_rulings`, `_is_digest`);
- every module constant it reads;
- `scripts/align_v4_kit.valid_lead_signature` and `UNSIGNED`.

The pins hold the sources as they are at r11 `bbfccb70ab993c395f254058694906610547651d`. A second test checks that the pin covers every module name `calibration_stop` reaches. If r11 changes any pinned source, the test fails, and the engine must re-port it before landing.

The engine's own R22-2 bar predicate is `engine._structural_bar`, ported from r11's `scripts/align_v4_next_arm_packet.py` (`WindowRecord.structural_bar`). It lives in the engine and is not part of this pin. R23j makes it stricter than r11: declared bars must be reproduced.
