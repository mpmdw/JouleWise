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

`tests/align/test_v4_calibration_port_pin.py` audits `calibration_stop` in
`v4_cadence.py` and `valid_lead_signature` in `scripts/align_v4_kit.py`. The
audit follows every module-scope name the pinned functions read, at call time
or def time: helpers, constants, imports such as `re`, and any shadowed
builtin.

- **Pinning.** Each reached name must have exactly one module-level binding.
  That statement is pinned by sha256 of its full source lines, including
  decorators and anything else on those lines. The pins were computed with the
  same audit on the files at r11 `bbfccb70ab993c395f254058694906610547651d`.
- **Refused drift paths:**
  - a second binding: assignment, augassign, subscript or attribute mutation,
    `del`, import, or rebinding def or wrapper;
  - a `global` or `nonlocal` declaration of a reached name;
  - `globals()`/`vars()` keyed by a reached name, or `setattr`/`delattr`;
  - module-level `exec`/`eval`/`compile`.
- **Mutation witnesses.** Each of these fails the test:
  - an added decorator, including Sol's `@lru_cache()`;
  - `CAL_TARGET_PER_PAIR += 1`;
  - an appended or same-line `CAL_WINDOWS += 1`;
  - `calibration_stop = wrapper(calibration_stop)`;
  - a helper redefinition;
  - global, `globals()` and `setattr` rebinding;
  - a shadowed `len`;
  - a `re` import alias;
  - `del`;
  - a value change;
  - module `exec`.
- **What it does not pin.** An unrelated edit to r11-owned triage code passes
  the audit, as intended.

If r11 changes anything reached, the engine must re-port it before landing.

The engine's own R22-2 bar predicate is `engine._structural_bar`, ported from r11's `scripts/align_v4_next_arm_packet.py` (`WindowRecord.structural_bar`). It lives in the engine and is not part of this pin. R23j makes it stricter than r11: declared bars must be reproduced.
