# Exhibit B — controlling authorities (verbatim, anchor-located extracts)

Generator output. Each extract is bounded by printed anchor strings and carries the five fields the charter requires of a bounded excerpt from a document whose own words are the object of a question. Nothing below is paraphrased.

## B1 — D-138 (the merge-staging rule this transaction is built on)

- Source path: `docs/decision_log.md`
- Immutable revision: `c8812172` (file sha256 at that revision: `3c756cfa102ddbfd04b548090db56155c79db5911710b85fc79466293c770468`)
- Exact line range: 10360-10382
- Anchors: start = the single line beginning `### D-138 — D-079-pinned estimator-input changes are merge-staged`; end = the line before the next line beginning `### D-138 implementation note`
- Proposition it addresses: Q1: whether a branch that changes a D-079-pinned estimator input may merge, and in what transaction shape.
- Why non-narrative primary evidence is unavailable: The cited text is itself the object of the question: the packet asks the judge to apply, amend or ratify these exact words. No non-narrative primary artifact states a ruling's or a brief's text; the code implements it but cannot evidence what was ordered.

```text
10360  ### D-138 — D-079-pinned estimator-input changes are merge-staged into the atomic re-freeze (magistrate, 2026-08-15; promoted from session ruling R-t9-4 at the T9 close)
10361  
10362  Any change to a file in the issued D-079 acceptance artifact's
10363  `estimator_code_sha256` pin set (`joulewise/powermetrics_fiducial.py`,
10364  `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`,
10365  `joulewise/reduce.py`) deliberately stales the issued artifact: the canonical
10366  suite's authenticated-staleness fan-out is a LIVE INVARIANT (the suite proves
10367  the issued artifact matches real bytes), and re-keying those tests to fixtures
10368  to make such a branch mergeable is FORBIDDEN — it would delete the invariant
10369  that catches accidental estimator drift.
10370  
10371  **Consequences:** (1) such branches complete their C-028 gauntlet normally but
10372  are MERGE-STAGED: they merge ONLY inside the atomic Phase-2 successor
10373  re-freeze transaction that re-issues the acceptance artifact and every
10374  dependent pin (first instance: `impl/wo-detect-pulses-budget` @ `5449e58`,
10375  carrying WO-DETECT-PULSES-BUDGET + the calexits flake fix). (2) Follow-on work
10376  that must touch the same pinned files RIDES THE SAME BRANCH rather than
10377  opening a second staleness event on main (the inheritance corollary; the
10378  flake fix is the precedent). (3) The re-issue and pin update remain lead-owned
10379  inside the re-freeze; tests may re-key only private synthetic fixtures.
10380  Authority context: R-t9-4 (docs/run_reports/2026-08-16-t9-session.md), the
10381  2026-08-15 D-078 registry amendment on the staged branch, and the council's
10382  Phase-2 re-freeze ruling.
```

## B2 — A267 rebuttal ruling 14, R3 and R4 (the corpus-replay bar and the attestation argv this packet's Q2 and Q6 turn on)

- Source path: `docs/process_traces/2026-09-22-activation-d9990b3c/01-coldgate-packet-a267-clock-discipline-anchor/14-coldgate-fable-rebuttal-ruling.md`
- Immutable revision: `c8812172` (file sha256 at that revision: `507c33cb62a55a1bfd23f8d863fc4203959838aac57793f8dff0801da1226ef1`)
- Exact line range: 17-23
- Anchors: start = the single line beginning `## R3 — Consult R2/R3 bars`; end = the line before the next line beginning `## R5 — Q3 corrections`
- Proposition it addresses: Q2 and Q6: the ruled `log show` argv (including `--style syslog`) and the twelve-envelope / 34-member replay requirements.
- Why non-narrative primary evidence is unavailable: The cited text is itself the object of the question: the packet asks the judge to apply, amend or ratify these exact words. No non-narrative primary artifact states a ruling's or a brief's text; the code implements it but cannot evidence what was ordered.

```text
   17  ## R3 — Consult R2/R3 bars: (i) AMEND Q4, (ii) SUSTAIN for v3 and AMEND for v3.1 (refuter BLOCKER 2 sustained, cured)
   18  
   19  (i) Yes, a corpus replay under the default method is required; under (c) the consult's "≤ 1 ms / ±0.25 ms" bar (`02-design-consult.md:107`) tightens to exact record equality, because (c) promises v3 byte-identity. The 34-member corpus is not in this checkout (the 2026-08-18 trace directory holds three markdown files; measurement roots are outside the judge's read set). Substitute, burden on the seat and lead: (a) in-repo regression 8: replay all twelve archived envelopes' `power.anchor.clock_stamps` and native rows under the default method and assert the derived dict equals the recorded `power.anchor` dict exactly (sha-pinned fixtures; twelve real members including the refused ones, zero delta); (b) pre-merge bench step by the magistrate on the corpus root: replay all 34 under v3, zero delta, with the 34 ids and the byte-equality result in the PR ledger; any unreachable member is listed by id and marked NOT EXECUTED, and the lane does not merge on fewer than 34 without that list. (ii) A16 and A17 (> 5 ms span) and `tests/test_uncertainty_evidence.py:772` (`effective_clock_anchor_bound_exceeded`) exercise both R3 bars for v3 and remain binding unchanged, since the default resolves to `V3_CAPS`. v3.1 adds regressions 9–11: (9) > 25 ppm sustained rate (ruling regression 5 already); (10) placement > 5 ms with rate within limit (stamp resolution 6 ms → `anchor_only_bound` > 5 ms → `effective_clock_anchor_bound_exceeded`); (11) backstop: 20 ppm over a 900 s baseline → span 18 ms → `wall_minus_monotonic_span_exceeded` under v3.1, killing a backstop deletion that the rate check alone would pass.
   20  
   21  ## R4 — Authenticated OFF: AMEND Q1 (refuter MATERIAL 4 sustained, cured)
   22  
   23  Deciding evidence: consult I4 requires an *authenticated* admission (`02-design-consult.md:92`, B3); C2 proves the read form is outside the slice; exhibit D shows `timed` logs every applied slew as `cmd,apply,src,adjtime` at level `Df` (ten lines), correlating with envelope 07's excursion. A set-command receipt is necessary, not sufficient, for I4. New Q1 rule 6: the chain (not the collector, the process killed on SIGTERM paths) runs, after each envelope's collector exits and before the next settle: `/usr/bin/log show --info --debug --style syslog --predicate 'process == "timed"' --start <sampling_started − 1 s> --end <sampling_stopped + 1 s>` (absolute path: the zsh `log` builtin returns nothing; `--info --debug` because the apply lines are `Df` and default `log show` omits them). It writes `evidence/envelope-NN/timed-log.txt`, its sha256, and scans for `cmd,apply,src,`, `ntp_adjtime`, `settimeofday`. Exit 0 and zero matches → the envelope's provenance gains `"attestation": {"state": "authenticated", "method": "timed_log_show_predicate_v1", "window_epoch_s": [start, end], "log_sha256": …, "matched_lines": 0}`. Any match → `"state": "slew_attested"`, `matched_lines` n, and the envelope is excluded with reason `network_time_slew_attested` (the night continues). Exit ≠ 0 → `"state": "asserted"` and exclusion `network_time_unattested`. Only `authenticated` envelopes are claim-bearing. Timing constraint: the query runs within ten minutes of the envelope (exhibit D shows the store retained ≥ 2.5 h at harvest); it is never deferred to harvest. Regression 12: the scanner over exhibit D returns 10 matches.
```

## B3 — A269 cold ruling 10, Q1 (cure, with amendments A1 and A2)

- Source path: `docs/process_traces/2026-09-22-activation-e4b4ead6/03-coldgate-packet-a269-start-drift/10-coldgate-fable-ruling.md`
- Immutable revision: `c8812172` (file sha256 at that revision: `37739f686206549595ba43a67f564bba799119bee26f81106ae007e33e73425b`)
- Exact line range: 11-17
- Anchors: start = the single line beginning `## Q1 — Cure.`; end = the line before the next line beginning `## Q2 — Registration.`
- Proposition it addresses: Q1 and Q7: the cure that fixes the 20 s inter-slot gap this packet's Q3 budgets, and the measured-not-budgeted standard the judge may apply.
- Why non-narrative primary evidence is unavailable: The cited text is itself the object of the question: the packet asks the judge to apply, amend or ratify these exact words. No non-narrative primary artifact states a ruling's or a brief's text; the code implements it but cannot evidence what was ordered.

```text
   11  ## Q1 — Cure. AFFIRM the lead's (c), with two binding amendments
   12  
   13  Ruled: **option (c)**, cure 2 — `slot_pitch_s: 620`, `envelope_s: 600` unchanged, under registration v2 (Q2); batched census (`pgrep -g <list>`, C5 13.8 ms) in the same landing; all finalisation and the R4 attestation inside the gap.
   14  
   15  Deciding evidence: the only ≤ 2 s figure in the record that is *measured* rather than budgeted is envelope 01 (P1: 0.160 s chain, 0.318 s session), the one slot with no predecessor (P2 line 490 shows why every other slot inherits the tail). Cure 2 makes every slot an envelope-01 by construction; worst observed tail 10.23 s + worst attestation 1.45 s = 11.7 s < 20 s gap. Options (a) and (b) rest on budgets: (a) 2.5–4.8 s serial per both seats (fails); (b) 0.6–0.9 s session-level is D2's arithmetic, unmeasured, and it places the 113-group census and `log show` (real work in `logd`, outside `observer_cpu_s` = SELF + reaped CHILDREN) inside slot i+1's capture — unattributed observer energy in a recorded window, even if outside the interior. (d) declined: it leaves the harness overrunning its own schedule and blinds the only tail-regression detector. Serial budget I accept as evidence: C2 stamps (postparse−stop 4.85–5.07, derive 0.01–2.29, nextpre−end 2.61–3.02), C5, C6.
   16  
   17  Amendments (MATERIAL): (A1) the 2 s bar of R6 is assessed on the **session-level** `start_drift_s` (the larger figure, line 361 takes the max), i.e. envelope 01's 0.318 s is the reference, not 0.160. (A2) `execute` gains an up-front total-window check before the first spawn: `settle_s + (envelopes−1) × slot_pitch_s + envelope_s ≤ window_max_s` (8020 ≤ 9000, C1); the per-slot check at line 480 stays as written (it correctly uses `envelope_s`, the capture length — D1's remark that line 481 "must learn pitch" is a NIT, not a defect). `validate_protocol` must reject `slot_pitch_s < envelope_s` and any CLI override, fail-closed.
```

## B3b — A269 cold ruling 10, Q2 (the ruled registration v2 and the merge order)

- Source path: `docs/process_traces/2026-09-22-activation-e4b4ead6/03-coldgate-packet-a269-start-drift/10-coldgate-fable-ruling.md`
- Immutable revision: `c8812172` (file sha256 at that revision: `37739f686206549595ba43a67f564bba799119bee26f81106ae007e33e73425b`)
- Exact line range: 19-27
- Anchors: start = the single line beginning `## Q2 — Registration.`; end = the line before the next line beginning `## Q3 — R6 precondition shape.`
- Proposition it addresses: Q1 and Q7: what registration v2 contains, and the ruled ordering constraint that both A267 Part 3 and A269 must be merged before any arm.
- Why non-narrative primary evidence is unavailable: The cited text is itself the object of the question: the packet asks the judge to apply, amend or ratify these exact words. No non-narrative primary artifact states a ruling's or a brief's text; the code implements it but cannot evidence what was ordered.

```text
   19  ## Q2 — Registration. AFFIRM the lead's (a)
   20  
   21  Ruled content of `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json`, byte-identical to v1 (B1, sha `f59804a9…`) except:
   22  - `"slot_pitch_s": 620` (new key, alphabetical position after `"settle_s"`);
   23  - `"start_drift_abort_s": 2` (new key, Q3 — the in-chain abort threshold is pre-registration text);
   24  - `"exclusions"` gains, appended after `"start_drift"`: `"network_time_slew_attested"`, `"network_time_unattested"`;
   25  - `"ruling"`: `"cold gate 10 Q1/Q2 (2026-09-19); adjudication 10a; sizing ruling 46b; A269 cold gate 10 (2026-09-22) Q1(c)/Q2(a)/Q3"`;
   26  - `"chain_source_sha256"` re-pinned only if `scripts/night_chains/quiet_predicate_evidence.zsh` changes bytes (the pitch lives in Python — unchanged unless the seat touches the zsh).
   27  Everything else unchanged: `schema` string, sizing, `minimum_retained` 8, `minimum_adjacent_pairs` 4, `start_drift_max_s` 10, `cadence_exclusion` text, `interior_*`, `envelope_s`, `settle_s`, `window_max_s`, `summary`, `stop_branches`, `receipt_class`. Code: `night_gate.QPE01_PILOT_REGISTRATION_SHA256` re-pinned to v2's digest; `RULED_REGISTRATIONS` gains the v2 entry (label "QPE-01 idle-variance pilot protocol v2 (A269 gate 2026-09-22)"); v1's entry retained as ruled history and marked superseded so it is never armable again. Ordering: v2 lands in the **same PR as the first of** A267 Part 3 (the two attestation reasons) or the A269 harness change to merge; a pinned list that omits reasons the code emits is an incomplete registration and must never exist on main. Both A267 Part 3 and A269 must be merged before any arm. Option (b) REJECTED (would make the pinned list documentary — contrary to the byte-pin's purpose); (c) not needed: the packet supplies the deciding facts.
```

## B4 — A269 cold ruling 10, Q3 (the replacement R6 clause) and Q4 (attestation mechanics i–iii)

- Source path: `docs/process_traces/2026-09-22-activation-e4b4ead6/03-coldgate-packet-a269-start-drift/10-coldgate-fable-ruling.md`
- Immutable revision: `c8812172` (file sha256 at that revision: `37739f686206549595ba43a67f564bba799119bee26f81106ae007e33e73425b`)
- Exact line range: 29-41
- Anchors: start = the single line beginning `## Q3 — R6 precondition shape.`; end = the line before the next line beginning `## Q5 — Record correction.`
- Proposition it addresses: Q4 and Q7: what `window_epoch_s` was ruled to mean, and whether the re-run night is itself the live check.
- Why non-narrative primary evidence is unavailable: The cited text is itself the object of the question: the packet asks the judge to apply, amend or ratify these exact words. No non-narrative primary artifact states a ruling's or a brief's text; the code implements it but cannot evidence what was ordered.

```text
   29  ## Q3 — R6 precondition shape. AFFIRM the lead's (c), amended to every envelope
   30  
   31  Ruled: **option (c)** — the re-run night is itself the live check, under a pre-registered in-chain drift abort. This gate is expressly presented with R6 and amends its precondition; R6 as issued remains in the record (charter §9). Amendment (MATERIAL): the abort fires at **every** envelope's spawn, not only 01–02 — R6's bar is "every envelope", and a drift > 2 s at a later slot after clean early ones is exactly a "new cause" R6 wants named. Rule location: threshold in the registration (`start_drift_abort_s: 2`, Q2); enforcement in chain code, `execute`, immediately after `actual = time.monotonic()` (line 482) and before `launch(...)`.
   32  
   33  Abort rule (exact): `if actual − scheduled > protocol["start_drift_abort_s"]: append_event(evidence_envelopes.jsonl, {index, scheduled_mono_s, actual_mono_s, start_drift_s, "abort": "start_drift_abort"}); write night refusal reason "start_drift_abort"; raise` — no collector spawned for that slot, night ends, outcome REFUSED (never a pack, never INCONCLUSIVE-by-data). Cost of disproof ≈ t0 + settle 600 + 620 ≈ 21 min at envelope 02.
   34  
   35  Replacement R6 final clause (exact text, replaces "live-installer dry check … or names a new cause."): "the pilot night re-run is prepared only after lane A269 has landed cure Q1(c) (`slot_pitch_s: 620`) under registration v2 and a daytime bench replay — real `execute` and real collector with an injected recorder replaying an archived plist, no sudo, no measurement, never labeled R6 evidence — shows chain-level `start_drift_s` ≤ 0.5 s on every slot; the re-run night is itself the live check: the chain refuses the night at the first envelope whose chain-level start drift exceeds `start_drift_abort_s` (2 s), before that envelope's capture; a night that completes with every envelope's session-level `start_drift_s` ≤ 2 s satisfies this precondition and counts; the re-run then yields at least eight bounded envelopes with none excluded for `start_drift`, or names a new cause." Options (a), (b), (d) REJECTED as strictly costlier with no rigor gain: (c) keeps rules-before-data (threshold pinned in v2 before t0).
   36  
   37  ## Q4 — Attestation mechanics
   38  
   39  (i) **AFFIRM** the widened window. Exact rule: `span = sampling_stopped.monotonic_before_s − sampling_started.monotonic_before_s`; `start = min(sampling_started.epoch_s, sampling_stopped.epoch_s − span) − 1`; `end = max(sampling_stopped.epoch_s, sampling_started.epoch_s + span) + 1`; record both endpoints in `window_epoch_s` and add `"window_method": "epoch_monotonic_union_v1"`. Under a wall step inside the envelope the union covers the true capture whichever endpoint the step displaced; ±1 s alone does not (D1 §Q6(e), verified against R4's text at ruling 14 line 23).
   40  (ii) **AFFIRM** as a rule: the attestation query is never concurrent with a `powermetrics` capture (`logd` work is unattributable observer energy, C3 `observer_definition`); under Q1(c) it runs after `cleanup_groups` and before the next sleep, inside the gap; R4's ten-minute constraint is met by construction (gap ≤ 20 s).
   41  (iii) **AFFIRM** R4's shape (attestation inside `session.json` via atomic rewrite by the chain after collector exit — safe under cure 2 because no finaliser ever rewrites the file again, D2 §Q6.6). NIT amendment: the attestation object records `"session_sha256_before": <sha256 of session.json before the rewrite>` so the edit is auditable; rewrite = write tmp + `os.replace`.
```

## B5 — Fix-round brief 06: WRITE_SCOPE and the Forbidden line

- Source path: `docs/process_traces/2026-09-22-activation-e4b4ead6/06-a267-fix-round-1-brief.md`
- Immutable revision: `c8812172` (file sha256 at that revision: `aa3c4f45d511d799d8239cfab017e6dfe3c4e554658b20d35c622c3d95968ed3`)
- Exact line range: 5-7
- Anchors: start = the single line beginning `SESSION_MODE: delegated`; end = the line before the next line beginning `## Magistrate triage`
- Proposition it addresses: Q3 and Q5: the scope the fix-round seat was bound to, and the freeze on `joulewise/uncertainty_evidence.py` that makes the r7 estimator pin final.
- Why non-narrative primary evidence is unavailable: The cited text is itself the object of the question: the packet asks the judge to apply, amend or ratify these exact words. No non-narrative primary artifact states a ruling's or a brief's text; the code implements it but cannot evidence what was ordered.

```text
    5  SESSION_MODE: delegated
    6  WRITE_SCOPE: joulewise/quiet_predicate_campaign.py, scripts/sample_quiet_predicate_evidence.py, tests/test_uncertainty_evidence.py, tests/test_sample_quiet_predicate_evidence.py, tests/test_quiet_predicate_campaign.py
    7  Forbidden: any edit to `joulewise/uncertainty_evidence.py` (D-079-pinned; its bytes are frozen for the r7 re-issue unless a ruling says otherwise — NEEDS_RULING if a cure seems to need it), any other file, sudo/systemsetup/powermetrics/real `log`, the canonical checkout, pushing.
```

## B6 — Fix-round brief 06: items 1, 2, 6 and 14 (the dictated closure shapes this packet's Q2, Q3, Q4 and Q5 amend or ratify)

- Source path: `docs/process_traces/2026-09-22-activation-e4b4ead6/06-a267-fix-round-1-brief.md`
- Immutable revision: `c8812172` (file sha256: `aa3c4f45d511d799d8239cfab017e6dfe3c4e554658b20d35c622c3d95968ed3`)
- Anchors: each item is the single line beginning `N. ` under `## Items`; the line range of each is printed beside it.
- Proposition it addresses: Q2 (item 2's header guard), Q3 (item 1's attestation bound), Q4 (item 14's window keys), Q5 (item 6's rewrite guard).
- Why non-narrative primary evidence is unavailable: The cited text is itself the object of the question: the packet asks the judge to apply, amend or ratify these exact words. No non-narrative primary artifact states a ruling's or a brief's text; the code implements it but cannot evidence what was ordered.

```text
   16  1. (05b B1 residual) `attest_network_time`: the `log show` timeout is bound to the gap — `timeout = max(5, slot_pitch_s − envelope_s − 5)` passed in from `execute` (15 s under v2), never the literal 300; on `TimeoutExpired` the state is `asserted` with reason `timed log query timed out` and the night continues. Journal the query's wall cost in the envelope entry (`network_time_attestation_wall_s`). Regression: fake `log` that sleeps past the bound → `asserted`, exclusion `network_time_unattested`, next slot still spawned on time (fake clock).

   17  2. (05b S1) Zero-output guard: `log show --style syslog` always emits a header line; rc 0 with empty stdout (or stdout lacking the syslog header pattern) → state `asserted`, reason `timed log query returned no header`. Regression: `fake_commands(timed_log="")` and a `<html>error</html>` body → `asserted`, never `authenticated`.

   21  6. (05b S6) `record_attestation` write failure (e.g. `PermissionError`) → the envelope's attestation state becomes `asserted` with reason `session rewrite failed: …` in the envelope entry, exclusion `network_time_unattested`; the night continues. Regression with a read-only `session.json` path.

   29  14. (05a N3) `attestation.window_epoch_s` records the whole-second values actually passed to `--start/--end` alongside the float union window (`window_argv_epoch_s`). (05a N5) Pedagogy: gloss "pulse" at its first module-level use in `uncertainty_evidence.py` — NO: that file is frozen; instead gloss it where the sampler/campaign docstrings use it, and gloss "ulp" ("unit in the last place: the spacing of adjacent float64 values") and "sudoers slice" at first use in the sampler/campaign. (05a N6) Rename the envelope-07 test to say backstop. (05b N1) `timed_log_argv` guarded against non-finite/absurd epochs (→ `asserted`). (05b N3) Regressions killing `round`→`int` on the endpoint and `ceil`→`round` on `uncertainty_ns` (the ruled outward rounding).

```

## B7 — First lines of the three saved log bodies (`repr`, exact bytes)

- Sources: the fixture at `489b0953` and the two saved live-capture exhibits at `c8812172`'s successor bookkeeping head (tracked paths below).
- Proposition it addresses: Q2 and Q6 — whether the guard's constant matches the header the ruled argv actually produces.
- Why non-narrative primary evidence is unavailable: not applicable; these ARE primary artifacts. Their digests are printed in exhibit C3.

```python
# tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt @ 489b0953
'Timestamp               Ty Process[PID:TID]'

# docs/process_traces/2026-09-22-activation-59857fe5/07c-exhibit-D2-timed-log-0210-0435-syslog.txt
'Timestamp                       (process)[PID]    '

# docs/process_traces/2026-09-22-activation-59857fe5/07c-exhibit-D3-timed-log-zero-match-syslog.txt
'Timestamp                       (process)[PID]    '
```
