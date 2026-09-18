# Opus pairing refuter on cold-gate ruling 71 — contract lens (session 5c919872, 2026-09-17)

Method: every `file:line` the ruling cites re-opened via `git -C
/Users/edr/code/JouleWise-wt-gate-quiet show 73cdbbc4:<path>` (HEAD verified, never edited),
plus `a90ab4e8:` / `5c5a3323:` and the records at main `f534a01f`. No suite, nothing armed. Charter digest recomputed: `099de884b1…c95d81`, matching the pin.

## 1. Q1 — the misquotation, and the CPython claim

**Where the clause originates — REFUTED in part (finding right, characterisation wrong).**

- Record 20:18 reads, verbatim: "No operation on the deadline-owning path … may wait for
  worker progress, EOF, filesystem completion, or child exit." Whole-file grep for `lock held`
  / `another thread` in record 20: **no match**; exhibit A §A4 quotes line 18 identically.
  CONFIRMED that record 20 lacks the clause and that the packet contradicts its own exhibit.
- But "is not the invariant as written **anywhere**" is **REFUTED**. The clause is written
  word for word at `22-brief-delta-reaudit-round-3.md:9` — the magistrate's own audit brief:
  "Any operation that can wait for worker progress, EOF, filesystem completion, **a lock held
  by another thread**, or child exit is a BLOCKER." Not packet fabrication but **brief drift**:
  the grading criterion (22:9) was stricter than the implementation contract (20:18), and the
  audit then recorded findings `against brief:18`. That `brief:` = record 20 is confirmed by
  F3's `brief:18,26` (20:26 = item 3, cancellation/reaping) and F4's `brief:36,38` (20:36/:38
  = items 8/9); record 22 has no line 26/36/38.
- So the packet's sentence is **true of record 22, false of record 20**, conflating the two.
  "False to the exhibit" is right on attribution but understates the defect: it is a drafting
  defect the magistrate owns and must not repeat in the round-4 audit brief.

**CPython claim — CONFIRMED.** `:2225` is `item = self.requests.get()`; `handle.write` /
`handle.flush` / `os.fsync` are `:2230-2232`, after `get()` returns and outside any mutex hold
(no `with self.requests.mutex` on that path). `Queue.get()` acquires `not_empty` (wrapping
`self.mutex`) and `Condition.wait()` releases the underlying lock while blocked, so the hold
spans the dequeue and `not_full.notify()` only. The launcher matches: `:2056` `get()`, with
`Popen.__new__`/`__init__` at `:2064-2067` outside the lock. `put_nowait` verified at `:2075`,
`:2078`, `:2253`, `:2263` — exactly F1's four sites. No production path holds the queue mutex
across I/O; F1's dissolution is sound.

**GIL argument — PARTIAL (rhetoric, not error).** "unsatisfiable by any threaded CPython
program (the GIL is such a lock)" strawmans 22:9, which plainly means explicit synchronisation
primitives; it does no work the replacement bar does not do better.

**Replacement bar's citations — CONFIRMED.** `CENSUS_INTERVAL_S = 30` at `run_night.py:65`;
`_BIND_JOURNAL_FLUSH_S = 1.0  # refusal cleanup only; never extends admission` at `:2003`.
Under that bar `Thread.start()`'s `_started.wait()` waits outside the ticker's control but
bounded small against 30 s, so F2 stays a NIT — consistent, but the round-4 brief must say so
or the next auditor re-raises F2.

## 2. Q2 — F3, and the "shrinking, enumerable set" reading

Every cited line CONFIRMED:

- `:2192` `if self.launch_done and (pid is None or self.reaped):`, inside `def poll_cleanup`
  (`:2178`), whose own comment at `:2179` reads "neither launch completion nor exit is awaited"
  — which `:2192` contradicts. A sharper statement of F3 than the ruling makes.
- `:2072` `task.launch_done = True` in the launcher `finally` (`:2070`), after
  `Popen.__init__` at `:2065-2067`. `:2049` is the docstring "Exec may wait for the
  executable's filesystem: do it off the ticker."
- `:2422` `if not jobs:`; the only `break`s are `:2424` (`writer.done`) and `:2427`, both inside
  it, and `:2425` `if time.perf_counter() >= cleanup_until:` likewise. So with one job that
  never reaches `launch_done`, `jobs` never empties, the budget is never consulted, and the
  REFUSED receipt is never authored. F3 is inside the pre-drawn class (filesystem completion).

**"19 of 26 kills" — CONFIRMED.** The JSON carries no count field, but the table resolves
exactly: each "startup/post" or "X; Y" row as two mutants, "remove fault ACKs" as one, and
"no-op supervisor" as the control not a mutant → 26 mutants, 19 killed, 7 survived; the
packet's survivor list also totals 7.

**"11 of 14 operation rows accepted" — REFUTED (packet), and the ruling missed it.** The
`operation_table` is a header plus **13** rows. Five carry a REJECT: startup (F2), census/start
(F1), reap/close (F3), journal (F1), finalize (F1); a sixth, ACK/failure/done, carries F6. Clean
rows are **7 of 13**, or 8 counting the F6 row — not 11 of 14. The packet reached 11 by
subtracting three *findings* from fourteen *entries including the header*. Ruling §7 missed it,
and §2 repeats a softer version by listing "**reap**" among the ACCEPTed rows when reap/close is
exactly where F3 sits ("ACCEPT ECHILD and pipe-close; final launch_done dependency REJECT F3").
**It strengthens the verdict rather than changing it:** once Q1 dissolves F1 and F2 the rejected
rows collapse from five to one, i.e. 12 of 13 clean with a single enumerable residue.

**Q2 conditions — CONFIRMED.** Audit V1 is `… PYTHONPATH=/tmp/refute-r3/audit_support …
python3 -B -m unittest` over six modules, observed `Ran 341 tests in 171.428s` /
`FAILED (failures=2, skipped=9)`; the two failures are unnamed anywhere in record 23 and the
injected `PYTHONPATH` is the likely cause — making the "green six-module run on its own
interpreter" condition exactly right. `21-full-replay-73cdbbc4.log` is 0 bytes (§C2).

## 3. Q3 — the four boundary conditions

- **(1) CONFIRMED with a citation defect.** `:2755-2758` is `elif plan.quiet_admission is not
  None: receipt = bind_until_quiet(…)` — a true v4 dispatch, outside the round-3 hunk
  (`@@ -1991,262 +1992,669 @@`, new lines 1992–2660; the only other hunks are the import and
  the parser lines at 3349/3367). **But `:298` is NOT a dispatch site**: it is
  `if plan.quiet_admission is not None:` inside `def _write_driver_refusal` (`:286`), adding
  `top_consumers_at_decision` to refusal evidence. The conclusion — PR 1 necessarily touches
  the driver — survives on `:2755` plus `:298` being a genuine v4-conditional driver site.
- **(2) CONFIRMED.** `prepare_result_descriptor` is `:293-296`, `publish_observation`
  `:298-316` (the ruling's single span names the second only — cite both); the diff against
  `5c5a3323` shows `+def prepare_result_descriptor`, `+def publish_observation`, `+def main`,
  all round-3 additions; `--observation` handling at `:329-334`. Exhibit C §C5 does put all of
  `quiet_admission.py` on the gate side, so the file/feature disagreement is real.
- **(3) CONFIRMED.** `quiet_admission.py:336` is `from scripts.run_night import
  smoke_observation_round`; that function is defined at `run_night.py:2559` (inside the round-3
  hunk) and grepping it on `5c5a3323:scripts/run_night.py` returns **nothing**. At a PR-1 head
  excluding the hunk the flagless CLI raises ImportError.
- **(4) CONFIRMED** — a statement about an unbuilt tree; nothing to falsify.

## 4. Q4 — CONFIRMED, with the same `:298` correction

At `a90ab4e8`, `from_mapping` (`:213`) computes `expected_keys` at `:218` with no quiet branch
and raises `PlanError("night_plan_malformed", "plan keys are not exact…")` at `:230-233`, with
the schema raise at `:234-238`; a v4 mapping is rejected there as an *unknown key* — by
accident, exactly as the ruling says. At `73cdbbc4`: `:231` `is_quiet = value.get("schema") ==
QUIET_PLAN_SCHEMA and not is_pack`, `:233-234` adds `quiet_admission` to `expected_keys`,
`:237-238` swaps in `QUIET_PLAN_SCHEMA`/`_VERSION`. Accepts. CONFIRMED. Re-aim the remedy:
`:2755` is the site needing the fail-closed refusal; `:298` is already on the refusal-authoring
path, and converting it is a mistake a round-4 seat could make from the ruling's wording.

## 5. Q5 — CONFIRMED on the code, PARTIAL on actionability

`:329` `if args.observation:`; `:330-331` the `parser.error('--observation requires --job-id
and --result-fd')` guard; `:332-334` `prepare_result_descriptor` then
`publish_observation(args.result_fd, args.job_id, lambda: sample_interval(…))`, writing one
length-prefixed frame (`:310-314`) and printing nothing; `:336` the excluded import. All
CONFIRMED. `sample_interval` runs no census — that lives in `smoke_observation_round`
(`run_night.py:2559-2563`, docstring "production exec, census and journal work"). Exhibit F
§F1 row Q5 confirms the observer floor is provisional pending census-inclusive re-measurement
in lane 232. **PARTIAL only on form:** a bare "Q5 REJECT" over-blocks, since §5 then permits the
same sampling through a harness supplying the pipe and decoding the frame. Record that route
beside the verdict.

## 6. Charter compliance — CONFIRMED

One verdict per question (REJECT / AFFIRM / AFFIRM / AFFIRM / REJECT); a severity tier on each
(MATERIAL, BLOCKER-class, MATERIAL, BLOCKER-if-omitted, MATERIAL); §9's "explicit
justification" present and argued from the pre-drawn partition (§2); §6 hygiene section present
(§7), naming five defects; no rule, decision-log entry, contract or pre-registration amended —
the replacement bar sits inside Q1's own "If REJECT: state the bar that replaces it" mandate;
one file written; 12 436 B < 14 KB. Exhibit B spot-check: `:2050`, `:2225`, `:2422` verbatim.

## 7. Errors, ordered by materiality

1. **`run_night.py:298` is not a dispatch site** (§3 cond. 1, §4): it is inside
   `_write_driver_refusal` (`:286`). Verdicts unchanged, but the Q4 *instruction* is mis-aimed
   and would mislead a round-4/PR-1 seat. The dispatch is `:2755-2758`; `:298` is a
   v4-conditional refusal-evidence site PR 1 may keep.
2. **"the invariant as written … anywhere" is false** (§1): the clause is at record `22:9`,
   the magistrate's own audit brief. Q1's verdict is unchanged, but the defect is brief drift,
   not packet invention; the fix belongs in the round-4 audit brief — grade against the
   implementation contract, and widen 20:18 first if the bar is to be widened.
3. **The packet's "eleven of the fourteen rows" is wrong** (7–8 of 13); §7 missed it and §2
   compounds it by listing "reap" as ACCEPTed when F3 lives on that row. Verdict unchanged and
   in fact strengthened, but the arithmetic must not be quoted forward.
4. Cosmetic: `quiet_admission.py:298-316` covers `publish_observation` only
   (`prepare_result_descriptor` is `:293-296`); the GIL strawman in §1; Q5's verdict line
   under-serving its own body.

Nothing above reverses a verdict; §2's F3 case is in fact *stronger* than stated, since
`poll_cleanup`'s own comment at `:2179` asserts the property `:2192` violates.

## 8. Verdict

**The magistrate may act on ruling 71 as written, with four corrections carried into the
round-4 brief rather than a re-ruling.** Every load-bearing line resolves: F1's dissolution is
correct on CPython `Queue`/`Condition` semantics and on the four `put_nowait` sites; F3 is real,
sits inside the partition drawn before it, and is one predicate plus one launcher-side
kill-on-cancel; the split's four boundary conditions each hold against the code and exhibit C
§C5; the v4 parser really does flip from accidental rejection at `a90ab4e8` to acceptance at
`73cdbbc4`, so Q4's code-enforced refusal is required; and Q5's premise really is wrong in kind.
Corrections: (a) re-aim Q4 and Q3-cond-1 at `:2755-2758`, stop calling `:298` a dispatch site;
(b) record that the clause originates at audit brief `22:9`, not nowhere, and forbid the round-4
audit brief from grading against a bar the implementation brief does not state; (c) restate the
operation-table arithmetic as 7–8 clean of 13 now, 12 of 13 once F1/F2 dissolve, dropping
"eleven of fourteen"; (d) transcribe Q5's REJECT with its permitted harness route. Round 4
scoped to F1–F6 under the replacement bar, fifth round forbidden, split held as fallback, is
supported by the record as verified.
