# Cold-gate refuter (Opus, CONTRACT lens) — replay verdict under "Low Power Mode"; PR #308 merge

Fresh read-only Opus refuter, paired with the cold Fable judge for cross-model diversity. Worked in the detached worktree
`/Users/edr/code/JouleWise-wt-idle-rc` at `83ab38edcacd67312171c0051cc31cc70a9be682`. Read only 43, 44, P1 (38), P2 (39a/39b),
P4 (42-md + 42-out); did NOT read the judge's ruling (44-coldgate-ruling-replay-verdict.md, written 06:03) to keep the seats
independent. No RUN_STATE / TASK_QUEUE / decision_log / CLAUDE* / AGENTS / skills / memory. All probes foreground, no subagents.

## Probes executed (commands + tails)

1. `git rev-parse HEAD` → `83ab38edcacd67312171c0051cc31cc70a9be682` (correct tree).
2. Timer probe, 20 × `time.sleep(0.05)`, run repeatedly 06:00–06:06 PDT:
   `0.1808`, `0.1532`, `0.1636`, `0.1705`, then `0.1076 0.1074 0.1106 0.1116` (interleaved with `caffeinate -dimsu`:
   `0.1080 0.1083 0.1081 0.1111`), then `0.1127`, `0.1068`, `0.1097`.
   → slack factor moved from **3.6× to 2.1× within ~4 minutes**, with powermode unchanged. `caffeinate` made no difference
   (the apparent early improvement was drift, exposed by the interleaved A/B). `taskpolicy -c background` gave `0.1200` —
   *lower* than the contemporaneous default-QoS baseline, i.e. QoS clamp is not the knob either.
3. `sleep(0.01)` ×50 → `0.0720` (7.2×). Added latency is not a fixed slack: +62 ms on a 10 ms sleep, +131 ms on a 50 ms sleep.
4. `pmset -g custom` → AC Power `powermode 1`, Battery `powermode 0`; `pmset -g batt` → "AC Power", 100 %, charged.
   `pmset -g therm` → no thermal or performance warning level recorded. Confirms the packet's machine-state facts.
5. `sysctl kern.timer*`: `coalescing_enabled: 1` (macOS default), `kern.timer_coalesce_bg_ns_max: 100000000` (100 ms),
   `tier3_ns_max: 75000000`. `hw.ncpu 16` (12 P + 4 E), load average 1.6–1.9 throughout.
6. `ps -Ao %cpu,command | sort -rn | head -8` → top consumer was the **cold judge's own** `python -m unittest
   …IdleAdmissionCoreVerdictTests.test_environment_refusal…` at 42.5 %; then the headless magistrate `claude -p` 2.6 %,
   Wispr Flow 2.1 %, Spotify 0.9 %, `scripts/magistrate_watchdog.py` 0.7 %, plus a leftover
   `joulewise-exit-witness-*/writer-fixtures/fake_sampler.py`. A later sample had `dasd` at 11.7 %.
7. Fixture timed twice, identical argv, same tree, 2 minutes apart, powermode 1 both times:
   - 06:01 → `real 18.94  user 0.93  sys 0.05`  (over the 17.5 s timeout → would FAIL)
   - 06:03 → `real 11.58  user 0.92  sys 0.05`  (well under 17.5 s → would PASS)
8. `_capture_timeout_s` read at `joulewise/adapters/powermetrics.py:1468–1470`:
   `nominal_s = count * (interval_ms/1000); return max(15.0, nominal_s * 1.5 + 10.0)` → for n=100, i=50 ms:
   `max(15, 5.0*1.5+10) = 17.5 s`. **17.5 s confirmed.** Fixture sleeps: `tests/fixtures/fake_powermetrics_process.py:63–70`,
   one `sleep(interval_s)` at index 0 plus one per index ≥ 1 = 100 × 50 ms = 5.0 s nominal → headroom is exactly **3.5×**.
9. Single failing test re-run at 83ab38ed, powermode still 1, judge's run still active on the box:
   `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 -m unittest
   tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_environment_refusal_does_not_hide_valid_retry_telemetry`
   → `Ran 1 test in 24.890s` / **`OK`**.
10. `git diff --stat 83ab38ed..5d13d0e6 -- joulewise scripts tests` → `tests/test_gen_state.py | 3 ++-` (only).
    `git diff --stat 83ab38ed..5db38b58 -- joulewise scripts tests` → `joulewise/night_gate.py 120`, `scripts/run_night.py 7`,
    `tests/test_night_gate.py 61`, `tests/test_run_night.py 45`.
    `git diff --name-only` on both, grepped for `powermetrics|fake_powermetrics|test_run_campaign` → **no hits**.
11. File mtimes: `42-bench-rootcause-low-power-mode.md` = **06:04:36**, i.e. edited *after* packet assembly (05:58) and after the
    judge's ruling (06:03). Its §3 now reads "Machine state co-occurring with the slack … inferred from co-occurrence, not from a
    toggle"; when I read it at ~06:00 the same paragraph read "**Why the timers are slow**: `pmset -g custom` → AC Power:
    powermode 1". `44-coldgate-packet.sha256` pins only files 43 and 44 — P1–P6 are unpinned, and P4 in fact mutated mid-gate.

## Refutations attempted

| # | Claim (P4) | Attempt | Result |
|---|---|---|---|
| R1 | "Why the timers are slow: … powermode 1" — LPM causes ~3.5× sleep inflation | Re-ran fixture and the failing test with powermode still 1 | **REFUTED.** Fixture 18.94 s → 11.58 s two minutes apart; the failing test returned `OK` in 24.9 s at 83ab38ed under powermode 1. Powermode 1 is neither sufficient nor stable-effect. (The 06:04 amendment concedes half of this.) |
| R2 | `_capture_timeout_s` = 17.5 s | Read lines 1468–1470 and the fixture sleep loop | **CONFIRMED**, and sharpened: headroom is exactly 3.5× nominal, so the test flips on any slack excursion above 3.5× — measured slack that morning ranged 2.1×–3.6×. This is a knife-edge, not a state. |
| R3 | "Nothing in either PR touches this path" | Both `git diff --stat` and a name-only grep for the three files in the failure path | **CONFIRMED.** #308 touches one test file (gen_state); #309 touches night_gate/run_night only. Neither touches `powermetrics.py`, the fixture, or `test_run_campaign.py`. |
| R4 | Failures are CPU-contention artefacts from the magistrate's own fleet | `/usr/bin/time -p` on the fixture; `ps`; load average | **Partly excluded, not cleanly.** The 18.94 s run used only 0.93 s user + 0.05 s sys — it was sleeping, not starved, and load 1.6–1.9 on 16 cores is no run-queue pressure. But wake-latency contention needs no CPU starvation, and the packet records nothing about what else ran during the replay or the two "alone" runs. |
| R5 | Timer coalescing (kernel default) explains it | `sysctl kern.timer*` ceilings vs observed | **Insufficient as stated.** Observed added latency was +131 ms on a 50 ms sleep, above every coalescing window ceiling on this kernel (`bg_ns_max` 100 ms, `tier3_ns_max` 75 ms). Coalescing alone cannot produce it. |
| R6 | Background-QoS inheritance from the launchd→magistrate process tree | `taskpolicy -c background` probe; `launchctl submit` probe from a launchd parent | **Not excluded.** Background clamp made the probe *faster* than the contemporaneous baseline, which argues against QoS as the driver; but the `launchctl submit` control produced no output before I moved on, so no clean non-descendant baseline exists. Every measurement in this gate — magistrate's, judge's, mine — descends from the same launchd-spawned tree. |

## Alternative causes not excluded

1. **Plain non-determinism in a wall-clock-coupled test** — now demonstrated, and the leading explanation. Same tree, same
   powermode, same argv: PASS and FAIL within minutes. The packet never ran the repeat-under-constant-state control.
2. **Contention/wake-latency from the magistrate's own fleet.** The replay itself ran `shards=4` in parallel; the two "alone"
   class runs are "alone in the process", not "alone on the machine", and the packet records neither their concurrency with each
   other nor the rest of the fleet. The four files (38, 39a, 39b, 40) share mtime 05:45:50, so provenance can't be recovered from
   the packet.
3. **Background-QoS timer treatment inherited from the LaunchAgent process tree** (R6) — no non-descendant control was obtained.
4. **macOS background daemons** (`dasd` at 11.7 % in one sample, `biomesyncd`, WindowServer) bursting on their own schedules.
5. Thermal/E-core residency — weakly excluded (`pmset -g therm` records no warning level).

## Contract-lens answer on row 9

Row 9: *"Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded."*

- **Letter.** The row states three obligations — unpiped, on the integration tree, exact tail recorded — and does **not** contain
  the word green or `rc=0`. Row 11 (*"CI green on final head"*) does. On an expressio-unius reading, a recorded FAIL tail
  satisfies row 9's text. So merging is not a *textual* violation.
- **But the letter is a drafting hole, not a licence.** A gate row that is discharged by pasting whatever came out cannot fail;
  it is a recording obligation wearing a gate's clothes. Reading it that way silently converts the twelve-row ledger into an
  eleven-row one. Choosing that reading *is itself an amendment of the row's meaning*, and amending a gate row is exactly what
  the magistrate/lieutenant may not do alone — which is why this cold gate is the right instrument.
- **My contract answer:** "exact tail recorded" is the *evidence* requirement, not the *pass* criterion. A non-green tail
  discharges row 9 only under an explicit, recorded waiver that names (a) the exact failing set, (b) positive evidence the
  failures are tree-independent, and (c) a bounded discharge condition. Merging on the bare letter, without the waiver written
  into the ledger, violates the spirit and should be recorded as a waiver, not as a pass. Ed should be asked to amend row 9's
  wording to say `rc=0, or a written waiver naming the failing set and its discharge` — otherwise this recurs.
- **For a CODE PR (#309) I would demand strictly more:** no waiver at all while a green replay is obtainable by retry — and my
  probe proves it is. Specifically: full-suite replay to **rc=0** (retries permitted, bounded and *every* tail recorded, so the
  flake rate is on the record rather than hidden), plus targeted green runs of `tests/test_night_gate.py` and
  `tests/test_run_night.py` (the changed surface) recorded, plus CI green on the final head. The docs-PR waiver rests entirely on
  "the diff cannot reach the failing path"; #309's diff *is* code, so that premise is unavailable to it.

## Over-statements

1. **P4 §3, original text (read at ~06:00, since amended at 06:04):** "**Why the timers are slow**: `pmset -g custom` → **AC
   Power: powermode 1**". Causation asserted from a single co-occurrence with no toggle. Refuted by R1. The 06:04 amendment
   ("inferred from co-occurrence, not from a toggle") concedes the epistemics but still keeps LPM as the headline of the
   filename and of every downstream sentence.
2. **Charge, context paragraph:** "the bench diagnosis attributes the failures to macOS Low Power Mode … so a sleeping test
   fixture overruns a 17.5 s capture timeout. **Turning Low Power Mode off needs sudo (the owner, Ed, who is away…)**." This
   frames Ed's sudo as the only route to a green replay and thereby biases Q1's option set: none of (a)/(b)/(c) is
   "re-run it — it's flaky", which is the correct and cheapest option. A cold judge ruling from this packet is being offered a
   menu that omits the right answer.
3. **P4 "Exact tails" / packet index: "Replay alone at 5d13d0e6"** and **"Class alone at 5d13d0e6: `Ran 71 tests in
   154.947s`"**. "Alone" is doing unpaid work: the replay ran `shards=4` concurrently, and nothing records what else was on the
   machine. Say "class alone in-process; machine state not recorded".
4. **P4 §5:** "Yesterday's record 99gm … **is consistent with Low Power Mode having been OFF then**, or with the fixture running
   under a less coalesced timer while an interactive user was at the console". Two speculations offered as reconciliation when
   the parsimonious one — a flaky wall-clock test that happened to pass — was available and is now proven.
5. **P1 tail, recorded verbatim into row 9:** `shards=4 … failures=4 … **failed_shards=4** result=FAIL`, while shards 1–3 each
   report `result=PASS`. Either `failed_shards` is a shard index misnamed as a count, or the summary is wrong. Row 9 rests on
   the fidelity of this exact string; the discrepancy should be resolved or annotated before it is pasted into the ledger.
6. **Packet integrity:** `44-coldgate-packet.sha256` pins only 43 and 44. P4 was edited at 06:04:36 — after assembly and after
   the judge's ruling file appeared. A cold gate whose evidence can move under the judge is not mechanically assembled in the
   sense the packet claims ("Assembled mechanically by magistrate activation 2145630c"). Hash P1–P6 too.

## Recommended answers Q1–Q4 (refuter's position)

**Q1 — (a) merge, but on a different and stricter condition than the packet's, and with the root cause corrected.**
I accept the *tree-independence* conclusion — it stands on four legs that survive my probing: the diff cannot reach the failing
path (R3), the failures reproduce on a main-equivalent tree, Linux CI is green at both heads, and the fixture overrun is
wall-clock, not code. I reject the *root cause* as recorded. Conditions I would require before the merge button:
(i) row 9 records the exact FAIL tail **plus** the corrected diagnosis — a transient wall-clock timeout flake against a 3.5×
timeout margin, with the LPM attribution marked refuted, citing the 18.94 s / 11.58 s pair and the `OK` re-run;
(ii) a **green targeted re-run recorded as an addendum before merge, not after** — the 71-test class alone takes ~155 s and
needs no sudo and no Ed; I already have 1 of the 4 green in 24.9 s at 83ab38ed under powermode 1;
(iii) if that re-run is not green, fall back to holding.
I reject **(b)** outright: it is premised on a refuted cause, and it would park a docs PR on an absent owner's sudo for nothing.
I reject **(c)** as a *blocker* — the fixture-timeout cure is real and should be registered as a lane, but it is not this PR's,
and a docs PR should not be held hostage to it.

**Q2 — No, the same disposition does not carry to #309.** Acceptance condition for the code PR: full-suite replay **rc=0**, with
retries permitted and bounded (I would say ≤3) and every tail recorded so the flake rate is visible; plus recorded green runs of
`tests/test_night_gate.py` and `tests/test_run_night.py`; plus CI green on the final head. Rationale: the docs-PR waiver is
purchased entirely by "the diff cannot reach this path", and #309's diff is 127 changed lines of `night_gate.py` and
`run_night.py`. And now that the failure is known to be retry-curable rather than a standing machine state, "cannot get a green
replay" is no longer true, so no waiver is warranted at all.

**Q3 — Register a lane, yes; but not the one the packet proposes, and do not gate on powermode.** The claim-bearing finding is
not Low Power Mode; it is that the capture timeout `max(15, n·i·1.5 + 10)` leaves only 3.5× headroom over nominal at n=100/i=50 ms
while this machine's measured wall-clock slack ranged 2.1×–3.6× inside five minutes. A real night hitting a slack excursion gets
a real `powermetrics` capture killed at the same deadline → `post_idle_unavailable` → strict-invalid members, with or without
LPM. Lane (registration only, design later): **night preflight measures and records the sleep-slack factor and the capture-timeout
margin, and records `pmset -g custom` powermode as run-record metadata**; flag when measured margin is thin. Gating on powermode
alone would gate on a demonstrated non-cause. On arming: a rehearsal/stub night under powermode 1 is fine; for a claim-bearing
night I would require the power state recorded in the run record and would prefer powermode 0 for comparability with the
calibration corpus — that comparability concern is genuine and independent of anything in this timeout story. Email Ed that the
sudo item is a comparability nicety, **not** a blocker, so it does not become a false dependency on an absent owner.

**Q4 — Over-stated:** the six items above; the load-bearing ones are (1) the LPM causal claim, (2) the charge's "needs sudo"
framing that removed the correct option from the judge's menu, and (3) the unqualified "alone".

## Verdict

**Packet flawed: its named root cause is refuted — the same test returns `OK` on the same tree with `powermode 1` still set, and
the fixture ran 18.94 s then 11.58 s two minutes apart against a 17.5 s timeout — so the tree-independence conclusion survives
but the "Low Power Mode / needs Ed's sudo" framing must not carry into row 9, and the correct discharge (retry until green,
recorded) was available all along.**
