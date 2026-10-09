CONTAMINATION DISCLOSURE: before this charge the session had auto-loaded the global and project CLAUDE.md files and the one-line memory index MEMORY.md (pointers naming block-5 checkpoints and process rules, no content of any window). I opened no RUN_STATE.md, no decision log, no docs/orchestration.md, no other process doctrine, no restricted file, and ran no program over a closed file. No energy, power, duration or member name of any claim window reached this session.

# Cold ruling: block 5, ALPHA attempt 1, the next arm

Judge: Fable 5.1, cold, read-only, single session. Working tree: detached worktree at 7e6158d669cbb6fb35761aee18abf363f07c5d36 (the harvest program's commit; `git rev-parse HEAD`).

Read, in order: the brief (`BRIEF-body.md`), seat 1 (`sol-consult.md`, body complete; its JSON header is a report envelope and is not part of the findings), seat 2 (`opus-consult.md`). Sources then read: `configs/campaigns/v5_claim_25g83/registration_block5.md` sections 0.2, 0.8, 0.9, 2, 4.1 to 4.5, 5.3, 6.4 to 6.9, 7, 8, 10, 14; `analysis_plan_block5.md` sections 2.1, 2.2 and the §8.1 attempt-history line; `flag_catalog.json` (rules, every code's family, effect and blinding); `joulewise/b5/harvest.py` lines 85 to 96, 1886 to 1925, 2601 to 2602, 3185 to 3228, 3730 to 3790, 4500 to 4615, 5335 to 5445, 6340 to 6395, 7790 to 7862; `joulewise/flags/exclusions.py` 195 to 406; `joulewise/hazards/contention.py` 300 to 425; `joulewise/b5/chain.py` 226 to 240 and 802 to 845; `40-magistrate-brief.md` sections 6, 9, 10. Open evidence read: the contention journal (structure: process names, CPU shares, counts), `hazards/arm.json` (decision, reasons, unmeasured), `night/hazard_result.json` (`neg8_corpus` counts, `yield` key names). Nothing else was opened.

Probes executed (all foreground, all read-only): the journal recount below; a grep of the registration, analysis plan and the window-executing code for `launchctl`, `LaunchAgents`, `mediaanalysis`, `corespotlight`, `spotlight`, `print-disabled`; a tally of the catalog by (family, effect, blinding). NOT EXECUTED: any command on live machine state (I did not repeat the magistrate's `launchctl` checks; they are taken as the charge states them), and anything over a restricted file.

Journal recount (my own program, `contention.jsonl`): 1,978 lines = 1 `session_start`, 1 `snapshot`, 1,975 `interval`, 1 `session_end`; 183 of 1,975 intervals carry an `outside_over_limit` entry above 0.05 CPU-s/s; intervals containing `mediaanalysisd` 77 (sole offender in 72), `corespotlightd` 51 (sole in 43), `fseventsd` 14 (sole in 12), `PerfPowerService` 13, `runningboardd` 10, `mobileassetd` 10, `deleted` 9, `mds` 7. Both seats' headline tallies are confirmed. `arm.json`: decision GO, reasons empty, unmeasured empty. `hazard_result.json` `neg8_corpus`: 12 listed, 10 kept.

---

## Q1. The next arm

**Ruling:** (b), step 1 only: boot out the two already-disabled agents, record it, then arm ALPHA attempt 2 from the same sealed clone; step 4 (a new persistent `launchctl disable` of `corespotlightd`) is not authorized now and goes to the owner as a question that does not gate the arm. Precondition from Q2: the family count runs first; it diverts the arm only in the one case named there.

**Reasons.**

1. *Better science.* The registered contention rule exists because "another process's CPU work during a request adds energy that would be attributed to the model" (registration §4.2, Contention, forcing problem). The harvest applies it as: any outside process other than `kernel_task` above 0.05 CPU-s/s in any 10 s interval that overlaps the request flags the member (`harvest.py:3208-3224`, `CONTENTION_EXEMPT` at 319, closed-interval `_overlaps` at 2601-2602; registration §6.4 lines 2349-2351). In ALPHA-1, 9.3% of intervals were dirty and one process, `mediaanalysisd`, accounts for 77 of the 183 dirty intervals, 72 of them alone. The magistrate's verification shows that process is a launchd agent someone already disabled (`print-disabled` lists it) that is still loaded and running as the same pid the journal saw (98055). An arm "unchanged" (seat 1's (a)) would knowingly run a second window against a measured, named, removable contaminant whose removal was already intended and merely never completed. Removing a contaminant that the registered rule would exclude anyway cannot bias a kept number; it only changes how many members survive. Widening the limit instead (route (c)) would admit the contaminant; seat 2 is right that the limit is not shown wrong by this journal and that the remedy is to remove the contender, not to raise the limit. Seat 1's reason for (a), "no demonstrated specific effective cure", is answered by the magistrate's `launchctl` finding, which seat 1 did not have: the cure is specific (two named services), the mechanism of its earlier failure is known (disabled after load, never booted out), and its taking is checkable before the arm.

2. *Compatible with the sealed registration.* A `launchctl bootout` of a gui-domain agent changes no file a window reads. The window reads the measurement clone's code, `configs/` and the plan; the harvest compares executed files with the sealed inventory and the clone (`code.executed_differs_from_sealed`, registration §6.5). The grep of the registration, the analysis plan, `joulewise/b5/*.py`, `joulewise/hazards/*.py`, `joulewise/whole_window.py`, `joulewise/flags/*.py` and `scripts/run_night.py` finds no reader of launchd state or of `/System/Library/LaunchAgents`; the only `~/Library/LaunchAgents` comparison is the driver's own refusal test (registration line 1148) and the desk dry arm (line 1003), and a system agent's disable state does not live there. No registered threshold, catalog effect, minimum or roster changes, so §10 (prospective cold erratum) is not triggered and §7.5 (collection code) is not touched. What the three analysed windows must share is "one acceptance, one macOS build and one collection head" (§7.5, lines 2857-2862); the set of background services is not in that list, and the registration already directs a machine-state removal of a contender before a re-arm without an erratum: §7.2's NULL row, "re-arm after the named hazard is gone (a contention dwell timeout: identify the process; …)", and the magistrate brief §6 NULL row ("A competing process: name it from the arm record. A leftover of ours: kill it. `fseventsd`: run the restart helper … then arm"). Booting out a disabled agent is a cure of exactly that kind, applied one row earlier in the table. No erratum and no owner gate is required for step 1: the persistent setting (disable) already exists on the machine; bootout only makes it effective in the current login session, and the existing disable prevents a re-bootstrap at the next login.

3. *No bias, no selection on an outcome (registration §7.6).* The decision reads process names and CPU shares (the journal is structure) and the four permitted records; it reads no energy. ALPHA-1 is re-armed either way (§7.2: a pack is re-armed until claim-usable) and is never analysed (analysis plan §2.1), so nothing about its numbers can be selected into or out of a claim. The cure can change only which members of ALPHA-2 carry `contention.request_overlap`; it cannot change the rule, the threshold, or any kept member's value. Its direction is one-sided and disclosed: fewer contaminated members, not more kept contaminated members.

4. *Comparability of the three analysed windows.* ALPHA-2 (or later), BETA-1 and GAMMA-1 will all run in the cured state if the state is checked before each arm. The check before every remaining arm, from the desk, no sudo: `launchctl print gui/501/com.apple.mediaanalysisd` and `launchctl print gui/501/com.apple.photoanalysisd` both fail with "Could not find service"; `pgrep -x mediaanalysisd` and `pgrep -x photoanalysisd` print nothing; `launchctl print-disabled gui/501` still lists both as disabled. Seat 2's "repeat after 10 minutes" is sound because the agent launches on demand. After each harvest, the same structural tally run on the window's own journal (dirty intervals and offender names, integers and names only) is written beside the attempt in the records note, so a drift of machine condition between the analysed windows is visible and disclosed in the attempt history (analysis plan §8.1, "every attempt of every pack with its verdict, cause key, flag counts by family and yield status").

5. *Why not step 4 now.* (i) It is a new persistent operating-system setting on the owner's machine with effects beyond measurement (Spotlight search), and seat 2 itself has not verified that clients do not respawn or spin against a missing service. (ii) The evidence is weaker: 51 intervals, and seat 2's own tally places 37 of 51 in the lowest quartile of measurement-tree CPU, so most probably fall outside requests. (iii) It is not needed to make the arm lawful or the window comparable; a persistent contender above 0.05 still refuses the arm dwell (§4.2) and the member rule still excludes it. Route: ask the owner in the arm notice (one word answers it); do not wait for the answer to arm. If ALPHA-2's journal still shows `corespotlightd` as the leading offender and a cell is lost again, that is the §7.3 same-cause consult, and step 4 with the owner's yes, or the Q3 erratum of registration §14, is decided there.

6. *If the bootout is refused.* Do not reboot or log out to get it (seat 2's step 3): its effect on §2's preconditions, the ledger, the uptime-dependent state and network time was not assessed by any seat or by me. Record the refusal, arm unchanged (seat 1's (a) is then the fallback), and send the owner the question with the exact error.

7. *What is recorded and disclosed.* In the records-branch note and the arm notice: the two commands, their exit status, the three check outputs before and after (service names, "Could not find service", pid presence as yes/no), the time, and the sentence "machine state changed between ALPHA attempt 1 and attempt 2: two launchd agents already disabled were booted out; no file a window reads, no threshold, no catalog effect changed." The same sentence goes into the attempt history under ALPHA-1's cause key (analysis plan §8.1). No energy, no member name, no error text from a restricted file.

**Checked:** registration lines 1168-1430 (§4.1-4.5), 2233-2360 (§6.4), 2359-2570 (§6.5-6.9), 2774-2900 (§7, §8), 3031-3054 (§10), 1140-1152, 3289-3300 (§14 Q3); magistrate brief lines 711-860 (§6), 906-1100 (§9, §10); `harvest.py` 319, 2601-2602, 3185-3228; the grep named above; the journal recount; `arm.json` decision.

---

## Q2. The count

**Ruling:** Neither seat's program may run. A narrower program, written below, may run once, by the magistrate, before the arm; its output (family names and integers only) may be written into the records note and the arm notice.

**Why the seats' programs may not run.** Seat 2's prints, per cell index, the kept count per stratum, the minimum, `resolvable`, and the dropped-unit codes: that names which reported quantity lost which units for which reason code, which is more than the cause key needs and is a count of flags by reason code, which the magistrate brief §10 forbids in records. Seat 1's prints per cell and per stratum, and opens `derived/flags.jsonl` and `derived/neg8-corpus-physics.json` as well; neither is needed (the corpus question is settled without them, Q3 item 2).

**Why a family-level count is permitted.** (i) The sealed registration requires it: §7.3 (lines 2835-2838) defines the cause key of a `cell.below_minimum` attempt as "the families of the member exclusions that removed the units", and the next arm's anti-spiral rule compares that key between attempts. Those families exist only in `derived/exclusions.json` (`members_excluded[].families`, `cells[].dropped_units[].codes`; `exclusions.py:376-406`). Without a program over that file the registration's cause key for this attempt cannot be formed. (ii) The registration releases it: §8 item 2 lists "flag counts by code and family" among what every record may release during the block; the analysis plan §8.1 prints "flag counts by family" for every attempt. (iii) SG-12's reason for closing the file is that it names codes "member by member"; a family total with no cell, stratum, unit, position or member identity carries none of that. (iv) Decision O-7 narrowed the custody map on purpose; this ruling narrows it back by exactly one program with a fixed output shape, and only because §7.3 cannot otherwise be applied. The brief §10 rule (no count by reason code in records) is kept: the program prints families, not codes.

**Why it cannot leak an energy.** `exclusions.json` holds no energy, power or duration of anything: its members carry `run_id`, `position`, `codes`, `families`; its cells carry unit ids, counts and codes (`exclusions.py:350-406`). The only member-excluding code whose presence is derived from a science energy is `member.anchor_energy_envelope_exceeded` (catalog: MEMBER_VALIDITY, EXCLUDE_MEMBER, blinding RESTRICTED; every other EXCLUDE_MEMBER code is STRUCTURE). Registration §8 item 2 says a member removed by a RESTRICTED code is released as "removed (restricted code)" without the code; the program below therefore counts a member or unit whose only member-excluding codes are RESTRICTED under the label `restricted`, never under its family, and never prints that code's name. The remaining families say that a process ran, a battery charged, a clock stepped, a bundle was missing or malformed: facts about the machine and the records, not about a measured energy.

**Why it cannot let the re-arm select on the science outcome.** ALPHA has no claim-usable attempt, so it is re-armed whatever the count says (§7.2); the count decides only whether the machine-state cure addresses the cause, and whether a non-physics cause needs its own consult first. No threshold, catalog effect or minimum may change on its account without a cold erratum (§10). ALPHA-1's numbers enter no analysis (analysis plan §2.1). The decision therefore reads reason-code families and integers, which §7.6 and brief §6 permit, and never an energy.

**The program.** Run once, from the desk, with the interpreter the brief's END STATE program uses, as `python3 -I`; copy its output verbatim into the records note. It opens `derived/exclusions.json` and the sealed catalog (not restricted) and prints family names and integers only.

```python
import json, collections
ARCHIVE = "/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261008T2201Z"
CATALOG = "/Users/edr/code/JouleWise/configs/campaigns/v5_claim_25g83/flag_catalog.json"
cat = json.load(open(CATALOG))["codes"]
ex = json.load(open(ARCHIVE + "/derived/exclusions.json"))

def families(codes):
    """Families of the STRUCTURE member-excluding codes among `codes`; `restricted` if none."""
    fams = {cat[c]["family"] for c in codes
            if c in cat and cat[c]["effect"] == "EXCLUDE_MEMBER" and cat[c]["blinding"] == "STRUCTURE"}
    return sorted(fams) or ["restricted"]

members = ex.get("members_excluded", [])
by_family = collections.Counter(f for m in members for f in families(m.get("codes", [])))
print("excluded_members_total", len(members))
for fam, n in sorted(by_family.items()):
    print("excluded_members_by_family", fam, n)

units = [u for c in ex.get("cells", []) if c.get("target") for u in c.get("dropped_units", [])]
unit_family = collections.Counter(f for u in units for f in families(u.get("codes", [])))
print("dropped_target_units_total", len(units))
for fam, n in sorted(unit_family.items()):
    print("dropped_target_units_by_family", fam, n)
print("target_cells_below_minimum", sum(1 for c in ex.get("cells", []) if c.get("target") and not c.get("resolvable")))
```

Output lines are of the form `<label> [<FAMILY>] <integer>`. All of them may go into the records note and the arm notice. Nothing else from the file may be printed, and the file is not otherwise opened.

**How the output is used.** The cause key of ALPHA-1 is `cell.below_minimum` with the families printed under `dropped_target_units_by_family`, plus `neg8.bound_not_derived` with family PHYSICS_IN_SPAN (Q3 item 2 shows this without any file). Then:

- If PHYSICS_IN_SPAN is the leading family of dropped target units (ties included), step 1 then arm, as Q1 rules.
- If a family other than PHYSICS_IN_SPAN alone leads, the cure of Q1 is still done (it is harmless and already intended) but the arm does not proceed on it: the leading family's cause is one the next window would meet again and the cure does not touch it. If that family is MEMBER_VALIDITY, suspect a harvest-side validity predicate (the harvest yield reports `strict_deferred` 119, that is, strict validation of every member deferred to harvest, so a deterministic strict-validation failure is the one non-physics mechanism that could remove five or more units of one stratum from 114 succeeded members): route it as a harvest investigation under brief §9 (R3), re-harvest on identical bytes if a defect is found, and only then decide the arm. Any other leading family goes to a consult on that family (brief §6 rule 1 shape).

**Does Q1 stand without the count?** The cure itself does: the journal alone justifies step 1, and step 1 changes nothing registered. The arm after the cure is what the count protects, because registration §7.3 needs the cause key for the next comparison in any case, and a non-physics cause would make a second unchanged window a probable repeat. The count costs seconds; run it.

**Checked:** `exclusions.py` 195-406 (what the file holds and how units are dropped); `harvest.py` 7790-7862 (what `harvest.json` and `window_flags.json` hold; `harvest.json` has no family counts, so the count cannot come from a permitted key); catalog tally (one RESTRICTED code, named above); registration §7.3 lines 2835-2838, §8 item 2, §7.6; analysis plan §2.1 and §8.1 line 470; brief §6 and §10.

---

## Q3. Errors that could bear on the next arm

1. **Seat 2's threshold arithmetic is off by one; seat 1's is right.** Seat 2: "Reaching fewer than 5 of 10 needs at least four more units of one stratum removed." With 9 kept after the one run-time loss, four more leaves 5, and 5 ≥ 5 is resolvable (`exclusions.py:347`, `len(kept[s]) >= minimum[s]`). At least five further units of one stratum must have been removed at harvest (kept ≤ 4). Seat 1 states this correctly. It does not change the arm; it slightly strengthens the point that the harvest-time losses were large, which is why the Q2 count matters.

2. **Seat 2's claim that the physics path emitted `neg8.bound_not_derived` is correct, and it settles more than seat 2 drew from it.** `neg8_corpus_physics` returns before writing anything when the first path derived no bound (`harvest.py:5362`, `check.get("derived_from") is None`) and again when no corpus member of the bound carries a code in `NEG8_PHYSICS_LOSS_CODES` (`5373`, `if not flagged: return`); after those returns it always writes `derived/neg8-corpus-physics.json` (`5433`). The first emitter fires only when `derived_from` is None (`4607`); the second runs only when it is not. So the two emitters are mutually exclusive and the file's existence (an existence test, permitted by the passage) proves: the bound was derived by the first path, and at least one of its members carried one of the six physics codes. With 10 members kept (`hazard_result.json` `neg8_corpus.members_kept`, an open file) and at least one flagged, `len(kept) < 10` is certain, so `clean_members_below_minimum` is in the problems list (`5405`) whatever else happened; no file needs opening to know it. All six codes in `NEG8_PHYSICS_LOSS_CODES` (`harvest.py:91-93`) are family PHYSICS_IN_SPAN (catalog tally), so the family of the corpus loss is known without opening anything: seat 1's third program block over `flags.jsonl` is unnecessary. What is not known, and cannot be known blind, is which of the six codes it was.

3. **"One flagged quad member removes the whole quad" is correct.** The roster attaches every member of a quad with the same `unit_id`, the quad's `block_id` (`harvest.py:1900-1902`; GAMMA contrasts `1911`), and the exclusion function drops a unit when the union of its members' member-excluding codes is non-empty (`exclusions.py:332-347`). Registration §6.6 says the same in words. Both seats have it right.

4. **"The corpus has no spare at all" (the procedure row, repeated by seat 1) is imprecise but changes nothing.** The chain runs one retry of the corpus stage when fewer than 10 of 12 succeeded (`chain.py:226-236`, `NEG8_RETRY_MINIMUM = 10`; the helper at 802-845 prints `no_retry` at 10 or more). At exactly 10 succeeded, as in ALPHA-1, no retry ran and the bound sat with zero margin against a harvest-time physics drop. Seat 2 reads this correctly. Changing the retry rule is collection code (§7.5); it is not for this arm.

5. **Seat 2's reading of the contention rule is correct**, including that the monitor's "exited over limit" imputation (`contention.py:377-385`, included in `outside_over_limit` at 415-416, read by `harvest.py:3185-3203`) counts as an offender; it touched 2 intervals and nothing turns on it.

6. **Seat 1 is right that the permitted evidence cannot join dirty intervals to the lost units**, and right to refuse a numeric window-failure probability. Seat 2's tables are explicitly parametric in an assumed request length and should be read as a sufficiency argument, not a measurement. Neither changes the ruling: the cure is justified by the identity and persistence of the contender, not by the probability tables.

7. **Seat 2's step 3 (logout or reboot as a fallback) is not authorized**, see Q1 item 6.

8. **Neither seat found a harvest defect, and I found none** in the paths read (`neg8_bound`, `neg8_corpus_physics`, `contention_member_flags`, `exclusions.compute`): the minimum applied is the catalog's 5 (`flag_catalog.json` `rules.cell_unit_minimum`; `exclusions.py:306`), the registration's §6.6 prose still says 8 and is the stale text, as both seats note.

---

**Standing order of operations for the magistrate, from this ruling:** (1) run the Q2 program once, copy its output into the records note; (2) `launchctl bootout gui/501/com.apple.mediaanalysisd` and `launchctl bootout gui/501/com.apple.photoanalysisd`; (3) the three checks of Q1 item 4, repeated after 10 minutes; (4) if PHYSICS_IN_SPAN leads the dropped-unit families, write the record and the arm notice (with the owner's corespotlightd question, not gating) and arm ALPHA attempt 2 from the same clone; otherwise follow the Q2 branch; (5) before BETA-1 and GAMMA-1, the same three checks; after every harvest, the journal tally beside the attempt.

RULING: CURE-STEP-1-THEN-ARM
