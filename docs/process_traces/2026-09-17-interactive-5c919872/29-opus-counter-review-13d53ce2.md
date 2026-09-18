# Opus counter-review (gate ledger row 6) — NIGHT-GATE-QUIET-ADMISSION-01 at head 13d53ce2

Reviewer: Opus 5, fresh eyes, design-level and cross-unit lens. Read-only via
`git show 13d53ce2:<path>` and `git diff a90ab4e8 13d53ce2` from the canonical
root; nothing in `/Users/edr/code/JouleWise-wt-gate-quiet` was touched, no tests
run, nothing armed. Against: seat brief D1–D7 (record 01), ruling 70 synthesis
(record 70/13, seven corrections), ruling 71 §1 bar and synthesis 71/13,
round-4 audit (27) and triage (28), D-182, and kernel row
NIGHT-GATE-QUIET-ADMISSION-01.

**Verdict: no BLOCKER. Two SHOULD-FIX, three NIT.** The assembled mechanism does
what ruling 70 affirmed, the units agree on every name, code and number I
checked, and no candidate cutoff exists anywhere in production code, generated
plans, fixtures or docs.

## Findings

### S1 (SHOULD-FIX) — the worker request is the one uncapped payload crossing a process boundary

`scripts/run_night.py:2311-2313` builds the static/hard/census worker argv with
`--request <json.dumps(request)>`, and `:2547-2548` puts the whole static
receipt into that request (`'static': json.loads(static.to_json_bytes())`). Held
against the design's own premise, stated in the contract doc at
`docs/contracts/night_quiet_admission.md:190-197` and enforced everywhere else:
the result frame is capped at 256 KiB (`_BIND_MAX_PAYLOAD`, `:1997`, checked at
`:2152` and `:2275`), reads are capped at 64 KiB and four calls per tick
(`:2135-2139`), jobs at 32 (`:2355`). The request has no cap and no assertion.
Evidence of the consequence: an argv over `ARG_MAX` raises `OSError` inside
`_BindLauncher._run` (`:2072-2073`) → `task.launch_error` → `_error` → `result()`
raises `ProbeError` (`:2180`) → outer `except` → `stop(night_probe_error)`
(`:2557-2558`). Fail-closed, so no night is admitted this way — but it burns the
night, and `night_probe_error` is *not* in `zero_capture_successor_allowed`'s
eligible set (`joulewise/arm_retry.py:210-211`), so D-182 grants no successor for
it. In practice the static receipt is a few KB, so this is bounded, not live.
Cure is one line: bound the serialized request by
`_BIND_MAX_PAYLOAD` in `start()`/`_bind_argv` with its own named refusal, or pass
the static receipt over the existing pipe rather than argv.

### S2 (SHOULD-FIX, doc/operational) — `samples_total` and the journal replay

`_BindJournal._run` (`:2241-2246`) opens `quiet_samples.jsonl` with `'ab+'`,
replays existing bytes and *seeds* `digest`/`lines` from them, and the receipt
reports that seeded count as `samples_total` (`:2565-2570`). The contract doc
(`night_quiet_admission.md:241-253`) describes `samples_total` as this night's
attempted intervals, with no mention of a replayed prefix. The two agree today
only because `_QUIET_WRITE_ONCE_RECORDS` (`:128`) adds `quiet_samples.jsonl` to
the rerun guard, so a second driver fire refuses at `:2723` before binding. That
coupling is load-bearing and undocumented: relax the rerun guard and
`samples_total` silently counts a previous fire's samples while
`samples_quiet_run_at_go` counts only this one. Cure: name the rerun guard in the
contract doc, or seed the receipt count from `attempted` instead.

### N1 (NIT, physics, input for lane 232) — the interval denominator overstates by one `ps` duration

`joulewise/quiet_admission.py:253-257` takes `ps_start` *after* `ps_before`
completes and `ps_end` *after* `ps_after` completes, then divides the per-process
counter deltas by `ps_end - ps_start` (`:264-266`). The true separation between a
given process's two counter reads is shorter than that by roughly one `ps` run
duration, so `process_busy_cores` is understated by about d/interval (d ≈ 0.05–
0.2 s on a loaded machine; ≈0.2–0.7 % at a 30 s interval). Understating is the
unsafe direction. It is far below anything the instrument can resolve, so it
changes nothing at merge; it matters only as a caveat for
QUIET-PREDICATE-EVIDENCE-01, which must not assume sub-1 % exactness from this
predicate when deriving a cutoff. Related and benign: `host_busy_cores` comes
from `top`'s own (shorter) window while `process_busy_cores` covers the bracketing
window; `busy_cores = max(...)` (`:160`) keeps the combination conservative.

### N2 (NIT) — a second, undocumented v4 authoring path

`joulewise/night_plan_writer.py:71-76` replaces `os.replace` with `os.link` for
v4 plans so publication can never overwrite sealed bytes (correct and stronger;
the temporary is cleaned in the `finally` at `:82`). The contract doc's authoring
section (`night_quiet_admission.md:295-303`) documents only the generator route,
which uses its own exclusive `open("xb")` (`scripts/gen_derivation_night.py:938-
941`). Two authoring paths with the same semantics, one described. One sentence
fixes it.

### N3 (NIT) — the one v4 guard that is an exception rather than a receipt

`joulewise/night_gate.py` `evaluate_night` raises
`PlanError("night_probe_error", "v4 requires supervised interval admission…")`
for a v4 plan instead of returning a REFUSED receipt. Nothing reaches it in
production (the driver dispatches at `run_night.py:2799` before any legacy call),
and ruling 71 Q4's code-enforced fail-closed refusal binds only a split PR-1
head, which this is not. Recorded so a later split does not inherit it as
satisfied.

### N4 (NIT, pre-existing, not introduced here) — an early fire is still terminal

The missed-fire guard (`night_gate.py:1001-1011`) refuses when `now < t0`, and it
runs once, at the start of binding. A driver that fires even a second before t0
therefore refuses the whole night with `night_window_expired`, which is outside
D-182's eligible set — so no successor either. The bind window now makes "wait
until t0" natural and it was not taken. The launcher historically lands after t0
(09-17: 15:30:01), so this is an observation, not a live defect.

## What I checked and found clean

**Ruling 70 in force, item by item.** Q1: first sample at t0, wait is plan data,
and `admission_is_capture_evidence: false` is a required receipt literal
(`_QUIET_RECEIPT_KEYS`, validator `night_gate.py:1487-1488`, emitted at
`run_night.py:2567`) with the reason stated at `night_quiet_admission.md:259-260`.
Q2: `consecutive_quiet_samples` is plan data only. Q3: the load probe is skipped
entirely in the v4 path (`_check_machine(..., legacy_load=False)`), survives only
as `load_avg_diagnostic` on every sample and receipt. Q4: **no candidate cutoff
anywhere** — a whole-tree grep for `busy_core_max` outside `tests/` and historical
process traces returns only the contract doc's non-admitting `0.0` example, the
validator, `is_quiet`, and the runsheet's f-string; `is_quiet`
(`quiet_admission.py:170`) and the receipt validator (`night_gate.py:1537-1539`)
both refuse admission when the cutoff is zero, so the fixture value cannot
authorize a night. Q5/correction 7: `observer_cpu_s` brackets the whole round
with the census included (`_bind_cpu` at `:2006-2009`, `:2330`, `:2573`; doc
`:136-149`). Q6: a fresh strict census runs inside `evaluate_dynamic_hard` at
pre-, post- and final-check phases, plus an independent 30 s cadence worker; the
driver's initial census is only checked for a hit (`:2410-2416`) and never reused
as a pass, unlike the legacy path's deliberate reuse (`:2806-2812`). Q7:
`programmed_span_s` = 600 + 11×600 + 480 = 7680, +300 pre-settle = **7980**,
enforced in both `build_spec` (`:511-514`) and `author_quiet_plan` (`:928-930`).
Q8: v2 key set, bytes and one-shot semantics untouched; a v2 plan carrying
`quiet_admission` fails the exact-key check; `is_quiet` dispatch excludes packs.
Corrections 1–6: 480 s slot arithmetic throughout the contract doc; non-admitting
fixtures; required non-empty `cutoff_authority` with `TEST-ONLY-NOT-A-RULING`;
distinct `night_refused_bind_expired` registered in both registries with the
overlap assertion narrowed to exactly that code (`night_gate.py:103-104`) and in
`COLD_GATE_CODES`; D7 landed after #357.

**Cross-unit agreement.** Driver summary keys ↔ `_QUIET_RECEIPT_KEYS` plus the
conditional `attribution_unavailable` / `boot_identity_unavailable` /
`journal_failure` / `observer_cpu_s` / `supervision_residue`: exact match.
Residue `kind` values emitted by `start()` (static, hard, sample, census) ↔ the
validator's allowed set: exact; `smoke-hard` never produces a receipt. Schema ids
`joulewise.night_plan.v4` / `joulewise.unattended_night_receipt.v3` agree across
gate, writer, generator and both contract docs. `_BIND_SAMPLE_GRACE_S = 7*30+5 =
215` matches the doc's "seven tool timeouts plus five seconds" and the seven
tools the sampler actually runs (boot, ps, top, ps, logicalcpu, loadavg, census).
`CENSUS_INTERVAL_S = 30` unchanged. The doc's worked example is arithmetically
exact: deadline min(t0+600, E−9000) = 15:40; GO at t0+187 leaves 9413 = 9000+413;
t0+540 leaves 9060; dead-man 60·ceil((E+300+3600)/60) = 19:15; 5 W×480 s = 2400 J,
0.05→120 J, 0.01→24 J, 1 J→0.0004 core. `install_close_epoch` = t0 − `PLAN_LEAD_S`
(8 min, `magistrate_watchdog.py:86`) − 120 s = **t0 − 10 min**, and the plan-span
gloss corrected from 25 to eight minutes matches `plan_span_active` (`:778`) —
both stale-doc fixes are right, not just different.

**Deadlines.** Nothing derived from E changed: `_completion_epoch_s`,
`deadman_epoch`, `install_close_epoch`, `COURIER_DEADLINE_S`,
`WINDOW_SHUTDOWN_GRACE_S` are byte-identical. The bind deadline is converted once
from the driver's *entry* clocks (`run_night.py:2711` → `:2334-2335`), so thread
bootstrap and a late start consume the allowance; a wall-clock rollback cannot
extend it, and `go_epoch > deadline_epoch` refuses (`:2533-2534`). For v4 the
chain's shutdown instant is anchored on the same entry clocks (`:2952-2954`)
rather than recomputed at chain start — same wall instant, immune to a clock step
during binding, and not passed at all for v2.

**Journal and courier.** Samples go to `quiet_samples.jsonl`, censuses to
`censuses.jsonl` (`:2247-2259`), so the receipt's digest and line count describe
samples only; the journal is append-only, never truncated, and is listed in
`_artifact_list` (`:978`) so the courier ships it. No intermediate `refusal.json`
for a WAIT; `stop()` is a no-op once in cleanup.

**D-182 route.** Eligible codes, positive zero-capture evidence, courier.sent,
`successors_used == 0`, new id *and* new digest, fresh notice after the terminal
write, ≥60 s spacing, then ordinary `retry_allowed` with empty history — the code
(`arm_retry.py:196-270`) and both generated policy copies say the same thing, and
the doc is explicit that the desk caller must harvest `zero_capture_evidence`
because a bare receipt cannot supply it.

**Contract doc.** It passes the first-use test on my read: bind window, sample
interval, busy-core equivalent, consecutive quiet samples, terminal/WAIT/ERROR,
attribution, observer, cutoff authority, supervisor, EOF, exec, cleanup budget,
frame, local allowance are each built or glossed before use, and the mechanism is
rebuildable from §"Rebuilding one observation" plus the pseudocode block alone.

**Merge-ability.** `git diff main 13d53ce2` is empty for
`docs/process/state_kernel.json`, `tests/test_gen_state.py` and
`docs/decision_log.md` — those landed on main already (0a95ad53, PR #357), so the
19-file count against `a90ab4e8` overstates the merge delta and there is no
duplicate-registration hazard. Nothing in the diff exceeds the lane: the only
file outside the seat's WRITE_SCOPE that is a real delta is
`docs/contracts/pack_night_go_receipt.md` (+4 lines), which is the F1 exception
ruling 70 required. All eleven named regressions exist by name across the six
test modules. Against the kernel acceptance row, what remained open at my read is
the full-suite replay on this head and the twelve-row gate ledger — both the
magistrate's to close.

**Round-4 R1.** I concur with record 28: restoring the `launch_done` predicate at
`:2202` is an equivalent mutant, because the whole-cleanup budget measured from
expiry on `perf_counter` (`:2388`, `:2458`) already bounds the return path; the
mutant that carries the property ("budget only when jobs empty") is killed. If
anyone wants the ambiguity gone, deleting the redundant predicate changes no
behaviour.
