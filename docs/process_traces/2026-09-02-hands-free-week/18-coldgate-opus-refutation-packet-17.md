# Opus contract-lens refutation — cold gate 17 (plan-pin + watchdog)

**Contamination disclosure.** I am NOT cold: my context carries the project's
operating doctrine (`CLAUDE.local.md` rule 11) and session memory, so I knew the
magistrate's dispositions before reading. Charter §5 charge only — falsify
exhibits/objects; I am not the judge.

**Pins.** coldgate-17 HEAD `6936b190` ✓; planpin `90698150` ✓; watchdog
`953a1645` ✓. `shasum -a 256`: charter `099de884…c95d81` = expected; packet
`8be2c69e…76ec68` = expected. Validator `"result":"PASS"`,
`coldgate-validator-receipt/v2`, 17/17 exhibits observed==expected, manifest
`9eb2efa7…ead6f69`, `"judge_handoff_bound":false`.

**Verdicts.** Q1 FALSIFIED in part (matrix stands; "exactly the gate's
acceptance" false) · Q2 FALSIFIED (wrong revision pin; row 4 unpinned) · Q3
STANDS w/ MATERIAL · Q4 STANDS · Q5 FALSIFIED (two paths) · Q6 FALSIFIED (all
three) · Q7 FALSIFIED (standard moved to fit the object).

## Q1 (executed: temp git repo, scratch plans, `--render-only` to scratch)

Trailing newline in `measurement_head`, relative `measurement_root`, and a v1
plan each REJECT `night_plan_malformed` at `from_mapping` and rc=3 at the
installer; the valid plan ACCEPTs at rc=0. Those four stand as claimed. The
equality claim does not — two inputs the installer ACCEPTS that the gate REFUSES:

| plan | installer | `evaluate_night` (now in window) |
|---|---|---|
| `authored_epoch_s` = now−40 h | **rc=0** | REFUSED `night_plan_stale` |
| `authored_epoch_s` = now+2 h | **rc=0** | REFUSED `night_plan_malformed` |

`PLAN_MAX_AGE_S` and the future check live in `evaluate_night`
(`night_gate.py:605-618`), never in `from_mapping` — the installer's whole raw
validation (`install_night_agent.sh:45-66`). Fail-closed, so not a blocker, but
hands-free a future-dated plan installs silently and burns the window with nobody
watching. **MATERIAL.** Cure: both checks in the installer's Python block.

## Q2 — wrong revision, and row 4 is unpinned

Q2 pins the file "at `63d12162`" = **fix round 1**, an ancestor; blob `d447457c`
vs head `fc189670` (129+/21−). The 2026-09-04 amendments postdate it: the async
probe row 4 blesses (`_cached_remote_stop`) has 0 hits at `63d12162`, appearing
only at `fc21ab3b`. The named revision cannot implement the named amendments
(charter §7). **BLOCKER for answerability**; cure: re-pin to `953a1645`.

At the real head (`git archive 953a1645` → temp copy): **36 tests OK**;
`REQUEST_LEAD_S=25*60`, `TERM_LEAD_S=16*60`, `KILL_LEAD_S=15*60`,
`USAGE_BACKOFF_S=(900,1800,3600,7200,7200)`. Mutations `TERM_LEAD_S=17*60`,
ladder rung `7199`, glob narrowed to `ops/stop-magistrate*`, and notice-ack moved
after the child-exit return are each **KILLED**. But **`SUPERVISOR_POLL_S` 10→60
and 10→600 both SURVIVE, 36/36 OK.**

So the fix rounds genuinely cured S2/S3 and notice-ack ordering holds — yet **row
4's central guarantee, "RESIDENT supervisor with ≤10 s resolution (a 300 s tick
cannot hit a deadline)", has no biting regression.** No test names
`SUPERVISOR_POLL_S`; at 600 s the resident cannot hit the 60 s TERM→KILL gap —
precisely row 4's failure mode — and the suite stays green. Same
ruled-not-installed class the fix rounds were convened to close, on the one
constant carrying the guarantee. **MATERIAL, blocker-shaped for the clause map.**
Cure: assert literal `10` plus a deadline-hit test at a mutated poll.

My "unbounded stop staleness" attack **failed**: `remote_stop_probe` is
`timeout=10` per ref on a reuse-guarded daemon thread; staleness ≤300 s + ~20 s.

## Q3 — D-171 does not authorize t0−15 as written

D-171 item 7 verbatim: **"Stand-down margin = 5 minutes before a window's t0 (30
was 'too much')"**. The addendum installs request t0−25 / TERM t0−16 / KILL
t0−15. File 15 row 4 gives the physics rationale, **but the addendum text neither
cites item 7 nor records that it supersedes a ratified number** — a reader of
amended R-9 cannot see Ed's figure was overridden. **MATERIAL.** No unrecovered
irreversible step: install reverses via `--uninstall` (no sudo); the first
stand-down kills only that session, the watchdog being the recovery path.

## Q4 — STANDS

Merge → install → stand-down → arm satisfies row 7 / file 14 Q6; retired-v1
fail-closes. Load-bearing in the inverse direction: the installer enforces
`repo_head` == driver HEAD (**executed rc=3**), so plans authored before the merge
must be re-pinned after it. The proposed order respects this.

## Q5 — two violation paths

1. **The armed-night git fence misses the checkout that now matters.** The prompt
fences only `/Users/edr/code/JouleWise` (line 9), but under v2 staleness keys on
the **measurement** checkout — and D-171 item 5 and the R-7 addendum direct the
magistrate to fast-forward it. Fast-forwarding
`/Users/edr/JouleWise-measurement-20260813` while armed silently fires
`night_plan_stale` and loses the night. The landing relocated the hazard; the
prompt did not follow. **MATERIAL.**
2. **Nothing bars ratifying a process rule.** Its only guard — "do not merge,
install, deploy, or take irreversible action **without its normal authority and
gates**" — lets the session self-certify authority. **MATERIAL.**
3. NITs: the prompt omits R-9 clause 3 (arming obligates ending the loop; the
watchdog request covers it physically), and "Ed's NO always overrides" is inert
when Ed "reads, does not reply".

## Q6 — none installable as written; exact amended text

**R-6.** "the driver checkout's HEAD … **never refuses**" is true of the gate,
**false of the installer** (executed rc=3). Amend: *"…is recorded in the census
row; the gate never refuses on it, while the installer still requires it to match
at install time. The installer applies the plan-age and future-authorship checks
in addition to `from_mapping`."*

**R-7.** "**deliberately** before each arm" is a disposition, not a checkable
condition, and omits the fence. Amend: *"The magistrate fast-forwards the
measurement checkout before an arm and never while a plan is armed; a
fast-forward after arming requires a re-arm with a re-pinned plan."*

**R-9.** "cooperative exit remains the **preferred** path" — no mechanism prefers
it. Amend: *"…the cooperative exit is the only path that emails at stand-down,
and the supervisor signals only after the request deadline elapses; the resident
poll is 10 s. This supersedes D-171 item 7's 5-minute margin: the physics margin
is 15 minutes on the runbook's 10-minute idle plus the chain's 180 s settle, and
Ed's 'too much' is honoured for the 25-minute request."*

## Q7 — hygiene: the standard was moved to fit the object

**BLOCKER.** Two seats (17k F3, 17m R1) returned **NOT LANDABLE** on the glob and
stop cadence. The magistrate resolved both not by changing code but by **amending
file 15's adopted rulings, dated 2026-09-04 02:20, to match the built object** —
and Q2 then asks whether the code implements "the adopted rulings … including its
dated amendments". The object supplies its own conformance standard, and the
amendments arrive as adopted rather than proposed (contrast 17j, correctly "not
installed"), though charter §3 item 4 makes a proposed rule a convening trigger.
Neither call is wrong on the merits (the wider glob is strictly safer; the D-161
rationale is sound) — the defect is procedural. Cure: relabel both as proposed
addenda four and five, decide them here, re-pin Q2 to `953a1645`.

Also **Q1 and Q2 are compound** (intent *and* equality; conformance *and*
replay), so a split verdict cannot be recorded cleanly. No omitted contrary
evidence found: both NOT-LANDABLE verdicts and the disposition are quoted.

**Disagreement with the labeled disposition:** 17m's "the code is otherwise
LANDABLE per this delta's own execution table" is unsupported for row 4 — that
row's ≤10 s guarantee is unenforced by any test. I do not otherwise dispute
landability on the merits.
