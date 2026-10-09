# ALPHA-1 consult, Opus seat: findings

Blinding kept: I opened only the six permitted `harvest.json` keys, `derived/code-identity.json`, `night/hazard_result.json`, `hazards/arm.json`, the contention journal, `window.env`, and code and sealed documents in the worktree. I listed the staging directory's file names but opened nothing in it. I tested six archive files for existence only. I ran four read-only machine queries (`launchctl print`, `launchctl print-disabled`, `mdutil -s`, `sudo -n -l`) and one `ps`. I wrote nothing.

## Cause

### What emits each code (verified by reading code)

**`cell.below_minimum`**: `joulewise/flags/exclusions.py:367-368`. It fires when any target cell has a stratum whose kept units fall below the minimum (line 347).
- The minimum is 5 (`flag_catalog.json` `rules.cell_unit_minimum`).
- A unit is dropped when any of its members carries any EXCLUDE_MEMBER code (lines 332-346), so one flagged quad member removes the whole quad.
- Run-time failures cannot explain it alone. Science stages lost 0, 1, 0, 1, 1, 0 members, so at most one or two units per stratum. Reaching fewer than 5 of 10 needs at least four more units of one stratum removed at harvest by member-exclusion flags (inference from the counts).

**`neg8.bound_not_derived`**: two emitters.
- `harvest.py:4607` (`neg8_bound`): the artifact is absent, does not validate against the collected manifest, or fails member re-derivation.
- `harvest.py:5435` (`neg8_corpus_physics`): at least one corpus member of the validated bound carries a member-level code in `NEG8_PHYSICS_LOSS_CODES` (`harvest.py:91-93`), and fewer than 10 clean members remain (line 5405) or the clean bound fails.

**Which emitter fired (existence tests only):**
- `derived/neg8-corpus-physics.json` and `derived/neg8-clean-corpus.json` exist; `withheld/neg8-clean-bound.json` is absent.
- The physics record is written only at line 5433, after the early returns at 5362 (bound not derived by the first path) and 5373 (no flagged corpus member).
- So the first path passed, and at least one of the 10 bound members carries a physics loss code.
- The driver kept 10 of 12 (`hazard_result.json` `neg8_corpus.members_kept` 10), so one flagged member gives 9, below `NEG8_DRIFT_MINIMUM_N` = 10 (`whole_window.py:136`).
- ALPHA-1's corpus had zero slack after its two run-time losses. The retry decision ran (rc 0) and no second corpus collection stage appears in the stage list.

**The contention rule as coded** (`harvest.py:3208-3224`, joined at 6380):
- A member is flagged when any outside process other than `kernel_task` (`CONTENTION_EXEMPT`, line 319) exceeds the limit in any 10 s interval that overlaps the request at all. `_overlaps` is closed-interval.
- This matches registration §6.4 lines 2349-2351.
- The arm record's contention thresholds carry `cpu_limit_s_per_s` 0.05; I did not trace the harvest's `contention_cpu_s_per_s` key in the plan, only in the registration (§6.9, line 2560).

**Harvest defect: none found.** The harvest applied the registered rule. The harvest counts the monitor's "exited over limit" imputation (`contention.py:381-385`) as an offender, but that touches only 2 intervals.

### What the journal shows (integer tallies, harvest's own rule)

- 1,975 intervals, 0 errors, 0 gaps, one monitor session, about 19,750 s.
- **183 of 1,975 intervals (9.3%) are dirty**, in 134 separate runs (107 of length 1, 20 of length 2, 4 of length 3, 2 of length 4, 1 of length 16).
- Dirty intervals per 30-minute bin: 21, 28, 3, 14, 8, 6, 20, 28, 21, 22, 12. It is spread across the window with one quiet stretch, not one cluster.
- The arm dwell before the chain was 6 of 6 clean (`arm.json`), with the largest outside process at 0.015. The dwell did not predict the in-window rate.

| Process | Dirty intervals | Sole offender | Pattern |
|---|---|---|---|
| `mediaanalysisd` | 77 | 72 | one pid; median rate 0.209; most common spacing 13-14 intervals |
| `corespotlightd` | 51 | 43 | one pid; bursts |
| `PerfPowerService` | 13 (3 pids) | 0 | every 180 intervals (30 min), with `runningboardd` (10) |
| `fseventsd` | 14 | 12 | one burst, intervals 222-235, at about 0.84 |
| `mobileassetd` / `deleted` / `mds` | 10 / 9 / 7 | 1 / 0 / 0 | clustered about every 390-460 intervals |
| 20 other names | 6 or fewer each | | |

**`mediaanalysisd` is coupled to our workload, not random background.**
- By twelfth of the window its hits are 7, 7, 0, 1, 0, 0, 2, 10, 12, 14, 15, 9: present in some stages and absent in others.
- 68 of its 77 hits fall 2 or 3 intervals after the measurement tree's CPU rises through its median (those two offsets cover 631 of 1,975 intervals).
- 44 of 77 hits are in the top quartile of tree CPU.
- `mdworker_shared` is listed in 71 of the 77 hit intervals (578 of 1,975 overall), and a `powermetrics` exit sits one interval earlier in 46 of 77 (323 of 1,975 overall).
- So it lands inside requests more often than uniform placement predicts.

**`corespotlightd` leans the other way**: 37 of 51 hits are in the lowest tree-CPU quartile, so its request overlap is probably lower than its count suggests.

**Raising the limit is not a cure**: dirty intervals are 183 at 0.05, 151 at 0.10, 104 at 0.20, 59 at 0.25, 23 at 0.50.

**Does 9.3% explain both codes?** I placed a hypothetical request of length T uniformly in the window (T is my parameter, not a measured duration):

| T | P(member flagged) | P(quad lost) | P(quad stratum keeps ≥5 of 10) | P(10 corpus members all clean) |
|---|---|---|---|---|
| 10 s | 0.16 | 0.50 | 0.62 | 0.18 |
| 20 s | 0.22 | 0.64 | 0.28 | 0.08 |
| 30 s | 0.29 | 0.75 | 0.08 | 0.03 |

Contention at the journaled rate is sufficient to produce both codes.

### Are the processes ours to remove (live state now, not at window time)

- **`mediaanalysisd`**: the journal's pid 98055 (started Sep 30 17:21:50) is still running, with 127 CPU-minutes accumulated.
  - `launchctl print-disabled gui/501` lists both `com.apple.mediaanalysisd` and `com.apple.photoanalysisd` as disabled.
  - Yet `launchctl print gui/501/com.apple.mediaanalysisd` shows it loaded and running (runs = 4, immediate reason = ipc (mach)), with `dasd` background-task triggers (`photos.pec`, `photos.maintenance` and others).
  - So someone disabled it but it was never booted out. A disable only stops the next bootstrap; the loaded agent keeps being launched on demand. This is a cure that did not take.
- **`corespotlightd`**: a gui/501 LaunchAgent (pid 711, since the Sep 18 boot), not disabled. `mdutil -s` reports indexing enabled on `/` and `/System/Volumes/Data`.
- **`PerfPowerService`, `runningboardd`, `mobileassetd`, `deleted`**: periodic OS housekeeping at rest. I would not touch them.
- **Sudo**: passwordless sudo covers only the fseventsd restart helper, network time, and `powermetrics`. `mdutil -i off` needs Ed.
- **History**: this is a known contaminant here. The 2026-10-03 session record (`docs/process_traces/2026-10-03-activation-5bffbeaf/00-session-record.md:52`) has `dasd` scheduling `mediaanalysisd.photos.maintenance` 4 s before a member.

### What the evidence cannot distinguish

- **Which code removed the corpus member and the cells' units.** Contention is sufficient and all six arm hazards passed, but battery, thermal, clock-step and validity codes remove units too. I cannot see flags.
- **Which cell and stratum fell below 5**, and whether the stage pattern of `mediaanalysisd` matches it.
- **Why `mediaanalysisd` wakes with the workload**: a reaction to our file writes through Spotlight importers, or `dasd` releasing deferred Photos work. Either way it recurs.
- **Actual request overlap.** I have no member spans; the table above is parametric. My Spotlight query (`mdfind -count`) returned 0 even on the source worktree, so it tells nothing about whether the runs roots are indexed.

## Recurrence

An unchanged ALPHA-2 would very probably fail the same way; my estimate is 85-95%.
- The top offender is one long-lived process, launch-on-demand, coupled to the workload, and seen on this Mac on 09-17, 10-03 and now.
- Its hits in the second half of the window (62 of 77) show no backlog draining.
- The clean dwell shows that waiting at idle does not screen it.
- Even at T = 10 s, the product of the two-cell quad survival and corpus survival is below 0.3, before run-time failures.

## Recommendation

**(b)**: cure the machine state, then arm ALPHA attempt 2 from the same sealed clone, with nothing a window reads changed.

**Why not the others:**
- **(a)** fails on the recurrence estimate.
- **(c)** is not required by the physics yet. The limit is not shown wrong: the main offender spends about 2 CPU-seconds per event inside requests, which is the disturbance the rule exists for. Removing a contender is better science than widening a limit to admit it, and no limit below 0.25 would admit it anyway.
- **(d)**: no defect found.
- **(e)**: the END STATE rule is nowhere near met (116 statuses, 1 not bounded).

**Steps (user domain, no sudo):**
1. Remove the two disabled-but-loaded agents:
   - `launchctl bootout gui/501/com.apple.mediaanalysisd`
   - `launchctl bootout gui/501/com.apple.photoanalysisd`
2. Check the cure took: `launchctl print gui/501/com.apple.mediaanalysisd` must fail with "Could not find service" (same for `photoanalysisd`), `pgrep -x mediaanalysisd photoanalysisd` must print nothing, and `launchctl print-disabled gui/501` must still list both as disabled. Repeat 10 minutes later, because launch is on demand.
3. If the bootout is refused, the fallback is a logout/login or reboot, after which the existing disable entries stop the bootstrap. I have not checked what a reboot does to the registration §2 preconditions; the magistrate should before using it.
4. For the second offender: `launchctl disable gui/501/com.apple.corespotlightd`, then `launchctl bootout gui/501/com.apple.corespotlightd`, with the same three checks.
   - I am less sure of this one. I have not verified that clients do not respawn or spin against a missing service.
   - The arm dwell is the net: a new persistent spinner above 0.05 refuses the arm.
   - If the magistrate prefers one change at a time, do step 1 only and accept lower odds.
5. Keep the same state for BETA and GAMMA. Run the step 2 checks before every remaining arm and name the state in each arm notice, so the three analysed windows share one machine condition.
6. ALPHA-2 is the real test, because the trigger is the workload and an idle check cannot show it. After its harvest, rerun the same tally on its journal. Pass means `mediaanalysisd` at 0 dirty intervals and the total near the residual below.

**Expected residual** (the same journal with the offenders removed, uniform placement):

| Scenario | Dirty intervals | P(quad stratum keeps ≥5), T = 20 s | P(corpus of 12 loses ≤2 to flags), T = 20 s |
|---|---|---|---|
| ALPHA-1 as run | 183 | 0.28 | 0.48 |
| minus `mediaanalysisd` | 111 | 0.83 | 0.83 |
| also minus `photoanalysisd` and the Spotlight family (`corespotlightd`, `mds`, `mds_stores`) | 64 | 0.97 | 0.95 |

The third row assumes step 4 also quiets `mds` and `mds_stores`, which the bootout does not directly do.

**If ALPHA-2 fails again with the same cause family**, §7.3 sends it to a consult, and the erratum I would then support (registration Q3, lines 3296-3299, anticipates it) has three parts:
- Judge contention by outside CPU-seconds inside the request span, not by any touch of a 10 s interval.
- Give the corpus a spare or retry when it sits at exactly 10, so a harvest-time physics drop does not remove the window.
- Ask Ed for `sudo mdutil -a -i off`.

The first two change window code or thresholds, so they carry the §7.5 and §10 cost; I would not pay it before the free cure is tried.

## Least sure

- **Whether contention is the code that actually removed the units and the corpus member.** It is sufficient and most likely, but I cannot see flags. If the removals are mostly another family (battery, thermal, validity), the daemon cure would not fix ALPHA-2 and my answer changes to a consult on that family.
- **Whether the bootout succeeds under SIP and stays gone**, and whether disabling `corespotlightd` is side-effect free. Both are inference from general macOS behaviour, not tested here.

**The one fact that would change my answer** is the exclusion count by code family for ALPHA-1 (below).

## Counts I would want

This reads a closed file (`derived/exclusions.json`) and prints only code names and integers: no member names, no positions. The magistrate decides whether to run it.

```python
import json, collections
a = "/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261008T2201Z/derived/exclusions.json"
d = json.load(open(a))
print("member-excluding codes, members carrying each:",
      sorted(collections.Counter(c for m in d["members_excluded"] for c in m["codes"]).items()))
print("members excluded:", len(d["members_excluded"]))
for i, cell in enumerate(d["cells"]):
    print("cell", i, "target", cell["target"], "kept", sorted(cell["n_kept"].items()),
          "minimum", sorted(cell["minimum"].items()), "resolvable", cell["resolvable"],
          "dropped-unit codes", sorted(collections.Counter(
              c for u in cell["dropped_units"] for c in u["codes"]).items()))
```

- If `contention.request_overlap` dominates the dropped-unit codes, (b) stands as written.
- If another family dominates, do not arm on the daemon cure alone.

A second count, existence only: whether `/Users/edr/night-b5/` and `/Users/edr/night-custody/` are on Spotlight's privacy list (System Settings, or Ed reading the volume configuration plist with sudo). That would say whether our own file writes feed the importers.
