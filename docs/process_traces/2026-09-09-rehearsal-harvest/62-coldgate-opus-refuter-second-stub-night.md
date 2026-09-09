# 62 — Opus contract-lens refuter (fresh, read-only): does the merged gate cure require a SECOND REHEARSAL_STUB night?

Paired with the cold Fable judge on packet 60 / charge 61. I did not read 61-coldgate-ruling-*. Worktree
`/Users/edr/code/JouleWise-wt-kernel-fold` at main `7ca2908f` (detached; canonical untouched). No edits except this file.
Contamination: the harness injected the global CLAUDE.md, the project CLAUDE.md/CLAUDE.local.md and the MEMORY.md index into my
system prompt before I read anything; I opened none of them and did not rely on them. `decision_log.md` read only via P1.

## Probes executed

| # | Command | Result (tail) |
|---|---|---|
| 1 | `git log --oneline -5 origin/main` | `7ca2908f` bookkeeping; `a52810c9` **Merge NIGHT-GATE-STUB-CHAIN-01 (PR #309)**; `5f234d89`; `6d76f964`; `a3da3463`. Cure **is** merged on main. |
| 2 | `git show --stat a52810c9` | 5 files, 225 insertions(+), 100 deletions(-): `docs/contracts/pack_night_go_receipt.md`, `joulewise/night_gate.py`, `scripts/run_night.py`, `tests/test_night_gate.py`, `tests/test_run_night.py`. |
| 3 | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate tests.test_run_night` | `Ran 136 tests in 9.555s` … `OK`. |
| 4 | `git diff --stat 5f234d89 6d76f964 -- tests/test_gen_state.py` | **empty** — the branch does not touch `test_gen_state.py` (see Over-statements O-1). |
| 5 | `launchctl list \| grep -i joulewise` | `-  0  com.joulewise.magistrate` only. Nothing night-related armed. |
| 6 | `ls /Users/edr/night-custody` | `active-campaigns`, `magistrate`, `magistrate-bench`, `retired-v1` — exactly as 21i records. No plan root. |
| 7 | `python3` read of the harvested `night-receipt.json` byte copy (`21b-…/night-harvest/night-receipt.json`) | verdict `REFUSED`; rows in order: `FAIL['detail']`, `NOT_APPLICABLE[]`, `FAIL['agent_census_exit_code','agent_census_stdout']`, `FAIL['detail']`, `FAIL[heads…]`. **This is the load-bearing probe — see below.** |
| 8 | `pmset -g custom` | Battery `powermode 0`; **AC `powermode 1`** (Low Power Mode ON on AC). |
| 9 | `python3` read of `docs/process_traces/2026-09-01-unattended/cold_start.json` | `durations_ms [5450,6300,5007,5303,5250]`, `median_ms 5303`. `scripts/run_night.py:51 COURIER_DEADLINE_S = 300`. |
| 10 | P2 excerpt vs full 21i (`docs/process_traces/2026-09-02-hands-free-week/21i-…-harvest-record.md` lines 60–76) | Excerpt is verbatim and complete for the six items. Accurate. |

Every packet fact I could check is TRUE: cure merged, tests green, nothing armed, custody tree as described, P2 faithful to 21i.

## Refutations attempted

- **"The cure is only unit-tested, so the cured *receipt path* is the untested surface."** REFUTED as a mis-location of risk.
  The cure (`joulewise/night_gate.py:1043–1117`) is a pure `if plan.receipt_class == "REHEARSAL_STUB":` branch that *skips* two
  `probes.read_text` calls and writes `chain_sha256: None` + `chain_stub: "built_in_stub_by_design"` into C5. It has no
  dependence on launchd, on the filesystem, or on any environment fact. A live night adds essentially zero information about
  *this* branch beyond "the plan JSON parsed to receipt_class REHEARSAL_STUB". The real untested surface is elsewhere (below).
- **"A stub night exercises the stub branch, not the DIAGNOSTIC_NO_PACK branch, so a second stub verifies nothing new."**
  REFUTED on primary evidence. Probe 7 shows the 09-09 gate returned at the C5 chain read, so C1, C4 and the *tail* of C3 were
  never evaluated live. C3's `measured` holds only `agent_census_exit_code`/`agent_census_stdout` — no `hid_idle_raw`,
  `ac_power_raw`, `pmset_g_raw`, `load_average_raw`, `cpu_speed_limit`. 21i states this in words: "C1/C4 'not evaluated
  after refusal', C3 census clean but FAIL-marked by the refusal". `grep -rl "hid_idle_raw\|cpu_speed_limit" docs/` returns
  **nothing** — no artifact in the repo shows those predicates ever evaluating live. And those checks are
  **class-independent**: `night_gate.py:1300` runs the C1 registration read for `{"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}`
  identically. So a second stub night exercises the exact code a DIAGNOSTIC_NO_PACK night will run.
- **"Nothing is armed" / packet's custody claim.** Confirmed (probes 5, 6).
- **"P7 shows what the merged cure changed."** REFUTED at the margin: the excerpt is stale (O-1).

## Contract lens on D-175 / 99ey / NIGHT_HANDBACK

**D-175 (P1) — authority is CLASS-scoped, not instance-scoped.** The operative sentence is
"Arming a `REHEARSAL_STUB` requires the eight conditions in that synthesis: stage the plan outside the watchdog's
`*/night_plan.json` glob, validate with `install_night_agent.sh --render-only` from the pinned measurement checkout,
`os.replace` into the plan directory, agents installed from that checkout at t0's hour/minute, arm email with pins before the
move, no OTHER agent session alive, pin reachability preserved, exit by t0 − 25 min."
It says *arming a REHEARSAL_STUB*, not *arming the post-watchdog rehearsal*. The Trigger and Why paragraphs are written about
the one 09-09 night, but the Decision is a class rule with no count limit, and it expressly contemplates repetition:
"a plan the session authored under NIGHT_HANDBACK may be re-armed or removed by that procedure". It also pre-authorises the
root: "A `/private/tmp` detached checkout is a valid `REHEARSAL_STUB` root … and must never be reused by a real plan."
**Conclusion: D-175 authorises a second stub night under the same eight conditions; no new authority is needed.**
Note condition 4 constrains the *plist's* hour/minute (t0's), **not** the install wall-clock — so a morning-before install
(option (c)) does not breach D-175.

**99ey (P4) — does not reach this question.** Its verdict fences "no **pack-bound** night until Q1.2–Q1.3, seat 4, and a fresh
un-inventoried rehearsal clone …". Its subject matter is `TRANSACTION_PACK` / T0_REHEARSAL census semantics
(`_pack_rehearsal_roots`, `arm_readiness._authenticate_go_purpose`). A `REHEARSAL_STUB` in `/private/tmp` is neither pack-bound
nor a production clone. **One forward-looking hazard:** 99ey Q1.2(1) would require plan `measurement_root` to *equal the running
checkout*. If that rule lands unqualified before the second stub night, verify it does not newly refuse a `/private/tmp` stub
root (a stub *is* run from its measurement checkout, so it should pass — but this must be checked, not assumed).

**NIGHT_HANDBACK (P6) — the only text that directly governs, and it requires a CURE, not a re-run.**
"Accept only `night_refused_agent_present` as a receipt refusal; **cure any other cause before re-arming**; never re-arm the same
plan on the same signature twice." Textually, the obligation created by the 09-09 `night_probe_error` is *cure before
re-arming*, and it is discharged at `a52810c9`. There is **no contract clause requiring the cure to be demonstrated by a live
night.** So option (b) is textually defensible; a requirement for a second stub must rest on risk judgment, not on contract. The
same sentence does impose a hard condition on any second stub: it needs a **new plan_id and a new signature**.

## For / against, with the precise code paths

**FOR a second stub night (strongest form — stronger than the charge states it).** Not "the cured receipt path has never run
end-to-end"; rather: **three of the five gate rows have never been evaluated live under launchd at all**, and the cure is
exactly what moves the first live failure point past C5 into them. Concretely, a live stub night newly exercises:

1. `launchd` start of `com.joulewise.night` at t0 from the disposable checkout (already exercised 09-09; re-exercised).
2. `night_gate.evaluate_night` **C3 tail**, none of which ran on 09-09 — `HID_IDLE_ARGV`
   (`/usr/bin/defaults -currentHost read … idleTime`, must be exactly `0`, `night_gate.py:1136–1153`),
   `PMSET_BATT_ARGV` (`"AC Power"` present), `PMSET_GENERAL_ARGV` (`displaysleep` regex),
   `LOAD_AVG_ARGV` (`sysctl -n vm.loadavg`, `LOAD_MAX = 2.0`), `THERMAL_ARGV` (`pmset -g therm`, every
   `CPU_Speed_Limit` must be `100`) — real machine state at 02:5x, mocked in every unit test.
3. **C4** (`night_gate.py:1255+`): `sysctl -n kern.bootsessionuuid` parsed as a canonical UUID, plus the epoch/monotonic pair.
4. **C1** (`night_gate.py:1300–1320`): `probes.read_text(plan.registration_path)` and the SHA-256 match against
   `D166_REGISTRATION_SHA256`. **This is the same shape of defect that caused the 09-09 refusal** — a plan-supplied path read
   live from a disposable checkout — and it is the branch shared verbatim with `DIAGNOSTIC_NO_PACK`.
5. The receipt write (`run_night.py:1514`), the driver's new refusal-reason log line (`run_night.py:1518–1523`), the
   results-branch push (`run_night.py:561`), and the courier (`run_night.py:774` `run_courier`, lock/heartbeat/`courier.sent`,
   plus the watchdog's FENCED→HOLD_CENSUS→FENCED transition the courier provokes).

**AGAINST.** Two honest points remain. (i) The consequence-bearing difference between the classes is *control flow, not gate
code*: `run_night.py:1545` sets `rehearsal_effective = rehearsal or plan.receipt_class == "REHEARSAL_STUB"`, and line 1546 only
aborts on a refused gate when `not rehearsal_effective`. So a stub night **cannot** exercise "gate refuses → night stops"; the
real night's abort path stays untested. (ii) 44 §Q3 is explicit that "a green stub says nothing about" the capture-timeout
seam, and the stub chain is `/bin/zsh -c "sleep 2; echo REHEARSAL"` (`run_night.py:1572–1575`) — no `powermetrics`, no capture.
Net: a second stub buys items 2–4 above (real value, class-shared) and buys nothing on abort flow or capture.

**Cost side the packet omits:** AC `powermode 1` today (probe 8). Under 44 §Q3 that already bars a real measurement night until
Ed sets `powermode 0` or rules. So the second stub costs **no critical-path time** — it fits inside a window the real night
cannot use anyway.

## Over-statements

- **O-1 (packet, fact-level).** P7's index line, "`60-excerpt-cure-diffstat.txt` … what the merged cure changed". The excerpt
  reads "6 files changed, 229 insertions(+), 101 deletions(-)" and lists `tests/test_gen_state.py | 5 +-`. The merged change
  is **5 files, 225(+), 100(−)** and does **not** touch `tests/test_gen_state.py` (probes 2, 4). Stale pre-rebase diffstat.
- **O-2 (packet, omission).** Index line P2: "item 6 MET with a finding; items 1, 4, 5 open". **Item 3 is PARTIAL**
  ("the send is recorded …; inbox receipt is not verifiable from a headless session") — the kernel row P3 says so explicitly
  ("item 3 PARTIAL (send recorded, inbox unverified)"). The packet's own summary drops it.
- **O-3 (charge, mis-location).** "the cure changed the receipt path exercised only by a real launchd-started night". False as
  written: the changed code is a receipt-class branch inside `evaluate_night`, fully reachable in unit tests (and covered by
  `test_rehearsal_stub_does_not_read_missing_chain_or_sidecar`). What is unexercised live is C3-tail/C4/C1, which the cure did
  not change but did *unblock*. The distinction matters: it is why the answer is "yes, run it", but for a different reason.
- **O-4 (charge, vocabulary).** "receipt PASS/REHEARSAL_ONLY". `PASS` is a **row status**, never a receipt verdict. A fully
  green stub yields verdict **`REHEARSAL_ONLY`** — `tests/test_night_gate.py::test_a_fully_green_rehearsal_can_never_yield_go`
  asserts exactly `self.assertEqual("REHEARSAL_ONLY", receipt.verdict)` with all rows PASS except C2. Any ruling should state
  the criterion in those terms or it is unfalsifiable at harvest.
- **O-5 (charge, option (b) framing).** "item 6 is MET on the strength of the first night plus the defect-shaped tests" — the
  first night's gate aborted after two of five rows; "the strength of the first night" is weaker than the phrase implies.

## Recommended answers

**Q1 — (c): REQUIRED, and may be COMBINED with item 5.** Not on contract grounds (NIGHT_HANDBACK requires cure, not re-run —
so a ruling of (b) would not breach anything), but on the risk finding above: C1, C4 and C3's five machine predicates have
never evaluated live under launchd, and they are the code a `DIAGNOSTIC_NO_PACK` night runs verbatim. Making the *first real
measurement night* their first live execution converts any defect there into a burned window on a machine that must be quiet.
The stub costs one arm ceremony inside a period when `powermode 1` blocks the real night anyway. **Caveat on (c):** if an agent
session is alive at t0 the receipt refuses `night_refused_agent_present` — acceptable, and it would close item 5 (the dead-man
stand-down is logged before the night) but **not** the non-refused-receipt condition. So (c) must be ruled as "one night may
close both; an agent-present refusal closes item 5 only and the item-6 re-run repeats", never as "one night closes both by
assumption".

**Q2 — yes, D-175's eight conditions suffice; no new authority, but five conditions to name explicitly.**
(N1) New `plan_id` and new signature (NIGHT_HANDBACK: never re-arm the same plan on the same signature twice); the 09-09 plan
root and stub checkout are gone, so this is a fresh authoring, not a re-arm.
(N2) **Decisive:** a fresh `/private/tmp` detached checkout at a head containing `a52810c9`, with the plan pinning
`measurement_head` = that head and the two agents installed **from** it. Pinned to `ae8f074f` the night would re-run the
pre-cure gate and reproduce the defect — the night would be worthless.
(N3) Record `pmset -g custom` (`powermode` for the active source, plus `pmset -g batt` source) in the arm record, per 44 §Q3's
registration lane; note in the arm record that a green stub says nothing about the capture-timeout seam.
(N4) State the harvest criterion in advance in the arm email: `receipt.json` verdict `REHEARSAL_ONLY` with C1/C3/C4/C5 `PASS`
and C2 `NOT_APPLICABLE` (`no_pack_by_design`); `result.json` verdict `REHEARSAL_ONLY`, `chain_exit_code` 0.
(N5) Before arming, re-check that 99ey Q1.2's `measurement_root == running checkout` rule, if it has landed by then, does not
refuse a `/private/tmp` stub root.
Nothing in 99ey otherwise changes the conditions; it fences pack-bound nights only.

**Q3.**
*Item 1* — `docs/process_traces/2026-09-01-unattended/cold_start.json` exists with `durations_ms
[5450, 6300, 5007, 5303, 5250]`, `median_ms 5303`, while `scripts/run_night.py:51` sets `COURIER_DEADLINE_S = 300` (s), ~57× the
5.303 s median. The file's existence therefore does **not** close the item as worded ("COURIER_DEADLINE_S set from its
median"). Closing evidence = a written derivation in the record linking 300 s to the 5303 ms median (cold start + send +
`COURIER_BACKOFF_S` retries + margin) — a desk task, no night needed. If no such derivation exists, the honest close is to
amend the acceptance wording rather than claim it.
*Item 5* — closing evidence = the two night agents installed **before 07:00 on the calendar day preceding t0**, plus the
driver/watchdog log showing the intervening 07:00 dead-man firing standing down having written nothing but its log line, and
`launchctl list` showing the agents present across that firing. Yes: it can only be closed by a night whose install precedes
that 07:00 — 21i records the 09-09 night installed at 01:57 the same night, so the R-7 observable never arose. Nothing else
closes it; no bench test substitutes, since the observable is a launchd firing against installed agents.

**Q4** — see Over-statements: O-1 (stale diffstat) and O-2 (item 3 dropped) are packet defects; O-3, O-4, O-5 are charge
defects. O-4 in particular should be corrected in the ruling text.

## Verdict

**Packet flawed (correctable, not fatal): every checkable fact is true, but P7's diffstat is stale (6 files/229 vs the merged
5 files/225, `test_gen_state.py` not touched), P2's summary drops item 3's PARTIAL status, and — the substantive defect — the
packet and charge locate the residual risk in the cured receipt path when the primary evidence (`night-receipt.json`: C1/C4
unevaluated, C3 census-only) shows it lives in the never-live-executed C3-tail/C4/C1 rows that `DIAGNOSTIC_NO_PACK` shares
verbatim. Recommended ruling: (c), REQUIRED and combinable, under D-175's existing eight conditions plus N1–N5.**
