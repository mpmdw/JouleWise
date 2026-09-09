# Cold-gate ruling — PR #309 replay door after two attempts (follow-up to ruling 44 Q2)

Judge: Claude Fable 5.1, single non-interactive session, convened 2026-09-09 08:42 PDT, ruling written 08:47 PDT. Working tree:
detached worktree `/Users/edr/code/JouleWise-wt-idle-rc` at `a3da3463` (origin/main), clean. Packet hashes verified: 12/12 OK
against `55-coldgate-packet.sha256` (`shasum -a 256 -c`). Read in full: packet index, charge, P1 (44), P2 (45), P3 (53), P4 (54),
P5 (55 kernel row), P6 (42 + addendum; 39b log heads/tails), P7 (31: lines 1–14 and 40–69, i.e. forcing defect, prune, bench,
lineage, verdict, addendum).

## Contamination disclosure

Written before any packet body was read beyond the index and the charge.

1. The harness injected, without my asking, the contents of the user's global `~/.claude/CLAUDE.md` (multi-model orchestration and the
   writing standard), the worktree's tracked `CLAUDE.md` (Codex bridge notes), and the auto-memory index `MEMORY.md` (one-line pointers
   only, not memory bodies). I did not open any memory file, RUN_STATE.md, TASK_QUEUE.md, docs/decision_log.md, AGENTS.md, or any skill.
2. The MEMORY.md index lines that bear on this question and that I therefore cannot un-see: a "Checkpoint 2026-09-09" line stating PR #308
   is merged and "PR #309 next" and that "Low Power Mode attribution WITHDRAWN"; a "Codex delegation growth" line stating "harness denies
   agent self-merge, Ed names merges"; a "Merge authority with review" line about a standing self-merge rule; and a "Threat-model prune
   (D-161)" line ("fail-closed only for physics/evidence/pre-registration"). I treat none of these as evidence. The packet's P6 addendum
   itself records the Low Power Mode attribution as withdrawn, so on that point the index and the packet agree and I rule from the packet.
3. The system prompt's git-status block showed the five most recent main commits (a3da3463 … 9c38c259) and their subjects. These are
   read-only git facts I would have been allowed to probe anyway.
4. I have no loop context, no prior session memory of rulings 44/45, and did not consult any other model or agent.
5. The charge's Q1 carries an "(Expected: no …)" parenthetical. I note it as a framing pressure and answer Q1 from P1's text.
6. General knowledge used: Python `threading.Thread.join(timeout=…)` semantics, unittest sharding, macOS timer behaviour.

## Probes executed

All foreground, all read-only except one test run that writes only to a `tempfile` directory it removes. No background tasks, no
subagents, no watchers.

```
$ git rev-parse HEAD ; git status --short                       → a3da3463686b8f66cf1ba5e1c742bd22de51a876 (clean)
$ cd /Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest && shasum -a 256 -c 55-coldgate-packet.sha256
                                                                → 12 files OK

# PR integration tree (read-only)
$ cd /Users/edr/code/JouleWise-wt-night-gate-stub && git rev-parse HEAD → 6d76f9647104d74b7b23cad945adaaf908eec0fd (clean)
$ git log --oneline -3          → 6d76f964 Merge origin/main into fix/…night-gate-stub-chain ; a3da3463 README… ; dd135364 Merge…
$ git merge-base --is-ancestor a3da3463 HEAD                    → yes (integration tree = main a3da3463 + the branch)
$ git diff --stat a3da3463..HEAD -- joulewise scripts tests
   joulewise/night_gate.py 120 | scripts/run_night.py 7 | tests/test_night_gate.py 61 | tests/test_run_night.py 45   (4 files)
$ git diff --name-only a3da3463..HEAD  → + docs/contracts/pack_night_go_receipt.md (5 files total; matches charge A2 list)
$ grep -l -E 'night_gate|run_night' tests/test_run_campaign.py tests/test_arm_readiness_lifecycle.py tests/test_docs_freshness.py
      joulewise/adapters/powermetrics.py joulewise/uncertainty_evidence.py joulewise/controller.py joulewise/cli.py
      scripts/run_campaign.py tests/fixtures/fake_powermetrics_process.py                          → no hits (charge A2 grep confirmed AS RUN)
$ grep -n -E '^(from|import) ' tests/test_arm_readiness_lifecycle.py | head
   line 20: import joulewise.arm_readiness as readiness ; line 36: from scripts import generate_arm_readiness … ; lines 85–89: loads
   scripts/launch_window.py by importlib as `launch_window`
$ grep -n -E 'night_gate|run_night' joulewise/arm_readiness.py
   9933:    from joulewise.night_gate import NightPlan, PlanError                 (inside def _admit_pack_launch_go, line 9925)
   9975:    from joulewise.night_gate import NightPlan, PlanError, AGENT_CENSUS_ARGV (inside def _authenticate_pack_launch_go, 9966)
$ grep -n -E 'night_gate|_admit_pack_launch_go' scripts/launch_window.py
   22: _admit_pack_launch_go (import) ; 121: go = _admit_pack_launch_go(night_plan=args.night_plan, …)   ← the race test's launch() path
$ git diff a3da3463..HEAD -- joulewise/night_gate.py | grep '^@@'   → ONE hunk: @@ -1040,64 +1040,78 @@ def evaluate_night(…)
$ awk … 'def evaluate_night' span                                 → lines 945–1338 (the hunk is inside it)
$ git diff … | grep -E '^[-+].*(class NightPlan|class PlanError|AGENT_CENSUS_ARGV|^[-+]def |^[-+]class )'   → no hits
$ grep -rn 'evaluate_night(' joulewise scripts | grep -v 'night_gate.py\|run_night.py'   → no hits (only night_gate.py and run_night.py call it)
$ sed -n 840,900p tests/test_arm_readiness_lifecycle.py           → 8 consumer threads on a Barrier(8); `thread.join(timeout=30)` each;
   assertion at line 891: `assertFalse(any(thread.is_alive() …), "every concurrent consumer must reach a recorded outcome")`

# Machine state, 08:44 PDT
$ pmset -g custom                       → Battery Power: powermode 0 ; AC Power: powermode 1   (unchanged from P6)
$ python3 -c "…sleep(0.05)×20…" ×3      → 0.1785  0.1845  0.1855   (3.57×, 3.69×, 3.71× nominal — ABOVE the charge's 2.1–3.6× band)

# CI
$ gh pr checks 309                      → gate-ledger FAIL (by design); build, installed-wheel, pr-fast (1,2), calibration-exits-exclusive
                                          (3.11, 3.14), calibration-writer-crash-matrix-exclusive ×4, test (3.11, 1–4), test (3.14, 1–4): ALL PASS
$ gh pr view 309 --json headRefOid,mergeable,state → head 6d76f964, MERGEABLE, OPEN   (A5 is now satisfied at the integration head, not pending)

# The one allowed alone run (08:45:00–08:45:24 PDT)
$ cd /Users/edr/code/JouleWise-wt-night-gate-stub && PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= \
    python3 -m unittest tests.test_arm_readiness_lifecycle -k test_atomic_launch_capability_race
   → Ran 1 test in 24.408s / OK / rc=0          (alone in-process; magistrate's 3/3 becomes 4/4; run while my own session was the only
                                                  test process I know of — I did not census the machine)
```

Not probed: A4 (`tests.test_night_gate tests.test_run_night` on 6d76f964) — not in my allowed set, and it is the magistrate's obligation;
the 71-test class; the full suite; whether the race test fails under four-shard concurrency on demand.

## Q1 — Does attempt 2 (P4) satisfy A1 as written?

**No.** A1 reads: failures = *exactly* the named set of four, "A fifth failure, any error, a different test name, or a different
assertion line is a hold — no 'near enough'." Attempt 2 records `failures=5` with a fifth test name
(`test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`)
at a different assertion line (`tests/test_arm_readiness_lifecycle.py:891`). By P1's own words attempt 2 is a hold. Attempt 1 (P3)
likewise: five failures, the fifth `test_docs_freshness…test_current_sections_do_not_copy_volatile_literals`. Neither replay discharges
row 9 under ruling 44 as written. The magistrate was right not to merge on either, and right not to run a third four-shard attempt on
the same terms.

## Q2 — The one acceptable path today

**Ruling: (b), restricted to this PR, this head, and this one named extra failure — NOT the general amendment of A1 that option (b)
proposes.** In the charge's own labelling this is (d): "attempt 2 accepted under a named, structurally-shown waiver," and I set out
why the general clause is refused.

### Why not (a), (c), or a third four-shard replay

- **(a) sequential replay.** It would remove shard concurrency, which is the only plausible cause of the race test's 30 s join
  overrun, so it would likely cure failure 5. It would NOT cure failures 1–4: the slack right now is 3.6–3.7× against a fixed 3.5×
  fixture-timeout margin, and P6's own 39b logs show the "four" are not a stable set even alone (`failures=4`, `4`, `3`). A 3–4 h
  serial run can therefore return three of the four, which also fails A1's "exactly" in the other direction, and the magistrate would
  be back here. Its information value on failure 5 is already delivered more cheaply by four alone runs plus the structural argument
  below. Cost 3–4 h of a machine that the packet says is needed for nights; gain nil in soundness.
- **(c) hold.** The trigger "until the machine's timer-slack state changes" has no defined observable now that the Low Power Mode
  attribution is withdrawn (P6 addendum; P2 R1). The fixture lane has no date. Meanwhile the PR cures the defect that made
  rehearsal-20260909 refuse with `night_probe_error` (P7 forcing defect), and every further stub or real night is blocked on it.
  Holding a review-clean four-file cure on an unattributed machine nuisance that reproduces on main itself buys nothing.
- **Refuter's rc-0-with-retries (P2).** Not available today: 39b shows three alone attempts of the class, none green; the slack is
  higher now than when the refuter measured. "Retry until green" would be round three and beyond with no mechanism change.
- **A third identical four-shard attempt.** Refused. Both extras are already explained (attempt 1: a main commit since cured; attempt 2:
  a join timeout under concurrency, green alone 4/4). A third run either repeats one of the known extras or surfaces a new one, and in
  neither case does it add evidence about PR #309. It would also be the escalation the packet's own rule forbids.

### Why the restricted (b) is sound for a code PR

P1 gave a code PR a narrower door than a docs PR because independence "must be shown, not assumed." For failure 5 it is shown, and
the showing is structural, not statistical:

1. **The PR's only code hunk cannot execute on the race test's path.** The whole `joulewise/night_gate.py` diff is one hunk inside
   `evaluate_night` (lines 945–1338; hunk at 1040–1104 of the new file), and `evaluate_night` is called only from `night_gate.py` and
   `scripts/run_night.py`. The race test drives `scripts/launch_window.py:launch`, which reaches `night_gate` only through the
   function-local import at `joulewise/arm_readiness.py:9933` (`NightPlan`, `PlanError`), and the diff touches neither class nor any
   module-level statement. So the PR changes no byte the race test executes.
2. **The failure mode is load, not logic.** The assertion at line 891 fails when any of eight consumer threads is still alive after a
   30 s `join`. The test's other assertions (exactly one `execve`, one `launch_consumption_invalid`, seven `readiness_record_consumed`)
   were never reached. A thread still running after 30 s under four concurrent shards on a machine with 3.6× timer slack is the
   shard-concurrency signature, and it passes alone 4/4 (23.7, 23.5, 23.6, 24.4 s) on the same head.
3. **Failures 1–4 are the P1 set exactly**, same names, same line 9581, same message, and reproduce on main-equivalent trees (P6, 39b).
4. **CI is green on the integration head** (my `gh pr checks 309`: every build/test job passes at 6d76f964; only `gate-ledger` red by
   design). The charge's "pending at 6d76f964" is now stale in the PR's favour.
5. **Nothing else changed in the door.** A2 (pathspec ∅ — my diffstat) holds, A3 holds, A6 (addendum) is re-imposed below.

### Why the general amendment is refused

The proposed clause — "OR any extra failure that passes alone 3/3 and belongs to a registered load-sensitivity lane (P5)" — is an
open-ended absorber: it would let every future concurrency flake through on a 3-run alone pass plus lane membership, with no
requirement that anyone show the PR under review cannot reach the flaking code. That is the erosion P2 warned of (a recording
obligation wearing a gate's clothes). Also P5 does not name this test: its goal is ARM/launch fixture determinism through
probe-result seams and its evidence is `readiness_clock_preflight_refused` occurrences; membership of a thread-join timeout in that
lane is by family, not by registration. So: no standing rule. Each extra failure, on each PR, gets its own named structural showing
or it is a hold. P1 C4 (no precedent) stands.

### Exact conditions (all mandatory; any miss is a hold)

- **W1.** The merge is of head `6d76f964` exactly. If the head moves for any reason, every condition below is re-established on the new
  head; this ruling does not travel.
- **W2.** Row 9 is discharged by **waiver**, recorded with the verbatim tails of BOTH attempts (P3 and P4 headers and `WORKERS SUMMARY`
  lines and `rc=1`), all five failure names of each attempt, and the independence showing for each extra (wording in Q3). It is never
  recorded as "pass", "green", or "effectively clean".
- **W3.** A4 is run on `6d76f964` before merge: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate tests.test_run_night`
  in `/Users/edr/code/JouleWise-wt-night-gate-stub`, tail and rc pasted into row 9. Anything but `OK` / rc 0 is a hold. (P7 recorded
  136 tests OK on the branch worktree at 5db38b58; the integration tree has not been run. It is ~9 s.)
- **W4.** A5 as observed by me at 08:44 (all build/test checks pass at 6d76f964) is quoted in row 9 with the run URL prefix
  `actions/runs/34365694272`; if CI re-runs before merge it must still be green.
- **W5.** The alone re-run count for the race test is recorded as 4/4 on 6d76f964 (three magistrate, one cold judge, times above), and
  the row says "alone in-process; machine census not recorded".
- **W6.** No further four-shard replay for this PR. A serial replay is NOT required.
- **W7.** The addendum obligations in Q3 are written into the row at merge time, not later.
- **W8.** P7's verdict sentence gets a second dated addendum citing this ruling (the first addendum cites 44 and says "any other failure
  or error is a hold"; that sentence is now superseded for this one named failure on this one head).

## Q3 — Ledger row-9 wording and what the addendum must record

### Row 9 text (paste, then fill the two bracketed items)

> **Row 9 — Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded: DISCHARGED BY WAIVER
> (cold gate 44 Q2 A1–A6, as applied by cold gate 56 W1–W8), not by pass.**
> Attempt 2, integration tree `6d76f964` (5db38b58 + main a3da3463), four shards concurrent, started 07:45:08 PDT 2026-09-09
> (`54-replay-309-attempt2-6d76f964-tail.txt`): `WORKERS SUMMARY shards=4 modules=221 tests=5642 failures=5 errors=0 skipped=108
> failed_shards=3,4 result=FAIL` / `rc=1`. Failures: (1–4) `test_run_campaign.IdleAdmissionCoreVerdictTests.
> {test_cpu_admission_reads_final_attempt_telemetry, test_environment_refusal_does_not_hide_valid_retry_telemetry,
> test_missing_final_attempt_telemetry_fails_closed, test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound}`, each at
> `tests/test_run_campaign.py:9581` `AssertionError: False is not True` — the exact ruling-44 set; pre-existing on the merge base in the
> same machine state (44 A3; 39b alone on 5d13d0e6: failures 4/4/3; wall-clock fixture timeout margin 3.5× vs measured slack 3.6–3.7× at
> 08:44; lane FIXTURE-TIMEOUT-WALLCLOCK-01; Low Power Mode attribution withdrawn, 42 addendum). (5)
> `test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`
> at `tests/test_arm_readiness_lifecycle.py:891` (a consumer thread still alive after `join(timeout=30)` under four-shard concurrency;
> the test's outcome assertions were not reached) — passes alone in-process on 6d76f964 4/4 (23.699, 23.499, 23.587 s magistrate;
> 24.408 s cold judge 56; machine census not recorded). Independence of (5) from this PR, shown structurally: the PR's only code hunk in
> `joulewise/night_gate.py` is `@@ -1040,64 +1040,78 @@` inside `evaluate_night` (945–1338); `evaluate_night` is called only from
> `night_gate.py` and `scripts/run_night.py`; the race test's path (`scripts/launch_window.py:121` → `arm_readiness._admit_pack_launch_go`)
> reaches `night_gate` only via the function-local import of `NightPlan`/`PlanError` at `joulewise/arm_readiness.py:9933`, whose
> definitions and every module-level statement are untouched by the diff. Attempt 1, integration tree `dd135364`, started 06:49:41 PDT
> (`53-replay-309-attempt1-dd135364-tail.txt`): same summary line with `failures=5`, the four above plus
> `test_docs_freshness.DocsFreshnessTests.test_current_sections_do_not_copy_volatile_literals`, caused by main commit 0d9881ef (README
> blurb) and cured on main at a3da3463 (main CI green). Pathspec: `git diff --stat a3da3463..6d76f964 -- joulewise scripts tests` =
> night_gate.py, run_night.py, test_night_gate.py, test_run_night.py only; grep for `night_gate|run_night` over the nine failing-path
> files = none. No third four-shard replay was run (escalation rule); no serial replay required (56 Q2). A4 on 6d76f964:
> `python3 -m unittest tests.test_night_gate tests.test_run_night` → [PASTE TAIL: `Ran N tests in … / OK`, rc 0]. A5: CI at 6d76f964
> run 34365694272, all build/test checks pass, gate-ledger red by design. Waiver is for PR #309 at head 6d76f964 only; no precedent
> (44 C4); the general "extra failure passes alone 3/3 + registered lane" clause was REFUSED (56 Q2). Addendum obligations: see
> [ADDENDUM-1..3 below, written now, filled later].

### What the later addendum(s) must record

- **ADDENDUM-1 (the four; inherited 44 C3/A6, retargeted).** Trigger: whichever comes first of (i) FIXTURE-TIMEOUT-WALLCLOCK-01 merged,
  (ii) the charge's timer probe reading ≤ 2.0× nominal (≤ 0.100 s per 50 ms sleep) on three consecutive samples, or (iii) Ed toggling
  Low Power Mode off and the probe being re-taken. Action: run `tests.test_run_campaign.IdleAdmissionCoreVerdictTests` (71 tests)
  alone in-process on then-current main; paste tail + rc + the probe readings before and after. If not green under condition (i) or
  (ii), the four are an open defect on main with their own lane; the merge stands; the record must say so.
- **ADDENDUM-2 (the race test).** On the NEXT full-suite four-shard replay on any integration tree (the next PR's row 9), record whether
  `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses` passed under concurrency, with the shard count and the
  timer-probe reading at start. If it fails again under concurrency, ARM-INTEGRATION-LOAD-01 (P5) must be amended to name it and its
  30 s join explicitly, and no further waiver is available for it on any PR until that lane lands.
- **ADDENDUM-3 (row wording).** Ed's answer to the refuter's proposal (45, contract-lens) that row 9 be reworded to "rc=0, or a written
  waiver naming the failing set, its independence showing, and its discharge". Until answered, every non-green row 9 is a rule-11
  trigger, as it was here.

## Q4 — Over-stated lines in the packet or the charge

1. **Charge, context: "no failing-path module imports night_gate or run_night (grep at the integration head)".** True for the grep as
   run (I reproduced it: no hits in the nine named files). Over-stated as a statement about attempt 2's fifth failure: the failing
   module imports `joulewise.arm_readiness`, which imports `night_gate` at `arm_readiness.py:9933` and `:9975`, and the race test's
   launch path executes the first of those (`scripts/launch_window.py:121`). Independence holds on the narrower ground in Q2
   (the hunk is confined to `evaluate_night`, unreachable from that path), and the row must state that ground, not the grep.
2. **Charge, context: "The machine's timer slack today is 2.1–3.6× (P6)".** That band is the refuter's 06:00–06:06 sample. At 08:44
   my three readings were 3.57×, 3.69×, 3.71×. "Today" should read "at 06:00–06:06"; the slack is not bounded above by 3.6×.
3. **Charge A3 / packet P6 line: "the four fail alone".** 39b attempt 3 recorded `failures=3`. The set is not stable even alone;
   ruling 44's "exactly the set … no near enough" is therefore under-specified for a run that shows a subset. My row wording treats a
   subset of the four as within the waiver (fewer pre-existing failures is not new information about the PR) and requires it verbatim.
4. **Packet index, header: "two consecutive replay attempts failing with the same signature".** They did not: attempt 1's extra was a
   docs-freshness literal check broken by a main commit; attempt 2's was a thread-join timeout. The common factor is only "one extra
   failure not caused by the PR". Rule 11 alone justified convening; the escalation-rule citation is loose.
5. **Charge A5: "pending at 6d76f964".** Stale, not wrong: at 08:44 every build/test check passes at 6d76f964.
6. **Charge (c): "Ed's Low Power Mode toggle is the cheapest unproven experiment".** Cheap, yes; but the packet's own P6 addendum and
   P2 R1 show powermode 1 is neither sufficient nor stable-effect, so the toggle is a comparability nicety for real nights, not a
   plausible cure for these tests. It should not be offered as the observable that ends a hold.
7. **Charge (b): "belongs to a registered load-sensitivity lane (P5)".** P5 does not register this test or this failure mode; it
   registers ARM/launch fixture determinism with `readiness_clock_preflight_refused` evidence and itself flags "census causation is
   unproven". Membership is by family. The row must not say "registered for this test".
8. **P4 header: "alone in-process (four shards concurrent)".** Correctly qualified; the alone re-run line "attempt 1/2/3 … OK" should
   carry the same "machine census not recorded" qualifier the P6 addendum adopted.
9. **Not over-stated:** P7's forcing defect and the review lineage; the charge's A2 file list (matches `git diff --name-only`); the
   packet's hash discipline (this time all seven packet files plus the charge and the 39b logs are pinned, and they verified).

## Verdict summary

- **Q1:** No. Attempt 2 records five failures; ruling 44 A1 says a fifth failure is a hold, no near enough. So does attempt 1.
- **Q2:** Path (b) restricted, i.e. (d): accept attempt 2 as the row-9 replay record for PR #309 at head 6d76f964 only, under a written
  WAIVER whose independence showing for the fifth failure is structural (PR hunk confined to `evaluate_night`, unreachable from the race
  test's path; join-timeout failure mode; alone 4/4). Conditions W1–W8: same head, waiver wording, A4 green on the integration tree
  before merge, CI green quoted, alone count recorded, no third four-shard replay, no serial replay, addenda written at merge time, P7
  amended. The general "any extra failure that passes alone 3/3 + lane" amendment to A1 is REFUSED; no precedent.
- **Q3:** Row-9 text supplied verbatim above with two fill-ins (A4 tail; addendum pointers). Addenda: (1) 71-test class green after
  the fixture lane lands or slack ≤ 2.0× or Ed's toggle, else open defect on main; (2) the race test's behaviour on the next four-shard
  replay, with lane amendment if it fails again; (3) Ed's ruling on rewording row 9 to "rc=0 or written waiver".
- **Q4:** The charge's import-independence sentence is over-stated (the failing test's path does import `night_gate`; independence
  rests on the hunk's location instead); "today's slack 2.1–3.6×" is stale (3.6–3.7× now); "the four fail alone" hides a 3-failure run;
  "same signature" is not accurate; A5 is stale in the PR's favour; the Low Power Mode toggle is not a hold-ending observable; P5 does
  not register this test.
