CONTAMINATION DISCLOSURE: before this charge the session had auto-loaded the global CLAUDE.md, the project CLAUDE.md of the worktree, and the one-line memory index MEMORY.md (pointers naming block-5 checkpoints and process rules, among them a line saying attempt 2 was armed and a restart was asked for; no content of any window, no energy, no member name). I opened no RUN_STATE.md, no decision log, no docs/orchestration.md, no other process doctrine, and no restricted file. I ran no program over a closed file: the only window files I read are the open ones (`night/hazard_result.json` of attempts 1 and 3, `hazards/monitor/contention.jsonl` of attempt 3, the plan-time `night_plan.json` and `window.env` of attempt 3). No energy, power, duration or member name of any claim window reached this session.

# Cold ruling: block 5, ALPHA attempt 3, the next arm

Judge: Fable 5.1, cold, read-only, single foreground session, no subagent, no background task. Worktree HEAD `7e6158d669cbb6fb35761aee18abf363f07c5d36`, clean (`git rev-parse HEAD`, `git status --porcelain`).

Read, in order: `BRIEF-body.md`; `sol-consult.md` (seat 1; its JSON header is a report envelope, the body is complete); `opus-consult.md` (seat 2); `../alpha-a1/RULING.md`. Sources then read: `scripts/run_campaign.py` 3010-3045, 2870-2935, 3596-3630, 6363-6387, 10725-10765, 10850-10900, 11370-11410, 11495-11522; `joulewise/b5/chain.py` 146-192, 220-245, 800-845, 1113-1135, 1180-1245; `configs/campaign_policies/quiet_mac_p2_b5.json`; `joulewise/idle_admission.py` 44-67, 330-345, 392-480; `joulewise/schemas.py` 233-237, 267-278, 474-506; `joulewise/controller.py` 183-197, 1240-1250, 1840-1860, 1935-2005, 2030-2140, 2595-2635, 3440-3456, 3528-3548, 3668-3690, 4455-4462, 4508-4516; `joulewise/clock.py` 34-56; `joulewise/b5/harvest.py` 4540-4615, 4700-4725, 4842-4860, 4925-4960, 5230-5242, 5355-5440; `joulewise/whole_window.py` 130-145, 157, 2188-2215, 2262-2276, 4254, 4700-4722; `joulewise/b5/driver.py` 1384-1392, 1400-1495, 1678-1692; `scripts/size_b5_window.py` 36-51, 108-112, 446-455, 592-615, 678-684; `configs/campaigns/neg8_reference_corpus_v5/` (file list, `derivation/settled_corpus.json` keys and member count); `configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json` (stage graph, resolved through `joulewise.b5.chain.stage_plan` and `stage_argv` to each stage's order manifest); `configs/campaigns/v5_claim_25g83/flag_catalog.json` (rules and every code's family, effect, blinding); registration `registration_block5.md` sections 0.12 (605-630), 5.1 (1590-1608), 5.3 (1639-1760), 5.5 (1795-1911), 6.6 (2482-2490), 7 and 8 (2774-2898), 10 (3031-3054), 14 (3289-3300); magistrate brief `40-magistrate-brief.md` sections 6 (711-857), 9 (906-963), 10 (964-1100).

Probes executed (all foreground, all read-only): the attempt-3 journal recount below; structure-only prints of the two open `hazard_result.json` files (stage ids and return codes, per-stage counts, `neg8_corpus` counts, `yield_tripwire` counts, fault reasons, driver flag codes); a grep for a hard-coded corpus size in the chain, driver, harvest, whole-window, plan and sizer code; resolution of every ALPHA collection stage's order manifest and the overlap between stages. NOT EXECUTED: any command on live machine state (launchd, `/private/tmp`, uptime; the charge's verified facts are taken as stated); anything over a restricted file; a verification of `run_campaign.py` 11038-11093 and 3652-3683 (seat 2's claim that the legacy pre-bundle cooldown refusal is switched off; immaterial, see Q3 item 9); the idle-baseline record cadence behind seat 2's "about 3 s" figure (immaterial).

Journal recount (my program over `v5-b5-alpha-a3-20261009T0644Z/hazards/monitor/contention.jsonl`): 1,916 lines = 1 `session_start`, 1 `snapshot`, 1,913 `interval`, 1 `session_end`; 173 intervals carry an `outside_over_limit` entry; by process `mediaanalysisd` 73 (alone 72), `find` 31 (alone 18), `signpost_reporte` 17 (alone 14), `fseventsd` 13, `mobileassetd` 12, `PerfPowerService` 10, `runningboardd` 9, `mds` 8, `corespotlightd` 8 (alone 3), `airportd` 7, `mds_stores` 7, `deleted` 7; intervals 1-180: 49 dirty, 181-360: 32, the remaining 1,553: 92; `find` in ordinals 74-104 only; runs of four or more consecutive dirty intervals: 42-45, 74-104, 198-205, 208-211, 228-232, 323-326, none later; the monitor's first interval starts 23:47:46 local and the first `find` interval starts 23:59:56 local (the interval containing 00:00:00). Both seats' tallies and the magistrate's are confirmed, and seat 2's midnight attribution is confirmed from the journal's own clock.

Open-file facts (attempt 3, `night/hazard_result.json`): corpus stage planned 12, present 12, succeeded 9, `min_valid` 10; start reference 3/3 present, 2 succeeded, `min_valid` 2; every science stage full; `neg8_corpus` 12 listed, 9 kept, pruned; `yield_tripwire` `attempted_seen` 131, `pre_bundle_runs_flagged` 0; faults `yield_low`, `bound_derivation_failed`; driver codes `network_time.off_output`, `yield.stage_low`. Attempt 1: corpus 10 of 12 succeeded, no retry stage in the chain list, derivation rc 0.

---

## Q1. The count

**Ruling:** Neither seat's program runs as written. One program, written below, may run once, by the magistrate, from the desk, before any arm; every line of its output may be written into the records note, the erratum brief and the arm notice. It opens, besides open files, only the planned members' `summary_metrics.json`, `metadata.json` and `events.jsonl` in the two runs roots of attempt 3, and it prints fixed labels and integers only. Printing the code name `processor_combined_power_w_p95_exceeded` with a count is structure, not a leak.

**Why not seat 1's program.** (i) It opens `night/transcript/neg8-corpus-before-retry.json`, which decision O-7 closes with the rest of `night/transcript/`, to learn whether the three failed summaries pre-existed the retry. That question is already settled without any file: the runner never launches a member whose bundle exists (`scripts/run_campaign.py:3024-3038`, action `skip complete` on any readable summary whatever its status, `incomplete existing` on a bundle without one; `10736-10759`, a failed evaluation counts as a failure and no command runs; `10865-10900`, `incomplete existing` runs nothing), and the open tripwire count says the same: 131 attempts seen = 119 planned + 12 rows the retry logged, with 12 present bundles and 9 succeeded after it. Every file not opened is one that cannot leak (brief section 6). (ii) It reads only the bound root, so it says nothing about the failed start reference and its failed spare, which the cure question also needs. Its whitelist discipline is right and is kept below. Its top-level read of `metadata["environment_admission"]` is correct: the controller writes the admission record as a top-level metadata key (`joulewise/controller.py:3451`, the dict at 3440-3545 is the metadata object itself; `4460` reads it the same way).

**Why not seat 2's two programs.** Program 1 prints whatever string the file holds for `status`, `failure_reason`, `phase`, `decision` and each condition (`"status=%s"`, `"failure_reason=%s"`, `"failure_stage=%s"`, `"attempt%s_conditions=%s"`): a malformed or unexpected value, or a message that landed in one of those fields, would be printed verbatim. The brief's rule is fixed code names and integers; a program that can print file text is not that program, however unlikely the case. Program 2 is sound in substance (fixed labels, process names from the open journal, no time printed) and is folded into the program below. Seat 2's recursive search for the admission record is unnecessary but harmless.

**Why the program below cannot leak a claim energy.** A member that did not succeed measured no request: there is no claim energy in its bundle to leak. For succeeded members the program reads one word (`status`) and two timestamps of the idle baseline (`start_s`, `end_s`), and prints neither the timestamps nor anything derived from them except a yes/no overlap with the open journal. Idle-admission conditions are hazard verdict words about the quiet state before a request (registration section 7.6 says `claim_usable` reads "power (idle admission, the bracket)" and that reading these cannot select on the science outcome; section 8 releases "hazard measurements" and status words). The condition `processor_combined_power_w_p95_exceeded` says that the package drew more than 1.0 W while idle during a baseline; it is the same kind of fact as the arm's six hazard verdicts, which are open, and the value itself is never printed. Nothing in the output is a count of flags by reason code (brief section 10): these are counts of members by status word, failure-reason word, failure phase and admission condition, none of which is a catalog flag.

**Why it cannot let the re-arm select on the science outcome.** ALPHA has no claim-usable attempt and is re-armed whatever the count says (registration section 7.2). The count decides only which cure the next arm carries and what the erratum names as the cause. No threshold, catalog effect, minimum or roster changes on its account without the cold erratum of Q2.

**The program.** Run once as `python3 -I`, from the desk, with the two runs roots of attempt 3 and the open journal as arguments; copy its output verbatim into the records note.

```python
import collections, json, os, sys

STATUSES = {"succeeded", "failed", "unsupported"}                      # joulewise/schemas.py:233-236
REASONS = {"did_not_fit", "runtime_unavailable", "model_identity_mismatch", "telemetry_unavailable",
           "format_unavailable", "permission_denied", "transport_unavailable", "unsupported_workload",
           "cleanup_failed", "unknown_error"}                           # joulewise/schemas.py:267-277
PHASES = {"validate", "prepare", "idle_baseline", "warmup", "measured_run",
          "idle_drift_sentinel", "cleanup", "reduce"}                  # controller._begin_stage call sites
CONDITIONS = {"cpu_baseline_telemetry_missing", "cpu_baseline_telemetry_malformed",
              "cpu_baseline_sample_count_insufficient", "cpu_busy_ratio_p95_exceeded",
              "processor_combined_power_w_p95_exceeded", "gpu_idle_admission_not_passed",
              "gpu_idle_admission_unknown"}                            # joulewise/idle_admission.py:44-50
DECISIONS = {"admitted", "abort"}

def load(path):
    try:
        with open(path, "rb") as handle:
            value = json.loads(handle.read())
        return value if isinstance(value, dict) else None
    except (OSError, ValueError):
        return None

def name(value, allowed):
    return value if isinstance(value, str) and value in allowed else "other"

def intervals_of(journal_path):
    rows = []
    with open(journal_path, "rb") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if not isinstance(row, dict) or row.get("kind") != "interval":
                continue
            values = row.get("values") if isinstance(row.get("values"), dict) else {}
            wall = (values.get("interval") or {}).get("wall_ns")
            names = sorted({o.get("command") for o in (values.get("outside_over_limit") or [])
                            if isinstance(o, dict) and isinstance(o.get("command"), str)})
            if isinstance(wall, list) and len(wall) == 2 and names:
                rows.append((wall[0] / 1e9, wall[1] / 1e9, names))
    return rows

try:
    bound_root, claim_root, journal_path = sys.argv[1:4]
    dirty = intervals_of(journal_path)
    span = (min(s for s, _, _ in dirty), max(e for _, e, _ in dirty)) if dirty else None
    for label, root in (("bound", bound_root), ("claim", claim_root)):
        tally = collections.Counter()
        clock_ok = clock_bad = 0
        for entry in sorted(os.listdir(root)):
            bundle = os.path.join(root, entry)
            summary = load(os.path.join(bundle, "summary_metrics.json"))
            metadata = load(os.path.join(bundle, "metadata.json"))
            if summary is None and metadata is None:
                continue
            tally["bundles"] += 1
            status = name(summary.get("status") if summary else None, STATUSES)
            tally["status." + status] += 1
            succeeded = status == "succeeded"
            admission = metadata.get("environment_admission") if metadata else None
            attempts = admission.get("attempts") if isinstance(admission, dict) else None
            attempts = [a for a in attempts if isinstance(a, dict)] if isinstance(attempts, list) else []
            # Join: did any idle-baseline attempt overlap a dirty journal interval?
            windows = [(a.get("start_s"), a.get("end_s")) for a in attempts]
            windows = [(s, e) for s, e in windows if isinstance(s, (int, float)) and isinstance(e, (int, float))]
            group = "succeeded" if succeeded else "not_succeeded"
            if not windows:
                tally["join." + group + ".baseline_times_absent"] += 1
            else:
                for s, e in windows:
                    if span and span[0] - 3600 <= s <= span[1] + 3600:
                        clock_ok += 1
                    else:
                        clock_bad += 1
                hit = set()
                for s, e in windows:
                    for ds, de, names in dirty:
                        if ds < e and de > s:
                            hit.update(names)
                tally["join." + group + (".baseline_overlaps_over_limit" if hit else ".baseline_clean")] += 1
                if not succeeded:
                    for process in hit:
                        tally["join.offenders_in_not_succeeded_baselines." + process] += 1
            if succeeded:
                continue
            tally["failure_reason." + name(summary.get("failure_reason") if summary else None, REASONS)] += 1
            try:
                with open(os.path.join(bundle, "events.jsonl"), "rb") as handle:
                    for line in handle:
                        try:
                            event = json.loads(line)
                        except ValueError:
                            continue
                        if isinstance(event, dict) and event.get("event_type") == "failure":
                            tally["failure_phase." + name(event.get("phase"), PHASES)] += 1
            except OSError:
                tally["failure_phase.events_unreadable"] += 1
            if not isinstance(admission, dict):
                tally["admission.record_absent"] += 1
                continue
            tally["admission.decision." + name(admission.get("decision"), DECISIONS)] += 1
            tally["admission.attempts." + (str(len(attempts)) if len(attempts) <= 2 else "more")] += 1
            for ordinal, attempt in enumerate(attempts[:2], 1):
                cpu = attempt.get("cpu_admission") if isinstance(attempt.get("cpu_admission"), dict) else {}
                codes = cpu.get("conditions") if isinstance(cpu.get("conditions"), list) else []
                for code in sorted(set(codes) & CONDITIONS):
                    tally["admission.attempt%d.%s" % (ordinal, code)] += 1
                if not codes:
                    tally["admission.attempt%d.no_condition" % ordinal] += 1
        tally["join.clock_check." + ("ok" if clock_bad == 0 else "mismatch")] = 1
        for key, count in sorted(tally.items()):
            print("%s.%s %d" % (label, key, count))
except Exception:
    print("probe.failed 1")
```

Shape of every line: `<bound|claim>.<fixed label>[.<fixed code name or process name from the open journal>] <integer>`. The clock check guards the join: controller timestamps are epoch seconds (`joulewise/clock.py:55`) and the journal's `wall_ns` is epoch nanoseconds (`joulewise/hazards/contention.py:357`), so every baseline of this window must fall inside the journal's span; if one does not, the join lines are not to be trusted and only the status, reason, phase and admission lines stand.

**How the output is read** (used by Q2):
- `bound.failure_phase.idle_baseline 3`, `bound.admission.decision.abort 3`, and threshold conditions (`cpu_busy_ratio_p95_exceeded` or `processor_combined_power_w_p95_exceeded`) on both attempts: the three corpus losses are physical admission aborts. The machine-state reading of both seats holds.
- Any failure phase other than `idle_baseline`, or a failure reason other than `unknown_error`, on a corpus member: an intermittent fault of the runner, runtime or telemetry, which no machine-state cure touches. It is routed as a defect into the same erratum lane as Q2 (iii) and fixed there, under the same new seal.
- `join.offenders_in_not_succeeded_baselines.*`: which named processes overlapped the aborted baselines. `find` or `fseventsd` or `airportd` there is the first-hour, clock-keyed and event-keyed story; `mediaanalysisd` or `corespotlightd` there is the restart story.

---

## Q2. The next arm

**Ruling:** Build the corpus change now; spend no window under the old seal; do not hold anything for the owner's restart, but ask him to do it during the build, which is already a period in which no window can run. The ruling does not depend on the Q1 count; the count decides what the erratum names as the cause and whether a runner fault is fixed in the same lane.

**Reasons.**

1. *The arithmetic of 12-needs-10 is wrong for this machine whatever the mechanism.* The registered sizing assumed one abort in 37 members (registration 5.3 lines 1645-1647; 6.6 lines 2484-2488). The corpus has lost 2 of 12 and then 3 of 12 at run time (5 of 24, about 0.21), while the science members lost 3 of 200 across the two chains (attempt 1: 1 + 1 + 1 of 100; attempt 3: 0 of 100), in line with the planning figure. The loss is therefore not a property of the members but of their position: the corpus is the first collection stage, and the first hour of both chains is the dirty hour (attempt 3: 81 of the first 360 intervals dirty against 92 of the remaining 1,553; attempt 1: 49 against 134 of 1,615; every sustained run in attempt 3 ends by interval 326). Nothing in the corpus rule has margin against that: at 10 succeeded the retry does not fire (`chain.py:235`, `NEG8_RETRY_MINIMUM = 10`; the helper at 835-836 prints `no_retry` at 10) and the harvest's physics drop then needs zero losses (attempt 1); at 9 the retry fires and measures nothing (Q3 item 1). A deterministic corpus fault is excluded by 9 and 10 succeeding from one shared configuration.

2. *Why not an unchanged attempt 4 now, even in daylight.* The free cures remove the midnight job and the Wi-Fi aftermath from the next window; they do not change the first-hour rate of `fseventsd` (attempt 1's 16-interval run at 221-236), `signpost_reporte` or `corespotlightd` (attempt 3's runs at 198-232 and 323-326), none of which is clock-keyed. Both seats put an unchanged attempt at 25-30 % claim-usable; I have no better number and do not need one: the decision turns on what happens after a usable ALPHA-4. Either the block then continues under the old seal, so BETA and GAMMA each face the same corpus with the same first hour and the same roughly one-in-three odds, with every lost attempt printed beside every reported cell (registration 7.6, analysis plan 8.1), or the corpus change is built afterwards and the usable window is discarded (registration 7.5, lines 2866-2868). The first is worse science and slower in expectation; the second makes the window a six-hour trial that the Q1 count answers in seconds. A window now also delays the build by its whole span plus its harvest, because no agent session may be alive while it runs. And deciding the design by whether a coin-flip window passes is exactly the thing the registration's protections exist to prevent, even when the coin is structural.

3. *Why not hold for the restart (seat 1).* The restart's demonstrated effect is on `mediaanalysisd` and, if the owner runs the disable, `corespotlightd`. In attempt 3 `mediaanalysisd` is a ten-second blip spread over the window (57 of its 73 intervals in the last 2.3 hours, where no member aborted; seat 2's tally, consistent with my recount) and `corespotlightd` is in 8 intervals. Neither is the first-hour sustained load that plausibly aborted the corpus members. The restart is still wanted, for the cells' physics drop at harvest (attempt 1's lost cell), and the build period is the free time for it. Holding an arm for a person is the stall the registration forbids elsewhere (7.2's NULL row re-arms when the hazard is gone, not when a person is available), and it gains nothing here because no arm is pending until the new seal exists.

4. *Compatibility.* A larger committed corpus changes files a window reads (six member configs, the order manifest, `derivation/settled_corpus.json`, the pack plan trees, the sizing output) and the registered roster of 5.3 and 0.12: a prospective cold erratum (registration 10, line 3033) and, because every completed window executed the corpus stage, supersession of the block with a new seal and clone (registration 7.5, lines 2866-2868; brief section 9, steps 1-4). The data cost is nil: no ALPHA attempt is claim-usable. The old clone stays untouched and the three attempts stay harvested and disclosed.

**(i) An unchanged attempt 4 now:** no. No window is spent under the old seal. Deleting this project's own scratch under `/private/tmp` is a free cure and is done now, before the build: it touches nothing a window reads (the magistrate verified that), the procedure permits it, and it removes the cause of the midnight burst rather than scheduling around it: `/usr/libexec/tmp_cleaner` runs two `find` passes over `/tmp` at 00:00 every day (plist `StartCalendarInterval {Hour 0}`), and their length is the size of the tree they walk. Before every later arm the check is the entry count under `/private/tmp` after the scratch is removed; a small tree makes the two passes a matter of seconds, inside one monitor interval. The settle after agent sessions is in (v).

**(ii) Held for the restart:** no. The arm notice and the records note ask the owner to run, in this order and whenever he can during the build period, `launchctl disable gui/501/com.apple.corespotlightd` and then a restart; after his login the magistrate verifies before the first arm from the new clone: `launchctl print-disabled gui/501` lists `com.apple.mediaanalysisd`, `com.apple.photoanalysisd` and `com.apple.corespotlightd` as disabled; `pgrep -x mediaanalysisd`, `pgrep -x photoanalysisd`, `pgrep -x corespotlightd` print nothing, repeated after ten minutes; `sysctl -n kern.boottime` has changed; the watchdog is loaded again. If the new seal is ready before he has restarted, the arm goes ahead without it: the restart addresses the cells, not the corpus, and a restart during a window ends that window, so the notice tells him to restart only between windows.

**(iii) The corpus change, built now.** Seat 2's rule is adopted, with these fixings:

- 18 committed members, every member runs in every window, in the committed order of the manifest; the bound is derived from every member that succeeded and that the mint and the harvest's physics drop keep; the minimum stays 10 (`NEG8_DRIFT_MINIMUM_N`, `whole_window.py:136`; `NEG8_RETRY_MINIMUM`, `chain.py:235`, unchanged); the one corpus retry stays and the registration says in words that it cannot fire for a member whose bundle exists (it already does, lines 1596-1602).
- The six new members are new run ids whose scientific content is identical to r01-r12 (the bound builder binds every member to one `scientific_config_sha256` and one `condition_id`, `harvest.py:5409-5411`, and the mint refuses kept members of more than one condition, registration 5.3), under a new `corpus_id` in `derivation/settled_corpus.json` (the old id names a 12-member set; the bound artifact carries the id and the manifest hash, and the core reader authenticates against the manifest at `REGISTERED_NEG8_REFERENCE_CORPUS_FILENAME`, `whole_window.py:157`).
- *Seat 2's claim that no code fixes 12 holds for everything I read.* The chain takes the stage's member count from the plan tree's `expected_count` (`chain.py:1126`; stage graph entries carry `expected_count`, 12 for `alpha-bound-collection`); the driver counts the order manifest (`driver.py:1402-1414`, `1432-1477`); the harvest requires only that the collected members be committed members, each once, in committed order, at least 10 (`harvest.py:4703-4721`); the mint requires at least 10 (`whole_window.py:4716-4720`, `4254`); the sizer counts the corpus stage's members from the stage rows (`size_b5_window.py:446-455`, `592-598`) and mentions 12 only in comments (108-109, 680, 684); `chain.py` mentions 12 only in comments and rendered comment strings (64-68, 268-271, 1200-1202), `harvest.py` only in comments (4514-4516). The chain's wall budgets for the corpus prune and the bound derivation are 1,800 s each (`chain.py:184-185`), against about 270-320 s for 12 bundles (registration 5.5), so 18 bundles fit with room. The builder must still prove it: the seal landing test, the bench, and the desk seal check of brief section 9 step 4, and a dry render of each pack's chain showing `expected_count` 18 and `--max-failures 18` on the corpus stage (`chain.py:510-516`).
- *Does it keep the bound's meaning?* Yes, and it tightens rather than loosens it. The bound estimates the reference workload's within-window spread from n kept draws with t at n − 1 degrees of freedom (registration 5.3 line 1643); n moves from 10-12 to 10-18, so the estimate rests on more draws and the t multiplier falls (about 2.26 at n = 10, 2.11 at n = 18): on a normal window the screen gets slightly stricter, never looser. The corpus spans about 15-25 minutes more of the window, so slow drift inside it enters the spread; that is the quantity the screen asks about. The erratum states the n range and the multiplier range beside the formula.
- *Does it keep the protections against selecting on an outcome?* Yes, unchanged: membership is decided by admission, validity and physics codes only (the mint's closed drop list and the six physics codes, registration 5.3), never by an energy; a succeeded member left out for any other reason is a selected corpus and removes the window (`harvest.py:4721-4725` onward, registration 5.3); the order is fixed in the manifest; no step of the chain decides anything from a corpus energy. Running all 18 unconditionally adds no decision at all, which is why it is preferred to seat 1's predeclared spare stage: a spare stage adds a run-time decision and a second manifest identity that the collected-subset authentication (`harvest.py:4703-4721`, one committed manifest, committed order) and the mint's launch-lineage check would both have to learn, for a saving of 15-25 minutes on a normal window. Seat 1's point that the spares must never run "until a desired energy appears" is met trivially by a rule with no spares.
- Not adopted now: a wait between the two admission attempts (needs the sampler stream restarted, registration 7.5 lines 2871-2873, new collection code), and any change to the 0.05 contention limit or the admission thresholds (no evidence that they are wrong; registration 14 Q3 stays open).

**(iv) Order.** Now: the Q1 count; delete the project's scratch under `/private/tmp`; write the records note and the owner's notice (restart and Spotlight disable, during the build, between windows only). Then the erratum and the build (v). No window runs until the new seal, clone and desk seal check exist, because the build needs agent sessions and no window may run with one alive, and because a claim-usable window under the old seal would be discarded at supersession (registration 7.5). Then ALPHA attempt 1 under the new seal, with the procedure items of (v) in force. If the Q1 count shows a runner or runtime fault (a failure phase other than `idle_baseline`), that fault is fixed in the same lane and under the same seal; it does not add a second supersession.

**(v) Gates.** The corpus change needs, before it is built, one prospective cold erratum (one Fable 5.1 judge, one Opus 5.5 refuter; registration 10 line 3033, brief section 9) stating the new rule, its n and t ranges, the files it changes, and the Q1 output as its cause statement; and, before it is armed, the merge gates for code that a window executes plus the new seal (brief section 9: independent executing review, the whole suite on the merged tree, CI green on the final head, a cold Fable pass since it touches measurement, the inventory regenerated and committed as the new seal commit, `tests.test_b5_seal_landing` passing, the new clone with ledger and pin carried over, the desk seal check), with the #416 re-audit scoped to the diff. The two procedure items are not registered rules and need no erratum, because they change no file a window reads, no threshold, catalog effect, roster or blinding rule: (a) the pre-arm `/private/tmp` check above, which replaces seat 2's "never arm across 00:00 local": a standing ban on spans containing midnight would forbid arms from about 18:00 to 00:10 every day, a quarter of the clock under back-to-back cadence, to avoid a five-minute job whose length is ours to remove; it becomes the fallback only if the tree cannot be made small; (b) a settling wait of 60 minutes between any daemon restart, Wi-Fi toggle or owner login and the arm, with the display asleep (`pmset displaysleepnow`), sized to the two observed aftermaths (attempt 3's `airportd`/`WiFiAgent` run at intervals 42-45 after the toggle; attempt 2's `fseventsd` loop), and no general wait after an ordinary agent session, for which the evidence is mixed (the first-hour load may be the chain's own writes being indexed, which no wait removes and the enlarged corpus absorbs). Both are written into the records note as procedure, with their reason.

---

## Q3. What either seat got wrong that bears on the next arm

1. **The retry cannot re-measure an existing failed bundle: both seats right, verified.** `run_campaign.py:3024-3038`: a readable summary gives `skip complete` whatever its status; a bundle without one gives `incomplete existing`. `10736-10759`: `skip complete` with a failed evaluation counts one failure, prints a refusal, runs nothing. `10865-10900`: `incomplete existing` runs nothing. `chain.py:226-236` says so; registration 5.1 lines 1596-1602 say so. The retry's `retried` mode lists only members with no summary in the snapshot and one after (`chain.py:806-809`), so `member.retried` was flagged for none. Confirmed by the open tripwire: 131 = 119 + 12.

2. **`neg8.screen_failed` follows from the missing bound; 2 of 3 start references does not by itself fail the screen: both seats right, verified.** With no artifact the first emitter fires (`harvest.py:4607-4611`, `derived_from` None at 4596-4603); the physics emitter is then unreachable (`5362`, returns on `derived_from` None). With no bound the bracket carries both underived conditions (`whole_window.py:2204-2212`), the re-screen needs a bound it does not have (`harvest.py:5235-5239`), and the code is emitted (`4955`). Endpoint survivor counts of 2 or 3 are valid (`whole_window.py:141`, `2269-2273`; `driver.py:1386-1389`; registration 0.12 lines 615-618). Seat 1's caution that the permitted evidence cannot prove the screen would pass on its drift arithmetic once a bound exists is correct and changes nothing.

3. **Seat 2's thresholds and the zero backoff: verified.** `quiet_mac_p2_b5.json`: busy-ratio p95 at most 0.5, combined power p95 at most 1.0 W, at least 30 samples, `on_missing_telemetry` fail, `on_fail` abort, one retry, no `retry_backoff_s` key; the schema default is 0.0 (`schemas.py:474`, `494-506`), so the sleep at `controller.py:1949-1957` is skipped and attempt 2 follows attempt 1 at once (`1958-1972`). Nearest-rank p95 (`idle_admission.py:337-341`); threshold conditions fail the attempt, evidence-only conditions are admitted and flagged on the hazard path (`idle_admission.py:457-478`; `controller.py:2101-2138`, `1243-1248`). Abort after two failed attempts raises the stage failure (`controller.py:1987-2002`), which is written as a complete failed bundle (`2599-2632`). Seat 2's "about 3 s or more of each idle window" depends on the record cadence, which I did not verify; immaterial.

4. **The last science stage's rc 1 with 20 of 20: confirmed in both chains from the open file; not explained; not a cause.** Attempt 3: `alpha-science-prefill-p2048-abba-06-10` rc 1, 20 present, 20 succeeded; attempt 1: the same stage rc 1 with 20 of 20, while `alpha-science-abba-06-10` is rc 0 with 20 of 20 in both. One explanation is excluded: each stage's order manifest lists only its own members (resolved through `chain.stage_plan` and `stage_argv`: 12, 3, 10, 20, 20, 1, 10, 20, 20, 3 entries, zero overlap between stages, no spare set on a science stage), so no earlier failed bundle is re-evaluated in that stage. What remains, from `run_campaign.py:11398-11404` and `11498-11505`: `counts["drained"]`, a provisional collection verdict of `blocked` or `invalid` (`6363-6387`: a missing or invalid unwaived member), or the minimal-verdict append raising inside `_hazard_call` (`3596-3630`, which also emits `campaign.runner_record_flagged` and returns `_HAZARD_FAILED`). Which one needs the stage log, which is closed. It removed nothing: the harvest kept every unit of every reported quantity. It goes to the erratum lane as a defect to explain on the real-model rehearsal archive (brief section 6, a rehearsal is not a claim window), not to this arm.

5. **Seat 1's restart-first recommendation mis-targets the loss.** Not a misread of code or registration, but the restart cures processes that are not the first-hour sustained runs (item 3 of Q2). Seat 1 also says "an unchanged window while awaiting the restart ... complicates the owner's safe restart opportunity": true, and it is why no window runs during the build.

6. **Seat 2's "never arm across 00:00 local" is replaced** by removing the cause (Q2 (v)); seat 2's identification of the job is confirmed by the journal's own clock (first `find` interval starts 23:59:56) and by the magistrate's plist reading.

7. **Seat 2's recurrence arithmetic treats member losses as independent and says so;** the clustering it names (one five-minute burst takes about two consecutive members, since two admission attempts take about 170 s) is the reason 18 rather than 14 or 15: 18 allows eight losses, about four bursts.

8. **Both seats' estimate that a usable attempt 4 under the old seal "costs nothing in data"** is right only if the change is built regardless; if the block continued under the old seal after a usable ALPHA-4, every later pack would pay the same odds. Neither seat priced that; Q2 item 2 does.

9. **NOT EXECUTED:** seat 2's claim that the legacy pre-bundle cooldown refusal is switched off on the hazard path (`run_campaign.py:11038-11093`, `3652-3683`). Immaterial: the open tripwire shows `pre_bundle_runs_flagged` 0 in attempt 3, so no corpus member was refused before its bundle existed, which is the only case the retry could have repaired.

10. **The attempt-1 ruling's standing points hold here:** machine-state cures that change no file a window reads need no erratum (its Q1 item 2), and a structure-only count over closed files is permitted when a registration rule cannot otherwise be applied, with a whitelist and no per-member identity (its Q2). The present count is permitted on the narrower ground that the cause of three run-time losses is not readable from any open file and the erratum must name it.

---

## Q4. A question only the owner can answer

No. The restart and the Spotlight disable are already answered yes; the notice only asks him to do them during the build, between windows. Deleting the project's scratch under `/private/tmp` is within the magistrate's procedure. The corpus change, the erratum and the new seal are agent work under the registration's own gates (sections 7.5 and 10) and need no owner ruling. If the magistrate wants one word from him all the same, it is: "Block 5 restarts at ALPHA under a new seal with an 18-member NEG-8 corpus (minimum 10 unchanged); no data is lost because no ALPHA attempt was usable. Reply NO to stop it; silence or anything else means proceed."

---

**Standing order of operations for the magistrate, from this ruling:** (1) run the Q1 program once; copy its output into the records note. (2) Delete this project's scratch under `/private/tmp`; record the entry count after. (3) Write the records note and the owner's notice: the ruling, the Q1 lines, the restart and Spotlight-disable request for the build period, between windows only. (4) Convene the prospective cold erratum for the 18-member corpus (one Fable judge, one Opus refuter), carrying the Q1 output and Q2 (iii) as its brief; if the count shows a non-admission fault, the same lane fixes it. (5) Build, gate, merge, regenerate the inventory, seal, clone, carry the ledger and pin, desk seal check (brief section 9, steps 1-4). (6) After the owner's login, the (ii) checks; whether or not he has restarted, arm ALPHA attempt 1 under the new seal, with the `/private/tmp` check and the 60-minute post-event settle in force, and no agent session alive.

RULING: BUILD-CORPUS-CHANGE-NO-WINDOW-UNDER-OLD-SEAL
