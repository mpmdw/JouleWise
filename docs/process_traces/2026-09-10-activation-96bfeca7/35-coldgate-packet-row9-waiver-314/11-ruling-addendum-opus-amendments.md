# 11 — Dated addendum to cold-gate ruling 10 (packet 35): Opus pairing amendments A1–A4 + W9, recorded 2026-09-10 ~07:50 PDT

Opus contract-lens refuter (report `12-opus-pairing-refuter-on-ruling-35.md`): **UPHOLD WITH AMENDMENTS.** Disposition (a), merge PR #314 at
`beb808bc` under the named waiver, stands. The resident magistrate records the amendments verbatim below and applies them to the PR ledger
and terminal review 36 before the merge; it overrules nothing. The refuter added a fourth reproduction: the test fails alone at the PR head
`beb808bc` itself (07:41:56–07:42:32 PDT, 36.297 s, line 1675, the same two strict reasons).

**A1 (independence clause; replaces the "ONE file" sentence).** Independence from this PR, shown by reachability: the failing test executes
`tests/test_controller.py`, `joulewise/adapters/powermetrics.py`, `joulewise/uncertainty_evidence.py`, `joulewise/cli.py`, `joulewise/reduce.py`,
`joulewise/controller.py` and `joulewise/environment_admission.py`; of these the PR changes TWO — `joulewise/controller.py` (+9/−2) and
`joulewise/environment_admission.py` (+5/−3) — and neither can bear on the failing assertion. (i) The three `controller.py` hunks all sit inside
`cooldown_gate` (def `:2464`; hunks `:2516`, `:2523`, `:2552`), which has two call sites, `controller.py:3072` (between-member campaign cooldown)
and `scripts/run_campaign.py:4174` (imported `:4149`, thermal-recovery note); the failing test is a single-run `HappyPathTests` case that drives
neither — it configures no cooldown, never imports `run_campaign`, and `grep -c cooldown_gate tests/test_controller.py` = 0. (ii) The
`environment_admission.py` change IS executed (strict validation reaches `current_environment_refusals` via `reduce.py:711`) but is a monotone
widening of one tolerance, 1e-9 → `ADMISSION_TIME_ROUNDING_S` = 1e-6, at three comparisons that can only ever WITHDRAW the reason
`environment_admission_missing`; it cannot emit either `idle_drift` reason, and seat 08 reproduced the failure with `environment_admission.py`,
`controller.py`, `load_transition_alignment.py` and `reduce.py` restored to base bytes (`git diff --stat ee25c47f..078a13a4 -- joulewise scripts
tests` is empty, so those base bytes are main's). The capture, salvage and strict-validation code that emits the two reasons (`powermetrics.py`,
`uncertainty_evidence.py`, `cli.py:1408/1416`, `reduce.py`) is byte-identical to main.

**A2 (reproductions; replaces W4's clause).** Pre-existing on the merge base in the same machine state: fails on clean main `078a13a4` (lead,
05:05 PDT, 73 tests, failures=1 — tail pasted below from the lead's tool transcript, not previously on the record), with
`environment_admission.py`, `controller.py`, `load_transition_alignment.py` and `reduce.py` restored to base bytes (seat 08 F2), on `58d4696b`
whose `joulewise/` tree is byte-identical to `beb808bc` (cold judge 35, 07:33 PDT, 36.840 s), and at head `beb808bc` itself (Opus refuter,
07:41:56–07:42:32 PDT, 36.297 s, same line 1675, same two reasons, unittest FAILED); all alone in-process, machine census not recorded.

Lead's 05:05 PDT run on the clean main worktree `/Users/edr/code/JouleWise-wt-bk-96bfeca7` at `078a13a4` (`python3 -m unittest tests.test_controller`),
verbatim tail from the session transcript:

```text
First list contains 2 additional elements.
First extra element 0:
'strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation'

+ []
- ['strict: uncertainty evidence: idle_drift does not match pre/post raw '
-  'sentinel derivation',
-  'strict: uncertainty evidence: idle_drift_bound_w does not match effective '
-  'drift derivation']

----------------------------------------------------------------------
Ran 73 tests in 90.454s

FAILED (failures=1)
CLEAN_MAIN_CONTROLLER_RC=1
```

**A3 (W7 re-shaped).** Addendum obligation, written into the row at merge time: when FIXTURE-SENTINEL-CONTROLLER-01 lands, the magistrate runs
`python3 -m unittest tests.test_controller` alone on then-current main and records the tail; if it is not `OK`, the failure is an open defect on
main with its own lane, the merge stands, and the record says so. The next PR whose replay shows this test name does NOT inherit this
disposition — it is a fresh mandatory cold-gate trigger under 44 C4 — and this ruling RECOMMENDS that the next cold gate refuse a further
waiver absent the cure. A standing bar on future waivers is a process rule, is NOT ruled here, and may be adopted only on the record and
visibly to Ed.

**A4 (new condition W9; filled here).** Machine state during the replay window 05:52:48–07:31:40 PDT, as known to the resident magistrate:
AC power attached (battery ~80 %, not charging), `pmset -g custom` powermode 0 on both profiles, system sleep 0; no interactive `claude`/T3
session live (both were terminated at 04:09 PDT); concurrent agent load present throughout: this headless magistrate (pid 51696), two to three
`codex` Astra seats (read-only refuters and the kernel bookkeeping seat), one Opus subagent, one detached `claude -p` cold judge (07:04–07:09
and 07:33–07:37), and the `com.joulewise.night.deadman` firing at 07:00:02. No formal census command was run for the window; this is the
magistrate's own account.

**Terminal-review row-9 line (amended).** … a pre-existing sleeping-fixture timeout that fails identically on main 078a13a4 on this host and is
unaffected by both production changes the PR makes on its path — the three `controller.py` hunks sit inside `cooldown_gate`, which the test never
reaches, and the `environment_admission.py` tolerance widening can only withdraw an admission refusal, never emit an `idle_drift` reason …

Nits carried without change: R8 (the four-shard prediction is reasoning, not fact; the measured fact is that the test fails alone in ~36 s at
two heads); R10 ("on a slow host", not "loaded"); W6 read as scoped to full-suite replays.
