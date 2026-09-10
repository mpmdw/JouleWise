# 74 — Opus execution-lens refutation of seat S2 (`7c4366ec..1e43d1cc`), 2026-09-10 ~11:33 PDT

Verdict: **MERGEABLE AFTER FIXES** (no wrong behaviour; witnessing gaps). Named ten modules: `Ran 450 tests in 753.923s / OK (skipped=7)`.

| id | sev | site | claim |
|---|---|---|---|
| E1 | should-fix | `joulewise/calibration_ledger.py:1656-1670` | assembler claim-order check unwitnessed: deleting `or slot != expected_slot` (claim branch) leaves six modules green |
| E2 | should-fix | `:1674-1690` | same for the finalization branch |
| E3 | should-fix | `:401-448` | `is_governed_open_bracket_extension` "exactly one open session" (`!= 1` → `< 1`) kills nothing |
| E4 | should-fix (report) | seat report | the 76-row production fixture has ZERO session rows; it cannot witness the session layer |
| E5 | nit | `tests/test_calibration_ledger_custody.py:166` | SimpleNamespace session double lacks `next_slot` (2 errors when the old tests run on the new library) |
| E6 | nit | `scripts/reserve_calibration_window_bracket.py:243-244` | only the dry-run payload gains keys; `--execute` payload byte-identical |

Why the three survive: the WRITER's pin check and `SLOT_ORDER_CONFLICT` shadow the reader's recomputation, so the ordering rule is tested once, not twice; the three checks are the authenticating-reader half (defence against a hand-edited ledger file).

Byte-identity witnesses (refuter-run): (i) snapshot dump of the production fixture identical old vs new (76 receipts, 38 observations, head `08456d50…`, reserialize identical; sessions 0); (ii) bracket session opened through the reserve CLI with OLD flags into the same absolute temp path: `cmp` IDENTICAL, sha256 `21ab2c7a900ed6a606f465c643bb1d08d19dd75481d3154e0d152ef1060453ed` both trees; (iii) pre-change `test_calibration_ledger` at 7c4366ec against the new library: `Ran 127 / FAILED (errors=2, skipped=4)`, both errors the E5 double.

A-1 as ruled: `resume_finalize_bracket_session(..., systematic_screen_s: Decimal | None)` at `:5431`; derivation disposition collapses to valid/ordinary-invalid; no terminal-slot auto-abort for a derivation session; `--slot` validated at readiness/validate-slot/resume-finalize through `_declared_slot_shape` with no enumeration (`d05` ACCEPTED, `pre`/`d13` REFUSED `calibration_reserved_slot_mismatch`). No `derivation-only` semantics leaked (grep empty). Footprint exactly the seven declared files. Worktree restored clean (`807f340d…`).

Disposition: fix round 1 launched 11:34 (E1–E5; E6 rides); delta re-audit after.
