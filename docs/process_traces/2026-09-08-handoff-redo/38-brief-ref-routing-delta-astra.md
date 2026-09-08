WRITE_SCOPE: []

# DELTA RE-AUDIT — fix round 1 on G2A-CHAIN-ROUTING-01 (gpt-6-astra, read-only)

HEAD = fix-round commit; HEAD~1 = f0fedc91 landing; HEAD~2 = main e4ce8b3b. Packet: `git diff HEAD~1 HEAD`
(7 files, +60/−6). The fix seat claims: B1 `tests/test_check_window_provenance.py` provenance test re-expressed
against the plan-path preflight contract (was pinning the retired `SMOKE_CHECKOUT="$1"` + August literal); B2 desk
Phase A step in SHAKEDOWN-G2-RUNSHEET.md that sets NIGHT_PLAN and derives MEASUREMENT_ROOT/HEAD with /usr/bin/jq
before any consuming block; B3 dated supersession pointers in RUNSHEET.md and 00-verification-notes.md; N1 preflight
run as a program (no-arg → exit 2; head mismatch → named refusal); N2 `--check` prints a FAIL line on a missing
heading; N3 fence-language sentence; the generator test's pinned routing-fence range moved 1516-1580 → 1534-1598
with the doc additions.

Break it: (1) the moved fence range: re-derive the block range independently from the runsheet and confirm the
emitter (`inventory_g2a_shell_blocks`, `expected_ranges`) and the test agree, and that `--check` still refuses a
drifted range; render the chain at night-date 20260910 and diff it against HEAD~1's rendering — the ROUTING BLOCK
must be byte-identical (doc additions must not have changed the emitted chain); (2) B1: does the rewritten
provenance test still guard the intent "the preflight pins exactly one documented argument", and would it pass if
the preflight silently accepted a second positional argument or an env fallback (mutation probe in $TMPDIR)? (3) B2:
run the new Phase A jq step against a real v2 plan (write one with `joulewise.night_plan_writer.write_night_plan`)
and confirm the exported values equal what `_run_chain_once` exports for the same plan; (4) N1: run the two new
subprocess tests and confirm they invoke `preflight.sh` itself (not a split prefix); (5) anything HEAD~1 had right
that HEAD broke; (6) grep HEAD's runsheet, RUNSHEET.md and 00-verification-notes.md for any historical byte
rewrite (git diff must show only additions in the historical regions). Run only the four modules
(`tests.test_check_window_provenance tests.test_preflight tests.test_gen_g2_phase_d tests.test_run_night`). Report
(genre review): `verdict` = {counts, findings} ONLY; header < 8192 bytes; findings with file:line, severity, exact
demonstrating command.
