# A267 fix round 1 — delta re-audit, CONTRACT lens (Fable, read-only)

Delta: `c5f4f9c6..62412ee6` in `/Users/edr/code/JouleWise-wt-a267-review2` (14 commits, five WRITE_SCOPE files; UE byte-identity and the three counterfactual mutations taken as the magistrate's bench facts, not re-derived). Read in full: brief 06, lenses 05a/05b, the seat's report, rulings 10/14 (A267) and 10 (A269) for the clauses cited, the full production diff and all three test diffs, plus the surrounding code at the head (`execute` 1020–1160, `restore_network_time` 356–426, `attest_network_time` 604–669, `cleanup_budget_s` 977–989). Ran only greps; no tests, no mutations, nothing edited. Line numbers are at 62412ee6. QC = `joulewise/quiet_predicate_campaign.py`, SQ = `scripts/sample_quiet_predicate_evidence.py`, TQ/TS/TU = the test modules.

## Findings

**BLOCKER** — none.

**SHOULD-FIX**

S1 (item 1, seat D3). The dictated bound `max(5, slot_pitch_s − envelope_s − 5)` is implemented exactly (QC:600–601, 15 s under v2), and the brief's arithmetic is what does not hold. QC:977–983 still says the reserve of 5 s is "a reserve that the attestation's `log show` fits in … so a teardown can never eat the attestation's time or run into the next spawn", while QC:579–597 gives the attestation 15 s and admits the pair overruns. Two comments in one module now describe two different budgets for the same 20 s. Failure scenario, with A269 ruling 10's own measured numbers: collector finalisation tail 10.23 s (worst observed) + a `logd` that answers in 9 s (below the 15 s bound, so the query is NOT abandoned) = 19.2 s, next spawn drifts ~2.2 s past `start_drift_abort_s` = 2 → `start_drift_abort` → the whole night REFUSED, and `top_up: false` forbids reusing its envelopes. Under `gap − cleanup_budget_s(protocol)` = 5 s (the reserve QC:983 already set aside for exactly this) the same event costs ONE envelope (`asserted`, excluded) and the night keeps its cadence; the band where the two formulas differ is a query taking ~8–15 s, above 5× the worst measured 1.45 s. Verdict on the magistrate's question (b): acceptable for the pilot night as a NAMED refusal (the abort is the ruled detector and `network_time_attestation_wall_s` on the journal row makes the cause readable), but it is the costlier of two fail-closed outcomes and contradicts the module's own reserve comment. Recommend the magistrate rule the bound to `max(ATTESTATION_TIMEOUT_FLOOR_S, gap − cleanup_budget_s(protocol))` (5 s under v2) and update TQ:1257's `15` pins, or, if the 15 s stands, rewrite QC:977–983 so the two comments agree. This amends a dictated shape, so it is the magistrate's call, not the seat's.

**NIT**

N1 (item 3). Brief: "executed truth table over outcome × cleanup_proven × restored (eight rows)". TQ:1334's third axis is the CAUSE of refusal (dead recorder vs two `cleanup_unproven`), not the final `cleanup_record`'s `cleanup_proven`; the harness asserts that flag True on every row (TQ:513). The `and cleanup["cleanup_proven"]` term at QC:1159 has no row in this table; deleting it is caught, if at all, only by pre-existing tests. Code CONFORMS; the regression's axes deviate from the dictated ones.

N2 (item 1). Reason literal is `timed log query timed out after 15 s` (QC:650) against the dictated `timed log query timed out`; TQ:1252 pins by `startswith`. Harmless (exclusions key on state). Also, the "next slot still spawned on time" regression (TQ:1257) stubs the attestation with `attest_burn` rather than running the real function against a sleeping fake `log`; the real `TimeoutExpired` path is proven only by the 0.5 s unit test at TQ:1239. Together they cover the brief; neither alone does.

N3 (item 14). `window_argv_epoch_s` is set only on the success path (QC:641–642) while `window_epoch_s` is initialised to `None` in the record skeleton (QC:619): blocked and window-unavailable records lack the key instead of carrying `null`. Initialise it beside `window_epoch_s`. Separately, `timed_log_window_epoch_s` (QC:459–472) parses a naive local `strptime(...).timestamp()`, which resolves the DST fold to its first occurrence; during the fall-back hour (2026-11-01 01:00–02:00 local) an argv in the second occurrence would be recorded 3600 s early, and TQ:1546's `floor` assertion would fail. The argv string itself is equally ambiguous to `log show` (pre-existing, ruled argv format); irrelevant to a September night, worth one docstring sentence.

N4 (item 5). A receipt write that fails inside the restore is swallowed with no reason anywhere (QC:411–412: `except Exception: pass`), while the brief's clause reads "caught and reported (… reason recorded)". The outcome then says `network_time_restored: true` and the control record on disk shows `on: null`. Pre-existing behaviour, the exit-code verdict is right; one `print(..., flush=True)` would close it.

N5 (item 6). On an `os.replace` failure the `session.json.tmp` is left in the envelope directory (QC:701–707); TQ:1483 checks no `.tmp` only for the write-fails case. Unlink it in the `except`.

## Items 1–14

1. CONFORMS — QC:576–601, 604, 1107–1113; the bound, the `TimeoutExpired` branch, the journal key and the `timeout=300` absence are all present and pinned. See S1 for the brief's arithmetic and N2 for the reason literal.
2. CONFORMS — QC:449–457, 662–663; header guard after rc, before the match; exhibit D, "", html, bare newline, headerless entry all pinned (TQ:1284).
3. CONFORMS — QC:1159–1160 is the dictated two-line precedence; `network_time_restored` on every outcome document (QC:1140–1142). N1 on the table's axes.
4. CONFORMS — QC:332–344 writes the six-key `off` receipt, then refuses; the seam is the named `NETWORK_TIME_SET_TIMEOUT_S` (QC:39), pinned at 30 (TQ:1361).
5. CONFORMS — sibling receipt for unreadable/non-dict (QC:395–410), outer guard (QC:416–426), `[]`/garbage end-to-end with bytes untouched (TQ:1437). N4.
6. CONFORMS — QC:701–714, `except OSError` → `asserted` + `session rewrite failed: …`, night continues; ordering in `execute` (record before the journal row, QC:1110–1115) makes the summary see it. N5.
7. CONFORMS — TS:1475–1521, four strip-equivalent variants refuse with exit 3, ruled bytes still pass.
8. CONFORMS — TU:1114–1127 and TU:1204–1214 assert method, literal `p2-038.4`, `dict(V3_1_CAPS)` on both unresolved paths.
9. CONFORMS — TS:1317–1354 keeps the span tiled and shorts `rail_sum_w` by exactly 1 ns.
10. CONFORMS — TQ:679–709 asserts the OFF receipt's stdout/exit and the fake clock at 0.0 (< `settle_s`) at the toggle.
11. CONFORMS — TQ:1507–1520 patches `cleanup_record` to raise; `on` exit 0 already on the record.
12. CONFORMS — SQ:314–329 adapter, SQ:332–365 integer signature, SQ:436–437 ints straight through; callers exhaustively listed and verified by grep (`reduce_interior`, `integrate_seconds` ← `collect`; nothing else in `joulewise/` or `scripts/`); 12.345 s regression TS:1523–1568.
13. CONFORMS — QC:875–880 computes `unattested` before the join and the join reads both gates; TQ:91 pins it.
14. CONFORMS — argv window key (see D1), non-finite/absurd guard with `OverflowError` (QC:630–639), glosses at QC:25–28 and SQ:274–276, backstop rename, endpoint-rounding pin (TS:1374–1400). N3.

## Deviations D1–D8

D1 HOLDS. Ruling 14 R4 defines `window_epoch_s` as the placement window and A269 ruling 10 Q4(i)/regression 5 pins it to `attestation_window(stamps)` (TQ:995, TQ:810 `[999.0, 1601.0]`). 05a N3's cure is "record the argv strings' epoch equivalents", i.e. a new field. The brief's sentence attaches its parenthetical ambiguously; the seat's reading is the only one that leaves the ruled key meaning what two sealed rulings say it means. Answer to (a): yes, the right reading.
D2 HOLDS. grep: no "pulse" in QC or SQ; its only use is in the frozen UE (out of scope by the brief's own Forbidden line).
D3 HOLDS as a faithful implementation of the dictated bound, and the seat was right to flag it; see S1 for why the brief's arithmetic, not the seat, is the defect, and why the pilot night can run on it.
D4 HOLDS. An absent record cannot be "overwritten"; the brief's protection clause is about existing bytes, and the pre-toggle refusal path's existing regression reads the main record.
D5 HOLDS. The `ValueError("network time OFF not established: TimeoutExpired: …")` re-raise keeps ruling 10 Q1 rule 2's refusal wording and the executor's except tuple; the underlying class survives in the message and in `off.error`.
D6 HOLDS. A necessary consequence of item 2 (an empty body can no longer authenticate); the `log_sha256` pin follows the fixture, not the other way round.
D7 HOLDS. The session-unreadable path is unreachable in practice — `attest_network_time` reads the same file first and would already be `asserted` — and the brief's item 6 dictated only the rewrite failure.
D8 HOLDS. `type(x) is int` is what makes the renamed signature a contract; it also rejects `bool`, which is correct. Not dictated, but strictly within "takes INTEGER nanoseconds".

## Verdict

All fourteen items implement the dictated closure shapes; the rulings cited by the brief (10 Q1 rules 1–6, 14 R2/R4/R5, A269 10 Q1(c)/Q3/Q4) still hold over the changed code, and every deviation D1–D8 survives. No blocker. One should-fix, and it is the brief's own arithmetic rather than the seat's execution: the attestation bound and the teardown budget both claim the same 15 s of a 20 s gap, and the module now carries two contradictory comments about the 5 s reserve. Cheapest closure is the magistrate ruling the bound to the reserve (5 s under v2) with the two TQ pins updated; the alternative is to keep 15 s and fix QC:977–983. Either way the pilot night fails closed and named. Five nits, all local.
