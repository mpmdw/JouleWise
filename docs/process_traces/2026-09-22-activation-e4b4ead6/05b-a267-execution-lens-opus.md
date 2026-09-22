# A267 QPE01-CLOCK-DISCIPLINE-ANCHOR-01 — EXECUTION-LENS refuter

Head `/Users/edr/code/JouleWise-wt-a267-review` @ `447fd6bf`, never moved or edited. Base exported
with `git archive ecbc0fac | tar -x -C /tmp/a267x/base`; mutations on `cp -r` copies under
`/tmp/a267x`. No sudo/systemsetup/powermetrics/real `/usr/bin/log`: `SUDO`/`SYSTEMSETUP`/`LOG`
rebound to fake executables or `subprocess.run` patched. No `[QUIET-MAC]` measurement.

## §0 Environment and baseline

Python 3.14.7, darwin 25.6.0. `env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest
tests.test_uncertainty_evidence tests.test_sample_quiet_predicate_evidence
tests.test_quiet_predicate_campaign` → **Ran 158 tests in 46.501s / OK**. Frozen protocol:
`envelopes=12, envelope_s=600, settle_s=600, interior_offset_s=60, interior_s=480,
start_drift_max_s=10, sample_interval_s=30, power_interval_ms=100`.

## §1 Probes (expected → observed → verdict)

**P0 deriver (charge 4) — PASS on all four sub-probes.** (a) v3 byte identity:
`/tmp/a267x/derive_dump.py` derives the default-method anchor for all 12 pilot fixtures at both
commits, dumps diffed → **IDENTICAL**; the base tree's own 47 `tests.test_uncertainty_evidence` run
with only `uncertainty_evidence.py` swapped to the head file → **OK**. (b) All 25 unresolved return
sites go through `functools.partial(_unresolved_anchor_v3, method=method)`, and over the 12
fixtures under v3.1 the identity fields are on **all twelve**, across 5 distinct outcomes
(`affine_clock_fit_empty` ×4; `wall_minus_monotonic_span_exceeded` ×1, carrying the rate fields at
37.9 ppm as ruled; `bounded` ×7). (c) Item assignment on the three caps mappings → `TypeError`, and
rebinding `ue.V3_1_CAPS` to a mutated dict does not reach admission. (d) `method="v9"` →
`ValueError: unregistered anchor method identity`.

**P1–P5 chain failure paths** (`/tmp/a267x/head/tests/probe_exec.py`, fake `sudo`/`log`): OFF exact
stdout + exit 1 → `rc=2` refused, refusal written, 0 envelope dirs (PASS). OFF exceeds its 30 s
timeout → `rc=2` refused, restore ran, **`control["off"] is None`** (S3). ON raises OSError in
`finally` → `rc=3`, `complete`, `restored=false`, `on.error` recorded (PASS). Control file
truncated before restore → `rc=0`, restored true, record rewritten `{"off": null, …}` (S4). Control
file parsing to `null` → **`TypeError` escapes the `finally`** (S5). SIGTERM inside
`establish_network_time_off` → `InterruptedError` caught, `rc=2` refused, restore ran (PASS).

**P6 collector exit 3, run live.** `env -u EVIDENCE_NETWORK_TIME_RECORD python3 -B
scripts/sample_quiet_predicate_evidence.py collect … --out /tmp/a267x/refusal-1` → **exit 3**,
`error_class: network_time_provenance`, `power: null`, empty `rounds.jsonl`, no powermetrics spawn.
Fed to the chain: `attest_network_time` → `asserted`, `record_attestation` → `True`, exclusion
`network_time_unattested`, `pilot_summary` excludes without raising. PASS; see N6.

**P7 timed-log adversarial inputs** (`subprocess.run` patched): rc 0 with empty stdout →
**authenticated**; rc 0 with `<html>error</html>` → **authenticated**; rc 0 with `ntp_adjtime`
in/out and no receipt → slew_attested (2); rc 0 with unparseable `Sep 22 …` stamps → slew_attested
(3); rc 1, `TimeoutExpired`, `OSError`, and a session missing `power` → asserted; a stamp `epoch_s`
of NaN → **ValueError escapes**. Scanner: exhibit D → 10 events / 30 marker lines (as
ruled); mangled stamps → 30; an `ntp_adjtime` 2.5 s from a receipt → 2 — grouping degradation is
always fail-closed. The two `authenticated` rows are S1.

**P8 sampler numeric edges (charge 3).** `align_frames` (fake deriver): negative/huge/zero
endpoints tile fine; `NaN` → `ValueError`; `inf` → `OverflowError`; `elapsed_ns == 0` yields a
zero-width frame `integrate` accepts (`parse_frames` refuses `elapsed<=0` upstream). `integrate`
with NaN/inf `uncertainty_s` → `ValueError`/`OverflowError` from `math.ceil` (the `<0` guard does
not screen NaN); an `uncertainty_ns` far exceeding the frame saturates correctly (0.1 s frames at
10 W, u=0.05/0.2/1.0 s → 13.0/15.0/31.0 J = `sum P_i*min(dt_i, 2*eps)`). `reduce_interior` with the
interior past the last frame, or before the first → `partial`, **no crash**. `overlap`'s float
callers ran live (`stationarity()`, `join_load_log`); none is sensitive to its new `int 0`.

**P9 exit-code truth table** (fake executables, real `subprocess`): complete + restored → **0**;
complete + restore failed → **3**; partial (collector rc 1) + restored → **0**; partial + restore
failed → **3**; refused (dead recorder) + restored → **2**, 1 refusal; refused (dead recorder) +
restore failed → **3**, 1 refusal; refused (2× `cleanup_unproven`) + restored → **2**; refused (2×
`cleanup_unproven`) + restore failed → **3**; complete with all twelve `slew_attested` → **0**. The
two refused-but-3 rows are S2.

**P10 mutations** (5 off the seat's list + 3 bonus; full 158-test suite per mutant): M1
`align_frames` endpoint `round()`→`int()` **SURVIVES**; M2 `uncertainty_ns` `math.ceil`→`round`
**SURVIVES**; M3 interior coverage `==`→`>=` **SURVIVES** (equivalent, N4); M6 span backstop
0.015→0.020 KILLED (4); M7 rate cap 25.0→50.0 ppm KILLED (2); M12 attestation window ±1 s→±0 s
KILLED (2); M13 collector stdout compare → `.strip()` **SURVIVES**; M14 placement cap 0.005→0.050
KILLED (2).

## §2 Findings

### BLOCKER

**B1 — the per-envelope `log show` sits synchronously on the inter-envelope critical path A269
exists to shorten.** `joulewise/quiet_predicate_campaign.py:763` calls `attest_network_time` inside
the envelope loop, after `cleanup_groups(budget_s=30)` and before the next slot's
`time.sleep(max(0, scheduled - time.monotonic()))`; line 410 gives the child `timeout=300`. With
`envelope_s=600` and a collector running the full 600 s the residual per-slot budget is ≈0, and
`start_drift_max_s=10` is a hard exclusion. A269 ENVELOPE-START-DRIFT-01 — p1 phase gate this
activation and the precondition ruling 14 R6 puts on the re-run (`start_drift ≤ 2 s` on a live dry
check) — is caused by exactly this pattern of per-slot serial finalisation (~4.9 s recorder-exit
wait + 130 MB plist parse + 0–2.3 s derive + ~2.8 s exit/spawn). A267 adds another serial
subprocess to that sum, ceiling 30× the drift gate, and **nothing measures its cost**. Repro: `quiet_predicate_campaign.py:757-771`.
Cure: record `attestation_elapsed_s` per envelope; bound the query by the residual slot budget
(`timeout=max(5, min(300, scheduled_next - time.monotonic() - margin))`, exhaustion → `asserted`,
already a safe state); preferably launch it detached at slot end and join at the next boundary,
still pre-rotation. At minimum R6's ≤2 s dry check must run with the attestation enabled.

### SHOULD-FIX

**S1 — an empty or degenerate `log show` result authenticates the envelope**
(`quiet_predicate_campaign.py:420-427`: rc 0 with zero matched markers ⇒ `authenticated`, the only
claim-bearing state). Executed: `""` → authenticated; `"<html>error</html>"` → authenticated. The
repo's own evidence refutes the premise that an empty result can come from a working query:
`tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt` line 1 is the syslog header
`Timestamp               Ty Process[PID:TID]`, which `log show --style syslog` emits even with no
matching entries — so zero lines means the query produced nothing at all. The suite pins the
defect: `fake_commands(timed_log="")` is the default and `test_every_envelope_is_attested_…`
asserts `authenticated`. Repro: `probe_exec2.py::TimedLog`. Cure: authenticate only when stdout
carries the header (or ≥1 line); capture `stderr` and force `asserted` when it is non-empty.

**S2 — exit code 3 swallows refusal code 2** (`quiet_predicate_campaign.py:805-807` returns 3
before the outcome is consulted). Executed, P9: a night refused for a dead covariate recorder, or
for two consecutive `cleanup_unproven` envelopes, returns **3** when the restore also failed, while
ruling 10 cl.5, brief cl.11 and the in-code comment all define 3 as distinct from 2 and as meaning
the captured envelopes stay valid. `scripts/run_night.py:3235` collapses both to
`EXIT_CHAIN_FAILED`, so today's driver verdict is unaffected, but a harvester acting on 3's
documented meaning would act on a refused night. Repro: `probe_exec2.py::TruthTable`. Cure: `base = 0 if outcome in
{"complete","partial"} and cleanup["cleanup_proven"] else 2; return 3 if (base == 0 and not
network_time_restored) else base`.

**S3 — a timed-out or raising OFF leaves no receipt** (`quiet_predicate_campaign.py:269-274` calls
`set_network_time("off")` before `write_control_record`). Executed (P2, `TimeoutExpired`):
`control["off"] is None`, contradicting the docstring's promise that a refused attempt is still on
the record. Repro: `probe_exec.py::P::test_p2_off_times_out`. Cure: wrap the call and write
`{"argv": …, "exit_code": None, "stdout": None, "error": f"{type(exc).__name__}: {exc}", …}` as the
`off` receipt before re-raising.

**S4 — the restore path destroys an unreadable OFF receipt in place**
(`quiet_predicate_campaign.py:294-310`: on a read failure `control` resets to `{"off": None}` and is
written back over the original). Executed (P4a, file truncated to `"{ not json"`): `rc=0`,
`network_time_restored: true`, and the record now claims `off: null` while every envelope's
`session.json` still carries `record_sha256` of the original bytes — an artifact asserting OFF was
never established for a night whose envelopes assert it was. Repro:
`probe_exec.py::P::test_p4a_control_file_truncated_at_restore`. Cure: preserve the original bytes
(rename to `.corrupt`) and record `"off": {"state": "unreadable", …}`, never `null`.

**S5 — a control record parsing to a non-dict kills the night with a traceback.** Line 296 catches
only `(OSError, ValueError)`; a payload parsing to `null`, a list, a string or a number raises
`TypeError` at line 308 — **inside the `finally`**, replacing any in-flight exception and caught by
neither `execute`'s nor `main`'s except tuple. Executed (P4b): it escapes, leaving no
`evidence_outcome.json` and no refusal document, exactly what the neighbouring comment forbids.
Repro: `probe_exec.py::P::test_p4b_control_file_is_json_null`. Cure, one line: `if not
isinstance(control, dict): control = {"schema": NETWORK_TIME_CONTROL_SCHEMA, "off": None}`.

**S6 — `record_attestation`'s write is unguarded, so one envelope's annotation can refuse the
night** (`quiet_predicate_campaign.py:448-452`: `write_text` + `os.replace`, no `except`). Executed
with a read-only envelope directory: `PermissionError` escapes, `execute` catches it as `OSError`,
and the whole night is refused. The function already returns `False` on an unreadable session and
`pilot_summary` already falls back to the envelope entry's `network_time_attestation`, so failing
soft is safe. Cure: `except OSError: return False` around the write/replace.

**S7 — the collector-side exact-stdout comparator has no whitespace regression.** M13
(`sample_quiet_predicate_evidence.py:255`, `stdout != EXPECTED…` → `stdout.strip() !=
EXPECTED….strip()`) survives all 158 tests. The chain-side comparator is pinned
(`test_lower_case_stdout_or_nonzero_exit_refuses_before_any_envelope`); the collector-side one,
which gates every envelope's provenance, is not, although ruling 10 Q1 rule 1 and the docstring
word it as byte equality. Cure: a regression feeding `" setUsingNetworkTime: Off "` and
`"setUsingNetworkTime: Off"` (no newline) to `network_time_provenance`, asserting refusal.

### NIT

**N1** — `quiet_predicate_campaign.py:407` (`argv = timed_log_argv(*window)`) sits outside the
guarded try, and `datetime.fromtimestamp` raises on out-of-range finite epochs: `1e18` → `OSError`
(caught, night refused); `1e300` → **`OverflowError`**, caught by neither except tuple. Unreachable
from a well-formed session (`write_json` uses `allow_nan=False`). Cure: move line 407 inside the
try; add `OverflowError`.

**N2** — `reduce_interior` (`sample_quiet_predicate_evidence.py:396-400`) maps the window to ns,
then hands `integrate` `start_ns/1e9` and `end_ns/1e9`, which line 333 re-rounds. Executed: exact for
every production value (0 mismatches over the twelve fixtures' real interiors and a 60 000-sample
sweep at the pilot epoch with durations 480/570/600 s), because those `duration_ns` are multiples
of the 256 ns float spacing at epoch scale. Not exact in general: `round((n/1e9)*1e9) != n` for
199 228 of 200 000 arbitrary epoch-scale integers, and the span shifts ±128 ns for durations such
as 0.002 s (+128), 0.006 s (−128), 12.3456789 s (−52). Since the completeness gate is now exact
integer equality, a future `interior_s` off that lattice would make a covered interior `partial`.
Cure: pass the integers through instead of round-tripping.

**N3** — two unkilled mutations in ruled code. M1 (line 292, `round`→`int`) leaves the rounding
mode of the single ruled float→ns conversion (14 R5) unpinned (≤1 ns). M2 (line 334,
`math.ceil`→`round`) survives although the docstring states the conversion is rounded outward so
the expanded round is never narrowed. Cure: one assertion each (an endpoint float at x.5 ns;
`integrate` with `uncertainty_s=1e-12` must expand by 1 ns).

**N4** — M3 (`rail_coverage_ns[rail] == duration_ns` → `>=`) survives but is an EQUIVALENT mutant:
`overlap` clips to the window and `integrate` raises on overlapping supports, so coverage can never
exceed the window. Likewise `overlap`'s zero floor change `0.0`→`0` (line 310) is benign — executed
`stationarity()` and the `join_load_log` tests, all outputs still float. No action on either.

**N6** — a night whose twelve collectors all refuse with exit 3 (verified live), or whose twelve
envelopes are all `slew_attested` (verified in P9), reports `partial`/`complete` and chain **rc 0**
with zero claim-bearing envelopes. Follows the pre-existing `collect_error` convention and
`summary.json` records INCONCLUSIVE; reported for visibility, not as a defect.

## §3 Same-signature statement

No same-signature repetition: first review round on `447fd6bf`, no fix rounds from this seat. The
one recurrence worth naming is structural — B1 and A269 share a signature (per-slot serial work on
the inter-envelope critical path), which is why B1 is tiered blocker.

## §4 Verdict

The scientific core of A267 holds up under execution. v3 is byte-identical to `ecbc0fac` on all
twelve pilot envelopes and on the pre-existing 47-test corpus run against the new deriver; the v3.1
identity is genuinely bound to its caps; all twenty-five unresolved return paths carry the identity
fields; all three admission constants are killed by the suite when moved. The numeric rewrite
behaves at every edge I could reach — partial interiors, windows past the last frame, saturating
uncertainty and zero-width frames all degrade to reported partials rather than crashes, and every
timed-log grouping degradation errs toward exclusion. The defects are in the new operational skin,
not the arithmetic: one blocker, where the per-envelope `log show` sits synchronously on exactly
the inter-slot path that A269 — a p1 gate and the ruling's own precondition for the re-run — must
shorten, with a 300 s ceiling against a 10 s drift budget and no instrumentation of its cost; and
seven should-fixes, sharpest among them that an empty `log show` yields the strongest verdict the
system can issue although exhibit D proves a working query always emits a header, and that the
`finally`-path restore can both destroy an OFF receipt it cannot read and escape with an uncaught
`TypeError` that leaves a night with no outcome document. None of these invalidate the twelve
regressions or the fixtures, and every should-fix is small, local and testable. Recommendation:
land after B1 is answered (instrument-and-bound at minimum, with R6's dry check re-run under the
attestation) and S1–S7 are cured, with a delta re-audit.
