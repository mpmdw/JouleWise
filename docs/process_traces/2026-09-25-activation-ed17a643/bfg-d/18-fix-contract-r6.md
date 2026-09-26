# BFG-D fix round 2 (seat round 6): the lead's FIX contract

The one source is the cold ruling BFG-D-PARSER-ESC-01, `15-parser-esc-ruling-source.md`. Implement its §4 grammar (exact final text) and its §6 obligations **R2-1 … R2-7**, exactly as written.

The paired Opus refuter (`16-parser-esc-refuter.md`, Phase 2) raised four MATERIAL additions. None of them reverses the ruling; each tightens it in the ruling's own direction. The lead adopts them as obligations **R2-8 … R2-11**, and the cold Fable final pass will review that adoption:

- **R2-8 (refuter M-1): type-check every recorded property.** The seven recorded-but-not-gated keys are `Amperage`, `Voltage`, `Temperature`, `FullyCharged`, `CurrentCapacity`, `AppleRawCurrentCapacity`, `AppleRawMaxCapacity`, plus `UpdateTime` if it is not already gated. Each must match its expected lexical type. Booleans must be exactly `Yes`/`No`. Integers use the same integer grammar as `InstantAmperage`, with the two's-complement rule where the value can be signed. A wrong type is a probe error, matching A-R5b "a malformed … property is not a pass". Test: the refuter's X8 case and one wrong-type case per key are refused at all four sites; both real captures still pass.
- **R2-9 (refuter M-2): freeze the grammar for the Revision-5 epoch.**
  - Add a test that pins the grammar. It pins either a sha256 over the structural-stage source text (a named function, extracted by `inspect.getsource`) or a sha256 over the committed grammar corpus plus its expected verdicts. A comment that explains the freeze sits next to the pin.
  - Add one sentence to the module docstring: any change to the structural stage while the Revision-5 epoch is unissued must, in the same PR, replay every committed Revision-5 verdict with zero `compare_verdict` differences; otherwise it is a registration amendment that needs an owner ruling.
  - Test: mutating the structural stage fails the pin test.
- **R2-10 (refuter M-3): `issue_epoch_continuation` refuses Revision 5 outright.**
  - `derive_record` must refuse any Revision-5 session before it reads any member (before its first `_read_member_evidence`), exactly as R2-2 does for the equivalence tool. Revision 5 registers no continuation branch.
  - The earlier gate becomes unreachable for Revision 5. Keep it for defence in depth only if it stays correct.
  - RED/GREEN test: a Revision-5 fixture with a **passing** committed verdict exits non-zero, writes nothing, and makes zero member reads.
- **R2-11 (refuter M-4, confirmed): every production feeder passes BYTES.**
  - `battery_float.observe` must refuse a `str` stdout. It raises a probe error; it never re-encodes.
  - Every production runner that executes `IOREG_BATTERY_ARGV` captures stdout as bytes, with no `text=True` and no universal newlines, and passes those bytes to `parse`. That covers the night-gate t0 runner, the evidence_night arm and publish runners, the installer, `arm_readiness_evidence_t0`, and the writer.
  - The recorded `raw_stdout_sha256` is the digest of those exact bytes.
  - Tests: for each of the three admission runners (arm, publish, t0), a CR-smuggled output (the refuter's executed case) is refused, and the recorded digest equals sha256 of the raw bytes.

**Rules.**
- For every obligation: RED on `faf0ea01` in a `/tmp` copy, then GREEN. Paste both.
- Never weaken an existing assertion. List every expected-value edit with its before and after.
- Run these to completion and paste their tails: `tests.test_battery_float`, `tests.test_night_gate`, `tests.test_evidence_night`, `tests.test_install_night_agent`, `tests.test_night_agent_install`, `tests.test_arm_readiness_evidence_t0`, `tests.test_run_night`, `tests.test_validate_powermetrics_fiducial_derivation_only`, `tests.test_issue_calibration_acceptance_generation`, `tests.test_calibration_cadence_report`, `tests.test_epoch_continuation`, `tests.test_epoch_equivalence_check`, `tests.test_acc_25g83_rev5`, `tests.test_custody_mode_inventory`, `tests.test_docs_freshness`, `tests.test_gen_state`.
- Pin proof: `git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs` is empty.
- R2-5's sweep table goes in your report. Every row carries file:line, what it reads or decides, the gate it sits behind, and the test that proves the gate. Any ungated row becomes code plus a test in this round, if it is in scope; otherwise report NEEDS_SCOPE.
- Stop rule (ruling §6): if you find the new grammar accepting a structurally wrong output that you cannot close within the grammar as ruled, stop and report. Do not improvise a third parser.
