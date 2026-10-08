# Seal gate of measurement block 5, stage 2: the ruling (part A, then part B)

## What this file is

The **seal gate** is the independent judgment that precedes the seal of measurement block 5: a model session that
took no part in writing or reviewing the block's rules reads them cold and rules on them. It ran in two stages.
Stage 1 ruled on an earlier revision and required changes (`RULING_STAGE1.md` beside this file). **Stage 2** judged
the final text, in two parts, because the text can be judged before the seal's commits exist and the digests and
the commits only afterwards:

- **Part A** read the final text of the registration, the analysis plan and the flag catalog before the head
  commit existed. Its ruling ends with the session's close at 2026-10-08 00:05 PDT, and its first line is
  `STAGE 2A: TEXT ADMITTED WITH REQUIRED CHANGES`.
- **Part B** is a later session, held once the head commit (H_claim), the sealed inventory and the seal commit
  existed. It computes the digests again, checks the seal's commits against the registered procedure, and ends
  the gate with one line, `SEAL: ADMIT` or `SEAL: REFUSE`, which it writes as the first line of its ruling.

Both judges were Fable 5.1 sessions (model id `claude-fable-5-1`), each a new session, and neither took part in
stage 1. The sealed registration (section 12) names this one file as the record of both parts.

Each part stands below under its own heading, byte for byte as its judge wrote it: nothing was reworded, re-wrapped
or corrected. The two marker lines around each part are not the judge's; they exist so that the copy can be checked.
The source files are `/Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE2A.md` and `RULING_STAGE2B.md`
beside it, which are outside the repository. To check a part against the digest in its opening marker line:

```
awk '/^<!-- BEGIN-BYTES RULING_STAGE2A.md /{f=1;next} /^<!-- END-BYTES RULING_STAGE2A.md -->$/{f=0} f' RULING_STAGE2.md | shasum -a 256
```

(and the same with `RULING_STAGE2B.md` in both patterns for part B).

## Part A. The final text (judge: Fable 5.1; ruling closed 2026-10-08 00:05 PDT)

<!-- BEGIN-BYTES RULING_STAGE2A.md sha256=0f2303a3cc5c836e1d157a72f7bf055b3fd0c35d1c1608a5dd114725ba34d4f9 bytes=51988 -->
STAGE 2A: TEXT ADMITTED WITH REQUIRED CHANGES

# Seal cold gate V5-CLAIM-25G83-B5, stage 2, part A: ruling on the final text

Judge: Fable 5.1 (claude-fable-5-1), new session, 2026-10-07. Charge: `/Users/edr/night-archive/gate-prune/wave-1007b/seal-gate/STAGE2A_DISPATCH.md`.

## 0. Contamination disclosure (written before any other file was opened)

What was in this session's context before the charge, supplied by the harness and not by the charge:

- `~/.claude/CLAUDE.md` (Ed's global rules: the multi-model playbook names and the 2026-08-19 writing standard).
- `/Users/edr/code/JouleWise/CLAUDE.md` (the Codex bridge notes: MCP path, reverse path, audited CLI path, the bridge-protocol pointer).
- `/Users/edr/code/JouleWise/CLAUDE.local.md` (Ed's private orchestration doctrine of 2026-09-29 with the 2026-10-05 "physics refuses; everything else is a flag" section and the 2026-10-06 "old rules don't bind" item). This overlaps the doctrine file the charge names (`REVIEW_BRIEF_RULE.md`), which I have not yet opened; I will apply the charge's file as written and note any difference between the two.
- The auto-memory index `MEMORY.md` for this project: about 120 one-line entries. The ones that bear on this gate: the 2026-10-07 checkpoint line ("seal prep PAUSED ... int5 fe28e5a0c verified; reg rev 9 draft; nothing armed"), the 10-05 doctrine line, the "check the physics, not the proxy" line, the "PR bodies can break blindness" line, and the "paper threat = hallucination, not forgery" line. None of these entries contain text of the registration, the plan or the catalog, and none contain any stage-1 finding. I have not opened any of the memory files behind the index lines.
- The git status snapshot of `/Users/edr/code/JouleWise` at session start (branch `main`, head `e0c738e9c`, PR #484 merged; one untracked `CLAUDE.local.md.bak-20261002T153934`).
- The system reminder that commits from this session carry a Claude Fable 5.1 attribution line (irrelevant: this session writes no commit).

Whether this session took part in writing or reviewing the documents or the code: no. This session began with the charge. It has not read or written the registration, the analysis plan, the flag catalog, the harvest code, the stage-1 ruling, the refuter's report, the fidelity sweep, the seal-landing records, or any pull request body. The memory index line "int5 fe28e5a0c verified" was written by some earlier session of this model family; I treat it as hearsay and will verify the integration head named in the charge (`cc0b3446d4...`) myself.

What I already believe about this project, from the context above and from nothing else:

- JouleWise is Ed's undergraduate capstone on mechanism-level energy profiling on a dedicated 128 GB M3 Max MacBook Pro with a KM003C wall meter; the advisor is Rivoire.
- Unattended measurement windows are scheduled by a launchd job (`com.joulewise.night`), held today by a remote ref `ops/stop-pause`; a pre-registration, analysis plan and flag catalog are sealed before block-5 windows run.
- Ed's doctrine: only a directly measured physical hazard refuses arming or t0; every other condition is a recorded flag, and the analysis plan names which flags exclude a window from a claim. Rules are past judgments about physics, not constraints; a worse rule is never kept because "the existing rule says".
- The paper's threat model is hallucination by the agents writing it, not forgery: every printed number is recomputed from preserved sources.
- I have no belief about the content of any stage-1 ruling, about what revisions 9 to 12 changed, about the cell minimum, the guard factors, the attribution floor, or the 192 catalog codes. Every number below is recomputed in this session.

Bias I can name: the context I was given is Ed's and the orchestrator's, so it predisposes me toward the doctrine "flag, not refuse". The charge tells me to apply that doctrine, not reopen it, so the predisposition and the charge coincide; where I find a sentence that refuses on something other than a measured physical hazard or a number-integrity condition I will say so as a finding, and where the doctrine would require a flag that the code refuses I will say that too.

Scratch directory for this session: `/private/tmp/sealgate-stage2a/`. Every probe runs in the foreground of this one session; no subagent, no background task. No write to any repository.

## Trust anchors (EXECUTED, 2026-10-07 about 23:55 PDT)

- `git -C /Users/edr/code/JouleWise-wt-ia-claim show c7408819c7c695bca077f5b697942d931b61e477:<path>` for the three files, piped to `shasum -a 256`:
  registration `d2ac89cd…c3b91`, plan `453a5db8…c2c6b`, catalog `5d77c725…1ee8d`. All three equal the charge's table. The commit is
  "Block-5 registration revision 12: the late items and the name-valued markers", 2026-10-07 23:45:46 -0700, and is the HEAD of
  `design/2026-10-05-v5-claim-block-draft` in that worktree.
- Revision 9 at `9b0c680ed79d5c7b72b4b39ed04b9fe51dd116d4` ("D-165 rationale allowlist …", 15:20:32 -0700): registration 3,492 lines,
  plan 807 lines, catalog 1,359 lines. Revision 12: registration 6,165 lines, plan 999 lines, catalog 1,359 lines (digests
  `12ac5c78…`, `9f0ad06b…`, `2b1595e4…` for revision 9).
- Integration worktree `/Users/edr/code/JouleWise-wt-int5` HEAD `cc0b3446d428024c0e4a0f22cf9dadf18ada2ede` ("Merge lane/2026-10-07-seal-rulings
  (a0920cb8c) into int5", 22:23:10 -0700), `git status --short` empty. Harvest worktree `/Users/edr/code/JouleWise-wt-harvest` HEAD
  `c10257418a9d7d2173bec306c0b1deb38e144343` ("Harvest H-13 …", 22:47:19 -0700), status empty.
- Doctrine read: `/Users/edr/night-archive/gate-prune/REVIEW_BRIEF_RULE.md` (the paragraph "Physics refuses; everything else is a
  flag"). It agrees with the section of the same name in the `CLAUDE.local.md` that was in my context; the charge's file is the one
  applied below.

Working copies of the six files are under `/private/tmp/sealgate-stage2a/` (`r9_*`, `r12_*`); every count below was taken on those
copies, whose digests are the ones above.

## A. The 48 rulings (EXECUTED by script, then every miss read)

Method. `/private/tmp/sealgate-stage2a/parse_t.py` parses each `T-n. <where>. Old: `…` New: `…`` block out of `RULING_STAGE1.md`
(48 found, T-1 to T-48, none missing, none duplicated). `check_t.py` then counts, with runs of whitespace collapsed to one space, (1) the
old text in revision 9, (2) the new text in revision 12, (3) the old text in revision 12, and (4) the new text byte-for-byte in
revision 12. Every old block occurs exactly once in revision 9 (48 of 48), which validates the parse against the stage-1 judge's own
once-check.

Result. **44 of 48 pass by script**: new text present once, byte-exact, old text absent (T-1 to T-22, T-24 to T-26, T-28 to T-31,
T-33 to T-39, T-41 to T-48). Four were read by hand:

- **T-23** (registration §0.16, now lines 1394-1399). New text present once, byte-exact. The script reports the old text as still
  present because the old text is a strict prefix of the new (the ruling appended two sentences). Not a miss. PASS.
- **T-27** (registration §0.12, now lines 1040-1045; a merge). The ruling's new text is present byte-exact from "not decode, or one
  with no string status); its energy cannot be read although it succeeded …" through "… which decides nothing by itself); it fails
  the strict check (". The ruling's tail "(below; at harvest" was replaced by a gloss that names where the strict check is built
  ("built in \"The strict check of a reference\" below; at harvest the flag is `member.strict_validation_failed`, and the reason
  is `strict_invalid` in the **verdict writer** … and in its **replay** …"). The loss `energy_unreadable`, its causes, the six
  harvest codes and the sentence that the harvest decides the loss all survive whole. The merged tail changes no rule: it names the
  flag and reason the writer and replay already use. PASS (merge sound).
- **T-32** (registration §8 item 2, now lines 4651-4660; a merge). Present byte-exact up to "no chain or campaign logs, no runs-root
  files."; the last sentence "`FILL[B5-BLIND-CUSTODY-MAP]` lists the restricted paths, these three files among them." became "The
  custody map at the end of this section (`B5-BLIND-CUSTODY-MAP`) lists the restricted paths, these three files among them." The
  marker was filled in revision 12, and the map's row at line 4702 reads "`<archive root>/derived/flags.jsonl`,
  `derived/exclusions.json` and `derived/window_flags.json` | the flags and the exclusions by code, the RESTRICTED codes included
  (item 2)". The ruling survives whole and its promise about the map is kept. PASS (merge sound).
- **T-40** (registration §7.5, now lines 4594-4601; a merge). Present byte-exact from "**Collection code** is any file …" through
  "… so all three windows must share one acceptance, one macOS build and"; the ruling's close "one collection head for the code
  they executed." became "the same collection code: no collection-code file that a completed window executed may differ, byte for
  byte, in the commit a later window runs." The ruling's own new text says the measurement checkout's HEAD moves by pin-only
  commits during the block, so "one collection head" could not be read literally; the merged close states the condition the
  harvest's head comparison and the sealed inventory actually test (bytes of executed files), which is the condition stage 1
  ruled in SG-8 step 1. The ruling survives whole; the close is classed in part D (it is the seal-landing procedure's statement,
  class (iii)). PASS (merge sound; see D for the by-bytes condition against `head_change_class`).

The charge names T-21 among the reported merges; its new text is present byte-exact once, so the reviser's merge there was a
no-op on the ruling. **A: all 48 rulings are present; the three merges keep each ruling whole.**

## C. The four orchestrator rulings made after stage 1, and the two disagreements (confirm or overturn)

### C.1 Section 7.3's cause key (reviser's cure for V-1). CONFIRMED, with one clause required for two-reader sameness.

Read: registration §7.3 and §7.6 at revision 12 (lines 4528-4563, 4629-4642), the same section at revision 9 (which keyed a
`cell.below_minimum` attempt "by the families of the member exclusions that removed the units"), the reviser's return in the
workflow journal (option (b), its stated cost), §8 item 2 (T-32) and the custody map (line 4702). Code (int5 `cc0b3446d`, READ):
`joulewise/b5/harvest.py:7454` writes `exclude_window_reasons` into `harvest.json` from the exclusion summary's `reasons`, and
no member-exclusion code is written there; `joulewise/b5/driver.py:2076, 2646` write `flags_emitted=list(window.flags)` into the
driver's terminal record. §8's custody table (line 3428) lists `harvest.json` as releasable and the three `derived/` files as
restricted.

- *Sound.* The key is built from the arm record (hazard modules that refused), `harvest.json`'s `exclude_window_reasons` with the
  catalog's families, and the driver's `flags_emitted`. Every input exists in a released record at the time the rule is applied.
  The cost the reviser states is real and is in the safe direction: two consecutive `cell.below_minimum` attempts go to a consult
  whatever removed their units, and a LOW with a shared cause that never ran three members in a row no longer holds the next arm.
  A consult costs a conversation; it stops no collection and changes no number.
- *Blind.* None of the three inputs is a science energy. The window-removing codes name reference-workload drift, identity,
  calibration and roster conditions; `claim_usable` reads no science energy except the RESTRICTED precheck ratio, which §7.6
  states. The rule keeps T-32's "only in-block reader" true as written, which is why option (b) was right: option (a) would have
  added a second reader of the restricted files and contradicted stage 1's T-32 sentence.
- *Same for two readers, with one clause missing.* §7.3 says the key is "the families of its window-removing codes", then "An
  attempt removed by `cell.below_minimum` is keyed by that code", then "When two consecutive attempts of the same pack share a
  cause key family". `cell.below_minimum` belongs to the catalog family ROSTER (§6.2 table), beside `roster.duplicate_run_id`
  and `roster.no_science_bundles`. Reader 1 keys a `cell.below_minimum` attempt by the code; reader 2 by its family ROSTER. For
  the pair (attempt 1: `roster.no_science_bundles`; attempt 2: `cell.below_minimum`) reader 1 allows a third arm and reader 2
  sends the next spend to a consult. Neither direction touches a number, but the charge's test is sameness, so the clause is
  required (T-S2A-1 in section F). The cure states what the sentence already implies: the code is its own family for this rule.

### C.2 Harvest-side items H-8 to H-12. CONFIRMED as harvest-side; one note for the lane.

Read: `harvest-lane/WORKLIST.md`; registration §0.18 (lines 1554-1565), §9.1 rows (4886-4893), §11 item 2 ("What the harvest
program at H_claim does instead") and item 4 (5328-5347). Code: `joulewise/b5/harvest.py` `code_identity` (5597-5731) and
`head_change_class` (184-195) at int5; `joulewise/flags/collect.py` `head_change_class` (543-556). EXECUTED in the harvest
worktree: `git merge-base cc0b3446d c10257418` = `9395cecfb`; `git diff --name-only 9395cecfb c10257418` lists
`joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `scripts/harvest_b5_window.py` and three test files, nothing else.

- Each of H-8 to H-12 changes the harvest's head comparison or its reading of the driver-checkout record. All five are decided
  from bytes the window preserved, after the window, by the desk program. None needs a window-time file: the per-file collector
  at the arm hashes the measurement checkout's files, not a separate driver checkout's, and the arm collector's head comparison
  compares HEAD with itself (installer `night_agent_install.py:1234-1242`, READ). So none of the five moves H_claim. Correct.
- H-8 in particular: at H_claim the harvest already records `driver_checkout` with `files_differing_from_sealed` and raises no
  flag (`harvest.py:5716-5731`, READ). The lane turns a non-empty list into `code.executed_differs_from_sealed`, EXCLUDE_WINDOW.
  A window whose driver ran unsealed code is removed from every claim at the harvest; no number from it enters a claim. Refusing
  earlier (at install, "from where a checkout lives") would be a refusal on a path, which §11 item 2 rightly declines. And under
  §11 item 2 the launchd job is installed from the measurement checkout, so the field is null and the case does not arise.
  Flagging at the harvest alone is the right placement.
- Note for the lane (no change required before the seal): H-9 makes every path not on the record-only list a window input, so a
  changed `env/mac-measurement-lock.txt` after H_claim would exclude a window although cold pass 5 (C11, EXECUTED there) shows
  the lock is read by no block-5 program and the installed runtime is measured per member. That is an exclusion in the safe
  direction on a condition that is not quite number integrity; unreachable in the registered sequence (only pin-only commits
  enter the measurement checkout). I record it; it is "flag, not refuse" material for the lane after block 5, not a seal item.
- After the lane the harvest's classes differ from the arm collector's (`collect.py` is not in the lane's diff). The registration
  says so (§11 item 2: "The arm's collector is collection code and keeps H_claim's classes; … at the arm it compares HEAD with
  itself"). Part B should confirm the lane's test change (`tests/flags/test_flags_collect.py`) no longer asserts the two sites
  class every path alike, or does so with the lane's table.

### C.3 Question 14's closure on cold pass 5, item 1. SUPPORTED.

Read: cold pass 5 `REPORT.md` items 1.1-1.5 and note 5; registration §4.5 (2296-2449) and Q14 (5861-5901). Code (int5):
`scripts/run_night.py:71` `CENSUS_INTERVAL_S = 30`; `joulewise/b5/driver.py:1272-1348` `HazardCensus`: a probe with any
stdout is "positive" and returns a `Refusal` (`night_refused_agent_present`), which stops the chain; "unmeasured" is retried
then flagged `census.unmeasured` and the chain goes on.

The closure rests on three executed results of the pass: 36 of 36 table rows match the expected verdict; every real way of
starting either agent on this machine is matched by a named rule; undecidable census lines stay hits. Each is EXECUTED in the
report with its probe named. The four misses §4.5 lists are the matcher's stated limits, and the one that belongs to the rule
(a runtime that reads its program from standard input without `-`) has no instance among the installed launch shapes. The
closure is supported by that evidence. The pass's sentence in item 1.2 that an over-match "cannot cost a window that has
already started, because the census is not re-run after GO" is true of the arm's census and false of the driver's, which runs
every 30 s and stops the chain on a hit. The registration does not repeat the pass's error: §4.5 ("an arm refused at the census,
or a chain stopped in the window") and Q14 ("a refused arm, or a stopped chain whose window is not claim-usable and is armed
again") state the whole cost, and Q14 says which program and constant it read. The in-window stop is Ed's kept doctrine item
("never start or continue a [QUIET-MAC] measurement while an agent session is active"), not a rule this gate reopens. Closure
confirmed; no change.

### C.4 The attribution floor registered as a formula, no number bound (§0.10). CONFIRMED; numbers recomputed.

Read: `q5-attribution-floor/RULING.md` (its five corrections), registration §0.10 (801-935), plan §11's note (980-984). EXECUTED
by hand from the text's inputs: point energy 0.065 × 2 + 0.91 × 30 + 0.065 × 20 = 28.730 J; a_1 at the corner (start −46 ms, end
+46 ms) with d = +2 ms: start −44 ms in the 2 W record (+0.088 J), end +48 ms in the 20 W record (+0.960 J) = 1.048 J, and the
opposite choice of d gives 0.976 J, so 1.048 is the maximum; a_2 at (start +46, end −46) with d = −2 ms: −0.088 − 0.200 − 1.140 =
−1.428 J, against −1.316 J at d = +2 ms and 1.048 J at the other corner, so 1.428 J is the maximum; the approximation
0.046 × 22 + 0.002 × 18 = 1.048 J; the a10 lineage 0.024999593 × 33.1251 + 0.006074236 × 30.9333 = 0.8281 + 0.1879 = 1.0160 J,
and 0.031073829 s × 32.697 W = 1.0160 J. All agree with the text.

The five corrections: (1) the exact maximum over the four corners and the common shift is the registered quantity and the
first-order form appears only as an approximation with its condition stated (§0.10 "An approximation, and where it fails"):
present. (2) No sentence says a decode-start record "holds mostly idle power" (`grep` of both documents: none). (3) The plan's
"does not include" sentence is gone and §11 of the plan records that it was false (line 980): present. (4) No upper limit of
the operative fiducial bound is stated in either document (`grep` 67.47, 50.99, 51.97: none), so the condition does not apply.
(5) is lane L9's. Registering the formula and binding no number is right: nothing in block 5 decides on the floor, it is
printed beside four cells, and the per-member bound changed by a factor of two between a10 and block 3, so any bound number
would print a floor the instrument does not have. Confirmed; no change.

### C.5 Two places where stage 1's text and the harvest lane disagree. RULED.

EXECUTED in `/Users/edr/code/JouleWise-wt-harvest` at `c10257418` with `PYTHONDONTWRITEBYTECODE=1 python3.13 -B`, importing
`joulewise.b5.harvest` and loading the revision-12 catalog: `PRE_HARVEST_CODES` has 67 codes (19 core-writer, 11 collector,
22 driver, plus the rest); `member.token_count_mismatch` is NOT in it (it is emitted at `harvest.py:4266` by the harvest alone);
the candidates for the prefix `member.tok` are the empty set; for `calibration.capt` exactly
`calibration.capture_battery_pair_unverified`; for `model.identity_m` exactly `model.identity_mismatch`. The EXCLUDE_MEMBER
codes a pre-harvest writer can emit are four: `env.member_quiet_state_violated`, `instrument.binary_identity_unmeasured`,
`member.idle_admission_telemetry_missing`, `member.timeout` (the last in `PRE_HARVEST_CORE_CODES`, the member writer's table).
`_candidate_codes` (`harvest.py:6969-6984`, READ): `{code} if exact else {item for item in PRE_HARVEST_CODES if
item.startswith(code)}`. The malformed lines come from `inputs.flags_dir/*.jsonl` (the desk and arm collectors' and the
driver's files, `harvest.py:6896-6927`) and from the marker lines of operator logs and the desk transcript (7060-7086); the
harvest's own `derived/flags.jsonl` is written once (`write_jsonl_once`, 7813) and is never a source.

(a) T-30's third example is wrong under K-5 as ruled and as coded: a line torn inside `"code": "member.tok` has no candidate,
so it is disclosed and removes nothing. The corrected example is T-S2A-2 (section F); its replacement case uses `member.timeout`,
whose prefix `member.tim` names that code alone among the pre-harvest codes.

(b) A malformed line that still shows its whole code keeps that code as its one candidate whether or not a pre-harvest writer
emits it. The orchestrator's view is right on reachability: every file the harvest reads for malformed lines is written before
the harvest, and the test holds `PRE_HARVEST_CODES` equal to those writers' tables, so a whole harvest-only code in such a file
would be a record no writer produced. The code's direction in that case removes more, never less. Rule: the text states the
fact; the lane does not change. The sentence is T-S2A-3 (section F).

### C.6 The allowlist text `neg8.screen_failed.protects`. A corrected sentence is REQUIRED before the freeze (K-S2A-1).

Read at int5 `cc0b3446d`: `configs/gates/hazard_refusals.json` `window_exclusions["neg8.screen_failed"].protects` names the
dropped references as "physics-excluded, timed-out, aborted or strict-invalid" and says "each loss is a named physical event".
After K-4, K-6 and the N8 ruling (§0.12 lines 1037-1060 at revision 12) a reference is also lost when its energy cannot be read,
its contention or battery evidence is unmeasured, its quiet state was violated, its battery pair failed, or its model identity is
not the sealed one or cannot be derived; the last three kinds are number-integrity losses, not physical events. The file is a
window input and freezes at H_claim; stage 1 corrected two sibling entries (K-1, K-3) in the same file for the same reason while
the head was open, and the head is still open. No effect changes; the allowlist test only requires 30 characters. Required
while the head is open; if the head has been fixed before this ruling is applied, it goes to the next allowlist pass and the
registration's §0.12 remains the normative list.

## D. The landing as text (the bytes are part B's)

Read in full at revision 12: §0.18 (1471-1600), §2 (1643-1966), §11 (5017-5366), §12 (5367-5510); `seal-land/SEAL_LANDING.md`
whole. Code at int5 `cc0b3446d` (READ): `joulewise/b5/harvest.py` `head_change_class` (184-195), `code_identity` (5597-5731),
`_changed_paths` (5736-5750), the `registration_digest_differs_from_plan` fault (1414); `joulewise/flags/collect.py`
`head_change_class` (543-556) and its `WINDOW_INPUT_PREFIXES`/`SEAL_DOCUMENT_PATHS`; `tests/test_b5_seal_landing.py`
(`seal_landing_problems`, 90-125, and its nine tests); `joulewise/b5/plan.py` 285-300 (a `{path, sha256}` locator whose file
does not hash to the digest raises `WindowPlanError`) and 721 (`PinAdvanceError` "the pin commit is not pin-only");
`joulewise/night_agent_install.py` 1234-1242 (`repo_head` and `measurement_head` must equal the two checkouts' HEADs);
`scripts/collect_window_flags.py` 39-49 (`--stage {desk,arm}`, `--h-claim`, `--sealed-inventory`); `scripts/size_b5_window.py:755`
and `scripts/write_b5_identity_pins.py:615` (`--check`); `scripts/rehearse_b5_real.py:285` `sealed_inventory()` and the lane's
wrapper `seal-land/make_sealed_inventory.py` (exists, 2,205 bytes).

**Can the procedure be carried out as written?** Yes. Each of §12's eight steps names a check that exists: step 1 (suite, refusal
census, the two generators' `--check`, CI); step 2 (the generator); step 3 (`git diff --name-only --no-renames`, the landing test,
which proves from git objects exactly the three statements §11 item 2 and §2 item 3 attribute to it, and a regenerated `files`
map); step 4 (the record commit's diff lists no window input; the suite and CI at R); step 5 (merge commit); step 6 (the clone's
diff and status; the desk collectors with the flags the script accepts); step 7 (the plan writer's digest refusal, which is the
generic locator check of `plan.py` 285-300, so the sentence "the plan writer also accepts a plan input that names no
registration" is the right qualification; the installer's two HEAD checks); step 8 (the pin advance). §0.18's picture and §11's
picture agree with `SEAL_LANDING.md` §3 and with each other.

**Does any sentence promise a check the code does not make?** None found. In particular: §0.18 "the harvest makes both
comparisons" (`code_identity` does both, READ); the four classes and the case-folding (`head_change_class`, both sites, READ);
"only a `window_input` path is a difference" (READ, 5684-5687); `git_diff_unavailable` → `code.identity_unmeasured` (READ,
5679-5681); the `driver_checkout` record with `files_differing_from_sealed` and no flag at H_claim (READ, 5716-5731); the harvest
fault on a registration digest that differs from the plan's (READ, 1414); §11 item 2's "What the harvest program at H_claim does
instead" matches the code I read (the UTF-8 fault I did not reproduce; it is review F6's executed finding). §11 item 2's table
states the harvest-lane rule and says so; the sentence that the arm's collector "keeps H_claim's classes" is true because
`collect.py` is not in the lane's diff (C.2).

**T-40's merged close** ("the same collection code: no collection-code file that a completed window executed may differ, byte
for byte, in the commit a later window runs") is the by-bytes condition the two comparisons test and that §11 item 1's
extension classes are built on. Class (iii), confirmed.

**Section 12's list of pinned files** (stage 1, finding 8). At H_claim it names: the catalog; the three packs' plan trees; the
model panel `configs/model_panels/qwen3_4bit.json`; the idle policy `configs/campaign_policies/quiet_mac_p2_b5.json`; the
acceptance `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`; the pin bundle "in each pack's `prefill_pin/`
directory, nine files with three distinct digests"; `sizing_b5.json`; `identity_pins.json`; the runbook. EXECUTED at int5
`cc0b3446d`: every one of those paths exists (`git cat-file -e`, 12 of 12 including the pin and the stub). `git ls-files` of the
three claim packs: `d117_floor_qwen3-1p7b_v5/prefill_pin/` 3 files, `d117_floor_qwen3-8b_v5/prefill_pin/` 3 files,
`d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/` 3 files (`prefill-prompt-ladder.json`, `prefill_prompt_pin.json`,
`selection.json`), nine files, with SHA-256 prefixes `43a77ea9…`, `d1209f6d…`, `c694c488…` repeated across the packs: three
distinct digests. The two floor packs' six files that stage 1 found missing are now covered. (A fourth `prefill_pin/`, in
`d117_contrast_v5`, is not a claim pack and is not pinned; its three files carry the same three digests.) Everything else a window
reads from outside its pack (window references, spares, the NEG-8 corpus, the two interior-reference manifests) is pinned by the
plan trees, which are pinned. **The list is complete.**

**Markers.** The registration at `c7408819c` holds seven `FILL[…]` sites: `FILL[H-CLAIM]` at lines 1649 and 5534, and
`FILL[B5-FINAL-HASHES]` at 756 (three on one line), 2522 and 3025. Both names are the two the charge says a script fills at the
seal commit. No other marker remains in the registration, so §12 step 3's "nothing in this file is left to fill afterwards" can
be met. The plan holds the same `B5-FINAL-HASHES` marker at three sites and eleven markers of lane L9's own, which §12 says are
filled after the seal with an addendum stating the new digest.

**One fact for part B.** At int5 `cc0b3446d` the catalog's bytes are `2e45cabe…6237bc`, not the judged `5d77c725…1ee8d`: the
two agree on the rule (`cell_unit_minimum` 5) and on every code's effect, family, class and blinding (EXECUTED), and differ in
42 code notes and the top-level notes; the int5 note for `code.executed_differs_from_sealed` is the stale one cold pass 5 (note 1)
named, and the judged catalog's note is the corrected one. The int5 registration there is still revision 9's bytes. So H_claim is
not yet made; late item 5 (the catalog copy) and K-S2A-1 are the window-input changes that must precede it.

## B. Every changed rule, revision 9 to the judged text

Method (EXECUTED): `/private/tmp/sealgate-stage2a/secdiff.py` splits both revisions into sections by heading, each section into
paragraphs (blank lines and list items), normalizes whitespace, and aligns the paragraph sequences with `difflib`; a changed
paragraph is paired with its nearest old paragraph (ratio > 0.5) and printed as a word diff. Outputs
`secdiff_reg.txt` (700 KB) and `secdiff_plan.txt` (108 KB). Of the registration's 71 sections 52 changed; the plan's 26, 18.
Re-wrapped paragraphs with no text change align as equal, so the counts below are text changes.

Classes: (i) a stage-1 ruling; (ii) a correction to what the code does, confirmed by me in the code where marked READ; (iii) the
seal-landing procedure or the attribution-floor ruling; (iv) a new rule.

**Registration, the named sections (read in full as word diffs):**

- **§0.12** (+3 −1 ~10). (i) T-21, T-22, T-27, T-31, with the two-rule explainer "Where the seal gate's two rules stand in the
  code" (the harvest at `9395cecfb` holds `NEG8_REFERENCE_LOSS_CODES` without `energy_unreadable` and the four unmeasured
  losses; the lane adds them; follows from stage 1 and the harvest lane). (ii) 7 reference files and 13 spare files with 7
  distinct digests; the lost-reference rows found through `neg8_slot` (`harvest._neg8_lost_rows`); the two functions that never
  see a bundle-less reference; the evaluation basis of the verdict row (`whole_window.build_evaluation_basis`): facts of the
  code, consistent with the harvest I read, not each re-opened. Glosses: science member, the two families, structural check
  against strict validation, runs root, calibration attachment, envelope. The worked example "the seal gate's two losses on the
  same numbers" applies RF-1 and RF-5 to the section's own synthetic numbers. **No (iv).**
- **§0.18** (+19 −2 ~1). Entirely (iii): the seal-landing terms, the two comparisons, the harvest-lane's five details stated as
  such, the proof-landing worked example (682 files; 1 pin-only, 3 seal-document, 2 record-only, 0 window-input) matching
  `SEAL_LANDING.md` §8, and the reading of "H_claim plus pin-only commits". (ii) READ: `PIN_ONLY_PATHS`, `SEAL_DOCUMENT_PATHS`,
  the case fold, the `code.identity_unmeasured` fallback. **No (iv).**
- **§2** (+8 −4 ~8). Items 1, 3, 5 and the "Before ALPHA-1's harvest" paragraph are (iii) and (i); item 1's delta-pass list and
  the SHA-256 of cold pass 5, the review and the orchestrator's ruling are records (I did not recompute those three digests; part
  B may). Item 6's dry-arm paragraph adds the reasoning that the refusal holds under the merged matcher (ii, consistent with the
  matcher rule I read in §4.5 and cold pass 5's row 8). Item 7's carry-over chain to `9395cecfb` (ii, the author's `git diff`
  search; not repeated). Item 8's sync statement (ii). **No (iv).**
- **§5.7** (+6 −5 ~0). Late items 2 and 3: the driver's science minimum stays ⌈planned × 4/5⌉ (16 of 20, 8 of 10) and its
  rationale is corrected to "an earlier warning than the cell rule"; the worked example is rewritten so that 0 of 20 in one
  decode quad stage leaves 5 quads and the window claim-usable, and one more lost member in the other decode stage (4 quads)
  removes it (ii; the author's run of `exclusions.compute` at `cc0b3446d`, which I did not repeat; the rule's arithmetic is
  consistent). EXECUTED here: the trip probabilities at p = 1/37 are 1.59 × 10⁻⁴ (20-member stage) and 2.05 × 10⁻³ (10-member
  stage), as printed; 1 − (36/37)² = 0.0533, as printed. The diagnostic-stage item (1 of 1 min_valid; a LOW from one lost
  diagnostic member) is (ii) plus the orchestrator's process ruling, classed under §7.3 below. **No (iv) in the numbers.**
- **§6.5** (+5 −4 ~8). (i) T-19, T-20, T-28 and the energy-unreadable clause. (iii) `code.executed_differs_from_sealed` rewritten
  for the head comparison. (ii) READ: `clock.systematic` counts members and the two captures' anchor statuses
  (`harvest.clock_systematic`, 5505-5515: `statuses += [capture.get("anchor") …]`, minimum from the thresholds, `2 ×
  non_bounded > recorded`); `roster.duplicate_run_id` is window-level (`harvest.py:3841`); the verdict's condition strings are
  `neg8_bracket_abs_delta_exceeded` and `neg8_bracket_idle_sub_abs_delta_exceeded` (`whole_window.py:165,168`); the reserved
  `instrument.precal_screen_failed`. **No (iv).**
- **§6.6** (+2 −2 ~2). (i) T-4, T-5. **No (iv).**
- **§6.11** (+4 ~2). (i)/(ii) K-1 to K-3 and the recount; verified in E. **No (iv).**
- **§7.1** (+3 −2 ~2). (ii) READ: the harvest's own reasons `window.null` (7401), `exclusions.function_unavailable` (7413),
  `harvest.fault` (7444); NO_COLLECTION decided by the stage journal's `campaign_collection` kind (7218-7220). **No (iv).**
- **§7.2** (+2 ~3). (i) T-19, T-42. (ii) READ: `first_claim_usable` exists (`joulewise/flags/exclusions.py:417`) and no block-5
  program calls it (the text says so). "Who applies these rules" states that the lead applies them (a fact about the code; no rule
  changes). "Two more conditions for the pack collector" (ii, not re-opened). **No (iv).**
- **§7.3** (+1 ~2). The cause key (C.1, confirmed with T-S2A-1). **One (iv):** "One LOW that does not hold the next arm"
  (orchestrator ruling of 2026-10-07): a LOW yield status that comes from one lost GAMMA diagnostic member alone does not hold the
  next arm. None of the charge's records rules it; it changes what the lead does between windows. Finding B-1: it is a process
  rule, not code; it excludes no data, computes nothing, reads no energy (the diagnostic member enters no cell and no contrast,
  and the yield is counts), and it relaxes a hold that the yield status's own definition ("stops nothing and removes nothing")
  never justified for a one-member stage whose chance trip rate is 5.3%. It is the orchestrator's call under the doctrine
  ("everything else is the orchestrator's call, recorded"), and it is recorded here with its reasoning. **Accepted as written; no
  change.** Part B need not revisit it.
- **§7.4** (+2 ~1). (ii) the count includes captures and names the two inputs; READ above. **No (iv).**
- **§7.5** (+3 −2). (i) T-40; (iii) the reading of the chain C → S → pin-only. **No (iv).**
- **§7.6** (~1). Follows from V-1: the list of what the rules read. **No (iv).**
- **§8** (+23 −1 ~2). (i) T-32. The custody map, filled in revision 12 before the seal commit (so it is sealed text, which is
  allowed; only values that arise after S go to the record), with the "Who may read" paragraph following V-1. The map's rows
  are facts of paths (ii, sampled: the three `derived/` files, `harvest.json` releasable). **No (iv).**
- **§11** (+59 −3 ~1), **§12** (+25 −1). (iii) throughout; read in full in D. §11 item 3's correction of what the import-graph
  test proves (ii, not re-opened; it narrows a claim, in the honest direction). **No (iv).**
- **§14** (+8 −2 ~4). Q5 (C.4), Q6 (T-36), Q9, Q11, Q12, Q13 (T-43) closures: (i)/(iii). Q14 (C.3). Q15 is a new open item,
  not a rule. **No (iv).**

**Registration, sampled sections:** §0.10 (+18; C.4, all (iii)); §4.5 (+31; the census rule as merged, revision 10's text
extended with the worked table and the limits; (ii), cold pass 5's 36 rows); §6.2 (+7 −2 ~4; T-29, T-30 and the narrowed-list
paragraph, (i); the reserved codes, (ii)); §6.7 (+11; roster facts, (ii), not re-opened); §9.1 (+21; the delta record of cold pass
5 and the review, records); §13 (+29 −4 ~12; the binding register's rows for the fills; records); §16 (+22; what the author
read). None of the sampled paragraphs changes an exclusion, a claim-usability condition, a computation, a read before release
or the scheduler. The header (+70) is the revision list and the status line.

**Analysis plan:** §2.2 T-7, T-44 (i); §2.4 T-24, T-25 (i) and a gloss on the interior references; §4 T-8 (i), step 4's bound B
rewritten per Q5 (iii; READ `reduce.py:114` `ANCHOR_SHIFT_METHOD = "common_trace_shift_plus_independent_edge_corners_v3"` and
`max_abs_delta_j` at 2142, 2268) and step 7 the attribution floor (iii), plus two digests that went stale replaced by
`FILL[B5-FINAL-HASHES]` (fact); §7.1 T-10, T-45 (i) and the P-14 glossary of step 2, the quantiles for n = 7, 6, 5 (i, consistent
with T-8); §7.2 T-46 (i) and the L2-ceiling condition expanded to the engine's own terms (ii; READ `claims.py:124-125, 212-213,
389`: `outcome_dependent_top_up`, `legacy_l1_mechanics_only`, `evidence_class == "legacy_l1"`; the clause "one top-up demotes
both contrasts" I did not trace); §8.1 T-11, T-33, T-35, T-47, T-48 (i), `<module>.arm_unmeasured` and the battery-temperature
readings per member (ii, not re-opened); §8.2 the per-member `meter.battery_activity` against the window-level `meter.*` codes
(ii, not re-opened). **No (iv) in the plan.**

**B result: one class-(iv) sentence (B-1, §7.3), accepted; every other change is (i), (ii) or (iii).**

## E. Numbers (EXECUTED, `/private/tmp/sealgate-stage2a/numbers.py`; Student-t quantiles by my own incomplete-beta routine)

- t(0.975, df): 9 → 2.262157162798; 8 → 2.306004135204; 7 → 2.364624251593; 6 → 2.446911851; 5 → 2.570581836; 4 → 2.776445105.
  All equal the plan's (T-8: the first three to fifteen places, the last three to nine).
- Guard g(n) = √(9/(n − 1)) (`detection_floor.small_sample_guard_factor`, READ: 1.0 at n ≥ 10, undefined below `GUARD_MINIMUM_N`):
  1.1339, 1.2247, 1.3416, 1.5 at n = 8, 7, 6, 5. Equal to T-9 and §6.6.
- Half-width factor t(0.975, n − 1)/t(0.975, 9) × √(10/n): 1.169, 1.293, 1.467, 1.736 at n = 8, 7, 6, 5. Equal to T-5/§6.6.
  The old "≈ 17%" at 8 recomputes as 0.169.
- Planning table P(m, p) = keep(p)² × keep(1 − (1 − p)⁴)² with keep(q) = Σ_{k≥m} C(10,k)(1 − q)^k q^(10−k): at p = 1/37:
  0.849, 0.971, 0.996, 1.000; p = 0.05: 0.508, 0.814, 0.952, 0.991; p = 0.08: 0.169, 0.474, 0.767, 0.929 (m = 8, 7, 6, 5).
  Repeat loss 0.027 and quad loss 0.104 at 1/37. (36/37)¹¹⁹ = 0.038 ("≈ 0.04"). All equal T-5/§6.6.
- Plan §7.2 worked example (T-46), quad 4 removed: n = 9, dbar = 3.0000, s_d = 0.19365, se = 0.064550, h = 2.306 × se = 0.1489,
  interval [2.8511, 3.1489]; with D = 0.05 J, [2.8011, 3.1989]; t = 46.5; leave-one-out shift ≤ 0.0375 J. All equal the text.
- Plan §8.1 worked example (T-47), quads 3 and 4 removed: n = 8, dbar = 2.9625, s_d = 0.16850, se = 0.059574, h = 2.365 × se =
  0.1409, interval [2.8216, 3.1034]. Equal. (The old interval with se_met 0.035355, [2.7987, 3.1263], is gone.)
- §6.11 against `configs/gates/hazard_refusals.json` at int5 `cc0b3446d`: sites by category, entries/sites: PHYSICS 30/31,
  NUMBER_INTEGRITY 35/58, INTERNAL 91/117, BASELINE 2,593/3,663, DEFERRED_REPRESENTATION 0/0; 2,749 entries, 3,869 sites;
  `scan.modules` 93 (91 `.py`, `scripts/backup_runs.sh`, `docs/phase_2/window_runbook.md`); `window_exclusions` 33 (29
  NUMBER_INTEGRITY, 4 PHYSICS, none BASELINE; `g3.recompute_failed` absent); `member_exclusions` 40 (20/16/4, the four BASELINE
  being the four the text names); every non-BASELINE entry's `protects` ≥ 30 characters; the two quoted `protects` texts equal the
  file's. The catalog's 32 EXCLUDE_WINDOW codes equal the 33 entries less `neg8.midpoint_lost_primary`, and its 40 EXCLUDE_MEMBER
  codes equal `member_exclusions` (symmetric differences empty). All equal §6.11.
- The catalog: revision 12 against revision 9: 192 codes, the same set; `rules.cell_unit_minimum` 8 → 5 (C-1); effect, family,
  class and blinding identical for every code; 42 notes changed (text only); effects 120 DISCLOSE / 40 EXCLUDE_MEMBER / 32
  EXCLUDE_WINDOW. Against int5's catalog at `cc0b3446d`: rule 5 and every code's four fields identical; 42 notes and the top-level
  notes differ (D, last paragraph). **The catalog is admitted as it is** (digest `5d77c725…1ee8d`), and it is the file that must
  be in H_claim.

## F. Required changes (the orchestrator applies each verbatim)

| # | Kind | Where | Old text (exact) | New text (exact) |
|---|---|---|---|---|
| T-S2A-1 | T | registration §7.3, line 4534 of `c7408819c` (the anchor occurs once) | `` `cell.below_minimum` is keyed by that code. Which member exclusions`` | `` `cell.below_minimum` is keyed by that code, which counts as a family of its own for this rule. Which member exclusions`` |
| T-S2A-2 | T | registration §6.2, lines 3455-3457 (T-30's third example; the anchor occurs once) | `A line that still shows a member's run id and is torn inside `"code": "member.tok` could only` ⏎ `  have been `member.token_count_mismatch` (EXCLUDE_MEMBER), so that member is removed (candidate lists computed from` ⏎ `  the catalog and the writers' code tables).` | `A line that still shows a member's run id and is torn inside `"code": "member.tok` names no candidate: the only` ⏎ `  catalog code with that prefix, `member.token_count_mismatch` (EXCLUDE_MEMBER), is emitted by the harvest alone, which` ⏎ `  derives it again from the preserved bytes, so the line is disclosed and removes nothing. A line that still shows a` ⏎ `  member's run id and is torn inside `"code": "member.tim` could only have been the member writer's `member.timeout`` ⏎ `  (EXCLUDE_MEMBER; `harvest.PRE_HARVEST_CORE_CODES`), so that member is removed (candidate lists computed from the` ⏎ `  catalog and the writers' code tables, `harvest.PRE_HARVEST_CODES` at the harvest lane's head `c10257418`).` |
| T-S2A-3 | T | registration §6.2, line 3445 (the anchor occurs once) | `so a damaged line cannot have lost it. If any candidate is an` | `so a damaged line cannot have lost it. A line that is malformed but still shows its whole code has that code as its` ⏎ `  only candidate, whether or not a program writing before the harvest emits it (`harvest._candidate_codes`); no such` ⏎ `  program emits a harvest-only code, so a whole harvest-only code in a file written before the harvest would be a record` ⏎ `  no writer produced, and the rule still excludes on what the line shows, in the direction that removes more, never` ⏎ `  less. If any candidate is an` |
| K-S2A-1 | K | `configs/gates/hazard_refusals.json`, `window_exclusions["neg8.screen_failed"].protects` (a window input; before H_claim) | `the NEG-8 drift screen failed for the window; since the NEG-8 survivors ruling (2026-10-07, registration 0.12) the screen runs on the surviving references (physics-excluded, timed-out, aborted or strict-invalid references dropped before aggregation, against bound(n_s, n_e) and any clean corpus bound), and it fails when fewer than two references survive at an endpoint (references_insufficient: each loss is a named physical event) or when that re-screen cannot run, since the stored screen then still holds a contaminated energy` | `the NEG-8 drift screen failed for the window; since the NEG-8 survivors ruling (2026-10-07, registration 0.12) the screen runs on the surviving references (a reference dropped before aggregation is one registration 0.12 calls lost: bundle absent, not succeeded, summary or energy unreadable, strict-invalid, physics-excluded in its span, contention or battery evidence unmeasured, quiet state violated, battery pair failed, or model identity not the sealed one or underivable; the seal gate's stage 1 added the losses after strict-invalid), against bound(n_s, n_e) and any clean corpus bound), and it fails when fewer than two references survive at an endpoint (references_insufficient: each loss is a named physical event or a number-integrity condition) or when that re-screen cannot run, since the stored screen then still holds a contaminated energy` |

(⏎ marks the line breaks of the file; the two-space indents are the file's. The three T items change the registration only; the
plan needs no change. K-S2A-1 changes no category, no effect and no site; `tests/hazards/test_refusal_allowlist.py` must stay
green on it.)

Not required, recorded: the H-9 over-inclusion of the environment lock (C.2, for the harvest lane after block 5); the harvest
and arm collector's head-comparison classes differing after the lane (C.2, part B confirms the lane's test).

## G. What part B must check at the seal commit

1. **Digests.** The three seal documents at S. The registration differs from `d2ac89cd…c3b91` (`c7408819c`) only by the three
   changes of section F and the filled markers: `H-CLAIM` at two sites (lines 1649, 5534 of `c7408819c`) and `B5-FINAL-HASHES` at
   five sites (756 ×3, 2522, 3025); no other byte. The plan differs from `453a5db8…c2c6b` only by `B5-FINAL-HASHES` at three
   sites and nothing else (no section-F change touches the plan). The catalog at H_claim and at S is byte-for-byte
   `5d77c725…1ee8d` (int5 at `cc0b3446d` still holds `2e45cabe…6237bc`; late item 5). No `FILL[` remains in the registration at S;
   the plan's eleven lane-L9 markers remain by design.
2. **H_claim.** `git diff --name-only cc0b3446d <H_claim>` lists the catalog, `configs/gates/hazard_refusals.json` (K-S2A-1) and,
   if anything else, nothing under `joulewise/` or `scripts/`; if a path there did change, §2 item 1 requires a delta cold pass
   before the seal. The four pinned estimator files unchanged. The inventory's `head` = H_claim; `files` count = `git ls-files`
   under the five roots + 1 (682 at `9395cecfb`); `status` `SEALED`; no `roots` key; the ledger pin absent from `files`.
3. **The seal commit.** Only parent H_claim; `git diff --name-only --no-renames H_claim S` = exactly the three seal documents;
   `python -m unittest tests.test_b5_seal_landing` passes at S; the generator run on a clean checkout of S yields the same
   `files` map; the generator used is named in the record (`seal-land/make_sealed_inventory.py` wrapping
   `scripts/rehearse_b5_real.py` `sealed_inventory`).
4. **The record commit.** Child of S; adds `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` (and `RULING_STAGE1.md`,
   `REFUTER_STAGE1.md`, `RULING_STAGE2.md` as §12 names them); carries the `tests/fixtures/d165_rationale_allowlist.json` line
   update if the plan's "physical-common-time" sentence moved (late item 4); `git diff --name-only --no-renames S R` lists no
   window input; the whole suite and CI green at R; the pull request merged with a merge commit.
5. **The seal record's digests** recomputable from H_claim: the catalog; the three plan trees; `qwen3_4bit.json`;
   `quiet_mac_p2_b5.json`; the acceptance; the nine `prefill_pin/` files (three distinct digests `43a77ea9…`, `d1209f6d…`,
   `c694c488…`); `sizing_b5.json`; `identity_pins.json`; `docs/phase_2/window_runbook.md`; and at S the three seal documents.
6. **The measurement clone.** Full clone at S; `git diff --name-only --no-renames H_claim HEAD` = the three seal documents;
   `git status --porcelain` empty; `scripts/collect_window_flags.py --stage desk --h-claim <H_claim> --sealed-inventory
   <clone>/configs/campaigns/v5_claim_25g83/sealed_inventory.json` raises no `code.*` flag for each pack.
7. **The harvest lane** (before ALPHA-1's harvest, not before the seal): its branch rebased or merged onto H_claim lands in a
   desk checkout only; `git diff --name-only H_claim..<lane head>` lists only `joulewise/b5/harvest.py`, `joulewise/whole_window.py`,
   `scripts/harvest_b5_window.py`, tests and fixtures; its tests include the RF-1, RF-3 and RF-5 synthetic windows the WORKLIST
   names; the lane's `tests/flags/test_flags_collect.py` change no longer asserts the two `head_change_class` functions agree on
   every path (or asserts the lane's table); the addendum names its files, digests and commit.
8. **Records.** The SHA-256s §2 item 1 prints for cold pass 5 (`46446fa4…`), the review (`fec2dc44…`) and the orchestrator's
   ruling (`92ba27dc…`) recomputed from the files; the repository copies of `RULING_STAGE1.md` and `REFUTER_STAGE1.md` equal the
   night-archive originals.

## H. For the project's owner, in plain words

Before the three measurement windows run, four documents fix the rules: what is measured, how the numbers are computed, which
recorded conditions throw data out, and the exact bytes of every file a window may run. An earlier judge (stage 1) read revision
9 of those documents and required 48 text changes, one catalog change and seven code changes. This session, a new judge that
took no part in any of it, checked revision 12, the text about to be sealed.

What was found: all 48 text changes are present as the first judge wrote them; the three places where a writer merged a change
with other edits keep the ruling whole. The catalog is correct and is admitted unchanged: 192 codes, the same effects as before,
and the cell minimum at 5. Every number the rulings changed (the cell minimum's planning table, the t quantiles, the guard
factors, the two worked intervals, the counts of the refusal allowlist) was recomputed here and agrees. The orchestrator's four
rulings made after stage 1 (how the lead decides not to re-arm on unchanged code; the five harvest-side checks; the census rule's
limits; the attribution floor as a formula) are each confirmed. Reading the whole text against revision 9, one sentence is a
genuinely new rule (a LOW yield caused by one lost diagnostic member on GAMMA no longer holds the next arm); it is a sensible
process rule that touches no data and is accepted.

What must change, four small things: one clause so that two readers key a "too few units" attempt the same way; one worked
example in the catalog section that said a torn record line removes a member when, under the first judge's own rule as now
coded, it only discloses; one sentence stating that a damaged line still showing a whole code is judged by that code; and one
description in the refusal allowlist that still lists only four of the ten ways a drift-check reference can be lost. None of
them changes which data are kept or which numbers are computed. After these, the text is the text stage 1 ruled plus only
corrections of fact and the consequences of rulings already made. Part B, a later session, checks the digests and the commits
once the seal commit exists, and writes the seal line.

Session end: 2026-10-08 00:05 PDT (`date`, EXECUTED). Every probe ran in the foreground; no subagent, no background task; nothing written in
any repository (`git status --short` empty in the three worktrees at the end); scratch under `/private/tmp/sealgate-stage2a/`
only (`parse_t.py`, `check_t.py`, `T_items.json`, `numbers.py`, `secdiff.py`, `secdiff_*.txt`, the six document copies, the two
catalog and allowlist copies). NOT EXECUTED: the exclusion-function runs of §5.7 (the author's), the UTF-8 fault of review F6, the
digests of the three records in §2 item 1 (for part B), the engine's "one top-up demotes both contrasts" clause.
<!-- END-BYTES RULING_STAGE2A.md -->

## Part B. The digests and the seal's commits (judge: Fable 5.1; 2026-10-08)

<!-- BEGIN-BYTES RULING_STAGE2B.md sha256=b7250e8bf5b3819e2577ec91e171a0b56f8d92b3888022856981a610d9cde33b bytes=34157 -->
SEAL: ADMIT

# Seal cold gate V5-CLAIM-25G83-B5, stage 2 part B: ruling (judge: Fable 5.1, model id claude-fable-5-1)

Session: https://claude.ai/code/session_01GCKeyKsbZhvoR1uzehCqqy. Date 2026-10-08. Ruling written as the checks are
made; each check is appended in the order it was run.

## 0. Contamination disclosure (written before opening anything else)

At the moment this section is written, the judge's context holds exactly the following and nothing more:

1. The charge, `/Users/edr/night-archive/gate-prune/wave-1007b/seal-gate/STAGE2B_DISPATCH.md`, read in full
   (110 lines, including the "Two facts added at dispatch" section).
2. Files the harness injects into every session in this repository, which the judge did not choose and had not
   opened before: `/Users/edr/.claude/CLAUDE.md` (global rules and the writing standard),
   `/Users/edr/code/JouleWise/CLAUDE.md` (bridge notes), `/Users/edr/code/JouleWise/CLAUDE.local.md` (the
   orchestration doctrine of 2026-09-29 and the "physics refuses" section of 2026-10-05), and the memory index
   `/Users/edr/.claude/projects/-Users-edr-code-JouleWise/memory/MEMORY.md`. The memory index is a list of titles with
   one-line summaries; the entries that touch this gate's subject say only "Checkpoint 2026-10-07 seal prep PAUSED ...
   int5 fe28e5a0c verified; reg rev 9 draft; nothing armed" and "Physics refuses doctrine 10-05 ... seat stopped at
   integration a0a4f5a7". No memory file behind the index was opened. None of these files names any digest, any
   commit of this gate, or any content of the four documents.
3. A harness snapshot of `git status` for `/Users/edr/code/JouleWise` (branch `main` at `e0c738e9c`, PR #484 merged;
   one untracked backup file). No content of any commit.
4. The judge's own model identity and the session attribution lines.

The judge took no part in stage 1, in stage 2 part A, in writing the registration, the analysis plan, the flag
catalog, the sealed inventory, the fill, the seal commit, or any review of them, and has not read
`RULING_STAGE2A.md`, the seal documents, any PR body, or anything under a `withheld/` directory. Those of the
stage's files the charge directs the judge to read (`RULING_STAGE2A.md` section F and G, the fill notes
`reg-final-b/fill/NOTES.md`, `SEAL_LANDING.md`) are opened only after this section, and are listed below as they are
opened.

Orders acknowledged: one session, every probe in the foreground, no subagent, no background task; read-only on every
repository (no fetch, pull, checkout, commit, stash, worktree in any repository; the scratch clone under
`/private/tmp/sealgate-stage2b/` is the only place anything is checked out or run); no sudo, launchctl, systemsetup,
powermetrics, pmset; nothing armed; no mail; no network request carrying a name or address; interpreter
`/opt/homebrew/bin/python3.13 -B`.

## 1. Files opened, in order

1. `/Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE2A.md` (whole; 476 lines; sections F and G are the
   ones acted on; its first line is `STAGE 2A: TEXT ADMITTED WITH REQUIRED CHANGES`).
2. `/Users/edr/night-archive/gate-prune/wave-1007b/reg-final-b/fill/NOTES.md` (the fill agent's sites, commands and
   values; 90 lines).
3. `/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/SEAL_LANDING.md` (the procedure; 291 lines).
4. Git objects of `/Users/edr/code/JouleWise-wt-int5` by `git show`/`git diff`/`git rev-list` only, and the scratch
   clone `/private/tmp/sealgate-stage2b/clone` (made by `git clone` of that worktree, checked out detached at the seal
   commit; `git rev-parse HEAD` there = `ab7b21e576a2d74f0b25d9a26b463d6934588368`).

No PR body, no `withheld/` directory, no memory file, no stage-1 ruling, no refuter record.

## 2. The landing's shape (EXECUTED first, because every later check depends on it)

Commands, all against `/Users/edr/code/JouleWise-wt-int5` (read-only):

- `git rev-parse HEAD` = `ab7b21e576a2d74f0b25d9a26b463d6934588368`, branch `integrate/2026-10-07-int5`. The worktree's
  HEAD is the seal commit, as the dispatch says.
- `git rev-list --parents -n1 ab7b21e5…` = `ab7b21e5… a64000884…`: ONE parent, and it is H_claim. **G.3 parent: PASS.**
- `git show --stat` of the seal commit: subject "Block 5 seal commit: the sealed inventory, the registration and the
  analysis plan"; three files changed.
- `git diff --name-status a64000884 ab7b21e5` = `M configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`,
  `M configs/campaigns/v5_claim_25g83/registration_block5.md`, `M configs/campaigns/v5_claim_25g83/sealed_inventory.json`.
  Exactly the three seal documents, all modifications (no add, delete or rename). **G.3 diff shape: PASS.**
- `git diff --name-status cc0b3446d a64000884` (the integration head part A saw → H_claim), 13 paths:
  `configs/campaigns/v5_claim_25g83/flag_catalog.json`, `configs/gates/hazard_refusals.json`, four under `docs/`
  (`docs/orchestration.md`, `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`, `docs/process/MAGISTRATE_WATCHDOG.md`,
  `docs/process/NIGHT_HANDBACK.md`), seven under `tests/` (`tests/fixture_signatures.json`,
  `tests/test_fixture_orphan_census.py`, `tests/test_g10_clock_step_control.py`, `tests/test_harvest_b5_window.py`,
  `tests/test_night_agent_install.py`, `tests/test_run_campaign_hazard_flags.py`, `tests/test_window_lineage.py`).
  This is exactly the dispatch's list (catalog, allowlist, four docs, seven tests). Nothing under `joulewise/` or
  `scripts/`, no other `configs/` file, not the runbook. **G.2 H_claim contents: PASS.**
- `git diff --name-status 9395cecfb a64000884 -- joulewise/ scripts/ configs/ docs/phase_2/window_runbook.md` =
  the catalog and `configs/gates/hazard_refusals.json` only. So relative to the head cold pass 5 judged, no code file,
  no script, no other config and not the runbook differs at H_claim. **G.2 no further cold pass owed: PASS** (the two
  differing files are the admitted catalog and the K-S2A-1 allowlist sentence, both of which part A required; their
  bytes are checked below).

## 3. G.1: the three digests and the text diffs (EXECUTED)

Paths (from the seal commit's own file list): `configs/campaigns/v5_claim_25g83/{registration_block5.md,
analysis_plan_block5.md, sealed_inventory.json, flag_catalog.json}`; the design branch holds the first two and the
catalog at the same paths (`git -C /Users/edr/code/JouleWise-wt-ia-claim ls-tree -r --name-only c7408819c`).

**3.1 Digests at the seal commit** (`git -C wt-int5 show ab7b21e5…:<path> | shasum -a 256`, and again from the scratch
clone's working tree at the same commit; the two readings agree on every file):

| File | SHA-256 at S | Dispatch's value |
|---|---|---|
| registration_block5.md | `4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841` | equal |
| analysis_plan_block5.md | `1172a4501e2311a98508e6102420de657daa88c8c455603717b8ff7b2a1e1b8a` | equal |
| sealed_inventory.json | `57ee5d4a8ce632dfca7858f8f834d75dce463276b35fffc4edad91af2d76312a` | equal |
| flag_catalog.json | `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d` | equal |

**G.1 digests: PASS.**

**3.2 Part A's anchors recomputed.** Design branch `c7408819c`: registration `d2ac89cd19ffe9c5cce9e1232dd7d25fde5a4d1d5927de219975e916827c3b91`,
plan `453a5db814b7d6c88c1cf6f198d16338f8dc67848ea599cb74dbe6f43e4e2c6b`, catalog `5d77c725…1ee8d`: all three equal the
dispatch's table and part A's trust anchors. Design branch `cf92f73ec` (the final text): registration `4d321fe3…0841`,
plan `1172a450…1b8a`, catalog `5d77c725…1ee8d`; `cmp` of the seal commit's registration and plan against `cf92f73ec`'s:
byte-identical both. The commits between (`git log c7408819c..cf92f73ec`, merge-base = `c7408819c`, a straight line
of four): `9864f7163` (00:06:48, "the three text changes the seal gate's stage 2A required"), `4321f5709` (01:13:56,
registration fills), `0ceffcf7c` (01:13:57, plan fills), `cf92f73ec` (01:15:07, §0.18 sentence). As the dispatch states.

**3.3 The catalog at H_claim and at S** is `5d77c725…1ee8d` at both (and `2e45cabe…6237bc` at `cc0b3446d`, `2b1595e4…1810`
at `9395cecfb`, as part A recorded). **PASS.**

**3.4 The registration's diff from part A's bytes** (`diff -U0 reg_P.md reg_S.md`, saved at
`/private/tmp/sealgate-stage2b/docs/reg_P_to_S.diff`): 6,165 → 6,173 lines, **16 hunks**, every one read and classed:

| Hunk (old line) | Class | What it is |
|---|---|---|
| 44 | marker-status sentence | header: "a script fills them when that commit exists" → "a script filled them on 2026-10-08, once that commit existed" |
| 52 | marker-status sentence | "beside the marker for H_claim's value" → "beside H_claim's value" |
| 528 | marker-status sentence | item 11 Records: "states H_claim as a marker" → "(as a marker until 2026-10-08, when it was filled)" |
| 535-536 | marker-status sentence | "the two that wait for H_claim remain" → "the two that waited for H_claim were filled at H_claim on 2026-10-08" |
| 756 | FILL ×3 | `B5-FINAL-HASHES` → ALPHA `1d87a309…`, BETA `0cdb3383…`, GAMMA `8b1d1d71…` (plan trees) |
| 1498-1501 | correction of fact (cf92f73ec), classed in 3.6 | §0.18: what H_claim's tree holds for the two texts |
| 1649 | FILL | `H-CLAIM` → `a64000884ef5bb4b76415835f02f39803f6eb620` |
| 2522 | FILL | `B5-FINAL-HASHES` → `a0865895…` (identity pins) |
| 3025 | FILL | `B5-FINAL-HASHES` → `89e7ea70…` (sizing output) |
| 3444 | T-S2A-3 | verbatim (3.5) |
| 3455-3457 | T-S2A-2 | verbatim (3.5) |
| 4534 | T-S2A-1 | verbatim (3.5) |
| 5515 | marker-status sentence | §13 row `H-CLAIM`: adds ": filled on 2026-10-08, once H_claim existed (§2 item 1)" |
| 5523 | marker-status sentence | §13 row `B5-FINAL-HASHES`: tenses, and "they were filled at H_claim on 2026-10-08" |
| 5533-5534 | marker-status sentence + FILL | "Two names were filled last, on 2026-10-08 … except in the sentences that said the two were still open"; `H-CLAIM` → `a64000884…` (second site) |
| 5537 | marker-status sentence | "`B5-FINAL-HASHES` marks" → "marked" |

Seven fill sites (756 ×3, 1649, 2522, 3025, 5534) = the seven part A listed. Three section-F changes. One §0.18
correction. Eight hunks of sentences that said the markers were still open, each a tense change or a "filled on
2026-10-08" clause; none states a rule, an exclusion, a threshold or a computation. No other hunk exists. `FILL[` occurs
0 times in the registration at S (`grep -c`). **G.1 registration: PASS.**

**3.5 The three section-F changes, verbatim** (`/private/tmp/sealgate-stage2b/check_f.py`: counts of the exact old and
new strings of part A's table, line breaks and two-space indents included, in `c7408819c`'s bytes and in S's):
T-S2A-1 old@P=1 new@S=1 old@S=0 new@P=0; T-S2A-2 the same; T-S2A-3 the same. **PASS.**

**3.6 The §0.18 correction (`cf92f73ec`), classed by this judge.** Old text: at H_claim the code tree holds "the two
texts as the seal gate judged them, with the two markers that wait for H_claim still open". New text: "revision 9 of
the two texts, the revision the gate's first stage judged. The final texts are written on a branch that holds only
the documents' drafts (the design branch) and enter the code tree in the seal commit. The gate's second stage reads
the final texts there, before H_claim exists, with the two markers that waited for H_claim still open …". EXECUTED:
at H_claim `git show a64000884:…/registration_block5.md | shasum` = `12ac5c78876f09e7b7611ed7de91c4ba70048e6381169143d7a98e5ed41b1eef`
and the plan = `9f0ad06bfdab1bb2c1f153802084be1347bc9a2e3f9397f1d4bda37665c60154`; the design branch at
`9b0c680ed` (revision 9, the revision part A's anchors name as the one stage 1 judged) gives the same two digests. So
the old sentence was false of `a64000884` and the new one is true. H_claim was committed 2026-10-08 01:10:37 PDT; part
A's session ran 23:55 to 00:05 on the design branch at `c7408819c`, which held the two markers open (seven sites): the
new sentence's account of the second stage is true. The change states a fact about the landing and no rule; class
(ii) in part A's taxonomy (a correction of what the tree holds), confirmed by digest. **Admitted.**

**3.7 The plan's diff from part A's bytes** (`/private/tmp/sealgate-stage2b/docs/plan_P_to_S.diff`): 999 → 999 lines,
**6 hunks**: line 211 `FILL[B5-FINAL-HASHES]` → `a6498f56…` (ALPHA `extraction_spec.json`); 214 → `2c0ee718…` (BETA
`extraction_spec.json`); 368 → `4342ea60…` (GAMMA `analysis_manifest_v3.json`); and three sentences that said the
marker was still open: 206 ("where a digest still waits … stands in its place" → "still waited … stood in its place
until it was filled on 2026-10-08"), 773-775 ("Where the mark stands … is written … before the seal commit is made …
it stands in three places" → past tense, "on 2026-10-08"), 985-986 ("now stands … so that filling it is" → "stood …
filling it, done on 2026-10-08, was"). Part A's G.1 said "three sites and nothing else"; the dispatch's item 2,
written after the fill, admits "the few sentences that said those markers were still open" for both documents. The
three sentence hunks are of that kind and only that kind; none touches a rule or a number. **G.1 plan: PASS**, with the
three sentence hunks recorded as admitted under the dispatch's item 2, beyond part A's letter.

**3.8 The plan's remaining markers** at S (`grep -o 'FILL\[…\]'`): `V5-FINAL-PINSET`, `V5-V2-INPUT-MANIFEST`,
`MINT-TO-CLOSEOUT-ADAPTER`, `REPORTED-ENERGY-ISSUER`, `CLAIM-VERDICT-TO-FILL-ADAPTER`, `DISCLOSURE-PRODUCER`,
`B5-BLIND-DRY-RUN-RECORD`, `GAMMA-MANIFEST-EXCLUSIONS-BINDING`, `B5-ANALYSIS-CUSTODY-ROOT`, `DISCLOSURE-SITES` ×2:
eleven, the same eleven as at `c7408819c` less the three `B5-FINAL-HASHES`; all lane L9's. No `B5-FINAL-HASHES` or
`H-CLAIM` remains in either document. **PASS.**

## 4. G.2: H_claim (EXECUTED)

- The 13-path list `cc0b3446d → a64000884` (section 2) is exactly the dispatch's: catalog, allowlist, four docs,
  seven tests. **PASS.**
- Against `9395cecfb` (cold pass 5's head) nothing under `joulewise/`, `scripts/`, no other `configs/` file and not the
  runbook differs (section 2). **PASS.**
- **The allowlist `configs/gates/hazard_refusals.json`.** JSON-level comparison `cc0b3446d → a64000884`
  (`/private/tmp/sealgate-stage2b/docs/hr_{cc0b,H}.json`, every leaf): exactly one differing leaf,
  `window_exclusions/neg8.screen_failed/protects`; text diff one hunk. The `protects` string at H_claim equals part A's
  K-S2A-1 new text byte-for-byte (Python `==`); the string at `9395cecfb` equals part A's old text; the entry's other
  key (`category`: `NUMBER_INTEGRITY`) unchanged. (The file at `9395cecfb` differs from `cc0b3446d` in three further
  places, `cell.below_minimum`, `g3.recompute_failed` removed, `neg8.midpoint_lost_primary`; those are stage 1's K-1
  and K-3, which part A verified in its section E at `cc0b3446d`, before H_claim.) **K-S2A-1 applied verbatim: PASS.**
- **The committed inventory**: keys `files`, `head`, `schema_version`, `status` only; `head` =
  `a64000884ef5bb4b76415835f02f39803f6eb620`; `status` = `SEALED`; `schema_version` = `joulewise.b5_sealed_inventory.v1`;
  no `roots` key; `files` is a map of 682 paths (150 `joulewise/`, 165 `scripts/`, 123 + 123 + 120 in the three
  claim packs, 1 catalog); `configs/calibration/calibration_ledger_head.json` absent; the three seal documents absent;
  every value a 64-hex SHA-256. At H_claim the file is the stub (`STUB_NOT_SEALED`, `head` null, `files` null,
  digest `39433d47…dd9c`). **PASS.**
- **The four pinned estimator files** (`joulewise/reduce.py`, `joulewise/uncertainty_evidence.py`,
  `joulewise/powermetrics_fiducial.py`, `joulewise/adapters/powermetrics.py`, named at registration line 1711):
  `git diff --name-status 9395cecfb a64000884 -- <four>` empty; `git diff --name-status a434e363d a64000884 -- <four>`
  empty (the frozen head the registration names). SHA-256 at H_claim: `7b9c0d28…9fcc`, `b583f35a…4ae8`, `bcdfeec0…b30c`,
  `70f47086…e5e4`. **PASS.**

**A fact about the name H_claim (recorded; no byte or number depends on it).** `a64000884` is a merge commit (parents
`1704059cc`, the catalog-and-allowlist commit of 00:07:54, and `3ff380b74`, the CI-linux-fixes lane head). Its tree id
equals `3ff380b74`'s (`96178f01…`); its diff from its first parent is the seven test files; `1704059cc` is an ancestor of
`3ff380b74`; `git diff --name-only 1704059cc a64000884 -- joulewise/ scripts/ configs/ docs/phase_2/window_runbook.md`
is empty. So the last commit on the integration line that changed a window input is `1704059cc`, and `a64000884` is
the merge, two commits later, that holds the same window-input bytes plus seven test files. The registration's
definition ("the last commit that changes any window input") fits `1704059cc` to the letter and `a64000884` as "the
commit whose window inputs are the final ones, from which the inventory was generated and whose only integration child
is the seal commit". Every digest the texts print was computed at `a64000884` and is identical at `1704059cc`; the
harvest compares executed heads against `a64000884`, so the two test-only commits before it are never a difference,
which is the cleaner choice for the harvest. Had `1704059cc` been named, the seal commit would not be its child and the
landing test would fail. This is a matter of naming, not of bytes; it is dispositioned "flag, not refuse" and stated as
a condition on the seal record (section 8, condition 5).

## 5. G.3: the seal commit (EXECUTED)

- One parent, H_claim (section 2). **PASS.**
- `git diff --name-status a64000884 ab7b21e5` = M, M, M on exactly the three seal documents (section 2). **PASS.**
- `PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_b5_seal_landing` in the scratch
  clone at `ab7b21e5…`: 9 tests, `OK` in 2.871 s, including
  `RepositorySealLandingTests.test_the_committed_inventory_is_the_stub_or_a_correct_landing` and
  `test_the_sealed_roots_are_the_ones_the_generator_lists`. **PASS.**
- **The `files` map regenerated from git objects by this judge** (`/private/tmp/sealgate-stage2b/regen_inventory.py`:
  `git ls-tree -r a64000884`, every blob under `joulewise/`, `scripts/`, the three claim-pack directories, plus the
  catalog; `git cat-file blob` and `hashlib.sha256`, no working tree): 682 entries; 0 paths in the tree but not
  committed; 0 committed but not in the tree; 0 digest mismatches; no symlink or submodule under the roots; per root
  150 / 165 / 123 / 123 / 120 / 1. Re-serialized with the wrapper's own layout (`json.dumps(sort_keys, indent=2) + "\n"`,
  `head` = H_claim, `status` SEALED) the bytes hash to `57ee5d4a…312a`, the committed inventory's digest. **PASS.**
- **The generator run on a clean checkout** (SEAL_LANDING step 4 check 3): the scratch clone at S, `git status
  --porcelain --untracked-files=all` empty; `make_sealed_inventory.py <clone> <out>` (the lane's wrapper around
  `scripts.rehearse_b5_real.sealed_inventory`, read: `git ls-files` under `joulewise`, `scripts`, the three packs, plus
  the catalog, SHA-256 of each working-tree file) → `files=682`; its `files` map `==` the committed map (Python). Its
  `head` is S, as it must be when run at S; its own digest therefore differs (`1ead3232…`), which is the expected
  consequence and not a finding. Two independent readings (git objects; working tree) agree. **PASS.**
- **Every filled digest recomputes from H_claim's tree** (`git show a64000884:<path> | shasum -a 256`):
  ALPHA plan tree `1d87a30955fa978d3a3a22dc0048720691e0128e4a3fe83477fc375d13dd031a`, BETA `0cdb33836f4632827bc74be194e388450c53b3314db1c72d9e9904e625868670`,
  GAMMA `8b1d1d7176f5ee2286038e91df6427e47476c3a4bdee45a1c24687d49d80e3bf`, identity pins
  `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9`, sizing output
  `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa`, ALPHA `extraction_spec.json`
  `a6498f56469448fd422e6ca2e0787b362a4fd6957bffab7d477ac7f30db38df6`, BETA `extraction_spec.json`
  `2c0ee7189f9aa7e8f534be3cca3bf6f4125c23b5e7bf7ee1e600c7edf9d81ddc`, GAMMA `analysis_manifest_v3.json`
  `4342ea609ec7f57fbb21860440995ac8f2038d93ed508f8d7bb72a540c86050d`. Each equals the value at its fill site in the S
  texts (the diffs of 3.4 and 3.7) and the fill agent's NOTES. Occurrences of each full value in the S texts
  (Python `count`): registration: H_claim 2, ALPHA/BETA/GAMMA plan trees 2 each (the fill site and §0.7's earlier
  print), identity pins 3, sizing 2; plan: 1, 1, 1. **PASS.**
- **Other children of H_claim.** `git rev-list --all --children` shows H_claim with two children in the local
  repository: the seal commit `ab7b21e5…` (branch `integrate/2026-10-07-int5`, and remote-tracking ref
  `origin/seal/2026-10-08-block5-seal-candidate` as the local repository last saw it) and `7e6158d669cbb6fb35761aee18abf363f07c5d36`
  ("Merge H_claim into the harvest lane, so the desk clone's commit descends from the sealed head", 01:23:10, parents
  `c10257418` and `a64000884`), reachable only from the local branch `lane/2026-10-07-harvest-lane`. Its diff from
  H_claim lists `joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `scripts/harvest_b5_window.py`,
  `tests/flags/test_flags_collect.py`, `tests/test_harvest_b5_window.py`, `tests/test_neg8_survivors.py`, nothing
  else; it touches no seal document. This is the harvest lane that part A's G.7 requires to descend from H_claim and
  to land in a desk checkout only; it is not a second seal candidate (the landing test's "only parent" statement is
  about the inventory's last change, which it does not make). "Only child" holds on the integration branch and on
  the seal ref. Recorded; a condition below keeps it out of the measurement clone. **Not a finding against the landing.**
- The int5 worktree's remote-tracking ref `origin/integrate/2026-10-07-int5` stands at H_claim, as the dispatch says
  (no fetch was made; this is the local repository's last view).

## 6. G.5: the table of pinned digests (EXECUTED; `git show <commit>:<path> | shasum -a 256`)

At H_claim `a64000884ef5bb4b76415835f02f39803f6eb620` (every one of these files is byte-identical at S; checked for
the catalog, sizing, identity pins and runbook, and implied for the rest by the seal commit's three-file diff):

| File | SHA-256 |
|---|---|
| `configs/campaigns/v5_claim_25g83/flag_catalog.json` | `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d` |
| `configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json` (ALPHA) | `1d87a30955fa978d3a3a22dc0048720691e0128e4a3fe83477fc375d13dd031a` |
| `configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json` (BETA) | `0cdb33836f4632827bc74be194e388450c53b3314db1c72d9e9904e625868670` |
| `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json` (GAMMA) | `8b1d1d7176f5ee2286038e91df6427e47476c3a4bdee45a1c24687d49d80e3bf` |
| `configs/model_panels/qwen3_4bit.json` | `78875a0e8b2c6d9f573cd42b0d27de6498cdfc8de57af4b4a502e1f93a02513a` |
| `configs/campaign_policies/quiet_mac_p2_b5.json` | `ba0f7b7f1538fe87f6281362efbba4b05f7dff74b4bfd78e84c98b9e8859bc60` |
| `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` | `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660` |
| `configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/prefill-prompt-ladder.json` | `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885` |
| `configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/prefill_prompt_pin.json` | `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb` |
| `configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/selection.json` | `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222` |
| `configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/prefill-prompt-ladder.json` | `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885` |
| `configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/prefill_prompt_pin.json` | `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb` |
| `configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/selection.json` | `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222` |
| `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/prefill-prompt-ladder.json` | `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885` |
| `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/prefill_prompt_pin.json` | `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb` |
| `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/selection.json` | `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222` |
| `configs/campaigns/v5_claim_25g83/sizing_b5.json` | `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa` |
| `configs/campaigns/v5_claim_25g83/identity_pins.json` | `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9` |
| `docs/phase_2/window_runbook.md` | `c4e8bf416269ba3a9fb5ffda3404414ce7227d162c1329cea92817a38ea384c5` |

The nine `prefill_pin/` files carry three distinct digests (`43a77ea9…`, `d1209f6d…`, `c694c488…`), as part A found;
a fourth `prefill_pin/` directory (`d117_contrast_v5`, not a claim pack) exists at H_claim and is not pinned.

At the seal commit `ab7b21e576a2d74f0b25d9a26b463d6934588368`:

| File | SHA-256 |
|---|---|
| `configs/campaigns/v5_claim_25g83/sealed_inventory.json` | `57ee5d4a8ce632dfca7858f8f834d75dce463276b35fffc4edad91af2d76312a` |
| `configs/campaigns/v5_claim_25g83/registration_block5.md` | `4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841` |
| `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` | `1172a4501e2311a98508e6102420de657daa88c8c455603717b8ff7b2a1e1b8a` |

Also at H_claim, for the plan's fills: ALPHA `extraction_spec.json` `a6498f56…8df6`, BETA `extraction_spec.json`
`2c0ee718…1ddc`, GAMMA `analysis_manifest_v3.json` `4342ea60…050d` (full values in section 5). **G.5: PASS** (every
digest recomputed; the orchestrator copies this table into the seal record).

## 7. G.8 and the three further checks (EXECUTED)

- **G.8, the three records §2 item 1 prints** (`shasum -a 256` of the files the registration names, lines 1681, 1698,
  1707): `/Users/edr/night-archive/gate-prune/cold-pass-5/REPORT.md` =
  `46446fa429bdceaac91da1bb3916714c3c59fd846c6bf4503bad4462e218e8ad`;
  `/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/REVIEW.md` =
  `fec2dc44938731c8528777b66c336df07ca553ff6f43f2bcd146cab641012f0a`;
  `/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/ORCHESTRATOR_RULING.md` =
  `92ba27dc49ce205e76111a46bdddda6450ba21863feb8f5d1177527be27fde4e`. All three equal the registration's. **PASS.**
  (The repository copies of `RULING_STAGE1.md` and `REFUTER_STAGE1.md` do not exist at S:
  `docs/process_traces/2026-10-07-block5-seal/` is absent from S's tree; they arrive with the record commit. For that
  check the night-archive originals hash today to `954ac12e9136bd29fdcc5979e654149fd51ca9490d7ded142010efba184d1279`
  and `f4a42b19c3edf3dd5c71a6ea1f9a817625387499c39a9f12a61d961fc228bdf8`; digests only, the files were not opened.)
- **`scripts/gen_state.py --check`** in the scratch clone at S: exit 0, no output. **PASS.**
- **`scripts/repin.py --check`** at S: `PASS 16 pin families current`, exit 0. The clone's status is still empty
  afterwards. **PASS.**
- **Section 6.9 parsed by the harvest's own parser**: `joulewise.b5.harvest.parse_registration_thresholds(raw)` on the
  S registration (`raw` hashes to `4d321fe3…0841`): 9 keys, `battery_accumulator_watts_per_unit` 0.001,
  `battery_limit_ma` 200, `battery_unmeasured_gap_s` 120.0, `clock_step_ns` 1000000, `clock_systematic_min_recorded` 5,
  `clock_unmeasured_gap_s` 3.0, `contention_cpu_s_per_s` 0.05, `disk_low_bytes` 10737418240,
  `thermal_unmeasured_gap_s` 15.0; `harvest._threshold_problem` returns none for every key; the key set equals
  `harvest.HARVEST_THRESHOLD_KEYS` (9) in both directions. **PASS.**

## 8. Conditions of the seal (G.4, G.6, G.7, and two this ruling adds)

1. **G.4, the record commit R.** Child of S (`ab7b21e5…`), on the integration branch; `git diff --name-only --no-renames
   ab7b21e5 R` lists only paths under `docs/` and `tests/` (never `joulewise/`, `scripts/`, `configs/` or
   `docs/phase_2/window_runbook.md`); it adds `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` and the
   gate's records as §12 names them, and the repository copies of `RULING_STAGE1.md` and `REFUTER_STAGE1.md` hash to
   `954ac12e…1279` and `f4a42b19…bdf8` (section 7); the whole suite and CI green at R; the pull request merged with a
   merge commit (`gh pr merge --merge`), never squashed or rebased, so that `a64000884` and `ab7b21e5` are in main's
   history; `git diff --name-only R M` empty.
2. **G.6, the measurement clone.** A full clone (no `--depth`), checked out detached at `ab7b21e5…`;
   `git diff --name-only --no-renames a64000884 HEAD` = exactly the three seal documents; `git status --porcelain`
   empty; `scripts/collect_window_flags.py --stage desk --h-claim a64000884ef5bb4b76415835f02f39803f6eb620
   --sealed-inventory <clone>/configs/campaigns/v5_claim_25g83/sealed_inventory.json` raises no `code.*` flag for each
   of the three packs. Afterwards only pin-only commits (`scripts/advance_b5_ledger_pin.py`) enter the clone; nothing
   is merged, pulled or checked out there.
3. **G.7, the harvest lane.** Its head today is `7e6158d669cbb6fb35761aee18abf363f07c5d36` on `lane/2026-10-07-harvest-lane`
   (diff from H_claim: `joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `scripts/harvest_b5_window.py`,
   `tests/flags/test_flags_collect.py`, `tests/test_harvest_b5_window.py`, `tests/test_neg8_survivors.py`). It lands in
   a desk checkout only, never in the measurement clone, and not on the integration branch or main before the
   addendum; before ALPHA-1's harvest its diff from H_claim still lists only those three code files plus tests and
   fixtures; its tests include the RF-1, RF-3 and RF-5 synthetic windows; its `tests/flags/test_flags_collect.py` no
   longer asserts the two `head_change_class` functions agree on every path, or asserts the lane's table (part A, C.2);
   the seal record's addendum names its commit, files and digests before the first harvest.
4. **The plan's eleven lane-L9 markers** (section 3.8) are filled only after the seal, and each fill is recorded in an
   addendum to the seal record stating the plan's new digest; the registration's bytes (`4d321fe3…0841`) never change.
5. **The seal record states the naming fact of section 4**: that `a64000884` is the merge of the CI-linux-fixes lane
   onto `1704059cc`, the last commit that changed a window input; that its tree equals `3ff380b74`'s; and that its
   window-input bytes equal `1704059cc`'s (empty diff over `joulewise/`, `scripts/`, `configs/` and the runbook).
   The harvest's comparisons are against `a64000884`, as the inventory's `head` says.

## 9. Ruling

Every check that can be made at the seal commit was made by execution and passed: the three seal documents and the
catalog hash to the values the dispatch states; the registration differs from the text part A admitted only by part
A's three required changes (verbatim), the seven filled sites, the eight sentences that said the markers were open,
and the one §0.18 sentence corrected to a fact this judge verified by digest; the plan only by its three filled sites
and three sentences of the same kind; no `FILL[` remains in the registration; H_claim holds, beyond what part A saw,
exactly the admitted catalog, the K-S2A-1 sentence, four documents and seven tests, and nothing under `joulewise/` or
`scripts/` differs from the head cold pass 5 judged; the inventory names H_claim, is `SEALED`, has no `roots`, omits
the pin, and its 682 entries equal, path by path and digest by digest, a map this judge regenerated from H_claim's git
objects and a second map the repository's generator produced from a clean checkout; the seal commit has one parent and
changes exactly the three seal documents; the landing test, the two generators' checks and the harvest's parser of
section 6.9 all pass at S. Two facts are recorded and attached as conditions, neither touching a byte a window reads:
the harvest lane's merge commit is a second child of H_claim on its own branch, and `a64000884` is the merge two
test-only commits after the last window-input change, with identical window-input bytes.

**SEAL: ADMIT**, subject to the five conditions of section 8.

For the project's owner, in plain words. Before any of the three measurement windows runs, the exact bytes of every
file a window can execute, and of the two documents that fix the rules and the arithmetic, have now been written down
in one commit and checked by a session that had no part in writing them: every digest was recomputed from the commit
itself and agrees, the only text changes since the previous judge are the four he required, the filled-in digests and
the sentences saying they were filled, and the code is the code the last cold pass read. Nothing a window reads has
changed since then, and nothing is armed. What remains is bookkeeping that cannot exist yet: the record commit that
pins this table, the measurement clone checked out at the seal commit, and the harvest lane kept on the desk.

Session end: 2026-10-08 01:26:30 PDT (`date`, EXECUTED). Every probe ran in the foreground of this one session; no
subagent, no background task; nothing written in any repository (`git status --short` empty in
`/Users/edr/code/JouleWise-wt-int5` and `/Users/edr/code/JouleWise-wt-ia-claim` at the end; no fetch, pull, checkout,
commit, stash or worktree command in either); scratch under `/private/tmp/sealgate-stage2b/` only (`clone/` at S,
`docs/` with the document copies and diffs, `check_f.py`, `regen_inventory.py`, `inv_regen_at_S.json`). No mail, no
network request, nothing armed. NOT EXECUTED (cannot be, yet): conditions 1 to 5.
<!-- END-BYTES RULING_STAGE2B.md -->
