# Opus 5 counter-review (gate item 6), contract lens, at 68db7e98 (verbatim; scratchpad paths redacted)

Seat: Opus 5 via `Agent`, read-only on `/Users/edr/code/JouleWise-wt-t26-b` at `68db7e98`, brief = C1–C7 (ruled-relation fidelity, `_MIN_IDLE_NS` derivation, boundary regressions, terra 229 DOC-ADDITIVITY disposition, unapplied bench texts, overbuild, same-signature statement). 123 677 tokens, 49 tool uses, 13.9 min.

## Counter-review

**C1 — Does the installed predicate implement exactly the ruled item-3 text?**

Yes. Verbatim, side by side.

Ruling (`/Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md:196-206`):

> **Verdict: AMEND — the 5 s constant and the 35 s corollary are STRUCK; the upper relation is retained as a well-typed LIVENESS bound on the consumer's clock, one-constant change.**
>
> > Ruled relation (replaces "R1-completion→validity-origin ≤5 s (oldest participating R1 result ≤35 s old at issuance)"):
> > `0 <= (valid_until_monotonic_ns − 21_600_000_000_000) − r1_batch_finished_monotonic_ns <= 600_000_000_000`
> > with both endpoints from `context.clock.monotonic_ns()` … Clock: ordinary monotonic (`time.monotonic_ns`, `CLOCK_UPTIME_RAW` on Darwin) — NOT `CLOCK_MONOTONIC_RAW`, which stays reserved for the anchor physics.

Code (`/Users/edr/code/JouleWise-wt-t26-b/joulewise/arm_readiness.py:6478-6482`, inside `if not (…): return False` opened at `:6466` in `_clock_probe_predicate_passes`, `:6414`):

```
6478:        # D-170 item 3 ruled 600 s liveness provenance: 11 * 45 s + 105 s; see reason-code-coverage-delta.md §6.3.
6479:        and 0
6480:        <= (valid_until - 21_600_000_000_000)
6481:        - value["r1_batch_finished_monotonic_ns"]
6482:        <= _T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS
```

with `_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS = 600_000_000_000` at `arm_readiness.py:6349`.

Term-by-term: same constant (600e9, not 5e9); same direction (`<=`, inclusive, upper bound on the R1→stamp gap); same subtrahend order; the lower half `0 <=` is the algebraic restatement of the pre-existing `valid_until - r1_finished >= 21_600_000_000_000` it replaced (`git diff main...HEAD -- joulewise/arm_readiness.py`), so the 6 h horizon is not weakened. No 5 s or 35 s value appears anywhere in the predicate.

Clock typing is correct and is the thing most at risk of drift here: `valid_until` comes from `receipt["valid_until_monotonic_ns"]` (`:6449`) and `r1_batch_finished_monotonic_ns` is the *ordinary*-monotonic publication; the RAW-typed siblings `r1_batch_finished_monotonic_raw_ns` / `r1_batch_started_monotonic_raw_ns` are consumed only for the 30 s duration relation (`:6461-6464`, `:6475-6476`). Both liveness endpoints are on the ordinary clock. No drift.

One documentation drift, not code: the amendment written into `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:158-160` states the bound is "on ordinary `CLOCK_MONOTONIC`". On Darwin `time.monotonic_ns` is `CLOCK_UPTIME_RAW`, which the cold-gate ruling names explicitly at `COLD-GATE-RULING.md:205-206`; `CLOCK_MONOTONIC` is a different clock id. In a ruling amendment whose entire subject is clock typing, naming the wrong clock is a real defect (F-1 below). The same addendum also restates the relation as `0 <= validity_origin_monotonic_ns − r1_batch_finished_monotonic_ns <= 600_000_000_000`, which is equivalent to the ruled and coded form only because `valid_until == validity_origin + 6 h` exactly — a relation enforced in a *different* function, not inside `_clock_probe_predicate_passes` (F-6).

**C2 — `_MIN_IDLE_NS` derivation: count, arithmetic, enforcement.**

I counted the sites myself with an AST walk over `joulewise/arm_readiness_evidence_t0.py` at this head (command and output in Executed evidence). Twelve `_fresh_probe` call sites exist: `:1101` (inside `_fresh_clock_reference_batch`, i.e. the R1 batch itself) and eleven others at `:1216, 1318, 1365, 1723, 1724, 1725, 1726, 1801, 1836, 1837, 1838`. R1 is issued from `_derive_clock_attestation` (`:1130-1209`, calling `_fresh_clock_reference_batch` at `:1152`), which derives `clock.correct_and_prior_state` — the first entry in `_EXPECTED_ROWS` (`:99-115`). The eleven others sit in derivers for rows that come later in that tuple (`clock.network_time_off`, `t0.background_quiet`, `t0.display_thermal_idle`, `t0.no_stray_keepawake`, `t0.passwordless_powermetrics`, `t0.power_path`). **The count of 11 post-R1 sites is right.** Arithmetic: 11 × 45 = 495; 495 + 105 = 600; `_PROBE_TIMEOUT_SECONDS = 45` at `:54`; `_MIN_IDLE_NS = 600 * 1_000_000_000` at `:51`; `600e9 == _T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS`. **The arithmetic is right.**

**The count is not enforced — it is prose only.** The single test that binds anything is `tests/test_arm_readiness_evidence_t0.py:855 test_t0_liveness_constant_matches_minimum_idle_interval`, which asserts `readiness._T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS == t0._MIN_IDLE_NS`. Nothing counts `_fresh_probe` sites, so adding a twelfth post-R1 site raises the governed envelope to 540 + 105 = 645 s with no failing test and no notice. That is F-2.

Worse, the equality test creates a coupling the ruling never asserted. `_MIN_IDLE_NS` already carries two unrelated physical meanings in its own module: the T-0 RAW anchor span floor (`:1162-1163`, "T-0 RAW anchor span is below 600000000000 ns") and the prewindow ten-minute idle capture floor (`:1303-1304`). The ruling cited the equality as *provenance* ("the sum equals the module's existing `_MIN_IDLE_NS`" — `COLD-GATE-RULING.md:210-211`), i.e. a noted coincidence. The test promotes it to an invariant across three semantically distinct quantities. If a future change moves `_MIN_IDLE_NS` for either of its own two reasons, the cheapest green is to move the cold-gate-ruled 600 s number, and **no live fence forbids that** — the "moves only by cold gate" fence exists only in the unapplied bench kernel row (file 11). That is F-3.

**C3 — Do the three boundary regressions test the boundary, and the production call site?**

They test the boundary, at all three sites, and they go further than the ruling required. The ruling asked for "600 s + 1 ns refuses, 600 s − 1 ns passes" (`COLD-GATE-RULING.md:232-234`); the branch adds the inclusive-endpoint case (exactly 600 s passes), which is the case that distinguishes `<=` from `<`:

- arm: `tests/test_arm_readiness.py:59, 62, 65, 68` (+1 ns refuse, −1 ns pass, exactly-600 pass, −1 ns-negative refuse)
- issuance: `tests/test_arm_readiness_evidence_t0.py:831, 841, 849`
- rehearsal: `tests/test_t0_rehearsal.py:562, 568, 574`

Not a copy of the predicate anywhere. Issuance drives the public `author_arm_readiness_evidence_t0(pack, custody)` end-to-end with a mocked clock, reaching `_readiness._predicate_passes` at `arm_readiness_evidence_t0.py:2342`. Rehearsal drives `rehearsal._run_real_arm_boundary`. The arm case calls `readiness._predicate_passes` directly — the production function (`arm_readiness.py:6511`), one level below the arm consumption entry points at `:6664` / `:9121`; the rehearsal test covers that entry level, so the gap is closed in aggregate rather than per-test.

I verified they are bound to *this* conjunct rather than passing for another reason, by mutating the constant at runtime (no file writes) and re-running: with the upper bound effectively removed, all three "+1 ns refuses" tests fail (3/3); with the constant set to 600 s − 1 ns, all three exactly-600 tests fail (3/3). Output in Executed evidence. This independently reproduces terra 229's V3/V4/V8.

The one duplicative test is `test_t0_liveness_bound_refuses_negative` (`test_arm_readiness.py:68`): the negative case was already covered pre-existing at `tests/test_arm_readiness_schemas.py:1184` (`21_599_999_999_999 → False`) and `:1240-1244` (`reverse_validity_horizon`). Harmless; pins the rewritten lower half in its new algebraic form. Nit, F-8.

**C4 — Terra 229's DOC-ADDITIVITY-01 and the magistrate's disposition.**

Verified myself; the disposition was right on the point it decided, and the restoration is byte-identical to main.

The grep false-positive claim is true: `printf 'exceeds 0.5 seconds.\n' | grep -c "5 s"` returns 1 — "0.5 **s**econds" contains the literal `5 s`. The seat had rewritten two ruled table rows (`RF-04`, `RF-08`) from "exceeds 0.5 seconds." to "exceeds the 0.5-second ceiling." purely to silence its own F-5 grep, which is a policy-bearing table row edited for a lint artifact. Bench commit `4cf4346f` reverted exactly those two lines. I diffed the branch's `RF-04`/`RF-08` rows against `main`'s: byte-identical at lines 477 and 481 (`diff` returned empty). The two lines matched by the grep at this head are precisely those two `0.5 seconds` rows — no live 5 s policy text remains.

The magistrate's supporting grep for the §6.3 heading rename (`grep -rn 'cold-gate-pending--r1\|63-cold-gate-pending\|five-second validity-origin bound' docs tests joulewise scripts`) I re-ran: the only hit is the disposition file quoting itself, so no anchor references break. Confirmed.

The remaining DOC-ADDITIVITY items the magistrate accepted as marker-style are genuinely additive: the `MAGISTRATE-RULING-T0-UNATTENDED.md` edit re-wraps main's line 79 into two lines with every word preserved plus an inline `[STRUCK 2026-09-02 …]` marker (compared against `git show main:…` lines 74-83); RF-17 (`:491`) and the numeric relation (`:522`) keep their full prefix with a `[superseded …]` marker appended. Accepted disposition, correctly reasoned.

**C5 — Do the two unapplied bench texts leave a ruled-not-installed gap?**

No *code* on this branch is contingent on them, but the branch ships a dangling link and a live kernel contradiction. Three decided-≠-done items survive the merge, plus one I am adding.

1. **`D-170` does not exist at this head, and production code cites it.** `arm_readiness.py:6478` and `reason-code-coverage-delta.md:1152` both cite D-170. `git show main:docs/decision_log.md | grep -c "D-170"` → `0`; the log ends at D-169. D-170 lives only on `origin/feat/2026-09-02-t26-install` (`:216`, `:10476`). No test resolves code-side `D-NNN` citations against the decision log (I checked `tests/test_docs_freshness.py`, which validates the index against bodies within the log only), so if merge order slips, production ships a citation to a nonexistent decision and nothing fails. This is a hard merge-order dependency, not a preference. F-4.

2. **The §6.3 addendum link has no target.** `reason-code-coverage-delta.md:1160-1161` links to `COLD-GATE-RULING.md#addendum-2026-09-02--item-3-drift-envelope-rationale`. `grep -n "Addendum\|addendum" /Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md` finds no such heading — the addendum exists only as trace file `12-bench-coldgate-addendum.md`. Merging as-is publishes a dangling cross-reference into an authority chain. F-5.

3. **`docs/process/state_kernel.json` still forbids what the code now does.** At `:4286-4289` the fence reads: *"The 5 s issuance bound is COLD-GATE-PENDING and must not be reinterpreted, relaxed, or implemented here, including as 'predicate recency'"*; at `:4345` the `T0-UNATTENDED-01` status note still says *"That upper bound is deliberately NOT implemented and no inert substitute was added."* Both are false at this head. The kernel row `T0-LIVENESS-BOUND-EMPIRICAL-01` (file 11) that would carry the empirical-closure obligation and the "600 s moves only by cold gate" fence is unapplied. This is terra 229's blocker, dispositioned to a post-merge bench batch. F-7.

4. **New here: the ruling's own dispositive premise is falsified by this branch's analysis, and nothing corrects it.** `COLD-GATE-RULING.md:214-217` states: *"A successful path is strictly below every probe ceiling, so the bound cannot false-refuse a healthy night."* The branch's own §6.3.1 (`reason-code-coverage-delta.md:1167-1200`), which I read and which terra independently re-derived, shows the *fixed bounded subprocess subtotal alone* is 495 s of probe waits plus 220 s of eleven 20 s git ceilings = **715 s, already above the ruled 600 s**, before untimed startup, I/O, hashing, scans, and `identity_pins` runtime preparation. So the ruling's stated ground for choosing 600 s over the refuter's 495 s is not merely unproven — it is contradicted. The branch registers this correctly as a limitation and proposes a kernel row, but the drafted cold-gate addendum (file 12) covers only PHYS-2, the drift-envelope arithmetic; **no drafted text corrects PHYS-1 in the authoritative ruling file.** Future readers of `COLD-GATE-RULING.md` will read a false safety claim. This is exactly the class T26 item 4 was ruled to catch. F-9, should-fix.

**C6 — Overbuild / merge-ability.**

The 1800 lines are overwhelmingly trace docs (1561 of them, files 01-16 plus MAGISTRATE-NOTES) — appropriate gauntlet record, not overbuild. Production is 1 added line and 4 removed. Tests are ~230 lines. Nothing is write-only: `SAMPLE_VALID_UNTIL_NS` and `T0_EVIDENCE_AUTHOR_REASON_CODES` each have exactly one consumer.

Two items that do not cleanly earn their place against *this* ruling:

- The 43-code `T0_EVIDENCE_AUTHOR_REASON_CODES` frozenset plus `test_t0_evidence_author_refusal_vocabulary_is_closed` (`tests/test_arm_readiness_integration.py:59-101, 694-714`) is ~75 of the ~230 test lines and is scope-adjacent: the ruling states flatly "no new reason code, so no REASON_CODE_COVERAGE delta" (`COLD-GATE-RULING.md:231-232`). It came from terra 212's F3 as an M8 mutation-kill, and it does kill M8, so it is defensible — but it is a regex-scrape-equals-hardcoded-list test that asserts nothing behavioral, and it lands a permanent 43-entry maintenance burden on a PR whose ruling said the reason-code census was untouched. Should-fix on scope discipline, not on correctness. F-10.
- The fixture comment at `tests/test_arm_readiness_schemas.py:44-46` gives the wrong reason for the sample ARM keeping `10**30`: it says "arm consumption is checked against the live monotonic clock." The actual reason is that `sample_arm` (`:221-253`) carries `"evidence": []` and `"rows": []` — it has no clock PROBE fact, so `_clock_probe_predicate_passes` never runs against it. A future reader trusting the stated reason would draw the wrong conclusion about ARM coverage. Nit, F-11.

Two accepted-as-fine items I checked and am not flagging: `__import__("re")` inline at `test_arm_readiness_integration.py:702` follows the file's own pre-existing convention (`:640`); and the shared-fixture change `sample_evidence()["valid_until_monotonic_ns"]` from `10**30` to `SAMPLE_VALID_UNTIL_NS` is necessary (the old value would now refuse) and the five-module suite is green.

Merge-ability: `main` is no longer an ancestor of HEAD (main has advanced to `ab91ebdb`), but the full-suite replay recorded in file 16 was run on integration tree `858f553e` — `Ran 4820 tests`, `OK (skipped=125)` — so the merge was tested, not just the branch.

**C7 — Same-signature statement.**

No defect class recurred between the refuter round (files 04/06/08) and the delta (file 14): the three refuter lenses produced test-coverage gaps (terra F1-F3), doc-consistency divergence (luna C10/C11/C13), and physics limitations (Sol PHYS-1/PHYS-2); the delta found no repeat of any of those — every runtime closure was INSTALLED and the ruled 600 s and its inclusive `<=` never moved. What the delta *did* miss is a fresh, opposite-direction regression the fix round introduced: at the landing `e40e7502` the conjunct carried a four-line comment reading "*this is a liveness/hang detector, not a metrology bound*" and citing "*D-170 / COLD-GATE-RULING item 3*", which luna 211 had explicitly confirmed as clause C4 ("Code comment labels liveness, not metrology — CONFIRMED"). The magistrate's own fix brief F-8 (`09-fix-round-1-brief.md:117-119`) then instructed the seat to compress it to "one line … point to §6.3", and `fea89b72` did so, deleting both the "not a metrology bound" labelling that `COLD-GATE-RULING.md:211-214` *ruled* into the code and the only in-code pointer to the authoritative ruling file — replacing it with a citation to D-170, which does not exist at this head. Terra 229 recorded the change under F-8 as INSTALLED ("its old four-line comment became the one-line ruled-provenance comment") without re-checking the ruled labelling clause a prior refuter had confirmed. That is the gauntlet's live blind spot on this lane: a fix round directed by the magistrate un-installed a ruled requirement, and the delta re-audit checked that the change *happened* rather than that the requirement *survived*. It is one occurrence, not a same-signature repeat, but it is the pattern worth naming.

## Findings

- **F-1 — should-fix — the ruling amendment names the wrong clock.** `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:159` says "on ordinary `CLOCK_MONOTONIC`"; the cold gate ruled `time.monotonic_ns`/`CLOCK_UPTIME_RAW` on Darwin and expressly distinguished the clocks (`COLD-GATE-RULING.md:203-206`). Code is correct; the authority text is not.
- **F-2 — should-fix — the "11 sites × 45 s" provenance is asserted, not enforced.** Nothing counts `_fresh_probe` sites; a twelfth post-R1 site (`joulewise/arm_readiness_evidence_t0.py`, current sites `:1216, 1318, 1365, 1723-1726, 1801, 1836-1838`) raises the governed envelope to 645 s with no failing test.
- **F-3 — should-fix — the constant-equality test manufactures an invariant across three unrelated quantities.** `tests/test_arm_readiness_evidence_t0.py:855` pins the cold-gate-ruled 600 s liveness ceiling to `_MIN_IDLE_NS`, which independently means the RAW anchor span floor (`arm_readiness_evidence_t0.py:1162`) and the prewindow idle floor (`:1303`). The "moves only by cold gate" fence lives only in the unapplied kernel row.
- **F-4 — should-fix (hard merge-order gate) — production cites a decision that does not exist.** `joulewise/arm_readiness.py:6478` cites D-170; `git show main:docs/decision_log.md | grep -c "D-170"` → `0`. D-170 exists only on `origin/feat/2026-09-02-t26-install`. No lint catches this.
- **F-5 — should-fix — dangling addendum link ships with the merge.** `docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:1160-1161` links to `COLD-GATE-RULING.md#addendum-2026-09-02--item-3-drift-envelope-rationale`; that heading does not exist in the ruling file on main.
- **F-6 — nit — the addendum's restatement of the relation is a paraphrase.** `MAGISTRATE-RULING-T0-UNATTENDED.md:158` writes the bound on `validity_origin` where ruling and code write `(valid_until − 6 h)`; equivalence depends on RF-18, which is enforced outside `_clock_probe_predicate_passes`.
- **F-7 — should-fix — the state kernel still forbids what the code now does.** `docs/process/state_kernel.json:4289` calls the 5 s bound COLD-GATE-PENDING and "must not be … implemented here"; `:4345` says the upper bound is "deliberately NOT implemented and no inert substitute was added". (This is terra 229's KERNEL-STALE-01; I re-verified both lines at this head. I grade it should-fix rather than blocker because the fence's literal object — the *5 s* bound — is struck, so the code does not violate it; the text is stale, not contradicted in force.)
- **F-8 — nit — duplicate negative-boundary coverage.** `tests/test_arm_readiness.py:68` re-covers ground held by `tests/test_arm_readiness_schemas.py:1184` and `:1240-1244`.
- **F-9 — should-fix — the ruling's dispositive safety premise is falsified and uncorrected.** `COLD-GATE-RULING.md:214-217` claims the bound "cannot false-refuse a healthy night"; this branch's §6.3.1 (`reason-code-coverage-delta.md:1167-1200`) establishes a 715 s fixed bounded subtotal above the 600 s bound. The drafted addendum (trace file 12) corrects only the PHYS-2 drift arithmetic; nothing corrects PHYS-1 in the ruling file.
- **F-10 — should-fix — reason-code census expansion is out of the ruling's scope.** `tests/test_arm_readiness_integration.py:59-101, 694-714` adds a 43-entry hardcoded vocabulary on a PR whose ruling states "no new reason code, so no REASON_CODE_COVERAGE delta" (`COLD-GATE-RULING.md:231-232`). It does kill M8, so keep or drop on scope grounds, not correctness.
- **F-11 — nit — fixture comment states the wrong reason.** `tests/test_arm_readiness_schemas.py:44-46` attributes the sample ARM's retained `10**30` to live-clock consumption; the real reason is that `sample_arm` (`:221-253`) has no clock PROBE fact at all.
- **F-12 — should-fix — fix round un-installed a ruled labelling and the only in-code pointer to the ruling.** `fea89b72` replaced the landing's four-line comment ("*not a metrology bound*", citing `COLD-GATE-RULING`) with the single line at `joulewise/arm_readiness.py:6478`, per the magistrate's own brief `09-fix-round-1-brief.md:117-119`. `COLD-GATE-RULING.md:211-214` rules that the bound "is labelled so in code; it is NOT a metrology bound", and `:234-235` directs the comment to "cite this file". Terra 229 recorded the change as INSTALLED without re-checking the clause luna 211 had confirmed. Partially mitigated by the constant name `_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS`.
- **F-13 — not-a-defect — the stale line citation in the addendum.** `MAGISTRATE-RULING-T0-UNATTENDED.md:160` cites `arm_readiness.py:6485`, which at HEAD is `if live_clock_anchor is …`; but the sentence pins the citation to "At landing `e40e7502`", where `:6485` *was* the conjunct's last line (verified with `git show e40e7502:joulewise/arm_readiness.py`). Accurate as written, misleading to a reader at HEAD. Flagging for awareness only.

**No blockers.** The installed predicate matches the ruled relation exactly and its regressions are mutation-verified at all three sites. Every remaining item is documentation/authority consistency or scope, and the merge-order dependency on D-170 (F-4).

## Executed evidence

```
$ cd /Users/edr/code/JouleWise-wt-t26-b && git log --oneline -1
68db7e98 custody: gate item 9 — full-suite replay on integration tree 858f553e (Ran 4820, OK, skipped=125)

$ git status --porcelain
(empty)
```

AST census of `_fresh_probe` call sites at this head:

```
$ python3 - <<'EOF'   # ast walk over joulewise/arm_readiness_evidence_t0.py
1101 _fresh_clock_reference_batch
1216 _derive_clock_probe
1318 _maintenance_probe
1365 _thermal_probe
1723 _derive_process_census
1724 _derive_process_census
1725 _derive_process_census
1726 _derive_process_census
1801 _derive_powermetrics
1836 _derive_power
1837 _derive_power
1838 _derive_power
total call sites: 12
```

```
$ grep -n "_MIN_IDLE_NS\|_PROBE_TIMEOUT_SECONDS" joulewise/arm_readiness_evidence_t0.py
51:_MIN_IDLE_NS = 600 * 1_000_000_000
54:_PROBE_TIMEOUT_SECONDS = 45
449:                process.wait(timeout=_PROBE_TIMEOUT_SECONDS)
1162:    if span < _MIN_IDLE_NS:
1303:    if capture["finished_monotonic_ns"] - capture["started_monotonic_ns"] < _MIN_IDLE_NS:
```

Five-module suite (mine, `TMPDIR` set to scratch):

```
$ TMPDIR=<scratch> python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 \
    tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_integration
Ran 180 tests in 195.766s

OK (skipped=12)
```

Runtime mutation A — upper bound effectively removed (`_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS = 10**18`, monkeypatched in-process, no file written):

```
FAIL: test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns
AssertionError: T0EvidenceAuthoringError not raised
- ('PASS', None)
+ ('REFUSE', 'readiness_clock_preflight_refused')
Ran 3 tests in 2.378s
FAILED (failures=3)
MUTANT A failures= 3 errors= 0
```

Runtime mutation B — cap minus 1 ns (`= 599_999_999_999`), the three exactly-600 s pass tests:

```
Ran 3 tests in 1.837s
FAILED (failures=2, errors=1)
MUTANT B failures= 2 errors= 1
```

C4 verification:

```
$ printf 'R0 ... exceeds 0.5 seconds.\n' | grep -c "5 s"
1

$ diff <(git show main:.../reason-code-coverage-delta.md | grep -n "^| RF-04\|^| RF-08") \
       <(grep -n "^| RF-04\|^| RF-08" .../reason-code-coverage-delta.md) && echo IDENTICAL
IDENTICAL

$ grep -rn "cold-gate-pending--r1\|63-cold-gate-pending\|five-second validity-origin bound" docs tests joulewise scripts
(only the magistrate disposition file quoting its own grep)
```

C5 verification:

```
$ git show main:docs/decision_log.md | grep -c "D-170"
0
$ git show main:docs/decision_log.md | grep -oE "^## D-1[0-9]+" | tail -3
## D-167
## D-168
## D-169
$ git show origin/feat/2026-09-02-t26-install:docs/decision_log.md | grep -n "D-170" | head -2
216:| D-170 | T26 COLD-GATE VERDICTS — install ruling status, tracked gate ledger, T-0 liveness bound, and executed-evidence duty | open (installs via T26-RULING-INSTALL-01) |
10476:## D-170: T26 cold-gate verdict installation (magistrate, 2026-09-02)

$ grep -n "Addendum\|addendum" /Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md
(no "## Addendum 2026-09-02 — item 3 drift-envelope rationale" heading; only item-4 discussion text at :259-:309)

$ awk 'NR>=4286 && NR<=4289' docs/process/state_kernel.json
"label": "cold-gate packet: ruling-status semantics (addendum: the 5 s T-0 bound)",
...
"rule": "The 5 s issuance bound is COLD-GATE-PENDING and must not be reinterpreted, relaxed, or implemented here, including as 'predicate recency'"
```

## What I did not check

- I did not run the canonical full suite; I relied on trace file 16 (`Ran 4820 tests … OK (skipped=125)` on integration tree `858f553e`) for whole-repo greenness and ran only the five named modules myself.
- I did not run any live T-0 authoring, rehearsal, arm, custody, or quiet-machine action. Every number about real elapsed R1→stamp intervals in this review is from static analysis and from §6.3.1's own analysis; I did not independently re-derive the 220 s git-ceiling half of the 715 s subtotal (I confirmed the 495 s probe half by AST census).
- I did not audit the ~1561 lines of trace prose for internal consistency beyond the files I quote (01, 04, 06, 08, 09, 10, 11, 12, 14, 15, 16, MAGISTRATE-NOTES); I did not read 02, 03, 05, 07, 13 in full.
- I did not verify that the eleven post-R1 derivers cannot be skipped or re-entered at runtime (which would make 495 s an over- or under-estimate); I verified only their static call sites and their position in `_EXPECTED_ROWS`.
- I did not check the sibling branches `feat/2026-09-02-t26-install` or `feat/2026-09-02-t26-gateledger` for conflicts with this branch beyond confirming D-170's presence in the former's decision log.
- I did not attempt an on-disk mutation of the checkout (read-only constraint); mutations were monkeypatched in-process, which exercises the constant but not, for example, a source-level `<=` → `<` edit. Terra 229's V4 covers that one.