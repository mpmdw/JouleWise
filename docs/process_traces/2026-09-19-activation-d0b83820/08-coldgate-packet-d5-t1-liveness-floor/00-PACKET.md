# Cold-gate packet — QUIET-PREDICATE-EVIDENCE-01 harness, finding D5-T1, fix round 2 result: may the real-load liveness floor `assertGreater(claimed_s, 0.0)` stand? (rule 11 mandatory triggers: third round on the same defect; reinterpretation of an adopted verdict; standing escalation trigger — same signature found twice)

Assembled 2026-09-19 ≈08:10 PDT by the resident magistrate (activation d0b83820). Mechanically assembled: every exhibit is a verbatim `git diff` or `cat` of branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `37ca3c35` (rebased onto main `2f79e633`) or of records already on main. The magistrate's own view is confined to the option list and is not an exhibit.

## What was found

Fix round 2 (Exhibit A) installed the assertion block that adjudication 01a §3 (Exhibit C) synthesized from cold-gate ruling 10 and Opus refutations 11/12 (Exhibits D, E): the delivery minimum is gone; the over-burn ceiling (≤ 0.14 cores), a per-period ceiling, a kernel `getrusage(RUSAGE_CHILDREN)` cross-check (`charged_s >= claimed_s - .01`; `charged_s <= .14 × duration + STARTUP_CPU_S`), and a liveness floor `assertGreater(claimed_s, 0.0, "no CPU burned…")` remain. Two fake-clock regressions were added. Bench acceptance (Exhibit B, V1–V7): 43 tests OK twice; three unmodified real-load runs charged 0.634–0.644 s against claimed 0.300 s; mutations `cores`, `alignment`, `observer`, `clock`, `catchup-capped` all killed; `burn-noop` survives (F2).

The seat returned NEEDS_RULING (Exhibit B, F1): the liveness floor is itself a delivery assertion. Executed counterfactual: a CORRECT worker first scheduled at 3.001 s, after its 3 s window, returns `periods=[]` with no error; `claimed_s` = 0 and the floor fails. Both same-signature statements are FOUND: "real-load assertion fails on correct code under scheduler starvation" (zero-service witness) and "assertion keyed to a quantity starvation destroys" (`claimed_s`). The seat also reports (Exhibit B, table "Mutation results" and the supplemental diagnostics) that mutation `clock` (`Clock.cpu → 0`) is killed TWICE: by the liveness floor (`0.0 > 0.0`) and by the kernel ceiling (`3.195601 > .92 CPU-s`). Refutation 12 (Exhibit D, line "The ruling's named example, mutation `clock` … is **not** a unique catch") said the same before the round ran. So the floor kills nothing the kernel ceiling does not already kill, and it re-creates the signature the gate was convened to remove.

F3 (Exhibit B): ruling 10's pin `every wake_late_s < 1e-3` for the preempted-burn regression fails CORRECT code under `FakeClock.ratio = 100` (correct rows carry lateness ≈ .005, 0, 0, 0, .010, .010); the seat kept record 11's executed `< .05` as the brief instructed and reported the contradiction. The late-start regression keeps `< 1e-3` (it passes there).

## Q1 — the liveness floor (rule one option or write a better one)

- (a) DELETE `self.assertGreater(claimed_s, 0.0, …)` from the real-load test. Keep everything else in the ruled block. Kill coverage: `clock` remains killed by the kernel ceiling (executed: 3.1956 > .92); `catchup-capped` by the per-period ceiling and the fake-clock pin; `cores`/`alignment`/`observer` unchanged. Cost: nothing in the real-load test proves the child did any work; that property, if wanted, moves to a deterministic assertion (Q2).
- (b) KEEP the floor and declare the assumption in the test ("assumes the scheduler runs the child at least once inside the 3 s window on the bench"); accept the zero-service false failure as out of scope for a 3 s bench test on an unarmed, census-clean machine (Ed's sensible-gates directive: tolerances sized to the instrument; D-161: the operator is the only adversary).
- (c) CONDITION the floor on kernel evidence: assert `claimed_s > 0` only when `charged_s > STARTUP_CPU_S` (the kernel says the child got CPU beyond start-up, so a zero claim is a clock defect, not starvation). State whether this is again "keyed to a quantity starvation destroys".
- (d) Other, with the same burden: the ruled assertion set must ACCEPT the three prior correct-code inputs (1.05 s late wakes; first scheduling 2 s late; burn preempted 100×) AND the zero-service input, and must still kill `clock` and `catchup-capped`.

Deliver: the ruled option and the exact assertion text (or the exact deletion), and the same-signature statement under the ruled option for both signatures named above.

## Q2 — the surviving `burn-noop` mutation (F2)

`burn_profile` returning a no-op survives all 43 tests: the budget loop's own overhead accrues `cpu_used_s`, so no assertion distinguishes "burned the requested work" from "spun the loop". Rule: (a) register as a lane for a deterministic assertion (e.g. a fake burn that records its calls, or `work_units` in the period row — say which, and whether a row-shape change is a contract change), NOT this round; (b) fix in this round with exact test text; (c) accept as an equivalent mutant with the one-paragraph reason a reader with no project grounding can follow.

## Q3 — F3, the contradicting pin

Affirm or reject the seat's resolution: record 11's executed `wake_late_s < .05` for the preempted-burn regression, ruling 10's `< 1e-3` retained only for the late-start regression. If rejected, give the number and the executed evidence for it.

## Constraints on the judge

Read-only. NOTHING IS ARMED on this machine now (both night agents uninstalled 07:41 PDT; magistrate agent loaded). Wall budget 15 minutes, hard. Probes allowed: `git show 37ca3c35:<path>` from the packet worktree, `rg`/`grep`, `sed -n`, Python snippets under `/tmp` against fake clocks, and at most ONE run of the single test module, read-only, in `/Users/edr/code/JouleWise-wt-harness-232` (branch head `37ca3c35`) as `env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence` (≈ 6 s; it launches one 3 s, 0.1-core subprocess). No `sudo`, no `powermetrics`, no `collect`. Never touch `/Users/edr/code/JouleWise` (canonical root), any `/Users/edr/JouleWise-measurement-*` directory, `/Users/edr/night-custody`, or `~/Library/LaunchAgents`.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
d2fbffd604b7fe312d3c03ea1e9148b09ea6397914a6229435bed14dda7f03e7  exhibit-A-fix-round-2-diff.md
3255eee63258dc56e21df4bfcfc505f74410416b3c91bbf5b5c8b38a0d08d005  exhibit-B-seat-06-report.md
04fde132772e5326e8d8fdd01fb92bf5842065cdb1ecfc72355dcb77ae27173b  exhibit-C-adjudication-01a.md
c485ac16ff07292dee2d29b8c87033c8bd539024be574ee405a3cfd228490ec1  exhibit-D-ruling-10-and-refutation-12.md
0232d7b2f22f89e684989acb811f3e96d61753c8c337c2a40abfb1e7ef940a92  exhibit-E-record-11.md
```
