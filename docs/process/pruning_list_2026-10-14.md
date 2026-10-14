# What to keep, flag or delete: JouleWise's checks and gates, 2026-10-14

For Ed. Written by the Opus 5.5 join seat of the 10-14 pruning workflow, from three inventories in this folder
(`CODE-INVENTORY.md`, `PROCESS-INVENTORY.md`, `HISTORY.md`), the threshold note's section 9
(`docs/design/next_block_threshold_proportion.md`), the block-6 draft (`docs/design/block6_collection_draft.md`),
the block-5 registration's section headings, and a static import scan of the code. Trees: main `0cb3dfb8d`, the
analysis worktree `JouleWise-wt-l9` `730842e05`. No tracked file was changed, nothing measured was opened, no PR
body was read.

**Revised after the challenge (2026-10-14, Opus 5.5 director).** A Sol 6.1 seat (xhigh, read-only), given only
this list and a table of code locations, argued every row against the code: for each FLAG, DELETE and MERGE, a
concrete input that would give a wrong, admitted or suppressed number without the mechanism; for each KEEP,
whether it is really X. Its report is `sol-challenge.md`; its brief is `BRIEF-sol-challenge.md`. Each table now
has a **Challenge** column with the outcome for that row, and section 1.1 lists what changed. The pre-challenge
text is kept as `PRUNING-LIST.pre-challenge.md`.

## 0. Words used, in the order they are needed

- **Session** (also **window** or **attempt**): one unattended collection run on the MacBook, about six hours.
  **Pack**: one of the three fixed workload plans, ALPHA, BETA and GAMMA; each session runs one pack.
  **Member**: one measured model run inside a session (a pack has 107 to 125).
- **Arm**: the checks run just before a session starts. **t0**: the moment the session's driver program starts.
- **Harvest**: the program that reads a finished session's raw files, applies the registered checks, and writes
  a verdict and an archive. **Claim-usable**: the harvest's verdict that the session may enter a published number.
- **Refusal**: a check that stops a session from starting, stops it part-way, or removes a member or a whole
  session from the published numbers. **Flag**: a check that writes its finding into the harvest record and
  keeps the session. The analysis plan, written before the data, names which flags exclude a session; the paper
  then prints the result with and without the flagged sessions (threshold note section 9, requirement 4).
- **L9**: the analysis code, in the worktree `JouleWise-wt-l9`, that turns harvested archives into the paper's
  numbers. It was built in stages S0 to S10 from 10-12 to 10-14.
- **Blinding**: nobody, person or model, reads a measured block-5 energy until the **release**, the moment the
  numbers are first looked at. **Independent recompute**: the headline numbers computed a second time from the raw
  power records by new code that shares nothing with L9 (RUN_STATE item 37; not yet run).
- **Seat**: one model session given one job. **Executing review**: a seat that did not write the code checks it
  by running it, with test inputs and deliberate small code changes ("mutations") to see whether tests notice.
  **Cold judge**: a fresh Fable session that rules on a written charge. **Refuter**: a seat that attacks a draft
  rule before the judge rules. **Two-seat consult**: Sol and Opus, each blind to the other, diagnose a lost session.
- **Digest**: a SHA-256 fingerprint of a file. **Pin**: a digest written down so a later program can insist the
  file has not changed. **Seal**: the block-5 act that froze the registration, analysis plan and code at one
  commit, with a table of pins. **Calibration capture**: a short known workload at a session's start and end that
  measures how far the power sampler's clock can be from the model's clock, in milliseconds. **Ledger**: the
  file that lists every calibration capture ever taken, chained by digests.
- **NEG-8 screen**: reference members run at the start and end of a session; if their energies moved more than a
  bound derived from an 18-member corpus, the machine drifted during the session. The bound feeds a "drift
  allowance" that widens the reported intervals.
- **CI**: the GitHub checks that run on every push; a failing required check blocks a merge.
- **Release path**: the code the block-5 release run will import. I computed it by reading the import statements
  of `joulewise/b5/harvest.py` and every L9 module (`joulewise/b5_analysis/*.py`) in the L9 tree, without running
  them: 125 modules. It includes most of the "retired" arm code (`arm_readiness.py`, `arm_readiness_evidence*.py`,
  `night_gate.py`, `t0_rehearsal.py`, `v5_qualification.py`), the hazard modules `hazards/arm.py` and
  `hazards/battery.py`, `b5/plan.py`, `b5/chain.py`, `controller.py` and `calibration_ledger.py`. Outside it:
  `b5/driver.py`, the watchdog, `scheduler_gates.py`, `arm_retry.py`, `night_agent_install.py`, all CI and test
  files, and the config registries.

**The class of each mechanism** (the test in the brief):
**P** measures a physical hazard directly (clock step or drift, battery, thermal pressure, an outside process
using the processor, free disk, the sampler not sampling). **R** recomputes a number from raw data, or protects the
result itself (blinding, arithmetic fixed before the data, executing review, independent recompute). **X** checks
a record about a record (digests, lineage, custody, pin matching, receipt formats, plan-id binding, ruling chains,
seals). Mixed rows say which part is which.

**What a "catch" counts as** (codes from `HISTORY.md`):
**W**: the defect would have changed or admitted a printed number, from data the real programs write.
**W-latent**: a wrong number only from a hand-made or damaged record. **S**: the defect removed or refused good
data (a member, a session, every session). **P-protective**: a physical check kept contaminated data out, as
designed. **T**: printed wording only. **N**: nothing. **unknown**: no record says whether it ever fired; this is
not the same as zero. C-numbers and K-numbers cite the rows of `HISTORY.md` tables 1 and 2; S-numbers are rows
of `CODE-INVENTORY.md`; letter-numbers (A1, B2, ...) are rows of `PROCESS-INVENTORY.md`.

**Periods**: **B3** block 3 and its re-harvest (10-03 to 10-04); **SC** block-4/5 build, seal and collection
(10-04 to 10-12); **L9** the analysis lane (10-12 to 10-14).

**Proposals**: **KEEP**; **FLAG** keep the check, but record its finding instead of refusing (for a CI check:
make it a warning that does not block a merge); **DELETE**; **MERGE** fold it into another mechanism named in the
row.

**Timing**:
- **(a) now**: outside the release path.
- **(b) after the block-5 numbers are produced and independently recomputed**: anything in the release path.
  Changing it earlier means re-verifying L9.
- **(c) before any block-6 collection**: anything that could refuse or discard a new session. These changes
  are written under the five requirements of threshold note section 9:
  1. replay the rule over every known-good session on disk;
  2. size it in joules on the smallest printed quantity;
  3. compute before the session whatever can be computed then;
  4. collect, flag, and decide in the analysis;
  5. one whole rehearsal per pack through the after-session check.
- **—**: kept as it is; nothing to schedule.

Many (c) rows sit in modules that are also on the release path (`hazards/arm.py`, `b5/plan.py`, `b5/chain.py`,
`controller.py`). If the release run is made from a tagged, frozen copy of the L9 tree, every (c) row can start
now. Without that tag, those rows wait for (b). This is decision 5 in section 6.

## 1. Summary

- **Counts (after the challenge).** 155 proposal rows, covering the 200 code mechanisms and the 67 process
  mechanisms (several rows group related ones): 72 KEEP, 36 FLAG, 31 DELETE, 16 MERGE. By timing:

  | Proposal | (a) now | (b) after release + recompute | (c) before block 6 | — (no change) | Total |
  |---|---:|---:|---:|---:|---:|
  | KEEP | 6 | 13 | 8 | 45 | 72 |
  | FLAG | 6 | 17 | 13 | 0 | 36 |
  | DELETE | 22 | 5 | 4 | 0 | 31 |
  | MERGE | 5 | 8 | 3 | 0 | 16 |
  | **Total** | **39** | **43** | **28** | **45** | **155** |

  Before the challenge: 70 KEEP, 38 FLAG, 33 DELETE, 14 MERGE; by timing 38, 43, 28, 46.

  A KEEP row with a timing keeps the mechanism but changes how it is run or sized, for example keeping a
  recompute but comparing its result numerically instead of byte for byte. Those 27 rows read "KEEP, but ..."
  in the tables.

- **Lines removed (estimate; section 3 gives the method).** About **47,000 lines of non-test code**
  (plausible range 35,000 to 60,000, because shared helpers are counted more than once). Add **74,237 lines of
  data** in four census registries, and about **8,700 lines of test code** that test only the deleted censuses.
  The 99 test files (about 115,000 lines) that name a retired arm module are not estimated: some of them test
  live code and would be rewritten, not deleted. For scale, the code inventory puts all 200 code mechanisms at
  about 93,000 non-test lines; the whole test tree is 325,156 lines.
  By timing: about **5,300 code lines and all 74,237 data lines now (a)**; **38,600 after the release (b)**;
  **3,200 before block 6 (c)**. Most of (b) is the retired arm and launch code (about 17,000), which the
  release path still imports. (Before the challenge: about 47,700; 5,100, 39,300 and 3,300.)
- **What the evidence says.** Every catch that would have changed a printed number (W) came from a second seat
  examining the code or the rule, most of them by running it (C16 was found by reading):
  - executing reviews: auxiliary-model runs pooled into the printed statistics (C63); every drift allowance
    dropped by a second spelling of a path (C59); a charging member kept (C11);
  - the early Opus cold pass, which ran the code: a sign error (C66);
  - the pre-arm triple audit: excluded members inside the printed mean (C16); a contaminated reference keeping
    its allowance (C18);
  - the Sol delta audit: three blockers (C20);
  - two refuters: C5 and C31.

  No X mechanism has a recorded catch that touched a number in any of the three periods. Several X mechanisms
  removed good data (S):
  - BETA a1, a4 and a5, about 18 h of collected sessions (K13, K17);
  - the nine S10 defects (C65), all guard and plumbing code refusing real data.
- **Two corrections to the inventories.**
  1. `PROCESS-INVENTORY.md` says the triple audit (B9) and the delta audit (B8) caught nothing. `HISTORY.md` shows
     W catches by both, and I confirmed the cited lines (`gates/30-triple-audit-fable.md:31`;
     `gates/33-sol-delta-audit-1.md:23-25`, all three marked EXECUTED). Both are KEEP below.
  2. `PROCESS-INVENTORY.md` blames first-seal ALPHA a1 on the midnight `/private/tmp` clean-up. The block-6 draft
     (section 2) shows that 18 of its 19 exclusions were outside processes inside the member's span: a physical
     cause, correctly excluded.
- **Block 6.** The (c) rows are what a block-6 collection needs first. Block 5 ended with one claim-usable
  session per pack. The block-6 draft targets three per pack in about 3 to 3.5 days of machine time, after the
  registration work, which it names as the critical path. That fits inside the month; this list does not by
  itself call for more time.

### 1.1 Changed by the challenge

Of the 155 rows, Sol challenged 10 on numbers (CHALLENGE-NARROW: keep one leg) and 7 on facts (CHALLENGE-FACT),
and called 11 KEEP rows X. It found no case on 73 rows and said 54 rows hold. All 17 numeric and factual challenges
were accepted, three of them in part or in another form (below). I checked each accepted numeric challenge
against the cited code before accepting it (`identity_pins.py:354-386`, `windows.py:238-297`,
`harvest.py:4486-4505`, `harvest.py:5505-5514`, `harvest.py:6280-6320`, `kept_units.py:178-184`,
`floor_extraction.py:2474-2537`, `bracket.py:342-368`, `test_b5_seal_landing.py:197-205`, and the live
network-time path in `hazards/arm.py` and `b5/driver.py`). None of the accepted challenges keeps any custody
machinery; each keeps one comparison that decides **which data** a number is computed from.

**Proposal or timing changed (8 rows; these move the counts):**

| Row | Was | Now | Why (the concrete case) |
|---|---|---|---|
| HV-19 | FLAG (b) | KEEP, but (b) | A manifest that omits one succeeded corpus member (18 to 17) gives a self-consistent but wrong NEG-8 bound. The succeeded-member and allowed-drop recompute stays; digests and lineage flag. |
| AN-5 | FLAG (b) | KEEP, but (b) | An index missing attempt 1 (an evicted archive, as on 10-12) lets attempt 2 be analysed instead of the registered first usable session. History completeness and first-usable selection stay. |
| AN-3 | KEEP, but (b) | KEEP (—) | As a flag, the floor extractor drops a cap-hit member that harvest kept, so the floor uses nine units while the other statistics use ten. The K26 case is already handled by the p42 exception. |
| AN-8 | DELETE (b) | MERGE (b) into AN-9 | The maximum reads only the longest ledger copy; without the prefix check, a larger observation in a shorter copy is lost. Replaced by a maximum over the union of copies. |
| HV-16 | KEEP (—) | KEEP, but (b) | Fact: `clock.systematic` is a majority count of saved anchor labels, not a measured systematic. It flags; block 6 computes a timing systematic in joules. |
| CA-15 | KEEP (—) | KEEP, but (c) | Fact: S-068's cited check is a record-shape and pin check, not the acceptance arithmetic. It flags. |
| CA-21 | DELETE (c) | MERGE (b) into CA-42 | Fact: the live arm already only records the network-time setter; the refusal is in `network_time_off.py`, which only retired modules import. |
| MG-21 | DELETE (b) | DELETE (a) | Fact: S-188 checks the historical seal landing and allows later code changes; it does not freeze block-5 bytes. The real freeze is L9's `test_frozen_files.py`. |

**Wording changed, same proposal and timing (13 rows):**
- **HV-21**: the exclusion now covers every field that defines the executed computation (model bytes, runtime
  name and version, kernel library, quantization, tokenizer), not only model bytes. An MLX upgrade between
  sessions would otherwise pool two configurations; the weights hash covers weight files only.
- **HV-23 and CA-46**: still FLAG. The block-6 plan names as an excluding flag any change to number-bearing
  acquisition or reduction code that no executing review covered before the session. A raw recompute cannot undo
  a wrong event boundary (a 100 ms shift at 40 W is 4 J).
- **AN-14**: still FLAG, but the finalized-floor identity comparison (`analysis_engine/inputs.py:1002`) stays a
  refusal. A valid floor from another attempt passes every recompute (the same defect class as C59).
- **CA-7**: pause and flag mid-session, and the members that overlapped the agent are excluded by a flag the plan
  names. HV-17 measures outside CPU only, not an agent's GPU work.
- **AN-18**: the independent recompute re-derives member exclusions from the raw monitor records instead of
  reading the harvest's exclusions. This answers AN-6's challenge (below).
- **HV-3**: the numeric comparison covers the uncertainty widths as well as the point energy.
- **OP-7**: the judge on a science split runs the disputed arithmetic.
- **CA-35, CA-48, HV-6, MG-23**: locators and descriptions corrected. Harvest already only discloses an evicted
  capture; the `on_fail=flag` prohibition is `schemas.py:695-700`, and `:721` (the production calibration-bracket
  requirement) stays; the kept freeze is named by its real test.

**Class changed, proposal kept (F9):** HV-8, MG-8 and OP-7 are X; CA-15, HV-16, HV-19 and AN-5 are now split
rows. CA-23, CA-24, CA-30, CA-49, CA-51, OP-10 and OP-17 were already X or Ed's controls in the list, and each
is kept for the reason the list states.

**Rejected or accepted in another form, with Sol's dissent recorded:**
- **AN-6**: Sol asked to keep the integrity check on the exclusions document, or replay the exclusions. I chose
  the replay (AN-18). It also catches a harvest bug, which a digest of the harvest's own output cannot. AN-6
  changes only at (b), after the recompute has run. Sol's dissent applies until that replay exists.
- **HV-23 and CA-46**: Sol asked for a refusal. I kept a flag that the plan makes excluding. It removes the same
  numbers without losing the session, as doctrine item 2 requires. Sol dissents.

The rest of Sol's verdicts were "no case" (every other FLAG, DELETE and MERGE row) or "holds" (every other KEEP
row). Sol's caveats: its counterexamples are static path analyses, not executed mutations, and "no case" does not
certify every way a proposal could be implemented.

## 2. The tables

### 2.1 Collection and arming

| # | Mechanism (IDs) | Class | Number-touching catches (B3 · SC · L9) | Cost | Proposal | Timing | Lines removed (est.) | Challenge |
|---|---|---|---|---|---|---|---|---|
| CA-1 | Clock frequency and drift at arm and t0 (S-005, S-006) | P | B3: unknown · SC: C10 shows the old fixed 5 ms check would have refused any span over about 26 min; the drift-corrected check replaced it · L9: n/a | minutes per arm | **KEEP** | — | 0 | Holds |
| CA-2 | Battery float at arm (S-007) | P | unknown at arm; the harvest's battery replay is HV-15 | minutes | **KEEP** | — | 0 | Holds |
| CA-3 | Thermal pressure (S-008) | P | unknown (no record of it firing) | seconds | **KEEP** | — | 0 | Holds |
| CA-4 | Free disk at arm and live (S-009, S-025) | P | unknown. The 10-12 disk fault (seat temporary files, iCloud eviction) was not caught by it | seconds | **KEEP** | — | 0 | Holds |
| CA-5 | Sampler actually sampling (S-010, S-023, S-024, S-056) | P | SC: P-protective, two rehearsals refused at arm on a 255 ms sampler interval against 150 ms (block-6 draft section 2) | 60 s each | **KEEP** | — | 0 | Holds |
| CA-6 | Contention dwell: a clean run of measured outside-process CPU (S-012) | P | SC: C34, P-protective (first-seal ALPHA a2, `fseventsd`) | K11: about 45 min | **KEEP** | — | 0 | Holds |
| CA-7 | Agent census: no agent process at arm, and a chain stop mid-session (S-001; process C1) | P (by process name) | SC: K15, BETA a2 lost a whole session to a 20 s keyboard session; no number shown, because member-level contention overlap (HV-17) already flags affected members | one session | **KEEP, but** at arm only; mid-session, pause and flag instead of stopping (block-6 draft 6.3), and give every member that overlapped the agent's presence an excluding flag named in the plan, with recovered idle power (CA-11) before resuming. Doctrine item 6 lists the stand-down fence as kept as-is, so this needs Ed (decision 4) | c | ~0 (a change, not a removal) | **Accepted** (F7): HV-17 measures outside CPU only; an agent's GPU work under the CPU limit enters the member's energy (10 W for 0.4 s is 4 J). Overlapping members are now excluded |
| CA-8 | Member runtime cap (S-026) | P | unknown | small | **KEEP** | — | 0 | Holds |
| CA-9 | Watchdog wall-against-monotonic clock check (S-032) | P | SC: C43 (BETA a4 sleep); its action, draining the harvest activation, cost K18 | a cut-short harvest, a wrong fault email | **KEEP, but** keep the measurement and make the drain a flag | c | ~20 | Holds |
| CA-10 | Live display/screensaver state and idle admission by measured power (S-041, S-042) | P | SC: C33, P-protective (baselines under 1 to 2 cores of outside load) | 13 of 53 quiet baselines fail (threshold note section 8) | **KEEP, but** wait instead of aborting (threshold note 3.1) | c | 0 | Holds |
| CA-11 | Recovered idle power before the next member (S-088) | P | unknown | small | **KEEP** | — | 0 | Holds |
| CA-12 | External wall meter connects (S-111) | P (already a flag) | none | none | **KEEP** | — | 0 | Holds |
| CA-13 | Evidence roots fresh, no overwrite (S-018); one writer at a time (S-037); no duplicate run id (S-035); bundle cannot be overwritten (S-046); runtime ran (S-045) | R | SC: C8 (a duplicated run id; diagnostic only) | small | **KEEP** | — | 0 | Holds |
| CA-14 | Decode-counter arithmetic (S-048) | R | unknown (off the block-5 path) | none | **KEEP** | — | 0 | Holds |
| CA-15 | Calibration raw inputs exist (S-049); calibration refit from raw reproduces (S-051); acceptance arithmetic (S-068); measured bracket drift fits the numeric budget (S-071) | R (S-068: X) | unknown as catches; they are the instrument's arithmetic | small | **KEEP, but** flag S-068: its check (`scripts/validate_powermetrics_fiducial.py:411`) is a record-shape and protocol/estimator pin check, not the acceptance arithmetic, which is `calibration_bracketing.py:795` with the refit at `controller.py:782` | c | ~30 | **Fact accepted** (F8). The script runs in the chain (`b5/chain.py:142`), so (c) |
| CA-16 | Opening calibration alignment screen as a stop (S-057) | R, sized at the maximum of 24 captures | SC: K16, BETA a3 lost; the screen saw a real excursion, but carrying the bound protects the number without a stop (threshold council section 8) | one session; then drove K17 | **FLAG**, carry the bound into the operative bound (threshold note 3.2) | c | ~40 | No case. Note accepted: the bracket evaluator (`calibration_bracketing.py:2697`) must carry the bound too, or its preflight still refuses |
| CA-17 | OS build and machine model must be listed in an acceptance epoch (S-002) | X | none recorded | unknown | **FLAG** | c | ~60 | No case |
| CA-18 | Arm record may be written only once (S-003) | X | none recorded | unknown | **FLAG** | c | ~50 | No case |
| CA-19 | Threshold and record shapes (S-004) | X | none recorded | unknown | **FLAG** stamp grammar; keep a refusal only when a registered threshold is absent, because then the P check cannot run | c | ~100 | No case |
| CA-20 | Requested probe frame count equals registered (S-011) | X | none | none | **DELETE** (CA-5 counts the frames actually received) | c | ~20 | No case |
| CA-21 | Network-time OFF receipt and setter wording (S-013) | X (proxy for clock steps) | none | K6-type process cost | **MERGE** into CA-42. The live arm already only records the setter's output (`hazards/arm.py:249-252`, `b5/driver.py:1911`); the refusal lives in `network_time_off.py`, which only retired modules import | b | ~100 (with CA-42) | **Fact accepted** (F8): nothing to change in the live arm before block 6 |
| CA-22 | Night plan, plan-locator digests, environment allowlist, chain grammar (S-014, S-015, S-016, S-017) | X | none | unknown | **FLAG**; keep only "the plan parses and the chain renders" as a refusal | c | ~600 | No case |
| CA-23 | Launch-claim markers, race guard against the watchdog (S-019) | X (close to the R writer lock) | none | small | **KEEP** (cheap; prevents two writers on one session) | — | 0 | Is X (F9): agreed; the list already keeps it for a stated non-R reason |
| CA-24 | Chain bytes equal the recorded sidecar digest (S-020) | X (already a flag at the driver) | none at the driver; its harvest exclusion is HV-23 | none here | **KEEP** as a flag | — | 0 | Is X (F9): agreed; already only a flag |
| CA-25 | Boot changed since the launch record (S-021) | P/X | none | unknown | **KEEP, but** keep the reboot detection (P) and flag the lineage comparison | c | ~40 | Holds |
| CA-26 | Pack config inventory publishable (S-022) | X | none | can lose a session before member 1 | **FLAG** | c | ~100 | No case |
| CA-27 | Two timeouts drain the rest of the science work (S-027) | X (proxy) | none | unknown | **FLAG** | c | ~100 | No case |
| CA-28 | Future stages skipped past a fixed calibration-age horizon (S-028) | X (proxy for calibration drift) | none | unknown | **FLAG**; the closing capture measures the drift | c | ~80 | No case |
| CA-29 | Wall-clock budgets for arm, stages and chain (S-029) | X | none | unknown | **KEEP, but** keep the chain deadline (a hung chain must end) and flag the per-stage budgets | c | ~100 | Holds |
| CA-30 | Owner STOP file and remote-control probe (S-030; process C3) | X (Ed's control) | n/a | none | **KEEP** (doctrine item 6) | — | 0 | Is X (F9): agreed; kept as Ed's control |
| CA-31 | Watchdog plan, lock, install and ownership holds (S-031) | X (proxy for contention) | none | unknown | **FLAG** the record checks; keep "no agent session starts during a session" | c | ~400 | No case |
| CA-32 | Config warnings must be acknowledged (S-033) | X | none | can stop before member 1 | **DELETE** | c | ~100 | No case |
| CA-33 | Config and order schemas agree (S-034); prospective manifest validates at collection (S-036); campaign-log ownership (S-038); child lineage (S-039) | X | none | unknown | **FLAG**; keep "the config parses" | c | ~690 | No case |
| CA-34 | Environment admission receipts (S-040); adapter wattage label continuity (S-043) | X (proxy for quietness and power path) | L9: C50 H2, N (a consult said one adapter-continuity site must stay a refusal; the judge had it wrong) | unknown | **FLAG**; CA-10 and HV-15 measure the physics | c | ~360 | No case |
| CA-35 | Config schema forbids `on_fail=flag` in production (S-044) | X | none | it forbids the doctrine's own remedy | **DELETE** that prohibition (`schemas.py:695-700`); keep key checks and the production calibration-bracket requirement at `:721`, which is R | c | ~200 | **Fact accepted** (F8): the locator `:721` was the bracket requirement, not the prohibition |
| CA-36 | Calibration operator switches and power-policy string (S-055); policy hash binding (S-054) | X (proxy) | none | unknown | **FLAG** S-055; **DELETE** S-054 (counted under the FLAG row) | c | ~160 | No case |
| CA-37 | Calibration digests, session binding, battery custody (S-050, S-052, S-053) | X | none; HV-15 recomputes battery from raw | unknown | **FLAG** | b | ~900 | No case |
| CA-38 | Calibration ledger custody machinery: worker timeouts, receipts, chain digests, head pins, session state machine, lease inodes, crash recovery, plan digest, pin advance (S-058 to S-066; process C7) | X | B3: K2, it mis-refused on its own bug (3.3 h). SC: C15 R2-1, every verdict would have failed on a head mismatch (a self-defect, caught by rehearsal); K3. L9: K21, one evicted historical capture would refuse a session | 3 to 4 h per incident | **MERGE** into a plain append-only list of captures with their measured values, read by content hash, with a writer lock | b | ~3,500 | No case |
| CA-39 | Acceptance generation, ruling records and operative declarations must match (S-067) | X | none | unknown | **DELETE** the ruling-record legs; keep the numeric derivation (CA-15) | b | ~800 | No case |
| CA-40 | Calibration acceptance stale (S-069) | R/X | SC: K17, BETA a4 and a5 (about 12 h), certain to fire from the ledger at arm | two sessions, an erratum | **KEEP, but** keep the numeric part (the observed range or systematic changed); delete the ledger-wide and corpus-growth triggers; compute before the session (requirement 3; C47 is this check) | b | ~120 | Holds |
| CA-41 | Calibration age and epoch labels (S-070) | X (proxy for calibration stability) | none | unknown | **FLAG**, sized in joules (requirement 2) | b | ~80 | No case |
| CA-42 | Retired ARM and t0 evidence chain: receipts, freeze and successor pins, evidence authors, GO tokens, installer receipts, t0 rehearsal custody, qualification history, cold-retry permission, legacy quietness proxies (S-158 to S-163, S-165 to S-167, S-169) | X | none in any period | dormant code that the live hazard modules and the release path still import | **DELETE**, after moving the physical probe functions (S-164) into `hazards/` and the pack-tree digest and lineage helpers that live rows still use | b | ~17,000 (range 14,000 to 22,000) | No case |
| CA-43 | Legacy physical probes on the retired path (S-164) | P | n/a | n/a | **MERGE** into the live hazard modules (part of CA-42) | b | ~0 | No case |
| CA-44 | Scheduler boot pins and family-publication markers (`scheduler_gates.py`, S-168) | X | none | none | **DELETE**; only two test files import it | a | ~1,080 (plus its tests) | No case |
| CA-45 | Salvage authorization (S-170) | R/X | unknown | unknown | **FLAG** the authorization and closure records; keep the raw proof that no workload ran | b | ~600 | No case |
| CA-46 | Clone-integrity checks at arm: clean clone, diff against the sealed commit, regenerated identity pins (process C6) | X (the model-bytes hash is close to R) | none | about 1 min per arm | **FLAG** all; keep the model-bytes hash as a flag. The flag records the changed paths; with HV-23, a change to number-bearing acquisition or reduction code that no executing review covered before the session is an excluding flag in the block-6 plan | c | (process) | **Accepted in part** (F1): a raw recompute cannot undo a wrong event boundary (100 ms at 40 W is 4 J). Rejected: a refusal at arm; a plan-named excluding flag removes the same numbers without losing the session. Sol dissents |
| CA-47 | `B5-ARM-RELEASED:` line in RUN_STATE read by a program (process C9) | X | none | two holds waiting on errata | **DELETE**; a one-line state file if still needed | c | (process) | No case |
| CA-48 | Never-move list for custody roots and captures (process C10) | X (locators by path) | none | turned the iCloud eviction into a refusal risk (K21) | **MERGE** into reads by content hash (CA-38). Harvest already only discloses an evicted capture (`harvest.py:6284-6288`, `calibration.historical_custody_unmeasured`); this row removes the process rule | c | (process) | **Fact accepted** (F8) |
| CA-49 | Arm notice with Ed's NO (process C2) | Ed's control | n/a | minutes | **KEEP** (Ed-reserved). The "no install if neither Gmail nor GitHub reaches him" refusal is X: decision 7 | — | 0 | Is X (F9): agreed; kept as Ed's control |
| CA-50 | Measured-cause procedures: small `/private/tmp`, 60-min settle, the midnight walk (now timed at 51 s), t0 preference (process C5) | P | SC: they removed the causes of the first-seal ALPHA losses; K12 cost (one chain a day until the walk was timed) | minutes | **KEEP** | — | 0 | Holds |
| CA-51 | Dead-man job, watchdog, courier (process C8); END STATE clock-status counts (C11); owner-answer file (C12) | P-adjacent / flag | operational only | small | **KEEP** | — | 0 | Is X in part (F9): the count and answer-file legs are records; kept as operations |
| CA-52 | Pre-mortem fan-out, 8 lenses (process A9) | operations | SC: C29, S (each finding would have lost the first session) | about 34 seats | **MERGE** into one whole rehearsal per pack (requirement 5) and the block-6 fault rehearsal | c | (process) | No case |

### 2.2 Harvest

All rows here are on the release path. For block 5 the registered exclusions stay as they are; the analysis
plan was fixed before the data and the release must apply it. The proposals take effect for block 6. A block-5
exception (a labelled second result that includes BETA a1, a4 and a5) is decision 1.

| # | Mechanism (IDs) | Class | Number-touching catches (B3 · SC · L9) | Cost | Proposal | Timing | Lines removed (est.) | Challenge |
|---|---|---|---|---|---|---|---|---|
| HV-1 | Archive cannot overwrite evidence (S-076); inputs unchanged during harvest (S-077); one unambiguous bundle per unit (S-080) | R | none recorded | small | **KEEP** | — | 0 | Holds |
| HV-2 | Fresh raw-to-trace reduction (S-083); clock-anchor recompute (S-085); token denominator (S-087); anchor energy envelope (S-091); measured span (S-092) | R | none recorded as catches; they are the arithmetic | small | **KEEP** | — | 0 | Holds |
| HV-3 | Re-reduction compared byte for byte with the stored summary (S-084) | R/X | B3 (end of block 2): K4, a harvest refused on a byte-for-byte equality of a re-serialized `config.json`, the same defect class | a fix round and re-harvest | **KEEP, but** keep the recompute; compare numerically within a tolerance every field used later (the energies and the uncertainty widths, not only the point energy); record a non-numeric difference as a flag | b | ~0 (a change) | Holds. **Refinement accepted**: the comparison covers the widths too |
| HV-4 | Saved anchor status says "bounded" (S-086) | X (proxy) | none | none | **MERGE** into HV-2's anchor recompute | b | ~25 | No case |
| HV-5 | Cooldown receipts and eligibility records (S-089) | X (proxy) | none | unknown | **MERGE** into CA-11, the measured recovery | b | ~350 | No case |
| HV-6 | Historical capture bytes against ledger digests (S-072) | X | L9: K21, one evicted capture would refuse a real session | refusal risk | **FLAG** the remaining refusal, which is only for changed bytes in captures the acceptance relied on (`harvest.py:6308`); an evicted capture already only discloses (`:6317`) | b | ~300 | **Fact accepted** (F8); no case for keeping the changed-bytes refusal |
| HV-7 | Catalog and flag-line formats (S-073) | X | SC: C14 B2, a malformed flag line would have release-blocked every session (found by rehearsal) | rehearsal rounds | **FLAG**; keep a parse | b | ~500 | No case |
| HV-8 | Every flag code must have a cataloged effect before release (S-074) | X (records each code's decided effect) | none | none | **KEEP** | — | 0 | Is X (F9): class accepted; kept because "flag, the plan decides" needs every flag code to carry a decided effect before release |
| HV-9 | Chain gone and terminal record present (S-075) | P/X | none | small | **KEEP, but** flag a missing terminal marker | b | ~40 | Holds |
| HV-10 | Threshold provenance: registration digest and key inventories (S-078) | X with an R core (the values used equal the registered values) | none | B3: K2-type fault path | **FLAG**, keeping the value comparison as R | b | ~80 | No case |
| HV-11 | Roster labels bind each bundle to its planned attempt (S-079) | X | SC: C14 B6, the lineage audit flagged 19 auxiliary bundles per session (S) | unknown | **FLAG**. AN-3's unit selection, which stays, is what keeps auxiliary runs out of the statistics | b | ~120 | No case |
| HV-12 | Member inputs present (S-081) | R/X | none | unknown | **KEEP, but** require the raw inputs; flag a missing stored summary or status label and re-reduce from raw | b | ~80 | Holds |
| HV-13 | Strict bundle validator, one umbrella refusal (S-082) | P/R/X | unknown per reason | unknown | **FLAG** its X reasons one by one; keep the P and R reasons | b | ~600 | No case |
| HV-14 | Sampling sufficiency (S-090) | P/R | unknown | small | **KEEP, but** flag the precheck-record leg | b | ~40 | Holds |
| HV-15 | Battery replay from raw observations (S-093); charge accumulator (S-094) | P | SC: C11 W, an executing review found a charging endpoint that this code's assist rule would have kept | small | **KEEP** | — | 0 | Holds |
| HV-16 | Thermal readings in the member's span (S-096); clock step or timing systematic (S-097) | P / P-R (`clock.systematic`: X) | unknown | small | **KEEP, but** flag `clock.systematic`, a majority count of saved anchor-status labels (`harvest.py:5505-5514`), not a measured systematic; block 6 replaces it with a computed timing systematic sized in joules (requirement 2) | b | ~15 | **Fact accepted** (F8/F9) |
| HV-17 | Outside-process CPU overlapping the member (S-095) | P | SC: C32, P-protective (18 members in first-seal ALPHA a1; a BETA a1 reference) | members | **KEEP** | — | 0 | Holds |
| HV-18 | NEG-8 bound derived from enough members (S-099); surviving-reference re-screen (S-101); GAMMA midpoint (S-102) | R | SC: C13, S (10 or 11 members always failed the screen); K10, the corpus size was set too small (12 committed, 10 needed, one retry) | two first-seal ALPHA sessions; a second seal | **KEEP, but** size the corpus under requirements 1 and 2 (block-6 draft keeps 18) | c | 0 | Holds |
| HV-19 | NEG-8 corpus digests, drop records and lineage (S-100) | R (cohort recompute) / X (digests, lineage) | SC: C12 W, but the W was in the drop logic and was found by a review, not by this check | unknown | **KEEP, but** keep the succeeded-member and allowed-drop recompute (`harvest.py:4486-4505`: a member that succeeded may leave the corpus only for a drop reason the mint itself gives); flag the digests, drop records and lineage | b | ~150 | **Accepted** (F4): a manifest omitting one succeeded member (18 to 17) yields a self-consistent but wrong NEG-8 bound; this leg re-derives the cohort from member status on the bound root, which is R |
| HV-20 | Verdict record absent or unreadable (S-098) | X (proxy) | SC: C17, S (triple audit F1 to F3: an absent verdict removes a session) | removes a session | **FLAG** | b | ~150 | No case |
| HV-21 | Model identity against pins (S-104) | X with an R core | SC: C20 A2 W, a wrong-model spare in the reference group (found by the delta audit, not by this check) | unknown | **KEEP, but** keep an exclusion when a field that defines the executed computation differs from the pack's registered stack: model bytes, runtime name and version, kernel library, quantization, tokenizer (`identity_pins.py:354-386`); flag sampler and output-policy spelling, OS string and labels | b | ~600 | **Accepted** (F1): the weights hash covers weight files only; an MLX upgrade between sessions would pool two configurations under one registered stack |
| HV-22 | A damaged flag line that might encode an exclusion removes the session (S-105) | X | SC: C14 B2 (rehearsal) | removes a session | **DELETE** the exclusion; record the damage | b | ~120 | No case |
| HV-23 | Pack, code and plan-tree identity against sealed digests: `pack.identity_mismatch`, `code.executed_differs_from_sealed` (S-103; process C7, K7) | X | SC: none. C24 and K7 found self-defects (the seal's own commit would have removed every session); C25 found a hole (W-latent). | a seal-landing lane, a second seal | **FLAG**: record the executed commit and the changed paths. The block-6 plan names as an excluding flag a change to number-bearing acquisition or reduction code (runtime adapter, reducer, sampler, driver timing) that no executing review covered before the session; other differences only disclose | b | ~500 | **Accepted in part** (F1, with CA-46): an accidental boundary shift in `adapters/mlx_runtime.py` survives the raw recompute. Sol wanted a refusal; rejected because a plan-named excluding flag removes the same numbers. Sol dissents |
| HV-24 | Desk pin and membership binding (S-106) | X | none | unknown | **FLAG** | b | ~150 | No case |
| HV-25 | Launch, calibration, bound, log and verdict provenance chain (S-107) | X | none | unknown | **FLAG** | b | ~1,200 | No case |
| HV-26 | Window-provenance assertions A1 to A5 (S-108) | X (already a flag in harvest) | none | none | **FLAG**: drop the standalone checker's nonzero exit | b | ~400 | No case |
| HV-27 | Executing whole-session verdict replay (S-109) | R | none recorded | small | **KEEP** | — | 0 | Holds. Note: G3 runs only for packs with an analysis manifest (`harvest.py:6842`) and its failure discloses; not a universal refusal |
| HV-28 | Calibration endpoints present (S-110) | R/X | none | unknown | **KEEP, but** keep missing raw endpoints as R; flag missing ledger finalization records | b | ~80 | Holds |
| HV-29 | Harvest pinning: only a pinned harvest may decide; a seal addendum per pin (process D1) | X with an R core (the harvest arithmetic is fixed before it reads data) | none of its own; the gates inside it caught things (B2 to B4) | 4 pins, about 12 to 20 h | **MERGE** into "version the harvest by commit, record which ran"; no addenda | a | ~200 (the pin test) | No case |
| HV-30 | Harvest error text readable only through a cold gate (process D9) | X | none | none | **DELETE**; read it through a structure filter | a | (process) | No case |

### 2.3 Analysis (L9 and the analysis engine)

All code rows here are on the release path, so every change is (b). The process rows (D3 to D6) are the
release's own protections.

| # | Mechanism (IDs) | Class | Number-touching catches (B3 · SC · L9) | Cost | Proposal | Timing | Lines removed (est.) | Challenge |
|---|---|---|---|---|---|---|---|---|
| AN-1 | Floor and estimator arithmetic: meter fit (S-112), floor domain (S-113), common mode (S-114), once-widened composition (S-116), recomputed widths (S-119), executing replay (S-120), raw parse (S-126), estimator domains (S-127), denominators (S-128), multiplicity (S-129), claim arithmetic (S-130), claim numbers (S-132), reported-energy recompute (S-138), output separation and release guard (S-139) | R | SC: C16 W (triple audit: a plain mean over excluded members, built right in S8); L9: C66 W (sign error, found by an executing cold pass) | small | **KEEP** | — | 0 | Holds |
| AN-2 | Paper-custody issuance replay (S-136); printed floor agrees (S-155); blinding route (S-156); sensitivity arithmetic (S-153) | R | L9: C64 S2 (two restricted comparisons visible before release) was a blinding catch | small | **KEEP** | — | 0 | Holds |
| AN-3 | Only complete kept units enter statistics: member cover (S-123), kept units (S-145), excluded reference kept out of the screen (S-146), archive read stable (S-142), source replay (S-152) | R | SC: C18 W (a contaminated reference kept its allowance). L9: C63 W (auxiliary runs pooled; the fix is unit selection); C53, C62 W-latent | small | **KEEP**, including S-145's target-cell tripwire (`kept_units.py:178-184`, already narrowed for non-target p42 cells) | — | 0 | **Accepted** (F5): as a flag, the floor extractor drops a cap-hit member that harvest kept (`floor_extraction.py:2482-2499`), so the floor uses nine units while the other statistics use ten. K26 is already handled by the p42 exception |
| AN-4 | Pack label of an archive must match the window analysed (part of S-140) | R (a wrong label analyses one pack's data as another's) | L9: C52 W-latent (a BETA archive indexed as GAMMA was analysed as GAMMA) | small | **KEEP** that one comparison | — | 0 | Holds |
| AN-5 | Window index, seal pins, attempt history (rest of S-140) | X (pins) / R (attempt selection) | none | K25 | **KEEP, but** keep attempt-history completeness and first-claim-usable selection (`windows.py:238-244`, `:297`); flag the seal pins and other index fields | b | ~400 | **Accepted** (F3): an index missing attempt 1 (an evicted archive, as on 10-12) lets attempt 2 be analysed instead of the registered first usable session |
| AN-6 | Archive digests (S-141); roster rebuild hash (S-143); exclusions catalog identity (S-144); survivor bracket authentication (S-147); source-manifest authentication (S-151); step-output digests (S-157) | X | none (the holes found in them were W-latent: C54, C55, C56) | L9: K25, K26; S10 rounds | **FLAG** | b | ~1,240 | **Accepted in another form** (F2): instead of keeping the exclusions-catalog digest as a refusal, AN-18 re-derives member exclusions from the raw monitors, which also catches a harvest bug a digest cannot. AN-6 is (b), so the replay exists first. Sol dissents until it does |
| AN-7 | Context provenance and window binding (S-148) | X with an R core | L9: C56 W-latent (a context for window A built from B's records admitted A) | small | **KEEP, but** keep the window-identity equality; delete the provenance switch | b | ~50 | Holds |
| AN-8 | Ledger copies are prefixes of each other (S-149) | X | none | unknown | **MERGE** into AN-9: compute the maximum over the union of observations in all ledger copies below the cutoff; record a copy disagreement as a flag (goes with CA-38) | b | ~150 | **Accepted** (F6): `bracket.py:354-368` reads only the longest copy; without the prefix check a larger observation in a shorter copy is dropped (0.12 s against 0.08 s is 40 ms on the sensitivity bound) |
| AN-9 | Bracket recompute (S-150) | R/X | L9: C50 H3 S (the stored-bracket replay would have refused every block-5 row) | unknown | **KEEP, but** keep the numeric recompute; flag the scope, cutoff and copy records | b | ~150 | Holds |
| AN-10 | Disclosure and sensitivity record shapes (S-154) | X | L9: C64 S1, S (every sensitivity record refused on an exact key set) | fix rounds | **FLAG** | b | ~600 | No case |
| AN-11 | Helper signature and parameter digest (S-115); git and interface checks in the floor mint (S-121) | X | none | unknown | **DELETE**; record the commit | b | ~230 | No case |
| AN-12 | Single-count rule tags (S-117) | X | none | unknown | **MERGE** into S-116's arithmetic check (AN-1) | b | ~170 | No case |
| AN-13 | Floor-mint preregistration pins (S-118); reported-energy registration order (S-137) | X (proxy for pre-registration) | none | unknown | **MERGE** into one check that the plan was committed, by date, before the data (OP-4) | b | ~1,620 | No case |
| AN-14 | Analysis manifest v3 and finalization attachments (S-122); authenticated reads (S-124); attachment and root matching (S-125) | X | none | K25-type refusals | **FLAG**; keep the manifest parse and the finalized-floor identity comparison (`analysis_engine/inputs.py:1002`): the floor consumed must be the floor the manifest finalized | b | ~2,950 | **Accepted** (F1): a valid floor from another attempt passes every recompute; only this comparison shows it is not the selected one. Same class as C59 (a second path spelling) |
| AN-15 | Claim artifact schema (S-131); output-identity report schema (S-134) | X | none | unknown | **FLAG** S-131 (S-134 is deleted inside this row) | b | ~1,150 | No case |
| AN-16 | Output identity (S-133) | R/X | none | unknown | **KEEP, but** keep the output comparison; flag the hash records | b | ~250 | Holds |
| AN-17 | Paper custody: supply map, grants, capability token, receipts (S-135) | X (aimed at forgery, which is not the threat) | none | unknown | **DELETE**; AN-2's executing replay is the issuance condition | b | ~1,000 | No case |
| AN-18 | Independent recompute (process D3) | R | not run yet | one lane | **KEEP**; make it the release condition with AN-20, and have it re-derive member exclusions from the raw monitor records (battery, outside CPU, thermal, clock) instead of reading the harvest's exclusions | a | 0 | Holds; **scope widened** by AN-6's challenge |
| AN-19 | Blinding (process D4); frozen estimator files and pre-registered arithmetic (D6) | R | SC and L9: it protected the result throughout | a passage in each brief | **KEEP** | — | 0 | Holds |
| AN-20 | Blind dry run of the pinned analysis over the real archives (process D5) | R | not run yet | one run | **KEEP** | — | 0 | Holds |

### 2.4 Merge and CI

None of these rows is on the release path, except where a row protects bytes that the block-5 release reads.

| # | Mechanism (IDs) | Class | Number-touching catches (B3 · SC · L9) | Cost | Proposal | Timing | Lines removed (est.) | Challenge |
|---|---|---|---|---|---|---|---|---|
| MG-1 | Executing test suite: quick, matrix and exclusive jobs (S-196); executing proof legs (S-200) | R | L9: C57 S (two regressions in the S3 head) | CI minutes | **KEEP** | — | 0 | Holds |
| MG-2 | Build, compile, install-the-wheel smoke (S-197) | ordinary engineering | unknown | CI minutes | **KEEP** | — | 0 | Holds |
| MG-3 | Whole suite on the merged tree before a merge (process B4) | R | L9: C57 S; 09-29: 115 failures on a tree every review had passed | 60 to 80 min, plus reruns of 3 to 5 contention-sensitive modules every time | **KEEP, but** fix or quarantine the contention-sensitive modules | a | 0 | Holds |
| MG-4 | Independent executing review by a non-author (process B2; the build seat's own executed audit is the same kind) | R | SC: C11 W, C12 W, C37 W. L9: C59 W, C63 W; plus W-latent C52 to C56, C62 | 30 to 90 min each | **KEEP** (the main R mechanism) | — | 0 | Holds |
| MG-5 | Cold final pass on number code, executing, two model families blind (process B3) | R | B3: C3 W-latent. SC: C22, C24 S. L9: C66 W (Opus, sign error), C67 S | 30 to 60 min each | **KEEP**, restricted to number-bearing code | — | 0 | Holds |
| MG-6 | Final-head rule (B5); integration review (B7); delta re-audit of number-code fixes (B8) | R | SC: C20 W, three blockers, all EXECUTED (B8) | small | **KEEP** | — | 0 | Holds |
| MG-7 | Pre-arm triple audit, three blind seats re-deriving from raw (process B9) | R | SC: C16 W (read), C18 W (executed); C17, C19 S | 3 seats at the highest effort setting, several hours | **KEEP**, once per frozen code change, before block 6's rules are fixed | c | 0 | Holds |
| MG-8 | Six-key merge ledger, keys 1 to 4 and the Impact statement, the PR's short answer to what the change can affect (process B1); light or full tier routing (B6) | X (records the R evidence of MG-3 to MG-7) | through MG-3 to MG-5 | minutes per PR | **KEEP** | — | 0 | Is X (F9): class accepted; kept as the place the R checks are recorded |
| MG-9 | Gate-ledger format checker, a required CI status (S-183) | X | none (process B1: it never caught anything) | a head-SHA edit after every push | **FLAG** (advisory) | a | 0 (code kept) | No case |
| MG-10 | Refusal-site allowlist and census (S-171; process D7) | X, but it is the list "physics refuses" is applied with | none | a fix round each time new code adds a site (K20, K22) | **FLAG**: a generated, non-blocking report | a | data 3,025; test ~1,000 | No case |
| MG-11 | Physics-row coverage map, 460 historical rows (S-172) | X | none | CI | **DELETE** (runtime mentions it only in comments) | a | data 7,605; test 199 | No case |
| MG-12 | Number-row coverage map, 1,674 rows (S-173) | X | none | CI | **DELETE** | a | data 28,989; test 183 | No case |
| MG-13 | Digest-pin registry and `repin`, which blocks every push including docs-only (S-174; process D8) | X | none | K20; S3 and S10 fix rounds | **DELETE**; keep a short check on the four frozen estimator files | a | code ~1,190; data 34,618; test ~285 | No case |
| MG-14 | Single-count source census (S-175) | X | none | CI | **DELETE** (AN-1 keeps the arithmetic invariant) | a | test 1,190 | No case |
| MG-15 | Retired-rationale phrase census (S-176); custody-mode call inventory (S-177) | X | none | CI | **DELETE** | a | code ~530; test ~650 | No case |
| MG-16 | Docs freshness: decision indexes, "Executed evidence" sections, clause maps (S-178, S-179, S-180) | X | none | blocks docs PRs | **DELETE** | a | test ~1,000 | No case |
| MG-17 | State kernel and generated RUN_STATE/queue views (S-181; process F5) | X | none | CI; blocks docs PRs | **DELETE**, if nobody reads `TASK_QUEUE.md` (decision 6) | a | code ~855 | No case |
| MG-18 | Historical receipt semantics fence (S-182) | X | none | CI | **DELETE** the CI step and command; its helpers go with CA-42 | a | code ~80 | No case |
| MG-19 | First-use term ledger (S-184); claims and terms lints (S-185) | X | none | CI | **FLAG** (advisory). The paper's own pedagogy review stays (OP-14) | a | 0 (code kept) | No case |
| MG-20 | Paper supplier-pin census (S-186); comparison and successor mirrors (S-187) | X (S-186 has an executing replay half, which stays) | none | CI | **DELETE** the census and mirrors | a | code ~1,350; test ~1,600 | No case |
| MG-21 | Sealed pack, plan and environment-document freeze tests (S-188) | X | none | CI | **DELETE**. Correction: S-188 (`tests/test_b5_seal_landing.py`) checks the historical seal landing and allows later code changes (`:197-205`); it does not hold block-5 bytes still. The working-tree freeze is L9's `tests/b5_analysis/test_frozen_files.py` (MG-23) | a | code ~200; test ~1,000 | **Fact accepted** (F8): moved from (b) to (a) |
| MG-22 | Fixture signature registry (S-189); import-graph and arm-census import prohibitions (S-190, S-191); reason-code partitions (S-193) | X | none | L9: K22, the import fence failed on the S4 to S9 heads | **DELETE**; keep the orphan-process census (OP-24) | a | code ~360; test ~830 | No case |
| MG-23 | Source freeze tests (S-192) | X, R for the estimator files | none | CI | **KEEP, but** keep L9's `tests/b5_analysis/test_frozen_files.py` (the four estimator files plus the flag, pack and harvest-pin files it lists) until the release; delete the rest, including S-192's calibration-chain pin test (`tests/test_preregistration_chain_digest.py`) | a | code ~250; test ~800 | **Fact accepted** (F8): the kept freeze is named by its actual test |
| MG-24 | Git fixture initialization census (S-194) | X (test hygiene) | unknown | CI | **FLAG** (advisory) | a | 0 | No case |
| MG-25 | Corpus completeness and skip certification (S-195) | R/X | unknown | CI | **KEEP, but** keep the executing-input part; make the skip policy advisory | a | ~50 | Holds |
| MG-26 | The dispatch-only production-proof workflow (D117): its proof-leg registry (S-198); transport custody census (S-199) | X | none | dispatch-only workflow | **DELETE** the registry and the custody census; keep the downloaded fixture's SHA check | a | code ~450 | No case |
| MG-27 | Fidelity sweep of registration text against code (process B10) | R on text | SC: C26 T (73 mismatches, 2,011 statements); one item reached a number through the L9 judge | about 1 h, several seats | **MERGE** into a one-shot check of the arithmetic sentences only, before block 6 is registered | c | (process) | No case |
| MG-28 | Word-for-word text gate on sealed documents (process B11) | X | none | about 1 h | **DELETE**; the orchestrator reads the diff | a | (process) | No case |
| MG-29 | Contamination disclosure and trust-anchor sections in each ruling (process B13) | X | none | 50 to 100 lines per ruling | **DELETE**; one line each | a | (process) | No case |

### 2.5 Orchestration process

These rows are rules for people and agents; none is code, so none is on the release path. "Lines removed" is
not estimated for them.

| # | Mechanism (IDs) | Class | Number-touching catches (B3 · SC · L9) | Cost | Proposal | Timing | Challenge |
|---|---|---|---|---|---|---|---|
| OP-1 | Two-seat consult before the next arm; the threshold council (process A6) | R/P (finds physical causes by counting) | SC: C36, C39, C42, C44 S (causes found: corpus margin, unrecorded sources, the 12:53 batch, staleness). L9: C50 S; C68 W (next block's design) | 10 to 30 min each | **KEEP** | — | Holds |
| OP-2 | Refuter paired with a ruling, executing (process A2) | R | B3: C5 W (a prefill-length pin could be taken from a session that did not qualify). SC: C31 W (do not bind the ~1 J floor); C45 S | 20 to 40 min | **KEEP** where a ruling bears on a number | — | Holds |
| OP-3 | Cold judge per rule change (process A1) | R when it executes, X otherwise | B3: C4 T/N. SC: C27 S, C36 S. L9: C49 S/T, C51 S/N; K27 (the L9 judges missed two defects later found by running code, and ruled one question wrong). No W in any period. The 10-13 audit: blind Opus re-rulings were never worse and better in 2 to 4 of 10 | 10 to 60 min plus charge writing; each ruling starts a build | **MERGE** into OP-2 plus a one-line orchestrator decision (OP-10). This changes doctrine Gates 2: decision 3 | a | No case |
| OP-4 | Seal: digest tables, seal conditions, landing lane, re-seal restarts the block (process A4) | X with an R core (rules fixed before data) | SC: none of its own (K7: self-defects that would have removed every session) | about 30 h with the errata; a re-seal restarted the block at ALPHA | **MERGE** into "the registration and analysis plan are committed in one dated commit before the first session" | a | No case |
| OP-5 | Erratum chain: draft, refuter, judge, corrections, text gate, new harvest pin (process A3) | X with an R core | only through OP-2 and OP-3 | the three block-5 errata took about 10 h (corpus), 3 h (sources) and 3.5 h (staleness) | **MERGE** into one recorded orchestrator decision plus one executing check when it bears on a number (threshold note section 9, last paragraph) | a | No case |
| OP-6 | "Prospective only": a corrected rule may not be applied to a completed session (process A5) | X | none; K14: it kept BETA a1, a4 and a5 out after a same-day cure | 2 to 3 sessions | **DELETE** for block 6. Block 5: decision 1 | a | No case |
| OP-7 | Cold judge when a consult splits on a science question (process A7) | X unless it executes | SC: started the corpus-18 chain (C36, S) | about 10 min | **KEEP**, science splits only; the judge runs the disputed arithmetic | — | **Is X, accepted** (F9): executing is what makes it R; only executing seats have W catches |
| OP-8 | Four-model council (process A8) | X | none (never run) | 0 | **DELETE** from the council skill | a | No case |
| OP-9 | Rehearsal of real programs over real-shaped data | R | SC: C14, C15 S (each would have refused every session). L9: C65 S (the nine S10 defects, found by running the real programs on a real archive) | rounds of hours | **KEEP** (requirement 5) | — | Holds |
| OP-10 | Orchestrator decisions, one recorded line each (process A10) | decision record | n/a | cheap | **KEEP**; this is where deleted X gates go | — | Is X (F9): agreed; kept as the decision record |
| OP-11 | WRITE_SCOPE fences, which limit the paths a seat may write (process E1) | R on estimator files, X elsewhere | none outside the estimator files | L9: 12 of 47 seats stopped at a fence, 30 to 60 min each (K22) | **KEEP, but** fence the estimator and pinned files; for build seats, list the module, its tests and every registry it joins | a | Holds |
| OP-12 | Bridge envelope: a seat's report must start with a parseable JSON header (process E2) | X | none | K19: rc=65 on every consult; the bodies were complete | **FLAG** when the body is complete | a | No case |
| OP-13 | One writer per working tree (E3); hand-forward file and stall watcher (E5); invocation manifest while automatic (E4) | P-adjacent / X | operational (E5 prevented a repeat of the 6.5 h stall) | small | **KEEP** | — | Holds |
| OP-14 | Pedagogy review of the registration and internal records (process B12) | X | none | about 40 min on the seal's critical path | **DELETE** for registrations and records; keep it for the paper and owner-facing prose | a | No case |
| OP-15 | Delegation-calibration ledger (process E6) | X | none (not applied) | — | **DELETE** | a | No case |
| OP-16 | RUN_STATE top block (process F1) | X | none | 6,831 lines, read and extended by every activation | **MERGE** into the session record; RUN_STATE becomes one screen: state and next action | a | No case |
| OP-17 | Per-activation records (F2); session record and trace appendix (F3) | X | none | about two thirds of main's commits since 10-07 | **KEEP, but** one short record per session (plan, verdict, codes, physical readings); drop step narration and the unfilled appendix sections | a | Is X (F9): agreed; kept as the session record |
| OP-18 | Decision log and council log (process F4) | X | none | 12,234 and 3,959 lines | **FLAG**: keep the decision log; stop council-log entries | a | No case |
| OP-19 | Stop cards (F6); credential-boundary push hand-off (F10) | X | none (F6's directory does not exist) | — | **DELETE** (F10 shrinks to two lines) | a | No case |
| OP-20 | Retired-but-still-written global-skill text: D-080 sweep, spend tallies, post-workload reassessment, Fable-authored traces, one-new-artifact rule, counterreview doctrine, magistrate/lieutenant pointer (process G1 to G7) | X | none (retired 09-29) | misleads seats that load the skills | **DELETE** the text (Ed's global files: decision 8) | a | No case |
| OP-21 | Email rules (F9); the pruning rule at session end (F8) | communication / meta | n/a | small | **KEEP** | — | Holds |
| OP-22 | Restricted reading in briefs (the structure-only rule) | R (blinding) | protected the result | a passage per brief | **KEEP** until the release | — | Holds |
| OP-23 | Two-seat councils (doctrine Gates 4) | R | as OP-1 | as OP-1 | **KEEP** | — | Holds |
| OP-24 | Session-end fixture orphan census (F7) | P (orphans add load) | unknown | seconds | **KEEP** | — | Holds |

## 3. How the line counts were estimated

- Per row I started from Sol's estimate in `CODE-INVENTORY.md` and kept only the part the proposal removes.
  - **FLAG**: about half to two thirds of a record-check's code goes; recording a finding needs less than
    authenticating it.
  - **KEEP, but ...**: zero, or only the named leg.
  - **MERGE**: the merged-away part.
- **CA-42**, the retired arm code. The files total 24,610 lines: `arm_readiness.py` 13,126,
  `arm_readiness_evidence.py` 3,677, `arm_readiness_evidence_t0.py` 2,603, `t0_rehearsal.py` 2,008,
  `v5_qualification.py` 1,090, `night_agent_install.py` 1,482, `arm_retry.py` 405, two author scripts 219.
  I subtracted about 2,000 lines of helpers that live rows still use (the pack-tree digest and launch-lineage
  locators, per correction 3 of the code inventory), about 550 lines of physical probes that move into
  `hazards/`, and a margin for code that `evidence_night.py` and the watchdog still call. That gives about 17,000.
  The range is 14,000 to 22,000 because I did not trace every call.
- Sums of the code column by area: collection and arming about 26,300 (of which CA-42 is 17,000 and CA-38 is
  3,500); harvest about 5,900; analysis about 10,100; merge and CI about 5,300. Total about 47,700. Helpers shared
  between rows are counted in each row, so the true figure is probably lower. I give 35,000 to 60,000.
  After the challenge: about 47,100. The kept legs of HV-19, HV-21, AN-3, AN-5, AN-8 and AN-14 lower the total by
  about 670 lines, and CA-15 and HV-16 add about 45; MG-21 moves about 200 lines from (b) to (a) and CA-21 about
  100 from (c) to (b).
- Data lines: the four census registries, 74,237 lines (MG-10 to MG-13).
- Test lines: about 8,700 that test only the deleted censuses and fences. Not estimated: the 99 test files
  (114,924 lines) that name a retired arm module.

## 4. What must stay, and why

**Physical checks (P).** They stay because doctrine (2026-10-05) lets only a physical hazard measured directly
stop collection, and because they are the only checks that keep contaminated energy out at the moment it happens.
- Arm and t0:
  - clock frequency and drift (CA-1);
  - battery float (CA-2);
  - thermal pressure (CA-3);
  - free disk (CA-4);
  - the sampler sampling (CA-5);
  - contention dwell (CA-6);
  - the agent census at arm (CA-7).
- Live:
  - the member runtime cap (CA-8);
  - the watchdog clock check (CA-9);
  - measured idle admission (CA-10);
  - recovered idle power (CA-11);
  - the meter (CA-12).
- At harvest, member by member:
  - battery replay and the charge accumulator (HV-15);
  - thermal and clock steps (HV-16);
  - outside-process overlap (HV-17).
- Recorded catches: C32, C33 and C34 (P-protective), CA-5's two rehearsal refusals, and C43 (the sleep).
- Several of them need resizing, not removal: CA-7, CA-9, CA-10 and CA-16 (the alignment screen), each sized
  under requirements 1 and 2.

**R mechanisms, with the catch that justifies each.**

| Mechanism | Why it stays: the catch |
|---|---|
| Independent executing review (MG-4) | C63: 32 auxiliary runs of another model were pooled into the printed median, range, spread and band. C59: a second spelling of the archive path dropped every drift allowance. C11: a member measured while charging would have been kept. C12: drift-bound members dropped for reasons unrelated to their energy. C37: the bound fell back to the uncapped member set. |
| Executing cold pass on number code (MG-5) | C66: the decision interval printed 2.8011 for an estimate of -2.8011. The review before it had flagged the line as untested but had not found the defect. |
| Pre-arm triple audit (MG-7) | C16: the reported-energy issuer averaged all 50 members, excluded ones included. C18: a reference excluded for contention kept its influence on the drift allowance (executed: 30 J of contamination passed the screen). |
| Delta re-audit of number-code fixes (MG-6) | C20: the wrong allowance bracket consumed; a wrong-model spare in the screen; an unscreened session admitted. |
| Refuter on a numeric ruling (OP-2) | C5: a prefill length pinned from a session that did not qualify would have set the prefill length of every pack built on it. C31: binding the ~1 J floor would have printed a floor the instrument does not have. |
| Two-seat consult and threshold council (OP-1) | C68: the 74.5 ms bound is about 92 ms; a +10% decode-length loophole is worth about 5.2 J; unseen GPU contention adds 6.2 J to a prefill. These numbers are for block 6's design. The consults also found the physical causes of four lost sessions. |
| Rehearsal of real programs (OP-9) | C14, C15, C65: each found a defect that would have refused every session (S). No W, but a session lost to a guard is a lost number. |
| Whole suite on the merged tree (MG-3) | C57 (S), and the 09-29 tree with 115 failures that every review had passed. No W recorded. It stays because it is the only full execution before a merge. |
| Unit selection and reference exclusion (AN-3) | It is the code that the C63 and C18 fixes live in: it is what keeps another model's runs and contaminated references out of the statistics. |
| The arithmetic of the instrument and estimators (CA-15, HV-2, AN-1) | They are the measurement. Their recompute checks (S-051, S-083, S-085, S-119, S-120, S-132, S-138) are the R that the X checks around them were meant to protect. |
| Blinding, the blind dry run, the independent recompute (AN-18 to AN-20, OP-22) | The independent recompute has no catch yet, because it has not run. It is the one mechanism aimed squarely at the owner's threat, a confident wrong number. The record above says only code run by a second party has caught such numbers. |
| Arithmetic fixed before data (the R core of OP-4; HV-8; HV-10's value comparison; frozen estimator files, AN-19 and MG-23) | It protects the result itself. It needs one dated commit, not a seal. |
| Which data a number is computed from (added by the challenge: HV-19's corpus recompute, AN-5's attempt history, AN-3's target-cell tripwire, AN-8's union maximum, AN-14's finalized-floor identity, HV-21's executed-stack identity) | No recorded catch; each keeps one comparison for which Sol gave a concrete input that the remaining recomputes would pass while the number came from the wrong members, session, floor or configuration (section 1.1). |

**Kept although X**, each for a stated reason:
- the launch race guard (CA-23), which is cheap and prevents two writers;
- the chain-digest flag (CA-24), already only a flag;
- the STOP file and the arm notice (CA-30, CA-49), which are Ed's controls;
- the executed-stack identity exclusion inside HV-21 (model bytes, runtime, kernel library, quantization,
  tokenizer): an energy measured on another model or runtime is not a measurement of the pack's configuration, and
  C20 A2 shows the case arises;
- the attempt-history and finalized-floor comparisons (AN-5, AN-14), which decide which session and which floor a
  number is computed from;
- the cataloged-effect check (HV-8), which "flag, the plan decides" depends on.

## 5. Which deletions change what a reader of the paper's methods section is told

**Block 5's paper.** None of the (b) proposals changes block 5's numbers if, as proposed, they are made after the
release. Block 5's paper reports the exclusions as registered (registration sections 6.3 to 6.5).
- **Not done after the release, therefore:** OP-6 (prospective only) and the HV rows that would have kept BETA
  a1, a4 and a5. Applying any of them to block 5 is a deviation from the registration. The methods would then
  have to say that a second, labelled result includes three sessions that the registered rules excluded, and
  that this choice was fixed before anyone saw a number. Decision 1.
- **Changes to how block 5 was verified,** if Ed accepts decision 2:
  - The methods would say the numbers were released after a blind dry run and after an independent recompute
    from raw power records agreed. Today the registration (section 8) says the release follows a cold gate.
  - It would say who verified the analysis code (MG-4, MG-5).
  - The triple audit (registration 9.1) stays as described.

**Block 6's paper.** Its methods would differ from block 5's in these places:

| Change | What the reader is told instead | Registration section it replaces |
|---|---|---|
| Seal and errata merged into a dated commit (OP-4, OP-5) | "The registration and analysis plan were committed on <date>, before the first session; later changes are listed with their date and reason." No seal, seal record or addenda | 10, 11, 12 |
| Cold judges replaced by a refuter plus an orchestrator decision (OP-3) | Rule changes were checked by an independent seat that ran them | 10 |
| Record checks become flags (CA-17, CA-22, CA-26, HV-6, HV-19 to HV-26, AN-5, AN-6 and similar) | "Only a directly measured physical hazard removed a session or a member. Record conditions were written as flags; the plan named which flags exclude, and results are printed with and without flagged sessions." | 4.7, 6.5, 6.10, 6.11 |
| `code.executed_differs_from_sealed` and `pack.identity_mismatch` become flags (HV-23) | The executed commit and any changed paths are reported per session; a session run on number-bearing acquisition or reduction code that no executing review covered is excluded by a named flag | 6.5, 11 |
| Calibration staleness (CA-40) and the alignment screen (CA-16) | "The calibration bound was carried into the operative bound and was not used as a screen," and the staleness rule is stated in milliseconds | 0.11, 5.1 |
| The ledger becomes a list read by content (CA-38) | A simpler description of how captures are stored | 0.11 |
| The agent census mid-session becomes pause and flag (CA-7) | How an interruption was handled; members that overlapped an agent are excluded | 4.5 |
| Corpus size set by replay and joules (HV-18) | The rule and its sizing | 5.3 |
| Prospective-only removed (OP-6) | Corrected rules are applied to all sessions, and the result under the original rule is printed beside it | 7.2, 10 |

**No change to the methods** from the merge and CI deletions (MG-9 to MG-29), the process deletions
(OP-8, OP-12 to OP-20), the retired arm code (CA-42, CA-44), or the record-keeping rows. A reader is not told about
those today.

## 6. Decisions for Ed

1. **Block 5's BETA a1, a4 and a5.** Should they appear in a second, labelled result? The three were removed by
   rules that were rewritten afterwards; a5 has no physical objection on the records, and a4 also lost 4 runs to
   a sleep. If yes:
   - decide before the release, while still blind;
   - it needs an L9 change and a re-verification of L9.

   If no, block 6 replicates instead. My lean is no: block 6 gives clean sessions under the new rules without a
   post-hoc deviation in block 5's paper.
2. **The release condition.** Make it the blind dry run plus agreement of the independent recompute, as an
   orchestrator act, in place of a cold gate. This changes doctrine Gates 2 for claim-bearing results.
3. **Cold judges per rule change.** Replace them with one executing refuter plus a recorded orchestrator line.
   This changes doctrine Gates 2. The record: no cold judge produced a W catch in three periods.
4. **The agent census mid-session.** Pause and flag instead of stopping the chain. Doctrine item 6 lists the
   stand-down fence as kept as-is.
5. **Tag the release tree.** If the block-5 release and the independent recompute run from a tagged copy of
   the L9 tree, the (c) rows can start now, in parallel with the release work. If not, every (c) row in a module
   the release imports waits for (b).
6. **`TASK_QUEUE.md` and the state kernel.** Does anyone read them? If not, delete MG-17 and the queue.
7. **The arm notice's "no install if neither Gmail nor GitHub reaches you" refusal.** Keep it or flag it?
8. **Your global files.** Delete the retired skill text (OP-20). In `~/.claude/CLAUDE.md`, add the exclusion of
   registrations and internal records from the pedagogy standard.

## 7a. Orchestrator decisions (02:57 PDT 2026-10-14, before any block-5 number is seen)

Ed, 2026-10-14: "the only doctrine is good science"; and on my decisions, that they "often seem to be" over-engineered. So each decision below takes the lightest form that keeps the science sound.

1. **BETA a1, a4 and a5: yes, as one labelled line, at no cost to the release.** The registered result stays primary and unchanged. Beside it, one line labelled "including three BETA sessions removed by rules later rewritten" prints the BETA floor quantities with them included, each session's flags listed. It is computed after the release by the independent recompute (no L9 change, no re-verification, no delay). Reason: section 9 requirement 4 of the threshold note (flagged sessions printed as a labelled line), and it adds BETA sessions on other days at no machine cost. Fixed now, while blind.
2. **Release condition: yes.** The release happens when the blind dry run passes and the independent recompute agrees with L9 within a tolerance fixed before release; no separate cold gate. The two-model final look on the L9 code at merge stays (it is about the code, not the release).
3. **Cold judges per rule change: yes**, replaced by one executing refuter and a recorded orchestrator line.
4. **Agent pause: done** (Ed, 02:26).
5. **Tag the release tree: yes.** The L9 merge commit is tagged; the release and the recompute run from the tag; (c) rows may then start in parallel.
6. **TASK_QUEUE.md and the state kernel: delete**, after the L9 merge, with the references to them in CLAUDE.md and the playbook. RUN_STATE is the pointer.
7. **Arm notice refusal when no channel reaches Ed:** Ed's control; asked in the morning email. Unchanged until he answers.
8. **Ed's global files:** the retired skill text (OP-20) is removed by me; the sentence for `~/.claude/CLAUDE.md` is Ed's to add, offered in the email.

Execution order: (a) rows that touch no file the L9 lane edits, and every process row, after the L9 merge (to avoid conflicts with lane branches); (c) rows from the tag in parallel with the release; (b) rows after the block-5 numbers and the recompute agree.

## 7. Uncertainty

- **Never fired.** Catches are "unknown" for every check with no record of firing (most P checks; many X
  checks). Unknown is not zero. Sol's code inventory says only that no inspected comment, test or document showed
  a catch. Because of blinding, result documents were not read, so a catch recorded only there could be missing.
- **Line counts.** They are gross and overlap; section 3 gives the method and ranges.
- **Release path.** The import closure is static. A module loaded by name at run time would be missed, and
  `night_gate.py` names `arm_retry` without the scan finding an import.
- **Timings.** They assume the block-5 release imports the L9 tree at `730842e05` plus its remaining stage S10
  fixes. If S10 adds imports, more rows move to (b).
- **Counts.** They are by proposal row. Several rows group mechanisms; the IDs in each row say which.
