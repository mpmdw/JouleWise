# Glossary of measurement terms

**Why this page exists.** Until 2026-10-12 the project's prose used the one
word "window" for thirteen different things (counted in a census of
2026-10-10), from a six-hour collection to a 100 ms instrument reading. A reader who had just learned that a window is
hours long could not know that "window edge" two sentences later meant the
boundary of a two-second phase. Reader-facing prose now uses the nine terms
below, one meaning each.

**What did not change.** Code identifiers, file names, schema names and the
sealed block 5 documents (`registration_block5.md`, `analysis_plan_block5.md`,
the seal record, and `docs/phase_2/window_runbook.md`, whose bytes are pinned
by the seal) still say "window". Renaming them would change bytes that the
seal fixed by hash, so they stay until block 5 is released. Each entry below
therefore ends with a **In code** line giving the name to search for.

The terms are ordered from the longest span of time to the shortest. The
examples use block 5's ALPHA collection (the small model, Qwen3 1.7B).

| Span | Term | Typical length |
|---|---|---|
| the whole collection | session | about six hours |
| one try at it | attempt | same |
| its ceiling | session time limit | 110,220 s for ALPHA |
| its two ends | opening and closing calibration | one stage each |
| one model execution | run | seconds to minutes |
| the scored part of a run | measured interval | the request only |
| a part of that | phase interval | prefill or decode |
| one instrument reading | sampling interval | about 100 ms |

(The ninth term, session verdict, is a record and not a span of time.)

## Session

One uninterrupted, unattended collection of measurements on the dedicated
laptop, made in one machine state: an opening calibration, a fixed list of
runs, a closing calibration. Nothing else is allowed to run on the machine
while it lasts.

*Example.* The ALPHA session is 14 stages. Stage 2 is the opening
calibration, stage 14 the closing calibration, and the stages between them
hold the 125 runs: 100 science runs, whose energies are the result, and 25
auxiliary runs, among them the 18 reference runs that check the machine for
drift.

*In code:* "window" with no qualifier. `WINDOW_ID`, `window_id`,
`scripts/launch_window.py`, `scripts/harvest_b5_window.py`, schema
`harvest_b5_window.v1`. The runbook's "claim window" is a session.

## Attempt

One try at a session. A session plan can be tried more than once, because a
try can be refused before it starts or removed afterwards by a pre-registered
check. Every attempt is kept and disclosed; the analysis uses exactly one per
plan, called the analysed attempt.

*Example.* The BETA plan (the larger model, Qwen3 8B) was tried six times.
The sixth, identified as `v5-b5-beta-a6-20261011T2011Z` (`a6` is "attempt
6"), is the analysed attempt: 122 of its 125 runs succeeded.

*In code:* the integer `attempt` in the plan inputs
(`joulewise/b5/plan.py`), and the `-aN-` part of a `window_id`. The phrase
"claim-usable window" in `RUN_STATE.md` means the analysed attempt.

## Run

One execution of one model on one prompt, with its own power recording and
its own folder of evidence. Runs are what a session's size is counted in.

*Example.* "ALPHA is 125 runs" means the small model was executed 125 times
in one session. It does not mean 125 sessions.

*In code:* "member" (`members`, `science_members` in
`configs/campaigns/v5_claim_25g83/sizing_b5.json`); the folder a run writes is
a "run bundle". No code calls a single run a window.

## Measured interval

The part of one run whose energy is reported: from the event-log marker
written once the power sampler is confirmed running, to the marker written
when it is stopped. Loading the model, the warm-up request and the cool-down
lie outside it. Every energy figure for a run adds up power readings that
fall strictly inside this interval.

*Example.* A run's life is idle sampling, model load, warm-up, the measured
request, cool-down. Only the fourth step is the measured interval, so a run
that takes, say, 20 s to load its model and 8 s to answer has an 8 s measured
interval.

*In code:* `BundleReader.measured_window()` in `joulewise/bundle_read.py`;
the bounds are `window.start_s` and `window.end_s`; the markers are the
`sampling_started` and `sampling_stopped` events.

## Phase interval

One of the two parts of a measured interval. The *prefill interval* is the
time the model spends reading the prompt before it emits anything; the
*decode interval* is the time it spends generating output tokens. The paper
reports energy for each separately.

*Example.* For a small model the prefill interval can be shorter than a few
100 ms instrument readings, too short to measure. That is why the
prefill probe of 2026-10-02 tried prompts of 512, 1024, 2048 and 4096 tokens:
to find the shortest prompt whose prefill interval overlaps at least five
readings.

*In code:* `window_class == "phase"` (as opposed to `"gross_request"`, the
whole measured interval); the sealed analysis plan's "phase window".

## Sampling interval

The stretch of time that one record from the power instrument summarises.
The instrument (`powermetrics`, the macOS power sampler) does not report
instantaneous power; each record is the average power over the interval
since the previous record.

*Example.* The instrument is asked for one record every 100 ms, so a 2 s
decode interval is covered by about 20 records, and a phase boundary that
falls inside a record splits that record's energy between two phases.

*In code:* `sampling_interval_ms` (value 100); the paper skeleton's
"averaging window".

## Session verdict

One record stating whether a session as a whole passed its session-level
checks, as opposed to a check on a single run. Which checks it covers, and
what a failing verdict does to the analysis, are fixed in the sealed
registration (section 0.17), not here.

*Example.* ALPHA has one session verdict covering all 125 runs, not 125
verdicts.

*In code:* "whole-window verdict": `joulewise/whole_window.py`, the file
`whole-window-verdict.json`, the flag `whole_window.verdict_absent`.

## Session time limit

The longest a session is allowed to last: its deadline is its start time
plus this limit. It is a ceiling computed before the session from the longest
each stage is permitted to take, retries included, so it is far above the
usual length.

*Example.* ALPHA's limit is 110,220 s (30 h 37 min), against a usual length
of about six hours. The rule is: add 3,300 s to the planned maximum span
and round up to a whole minute.

*In code:* `window_max_s` in `sizing_b5.json`, `WINDOW_MAX_S` in the plan
environment, computed by `scripts/size_b5_window.py`.

## Opening calibration and closing calibration

The first and last measuring stages of a session. Each is a calibration
capture: a recording used to check the power instrument's timing. Taking one
before the runs and one after them brackets the session: the instrument is
checked on both sides of the runs it measured.

*Example.* In ALPHA the opening calibration is stage 2
(`alpha-pre-calibration`) and the closing calibration is stage 14
(`alpha-post-calibration`).

*In code:* `pre_calibration_dir` and `post_calibration_dir` in
`joulewise/b5/plan.py`; "pre-window" and "post-window" capture in the sealed
registration.

## Historical names you will still meet

"Window A", "Window B", "Window C" and "Window D" are names of measurement
campaigns and sessions from mid-2026, kept as written wherever
a record quotes them. "Window A" was a campaign of several sessions (for
example session a10 of 2026-07-25); it was never a single session. "Night"
in dated history entries means a session that ran overnight; since
2026-09-29 sessions start at any hour.
