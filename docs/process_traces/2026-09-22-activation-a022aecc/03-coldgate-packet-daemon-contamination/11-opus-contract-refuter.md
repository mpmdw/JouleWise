# Record 11 — Opus contract-lens refuter, cold-gate packet QPE01-DAEMON-CONTAMINATION-01 (2026-09-23)

Lens: does each proposed rule fit the byte-pinned registration, `night_gate`'s codes and receipt schema,
`quiet_admission`'s observation schema, the campaign summary contract, NIGHT_HANDBACK's refusal tables
and D-181/D-182/D-161 **without silently amending any of them**? Read-only; this is the only write.

## Disclosure (auto-loaded files)

Not a clean fresh-eyes seat, and it must be said. Auto-loaded before any instruction of mine:
`~/.claude/CLAUDE.md`, `JouleWise/CLAUDE.md`, `JouleWise/CLAUDE.local.md` (orchestration doctrine incl.
rule 11), the memory index `…/memory/MEMORY.md` (≈70 checkpoint one-liners, several naming this night),
and a git-status block with the last five commit subjects. No further loop context was sought (no RUN_STATE.md,
TASK_QUEUE.md, council log, memory body, or trace outside the packet directory and what exhibit B
cites). Read: `00-PACKET.md`, exhibits A/B/C + generators, two greps of `../01-…harvest-record.md`
for the census count; plus `git show 91f80870:<path>` and `python3` over the two archives. No sudo/powermetrics/launchctl; no test run; `/usr/bin/log` not invoked.

## Verification ledger

| # | Claim | Expected | Observed | Method |
|---|---|---|---|---|
|1|packet + 5 exhibits + charter|manifest / charter pin|all identical (packet `7083c815…`, charter `099de884…`)|`shasum -a 256`|
|2|registration digest = gate constant|`2c539240…79f1`|identical; `RULED_REGISTRATIONS` `binds_chain: True`|`night_gate.py:61,78-92`|
|3|sizing (six pairs) and C7(ii)|144.279111 / 254.234208 / 517081; 20.19 / 39.15 / 12,264|both reproduced exactly|`stdev` × √(df/χ²₀.₁₀)|
|4|0.31 W/core; 0.05→7 J, 0.10→15 J; logs ≈40/h|—|0.31944 W; 7.67/15.33 J; 42.2/h (806/19.1 h), hourly 36–47|(306.2873−152.9535)/480; C6|
|5|**"v2 skips the legacy load predicate"**|as packet states|**FALSE** — v2 enforces it at 2.0|`night_gate.py:1262,1575`; `run_night.py:3060`; receipt C3 detail (`:1390-1391`); B3b|
|6|journal marks the observer set|non-empty `observer: true`|**0 rows** with `observer: true` in 245 (tonight) and 238 (prior)|json scan of both `evidence_busy_cores.jsonl`|
|7|`powermetrics` is an observer|yes|**`observer: false` in all 234/229 rows**; per-envelope median 0.093–0.106 tonight, **0.111–0.115 prior**|scan + monotonic join|
|8|"prior night's top non-observer ≤0.06 cores mean"|as packet states|**FALSE** — `powermetrics` mean 0.1118, max 0.1338 (its own C4)|C4 + scan|
|9|prior night's registered stop outcome|not stated in packet|**`no cutoff qualifies`**, cause `observer_floor_above_smallest_holdable_share`|prior `summary.json`|
|10|observer floor vs 0.05|—|tonight 0.052823, prior **0.053098**|both summaries|
|11|mediaanalysisd range, envelope 1|label says 1.4–1.8|**0.9416–1.7894** over 11 rows|C3 t+243…t+547|
|12|census "268 of 268"; 30 s t0 fits|C5; —|C5 says 267 (268 only in harvest record §9); 12×620+600 = 8040 s < `window_max_s` 9000|C5; A5|

## Q1 — standing of the 20260922-2100 outcome

**Dissent in part from (c) — not on the label, on its reason.** (c) argues that binding the stop branch
"would turn a daemon bug into the paper's conclusion". True of one of the two registered causes.
`sized_pairs_above_24` is daemon-driven; `observer_floor_above_smallest_holdable_share` is not — it
compares the night's own machinery (0.052823 cores) against `smallest_holdable_share` 0.05, and it
**already fired on the 02:17 night** (no `fseventsd`, no `mediaanalysisd`, busy median 0.24) at
0.053098 (ledger 9–10). "No cutoff qualifies" has now been produced twice, once on a machine the packet
itself calls clean. A ruling adopting (c) on the packet's reasoning reads later as setting aside both
causes; it must set aside the sized-pairs cause as contaminated and say the observer-floor cause stands.

Worse for Q3's "re-run once": the floor is structural and **understated**. The registration's observer
accounting (A5 summary line 74, "self plus reaped children including recorder") measures ≈31.6 CPU-s per
600 s envelope = 0.0527 cores and excludes `powermetrics`, the collector's own sampler, at 0.094 cores —
real self-cost ≈0.147 cores, ≈3× the share block two must hold, and no machine-state predicate touches
it. Concur with rejecting (a) (a covariate rule is not a machine rule) and (b) (VOID mislabels correct
measurements of the wrong machine).

**Label text:** the measured `mediaanalysisd` range is **0.94–1.79 busy cores over eleven consecutive
30 s samples (≈5 min)**, not "1.4–1.8" (ledger 11). The stop-branch sentence must not be quoted
alone: alone it asserts a conclusion whose two causes have different standing.

## Q2 — the machine-state predicate

**Dissent from (a) as drafted: unimplementable and self-terminating.**

1. **The observer set it depends on does not exist.** `record_covariates` (A3a:853) calls
`sample_interval(protocol["sample_interval_s"])` with **no** `observer_pid`, so it defaults to the
recorder's own pid (`quiet_admission.py:240`), and the chain, collector and `powermetrics` — a separate
tree under `chain.zsh` — are non-observers. **Not one row in either night carries `observer: true`**
(ledger 6): the split the rule reads is empty.

2. **So ENV_SHARE 0.10 excludes clean nights.** `powermetrics` is non-observer at a per-envelope median
of **0.111–0.115 in all twelve envelopes of the 02:17 night**, and 0.1064 in tonight's envelope 1
(ledger 7). The rule excludes **twelve of twelve** envelopes of the clean night naming `powermetrics`;
with the two-consecutive abort it kills every future pilot at envelope 2. Regression (1)'s expected
"02:17 → zero exclusions" **fails at `91f80870`**: the packet's own acceptance criterion refutes the
rule. "The previous night's top non-observer consumer never exceeded 0.06 cores mean (C4)" is
contradicted by C4 itself (ledger 8). Any (a)-shaped ruling must first repair the observer marking
(pass the chain/collector pgid or an observer-command allowlist into `sample_interval`; re-mark
archived rows only as a labelled diagnostic), then choose a bar.

3. **The "zero-capture-class stop" silently amends D-182.** Ed's ratified terms (B1b): zero capture
means "no reservation opened a ledger session, no capture writer ran and the plan's
`runs/instrument_validation` directory is empty; the successor route requires positive evidence of all
three". After two captured-and-excluded envelopes all three are false. A cold gate cannot extend an Ed
decision: either the abort ends the night with no successor licence, or the extension goes to Ed. (The
abort itself is fine and has precedent — but `start_drift_abort` fires on the **first** offender,
`start_drift_abort_s: 2`, A5:61, fires on the first offender, `campaign:1262`; "two" is unexplained.)

4. **The journal is declared non-evidential by the code that writes it.** Every row carries
`role="covariate_only"`, `admits_nothing=True`, `evidence_status="PROVISIONAL"` (A3a:857); exclusion
weight contradicts that unless the recorder is amended too. No behaviour is stated for the 2 rows
without metrics, the 9 rows outside every envelope window, or the 19-vs-20 row counts (C3); a median
over a variable, partly-missing sample needs a fail-closed rule.

5. **A coverage hole (b) does not have.** `interval_metrics` returns only the **top ten** consumers
(A2c:162) and puts every process without a measurable interval delta into `unaccounted` with no
`busy_cores` (`:147-150`) — which is why the schema keeps `busy_cores = max(process_busy, host_busy)`
(`:160`). A load spread over many short-lived children (a Spotlight re-index) is invisible to a
per-process median and fully visible to the total; (a) alone does not generalise.

6. **The packet misstates which predicate governs the path it amends (ledger 5).** For v2,
`evaluate_night` → `_check_machine(..., legacy_load=True)`: the load average **is** an enforced t0
refusal at `LOAD_MAX = 2.0`, proved by the receipt's own C3 detail string and by B3b in words ("One-shot
load refusal for v2"); `legacy_load=False` is only the TRANSACTION_PACK hard re-check (`:1530`), where
CPU admission belongs to the driver. So **(c) is not "restore"** but "re-size a bar already in force",
and the missed option is **(c′): lower `LOAD_MAX`** — no registration change, no covariate promotion, no
observer repair, already carrying `night_refused_not_quiet` (inside D-182's list) at both the arm check
and t0. Tonight's 1.03 refuses at any bar ≤1.0; 09-15's 2.55 already refused. The packet rejects (b)
because a guessed total bar pre-empts the pilot, then guesses **two** per-process bars on no more
evidence — and the pilot sizes an *admission* cutoff for block two's measurement, not a refusal-to-start
bar, so the circularity objection does not separate them.

7. **Ordering defect.** `_check_machine` runs **before** `_check_registration` (`:1575-1580`), so a
T0_SHARE read from the v3 registration comes from a file whose digest is not yet verified. Put the bar
beside `LOAD_MAX` as a code constant (pinned via the `RULED_REGISTRATIONS` record list), or move the
registration check first — itself a probe-order change, and that order is explicitly "fixed and
reviewable" (`:1287`).

8. **Checked, non-blocking:** a 30 s t0 observation fits the schedule (ledger 12); a failed observation
must map to `night_refused_not_quiet`, not `night_probe_error`, which is **not** in D-182's list.

Concurs: (d) cannot be the gate (the daemon started at 04:49 unattended); a new exclusion reason needs
registration v3 (`exclusions` is byte-pinned, A5:19-30); the `mediaanalysisd` class needs nothing beyond
a working per-envelope rule once (1)–(2) are fixed.

## Q3 — retroactive re-analysis and the pilot count

**Concur with (a)'s principle; dissent from its expectation and from "re-run ONCE".** "Expected: all
twelve excluded" is right for tonight only by accident: as drafted the rule excludes the clean night too
(ledger 7), so the diagnostic proves nothing until the observer set is fixed. Rejecting (c) because "no clean pilot has produced that conclusion" is wrong on the record — the
02:17 night produced exactly that registered outcome through the observer-floor cause (ledger 9). Order the
re-run only with a ruling on the observer floor — cut the night's own CPU below 0.05 cores, re-fix
`smallest_holdable_share`, or pre-register that cause as a finding about the instrument rather than a
conclusion about idle variance.

## Regressions

- (1) **Dissent.** Its second half fails at `91f80870` (Q2(2)): as an acceptance criterion it is the
rule's refutation. Keep it — run it before any bar is ruled.
- (2) **Dissent.** "the same consumer marked `observer: true` → admitted" cannot be exercised against
production: no production path sets that flag (ledger 6), so a fixture proves only that the fixture
works. Add the real counterfactual: the live chain's `powermetrics` must classify as observer.
- (3) **Concur on shape, dissent on the class:** add "and the abort's terminal record does **not** claim
the D-182 zero-capture class" (Q2(3)).
- (4) **Concur.** `RULED_REGISTRATIONS` already carries v1 with `superseded_by: v2`, read at
`night_gate.py:1465`; v3 repeats the pattern.
- (5) **Concur**, with Q2(4)'s missing-row rule explicit.
- **Missing:** that the t0 refusal keeps `night_refused_not_quiet`, and that a churning multi-process
load is caught — today it is not.

## Findings

**BLOCKER** — B1 ENV_SHARE 0.10 excludes all twelve envelopes of the *clean* 02:17 night for
`powermetrics`, and the observer split it reads is empty in every row ever recorded (Q2(1)-(2)).
B2 `observer_floor_above_smallest_holdable_share` is daemon-independent and already fired on the clean
night, 0.053098 > 0.05, so a v3 re-run reproduces the stop outcome (Q1, Q3). B3 the "zero-capture-class
stop" contradicts D-182's ratified definition (Q2(3)).

**MATERIAL** — M1 "for v2 the legacy load predicate is not applied" is false (ledger 5). M2 missed
option (c′); no clean-night load average is supplied, so no bar is evidence-sized.
M3 exclusion weight on a journal whose rows declare `admits_nothing: true`; missing rows unhandled.
M4 per-process medians cannot see `unaccounted` or past the top ten. M5 bar in the registration vs
`_check_machine` before `_check_registration`. M6 label range misstated (0.94–1.79). M7 "0.05 cores
≈ 7 J" is a lower bound (envelope 1 implies ≈0.48 W/core, not 0.31).

**NIT** — N1 "268 of 268" censuses is outside the packet's evidence (C5 says 267). N2 "two consecutive" is
unexplained beside `start_drift_abort_s`, which fires on the first offender.

## Verdict

The packet is mechanically assembled, its digests check, and every arithmetic claim I recomputed
(sizing, `s_upper`, 517,081, the C7 counterfactual, 0.31 W, 7/15 J, ≈42 log lines per hour) is correct,
and the physical diagnosis — a runaway `fseventsd` at one core all span plus `mediaanalysisd` in
envelope 1, ≈150 J and ≈343 J of interior energy against a ≈5 J claim bar — is sound and well evidenced.
The contract layer does not hold. Q2's disposition (a) rests on an observer/non-observer split that is
empty in every row the system has ever written, and against the packet's own clean-night control it
excludes twelve of twelve envelopes for the night's own power sampler: as drafted it ends the campaign
rather than protects it. Its abort clause claims a D-182 class D-182's ratified text excludes, and its
account of which predicate governs the v2 t0 path is contradicted by the receipt in exhibit C and the
refusal table in exhibit B. Q1 and Q3 are argued as though contamination explains the whole stop
outcome, when one of the two causes is the instrument's own cost and has already fired on a clean night.
I would rule (c) on Q1 with a corrected reason and label; defer Q2 pending a repaired observer set and a
clean-night load/busy distribution to size any bar against, with (c′) as the low-surgery interim; and
rule Q3(a) only bundled with a ruling on the observer floor, without which the re-run has a foregone
conclusion.
