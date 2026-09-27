# QPE-SHAPE3-NIGHT-BLANK-01: paired Opus contract refuter (Opus 5.5)

Seat: Claude Opus 5.5 (`claude-opus-5-5`), contract lens, paired with the cold Fable judge. Probe tree `JouleWise-wt-qpe3sol-e6f06c96` at `a30385e8` (only `tests/test_gen_state.py` differs from `1417c0c4` under `joulewise/ scripts/ tests/ configs/`: `git diff --stat 1417c0c4 HEAD -- joulewise scripts tests configs`). Read-only on code; scratch under `/tmp/qpe3opus/` (`driver.py`, `p1_sigterm.py`, `p2_summary.py`, `p3_auth.py`, `p5_attest.py`). Not read: RUN_STATE, TASK_QUEUE, AGENTS, decision log, memory or skill files. The harness loaded the global and project CLAUDE files and the memory index into my context without my choosing.

## A. Independent answers

### A.0 Executed evidence (this session, foreground)

| # | Probe | Observed |
|---|---|---|
| P1-V1 | **Real signals.** A driver mirroring `main()`'s collect branch (SIGTERM handler raising `KeyboardInterrupt`, `:1675-1677`) runs the real `collect` with a round runner that stalls in round 2 and a stand-in power recorder whose `finish()` takes 1.0 s (the powermetrics teardown). Launched with `start_new_session=True`, its pgid journaled; the parent waits with a timeout, books `124`, then calls the **real** `cleanup_groups` (the executor's `:1564-1572` sequence). | executor code **124**, real rc **-2** (uncaught `KeyboardInterrupt`), `cleanup_proven` True, on disk: `session.json` = first write (`end_stamp` absent, `error` None, `error_class` None, no `whole_envelope_observer_cpu_s`), `rounds.jsonl` **2 provisional rows**. Shape (iii). |
| P1-V2 | Same, no power recorder (fast `finally`) | code 124, real rc **1**, `end_stamp` **present**, `error = "KeyboardInterrupt: collector termination requested"`. **Shape (ii) with `collector_exit = 124`.** |
| P1-V3 | Same as V1 but ONE SIGTERM instead of `cleanup_groups` | code 124, rc 1, `end_stamp` present. Shape (ii). |
| S-1 | Source `cleanup_groups` `:267-303` | Re-sends `killpg(SIGTERM)` to every non-absent group on every 50 ms sweep for up to `min(20, 0.67*budget)` s, then SIGKILL. The first SIGTERM lands in the round/loop (caught at `:1099`/`:1148`), a later one lands inside the `finally` (`recorder.finish()` catches `Exception` only, `:1152-1154`) and escapes `collect`. **This is why V1 is shape (iii) and V3 is not.** With S2's post `ioreg` read in the same `finally`, `observe` catches `Exception` only (`battery_float.py:342`), so the storm escapes it too. |
| P2-a | `pilot_summary` **today** on a night: envelope 01 completed (real `collect`, `FakeClock`), envelope 02 = the P1-V1 directory, entry `collector_exit 124` | **RAISED `ValueError: envelope 2: whole_envelope_observer_cpu_s or envelope span missing; absent evidence is never a pass`** (`:1321-1323`). The executor maps this to `outcome refused`, `"pilot summary failed: …"` (`:1686-1687`). |
| P2-b | Same night, envelope 02's `rounds.jsonl` deleted (kill before the first journal append) | Summary written, envelope 02 `excluded = [collect_error, incomplete_interior_support]`, `error` set. This is the only shape in which F2 holds. |
| P2-c | Same night, envelope 02 = a real network-time refusal envelope (shape (i), entry `collector_exit 3`) | **RAISED the same `ValueError`**: the refusal path writes no `whole_envelope_observer_cpu_s`, its empty journal parses, so it lands in `readable`. |
| P3-a | `authenticate_quiet_session` on P1-V1 with a text-5 pre (`float.ioreg`, the collector's own uuid) injected into the first-write session | `evidence_missing`, reasons **`("post evidence missing: phase not recorded",)`**, not `quiet span unavailable` (one stamp, so the span block at `battery_float.py:925` never runs). Same as merged T30-f (`tests/test_battery_float.py:780-796`). |
| P3-b | + journal replaced by `{` | unchanged (journal not an input in shape (iii)). |
| P3-c | + pre raw altered | **`CustodyFailure`** (rung (b)). |
| P3-d | V1 + **charging** pre | **`battery_float_confounded`**, reasons `pre IsCharging is not No`, `pre InstantAmperage exceeds 200 mA`, `post evidence missing: phase not recorded`. The helper does **not** short-circuit shape (iii); confounded dominates. |
| P3-e/f/g | V1 + stale / malformed / exit-code-2 pre | `evidence_missing` with a **pre** reason plus the post reason. |
| P3-h | V1 + pre **and** post, no `end_stamp` (a stripped completed record; not an honest shape) | `evidence_missing`, `("quiet span unavailable",)`. |
| P3-i | V1 without `battery_float` | `evidence_missing`, both phases "not recorded" (historical rule). |
| P4 | **Honest shape (iii) with no kill:** round runner returns `observer_cpu_s = NaN`, driven through the real `main()` | `main` rc **2**; the provisional append raises inside the `try`, the `finally` runs, then the finalization rewrite (`open("w")` then `json.dumps(allow_nan=False)`) raises: `session.json` first write, **`rounds.jsonl` truncated to 0 bytes**. With the pre injected: `("post evidence missing: phase not recorded",)`. |
| P5 | `attest_network_time` + `record_attestation` on V1 and V2 | Both `asserted`; the rewrite loses no key (V2 keeps `end_stamp`, V1 stays without). |
| NOT EXECUTED | A real powermetrics/`ioreg`/sudo collector; S2 code (not written) | The power teardown is a 1.0 s sleep stand-in; the pre is injected after the fact, as the erratum judge did. |

### A.1 Bench facts

- **F1 — CONFIRMED with a correction.** `:1566-1567` books `124` on `TimeoutExpired`; `cleanup_groups` then reaps. But the reap is a **SIGTERM storm** (S-1), and the collector's handler turns each SIGTERM into `KeyboardInterrupt`. A timed-out collector is therefore not simply "killed": it reaches shape (ii) if its finalization fits between two SIGTERMs (V2, V3) and shape (iii) otherwise (V1). With a real powermetrics teardown and S2's post `ioreg` in the `finally`, shape (iii) is the expected outcome. Both shapes carry `collector_exit = 124`.
- **F2 — REFUTED for the realistic shape.** Today a shape-(iii) envelope with at least one journaled row does not cost "only its own admission": `pilot_summary` raises `ValueError` in the observer-floor loop (P2-a) and the executor refuses the whole night. F2 holds only when the kill precedes the first journal append (P2-b). So today's cost is already a whole night, and text 6 would not make it worse; the amendment must fix this path too, or S2 will reproduce the refusal under a new name (A.7, T6-2).
- **F3 — CONFIRMED and widened.** First write at `:1084`, `end_stamp` only in the `finally` (`:1163`), final write `:1208`. Shape (iii) also arises **without any kill** from any exception between the `finally` and `:1208` (P4: rc 2 on a `ValueError`; an uncaught non-`ValueError` gives rc 1). A kill after `end_stamp` is set in memory but before `:1208` also leaves shape (iii) on disk, possibly with a truncated or finalized journal (P4 shows the truncation; amendment 34 makes the rewrite atomic but does not change the shape).
- **F4 — CONFIRMED with a correction to the reason.** The envelope is outside amendment 32's step (1) (session exists), `authenticate_quiet_session` runs, rung (b) raises first on a bad pre raw (P3-c). But the honest reason is `post evidence missing: phase not recorded`, **not** `quiet span unavailable` (P3-a); `quiet span unavailable` appears only when a post record is present without `end_stamp` (P3-h), which no honest collector writes. Any amendment that keys on the reason string must use the right one.

### A.2 Question 1: shape (iii) with `collector_exit != 0`: **AMEND, narrowly.**

Excuse only the one reason the collector failure itself causes. The envelope is excluded (`collect_error` is already on it, because `collector_exit != 0`) and the night proceeds **iff all** of the following hold: the executor entry's `collector_exit != 0`; the admitted `session.json` has a `battery_float` key, no `end_stamp`, `error_class != QUIET_REFUSAL_ERROR_CLASS` (shape (iii)); `battery_float` is a dict without a `post` key; and the verdict is `battery_float_evidence_missing` with reasons **exactly** `("post evidence missing: phase not recorded",)`. Every other verdict on that envelope follows text 6 unchanged.

Why: every honest shape-(iii) producer (V1, P4, SIGKILL, OOM) leaves a first-write session whose post was never written, because text 5 puts the post only in the final write. The missing post brackets no retained number: the envelope yields `joules None` and is excluded, and every retained envelope carries its own pre/post at its own span edges. Blanking the night for it charges an honest collector failure a whole night, against the erratum's class rule. Keying on `collector_exit` (executor memory, never re-read from disk) prevents a stripped `end_stamp` from reaching the excuse through `pilot_summary`.

### A.3 Question 2: a `confounded` pre still blanks the night; so does any pre defect.

P3-d: the helper already returns `battery_float_confounded` on a shape-(iii) envelope with a charging pre, so an excuse keyed on the exact reason tuple leaves it blanking with no extra code. The science: a charging observation at `t_k` is direct evidence that the float condition failed during this night. The pooled statistics (pairs, sizing, spreads) assume one machine regime across the night. Excusing that observation because the same collector also failed makes the outcome depend on an unrelated fault. It also opens a selection channel: if charging and collector stalls are correlated (thermal, power-state transitions), the excuse would hide exactly the confounded envelopes. The same logic applies to a pre that is stale, malformed or failed (P3-e/f/g): that evidence gap is independent of the collector failure, and in a completed envelope it would blank the night, so it must blank here too. Only the missing post is excused.

### A.4 Question 3: custody. Confirmed, with one caveat for S2.

The excuse is applied to a returned `PairVerdict` only, so every raise precedes it: amendment 29 on `session.json`, then rung (b) on the pre raw (P3-c). Amendment 30's journal raises do not apply in shape (iii) by design (P3-b), and no exclusion is involved in that. Amendment 32's step (1) carve-out (no authentication) must **not** be widened to cover shape (iii): that would skip rung (b) and swallow P3-c. Caveat: `CustodyFailure` is a `RuntimeError`, and the executor's `pilot_summary` guard catches only `(OSError, ValueError, KeyError, TypeError)` (`:1686`). Custody therefore propagates, which is correct, but it also skips `write_refusal` and `evidence_outcome.json`. S2 must not widen that `except` to catch it, and should state what outcome record a custody raise leaves (SHOULD-FIX for the S2 brief, outside text 6).

### A.5 Question 4: shape (iii) with `collector_exit == 0`: not honest; not excused.

Exit 0 requires `main` to return `int(session["error"] is not None) == 0` after `collect` returns, and `collect` returns only after `:1208` has written `end_stamp` (a failing write gives rc 2 via `except (OSError, ValueError)`, or a traceback). After exit, only `record_attestation` rewrites `session.json`, and it loses no key (P5). So exit 0 plus no `end_stamp` means a finished collector's record was altered. Minimum treatment: text 6 applies (the night is blanked, no excuse). My preference: raise `CustodyUnreadable("session.json lost end_stamp after collector exit 0")`, because the class rule says loss after the collector finished is custody, not status. If the judge prefers blanking, no number escapes either way. `pilot_summary`'s `entry.get("collector_exit", 0)` default must not feed this rule: an entry without the key is not exit 0. Today every executor entry carries the key (`:1621`), and S2 should make a missing key a `ValueError`.

### A.6 Question 5: `summarize` keeps text 6 (raise) on shape (iii).

`summarize` has no executor witness. The only way it could excuse shape (iii) would be on shape alone, and a stripped `end_stamp` reaches shape (iii) from a completed envelope whose journal failed custody. The excuse would then turn a would-be custody raise into a silent exclusion. `summarize` is descriptive (`evidence_status PROVISIONAL`), and the night's registered summary is `pilot_summary`, so the campaign cost of a raise there is an operator re-run, not a night. It raises on the non-pass verdict, names the envelope and says that shape (iii) is excusable only through `pilot_summary`'s executor witness. It never reads the provisional journal of a shape-(iii) session (today it would: `rglob("rounds.jsonl")` reads provisional rows into its aggregate).

### A.7 Honest shapes and paths the charge missed

1. **Shape (ii) with `collector_exit = 124`** (V2, V3): authenticated normally, already excluded `collect_error`, and the night follows its pair. No change is needed, but T6 should pin it.
2. **Shape (iii) with no kill** (P4, rc 1 or 2): covered by keying on `collector_exit != 0`, not on `124`.
3. **Today's observer-floor `ValueError`** (P2-a) on any shape-(iii) envelope with a readable provisional journal. An S2 that implements only "exclude as `collect_error`, do not blank" still refuses the night here. The excused envelope must leave `pilot_summary` through the unreadable-envelope branch: `error` set, `joules None`, `continue` before `all_rows.extend`, so it is outside `readable`.
4. **The refusal envelope (shape (i), exit 3) hits the same `ValueError`** (P2-c) and refuses the night today. This predates text 6 and is not shape (iii). Under text 5 the refusal envelope carries a full pair, so its battery verdict is benign, but the observer-floor loop still refuses the night. Flag for S2 (SHOULD-FIX): an envelope without `whole_envelope_observer_cpu_s` whose `collector_exit != 0` should be kept out of `readable`, with the reason recorded.
5. **Refusal-path timeout** (kill during text 5's refusal-path post read, before `:1081`): no `session.json` is written, so amendment 32's step (1) carve-out applies (`collect_error`). This is consistent, and no change is needed.
6. **Slow post `ioreg` in a completed envelope** (`timed_out`, exit 0): `evidence_missing`, and text 6 blanks the night. This is a probe failure, not a collector failure, and it lies outside this charge. It is the residual "one slow probe costs a night" case, and I record it without asking for a change.

### A.8 Question 6: T6 rows for S2 (call site `pilot_summary` / `summarize` → `authenticate_quiet_session`)

Build the shape-(iii) envelope through the real `collect`. Either use a round runner raising `SystemExit` in round 2 (the in-process stand-in the erratum used), or run P1-V1's subprocess with the real `cleanup_groups`. Then put the text-5 pre in the first write (after S2, the collector writes it itself).

- **T6-1** (core). Twelve-envelope night, envelope 02 shape (iii) with a float pre and 2 provisional rows, entry `collector_exit 124`. Expect: summary written; the status is not `BATTERY_FLOAT_*`; envelope 02 `excluded ⊇ {collect_error}`, `joules None`, `error` set; `battery_float_envelopes` lists index 2 with status `battery_float_evidence_missing`, reasons `("post evidence missing: phase not recorded",)`, `excused: "collector_failure_post_not_recorded"`. **RED vs naive text 6:** night blanked. **RED today:** `ValueError whole_envelope_observer_cpu_s … missing`.
- **T6-2**. The same envelope through an implementation that removes only the blanking. Expect T6-1's outcome. **RED:** the observer-floor `ValueError` (A.7 item 3).
- **T6-3**. The same envelope with the **charging** pre. Expect: night blanked `BATTERY_FLOAT_CONFOUNDED`. **RED vs "exclude every shape (iii) with exit ≠ 0":** the night proceeds.
- **T6-4**. The same envelope with the pre `exit_code 2`, stale, or malformed (three sub-rows). Expect: night blanked `BATTERY_FLOAT_EVIDENCE_MISSING`. **RED vs "excuse any `evidence_missing` shape (iii)":** the night proceeds.
- **T6-5**. The same envelope with pre **and** post recorded and `end_stamp` absent (P3-h), exit 124. Expect: blanked (reason `quiet span unavailable` is not excused). **RED vs "excuse on shape + exit + status":** the night proceeds.
- **T6-6**. The same envelope with `collector_exit 0`. Expect: blanked, or `CustodyUnreadable` if the judge adopts A.5's preference. **RED vs a shape-only rule:** excused.
- **T6-7**. The same envelope with the pre raw altered. Expect: `CustodyFailure` propagates and no `summary.json` is written. **RED vs an exclusion applied before authentication:** excluded, summary written.
- **T6-8**. P4's shape (rc 2, no kill, empty journal), entry `collector_exit 2`. Expect: T6-1's outcome.
- **T6-9**. A kill before the first journal append (first-write session with the pre, no `rounds.jsonl`), exit 124. Expect: T6-1's outcome (excused through authentication, not through step (1), because `session.json` exists).
- **T6-10**. `summarize` on the T6-1 directory. Expect: raise naming envelope 02, and no provisional row read. **RED vs a `summarize` that excludes shape (iii):** returns a summary.
- **T6-11**. V2's shape (ii) with `collector_exit 124` and a passing pair. Expect: excluded `collect_error`, night proceeds (pins A.7 item 1).

### A.9 My amendment 35 (for comparison with the ruling)

> 35. **Collector-failure excuse (amends text 6, `pilot_summary` only).** In `pilot_summary`, after amendment 32 step (2)'s `authenticate_quiet_session(out)` has returned a verdict (every `CustodyFailure` has already propagated), an envelope is **excused** iff all hold: (a) the executor entry carries `collector_exit` and it is non-zero (a missing key is `ValueError`); (b) the admitted `session.json` has a `battery_float` key, no `end_stamp`, and `error_class` is not `QUIET_REFUSAL_ERROR_CLASS`; (c) `session["battery_float"]` is a dict with no `post` key; (d) the verdict status is `battery_float_evidence_missing` and its reasons equal `("post evidence missing: phase not recorded",)` exactly. An excused envelope is appended to `values` with `excluded` containing `collect_error`, `error` = `"collector failed before its final record (shape iii); round journal not read"`, `joules`/`combined_joules`/`interior` None, and `continue`s before its `rounds.jsonl` is read and before `all_rows.extend`, so it is outside `readable` and the observer floor. It is listed in `battery_float_envelopes` (index, status, reasons, raw digests, `excused: "collector_failure_post_not_recorded"`) and does **not** set `status`/`evidence_status` or blank anything. Every other non-pass verdict, including `battery_float_confounded` and any reason naming the pre, follows text 6 unchanged. `summarize` excuses nothing: it raises on every non-pass verdict and never reads a shape-(iii) journal. The exclusion vocabulary and the registration digest `69321c69…` do not change.

## B. Refutation

Ruling read in full at 16:06 PDT (file complete; it ends with the plain summary for Ed). New probes: `/tmp/qpe3opus/p6_stale.py`, `/tmp/qpe3opus/p7_downgrade.py`. P7 applies a reference copy of amendment 35 item 4's predicate (unfinished ∧ executor witness ∧ status `evidence_missing`) and, beside it, the same predicate plus the structural clause proposed in B-2, both to verdicts returned by the merged helper.

**Where the ruling and Phase A agree (no finding):** F1 (SIGTERM storm), F2 false (the observer-floor `ValueError`), F3 (a no-kill path), and F4's reason string were reached independently by both seats with matching probes (ruling P-A/P-B against my P1/P2/P4). So were Q1 AMEND, Q2 confounded blanks, Q3 order, and Q5 KEEP for `summarize`. The executed agreement is evidence. The agreement of the two models is not. **F5 CONFIRMED** from the registration: `envelope_s 600`, `slot_pitch_s 620`, `start_drift_abort_s 2`, so a 630 s wait makes the next slot at least 10 s late. I had missed this.

**Where the ruling beat Phase A (I withdraw):** Phase A A.3 would blank the night on a stale, malformed or failed pre. The ruling excuses them, and on the numbers that is correct. P6 shows that staleness masks content: `parse` on `charging-synthetic-from-real.ioreg` at age 185 s raises `ProbeError: UpdateTime stale` before the predicate runs, so a stale charging reading reports as `evidence_missing`. Even so, no information is lost. Under the gate's own 180 s bound, a pre(k) reading older than 180 s at t≈620 predates post(k−1), taken at ≈600, and battery readings only advance. So post(k−1) read that same reading or a newer one, and it was gated on it: charging makes post(k−1) confounded, and staleness makes it evidence-missing. Either way the night blanks through envelope k−1. For k = 1 no interior precedes the pre. The ruling's own Q2 scenario (a fresh charging reading that appears between post(k−1) and pre(k)) is the one case where pre(k) carries unique evidence, and a confounded verdict covers it. My A.9 exact-tuple clause is withdrawn in favour of B-2's structural clause.

### B-1 SHOULD-FIX: item 3 ("`pass`: summarized as today") refuses the night on an honest network-time refusal envelope

Evidence: P7-d. A refusal-shape envelope with the full pair that text 5 (M1) obliges returns **`pass`**. P2-c: today's `pilot_summary` on a night holding a real refusal envelope (`collector_exit 3`) **raises `ValueError: envelope 2: whole_envelope_observer_cpu_s or envelope span missing`** at `:1324-1327`, and the executor books the night refused (`:1685-1686`). The refusal path returns before the `try`/`finally`, so it never records `whole_envelope_observer_cpu_s` or `end_stamp`, and its empty journal parses, which puts the envelope in `readable`. Amendment 35 routes only *unfinished* envelopes around the floor. Its item 3 sends a passing refusal envelope into the same raise it cures for unfinished ones. The cause is honest (the control record became unreadable in the middle of the night, `network_time_provenance` `:276-285`), and the class rule the ruling invokes ("never costs more than its own envelope's admission") is broken by the ruling's own item 3. No number is at risk. The defect is campaign cost, reachable but rare.

Replacement for item 3:

> 3. Verdict `pass`: the envelope is summarized as today, **except** that an envelope whose entry carries the executor witness and whose admitted `session.json` has no `whole_envelope_observer_cpu_s` (the refusal shape, which returns before the collector's `finally`) is appended through item 4's unreadable-envelope path, with `excluded` = the reasons already booked from the entry plus `incomplete_interior_support`, `error` = `collector did not finish: no whole_envelope_observer_cpu_s, collector_exit <code>`, and energy fields `None`. It blanks nothing and is left out of `readable`.

New T6 row: **T6-p.** Envelope 5 = the refusal shape with a passing pair (fixture `RoundThreeAuthenticationTests.quiet(refusal=True)`, `error_class network_time_provenance`, empty journal), `collector_exit 3`. Expect: summary written, `retained == 11`, envelope 5 excluded, and the status is not a battery status. **RED against the ruled text and today:** `ValueError … whole_envelope_observer_cpu_s or envelope span missing`.

### B-2 SHOULD-FIX: the excuse admits two shapes no honest collector writes, and one of them turns a journal custody failure into an exclusion (the erratum's residual-downgrade check no longer holds)

Evidence: P7.
- **P7-a** (control). A completed record whose journal row digest disagrees, `collector_exit 1`: **`CustodyFailure`**.
- **P7-a′.** The same record with `end_stamp` deleted: `evidence_missing ('quiet span unavailable',)`. **Ruled item 4: EXCUSED**, the night proceeds, and the journal is never read.
- **P7-b.** An unfinished record with no `battery_float` key, exit 124: `evidence_missing` (both phases not recorded). **Ruled item 4: EXCUSED.**
- **P7-c** (the honest shape, pre only), exit 124: excused under both predicates.

The erratum ruled R-2's residual downgrade safe **because** text 6 blanks: "stripping `end_stamp` from a completed envelope to reach shape (iii) yields a non-pass, which text 6 blanks; no number escapes". Amendment 35 removes that premise without re-checking it. After amendment 35, the same stripping on any envelope whose collector exited non-zero converts an amendment-30 journal custody raise into a `collect_error` exclusion, against the class rule "custody is never a status". Reaching it takes a deliberate edit of `session.json`, so under D-161 this is SHOULD-FIX, not BLOCKER. The fix costs no honest shape anything. Text 5 writes the post only in the final write, beside `end_stamp`, and writes the pre in the first write, so every honest unfinished record holds `pre` and no `post` (P1-V1, P4, ruling P-B, P-C K1–K3). The ruling forbids keying on reason strings, and this clause is structural.

Replacement for item 4's condition:

> 4. **Excused**, only when all four hold: the envelope is unfinished; the entry carries the executor witness; `session["battery_float"]` is a dict that has a `pre` key and **no `post` key** (text 5 writes the post only in the final write, so an unfinished record holding a post, or holding no battery record at all, was not written this way by the collector); the verdict's status is `battery_float_evidence_missing`. …

And add to item 5's list: "an unfinished envelope whose `battery_float` is absent, not a dict, lacks `pre`, or holds `post`".

New T6 rows: **T6-q.** P7-a′ (completed record, journal digest disagreeing, `end_stamp` stripped, exit 1): night blanked. **RED against the ruled text:** excused. **T6-r.** P7-b (no `battery_float` key, exit 124): night blanked. **RED against the ruled text:** excused. **T6-s** (paired control). P7-a with `end_stamp` intact: `CustodyFailure`, no summary.

### B-3 NIT: item 2's wording contradicts item 1

Item 2 says "no test of the exit code or of the shape may precede this call", but item 1 tests the exit code before any authentication. Replace it with: "apart from item 1's test, no test of the exit code or of the shape may precede this call."

### B-4 NIT: Q2's "a pre read that … is stale is absence" is right, but the reason given is not the reason it holds

P6: a stale reading's *content* can show charging, and `parse` hides it behind `ProbeError`. The excuse is safe only because post(k−1) necessarily read the same or a newer reading and was gated on it (argument above). Add one sentence to Q2 so a future change to the post's timing (for example, moving the post read later) is checked against it: "Safe because the previous envelope's post read is at most about 20 s earlier and battery readings only advance, so any reading pre(k) could see stale was already gated as post(k−1)."

### B-5 NIT: make T6-n deterministic

P1-V2 shows that a collector whose finalization completes within one 50 ms sweep survives the SIGTERM storm and writes shape (ii). T6-n's own `end_stamp`-absent assertion would catch that, but the test would then be timing-flaky. The injected recorder's `finish()` should block (for example `time.sleep(3600)`) so the second SIGTERM always lands inside the `finally`. Also add the P1-V2 control as **T6-t**: shape (ii) with `collector_exit 124` and a passing pair is summarized normally (excluded `collect_error`, night proceeds), which shows that the witness alone does not route a completed envelope around the floor.

### B-6 NIT (S2 brief, outside amendment 35): a custody raise leaves no custody text in the night's outcome

`CustodyFailure` is a `RuntimeError`, and the executor's guard at `:1686` catches only `(OSError, ValueError, KeyError, TypeError)`. Custody therefore propagates, correctly, out of `execute`'s `finally` before `write_refusal` and `evidence_outcome.json`. The courier then writes `refused` with the detail "chain ended without evidence outcome" (`run_night.py:1373-1385`). That outcome fails closed, but the custody text is lost from the record. S2 should print the exception to the chain log before it propagates, and must not widen `:1686`.

### Line-cite correction to Phase A

The observer-floor raise sits at `:1324-1327` (`readable` at `:1321`), as the ruling cites. My A.0 row P2-a said `:1321-1323`.
