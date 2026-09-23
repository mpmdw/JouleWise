VERDICT: MERGE-AFTER-DICTATED-CLOSURES

# Cold Fable 5.1 ruling, lane A276 (NOTICE-SUMMARY-V3-TEXT-01), head 912345cd

Judge: Claude Fable 5.1, cold, detached worktree /Users/edr/code/wt-1d3796d5-fable276 at 912345cd (branch base main 313efcca). No repository file edited; nothing under /Users/edr/night-custody touched; no launchctl or sudo. Packet read in full: records 03, 04b, 15, 22, 25, 26, 31; diffs 313efcca..912345cd and c9e2bd14..912345cd. Everything below marked EXECUTED was run in this session; anything I could not run is marked NOT EXECUTED.

## Executed baseline

```
python3 -B -m unittest tests.test_evidence_night            -> Ran 131 tests in 587.108s  OK   (rc=0)
python3 -B -m unittest tests.test_quiet_predicate_campaign  -> Ran 156 tests in 26.815s   OK   (rc=0)
python3 -B -m unittest -k corecaptured_t0 tests.test_night_gate -> Ran 5 tests  OK
render_notice(state built exactly as NoticeProtocolTextTests.state) -> 31-line notice, printed below in Q3
registration sha256 69321c69... == night_gate.QPE01_PILOT_REGISTRATION_SHA256 -> True
```

The two named modules were run as two separate invocations (macOS has no `timeout`; the single combined command would have exceeded my per-command cap). 131 + 156 = 287, matching the delta re-audit's V1 count.

## Q1. F1, F2, F3: confirm or refute, then the dictated closure

### F1: CONFIRMED (false generated text)

Rendered line 12 says the arm check is "the checks run when the night is installed". EXECUTED reading of the lifecycle order in joulewise/evidence_night.py:

- `check()` (line 1082) writes `lifecycle/check.json`; its busy-core predicate is `machine_quiet_check` at line 1144, which imports the gate's `non_observer_offender` and bar (lines 839-871), so this IS the notice's "arm check" for the 0.5-core rule.
- `notice()` (line 1282) calls `require_fresh_check(state, launchctl_bin, command="notice")` at line 1286 BEFORE rendering: the check must already exist when the notice Ed receives is produced.
- `publish_install()` (line 1445) calls `require_fresh_check` at line 1451 and refuses at lines 1460-1466 unless `notice.txt` exists and is newer than `check.json`; only then does it publish `night_plan.json` and install.

So the checks run before the notice and before installation. The gloss inverts the order. The wording was dictated by the fix brief (record 25, X3), so the seat reproduced a brief-authored falsehood; the re-audit's F1 stands.

DICTATED CLOSURE F1. Replace, in joulewise/evidence_night.py `render_notice`, the fragment

    refuses the night at the arm check (the checks run when the night is installed) or at t0, the scheduled start.

with, verbatim,

    refuses the night at the arm check (the pre-arm checks run before this notice is sent and before the night is installed) or at t0, the scheduled start.

so that rendered line 12 reads in full:

    A process outside the measurement apparatus (the night's own measurement processes) at or above 0.5 busy cores refuses the night at the arm check (the pre-arm checks run before this notice is sent and before the night is installed) or at t0, the scheduled start.

Test site: tests/test_evidence_night.py, `NoticeProtocolTextTests.test_v3_notice_states_bound_schedule_and_all_refusal_rules`, the `assertIn` that currently carries "(the checks run when the night is installed)" takes the new sentence verbatim (the f-string keeps `{protocol["t0_non_observer_share_max"]:g}`). No other test asserts the old gloss (the lifecycle test at line ~2263 asserts only the substring "at or above 0.5 busy cores refuses the night", which is unchanged).

### F2: CONFIRMED (unpinned data meaning of a pinned sentence)

EXECUTED. `tests/test_quiet_predicate_campaign.py:106` calls `campaign.pilot_summary(root, protocol, [])` with zero envelopes, so the label is asserted against `None J` and the computation at joulewise/quiet_predicate_campaign.py:1344 is never exercised with an excluded envelope. In a /tmp copy of joulewise/, tests/, configs/ and scripts/ I mutated line 1344 to drop excluded envelopes:

```
1344:    unfiltered = [v["joules"] for v in values if v["joules"] is not None and not v.get("excluded")]
---- existing label test on MUTANT:
Ran 1 test in 0.162s
OK                                   <- SURVIVES
---- proposed test (below) on MUTANT:
AssertionError: unfiltered SD 0.0 != stdev over every readable envelope 0.5773502691896257   <- KILLED
---- proposed test on ORIGINAL 912345cd:
retained 11 excluded[1] ['census_not_clean_or_unknown'] unfiltered SD 0.5773502691896257 expected(all 12) 0.5773502691896257
PASS
```

Whole-module run on the mutant: NOT EXECUTED by me (my probe chain aborted on a zsh `PIPESTATUS` error after the two results above); the delta re-audit reports all 156 pass on an equivalent mutant, and nothing I read contradicts that.

DICTATED CLOSURE F2. Add to `CampaignTests` in tests/test_quiet_predicate_campaign.py, using the existing `summarize` helper (twelve envelopes, envelope 2 excluded by `census_clean = False`):

```python
    def test_unfiltered_sd_label_is_computed_over_every_readable_envelope(self):
        # The label at quiet_predicate_campaign.pilot_summary promises "every
        # envelope with a readable energy value, excluded envelopes included";
        # this binds the NUMBER to that promise.  Envelope 2 is excluded and
        # carries the only 12 J value: a retained-only computation gives 0.0 J,
        # the promised computation gives the sample SD over all twelve.
        energies = [10, 12, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        report = self.summarize(energies, excluded=(2,))
        self.assertEqual(report['retained'], 11)
        self.assertEqual(report['envelopes'][1]['excluded'], ['census_not_clean_or_unknown'])
        self.assertAlmostEqual(report['unfiltered_single_envelope_sd_j'], 0.5773502691896257, places=12)
```

The literal 0.5773502691896257 is `statistics.stdev(energies)` over all twelve values (EXECUTED above); the retained-only value is 0.0, so the test fails on the mutant and passes on 912345cd. The label text itself stays pinned by the existing `test_summary_text_follows_registration_exclusion_rule`; summary.md prints the same `report['unfiltered_single_envelope_sd_j']` variable (line 1438), so label and number share one source.

### F3: CONFIRMED (overclaim, pre-existing from round 1, carried as a nit)

EXECUTED reading of joulewise/night_gate.py:1509-1526: the `/usr/bin/log show --last 10m` read runs inside `try`; on `ProbeError`/`ValueError` the gate records `rows["C3"].measured["corecaptured"] = {"status": "not_measured", ...}` and falls through; the refusal `spawns.count > corecaptured_loop.SPAWNS_MAX` (SPAWNS_MAX = 2, corecaptured_loop.py:13) is reached only in the `else` branch after a successful read. EXECUTED: `tests.test_night_gate.EvidenceRegistrationTests.test_corecaptured_t0_log_failure_is_recorded_without_refusal` passes (receipt.refusal is None, status not_measured). Rendered line 14 promises refusal unconditionally.

DICTATED CLOSURE F3. Replace rendered line 14

    At t0, the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes.

with, verbatim,

    At t0 the gate reads launchd's log for the previous ten minutes; when that read succeeds, the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes. When the log cannot be read, the count is recorded as not measured and the night continues.

The mandated clause "the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes" is contained verbatim. Test sites (two): tests/test_evidence_night.py `test_v3_notice_states_bound_schedule_and_all_refusal_rules` (the `assertIn` of the old line 14) and `PrepareTests` (the `assertIn(... first["notice_draft"])` of the same old sentence, currently near line 368) both take the new text verbatim. Enforcing lines for the new second sentence: night_gate.py:1519-1521 (not_measured) and the fall-through to `_check_machine` at 1531 onward.

## Q2. Structural: mechanical cure in scope, or follow-up lane?

Twice the false text was AUTHORED BY THE BRIEF, not invented by the seat: round 1's brief specified the corecaptured clause as mandatory verbatim (record 03 §2a), and the fix brief specified the "installed" gloss verbatim (record 25 X3). The review layer detected both (Opus lens record 22 flagged the corecaptured overclaim in round 1; the delta caught F1); the defect is that dictated wording is exempt from the seat's own line-citation duty and gets carried as a "nit" because it is mandated.

There is no mechanical in-lane cure: a gloss about process ORDER ("before install") is not derivable from a constant, and a test can only pin the string, not its truth (all 33 mutants and the F2 mutant show exactly this: pinned strings, unpinned meaning). Within this lane the cure is the three dictated closures plus the F2 test, nothing more.

Follow-up lane (small, process, not code): a brief-writing rule for generated owner-facing prose. Briefs name the TERM to gloss and the enforcing symbol; the seat writes the gloss from the code and cites file:line for every clause (the seat report's evidence table already has this shape for numbers). Any wording a brief mandates verbatim must arrive with its own enforcing line in the brief, or the seat is instructed to qualify it and report the conflict rather than reproduce it. Route: a follow-up lane, because it edits doctrine and brief templates, which are outside this lane's WRITE_SCOPE and outside what this judge may edit.

## Q3. Every sentence of the rendered v3 notice, checked

EXECUTED render (`render_notice` on the state built exactly as `NoticeProtocolTextTests.state`, registration = `night_gate.QPE01_PILOT_REGISTRATION_PATH` = pilot_protocol_v3.json):

```
01| DRAFT — NOT SENT; prerequisites and veto observations are not yet recorded.
02| To: claude2.glaring610@passmail.net
03| Subject: NIGHT NOTICE — fixture (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1
04|
05| Ed,
06| Launch needs no action from you unless you reply NO. Your NO overrides.
07| Arm attempt 1; prior candidates for this date: none.
08| This idle-variance evidence night sizes a later experiment; it activates no new quietness cutoff.
09| After 600 seconds settling, twelve 600-second idle envelopes start 620 seconds apart and use 480-second interiors after 60-second offsets.
10| Power sampling is every 100 ms, with census, AC-power, thermal, timing and cleanup observations and a journal of busy cores (the average number of CPU cores a process kept busy).
11| The 8,020-second program fits inside the 9,000-second window; no top-up or automatic repeat.
12| A process outside the measurement apparatus (the night's own measurement processes) at or above 0.5 busy cores refuses the night at the arm check (the checks run when the night is installed) or at t0, the scheduled start.
13| A process outside the measurement apparatus using 30 or more core-seconds (busy cores multiplied by seconds) inside an envelope excludes that envelope. Two such exclusions in a row end the night.
14| At t0, the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes.
15| During the night, read-only git show checks run in the measurement clone; successful results publication commits and pushes them from a separate results clone.
16| Partial observations and refusals are kept. No model, load generator, calibration-ledger session or measurement pack runs.
17| The scheduler supervises the program and the courier emails the result. Evidence remains PROVISIONAL.
18| After delivery the lead sizes block two or records 'no cutoff qualifies'.
19-27| plan_id / H / clone / custody / runs / staged plan / authored_epoch_s / registration sha256 / chain sha256 (state echoes)
28| No-objection opens only on mail service acceptance of the exact notice. Publication follows acceptance with no additional minimum waiting interval.
29| Every observed NO stops publication, including older threads. Reply NO on the thread or through an owner-authored directive; no reply is required.
30| The magistrate checks readable NO/directive/stop channels before publication and exits before REQUEST.
31| Keep agent applications closed and the machine untouched from REQUEST through completion, longer if the night remains active.
```

FALSE or MISLEADING (with enforcing line):

1. Line 12, "(the checks run when the night is installed)": FALSE. evidence_night.py:1286 (check required before notice), :1451 and :1460-1466 (check and notice required before publish-install installs). Closure F1.
2. Line 14, unconditional refusal: MISLEADING. night_gate.py:1519-1521 records not_measured and continues when the log read fails; refusal only at :1523-1526 after a successful read. Closure F3.

TRUE, verified this session against registration/code:

- Line 9: settle_s 600, envelopes 12 ("twelve" via count_word), envelope_s 600, slot_pitch_s 620, interior_s 480, interior_offset_s 60: all read from pilot_protocol_v3.json (fields present; registration sha matches the gate's current digest).
- Line 10: power_interval_ms 100 (registration); census/AC/thermal/clock/cleanup are the named exclusions in the registration's `exclusions` list; busy-cores journal = `recorder_journal` "evidence_busy_cores.jsonl". The gloss "average number of CPU cores a process kept busy" matches the registration's per-process `busy_cores * interval_s` statistic.
- Line 11: span 600 + 11*620 + 600 = 8,020 computed in render_notice from the registration and refused if > window_max_s 9000 (evidence_night.py:293-297); top_up false in the registration and at quiet_predicate_campaign.py:1386/1538. "no automatic repeat" refers to the program inside the window; note (not a defect, unchanged meaning from the base text) that joulewise/arm_retry.py does license a NEW-plan successor for some zero-capture refusals, which a reader could confuse with "repeat". Leave as is.
- Line 12 remainder: `non_observer_offender` uses `>=` T0_NON_OBSERVER_SHARE_MAX (night_gate.py:846-851); the arm side imports the same predicate (evidence_night.py:839-871, called at :1144); the t0 side is `_check_machine` from `evaluate_night` (night_gate.py:1772). Observer identity = `consumer["observer"]` (night_gate.py:841-842), the registration's `observer` clause.
- Line 13: bar_core_seconds 30 and abort_after_consecutive 2 read from the registration; enforcing comparisons at quiet_predicate_campaign.py:1024 (`>=`) and :1643-1645 were reported by three prior reviews (records 15, 22, 31) and are quoted in the appendix below, which I executed at write time.
- Line 15: `tracked_bytes` runs `/usr/bin/git -C root show HEAD:name` (quiet_predicate_campaign.py:94-96) for the eight MANIFEST_PATHS (:83-85) and again for the recorder subprocess (:1528); `_durable_record` (scripts/run_night.py:1056-1120) clones `custody_root/results-clone` when absent, then `checkout -B`, `commit`, `push` there, best effort, hence "successful". TRUE. (The clone step is a fetch when results-clone is absent; the sentence does not deny it.)
- Lines 8, 16-18, 28-31: unchanged policy text from the base notice; consistent with receipt_class DIAGNOSTIC_NO_PACK, load_generator false, `courier` = `claude` on PATH (evidence_night.py:1117). Not re-derived beyond this reading; outside the lane's change set.

## Q4. MERGE-AFTER-DICTATED-CLOSURES

Reasons:

1. The remaining defects are three sentences and one missing test. None touches a computed value, a gate, or a sealed artefact; the production diff of this lane in quiet_predicate_campaign.py is one label string, and in evidence_night.py the H-side registration checks were verified by the re-audit's mutants (5/5 killed) and by the full named modules, which I re-ran green at 912345cd (131 + 156 OK).
2. Each closure is dictated to the character here, with its test sites named, so a mechanical check can confirm landing: grep the three dictated strings in joulewise/evidence_night.py and tests/test_evidence_night.py (F1 once in production, once in the text test; F3 once in production, twice in tests), the F2 test method in tests/test_quiet_predicate_campaign.py, then `python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign` green. The F2 test's kill of the retained-only mutant is already executed in this ruling, so it need not be repeated.
3. A third full review round would spend a consult's worth of tokens to re-read text this ruling has already read sentence by sentence against the code (Q3). Another round is warranted only if the closures land in any wording other than the dictated one.

Conditions (mechanical, all must hold): dictated strings landed verbatim; no other production line changed; named modules pass.

## Appendix: enforcing lines quoted at write time (EXECUTED)
```
--- quiet_predicate_campaign.py 1017-1026
                continue
            identity = (consumer["pid"], consumer.get("start_identity"))
            totals[identity] = totals.get(identity, 0.0) + consumer["busy_cores"] * interval_s
            names[identity] = consumer["command"]
    hits = [{"process": os.path.basename(names[identity]), "pid": identity[0],
             "start_identity": identity[1], "core_seconds": total,
             "bar_core_seconds": rule["bar_core_seconds"]}
            for identity, total in totals.items() if total >= rule["bar_core_seconds"]]
    return sorted(hits, key=lambda hit: (-hit["core_seconds"], hit["pid"]))

--- quiet_predicate_campaign.py 1640-1646
            consecutive_cleanup_failures = 0 if cleanup["cleanup_proven"] else consecutive_cleanup_failures + 1
            if consecutive_cleanup_failures >= 2:
                raise ValueError("two consecutive cleanup_unproven envelopes")
            consecutive_non_observer = consecutive_non_observer + 1 if non_observer else 0
            rule = non_observer_rule(protocol)
            if rule is not None and consecutive_non_observer >= rule["abort_after_consecutive"]:
                raise NonObserverAbort(
--- night_gate.py 190
# the registration's `non_observer_process_busy` integral.  The bar is a GATE
# predicate, not a registration field, so it binds v2 and v3 plans alike.
T0_NON_OBSERVER_SHARE_MAX = 0.5
NON_OBSERVER_OBSERVATION_INTERVAL_S = 30
--- git status (judge worktree unchanged)
## HEAD (no branch)
```
