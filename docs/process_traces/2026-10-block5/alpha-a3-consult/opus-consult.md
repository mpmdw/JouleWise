# ALPHA attempt 3 consult: Opus seat

Seat: blind consult, Opus 5.5. Code read at worktree commit `7e6158d669cbb6fb35761aee18abf363f07c5d36`
(paths below are relative to that tree unless they start with `~`). Evidence opened: the five permitted
files of attempts 1 and 3, attempt 2's `hazard_result.json`, the plan-time `chain.zsh` of attempt 3, the
attempt-1 and attempt-3 contention journals, and system launchd property lists (not restricted). No
restricted file was opened and no program was run over one. One scratch script was written under `/tmp`
to tally the two contention journals and was deleted afterwards.

Structure only: no energy, power or duration of a member, no member name, no error text.

## Cause

### (a) What makes a NEG-8 corpus member end as not succeeded, and what the retry can repair

The run-time condition that fits all the permitted evidence is the **idle-admission abort**, and it is a
physical condition. The reason the retry did nothing is **deterministic**.

1. The abort. Before its measured request each member records an idle baseline
   (`sampling.idle_seconds` in the corpus configs). The baseline is admitted only if, over its records,
   (i) the 95th percentile of the busiest single CPU's busy share is at most 0.5, (ii) the 95th
   percentile of CPU-plus-GPU package power is at most 1.0 W, on at least 30 records, and (iii) the GPU
   idle test passes. Thresholds: `configs/campaign_policies/quiet_mac_p2_b5.json`
   (`idle_admission_extension.cpu_criteria`). Evaluator: `joulewise/idle_admission.py:392-478`; the
   percentile is nearest-rank (`:337-341`), so an attempt fails once about 5% of its records are over
   either limit. GPU test: `joulewise/adapters/powermetrics.py:1949-2006`, limits at `:70-72`.
   A failed first attempt is followed immediately by a second (`retry_backoff_s` is 0 in the policy, so
   the sleep at `joulewise/controller.py:1949-1957` is skipped); if the second also fails and the policy
   says `on_fail: abort`, the controller raises a stage failure
   (`joulewise/controller.py:1945-2002`, the raise at `:1991-2002`). On the HAZARD path only the
   *threshold* conditions keep this abort; missing-telemetry conditions admit and flag
   (`:2101-2138`, set at `:1243-1248`), and the environment-guard observations are recorded, not
   refusals (`:1881-1884`, `:1896-1897`, `:1960-1961`, `:2183-2185`).
   The stage failure is caught and written as a complete failure bundle with a summary whose status is
   not `succeeded` (`joulewise/controller.py:1616-1645`).
   So: **a member aborts when a background load of roughly 3 s or more out of each of two back-to-back
   idle windows pushes one core over half busy or the package over 1.0 W.** Two attempts with no gap
   sample the same burst, so any burst longer than about one idle window defeats both.

2. Other ways a member can end not succeeded on the HAZARD path (all leave a bundle directory):
   a failed admission-sampler start (`controller.py:1939-1943`), runtime prepare or warm-up failure
   (`:1777`, `:2298`), measured-run sampler start failure (`:2333`), any unexpected exception
   (`:1630-1638`), the 1800 s member cap (`scripts/run_campaign.py:3771`, `:11125-11151`,
   `:11235-11236`), or a bundle that exits 0 but fails the structural, custody, prompt-hash or
   config-binding checks (`scripts/run_campaign.py:2876-2934`, `:472-501`). A condition of this group
   that is deterministic in the code or the corpus configuration would fail all 12 corpus members (they
   share one configuration) and is excluded by 9 of 12 succeeding in attempt 3 and 10 of 12 in attempt
   1. An intermittent fault of this group is not excluded by the permitted evidence (see Least sure).

3. What the one retry can repair: only a member with **no bundle directory at all**. The retry re-runs
   the same stage into the same root (`joulewise/b5/chain.py:1214-1242`; attempt 3's
   `~/night-custody/v5-b5-alpha-a3-20261009T0644Z/chain.zsh:545-569`). The runner then decides per
   member (`scripts/run_campaign.py:3024-3039`): summary present gives `skip complete`, which is logged
   as failed and never re-measured when the bundle did not succeed (`:10731-10759`); a directory
   without a summary gives `incomplete existing`, also never re-measured (`:10865-10942`); only a
   missing directory gives `would run`. On the HAZARD path the one legacy way to fail before a bundle
   exists (cooldown unknown, `:11038-11093`) is switched off (`:3652-3683` returns true, so the branch
   is never taken). The registration says the same in words
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:1592-1606`).
   Attempt 3 confirms it with integers from `night/hazard_result.json`: corpus stage planned 12,
   present 12, succeeded 9 (present means a metadata or summary file exists,
   `joulewise/b5/driver.py:1480-1492`); `yield_tripwire.attempted_seen` 131 = 119 planned + 12 rows
   logged by the retry (9 skips and 3 refusals of an existing failed bundle;
   `joulewise/b5/driver.py:1683-1689`); `pre_bundle_runs_flagged` 0. **The retry measured zero
   members.** For an idle-admission abort, and for every failure in point 2, row 13's retry is a
   guaranteed no-op. The corpus has no working retry on this path; "12 planned, 10 needed" is the whole
   margin.

4. Physical or deterministic. The abort itself is physical: measured host load during the idle
   baseline. What is deterministic is that nothing downstream can recover from it, and one of the
   loads is clock-scheduled (below).

### (b) The two harvest codes

- `neg8.bound_not_derived` is emitted in two places. `joulewise/b5/harvest.py:4607-4611`: no bound
  artifact in the bound root, or one that validates against neither the committed 12-member manifest
  nor the custodied collected subset; the subset is rejected below 10 members (`:4718-4721`).
  `:5435-5438`: a bound existed but the harvest's physics drop left fewer than 10 clean members
  (`:5405-5406`). Attempt 3 is the first case: the chain's derivation ran on 9 members and exited 2
  (the core refuses below 10: `joulewise/whole_window.py:136`, `:1555`, `:4254`, `:4716`), so there is
  no artifact. Attempt 1 was the second case (10 kept at run time, derivation rc 0, then at least one
  physics drop).
- `neg8.screen_failed` (`harvest.py:4842-4956`) is emitted when the stored verdict's NEG-8 bracket is
  absent, not passed, or carries any `neg8_*` condition, unless a re-screen passes. With no valid
  bound the bracket carries both "bound underived" conditions (`whole_window.py:2204-2212`). The
  re-screen needs a bound (`harvest.py:5235-5239`); with `derived_from` unset neither the clean nor the
  collected bound exists (`:4596-4603`), so the re-screen cannot run and the code is emitted
  (`:4955`). **In attempt 3 the screen failure follows from the missing bound.** The start reference
  kept 2 of 3, which meets the endpoint minimum of 2 (`joulewise/b5/driver.py:1386-1389`;
  `whole_window.py:2192-2201`), so the reference count alone does not fail the screen. Attempt 1 shows
  the contrast: bound derived at run time, lost at harvest, and no `neg8.screen_failed`.
  Not knowable: whether the screen would pass on its drift arithmetic once a bound exists. That needs
  a bound, and there is none.
- No harvest or derivation defect found. Both codes are what registration 5.3 prescribes for 9 kept.

### (c) The contention journal

Attempt 3, 1,913 ten-second intervals, 173 over the limit (I reproduce the magistrate's tallies exactly,
and the attempt-1 figures 1,975 / 183).

- **Clustering at the start: yes.** First 360 intervals (the first hour, where the corpus and the start
  references run): 81 over-limit. Remaining 1,553: 92. That is 22% against 6%. Attempt 1: 49 of the
  first 360, 134 of the remaining 1,615 (14% against 8%).
- **What matters is sustained runs, not the count.** Runs of 4 or more consecutive over-limit intervals
  in attempt 3: six, all inside the first 326 intervals; none in the remaining 1,587. They are:
  intervals 42-45 (`airportd`, with `WiFiAgent`: aftermath of the Wi-Fi toggle); **74-104, 31
  intervals** (`find` in all 31, `fseventsd` in 13, `mds` and `mds_stores` in 2 each; summed offender
  share 0.32 to 0.84 CPU-s/s throughout); 198-205, 208-211 and 228-232 (`signpost_reporte` in 15 of
  those 17, `corespotlightd` in 4); 323-326 (`corespotlightd` in 4). After that the longest run in
  five more hours is 3, and the 100 science members lost none at run time.
  Attempt 1: one 16-interval run at intervals 221-236 (`fseventsd` in 14, share up to 0.86), inside
  the first hour, and two 4-interval runs much later; that chain lost 2 corpus members and 3 of 100
  science members at run time.
- `mediaanalysisd` is the most frequent offender (73 intervals, alone in 72) but it is a 10-second blip
  at 0.06 to 0.22 CPU-s/s, spread over the whole window: 57 of its 73 intervals fall in the last 2.3
  hours, where no member aborted. It is unlikely to be what aborts corpus members. It does matter for
  the harvest's in-span contention exclusions (attempt 1's `cell.below_minimum` and its corpus drop).
- **`find` is an operating-system job, not ours.** Two processes: the first started at exactly
  00:00:00 local and is over the limit in 18 intervals; the second started at 00:02:47, as the first
  ended, and is over the limit in 14. Share 0.29 to 0.48. This is the system launch daemon
  `com.apple.tmp_cleaner` (`/System/Library/LaunchDaemons/com.apple.tmp_cleaner.plist`:
  `StartCalendarInterval {Hour 0}`, program `/usr/libexec/tmp_cleaner`), a shell script that runs two
  `find` passes over `/tmp` in sequence (script lines 29 and 30: files, then empty directories). Of
  the 901 launchd property lists that parse on this Mac (system, local and user) it is the only one
  with a midnight calendar interval; there is no crontab and no `/etc/periodic`. Its
  five minutes of work are long because `/private/tmp` is very large here (about 149 GB, mostly
  session scratch); that part is ours. `fseventsd` in the same intervals is alone in none of them: it
  is reacting to the walk.
  **Consequence: any window whose span contains 00:00 local meets a roughly 5-minute, 0.3 to 0.8 core
  burst at a fixed clock time.** Attempt 3 armed at 23:44, which put that burst about 12 minutes into
  the monitor record, inside the corpus stage.

### What the permitted evidence cannot distinguish

- Whether the three corpus members that failed are the ones whose idle baselines fell in intervals
  74-104, and whether the failed start reference and its failed spare fell in 198-232 or 323-326. The
  stage and member times are in closed files. The fit is by position only: corpus first, start
  references next, six sustained runs in the first 55 minutes, none after.
- Whether the failures are idle-admission aborts at all, as opposed to an intermittent fault from
  point 2 of (a). The two programs under "Counts I would want" settle both.
- Which of the two limits (core busy, package power) was exceeded.

## Recurrence

Estimate for an unchanged attempt 4: **about 30% claim-usable (range 15% to 45%).**

What it rests on:

- Corpus run-time loss so far: 2 of 12 and 3 of 12, so 5 of 24 (0.21). Attempt 1 lost at least one
  more of its 10 at harvest. The sealed sizing assumed an abort probability of 1/37 per member
  (`registration_block5.md:2484-2488`); the corpus stage on this machine is running at about eight
  times that, while science members are at 3 of 200 (0.015), in line with the planning figure.
- With independent losses at 0.21 to 0.25 per member, the chance that at most 2 of 12 are lost is
  0.52 to 0.39. Losses are in fact clustered by burst, which helps when no long burst lands on the
  corpus and hurts when one does; two chains out of two had one land there.
- The corpus must also survive the harvest's physics drop with zero spare (attempt 1 did not), and the
  cells must keep their minimum (lost in attempt 1, kept in attempt 3). I put those two together at
  0.6 to 0.7.
- An attempt armed in daylight avoids the midnight job and the Wi-Fi-toggle aftermath, which is why
  the estimate is not lower. It does not avoid `fseventsd` episodes (attempt 1) or the
  `signpost_reporte`/`corespotlightd` episode.

The same odds then apply again to BETA and to GAMMA, each of which has its own corpus stage.

## Recommendation

**(c), with the no-cost parts of (b) adopted at once.** Not (d): the harvest and the derivation did
what registration 5.3 says. Not (e): the END STATE count is 2 of 233.

Why (c) and not another unchanged attempt: the corpus rule is sized on a loss rate the machine does not
have, its retry cannot fire for the failure that actually happens, and all three packs must pass
through it. At about 0.3 per attempt the block needs on the order of ten windows; a claim-usable
attempt 4 under the old seal would in any case be discarded when the cure supersedes the block
(`registration_block5.md:2866-2868`).

The new rule, and why it is better science:

1. **Enlarge the committed corpus from 12 members to 18; every member runs in every window; the bound
   is derived from every member that succeeded and that the mint and the physics drop keep; the
   minimum stays 10.** No threshold is loosened: admission, the 0.05 contention limit, the minimum of
   10 and the screen are unchanged. Membership is still decided only by admission and physics codes,
   never by a measured energy, and the order is fixed in the manifest. The bound is estimated from
   more draws on a normal window, never from fewer than today. At a per-member loss of 0.25 the chance
   of keeping 10 of 18 is about 0.98 (about 0.86 at 0.35), against 0.39 for 10 of 12. This also gives
   the harvest's physics drop the margin it lacked in attempt 1.
   I found no code that fixes the number 12: the driver takes the count from the order manifest
   (`joulewise/b5/driver.py:1402-1477`), the chain from the stage's expected count
   (`joulewise/b5/chain.py:1126-1132`), and `whole_window.py` and `harvest.py` mention 12 only in
   comments. So the change should be configuration and seal documents: six more member configurations,
   the order manifest, the settled-corpus manifest (new corpus id and pin), each pack's plan tree, and
   registration 5.3 and 5.5. The builder must confirm that claim before relying on it.
2. Leave row 13's retry in place and say in the registration that it cannot fire for an admission
   abort. Removing it is a code change with no gain.
3. Not recommended now: a wait between the two admission attempts. `retry_backoff_s` exists in the
   policy schema (`joulewise/schemas.py:474-506`) and the controller, but the registration records
   that a wait needs the sampler stream restarted to fit the clock budget
   (`registration_block5.md:2871-2873`). That is new collection code. It is the right second step if
   the enlarged corpus proves insufficient.

Gate: one prospective cold erratum (registration section 10), then the new sealed clone; the block
restarts at ALPHA with no data lost.

Steps, in order:

1. Now, magistrate alone, no window input changed: **never arm a window whose span contains 00:00
   local.** Check before arming: `date +%H:%M`; arm only between 00:10 and 18:00 local (span plus
   margin). This removes the `tmp_cleaner` burst from every stage, including the end references,
   where a 5-minute burst could take two of three.
2. Now: email the owner to restart during the desk period, when it costs no window, and to run
   `launchctl disable gui/501/com.apple.corespotlightd` before he does. Check after login:
   `pgrep -x mediaanalysisd; pgrep -x photoanalysisd; pgrep -x corespotlightd` prints nothing, and
   `launchctl print-disabled gui/501 | grep -E 'mediaanalysisd|photoanalysisd|corespotlightd'` shows
   each as disabled. The three daemons appear in at most 81 of 173 over-limit intervals in attempt 3
   (73 + 8) and at most 128 of 183 in attempt 1 (77 + 51; the sums count an interval twice when two
   of them share it). The main benefit is to the cells, not the corpus. Do not hold an arm for it.
3. After any restart, any daemon restart or Wi-Fi toggle, and after the last agent session ends: put
   the display to sleep (`pmset displaysleepnow`) and wait 60 minutes before the arm. Attempt 3 armed
   38 minutes after the `fseventsd` restart and right after the Wi-Fi toggle, and its first-hour
   record shows both. The arm's own 180 s dwell passed at once and did not see what followed.
4. Build (c) item 1, take it through the erratum and the seal, arm ALPHA under the new seal with steps
   1 to 3 in force.
5. Whether (b) runs in parallel: the build needs agent sessions on this Mac, and no window runs while
   one is alive, so the two do not overlap. If the desk is idle waiting on a gate or a person, an
   unchanged attempt with steps 1 and 3 is a free trial of those two steps and nothing more.

## Least sure

1. That the three corpus failures are idle-admission aborts caused by the sustained runs. It is
   inferred from the code and from position in the journal, not from a member record. If the first
   program below shows a different failure stage (sampler start, runtime, the member cap), the cause is
   an intermittent fault, the enlarged corpus is still protective, but the quiet-machine steps would
   not be the cure and the fault itself would need a fix.
2. That enlarging the corpus is configuration only. One reader that authenticates against exactly the
   committed manifest could turn it into a code change; the cost under registration 7.5 is the same
   either way.
3. The cells. Attempt 1 lost a cell and attempt 3 did not; with two chains I cannot size that risk,
   and (c) does not touch it. Step 2 is the lever for it.
4. Side observation, not a cause: the last science stage returned rc 1 with one logged failure and 20
   of 20 bundles succeeded, in attempt 1 and again in attempt 3. Identical twice suggests something
   deterministic in that stage's log or verdict row. It removed nothing, but it should be explained.

The one additional structural fact that would change my answer: the failure stage and admission
condition codes of the non-succeeded members (first program). A result other than "idle baseline, a
threshold condition on both attempts" moves the cause from the machine to the code.

## Counts I would want

Both print integers and code names only: no member name, no measured value, no message text.

**Program 1: why the non-succeeded members failed.** Arguments: the bound runs root, then the claim
runs root.

```python
import collections, json, os, sys

def admission(node):
    if isinstance(node, dict):
        value = node.get("environment_admission")
        if isinstance(value, dict):
            return value
        for child in node.values():
            found = admission(child)
            if found is not None:
                return found
    elif isinstance(node, list):
        for child in node:
            found = admission(child)
            if found is not None:
                return found
    return None

def load(path):
    try:
        with open(path, "rb") as handle:
            return json.loads(handle.read())
    except (OSError, ValueError):
        return None

for label, root in zip(("bound_root", "claim_root"), sys.argv[1:3]):
    tally = collections.Counter()
    for name in sorted(os.listdir(root)):
        bundle = os.path.join(root, name)
        summary = load(os.path.join(bundle, "summary_metrics.json"))
        metadata = load(os.path.join(bundle, "metadata.json"))
        if summary is None and metadata is None:
            continue
        status = summary.get("status") if isinstance(summary, dict) else None
        if status == "succeeded":
            tally["succeeded"] += 1
            continue
        tally["not_succeeded"] += 1
        tally["status=%s" % status] += 1
        reason = summary.get("failure_reason") if isinstance(summary, dict) else None
        tally["failure_reason=%s" % reason] += 1
        try:
            with open(os.path.join(bundle, "events.jsonl"), "rb") as handle:
                for line in handle:
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(event, dict) and event.get("event_type") == "failure":
                        tally["failure_stage=%s" % event.get("phase")] += 1
        except OSError:
            tally["events_unreadable"] += 1
        record = admission(metadata)
        if record is None:
            tally["admission_record_absent"] += 1
            continue
        tally["admission_decision=%s" % record.get("decision")] += 1
        attempts = record.get("attempts") if isinstance(record.get("attempts"), list) else []
        tally["admission_attempts=%d" % len(attempts)] += 1
        for row in attempts:
            cpu = row.get("cpu_admission") if isinstance(row, dict) else None
            codes = cpu.get("conditions") if isinstance(cpu, dict) else None
            key = "+".join(sorted(str(code) for code in codes)) if isinstance(codes, list) else "unrecorded"
            tally["attempt%s_conditions=%s" % (row.get("attempt") if isinstance(row, dict) else "?", key or "none")] += 1
    print(label)
    for key, count in sorted(tally.items()):
        print("  %s %d" % (key, count))
```

**Program 2: do the aborted members' idle baselines sit in over-limit intervals.** Arguments: the bound
runs root, then the window's `hazards/monitor/contention.jsonl`. It prints a two-by-two table and the
offender names; it prints no time and no count of intervals per member.

```python
import collections, json, os, sys

def admission(node):
    if isinstance(node, dict):
        value = node.get("environment_admission")
        if isinstance(value, dict):
            return value
        for child in node.values():
            found = admission(child)
            if found is not None:
                return found
    elif isinstance(node, list):
        for child in node:
            found = admission(child)
            if found is not None:
                return found
    return None

intervals = []
with open(sys.argv[2], "rb") as handle:
    for line in handle:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        values = row.get("values") if isinstance(row, dict) else None
        if row.get("kind") != "interval" or not isinstance(values, dict):
            continue
        start, end = (stamp / 1e9 for stamp in values["interval"]["wall_ns"])
        names = sorted({item["command"] for item in values.get("outside_over_limit") or []})
        intervals.append((start, end, names))

table, offenders = collections.Counter(), collections.Counter()
for name in sorted(os.listdir(sys.argv[1])):
    bundle = os.path.join(sys.argv[1], name)
    try:
        with open(os.path.join(bundle, "summary_metrics.json"), "rb") as handle:
            status = json.loads(handle.read()).get("status")
        with open(os.path.join(bundle, "metadata.json"), "rb") as handle:
            record = admission(json.loads(handle.read()))
    except (OSError, ValueError, AttributeError):
        continue
    attempts = record.get("attempts") if isinstance(record, dict) else None
    if not isinstance(attempts, list) or not attempts:
        table["%s admission_times_absent" % ("succeeded" if status == "succeeded" else "not_succeeded")] += 1
        continue
    hit = set()
    for row in attempts:
        begin, finish = row.get("start_s"), row.get("end_s")
        if not isinstance(begin, (int, float)) or not isinstance(finish, (int, float)):
            continue
        for start, end, names in intervals:
            if names and start < finish and end > begin:
                hit.update(names)
    group = "succeeded" if status == "succeeded" else "not_succeeded"
    table["%s %s" % (group, "idle_overlaps_over_limit" if hit else "idle_clean")] += 1
    if group == "not_succeeded":
        for item in hit:
            offenders[item] += 1
for key, count in sorted(table.items()):
    print(key, count)
print("offenders_in_not_succeeded_idle_baselines")
for key, count in offenders.most_common():
    print("  %s %d" % (key, count))
```
