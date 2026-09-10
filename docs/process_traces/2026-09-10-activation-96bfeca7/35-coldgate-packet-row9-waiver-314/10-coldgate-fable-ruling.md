# Cold-gate ruling 35 — row-9 waiver for PR #314 (GATE-SENSIBILITY-SWEEP-01) with one known local-only replay failure

Judge: Claude Fable 5.1, single non-interactive session, convened 2026-09-10 ~07:31 PDT under rule 11 by magistrate activation
96bfeca7; ruling written 07:36–07:40 PDT. Working tree: `/Users/edr/code/JouleWise-wt-coldgate-gate-prose`, detached at
`58d4696bbcd4b95cdc40e06d4163628d5d29c78a`, clean apart from three untracked packet directories. Packet digest verified:
`shasum -a 256` of `00-PACKET.md` + `exhibit-A-replay-tail-34.md` = `44ebca77ffc9a944…` (matches the charge). Read in full:
00-PACKET, exhibits A–G, precedent rulings 44 and 56 and refuter 57 under `docs/process_traces/2026-09-09-rehearsal-harvest/`.
Nothing else in that directory was opened.

## Contamination disclosure

Not clean, and here is exactly what leaked before I read the packet. The harness injected into my system prompt: the user's global
`~/.claude/CLAUDE.md` (multi-model orchestration pointers and a writing standard), the worktree's tracked `CLAUDE.md` (Codex bridge
notes), a git-status block listing the five most recent commit subjects on this checkout (58d4696b … 30dc8aab, all
GATE-SENSIBILITY-SWEEP-01 fix rounds), and the auto-memory INDEX `MEMORY.md` (one line per memory, no bodies). I did not open any
memory file, RUN_STATE.md, TASK_QUEUE.md, docs/decision_log.md, anything under docs/process/, any other process trace, `.claude/`, or
any skill. The index lines that bear on this question and that I cannot un-see: "Sensible gates directive — Ed 2026-09-10: no silly
gates on accepting numbers … run GATE-SENSIBILITY-SWEEP-01 before consuming real numbers" (this PR's own subject and priority);
"Checkpoint 2026-09-10 — NEXT = short real G2-a window for real numbers ASAP"; "Merge authority with review — STANDING gh self-merge
(D-072) after the full gate shape"; "Codex delegation growth — harness denies agent self-merge, Ed names merges"; "Threat-model prune
(D-161) — fail-closed only for physics/evidence/pre-registration"; "Docs are context, code is truth"; "Packet facts bench-verified
(PD-1) — never label a fact bench-verified without running it this session". I treat none of these as evidence. Every conclusion
below is reasoned from the packet, the two precedent rulings, the refuter, and the probes listed at the end; where a conclusion
happens to agree with an index line, the reason given is the probe. General knowledge used: Python `unittest` exit semantics,
`subprocess.run(timeout=…)`, binary64 ULP arithmetic. No other model or agent was consulted; no background work of any kind.

## Executed probes (all foreground, read-only; one test run that writes only to its own temp directory)

```
$ git rev-parse HEAD                                   → 58d4696bbcd4b95cdc40e06d4163628d5d29c78a
$ git status --short                                   → only the three untracked packet dirs (24-, 31-, 35-coldgate-packet-*)
$ cat 00-PACKET.md exhibit-A-replay-tail-34.md | shasum -a 256
                                                       → 44ebca77ffc9a9444dca999b58277a6dce72bbd9214bf9e7bff2196f969929b9  (matches charge)

$ git log --oneline 58d4696b..beb808bc                 → beb808bc (fix round 6), 92c3e15a (round 5), 5b85d401 (round 4), 456b09a9 (round 3)
$ git merge-base --is-ancestor 078a13a4 beb808bc       → yes (main 078a13a4 is an ancestor of the PR head)
$ git diff --stat 58d4696b..beb808bc -- joulewise      → EMPTY. Rounds 3–6 changed no production byte; this checkout's joulewise/
                                                          tree is byte-identical to the PR head's.
$ git diff 078a13a4..beb808bc --stat                   → 15 files, +1654/−20: two contract docs, seven trace docs,
                                                          joulewise/controller.py 11, environment_admission.py 8,
                                                          load_transition_alignment.py 2, scripts/generate_g2a_probe_inputs.py 11,
                                                          tests/test_gate_sensibility_rounding.py 240 (new), tests/test_generate_g2a_probe_inputs.py 31
$ git diff 078a13a4..beb808bc --stat -- tests/test_controller.py joulewise/adapters/powermetrics.py joulewise/uncertainty_evidence.py \
      joulewise/controller.py joulewise/cli.py scripts/run_campaign.py tests/fixtures/fake_powermetrics_process.py
                                                       → joulewise/controller.py | 11 +++++++++--   (1 file)  ← NOT the empty set
$ git diff 078a13a4..beb808bc -- joulewise/controller.py
                                                       → three hunks, ALL inside `def cooldown_gate(` (function starts at :2464):
                                                          @@ -2516 (coverage_rounding_s = 0.0), @@ -2523 (+= ulp(evidence_end)+ulp(clipped_start)),
                                                          @@ -2552 (span slack 1e-9 → 1e-6; coverage_slack_s = max(1e-6, rounding + ulp(coverage_s)))
$ grep -n -E 'def cooldown_gate|cooldown_gate\(' joulewise/controller.py
                                                       → :2464 def ; :3072 the ONLY call site, inside the between-member campaign cooldown
                                                          (`cooldown_run_id = f"{experiment_id}-cooldown-{after_member}"`, campaign_policy.cooldown)
$ grep -c cooldown_gate tests/test_controller.py       → 0
$ sed -n 1599,1680p tests/test_controller.py | grep -i -E 'cooldown|thermal|sustained'
                                                       → one hit: the samplers string "cpu_power,gpu_power,ane_power,thermal" (no cooldown config)

# The one permitted test run, alone in-process, 07:33:52–07:34:29 PDT (machine census not taken)
$ python3 -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce
  FAIL: test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce (…HappyPathTests…)
    File "…/tests/test_controller.py", line 1675, in test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce
      self.assertEqual(validate_bundle(bundle_path, strict=True), [])
  AssertionError: Lists differ: ['strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation',
                                  'strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation'] != []
  Ran 1 test in 36.840s
  FAILED (failures=1)
  (The process rc was not captured cleanly: my `time … | tail` wrapper reported the pipeline's rc, not unittest's. unittest exits 1
   on `FAILED`; I did not re-run because the charge allows one run.)
```

Not probed (out of scope or budget): the full suite; the four-shard runner; the 73-test `tests.test_controller` module; whether the
failure also occurs on main in this exact session (the lead's 05:05 run on 078a13a4 and seat 08's restored-bytes run are the packet's
evidence for that, and my run on production bytes identical to beb808bc is consistent with them); GitHub CI (exhibits E/F are the
packet's evidence; I ran no `gh`).

## Q1 — May PR #314 merge under a named row-9 waiver for this one failure?

**Ruling: (a) — YES, merge at head `beb808bc` under a named row-9 waiver, with the conditions W1–W8 below. One packet claim must
be corrected before it is written into the ledger: the failing test's path is NOT "disjoint from the PR's code changes" at file
level. The PR changes `joulewise/controller.py`, which is on the failing path. Independence holds, but at hunk level, and the row
must say so in those words.**

Reasoning, sized to what row 9 guards (a branch regression hidden by a stale or partial run):

1. **The replay was neither stale nor partial.** Exhibit A is a single-process, unpiped `unittest discover` on the PR's final head
   `beb808bc`, 5668 tests, 1 h 39 min, rc 1 recorded from the process. That is the strongest form row 9 asks for. It found exactly
   one failure, and it found it by name and line. Row 9's purpose, regression detection on the integration tree, was served.

2. **The one failure is pre-existing on the merge base in the same machine state, and I reproduced it on the PR's production
   bytes.** The lead ran `tests.test_controller` on clean main 078a13a4 at 05:05 (73 tests, failures=1, same two strict reasons);
   seat 08 reproduced it with the four changed modules restored to HEAD bytes; my run at 07:33 on 58d4696b, whose `joulewise/`
   tree is byte-identical to beb808bc (empty diffstat), fails at the same line 1675 with the same two strict messages, in 36.8 s.
   A failure present on the merge base cannot be a regression introduced by the PR.

3. **Independence is shown structurally, not statistically, but the packet's file-level sentence is false and must be replaced.**
   The failing path (per exhibit B: `tests/test_controller.py`, `joulewise/adapters/powermetrics.py`, `joulewise/uncertainty_evidence.py`,
   `joulewise/controller.py`, `joulewise/cli.py`) intersects the PR's diff in ONE file, `joulewise/controller.py`. My diff shows all
   three hunks in that file sit inside `cooldown_gate` (:2464 onward), and `cooldown_gate` has exactly one caller repo-side, the
   between-member campaign cooldown at `controller.py:3072`. The failing test is a single-run `HappyPathTests` case; its module never
   names `cooldown_gate`, and the test body configures no cooldown policy. The post-idle capture, custody salvage, and strict
   validator that produce the two strict messages live in `powermetrics.py`, `uncertainty_evidence.py`, and `cli.py`, all of which are
   byte-identical to main. So the PR changes no byte the failing test executes. This is the same shape ruling 56 required for the
   race test (hunk confined to a function the failing path cannot reach) and refuter 57 R1 insisted on: the row carries the
   reachability argument, never a "disjoint files" claim that a diffstat refutes.

4. **The mechanism is established, and it is a fixture timing defect, not a numeric one.** Exhibit B reproduced, under 3.5× sleep
   stress on Python 3.14.7 and 3.13.1, the chain: fixture oversleeps → post-idle capture exceeds the 17.5 s deadline
   (`powermetrics.py:1468–1470`) → producer stores `post_idle_unavailable` → salvage keeps 77–79 of 100 raw samples → strict
   validator derives a bounded drift from them → the two messages my run shows. The `--no-sleep` control gives exact agreement.
   Epoch/ULP dependence, Python-version numerics, and changed fixture bytes were each tested and excluded. This matters for THIS
   PR in particular: its whole subject is ULP-scale slack in timestamp comparisons, so a reviewer would rightly ask whether the
   new 1e-6 allowances or the coverage-ULP term could have caused a strict-validation disagreement. They could not: the failing
   comparison is an equality on drift values that consume powers and a stored mean, not timestamps, and the messages appear on
   main where none of the new allowances exist.

5. **Row 11 holds.** Exhibit E: 18 checks pass at beb808bc across Python 3.11 and 3.14, eight full-suite test shards; only
   `gate-ledger` red by design. Exhibit F: main CI success at 078a13a4. Neither the branch nor main shows this failure on Linux.

6. **Why not (b).** The four-shard runner adds load to a test that already fails alone on this host; it cannot make the failure go
   away and is likelier to add a second load flake (ruling 56 saw exactly that with the race test). Its most probable outcome is
   the same one failure or one more, and either way it says nothing new about PR #314. Forty-four minutes of the machine for no
   information is the wrong economy when the first real G2-a window is planned for 09-12 02:56 and the sweep is a p1 gate before
   any G2-a number is consumed. Landing FIXTURE-SENTINEL-CONTROLLER-01 first is also refused as a prerequisite: it is a change to
   the fixture/adapter seam of a claim-bearing path and deserves its own reviewed PR; ruling 44 reason 6 said the same about the
   campaign-helper cure, and a hurried fixture patch slipped under a merge is worse than a named waiver.

7. **Why not (c).** A targeted re-run under the shard runner is more load on a load-sensitive test; it can only add noise. A
   `--no-sleep` replay of that one module is not available without code: the controller test does not plumb the fixture's
   `--no-sleep` flag (that plumbing IS the cure lane). The cheap evidence (c) would want is already on the record: exhibit B's
   pipe-only `--no-sleep` control shows exact agreement when the capture completes. So (c) adds a condition that either cannot be
   met without the cure or adds nothing. I impose instead the cheaper, sharper conditions below.

8. **The residual, named honestly.** Exhibit B F2 is real: a real post-idle capture that times out with enough salvaged samples
   can reach the same producer/validator disagreement in production. That is a fail-closed outcome (the member is strict-invalid
   and cannot be consumed, `run_campaign.py:445`), so it wastes a member, not a number. It is not this gate's question and must not
   be cured inside this PR; it is registered under W8.

**Conditions (all mandatory; any miss is a hold):**

- **W1.** The merge is of head `beb808bc` exactly. If the head moves, every condition is re-established on the new head; this ruling
  does not travel. (Rounds 3–6 after 58d4696b are prose-only; the production tree is unchanged, which is why my run stands for the head.)
- **W2.** Row 9 is discharged BY WAIVER, recorded with exhibit A's tail verbatim (`Ran 5668 tests in 5930.030s` / `FAILED (failures=1,
  skipped=109)` / `rc=1`) and the one test name and assertion line. It is never recorded as "pass", "green", or "effectively clean".
- **W3.** The independence sentence in the row is the hunk-level one from reason 3, and the packet's "disjoint from the PR's code
  changes" sentence is NOT written into the ledger. The row states plainly that `joulewise/controller.py` IS on the failing path and
  IS changed, and why that does not matter.
- **W4.** The row records the three same-state reproductions by name: lead on main 078a13a4 at 05:05 (73 tests, failures=1), seat
  08 with restored bytes, cold judge 35 on 58d4696b at 07:33 (36.840 s, production bytes identical to beb808bc), each qualified
  "alone in-process; machine census not recorded".
- **W5.** Row 11 is quoted with the run id: Actions run 34479219008 at beb808bc, 18 checks pass, `gate-ledger` red by design;
  main 078a13a4 success (run 2026-09-10T11:14:03Z). If CI re-runs before merge it must still be green.
- **W6.** No four-shard replay and no serial re-replay are required for this PR. No second full replay is to be attempted "to see
  if it goes green"; that is the escalation shape the rule forbids.
- **W7.** Addendum obligation, written into the row at merge time: when FIXTURE-SENTINEL-CONTROLLER-01 lands, the magistrate runs
  `python3 -m unittest tests.test_controller` alone on then-current main and records the tail. If it is not `OK`, the failure is an
  open defect on main with its own lane, the merge stands, and the record says so. Until that lane lands, NO further row-9 waiver
  is available for this test name on any PR: the next PR whose replay shows it must either land the cure first or come back to a
  cold gate with a fresh packet. This is the third instance of the sleeping-fixture class (87, 99, 19); registration without a
  landing date is how it became the third.
- **W8.** Exhibit B F2 (production incomplete-capture custody versus strict rederivation) is registered as its own lane or folded
  into FIXTURE-SENTINEL-CONTROLLER-01 with a separate line, named as fail-closed, not cured in this PR.
- **No precedent.** Ruling 44 C4 stands. This is a rule-11 disposition for one replay on one PR. "Same as 35" is not a
  magistrate-level disposition; the next rc≠0 replay is its own trigger.

## Q2 — Exact sentences

**Ledger row 9 evidence (paste verbatim):**

> Row 9 — Lead unpiped full-suite replay on the integration tree, exact tail recorded: DISCHARGED BY WAIVER (cold gate 35, W1–W8), not by
> pass. Single process, alone, `python3 -m unittest discover -s tests` at final head `beb808bc`, 05:52:48–07:31:40 PDT 2026-09-10
> (record 34): `Ran 5668 tests in 5930.030s` / `FAILED (failures=1, skipped=109)` / `rc=1`. The one failure:
> `tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` at `tests/test_controller.py:1675`,
> strict reasons `idle_drift does not match pre/post raw sentinel derivation` and `idle_drift_bound_w does not match effective drift
> derivation`. Pre-existing on the merge base in the same machine state: fails on clean main 078a13a4 (lead, 05:05 PDT, 73 tests,
> failures=1), with the four changed modules restored to HEAD bytes (seat 08), and on 58d4696b whose `joulewise/` tree is byte-identical
> to beb808bc (cold judge 35, 07:33 PDT, 36.840 s); all alone in-process, machine census not recorded. Root cause (record 19, Astra,
> `cause: probable`): the controller fixture sleeps through its post-idle capture against the real 17.5 s deadline
> (`powermetrics.py:1468–1470`); on a slow host the capture times out, the producer stores `post_idle_unavailable`, salvage keeps the
> partial raw samples, and strict validation derives a bounded drift the producer never recorded; `--no-sleep` control agrees exactly;
> epoch/ULP, Python-version, and fixture-byte causes excluded. Independence from this PR, shown by reachability: `git diff --stat
> 078a13a4..beb808bc` intersects the failing path ({tests/test_controller.py, joulewise/adapters/powermetrics.py,
> joulewise/uncertainty_evidence.py, joulewise/controller.py, joulewise/cli.py}) in ONE file, `joulewise/controller.py` (+9/−2), whose three
> hunks all sit inside `cooldown_gate` (:2464; hunks at :2516, :2523, :2552), a function with one caller, the between-member campaign
> cooldown at `controller.py:3072`; the failing test is a single-run HappyPathTests case that configures no cooldown and whose module
> never names `cooldown_gate`; the capture, salvage, and strict-validation code that emits the two reasons is byte-identical to main.
> Row 11: Actions run 34479219008 at beb808bc, 18 checks pass across Python 3.11/3.14 and eight full-suite shards, `gate-ledger` red by
> design; main 078a13a4 CI success. No four-shard or serial re-replay was run or required (35 W6). Cure lane
> FIXTURE-SENTINEL-CONTROLLER-01 registered (kernel branch bookkeeping/2026-09-10-kernel-lanes); record-19 F2 (production incomplete
> capture vs strict rederivation, fail-closed) registered under 35 W8. Waiver is for PR #314 at head beb808bc only; no precedent (44 C4).
> ADDENDUM (to be filled): after FIXTURE-SENTINEL-CONTROLLER-01 lands, `python3 -m unittest tests.test_controller` alone on then-current
> main → [tail, rc]; if not OK, open defect on main with its own lane, merge stands. No further row-9 waiver for this test name on any
> PR until that lane lands.

**Terminal review's row-9 line (paste verbatim):**

> Row 9: WAIVED, not passed — the unpiped single-process replay at beb808bc ran 5668 tests, rc=1, with exactly one failure,
> `test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`, a pre-existing sleeping-fixture
> timeout that fails identically on main 078a13a4 on this host and is unreachable from the PR's only controller hunks (all inside
> `cooldown_gate`); waiver named and conditioned by cold gate 35 (W1–W8), CI green at beb808bc, cure lane FIXTURE-SENTINEL-CONTROLLER-01
> registered, addendum owed when it lands.

## Over-stated lines in the packet (for the record)

1. **00-PACKET option (a), "the failing test's path is disjoint from the PR's code changes"** and the evidence bullet "the failing test
   exercises the powermetrics retry/promotion path in `controller.py`, not `cooldown_gate`". The second is true; the first is false at
   file level (`controller.py` is in both sets). The row must carry the hunk-level argument (W3).
2. **Exhibit A, "reproduced on a clean main checkout … at 05:05"** is the lead's run, not bench-verified in the packet's own session.
   My run on production bytes identical to the head is the in-session reproduction; the row cites all three by author.
3. **Exhibit C, "Bench-timing dependent; CI runners are not loaded the same way."** Supported by exhibit B's stress reproduction, but
   the exact bench bundle from 05:05 was not recovered (B F1). The word "probable" in the verdict is the right one and the row keeps it.
4. **00-PACKET, "the seat-08 replay of the same test with the four production modules restored to HEAD reproduced the failure."**
   Consistent with everything I saw; not independently verified by me (no seat log in the packet). Cited as the packet's claim.
5. **Not over-stated:** exhibit A's command and rc form (process rc, not pipeline); exhibit E's check list; exhibit B's disproved
   alternatives, each of which was actually run.

## Verdict summary

- **Q1:** (a) — merge PR #314 at head beb808bc under a named row-9 waiver, conditions W1–W8: same head; waiver wording never "pass";
  hunk-level independence (controller.py IS touched, all hunks inside `cooldown_gate`, unreachable from the failing single-run test);
  three same-state reproductions named; CI quoted by run id; no re-replay; addendum owed when FIXTURE-SENTINEL-CONTROLLER-01 lands and no
  further waiver for this test until then; F2 registered. Options (b) and (c) refused: more load cannot cure a fixture that oversleeps
  a fixed deadline alone, and a `--no-sleep` module replay needs the very plumbing the cure lane will add.
- **Q2:** Row-9 evidence sentence and terminal-review line supplied verbatim above, with one addendum fill-in.
