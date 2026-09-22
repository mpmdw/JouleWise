# A267 fix round 1 — implementation seat report

Worktree `/Users/edr/code/JouleWise-wt-a267-d9990b3c`, branch
`feat/2026-09-22-a267-clock-anchor-v3_1`, base `c5f4f9c6`, head `489b0953`,
tree clean, nothing pushed. All 14 brief items implemented; none skipped.
`joulewise/uncertainty_evidence.py` is byte-identical to c5f4f9c6
(sha256 `b583f35a…4ae8` both sides, `git diff` 0 lines). Files touched: exactly
the five in WRITE_SCOPE (`git diff --stat c5f4f9c6..HEAD`: campaign +259,
sampler +70, three test modules +687, 937 insertions / 79 deletions).

## Per item (file:line at HEAD)

1. **05b B1 residual** — `attestation_timeout_s(protocol)` (campaign.py:579)
   = `max(ATTESTATION_TIMEOUT_FLOOR_S=5, slot_pitch_s − envelope_s − 5)` = 15 s
   under v2; `attest_network_time(out, blocked=None, timeout=…)`
   (campaign.py:604) takes it, `execute` passes it (1107) and journals
   `network_time_attestation_wall_s` per envelope (1113). `TimeoutExpired` is
   its own branch → `asserted`, reason `timed log query timed out after N s`.
   No literal 300 remains. Regressions (test_quiet_predicate_campaign.py:1239,
   1257): a real fake `log` sleeping 5 s against a 0.5 s bound returns in <3 s
   `asserted`/`network_time_unattested`; the bound equals the gap for v2, the
   scaled protocol (floor) and a 700 s pitch; a night whose every query burns
   its whole 15 s bound still spawns all twelve slots at 600+620·i with
   |drift| ≤ 0.02 s and 15 s on each envelope entry.
2. **05b S1** — `TIMED_LOG_HEADER_FIELDS` + `timed_log_has_header`
   (campaign.py:450–457); rc 0 without the syslog header → `asserted`, reason
   `timed log query returned no header` (629). Regression (tests:1284) over
   exhibit D, "", `<html>error</html>`, a bare newline, a headerless entry
   line, and three end-to-end nights. **Kill:** deleting the guard →
   `- authenticated / + asserted`, `FAILED (failures=2)`; restored → `OK`.
3. **05b S2 / 05a N2** — `base = 0 if outcome in {complete,partial} and
   cleanup_proven else 2; return 3 if base == 0 and not restored else base`
   (campaign.py:1165). Regression (tests:1334): executed eight-row truth table
   over outcome × cleanup × restore, asserting outcome document, refusal count
   and code (0,3,0,3,2,2,2,2). **Kill:** pre-fix `if not network_time_restored:
   return 3` → `AssertionError: 3 != 2 : refused (two cleanup_unproven),
   restore failed`, `FAILED (failures=2)`.
4. **05b S3** — `establish_network_time_off` (campaign.py:319) wraps the set
   form; a raise/timeout writes `off = {argv, exit_code: null, stdout: null,
   error, epoch_s, monotonic_s}` before refusing; the 30 s bound is the named
   `NETWORK_TIME_SET_TIMEOUT_S` (39). Regression (tests:1351): fake `sudo`
   sleeping 5 s against a 0.5 s seam → rc 2, one refusal, `calls == []`,
   `off.error` carrying TimeoutExpired, restore still ran.
5. **05b S4, S5** — `restore_network_time` (campaign.py:356): ON receipt goes
   to the sibling `network_time_control.restore.json` (43) whenever the record
   is present but unreadable or not an object; nothing escapes (inner guards
   for the toggle and the write, outer guard for any residual class).
   Regressions (tests:1388, 1414, 1437): five non-dict payloads keep their
   bytes for both verdicts; a raising toggle, a receipt with no exit code and a
   PermissionError on the write each return a verdict; two whole nights whose
   record is corrupted between OFF and the restore still write summary and
   outcome. **Kill:** pre-fix rewrite → 6 red rows, e.g.
   `'{\n  "off": null,…' != '[]\n'`.
6. **05b S6** — `record_attestation` guards the write (campaign.py:706); on
   `OSError` the attestation becomes `asserted`, reason
   `session rewrite failed: …`, and the night continues. Regressions
   (tests:1464, 1485): a read-only envelope directory keeps session.json byte
   for byte with no `.tmp`; a night with every rename refused finishes
   complete, rc 0, twelve unattested, zero retained.
7. **05b S7** — test-only. `test_whitespace_variants_of_the_off_stdout_refuse_
   with_exit_three` (test_sample_quiet_predicate_evidence.py:1491): four
   strip-equivalent variants each leave provenance `None`, refuse before any
   child and exit 3; ruled bytes still admitted. **Kill (not required, shown):**
   `stdout.strip() != EXPECTED.strip()` → `FAILED (failures=4)`.
8. **05a S1** — test-only; both unresolved v3.1 regressions
   (test_uncertainty_evidence.py, envelope-07 backstop and the 6 ms placement
   refusal) now assert `clock_anchor_method`, `schema_version == "p2-038.4"`
   (literal) and `caps == dict(V3_1_CAPS)`. Also 05a N6: the envelope-07 test
   is renamed `…trips_the_backstop…`.
9. **05a S2** — test-only
   (test_sample_quiet_predicate_evidence.py, `ExactTilingTests`): the frame the
   interior opens inside is split into two exactly abutting tiles and
   `rail_sum_w` dropped from the 1 ns head → `span_mismatch False`,
   `coverage_ns` 480 s, `combined_w` complete, `rail_sum_w` = 480e9 − 1,
   interior partial. **Kill:** 1 µs tolerance on the rail comparator →
   `AssertionError: True is not false`.
10. **05a S3** — the SIGTERM-during-settle night now asserts the OFF receipt
    exists with the exact ruled stdout and exit 0, and that the fake clock read
    0.0 (< settle_s) at the toggle, with ON after settle_s. **Kill:** toggle
    moved after the settle → `unexpectedly None : the night died inside the
    settle with no OFF receipt`.
11. **05a S4** — harness gained `tolerate_raise`; `cleanup_record` patched to
    raise → the control record must already carry ON exit 0 (tests:1507).
    **Kill:** restore ordered after `cleanup_record` → `unexpectedly None : the
    restore did not run before cleanup_record`.
12. **05a N1 / 05b N2** — `integrate(frames, start_ns, end_ns,
    uncertainty_ns=0)` (sampler:332) enforces integers (TypeError);
    `integrate_seconds` (314) is the single float door (endpoints to nearest,
    uncertainty outward); `reduce_interior` passes its own integers (436);
    `collect` uses the adapter (1009). **Callers, exhaustively:**
    `reduce_interior` and `integrate_seconds`; `integrate_seconds` is called
    once, from `collect`'s round loop; the six test call sites moved to the
    adapter. Regressions (sampler tests, `IntegerWindowTests`): a 12.345 s
    interior on a tiled fixture covers 12_345_000_000 ns exactly and completes;
    float args raise TypeError; 1 ps uncertainty buys 1 ns. **Kills:** restoring
    the float round trip → `12344999936 != 12345000000`; `ceil`→`round` in the
    adapter → `0.0 not greater than 0`.
13. **05a N4** — the attestation block moved above the busy-core join and the
    join reads both gates (campaign.py:878–880). Regression: envelope 05 with
    the 99-core excursion **and** a slew → excluded by name, retained 11, its
    own entry still reports 99, clean-machine and overall maxima 0.01.
    **Kill:** `if not hard` → `AssertionError: 99 != 0.01`.
14. **05a N3 / N5 / N6, 05b N1 / N3** — `timed_log_window_epoch_s`
    (campaign.py:459) and `window_argv_epoch_s` on the attestation (642); the
    argv formatting moved inside the guard with a finiteness check and
    `OverflowError` (620–639). Glosses: "sudoers slice" built at first use
    (campaign.py:24–28), "ulp" expanded at first use (sampler:274). Regressions:
    tests:1526 (both windows recorded, each argv value the floor of its float
    counterpart, span 602 s) and tests:1549 (NaN, inf, 1e300, 1e18 → `asserted`,
    `capture window unavailable`, no traceback); `EndpointRoundingTests`
    (sampler tests:1385) pins round-to-nearest. **Kill:** `round`→`int` on the
    endpoint → `1000000000000 != 1000000000001`. N6 landed with item 8; the
    `ceil` kill landed with item 12.

## Test counts and exact tails

Before (c5f4f9c6): `Ran 177 tests in 49.983s / OK` (three brief modules).

```
$ env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest \
    tests.test_uncertainty_evidence tests.test_sample_quiet_predicate_evidence \
    tests.test_quiet_predicate_campaign
----------------------------------------------------------------------
Ran 224 tests in 55.218s

OK
```

Both commands above were executed at `62412ee6`; the only later commit,
`489b0953`, is a docstring rewrap. The first command was re-executed at the
final head `489b0953`: `Ran 224 tests in 55.974s / OK`.

```
$ env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest \
    tests.test_night_gate tests.test_run_night tests.test_gen_evidence_night \
    tests.test_night_agent_install
----------------------------------------------------------------------
Ran 392 tests in 742.268s

OK
```

## Commits (`git log --oneline c5f4f9c6..HEAD`)

```
489b0953 A267 fix round 1: rewrap the record_attestation docstring after item 6
62412ee6 A267 fix round 1 item 14 (05a N3, 05a N5, 05b N1, 05b N3): the record says what was queried
c1bfcdd8 A267 fix round 1 item 13 (05a N4): an unattested envelope never feeds the clean busy-core diagnostic
5090a722 A267 fix round 1 item 12 (05a N1, 05b N2): integrate takes integer nanoseconds
e9ea447b A267 fix round 1 item 11 (05a S4): the restore is pinned as the first action of the finally
0f67e0cf A267 fix round 1 item 10 (05a S3): the OFF toggle's placement before the settle is pinned
dbe022c0 A267 fix round 1 item 9 (05a S2): the per-rail coverage comparator has its own kill
a655eecb A267 fix round 1 item 8 (05a S1, and 05a N6): the unresolved v3.1 records carry their identity
fbe481c2 A267 fix round 1 item 7 (05b S7): the collector-side OFF comparator is pinned to byte equality
b10e8bd2 A267 fix round 1 item 6 (05b S6): a failed session rewrite asserts the envelope, not the night
db5d0688 A267 fix round 1 item 5 (05b S4, S5): the restore protects the control record and never raises
6505220e A267 fix round 1 item 4 (05b S3): an OFF that times out or raises still leaves its receipt
0bb7bf29 A267 fix round 1 item 3 (05b S2, 05a N2): a refused night returns 2 whatever the restore did
8ec9234b A267 fix round 1 item 2 (05b S1): an empty log show result is asserted, never authenticated
d94d51f2 A267 fix round 1 item 1 (05b B1 residual): the clock query is bounded by the gap it runs in
```

## Deviations (all within the dictated shapes; flagged for the magistrate)

- **D1 (item 14, 05a N3 — reading of the brief).** The sentence names
  `window_epoch_s` as the whole-second values with `window_argv_epoch_s` as the
  float union window. I implemented the opposite assignment: `window_epoch_s`
  stays the float union window and the NEW `window_argv_epoch_s` holds the
  whole-second epochs parsed back from the argv strings. Reasons: the key name
  "argv" is truthful only of the argv's own values; 05a N3's cure asks for "the
  argv strings' epoch equivalents" to be recorded, i.e. the new thing; and two
  already-ruled regressions pin `window_epoch_s` to `attestation_window(stamps)`
  (A269 regression 5) and to `[999.0, 1601.0]`. The swap would have broken both.
- **D2 (item 14, 05a N5 — "pulse").** No occurrence of "pulse" exists in the
  sampler or the campaign module (case-insensitive); its only use is the frozen
  deriver's module comment, which is out of scope. Nothing to gloss; "ulp" and
  "sudoers slice" were.
- **D3 (item 1 — residual the brief's own arithmetic leaves).** The dictated
  bound (15 s under v2) coexists with a teardown budget of 15 s inside a 20 s
  gap, so a slot that spends both overruns the gap by 10 s. Implemented as
  dictated and documented in `attestation_timeout_s`: the overrun is then caught
  by the 2 s start-drift abort at the next spawn — REFUSED at a named abort
  rather than silent drift. If the magistrate wants the pair to fit the gap by
  construction, the bound should be `gap − cleanup_budget_s(protocol)`.
- **D4 (item 5).** An ABSENT control record (a refusal before the toggle, e.g.
  `window_budget_exceeded`) still opens the main record rather than the sibling:
  there are no bytes to protect, and an existing A269 regression reads
  `network_time_control.json` on exactly that path.
- **D5 (item 4).** The failed OFF is re-raised as
  `ValueError("network time OFF not established: TimeoutExpired: …")`, so the
  executor's except tuple and the refusal wording are unchanged.
- **D6 (item 2, test fixtures).** The executor harness's default `timed_log`
  changed from `""` to the syslog header line, since an empty body can no
  longer authenticate; `log_sha256` in the default-night assertion follows.
- **D7 (item 6).** `record_attestation` still returns False without an
  `asserted` reason when the SESSION cannot be read (pre-existing path); the
  reason is set only on the rewrite failure, as dictated.
- **D8 (item 12).** `integrate` enforces `type(x) is int` and raises TypeError.
  Not spelled out in the brief, but it is what turns the renamed signature into
  a contract; the adapter is the only float door.

## NEEDS_RULING

None. No item required touching `joulewise/uncertainty_evidence.py` or leaving
WRITE_SCOPE.

## Unfinished

None. Items 1–14 are implemented, each with its pinning regression; mutation
kills recorded for the five required items (2, 3, 5, 9, 12) and additionally
for 7, 10, 11, 13 and 14.
