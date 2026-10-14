# Block 6 collection design: draft for the owner

Reconciler: Opus 5.5, 2026-10-14. This draft combines two blind design seats, Sol 6.1 (`seat-sol.md`) and Opus 5.5
(`seat-opus.md`), both in this directory. Every number either seat gave was checked against its source; the
check is in section 10, and three numbers are corrected there. Nothing tracked was changed. No block-5 energy,
power, floor or outcome was opened; the only measured values read are durations, run counts, stage exit codes
and the calibration times of non-claim rehearsals.

## 0. Words used

- **Pack**: one of block 5's three measurement plans. ALPHA and BETA each measure the *detection floor* (the
  smallest energy difference the method can tell apart from noise) for one model (ALPHA the 1.7-billion-
  parameter model, BETA the 8-billion one). GAMMA measures two paired contrasts between the two models.
- **Run**: one model execution with its own idle baseline before it (code: member).
- **Unit**: what an estimator counts. Either a *repeat* (one run) or a *quad* (four runs in the order A, B, B, A,
  which cancels a slow drift of the machine).
- **Stratum**: all units of one kind in one phase (for example, the decode quads). The registered estimators
  need at least 5 units per stratum; block 5 plans 10.
- **Session**: one unattended collection of a whole pack (block-5 code: window). **Attempt**: one try at a
  session. **t0**: the moment the session's driver starts.
- **Calibration capture**: a short run of a known workload at the start (*opening*) and end (*closing*) of a
  session that measures how far the power sampler's clock can be from the model's clock. Its result is a time
  in milliseconds. The *alignment screen* compared it with 36.46 ms, the largest of 24 earlier good captures.
- **Calibration ledger**: the file that lists every capture ever taken. The **calibration acceptance** is the
  registered judgement, read from the ledger, that the capture method is still trustworthy.
- **Harvest**: the program that reads a finished session's raw records, applies the registered checks and
  writes the archive the analysis reads.
- **Claim-usable**: the harvest says the session may enter a published number.
- **Flag**: a condition written into the harvest record without discarding the session. The analysis plan says
  in advance which flags exclude a session from a claim, and the paper prints results with and without
  flagged sessions.
- **Physical hazard**: one of the six conditions the owner's doctrine (2026-10-05) lets stop collection:
  the clock stepping or drifting beyond budget, running on battery, thermal pressure, an outside process using
  power, too little free disk, the sampler not sampling. Everything else is a flag.
- **Blind dry run**: the analysis program running over the real archives before release, with no person or
  agent reading its numbers. **Independent recompute**: the same headline numbers computed again from raw
  power records by code that shares nothing with the analysis program (RUN_STATE item 37).
- **Rule-loss**: a session removed by a rule about records, not by a physical measurement.

## 1. The answer

1. Block 5 did not lose time to session length. BETA spent 42.5 h of wall time for one usable 5.9 h session:
   21.4 h of it in five lost attempts and 15.1 h in the gaps between them (consults, errata, new harvest pins).
   Three of the five losses were rule-losses; two of those (attempts 4 and 5) were certain before t0 from
   files already on disk (section 2).
2. Keep the session exactly block 5's shape: 125 runs for ALPHA and BETA, 107 for GAMMA, 10 units per stratum,
   a reference corpus of 18 runs. Halving it costs about 46% more machine time per unit of science, widens every
   interval 1.74 times and makes a lost unit fatal (section 4).
3. Three kinds of short check, each with a written pass rule, so nothing is read later as "rehearsal noise":
   a **pre-session check** (about 5 min, no model runs, before every session), a **smoke** (about 25 to 30 min of
   collection and about 30 min of desk programs, before every session), and a **fault rehearsal** (about 1.5 h
   per pack with deliberately injected faults, once per change of code or registration). Before registration,
   one full-length **round 0** of non-claim sessions, one per pack, runs through the real unattended loop.
4. Target 3 claim-usable block-6 sessions per pack (the owner's commitment is at least 2), collected in
   interleaved rounds ALPHA, BETA, GAMMA. One round takes about 23 h; three rounds about 2.9 days back to back
   with no loss, about 3.4 days at block 5's loss rate. Disk, not time, is the binding resource (section 5).
5. The loop between sessions is plain programs under launchd with no agent alive. A physical hazard waits and
   retries; anything else is a flag; a non-physical smoke failure holds only that pack's next session and
   wakes the orchestrator.
6. The critical path is the work before registration (section 7), not machine time.

## 2. What block 5 lost

BETA, from the window records (`seal2-beta-a*-window.md` on the records branch) and RUN_STATE items 16 to 28.
"Chain" is the driver's collection from t0 to exit; "gap" is from one chain's end to the next t0.

| Attempt | Chain (PDT) | Chain h | What removed it | Known before t0? | Gap to next |
|---|---|---|---|---|---|
| a1 | 10-10 00:42 to 06:45 | 6.05 | `neg8.screen_failed`: an end reference was lost at idle admission, its spare left no record, and the sealed verdict writer then wrote no source list, so the harvest could not repeat the reference screen. A record, not a measurement | No; a rehearsal that loses one reference would have shown it | 4.2 h |
| a2 | 10:56 to 13:28 | 2.53 | A `claude` session opened at the keyboard at 13:28:09 and closed 20 s later; the census (a 30 s scan for agent processes) stopped the chain on first sight | No | 1.4 h |
| a3 | 14:51 to 14:59 | 0.13 | Opening capture above the 36.46 ms screen; zero runs | Not that capture; but the same stop happened in rehearsal `gamma-1` on 10-06 (48.0 ms) | 0.6 h |
| a4 | 15:37 to 22:34 | 6.95 | Calibration acceptance stale since a3's capture (ledger sequence 456). The Mac also slept 3,507 s after a 26 s charger drop, which cost 4 runs and was not the removal reason (item 23) | **Yes**: sequence 456 was in the ledger at the arm | 2.1 h |
| a5 | 10-11 00:39 to 06:25 | 5.77 | The same staleness | **Yes** | 6.8 h |
| a6 | 13:16 to 19:11 | 5.92 | Usable | | |

Lost chain time: 6.05 + 2.53 + 0.13 + 6.95 + 5.77 = 21.4 h. Gaps: 4.2 + 1.4 + 0.6 + 2.1 + 6.8 = 15.1 h. Wall time
from a1's t0 to a6's end: 42.5 h. Under the doctrine now in force, a1, a3, a4 and a5 would each have been kept
with flags, and a2 would have lost one run to a pause instead of the session (section 6.3).

The other losses of the block:
- First-seal ALPHA a1 (t0 15:01 PDT on 10-08, 5.3 h): 19 runs excluded, 18 of them for an outside process
  inside the run (`mediaanalysisd`, `corespotlightd` and others; `alpha-a1-consult.md`), which left the corpus
  and one stratum below their minimums. First-seal ALPHA a3 (t0 23:44 PDT, 5.5 h): corpus runs lost to the
  midnight `/private/tmp` walk. Both seats' and the process inventory's attribution of a1 to midnight is wrong.
  The analysis agents are disabled from Ed's next login (item 35 (d)); he has not restarted yet.
- First-seal ALPHA a2: refused at arm on contention. Cost minutes; the check did its job.
- Rehearsals `corpus18-20261009T1816Z` and `...1944Z`: refused at arm after 60 s, sampler median interval 255.0
  and 253.9 ms against 150 ms (a wrong launch context). Cost 60 s each; the check did its job.

What the rehearsals already showed. Seven rehearsal captures read 30.6, 30.1, 29.3, 30.5, 32.8, 40.1 and 48.0 ms
(`b_fiducial_s` in the operator logs). Two of seven crossed 36.46 ms; `gamma-1`'s 48.0 ms stopped its chain on
10-06 while leaked test-fixture processes (`fake_powermetrics_process.py`) were alive. That is attempt 3's
failure, on disk four days earlier. The rehearsals had no written expected outcome, and they overrode the census
on every call (`driver_census_overridden` equals `driver_census` in all four), so they never exercised the path
that stopped a2. **Hence every check below has a written expected result, and none overrides a check.**

## 3. The short checks

### 3.1 The smoke: what runs

Same sealed code, same pack, same launch route as the real session (launchd job, census live, keep-awake job,
sampler in the production launch context). Built with the rehearsal rig's per-stage `keep` map, with no
overrides, and with one rig change: a stage whose `keep` is 0 is left out, not run empty (an empty stage still
costs 2.2 min in `corpus18-20261009T1949Z`).

| Step | ALPHA | BETA | GAMMA |
|---|---|---|---|
| Opening capture | yes | yes | yes |
| Start reference | 1 run | 1 | 1 |
| Decode science | 1 repeat | 1 | 1 run of each model |
| Prefill science | 1 repeat | 1 | 1 run of each model |
| End reference | 1 run | 1 | 1 |
| Closing capture | yes | yes | yes |
| Runs | 4 | 4 | 6 |

Not in the smoke: the corpus, the bound derivation, the midpoint reference, the quads. Their code does not
change between two sessions on the same code; the fault rehearsal and round 0 exercise them (3.4).

**Duration.** From the rehearsal of 10-09 and BETA attempt 6: driver start to first stage 3 to 5 min (BETA a6
5 min, GAMMA a1 3 min, BETA a3 3.8 min); a capture 3.6 to 4.4 min (eight measured); a run 2.25 to 2.5 min
including its idle baseline (rehearsal 20-run stage 47.1 min; BETA a6 20 runs in 50 to 56 min, item 29). A
one-run stage in the rehearsal took 2.15 min, so a stage adds no visible fixed cost beyond its runs.

- ALPHA or BETA: 5 + 2 x 4.2 + 4 x 2.5 = 5 + 8.4 + 10 = **23.4 min**
- GAMMA: 5 + 8.4 + 6 x 2.5 = **28.4 min**

Then the desk part, all plain programs, no agent:

1. Harvest into a non-claim archive. **About 20 min**: the rehearsal harvests took 20.1 min (13 runs) and 23.4 min
   (53 runs) when they evaluated the calibration bracket, and 2.3 min when the closing capture had failed and no
   bracket was evaluated. So about 18 min is a fixed cost of opening the historical captures. (The Opus seat
   budgeted 10 min, the Sol seat 50; both are corrected here.)
2. The block-6 acceptance function on that archive (section 3.2 defines it).
3. The analysis program's dry run on the smoke archive. Smoke data are non-claim and not blinded. With one unit
   per stratum every estimate is undefined (n below 5), so the expected result is an exact list of refusals.
   This catches a format mismatch between the harvest and the analysis program, the kind lane L9 met when the
   archives carried no reference slots.
4. The independent recompute on the same archive, compared run by run with the harvest's phase energies within
   a tolerance fixed in advance from rehearsal data.

Steps 2 to 4 are unmeasured; budget 10 min. **Smoke total: about 55 to 60 min**, of which 25 to 30 min is on the
measurement path. The arm notice's 30 min lead (Ed's chance to say NO) runs during the smoke and adds nothing.

**Pass rule** (written once per pack from its first clean smoke in round 0, then frozen):
- chain exit 0, and each stage's exit code equals the expected one;
- harvest exit 0, verdict `COLLECTED`, and the set of flag kinds equals the expected set, except for *chance
  physical flags* (a capture above 36.46 ms but below the stop line, an idle wait, a contention flag), which
  re-run the smoke once and hold the pack only if they recur;
- the acceptance function's verdict equals the expected one;
- the dry run's refusal list equals the expected list;
- every run agrees with the recompute within tolerance;
- physics during the smoke: sampler median interval at most 150 ms, no sleep, no clock step, no battery draw,
  thermal nominal;
- each stage within plus or minus 25% of its expected duration (a slowed model adds energy; note 8.2 item 1).

The smoke's captures go into a **copy** of the calibration ledger in the smoke's own folder, never the claim
ledger, so a smoke capture can never change a session's acceptance (BETA a4 and a5 were lost to one capture of
another session). The smoke sends no mail through an agent: the courier of block 5 is a `claude -p` session, and
it tripped the watchdog's agent census after BETA a1, BETA a5 and GAMMA a1. The smoke's result is a file.

### 3.2 What each check would have caught

| Loss | Smoke | Pre-session check | Fault rehearsal / round 0 | Cure that makes it not a loss |
|---|---|---|---|---|
| BETA a1, no source list after a lost reference | No: a clean smoke never loses a reference | No | **Yes**: inject a lost end reference | Remove the spare (it left no record in 2 of 2 live uses, item 15); a lost reference is a flag; the screen runs on the survivors |
| BETA a2, agent at the keyboard | No | Only at t0 (the agent came later) | Yes: inject a process named `claude` mid-chain | Pause between runs instead of stopping (6.3); the run in flight is excluded and flagged |
| BETA a3, opening capture over the screen | Partly: its own captures show the sampler's state today, but cannot predict the session's | No | Yes: a capture under one core of load drives the branch | The screen is a flag and the capture's value is carried into the timing bound (council T1); one stop line, sized by test 15 |
| BETA a4, sleep | Partly: proves the no-sleep assertion holds in the live launch context | Yes: assertion held, AC attached, battery not supplying | Yes: `pmset sleepnow` during one idle baseline | Driver-held no-sleep assertion; a per-run sleep reading (council S1) |
| BETA a4 and a5, stale acceptance | **Yes**, in about an hour instead of 6.5 h, twice | **Yes**: the same function on the live ledger | Yes | Acceptance reads the session's own captures; other sessions' captures are flags (Erratum 3 as the default) |
| First-seal ALPHA a1, outside processes in runs | Yes if they are running then | Yes: contention dwell; list of running analysis agents | Round 0 measures loss under waiting | Ed's restart (disables take effect); waiting admission |
| First-seal ALPHA a3, midnight walk | No (time of day) | Records which stage 00:00 falls in | Round 0 BETA crosses 12:53 and midnight | Waiting admission: a disturbance costs minutes, not runs |
| Wrong launch context (255 ms sampler) | Yes, in its first minute | Yes: the 60 s instrument check | | Already a physical refusal |
| Leaked fixture processes (`gamma-1`) | Yes | Yes: orphaned processes with parent pid 1 listed and killed | | Kill orphans before arming |
| Historical capture evicted to iCloud (item 34) | Yes: the harvest's bracket evaluation opens every capture | Yes: `-flags +dataless` check | | `brctl download` per file |

**What the smoke cannot catch**: random events inside six hours (the scan, the daily batch, a charger drop, a
person at the keyboard); anything that depends on full counts (the 18-run corpus, the drift screen over 3 + 1 + 3
references, 10-unit strata, a whole session's disk growth and harvest time); the session's own captures;
slow thermal effects; the release and claim path. Random events are handled by waiting and flags; count-dependent
paths by the fault rehearsal, round 0 and the pre-check's synthetic full session.

### 3.3 The pre-session check

Requirement 3 of the threshold note, section 9: anything the after-session check will test that can be computed
before t0 is computed then, by the same function. So the acceptance becomes one function, `A`, used by the
harvest, the smoke desk, the pre-check and the analysis. Its inputs are the session's evidence, the ledger, the
code identity, the plan and the registration. The pre-check calls it twice:

- **Nominal**: with the session's evidence replaced by a synthetic full session built from the plan (all runs
  succeed; captures at the median of the last 24 valid ones). If `A` refuses this, the session is certain to be
  excluded: **do not start**; wake the orchestrator to fix the cause. This is not a procedural gate: it prevents
  only a session the registered analysis would certainly exclude.
- **Margin**: the same with block 5's worst usable loss applied (8 of 125 runs, clustered in one stage, as the
  scan did to BETA a1). If `A` refuses this, start anyway and write "thin margin" in the notice.

Conditions that cannot be known before t0 (closing capture, sleep, clock steps in runs, actual losses) are
recorded as *pending*, not passed. Physical readings, measured directly:

| Check | How | On failure |
|---|---|---|
| Clock | CLOCK_REALTIME minus CLOCK_MONOTONIC_RAW over 60 s, against the rate budget for the longest admitted stream | wait 10 min, re-measure |
| Time-server offset (diagnostic) | `sntp` to two servers, nothing set | record only |
| Power | AC attached, battery current within 200 mA, `pmset` battery `sleep 0`, no-sleep assertion held | wait |
| Thermal | OS thermal level 0 | wait |
| Contention | 180 s clean; orphaned fixtures (parent pid 1) killed; analysis agents listed | wait |
| Agents | census empty; last keyboard event older than the settle | wait |
| Disk | free space at least the measured writes of the largest session plus 20 GiB (43 + 20 = 63 GiB), plus the smoke's | wake the orchestrator; never delete evidence automatically |
| Instrument | 300 frames, median interval at most 150 ms | relaunch once in the production context, then wake the orchestrator |
| Evicted captures | every ledger-referenced capture is local | `brctl download` per file, re-check |
| Model files | hash equals the sealed one | flag; wake the orchestrator |

Output `precheck.json`: `would_refuse` (physics; wait), `certain_exclusion` (do not start), `predicted_flags`
(recorded, sent in the notice). Run time about 5 min (item 26's acceptance helper takes about 2 min; the 60 s clock,
60 s sampler and 180 s contention readings overlap).

### 3.4 The fault rehearsal and round 0

**Fault rehearsal**, once per pack per change of code, plan or registration. A clean rehearsal would not have
found BETA a1, because the faulty branch ran only when a reference was lost, so each fault rehearsal injects the
faults block 5 met, each with its expected record:

| Injection | How | Expected record |
|---|---|---|
| Lost end reference | kill the reference's process after its idle baseline | flag; screen evaluated on survivors |
| Idle disturbance before a run | one busy core for 120 s inside the baseline | baseline slides, wait recorded, no run lost |
| Contention inside a run | one busy core for 20 s inside a run | run flagged and excluded at the registered level; session continues |
| Sleep | `pmset sleepnow` in one idle baseline | that run excluded by the sleep reading; session continues |
| Agent sighting | a process named `claude` for 30 s | pause between runs; run in flight excluded; resume after the settle |
| Capture over the screen | closing capture under one busy core | flag, value carried into the timing bound |

Plus desk replays with no machine time (Sol seat): an archive missing a record about a reference, a ledger with
another session's systematic capture, absent metadata, an interrupted harvest re-run on the same bytes.

Contents: opening capture, a corpus of 6 (the minimum the council adopted, so the bound runs at its smallest
count), references 3 + 1 + 3, one quad and one repeat per phase, closing capture: 6 + 7 + 2 x (4 + 1) = 23 runs.
Time: 5 + 8.4 + 23 x 2.5 + about 8 min of injected waits = 79 min, plus about 30 min of desk: **about 1.8 h per
pack**, 5.5 h for three.

**Round 0**: one full-length non-claim session per pack, run through the real unattended loop including the hand-
over to the next pack's pre-check and smoke. It checks what only full counts show (corpus 18, 10-unit strata,
the analysis program's success path including GAMMA's contrasts, full harvest time, disk growth per session) and
that the loop itself works. BETA's is placed to cross the 12:53 daily batch and its loss rate under waiting is
the council's test 9. Each pack's first round-0 smoke is frozen as its smoke expectation. About 23 h.

## 4. Session length and structure

### 4.1 Where a session's time goes (BETA attempt 6; item 29 and the window record)

| Part | Minutes | Kind |
|---|---|---|
| t0 to first stage | 5 | fixed |
| Opening capture | 6 | fixed |
| Reference corpus, 18 runs | 45 | fixed |
| Bound derivation | 12 | fixed |
| Start and end references, 3 + 3 | 14 | fixed |
| Midpoint reference | 4.5 | fixed |
| Closing capture | 4 | fixed |
| Science: 2 strata of 10 repeats | 53 | science |
| Science: 2 strata of 10 quads (80 runs) | 212 | science |
| **Chain** | **355.5** (record: 355) | |
| Harvest | 49 | fixed |
| Acceptance, dry run, recompute | 10 | fixed (unmeasured) |
| Pre-check, smoke, settle | 5 + 60 + 10 = 75 | fixed (proposed) |
| **Cycle** | **about 490** | |

Fixed cost per session: 90.5 min in the chain plus 134 at the desk, about 225 min, against 265 min of science.

### 4.2 Fewer long sessions against more short ones

For the same science as one block-5 session:

| Design | Runs of science per session | Machine time | Units per stratum | Interval width | Floor guard |
|---|---|---|---|---|---|
| Block-5 shape, one session | 100 | 90.5 + 265 + 134 = 489.5 min | 10 | 1.00 | 1.0 |
| Two half sessions | 50 each | 2 x (90.5 + 132.5 + 134) = 714 min, **+46%** | 5 | 2.776 / 2.262 x sqrt(10 / 5) = **1.74** | sqrt(9 / 4) = **1.5** |

(Interval width uses the registered half-width t(0.975, n - 1) x s / sqrt(n); the floor guard is the registered
g(n) = sqrt(9 / (n - 1)) below 10 units.) A half session's smaller harvest would save perhaps 13 min each, so
+40% at best.

At 5 planned units every stratum sits on its minimum and one lost unit makes it undefined. The probability that
all four strata of a floor session keep at least 5 units:

| Planned units | At 1 lost run in 37 (the note's measured rate) | At 28 lost in 732 (all block-5 sessions that ran whole) |
|---|---|---|
| 10 | 0.9996 | 0.998 |
| 8 | 0.988 | 0.963 |
| 5 | 0.254 | 0.142 |

These assume independent losses; block 5's were clustered, so they are illustrations, not reliabilities.

Short sessions win only on the risk of a session-stopping event per hour. In block 5's 38.0 h of second-seal
chain time (350 + 363 + 152 + 8 + 417 + 346 + 355 + 291 min) one event stopped a chain for a physical reason (the
keyboard agent), about 0.026 per hour; with the first seal's two chains, 1 in 48.8 h. A 5.92 h chain then
survives with probability exp(-0.026 x 5.92) = 0.86. The two designs break even only above 0.16 stops per hour,
one every 6.3 h (Opus seat's arithmetic, checked). Block 5 was far below that, and with the pause of 6.3 the one
event observed would stop nothing. Thermal state does not favour short sessions: each run starts after its own
idle baseline, and the 45-minute corpus warms the machine before the first science run in either design.

**Decision: block 5's shape, unchanged** (both seats agree): 125 runs for ALPHA and BETA (18 + 7 + 2 x (10 + 40)),
107 for GAMMA (18 + 9 + 2 x 40), 10 planned units, 5 the registered minimum, corpus 18 planned although the bound's
minimum becomes 6, nothing changed inside a run. The council kept 10 units (threshold note 8.1, R1). One
correction to that note: section 3.5 says 125 runs "take about 9 hours"; block 5 measured 5.8 to 6.0 h.

## 5. How many sessions, in what order

**Target 3 claim-usable block-6 sessions per pack; at least 2 (the commitment of item 37).** Block 5 has one
session per pack, so it cannot show whether a number holds on another day. With block 6 at 2 the paper has three
independent sessions per quantity; at 3 it has four. A spread estimated from four sessions rests on 3 degrees of
freedom instead of 2, and a mean over sessions narrows by t / sqrt(n): 4.303 / sqrt(3) = 2.48 at three sessions,
3.182 / 2 = 1.59 at four, 36% narrower. The third round costs about 23 h of a month. Any summary over sessions is
a new estimator and must be registered before data; the per-session arithmetic stays block 5's.

**Order: interleaved rounds** ALPHA, BETA, GAMMA, three times. A slow change of the machine over days then spreads
across packs instead of hiding in one; GAMMA in round k takes its floors from ALPHA and BETA of round k, of the
same days (if a floor session of round k does not count, the next counting one of that pack, fixed now); and a
round of about 23.3 h moves each pack's t0 about 40 minutes earlier each day, so sessions sample different times of
day.

**What counts.** A session counts toward the target when no physical hazard stopped it and it carries no flag the
block-6 analysis plan names as excluding. Every other session is kept, flagged and printed in the
flagged-inclusive line, and does not count.

**Attempts.** A pack stops at 3 counting sessions. The same cause removing two consecutive attempts of a pack
sends that pack's next spend to a two-seat consult (doctrine gate 3); the other packs continue. After 5 attempts
of one pack without its target the loop pauses that pack and wakes the orchestrator; this never cancels the
commitment of 2.

**Time.** Cycle per pack: ALPHA 350 (t0 to chain end, 16:12 to 22:02) + 45 harvest + 85 desk = 480 min; BETA 360
+ 49 + 85 = 494; GAMMA 294 + 42 + 85 = 421. A round is 1,395 min = 23.3 h. Three rounds: 69.8 h, **2.9 days**
with no loss. At 0.86 usable per attempt, 9 / 0.86 = 10.5 attempts, **3.4 days**. Before them: fault rehearsals
(5.5 h) and round 0 (23 h).

**Disk is the binding resource.** A collected session keeps about 43 GiB (item 21). Nine claim sessions need
9 x 43 = 387 GiB, three round-0 sessions 129 GiB more, plus 20 GiB reserve: 536 GiB. Free now: 327 GiB (`df -g`,
2026-10-14). Either the per-session bytes shrink (measure which part of the 43 GiB is needed), round-0 archives
are removed after their record, or block-6 archives move to a local external drive that macOS cannot evict
(iCloud cannot be used: item 34). This is Ed's hardware call and comes before registration. If it is not
solved, the registration says 2 sessions per pack, decided before any data.

**Update 03:01 PDT 2026-10-14: disk is solved by compression.** Measured on a non-claim rehearsal: a 83.0 MB powermetrics plist compresses to 1.2 MB with `zstd -3` (about 70 times; byte-identical round trip), and a session's archive also holds a second full copy of its runs root (8.2 of 17 GB in `corpus18-20261009T1949Z`). Compressing raw files at the session desk, after the harvest and the recompute (never between runs: that time is the next run's idle baseline), brings a session from about 43 GiB to well under 2 GiB. Target 3 per pack stands with no external drive. An external SSD may hold an off-machine backup, connected only at the desk and ejected before arming.

## 6. The unattended loop

### 6.1 The loop

```
PRECHECK(pack) --physics fails--> WAIT, re-measure every 5 min --> PRECHECK
     |  certain exclusion ------------------------------------------> WAKE ORCHESTRATOR
     v  ok; arm notice sent (its 30 min NO window runs during the smoke)
SMOKE collection (25-30 min) --> SMOKE DESK: harvest, A, dry run, recompute (~30 min)
     |  fails on physics --> WAIT --> SMOKE again
     |  fails otherwise  --> hold this pack; go to PRECHECK(next pack); WAKE ORCHESTRATOR
     v  pass
SETTLE (at least 10 min, until a 75 s idle baseline passes)
     v
SESSION collection from t0 (5-6 h) --> SESSION DESK: harvest, A, sleep reading,
     |                                  recompute agreement (structure only), record line
     v
ROTATE to the next pack of the round (skip a pack that has its target) --> PRECHECK ...
     ... until every pack has its target --> WAKE ORCHESTRATOR for the close
```

Named elements: PRECHECK is section 3.3; SMOKE and SMOKE DESK are section 3.1; SETTLE is a measured quiet
period; SESSION DESK is the block-5 brief's after-window steps as one script; ROTATE applies section 5's order
and stopping rule; WAKE ORCHESTRATOR starts a headless Opus 5.5 activation, which may run only while no
collection is installed (an agent draws 8 to 47 W at idle, threshold note Q4). No agent process is alive from
the smoke's start to the session desk's end.

### 6.2 Failure classes

| Class | Examples | Action | Owner told |
|---|---|---|---|
| Physics before t0 | clock, battery, thermal, contention, agent present, sampler, disk | wait and re-measure every 5 min; disk and sampler get one automatic remedy, then the orchestrator | fault mail if a wait passes 2 h |
| Physics inside a run | idle disturbance, contention, sleep, charger drop, clock step | the idle baseline slides up to 1,500 s (note 3.1); otherwise the run is excluded and flagged and the session continues; a per-session wait budget of 2 h, after which waits become skips | in the session line |
| Agent at the keyboard | census sees `claude` or `codex` | finish or exclude the run in flight, pause, resume 10 min after the last sighting with a fresh idle admission; stop only after 2 h of pause | in the session line |
| Physics that ends a session | sampler down more than 10 min; disk exhausted; sustained thermal emergency; session time limit reached | stop, keep the bytes, harvest with flags, rotate | fault mail |
| Smoke failure, not physics | stage exit code, flag kinds or refusal list differ from expected; recompute disagrees; harvest error | that pack's session is not armed; next pack's pre-check; orchestrator wakes. The same failure on two packs stops the loop | fault mail |
| Session harvest fault | program error | keep the raw bytes; orchestrator wakes; re-run the harvest after the fix (a pure function of the bytes); the next pack runs only if its own smoke, which includes a harvest, passes | fault mail |
| Session flags | any record condition | recorded, session kept; the same flag kind twice in a row on one pack sends a consult before that pack's next session | in the session line |

A measured science run that failed is never replaced. An idle wait that reaches the 1,500 s cap is a skip with a
flag, not proof the run was bad.

### 6.3 Two window-code changes this needs (so they enter block 6's seal)

1. **Pause instead of stop on an agent sighting** (adopted 2026-10-14 02:26 PDT; Ed: "the only doctrine is good science"). One 20-second `claude` session cost BETA 2.5 h of chain plus an
   attempt. The hazard is real (8 to 47 W) and belongs to the runs it overlaps, not the session. First the
   one-setting test (doctrine gate 5): a shell function in Ed's `~/.zshrc` that, while a session is armed, prints
   its end time and asks before starting `claude`. That is Ed's file and his call. Build the pause anyway, since
   a seat or a launcher can also start an agent.
2. **The driver holds its own no-sleep assertion** and reads the sleep-blind minus sleep-counting clock at every
   run's start and end (council S1). The keep-awake launchd job stays as the second layer.

### 6.4 What the owner is told

The arm notice with Ed's NO stays; it also carries the previous session's line (verdict word, counting or not,
flag kinds, durations). Fault mail on the rows marked above. Nothing before release names an energy, floor, sign
or outcome word. The mail is sent by a small program, not an agent. Delivery failure is recorded and retried and
never removes data. One mail per state change; a continuing hold is not repeated.

## 7. Before block 6 is registered, in order

1. **Decide now, blind** (orchestrator, recorded in RUN_STATE and the registration draft): session shape as block
   5; target 3, minimum 2, the attempt rule of section 5; interleaved rounds and GAMMA's pairing with fallback;
   what counts; the three checks and their pass rules; the replication word for GAMMA when there are two or
   three block-6 sessions (recommended: every counting block-6 session's word is printed, and "replicated" means
   all of them match block 5's); block 6's registration is sealed before block 5's release.
2. **Ed's restart**, so the `mediaanalysisd` and `photoanalysisd` disables take effect (item 35 (d)); and **Ed's
   storage decision** (section 5). Both need Ed; both come before the measurements.
3. **Quiet-machine measurements** (threshold note 8.3), no agent alive. Order: the measure-first list below,
   items M1 to M5 first, because they set the only refusal lines.
4. **Write the block-6 rule set**: each rule sized in joules (requirement 2), each refusal a measured physical
   hazard, everything else a flag; acceptance as the one function `A`.
5. **Replay** every new or changed rule over every known-good archive on disk (the rehearsals; block 5's three
   usable sessions, structure-only output: verdict words, flag kinds, counts). Refusal counts beside each rule
   (requirement 1).
6. **Build**: the pause and the no-sleep assertion (6.3); waiting admission (note 3.1); flag-and-carry for the
   capture; spare removed; the smoke rig change and the injections; the pre-check; the session-desk script; the
   loop; mail without an agent. Merge gates as the doctrine keeps them.
7. **Fault rehearsal per pack** on the release candidate (5.5 h), then **round 0** (23 h); freeze each pack's smoke
   expectation. Any failure goes back to step 6.
8. **Fix the independent recompute's agreement tolerance** from the fault-rehearsal and round-0 archives.
9. **Registration and analysis plan**: session shape, counting rule, which flags exclude a run or a session (the
   clause where the science is now protected), side-by-side reporting, any between-session summary. Cold gate,
   then seal.
10. Arm round 1 through the loop.

## 8. Measure first

These questions divide the seats or the design, and no argument settles them.

| # | Question | Why it matters | Measurement | Cost |
|---|---|---|---|---|
| M1 | Where is the one stop line on the timing bound? | the only capture refusal left (council T1) | test 15 extended: captures on a quiet machine, under one busy core, in the faulty launch context; and how often an ordinary capture exceeds 36.46 ms (rehearsals: 2 of 7, both possibly contaminated) | about 1 h |
| M2 | Does a long idle wait change a run's phase energy? | if yes, a waited run is flagged; sets the 1,500 s cap | test 8: 10 reference runs after the ordinary 85 s idle, 10 after 20 min, alternated | about 4 h |
| M3 | What is the longest sampler stream under waiting, and the clock's drift rate with network time off? | the clock-rate budget is (15 ms minus 5 ms placement) / longest stream: 10 ms / 1,835 s = 5.45 ppm if the stream grows by the full 1,500 s (Sol seat, illustrative) | read the stream length from the fault rehearsal; CLOCK_REALTIME minus CLOCK_MONOTONIC_RAW over hours | inside other tests |
| M4 | Outside power in watts per CPU-second, including bursts as long as a phase | the contention limit (Q1) | test 1 with burst placements | 10 min |
| M5 | Does a graphics-processor contender add power the CPU count misses? | 10 W would add 6.2 J to a prefill | read the graphics rail in idle and in a CPU-only reference run | short |
| M6 | Per-session bytes, by part | decides whether 9 + 3 sessions fit (section 5) | `du` of round 0's runs root and archive by subfolder | minutes |
| M7 | Smoke desk time: harvest, acceptance, dry run, recompute | the cycle length; the harvest's ~18 min fixed part may shrink | the first fault-rehearsal smoke | none extra |
| M8 | Loss rate under waiting admission | whether 10 units keep a margin; replaces the 0.86 usable rate | round 0's BETA across 12:53 (test 9) | inside round 0 |
| M9 | Time-server query scatter | sizes the diagnostic offset flag | test 11 | 10 min |
| M10 | Do the rails read true watts? | the paper's comparability statement | rails against the wall meter in a charger-supplied state (test 13) | half a day |
| M11 | Does a smoke an hour before t0 change a session against block 5's, which had none? | replication | cannot be tested blind; the 10 min settle, idle admission and the 45 min corpus come between; recorded as an assumption | none |
| M12 | Do injected faults behave like the real ones? | the fault rehearsal's value | compare the injected sleep and agent records with BETA a4's and a2's | minutes |
| M13 | Can the wall meter (50 samples/s, clock fitted to the Mac's) locate a phase's power edges well enough to check the sampler's alignment bound independently? | the alignment bound (about 30 ms) drives the first-kind bound and every floor; a second instrument would test it instead of trusting the calibration capture alone | a known square load step on a quiet machine: meter edge versus sampler edge versus the program's own edge timestamp; measure the meter clock fit's precision and the power path's lag (adapter, input stage, battery) | about 1 h |
| M14 | Is the meter's idle-baseline power a direct measure of outside power, in watts, including graphics and neural-engine contenders that processor time misses? | would replace the processor-time proxy for contention (M4, M5) with the hazard measured directly, at the machine's input | idle baselines with and without a known graphics-processor load and a known processor load; compare the meter's idle power step with the rails' | about 1 h |

Added 02:34 PDT 2026-10-14 (orchestrator, after Ed asked whether the wall meter could do more and whether toggling network time helped). Network time: keep it OFF and stop switching it on between sessions. No energy number uses the time of day; the join needs only a steady clock with no jump inside a run, and with network time off the Mac's clocks run at one rate (2.72 ppm offset is 0.33 ms over a two-minute run). Switching the daemon on is the one known way to make the clock jump. The query-only time-server reading (council C1) stays as the outside check. The meter is not a clock reference (no time of day, a crystal of unknown accuracy, samples arriving 10 to 17 ms late over USB), but M13 tests whether it can serve as an independent timing check of the thing that is actually uncertain, the sampler's alignment.

## 9. Where the seats disagreed, and the decision

| Question | Sol 6.1 | Opus 5.5 | Decision and reason |
|---|---|---|---|
| What the smoke runs | 37 runs: corpus of 12, all references, one repeat per phase, one quad in each of four stages; about 3 h 13 min with desk; "a 10 to 30 minute smoke is impossible" | 4 to 6 runs, no corpus, no quads; about 45 min | **Opus's short smoke.** A check repeated before every session should test what changes between sessions: the machine, the ledger, the disk, the launch context, the OS. The corpus, bound and quad code do not change between sessions on the same code, so they are tested once per code change (fault rehearsal, round 0). Sol's smoke would add about 19 h over six sessions for no catch the short one misses. Sol's 30 min impossibility applies to its own 37-run smoke, not to a 4-run one |
| What a smoke pass means | a pipeline pass, not a claim acceptance; the expected insufficient-unit refusals | an exact expected refusal list | Agreed. Refined here: chance physical flags re-run the smoke once instead of failing it |
| Smoke harvest time | 50 min | 10 min | **About 20 min**, from the three rehearsal harvests (section 3.1) |
| Analysis success path | run the analysis on a full clean rehearsal archive at every smoke | covered by the fault rehearsal | **Once per code change** (round 0): the same code on the same frozen archive gives the same answer every time |
| Full-length rehearsal | one per pack | one, BETA, across 12:53 | **One per pack, as round 0 through the real loop.** Requirement 5 asks for one per pack; GAMMA's contrast analysis is a different success path from the floors; the loop's hand-over to the next arm needs showing; about 23 h of a month |
| Sessions per pack | two rounds | target 3, at most 5 attempts | **Target 3, minimum 2**, conditional on disk (section 5). Four sessions per quantity instead of three is the cheapest gain in between-session evidence available |
| Smoke cadence | before every arm | before every session, then only after a change once nine in a row catch nothing | **Before every session in block 6.** Nine smokes is the whole block; apply the pruning rule at its end |
| The spare reference | specify and test it | make it work or remove it | **Remove it.** 0 of 2 live uses worked (item 15), and its failure caused BETA a1's loss. A lost reference becomes a flag; the registration must state that the drift screen is defined on the survivors |

The seats agreed on: 10 units, corpus 18, nothing changed inside a run; acceptance as one shared function called
before t0; a physical hazard waits, anything else is a flag; pause, not stop, on an agent; a no-sleep assertion in
the driver; no agent courier; the smoke's captures kept out of the claim ledger; GAMMA paired with the same
round's floors; disk sized as measured writes plus 20 GiB per arm.

## 10. Dissent

- **Sol 6.1** would keep a 3 h smoke that runs the corpus and all four science stages before every session, and
  would stop at two rounds. Its strongest point, kept here: do not call usability "near-certain" until round 0
  and the measure-first list replace the forecasts. Nothing in this design has been run yet.
- **Opus 5.5** would freeze the smoke's flag set exactly. This draft relaxes that for chance physical flags,
  because an exact match would fail about 1 smoke in 13 on a capture tail alone (two captures, 1 in 25 each).
- **The reconciler's own reservation**: a third round is worth 23 h only if disk is solved without moving claim
  evidence to storage macOS can evict; if it is not, two rounds is the honest choice and must be written before
  any data.

## 11. Numbers checked

Every number either seat used was checked against its source. Agreed unless marked.

| Claim | Source | Result |
|---|---|---|
| BETA chain times a1 to a6, 21.4 h lost, 42.5 h wall, gaps 4.2/1.4/0.6/2.1/6.8 h | `seal2-beta-a*-window.md` | correct |
| ALPHA a1 chain 350 min, harvest 45; BETA a6 355 (t0 to end 360), harvest 49; GAMMA a1 291 (t0 to end 294), harvest 42 | window records | correct |
| Run losses 2 + 8 + 5 + 6 + 3 + 4 = 28 of 732 | window records, items 18, 23, 28, 31 | correct |
| Rehearsal durations 4,117 s, 3,381 s, 458 s, 8,635.7 s; harvests 20.1, 2.3 min, 2 s, and 23.4 min | `rehearsal-real/*` logs and file times | correct; the 23.4 min is new here |
| Corpus-18 rehearsal harvest: `cell.below_minimum`, `code.identity_unmeasured` | `harvest-pinned.stdout` | correct |
| Rehearsal captures 30.6, 30.1, 29.3, 30.5, 32.8, 40.1, 48.0 ms | operator logs, `b_fiducial_s` | correct |
| Sampler 255 and 254 ms at the rehearsal arm refusals | `refusal.json` | correct (255.0, 253.9) |
| 1.74x interval, 1.5 floor guard, 0.9996 / 0.988 / 0.254 survival, 5.45 ppm, 278 GiB, 0.026 per hour, 0.158 per hour crossover | arithmetic re-run | correct |
| Opus: smoke harvest 10 min; a stage costs 1.5 min fixed | rehearsal data | **corrected**: about 20 min; no visible fixed cost per stage beyond its runs |
| Opus and the process inventory: first-seal ALPHA a1 lost to the midnight walk | `alpha-a1-consult.md`; t0 15:01 PDT | **corrected**: outside analysis agents inside runs; a3 was the midnight walk |
| Sol: "the first arm has 63 GiB free" | threshold note 8.1, L2 | **corrected**: 63 GiB is the required free space; 327 GiB is free now |
| Threshold note 3.5: 125 runs "take about 9 hours" | window records | **corrected**: 5.8 to 6.0 h |

## 12. Read and not read

Read: both seat files; `RUN_STATE.md` items 9 to 37 and the first-seal summary; the threshold note, sections 3 to 9;
on the records worktree the `seal2-*-window.md` records, `alpha-a1-consult.md`, `alpha-a3-window.md` (times only);
`/Users/edr/night-archive/pruning-1014/PROCESS-INVENTORY.md`; under `gate-prune/rehearsal-real/` the console logs,
`run-result.json`, `state.json`, `chain-stages.jsonl`, refusal records, operator-log capture receipts and harvest
summaries. Not opened: anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`,
`/Users/edr/night-g2a/`, `/Users/edr/night-archive/harvest-v5-b5-*`, any runs root under
`/Users/edr/night-custody/measurement/`, any pull request body.

## 13. Changes after Ed's objections and the three-model check (03:26 PDT 2026-10-14, before any block-5 number is seen)

Ed's objections (02:30 to 02:50): re-staging every fixed failure is silly once the cure is evidenced; a forced sleep cannot be undone unattended (waking needs root `pmset schedule wake`) and only re-proves a detector already proven on BETA a4; a "write the expected result before every check" ground rule is heavy-handed. Then Fable 5.1, Sol 6.1 and Opus 5.5 each answered the design questions blind and reviewed this plan (`/Users/edr/night-archive/block6-check/SYNTHESIS.md`). All three reached, unprompted, the plan's answers on the cause of block 5's losses, the pre-session check, pause instead of stop, and network time; all three chose 10 units, target 3 / minimum 2, interleaved rounds. Decisions (orchestrator):

**Science (fixed now, blind):**
1. **Replication needs the sign.** A GAMMA contrast is "replicated" only if every counting block-6 session gives the same outcome word AND the same sign of dbar as block 5 (plan 7.2: direction is the sign of dbar). All three found this.
2. **Exclusion levels come from a formula on non-claim data, never from block 5's results.** The level at which a flag excludes a run (contention, waiting admission, any other) is the level at which the added energy reaches one quarter of the smallest floor the paper prints, its watts measured on the quiet machine (tests M4, M5, M14). Block 5's unblinded sensitivity line is not consulted for any block-6 level; the threshold note's suggestion to read it first (3.3, section 5 item 2) is withdrawn.
3. **The single-step reconstruction estimator is declared now as a labelled diagnostic** for both blocks (F5: it cut the rehearsal's prefill scatter 4.6 times). It is printed beside estimator 1 and replaces nothing; the independent recompute computes it.
4. **The between-session summary is simplified:** per printed quantity, each counting session's value, their mean and their standard deviation across sessions. The ratio to a half-width is dropped (undefined for floors, and at four sessions it ranges 0.12 to 0.78 by chance alone).
5. **Whole-machine energy per phase is redefined to fit what the meter can see:** the meter term only (50 samples a second), gross over the phase, the same basis as the rail cells; the battery term (read once a second, absent in 38% of prefill phases) stays at request level, and a phase whose request shows battery assist is flagged. Same units as estimator 1; GAMMA, which has no repeat stratum, is not given this line.
6. **An agent sighting** pauses at the next run boundary, and the whole unit overlapping the agent's presence is excluded (a whole quad, since a pause breaks its A B B A spacing), with a flag.
7. **A lost reference, including GAMMA's midpoint, is a flag;** the drift screen runs on the surviving references and the registration says so.
8. **Block-6 energies stay blinded until block 6 closes** (3 counting sessions per pack, or 2026-11-07, whichever comes first; a pack that ends short is printed with its count and called short).
9. **A model-file hash mismatch stops the session** (it is a direct measure of running the wrong experiment, not a record about a record).

**Before block 6 arms:** a fresh calibration acceptance from quiet-machine captures (item 27's doubling trigger stands at 45 of 48 and would fire in block 6's second session); threshold-note test 7 (drift transfer to the 8B workload, and bias between the two models' measurements) added to the measure-first list as M15; compression at the desk never touches a capture the calibration ledger names (item 26; item 34).

**Process, made lighter:**
- Fault rehearsal per pack is replaced by desk tests on synthetic records at every code change (lost reference, capture over the screen, another session's capture in the ledger, a killed chain, disk fill) and one machine test of about 40 minutes on the final code (agent pause, an idle disturbance up to the 1,500 s cap, meter unplugged). No forced sleep: the cure is a setting in force since 10-10 (item 19) and its detector caught BETA a4's real sleep.
- No "expected result before every check" rule and no frozen per-pack smoke expectation: the smoke runs the session's own acceptance code and the loop reads its verdict. The smoke is collection, harvest and acceptance only (about 25 minutes plus the harvest); the analysis dry run and the independent recompute run once per code change, in round 0.
- No duration-based smoke hold (a 50% slower phase is about 1% of a run); a slowed model is caught by the per-run duration flag (note 8.2 item 1).
- No consult rule on a repeated flag kind; no settle by clock time (idle admission measures quiet directly); pack order rotates by round (A B G, B G A, G A B).
- Round 0 stays, one full-length non-claim session per pack, BETA first (the 8B pack has never run on a quiet machine).

**Corrections:** four of BETA's five losses were rule-losses, 18.9 of 21.4 hours (88%), not three; 0.86 was survival against one kind of stop, not a usable rate (block 5's second seal: 3 usable of 8 attempts), so the 3.4-day figure is a floor, not an estimate.

### 13.1 Smoke by fingerprint; no round 0 (03:33 PDT 2026-10-14, after Ed asked what smoking only on change risks and whether a full-length rehearsal tests anything shorter ones do not)

- **Smoke by fingerprint.** The pre-session check records a fingerprint of what a session depends on: code commit, OS build, model file hashes, boot session, meter device, powermetrics version, pack. The smoke (collection, harvest, acceptance) runs only when the fingerprint differs from the last passing smoke. Everything that drifts between sessions without a change (sampler cadence, contention, leaked processes, disk, evicted captures, clock, ledger) is measured directly by the pre-check. Residual risk: an unfingerprinted change shows up as flagged runs in one session, not a lost session.
- **No round 0.** Its count-dependent checks run at the desk on full-size synthetic archives (S10's production-shaped windows) through harvest, analysis and the independent recompute; time-of-day events are measured in block 5 and absorbed by waiting admission; BETA a6 was a full-length 8B session. Its one unique value, new code over six hours and the hand-over between sessions, is carried by each pack's first claim session under a rule fixed now: **a session in which the collection code failed structurally (crash, a missing record class, a hand-over that did not happen) is excluded, judged from structure alone before any energy is seen;** the structure of each pack's first session is examined before the next pack arms, and a defect is fixed before it does.
