# Cold-gate ruling — replay verdict under Low Power Mode; merge of PR #308 and the shape for PR #309

Judge: cold Fable 5.1 session (non-interactive, single turn), convened 2026-09-09 under rule 11 by magistrate activation 2145630c.
Working directory: `/Users/edr/code/JouleWise-wt-idle-rc`, detached at `83ab38edcacd67312171c0051cc31cc70a9be682` (origin/main), clean.
Packet: `43-coldgate-packet-replay-verdict.md` (P1–P6 read in full or to their verdict sections; P7/P8 re-executed by me). Charge: `44-coldgate-charge-replay-verdict.md`.

## Contamination disclosure

Not clean, and I am recording exactly what leaked. Beyond the packet I did NOT open RUN_STATE.md, TASK_QUEUE.md,
docs/decision_log.md, AGENTS.md, any skill file, or any memory file. However, the harness injected into my system prompt,
before I read anything:

1. `~/.claude/CLAUDE.md` (global): multi-model orchestration pointers and a writing standard. No bearing on these questions.
2. The worktree's `CLAUDE.md`: the Codex MCP bridge notes (WRITE_SCOPE, `[QUIET-MAC]` rule, bridge depth). No bearing.
3. The auto-memory INDEX `MEMORY.md` (one line per memory, ~50 lines). I did not open any memory file, but the index lines
   themselves carry project facts. The ones that could bear on this ruling, which I name so the reader can discount them:
   "Merge authority with review — STANDING gh self-merge (D-072) after the full gate shape"; "Threat-model prune (D-161) —
   fail-closed only for physics/evidence/pre-registration"; "Docs are context, code is truth"; "Checkpoint 2026-09-08 — next =
   CLONE-READINESS-01 → G2-a"; "Ed remote approval for windows — email for every stand-down + relaunch approval"; "Packet facts
   bench-verified — never label a fact bench-verified without running it this session". I have ruled from the packet and my own
   probes only; where a ruling below happens to agree with one of those lines, the reason given is the packet evidence, not the line.
4. General knowledge of macOS power management and Python's `subprocess`/`time.sleep` behaviour, which I used.

The charge's expectation ("nothing but general software judgment") is therefore not met on item 3. Whoever consumes this ruling
should weigh it as a cold read of the packet by a judge who has seen the project's memory index headlines.

## Probes executed (all foreground, read-only except two temp files I removed)

```
$ git rev-parse HEAD ; git status --short
83ab38edcacd67312171c0051cc31cc70a9be682            (clean)

$ gh pr checks 308        → gate-ledger fail; build, installed-wheel, pr-fast (1,2), calibration-exits-exclusive (3.11,3.14),
                            calibration-writer-crash-matrix-exclusive ×4, test (3.11, 1–4), test (3.14, 1–4): ALL pass
$ gh pr checks 309        → identical shape: only gate-ledger fail; every test/build check pass
$ gh pr view 308 --json headRefOid,files → head 5d13d0e6; files = RUN_STATE.md, TASK_QUEUE.md, docs/process/NIGHT_HANDBACK.md,
                            docs/process/state_kernel.json, docs/process_traces/** (many), tests/test_gen_state.py
$ gh pr view 309 --json headRefOid,files → head 5db38b58; files = docs/contracts/pack_night_go_receipt.md, joulewise/night_gate.py,
                            scripts/run_night.py, tests/test_night_gate.py, tests/test_run_night.py
$ git merge-base --is-ancestor 83ab38ed 5d13d0e6 → yes ; … 5db38b58 → yes
$ git diff --stat 83ab38ed..5d13d0e6 -- joulewise scripts tests
 tests/test_gen_state.py | 3 ++-      (adds "NIGHT-GATE-STUB-CHAIN-01" to EXPECTED_IDS; count 156 → 157)
$ git diff --stat 83ab38ed..5db38b58 -- joulewise scripts tests
 joulewise/night_gate.py 120 | scripts/run_night.py 7 | tests/test_night_gate.py 61 | tests/test_run_night.py 45
 (neither PR touches tests/test_run_campaign.py, joulewise/adapters/powermetrics.py, joulewise/uncertainty_evidence.py,
  joulewise/controller.py, joulewise/cli.py, scripts/run_campaign.py, or tests/fixtures/fake_powermetrics_process.py)

$ sed -n 1468,1470p joulewise/adapters/powermetrics.py
    def _capture_timeout_s(self, config: BenchmarkConfig, count: int) -> float:
        nominal_s = count * (self._interval_ms(config) / 1000.0)
        return max(15.0, nominal_s * 1.5 + 10.0)              → 100 × 0.050 × 1.5 + 10 = 17.5 s   (P4 §1 confirmed)

$ pmset -g custom          → Battery Power: powermode 0 ; AC Power: powermode 1   (P4 §3 confirmed)
$ pmset -g batt            → Now drawing from 'AC Power'; InternalBattery-0 100%; charged   (P4 §3 confirmed)
$ python3 -c "…time.sleep(0.05)×20…"  → 0.17921999164973385   (3.58× nominal; P4 §2 measured 0.1769 s — confirmed)

$ /usr/bin/time -p python3 tests/fixtures/fake_powermetrics_process.py -n 100 -b 0 -i 50 --samplers cpu_power,gpu_power,ane_power,thermal --format plist -o /tmp/coldgate-fixture-probe.plist
real 18.02  user 0.92  sys 0.05      (> 17.5 s timeout; P4 §2 measured 18.58 s — confirmed)

$ PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_environment_refusal_does_not_hide_valid_retry_telemetry
  File ".../tests/test_run_campaign.py", line 9581, in _produced_retry_member
    self.assertIs(evaluation.strict_valid, expected_strict_valid)
AssertionError: False is not True
Ran 1 test in 37.831s
FAILED (failures=1)
rc=1                                  (reproduced on MAIN itself, 83ab38ed, same machine state, this session)

$ git log --format='%h %ci' -1 58d9225b → 58d9225b 2026-09-08 21:15:00 -0700   (the head of yesterday's rc-0 replay record 99gm)
```

Not probed (cannot without sudo): whether the slack disappears with powermode 0; whether real `powermetrics -i 50` slips under
powermode 1. Not probed (out of budget): the full class of 71 tests; the full suite.

## Q1 — PR #308 (docs + bookkeeping checkpoint)

**Ruling: (a) — merge now, with conditions.** Row 9 is satisfied by recording the exact rc=1 tail verbatim plus the root-cause
record (P4) and this ruling; it is NOT satisfied by recording the replay as "green", "pass", or "effectively clean".

Reasons and the evidence relied on:

1. **Row 9's purpose is regression detection on the integration tree, and that purpose was served.** The replay ran 5636 tests
   with exactly 4 failures, all four in `IdleAdmissionCoreVerdictTests` via the one shared helper assertion at
   `tests/test_run_campaign.py:9581` (P1, all four FAIL blocks). The identical four fail alone at the PR head 5d13d0e6 (P2a,
   `Ran 71 tests … FAILED (failures=4)`), at main+#309 5db38b58 (P2b, same), and — decisive for a docs PR — on main itself at
   83ab38ed (P4 diagnostic out, `Ran 1 test in 38.839s FAILED`; reproduced by me this session, 37.831 s, rc=1). A failure that is
   present on the merge base in the same machine state cannot be a regression introduced by the PR.
2. **The PR cannot reach the failing path.** Its only non-doc change is two lines in `tests/test_gen_state.py` (my diffstat above);
   none of the seven files on the failing path is touched. This is a structural, not statistical, argument.
3. **The mechanism is bench-established, not merely narrated.** Timeout formula confirmed at `powermetrics.py:1468–1470`; sleep
   slack reproduced (0.179 s per 50 ms sleep); the fixture alone overruns the timeout (18.02 s vs 17.5 s); the diagnostic (P4 out)
   shows `subprocess.TimeoutExpired … timed out after 17.5 seconds` on `powermetrics_idle_post.plist`, the producer storing
   `post_idle_unavailable`, and the strict validator deriving `bounded 0.9927 W` from the 94 samples that did land — the exact
   pair of strict problems that flip `strict_valid` to False. Every link in the chain from timer slack to the assertion is observed.
4. **Row 11 holds:** every test shard passes at 5d13d0e6 on Linux, Python 3.11 and 3.14 (my `gh pr checks 308`). Only
   `gate-ledger` is red, by design until the ledger is filled.
5. **Why not (b).** Holding a docs/bookkeeping PR on a machine-state nuisance that is proven independent of the change buys no
   soundness, and the machine state is Ed's to change on an unknown timeline. Holding would also leave the checkpoint (RUN_STATE,
   kernel, harvest record) unmerged, which is itself a hazard for the successor sessions that read them.
6. **Why not (c).** A fixture-timeout cure is a change to the adapter/fixture seam of a claim-bearing path
   (`reduce.py` consumes `idle_drift_bound_w`, per P3). It deserves its own reviewed PR and must not be a prerequisite slipped
   under a docs merge; nor should a docs merge be the occasion for a hurried loosening of `_capture_timeout_s` in production code.

**Conditions on (a)** (all mandatory; the magistrate records them in the ledger row, not in prose elsewhere):

- C1. Row 9 quotes the tail verbatim, including `WORKERS SUMMARY shards=4 modules=221 tests=5636 failures=4 errors=0 skipped=108
  failed_shards=4 result=FAIL` and `rc=1`, followed by the four test names and the words "pre-existing on merge base 83ab38ed in
  the same machine state (powermode 1 on AC); see 42-bench-rootcause-low-power-mode.md and 44-coldgate-ruling-replay-verdict.md".
- C2. Row 9 states the independence argument in one line: `git diff --stat 83ab38ed..5d13d0e6 -- joulewise scripts tests` =
  `tests/test_gen_state.py` only.
- C3. **Addendum obligation.** After Ed sets powermode 0 (or a fixture cure merges, whichever first), the magistrate re-runs
  `python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests` (71 tests) on then-current main and records the
  tail as a dated addendum to this ledger row. If it does NOT go green with powermode 0, the Low Power Mode attribution is
  falsified and the four failures become an open defect on main with its own lane; the merge stands (docs PR) but the record
  must say so.
- C4. **No precedent.** This is a rule-11 disposition for one replay on one PR. Any future rc≠0 replay is its own mandatory
  trigger; "same as 44" is not a magistrate-level disposition.
- C5. A kernel lane is registered for the test-side coupling (fixture sleeps under a wall-clock timeout; cure = fixture-aware
  timeout or a non-sleeping fixture; P4 "Test-side" paragraph). Registration only.

## Q2 — PR #309 (code cure in the night gate), replay not yet run

**Ruling: the same disposition MAY apply, under a strictly stronger acceptance condition; anything short of it is a hold.**
Code PRs get a narrower door than docs PRs because the independence argument for a docs PR is structural (no code reached), while
for a code PR it must be shown, not assumed.

Acceptance condition for #309 (all of the following, exactly):

- A1. Replay alone on the integration tree (main + #309, i.e. 5db38b58 or its rebase onto then-main) records
  `tests=5636` (or the correct count if main moved), `errors=0`, and failures = **exactly** the set
  {`test_cpu_admission_reads_final_attempt_telemetry`, `test_environment_refusal_does_not_hide_valid_retry_telemetry`,
  `test_missing_final_attempt_telemetry_fails_closed`, `test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound`},
  each failing at `test_run_campaign.py:9581` with `AssertionError: False is not True`. A fifth failure, any error, a different
  test name, or a different assertion line is a hold — no "near enough".
- A2. Independence shown by pathspec, recorded in the row: the PR's changed files
  ({docs/contracts/pack_night_go_receipt.md, joulewise/night_gate.py, scripts/run_night.py, tests/test_night_gate.py,
  tests/test_run_night.py} — my `gh pr view 309`) intersect the failing path
  ({tests/test_run_campaign.py, joulewise/adapters/powermetrics.py, joulewise/uncertainty_evidence.py, joulewise/controller.py,
  joulewise/cli.py, scripts/run_campaign.py, tests/fixtures/fake_powermetrics_process.py}) = ∅. Verified by me at 5db38b58; must be
  re-verified if the head moves. Additionally the row must confirm the PR does not import-touch the failing path indirectly
  (i.e. `night_gate.py`/`run_night.py` are not imported by `run_campaign`/`controller`) — one grep line, recorded.
- A3. The four tests fail identically on the merge base in the same machine state, same session — already satisfied by P4 out and
  my rerun at 83ab38ed. If the merge base moves, re-establish it.
- A4. The tests that DO cover the PR's files pass locally on the integration tree in the same session:
  `python3 -m unittest tests.test_night_gate tests.test_run_night` (P6a records 136 tests rc 0 on the branch worktree; this must
  be re-run on the integration tree, not the branch — row 9's own wording).
- A5. Row 11: CI green on the final head (currently true at 5db38b58, my `gh pr checks 309`).
- A6. Same addendum obligation as Q1-C3 (class re-run green after powermode 0), and P6a's verdict sentence ("…once … the full-suite
  replay alone on the integration tree records rc 0") is amended by a dated addendum to file 31 citing this ruling — not silently.

Difference from the docs PR, stated plainly: for #308 the diffstat alone closes the question; for #309 the magistrate must
additionally (A2 import check, A4 integration-tree run of the covering tests) demonstrate that the cure's own blast radius was
exercised green on the same tree where the four unrelated failures were observed. If the replay for #309 shows anything other
than exactly the four, it holds for a green replay or a fixture cure regardless of this ruling.

## Q3 — Is Low Power Mode claim-bearing for real nights? Lane? Arming?

**Claim-bearing: yes, in two distinct ways, of different severity.**

1. **Machine-state validity (claim-bearing, severe).** Low Power Mode on Apple Silicon changes CPU/GPU frequency caps, scheduling,
   and timer coalescing. Energy-per-token and idle floors measured under powermode 1 are measurements of a different machine than
   the calibration corpus and any night measured under powermode 0. The packet does not tell me which state the calibration
   corpus was taken in, and neither does my probe set; that is exactly the problem — the state is currently **unrecorded**, so a
   night could be consumed against a calibration taken in the other state with nothing in the receipt to catch it. Evidence:
   `pmset -g custom` shows powermode differs by power source (AC 1, battery 0), so the state can flip without any repo action.
2. **Availability (fail-closed, not silent).** A real post-idle `powermetrics` capture under the same `_capture_timeout_s` could
   time out if the real sampler slips as the Python fixture does; the observed outcome is `post_idle_unavailable` → strict-invalid
   members → refused, i.e. a wasted night, not a wrong number. I could not test whether real `powermetrics` (a system daemon, not
   `time.sleep`) slips under powermode 1; P4's "if the real sampler slips the same way" is correctly conditional and should stay so.

**Lane: yes, register it now (registration only, design later).** Content of the registration: night readiness / arm preflight
records `pmset -g custom` (at minimum `powermode` for the active source and `pmset -g batt` source) into the plan and the receipt;
consumption-side validation refuses or flags a night whose recorded powermode differs from the calibration corpus's recorded
powermode; and the calibration corpus's own powermode must be established (by record if it exists, by Ed's recollection with a
stated confidence if not). The design question of refuse-vs-flag is deferred; the recording is not controversial.

**Arming recommendation for Ed (no gate installed by the magistrate):**

- **Rehearsal STUB nights** (`sleep 2; echo REHEARSAL`, no capture) may be armed under powermode 1; they measure nothing. Note in
  the arm record that the stub does not exercise the capture-timeout seam, so a green stub says nothing about item 2 above.
- **No real or pack-bound measurement night should be armed while powermode 1 is set**, until either Ed sets powermode 0
  (`sudo pmset -a powermode 0`, or via System Settings → Battery → Low Power Mode "Never"), or a ruling records that the
  calibration corpus was itself taken under powermode 1 and the night will be consumed only against it. The cost of arming anyway
  is at best a refused night (item 2) and at worst a consumable night in an unrecorded machine state (item 1).
- Ask Ed, in the same email, whether Low Power Mode was ON during the 2026-09-08 21:15 replay (58d9225b, rc 0). If it was, the
  attribution in P4 is wrong and C3's addendum will show it.

## Q4 — Over-stated or unsupported lines in the packet

1. **P4 title and §3, "local … failures = macOS Low Power Mode timer slack" / "Why the timers are slow: … powermode 1".**
   The slack is measured; the fixture overrun is measured; the assertion chain is measured. The step from "powermode 1 is set"
   to "powermode 1 is the cause of the slack" is inferred from co-occurrence, not from a toggle. It should read "consistent with"
   until powermode 0 removes the slack. A competing cause I could not exclude: macOS timer coalescing applied to background-QoS
   process trees (headless sessions); my probe ran from another headless session and showed the same slack, which is consistent
   with a system-wide cause but does not discriminate. `kern.timer.coalescing_enabled: 1` (P4 §3) is the macOS default and is
   not evidence for Low Power Mode; it should not sit in the "why" list.
2. **Charge, "reproduced … on a main-equivalent tree".** 5db38b58 is main + #309, not main. Main itself (83ab38ed) is covered
   only by the single-test diagnostic (P4 out) and now by my rerun, not by the 71-test class run. Adequate for this ruling
   (Q1 reason 1), but the phrase should say "main + #309 (5db38b58), and on main itself for one of the four tests".
3. **Charge, "its only non-doc change is one expected-ID line".** It is two lines: the ID and the count 156 → 157
   (`tests/test_gen_state.py:24` and `:727`). Immaterial to the ruling; material to the "exact" standard the ledger claims.
4. **P1 tail, `failed_shards=4`.** Only shard index 4/4 failed; shards 1–3 record `result=PASS`. Whether this field is a count
   or the failing shard's index is ambiguous from the tail; the row-9 record must quote it verbatim and must not gloss it as
   "four shards failed".
5. **P4 §5, "consistent with Low Power Mode having been OFF then, or with … a less coalesced timer while an interactive user was
   at the console".** Honest speculation, correctly labelled; but it means the packet does not establish when the machine entered
   this state, so P4's chain has an unexplained temporal gap that C3 exists to close.
6. **P6a verdict line, "CLEAN for merge … once … the full-suite replay … records rc 0".** Not over-stated when written, but it
   is now a standing commitment in the trace that Q2 would amend. It must be amended by addendum (A6), otherwise the trace will
   contradict the ledger.
7. **P3 (Astra) is not over-stated** — it explicitly refuses to name a cause ("hypothesis, not a confirmed diagnosis") and its
   F2 warning ("do not weaken strict equality or declare scientific neutrality before identifying the divergent input") is the
   right fence for any fixture cure. P4 §1 then supplies exactly the divergent input P3 asked for. I note that P3's producer
   fallback hypothesis (capture exception → `post_idle_unavailable` while retained bytes survive) is the mechanism P4 observed;
   the packet index's summary "derivation located; execution blocked by sandbox" undersells P3 slightly — it located the
   mechanism as well.

## Verdict summary

- **Q1:** (a) — merge #308 now; row 9 records the verbatim rc=1 tail + names + P4 + this ruling, the diffstat independence line,
  and an addendum obligation to re-run the 71-test class green after powermode 0; no precedent; fixture-coupling lane registered.
- **Q2:** Same disposition available for #309 ONLY under A1–A6: exactly those four failures by name and assertion line, pathspec
  and import independence recorded, covering tests re-run green on the integration tree, CI green, same addendum; anything else
  is a hold.
- **Q3:** Claim-bearing (unrecorded machine state ≠ calibration state; capture timeout is fail-closed but wastes a night);
  register the powermode preflight/record lane now; stub nights may arm, no real or pack-bound night while powermode 1 is set
  until Ed changes it or a ruling binds the night to a same-state calibration; ask Ed whether it was on during the 09-08 replay.
- **Q4:** P4's causal wording ("= Low Power Mode") outruns its toggle-free evidence and should read "consistent with";
  `kern.timer.coalescing_enabled` is not evidence; "main-equivalent" and "one line" are loose; `failed_shards=4` must be quoted,
  not glossed; P6a's rc-0 sentence needs a dated addendum.
