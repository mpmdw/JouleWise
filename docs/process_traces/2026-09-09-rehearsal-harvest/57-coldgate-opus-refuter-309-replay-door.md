# Cold-gate refuter (Opus, CONTRACT lens) — PR #309 replay door after two attempts

Fresh read-only Opus refuter paired with the cold Fable judge, on the follow-up packet 55 / charge 56. Worked in the detached
worktree `/Users/edr/code/JouleWise-wt-idle-rc` at `a3da3463686b8f66cf1ba5e1c742bd22de51a876` (origin/main), clean; the PR tree
`/Users/edr/code/JouleWise-wt-night-gate-stub` (6d76f964) was read-only for me. Read: 55, 56, 53, 54, 44 (P1), 45 (P2), 55-kernel-row
(P5), plus primary source in both trees. Did NOT read 56-coldgate-ruling-* (it did not exist when I finished), RUN_STATE,
TASK_QUEUE, decision_log, CLAUDE*, AGENTS, skills or memory files. All probes foreground; no subagents; no background tasks.
Contamination note: the harness injects the global CLAUDE.md, the repo CLAUDE.md/CLAUDE.local.md and the memory INDEX headlines
into my system prompt before I read anything; I ruled from packet + probes, and where a conclusion agrees with one of those lines
the reason given is the probe.

## Probes executed (commands + tails)

1. `shasum -a 256 -c 55-coldgate-packet.sha256` → **12/12 OK**. (P2's item 6 complaint from the last gate is cured: P1–P7 are
   pinned this time, not just the packet and charge.)
2. `git rev-parse HEAD` in my tree → `a3da3463…` ; `git status --short` → clean.
3. `git diff --name-only 83ab38ed..5db38b58` → exactly the five PR files
   `{docs/contracts/pack_night_go_receipt.md, joulewise/night_gate.py, scripts/run_night.py, tests/test_night_gate.py,
   tests/test_run_night.py}`. **Confirms the packet.**
4. `git diff --stat a3da3463..6d76f964` (integration head vs *current* main) → same five files, 225 ins / 100 del.
   `git diff --stat 83ab38ed..6d76f964 -- joulewise scripts tests` → the four code/test files + `tests/test_gen_state.py 5 ++`
   (that last one arrives from main via #308, not from #309).
5. **A2 grep, run verbatim from the charge, in BOTH trees:**
   `grep -ln "night_gate\|run_night" joulewise/run_campaign.py joulewise/controller.py joulewise/cli.py joulewise/adapters/powermetrics.py joulewise/uncertainty_evidence.py scripts/run_campaign.py tests/test_arm_readiness_lifecycle.py joulewise/arm_readiness.py`
   → `grep: joulewise/run_campaign.py: No such file or directory` (that path does not exist; the real file is
   `scripts/run_campaign.py`, 351 KB) and **`joulewise/arm_readiness.py` MATCHES**, exit 2.
   The matches: `arm_readiness.py:9933  from joulewise.night_gate import NightPlan, PlanError` /
   `:9975  from joulewise.night_gate import NightPlan, PlanError, AGENT_CENSUS_ARGV` /
   `:10111  # Existing run_night._census_record transport, retained as`.
   And `tests/test_arm_readiness_lifecycle.py:20  import joulewise.arm_readiness as readiness`.
6. Reachability follow-up: `git diff 83ab38ed..6d76f964 -- joulewise/night_gate.py | grep -c '^@@'` → **1** hunk,
   `@@ -1040,64 +1040,78 @@ def evaluate_night(plan: NightPlan, probes: Probes, …)`; `def evaluate_night` is at :945, while
   `AGENT_CENSUS_ARGV` (:42), `class PlanError` (:159), `class NightPlan` (:195) are far outside the hunk.
   `grep -rn evaluate_night joulewise scripts tests` (excluding night_gate.py) → only `scripts/run_night.py:42,1503,1515`,
   `tests/test_run_night.py` (6 sites), `tests/test_night_gate.py` (3 sites) — **all five are PR files**.
7. `git log origin/main -3 --format='%h %ci %s' -- README.md` →
   `0d9881ef 2026-09-09 06:49:36 -0700 README: activity blurb …` and
   `a3da3463 2026-09-09 07:44:51 -0700 README: drop pull-request literals from the activity blurb (test_docs_freshness volatile-literal rule; main CI red on 0d9881ef cured)`.
   Attempt 1 started **06:49:41**, five seconds after 0d9881ef; attempt 2 started **07:45:08**, seventeen seconds after the cure.
   **Both timings confirm the packet's account of extra failure #1 exactly.**
8. `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness` in my tree (a3da3463) → `Ran 31 tests in 1.050s` /
   **`OK`** (1.15 s wall). Extra failure #1 is dead, and attempt 2's tail independently shows it green.
9. **The one permitted alone run** of the race test in the PR tree:
   `Ran 1 test in 24.388s` / **`OK`**; `/usr/bin/time` line: `41.01s user 50.25s system 370% cpu 24.665 total`.
   That is the **4th** consecutive alone pass (packet's 3 + mine), and the CPU figure is the load argument in numbers: the test
   burns ~91 s of CPU and only finishes in 24 s because it gets ~3.7 cores. Under four concurrent shards it cannot get 3.7 cores,
   so blowing a 30 s per-thread `join` deadline is arithmetic, not mystery.
10. `pmset -g custom` → Battery `powermode 0`, AC `powermode 1` (unchanged from yesterday).
    Timer probe ×3: `0.1802`, `0.1879`, `0.1571` s per 50 ms sleep → **3.1×–3.8× slack, still present today**.
11. `gh pr view 309 --json headRefOid,mergeStateStatus` → head **`6d76f9647104d74b7b23cad945adaaf908eec0fd`**, `UNSTABLE MERGEABLE`.
    `gh pr checks 309` → **only `gate-ledger` fail**; `build`, `installed-wheel`, `pr-fast (1,2)`,
    `calibration-exits-exclusive (3.11, 3.14)`, `calibration-writer-crash-matrix-exclusive` ×4, and **`test (3.11, 1–4)` +
    `test (3.14, 1–4)` all PASS**.
    `gh api …/actions/runs/34365694272` → `head_sha 6d76f964…`, `status completed`, `conclusion success`, created `14:45:14Z`
    (= 07:45:14 PDT, i.e. it finished long before the 08:42 packet assembly).
12. `scripts/shard_tests.py` read: sharding is deterministic (`sorted(module_list)`, greedy least-loaded packing over a checked-in
    timing map), so module→shard assignment is stable between attempts — the "shard 3 / shard 4" pattern in both tails is expected,
    not evidence of anything.
13. Mechanism read: `joulewise/arm_readiness.py:10527-10545` — the consumption receipt's single-use linearization point is
    `_exclusive_write` → `os.open(path, O_WRONLY|O_CREAT|O_EXCL)` (`:5438`), with its own comment: *"This atomic no-clobber primary
    is the only real enforcement and the single-use linearization point; every later complete caller must lose this write."*
    Collision → `readiness_output_collision` → re-raised as `readiness_record_consumed`.

## Refutations attempted

| # | Claim | Attempt | Result |
|---|---|---|---|
| R1 | Charge: "no failing-path module imports night_gate or run_night (grep at the integration head)" | Ran that exact grep in both trees | **REFUTED.** `joulewise/arm_readiness.py` imports `joulewise.night_gate` twice (:9933, :9975), and attempt 2's extra failure is `tests/test_arm_readiness_lifecycle.py`, which imports `joulewise.arm_readiness` (:20). The A2 predicate P1 requires the ledger row to record is **false as written**. The charge's file list also names `joulewise/run_campaign.py`, which does not exist. |
| R2 | The PR could actually have broken the arm race test | One-hunk diff + caller graph (probe 6) | **CONFIRMED INDEPENDENT — but by reachability, not by "no import".** The single changed hunk lives inside `evaluate_night`; `evaluate_night`'s only callers repo-wide are `scripts/run_night.py` and the two PR test modules. `arm_readiness` imports only `NightPlan`/`PlanError`/`AGENT_CENSUS_ARGV`, none of which the hunk touches. This is the argument the row should carry. |
| R3 | Extra failure #1 was a docs test cured on main | `git log` timings + ran the module | **CONFIRMED, and tighter than the packet states.** Not merely "cured": the breakage was introduced by 0d9881ef *five seconds before* attempt 1 launched, and cured by a3da3463 *seventeen seconds before* attempt 2 launched. It is a real defect, correctly found and fixed — not a flake. |
| R4 | Extra failure #2 "passes alone 3/3" | Ran it once myself | **CONFIRMED (4/4 now), 24.388 s.** |
| R5 | The alone runs are worthless because the concurrency that provokes the bug is external | Read the test, `tests/test_arm_readiness_lifecycle.py:855-925` | **REFUTED.** The contention is *internal*: `threading.Barrier(8)` + 8 threads all calling `launch_window.launch(args)`. The alone run exercises the exactly-one-consumer property under genuine 8-way contention and reaches every property assertion (`execve.call_count == 1`, `outcomes.count("launch_consumption_invalid") == 1`, `…("readiness_record_consumed") == 7`, `"readiness_lock_unavailable" not in outcomes`). External shard load only perturbs the interleaving distribution and the wall clock. |
| R6 | The two attempts are "the same signature" (packet header, escalation-trigger claim) | Compared the two extras | **PARTLY REFUTED.** The two fifth failures have different causes: a genuine self-inflicted docs regression vs a wall-clock artefact. The only shared signature is the arithmetic "four + one extra". Attempt 1 does not count as a flake round, which weakens the "two rounds, same signature" framing while strengthening the case that only one flake has actually been seen. |
| R7 | P5 is "a registered load-sensitivity lane" this failure "belongs to" | Read `55-arm-integration-load-01-kernel-row.txt` | **NOT SUPPORTED.** The row is `"status": "queued"`; its recorded evidence is four `readiness_clock_preflight_refused` occurrences, a *different* failure mode from a thread-join timeout; and it carries its own flag: *"four occurrences are lead-reported, not four independently reconstructed failing runs."* The race test is not named in it. |
| R8 | A5 is outstanding ("integration head 6d76f964 CI pending") | `gh pr checks` + run API | **REFUTED — stale.** The PR head *is* 6d76f964 (it was pushed); CI run 34365694272 on that exact SHA completed **success**, all 8 full-suite `test` shards across Python 3.11 and 3.14, before the packet was assembled. Only `gate-ledger` is red, by design. |
| R9 | Low Power Mode / timer slack is a stable machine state one can wait out | 3 timer probes today, powermode unchanged | **Still refuted (P2 R1 stands).** Slack 3.1×–3.8× today, same powermode as when the refuter measured 2.1×–3.6×; option (c) would be waiting on a demonstrated non-cause. |

## Race-test failure-mode analysis

The failing assertion is the *first* one after the join loop:

```python
for thread in threads:
    thread.join(timeout=30)
self.assertFalse(any(thread.is_alive() for thread in threads),
                 "every concurrent consumer must reach a recorded outcome")
```

**Can it mask a real exactly-one-consumer defect? No — the masking direction is impossible, and the confusion direction is real.**

1. **It cannot turn a defect into a pass.** The assertion fires *before* `execve.call_count == 1` and the `outcomes` counts. A run
   that trips it FAILS. There is no channel by which two consumers spending the capability produces a green tail. A thread that
   died on an uncaught exception would also shorten `outcomes` and fail a later count. I found no spurious-pass path.
2. **It cannot be a lock-starvation signature, because there is no lock.** The single-use linearization point is one
   `O_EXCL` create (`arm_readiness.py:5438`, called at `:10538`). An atomic no-clobber create does not block, has no timeout, and
   cannot deadlock; losers get `FileExistsError` immediately and are converted to `readiness_record_consumed`. The
   `readiness_lock_unavailable` code the test asserts *absent* is therefore the signature of a *different* failure, and it did not
   appear. A hung consumer would have to be stuck in JSON rendering, validation, or `fsync` — i.e. in work, not in waiting.
3. **The quantitative case is decisive.** The test needs ~91 s of CPU (41 user + 50 sys) and finishes in 24 s alone by consuming
   ~3.7 cores; four concurrent shards on 16 cores with fsync-heavy siblings cut its share, and the 8-thread section then exceeds a
   30 s per-thread deadline. This is the same wall-clock-coupling family as the four `IdleAdmissionCoreVerdictTests`, not a new one.
4. **What it genuinely costs: the run yields ZERO positive evidence about the property.** Because the guard assertion fires first,
   attempt 2's tail says nothing about whether exactly one consumer won. The evidence has to come from somewhere else — and it
   does: 4/4 alone runs (which do reach every property assertion, under real 8-way contention) plus green Linux CI on the exact
   head across two Python versions and eight shards.
5. **The real defect here is in the test's instrumentation, not in the seam.** On timeout the message does not record how many
   threads were alive, the partial `outcomes` list, or `execve.call_count`. A slow-but-progressing run and a genuinely stuck
   consumer are indistinguishable from the tail. Since this test guards a claim-bearing atomicity seam (D-176), that is a real
   gap and belongs in the fix, whatever is decided about the merge. Nit while I was there: the `consume()` closure leaves
   `outcome` unbound if `launch()` ever returns normally, so the test silently depends on all eight callers raising.

**Verdict on (2): timeout artefact, with fail-loud (never masking) semantics — but the run is uninformative rather than
reassuring, so the atomicity evidence must be sourced from the alone runs and CI, and must be named as such in the row.**

## Contract-lens answer on the options

Row 9's purpose (P2, last gate) is regression detection on the integration tree, and P1-A1 is the concrete form that purpose took
for a *code* PR. The question is which option preserves the purpose without converting the gate into a rubber stamp.

**(a) Sequential `--workers 1` replay — REJECT as the required path (accept only as optional extra).**
Uncovered risk it leaves: none that matters, and it *adds* one. P2 measured slack swinging 2.1×→3.6× within four minutes at
constant load and constant powermode; my probes show 3.1×–3.8× today. Removing shard concurrency removes one contributor to a
hazard that demonstrably fires without it (the four IdleAdmission tests failed **alone** at 83ab38ed in P1's own probe, 37.8 s,
rc=1). A 3–4 h run over 5642 wall-clock-exposed tests is *more* exposure-time, not less, and its most likely outcome is a third
"four plus one different extra" tail — which is precisely round three against the standing escalation rule the magistrate invoked
to convene this gate. Its stated acceptance wording is also broken: "must record exactly the four" would reject an all-green
sequential replay. If anyone wants confirmation of the load hypothesis, the cheap form is a **sequential re-run of the two
affected modules only** (`tests.test_run_campaign` ~350 s + `tests.test_arm_readiness_lifecycle` ~166 s ≈ 9 minutes), which
answers the same question at 4 % of the cost.

**(b) Amend A1 to "exactly the four … OR any extra failure that passes alone 3/3 and belongs to a registered load-sensitivity
lane" — REJECT as an amendment; ACCEPT its evidentiary content as PR-specific facts.**
Three concrete uncovered risks:
  - *It makes A1 unfalsifiable.* Any wall-clock-coupled test can be re-run alone until it passes. A test that genuinely fails 30 %
    of the time under load clears "alone 3/3" with high probability. The filter admits exactly the defects it claims to exclude.
  - *"Belongs to a registered lane" is self-certified by the merging party.* Probe R7: the lane row is `queued`, its evidence is a
    different failure mode (`readiness_clock_preflight_refused`), it carries its own "lead-reported, not independently
    reconstructed" flag, and it does not name this test. Under the amendment, the party that wants the merge decides membership.
  - *It creates the precedent P1-C4 forbids* ("No precedent. This is a rule-11 disposition for one replay on one PR"). A standing
    amendment to a gate row's acceptance condition is exactly the class the lieutenant/magistrate may not decide alone; writing it
    as a general rule now converts a one-off waiver into permanent doctrine, on a sample of one flake.

**(c) Hold until the machine's timer-slack state changes — REJECT.**
Uncovered risk: it buys no information and blocks the whole night lane on a demonstrated non-cause. P2 refuted the Low Power Mode
attribution (fixture 18.94 s then 11.58 s two minutes apart, powermode 1 both times); my probes show the slack persists today at
the same powermode. Waiting for Ed's sudo is waiting for a knob that has not been shown to move the needle, while
NIGHT-REHEARSAL-01 stays blocked and the *known* defect that #309 cures stays in main.

**(d) ACCEPT — a bounded, PR-specific waiver with a corrected independence predicate. This is what I would sign.**
It keeps A1 intact as the standing rule, records a named exception for #309 alone, and — unlike (b) — discharges *each* failure on
its own evidence rather than by a general dismissal rule:
  1. **Do not amend A1.** Record a waiver for PR #309 only, restating P1-C4.
  2. **Correct A2 before it is written into the ledger.** The "no import" claim is false (R1). Replace it with the reachability
     statement, which is stronger and true: one hunk, inside `evaluate_night` (:945; `@@ -1040,64 +1040,78 @@`), whose only callers
     repo-wide are `scripts/run_night.py:1503,1515`, `tests/test_night_gate.py` and `tests/test_run_night.py` — all PR files, all
     covered by A4; `arm_readiness` imports only `NightPlan`/`PlanError`/`AGENT_CENSUS_ARGV`, none of them touched.
  3. **Run A4 before merge.** It is still unexecuted, it is the cheapest outstanding obligation (~2–3 min), and it is the one that
     covers the cure's own blast radius on the integration tree. Not running it while debating a 3–4 h replay is the wrong economy.
  4. **Record A5 as SATISFIED on the integration head** with the corrected fact (R8): run 34365694272, head_sha 6d76f964,
     conclusion success, 8 full-suite shards × 2 Python versions, only `gate-ledger` red by design. Neither local extra failure
     reproduces on Linux at the exact tree under test.
  5. **Discharge each of the two extras by name**, per the analysis above: #1 is a real, self-inflicted, already-cured defect
     (0d9881ef → a3da3463; green in attempt 2 and in my run); #2 is a fail-loud timeout artefact whose seam evidence comes from
     4/4 alone runs and CI, with an O_EXCL linearization point that cannot deadlock.
  6. **Carry the durable obligation:** amend ARM-INTEGRATION-LOAD-01 to name this test and require the join-timeout branch to emit
     discriminating evidence (alive-thread count, partial `outcomes`, `execve.call_count`), so the next occurrence distinguishes
     slow from stuck. Without this clause, (d) leaves exactly one thing uncovered — an under-instrumented, load-fragile guard on a
     claim-bearing seam — and that is the only uncovered risk I would accept, because it is registered rather than ignored.
  7. Optional, if the judge wants one more datum before the button: the ~9-minute two-module sequential run from (a) above.

## Over-statements (quoted)

1. **Charge:** *"A2 evidence: PR files {…} do not intersect the failing paths, and **no failing-path module imports night_gate or
   run_night (grep at the integration head)**."* — **False.** `joulewise/arm_readiness.py:9933,:9975` import `joulewise.night_gate`;
   `tests/test_arm_readiness_lifecycle.py:20` imports `joulewise.arm_readiness`. This is the packet's most load-bearing factual
   error, because A2 is the exact predicate P1 orders recorded in row 9. The list also names `joulewise/run_campaign.py`, a path
   that does not exist (the file is `scripts/run_campaign.py`), so a literal re-run of the stated grep exits 2.
2. **Packet P7:** *"A5 CI green at 5db38b58 (**integration head 6d76f964 CI pending**)."* — Stale. CI on 6d76f964 completed
   **success** at run 34365694272 (created 14:45:14Z), well before the 08:42 PDT assembly. The packet understates its own case and
   states an unverified CI status as fact.
3. **Packet P4 line:** *"thread join timeout **under load**; passes alone 3/3 at 23.5 s."* — The tail shows only
   `AssertionError: True is not false`, i.e. threads alive at the deadline. "Under load" is the (well-supported) conclusion smuggled
   into the evidence description. Say "threads still alive at the 30 s join deadline; attributed to shard load".
4. **Packet header:** *"the standing escalation trigger (two consecutive replay attempts failing with **the same signature**…)."* —
   The two extras have different causes: a genuine docs regression the magistrate itself introduced and fixed, and a timing
   artefact. Only the shape "four + one extra" is shared. Counting attempt 1 as a flake round overstates the flake history.
5. **Charge Q2 option (a):** *"a sequential replay … **that must record exactly the four**."* — As written this rejects an all-green
   sequential replay. The acceptance set must be "the four, or any subset of them, and nothing else".
6. **Charge Q2 option (b) / packet P5:** *"belongs to a **registered** load-sensitivity lane (P5)."* — P5's own text is
   `"status": "queued"`, its evidence is four `readiness_clock_preflight_refused` occurrences (a different failure mode), it does
   not name this test, and it self-flags that the four occurrences are "lead-reported, not four independently reconstructed
   failing runs". "Registered" is doing unpaid work.
7. **Packet P3:** *"cured on main at a3da3463, **main CI green**."* — I verified the cure and that the test passes at a3da3463; I
   verified CI green on the PR head, not on the main branch. Adjacent claim, unverified in-session (PD-1).
8. **Both documents, "alone"** — the packet repeats the word for runs that are alone *in-process*, not alone *on the machine*
   (P2 flagged exactly this last gate, item 3). My own alone run had the rest of the fleet on the box; it still passed, which
   argues for the merge, but the word should be qualified anyway.
9. **Credit where due:** *"SHA256 of every listed file is in 55-coldgate-packet.sha256"* is **true and verified 12/12** — the prior
   refuter's packet-integrity complaint has been fixed.

## Recommended answers Q1–Q4

**Q1.** **No.** Attempt 2 does not satisfy A1, and neither does attempt 1. A1 says the replay must record failures = *exactly* the
four named tests and that *"a fifth failure, any error, a different test name, or a different assertion line is a hold — no 'near
enough'."* Both tails record `failures=5`. Under P1's own words this is a hold. Nothing in my probes softens that; the door has to
be opened deliberately, by a recorded waiver, not by reading A1 loosely.

**Q2.** **(d)**, as specified above: no amendment to A1; a PR-#309-only waiver that (i) replaces the false "no import" predicate
with the true reachability argument, (ii) requires A4 to actually be run on the integration tree before merge, (iii) records A5 as
satisfied on head 6d76f964 with run id and conclusion, (iv) discharges each extra failure by name with its own evidence, and
(v) amends ARM-INTEGRATION-LOAD-01 to name the race test and require discriminating evidence on join timeout. Reject (a) as the
gate (3–4 h, adds exposure, most likely outcome is round three), reject (b) as a standing amendment (unfalsifiable filter,
self-certified lane membership, violates P1-C4), reject (c) (waits on a refuted cause while the night lane stays blocked).

**Q3.** Row-9 wording I would accept (magistrate to paste, verbatim, with the real tails):

> Row 9 — DISCHARGED BY RECORDED WAIVER (PR #309 only; no precedent, per ruling 44 C4). Full-suite replay run unpiped on the
> integration tree 6d76f964 (= 5db38b58 + main a3da3463), four shards concurrent, started 07:45:08 PDT 2026-09-09. Verbatim:
> `WORKERS SUMMARY shards=4 modules=221 tests=5642 failures=5 errors=0 skipped=108 failed_shards=3,4 result=FAIL` / `rc=1`.
> Failures: the four `IdleAdmissionCoreVerdictTests` tests named in ruling 44 A1, each at `tests/test_run_campaign.py:9581`
> with `AssertionError: False is not True`, pre-existing on the merge base in the same machine state (44 A3); plus a fifth,
> `test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`,
> failing at `tests/test_arm_readiness_lifecycle.py:891` on `assertFalse(any(thread.is_alive()…))` — threads still alive at the
> 30 s per-thread join deadline. A1 is therefore NOT met and this row is discharged by waiver, not by pass.
> Waiver basis: (1) independence by reachability — the PR's only production hunk is inside `night_gate.evaluate_night`
> (`joulewise/night_gate.py:945`, `@@ -1040,64 +1040,78 @@`), whose only callers repo-wide are `scripts/run_night.py:1503,1515`,
> `tests/test_night_gate.py` and `tests/test_run_night.py`, all PR files; `joulewise/arm_readiness.py:9933,9975` does import
> `night_gate`, but only `NightPlan`, `PlanError` and `AGENT_CENSUS_ARGV`, none of which the hunk touches. [This supersedes the
> earlier "no failing-path module imports night_gate" formulation, which is false.]
> (2) The fifth failure's guard assertion is fail-loud and cannot mask a defect: the exactly-one-consumer linearization point is a
> single `O_EXCL` create (`joulewise/arm_readiness.py:5438`, called at `:10538`) which cannot block or deadlock, and the test's
> 8-way contention is generated internally by `threading.Barrier(8)`, so the alone runs do exercise the property. The test passes
> alone 4/4 on this tree (23.699 / 23.499 / 23.587 s recorded 2026-09-09; 24.388 s re-run by the cold-gate refuter), consuming
> ~91 s CPU at ~370 %, which is why it exceeds a 30 s join under four-shard concurrency.
> (3) A4: `python3 -m unittest tests.test_night_gate tests.test_run_night` on the integration tree — [tail, rc].
> (4) A5: CI green on the PR head 6d76f964 — Actions run 34365694272, conclusion success, `test (3.11, 1–4)` and `test (3.14, 1–4)`
> all pass; only `gate-ledger` red, by design.
> (5) Attempt 1 (dd135364, started 06:49:41 PDT) is recorded for completeness: same four plus
> `test_docs_freshness.…test_current_sections_do_not_copy_volatile_literals`, a real regression introduced by main commit 0d9881ef
> (06:49:36) and cured by a3da3463 (07:44:51); the module passes green at a3da3463 (`Ran 31 tests in 1.050s OK`) and passed in
> attempt 2.
> `failed_shards=3,4` is quoted verbatim and is not glossed as a count.

Later addenda that MUST be recorded: (i) ruling 44's A6/C3 addendum obligation is unchanged — re-run
`tests.test_run_campaign.IdleAdmissionCoreVerdictTests` (71 tests) on then-current main once the machine's slack state changes, and
record the tail; if it does not go green, the four become an open defect on main with their own lane; (ii) a dated addendum to
`31-terminal-review-night-gate-stub-chain.md` amending its "once the full-suite replay records rc 0" sentence to cite this waiver
(A6, still outstanding); (iii) the ARM-INTEGRATION-LOAD-01 kernel row amended to name
`test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`, note that its recorded evidence to date is a
*different* signature (`readiness_clock_preflight_refused`), and require the join-timeout branch to report alive-thread count,
partial `outcomes` and `execve.call_count`; (iv) if the optional two-module sequential run is done, its tail.

**Q4.** The nine items above; the load-bearing ones are (1) the false A2 "no import" predicate — because it is the very fact the
ledger row is ordered to record — and (2) the stale "CI pending at 6d76f964", which is now green on the exact head and materially
changes the evidence balance. (5) and (6) matter because they are the wording by which options (a) and (b) would be adopted.

## Verdict

**Packet flawed: its A2 independence predicate is false as written — `joulewise/arm_readiness.py:9933,9975` imports
`joulewise.night_gate`, and attempt 2's extra failure lives downstream of that import — and its A5 line is stale, since CI is
green on the actual PR head 6d76f964 (run 34365694272, 8 full-suite shards × 2 Pythons). Both corrections happen to strengthen the
case for merging, but the ledger row must record the true reachability argument, not the false grep; A1 is plainly not satisfied
and the door should be opened by a named, PR-specific waiver — never by amending A1 into a rule that "passes alone 3/3" can
discharge.**
