# Registration V5-CLAIM-25G83-B5: the first claim-bearing `_v5` windows (measurement block 5)

Status: **Revision 12, 2026-10-07.** This is the text that is committed at the seal, in the **seal commit**: the
one commit made directly after the last commit that changes anything a window reads, carrying this file's final
bytes (the list of companions below says why the seal needs a commit of its own). It is sealed when the
**seal record** of §12, the file that lists the SHA-256 of every
sealed file (`FILL[B5-SEAL-RECORD]`), exists and pins this file's SHA-256; until that record exists it binds
nothing. Written by Opus 5.5, as lane L6 of the gate-prune workflow
(revision 3, commit `71c91d74`), then as the registration-sync side lane (revision 4, last commit `7261a585`), then
as the REG lane of gate-prune round 3 (revision 5, last commit `9d63b4df`), then as the REG sync to the frozen head
(revision 6, last commit `c6843537`), then as the REG sync to the audit fixes and the NEG-8 ruling (revision 7, last
commit `dc046d4d`), then as the REG final pass to `43ac12d0c`, at that time the candidate for H_claim (H_claim is
the last commit that changes a file a window can read, so every block-5 window runs the bytes it holds; one data
file is excepted, the pin of the calibration ledger, which advances after each window; §0.18 and §11; revision 8,
last commit `30d92227`), then as the REG sync to the int5 head `fe28e5a0c` (revision 9, last commit `bc8ad4ae`),
then as the REG preparation pass that read the merged census interpreter rule at the int5 head `9b0c680ed`
(revision 10, last commit `1d97f0a60`), then as the correction pass that followed a comparison of these
documents with the code at
that same head (revision 11, last commit `7c19c9c79`; "What changed in revision 11" below describes the
comparison), then as the pass that wrote in the rulings of the first stage of the seal gate (the independent
ruling that seals this file, given in two stages; §0.1, §12) and the procedure by which the seal is committed
(revision 12; "What changed in revision 12" below), on
branch `design/2026-10-05-v5-claim-block-draft` (revision 2 is commit `bfd1ee8c`). Unsealed, this file authorizes no
arm (the **arm** is the sequence of checks, run at a window's scheduled start, that decides whether its collection
begins; §0.15), no launch and no analysis. It binds only when the seal gate (one cold gate, §0.1, run in two stages,
§12) seals it together with three companions in the same directory:

- `analysis_plan_block5.md`, the **analysis plan**: what is computed from the collected bytes, and how;
- `flag_catalog.json`, the **flag catalog**: for every flag code, whether it removes a member from the claims,
  removes a whole window, or is only disclosed (§6);
- `sealed_inventory.json`, the **sealed inventory**: the SHA-256 of every tracked file of the code (`joulewise/`,
  `scripts/`) and of the three packs, and of the flag catalog, as one named commit holds them. That commit is
  H_claim, and every window runs those bytes (§0.18, §11). The inventory names H_claim, and a file cannot name the
  commit that contains it, so the filled inventory is committed one commit after H_claim, in the **seal commit**,
  together with the final bytes of this file and of the analysis plan. At H_claim itself the inventory is an empty
  stub (§0.18).

A **FILL** is a value that must be tied to authenticated bytes before the point named in §13. It is never a
default. Until the value is written, a marker stands in its place: the word FILL followed by the value's name in
square brackets. Revision 12 leaves markers of six names, because each names a value that exists only once H_claim
is fixed. Each marker stands exactly where its one value goes, so filling it replaces the marker and changes no
other word. The six names (written here without the marker form, so that this list is not itself filled):

- `H-CLAIM`: the 40-character name of the commit H_claim (§2 item 1).
- `B5-FINAL-HASHES`: the SHA-256, computed at H_claim, of the one file that the marker's sentence names. In
  earlier revisions this marker followed a digest computed at an earlier integration head, as a note to compute it
  again at the last one: revision 8 recomputed every such digest at `43ac12d0c`, revision 9 at `fe28e5a0c` (only the
  identity pins had changed, §4.6 item 3), and revision 10 found each unchanged at the int5 head `9b0c680ed` (§13).
  Those digests stay in the text, each with the head it was computed at, beside the marker for H_claim's value.
- `B5-SEAL-SEATS` and `B5-SEAL-RECORD`: the seats of the seal gate (a **seat** is one model session working to a
  written brief, §0.1), and the repository path of the seal record (§12).
- `B5-PLANS-REGENERATED` and `B5-RELEASE-EVENT`: these two values come into being only after the seal commit (the
  window plans are written from the sealed text; the release event is recorded after the block has closed), and
  this file's bytes may not change after the seal commit (§0.18). So neither is ever written here: each is a named
  section appended to the seal record (§12), and the marker stands where the name of that section goes.

No claim-eligible `_v5` energy exists at this writing, and none was read (§16).

**What changed from revision 2.** On 2026-10-05 Ed ruled that arming refuses only on a physical hazard, measured
directly, and that every other check becomes a recorded flag (Ed: "this again feels like in ability to prune silly
gates that prevent data collection for the sake of semantics not science"). Revision 2 let a window start only
after a chain of receipts verified, and discarded a whole window when one member failed. Revision 3:

1. refuses a window before it starts only on a measured physical hazard (clock, battery, thermal pressure, a
   competing process, free disk, the sampler) or on the agent census (a check that no AI agent session is running
   on the machine), which doctrine keeps (§4);
2. turns every other check into a **flag**, a recorded fact that never stops collection; the sealed flag catalog
   decides which flags remove a member or a window from the claims (§6);
3. has the harvest (the desk program run after each window) always emit the numbers plus the flags. A window is
   **claim-usable** when no window-removing flag fired and each reported number still rests on at least 5 of its 10
   planned independent repeats and 5 of its 10 planned groups of four interleaved members (§0.8, §6.6). (Revisions
   3 to 11 set this minimum at 8; the seal gate set 5, revision 12 list, item 1.) Each pack's
   analysed window is its first claim-usable attempt (§7.2);
4. folds block 4, the separate qualification window, into block 5: G10, a deliberate clock step that shows the
   clock check can see one, runs as a recorded diagnostic at the tail of the first ALPHA window (§3).

§15 maps each item of the approved implementation plan (`/Users/edr/night-archive/gate-prune/PLAN.md` §6, items
1–15) to the section that carries it.

**What changed in revision 4.** This revision brings the text into line with the integrated code (branch
`feat/2026-10-05-gate-prune`, commit `f8164893`). No threshold changed except by the timing ruling of item 6.

1. §5.3: each window starts with 12 reference runs, the NEG-8 corpus, from which a drift bound is derived (§0.12). A
   window in which only 10 or 11 of them succeeded no longer loses that bound: the harvest validates the bound
   against the members actually collected and re-screens the window against it (§14 Q1 closed).
2. §4.6 item 3: the pins that fix which model files and runtime versions may be measured live in
   `identity_pins.json` in this directory, not in the packs' plan trees.
3. §6.3, §6.5: the whole-window verdict (one pass/fail record over the whole window, §0.17) stays disclosed rather
   than window-removing, but each member it fails is now removed by a new member code,
   `member.whole_window_member_failure`. Without that code, revision 3 had dropped the check that the displays stayed
   asleep and the screensaver off through each request, which decision D-078 (item 4) installed after a screensaver
   contaminated captures in July 2026. Also, `calibration.ledger_snapshot_refused` now removes the window: the
   calibration bracket is judged from that same ledger, so the bracket check already fails with the same reasons.
4. §5.5: the sizing output is filled in, and revision 3's claim that a generous window deadline costs nothing is
   withdrawn. The supervising watchdog treats a window as running until its scheduled start plus that deadline, which
   is about 15 h after a normal chain ends (§14 Q8).
5. §1, §4.2, §5.6: the boundary label and the backup destinations are filled in. The backups sit on the same disk
   volume as the collected data, so the disk check at arm counts three copies of the window's bytes there, not one.
6. §0.3, §0.6, §0.13, §2, §4.6, §5.1, §5.5: the cold-judge timing ruling of 2026-10-06
   (`/Users/edr/night-archive/gate-prune/timing/RULING_fable_cooldown_2026-10-06.md`). The cooldown now starts the
   next member at the first 5 s reading at or below twice the previous member's idle baseline (was: 30 s within
   10%), under a new block-5 policy file; the idle baseline is 576 records, about 75 s (was 750 records, about
   98 s), with the admission tests unchanged; all eleven settles are 60 s (was 180 s); a battery-temperature
   diagnostic is added as a disclosed flag; and one 15-minute machinery smoke of the new cooldown is required before
   the seal. The packs, the identity pins and the sizing output were regenerated.

**What changed in revision 5.** This revision registers every decision of 2026-10-06 that changes collection or
claim use, checked against the integration head `b9d02700a` (branch `integrate/2026-10-06-gate-prune-3`, whole suite
green). A last code round (P3: lanes `lane/2026-10-06-p3-{harv,haz,drv,wd}`) is in flight; where this text describes
behaviour that only P3 installs, it says so, and the item is listed under §13 as a sync point to check before the
seal. Lane names (P2-…, P3-…, L10) and design-row ids in parentheses (PLAN2 row 8, core-prune A14, interface J1) are
citations for tracing a rule to the record that motivated it; no rule here depends on them for its meaning.

1. **Battery** (§0.17, §4.2, §6.4, §6.5, §9.2): the battery current is read from the SMC (the Mac's power
   controller) once a second instead of from the battery registry, which republishes only once a minute. The battery
   supplying part of the load while the adapter is connected and the battery is not charging ("assist") is now
   disclosed (`battery.assist`), not excluded; charging, loss of AC power and missing evidence still exclude. The same
   rule applies to calibration captures. The arm refusal is unchanged. The orchestrator's ruling of 2026-10-06
   (`/Users/edr/night-archive/wallmeter-probe/verify/RULING_battery_assist_2026-10-06.md`) and its reasons are in
   §9.2.
2. **Whole-machine meter** (§0.17, §1, §6.8; analysis plan §8.2): an inline USB-C power meter records the Mac's
   DC input at 50 samples per second. It is a recorded diagnostic with a pre-registered descriptive analysis. It never
   refuses, excludes or enters a claim number.
3. **Timing** (§3, §4.1–4.3, §5.1–5.5, §10): stand-down leads of 180, 90 and 60 s; operator countdowns of 0 s
   except at the post calibration (the fifth registered deviation); a contention dwell (the wait at the arm that
   ends once the machine has shown no competing process for that long, §4.2) of 180 s instead of 600 s; a
   collection deadline that keeps the post calibration inside the 24 h calibration horizon; one retry of the NEG-8
   corpus; a 1,800 s cap per member; strict validation (the full check of a member's files: they are complete and
   well formed, and the stored summary equals a fresh reduction of the raw records; §0.12) moved to the harvest; the
   calibration refit done once per
   window; the watchdog releasing a finished window at once; the sizing and the expected chain re-derived.
4. **Yield tripwire** (§5.7, §7.3): the driver counts collected bundles per stage and at the window's end, flags
   empty and short stages, and gives the window a yield status; a process rule stops a deterministic loss from
   repeating through back-to-back windows.
5. **Checks that now record instead of refusing** (§5.3, §6.10): the NEG-8 corpus drop rule (one closed list shared
   by the mint and the harvest), physical timestamps for the NEG-8 bound's age, the power-supply and OS-build
   strings disclosed, the cooldown fallback reference, and the records of the controller (the program that runs
   one member, §0.3), of the fiducial writer and of the reservation.
   Historical calibration custody is re-verified at the harvest, and a mismatch removes the window. The arm's one
   identity refusal, an OS build and machine model that no acceptance judged, is registered (§4.7).
6. **GAMMA's interior references** (§0.7, §0.12, §2, §4.6, §5.1, §5.5): lane L10's erratum is applied.
7. **Era pins** (§11 item 5): two older documents' digests are records of their era; the block's live pins are the
   sealed inventory at H_claim.
8. **Catalog** (`flag_catalog.json`): `battery.assist` (DISCLOSE), `calibration.historical_custody_mismatch`
   (EXCLUDE_WINDOW) and `calibration.historical_custody_unmeasured` (DISCLOSE) are added; the battery notes follow
   the ruling.

**What changed in revision 6.** Revision 5 described several rules "as P3 will install them". The P3 round, lane
L10, a **refusal census** (a sweep that listed every place the code can refuse, stop or exclude, and turned each one
that was not physics or number protection into a flag) and an integrator's triage of what the census found have
since been merged into one **frozen head**: the commit the integration stopped changing so that the review gates
before the seal all judge the same bytes. It is commit `a434e363d96621318657418e60b8d14410079d82` (branch
`integrate/2026-10-06-gate-prune-4`; whole suite run at that commit,
`/Users/edr/night-archive/gate-prune/FROZEN_HEAD.md`), and it is the candidate for H_claim (§2 item 1). This
revision reads that code and makes the text
say what it does. Where the code chose differently from revision 5, the text now follows the code; each such place
is listed here and in the sync record of §13. No registered threshold changed.

1. **Battery** (§4.2, §6.3, §6.4, §6.5, §9.2): assist is now **any** negative battery current read from the SMC,
   not only one below −200 mA; −200 mA is the threshold the assist report counts reads against. The
   charge-accumulator test keeps its own code, `battery.accumulator_excursion`. The assist report splits a member
   into the code's three phases: before the measured request, the request, after it. A calibration capture's assist
   is `calibration.capture_battery_assist`. A member's #421 pair (the battery registry read just before and just after
   its sampler stream) that failed on discharge alone is disclosed when the SMC reads cover the member. With SMC
   coverage, a hole of more than 120 s between registry reads of the charging and AC state makes the member
   `battery.unmeasured`.
2. **Desk order** (§2, §4.6 item 6): the **pin advance** (the pin-only commit that moves the repository's record of
   the calibration ledger's tip to this window's last entry) now comes **before** the harvest, not after it, because
   the program that writes the whole-window verdict at the desk reads the ledger through that committed record.
3. **Clock** (§4.2): a clock sample whose three reads took more than 250 µs is read again, up to five reads in all
   (the first and at most four more); when all five took more than 250 µs the sample is unmeasured, never a step
   (the FILL `P3-CLOCK-SKEW-BOUND` filled).
4. **Driver** (§0.17, §2, §5.4): the monitor and meter stop at least 5 s after the chain exits, after G10; the
   pre-launch lineage check records a mismatch (`records.lineage_prelaunch_mismatch`) and refuses only when the
   machine rebooted since the lineage was published.
5. **Records that no longer remove anything** (§6.3, §6.8, §6.10): `member.stderr_uncopied` is disclosed; an
   exception inside the member environment guard's collector is disclosed (`env.member_guard_flagged`, finding
   `collector_raised`); a historical calibration capture whose bytes changed removes the window only when this
   window's acceptance relies on it (`calibration.historical_custody_mismatch_unused` otherwise).
6. **A new window exclusion** (§6.5): `whole_window.member_failures_unreadable`, when a verdict that did not pass
   cannot name the members it failed.
7. **Which refusals may remain** (§6.11, new): every refusal left in the code is either physics or the protection
   of a number, and a test enforces the list.
8. **Fills** (§2 item 7, §2 item 8, §13): the cooldown smoke record, the P3 sync record and the sizing and pin
   digests at the frozen head.
9. **Smaller corrections:** the meter's restricted record is one file, `withheld/meter.json` (§5.8); G3, the desk
   provenance checker `scripts/check_window_provenance.py`, does not run on the floor packs, that is, on ALPHA and
   BETA, the two one-model packs from which the detection floors are estimated (§2 item 7, §6.8); GAMMA's
   battery-assist line is adopted (§14 Q9 closed; analysis plan §8.1).

**What changed in revision 7.** After the frozen head, the pre-arm audits (§9.1) and a Fable cold pass found defects
that two fix lanes (`lane/2026-10-07-audit-fixes-1`, `01232742e`; `lane/2026-10-07-audit-fixes-2`, `0571cf8fd`) and
one ruling lane (`lane/2026-10-07-neg8-survivors`, `2011ec285`) repaired. All three are merged in the integration
branch `integrate/2026-10-07-int5`, whose head at this writing is `d3c107f2f` (`/Users/edr/code/JouleWise-wt-int5`).
This revision makes the text say what that code does. The finding labels in parentheses (A1, F3, N4, item 6) cite the
audit or cold-pass record a rule came from; no rule depends on them for its meaning.

1. **Lost NEG-8 references** (§0.12, §5.1, §5.3, §5.5, §5.7, §6.5; analysis plan §2.4). *Forcing problem:* the
   screen accepted exactly 3 start, 1 midpoint and 3 end references, so one start reference aborted by idle admission
   made the counts (2, 1, 3), which the screen called invalid, and the whole window was removed (Opus audit F1); and a
   reference whose request overlapped a competing process removed nothing, although its energy entered the screen and
   the allowance (Astra audit A1). A cold ruling of 2026-10-07
   (`/Users/edr/night-archive/gate-prune/neg8-council/RULING.md`) replaced the exact-count rule: a lost reference is
   dropped, each reference stage gets one retry from
   pre-registered spare members, the screen runs on the survivors (at least 2 at each endpoint) against a bound sized
   to the surviving counts, and a corpus member with a physics exclusion is dropped from the bound. Two disclosed codes
   are added, `neg8.reference_lost` and `neg8.midpoint_lost`; the analysis plan makes the second claim-excluding for
   GAMMA's primary contrasts. The first fix lane's interim answer to A1, a window exclusion for any physics flag on a
   reference, is superseded by the ruling: its flag code was deleted from the harvest, both catalogs and the allowlist.
2. **An unread hazard probe at the arm** (§0.15, §4.1). UNMEASURED now refuses only for the instrument; for the
   other five hazards it is the disclosed flag `<module>.arm_unmeasured`, because the monitor measures those hazards
   over every member span anyway (audit A3).
3. **The agent census** (§4.5, §5.1, §5.7). A listed process counts only when its executable is an agent's, and the
   window's own process tree is ignored, so a run id containing "t3" no longer stops a window (Opus audit F3; the
   census then also searched command lines for `t3`, the name of T3 Code, an agent harness that was used on this
   machine to run agent sessions and that revision 9 removes from the census). In the
   window an unreadable census is disclosed and never stops the chain (audit A3).
4. **No code is permanently unclassified** (§6.2, §6.10). A flag line that fails validation is disclosed, with an
   exclusion beside it when the line could have been one (Opus audit F2).
5. **Smaller code changes:** the monitor's clock skew bound follows the plan's step threshold (§4.2); the monitor and
   the meter stay supervised during G10 (§5.4); an unusable pack inventory refuses before launch (§0.17, §6.11); the
   exclusion function resolves bundle ids (§0.16); the powermetrics digest is re-derived at harvest on the collection
   boot (§6.3, §6.10); a sign-inconsistent discharge accumulator under SMC coverage is disclosed (§6.4); operating-system
   metadata files are not source changes (§6.5); a post-run guard collector exception is disclosed on the verdict path
   only (§6.3, §6.10); two new runner record kinds and one new writer record kind (§6.10); the monitor's restarts and
   unverified orphans are written (§6.8); model identity can be superseded at harvest (§7.2).
6. **Re-derived artifacts** (§0.7, §4.2, §4.3, §4.6, §5.5). The spares change the plan trees, the identity pins (which
   record the plan-tree digests), the sizing output and each window's planned disk bytes. Each digest is given at
   `d3c107f2f` and marked with the FILL `B5-FINAL-HASHES` (filled in revision 8).
7. **Catalog** (`flag_catalog.json`): the fourteen codes above are added with the code's effects (§13).

**What changed in revision 8.** The integration stopped changing at `43ac12d0ce554813278619b8e8e2331c9eb35be2`
(`integrate/2026-10-07-int5`; `/Users/edr/night-archive/gate-prune/FROZEN_HEAD_3.md`), the candidate for H_claim. Since
`d3c107f2f` it carries: a Fable delta cold pass's fixes (lane `lane/2026-10-07-coldpass2-fixes`, `d06ab4778`; findings
D1 and N1–N7 of `/Users/edr/night-archive/gate-prune/cold-pass-2/REPORT.md`); three orchestrator rulings (Q11 and
N8, described in items 1 and 2 below, and the evidence-manifest ruling: the list of files that an older kind of
night, the quiet-predicate evidence night, digests as its evidence now includes the census matcher
`joulewise/agent_identity.py`, commit `39ac4972d`; block 5 does not run that kind of night, so the ruling changes
nothing in this text, §13); and test-only fixture repairs. This revision makes the text say what that code does.
No registered threshold, sizing value or pinned digest changed.

1. **Q11 closed** (§0.12, §0.16, §7.2, §14; analysis plan §2.4). On GAMMA only, an attempt carrying
   `neg8.midpoint_lost` is not claim-usable (window reason `neg8.midpoint_lost_primary`), so GAMMA is re-armed. On
   ALPHA and BETA the flag stays disclosed only.
2. **More ways a NEG-8 reference is lost** (§0.12, §6.5). A reference whose summary cannot be read
   (`summary_unreadable`, cold pass 2 D1), and a reference whose model identity is not the sealed one or cannot be
   derived (ruling N8), is lost, not a reason to fail the window. A planned reference that never ran is named
   (`bundle_absent`, N2), and never-run references count toward `references_insufficient` (N3). When the verdict's
   sources do not authenticate, the harvest still maps losses from the manifests in the window's claim runs root
   (the directory under which its science and reference members and the runner's own records of each stage are
   written, §0.17) and fails the screen
   instead of leaving a stored screen standing (N1).
3. **Smaller changes:** the census also recognises an agent run by its npm package path (§4.5, N5; replaced in
   revision 10 by the rule that reads every argument of a JavaScript runtime); the unusable-pack
   refusal keys on an exception type, not a message (§0.17, N6); a torn flag line with an empty code prefix names no
   code (§6.2, N7); the refusal allowlist gains the GAMMA window reason and the retyped raise (§6.11).
4. **Fills** (§0.7, §2, §4.6, §5.5, §9.1, §13): `B5-FINAL-HASHES` (every digest recomputed at `43ac12d0c`),
   `416-AUDIT-RECORD` and `416-SEATS` (the pre-arm audit run at the frozen head `a434e363d`, §9.1).
5. **Analysis plan:** §2.4 follows Q11; §4 names which drift allowance the issuer reads after a harvest re-screen
   (cold pass 2 N4).

**What changed in revision 9.** Two review passes ran on the revision-8 candidate `43ac12d0c`: a Sol 6.1 delta
re-audit of `a434e363d..43ac12d0c` (five findings, A1–A5) and the dry arm, which showed that the census could not see
an agent that had launched it (dry-records finding F1). Two lanes fixed them (`lane/2026-10-07-census-ancestors`,
`ca25d9299`; `lane/2026-10-07-neg8-delta-fixes`, `294f6e573`), the orchestrator added a sealed identity pin for the
reference workload (`754c8c093`), and on Ed's word T3 (T3 Code, the agent harness named in the revision 7 list,
item 3) was removed from the census (`63d2b9bad`, `fe28e5a0c`). The int5
head is now `fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7` (`/Users/edr/night-archive/gate-prune/FROZEN_HEAD_4.md`). One
more commit, the census interpreter rule, was being merged after it when revision 9 was written (§4.5; it is merged
at `84661ddb3`, and revision 10 restates it from the code). This revision makes the text say what that
code does. No registered threshold, sizing value or plan tree changed.

1. **The agent census** (§4.5). The probe is now `/usr/bin/pgrep -a -lf '[c]odex|[c]laude'`. `-a` makes `pgrep` list
   the census's own ancestors, which Darwin's `pgrep` otherwise leaves out, so an agent session that launched the arm
   is a hit (F1). The window's own process tree is followed downward only. T3 Code is no longer an agent (Ed,
   2026-10-07). A JavaScript runtime is an agent when any element of its command line names an agent's package or
   install path, with no option parsing (then a pending commit, described from the orchestrator's text; revision 10
   item 1 gives the rule as merged, which is wider).
2. **NEG-8 references** (§0.12, §4.6 item 3, §6.5). A reference that fails the strict check is lost (reason
   `strict_invalid`) in the verdict writer (the desk program that writes the whole-window verdict) and in its replay
   (the re-computation by which a later reader authenticates a stored verdict), not a reason to fail the screen
   (A5). Every reference and
   spare is checked against one sealed identity, the new `neg8_reference` pin (A2). A reference or spare that ran
   another model removes the window (orchestrator call (ii)); one whose identity cannot be derived is lost, and the
   survivors decide. The sealed roster names every planned reference and spare, so a known loss is never erased by
   an unreadable manifest (A3).
3. **Which bracket carries the drift allowance** (§0.12; analysis plan §3.1, §4, §11). The harvest records it in
   `derived/neg8-allowance.json`, and a claim consumer on a block-5 window must be given the harvest archive (A1).
   Two consumers do not yet reach that record (Sol R2 and Sol R3, the second and third findings of the Sol
   re-verification of §9.1, written with "Sol" because R3 alone names the fix route of §0.1; and Fable cold pass 4,
   finding D1). They are assigned to a named analysis lane, L9-NEG8, which must land before any claim; until it
   does, the affected floors and contrasts are not claimable.
4. **§7.2:** the sentence that put `neg8.midpoint_lost_primary` in the NEG8 family for the anti-spiral rule is
   struck. That rule is a process rule for the orchestrator (§7.3), and no code computes it.
5. **Fills** (§2 items 1, 2 and 6, §9.1, §13): `B5-FINAL-HASHES` (every digest recomputed at `fe28e5a0c`; the final
   head is itself a FILL), `416-DELTA-RECORD`, `B5-DRY-RENDER-RECORD` and `B5-DRY-ARM-RECORD`.
6. **Catalog** (`flag_catalog.json`): no code added or removed and no effect changed; five notes rewritten (§13).

**What changed in revision 10.** Revision 9 described one rule, the census's rule for JavaScript runtimes, from the
text of a commit that had not yet been merged. That commit is now merged (lane `lane/2026-10-07-census-interp`: the
rule is commit `2524637ae`, the lane's last commit is `455e59b86`, and commit `84661ddb3` merged it into int5). This
revision reads the merged code at the int5 head `9b0c680ed79d5c7b72b4b39ed04b9fe51dd116d4` and makes the text say
what it does. It then checks every item of the integration's list of required text changes
(`/Users/edr/night-archive/gate-prune/REG_PENDING.md`, every section) against this file, the analysis plan and the
catalog, and repairs the gaps it found. No registered threshold, sizing value, plan tree, pin or catalog effect
changed. No FILL that waits for the final head or for the seal is filled: `H-CLAIM`, the final head under
`B5-FINAL-HASHES`, `B5-SEAL-SEATS`, `B5-SEAL-RECORD`, `B5-PLANS-REGENERATED`, `B5-BLIND-CUSTODY-MAP` and
`B5-RELEASE-EVENT` stay open, and §11 and §12 are unchanged.

1. **The census's rule for JavaScript runtimes, from the merged code** (§4.5; also §2 items 1, 6, 7 and 8, §9.1,
   §13, §14 Q14 and Q15, §16). Some agents are JavaScript programs, so the process that runs one is a JavaScript
   runtime (a program that executes JavaScript: `node`, `bun` or `deno`), and the agent shows only in the strings
   the process was started with, its arguments. Such a process now counts as an agent when any argument holds a path
   component or word beginning `claude` or `codex`. The census no longer tries to work out which argument is the
   script: that needed a table of the arguments that configure each runtime (its options), and two audits in a row
   found the table wrong. A runtime that names no agent, but whose arguments say that it runs code no argument names
   (code written on the command line, or a script fed to the process's input), is undecided and counts as an agent.
   Revision 9's wording ("names an agent's package or install path") was narrower than the code. §4.5 now builds the
   rule from the two audit findings that forced it, shows it on nine command lines, and says in which direction it
   can err.
2. **Gaps found against the list of required changes.** Each of these was in the list and was missing here or only
   implied: a failed spare does not stop the spares after it, because the spare retry passes `--max-failures k`
   (§0.12); the programs that run the census, all through one shared decision code, are named (§4.5); the lane that
   audit finding A5 deferred is stated (§9.1); and the analysis plan discloses a hazard whose probe at the arm
   returned no reading (analysis plan §8.1).
3. **Sync at `9b0c680ed`** (§13, `B5-REV10-SYNC`). Since `fe28e5a0c` the integration changed the census matcher and
   its tests, one explanatory comment in the harvest and one test data file, and it added a copy of revision 9 of
   these documents (commit `763b678a7`). The plan trees, the sizing output, the identity pins, the pin registry
   (`configs/pins/registry.json`, the list of every digest written into the tests and configs) and the refusal
   allowlist (§6.11) are byte-identical to `fe28e5a0c`. Revision 10 exists only on this branch until the seal
   preparation copies it into the integration.
4. **Catalog** (`flag_catalog.json`): no code, effect or note changed; its 192 codes agree with the code at
   `9b0c680ed` (§13).

**What changed in revision 11.** Before the seal, every statement of this file, the analysis plan and the flag
catalog that can be checked against the code was compared with the code at the int5 head
`9b0c680ed79d5c7b72b4b39ed04b9fe51dd116d4`. Fifteen readers (each a seat: one model session working to a written
brief, §0.1) checked 2,011 such statements and reported 143 places where the text and the code differ. Of those, 73 said that the text states a fact wrongly, and each of
the 73 was reproduced from the code by a second seat that had not seen the first one's reasoning; none was refuted.
After twins were merged (one fact reported by two readers) they are 69 distinct facts. The other 70 reports were 7
sentences that are hard to read correctly and 63 terms used without being built. The list is
`/Users/edr/night-archive/gate-prune/wave-1007b/reg-fidelity/REG_FIDELITY.md`, and the orchestrator's ruling on each
item is `ORCHESTRATOR_RULINGS.md` beside it (2026-10-07). This revision corrects the text to what the code does.
Four writers each took one part (§§0–4; §§5–6; §§7–10 and §§13–16; the analysis plan and the catalog), and each
checked a fact in the code before writing the sentence about it. No code changed. No registered threshold, sizing
value, plan tree, pin or catalog effect changed. One registered rule is withdrawn (item 2), because no program and
no registered number could carry it out. In §§5–6 a corrected sentence is followed by a note of what revision 10
said, in the form "(Revision 10 said …)".

1. **Corrections that bear on a number, an exclusion or whether collection runs.** In each of these the code is
   unchanged and the earlier text would have led a reader to predict a different outcome for some window or member.
   - §0.14: a member's clock anchor is `bounded` only when six conditions hold, not two.
   - §0.15, §9.2: the arm refuses a battery current above 200 mA in either direction, not any current.
   - §4.2: the arm's clock rule has five conditions, the fifth being an unchanged boot session; one dwell sample
     that could not be read leaves the whole dwell's clock rules unjudged, which is disclosed and does not refuse.
   - §4.6 item 2: the five events after which the calibration acceptance must be derived again (its re-derivation
     triggers) are named, with what observes them and what follows for the window.
   - §4.7: the arm and the pre calibration writer do not read the same set of judged epochs; the arm's is the same
     or larger.
   - §5.1, §10: the countdown of 20 s is a literal of the ten collection stages only, and the chain adds two
     arguments to both calibration captures. The second of them is a new registered deviation, number 6.
   - §5.3: a derived NEG-8 bound must also pass a re-check of each corpus member it names; the time at which the
     bound's age is judged is stated.
   - §5.4: the conditions under which the watchdog releases a finished window, including the window that was
     refused before its chain began.
   - §6.4: the span over which contention is judged when a member has no request span.
   - §6.5: `clock.systematic` counts members and calibration captures together; `roster.duplicate_run_id` is added
     to the codes that remove a window; the four causes of `neg8_bracket_reference_invalid` are listed.
   - §6.7: a bundle is ignored under four conditions, not three.
   - §6.10: an exception in the auxiliary-config comparison still refuses the member; only the record is new.
   - §7.2: the two further conditions under which an arm's `pack.identity_unmeasured` is superseded.
2. **One rule withdrawn** (§5.5, §10). Revision 10 said that after a chain stopped at its deadline the next
   attempt's per-member time allowance would grow by "the sizing margin", with no erratum. No such margin is
   defined anywhere, and no program derives an allowance from an observed member. A larger allowance is now a cold
   erratum with a new sizing file, after a consult. §5.5 gives the reason the case is remote: the deadline is about
   27 h, against a projected chain of 4.8 to 5.7 h.
3. **Places where the code does something other than the earlier registered design.** The orchestrator ruled that
   none of them puts a wrong number into a claim, removes clean data or breaks blinding, so the code stays for
   block 5 and the text now states it.
   - §5.7, §7.3: one lost member of GAMMA's two one-member diagnostic stages gives the window the yield status LOW.
     That happens by chance in about 5.3% of GAMMA windows, and it does not hold the next arm.
   - §5.1, §6.2, §6.5: no program writes `instrument.precal_screen_failed`. A failed pre-calibration screen stops
     the chain at exit 12, and the window is removed by `calibration.no_bracket`.
   - §6.2: nine catalog codes have no program that writes them. They stay as reserved codes and are named.
   - §3: the "deliberately incomplete finalization" check is struck; it exists only in the block-4 harvest script.
   - §7.1: a chain that left no stage journal is harvested as COLLECTED, not NO_COLLECTION.
   - §7.2, §7.4, §7.6: the rules for re-arming, for END STATE across attempts and for the order of the packs are
     applied by the lead from the harvest verdicts. No program computes them.
   - §6.2, §6.7: of the five roster codes the catalog marks as removing a member, two do so under their own name.
   - §6.4: after a charging current above 200 mA the member is removed, and its assist energy is still computed
     and written to the withheld record.
   - §6.11: the refusal allowlist admits a fourth class, `DEFERRED_REPRESENTATION`, which must name an owner.
4. **Found by the writers while checking, beyond the list.**
   - §7.2: the harvest cannot read which members each collection stage of ALPHA or BETA launches, because it asks
     the plan module for a reader that does not exist and those two plan trees carry no fallback entry. It records
     `roster.dispatch_unresolved` on every ALPHA and BETA harvest, and an arm's `pack.identity_unmeasured` can then
     never be superseded on those packs. No number is touched. Whether the code is repaired before the seal is the
     orchestrator's open ruling; the catalog's note on `roster.dispatch_unresolved` still describes the fallback
     as if it always read the members, and waits for that ruling.
   - §4.6 item 2: no program reads the triggers before an arm, but an observed trigger makes the harvest's
     evaluation of the bracket fail, which removes that window and every later one.
   - §0.17: the bound runs root holds only the 12 NEG-8 corpus members and the bound; reference members are
     written to the claim runs root.
   - §0.2: the statistic behind the sampler's record length is stated (the mean per member over its whole
     stream). §3: whether an attempt runs G10 (the clock-anchor positive control of §3) is a value the plan
     writer only type-checks, so which attempt runs it is the lead's rule. §0.12: "the only reference inside the window" is narrowed to the one the screen and the allowance read.
5. **Record-only corrections, readability and terms.** The record-only corrections of the list (B1 to B40, except
   B37, which names two files that disagree about a class label and waits for the orchestrator to say which one
   moves), the five readability corrections R1 to R5 and the terms U1 to U50 are applied in their sections: each
   term is built before its first use, glossed at it, or deleted. §0.5 now prints the canonical hash of each
   pack's decode prompt manifest and the byte SHA-256 of ALPHA's and BETA's, which adds five 64-character digests
   to this file (53, against 48 in revision 10).
6. **Not touched, and why.** §8 item 2 waits for the seal gate's judge (question SG-12: how a member removed by a
   RESTRICTED code is released). §11, §12 and the sentence of §14 Q13 about collection code wait for the ruling on
   how the sealed documents land in the code tree; one correction of the list, B41, and the second use of one
   term, U47, sit in §11 and wait with it. No FILL that waits for the final head or for the seal is filled.
7. **Catalog and analysis plan.** `flag_catalog.json`: no code added or removed, and no effect, family, class or
   blinding value changed (compared by script with revision 10: 192 codes, same order); 33 notes rewritten, nine
   of them to say "Reserved: no emitter at H_claim." The analysis plan's changes are listed in its §14.

**What changed in revision 12.** Revision 12 is the text that the second stage of the seal gate judges and that
the seal commit carries (§0.18, §12). Three records arrived after revision 11 was written, and this revision
writes all three in:

- *The first stage of the seal gate* (2026-10-07; §12). A Fable 5.1 judge ruled on twelve questions about
  revision 9 of these documents and the code at the int5 head `9b0c680ed`, and on five **breaks** that an Opus 5.5
  refuter had reported (a break is a place where the refuter showed a rule or the code to give a wrong outcome).
  The ruling is `/Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE1.md`, and the refuter's file is
  `REFUTER_STAGE1.md` beside it. It requires 48 changes to the text of this file and of the analysis plan, one
  change to the flag catalog, and seven changes to code or to records in the code tree. The labels in
  parentheses below (SG-1, RF-3 and so on) are the ruling's own names for its questions and for the refuter's
  breaks; no rule depends on them for its meaning.
- *The seal landing.* The orchestrator accepted the procedure by which the seal is committed to the repository
  (lane `lane/2026-10-07-seal-landing`, merged into int5 at `9395cecfb`;
  `/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/SEAL_LANDING.md`, with the lane's list of facts
  `REGISTRATION_FACTS.md` and the orchestrator's ruling on the lane's review, `ORCHESTRATOR_RULING.md`, beside it).
- *The attribution floor.* The orchestrator ruled on §14 Q5
  (`/Users/edr/night-archive/gate-prune/wave-1007b/q5-attribution-floor/RULING.md`).

Five writers each took one part (the header and §§0–4; §§5–6; §§7–10 and §§13–16; §§11–12; the analysis plan and
the catalog). Each of the judge's 48 changes is written in the judge's own words. Where revision 10 or 11 had
already changed a passage that the judge quoted from revision 9, the judge's new text is written and revision
11's correction of fact is kept beside it. No registered threshold, sizing value, plan tree or pin changed. One
catalog rule changed, the cell minimum of item 1; no catalog code was added or removed, and no code's effect
changed.

1. **The cell minimum is 5, not 8** (the revision-3 list above; §0.16, §5.5, §5.7, §6.2, §6.6, §10; ruling SG-1,
   on the refuter's fourth break). A window was removed when one of its reported numbers rested on fewer than 8
   of its ten repeats, or of its ten groups of four (item 3 of the revision-3 list). The judge ruled that an
   exclusion needs one of two grounds, a physical hazard measured directly or a number that would be wrong or
   could not be attributed, and that 7 kept repeats or groups are neither: they give a correct mean and a
   correct, wider interval. Below 5, the registered estimator of the detection floor (the smallest difference the
   instrument can resolve, §0.10) is undefined, so the number does not exist; the minimum is set there.
   (Revisions 3 to 11 said 8.) §6.6 prints the price and the gain: compared with all 10 kept, the interval's
   half-width grows by a factor of 1.169 at 8 kept and 1.736 at 5, and at the one measured loss rate, one member in
   37, a window of ALPHA or BETA keeps both of the numbers it must report (decode, and prefill at 2048 tokens) at
   or above the minimum with probability 0.849 under a minimum of 8 and 1.000 under a minimum of 5.
2. **NEG-8 references** (§0.12, §0.17, §5.3, §6.5; rulings RF-1 and RF-5 on the refuter's first and fifth breaks,
   SG-5 on its second, and SG-7). The terms, from §0.12: a window runs **references**, members of one fixed
   reference workload, at its start, at its middle (the **midpoint** reference) and at its end. The NEG-8 **screen**
   tests whether their energy changed between the start and the end by more than a registered bound, and a window
   that fails it is removed. A reference that is left out of that test is **lost**; the others **survive**, and the
   screen is run on them.
   - A reference that succeeded but whose energy cannot be read is lost (reason `energy_unreadable`), and the
     surviving references decide. Before, that one reference made the screen fail, and the window was removed.
   - A reference whose contention evidence or battery evidence is unmeasured, or that carries a measured
     quiet-state violation (display awake, screensaver running or Low Power Mode on) or a failed battery pair
     (the two battery reads that enclose a member, revision-6 list item 1), is lost. Before, an unmeasured
     reference was kept, so a contender nobody saw could move the screen.
   - The lost-midpoint rule for GAMMA (a GAMMA window whose midpoint reference is lost is not claim-usable, and
     GAMMA is armed again; revision 8 list, item 1) is confirmed with its premise corrected: the midpoint is the
     only NEG-8 reference inside the window, not the only reference, because GAMMA also runs two diagnostic
     references there, which are recorded and which the screen does not read. The sentence that allowed the rule
     to be relaxed later now reaches a later block only.
   - §0.17 states what the harvest re-derives for the screen, and that `whole_window.verdict_unauthenticated` is
     recorded on every window and carries no information.
3. **A damaged flag line** (§6.2; ruling RF-3, on the third break). The codes a damaged line could have been are
   drawn only from the codes that a program writing flag files before the harvest can emit, so a torn copy of a
   disclosed flag no longer removes a window for a code that only the harvest writes.
4. **Two sentences about catalog effects** (§6.5, §7.2; ruling SG-2). §6.5 names the two codes that remove the
   window when the verdict file is absent or unreadable. `model.identity_unpinned` joins the codes of §7.2 whose
   cause is treated as a harvest problem first.
5. **Blinding** (§8; ruling SG-12). A flag computed from a science energy has the blinding class RESTRICTED
   (§0.16). Three harvest outputs write such a flag's code by name; they are restricted until the release event
   (the recorded moment, after the block closes, from which energies may be read, §0.1). The custody map of §8,
   the list of the restricted paths, is filled.
6. **The sensitivity line is adopted, narrowed** (§6.3, §12, §14 Q6; analysis plan §8.1; ruling SG-4). The line
   is a second value printed beside a number, computed as if certain exclusions had not been applied, so that a
   reader can see whether those exclusions pull the number. It sets aside three codes that describe a hazard
   which follows load, and no others.
7. **Collection code is judged by checkout** (§7.2, §7.5, §11, §14 Q13; ruling SG-8). Collection code is code a
   window executes (§7.5). The **measurement checkout** is the clone of the repository that the windows run from,
   and a **desk checkout** is any other, from which programs are run after a window (§0.18). A repair to a desk
   program lands in a desk checkout and changes no collection code, even when the file it changes is also
   imported inside a window from the measurement checkout. A re-harvest that changes whether an attempt is
   claim-usable follows the rule of §7.2 for a code that is classified late.
8. **Where the seal is committed** (this header, §0.18, §2, §4.1, §4.6, §5.5, §6.5, §7.5, §10, §11, §12, §13; the
   seal landing). H_claim is the last commit that changes a file a window can read (the pin of the calibration
   ledger apart, a data file that advances after each window). The filled inventory, and
   the final text of this file and of the analysis plan, are committed one commit later, in the seal commit; the
   seal record follows; the measurement checkout is a full clone checked out at the seal commit. A window is
   compared with the seal file by file and head against head, and between the two heads only a changed **window
   input** counts, that is, a changed file that a window can read (§0.18). Revisions up to 11 said the measurement
   checkout is "fast-forwarded to H_claim" and that windows run H_claim's commit; both are corrected. §11 and §12
   are rewritten, and the correction that revision 11 held over for them (item 6 of its list) is applied in §11.
9. **What the gate changed outside these two texts.** Before H_claim, because the files are window inputs or
   tests: the catalog's `rules.cell_unit_minimum` (item 1) and note texts, three entries of the refusal allowlist
   `configs/gates/hazard_refusals.json` (§6.11), and one test fixture. After the seal, in a desk checkout, and
   before ALPHA-1's harvest: the harvest lane of §11 item 4, which installs the reference losses of item 2, the
   candidate list of item 3, a record of the harvest's own commit, and five details of the head comparison that
   the review of the seal landing and cold pass 5 found (§0.18, §11). ALPHA-1's harvest does not run until that
   lane is pinned, that is, until an addendum to the seal record names its files, their SHA-256s and its commit.
   Nothing a window executes changes after H_claim.
10. **The attribution floor is a registered formula** (§0.10, §0.14, §10, §13, §14 Q5; analysis plan §4 and
    §8.1; the orchestrator's ruling). Revisions up to 11 named a constant, decision D-078's "about 1 J", and left
    its value open. That figure was one member's bound in a window of July 2026 on another OS build; on block 3
    the same bound was 1.38 to 2.86 J. §0.10 now builds the bound from its three timing inputs and registers the
    floor of a cell as the largest bound over the cell's kept members, computed from the window's own bytes. No
    number is bound. §10 records this as a seventh registered deviation.
11. **Records** (§2, §9.1, §13, §14). §2 item 1 states H_claim as a marker and lists the Fable delta cold pass 5
    (on `fe28e5a0c..9395cecfb`, PASS WITH NOTES) and the independent executing review of the seal-landing lane;
    together they are the second part of the #416 delta record. §14 closes Q5 and Q6 and records the gate's
    confirmation of Q9, Q11, Q12 and Q13.
12. **Status and markers.** The status line says what seals this file. The six markers that remain are listed
    at the head of this file, each with the one value that replaces it.
13. **Catalog and analysis plan.** `flag_catalog.json`: `rules.cell_unit_minimum` is 5; ten notes and the status
    note are rewritten; 192 codes, with no effect, family, class or blinding value changed. The analysis plan's
    changes are listed in its §14; besides the items above they remove the metrology term (a second variance term
    that the plan added to an interval the measured scatter already covers) from the two GAMMA contrasts (ruling
    SG-13), and they have the analysis check each attempt's catalog digest and harvest commit against the seal
    record (ruling SG-11).

## 0. Terms, built in the order they are used

### 0.1 People, seats and records

- **Ed** owns the capstone project and this machine. **The lead** is the orchestrating Opus 5.5 session: it
  dispatches seats, decides, records dissent and merges. A **seat** is one model session the lead dispatches with a
  written brief: Sol 6.1 (the default implementation and review seat), Opus 5.5, or Fable 5.1.
- **Consult.** One blind round from two seats, each licensed to disagree; the lead decides and records dissent.
- **Cold gate.** An independent ruling on a named question by a **judge** seat with no prior involvement, checked by
  a **refuter** seat whose job is to show the ruling wrong. A challenge that survives goes back to the judge once; a
  disagreement settles in one erratum, not a chain. A **cold erratum** is a change to a sealed document made this
  way; it is **prospective** when it is made before the bytes it governs exist.
- **R3.** The standing route for a tooling fault: fix it in a reviewed pull request, merge, then re-run the failed
  *desk* step (a step run after collection, at the desk) on identical bytes. R3 never re-collects anything. Two
  other labels contain the same characters and have nothing to do with this route. The Sol re-verification of §9.1
  numbers its three findings R1, R2 and R3; this file writes them **Sol R1**, **Sol R2** and **Sol R3**. And
  "R3-1" is finding 1 of mock rehearsal round 3 (§4.2).
- **Custody.** A directory whose files are written once, never modified, and listed with their SHA-256s.
  **Restricted custody** is custody that only automation may read until the **release event** (the recorded moment,
  after the block closes, from which energies may be read, §8); nothing in it is printed, emailed or committed
  during the measurement block.
- **To tie** a value to a file is to record the file's path and SHA-256 beside the value.
- **D-numbers** (D-078, D-179, …) are the project's numbered decision records in `docs/decision_log.md`; each is named here
  by what it fixed. **#416** and **#421** are Ed's numbered directives: the pre-arm audit (§9.1), and battery
  **float** (§9.2), the state in which the machine runs from its adapter while the battery neither charges nor
  supplies it. Float is measured as: on AC power, the battery not charging, and the battery current at most 200 mA
  in either direction (§4.2).

### 0.2 The machine and the sampler

The machine is one Apple M3 Max laptop (model identifier Mac15,9) running macOS build 25G83 on a 140 W mains
adapter. Everything below happens on that one machine.

- **Sampler.** macOS `powermetrics`, asked for one **power record** every 100 ms. It never samples faster than
  asked. In block 3 a record was about 129 ms long: taking the whole sampler output of each of the 37 measured
  runs, the mean record length was 127.0–131.7 ms (median 128.9 ms; recomputed by this author from the records'
  `elapsed_ns`), and over the idle stretch that opens each run it was about 130.5 ms (§0.3 builds the run, its
  sampler stream and its idle baseline). Each record states the average power over its own time span (its
  **support**) of the processor rails, CPU, GPU and ANE combined (`combined_power_w`,
  `joulewise/adapters/powermetrics.py`).

### 0.3 A member, step by step

A **member** is one run of one inference request in its own process. Its steps, in order:

```
 prepare | idle baseline (idle admission; one retry if refused) | warm-up | measured request | cleanup | reducer
          |<--------------------------- sampler stream ------------------------------->|
 ...then, before the next member of the same stage starts: cooldown (§0.6)
```

- **Idle baseline.** The sampler records the idle machine for a fixed number of power records. The adapter sets
  that number from the configuration's `idle_seconds` as if a record arrived every 100 ms, the requested interval:
  records = ceil(`idle_seconds` / 0.1) (`joulewise/adapters/powermetrics.py` `_idle_count`). The sampler in fact
  delivers a record about every 130.5 ms (130.2–132.1 ms over block 3's 37 idle captures), so the record count, not
  the setting, fixes how long the baseline lasts. Every `_v5` pack sets `idle_seconds` 57.6: 576 records, which over
  those 37 captures would have spanned 75.0–76.1 s (median 75.2 s; the first 576 records of each capture summed by
  this author from the records' `elapsed_ns`: 75.010–76.082 s). 575 records would have fallen short of 75 s on
  11 of the 37. The packs set 75 s until the timing ruling of 2026-10-06 (§0.6); that gave 750 records spanning
  97.7–99.1 s (97.667–99.055 s). **Idle admission** then tests whether the machine was quiet during that baseline
  (the tests are in §0.13; they did not change). Replayed on the first 75 s of block 3's 37 captures, the unchanged
  tests changed one verdict, from pass to refuse: the 8B p4096 probe, a workload outside this registration (its
  CPU-busy 95th percentile rose from 0.469 to 0.576).
- **Warm-up.** One untimed generation of the same request, so the measured request does not pay first-call costs.
- **Measured request.** The request whose energy is reported: 11.1–23.6 s long in block 3.
- **Controller.** `joulewise/controller.py`, the program that carries one member through these steps: it starts
  and stops the sampler, sends the requests, stamps each step on the machine's clocks and writes the bundle.
- **Reducer.** `joulewise/reduce.py`, which turns the raw power records and the event timestamps into the member's
  summary (`summary_metrics.json`).
- **Sampler stream.** One continuous `powermetrics` process from the start of the idle baseline to the end of the
  measured request. An idle-admission retry stays inside the same stream, so a retry lengthens the stream. The
  cooldown is outside it.
- **Bundle.** The member's write-once directory of raw files, events and summary.

### 0.4 Phases and phase energy

- **Phase.** A named, timestamped part of the measured request. **Prefill**: the model reads the whole prompt and
  computes the first output token; it ends at the first streamed token. **Decode**: the model produces the remaining
  output tokens.
- **Phase energy.** Each power record contributes its power times the length of the overlap between its support and
  the phase (`reduce.py` `_integrate`). Records wholly inside count in full; a record that straddles a phase edge
  counts in proportion to its overlap; records outside count zero. No idle power is subtracted (**gross** energy).
  *Worked example (synthetic).* A phase runs from t = 10.00 s to t = 10.25 s. Record 1 covers 9.90–10.03 s at 20 W:
  overlap 0.03 s, 0.60 J. Record 2 covers 10.03–10.16 s at 30 W: overlap 0.13 s, 3.90 J. Record 3 covers
  10.16–10.29 s at 30 W: overlap 0.09 s, 2.70 J. Phase energy = 7.20 J.
- A phase needs at least 3 overlapping records or the reducer refuses it (`MIN_PHASE_SAMPLES = 3`). Each phase also
  carries a **precheck**: a per-phase list of pass/fail tests on its timing evidence (record count, record
  regularity, the clock bound of §0.14 against the phase length; full list in `joulewise/whole_window.py`
  `_METRIC_LOCAL_PRECHECK_REASONS`).

### 0.5 The two workloads

- **Decode workload.** Prompt 0 of `real_prompts_v1`, rendered through the Qwen3 chat template with thinking off: a
  42-token prompt for both models. Each of the three packs (ALPHA runs Qwen3-1.7B, BETA runs Qwen3-8B and GAMMA
  runs both; §0.7) carries its own **decode prompt manifest**, the file that describes the one prompt item its
  decode members run (`decode_prompt_manifest.json` in ALPHA and BETA;
  `decode_prompt_manifests/<model>/01_sky_color.json` for each of GAMMA's two models). Every decode member's config
  records its manifest's **canonical hash** (`suite_manifest_sha256`): the SHA-256 that
  `joulewise.suite.suite_manifest_sha256` computes over the manifest's content written out again in the function's
  own fixed form (sorted keys, two-space indent), so it equals the SHA-256 of the file's bytes only when the file
  is stored in that form. Each manifest names its own pack and model (its `suite_id`), so the four hashes differ:
  ALPHA
  `31301c9df7e1f79c027d05a8b8e6022bf4d14e22b9c7f77ce8431b0ac3256694`, BETA
  `6dc7448c3e14ee18383f7904830f96dbc624e37875d3abac2561321669668705`, GAMMA's 1.7B side
  `d60a7f4d2e3498947fef630fd3092da59ffb13b52e604894ada065e4e9647b23` and GAMMA's 8B side
  `c35156575b7c14c9f2271b442f71c9fafa3944363c2f46ae2821731134229185` (recomputed by this author with that function
  at `9b0c680ed`, and counted in the member configs: 50, 50, 20 and 20 members). ALPHA's and BETA's manifest files
  are not stored in the fixed form: their byte SHA-256s are
  `446c7ef368d34a558d4fd264b0b86c99314b1dc22ec7ac3447d6d0fea93501d7` and
  `46887b91cda436c1da90a217b1950d051371b215a0d5bd4ed00636196057206e`. GAMMA's two are stored in it, so their byte
  SHA-256s equal their canonical hashes (`shasum -a 256`, run by this author).
  Output is forced to exactly 512 tokens (greedy, end-of-sequence suppressed). Prefill computes the first output
  token, so the decode phase spans the other 511 generation steps; the decode per-token value divides by all 512
  runtime-observed output tokens (D-179; analysis plan §4).
- **p42.** The prefill phase of the decode workload: 42 prompt tokens, a few tens of milliseconds, shorter than one
  power record. Block 3's comparably short phases failed their prechecks on all 24 members. The p42 cells are
  registered as **expected unresolvable**; their refusal blocks nothing.
- **Prefill workload.** A prompt of exactly L = 2048 tokens (token-ID hash
  `202e4913340b2bae39bf9a9d3a314f62bb5ff783fae483ad6a98507d071e1479`), 512 output tokens. Block 3 chose L as the
  shortest of 512/1024/2048/4096 at which every small-model probe member's prefill overlapped at least 5 records
  (`selection.json`, SHA-256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`).

### 0.6 Stages, settles and cooldowns

The values in this section follow the cold-judge ruling on block-5 per-member time of 2026-10-06
(`/Users/edr/night-archive/gate-prune/timing/RULING_fable_cooldown_2026-10-06.md`; its numbers are in
`judge/judge_checks.json` beside it).

- **Stage.** One ordered list of members that `scripts/run_campaign.py` runs together. Each stage starts with a
  60 s **settle**: the **chain** (the script that runs a window's stages in order, §0.17) sleeps so the machine
  returns to idle. The same 60 s settle precedes the pre calibration, so a window has eleven settles. The runbook's
  180 s (`docs/phase_2/window_runbook.md` `SETTLE_S=180`) still governs the older windows; the block-5 chain lists
  the difference among its deviations (`joulewise/b5/chain.py` `SETTLE_S`, `DEVIATIONS`). *Why 60 s:* processor
  power is back at idle within about 15 s of a decode ending (block 3's **sentinel reading**, the short idle
  reading the controller takes right after each request, showed 0.1 W at 9 s), each first member measures its own
  idle baseline, and the pre-calibration settle starts only after the arm (the checks run at the window's scheduled
  start, §0.15) has watched the idle machine through its **dwell**: a wait that ends once 180 s in a row have passed
  with no competing process, so it lasts at least 180 s (§4.2; under revision 4's 600 s rule it lasted
  633–1,477 s). A longer settle has nothing left to recover from.
- **Cooldown.** Between members of a stage the runner reads the idle machine in 5 s readings: each reading is one
  short sampler capture reduced to its mean processor power. The capture asks for 50 records, which span about
  6.5 s; one reading takes about 7.5 s of wall time, and the first is complete about 8.5 s after the cooldown
  begins (block 3's 26 cooldown traces: captures of 6.36–6.59 s, 7.46–7.69 s from one reading to the next,
  8.49–8.66 s to the first; recomputed by this author). The runner
  starts the next member at the first reading whose mean is at most twice the previous member's idle-baseline mean
  while the OS thermal state is nominal, or at the 300 s **cap**, whichever comes first. The first member of a stage
  has no previous member and no cooldown (`first_run_exempt`). A member whose cooldown reached the cap is recorded as
  `cooldown_cap_hit`. The policy file states the rule as `sustained_window_s` 5.0 (only the last 5 s of readings
  count, so one reading decides), `coverage_fraction` 0.8 (the readings must cover at least 4 of those 5 s),
  `tolerance_fraction` 1.0 (the bound is the previous baseline × (1 + 1.0)), `subwindow_s` 5.0, `cap_s` 300 and
  `require_thermal_nominal` true (`configs/campaign_policies/quiet_mac_p2_b5.json`, §0.13).
  *Worked example (synthetic).* The previous member's idle baseline averaged 0.037 W (block 3's median), so the
  bound is 0.074 W. The first reading averages 0.082 W: no start. The second averages 0.045 W with thermal state
  nominal: the next member starts, about 16 s after the cooldown began (about 8.5 s to the first reading and 7.5 s
  more to the second; block 3's traces reached their second reading at 16.0–16.3 s).
  *Why this rule, not block 3's.* Block 3 required 30 s of readings within 10% of the previous baseline. Its waits
  averaged 53.9 s over 26 cooldowns; the new rule would have averaged about 9.1 s. One wait, 114 s before w2
  member `g2a-small-p2048-r03` (readings of 0.822, 0.614 and 0.336 W after three readings of 0.034–0.064 W), was a
  background OS process (Apple Intelligence asset activity in the unified log), which then made that member's idle
  admission refuse it twice; the new rule would have started it at 8.6 s and admission would have refused it the
  same way. Over the timing judge's sample of 28 block-3 members of the smaller model that have a recorded gap
  since the previous run's end, each member's gross energy minus its group mean did not move with that gap (gaps
  79–702 s; slope 0.003 J per 100 s, r = 0.027, residual SD 0.22 J on 60–125 J members; `judge/judge_checks.json`).
  That sample is not the set of members that had a cooldown: block 3 had 26 cooldowns, and no member that had one
  had a gap above 231 s, so the sample's longer gaps belong to members that started a stage with no cooldown.
  Neither rule measures temperature, so neither bears on heat carried from
  one 8B member to the next; that is measured by the reference members and the NEG-8 screen (§0.12) and by the
  diagnostic below.
- **Battery-temperature diagnostic** (recorded, never a refusal or an exclusion). Just before every member starts,
  the first member of a stage included, the runner reads the battery thermistor (`ioreg -rn AppleSmartBattery`, key
  `Temperature`, in hundredths of a degree Celsius; no privileges; after the cooldown's readings, when there is a
  cooldown, and before the member's sampler stream starts) and writes the reading into the stage's **campaign
  manifest**, the file in which the runner records one stage as it runs it (its members, their cooldowns and
  these readings). A stage of N members therefore has N readings, the first taken before its first member, and a
  one-member stage has one. At harvest (the desk program run after the window, §0.17), for each stage with at least
  two readable readings: the **rise** is the last readable reading minus the first readable one, and the stage has
  a **plateau** when it has at least three readable readings and the last three lie within 0.5 K of each other
  (largest minus smallest ≤ 0.5 K). A stage whose rise exceeds 3 K with no plateau is flagged
  `thermal.stage_battery_rise`. A stage with no reading recorded, or with any reading unreadable, a one-member
  stage included, is flagged `thermal.battery_temperature_unmeasured`; with fewer than two readable readings it
  gets no rise judgment. Both are DISCLOSE (§6.8) and are reported beside the window's NEG-8
  result. If the NEG-8 screen passes, the numbers stand and the kelvin figure sizes future gaps; if it fails, the
  window is already removed by `neg8.screen_failed`. *Worked example (synthetic).* Readings 30.1, 31.0, 31.9, 32.6,
  33.3 and 33.9 °C: rise 3.8 K; the last three span 1.3 K, so no plateau; the stage is flagged. The reading is
  taken by `scripts/run_campaign.py` (`_hazard_read_battery_temperature`, manifest key
  `battery_temperature_readings`) and judged by the harvest; both are at the frozen head `a434e363d`.

### 0.7 Packs, attempts, windows and the measurement block

- **Pack.** The frozen, hash-pinned set of stages, member configurations and plans for one window. Its **plan tree**
  (`plan_tree.json`) lists the stages in order (`stage_graph`), with each stage's inputs, command line and expected
  member count. Three packs exist, all with the duration-sized idle baseline of §0.3 (`idle_seconds` 57.6) and the
  block-5 policy of §0.13:
  **ALPHA** `configs/campaigns/d117_floor_qwen3-1p7b_v5` (Qwen3-1.7B, 4-bit), **BETA**
  `configs/campaigns/d117_floor_qwen3-8b_v5` (Qwen3-8B, 4-bit) and **GAMMA**
  `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (both models). Their plan-tree SHA-256s at the
  int5 head `fe28e5a0c` (the same as at `43ac12d0c` and at `d3c107f2f`, after the NEG-8 lane added each reference
  stage's spare members, §0.12) are ALPHA
  `1d87a30955fa978d3a3a22dc0048720691e0128e4a3fe83477fc375d13dd031a`, BETA
  `0cdb33836f4632827bc74be194e388450c53b3314db1c72d9e9904e625868670` and GAMMA
  `8b1d1d7176f5ee2286038e91df6427e47476c3a4bdee45a1c24687d49d80e3bf`, computed by this author with `shasum -a 256`
  at `fe28e5a0c`, equal to each pack's committed
  `plan_tree.sha256` there, with each pack's `generate_configs.py --check` exiting 0, and recorded in the sizing
  output (§5.5); this author computed the same three values again at the int5 head `9395cecfb`. At H_claim the three
  files hash to ALPHA `FILL[B5-FINAL-HASHES]`, BETA `FILL[B5-FINAL-HASHES]` and GAMMA `FILL[B5-FINAL-HASHES]`.
  Earlier
  values: at the frozen head `a434e363d`, ALPHA `5218c270…` and BETA `5bab773a…` (as the timing lane `f4cf9047` left
  them) and GAMMA `fb51b4aa…` (after lane L10 gave its interior references distinct run ids, branch
  `lane/2026-10-06-l10-gamma-refs`, commit `c6309e1a`; §2, "Before GAMMA-1 arms"); GAMMA `523864e2…` at the
  integration head `b9d02700a`, which did not carry L10; and `a0076ae7…`, `ebd8c160…` and `7cdf1891…` at the
  gate-prune integration head `f8164893`, before the timing lane. The values in force are those in the sealed
  inventory at H_claim (§11).
- **Attempt.** One arm-to-harvest occurrence of one pack, labelled `ALPHA-n`, `BETA-n` or `GAMMA-n`, n = 1, 2, …
- **Window.** The stretch of machine time an attempt occupies, from its scheduled start t0 (§0.17) to its chain's
  exit.
- **Measurement block.** A registered set of windows sealed under one registration. This file registers measurement
  block 5. Block 3 (2026-10-03/04) was the prefill-length probe; block 4, the planned qualification block, does not
  run (§3).

### 0.8 Quads, contrasts, units and strata

- **A/B/B/A quad.** Four consecutive members in the order A1, B1, B2, A2. (The code calls this a "block":
  `block_ids`, `paired_block_incomplete`. This file says **quad**, so that "block" means only a measurement block.)
  A and B are the quad's two **sides** (the code says "arms", a use of the word unrelated to the arm at a window's
  start, §0.15).
- **Why A/B/B/A.** A slow linear drift cancels inside a quad. *Worked example.* If every member reads δ more than the
  one before it, positions 0, 1, 2, 3 carry 0, δ, 2δ, 3δ of drift; side A (positions 0 and 3) averages 1.5δ and side
  B (positions 1 and 2) averages 1.5δ, so the A-versus-B difference gains 0. A curved drift does not cancel: with
  drift k² at positions k = 0…3, side A averages 4.5 and side B 2.5.
- **Null quad.** In ALPHA and BETA both sides are the *same* model and workload, so any A-versus-B difference can
  only come from the instrument and the machine.
- **Contrast.** In GAMMA, side A is Qwen3-1.7B and side B is Qwen3-8B on the same workload. A quad's difference is
  `d = (B1 + B2)/2 − (A1 + A2)/2`; the contrast is the mean of d over GAMMA's quads for one phase.
- **Absolute repeat.** One member run on its own (not in a quad); ten in a row per workload.
- **Unit.** A group of members the statistics treat as one independent draw: each absolute repeat is one unit, and
  each quad is one unit. A **stratum** is one kind of unit: the **repeat stratum** or the **quad stratum**. D-179
  fixes 20 units per reported cell: 10 repeats and 10 quads. Consecutive units share slow drifts (temperature,
  background load), so their independence is a **modelling assumption**, not a measured fact, and every reported
  interval carries that caveat.

### 0.9 Reported cells

A **reported cell** is one registered energy number per model and phase, computed from that model's 10 absolute
repeats and 10 null quads (50 members): three per floor pack, six in all
(`d117-reported-mean-ph-{decode,prefill-p42,prefill-p2048}-{qwen3-1p7b,qwen3-8b}`). Decode and p42 read the same 50
members (the decode stages); prefill-p2048 reads its own 50. The four **paper cells**, also called the **target
cells**, are decode and prefill-p2048 for each model; the two p42 cells are computed if they can be and never
printed. GAMMA's two contrasts are its target cells, each over 10 quads.

### 0.10 Floors

- **Detection floor.** The largest difference the instrument produces when nothing differs, estimated from a model's
  absolute repeats (the **absolute** form) or null quads (the **comparative** form); hence the smallest real
  difference it can resolve. A contrast whose estimate does not exceed its floor is reported as `not_resolvable`
  (formulas: analysis plan §5). A **mint** is the authenticated issuance of the aggregate floor artifact.
- **Attribution floor.** A different quantity from the detection floor: a bound, in joules, on how far the energy
  assigned to one phase can move because the phase's two edges are placed against the power records only to
  within timing bounds. It belongs to one reported cell of one analysed attempt and is computed from that window's
  own members. This file registers its formula and binds no number (orchestrator's ruling of 2026-10-07 on §14 Q5,
  `/Users/edr/night-archive/gate-prune/wave-1007b/q5-attribution-floor/RULING.md`; `REPORT.md` and
  `REFUTATION.json` beside it are the investigation and the refuter that recomputed its figures from raw bytes).
  The formula is what fills the binding `ATTRIBUTION-FLOOR-BINDING` of §13.

  *Forcing problem.* Phase energy is assigned by overlap (§0.4). If a phase edge truly lies a time δ away from
  where it was placed, the record that straddles the edge has δ times its power counted on the wrong side of the
  edge. Three timing bounds limit δ. Each is derived in a later section; in plain words:
  - **b**, the **fiducial bound**: how far an edge in the sampler's power records can sit from the moment the
    power truly changed, as a calibration capture measures it against commanded pulses (§0.11). A window has two
    captures, one before it (pre) and one after it (post). The analysis uses the window's **operative fiducial bound**,
    b_op = max(pre, post) + max(|post − pre|, 0.014531 s): the larger of the two captures' bounds, plus an
    allowance for drift between them that is never less than 0.014531 s. That value is the **bracket screen** of
    the calibration **acceptance**, the issued file that judges a window's two captures: it is the largest minus
    the smallest fiducial bound among the 24 captures the acceptance was derived from (§0.11;
    `joulewise/calibration_bracketing.py`, allowance rule `max(observed_drift_s,bracket_screen_s)`). One b_op
    serves every member of the window.
  - **s_i**, member i's **wall-minus-monotonic span**: how much (wall clock − monotonic clock) changed while the
    member's sampler stream ran (§0.14).
  - **m_i**, member i's **clock bound**: how far its whole sequence of records can be misplaced on the wall clock
    (the effective bound of §0.14; a kept member's is at most 5 ms).

  *The per-member bound a_i.* Write E(x, y) for the energy the overlap rule assigns to the interval from x to y,
  and (t_on, t_off) for the phase's recorded edges. Each edge may be displaced on its own by up to the **edge
  bound** g_i = b_op + s_i, and the whole trace (the member's sequence of power records) may be shifted against
  both edges together by up to m_i. Then

      a_i = max | E(t_on + e_on + d, t_off + e_off + d) − E(t_on, t_off) |
            over e_on ∈ {−g_i, +g_i}, e_off ∈ {−g_i, +g_i} and every d with |d| ≤ m_i.

  The four combinations of e_on and e_off are the **corners**. They suffice because power is never negative, so
  the assigned energy can only grow when the start edge moves earlier or the end edge moves later. Within a corner
  E is piecewise linear in d, so its largest and smallest values lie at d = ±m_i or where a displaced edge meets a
  record boundary, and the code evaluates every such point (`joulewise/reduce.py`
  `_corner_composed_anchor_shift_envelope`; `reduce.py` is one of the four estimator files that no block-5 lane
  may change, §2 item 1). The reducer stores the result as the phase's **anchor-shift envelope**
  (`energy_anchor_shift_envelopes["/phase_energy_j/<phase>"]`, method
  `common_trace_shift_plus_independent_edge_corners_v3`): the point energy, the lowest and the highest energy
  over all corners and shifts, and `max_abs_delta_j`, which is a_i. (It stores an envelope of the same kind
  for the whole request's gross energy, under `/gross_energy_j`; §0.12 reads that one.) The analysis calls a_i
  `E_clock_anchor_shift_bound_j`.

  *Which b enters.* A member's stored summary was reduced under the pre capture's bound alone, because the post
  capture did not exist yet. The a_i used here is taken from the member's summary reduced again, in memory, under
  b_op. A **consumption session** does that (`whole_window.AuthenticatedConsumptionSession`): it is the object
  through which analysis code reads a window's members. It authenticates the window's two captures against the
  calibration ledger (the append-only record of every capture, §0.11), computes b_op, and re-reduces each member
  under it without writing any file.

  *Worked example (synthetic; computed by this author with the reducer's
  `_corner_composed_anchor_shift_envelope` at the int5 head `9395cecfb`).* Records are 130 ms long. The window's
  b_op is 45.7 ms; the member's span is 0.3 ms and its clock bound 2 ms, so g = 46 ms and m = 2 ms. The phase is
  recorded from t_on = 10.015 s to t_off = 11.055 s, so each edge lies 65 ms inside its record:

      [    2 W     ][    30 W    ]  ...  [    30 W    ][    20 W    ][    4 W     ]
      9.95          10.08         10.21  10.86         10.99         11.12         11.25 s
             ^                                                ^
         t_on = 10.015                                  t_off = 11.055
         <-g-|-g->                                        <-g-|-g->
      <-------- d: the whole trace moved against both edges together, |d| ≤ m --------->

  Each bracket is one power record: its width stands for the record's support, the number inside is its average
  power, and the numbers beneath are the times, in seconds, of the boundaries between records. The `...` stands
  for five more records of 30 W. Each `^` marks a recorded edge of the phase. `<-g-|-g->` is the range over which that
  edge is moved on its own, g to either side. The bottom arrow is the common shift d, at most m either way. The
  point energy is 0.065 × 2 + 0.91 × 30 + 0.065 × 20 = 28.730 J. The largest change is at the corner "start edge
  46 ms early, end edge 46 ms late", with the common shift putting both edges a further 2 ms late: the start edge
  then lies 44 ms early, still in the 2 W record (+0.088 J), and the end edge 48 ms late, still in the 20 W record
  (+0.960 J). So a_1 = 1.048 J. A second member has the same records, but its end edge is at t_off = 11.000 s,
  only 10 ms inside the 20 W record. Its largest change is at the opposite corner, start edge 46 ms late and end
  edge 46 ms early, with both edges a further 2 ms early: the start edge lies 44 ms late (−0.088 J), and the end
  edge 48 ms early, of which 10 ms are in the 20 W record (−0.200 J) and 38 ms in the 30 W record before it
  (−1.140 J). So a_2 = 1.428 J.

  *An approximation, and where it fails.* While every displaced edge stays inside the record that straddles its
  recorded edge, a_i = g_i × (P_on + P_off) + m_i × |P_off − P_on|, where P_on and P_off are the average powers of
  the two records that straddle the recorded edges. For the first member that is
  0.046 × (2 + 20) + 0.002 × (20 − 2) = 1.012 + 0.036 = 1.048 J, the bound. For the second it is again 1.048 J,
  where the bound is 1.428 J, because that member's end edge crosses into the neighbouring record. On 194
  recomputed phases of earlier windows the approximation ran from 63% below the bound to 20% above it
  (`REFUTATION.json`). The registered quantity is the exact maximum, the code's `max_abs_delta_j`. The
  approximation is given only to show what the bound is made of: a timing bound times the power at the phase's
  edges, whatever the phase's length.

  *The floor of a cell: the registered formula.* For one reported cell of one analysed attempt, the attribution
  floor is the largest a_i over the cell's kept members, that is, the members of the units that remain after the
  exclusions of §6. In the example, were those two the cell's only kept members, the floor would be 1.428 J. The
  analysis computes it when it issues the cell, from the window's own members and its two captures (analysis
  plan §3.1 step 10 and §4 step 7; field `binding.attribution_floor_j`), and records with it the member that attains
  it, the smallest a_i, and the stratified average of the a_i (next paragraph). It is computed from the energies of
  a block-5 window, so it is restricted until the release event (§0.1, §8).

  *What is already inside the interval, and what is printed beside it.* A reported cell's interval is its mean ±
  (h + B) (analysis plan §4 steps 3 to 5). h is the statistical half-width. **B** is the sum of the stratified
  averages of three energy bounds, in joules, that every member records (analysis plan §4 step 4). They are not
  the three timing bounds b, s and m above, which are times. The first is a_i. The second is an interpolation
  bound, which is 0 for this sampler's traces, because each of its power records states the interval it covers
  and nothing is interpolated between records. The third is half of the window's drift allowance, the allowance
  that the NEG-8 check of §0.12 sets for a change of the instrument between the window's start and its end. A
  **stratified average** is 0.2 × (the mean over the kept repeats) + 0.8 × (the mean over the members of the kept
  quads). So the average of the a_i is already inside every cell's interval. The attribution floor is their
  maximum, which is at least as large. It is printed beside the interval and is not added to it (the cell's
  record carries `attribution_floor_composed: false`, `joulewise/paper_reported_energy.py`).

  *Why it is printed.* Repeating the measurement does not shrink it. Every member of a window is reduced under
  the same b_op: if the sampler's edges sit 20 ms late, they sit 20 ms late in every member, and every member's
  phase energy moves the same way. The scatter between members averages down over a cell's units; this does not.

  *What it does not bound* (the addendum of 2026-09-04 to decision D-078, `docs/decision_log.md`). a_i bounds how
  far the overlap assignment moves over the registered timing bounds, with the power taken as constant within
  each record. It does not bound the physical energy of the phase under an arbitrary distribution of power inside
  a record. Every sentence printed beside a cell carries that condition.

  *Lineage, and why no number is bound.* Decision D-078 (clause 11, 2026-07-25) called this limit "about 1 J".
  That figure was the a_i of one member of window a10, a window of 2026-07-25 on an earlier OS build (25F84), with
  the model Qwen2.5-1.5B and a fiducial bound of 24.879 ms taken from the pre capture alone: g = 25.000 ms,
  m = 6.074 ms and edge records of 1.0959 W and 32.0292 W give 0.024999593 × (1.0959 + 32.0292) + 0.006074236 ×
  (32.0292 − 1.0959) = 0.8281 + 0.1879 = 1.0160 J; in D-078's round figures, a timing bound of 31 ms
  (0.031073829 s, the sum b + s + m) at about 33 W. Over that window's 30 members the bound ran from 0.571 to
  1.468 J. It is not a constant of the instrument, and every input to it has changed for block 5. On block 3
  (build 25G83, the two Qwen3 models; not a claim window), under that window's operative bound of 45.669 ms, the
  same bound was 1.38 to 2.86 J per member, and it changes with each window's own two captures. A registered
  value of 1 J would print beside block 5's cells a floor the instrument does not have. (Every figure of this
  paragraph was recomputed from the retained bundles by the investigation cited above and reproduced from the raw
  power traces by its refuter; this author did not open those bundles.)

### 0.11 Pulse calibration, acceptance, ledger and bracket

- **Pulse calibration.** A capture in which the GPU is driven through 59 commanded on/off pulses. For each pulse the
  estimator fits the power records as a baseline plus a rectangle whose start and end may be delayed from the
  commanded times, and returns the interval of delays consistent with the records. The **fiducial bound** is the
  largest absolute end of those intervals over all pulses: the largest timing error between commanded and observed
  edges. With 59 pulses it is a 95/95 bound (1 − 0.95⁵⁹ ≥ 0.95).
- **Pre** and **post** calibrations enclose a window; together they are its **bracket**.
- **Acceptance.** The issued file that judges brackets:
  `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, SHA-256
  `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`, derived from 24 captures. Its numbers: the **pre
  screen** 0.036462861644980 s (the largest fiducial bound among the 24; a pre capture above it stops the chain before
  any member); the **bracket screen** 0.014531 s (their range); the drift allowance max(observed |post − pre|,
  bracket screen) must not exceed 0.01550217418713139 s.
- **Ledger.** The append-only record of every calibration capture (`runs/calibration_observation_ledger.jsonl` in the
  measurement checkout, the clone of the repository that the windows run from, §0.18). Its last entry is the
  **ledger tip**. The tip committed to the repository is the **ledger
  pin** (`configs/calibration/calibration_ledger_head.json`: sequence 402, head digest
  `3ce1676c530452df301e8f09d97905487b06b8ed8887d7c7a728a08fd5310c08`, block 3's final tip). The acceptance was derived
  from the ledger up to sequence 376, its **cutoff**; brackets are judged against that cutoff while the ledger grows.
- **Bracket session.** Before a window's pre calibration, the chain opens ("reserves") a session in the ledger naming
  the window's plan; the pre and post captures are recorded against it. The **bracket binding** is the file that ties
  the two captures to that session.

### 0.12 Reference members and the NEG-8 drift check

The rules of this section follow the cold ruling of 2026-10-07 on lost and contaminated references
(`/Users/edr/night-archive/gate-prune/neg8-council/RULING.md`), as the NEG-8 lane implemented it
(`lane/2026-10-07-neg8-survivors`, merged in the int5 head `d3c107f2f`), with the cold-pass-2 fixes and the
orchestrator rulings N8 and Q11 of 2026-10-07 (in `43ac12d0c`), and the fixes of the Sol delta audit's findings A1,
A2, A3 and A5 with the sealed reference pin (lane `lane/2026-10-07-neg8-delta-fixes`, `294f6e573`, and commit
`754c8c093`, both in the int5 head `fe28e5a0c`). Where the code differs from the ruling's wording, the text follows
the code and says so.

Two rules of this section were set later, by the first stage of the seal gate (2026-10-07, §12), and the harvest
program at the int5 head `9395cecfb` does not apply them yet. The item "Where the seal gate's two rules stand in
the code", after "Who applies the loss test" below, says which two they are and why every block-5 window is
nevertheless judged by them.

- **Reference member.** A member of one fixed reference workload (Qwen2.5-1.5B, 1024-token prompt, 256 output
  tokens). Each window runs 12 at its start, the **NEG-8 corpus** (NEG-8 is an inherited label from the project's
  negative-control list; it is a name, not an abbreviation), then a **start triplet** (three reference members), one
  **midpoint reference**, and an **end triplet**. A **science member** is a member of a reported-cell or contrast
  stage (§0.8, §0.9), as opposed to a member of the reference workload. The midpoint reference runs at the
  boundary between the window's **decode arm** (its decode stages) and its **prefill arm** (its prefill stages;
  "arm" here follows a stage name, GAMMA's `gamma-reference-arm-boundary`, and is neither the arm of §0.15 nor a
  quad's side), which is also its temporal midpoint: after
  science member 50 of 100 in ALPHA and
  BETA, after science member 40 of 80 in GAMMA. The start triplet, the midpoint reference and the end triplet are the
  window's three **reference stages**.
- **Spare members.** Each reference stage also lists **spares**: copies of the stage's first reference config, byte
  for byte except the run id, with the stage's role, run only by the retry below. There are three for each triplet
  (`neg8-window-start-spare-1` to `-3`, `neg8-window-end-spare-1` to `-3`) and one for the midpoint
  (`neg8-window-midpoint-spare-1`). They live in `configs/campaigns/window_reference_spares_v5/`: for each stage and
  each count k, a directory `<stage>_spares_<k>/` holds spares 1 to k and an order manifest listing exactly them.
  Each pack's plan tree pins every spare config and spare-set manifest by SHA-256 in the stage's `spare_retry` record
  (`joulewise/b5/reference_spares.py` writes and checks them).
- **Diagnostic interior reference (GAMMA only).** GAMMA also runs one reference in the middle of each arm, after
  science members 20 and 60. Each is the midpoint reference's config under its own run id
  (`gamma-interior-reference-decode-midpoint`, `gamma-interior-reference-prefill-midpoint`), with the role
  `window_interior_reference_diagnostic`. That role is not a NEG-8 role, so neither the NEG-8 screen nor the drift
  allowance below reads these two members; they are recorded as a measure of drift within each arm, and they have no
  spares. (The screen counts only members with the start, midpoint and end roles; "The screen on the survivors" below
  says how many of each it needs. A window with more than three start, more than one midpoint or more than three end
  references is a roster error and fails the screen.)
- **NEG-8 bound.** From the kept corpus members' gross energies (and separately their idle-subtracted energies; the
  gross energies and the idle-subtracted energies are the check's two **families**, and every step below is done
  once for each), with
  n their count (10, 11 or 12; §5.3), s their sample standard deviation and t = t(0.975, n − 1). For an endpoint pair
  of n_s start references and n_e end references, let U_j be the mean of the corpus's j largest energies and L_j the
  mean of its j smallest. Then

      bound(n_s, n_e) = max( max(U_ns − L_ne, U_ne − L_ns), t × s × √(1/n_s + 1/n_e) ).

  The first term is the **envelope**: the widest gap that a start mean of n_s members and an end mean of n_e
  members could show if both were drawn from the corpus itself, so no screen statistic smaller than it is evidence
  of anything but repeatability. The second term is the 95% repeatability bound for a difference of two means of
  those sizes when nothing drifts (the corpus supplies the variance, so t keeps the corpus's n − 1 degrees of
  freedom). At the planned shape (3, 3) this is the former rule, max(U_3 − L_3, t × s × √(2/3)); at (1, 1) it is
  the legacy single-member bound max(U_1 − L_1, t × s × √2). At those two shapes the code reuses the terms stored in
  the bound artifact, so every bound minted before this rule replays to the same bytes; any other shape is computed
  from the artifact's corpus members (`whole_window.py` `build_neg8_drift_bound_artifact`,
  `neg8_family_endpoint_bound`, `neg8_count_adjusted_bound`, formula string `NEG8_COUNT_ADJUSTED_BOUND_FORMULA`).
- **NEG-8 screen.** The window passes when |mean of the end references that survive − mean of the start references
  that survive| ≤ bound(n_s, n_e), for both the gross and the idle-subtracted energies. A reference **survives** when
  it is not lost (the next item). The **whole-window drift allowance** is max(spread, bound(n_s, n_e)), where the
  spread is the largest minus the smallest of three values: the start mean, the midpoint reference's energy and the
  end mean (`whole_window.py`, `trajectory_excursion_max_j`); when the midpoint is lost, the spread is
  |end mean − start mean|. Each member carries half of the allowance (`E_whole_window_drift_allowance_j`), so a
  contrast carries it once in total. The allowance always uses the realised-count bound, on passing windows too, so a
  lost reference widens the uncertainty instead of hiding it.
- **Lost references.** Four terms come first, because the list uses them. The **strict check** is the full check
  of a reference's files, built in "The strict check of a reference" below. The **verdict row** is the one row of
  the whole-window verdict (§0.17); the harvest has it written after the window, and it is stored in the window's
  claim runs root. A reference's **envelope** is the anchor-shift envelope of §0.10 that the reducer
  stores for its whole request's energy (the lowest and the highest energy the request can be assigned within the
  member's timing bounds); it has nothing to do with the corpus envelope of the NEG-8 bound above. And a member's
  **calibration attachment** is the copy of the pre calibration capture's evidence that the controller places in
  the member's bundle (`instrument_calibration/instrument_evidence.json`), which the reducer verifies against its
  recorded SHA-256 before it takes the fiducial bound from it; when that fails, or when the member's clock anchor
  is not `bounded` (§0.14), the reducer has no timing bound to build an envelope from and writes none.
  A reference is **lost** when its bundle is absent; its summary status is not `succeeded`
  (which includes `member.admission_aborted` and `member.timeout`); its summary cannot be read (reason
  `summary_unreadable`: no summary file, as after a member is killed at the 1,800 s cap of §5.2, a file that does
  not decode, or one with no string status); its energy cannot be read although it succeeded and passed the strict
  check (reason `energy_unreadable`: the reducer gave its request energy no envelope, as when its clock anchor is not
  `bounded`, §0.14, or its calibration attachment does not verify; at harvest also `member.anchor_not_bounded`,
  `member.anchor_recompute_mismatch`, `member.reduction_mismatch`, `member.unreadable`, `member.bytes_missing` or
  `member.bytes_ambiguous` on the reference; the harvest decides this loss, and the stored in-window verdict row may
  record the screen as failed for it, which decides nothing by itself); it fails the strict check (built in "The strict check of a reference"
  below; at harvest the flag is `member.strict_validation_failed`, and the reason is `strict_invalid` in the
  **verdict writer**, the program that writes the whole-window verdict of §0.17, and in its **replay**, the
  re-computation by which a later reader authenticates a stored verdict row); any
  member-level physics exclusion of §6.4 fires on it (`contention.request_overlap`, `battery.member_span`,
  `battery.accumulator_excursion`, `thermal.os_level_nonzero`, `thermal.powermetrics_pressure_elevated`,
  `clock.step_overlap`); or its model identity cannot be derived from its own record (`model.identity_underivable`)
  or is not the reference workload's sealed identity (`model.identity_mismatch`, §6.5; below). The last two are orchestrator
  ruling N8 (2026-10-07): a reference that ran another model, or cannot show which model it ran, measured a different
  workload, so its energy says nothing about the instrument's drift. Four more losses, set by the seal gate, are
  stated under "Who applies the loss test" below: a reference whose contention evidence or battery evidence is
  unmeasured; one whose quiet state was measurably violated during its request (display awake, screensaver
  running or Low Power Mode on); and one whose battery pair failed (the two registry reads that enclose its
  sampler stream show charging or the loss of AC power, §6.4).
- **Which model a reference must have run.** The 7 references and 7 spares are copies of one workload (their
  configs are 7 reference files and 13 spare files, because each spare's file is repeated in every cumulative
  spare-set directory that holds it; the 13 files have 7 distinct SHA-256s), so the
  harvest checks all of them against one identity unit, `neg8_reference` (`harvest.NEG8_REFERENCE_IDENTITY_UNIT`,
  `_reference_model_identity`; delta audit A2). Before that fix a spare sat in an unpinned group of its own, so a
  spare of another model raised no flag and its energy entered the screen. The expected identity is the sealed pin
  under `units.neg8_reference` of `identity_pins.json` (§4.6 item 3); only when the pins carry none is it the identity
  a strict majority of the window's measured references and spares share, and with no strict majority every
  reference is `model.identity_underivable`. The two outcomes differ:
  - *A reference or spare that ran another model removes the window.* It gets member-level
    `model.identity_mismatch`, and, because the unit then holds two identities, window-level
    `model.identity_inconsistent_in_window` as well (Fable cold pass 4, note N-1). The catalog makes both
    EXCLUDE_WINDOW, and the exclusion function applies that effect whatever the flag's scope, so the window is not
    claim-usable whatever the survivors screen says (the harvest still drops that reference from the screen).
    *Why:* the pack that executed is not the pack that was sealed, which is a failure of number integrity, not a lost
    measurement (orchestrator call (ii), 2026-10-07). Revision 8 wrote that the survivors would decide; that is
    withdrawn for this case.
  - *A reference whose identity cannot be derived is lost, and the survivors decide.* `model.identity_underivable`
    removes only its member (EXCLUDE_MEMBER), so the screen runs on the remaining references as below.
- **The strict check of a reference.** Two checks of a bundle are named here; both are `joulewise/cli.py`
  `validate_bundle`. The **structural bundle check** (the function's default) tests that the bundle's required
  files are present, parse and agree with their schemas. **Strict validation** (the same function with
  `strict=True`; "full strict validation" below) adds, for a member whose summary says `succeeded`, the
  analysis-grade tests: the raw records can be reduced, and the stored summary equals a fresh reduction of them.
  Before the Sol delta audit (finding A5), a reference that had succeeded but
  failed strict validation was handed to the screen with no energy, and the whole screen failed
  (`neg8_bracket_reference_invalid`), although enough valid references survived. Now it is lost before aggregation,
  in three places. The verdict writer (a desk step, not part of the window: the harvest runs
  `scripts/run_campaign.py --whole-window-verdict` after the chain has exited and the ledger pin has been advanced,
  §0.17 and §4.6 item 6) judges a reference by the structural bundle check,
  the custody triangle (when the metadata's `config_sha256` authenticates the bundle's `config.json`, the config, the
  metadata and the summary must name the same telemetry backend, so a mock-instrument bundle cannot pass as a real
  one; `whole_window.custody_telemetry_identity`) and its config binding (its `config.json` is the registered config),
  and records the loss with reason `strict_invalid` (`run_campaign.py` `_idle_admission_core_evaluation`). The replay
  that authenticates a stored verdict row re-checks each reference the row lists as `strict_invalid` (custody triangle
  or strict validation) and reads it if it verifies valid, so a row that dropped a valid reference differs from its
  replay and is refused as `whole_window_verdict_provenance_invalid` (`whole_window._derived_neg8_decision`).
  The harvest drops a reference that fails full strict validation or the custody triangle before re-running the
  screen. The three predicates are not yet one function
  (Fable cold pass 4, note N-3): a reference whose `config.json` disagrees with its registered config is
  `strict_invalid` to the writer but valid to the replay and the harvest, and the window then fails the screen
  (`rederivation_differs_from_stored_bracket`). That outcome is an exclusion, never a pass; one shared predicate is
  part of lane L9-NEG8 (analysis plan §11), which moves the harvest and replay to the writer's predicate and leaves the
  writer's bytes unchanged.
- **Who applies the loss test.** Before cold pass 2 (finding D1), a reference with no readable summary was counted as
  present with no energy, which the screen called invalid, so the window was removed even when the stage's spare had
  succeeded. Two programs apply the test.
  The verdict writer drops a reference whose recorded status is not `succeeded` or cannot be read, or that fails its
  strict check (reasons `status_not_succeeded`, `summary_unreadable`, `strict_invalid`); the harvest, which
  alone sees the monitor journals, runs strict validation and compares model identities, drops a reference that
  carries one of the flags above and re-runs the screen on what survives (`harvest.NEG8_REFERENCE_LOSS_CODES`,
  `_neg8_rescreen`, with `whole_window._derived_neg8_decision`'s `exclude_bundle_ids`; the harvest's
  `model_identity` step runs before the screen and covers reference members). The harvest names the references from
  the sealed roster (each planned reference's `neg8_slot` and each spare's `spare_slot`) as well as from the verdict's
  source manifests, so a known loss reaches the re-screen even when no manifest can be read (delta audit A3: before
  the fix, absent manifests left no reference named and the stored passing screen stood). A reference with several
  of these flags is named by the first in the order physics, `member.timeout`, `member.admission_aborted`,
  `member.strict_validation_failed`, `model.identity_mismatch`, `model.identity_underivable`; a member killed at the
  cap is named `member.timeout`, its physical cause, rather than `summary_unreadable`. A lost reference's energy
  enters neither the screen nor the allowance, for either family. A reference whose contention or battery evidence
  is unmeasured (`contention.unmeasured`, `battery.unmeasured`) is lost, by the test §6.4 applies to a science member:
  the evidence that would show it clean was never taken, and an unseen contender or charge inside a reference can
  move the screen. So is a reference with a measured quiet-state violation or a failed battery pair
  (`env.member_quiet_state_violated`, `battery.capture_pair_failed`). `clock.unmeasured` and `thermal.unmeasured` do
  not lose it, for the reasons §6.4 gives (its own anchor bound and its own thermal records carry the quantity). A
  monitor outage over all three references of one endpoint therefore fails the screen (`references_insufficient`);
  the science members in that stretch are unmeasured and removed in any case. The corpus keeps its own rule (§5.3).
  The loss test never reads the reference's
  energy, so no reference can be dropped for its value. A lost reference's physics flags still apply to every
  science member and calibration they touch; losing the reference cures nothing else.
- **Where the seal gate's two rules stand in the code.** Two rules above were set by the first stage of the seal
  gate (2026-10-07, §12): the loss `energy_unreadable` under "Lost references", and the four losses for evidence
  that is unmeasured or violated under "Who applies the loss test". The harvest at the int5 head `9395cecfb` does
  not apply them yet. There its loss list (`harvest.NEG8_REFERENCE_LOSS_CODES`) holds the six physics codes that
  "Lost references" names, `member.timeout`, `member.admission_aborted`, `member.strict_validation_failed` and the
  two identity codes, and one reference whose energy cannot be read makes the screen fail
  (`neg8_bracket_reference_invalid`). Both rules are added by the harvest lane, a set of changes to programs that
  run only after a window. The lane is committed in a desk checkout, that is, a checkout of the repository other
  than the one the windows run from (§0.18), and §11 item 4 says what it may change. ALPHA-1's harvest does not
  run until the lane is pinned, that is, until an addendum to the seal record names its files and its commit (§11
  item 4). So every block-5 window is judged by a harvest that applies the rules as this section states them.
- **One retry, by spare slot.** When a reference stage ends with fewer succeeded members than it planned, the chain,
  before the next stage, counts the stage's members by their summary status alone and writes that count once to
  `neg8-spares-<stage id>.json` in the chain's transcript directory (a 300 s wall budget, §5.1). It then runs the
  spare set of size k = planned − succeeded (at most the stage's spares) once, into the stage's own **runs root**
  (the directory under which the runner writes a stage's member bundles, its campaign manifest and the **campaign
  log**, `campaign_log.jsonl`, which has one row for each member launched; a window has two runs roots, §0.17),
  after the ordinary 60 s settle and under the ordinary cooldown and admission procedure, provided the collection
  deadline
  allows 60 + 180 + 620 × k s (§5.1). The run is the stage's own command line with two changes: its config directory
  is the spare set's, and it passes `--max-failures k` (the runner's limit on failed members before it ends a stage,
  §5.2), so one failed spare does not stop the spares after it (`chain.spare_argv`). The failed attempt's bundle is
  never moved, re-measured or replaced; both
  attempts stay in the roster, and the spare takes the slot's role (start, midpoint or end), so the screen reads it
  at that position. Each spare that left a bundle is flagged `member.retried` (DISCLOSE; observed: the stage, the
  slot, k, attempt 2). There is one retry per stage; a second loss at the same stage is evidence about the machine and
  is handled by the survivors rule. A retry is never run because a reference's energy is large, differs from its
  siblings or would fail the screen, and a loss found at harvest (contamination) is never repaired by a later
  reference. (`joulewise/b5/chain.py` `spare_retry_lines`, `SPARE_RETRY_HELPER`.) *Code differs from the ruling:*
  the ruling said "immediately"; the chain runs the spares after the ordinary 60 s settle that precedes every
  collection stage.
- **The screen on the survivors.** With n_s surviving start references and n_e surviving end references, the screen
  needs n_s ≥ 2 and n_e ≥ 2. With fewer at either endpoint, `neg8.screen_failed` removes the window with
  `observed.reason` `references_insufficient` and, in `observed.lost`, each lost reference's run id, slot and
  reason. References that never ran count the same way (cold pass 2 N3): a planned roster (one that has a midpoint
  reference, or three references at an endpoint) with fewer than two at an endpoint and no recorded loss is
  `references_insufficient`, not the older "ambiguous reference" condition (`whole_window.evaluate_neg8_point_drift`,
  `run_campaign._idle_admission_core_evaluation`). Those two functions never see a reference that has no bundle, so
  it is the harvest that names each planned reference with no bundle in `observed.lost`, with reason
  `bundle_absent`: it finds them through the slot (`neg8_slot`) that `harvest.build_roster` gives every planned
  reference (`harvest._neg8_lost_rows`). Between two and three at each endpoint, the screen runs as above
  with bound(n_s, n_e). The midpoint is not required by the screen. The code names the shapes (`endpoint_protocol`):
  the planned (3, 1, 3) is `replicated_endpoints_with_midpoint`; any other shape with two or three references at
  each endpoint and zero or one at the midpoint is `replicated_endpoints`; more references than planned is
  `neg8_bracket_reference_invalid`.
- **A lost midpoint.** The window keeps its screen result, its allowance (computed as above with the two-value
  spread) and its numbers, and carries `neg8.midpoint_lost` (DISCLOSE in the catalog). Because the midpoint is the
  only NEG-8 reference inside the window (GAMMA's two diagnostic interior references, after science members 20 and 60,
  are recorded but by rule enter neither the screen nor the allowance), its loss leaves any excursion that reverts by
  the end unmeasured by the allowance. What follows
  depends on the pack. On **GAMMA**, whose window exists for the two primary contrasts, the attempt is not
  claim-usable: the exclusion function adds the window reason `neg8.midpoint_lost_primary`, so GAMMA is re-armed and
  the attempt is never analysed (orchestrator ruling Q11 of 2026-10-07, which the first stage of the seal gate
  confirmed, with the premise corrected as the sentence above now reads; §7.2, §14 Q11; analysis plan §2.4). On
  **ALPHA and BETA** the flag is disclosed only, and the window's reported cells and floors
  stand; the fixed sentence of analysis plan §8.1 discloses that the interior drift was not measured, and that
  window's bound B may be understated by an amount nothing measured. Once a block's midpoint record (read only after
  its release event) shows the midpoint never moved the spread beyond the bound, an erratum may downgrade the flag to
  disclose-only on GAMMA for a later block; it cannot reinstate a block-5 attempt that was re-armed.
  *What the rule costs on GAMMA* (seal gate, first stage, on the refuter's second break). GAMMA does run
  references inside the window, the two diagnostic ones, and the rule sets them aside because the registered
  allowance does not read them. Reading them would change the definition of the allowance in the verdict writer,
  its replay and the claim consumer, and the judge did not order that during the seal. Lane L9-NEG8's design may
  propose a prospective erratum, before GAMMA-1 arms, that reads the surviving interior references into GAMMA's
  spread when the midpoint is lost; the GAMMA reason would then apply only when the midpoint and both interior
  references are lost.
- **Disclosure.** A window whose screen ran on fewer than (3, 1, 3) references records `neg8.reference_lost`
  (DISCLOSE, window level). Its `observed` names each lost reference's run id, slot, reason, status and the outcome
  of its stage's retry (the spares measured and the spares that succeeded; a planned reference that never ran is
  named from the sealed plan tree, with reason `bundle_absent`, cold pass 2 N2), the realised and planned counts,
  and the bound's formula; it also names the record that holds bound(n_s, n_e) and its two terms: the whole-window
  verdict, or `withheld/neg8-rescreen-bracket.json` when the harvest re-ran the screen. *Code differs from the
  ruling:* the flag itself carries no bound value, because a bound is computed from reference energies and flags are
  released as structure (§8). A loss that the retry restored (counts back at (3, 1, 3)) records no
  `neg8.reference_lost`; it is disclosed by the spare's `member.retried` and the lost member's own flag.
  `derived/neg8-screen.json` records the counts, the formula used and which bound was used.
- **Which bracket carries the allowance.** *Forcing problem* (Sol delta audit A1): when the harvest's re-screen on
  the survivors passed, the window was released, but the program that hands each claim its drift allowance
  (`whole_window.whole_window_drift_allowances`) still read the bracket stored in the verdict row, which can hold a
  reference the harvest found contaminated. In the first worked example below that is 0.5933 J where the survivors'
  allowance is 0.6383 J. *Mechanism:* the harvest writes `derived/neg8-allowance.json` (schema
  `joulewise.b5_neg8_allowance.v1`; structure only), naming the verdict row it screened (the canonical SHA-256 of the
  row, and the digest the row stores for its **evaluation basis**, the part of the row that binds the verdict to
  its inputs: the policy file's digest, each member bundle read, the calibration pair and, on a block-5 window, the
  launch lineage; `whole_window.build_evaluation_basis`) and the source of the allowance: `stored_verdict` (no new
  loss, so the row's own bracket stands), `survivor_rescreen` (with the SHA-256 of
  `withheld/neg8-rescreen-bracket.json`, of the bound the re-screen used and, when the corpus was cleaned, of
  `withheld/neg8-clean-bound.json` and the clean corpus manifest),
  or `none` (the screen failed). `harvest.json` lists the record's digest. A claim consumer reads it through
  `whole_window.harvest_neg8_allowance_bracket`, which authenticates each digest, requires the row it is given to be
  the row the harvest screened, and for a survivor re-screen recomputes the allowance from the withheld bracket and
  bound; any mismatch gives no allowance, never a fall-back to the stored bracket. So on a block-5 runs root (one that
  carries the hazard lineage locator, `.joulewise-launch-lineage.json`) a claim consumer must be given the harvest
  archive (`python -m joulewise analyze-claims --neg8-harvest-archive <archive>`); without it the allowance is absent
  and every number that needs it is refused (`whole_window_drift_allowance_unrecorded`). *Two consumers do not reach
  the record yet* (Sol R2 and Sol R3, findings of the Sol re-verification at `fe28e5a0c`, §9.1; Fable cold pass 4,
  D1): floor extraction
  and the mint have no way to receive the archive, so every block-5 floor cell is refused; and the claim validator
  rejects a row whose stored screen failed before it reads the harvest's record, so a window released by a passing
  survivor re-screen gets no allowance for its contrasts. Both refuse; neither can print a wrong number. Both are
  claim-time code that never runs during collection, which §11 item 1 (ii) allows to be fixed after the seal, and
  both are assigned to lane L9-NEG8 (analysis plan §11), which must land, under §11 item 4, before any claim is
  computed. Until it lands, no block-5 floor and no contrast resting on a recorded survivor re-screen has an
  allowance, so none of them is claimable.
- *Worked example (synthetic; recomputed by this author with the code's `neg8_count_adjusted_bound`).* Twelve corpus
  gross energies: 99.62, 99.71, 99.80, 99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22, 100.31, 100.38 J;
  s = 0.2353 J, t(0.975, 11) = 2.201; U_3 = 100.3033, L_3 = 99.7100, U_2 = 100.3450, L_2 = 99.6650 J. Planned
  bound(3, 3) = max(0.5933, 2.201 × 0.2353 × √(2/3) = 0.4228) = 0.5933 J. Start triplet: r1 = 100.02 J, r2 aborted
  by idle admission (a failed bundle; corespotlightd at 0.54 CPU-s/s), r3 = 99.91 J. The chain runs one spare,
  `neg8-window-start-spare-1` = 99.95 J, flagged `member.retried`; start survivors [100.02, 99.91, 99.95], mean
  99.9600 J. Midpoint 100.20 J. End triplet [100.26, 100.19, 101.08] J; at harvest the third end member's request
  overlapped a contender (`contention.request_overlap`), so it is lost with no retry; end survivors
  [100.26, 100.19], mean 100.2250 J. Counts (3, 1, 2): bound(3, 2) = max(max(U_3 − L_2 = 0.6383, U_2 − L_3 =
  0.6350), 2.201 × 0.2353 × √(1/3 + 1/2) = 0.4727) = 0.6383 J. |100.2250 − 99.9600| = 0.2650 ≤ 0.6383: passes.
  Spread = max(99.96, 100.20, 100.225) − min(99.96, 100.20, 100.225) = 0.2650 J; allowance = max(0.2650, 0.6383) =
  0.6383 J; each member carries 0.3192 J. Had the contaminated end member been kept, the end mean would be
  100.5100 J, the screen statistic 0.5500 J (a near-failure caused by a contender, not by drift) and the spread
  0.5500 J. Had the midpoint also been lost, the spread would be |100.2250 − 99.9600| = 0.2650 J, the allowance
  unchanged at 0.6383 J, and the window would carry `neg8.midpoint_lost` (were this a GAMMA window, the attempt would
  then not be claim-usable and GAMMA would be re-armed). The idle-subtracted family subtracts one
  idle energy (here 36.00 J) from every corpus and reference energy, so its s, differences and decisions are the
  same. `neg8.reference_lost` names r2 (`member.admission_aborted`; its stage's spare
  `neg8-window-start-spare-1` measured and succeeded) and the third end member (`contention.request_overlap`; no
  spare, because the loss was found at harvest), counts (3, 1, 2), and `withheld/neg8-rescreen-bracket.json` as the
  record holding bound(3, 2) = 0.6383 J and its terms.
  *The seal gate's two losses on the same numbers.* Suppose the monitor's journal had a gap over the third end
  member's request, so that no overlap could be seen: the member carries `contention.unmeasured` instead of
  `contention.request_overlap`. Kept, as revision 11 had it, its 101.08 J would enter the end mean (100.5100 J) and
  the screen statistic would be 0.5500 J, 0.04 J inside bound(3, 3) = 0.5933 J, with nothing to say whether a
  contender or drift had moved it. Under the gate's rule it is lost exactly as in the first example: end
  survivors [100.26, 100.19], bound(3, 2) = 0.6383 J, statistic 0.2650 J. And suppose the spare
  `neg8-window-start-spare-1` had succeeded with a clock anchor that is not `bounded`: its summary holds no
  envelope for its request energy, so it is lost as `energy_unreadable`. The start survivors are then
  [100.02, 99.91], mean 99.9650 J, the counts are (2, 1, 2), bound(2, 2) = max(U_2 − L_2 = 0.6800,
  2.201 × 0.2353 × √(1/2 + 1/2) = 0.5179) = 0.6800 J, and |100.2250 − 99.9650| = 0.2600 ≤ 0.6800: the window
  passes on its survivors. Before the gate's rule that one reference would have failed the whole screen
  (`neg8_bracket_reference_invalid`) and removed the window.
  *Second example (synthetic, every reference kept).* A bound of 0.40 J; start mean 20.10 J, end mean 20.35 J:
  0.25 ≤ 0.40 passes; with a midpoint reference of 19.90 J the spread is 20.35 − 19.90 = 0.45 J, so the allowance is
  0.45 J and each member carries 0.225 J. In GAMMA, a diagnostic interior reference of 19.70 J would change nothing:
  it is not one of the three values, so the spread stays 0.45 J.
- The NEG-8 screen reads reference-workload energies, never a science member's energy.

### 0.13 Idle admission

Before each member's request, its idle baseline must pass the block-5 policy
`configs/campaign_policies/quiet_mac_p2_b5.json`, SHA-256
`ba0f7b7f1538fe87f6281362efbba4b05f7dff74b4bfd78e84c98b9e8859bc60`. It is the production policy
`configs/campaign_policies/quiet_mac_p2_production.json` (SHA-256
`b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd`) with three cooldown fields changed (§0.6:
`sustained_window_s` 30 → 5, `tolerance_fraction` 0.1 → 1.0, `coverage_fraction` written out at its default 0.8)
and its `policy_id` set to `quiet-mac-p2-b5`. The admission tests below and the retry rule are byte-for-byte the
production policy's. The production file stays unchanged because the older packs and `scripts/run_campaign.py`'s
default still use it. The tests:

- an **environment guard**: AC power, external power connected, displays asleep, screensaver not running, Low Power
  Mode off, thermal state nominal;
- **CPU criteria**: over at least 30 CPU-telemetry samples, the 95th percentile of the CPU busy ratio (the fraction
  of time the cores were not idle) is at most 0.5, and the 95th percentile of processor power is at most 1.0 W.

A refused baseline is retried once, immediately, in the same sampler stream (`retry_attempts: 1`, no wait). A second
refusal aborts the member. In revision 2 an aborted member aborted the whole window; in revision 3 it removes only
that member's unit (§6.3).

### 0.14 The clock

- **The problem.** Each power record carries the sampler's own whole-second wall-clock label and an elapsed
  duration; phase edges are stamped on the machine's clocks. Placing records against phase edges needs the offset
  between the two time bases. An error of 5 ms in that placement moves 0.2 J across one phase edge whose record
  holds 40 W (5 ms × 40 W; block 3's edge records held up to 41.2 W). That is small beside the rest of the same
  member's timing bound (§0.10): the edge part of that bound rests on the fiducial bound, about 46 ms on block 3's
  bracketed window, about nine times 5 ms, and those members' whole bounds were 1.38 to 2.86 J. Condition (e) below
  holds the clock's part to this size, by removing any member whose clock bound exceeds 5 ms.
- **Per-member anchor bound** (`joulewise/uncertainty_evidence.py`, unchanged). The method assumes wall time is
  affine in monotonic time over one sampler stream (one rate, no jump). Each record's endpoint, found by adding up
  the elapsed durations, must fall inside its whole-second label, widened by 250 µs; the set of (offset, rate) pairs
  that satisfies every record at once is computed exactly (this set is the member's **anchor fit**). Its half-width
  at the first record is **h**. The
  **effective bound** is h + the change in (wall − monotonic) over the stream + 2 µs of stamp resolution and
  padding. A member is **`bounded`** only when all six of the following hold (the default method,
  `derive_powermetrics_anchor_v3`):
  - (a) *Enough stream to fix a rate.* The durations of the records after the first, that is, the time from the
    first record's endpoint to the last record's endpoint, sum to at least 60 s, and the controller's own
    monotonic clock, read just before it started the sampler and again after it parsed the sampler's output, spans
    at least that sum. The first record does not count: a stream whose records sum to between 60 s and 60 s plus
    the length of its first record is not `bounded`.
  - (b) The whole-second label changes from one record to the next at least twice in the stream.
  - (c) Every rate in the fit lies within 50 parts per million of 1.
  - (d) The **first parse lag**, the time from the first record's endpoint to the moment the controller first
    parsed the sampler's output, taken at the largest value the fit allows, is between 0 and 0.25 s.
  - (e) The effective bound is at most 5 ms.
  - (f) The inputs are sound: the controller's five clock stamps are present and in order; every record has a
    positive duration, a whole-second label that is not earlier than the label before it and not ahead of it by
    more than the record's duration plus 1 s, and an energy equal to its power times its duration to within
    0.002 J plus 0.1%; and the fit is not empty. (The function names each way an input can fail; these are the
    kinds.)

  This bound is authoritative for every member: a member that is not `bounded` gets `member.anchor_not_bounded`,
  which removes it (§6.3). *Worked example (synthetic).* A stream of 462 records of 130 ms each sums to 60.06 s,
  but the records after the first sum to 59.93 s, so condition (a) fails and the member is removed, although "60 s
  of records" would have passed it. Block 5's idle baseline alone is 576 records, which took at least 75.0 s on
  each of block 3's 37 idle captures (§0.3), so a member that reaches its measured request clears (a) with room.
- **Clock anchor.** CLOCK_REALTIME (the wall clock) minus CLOCK_MONOTONIC_RAW (a hardware counter nothing adjusts),
  read in process. A step of the wall clock moves the anchor at once.
- **Frequency word f.** The kernel's stored rate correction for the wall clock, read without privileges by
  `ntp_adjtime` with `modes = 0` (`joulewise/kernel_clock.py`). With **network time** (automatic clock setting from a
  time server) OFF, nothing steps the clock, and the anchor drifts steadily at rate f. On 2026-10-05 f was
  −3.17 ppm, so the anchor moved about 0.27 s per day.
- **Residual.** The anchor's movement minus f × elapsed raw time. Steady drift leaves the residual flat; a step makes
  it jump.
- **Why f matters to the members.** The middle term of the effective bound grows with |f| × the stream's length. The
  longest stream any `_v5` member can have, **T_stream_max**, is 335 s: an 8B member with both idle-admission
  attempts, its warm-up, prefill, decode and guards
  (`configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json`, SHA-256
  `f414301cd0328236f9309962b60ff4635026dac973ca3b0ce564b677c47baa81`,
  `/derivations/stream_max`: max(15 + 265 + 10 + 2 + 5 + 17, 15 + 265 + 16 + 9 + 13 + 17, 240) = 335 s). The largest
  member half-width h in block 3 was 3.598 ms. The **frequency gate**, one of the checks run just before a window
  starts (the arm, §0.15 and §4.2), predicts the worst member's bound from these numbers before any member runs.

### 0.15 Hazards and the arm

- **Physical hazard.** A condition of the machine that would corrupt a measured energy if collection ran through it.
  Six are registered (§4.2): the clock stepping or drifting beyond budget; the machine off AC power or its battery
  charging (and, at the arm, a battery current above 200 mA in either direction while the machine is idle); OS
  thermal pressure; a competing process
  above 5% of one core; too little free disk for the window; the sampler not sampling at its cadence.
- **Hazard module.** Code (`joulewise/hazards/`, one module per hazard) that measures one physical quantity
  directly, keeps the raw bytes with their SHA-256, and returns **PASS**, **REFUSE** or **UNMEASURED** (the probe
  failed or timed out). A check that reads a proxy for a hazard (a settings string, a receipt, a setter's wording) is
  not a hazard module; doctrine requires measuring the quantity itself.
- **Arm.** The sequence the driver runs after t0 that decides whether this window's chain starts (§4.1). It returns
  **GO** only if no hazard verdict is REFUSE, the instrument's verdict is PASS, the agent census (§4.5) is clean, and
  the machine's OS build and model are ones the calibration acceptance has judged (§4.7). An UNMEASURED verdict
  refuses only for the instrument: a sampler that cannot start or sample is the hazard itself. For the other five
  hazards an UNMEASURED verdict is a failed probe, not a measured hazard, and the monitor measures each of them over
  every member span in the window (§0.17, §6.4); the driver records it in `hazards/arm.json` and as the disclosed
  flag `<module>.arm_unmeasured` (for example `contention.arm_unmeasured`) and the arm goes on (audit A3,
  `joulewise/hazards/arm.py`, `joulewise/b5/driver.py` `normalize_decision`). An arm that raised or timed out as a
  whole is still NULL, because the instrument is then unverified. Nothing else enters the decision. Which refusals the code may contain anywhere, at the arm or later, is fixed by
  one rule (physics or number integrity) that a test enforces (§6.11).

### 0.16 Flags, the catalog, exclusions and claim-usable

- **Flag.** One JSON line (schema `joulewise.flag.v1`) recording one fact: a **code** such as
  `battery.member_span`; a **scope** (window, stage, quad or member); a time interval on the machine's clocks; the
  observed and expected values; the evidence (path and SHA-256 of raw bytes); and a **blinding class**, STRUCTURE or
  RESTRICTED (RESTRICTED for anything computed from a science energy, §8). A flag never stops collection.
- **Flag catalog.** `flag_catalog.json` (schema `joulewise.flag_catalog.v1`), sealed with this file. It gives each
  code a family, a class and exactly one effect. The **class** says what kind of fact the code records: PHYSICS, a
  physical state of the machine; NUMBER, a check that protects a number's integrity (which bytes were measured, by
  which code, with what arithmetic); REPRESENTATION, only the form of a record (a receipt, a schema, a name). The
  three names come from the **gate inventory**, the gate-prune plan's list of every place the block-5 window path
  could refuse (`/Users/edr/night-archive/gate-prune/INVENTORY.md`), which sorted each refusal as physics (measured
  directly or through a proxy), number, representation, or a step that simply cannot run. The **effect** is one
  of: **EXCLUDE_MEMBER** (the member is removed from every cell it feeds), **EXCLUDE_WINDOW** (the window is not
  claim-usable) or **DISCLOSE** (recorded and reported, removes nothing). The harvest looks effects up; it never
  decides them. A code the catalog does not list is **UNCLASSIFIED**: it blocks only the release event (§8) until it
  is classified blind (§7.2), and never blocks collection.
- **Exclusion function.** `joulewise/flags/exclusions.py` `compute(flags, roster, spans, catalog)`: a pure function
  from the flags, the planned roster of members and units, and the members' time spans to a document naming the
  excluded members, the kept units of each cell, and `claim_usable`. A member flag that names its member by bundle id
  instead of run id (the whole-window verdict names members by bundle id) is resolved through the roster's map from
  bundle id to run id; before that fix such an exclusion was silently dropped (Fable audit F9). It reads only each
  flag's code, scope, interval and id, and the roster's pack id, never an energy, power or duration; its tests prove
  this by passing bundles whose energy fields raise when read. Identical inputs give byte-identical output.
- **Pack-scoped window reason.** A DISCLOSE code that removes the window on one pack only. There is one: on GAMMA
  (pack id `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`), `neg8.midpoint_lost` adds the window reason
  `neg8.midpoint_lost_primary` (`exclusions.PACK_SCOPED_WINDOW_REASONS`; §0.12, §7.2). The reason appears in the
  output's `reasons` list like a window-removing code, but it is not a catalog code. The rule is keyed by the roster's
  `pack_id`, which the harvest always sets from the window plan; a roster handed to `compute` without it would apply
  no pack-scoped reason.
- **Claim-usable.** A window is claim-usable when no EXCLUDE_WINDOW code fired, no pack-scoped window reason applies,
  and every target cell keeps at least 5 of its 10 units in each stratum (§6.6).

### 0.17 Driver, chain, monitor and harvest

- **t0** is the planned start instant. The **launchd job**, the macOS scheduler entry installed for the window,
  starts the **driver** `scripts/run_night.py` at t0.
- **Window plan.** The per-attempt file written at the desk by `scripts/write_b5_window_plan.py` (receipt class
  `HAZARD_PACK`): plan id and attempt, the pack, the bracket session id, two freshly created runs roots (a runs
  root is the directory under which the runner writes member bundles, campaign manifests and the campaign log,
  §0.12: the **claim** root takes the science members and every reference member of the window, that is, the start
  triplet, the interior references, the end triplet and any spares; the **bound** root takes the 12 NEG-8 corpus
  members and the bound derived from them), the thresholds of §4.3, the window's sizing (§5.5), and whether G10
  runs at the tail (§3).
- **Chain.** The zsh script the driver launches; it runs the pack's stages in order and writes `night/chain.started`
  when it begins (§5.1).
- **Launch lineage.** A small file in each runs root, published by the driver before the chain starts, that ties
  every bundle to its plan, window and bracket session (`joulewise/window_lineage.py`, schema
  `joulewise.hazard_window_lineage.v1`). The measurement code reads it before writing a `_v5` bundle and refuses a
  member whose configuration bytes are not in the pack's committed inventory (§6.3). Just before launching the chain
  the driver reads each runs root's lineage back with the members' own reader (`_production_lineage_check`). Two
  findings refuse the window. (1) The machine has rebooted since the lineage was published
  (`night_refused_boot_changed`), because member stamps on the monotonic clocks of two different boots cannot be
  placed on one time axis. (2) The publication still fails after its one retry, 5 s later, because the pack's
  committed inventory is unusable (`night_refused_pack_inventory_unusable`, audit A5): no member's configuration bytes
  could then be checked against it, and every member would refuse itself. The driver recognises this case by the
  exception's type, `window_lineage.PackInventoryUnusableError`, which the publisher raises only for it (cold pass 2
  N6; it used to match the message text, so a reworded message would have launched a chain whose members all
  refuse). Everything else is recorded and the chain
  launches: a lineage file that is absent, unreadable, rejected by the members' reader, or naming another plan, window
  or bracket session is `records.lineage_prelaunch_mismatch` (DISCLOSE), and a publication that still fails after its
  retry for any other reason is `records.lineage_formality` (DISCLOSE). Both flags carry
  `observed.science_members_expected_to_refuse`: the runs roots whose lineage could not be read, where the members
  will refuse themselves. Members that cannot authenticate their lineage refuse themselves, and the yield counts
  (§5.7) show it.
- **Monitor.** `scripts/hazard_monitor.py`, a background process that runs from GO until the chain's processes are
  proven gone. It journals the clock anchor every 1 s and the frequency word every 5 s, the battery state (from the
  **registry**, the OS's record of the battery that `ioreg` prints) and the thermal level every 5 s, the battery
  current (from the **SMC**, the Mac's power-management controller; both sources are built in §4.2) every 1 s,
  per-process CPU every 10 s and free disk every 60 s, one append-only file per hazard. Every reading carries three
  timestamps (wall time, the controller's `time.monotonic_ns()`, and CLOCK_MONOTONIC_RAW), so readings join member
  spans exactly. The driver stops it no sooner than 5 s after the chain exits (`joulewise/b5/driver.py`
  `MONITOR_POST_CHAIN_HOLD_S` = 5.0, `hold_monitors_after_chain`), so that the 1 s battery reads cover the end of the
  post calibration (§6.5).
- **Meter.** `scripts/km003c_monitor.py`, a second background process, started and stopped with the monitor, that
  records the whole machine's DC input through an inline USB-C power meter (§5.8). It is a diagnostic: it never
  refuses, removes or enters a claim number. The driver runs it under its own supervisor (`MonitorSupervisor`, name
  `meter`), which restarts it after a crash but never after a clean exit, because the reader exits cleanly when no
  meter is attached.
- **Harvest.** `scripts/harvest_b5_window.py`, the desk program run after the chain exits. It archives the window,
  re-derives every number-protecting check from the preserved bytes (for the NEG-8 screen, by running the production
  verdict writer itself on those bytes and then re-screening on the survivors whenever a reference carries a loss
  flag; a stored bracket with no reason and no new loss is read as written), joins the monitor's journals to the
  member spans, writes every flag, and runs the exclusion function (§7.1). The row it writes never authenticates
  under the validator's consumption semantics, so `whole_window.verdict_unauthenticated` (DISCLOSE) is recorded on
  every window and carries no information about the window.
  Three terms of those two sentences. The **stored bracket** is the verdict row's **NEG-8 bracket**: the row's own
  record of the NEG-8 screen, with the references it read and, for each family, the bound and the allowance. It
  is not the calibration bracket of §0.11. The **validator** is `whole_window.validate_whole_window_verdict_row`,
  the function by which a later reader authenticates a verdict row by replaying it from the bundles the row
  names. A **consumption semantics** is the registered rule by which such a reader chooses the fiducial bound it
  re-reduces members under (block 5's is the operative bound of §0.10); under every such rule the validator needs
  a consumption session (§0.10), and the harvest has none to give it, so at the harvest the validator reports
  every row as not authentic (`harvest.whole_window`, `harvest._neg8_rescreen`).
- **Whole-window verdict.** One row, produced by the harvest with the production writer
  (`run_campaign.py --whole-window-verdict`), stating whether the window as a whole passed: every member admitted,
  the AC adapter's wattage unchanged, the CPU criteria held, the NEG-8 screen passed, and the bracket, read through
  its bracket binding, passed the acceptance (`joulewise/whole_window.py`). Its overall pass or fail removes nothing.
  Each of its parts acts through its own code: the NEG-8 screen and the bracket at window level, and each member's
  own failures at member level (§6.5).

### 0.18 Commits and the seal

*Forcing problem.* A window's numbers can be sealed only if the bytes the window ran are the bytes that were
reviewed. The sealed inventory therefore lists those bytes and names, in its `head` field, the commit that holds
them. But a file cannot name the commit that contains it: a commit's name is a hash over its content, so writing
the name into one of the commit's own files would change the name. The filled inventory, and every sentence of
this file that prints that commit's name, can only be committed in a later commit. So the windows do not run
*from* the commit whose bytes are sealed. They run from a later commit, and a comparison must show that the later
commit holds the same bytes wherever a window can read them. The terms below name the commits and that comparison
(orchestrator's ruling of 2026-10-07 on the procedure of lane `lane/2026-10-07-seal-landing`,
`/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/SEAL_LANDING.md`; §11 gives the rule in full).

- **H.** An exact git commit, named by its 40-character hash. Three git words are used below. A file is
  **tracked** when git records it in commits. A commit's **parent** is the commit it was made on top of. A
  checkout's **HEAD** is the commit it has checked out.
- **Window input.** A tracked file whose bytes a window can read while it is planned, armed or run: every file
  under `joulewise/` and `scripts/` (the code); every file under `configs/` (the packs and the files their plan
  trees pin, the flag catalog, the identity pins, the sizing output, the policies, the calibration files); and one
  document, `docs/phase_2/window_runbook.md`, because the plan writer copies its pre-calibration screen into the
  chain. Four files under `configs/` are excepted, although a window reads them. One is the ledger pin (§0.11),
  `configs/calibration/calibration_ledger_head.json`: it is data that the desk advances after every window, so it
  must be able to change after H_claim ("Pin-only commit", below). The other three are the seal documents, below.
- **H_claim.** The last commit that changes any window input. Every block-5 window runs the window inputs that
  H_claim holds.
- **Seal documents.** Three files of this directory: `sealed_inventory.json`, this file and the analysis plan.
  Their final bytes cannot exist at H_claim, because they name it. At H_claim they are the inventory stub
  (`status` `STUB_NOT_SEALED`, `head` null, `files` null) and the two texts as the seal gate judged them, with the
  markers of the header still open. Every other sealed file (the flag catalog, the identity pins, the sizing
  output, the three packs, the runbook) is a window input and has its sealed bytes at H_claim.
- **Seal commit.** The one commit whose only parent is H_claim and which changes the seal documents and nothing
  else. It carries the filled inventory (`status` `SEALED`; `head`, the name of H_claim; `files`, the SHA-256 at
  H_claim of every tracked file under `joulewise/`, `scripts/` and the three pack directories and of the flag
  catalog; the ledger pin is not listed) and the final bytes of this file and of the analysis plan. This file's
  bytes never change after the seal commit: each window plan is written from a plan-input file (the desk file
  from which the plan writer writes a plan) that names this file by path and SHA-256 (the lead's rule, §12; the
  plan writer also accepts an input that names no registration), the plan writer refuses a checkout whose copy
  does not hash to the value it is given (`joulewise/b5/plan.py`), the plan records the value, and the harvest
  stops with a fault when the copy it reads differs from the plan's digest (`joulewise/b5/harvest.py`, problem
  `registration_digest_differs_from_plan`; a harvest fault is a tooling outcome, cured and re-run on identical
  bytes, §7.1).
- **Seal record.** A file under `docs/process_traces/`, committed after the seal commit, that lists H_claim, the
  seal commit and the SHA-256 of every sealed file (§12). Nothing lists the seal record's own hash, so no file has
  to contain its own hash; this file names the record by its path. A value that comes into being only after the
  seal commit is appended to the seal record as a named section (the header names two such values).
- **Pin-only commit.** A commit that changes only `configs/calibration/calibration_ledger_head.json`, the ledger
  pin (§0.11). The pin is data that advances after each window (§4.6 item 6), not code.
- **Measurement checkout.** The dedicated clone of the repository that the windows run from (the seal-landing
  records call it the measurement clone). It is a full clone, one that holds every commit of the repository's
  history, checked out at the seal commit. The only commits ever added to it are pin-only commits, made by the
  pin-advance program (§4.6 item 6), which commits the pin's path alone and
  then refuses if the commit it made changed any other path (`joulewise/b5/plan.py`, "the pin commit is not
  pin-only"). A **desk checkout** is any other checkout of the repository. Desk programs (the harvest, the
  analysis) run from one: they import their own checkout's code and are given the measurement checkout as the
  place to read a window's inputs and bytes from (`measurement_root`).
- **Executed head and executed-file inventory.** At each arm the driver records the measurement checkout's HEAD
  (the **executed head**: the seal commit for the block's first window, the latest pin-only commit afterwards),
  its `git status`, the chain's bytes, and the SHA-256 of every tracked file under `joulewise/`, `scripts/` and the
  window's pack (the **executed-file inventory**). The window plan's `measurement_head` field holds that same
  commit: the program that installs a window's launchd job refuses unless the field equals the checkout's HEAD
  (`joulewise/night_agent_install.py`).
- **The two comparisons with the seal.** The harvest makes both (`harvest.code_identity`). A difference found by
  either is `code.executed_differs_from_sealed`, which removes the window (§6.5).
  - *Per file.* Every file under `joulewise/`, `scripts/` and the window's pack, executed against sealed: a
    changed, missing or added file is a difference. (At the arm, the collector that §4.1 lists as the
    executed-file inventory hashes the same files itself and makes the same comparison, recorded as a flag.)
  - *Head comparison.* The harvest runs `git diff --name-only --no-renames -z H_claim..<executed head>` in the
    measurement checkout, taking H_claim from the sealed inventory's `head`. Each path the command lists falls in
    one class (`harvest.head_change_class`): `pin_only`, the ledger pin; `seal_document`, the three seal
    documents; `window_input`, any other path under `joulewise/`, `scripts/` or `configs/`, and the runbook
    (matched without regard to letter case, because the measurement Mac's volume does not distinguish case);
    `record_only`, every other path (documents, tests, `RUN_STATE.md`). Only a `window_input` path is a
    difference. The four lists are written to `derived/code-identity.json`. If the command cannot run, the window
    is `code.identity_unmeasured` instead, which also removes it; that is why the clone is a full one, with
    H_claim in its history.

  For the identity pins, the sizing output, the flag catalog and the runbook, the head comparison is the only
  check that code makes: they lie outside a window's **executed roots** (`joulewise/`, `scripts/` and the
  window's own pack, the three directories that the executed-file inventory and the per-file comparison cover),
  and no plan tree pins them.

  This is the comparison as the code at the int5 head `9395cecfb` makes it. The harvest that judges block-5
  windows differs from it in five details, which the harvest lane of §11 item 4 adds in a desk checkout before
  ALPHA-1's harvest (`/Users/edr/night-archive/gate-prune/wave-1007b/harvest-lane/WORKLIST.md`, items H-8 to
  H-12, from the orchestrator's ruling on the seal-landing review and from cold pass 5, §2 item 1): `record_only`
  becomes a positive list (`docs/` except the runbook, `tests/`, dot-directories and Markdown files at the
  repository's root), so that any path not on it is a window input; a sealed inventory with no `head` is
  `code.identity_unmeasured`; a code file that differs between the sealed inventory and a separate driver
  checkout (a checkout other than the measurement checkout from which a window's launchd job was installed, §2
  item 5) is a difference; a changed path whose name is not valid UTF-8 no longer stops the harvest with a fault;
  and a commit confined to the directory of one of the three packs other than the window's own is recorded and is
  not a difference. §11 item 2 states the comparison in that final form.

```
 integration branch    ... ── C ─────── S ─────── R ── ...
                              │         │         └─ R: adds the seal record (a path under docs/, so record_only)
                              │         └─ S, the seal commit: changes only the three seal documents
                              └─ C = H_claim: the last commit that changes a window input

 measurement checkout  ... ── C ── S ── p1 ── p2
                                   │    │     └─ p2: pin-only commit after BETA-1; the executed head of GAMMA-1
                                   │    └─ p1: pin-only commit after ALPHA-1; the executed head of BETA-1
                                   └─ S: where the clone is checked out; the executed head of ALPHA-1
```

Each `──` joins a commit to its child, left to right. C, S and R are consecutive commits on the integration
branch `integrate/2026-10-07-int5`. p1 and p2 exist only in the measurement checkout, and the picture shows a
block in which each pack is armed once; a re-armed pack adds one pin-only commit per attempt. Each window's
harvest compares its executed head (S, p1 or p2) with C.

*Worked example* (the seal-landing lane's proof run on a disposable clone, 2026-10-07, with the lane's last
commit `2737ef88c` standing in for C; `seal-land/proof-landing.log` beside the procedure, read by this author; §11
item 2 walks through the whole run). The inventory generated from C lists 682 files: 150 under `joulewise/`, 165
under `scripts/`, 123, 123 and 120 in the three packs, and the flag catalog (this author counted the same six
numbers with `git ls-files` at the int5 head `9395cecfb`). S changed three paths, the seal documents. After one
commit of records (two paths) and one pin-only commit, the comparison from C listed six paths: one `pin_only`,
three `seal_document`, two `record_only` and no `window_input`, so no flag was raised. One further commit that
edited `identity_pins.json` added one `window_input` path, and the window was
`code.executed_differs_from_sealed`. (The proof ran the arm's collectors with C passed in by hand. At a real arm
the collector is given the plan's `measurement_head`, which is the executed head itself, so its own head
comparison lists nothing; the harvest's comparison is the one that ties a window to the seal.)

**"H_claim plus pin-only commits".** Passages of §7.5, §11 and §14 that the seal gate's first stage wrote say
that the measurement checkout's HEAD stays "H_claim plus pin-only commits", or "at H_claim", for the whole block.
The judge's ruling notes that it had not read the landing procedure. Read with the terms above they mean: the
checkout holds H_claim's window inputs throughout, at the seal commit or at a pin-only commit after it. The seal
commit differs from H_claim only in the three seal documents, which are not window inputs.

### 0.19 The claims ladder

`docs/contracts/claims_ladder.md` fixes how strong a sentence may be. **L1** (instrument result): on this exact stack
(machine, OS build, runtime, model, quantization, sampler) and boundary (what energy the sampler covers, here
`M3 Max / MLX / powermetrics` SoC rails), this quantity was observed. **L2** (comparative result): one condition
differed from another within one boundary, with intervals reported, interleaved order, and the effect above the
detection floor. L3 and L4 (a fitted model checked on held-out cells; replication across machines) are out of reach.
**Holm** is the correction that keeps the chance of any false positive across the two contrasts at 5%.

## 1. Purpose, and what each window can support

Block 5 collects the three claim-bearing `_v5` windows. Their bytes are the only sources of the `_v5` numbers the
capstone paper can print: the reported phase energies (D-179), the detection floors (D-117/D-124), the dominance
ratios (D-165/D-168) and the two model contrasts (GAMMA's frozen prospective analysis manifest).

**Dominance ratios.** For each model, phase and floor form, R = (detection floor with each value free to move within
its timing uncertainty) ÷ (the same floor with every value at its point value) (analysis plan §6). R ≥ 2 means
timing uncertainty at least doubles the floor. The **contingent subtitle** is the "attribution-limited" paper
subtitle D-165 licenses only when every required ratio is at least 2.

| Window(s) | What it can support | Rung | Why not higher |
|---|---|---|---|
| ALPHA, its first claim-usable attempt | Reported phase energy of Qwen3-1.7B for decode and prefill-p2048, each with its interval, J/token, kept units and the attribution floor beside it; the 1.7B floor cells | L1 | One stack, one boundary, no comparison |
| BETA, the same | The same for Qwen3-8B | L1 | Same |
| ALPHA beside BETA | Side-by-side L1 cells only, labelled as collected in separate windows in a fixed order | L1 | Forced order stays below L2; the two models were never interleaved |
| GAMMA with the ALPHA and BETA floors | Two primary contrasts (8B minus 1.7B phase energy, decode and prefill-p2048), Holm family of two, plus the registered ratio and per-token difference (analysis plan §7.3) | L2 if and only if the **claim gate** returns `claim_ready_for_l2_l3` true. The claim gate is the analysis program's decision function for one contrast (`joulewise/analysis_engine/claims.py` `evaluate_claim`); it returns that value true only when every condition of analysis plan §7.2 holds, chiefly: the contrast's direction is supported (the estimate is above the detection floor, its intervals exclude 0 and the Holm correction rejects), the contrast is one that GAMMA's analysis manifest registered in advance as primary and confirmatory, dropping any one quad leaves the verdict unchanged, and the direction is the registered one | No held-out cells, no second machine |
| Floors and GAMMA | Dominance ratios; the dominance sentence and the contingent subtitle only if every required ratio is at least 2 | Disclosure | D-165 addendum |

Every phase-energy sentence carries the D-177 limitation (phase attribution was not characterized by a measured
instrument check). Nothing here supports a prompt-population claim (one fixed decode prompt), a claim about prompt
lengths other than 2048, or a claim outside one measurement boundary. **Boundary label** (`BOUNDARY-LABEL`, filled
from committed bytes): `M3 Max / MLX / powermetrics SoC rails`, the claims ladder's form (§0.19). Every bundle records
the same boundary as `"boundary": "Apple SoC CPU + GPU + ANE package power"` with rails `cpu_power`, `gpu_power` and
`ane_power` (`joulewise/adapters/powermetrics.py`, `_base_device_metadata` and `RAIL_MANIFEST`). The identity pins
record it for each identity unit, that is, each model running one workload in one pack
(`stack_identity.measurement_boundary_label` in `identity_pins.json`, §4.6). The energy reported is therefore that
of the processor package rails, never wall power or the whole machine. The whole-machine meter of §5.8 measures a
wider boundary (the Mac's DC input); its numbers are a descriptive cross-check (analysis plan §8.2) and never a claim.

What the paper prints, and from which artifact, is fixed in analysis plan §9; printing anything needs the placement
ruling of §14 Q4.

## 2. Preconditions

Each is evidenced by a path and SHA-256 before the point named.

**Before ALPHA-1 arms:**

1. H_claim is fixed (§0.18: the last commit that changes a window input). **H_claim is `FILL[H-CLAIM]`**, on
   branch `integrate/2026-10-07-int5`. It carries PR #483 (the `_v5` qualification-code integration), lanes L1–L4,
   L7 and L8 of the gate-prune plan, the timing lane of 2026-10-06 (block-5 policy, idle records and settles; branch
   `lane/2026-10-06-timing-policy`), the core-prune lanes and gate-prune round 2 (integration head `b9d02700a`,
   branch `integrate/2026-10-06-gate-prune-3`), the P3 round (lanes `lane/2026-10-06-p3-{harv,haz,drv,wd}`) and
   lane L10, the two audit-fix lanes of 2026-10-07 and the NEG-8 survivors lane (revision 7 list), the cold-pass-2
   fix lane and the rulings Q11 and N8 (revision 8 list), the census-ancestors and NEG-8 delta-fix lanes, the sealed
   reference pin and the T3 prune (revision 9 list), the census interpreter rule (revision 10 list), the
   seal-landing lane (the head comparison of §0.18) and the changes that the seal gate's first stage required
   before the head could be fixed (revision 12 list, item 9), merged under the merge gates, with
   one consolidated Fable cold pass over the measurement code changed since `e6b6a0ce` (done at the frozen head
   `a434e363d`, `/Users/edr/night-archive/gate-prune/cold-pass/`) and Fable delta cold passes over the measurement code
   changed after `a434e363d`. In the order they were merged, H_claim holds: the frozen head
   `a434e363d96621318657418e60b8d14410079d82` (the refusal census and its triage, revision 6 list); the three lanes
   of revision 7; the changes of revision 8 (at `43ac12d0c`); those of revision 9, up to
   `fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7` (`/Users/edr/night-archive/gate-prune/FROZEN_HEAD_4.md`); the census
   interpreter rule (lane `lane/2026-10-07-census-interp`, last commit `455e59b86f19dcdf4c25ca464dbed17be4e51ec3`,
   merged into int5 by commit `84661ddb36865c6c478fc7b862d1bc274f1921cd`; §4.5); the placement of these documents
   in the code tree (commit `763b678a7`, and the test fixture that follows it, `9b0c680ed`); the seal-landing lane
   (lane `lane/2026-10-07-seal-landing`, last commit `2737ef88c92754fe20c8417f66dc62edc7d0ae8c`, merged into int5
   by commit `9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a`); and what was merged after that commit, which the last
   paragraph of this item bounds. The delta cold passes:
   - pass 2, on `a434e363d..821b58f8b` (`/Users/edr/night-archive/gate-prune/cold-pass-2/REPORT.md`), refused on one
     defect, D1 (§0.12); D1 and the notes N1–N3 and N5–N7 are fixed in `d06ab4778`, merged at `ffdca2250`;
   - pass 3, on `821b58f8b..43ac12d0c` (`cold-pass-3/REPORT.md`): PASS WITH NOTES; D1 fixed on all three paths, no
     defect;
   - pass 4, on `43ac12d0c..fe28e5a0c` (`cold-pass-4/REPORT.md`): PASS WITH NOTES; one defect, D1 of that pass, in
     claim-time code (floor extraction cannot receive the harvest archive, §0.12), which the pass judged not to block
     the seal or the arm, assigned to lane L9-NEG8 (analysis plan §11);
   - pass 5, on `fe28e5a0c..9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a`
     (`/Users/edr/night-archive/gate-prune/cold-pass-5/REPORT.md`, SHA-256
     `46446fa429bdceaac91da1bb3916714c3c59fd846c6bf4503bad4462e218e8ad`, computed by this author with
     `shasum -a 256`): PASS WITH NOTES. It covers three things. The first is the census interpreter rule (§4.5: how
     the agent census reads the command line of a JavaScript runtime). The pass ran the matcher, the function that
     applies the rule, on 36 command lines, and each got the verdict the pass's brief expected of the code at
     `9b0c680ed`; and a real `node` process, started with the option that finding Sol R1 had shown the earlier
     matcher to misread (`--trace-require-module all`, §4.5), was counted by the census as an agent, which §4.5
     calls a hit. The second is the placement of these documents in the code tree. The third is the seal-landing
     lane's change to the head comparison (14 cases, C1 to C14, each run through the harvest and through the arm's
     collector on a real git repository). One defect, of the
     kind that removes too much and never prints a wrong number: a commit after H_claim that changes only the
     directory of another claim pack is classed as a window input and removes a window that never read that directory.
     It cannot arise under the registered procedure, in which only the pin advance commits in the measurement checkout
     (§0.18), and the pass itself disposed of it as "flag, not refuse": it is assigned to the harvest lane (§11 item
     4; §0.18 lists it).

   The seal-landing lane also had an independent executing review, that is, a review by a seat that had not written
   the lane and that ran its code (`/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/REVIEW.md`, SHA-256
   `fec2dc44938731c8528777b66c336df07ca553ff6f43f2bcd146cab641012f0a`; reviewed commit `2737ef88c`). It made sixteen
   changes to a window input after H_claim, one at a time (a byte added to a code file, to a pack file, to the
   identity pins, to the sizing output, to the catalog and to the runbook; a new file, a deleted one, a moved one, a
   changed file mode), and found the window removed every time by the harvest, and by the arm's collector when that is
   given H_claim by hand; it found no permitted kind of commit that removed a window; and it carried the procedure out
   as written. It reported one major gap, which the lane had itself raised and which is older than the lane: a launchd
   job installed from a checkout other than the measurement checkout runs that checkout's driver, hazard modules,
   monitor and collectors, and when those files differ from the sealed inventory the code at `9395cecfb` only records
   the fact. The orchestrator's ruling (`seal-land/ORCHESTRATOR_RULING.md` beside the review, 2026-10-07, SHA-256
   `92ba27dc49ce205e76111a46bdddda6450ba21863feb8f5d1177527be27fde4e`) sends that gap and three smaller findings to
   the harvest lane, because each check lives in the harvest (§0.18 lists them; §11 item 4), and item 5 below keeps
   the major case from arising.

   The four pinned estimator files (`joulewise/reduce.py`, `uncertainty_evidence.py`, `powermetrics_fiducial.py`,
   `adapters/powermetrics.py`) are byte-identical from `a434e363d` to `fe28e5a0c`, to the int5 head `9b0c680ed` that
   revision 10 read, and to `9395cecfb` (`git diff`, empty each time, run by this author).

   *What H_claim may add after `9395cecfb`.* Pass 5 and the review read the code as it stood at `9395cecfb`. The
   seal gate's first stage then required changes that had to be committed before the head could be fixed, because
   they touch files under `configs/`, which are window inputs: the flag catalog's `rules.cell_unit_minimum` and
   note texts, and entries of the refusal allowlist `configs/gates/hazard_refusals.json` (§12; revision 12 list,
   item 9). No window executes either file as code, and the catalog is one of the four documents that the second
   stage of the seal gate judges (§12). If H_claim changes any file under `joulewise/` or `scripts/` after
   `9395cecfb`, a further delta cold pass over that difference is part of this precondition. Revision 10 repeated
   the sync of item 8 on the difference `fe28e5a0c..9b0c680ed` (§13, `B5-REV10-SYNC`), and revision 12 repeats it
   on `9b0c680ed..9395cecfb` (item 8).
2. The #416 pre-arm triple audit has run, and every BLOCKER or MAJOR it found has been sent to a refuter of another
   model family and, if confirmed, fixed (§9.1). **`416-AUDIT-RECORD`** (filled in revision 8): see §9.1. The
   diff-scoped re-audit of the fixes made since has run, and every BLOCKER it found is fixed or assigned to the
   claim-time lane L9-NEG8: **`416-DELTA-RECORD`** (filled in revision 9), see §9.1. For the code merged after
   `fe28e5a0c`, the delta record is the two records of item 1: Fable delta cold pass 5 and the independent
   executing review of the seal-landing lane (§9.1 gives each finding and where it went; §13).
3. This file, the analysis plan, the flag catalog and the sealed inventory are sealed (§12): the seal commit
   exists, its only parent is H_claim, and it changes only the three seal documents (§0.18;
   `tests.test_b5_seal_landing` checks all three statements, and that the inventory lists exactly H_claim's files,
   from git objects); and the seal record exists and pins the four files. The seal record is
   `FILL[B5-SEAL-RECORD]`.
4. The three packs as the timing lane regenerated them, with GAMMA as lane L10 changed it and every reference stage
   carrying its spares (§0.7, §0.12), are at H_claim, and their files are in the sealed inventory. The spare configs
   and spare-set manifests, like the window references, sit outside the pack directories and are pinned by SHA-256 in
   each plan tree. Every window plan, and every plan-input file it is written from, uses
   the sealed threshold block of §4.3 (contention `clean_s` 180) and is written after the seal commit. A plan
   written earlier cannot be used: a plan's `measurement_head` must equal the measurement checkout's HEAD when its
   launchd job is installed, which is the seal commit or a later pin-only commit, and a plan is given this file's
   SHA-256, which exists only from the seal commit on (§0.18). The record that the plans were written this way is
   made after the seal, so it is not in this file: it is the seal record's section `FILL[B5-PLANS-REGENERATED]`.
5. The measurement checkout (§0.18) is a full clone of the repository, made without `--depth` so that H_claim is
   in its history, and checked out at the seal commit, with its Python environment relocked and the ledger seed
   (§4.6 item 6) installed at its default ledger path. `git diff --name-only --no-renames H_claim HEAD` in it
   lists the three seal documents and nothing else, and `git status --porcelain` prints nothing. The launchd job
   of every window is installed by this checkout's own `scripts/install_night_agent.sh`. *Why:* the driver, the
   hazard modules, the monitor, the collectors, the G10 program and the meter program run from whichever checkout
   installed the job (`scripts/run_night.py`, `joulewise/b5/driver.py` `production_seams`), while the chain's
   tools run from the measurement checkout; installing from the measurement checkout makes them one checkout, so
   that the executed-file inventory covers everything that runs. If the two ever differ, the driver records the
   other checkout's files (`driver_checkout`), and what follows is §11's rule. The pull request that brings
   H_claim and the seal commit to `main` is merged with a merge commit, never squashed or rebased: a squash would
   replace both by one new commit, and the head comparison needs H_claim itself in the history.
6. A harness render of all three packs' chains through the `HAZARD_PACK` driver has passed (every expected
   bundle present, driver return code 0), and a desk dry arm with agents alive has refused at the census before any
   action. The render is a test of the driver and the generated chain, not of the real tools the chain calls: the
   harness (`tests/test_b5_driver.py` `Harness`) replaces those tools with stand-ins that write only the files the real
   tools leave, and it uses fixture thresholds and a fixture sizing. (The records call it the "L2 harness" after
   lane L2 of the gate-prune plan, the lane that wrote the driver and this test rig; that L2 is a lane number and
   has nothing to do with rung L2 of the claims ladder, §0.19.) The real campaign runner, cooldown and idle
   admission were exercised by the cooldown smoke run-4 (item 7) and by the real-model rehearsal of 2026-10-06
   (`/Users/edr/night-archive/gate-prune/rehearsal-real/`, whose reference bundles the sealed reference pin was
   derived from, §4.6 item 3). Both records were written at the int5 head `fe28e5a0c` by a Sonnet 5.5 investigation
   seat in a fresh clone, with no repository change
   (`/Users/edr/night-archive/gate-prune/dry-records-2/DRY_RECORDS.md`, SHA-256
   `4e2570b31f169094bff4caf2feb4030ce2ad6bc59f7ac7fc6a7943747074db9b`; every SHA-256 below recomputed by this author).
   **`B5-DRY-RENDER-RECORD`** (filled in revision 9). 2026-10-07 20:17–20:19 UTC, interpreter
   `/opt/homebrew/bin/python3.13` (not the project environment), each pack rendered twice: once clean and once with
   every reference stage failing on purpose, so that the spare-slot retry runs (`rig/dry_render.py <pack> <out>
   [--fail-references]`). All six renders: driver GO, chain exit 0, no missing or extra bundle, NEG-8 corpus 12 listed
   and 12 kept, the monitor proven stopped, G10 discharged. Counts: for claim bundles (the bundles in the claim runs
   root, §0.17), expected / present / directories / succeeded; for bound bundles (the 12 NEG-8 corpus members in
   the bound runs root), expected / present / succeeded; and the spares run:

   | Render | Claim bundles | Bound bundles | Spares run | Stage rows (rc 0) | Flags emitted |
   |---|---|---|---|---|---|
   | ALPHA clean | 107/107/107/107 | 12/12/12 | 0 of 7 | 22 (22) | `network_time.off_output` |
   | BETA clean | 107/107/107/107 | 12/12/12 | 0 of 7 | 22 (22) | `network_time.off_output` |
   | GAMMA clean | 89/89/89/89 | 12/12/12 | 0 of 7 | 22 (22) | `network_time.off_output` |
   | ALPHA, references failed | 107/107/114/107 | 12/12/12 | 7 of 7 | 25 (22) | the above and `yield.stage_low` ×2 |
   | BETA, references failed | 107/107/114/107 | 12/12/12 | 7 of 7 | 25 (22) | the above and `yield.stage_low` ×2 |
   | GAMMA, references failed | 89/89/96/89 | 12/12/12 | 7 of 7 | 25 (22) | the above and `yield.stage_low` ×2 |

   In each failed render the three reference stages that fail on purpose return 1 (the stand-in runner's member
   failures), which is why 22 of 25 stage rows return 0, and the driver still returns GO; the seven spares run as
   planned (start 1–3, midpoint 1, end 1–3). The counts equal those of the earlier render at `43ac12d0c`
   (`dry-records/DRY_RECORDS.md`) number for number. *Stand-ins:* the agent census (a clean fake), the hazard arm (all
   six modules PASS), the network-time setter (a state file), the lineage publisher and verifier, the hazard monitor,
   the record-only collectors, the G10 program, the free-disk reading, the driver's two last steps (the **durable
   record**, a best-effort copy of the window's record files in `night/`, without the chain's logs, pushed to a
   results branch `night-results/<plan id>` of the repository; and the **courier**, one headless session that
   emails Ed the window's structural report and writes `night/courier.sent` once the email is accepted, §5.4), and
   the five chain tools of the fake measurement checkout: the bracket reserver, the powermetrics fiducial capture,
   the campaign runner, the ledger session-status reader and the window verdict writer. Because the runner is a
   stand-in, the
   controller, the runtime adapter, telemetry, the bundle writer, the cooldown and idle admission do not run in the
   render. Reductions: 0 s settles, a fixture sizing with a 3,600 s programmed span, placeholder heads, and fixture
   thresholds instead of the sealed block of §4.3. Render summaries, SHA-256: ALPHA
   `ebfad2165321886f597478f97b95945d3c9ef5cbc89a1b231733e7b2be5699b8`, BETA
   `6da7dad82314a97ca3519c1807a2e99f628185a1c9e648ddfffbf78e8886acd4`, GAMMA
   `ade57caaebe52f0810a588a33ba96bde902078163b980465b4ee0cb7721e5e07`; with failed references ALPHA
   `78b099dabda9a1502dd60e949f32b95f985ed0c2b4cad549219be9f98c0a9e27`, BETA
   `912b9ba2a011d892e3c5655f381f40d9ff0f7cf38a675bf3d935fee095074d23`, GAMMA
   `03a8248b8c809ffeced32df9131d33a5fa757d2babbc30cdb5f5630d2ab1c9a1`. The harness's own whole-run tests
   (`tests.test_b5_driver.MockRuntimeDryRenderTests`, `DryArmTests`) passed, 5 tests.
   **`B5-DRY-ARM-RECORD`** (filled in revision 9). 2026-10-07 20:16:52 UTC (`dry-arm.json` records its start as
   `started.wall_s` 1791404212.513914, which is 20:16:52.51; the prose summary `DRY_RECORDS.md` prints 20:16:51,
   one second early), the production command, unmodified:
   `scripts/run_night.py run --plan <custody>/night_plan.json --dry-arm`, on an ALPHA `HAZARD_PACK` plan
   (`DRYARM-b5-alpha-desk`) written by the production plan writer over the fake measurement checkout (plan SHA-256
   `d3fda4ab0246f81f47e1ca4b8f1c637e7a62f6f0d3a1a1d696ee1bacb84f56b4`). Nothing was stubbed: the real `pgrep` census
   and the production code ran. Exit 3 (refused) after 0.177 s; record `dry-arm.json` (SHA-256
   `0b9b2ad76a9ba4cd2d2c38aa654bbd72fa8f1ab0c28a38a9a1427fcbc4bd4417`): verdict REFUSED, stage `census`, reason
   `night_refused_agent_present`, arm not run, nothing launched, zero network-time calls, zero collector calls. The
   census argv was `/usr/bin/pgrep -a -lf '[c]odex|[c]laude'`; it listed 13 processes, of which 9 were agents and 4
   were shells the matcher ignored (`not_agent_executable`). Among the 9 was the investigation seat's own `claude`
   process, the grandparent of the dry arm, which the census at `43ac12d0c` could not see (F1; §4.5); seven others
   were Codex processes (an exec seat of another session, a Codex MCP server, their vendor binaries and a bridge
   server) and one was an `npm exec` process (the census note below). No window or rig process was a hit.
   The digests of the custody tree, the ledger, the runs roots, the backup destinations and `~/Library/LaunchAgents` were unchanged, and `night/`,
   `hazards/` and `flags/` were never created. The other record files: `dry-arm-summary.json`
   `c572568c201dbe6ecbdb2e67243a7b289a84648668e48962d4ceb5f153a06f43`, `run_night.stdout.txt`
   `9cd97d2a40cc61648433109bb35821ce7ee4a1a9402ce1119ed94f60c28f0e73`. *Privacy:* `dry-arm.json` and
   `dry-arm-summary.json` keep the census output verbatim, which holds the full command lines (prompt text included)
   of other sessions' agent processes; they stay in `night-archive` and are cited here only by hash. *Census note:*
   one hit, an `npm exec` process, matched only through environment text that `npm exec` leaves in its process title
   (the macOS cryptex path `…/codex.system/…`), not through its arguments. A window launched by `launchd` has no such
   process, so this cannot refuse a window; it can only over-refuse a desk arm while such a process is alive.
   *The census matcher changed after these records.* Both were written at `fe28e5a0c`. After it, commit `84661ddb3`
   changed how the census decides a process that runs a JavaScript program (§4.5). The render uses a stand-in
   census, so it does not exercise the matcher. The dry arm's refusal holds under the merged rule, because one agent
   is enough to refuse and the seat's own `claude` process is one either way: if it ran as Claude Code's own program
   file, it is decided by that file's name and location, a rule the commit did not touch; if it ran as a JavaScript
   program under `node`, its arguments hold the directory name `claude-code`, which the merged rule counts. The
   command line `node /opt/homebrew/bin/codex exec`, which revision 9 recorded among the dry arm's agents (§13), is
   an agent under the merged rule as well (computed by this author with the code at `9b0c680ed`, §4.5). The dry arm
   itself was not run again at `9b0c680ed`; §14 Q15 asks whether it is repeated at the final head.
7. Before the seal, one machinery smoke of the block-5 cooldown policy has passed (timing ruling item 2): a
   dummy-label stage of three small members run under `quiet_mac_p2_b5.json` and harvested through the cooldown
   join, `campaign_cooldown_evidence` (the check that pairs each member with its cooldown record in the campaign
   manifest and verifies that record's raw trace). The ruling also named `scripts/check_window_provenance.py` (G3),
   but G3 does not apply to a floor pack: the harvest runs it only on a pack with an analysis manifest
   (`analysis_manifest_v3.json`, GAMMA's), and records `g3.not_applicable` (DISCLOSE) on ALPHA and BETA. So the smoke,
   an ALPHA stage, is judged on the cooldown join alone. It passes when every cooldown record verifies as `recovered`
   (or `first_run_exempt`) with a one-reading trace, and the join reports zero `campaign_cooldown_evidence_missing`
   and zero `cooldown_evidence_unverified`. It takes about 15 minutes. No thermal qualification run is required: the
   first BETA window measures 8B-after-8B carryover through its reference members (§0.12) and the
   battery-temperature diagnostic (§0.6).
   **`B5-COOLDOWN-SMOKE-RECORD`** (filled in revision 6; the record as written by the smoke's lead, with the four
   SHA-256s re-computed by this author from the files under
   `/Users/edr/night-archive/gate-prune/cooldown-smoke/run-4/`, where `night/` is `custody/night/` and
   `harvest.json` is `archive/harvest.json`): "Cooldown smoke run-4,
   2026-10-06 23:27–23:48 PDT, at head 3a9327e51c9d51ce5181f6db44983b6cf83a91df (integrate/2026-10-06-gate-prune-4;
   H_claim clone 3e2f67fb6). Plan REH-cdsmoke-alpha-20261007T0627Z, ALPHA pack, one stage of three small members
   (01_phase_decode_absolute r01–r03) under quiet_mac_p2_b5.json; other stages zero members. Rehearsal overrides:
   agent census (R1) and display (R4) only, arm dwell 60/120 s. Lineage published and verified without workaround;
   driver GO. Cooldown join (campaign_cooldown_evidence): r01 first_run_exempt, r02 recovered (waited 8.19 s), r03
   recovered (waited 8.20 s), all verified with one-reading traces; campaign_cooldown_evidence_missing 0,
   cooldown_evidence_unverified 0. PASS. Member r02 was refused by the real idle admission (CPU busy p95 0.634 and
   0.732 against 0.5; Spotlight indexing, corespotlightd 0.54 CPU-s/s), a physics refusal, not a cooldown fault.
   Evidence: night-archive/gate-prune/cooldown-smoke/run-4/cooldown-join-check.json sha256
   57ec28128a2915b2a0b73fb6a85d0f4f0fd4b9650791d6954fe5950d40a2be90; night/lineage.json sha256
   c35cb60a94333050cb2a0e8aa3a31aef79e09789f5bec15705947f7f5254faf4; night/result.json sha256
   b0863e43a4d0b90dc91fa7d92e5ef0943462c6f6227bf6ab483b67cd50a46619; harvest.json sha256
   b5015904eceddc640f28c4b088d77f8af455918d6bc882a11f4cba228a4482fa." (In that record, R1 and R4 are the
   rehearsal's own labels for the two checks it overrode, the agent census and the display check; they are neither
   review findings nor the fix route R3 of §0.1.) The frozen head `a434e363d` carries the same
   driver code: between `3a9327e51` and `a434e363d` (`git diff --stat`, run by this author) only
   `joulewise/b5/harvest.py`, `joulewise/calibration_ledger.py`, `joulewise/controller.py` (the guard-collector and
   pack-root triage of §6.10), `joulewise/flags/catalog.py`, `joulewise/flags/core.py` and
   `configs/gates/hazard_refusals.json` changed under `joulewise/`, `scripts/` and `configs/`; the driver, the chain,
   the runner `scripts/run_campaign.py` and the cooldown join are byte-identical. From `a434e363d` to the int5 head
   `d3c107f2f` the driver, the chain and the runner did change (revision 7 list), but no added or removed line in
   `scripts/run_campaign.py`, `joulewise/controller.py` or `joulewise/b5/harvest.py` mentions the cooldown, and
   `configs/campaign_policies/` is unchanged (`git diff`, searched by this author), so the smoke's result carries
   over to that head. The same search from `d3c107f2f` to `43ac12d0c` finds no added or removed line mentioning the
   cooldown in those three files and no change under `configs/campaign_policies/`, so it carries over to `43ac12d0c`
   as well, and the same search from `43ac12d0c` to `fe28e5a0c` again finds none (the runner's only change there is
   the `strict_invalid` loss of §0.12), so it carries over to `fe28e5a0c`. From `fe28e5a0c` to the int5 head
   `9b0c680ed` (searched by this author for revision 10) the runner and the controller did not change, the harvest
   changed in one explanatory comment that does not mention the cooldown, and `configs/campaign_policies/` did not
   change, so it carries over to `9b0c680ed`. From `9b0c680ed` to the int5 head `9395cecfb` (searched by this
   author for revision 12) the runner and the controller did not change, the harvest changed only in its
   comparison of a window's code with the seal (§0.18), with no added or removed line that mentions the cooldown,
   and `configs/campaign_policies/` did not change, so it carries over to `9395cecfb`. The search is repeated at
   H_claim if H_claim changes one of those three files or that directory after `9395cecfb`.
8. The P3 sync points of §13 are each confirmed against the merged code, and this text is corrected where the code
   chose differently (a draft edit, before the seal). **`P3-SYNC-RECORD`** (filled in revision 6): confirmed against
   the frozen head `a434e363d`; the result of each sync point is the table in §13, and the catalog comparison there.
   Revision 7 repeats the sync for the code merged after `a434e363d` (the audit fixes and the NEG-8 lane), against
   the int5 head `d3c107f2f`, in a second table in §13 (`B5-REV7-SYNC`), and revision 8 repeats it for the code
   merged after `d3c107f2f`, against `43ac12d0c`, in a third (`B5-REV8-SYNC`), and revision 9 for the code merged
   after `43ac12d0c`, against `fe28e5a0c`, in a fourth (`B5-REV9-SYNC`), and revision 10 for what the integration
   changed after `fe28e5a0c`, against the int5 head `9b0c680ed`, in a fifth (`B5-REV10-SYNC`), which also confirms
   the interpreter rule that the fourth table listed as still to be checked. Revision 12 repeats it for what the
   integration changed after `9b0c680ed`, against the int5 head `9395cecfb`: the seal-landing lane changed
   `joulewise/b5/harvest.py` and `joulewise/flags/collect.py` (the head comparison) and three test files, and
   nothing else (`git diff --stat 9b0c680ed 9395cecfb`, run by this author). The text for that code is §0.18,
   items 3 to 5 above, §4.1 step 4 and §11, written from the lane's own list of facts
   (`/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/REGISTRATION_FACTS.md`); for §0.18, §4.1 and the
   items above, the writer read each fact in the code at `9395cecfb` before writing the sentence. Together the
   records hold for H_claim only if H_claim's files under `joulewise/`, `scripts/` and `configs/` are those of
   `9395cecfb`, apart from the four documents of item 3 and the refusal allowlist (item 1, last paragraph); any
   other difference is synced again.

**Before ALPHA-1's harvest:** the harvest lane that the seal gate's first stage required has landed in a desk
checkout (§11 item 4: the reference losses of §0.12, the narrowed candidate list of §6.2, the record of the
harvest's own commit, and the five details of the head comparison listed in §0.18), with an independent executing
review and a cold Fable pass, as for any code on the path to a claim; and the harvest program (lane L5) as that
lane leaves it is pinned by an addendum to the seal record that names its files, their SHA-256s and the desk
checkout's commit (§11 item 4). ALPHA-1's harvest does not run until that addendum exists. Three requirements that
revision 5 listed here are met at the frozen head
`a434e363d`:

- the harvest emits `member.whole_window_member_failure` for every member the whole-window verdict fails for one of
  the reasons of §6.3 (`harvest.whole_window_member_failures`), and `whole_window.member_failures_unreadable` when a
  verdict that did not pass cannot name its failed members (§6.5);
- the desk verdict's timeout is sized to the window: max(1,800 s, 90 s per claim-root bundle), with a 60 s
  heartbeat (`harvest.desk_verdict_timeout_s`; an ALPHA verdict needs about 3,700 s, and the old fixed 1,800 s would
  have lost it as `whole_window.verdict_absent`);
- the verdict writer never reads a stale ledger pin. *Forcing problem* (real-model rehearsal): the writer reads the
  calibration ledger through the committed pin, and the window's own post calibration has moved the ledger past the
  pin the window armed at, so a verdict written before the pin advance fails its bracket with
  `calibration_ledger_head_mismatch`, and its row stays in the append-only campaign log. *Mechanism:* the desk order
  is chain exit, then the pin advance, then the harvest (§4.6 item 6). Before starting the writer the harvest checks
  that the committed pin is this bracket session's terminal entry (`harvest._desk_pin_problem`); if it is not, it
  writes no verdict and records why (`whole_window.producer_failed`, `step` `head_pin`, with a reason such as
  `pin_behind`). The window then lacks a verdict (`whole_window.verdict_absent`, a harvest problem under §7.2); the
  cure is the advance and a re-harvest from the same bytes.

**Before GAMMA-1 arms:** GAMMA's three interior reference stages launch three distinct `run_id`s (lane L10, branch
`lane/2026-10-06-l10-gamma-refs`, commits `c6309e1a` and `7bfd7c2c`). Before L10 all three launched the same
one-member input, `window_references_v5/midpoint` (run id `neg8-window-midpoint`), and `run_campaign.py` skips a
`run_id` whose complete bundle already exists, so the second and third were never measured and the harvest removed
the window (`roster.duplicate_run_id`). Giving all three the midpoint role would instead fail the NEG-8 screen,
which accepts one midpoint (§0.12). So the arm boundary (stage `gamma-reference-arm-boundary`, after science member
40) keeps the shared midpoint reference and is GAMMA's one NEG-8 midpoint, and the two arm-midpoint stages run the
diagnostic interior references under `configs/campaigns/gamma_interior_references_v5/` (§0.12). GAMMA's plan tree
pins those two manifests and configs by SHA-256 as external inputs, as it pins the window references, and its
generator refuses if their bytes differ from the shared midpoint's in anything other than `run_id`. No science
config, calibration plan, analysis manifest or root order manifest changed; GAMMA still runs 80 science and 21
auxiliary members. Besides GAMMA's pack and the two new reference directories, the change touches the shared
contrast-pack generator (`configs/campaigns/d117_contrast_v5/generate_configs.py`, 173 changed lines, the same
change as in the pack's own copy), the pin registry (`configs/pins/registry.json`, the list of every digest
written into the tests and configs: four new entries for the four new reference files, and the renumbering that
follows), the retired block-4 writer (`scripts/write_v5_qualification_plan.py`, which no block-5 window runs) and
tests (`git show --stat` of the two commits, read by this author). L10 is merged in
the frozen head `a434e363d` (commit `7bfd7c2cf` is its ancestor), with the sizing output and identity pins re-derived
there (§4.6 item 3, §5.5), so its bytes are sealed directly with H_claim and no erratum is needed. Under §7.5 it
supersedes no completed ALPHA or BETA window, because neither executes GAMMA's files.

**Before the release event:** the analysis code (lane L9) is written blind, pinned by an addendum, and the blind dry
run of analysis plan §3.2 has completed.

**Deleted from revision 2, with the reason:**

- the block-4 verdicts and the L10-A ratification: block 4 does not run; ALPHA-1 carries its structural checks as
  disclosed diagnostics (§3);
- Q110 (the age of the readiness evidence): the readiness receipt no longer exists;
- A6 at H_claim (a launch-time recheck that the launched bytes are the reviewed bytes): replaced by the
  executed-file inventory and the model-identity check, both replayed at harvest (§6.5);
- V5-TRANSACTION-GO-01, the `CAMPAIGN_TRANSACTION` authorization records and the step-6 confirmation record: the
  receipt route they authorized (`TRANSACTION_PACK`: ARM, GO, `scripts/launch_window.py`) is retired for block 5
  (§11 item 3).

## 3. Block 4 folded into block 5

**G10, the clock positive control, at ALPHA-1's tail (agent-run).** Ed, 2026-10-05: "make it all agent run, don't
let old decisions stop progress on the paper. remember those are vestiges of weaker models, scaffolding i had to
build to corral weaker models working on this".

- *What it shows.* That the clock hazard's arm check can see a clock step at all. Without it, a clock module that
  always passed would look the same as a quiet clock.
- *When.* The driver runs `scripts/g10_clock_step_control.py` after the chain's process group is proven gone and
  before its terminal record, so no capture can be touched; the monitor and the meter stay supervised meanwhile
  (§5.4). Whether an attempt runs G10 is the boolean `g10` of its window plan. The plan writer copies that value
  from the plan input (the desk file a window plan is written from) and checks only that it is a boolean
  (`joulewise/b5/plan.py`); no code decides it. The rule is the lead's, applied when it prepares the plan input:
  `g10` is true until a G10 record exists in this measurement block, and false after it. In practice this is
  ALPHA-1; if ALPHA-1 never starts its chain, or its chain is stopped by the agent census, the next attempt carries
  it.
- *Steps.* (1) Read f₀ and the anchor; check read-only that no capture process is alive (if one is, ON is skipped and
  the result is UNMEASURED). (2) `sudo -n systemsetup -setusingnetworktime on`; its output is recorded only.
  (3) Poll the anchor at 1 Hz for up to 300 s until the residual moves more than 5 ms. (4) Evaluate the clock
  module's own arm check (§4.2) on the before/after pair; a REFUSE whose measured residual exceeds 1 ms is
  **DISCHARGED**. (5) Keep network time ON while reading f each minute; switch OFF at the first read, at least 60 s
  after ON, at which the next arm's frequency gate (§4.2: 3.7 ms + (|f| + 0.25 ppm) × T_stream_max ≤ 5 ms) would pass,
  or 15 min after ON. (Revision 4's |f| ≤ 3.0 ppm target sat below this machine's own f of about −3.17 ppm, so it
  would always have run the full 15 min; each read still records whether |f| ≤ 3.0 ppm. PLAN2 item S7,
  `scripts/g10_clock_step_control.py` at `a434e363d`.) OFF always runs, including on an exception or a SIGTERM or
  SIGHUP. (6) Write `night/g10.json` write-once.
- *Why it should discharge.* With network time OFF the wall clock's offset from a time server was about 1.15 s on
  2026-10-05 and grows about 0.3–0.5 s per day (gate-prune plan §4), so turning network time ON one night later
  corrects roughly 1.3–1.8 s, far above 5 ms.
- *Effect.* G10's result is a disclosed diagnostic (`g10.discharged`, `g10.not_discharged`, `g10.unmeasured`,
  `g10.interrupted`, `g10.error`). It touches no ALPHA-1 number, because each member carries its own anchor bound. A
  result other than DISCHARGED goes to one consult before BETA arms.
- *Frequency redraw.* G10 leaves a new f. If the next arm's frequency gate refuses (§4.2), the desk redraws f before
  re-arming: network time ON; read f once a minute; OFF at the first read, at least 60 s after ON, at which the
  frequency gate passes, or after 15 min; re-read f 10 min later; up to three cycles, then a consult. This loop reads
  only the frequency word, never an energy.

**a1 and a2 (the arm-then-abort controls) retire.** Their two physical questions are answered without a window:
does a refusal before launch leave nothing launched and nothing changed (the driver's tests inject each hazard
REFUSE and compare the ledger, `~/Library/LaunchAgents`, the custody roots and the network-time state before and
after; the desk dry arm of §2 item 6), and does arming run end to end on native output (every real arm writes
`hazards/arm.json`). The watchdog's stand-down is recorded live at ALPHA-1's arm.

**Stand-down leads.** *Forcing problem:* the agent census at t0 (§4.5) refuses the window if any agent session is
alive, so every session must be gone by t0; but every second of agent-free idle before t0 is time the machine does
nothing, and the arm's own dwell measures contention after t0 anyway. The supervising watchdog (a scheduled job,
`scripts/magistrate_watchdog.py` at `a434e363d`, P2-WD, that starts and stops the agent sessions on this machine
around each window) therefore stops launching sessions and asks every agent
session to exit at t0 − 180 s, sends SIGTERM to any that remain at t0 − 90 s, and SIGKILL at t0 − 60 s (revision 4:
t0 − 8, −6 and −5 min, about 450 s of agent-free idle before t0; now about 150 s). *Why these numbers:* real
sessions took 20–31 s to exit after the request. That figure is the code's: the comment above `PLAN_LEAD_S` in
`scripts/magistrate_watchdog.py` gives it and cites the session exits recorded at the stand-downs before three
earlier windows, which it labels c1, c2 and d117. This author did not re-derive it. So a request at t0 − 180 s
leaves 149–160 s, about 150 s, before t0 (by the same subtraction revision 4's 480 s left about 450 s), and the
watchdog's 10 s poll gives 9 polls between request and SIGTERM and 3 between SIGTERM and SIGKILL. A session that
survives all three is refused by the t0 census, which stays the backstop.

**s1 (the one-quad qualification window) becomes ALPHA-1.** ALPHA-1 contains everything s1 had: pre calibration, the
NEG-8 corpus and bound, references, null quads and post calibration. s1's structural checks run at every block-5
harvest, ALPHA-1's first, as disclosed diagnostics. The harvest writes four `diagnostic.s1_structural` flags
(`harvest.diagnostics`), one for each check:

- `l10a_prefix`: the number of bundles, how many of them passed strict validation (§0.12) and how many re-reduced
  to a summary identical to the stored one;
- `precheck_counts`: for each cell of the pack, the p42 cells included, the number of members whose precheck for
  that cell's phase (§0.4) passed with no reason recorded and the number whose did not. This one flag is
  RESTRICTED, because a precheck can turn on an energy test;
- `stream_sizes`: the shortest and the longest sampler stream, in bytes, each with its run id;
- `time_outside_members`: the gaps between consecutive member spans (a member's span is the time it occupies,
  from the start of its idle baseline to the end of its last reading): how many, their total and the longest.

Revisions up to 10 listed a fifth check here, "a deliberately incomplete finalization": the block-4 harvest asks
the desk provenance checker (G3, `scripts/check_window_provenance.py --expect-finalize-refusal`) to finalize an
analysis whose member list does not cover the window, and expects it to refuse. The block-5 harvest does not run
that step and records no finalization of any kind. The step exists only in the block-4 harvest script
(`scripts/harvest_v5_g2b_window.py`), which no block-5 window runs.

## 4. The arm: physical hazards, measured directly

### 4.1 Order

Everything below runs inside the launchd job after t0, so no person or agent session is present.

1. **Agent census** (§4.5).
2. **Instant reads:** battery, thermal, disk, and the clock's frequency gate and first anchor read; then the OS
   build and machine model against the acceptance's **judged epochs**, the identities of machine and software
   under which the calibration acceptance may judge a window (§4.7).
3. **Network time OFF, as an action** (§4.4).
4. **Record-only collectors:** one command, `scripts/collect_window_flags.py --stage arm`, which is killed as a
   whole after 120 s. It runs five collectors, each in its own subprocess with its own time budget: pack identity
   (the pack's files against the digests its plan tree pins; 15 s), checkout identity (the measurement checkout
   has no edited tracked file and no untracked file under `joulewise/`, `scripts/` or the pack, and no window input
   differs between the commit the window plan names as its `measurement_head` and the checkout's HEAD; at a real
   arm those two are the same commit, so this last comparison lists nothing there, and the comparison with H_claim
   is the harvest's, §0.18; 10 s), the executed-file inventory (§0.18; 15 s), the model-identity
   check (§4.6 item 3; 55 s) and calibration-ledger readiness (the read-only check of §4.6 item 6; 15 s; it runs
   when the pack holds a `calibration_plan.json`, which all three packs do). Their findings are flags (§6); they
   never change the arm decision.
5. **Instrument cadence probe:** about 40 s.
6. **Dwell:** a wait of 180 to 2,700 s on the idle machine. It ends at the first moment 180 s in a row have passed
   with no competing process, and refuses at 2,700 s (§4.2, Contention). Through it the clock is sampled once a
   second, to check its **linearity**: that the residual of §0.14 (the anchor's movement minus f × elapsed time)
   stays within 1 ms of its value at the dwell's start, as it does when the clock runs at one steady rate with no
   step (§4.2, Clock, condition ii, with conditions iv and v on the same samples).
7. **Final reads** of battery, thermal and the frequency word, and the agent census again; then GO; then the monitor
   starts; then the chain launches.

The chain therefore starts about 4–46 min after t0: about 41 s of reads, collectors and cadence probe, then a dwell
of 180 s at the least and 2,700 s at the most, so 221 s to 2,741 s (revision 4 gave 11–47 min, with a 600 s
minimum dwell; revisions 5 to 10 kept its 47, which this sum does not reach, and a comment in
`joulewise/hazards/arm.py` still says about 47 min). A refusal at any
step ends the attempt as NULL (§7.1) with nothing launched. A refusal is a measured REFUSE, an UNMEASURED instrument,
an agent census that lists an agent process or cannot be read, or an OS build and machine model that no acceptance
judged. An UNMEASURED
clock, battery, thermal, contention or disk verdict is not a refusal: it is recorded under `unmeasured` in
`arm.json`, with its phase and reasons, and as `<module>.arm_unmeasured` (DISCLOSE), and the arm continues (§0.15).
A contention dwell in which every snapshot failed therefore runs to its 2,700 s cap and ends with
`contention.arm_unmeasured`, while a dwell that measured a contender still refuses. The arm writes
`<custody>/hazards/arm.json` write-once with every measurement, verdict and raw-byte digest.

### 4.2 The six hazards

**Clock.** *Forcing problem:* a clock step inside a member's stream breaks the anchor fit, and a large |f| makes
the longest streams exceed the 5 ms bound (§0.14).
- *Arm: five conditions, judged in two places* (`joulewise/hazards/clock.py`, `joulewise/hazards/arm.py`).
  (i) The **frequency gate** 3.7 ms + (|f| + 0.25 ppm) × 335 s ≤ 5 ms, where 3.7 ms is
  block 3's largest half-width 3.6 ms plus a 0.1 ms placement margin and 0.25 ppm allows for the rate over a stream
  differing from the stored word (ruling 76 B.2, `docs/process_traces/2026-10-04-desk-day-v5/76-r1-fold-ruling.md`);
  this holds for |f| ≤ 3.6306 ppm. *Worked example:* at
  f = −3.17 ppm the bound is 3.7 + 3.42 × 0.335 = 4.846 ms, PASS; at |f| = 3.7 ppm it is 3.7 + 3.95 × 0.335 =
  5.023 ms, REFUSE. (ii) *Linearity:* over the dwell, sampled at 1 Hz, the residual stays within ±1 ms of its start
  value. (iii) Each anchor's read skew, the time between the two RAW reads that enclose its REALTIME read (built
  under "In window" below), is at most 1 ms.
  (iv) f is identical at every sample from the dwell's start to GO; any change means something adjusted the clock.
  (v) The **boot session** identifier (`kern.bootsessionuuid`, a value the kernel sets anew at every boot) is the
  same at the dwell's start and at GO: after a reboot the anchors of before and after cannot be compared.
  - *At the instant read* (§4.1 step 2) the arm reads the boot session identifier, one anchor and f, and judges
    (i) and (iii). The anchor is read up to five times; the first read whose skew is at most 1 ms is kept. If all
    five exceed it, the last is kept and judged, and it refuses. This is the only place where (iii) can refuse.
  - *Over the dwell and at GO* the arm judges one series: a sample at the dwell's start, one each second through
    the dwell, one at its end and one at GO, about 180 to 2,700 samples in all. Each sample is an anchor (read up
    to five times against the same 1 ms) and f. The boot session identifier is read at the dwell's start and
    again at GO. On the series the arm judges (ii), (iv) and (v), and (i) again on the first sample's f.
  - *A series with a hole is not judged.* If one sample of the series has no anchor (the skew of all five of its
    reads exceeded 1 ms), or any read in it failed, or the boot session identifier could not be read at either end,
    the series is UNMEASURED as a whole. The arm then records `clock.arm_unmeasured` (DISCLOSE, §0.15) and goes
    on, and (ii), (iv), (v) and the repeat of (i) are not judged at this arm. So a slow anchor read in the dwell
    never refuses; it removes the dwell's clock verdict. *Why this is accepted for block 5* (orchestrator ruling
    of 2026-10-07, on item C5 of that day's comparison of this text with the code): no number rests on the dwell's
    verdict. Each member carries its own anchor bound (§0.14), and the monitor's 1 Hz journal is judged against
    every member span at the harvest (`clock.step_overlap`, §6.4). The dwell only guards against starting a
    window on a clock that is already disturbed. Judging the series on the samples that did read is a code change
    listed for after block 5.
- *In window:* the monitor journals the anchor at 1 Hz and f every 5 s. A residual move of more than 1 ms between
  consecutive samples is a `clock.step`; a change of f is `clock.frequency_changed`. Each anchor sample is three reads
  in a row, RAW, REALTIME, RAW (CLOCK_MONOTONIC_RAW, then CLOCK_REALTIME, then CLOCK_MONOTONIC_RAW again). The anchor
  is the REALTIME read minus the midpoint of the two RAW reads (`joulewise/clock_reference.py` `sample_anchor`), and
  the sample's **read skew** is the time between the two RAW reads. *Forcing problem:* in mock
  rehearsal round 3 a `ps` probe pre-empted the monitor between those reads, giving skews of 3.9–8.3 ms, and the
  residual computed from such a sample moved by more than 1 ms with no clock step, so the harvest recorded false
  `clock.step` and `clock.step_overlap` (finding R3-1, that round's first finding; not the fix route R3 of §0.1).
  *Mechanism* (lane P3-HAZ, at `a434e363d`):
  **`P3-CLOCK-SKEW-BOUND`** (filled in revision 6) is a quarter of the step limit, 1 ms ÷ 4 = 250 µs
  (`joulewise/hazards/clock.py` `window_skew_max_ns`, `SKEW_DIVISOR_OF_STEP` = 4). The monitor takes the step limit
  from the window plan (`hazard_window.harvest_thresholds.clock_step_ns`, else `thresholds.clock.step_ns`), as the
  harvest does, so the two bounds stay equal if the limit is ever re-registered; a missing or unusable value keeps
  the module's 250 µs and never stops the monitor (cold pass N5, `joulewise/hazards/monitor.py` `build_config`). The
  monitor reads the anchor up to
  five times (`ANCHOR_TRIES` = 5) and keeps the first read whose skew is at most 250 µs; if all five exceed it, the
  sample has no anchor, its rejected reads are journaled, and the member join records `clock.unmeasured` (DISCLOSE,
  `observed.rule` `read_skew`). The harvest applies the same 250 µs bound to every journaled sample
  (`harvest._clock_point`): a sample above it is skipped, and the next good sample is compared with the last good one,
  so a step is never computed from a skewed sample. A real step moves every later sample, so a skipped sample cannot
  hide one. *Why a quarter:* the REALTIME read lies somewhere between the two RAW reads and the anchor uses their
  midpoint, so a sample with read skew s places the anchor within s/2 of its true value. At the 250 µs bound each
  sample is off by at most 125 µs, so two consecutive samples off in opposite directions differ by at most 250 µs,
  a quarter of the 1 ms that defines a step, and a residual move of more than 1 ms holds at least 750 µs of real
  clock movement. (The arm re-reads its own anchors the same way, up to five times, against its own bound
  `skew_max_ns` = 1 ms; what follows when all five exceed it is in the arm item above.)
- *Replaces:* the 8 ppm sizing convention of revision 2 and the network-time OFF receipt's wording check. There is
  no resync at the arm: the wall clock's absolute offset enters no energy, because the anchor fit and every phase
  edge use relative times.

**Battery** (directive #421; ruling of 2026-10-06, §9.2). *Forcing problem:* while the battery charges, the
battery heats and the machine draws more from the adapter than the work needs; with the adapter disconnected the
machine runs on battery under a different power policy. Either way the machine is not in the power state every
registered number assumes. A capture taken while charging was registered as confounded (`battery_float_confounded`;
decision log, amendment A-R5b of 2026-09-25). The rule is decided from instrument state alone, never from an
outcome.

- *Two sources.*
  - **State, from the registry.** `ioreg -r -c AppleSmartBattery` prints the OS's record of the battery; raw bytes
    are kept. It gives ExternalConnected (an adapter is supplying power), IsCharging, InstantAmperage (signed),
    Amperage, UpdateTime, Voltage and the `PowerTelemetryData` **accumulators**: running sums the registry keeps of
    the battery's charging power and of its discharging power, each with a count of the samples summed, so that
    the change of a sum between two publications divided by the change of its count is the mean power of that
    sign over the interval (`joulewise/hazards/battery.py` `accumulator_interval`; used in §6.4). The registry
    **publishes** a new set of values about once every 60 s (and on some events); between publications every
    value is frozen.
  - **Current, from the SMC.** The SMC (System Management Controller) is the chip that manages the Mac's power and
    exposes its sensor readings as four-letter **keys**, read in process without privileges
    (`joulewise/hazards/smc.py`). **B0AC** is the battery current in mA, signed, negative when the battery
    discharges into the machine; **B0AV** is the battery voltage in mV. The SMC refreshes them about once a second
    (largest gap 1.01 s over 580 s on 2026-10-06). Three more keys are recorded, not judged: PDTR (the DC input power
    from the adapter, W), PSTR (the system's total power, W) and PPBR (the SMC's own battery-power figure).
  - *Why the current comes from the SMC.* The registry's current is a snapshot, not an average. On 2026-10-06, at
    each of nine registry publications InstantAmperage equalled Amperage, and both equalled the last B0AC read before
    the publication (at one, −793 mA against a B0AC read of −727 mA taken 0.7 s earlier, within one SMC refresh), not
    the mean over the preceding interval. Between publications the registry misses discharge entirely: over the interval ending at
    UpdateTime 1791324894, B0AC read as low as −3,580 mA (mean −351 mA), and the registry published 0. A probe
    earlier that day (`/Users/edr/night-archive/wallmeter-probe/xc1/`, not a claim window) saw one burst of
    −865 mA lasting 0.9 s while Qwen3-8B was being loaded, 19 s before its first request and outside every
    request, and currents down to −216 mA during the three 8B decodes; all 182 registry reads of that probe gave 0
    (this author joined the probe's `smc.jsonl` to its `mlx.jsonl`; §9.2 item 3 says the same of the burst). So
    the registry now supplies only the state, and the SMC the current (`joulewise/hazards/battery.py`, and the
    harvest's own copy of the member rule, `harvest.battery_join`, at `a434e363d`).
  - *Validation of B0AC* (`/Users/edr/night-archive/wallmeter-probe/verify/b0ac_validation.md`, 2026-10-06 22:12Z).
    25 s idle, then 170 s of load (a 16-process CPU burner plus four Qwen3-8B generations; DC input peaked at
    135.7 W on the 140 W adapter, so the battery had to help), then 200 s of recovery. *Sign:* B0AC was negative
    exactly when PSTR exceeded PDTR, that is, when the machine drew more than the adapter supplied: at 126 of 536
    distinct SMC publications, all during the load; it read exactly 0 throughout the idle and the recovery.
    *Magnitude:* over the load, ∫ −B0AC × B0AV dt = 606.9 J against ∫ (PSTR − PDTR) dt = 595.4 J, 1.9% apart; on 20 s
    bins the slope of PSTR − PDTR on −B0AC × B0AV is 1.027 (r = 0.954). Single 1 s reads disagree (r = 0.32),
    because the SMC refreshes its keys out of phase with one another; time averages agree. *Charging direction:* not
    observed (the battery sat at its 80% charge limit). Positive B0AC is read as charging by the registry's
    convention: the archived charging capture shows InstantAmperage +1,716 mA with IsCharging Yes, and the registry
    current is B0AC's snapshot.
- *Arm:* ExternalConnected Yes; IsCharging No; |B0AC| ≤ 200 mA (|InstantAmperage| ≤ 200 mA when B0AC cannot be read,
  recorded as `battery.smc_unavailable`); the registry reading no older than 180 s. The first three together are
  the measured form of battery float (§0.1). The arm runs on an idle machine, so a battery current above 200 mA in
  either direction means the adapter is not supplying the machine, a real hazard; this refusal is unchanged by the
  ruling (§9.2).
- *In window:* the registry polled every 5 s, its raw bytes stored at every publication; the SMC read every 1 s.
  The member rule is §6.4: charging, loss of AC power and missing evidence remove the member; discharge with the
  adapter connected (**assist**) is disclosed.

**Thermal.** *Forcing problem:* under thermal pressure the processor throttles, which changes both power and
duration.
- *Measurement:* the OS thermal-pressure level, `notifyutil -g com.apple.system.thermalpressurelevel` (unprivileged,
  0 = nominal). `pmset -g therm` is recorded as a diagnostic only: on this Mac it prints only "No thermal warning
  level has been recorded", so a check built on it tests nothing.
- *Arm:* level 0. *In window:* level every 5 s; inside each member, powermetrics' own per-record thermal pressure.

**Contention.** *Forcing problem:* another process's CPU work during a request adds energy that would be attributed
to the model; idle admission screens only the idle baseline before the request. On 2026-09-22 a background indexer
(`fseventsd`) contaminated captures this way.
- *Measurement:* CPU-seconds per second of each process outside the measurement tree (the driver, the chain's
  process group, `sudo` and `powermetrics`, `caffeinate`, the monitor), computed from the difference of cumulative
  CPU time between two `ps` snapshots, not from the decaying `%CPU`. *Worked example:* a process whose cumulative
  CPU time goes from 12.40 s to 13.10 s across a 10 s interval used 0.07 CPU-s/s, above the 0.05 limit (5% of one
  core).
- *Arm (the dwell):* 30 s intervals; an interval is clean when no outside process exceeds 0.05 CPU-s/s. GO needs
  180 s (six intervals) of consecutive clean intervals; none within 2,700 s refuses. *Why 180 s, not revision 4's
  600 s* (PLAN2 finding t2-08; `joulewise/hazards/contention.py` `HAZARD_ARM_CLEAN_S` at `a434e363d`): no number
  depends on the dwell. Each member's idle admission screens its own baseline, the monitor checks contention every
  10 s through the window, and a persistent contender still fails the 0.05 limit in every interval and is refused at
  the cap. The dwell also carries the clock's linearity check (condition ii above), and 180 s still sees a step or
  a **slew**, which is the clock being run fast or slow at a set rate for a set time in place of a step: a slew of
  500 ppm over 180 s moves the clock 90 ms, ninety times the 1 ms limit. Under revision 4 the dwell took 633–1,477 s;
  the change saves at least 420 s per window. (The legacy prewindow dwell, `prewindow.MIN_CLEAN_DWELL_S`, keeps its
  600 s; only the hazard arm changed.)
- *`kernel_task`.* An unprivileged `ps` never lists `kernel_task` (process id 0; checked 2026-10-05), so neither the
  dwell nor the window can judge it by name. Its work is inside the host's total busy time, which every interval
  journals (`host_busy_cpu_s_per_s`) and nothing judges: `aggregate_cpu_limit_s_per_s` is null (§4.3) until ALPHA-1's
  journal measures this Mac's idle total under a launchd job. (Revision 4 said the dwell included `kernel_task` and
  the window disclosed its share; neither could happen.)
- *In window:* every 10 s. The member rule is §6.4.

**Disk.** *Forcing problem:* a write failure mid-window loses bytes.
- *Measurement:* `statvfs` free bytes on the runs-root volume and each backup destination.
- *Arm:* on every volume, free ≥ planned bytes × the copies planned on that volume + 20 GiB. Planned bytes are
  182 MiB per member (block 3 measured) × (the window's members + the 7 spares its reference stages can add at most,
  §0.12; `joulewise/b5/plan.py`): 22.4 GiB for ALPHA and BETA (119 + 7 = 126 members), 19.2 GiB for GAMMA
  (101 + 7 = 108). The driver plans one copy in the claim runs root and one in each of the two backup destinations
  (§5.6); the bound runs root and the custody root need only the headroom (`joulewise/b5/driver.py`, disk targets).
  The harvest archive is an APFS clone (a copy that shares storage with its source until either is modified), so it
  adds no copy. Targets on one volume add their copies. The backup destinations are in iCloud Drive, whose local
  folder is on the same volume as the runs roots (one device number, read with `stat` on 2026-10-06). So three copies
  land on that volume: 3 × 22.39 + 20 = 87.2 GiB required for ALPHA and BETA, and 3 × 19.20 + 20 = 77.6 GiB for
  GAMMA, against 264 GiB free on 2026-10-05 (revision 6, before the spares: 83.5 and 73.9 GiB).
- *In window:* every 60 s; below 10 GiB the monitor journals `disk.low` and the driver stops the chain.

**Instrument.** *Forcing problem:* a sampler running slower than its cadence (as the launchd context did on
2026-09-19, at 244–250 ms per record) leaves phases without enough records.
- *Arm:* a 300-frame idle capture through the production adapter, inside the launchd job: exit 0, exactly 300
  frames within 55 s, median interval ≤ 150 ms, maximum ≤ 200 ms.
- *In window:* not polled; each member's own records are checked (§6.3), and the pre-calibration screen stops the
  chain before member 1 (§5.1).

### 4.3 Registered thresholds

The window plan copies this block verbatim into `hazard_window.thresholds`; the plan writer refuses a plan that
lacks a key a hazard module reads. The two **sized** keys (`disk.planned_bytes`, `clock.t_stream_max_s`) are replaced
by the window's own values (§5.5); the values shown are ALPHA's (`planned_bytes` = 126 × 182 MiB = 24,045,944,832
bytes, the window's 119 members plus its 7 spares, computed by this author; revision 6 showed 119 × 182 MiB).

```json
{
  "clock":      {"t_stream_max_s": 335, "h_ms": 3.7, "frequency_margin_ppm": 0.25, "limit_ms": 5.0,
                 "skew_max_ns": 1000000, "residual_max_ns": 1000000, "step_ns": 1000000},
  "battery":    {"limit_ma": 200, "max_update_age_s": 180, "max_unobserved_s": 120},
  "thermal":    {"max_level": 0, "max_gap_s": 15},
  "contention": {"cpu_limit_s_per_s": 0.05, "interval_s": 30, "clean_s": 180, "cap_s": 2700,
                 "window_interval_s": 10, "aggregate_cpu_limit_s_per_s": null},
  "disk":       {"planned_bytes": 24045944832, "headroom_bytes": 21474836480, "low_bytes": 10737418240},
  "instrument": {"frames": 300, "bound_s": 55.0, "median_ms_max": 150.0, "max_ms_max": 200.0}
}
```

`aggregate_cpu_limit_s_per_s: null` means the whole-machine CPU total is journaled at the dwell but not judged; only
the per-process limit decides.

`clean_s` is 180 in revision 5 (was 600). The hazard module's default is already 180 at `a434e363d`, but the arm
judges the value the window plan copied from this block (`joulewise/b5/driver.py` `_arm_thresholds`), and the plan
writer records any copied value that differs from a module default. So the change takes effect only in plans written
from this block after the seal: any window plan written earlier, and any plan-input file (the input from which the
plan writer copies this block) prepared earlier, carries 600 and is not used. Every plan is written after the seal
commit (§2 item 4), and the record that the plans were written so is the seal record's section
`FILL[B5-PLANS-REGENERATED]` (§13).

### 4.4 Network time

- At every arm the driver runs `sudo -n systemsetup -setusingnetworktime off` as an action, whatever the current
  state, because running it removes the hazard. Its return code and output are recorded only (`network_time.off_output`,
  disclosed); nothing reads its wording. Whether the clock is in fact undisturbed is measured by the clock hazard
  (§4.2: the dwell residual and the f-equality checks).
- There is no settle wait after OFF and no ON at the arm. Network time is turned ON only by G10 at ALPHA-1's tail
  and by the desk frequency redraw (§3). Revision 2's "no ON at any point" is withdrawn.

### 4.5 Agent census

Kept by doctrine ("never start or continue a [QUIET-MAC] measurement while an agent session is active";
[QUIET-MAC] marks work run on the dedicated, quiet measurement Mac). The census probe
is `/usr/bin/pgrep -a -lf '[c]odex|[c]laude'` (`joulewise/night_gate.py` `AGENT_CENSUS_ARGV`, and the same argv in
`joulewise/hazards/arm.py`): it lists every process whose command line contains `codex` or `claude` anywhere. (The
brackets stop a concurrent census's own `pgrep` command line from matching this one.) `-a` makes Darwin's `pgrep`
list the census's own ancestors too, which it otherwise leaves out.
*Forcing problem* (dry-records finding F1, 2026-10-07): without `-a`, an agent session that launched the arm was invisible to the census that should have refused it. With `-a`, a desk dry
arm launched from inside an agent session always refuses at the census (§2 item 6).

That list is a superset: it holds every process with either string anywhere in its command line, whether or not it
is an agent. Each process on it is a **listed process**, and one matcher (`joulewise/agent_identity.py`) decides each
listed process by what the kernel says it runs (the kernel is the operating system's core, which holds each
process's real program file and arguments). A listed process that the matcher counts as an agent is a **hit**.
For each listed process id the matcher reads two things from the kernel: the **executable**, the path of the program
file the process is running (`proc_pidpath` on macOS), and the **arguments**, the strings the process was started
with (`KERN_PROCARGS2`). The first argument is the **process name**, which a program may set to anything. Every
census that a block-5 window depends on calls this one matcher: the driver's census before the arm, again before the
launch and every 30 s in the window (`joulewise/night_gate.py` `agent_census`); the hazard arm's own census at its
start and at GO (`joulewise/hazards/arm.py` `agent_census`); and the watchdog's check that no agent is left before it
releases a finished window (§5.4). Two older census sites that block 5 never runs call it as well: the
quiet-admission sampler of the earlier night kinds (`joulewise/quiet_admission.py` `sample_interval`) and the retired
t0 evidence author (`joulewise/arm_readiness_evidence_t0.py`, §11 item 3). The matcher's rules:

- **Executable identity.** A listed process is an agent when the file name of its executable, or its process name,
  begins `claude` or `codex` (letter case is ignored; examples are `codex`, `codex-code-mode-host` and the Claude
  desktop app's `Claude`), or when its executable sits in a `claude/versions/<version>` or `codex/versions/<version>`
  install (the Claude Code native binary is `~/.local/share/claude/versions/<version>`, a file named only by its
  version number).
- **JavaScript runtimes.**
  *Forcing problem.* Some agents have no program file of their own. Claude Code installed from npm (the JavaScript
  package registry), and the launcher npm installs for Codex (a small JavaScript program that starts the Codex
  binary), are JavaScript packages. The process that runs one is a **JavaScript
  runtime**, a program that executes JavaScript (Node.js, Bun or Deno, whose executables are `node`, `bun` and
  `deno`), and the agent appears only among the runtime's arguments, as the path of the script it was told to run.
  Executable identity reads such a process as `node`, which is not an agent. Earlier versions of the matcher
  therefore tried to find *the script* among the arguments. That needs, for every **option** of every runtime (an
  argument beginning `-` that configures the runtime), the knowledge of whether the next argument is that option's
  value or the script. Two audits in a row found a launch that this knowledge got wrong, and each time a live agent
  read as no agent and the census came back clean:
  - Sol delta audit A4, at `43ac12d0c`: in `node --require /tmp/preload.cjs …/claude-code/cli.js` the matcher took
    `/tmp/preload.cjs`, the value of `--require` (a file the runtime loads before the script), for the script, and
    never looked at the Claude Code path after it.
  - Sol R1 (the first finding of the Sol re-verification, §9.1), at `fe28e5a0c`, after A4's fix (`ca25d9299`) had
    added a table of the options that take
    a value and a rule that an option beginning `--trace-` takes none: `--trace-require-module` does take one
    (Node.js v23.7.0 accepts `node --trace-require-module all …/@openai/codex/cli.js`), so the matcher took its
    value `all` for the script, and a running Codex process was not a hit.

  The second miss showed that the mechanism was wrong, not one table entry. Such tables are a copy of three
  runtimes' command-line grammars, which change with their releases, and every error in the copy hides an agent.

  *Rule* (orchestrator ruling of 2026-10-07; commit `2524637ae` of lane `lane/2026-10-07-census-interp`, merged into
  int5 by commit `84661ddb3`; `agent_identity.identify`). The matcher no longer looks for the script, and it never
  parses a runtime's options. A listed process whose executable's file name, or whose process name, begins `node`,
  `bun` or `deno` (so `node22` and `bun-1.1` count) is treated as a runtime, and then:
  1. It is an **agent** when any of its arguments, the process name included, names an agent. To test an argument,
     the matcher puts it in lower case and cuts it into pieces at every `/`, `\`, white space, quote, bracket and
     each of the characters `=`, `,`, `;`, `:` and `+`. A piece that begins `claude` or `codex` names an agent. It
     does not matter where the argument stands: it may be an option's value, the script, or anything after the
     script.
  2. Otherwise it is **undecided**, and an undecided process counts as a hit, when its command line says that it
     runs code which no argument names. That is the case when one of the arguments after the process name is `-`
     (the script is read from standard input, the process's input stream, so no file name appears), or is `-e`,
     `-p`, `-pe`, `--eval`, `--print` or `eval` (the code itself is written on the command line), or begins
     `--eval=` or `--print=`.
  3. Otherwise it is **not an agent**.

  Every other listed process (a shell, Python, a system tool) is decided by executable identity alone; its arguments
  are never read.

  *Worked example.* Each verdict below was computed by this author with the merged code at `9b0c680ed`
  (`agent_identity.identify`); the executable is `/opt/homebrew/bin/node` unless the row says otherwise.

  | Arguments | Pieces that decide | Verdict |
  |---|---|---|
  | `node --trace-require-module all /opt/homebrew/lib/node_modules/@openai/codex/bin/codex.js` (the form of Sol R1's launch) | `codex`, `codex.js` | agent |
  | `node --require /tmp/preload.cjs /Users/x/.npm/lib/node_modules/@anthropic-ai/claude-code/cli.js` (the form of A4's launch) | `claude-code` | agent |
  | `node /opt/homebrew/bin/codex exec` (the Codex launcher, an agent in the dry arm of §2 item 6) | `codex` | agent |
  | `npm exec @openai/codex@0.153.3 mcp-server` (one argument: `npm exec` rewrites the process name of its `node` process to this text) | `codex@0.153.3` | agent |
  | `node -e "require('@openai/codex')"` | `codex`, cut out at the `/` and the quote | agent |
  | `node -e "console.log(1)" /Users/x/.claude/notes.txt` | none begins `claude` or `codex` (`.claude` begins with a dot); `-e` is present | undecided, a hit |
  | `node somescript.js --path /Users/x/.claude/custody/attempt3/out` | none; no argument of rule 2 | not an agent |
  | `python3.13 -B /Users/x/.claude/custody/run.py` (executable `/opt/homebrew/bin/python3.13`) | arguments not read | not an agent |
  | `zsh /Users/x/.claude/custody/chain.zsh` (executable `/bin/zsh`) | arguments not read | not an agent |

  *In which direction the rule can err.* It can count a process that is no agent: a runtime with any argument
  holding a piece that begins `claude` or `codex` (`node /Users/x/claude-notes/build.js` is a hit), and a program
  that is not a JavaScript runtime but whose name begins with one of the three names (Ruby's `bundle` begins `bun`,
  so it is read by rules 1 to 3). The cost is an arm refused at the census, or a chain stopped in the window. A
  window is launched by `launchd` on a machine kept for the measurement, and the window's own processes are Python,
  shell and system tools, which the next rule ignores whatever they run, so no window process can be such a hit.

  It can also miss an agent, in four ways:
  - a runtime that names its script and whose arguments carry the agent's name only inside a longer piece
    (`my-codex-tool`, `.claude`). This follows from the test of rule 1, which asks for a piece that *begins* with an
    agent's name, so that a runtime that merely works under a directory such as `.claude` is not counted;
  - a runtime that names no agent and reads its program from standard input without the `-` argument
    (`node --require /Users/x/.claude/hook.cjs`, for example). Telling this from a launch that names its script
    would need the option parsing that the rule withdrew;
  - an agent run by an interpreter that is not one of the three runtimes and is not itself named for an agent (a
    Python program);
  - an agent whose command line holds neither `codex` nor `claude`, which the probe never lists.

  The census is the doctrine's check that no agent session is alive; it is not the measurement of what an agent
  would do to a number. That physical hazard, a process using the CPU while a member runs, is measured directly and
  by no name: the contention hazard judges every process outside the measurement tree against 5% of one core, at
  the arm's dwell and every 10 s in the window (§4.2), and a member whose request such a process overlapped is
  removed (`contention.request_overlap`, §6.4). §14 Q14 puts these limits to the seal gate.

  H_claim carries this rule (§2 item 1); §13 (`B5-REV10-SYNC`) records what was confirmed at the int5 head
  `9b0c680ed`, and the Fable delta cold pass 5 re-ran the matcher on 36 launch shapes at `9395cecfb` (§2 item 1).
- **The caller's own tree.** A process in the caller's own process tree (the driver or the arm and their descendants,
  or a process group led by one of them) is the window itself and is ignored, whatever it runs. The tree runs downward
  only: the caller's ancestors (the shell or agent session that launched it, `launchd`) are not in it and are decided
  by executable identity like any other listed process, so an agent that launched the window is a hit, while a shell
  that runs `chain.zsh` from a custody path containing "claude" is not. *Forcing problem* (Opus audit F3): the
  window's own `python`, `zsh` and `run_campaign` processes carry paths such as a custody root, and the earlier
  string-only census refused the window for a string.
- **Proof that a line is that process.** A line is decided only when the live process's arguments, joined as `pgrep`
  joins them, equal the listed text, which proves the line is that process and not a reused process id; a line that
  cannot be decided stays a hit. Ignored lines are recorded with their process id, executable and reason.

**T3 is not an agent.** Ed, 2026-10-07: "I've abandoned all t3 integration as a control plane so you can prune all
that out". Revisions 3 to 8 matched `[t]3` in the probe and treated the T3 Code app and its command-line helpers as
agents; both are removed (`63d2b9bad`, `fe28e5a0c`). One sealed script keeps `t3`: the legacy pre-window check
`scripts/prewindow_check.sh` still lists `t3` among the process names it refuses, because the sealed revision-6
calibration registration pins its bytes (`prewindow_check_sha256`, `d8458eea…`, which calibration acceptance checks
the dwell script against). Changing it would need an erratum to that registration. A block-5 window does not run that
check (the contention dwell replaced it, §4.2); it runs in the clean dwell of a calibration derivation night
(`scripts/run_night.py` `_admit_derivation_clean_dwell`), where the only effect of the extra name is to over-refuse a
process named `t3`, never to miss an agent.

The census is clean when, after this matching, nothing remains (`pgrep` exit 1 with empty output, or every listed
line ignored).
It runs first at the arm, again just before GO, and every 30 s in the window. At the arm, a census that lists an
agent process or cannot be read refuses. In the window, a census that lists an agent process stops the chain; the
window then has no post calibration, so it is not claim-usable (`calibration.no_bracket`). An in-window census that
cannot be read is `census.unmeasured` (DISCLOSE, with the count of consecutive unreadable censuses) and never stops
the chain (audit A3; the earlier stop after four consecutive unreadable censuses, `night_stopped_census_unmeasured`, PLAN2
row 7, is removed, and that code has no emitter). Seats exit before t0, and from 180 s before t0 until it releases
the finished window the watchdog launches no agent session (this hold on launches is the window's **fence**, §3 and
§5.4), so a stop should not fire.

Three things that revision 2 judged are no longer judged. The load average is recorded for each member: the
1, 5 and 15 minute values that `uptime` prints, in the member's environment record
(`per_run_environment_evaluation`, field `load_average_evidence`, marked as not an admission test). Process names
are recorded in every `ps` snapshot the contention hazard takes, at the dwell and in the window (§4.2). The
`corecaptured` spawn count (how often `launchd` started the macOS process `corecaptured` in the last 10 min; the
earlier night kinds refused above two) is not read at all in a block-5 window: its only readers serve those
earlier night kinds (`joulewise/night_gate.py`, `joulewise/evidence_night.py`).

### 4.6 Fixed inputs

1. **Machine:** §0.2; AC power, power mode `ac_high_power`, sampler interval 100 ms; driver standard input is
   `/dev/null`.
2. **Acceptance:** §0.11, ledger cutoff 376, one acceptance for all three windows.
   *When the acceptance stops being usable.* The acceptance file names five **prospective re-derivation triggers**
   (its key `prospective_rederivation.triggers`): events after which a new acceptance must be derived before any
   further bracket is judged. Its rule for them is `judge_under_prior_artifact_never_self_fit`: a capture is judged
   by the acceptance that existed before it, never by one fitted to it. It has no calendar expiry. The five:
   - `protocol_or_estimator_byte_change`: the calibration protocol's digest, or the SHA-256 of one of the four
     estimator files (`joulewise/reduce.py`, `uncertainty_evidence.py`, `powermetrics_fiducial.py`,
     `adapters/powermetrics.py`), differs from the value the acceptance records;
   - `identity_field_change`: the bracket's captures were taken under an identity that is no judged epoch (§4.7
     names the six fields);
   - `corpus_doubles_from_24_to_48`: the ledger holds 48 or more captures of one judged epoch that it classes as
     valid, not counting captures set aside by a decision the acceptance names;
   - `new_valid_same_identity_capture_expands_observed_range`: a valid capture of a judged epoch that the
     acceptance does not list among its prior observations (so, one recorded after its cutoff) has a fiducial
     bound outside the range of the 24, that is, below 0.02193176218569716 s or above 0.03646286164497997 s. A
     window's own pre and post captures are captures of this kind;
   - `new_systematic_failure_challenges_preflight_screen`: a capture of a judged epoch recorded after the cutoff
     carries the ledger class `systematic-invalid` (its own evidence is valid, but its fiducial bound is above the
     screen the ledger recorded it against), or the bracket's pre bound is above the pre screen.

   *Who observes them.* The bracket evaluation (`joulewise/calibration_bracketing.py`), which the harvest runs at
   the desk on each window's bracket. It reads the ledger and lists the triggers it sees under
   `acceptance.prospective_rederivation.observed_triggers` (the identity change under `freshness.stale_fields`).
   When it has seen one, it marks the acceptance stale and fails the bracket with the reason
   `calibration_acceptance_bound_stale`. (One case has another reason: a pre bound above the pre screen fails the
   bracket as `instrument_calibration_mismatch`.) The harvest then records `calibration.bracket_acceptance_failed`,
   which removes the window (§6.5). The capture that fired the trigger stays in the ledger, so every later window's
   bracket fails the same way until a new acceptance is issued.
   *Who stops the next arm.* No program: nothing at the arm, in the plan writer or in the watchdog reads the
   triggers. It is a rule the lead applies. The lead reads the reasons in the harvest's flag (structure, no
   energy), arms no further window, and takes the question of a new acceptance to a cold gate.
3. **Models:** `mlx-community/Qwen3-1.7B-4bit` at revision `3b1b1768f8f8cf8351c712464f906e86c2b8269e` and
   `mlx-community/Qwen3-8B-4bit` at revision `545dc4251c05440727734bcd94334791f6ab0192`, with the tokenizer bytes the
   pack configs pin (panel `configs/model_panels/qwen3_4bit.json` at H_claim).
   **The identity pins are a file in this directory, not part of the plan trees.** Each pack's
   `identity_pin_projection` is `unprojected` and carries no pin. The pins are
   `configs/campaigns/v5_claim_25g83/identity_pins.json`, schema `joulewise.b5_identity_pins.v1`, sealed with this
   file (§12). An **identity unit** is one model running one workload in one pack. There are eight science units:
   `alpha` and `alpha/prefill_p2048` (ALPHA), `beta` and `beta/prefill_p2048` (BETA), and GAMMA's `A/decode`,
   `A/prefill_p2048`, `B/decode` and `B/prefill_p2048`; and, since `754c8c093`, one reference unit,
   `neg8_reference`, shared by all three packs (below). For each unit the file gives three digests:
   - the model artifact SHA-256 (Qwen3-1.7B `e1a4505d32a97bb080eac1d2046b6c99ef46f4483a4323484aaf9b4c546b7f4a`,
     Qwen3-8B `3e0fb77e7ce1ecb7ec844be3ef8856a23643e05317a55054a63d6af62252be31`);
   - the runtime identity SHA-256: the digest of the recorded stack (runtime and version, quantization, tokenizer,
     sampler and output policy, boundary), in the form the harvest recomputes from each bundle;
   - the configuration-set SHA-256: a digest over the scientific content of the unit's member configs.

   Once for the whole block, the file also gives the SHA-256 of the measurement interpreter's package versions,
   `9033a69906aab1f0ff5724b5a6c2f3efd623512ee49a7048713e2410e701c794`. That digest covers Python 3.13.1, mlx 0.31.2,
   mlx-lm 0.31.3, mlx-metal 0.31.2, numpy 2.5.1, safetensors 0.8.0, tokenizers 0.22.2 and transformers 5.12.1.
   `scripts/write_b5_identity_pins.py` generated the file from the packs' identity units and 24 block-3 reference
   bundles of the same two models, without loading a model.
   **The reference unit `neg8_reference`** (orchestrator call, commit `754c8c093`; §0.12, "Which model a reference
   must have run"). *Forcing problem* (Sol delta audit A2): the NEG-8 references and spares run a third model, which
   no science unit pins, so a spare that ran another model raised no identity flag. *What the unit pins:* its member
   configs are all 20 committed reference and spare configs (`configs/campaigns/window_references_v5/`, 7 references,
   and `window_reference_spares_v5/`, 13 spares; `config_count` 20), which name one model,
   `Qwen2.5-1.5B-Instruct-4bit` at revision `8b403126fc14f14cfc99bb4cfa72ecbc129ea677`, and one output policy
   (`run_workload`, a fixed budget of exactly 256 tokens). The runtime stack is taken from the six real `neg8-window-*`
   reference bundles of the 2026-10-06 real-model rehearsal
   (`/Users/edr/night-archive/gate-prune/rehearsal-real/{alpha-1,gamma-2}/archive/sources/claim-runs`), which share
   one stack and each pass the runtime-environment check against the measurement interpreter. Pinned values: model
   artifact `fea4cb940b54448a693c95a0734949cbdca21a39dda990d669b7f615e4a7c712` (as the bundles recorded it; the
   generator requires it to equal the frozen pins of the same model and revision in the committed plan trees
   `d117_floor_qwen25_1p5b_v1` and `d117_contrast_qwen25_1p5b_vs_7b_v1`, and it does), runtime identity
   `e769305d149c49ec2ec5b1ecca1be2c3a5152838a49d25d2b7d22b26d157891a`, configuration set
   `c8d759abd76ec820aba792db92bc4d539d262254c3ac58564a436cc8d0b0607c` (read by this author from the file). The
   science units are unchanged by it.
   The file's SHA-256 at H_claim is `FILL[B5-FINAL-HASHES]`. At the int5 head `fe28e5a0c` it was
   `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9` (computed by this author with
   `shasum -a 256`; `scripts/write_b5_identity_pins.py --check` reproduced the file there, exit 0), and this author
   computed the same value again at the int5 head `9395cecfb`. (The file's own `status` and `sealed` fields are
   labels its generator wrote before the seal; §12 says what seals the file.) It was
   `f78a27f8c8c921e9b3de3403d6b56ea9da4cee92c23520e8ca24c666ecd95257`
   at `43ac12d0c` and at `d3c107f2f`; the only changes since are the added reference unit and the file's `note`,
   which now names it (`git diff 43ac12d0c fe28e5a0c`).
   The NEG-8 lane changed only the three packs' plan-tree digests in it (`git diff a434e363d d3c107f2f`). Earlier
   drafts: `ccce59f9…` at the frozen head `a434e363d`, after lane L10 (`c6309e1a`); `9c2ecd89…` after the timing
   lane `f4cf9047` and at the integration head `b9d02700a`; `039d3e3c…` at `f8164893`. The timing lane's change
   (`039d3e3c…` to `9c2ecd89…`) moved the three packs' plan-tree digests and, for each of the eight science units,
   two digests of its member configs: the configuration-set digest defined above (`config_set_sha256`) and the
   **config-inventory digest** (`config_inventory_sha256`: a digest of the list of the unit's member config files,
   each with its path and the SHA-256 of its bytes, which the file records beside the three pinned digests). L10's
   change moved only GAMMA's plan-tree digest. Neither moved a model or runtime pin (`git diff` of the file across
   those commits, read by this author). The seal binds the bytes at H_claim.
   Two programs compare against these pins. At the arm, the driver passes the file to the model-identity collector
   (`--identity-pins`) when the measurement checkout holds it. At harvest, the harvest reads its archived copy. If
   either finds no pin to compare against, it records `model.identity_unpinned`, which removes the window (§6.5).
4. **Packs:** the three packs at H_claim (§0.7), with the pin bundle of the packs: prompt pin
   `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`, selection
   `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`, ladder
   `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885`.
5. **Policy:** §0.13, `configs/campaign_policies/quiet_mac_p2_b5.json`,
   `ba0f7b7f1538fe87f6281362efbba4b05f7dff74b4bfd78e84c98b9e8859bc60`.
6. **Ledger seed:** block 3's ledger at pin 402 (§0.11), installed at the measurement checkout's default ledger path,
   `<checkout>/runs/calibration_observation_ledger.jsonl`, because the controller's pre-calibration route reads that
   path; the plan writer refuses at the desk if the plan names another. Before each arm the desk runs the read-only
   ledger readiness check; a session left open by an abandoned attempt is closed with the existing abort plus a pin
   advance. For each later attempt the seed is the previous attempt's terminal ledger, whose tip the pin advance
   names. A pin advance is a pin-only commit made in the measurement checkout (which is at the seal commit plus
   pin-only commits, §0.18, §11), not a merged pull request: the merge path took 15–60 min per window for a
   one-file data change (PLAN2 X4).
   **The desk order is chain exit, pin advance, harvest, next arm** (`scripts/advance_b5_ledger_pin.py` at
   `a434e363d`; revision 5 had the advance after the harvest, which the code no longer allows). *Why this order:* the
   window's own post calibration finalizes its bracket session and moves the ledger past the pin the window armed at.
   The desk verdict writer and the next window's **bracket reservation** (the first stage of its chain, which
   opens that window's bracket session in the ledger, §0.11 and §5.1) both read the ledger through the committed
   pin, so both refuse until the pin names this session's terminal entry (§2, "Before ALPHA-1's harvest"; the plan
   writer refuses the next plan at the desk for the same reason). The advance reads the session's terminal entry
   from the ledger, advances the pin through the guarded `advance-head-pin` path of
   `scripts/recover_calibration_ledger.py`,
   and makes a pin-only commit that it checks changes that one path alone. A window stopped before its post
   calibration leaves its session open: the desk aborts the session first, and the abort is then the terminal entry.
   The harvest still reads the live ledger and records how the committed pin relates to the window's terminal entry
   (`pin_relation`; `equal` when harvested in this order).

A change to any item after the seal needs a prospective cold erratum before the next arm (§10).

### 4.7 The one identity refusal at the arm: an OS build and machine model no acceptance judged

*What it checks* (core-prune row ARM-OS; `joulewise/hazards/arm.py` `identity_read`, `joulewise/b5/driver.py`
`_production_arm`, at `a434e363d`). Right after the instant reads, the arm reads `kern.osversion` (the OS build, for
example 25G83) and `hw.model` (Mac15,9) with `sysctl`, and compares the pair with the **judged epochs** of the
calibration acceptance.

- An **epoch** is the identity under which calibration captures are taken. It has six fields: the OS build, the
  machine model, the power policy, the sampler interval, the estimator revision and the pulse protocol
  (`joulewise/calibration_ledger.py` `IDENTITY_EPOCH_FIELDS`). The acceptance was derived on one epoch: 25G83,
  Mac15,9, `ac_high_power`, 100 ms, `joint_loss_sublevel_interval_branch_v2`, `powermetrics_pulse_fiducial_v3`.
- A **continuation** is a registered record that extends the acceptance to one further epoch, on the evidence of
  a derivation session (a ledger session whose captures are taken to derive or extend an acceptance, not to
  bracket a window; `joulewise/calibration_epoch_continuation.py`). The registry of continuations
  (`calibration_bracketing.EPOCH_CONTINUATION_REGISTRY`) is empty at `9b0c680ed`, so at that head the acceptance's
  own epoch is the only judged epoch.
- The **judged epochs** are the acceptance's own epoch and the epoch of every registered continuation that
  authenticates.

The arm loads the judged epochs without the calibration ledger (`acceptance_judged_epochs(artifact, None)`). A
continuation is then authenticated by its registry pin (the SHA-256 of its file) and by the checks of the file
itself; the check of its derivation session against the ledger is skipped. The arm compares only the two fields it
reads, the OS build and the machine model. A pair that matches no judged epoch refuses the window
(`refused_at: "identity"`), before network time is touched. A read that fails is recorded and never refuses; if
the judged epochs cannot be loaded, the check is skipped.

*Why a refusal that is not a physical hazard.* Every timing bound in a window rests on the calibration acceptance
(§0.11), which was derived on one OS build. After an OS update the sampler, the scheduler and the timing estimator's
inputs may all differ, and the acceptance says nothing about them. The pre-calibration writer already refuses such a
window at the pre slot (its kept epoch check, `scripts/validate_powermetrics_fiducial.py`), after the whole dwell.
The arm's check adds no new refusal outcome: it moves that refusal before the dwell. The two do not read the same
set of epochs. The writer loads the judged epochs with its ledger snapshot, so it also checks each continuation's
session against the ledger, and it compares all six fields. The arm's set therefore equals the writer's or
contains it, and the arm tests fewer fields, so the arm never refuses a window the writer would accept. Two cases
pass the arm and are still refused by the writer at the pre slot, after the dwell: a pair covered only by a
continuation the ledger rejects, and a difference in one of the four fields the arm does not read.
*Dissent recorded:* the Sol consult seat (core-prune DESIGN §7, R7) would record the identity at the arm and leave
the refusal to the writer, because doctrine lets only physics refuse. The orchestrator kept it: it changes when a
refusal happens, not whether. *Worked example (synthetic):* macOS updates overnight to build 25H12; the next arm reads
("25H12", "Mac15,9"), finds it among no judged epoch, and refuses in about a minute instead of after a dwell of
3–45 min and a pre calibration.

## 5. Window shape and sizing

### 5.1 The chain

The chain runs its pack's stage graph in block 3's order: the bracket reservation; a 60 s settle; the pre
calibration and its screen; the NEG-8 corpus and the bound derivation; the start triplet; the science stages with
the pack's interior references in their places (the midpoint reference in every pack; in GAMMA also the two
diagnostic interior references, §0.12); the end triplet; the post calibration and a record of the bracket
session's status. Each of the three reference stages (start triplet, midpoint, end triplet) is followed by its
spare-slot retry decision, which runs spares only when the stage lost members (§0.12). Every collection stage starts with its own 60 s settle (§0.6; block 3 used 180 s).

- **The only stops**, all before member 1 (about 13 min into the chain): a failed reservation (chain exit 10), a
  failed pre calibration capture (exit 11), and a pre fiducial bound above the pre screen 0.036462861644980 s
  (exit 12). The chain keeps a **stage journal**, `night/chain-stages.jsonl`: one line for each finished stage, with
  its id, its kind, its return code and its start and end times. A stop adds one line with the stage id `chain.stop`,
  the reason as its kind (`reservation_failed`, `pre_calibration_capture_failed` or
  `pre_calibration_screen_failed`) and the exit code as its return code. A stop writes no flag of its own. It
  leaves the window's bracket session never **finalized**: a session is finalized when both of its captures, the
  pre and the post, have been recorded against it (§0.11), and after a stop either no session was opened or the
  one opened holds at most its pre capture. The harvest therefore removes the window by `calibration.no_bracket`
  (§6.5), and it records `chain.stopped_before_collection` (DISCLOSE). (Revision 10 named a flag
  `instrument.precal_screen_failed` for the exit-12 stop. No program writes that flag; it stays in the catalog as a
  reserved code, §6.2.) The driver records such a window as CHAIN_STOPPED, not GO (§5.7).
  Outside the chain, the driver stops it on `disk.low`, on a census that lists an agent process (§4.5; an unreadable
  census never stops it), when the monitor has written no
  battery or contention reading for about 10 min (`monitor.outage`, PLAN2 row 11), and at the window deadline
  (§5.5).
- Every other stage records its return code and the chain continues. A chain that reaches its end exits 0 whatever
  its stages returned; the flags, not the return code, decide claim use.
- **Operator countdowns: 0 s, except 20 s at the post calibration** (registered deviations 5 and 6, §10; P2-CHAIN,
  `joulewise/b5/chain.py` `COLLECTION_ARM_COUNTDOWN_S`, `CALIBRATION_ARM_COUNTDOWN_S`). An operator countdown is a
  pause, set by the argument `--arm-countdown-s`, written for an operator to step away from the machine before a
  stage captures anything. It has two sources. *The pack:* each of a pack's ten collection stages carries the literal
  `--arm-countdown-s 20`. The two calibration capture stages carry no countdown argument, and the default of the
  capture tool (the calibration writer, `scripts/validate_powermetrics_fiducial.py`, the program that runs one
  calibration capture) is 0 s. *The window runbook* (`docs/phase_2/window_runbook.md`, the written shell procedure
  for running a window, whose `calibrate_slot` function every live window since block 3 used for its captures):
  each calibration capture is run with `--arm-countdown-s 20 --sleep-display-before-capture`. A window runs
  headless, and every collection stage and the pre calibration already follow a 60 s settle, so there the pause
  waits for nothing. The chain therefore does two things. *Deviation 5:* it replaces 20 with 0 on the ten
  collection stages, the only stages whose pack bytes carry a countdown. *Deviation 6:* it adds the runbook's two
  arguments to each calibration capture, with a countdown of 0 s at the pre slot and 20 s at the post slot;
  `chain.py`, which writes the chain script, refuses to render a calibration stage whose pack template already
  carries either argument. The second argument, `--sleep-display-before-capture`, makes the capture tool run
  `pmset displaysleepnow` (the macOS command that turns the display off at once) after the countdown and wait 5 s
  before it captures; if the command fails, the capture goes on and the failure is recorded
  (`display_sleep_action_failed`, §6.10). The post calibration keeps 20 s because no settle precedes it: it follows
  the last end-triplet member directly. *The saving depends on the baseline.* Against the runbook protocol, which
  pauses 20 s at twelve places (ten collection stages and two calibration captures), the chain pauses once, at the
  post slot: 11 × 20 = 220 s saved per window. Against the pack's own bytes, the ten collection stages save
  10 × 20 = 200 s, the pre slot is unchanged at 0 s and the post slot is 20 s longer. (Revision 10 said that each
  pack stage carries the literal 20 and treated the pre slot's 0 s as replacing a pack literal. Only the ten
  collection stages carry it; both calibration countdowns are arguments the chain adds, and the 220 s is counted
  against the runbook.)
- **The window calibration verdict, computed once** (P2-CHAIN and P2-CTL, interface J1). *Forcing problem:* the
  timing estimator's fit of the pre calibration (the **refit**: re-running the pulse fit on the stored 90 MB raw
  capture) is a constant of the window, because its inputs are the same bytes for every member. Yet each member
  recomputed it three times, about 13.5–15 s each: in the child before the run, in the child's reduction, and in the
  parent's strict validation, 357 times per ALPHA window. *Mechanism:* right after the pre-calibration screen the
  chain runs the refit once (`scripts/b5_window_calibration_verdict.py`) and writes the create-once file
  `<claim runs root>/instrument_validation/window_calibration_verdict.json`, holding the SHA-256s of the calibration
  evidence, its manifest, the raw capture, its events and the estimator's code files, and the effective fiducial
  bound. A member uses it only when every digest equals that of its own installed copy and the bound is finite and at
  least the stored bound; otherwise it refits as before and records `calibration.refit_cache_miss` (DISCLOSE). It
  never refuses. The harvest never reads this file: it refits from the raw bytes itself. Saving: 1,654 s before the
  runs and 1,642 s in the reductions per ALPHA window (PLAN2 M1, M2), about 0.92 h.
- **Wall budgets on non-member stages** (PLAN2 row 8, `STAGE_WALL_BUDGET_S`): bracket reservation 900 s, pre
  calibration capture 1,800 s, window calibration verdict 600 s, the corpus-retry decision 300 s, each spare-retry
  decision 300 s (`neg8_spare_retry_decision`), the collected-corpus
  copy 1,800 s, the bound derivation 1,800 s, the session-status record 600 s, each chain flag record 120 s. On
  expiry the stage's process tree gets SIGTERM, then SIGKILL 30 s later, and the stage records return code 124; the
  chain continues as after any failure of that stage. The post calibration capture has no budget: it must be allowed
  to finish, or the window loses its bracket.
- **The collection deadline** (PLAN2 row 17; `chain.py` `CALIBRATION_HORIZON_S`, `HORIZON_*`). *Forcing problem:* a
  bracket is fresh for 24 h from the pre calibration capture, and the window's deadline (§5.5, 28.4 h for ALPHA) is
  longer. A chain that overran past 24 h would lose its bracket, and with it the whole window, not just a tail. The
  deadline cannot simply be lowered: it is the driver's kill time, and a kill loses the post calibration.
  *Mechanism:* a collection stage, the corpus retry, a spare retry and the bound derivation launch only when now +
  the stage's
  allowance ≤ pre-capture start + 86,400 s − 1,430 s. The 1,430 s reserve is a 60 s settle, the 770 s calibration
  pair allowance and 600 s of margin. A collection stage's allowance is 60 s settle + 180 s stage overhead + its
  members × 620 s (at least block 4's largest member allowance, 619 s); a spare retry's is 60 + 180 + k × 620 s for k
  spares. Once one stage is refused (return code 75),
  every later stage is skipped, the chain goes to the post capture, and `roster.horizon_truncated` (DISCLOSE) is
  recorded once; the units lost are then judged by the cell minimum like any other loss. *Worked example:* a
  20-member stage needs 60 + 180 + 20 × 620 = 12,640 s, so it launches only if it starts within 84,970 − 12,640 =
  72,330 s (20.1 h) of the pre capture. A normal ALPHA chain reaches its last stage 5–9 h after the pre capture
  (§5.5), so this fires only on a chain running more than twice its slowest expected length.
- **One retry of the NEG-8 corpus** (PLAN2 row 13; `chain.py` `NEG8_RETRY_MINIMUM`). *Forcing problem:* a corpus
  with fewer than 10 succeeded members cannot give a bound, so the window is lost about 1 h into the chain while the
  chain runs about 7 h more. *Mechanism:* when fewer than 10 of the 12 corpus members succeeded, the corpus stage runs
  once more into the same bound root, inside the collection deadline. The campaign runner skips a member whose bundle
  succeeded, refuses (never re-measures, never replaces) a member whose bundle exists and failed, and measures a
  member that has no bundle. So the retry recovers exactly the members refused before their bundle existed (a
  blocked cooldown, a lineage read failure), never a member that was measured and failed. Each member it measures is
  recorded `member.retried` (DISCLOSE). There is no drain (no early jump to the end references): a window whose corpus
  still has fewer than 10 is removed by `neg8.bound_not_derived` and collects the rest as data. *Worked example:*
  members 4, 5 and 6 are refused before their bundles exist and member 9 is aborted by idle admission (a failed
  bundle), so 8 of 12 succeeded. The retry measures 4, 5 and 6, each flagged `member.retried`, and leaves 9 alone. If
  all three succeed, 11 have succeeded and the bound is derived from those 11 (§5.3). The reference stages have
  their own retry instead, one spare-slot retry per reference stage (§0.12): because the runner never re-measures a
  failed bundle, the reference retry runs pre-registered spares under their own run ids, which also recovers a
  reference that was measured and failed.
- The bracket binding and the whole-window verdict are not chain stages. The harvest produces them at the desk with
  the production writers (`prepare_desk_verdict`). The backups are not chain stages either: they are a desk step after
  the harvest (§5.6).

### 5.2 A failed member costs only itself, and only up to 30 minutes

Every science and auxiliary stage in the committed packs passes `--max-failures 1`, so one admission abort today
drops the rest of a 20-member stage. The chain writer passes `--max-failures <the stage's expected member count>`
instead. This is a **registered deviation** from the pack bytes (§10). The plan trees' `attempt_policy`
(`abort_window_on_any_required_member_failure` in ALPHA and BETA, `abort_window_and_demote_to_non_claim_bearing` in
GAMMA) is read only by the retired freeze author (`arm_readiness_evidence.py`); it is superseded by the flag catalog
and disclosed, not regenerated.

**The member cap** (PLAN2 row 8; `scripts/run_campaign.py` `HAZARD_MEMBER_CAP_S` at `a434e363d`). *Forcing problem:*
no member had a wall-clock limit. A hung member held the chain until the window deadline, whose kill then lost the
post calibration and so the whole window, plus about 15 h of machine time; on 2026-09-16 a blocked file open held a
driver for 11 h. *Mechanism:* a member's child process gets 1,800 s. On expiry it gets SIGTERM, then SIGKILL 30 s
later, to its whole process tree; the runner proves no sampler process of that member is left, writes a `timeout`
row, records `member.timeout` (EXCLUDE_MEMBER) and goes on to the next member. After 2 consecutive timed-out members
the stage drains: only end references still run, then the post calibration. *Why 1,800 s:* the longest member the
sizing allows is an 8B member with both admission attempts and the cooldown at its cap, 619 s, plus 77 s of
bookkeeping, 696 s in all. The longest member cycle block 3 measured (one member's start to the next member's start
inside a stage, the cooldown included) was 274.9 s in its window `g2a-b3w1-20261004T1305Z` and 406.6 s in its window
`g2a-w2-20261003T1748Z` (§5.5 names the member sets). 1,800 s is 2.6 times the allowance and 4.4 times the longest
measured cycle, so it cuts only a member that is not progressing.

**Strict validation moves to the harvest** (PLAN2 M3; P2-RC). In revision 4 the runner strictly validated each bundle
right after it was written: a fresh reduction including a third refit, about 28–30 s per member, all of which the
harvest repeats. Now the runner checks each bundle's structure only (files present and hashed, the config binding,
the prompt hash, the custody identity) and records `strict_validation: "deferred_to_harvest"`; the harvest runs the
full strict validation on every bundle, and a failure is `member.strict_validation_failed` (EXCLUDE_MEMBER) as
before. The runner's stage-end verdict row is labelled provisional, and its idle-admission summary
`deferred_to_desk`: nothing in block 5 reads it. Saving: about 3,475 s plus 655 s per ALPHA window.

### 5.3 The NEG-8 corpus may lose up to two members, for validity or for physics

A corpus member aborted by idle admission no longer aborts the window. **Registered rule:** the bound is derived
from the corpus members that were collected and succeeded, provided there are at least 10 of the 12
(`whole_window.NEG8_DRIFT_MINIMUM_N` = 10); t uses n − 1 degrees of freedom. With fewer than 10,
`neg8.bound_not_derived` removes the window.

*Why it matters.* At 1 abort in 37 members (the block 2 and 3 record), the chance that all 12 corpus members succeed
is (36/37)¹² ≈ 0.72. A rule that needed all 12 would lose about 28% of windows to the corpus alone.

*Implementation at `f8164893` (fix lane fx-harvest).* That lane changed the harvest only. It left the core module
`joulewise/whole_window.py`, which builds, reads and screens the bound, as it was, so the core reader of item 2
still knows only the full corpus. Three programs touch the bound, in this order:

1. **The chain** derives the bound from a window-local copy of the corpus manifest that lists only the collected
   members that succeeded. It records that copy's path and SHA-256 in the driver's terminal record
   (`night/hazard_result.json`, `neg8_corpus.collected_manifest`).
2. **The production verdict writer**, which the harvest runs, reads the bound through the core's reader
   (`whole_window.load_neg8_drift_bound_artifact`, in that core module). That reader authenticates a bound only
   against the committed 12-member manifest. It therefore treats a 10- or 11-member bound as absent, and the stored
   NEG-8 screen fails with exactly two conditions, `neg8_drift_bound_underived` and its idle-subtracted twin.
3. **The harvest** decides both questions itself:
   - *Was the bound derived?* (`neg8_bound`) The bound must be accepted by one of two routes and must then pass a
     member check. *Route 1:* the core reader accepts the bound. *Route 2:* otherwise the harvest reads the
     custodied collected manifest and requires all of the following: its bytes hash to the recorded SHA-256; its
     header equals the committed manifest's; its members are committed members, each once, in committed order; there
     are at least 10 of them; and every member it leaves out did not succeed (a succeeded member left out would be a
     selected corpus; the one closed list of exceptions is below). Then
     `whole_window.validate_neg8_drift_bound_artifact` checks the bound's arithmetic and corpus identity against
     those bytes. If both checks pass, the bound is accepted as derived from the collected subset.

     *The member check* (`harvest.neg8_bound_member_problems`; `derived/neg8-bound.json` records its outcome as
     `members_rederived`). *Forcing problem:* both routes check the bound's arithmetic and which manifest it names.
     Neither reads a bundle, so neither ties the numbers inside the bound to the bundles that lie in this window's
     bound root: a bound file with consistent arithmetic whose numbers came from other bundles would pass both.
     *Mechanism:* the check runs whenever the bound root carries the hazard lineage locator (§0.12), which the
     driver publishes in every block-5 runs root (§0.17), so it runs on every block-5 window. For each corpus member
     the bound names, all of these must hold: (i) exactly one ordinary bundle directory, not a symbolic link, exists
     for it in the bound root; (ii) the SHA-256 over that bundle's complete file inventory equals the
     `bundle_evidence_sha256` the bound recorded for the member; (iii) the bundle's launch lineage does not fail
     authentication (a bundle that carries no lineage stamp passes this test); (iv) its **calibration identity**
     equals the bound's (a bundle's calibration identity is the SHA-256 of the evidence file,
     `instrument_evidence.json`, of the pre calibration it was measured under, recorded in its metadata as
     `instrument_calibration.artifact_sha256`; the bound records the one its corpus shared as
     `calibration_identity_sha256`); (v) its custody triangle agrees (§0.12) and its summary was produced by the
     current reducer from real, non-mock sampler records; (vi) it is the **canonical condition**, which is the
     reference workload of §0.12 as the code tests it (workload profile `df_rq_mid`, 1,024 prompt tokens, 256
     output tokens, no dataset or suite reference, and a `config.json` whose SHA-256 the bundle's metadata
     records), and the SHA-256 of its configuration without the run id equals the one the bound records for its
     corpus; (vii) its gross and its idle-subtracted energy, re-derived from the bundle by the core's own function
     (`whole_window._reference_energy_evidence`), equal the values the bound recorded for it, to a relative and an
     absolute tolerance of 10⁻⁹. One condition is across members: the bundles that carry a lineage stamp (the copy
     of the window's launch lineage, §0.17, that a bundle records in its metadata as `extra.launch_lineage`) must
     all carry the same one, and it must equal the bound's own when the bound records one.

     The bound counts as derived only when a route accepted it and the member check found no problem. In every
     other case, including a bound that names no member and a member check that itself raises an exception,
     `neg8.bound_not_derived` removes the window.
   - *Did the screen pass?* The harvest re-screens the window (`_neg8_rescreen`) in three cases: (a) the stored
     screen's only NEG-8 conditions are the two bound-underived ones and the bound was derived from the collected
     subset; (b) a reference the verdict names is lost at harvest and the stored bracket did not drop it (§0.12,
     "Lost references": it carries a loss flag, or its energy cannot be read, `energy_unreadable`, §6.5); (c) a
     corpus member was dropped for physics and the bound re-derived (below). It re-derives the NEG-8 bracket with
     the core's own **re-derivation**, the function that rebuilds a verdict's NEG-8 bracket from the reference
     bundles instead of trusting the stored row (`whole_window._derived_neg8_decision`). This is not the function
     that this file calls the evaluator, `whole_window.evaluate_neg8_point_drift` (§6.5, §9.1): the re-derivation
     reads the references and then calls the evaluator to screen them. It runs over the reference bundles the
     verdict names, with the window's own validated bound (the physics-clean bound if there is one, else the
     collected-subset bound, else, in case (b) only, the stored bracket's). The time at which the bound's age is
     judged is a physical one ("The bound's age", below). The harvest hands the re-derivation the verdict's
     completion time (the verdict row's `evaluation_scope.completed_at`, else the row's time stamp), and on a
     block-5 runs root the re-derivation replaces it with the latest end of a measured window among the end
     references it reads (a bundle's measured window is its measured request; it ends at the bundle's
     `sampling_stopped` stamp), when every one of those ends can be read. When only some can be read, it uses the
     later of the completion time and the latest readable end, so the bound never looks younger than a physical
     end shows. When none can be read, the
     completion time stands. (Revision 10 said here only "judged at the verdict's completion time".) Re-derived
     first without the harvest's losses, the bracket must have the stored bracket's endpoints and estimand; if it
     does not, these are not the bundles the verdict was written from, and nothing is evaluated. (For a reference
     whose energy cannot be read, this first re-derivation writes what the verdict writer wrote for it, an endpoint
     entry with no energy, so that the comparison can confirm the stored bracket before the reference is dropped.
     That handling was ruled by the **seal gate**, the cold gate that seals this file (§12). The gate ran in two
     stages; **stage 1**, on 2026-10-07, judged revision 9 and required changes, which sections 5 and 6 cite by
     the ruling's own item names (here RF-1). The handling belongs to the harvest program pinned before ALPHA-1's
     harvest, §11 item 4; §6.5 gives the rule and its example.) The decision is
     then the re-derivation that drops the lost references before aggregation.
     The re-screen alone decides: `neg8.screen_failed` is emitted unless the re-screen ran, passed and listed no
     condition. In case (a), any other NEG-8 condition leaves the screen failed; in every case, a re-screen that
     cannot run leaves it failed. The screen runs after the monitor joins (harvest steps `neg8_corpus_physics`, then
     `neg8_screen`), because the physics flags it reads come from them.

Structure (decisions, conditions, member counts, digests) goes to `derived/neg8-bound.json` and
`derived/neg8-screen.json`. The re-derived bracket holds reference-workload energies, so it goes to restricted custody
(`withheld/neg8-rescreen-bracket.json`). The stored verdict of such a window still reads "failed", which is
`whole_window.not_passed`, disclosed only (§6.5).

**Which corpus members may be left out of the bound: one closed list.** *Forcing problem:* the bound may rest on
10 or 11 members, so something must decide which succeeded members are left out, and a loose rule would let a
corpus be *selected* (an inconvenient but valid member dropped). The **NEG-8 mint** is the core function that
builds the bound from the corpus bundles (`whole_window._mint_hazard_neg8_drift_bound`, at `a434e363d`; "the mint"
here and in §0). It gives each corpus member one of three verdicts:

- **keep:** it passes every per-member test the mint applies;
- **omit:** it fails a registered member-validity test that would also remove a science member. The reasons are a
  closed set, `whole_window.NEG8_MINT_DROP_REASONS`: `status_not_succeeded`, `not_current_strict_mint` (its summary
  was not produced by the current reducer from real, non-mock sampler records, so it cannot bear a strict claim),
  `custody_triangle_disagrees` (the three records that name the bundle's sampler, its config, metadata and summary,
  disagree about which sampler produced it),
  `precheck_ineligible` (the fresh re-reduction's gross or idle-subtracted precheck is not eligible) and
  `reduction_mismatch` (the fresh re-reduction differs from the stored summary). The bound is derived from the rest;
- **indeterminate:** the evaluation could not run or could not classify what it saw (a reducer exception, an absent
  or unknown precheck, a missing fresh number). The member is **kept**: unknown evidence never authorizes an omission.
  A kept member with no verified numbers cannot enter a bound, so the mint then refuses.

The mint refuses outright (no bound; `neg8.bound_not_derived`) on anything that is not evidence about one member's
number: an unauthenticated launch lineage, a member that is not the canonical condition (item 3, test vi), an
unrecorded calibration identity (item 3, test iv), a bundle inventory that cannot be sealed (the digest of test ii
cannot be computed: a file cannot be read, or the bundle holds a symbolic link or no file), kept members of more
than one condition (no majority vote), of more than one calibration identity or of two window lineages, or fewer
than 10 kept members. The chain's corpus prune asks the mint itself which members it drops
(`whole_window.neg8_corpus_mint_drops`), so the chain's collected manifest and the mint's input are the same
bytes. The harvest accepts a left-out succeeded member only for one of the five reasons, and records it
`neg8.corpus_member_dropped` (DISCLOSE); any other left-out succeeded member makes a selected corpus and
`neg8.bound_not_derived`. The harvest's accepted reasons are the mint's own set, imported, not copied
(`harvest.py`: `from joulewise.whole_window import NEG8_MINT_DROP_REASONS as NEG8_ACCEPTED_DROP_REASONS`, at
`a434e363d`), so the two cannot drift. *Worked example:* member 7 succeeded, but its fresh re-reduction differs from
its stored summary (`reduction_mismatch`): it is omitted, the bound uses the other 11, and the harvest records
`neg8.corpus_member_dropped` for it. Had member 7's reducer raised instead, it would be indeterminate and kept, and
the mint would refuse.

**A fourth source of omission: physics, applied by the harvest** (NEG-8 ruling of 2026-10-07, decision 4; §0.12).
*Forcing problem:* a corpus member whose request overlapped a competing process measured the contender, not the
instrument. Kept, it inflates the corpus's standard deviation and its envelope, which widens the bound and the
allowance: a bias toward passing. The member-level physics codes of §6.4 are evaluated at harvest from the monitor
journals, which the chain's mint cannot see when it derives the bound. *Mechanism*
(`harvest.neg8_corpus_physics`, after the monitor joins): a corpus member of the validated bound on which a
member-level physics exclusion of §6.4 fires (`contention.request_overlap`, `battery.member_span`,
`battery.accumulator_excursion`, `thermal.os_level_nonzero`, `thermal.powermetrics_pressure_elevated`,
`clock.step_overlap`) is **omitted** from the bound, because its energy is an observation of the disturbance. A corpus
member whose physics is unmeasured is kept. The harvest records `neg8.corpus_member_dropped` for it
(`observed.source` `harvest_physics`, `observed.reason` the first of those codes that fired), writes the bound's own
manifest less those members to `derived/neg8-clean-corpus.json`, builds the bound from the clean members' recorded
points with the core's own builder, and validates its arithmetic and corpus identity against those bytes, as the
collected-subset path of item 3 does. A clean bound that validates goes to restricted custody
(`withheld/neg8-clean-bound.json`), the screen is re-run against it, and the record of the drop is
`derived/neg8-corpus-physics.json`. The minimum stays 10 kept members; fewer, or a clean bound that does not
validate, gives `neg8.bound_not_derived` (`observed.source` `corpus_physics`). For those six measured physics codes
the reference members and the corpus therefore share one rule: each of the six drops a reference from the screen
(§0.12) and a corpus member from the bound. The two differ on evidence that was never taken. Since the seal gate's
stage 1 (2026-10-07, its item RF-5), a reference whose contention or battery evidence is unmeasured
(`contention.unmeasured`, `battery.unmeasured`) is lost, and so is a reference with a measured quiet-state violation
or a failed battery pair (`env.member_quiet_state_violated`, `battery.capture_pair_failed`; §0.12). A corpus member
whose physics is unmeasured is still kept, as above. The gate left the corpus's rule as registered and recorded the
difference for the design round of lane L9-NEG8, to be considered before GAMMA-1 arms: an unseen contender in a
corpus member widens the corpus's standard deviation and envelope, and so the bound, which makes the screen easier
to pass. (Revision 11 said the references and the corpus "share one eligibility rule" without this limit.)
*Worked example (synthetic):* of 12 succeeded corpus members, member 3's request overlapped a
process at 0.09 CPU-s/s (`contention.request_overlap`): the bound is re-derived from the other 11 with t(0.975, 10),
and the screen is re-run against it. Had a second member also been flagged, the bound would rest on 10; had a third,
on 9, and the window would carry `neg8.bound_not_derived`.

**The bound's age is judged on physical times** (PLAN2 row 2, V1). *Forcing problem:* the bound is valid for 24 h,
and revision 4 judged its age at the desk clock of whoever wrote the verdict. A headless harvest of BETA would start
after the watchdog's hold, when BETA's bound was already 23.8–24.4 h old, and the window would be removed for good
(`validity_horizon_expired`). *Mechanism* (`whole_window.py` at `a434e363d`): the bound's derivation time is the end
of the latest kept corpus member's measured window, and its evaluation time is the end of the last end reference's
measured window, both read from the bundles. *Worked example:* the corpus's last member ends at 01:10 and the last end
reference at 08:40: the bound is 7.5 h old when used, whether the verdict is written at 09:00 or 40 h later. A corpus
none of whose kept members has a readable measured-window end has no physical derivation time; the mint then
refuses (`whole_window._hazard_bound_derived_at_s` raises, at `a434e363d`) instead of dating the bound by its own
clock, and the window gets `neg8.bound_not_derived`. Every real kept member passed a fresh reduction, which itself
refuses a bundle with no measured window, so this can happen only to a corrupted corpus.

**OS-build and power-supply strings are disclosed, not staleness triggers** (V2). The bound records the OS build and
a digest of the power-supply identity its corpus saw. A difference against the references used to mark the bound
stale and remove the window; both are labels (a string the OS prints, a hash of the adapter's description), not
measurements of the machine's state. On a block-5 window (the hazard route) a difference is now recorded in the verdict's
`disclosed_binding_changes`; a change of calibration identity stays a staleness trigger, because the bracket is
judged against that identity.

### 5.4 The window's tail

After the post calibration, in this order (`joulewise/b5/driver.py` `run_hazard_night`, at `fe28e5a0c`, unchanged
since `43ac12d0c`): the chain's own process exits; inside the same supervision call (`scripts/run_night.py`
`_run_chain_once`) the driver takes a census of the chain's process group without sending a signal and, if anything
survives, terminates the survivors and proves them gone; only when that call returns does the driver take its time
stamp, which is therefore no earlier than the chain's exit and comes after the proof; next it counts the window's
yield (§5.7); G10 runs if the plan asks and the chain exited by itself (§3), with the monitor and the meter still
journaling; then the driver waits until at least 5 s have passed since that stamp, and so at least 5 s since the
chain exited (polling both supervisors meanwhile; after G10 that time has long passed) and stops the monitor and
the meter (§0.17); last, it writes its terminal record with the window's yield. (Revision 10 put the stamp at the
chain's exit, before the proof.) If the chain's exit could not be proven, the monitor and the meter are left
running for the dead-man (the watchdog's fallback stop). During G10 the driver keeps supervising (cold pass N7,
`_run_g10`, `_wait_supervised`): it waits on G10's process 5 s at a time (`G10_POLL_S`) under the same 1,500 s cap,
and between waits runs the chain's supervision pass, which restarts a monitor or meter that died, records
`monitor.outage` and checks free disk, as during the chain. A supervision pass that raises is recorded
(`supervision_errors`); one that asks for a stop has already written its flag, is recorded (`supervision_stop`) and
ends supervision, while G10, a diagnostic, runs to its end. (Revision 6 said nothing restarted a dead monitor
during G10: the driver then blocked for up to 1,500 s in one wait.) The harvest may open as soon as the terminal
record exists (§7.1), because the driver holds nothing after it.

**The dead-man never signals an unidentified process group** (audit-fix item 9; `driver.reap_orphan_monitor`). When
the watchdog's fallback stop finds a recorded monitor or meter process group, it signals it only if it can identify
the group's leader: either by the recorded start time and the identity reader, as before, or, without them, by `ps`
showing the recorded command line on a process that started between 5 s before and 1 s after the journal's start
stamp. Otherwise it leaves the group alone and writes `monitor.orphan_unverified` (DISCLOSE), because signalling an
unidentified group could hit an unrelated process that reused the id.

**The watchdog releases a finished window at once** (PLAN2 X1; `scripts/magistrate_watchdog.py` at `a434e363d`,
P2-WD). *Forcing problem:* in revision 4 the watchdog treated a window as running until t0 + `WINDOW_MAX_S` + 300 s
even after its chain had exited, and launched no headless session meanwhile, so the machine sat idle about 15 h after
every chain. *Mechanism:* while the watchdog treats a window as running it launches no headless session. That hold
on launches is the window's **fence**; it begins 180 s before t0. The watchdog releases the fence, once and for good
(a one-way latch keyed on the plan id, the custody root and the SHA-256 of `result.json`), when on one tick it sees
both a finished custody directory and a quiet process table. The release exists only for block-5 plans (receipt
class `HAZARD_PACK`, §0.17).

- *The custody half* (`joulewise/arm_retry.py` `terminal_window_release`). Two files in the window's `night/`
  directory are always required. One is `courier.sent`. The **courier** is the driver's last step: it launches a
  headless session, retried up to three times, that emails Ed the window's structural report (§5.7), and that
  session writes `night/courier.sent` once its email has been accepted for delivery. The other is the driver's
  terminal `result.json`, carrying this plan's id, the receipt class `HAZARD_PACK` and a finite end time no later
  than now. Beyond those, the directory must have one of two shapes:
  - *a collected or a CHAIN_STOPPED window:* `chain.started` and `chain.exited` are both present, and the driver's
    verdict in `result.json` is one of GO, REFUSED, ABORTED (a chain the driver itself stopped, §5.1) or
    CHAIN_STOPPED. The driver writes `chain.exited` only once the chain's process group is proven gone (above);
  - *a NULL window* (a refusal before the chain was started): neither `chain.started` nor `chain.exited` is
    present, the driver's verdict is REFUSED, and `result.json`'s `chain_exit_code` and `chain_sha256` are both
    null.
- *The process half* (`scripts/magistrate_watchdog.py`), on the same tick: the agent census is empty; no driver
  process is running; and no live process has a command line that names the plan's custody root (the driver, the
  monitor, the arm's collectors and G10 all carry it). A process table that cannot be read never releases.

A driver that never wrote its first record is released through a create-once `night/launch_abandoned.json`. A
failed courier keeps the old dead-man timing. After the release, `WINDOW_MAX_S` bounds only a hung chain or a dead
driver. (Revision 10 required `chain.started` and `chain.exited` for every release, which would never release a
NULL window, and named two of the three process conditions.)

### 5.5 Sizing

- **T_stream_max** = 335 s for every window (§0.14). The sizing output records each pack's own longest stream:
  ALPHA's is 314 s (its members are all 1.7B-class), and BETA's and GAMMA's are 335 s (their 8B members). It sets
  every pack's `T_stream_max_s` to the block's longest, 335 s, at which the frequency gate passes for
  |f| ≤ 3.6306 ppm.
- **Programmed span.** The programmed span is the chain's length if every member takes its longest allowed path. The
  rule keeps block 4's conventions and uses the chain at the int5 head `fe28e5a0c` (`scripts/size_b5_window.py`, its
  `conventions` list):
  - span = (1 + collection stages) × 60 s settle + the collection stages' countdowns (0 s, §5.1) + the pre and post
    calibration pair (770 s) + the bound derivation (320 s) + the corpus prune (320 s) + the window calibration
    verdict (60 s) + the sum of member allowances + stage custody + the terminal shutdown (300 s) + one corpus retry
    + the reference spare retries;
  - a **member allowance** is load + warm-up + prefill + forced decode + the cooldown at its 300 s cap + both
    idle-admission attempts (275 s: two attempts of 110 s each plus guards, against an observed attempt maximum of
    103.6 s at the former 750 records). That is 595 s for a 1.7B member and 619 s for an 8B member. NEG-8 and
    reference members are charged as 1.7B members. These allowances come from block 4's committed source, which
    predates the 576-record idle baseline (§0.3); an attempt now takes about 83 s (75 s of capture plus block 3's 8 s
    of attempt overhead), so the allowance over-covers it and is kept;
  - **stage custody** (the bookkeeping time around members) is 180 s per collection stage, plus 77 s per member
    (45 s reduction, 32 s sampler start and wind-down), plus 2 × 240 s bracket-writer custody, 300 s reservation and
    120 s terminal custody;
  - **one corpus retry** (§5.1) is charged as one more corpus stage: 60 s settle + 180 s overhead + 12 × (595 + 45 +
    32) s = 8,304 s;
  - **the reference spare retries** (§0.12) are charged at their worst case, every spare run: for each reference
    stage, 60 s settle + 180 s overhead + its spares × 672 s (spares are reference members, charged as 1.7B members,
    595 + 77 s). That is 2,256 s for each triplet (3 spares) and 912 s for the midpoint (1 spare), 5,424 s (1.51 h)
    per window, the same in all three packs (`reference_spare_retry_s` in the sizing output);
  - the **bound derivation** is now charged 320 s, not block 4's 60 s: a real derivation re-reduces 12 bundles,
    about 270–320 s (PLAN2 §1.4 item 6; never measured live). The **corpus prune**, which asks the NEG-8 mint which
    corpus members it would drop (§5.3), reads the same 12 bundles and is charged the same. The **window calibration
    verdict** (§5.1) is charged 60 s for one refit of about 15 s.
- **`WINDOW_MAX_S`**, the window's deadline measured from t0, = 60 × ceil((span + 3,300 s) / 60). The 3,300 s is the
  arm's allowance: the dwell cap of 2,700 s plus the census, reads, network-time OFF, collectors and cadence probe.
- **`B5-SIZING-OUTPUTS`**: `configs/campaigns/v5_claim_25g83/sizing_b5.json`, schema `joulewise.b5_sizing.v1`. Its
  sealed bytes are the bytes it has at H_claim, and the seal record (the record of §12 that pins each sealed file
  by its SHA-256) pins theirs. SHA-256 at H_claim: `FILL[B5-FINAL-HASHES]`. At the int5 heads `fe28e5a0c` and
  `9395cecfb` it was `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa`, unchanged from `d3c107f2f`
  (`shasum -a 256`, and `scripts/size_b5_window.py --check` reproducing the file byte for byte with exit 0: both run
  by revision 9's author at `fe28e5a0c` and by this revision's author at `9395cecfb`). *The file's own labels.* The
  file carries `"status": "UNSEALED_DRAFT"` and `"sealed": false`, and its `note` begins "UNSEALED DRAFT". The
  program that generates the file (`scripts/size_b5_window.py`, below) writes those labels, and no program reads
  them. They are not rewritten at the seal, because a rewrite would change the sealed bytes and that program's
  `--check`, which regenerates the file and compares, would then fail on a label; the seal record's SHA-256 of the
  file is what seals it (orchestrator ruling of 2026-10-07 on the seal preparation, its item F6; §12). Earlier
  drafts:
  `f114f9b9…` at the frozen head `a434e363d`, before the spares; `a5c6ec05…` at `b9d02700a`; `7c53ebc8…` on lane
  L10's branch with the older sizer; `b31a27b5…` after the timing lane `f4cf9047`; `9d16edfe…` at `f8164893`. The
  value in force is the one the seal record pins. `scripts/size_b5_window.py` writes the file from block 4's
  committed sizing source
  (`configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json`, SHA-256
  `f414301cd0328236f9309962b60ff4635026dac973ca3b0ce564b677c47baa81`) and from the packs' stage graphs, order
  manifests and configs. `--check` reproduces the file byte for byte. The program also refuses unless its arithmetic
  reproduces block 4's committed 22,494 s span and 25,800 s window. Block 4's source names four GAMMA configs to fix
  which model is 1.7B-class and which 8B; the timing lane's regeneration changed their bytes (their `idle_seconds`
  and the entry `calibration-plan-sha256=<digest>` in their `run_metadata.tags`, which names the pack's calibration
  plan by its SHA-256), so the program reads them at the bytes GAMMA's plan tree now records and lists them under
  `class_map.superseded_block4_configs`; bytes recorded by neither still refuse. Each window plan reads
  `/packs/<label>/programmed_span_s` and `/packs/<label>/T_stream_max_s` from it. Lane L10 changes only GAMMA's
  plan-tree digest and the two diagnostic stages' order-manifest paths and digests; the members per class (61 / 40),
  the programmed span and `WINDOW_MAX_S` do not change, because the sizing still charges each diagnostic stage as
  one auxiliary member at the reference members' allowance. (That is the sizing's classification only. The yield
  count of §5.7 classes the same two stages as science stages.)

  | Pack | Members, 1.7B-class / 8B | Programmed span | `WINDOW_MAX_S` | Expected chain, block-3 basis | Expected chain, projected |
  |---|---|---|---|---|---|
  | ALPHA | 119 / 0 | 98,826 s (27.5 h) | 102,180 s (28.4 h) | 31,584 s (8.8 h) | 19,460 s (5.4 h) |
  | BETA | 19 / 100 | 101,226 s (28.1 h) | 104,580 s (29.05 h) | 32,634 s (9.1 h) | 20,510 s (5.7 h) |
  | GAMMA | 61 / 40 | 87,690 s (24.4 h) | 91,020 s (25.3 h) | 27,747 s (7.7 h) | 17,426 s (4.8 h) |

  The programmed spans and `WINDOW_MAX_S` are read from the sizing output with the SHA-256 printed above for
  `fe28e5a0c` and `9395cecfb`; they are the sealed file's values when its SHA-256 at H_claim, also above, is that
  same digest. Each span is revision 6's plus the 5,424 s of spare retries (93,402, 95,802 and 82,266 s at
  `a434e363d`). The
  members column counts the planned roster, without spares; the expected-chain columns assume no spare runs.

- **Why the deadline is about three times the expected chain.** The rule charges every member, at once, both worst
  cases: the cooldown runs to its cap and idle admission needs its second attempt; and it charges a corpus retry and
  seven spares that most windows never run. *Worked decomposition, ALPHA:* 119 members × 595 s = 70,805 s, of which
  35,700 s is every member's cooldown at its 300 s cap and 32,725 s is every member's two admission attempts.
  Per-member custody adds 119 × 77 = 9,163 s; the corpus retry 8,304 s; the spare retries 5,424 s; settles,
  calibration, derivation, prune, the window calibration verdict, stage custody and shutdown the other 5,130 s; span
  98,826 s. For comparison, block 3's window `g2a-b3w1-20261004T1305Z` measured 16 **cooled member cycles** (the
  time from one member's start to the next member's start inside a stage, when the next member had a cooldown; the
  cooldown and the custody are inside it), with a median of 236.5 s, a mean of 242.9 s and a maximum of 274.9 s;
  each member here is charged 672 s (595 + 77).
- **Is that right? As a deadline, yes.** A chain stopped at its deadline loses its post calibration, and so the
  whole window. The deadline must therefore never cut a slow window that could still be claim-usable. A chain
  anywhere near this bound would have most members at the cooldown cap, and `member.cooldown_cap_hit` removes such
  members, so that window would fail the cell minimum anyway (5 of 10 units in each stratum since the seal gate,
  8 before; §6.6). A quad is dropped when any one of its four members is removed, so if only half the members were
  removed, independently, a quad would be kept with probability (1/2)⁴ = 1/16, and a cell would keep at least 5 of
  its 10 quads with probability about 1.8 × 10⁻⁴ (the binomial tail for 10 quads at 1/16, computed by this author).
  The deadline now exceeds the 24 h calibration
  horizon; the collection deadline (§5.1) keeps the post calibration inside the horizon, so a slow chain is truncated
  to a usable tail rather than killed. Since the watchdog releases a finished window at once (§5.4), the generous
  size costs only the time to notice a hung chain or a dead driver.
- **Expected chain time** (planning only; it gates nothing). Two figures:
  - *Block-3 basis* (measured, an upper planning figure). The median of the 16 cooled member cycles of block 3's
    window `g2a-b3w1-20261004T1305Z` (above), at 750 idle records, 236.5 s, plus 10.5 s for an 8B member; per
    collection stage 60 s settle + 39 s head + 62 s tail (block-3 maxima); fixed 60 s pre-calibration settle +
    770 s calibration pair + 320 s bound derivation + 320 s corpus prune + 60 s window calibration verdict + 300 s
    terminal = 1,830 s (scratch `sizing_v2.json`, SHA-256
    `6a82745f47b40c8aa1ea6aefe2c45c2d4cce2b7a7e65d114165057e64fae00de`). Each pack has 10 collection stages.
    - ALPHA: 1,830 + 10 × 161 + 119 × 236.5 = 31,584 s ≈ 8.8 h.
    - BETA: 1,830 + 1,610 + 19 × 236.5 + 100 × 247.0 = 32,634 s ≈ 9.1 h.
    - GAMMA: 1,830 + 1,610 + 61 × 236.5 + 40 × 247.0 = 27,747 s ≈ 7.7 h.
  - *Projected* (not measured; built from the measured block-3 mean cycle and the savings of the changes now in the
    code). Its starting figure is 257.1 s, the mean start-to-start cycle PLAN2 §1.1 gives for 36 members of block
    3's two windows (`g2a-w2-20261003T1748Z` and `g2a-b3w1-20261004T1305Z`; PLAN2 gives a median of 234.5 s for the
    same 36, and this author did not re-derive either). That is a different member set from the 16 cycles of the
    block-3 basis, so 236.5 s and 257.1 s are not the median and the mean of one sample. For scale, the 26 cooled
    member cycles of the two windows together have a mean of 262.7 s and a maximum of 406.6 s (recomputed by this
    author from `/Users/edr/night-archive/gate-prune/timing/member_timing.csv`, timing fields only). Per member,
    subtract 22.9 s for the 576-record idle baseline (2,725 s over 119 members, timing ruling), 41.0 s for the 2×
    cooldown rule (mean wait 53.9 → 9.1 s over 109 cooldowns, 4,883 s over 119 members, timing ruling) and 56.9 s
    for the refit done once and strict validation moved to the harvest (1,654 + 1,642 + 3,475 s over 119 members,
    PLAN2 M1–M3): 136.3 s for a 1.7B member, 146.8 s for an 8B member. Per collection stage subtract the 20 s
    countdown (assuming, as PLAN2's budget does, that it ran inside the 39 s head): 141 s. The stage-end verdict
    saving (PLAN2 S4, about 655 s per window) is not subtracted, because the 62 s tail is not decomposed.
    - ALPHA: 1,830 + 10 × 141 + 119 × 136.3 = 19,460 s ≈ 5.4 h.
    - BETA: 1,830 + 1,410 + 19 × 136.3 + 100 × 146.8 = 20,510 s ≈ 5.7 h.
    - GAMMA: 1,830 + 1,410 + 61 × 136.3 + 40 × 146.8 = 17,426 s ≈ 4.8 h.
  ALPHA-1 measures which figure is right. Each window adds its 4–46 min arm (§4.1: about 41 s of reads, collectors
  and cadence probe, then a dwell of 180 to 2,700 s, so 221 to 2,741 s). Below about 119 s from one decode's end
  to the next idle capture, recovery is untested (archived gaps 119–740 s); ALPHA-1 records idle medians and cooldown
  waits against block 3's 30.6 mW reference as a diagnostic (PLAN2 §1.4 item 4).
- **Deadline stop.** A chain still running at t0 + `WINDOW_MAX_S` is stopped by the driver; the window then has no
  post calibration, so it is not claim-usable (`calibration.no_bracket`). Nothing is resized after such a stop.
  Each member's time allowance and `WINDOW_MAX_S` are values of the sealed sizing output (`sizing_b5.json`:
  `member_allowance_s` and each pack's `window_max_s`). The sizing program takes no observed member cycle as an
  input, and its `--check` passes only when it reproduces the sealed file byte for byte. A larger member allowance
  is therefore a change to a sealed output. The question goes to a consult first (§0.1). If the consult finds that
  an allowance must grow, the change is a cold erratum (§10) with a new sizing file, and the new file is pinned,
  before the next arm, by an addendum to the seal record (§12: the record that pins each sealed file by its
  SHA-256; an addendum adds a pin to it). *Where the new file may lie.* It is never a changed `sizing_b5.json`
  committed in the measurement checkout. That file is a window input (a tracked file under `joulewise/`, `scripts/`
  or `configs/`, whose bytes a window can read; §6.5 builds the term), so a commit that changes it there would give
  every later window the flag `code.executed_differs_from_sealed`, which removes the window (§6.5). The plan writer
  takes an allowance from any file inside the measurement checkout: it is given the file's path, its SHA-256 and a
  pointer to the value, and refuses unless the file's bytes hash to that SHA-256 and the pointer resolves to the
  stated number of seconds (`joulewise/b5/plan.py` `read_allowance`). So the new sizing file is written as a new,
  untracked file outside `joulewise/`, `scripts/` and the pack's directory (an untracked file under those roots is
  itself a difference, §6.5), for example under the git-ignored `runs/` directory, and the next plan cites it
  there with the SHA-256 the addendum pins. *Why the case is remote:* the deadline is built from the programmed
  span, the chain's length if every member takes its longest allowed path: 24.4, 27.5 and 28.1 h for GAMMA, ALPHA
  and BETA (the table above), about 27 h, to which `WINDOW_MAX_S` adds the arm's 3,300 s. The projected chain is
  4.8 to 5.7 h, about 5 to 6 h, and the block-3 basis 7.7 to 9.1 h. A chain reaches its deadline only by running
  about five times its projected length, or about three times the block-3 basis. A chain that slow is sent to its
  post calibration first by the collection deadline of §5.1, inside the 24 h calibration horizon, as the bullet
  "Is that right?" above says. (Revision 10 registered a rule that set the next attempt's allowance, without an
  erratum, to the larger of the sizing output's and the stopped attempt's largest observed member cycle, "plus the
  sizing margin". No such margin is defined in this registration, the analysis plan, the flag catalog, the sizing
  file or the sizing program, and no program derives an allowance from an observed cycle, so that rule is
  withdrawn.)
- **Block duration.** Assume every window is claim-usable on its first attempt. With the watchdog releasing each
  window at its terminal record (§5.4), one window to the next is the window plus about 0.6–1.6 h: the driver's tail
  and courier about 0.1 h, a watchdog tick of up to 5 min, the pin advance and the next plan a few minutes, the
  harvest 0.5–1.5 h, and the 180 s stand-down lead (PLAN2 §1.3). Adding three arms of 4–46 min, the three windows
  take about 18–23 h at the projected chains (15.9 h of chain) and about 28–33 h at the block-3 basis (25.6 h of
  chain), before any re-arm or frequency redraw. (Revision 4, with the
  fence held to t0 + `WINDOW_MAX_S` + 300 s, gave about 71 h before desk gaps.)

### 5.6 Disk between windows

The harvest archive is an APFS clone of the collected roots where the tool allows (it shares storage until
modified).

**`BACKUP-DESTINATIONS`** (filled from committed code and the runbook):

- *Where they are named.* Each attempt's window plan names two destinations, `claim_backup_destination` and
  `bound_backup_destination`, as absolute paths (`joulewise/b5/plan.py`).
- *What is checked.* At the arm, the disk hazard requires room for one planned copy on each destination's volume
  (`joulewise/b5/driver.py`, disk targets). In the window only the volumes the chain writes to are watched, so a full
  backup volume never stops a chain.
- *Where they point.* By the window runbook's convention (`docs/phase_2/window_runbook.md`, `CLAIM_BACKUP_DEST` and
  `BOUND_BACKUP_DEST`) they are `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/<window>/claim` and
  `…/bound` in iCloud Drive. iCloud Drive's local folder is on the runs volume, which is why the arm counts three
  copies there (§4.2).
- *Who copies.* The copy itself is a desk step after the harvest (`scripts/backup_runs.sh`, the packs' `backup`
  stages, which the chain does not render). No block-5 program runs it at this writing; the lead runs it.

The disk hazard re-measures free space at every arm, so no separate disk ledger is kept.

### 5.7 Yield: counting what was collected

*Forcing problem.* Several causes make every member of a window refuse before its bundle exists: about 15 window-level
checks are repeated by each member, so one deterministic failure among them loses all of them. In revision 4 such a
window ended with 0 of 119 bundles, chain exit 0 and verdict GO. A stage's return code of 1 cannot tell one lost
member from twenty (a healthy ALPHA shows about 2.6 stages with a nonzero code), the cause sat only in logs the
courier does not send, and chain stops at exit 10, 11 or 12 also said GO. With windows back to back, a deterministic
cause would repeat in every window, at 1.5–3 h of chain each, until someone read a harvest.

The **yield** is counts only: members planned, logged, succeeded, and bundles present. It is never an energy, a
power or a duration, so it is releasable structure under §8 item 2. It never stops collection, and it costs under
50 ms of reads per stage boundary. (PLAN2 §2.2; `joulewise/b5/driver.py` and the harvest at `a434e363d`.)

- **Yield plan.** Before the chain starts, the driver lists, for each collection stage: its id and position, its
  runs root, its run ids (less any run id an earlier stage already launched into the same root), the number planned,
  and **min_valid**, the fewest succeeded members that still leave the stage able to do its job:
  - the NEG-8 corpus stage: 10 (the bound's minimum, §5.3; a minimum of 12 would raise a false alarm in about 28% of
    windows);
  - start and end triplets: 2 of 3; midpoint: 0 of 1 (the screen's minimum, §0.12; `driver.REFERENCE_ENDPOINT_MIN_VALID`,
    `REFERENCE_MIDPOINT_MIN_VALID`). The driver does not count spares: its yield plan lists only the planned
    members, so a stage whose loss a spare restored still shows that loss in the driver's counts;
  - science stages: ⌈planned × 8 / 10⌉ (`driver.SCIENCE_MIN_NUMERATOR` and `SCIENCE_MIN_DENOMINATOR`, 4 and 5): 16
    of a 20-member quad stage (five quads), 8 of a 10-member absolute stage (a workload's ten absolute repeats,
    §0.8). If each member is lost independently with probability 1/37, these trip by chance with probability
    1.6 × 10⁻⁴ and 2.1 × 10⁻³, so a trip means a systematic cause. This fraction was the stage's share of the cell
    minimum while that minimum was 8 of 10 units (revisions 3 to 9). The seal gate then set the cell minimum to 5
    (§6.6). The driver's fraction is a constant of its own, not read from the catalog, and it stays at 8 of 10: a
    yield status removes nothing, and the two probabilities above still hold for it. So for a science stage LOW
    is now an earlier warning than the cell rule, and a stage can be LOW, or even ZERO, in a window whose cells
    all still meet the minimum (the worked example at the end of this section);
  - GAMMA's two diagnostic interior-reference stages (`gamma-reference-decode-midpoint` and
    `gamma-reference-prefill-midpoint`, one member each, §0.12): 1 of 1. The driver sorts a stage by its runs root
    and its members' roles (`driver._stage_role`). A stage that writes to the bound root, or holds a member with the
    role `neg8_reference_corpus_member`, is the corpus stage. A stage whose members all have the role
    `neg8_daily_reference_midpoint` is the midpoint. A stage whose members' roles all begin `neg8_daily_reference`
    (`…_start`, `…_end`) is a triplet. Every other stage is treated as a science stage. The diagnostic role,
    `window_interior_reference_diagnostic`, fits none of the first three, so these two stages get the science
    rule, ⌈1 × 8 / 10⌉ = 1. One lost diagnostic member therefore gives its stage the status ZERO (no bundle
    present) or LOW (fewer succeeded than min_valid), both defined in the next item, and gives the window the
    yield status LOW ("Terminal record", below). At the same loss rate of 1 member in 37 that happens by chance in
    1 − (36/37)² = 5.3% of GAMMA windows, so for these two stages a trip does **not** indicate a systematic cause.
    The diagnostic members enter no claim. A yield status stops nothing and removes nothing; it sends a notice. A
    LOW that comes from one lost diagnostic member alone is one lost member, not a cause repeated across members,
    and it does not hold the next arm (§7.3). The magistrate's brief carries that sentence (the magistrate is the
    headless lead session the watchdog launches, and its brief is the instructions it runs under). (Revision 10
    did not list this case. By the orchestrator's ruling of 2026-10-07 the code stays as it is for block 5; giving
    the diagnostic role its own minimum, 0 of 1 like the midpoint's, is a code change deferred until after
    block 5.)

  It is written once to `night/yield_plan.json`, outside the plan's `hazard_window` block.
- **Counting a stage.** To count a stage the driver checks each planned bundle directory: present, and summary
  status succeeded. Raw-byte validity stays with the harvest. It writes one line to `night/stage_yield.jsonl` with
  the stage's status: **ZERO** (none of the planned members present), **LOW** (succeeded below min_valid) or
  **OK**. ZERO and LOW record `yield.stage_zero` or `yield.stage_low` and write
  `night/yield_alert-<position>.json` once. *When a stage is counted* (`driver.YieldTripwire`,
  `YIELD_COUNT_FRESH_S` = 30): the count must never run during an idle capture, so a stage is counted inside the
  window only in the settle that follows it. That needs two things: the next stage in the chain is a collection
  stage or the bound derivation (a collection stage starts with a settle, and the derivation captures nothing), and
  the stage's line in the stage journal (§5.1), when the driver reads it, has an end time between 2 s in the future
  and 30 s in the past. Every other stage is counted once, at the terminal record, after the chain's process group
  is gone: the last collection stage, which runs straight into the post calibration, and any stage whose journal
  line was already older than 30 s or has no numeric end time. Such a stage's yield line, flag and alert file are
  written only then, so the watchdog can pick that alert up only after the chain has ended.
- **Repeated refusals.** The **campaign log** is `<runs root>/campaign_log.jsonl`, to which the campaign runner
  appends one row for each member it handled, with the member's run id and status, whether it ran the member or
  blocked it before invoking it. The driver reads the rows added since its last read, but only at a stage boundary
  (in the settle in which it counts the stage) and once more in the terminal pass, never during a stage. Three
  consecutive members that ended without a bundle for one shared cause record
  `stage.members_refused_pre_bundle_identical`, once per cause; because of when the log is read, the flag is written
  when the stage holding the three members ends, not right after the third. The cause is the log row's
  `child_refusal`: the member's last non-empty error line with its digits replaced by `#`, cut to a fixed length,
  or, when the member was refused by the launch-lineage check, that check's reason code. A row without one is keyed
  by its exit code together with whether the member was blocked before it was invoked (`blocked_before_invoke`).
  (Revision 10 said the driver reads the log "as it grows" and gave the exit code alone as the second key.)
- **Stall.** No new bundle directory and no new stage journal line for 3,600 s records `yield.stage_stalled`, once.
- **No process is started for any of this in the window.** A network call would sit inside a settle, the idle
  stretch the next member's cooldown and baseline read. (Revision 6 also cited the agent census, which then matched
  "t3", "claude" or "codex" anywhere in a command line; it now ignores the window's own processes, §4.5.) The watchdog, a scheduled job and not an agent,
  picks the alert files up on its own tick (`scripts/magistrate_watchdog.py` `queue_yield_alerts`, lane P3-WD, at
  `a434e363d`): for a window from t0 − 180 s until its dead-man deadline, each `night/yield_alert-*.json` is queued
  once as a notice for Ed (`notice_pending`, kind `yield_alert`, with the file's SHA-256). A file it cannot read is
  recorded as an event, and a file over 64 KiB is queued unread. Reading an alert never changes a fence, a release or
  a launch. The notice reaches Ed when the watchdog next launches a headless lead session (the **magistrate**), which
  comes soon after the window ends because the watchdog releases a finished window at once (§5.4); a true mid-window
  email would need a network process inside the window.
- **Terminal record.** After the chain's process group is proven gone, the driver writes the window's yield into
  `night/hazard_result.json`: planned, logged, succeeded, failed, bundles present, the per-stage rows, and the
  **yield status**: **EMPTY** (no bundle present at all), **LOW** (some stage below its min_valid), **FULL** (every
  planned member succeeded), **PARTIAL** (otherwise), or **UNKNOWN** (the count failed or nothing was planned; it
  changes nothing else). The verdict stays GO for a collected window, because it describes the arm; an EMPTY window
  exits 5. A chain stopped at exit 10, 11 or 12 gets the verdict **CHAIN_STOPPED**, never REFUSED (which would have
  held the watchdog longer). A failed post calibration and a failed bound derivation are recorded as their own faults.
  EMPTY, LOW and CHAIN_STOPPED send a fault email to Ed (a change of state). The courier's notice leads with
  "collected X of Y planned members"; it never carries durations, member identities or error texts.
- **At the harvest.** `harvest.json` and `derived/window_flags.json` carry planned, present, raw-valid (a stream of at
  least 1 MiB and no missing files) and succeeded, overall and per stage; a spare counts as planned only when the
  retry ran it (its bundle exists), and an unrun spare is never `member.bytes_missing`. The command prints members =
  raw-valid / planned and the window-removing reasons. When members were planned and no bundle is present, the
  harvest's yield step records `collection.zero_yield`, and the command exits 6 when the harvest's verdict is
  COLLECTED or NO_COLLECTION (§7.1); a chain stopped at exit 10, 11 or 12 therefore records the flag and exits 6.
  (Revision 10 tied both to a COLLECTED window only.) `collection.failure_histogram` reads the **operator logs**
  (`<custody>/operator-logs/*.log`, one log for each stage's output), takes every line that begins `error:`, and
  groups those lines by their text with the digits replaced by `#` (full texts to
  `withheld/failure-texts.json`). A disagreement with the window's own `stage_yield.jsonl` records
  `yield.harvest_disagrees_with_window`. A window whose stage journal (§5.1) exists and holds no line of a
  collection stage is harvested as **NO_COLLECTION**, with `chain.stopped_before_collection`, every collector
  still run (§7.1). A chain that started and was killed before its first stage ended has written no stage journal
  at all. That window is harvested as COLLECTED, without that flag; `collection.zero_yield` then records that no
  bundle is present, and `calibration.no_bracket` removes the window.

Every yield code is DISCLOSE (§6.8): `cell.below_minimum` and `neg8.bound_not_derived` already remove a window where
it matters; the yield exists to say early that members were lost and to stop a repeat (§7.3). *Worked example
(synthetic).* An ALPHA window ends with stage rows corpus 12/12, start triplet 3/3, the first decode quad stage 0/20
(ZERO), the rest full. The terminal status is LOW (a stage below its min_valid of 16), and Ed gets a fault email
that leads "collected 99 of 119 planned members". At the harvest the 20 members without a bundle are removed
(`member.bytes_missing`, §6.7). They are five of the decode cell's ten quads, so the cell keeps 5 quads and all 10
repeats. That meets the minimum of 5 units in each stratum (§6.6): `cell.below_minimum` does not fire, and the
window is claim-usable if nothing else removed it, with the decode cell's 5 kept quads printed beside it. Under the
minimum of 8 that revisions 3 to 9 registered, the same window was removed. One more lost member in the second
decode quad stage would leave 4 quads, and `cell.below_minimum` would then remove the window. (Both outcomes were
computed by this author with the exclusion function, `joulewise.flags.exclusions.compute`, on ALPHA's roster as the
harvest builds it at the int5 head `9395cecfb`, with the catalog whose `rules.cell_unit_minimum` is 5, int5 lane
commit `059fafc55`: 5 kept quads give `claim_usable` true, 4 give false with the reason `cell.below_minimum`.)
Whatever the harvest decides, when the 20 members were refused for one shared cause the orchestrator does not arm
the next window on the same code until that cause is fixed (§7.3).

### 5.8 The whole-machine meter (a recorded diagnostic)

*Forcing problem.* Every registered number is a processor-rail energy (§1): the CPU, GPU and ANE package as the
sampler reports it. A reader will ask what share of the machine's energy that is, and whether the rail estimate moves
with the machine's energy from member to member. The sampler cannot answer: it sees only the rails. An independent
instrument at the machine's power input can, without touching any claim.

*Boundary.* Every element of the path, from the wall to the rails:

```
 mains AC --> [adapter, 140 W] --USB-C cable, 28 V--> [KM003C meter] --USB-C--> [Mac DC input]
               AC-to-DC loss here:                    Vbus and Ibus,               |
               NOT measured                           50 samples/s                 +--> processor rails, CPU+GPU+ANE
                                                                                   |    (powermetrics: the claim boundary)
                                                                                   +--> rest of the machine (memory,
                                                                                   |    storage, fans, display asleep)
                                [battery] <--- B0AC x B0AV, SMC, 1 read/s -------->+
```

- *mains AC* and the *adapter*: the 140 W charger; its conversion loss happens before the meter and is not measured;
- *USB-C cable, 28 V*: the adapter and the Mac agree to 28 V under USB Power Delivery's extended power range;
- *KM003C meter*: an inline USB-C power meter (POWER-Z KM003C) in that cable, reporting the bus voltage (Vbus) and
  current (Ibus) 50 times a second;
- *Mac DC input*: the meter measures what enters the Mac; the Mac's own reading of the same quantity is the SMC key
  PDTR (§4.2);
- *battery*: when it assists, it supplies the machine beside the DC input, and the meter cannot see that energy; the
  battery term −B0AC × B0AV (SMC, once a second) adds it back;
- *processor rails* inside the machine are the claim boundary; the *rest of the machine* is everything else the
  DC input feeds.

So the meter's boundary is **whole-machine DC input plus the battery term**, not wall AC: the charger's loss is
excluded.

*The reader.* `scripts/km003c_monitor.py` (at `a434e363d`) polls the meter every 200 ms at ordinary scheduling
priority (the probe rejected background priority) and reads B0AC, B0AV, PDTR, PSTR and PPBR from the SMC at every
poll. It writes one create-once stream file per start, `<custody>/hazards/meter/stream-NNN.jsonl`: a header (status
`streaming` or `absent`), one line per poll, error lines, and a trailer. The header and trailer each carry a pair of
clock readings (CLOCK_MONOTONIC_RAW and `time.monotonic_ns`), so the stream can be placed on the members' clock. When
no meter is attached it writes an `absent` header and exits 0, and the driver does not restart it. Its cost: 0.302
CPU-s over a 120 s live run, 0.25% of one core. It runs outside the chain's process tree, so the contention monitor
counts it, at about 0.0025 CPU-s/s, one twentieth of the 0.05 limit; its own energy is on the rails like the
monitor's and is disclosed with it (analysis plan §8.1).

*Quantities* (`joulewise/external/km003c_parse.py` and the harvest's `meter_joins`, at `a434e363d`), for each member
over one window, its measured request (the harvest's request span, `sampling_started` to `sampling_stopped`). Revision
5 also named each phase; the code computes the request only, so phase-level figures are not produced in block 5:

- **ΔE_rail**: the rail energy above the member's idle baseline, the bundle's `idle_subtracted_energy_j` as the
  harvest re-derives it from the raw records;
- **ΔE_machine** = [E_meter(window) − P_meter(baseline) × T] + [E_battery(window) − P_battery(baseline) × T], where
  T is the window's length, E(window) is the mean of the samples inside the window times T, P(baseline) is the mean
  over the member's idle-baseline stage, the meter power is Vbus × Ibus and the battery power is −B0AC × B0AV at each
  SMC read. When no SMC read falls in the window or the baseline, the battery term is marked unavailable and
  ΔE_machine is the meter term alone;
- **ρ** = ΔE_rail ÷ ΔE_machine, the rails' share of the machine's extra energy; undefined when ΔE_machine ≤ 0.

The meter's timestamps are CLOCK_MONOTONIC_RAW; member spans are in `time.monotonic_ns`. The two differ by a constant
except across a system sleep, taken from the stream's own clock pairs (rejected if its start and end pairs disagree
by more than 1 ms) or, failing that, from the monitor's clock journal line nearest the span.

*Worked example (synthetic).* A member's idle baseline reads a meter mean of 9.0 W and a battery power of 0 W. Its
measured request lasts 20.0 s with a meter mean of 52.0 W and a battery mean of 1.5 W (assist). The meter term is
52.0 × 20 − 9.0 × 20 = 860 J; the battery term is 1.5 × 20 − 0 = 30 J; ΔE_machine = 890 J. With ΔE_rail = 712 J,
ρ = 712 ÷ 890 = 0.80, inside the hard band of analysis plan §8.2 (0 < 0.80 ≤ 1, and 890 − 712 = 178 J ≥ 0). Without
the battery term ρ would read 712 ÷ 860 = 0.83: leaving the battery out overstates the rails' share whenever the
battery helps.

*How well it reads* (all on 2026-10-06). At the desk, 120 s idle: 0 dropped and 0 duplicated samples, largest
clock-fit residual 10.0 ms (the parser fits the meter's sample clock to the host's clock from the poll times; the
residual is how late a batch arrived beyond that fit), median PDTR/meter ratio 0.992, Vbus 27.44–27.50 V, no flag.
The probe's 300 s run: largest residual 16.8 ms; PDTR/meter median 0.986. Under the B0AC validation load (§4.2), on
20 s bins: PDTR = 0.955 × meter + 2.3 W (r = 0.9975), median per-second ratio 0.987; and PSTR = 0.959 × (meter +
battery power) + 2.1 W (r = 0.993), so the system's total is accounted for by the DC input plus the battery term. The
probe could not test ρ itself: on the loaded desk machine background work moved the baseline and gave negative ρ. So
the central band for ρ is set by the first clean window (analysis plan §8.2).

*Flags* (all DISCLOSE; their observed fields hold counts, mA, V, milliseconds and the PDTR/meter ratio, never an
energy, so they are structure):

| Code | Fires when |
|---|---|
| `meter.absent` | the stream header says `absent`, the stream has no samples, or no stream file exists |
| `meter.drops_excess` | dropped samples ÷ (kept + dropped) > 0.5% |
| `meter.duplicates` | the meter re-delivered samples that the parser dropped (count > 0) |
| `meter.clock_fit_residual` | the largest clock-fit residual > 2 sample periods (40 ms at 50 samples/s), or no fit |
| `meter.pdtr_gain_out_of_band` | the median over 1 s bins of mean PDTR ÷ mean meter power is outside 0.95–1.02, or cannot be computed |
| `meter.battery_activity` | a B0AC read inside a member window is nonzero (either direction) |
| `meter.vbus_out_of_contract` | a sample's Vbus is outside 26.6–29.4 V (28 V ± 5%) |

*What it can never do.* The meter never refuses an arm or a window, never removes a member, and never enters a
claim-bearing number. ΔE_rail, ΔE_machine and ρ are energies and an energy ratio: they go to restricted custody in
one file per window, `withheld/meter.json` (one row per member, with the stream used, the clock-offset source and
whether the battery term was available), until the release event, like every other energy (§8). No file is written
when the window has no meter stream; `meter.absent` records that. `meter.battery_activity` is a member-level flag;
the other `meter.*` flags are window-level. The driver's supervision of the reader (§0.17) adds one more DISCLOSE
code, `meter.supervision_fault`: the reader could not be started; it crashed within 30 s of its start five times in a
row (it is still restarted, every 30 s instead of every 1 s); the supervisor failed to record an event; or the
reader could not be proven stopped (`joulewise/b5/driver.py`, `MONITOR_BACKOFF_AFTER` = 5, `MONITOR_RAPID_EXIT_S` = 30,
`MONITOR_RESTART_BACKOFF_S` = 30).

## 6. Flags and exclusions

### 6.1 Where flags come from

How each kind of file in the table is written (an **fsync** is the call that forces written bytes onto the disk):

- the flag files `<custody>/flags/*.jsonl` are append-only, with an fsync after every line;
- the driver's `night/stage_yield.jsonl` is appended a line at a time, with an fsync after every line;
- the monitor's journals under `hazards/monitor/` are append-only and written a line at a time, but synced to disk
  at most once every 5 s and when the journal is closed (`hazards/monitor.py` `FSYNC_INTERVAL_S` = 5.0), so a
  power loss or kernel panic can lose about the last 5 s of readings;
- the meter's stream files `hazards/meter/stream-*.jsonl` (§5.8, a diagnostic) are each created once by one run of
  the meter reader, written through a memory buffer that is handed to the operating system about once a second,
  and synced to disk once, when that run stops (`scripts/km003c_monitor.py`);
- `derived/flags.jsonl` is not appended to: the harvest creates it once, in a single pass, with an fsync after every
  line;
- the JSON documents in the table (`arm.json`, `window_flags.json`, `exclusions.json`, the yield alert files) are
  not line files: each is written whole, once.

(Revision 10 said of all of them: "append-only, with an fsync per line".)

| Stage | File | Writer |
|---|---|---|
| Desk, before an arm (never during a dwell or a window) | `<custody>/flags/desk.jsonl` | the record-only collectors run by the lead; a window-removing flag here means the cause is fixed before scheduling; the driver never reads these flags |
| Arm | `<custody>/hazards/arm.json` (verdicts and measurements); `<custody>/flags/arm.jsonl` (collectors) | the hazard arm; the collectors |
| Window | `<custody>/hazards/monitor/{clock,battery,thermal,contention,disk}.jsonl` plus raw bytes; `<custody>/hazards/meter/stream-*.jsonl` (§5.8); the driver's flags, `night/stage_yield.jsonl` and `night/yield_alert-*.json` (§5.7) | the monitor; the meter reader; the driver |
| Harvest | `derived/flags.jsonl` (every flag, de-duplicated); `derived/window_flags.json` (summary); `derived/exclusions.json`; numbers under restricted custody `withheld/` | the harvest |

### 6.2 The catalog

`flag_catalog.json` is normative; this section states its rules in words. Its `rules.cell_unit_minimum` is 5.

*No code stays unclassified for good* (audit-fix 2, Opus audit F2). Revision 6 kept two codes deliberately out of the
catalog so that they would always block the release event. But the loader also refused any catalog that classified
them, so the registered cure for an UNCLASSIFIED code (a cold erratum classifying it, §7.2) could never be applied,
and one torn flag line left its attempt blocked for ever. Now:

- `records.malformed_flag` (a flag line that failed validation: torn, not JSON, or not a valid flag record) is
  DISCLOSE. Because the line may have carried an exclusion, the harvest reads what the line still shows of its code,
  whole or as the prefix it was torn inside, and lists every code it could have been among the codes that a program
  writing flag files before the harvest can emit (`harvest.PRE_HARVEST_CODES`, held equal to those writers' code tables
  by a test); a code that only the harvest emits is never a candidate, because the harvest derives it again from the
  preserved bytes, so a damaged line cannot have lost it. If any candidate is an
  EXCLUDE_WINDOW code, it adds `records.malformed_flag_exclusion_possible` (EXCLUDE_WINDOW). Otherwise, if any is an
  EXCLUDE_MEMBER code and the line still shows a run id, it adds `records.malformed_flag_member_exclusion_possible`
  (EXCLUDE_MEMBER) on that member. A line that shows no code, or a possible member code but no run id, is disclosed
  only: the rule excludes on what the line shows, never on what it might have said (`harvest._malformed_flag_line`).
  A line torn just after the opening quote of its code shows an empty prefix, which names no code (cold pass 2 N7;
  before the fix, the empty prefix matched every code and so removed the window).
  *Worked example (synthetic):* a line torn after `{"code": "calibration.capt` could only have been the controller's
  `calibration.capture_battery_pair_unverified` (DISCLOSE): the four window-removing codes with that prefix are
  emitted by the harvest alone, so the line is disclosed and removes nothing. A line torn after
  `{"code": "model.identity_m` could have been the arm collector's `model.identity_mismatch` (EXCLUDE_WINDOW), so the
  window is removed. A line that still shows a member's run id and is torn inside `"code": "member.tok` could only
  have been `member.token_count_mismatch` (EXCLUDE_MEMBER), so that member is removed (candidate lists computed from
  the catalog and the writers' code tables).
  *Where the narrowed list lives.* Limiting the candidates to the codes of programs that write before the harvest is
  the seal gate's ruling of stage 1 (2026-10-07, its item RF-3; revision 11 listed every catalog code as a
  candidate, so a torn copy of a disclosed flag could remove a window). The constant `harvest.PRE_HARVEST_CODES` and
  the test that holds it equal to those writers' code tables are part of the harvest program that an addendum to
  the seal record pins before ALPHA-1's harvest (§11 item 4). The harvest at H_claim still draws its candidates from
  every code the catalog or its own code table lists (`harvest._candidate_codes`); that can only remove more, never
  less, and no block-5 window is harvested with it.
- `collector.unmeasured` (a collector the flag package does not know how to class) is still absent from the catalog,
  so it blocks the release event until a cold erratum classifies it, which the loader now accepts.

| Family | What it covers | Effect |
|---|---|---|
| PACK_IDENTITY, CODE_IDENTITY, MODEL_IDENTITY | the pack, the executed code or the model differs from what was sealed, or could not be compared | EXCLUDE_WINDOW (one member whose model identity cannot be derived from its own metadata: EXCLUDE_MEMBER) |
| CALIBRATION | the bracket is missing, invalid, unbound or fails the acceptance, the ledger it is judged from fails its own integrity checks, a capture saw charging or AC loss, or an earlier capture the acceptance relies on changed | EXCLUDE_WINDOW (DISCLOSE: the desk's ledger-readiness checks before an arm; battery assist during a capture; a changed capture the acceptance does not rely on; a historical file that could not be read; the writers' records of §6.10) |
| NEG8 | the bound was not derived, the screen failed, the verdict holding the screen is absent, or a verdict that did not pass cannot name its failed members | EXCLUDE_WINDOW (DISCLOSE: the aggregate verdict codes of §6.5, a corpus member dropped for a registered reason or for physics, lost references and a lost midpoint (§0.12; on GAMMA a lost midpoint makes the attempt not claim-usable through the pack-scoped window reason `neg8.midpoint_lost_primary`, §0.16), and the verdict producer's own records) |
| INSTRUMENT | a member that could not read the sampler binary's digest; and one reserved code for a failed pre-calibration screen, which no program writes (the failed screen stops the chain at exit 12 and the window is removed under CALIBRATION by `calibration.no_bracket`, §5.1, §6.5) | the member that could not read the digest: EXCLUDE_MEMBER, §6.3, unless the harvest re-derived it: DISCLOSE; the reserved code: EXCLUDE_WINDOW in the catalog |
| CLOCK_SYSTEMATIC | a step during a calibration capture; most recorded anchors not `bounded` | EXCLUDE_WINDOW |
| MEMBER_VALIDITY | §6.3 | EXCLUDE_MEMBER |
| PHYSICS_IN_SPAN | §6.4 (battery assist is DIAGNOSTIC, not this family) | EXCLUDE_MEMBER |
| ROSTER | §6.7 | EXCLUDE_MEMBER in the catalog for five codes. Two of them remove a member under their own name: `roster.run_id_mismatch` and `roster.before_chain_started`. The other three (`roster.not_in_plan`, `roster.foreign_attempt`, `roster.creation_unplaced`) only label a bundle that is ignored; the member such a bundle leaves without a usable bundle is removed as `member.bytes_missing` (§6.7). Window-level roster failures (`roster.duplicate_run_id`, `roster.no_science_bundles`, `cell.below_minimum`, §6.5): EXCLUDE_WINDOW. The chain's and the harvest's roster records, such as a retried member, a horizon-truncated tail (§5.1) or a window with nothing present (§5.7): DISCLOSE |
| RECORDS | lineage formalities and the driver's pre-launch lineage check, the pin ledger, missing journals, a member's error output not copied, malformed and rebuilt flag lines, unreadable operator logs; and five reserved codes that no program writes (receipts, attempt history, provenance digests, naming, notices; listed below) | DISCLOSE (three exceptions: source bytes changed during the harvest, EXCLUDE_WINDOW; a malformed flag line that could have been a window exclusion, EXCLUDE_WINDOW, or a member exclusion naming a readable member, EXCLUDE_MEMBER) |
| DIAGNOSTIC | network-time output, clock steps and frequency changes outside any span, G10, s1-structural checks, the battery-temperature rise across a stage (§0.6), battery assist (§6.4), the whole-machine meter (§5.8), the yield counts (§5.7), an unread hazard probe at the arm (§4.1), monitor restarts and orphans left unsignalled (§5.4, §6.8); and three reserved codes that no program writes (listed below) | DISCLOSE |

**Nine reserved codes.** Nine codes are in the catalog although no program writes them at the code this revision
read (`9b0c680ed`; searched in `joulewise/` and `scripts/` for each code's literal and for flag codes assembled
from parts). An **emitter** is a place in a program that writes a flag with a given code. A code with no emitter
cannot fire, so in block 5 these nine remove nothing and disclose nothing. They stay in the catalog as
**reserved** codes, each with its registered effect (orchestrator ruling of 2026-10-07 on the fidelity sweep), and
the catalog's note on each says "Reserved: no emitter at H_claim." They are:

- `instrument.precal_screen_failed` (INSTRUMENT, EXCLUDE_WINDOW). Its condition, a pre fiducial bound above the pre
  screen, stops the chain at exit 12, and the window is removed by `calibration.no_bracket` (§5.1, §6.5);
- `records.receipt`, `records.attempt_history`, `records.provenance_digest`, `records.naming` and `records.notice`
  (RECORDS, DISCLOSE). The flag package defines them in one group of seven record formalities
  (`joulewise/flags/catalog.py`); the other two of the seven do have an emitter: `records.lineage_formality` (the
  driver, §0.17) and `records.pin_ledger` (the controller, §6.10);
- `clock.sntp_offset` (the offset from a time server), `monitor.probe_in_phase` (a monitor probe inside a target
  phase) and `battery.accumulator_diagnostic` (accumulator intervals with no registered unit scale) (all DIAGNOSTIC,
  DISCLOSE). For the last, the condition can no longer be reached as a flag: without a registered scale the
  accumulator rule raises an error, which the harvest records as a fault of its own, so that harvest ends as
  HARVEST_FAULT (§7.1).

`contention.kernel_task_share` is a different case: it has an emitter whose condition cannot occur today (§6.8).

### 6.3 Member exclusions: validity

A member is removed from every cell it feeds when any of these is flagged:

- its status is not `succeeded` (`member.status_not_succeeded`), or idle admission refused it after its retry
  (`member.admission_aborted`);
- its bundle fails strict validation, which re-reduces the raw evidence (`member.strict_validation_failed`); its
  re-reduction is not byte-identical to the stored summary (`member.reduction_mismatch`); or a required file is
  missing, unreadable or present twice (`member.bytes_missing`, `member.unreadable`, `member.bytes_ambiguous`);
- its clock anchor is not `bounded` (`member.anchor_not_bounded`), or the harvest's recomputed status differs from
  the recorded one (`member.anchor_recompute_mismatch`);
- its runtime-observed token counts differ from the registered counts (42 or 2048 prompt tokens, 512 output tokens)
  (`member.token_count_mismatch`);
- its target phase (`phase.decode` for decode members, `phase.prefill` for p2048 members) fails its precheck
  (`member.target_phase_precheck_failed`), including the one precheck test that reads a science energy,
  `anchor_energy_envelope_exceeds_quarter_metric` (`member.anchor_energy_envelope_exceeded`, blinding RESTRICTED). The
  p42 phase is not a target phase. The catalog's blinding class (§0.16) is each code's default: 191 codes are
  STRUCTURE and this one is RESTRICTED. The harvest also marks single flags RESTRICTED in two places, whatever
  their code's default (§8 governs every RESTRICTED flag). One is a `member.target_phase_precheck_failed` flag
  among whose listed reasons (the precheck's reasons that have no code of their own) one has a name that contains
  "energy" or "effect" or ends in "_metric" (`harvest.restricted_reason`; in practice the one reason
  `anchor_energy_envelope_unrecorded`). The other is the `diagnostic.s1_structural` flag that carries the per-cell
  precheck counts, always, because whether a precheck is eligible can turn on the energy envelope (revision 10
  named only the one RESTRICTED code);
- the GPU was not idle during its idle baseline (`member.idle_window_suspect`); its cooldown hit the cap
  (`member.cooldown_cap_hit`); or its campaign cooldown evidence does not verify (`member.cooldown_evidence_unverified`);
- its configuration bytes are not in the pack's committed inventory (`member.config_not_in_inventory`; the lineage
  check refuses such a member at write time, so normally its bundle is simply absent);
- its model identity cannot be derived from its metadata (`model.identity_underivable`; on a NEG-8 reference or
  spare this also makes the reference lost, and the survivors decide the screen, §0.12);
- its #421 per-capture battery pair (the registry read just before and just after its sampler stream, kept as raw
  bytes) is present and failed (`battery.capture_pair_failed`). One failure is disclosed instead: when the pair failed
  on its endpoint current alone (the pair rule tests the unsigned |InstantAmperage| > 200 mA), every failed endpoint
  reads a negative InstantAmperage from its own raw bytes, the SMC reads cover the member (§6.4), and the member's
  battery join found none of `battery.member_span`, `battery.accumulator_excursion` and `battery.unmeasured`, the
  failure was discharge, and `battery.capture_pair_assist` (DISCLOSE) replaces the exclusion and names it
  (`harvest._pair_assist`). Without SMC coverage the exclusion stands, because the journal then cannot show the span
  free of charging;
- the whole-window verdict lists it among its per-member failures (`member_failures` in the verdict row) for a reason
  that no other member code carries (`member.whole_window_member_failure`). Those reasons are:
  - its environment evidence is missing or failed (`environment_admission_missing`, `environment_admission_failed`);
  - its CPU-idle criteria do not replay from its own telemetry (the `cpu_*` reasons and
    `processor_combined_power_w_p95_exceeded`), or its GPU idle admission does not (`gpu_idle_admission_*`);
  - its idle-admission attempt cannot be paired with the telemetry it was judged on
    (`idle_admission_attempt_ledger_invalid`).

  The verdict's other two per-member reasons already have their own codes. In-window thermal pressure is
  `thermal.powermetrics_pressure_elevated` (§6.4), and an invalid bundle is `member.strict_validation_failed` and its
  kin. Leaving those two out keeps each exclusion in one family, and the sensitivity line of analysis plan §8.1 names
  `thermal.powermetrics_pressure_elevated` among the three codes it ignores. (The **sensitivity line** is a second
  value printed beside a cell's or a contrast's primary value, the one computed with every registered exclusion
  applied. Thermal pressure and contention plausibly rise with the workload's own load, so removing the members
  they touched could pull a mean toward its cooler members. When a unit was removed by one of the three codes for
  those hazards, `thermal.os_level_nonzero`, `thermal.powermetrics_pressure_elevated` and
  `contention.request_overlap`, the same estimator is therefore computed again over the units that would be kept
  if those three codes were ignored. A unit that carries any other code stays removed. The seal gate adopted the
  line in this narrowed form at its stage 1 (2026-10-07; §14 Q6). Revision 11 described here the proposal the gate
  then judged, which ignored the whole PHYSICS_IN_SPAN family. Had in-window thermal pressure also been listed
  under `member.whole_window_member_failure`, every member with thermal pressure would carry that second code as
  well, and the line could never restore it.)

  *Why this rule is needed.* Its environment evidence includes the post-run observation that the displays stayed
  asleep and the screensaver stayed off through the request. That observation is how decision D-078 (item 4) closed
  the screensaver contamination class of July 2026, and no other code measures it. The verdict as a whole is only
  disclosed (§6.5), so without this member rule a member whose display woke during its request would be kept.
  *Code state:* the harvest emits it at `a434e363d` (`harvest.whole_window_member_failures`), one flag per listed
  member with its reasons, whether or not the verdict authenticates. When a verdict that did not pass has no
  `member_failures` list, or one its own validator rejects, no member can be named, and the window is removed
  instead (`whole_window.member_failures_unreadable`, §6.5).
  *One case moved* (audit-fix item 6 and the orchestrator's ruling on it, 2026-10-07): a post-run guard observation
  whose collector raised an exception (every reading null, `collector_error` set; §6.10) is no longer missing
  environment evidence to the verdict, so the verdict does not list the member for it. The member is still removed,
  by `member.target_phase_precheck_failed`, through the reducer's **environment barrier**. That is the step of the
  reducer (`joulewise/reduce.py` `_apply_environment_claim_barrier`; the reducer is one of the four pinned estimator
  files of §2 item 1, whose bytes are unchanged since `a434e363d`) that reads the member's recorded environment
  evidence, its admission record and its post-run observation, and, when that evidence is missing or failed, writes
  the reason (`environment_admission_missing` or `environment_admission_failed`) on every precheck of the member,
  the phase prechecks included, so that none of them is eligible. The ruling left the barrier unchanged: it marks
  such a record `environment_admission_failed` on the member's target prechecks, because an unmeasured post-run
  environment cannot show the member clean.

Codes added since revision 4 that remove a member (catalog effect EXCLUDE_MEMBER; their writers are in §6.10):

- `member.timeout`: the member's child was stopped at the 1,800 s cap (§5.2);
- `env.member_quiet_state_violated`: during the member a display was awake, the screensaver ran, or Low Power Mode
  was on (measured states);
- `member.idle_admission_telemetry_missing`: idle admission passed every test it could evaluate, but its CPU
  telemetry was missing or too short, so the idle window's quietness is unmeasured;
- `instrument.binary_identity_unmeasured`: the member could not read the SHA-256 of the `powermetrics` binary it ran
  (a different digest still refuses the member before it runs). The harvest supersedes it when it can re-derive the
  digest (cold pass N1, Fable audit F10; `harvest` step `binary_identity`): the binary is a system file that changes
  only across a reboot, so when the member's collection boot (`extra.launch_lineage.collection_boot_session_id`) is
  the harvest's own boot and the SHA-256 of the executable the member recorded (`device.powermetrics.executable_path`,
  `/usr/bin/powermetrics` by default) equals the calibrated digest (`instrument_calibration.bindings.powermetrics_sha256`),
  the flag is moved whole into `instrument.binary_identity_rederived` (DISCLOSE) and the member is kept. A different
  digest, another or an unknown boot, or an unreadable executable keeps the exclusion.

Revision 5 also listed `member.stderr_uncopied` here. It is now DISCLOSE (orchestrator, 2026-10-06, at `a434e363d`):
it records that the copy of a member's error output into the stage log failed, which is a record not written, not
a measured fault. A writer that cannot write a flag to its flag file prints the whole flag on its error output
behind the fixed marker `JOULEWISE_UNWRITTEN_FLAG ` (§6.10). A flag the member printed that way is still recovered,
because the harvest also scans the member's own error-output file (`operator-logs/member-stderr/`).

### 6.4 Member exclusions: physics in the member's span

A member's **span** is the earliest-to-latest hull of two time ranges, in the controller's `time.monotonic_ns()`
domain: its sampler stream (the `pre_spawn` to `post_parse` clock stamps, or the sampling markers when those are
missing) and the controller's battery span (from the start of the idle baseline to the end of the **idle drift
sentinel**, the short idle reading the controller takes right after the request). The hull over-covers rather than
under-covers. The member's **request span** is `sampling_started` to `sampling_stopped`: the measured request
(`harvest.member_spans`, at `a434e363d`). A member whose span cannot be placed is removed (`member.span_unknown`),
because the rules below cannot be applied to it.

**Battery** (ruling of 2026-10-06, §9.2; sources and validation in §4.2). The harvest's join decides
(`joulewise/b5/harvest.py` `battery_join`, `_battery_assist`, `accumulator_member_flags`, at `a434e363d`). Terms used
below:

- The registry publications **in force** for a span are the last publication at or before its start, every
  publication inside it, and the first publication at or after its end. SMC reads in force are chosen the same way.
- An SMC read is **good** when B0AC is an integer with no read error, and **fresh** when its five recorded keys
  (B0AC, B0AV, PDTR, PSTR, PPBR) differ from the previous good read's: a frozen SMC repeats its block, and repeats
  are not new measurements. The SMC **covers** a span when good, fresh reads are no more than 5 s apart across it
  (`battery.SMC_MAX_GAP_S`). When it does not, the registry's InstantAmperage and Amperage at the in-force
  publications stand in for B0AC in the current rules below, and `battery.smc_unavailable` (DISCLOSE) records the
  fallback.
- Each good read **holds** its value from its own time until the next good read, never longer than 5 s. A read
  belongs to a stretch of time when its hold overlaps that stretch for a positive time, so the read in force at a
  stretch's start belongs to it, and a read taken at or after its end belongs to what follows.
- **Assist**: the battery discharging into the machine while the adapter is connected and the battery is not
  charging. It is **any** negative B0AC read (ruling item 1) on a span in which no registry read showed the charging
  state (IsCharging Yes) or the loss of AC (ExternalConnected No). −200 mA is not part of the definition; it is the
  threshold the assist report counts reads against.

Rules:

- `battery.member_span` (EXCLUDE_MEMBER) fires on any of:
  1. *charging current:* a good B0AC read in force above +200 mA; without SMC coverage, InstantAmperage or Amperage
     above +200 mA at an in-force publication;
  2. *charging or AC lost:* IsCharging Yes or ExternalConnected No at any in-force publication, or at any good 5 s
     registry poll inside the span.
- `battery.accumulator_excursion` (EXCLUDE_MEMBER): over an interval between two consecutive in-force publications,
  the charge accumulator implies a mean charging power above 200 mA × the publication's voltage (units below); or,
  without SMC coverage, the discharge accumulator's mean is **positive** and beyond that limit. The discharge
  accumulator sums discharging ticks only, so a positive mean is inconsistent evidence, not discharge, and without
  SMC coverage it keeps the exclusion. The flag marks the case on the interval's own row:
  `observed.intervals[i].sign_inconsistent` is true (`observed` itself holds `rule`, `intervals` with the first 8
  rows, `count` and `watts_per_unit`; revision 10 wrote the marker as `observed.sign_inconsistent`). With SMC
  coverage the same reading is `battery.accumulator_unavailable` (DISCLOSE; cold pass N4), whose row carries the
  whole interval entry under the same per-row key: the 1 s SMC reads measure the current directly and remove the
  member for any charging read (`battery.member_span`), so a 60 s registry record that disagrees with itself adds
  no evidence of a hazard. The harvest and the hazard module's copy of the rule (`hazards/battery.py`, where the
  same case was `battery.member_span`) changed together, and a parity test holds them equal. A negative discharge
  mean beyond the limit is assist evidence, below.
- `battery.unmeasured` (EXCLUDE_MEMBER), the missing-evidence predicate: the charging and AC state over the span is
  unknown, so the member cannot be kept. Only the registry reads that state; the SMC current says nothing about it.
  - *With SMC coverage:* no registry publication in force at or before the span's start; an in-force publication
    that lacks IsCharging or ExternalConnected; or a **state hole**: more than 120 s between consecutive good
    registry reads that carry both state fields, among the last such read at or before the span's start, every one
    inside and the first at or after its end. With no read before the start, the stretch from the start to the first
    read counts; with no read after the end, the stretch from the last read to the end counts (the monitor may have
    stopped after the span; while it runs, its 5 s poll writes a line on any state change).
    *Worked example (synthetic):* span 100–130 s. State reads at 0 s and 62 s and none after: of the reads at or
    before the start only the last, at 62 s, is in the set (the read at 0 s plays no part), so one stretch is
    judged, from 62 s to the span's end, 130 − 62 = 68 s. That is at most 120 s, so the state counts as measured.
    State read only at 0 s: the stretch from 0 s to the span's end is 130 s, more than 120 s, so the member is
    `battery.unmeasured`.
  - *Without SMC coverage* (unchanged from revision 4): no registry publication for more than 120 s overlapping the
    span, or an in-force publication lacking a state or current field.
- `battery.assist` and `battery.assist_outside_request` (both DISCLOSE). The computation is skipped only on a state
  read: an in-force publication, or a good 5 s registry poll inside the span, that read IsCharging Yes or
  ExternalConnected No (rule 2 of `battery.member_span`). A charging-current read above +200 mA (rule 1) removes the
  member but does not skip the computation: the span's negative reads still give the assist flag, and their
  discharged energy is still written to the withheld record below. (Revision 10 said no assist was computed in
  either case.) The member's span is split into **phases**: with a request span inside it, `pre_request` (from the
  span's start to the request: the idle baseline and the warm-up), `request`, and `post_request` (from the
  request's end: the idle drift sentinel); without one, the whole span is one phase, `span`. For each phase the
  flag records: the SMC reads that belong to it (`smc_reads_in_force`), how many are negative
  (`smc_reads_negative`) and how many are below −200 mA (`smc_reads_below`), the minimum B0AC, the held time below
  −200 mA (`smc_duration_below_s`), and, without SMC coverage only, the in-force publications taken before the
  phase ends whose InstantAmperage or Amperage is negative (`registry_publications_negative`); also the
  discharge-accumulator intervals beyond the limit that overlap the phase (`accumulator_intervals_over_limit`). A
  phase is **assisted** when at least one of three of these counts is nonzero: `smc_reads_negative`,
  `registry_publications_negative` or `accumulator_intervals_over_limit`. (`smc_reads_in_force` is nonzero for every
  phase the SMC reads cover, and decides nothing; revision 10 listed it among the deciding counts.) The member
  carries `battery.assist` when the deciding phase (`request`, or `span`) has a negative SMC read, or, without SMC
  coverage only, any of the other evidence; it carries `battery.assist_outside_request` when only other phases
  were assisted, which decides nothing (ruling item 5). `battery.assist` is the marker of the **battery-assist
  sensitivity line** (analysis plan §8.1): every reported cell is printed as a pair of values, one over all kept
  units and one over the kept units less every unit that holds a member carrying this flag. With SMC coverage the
  1 s reads locate the discharge, so an accumulator interval (about 60 s long) that overlaps the request without a
  negative read in it is reported in that phase and does not decide. The discharged energy of each phase, the sum
  over its negative reads of held time (clipped to the phase) × (−B0AC × B0AV), goes to restricted custody
  (`withheld/battery-assist.json`) with the other machine energies (§8); the counts, minimum and durations are
  structure. Battery energy is never added to or subtracted from a rail energy. A member that is also
  `battery.unmeasured` because a publication in force did not read the state keeps its disclosure, marked
  `observed.state_unread`.
- `battery.accumulator_activity` (DISCLOSE): an accumulator sign with at least one tick on an in-force interval and
  a mean at or below the limit. Every archived calibration capture shows 7–32 discharge ticks at −122 to −151 mW
  while InstantAmperage read 0.
- `battery.accumulator_unavailable` (DISCLOSE): the accumulator rule could not run on an interval, for one of four
  reasons: a field not read at both publications; a tick counter that went backward; an accumulated value that
  changed while its tick counter did not (revision 10 left this one out); or no voltage at either publication.
  Also, with SMC coverage, a gap of more than 120 s between registry publications, over which only the accumulator
  test goes unevaluated, and a sign-inconsistent discharge accumulator (above).

*Accumulator units* (lane L1, 2026-10-05, on 66 archived publications and a live read): each `Accumulated*` field
adds its instantaneous value in mW once per tick (about 1.01 s), each `*AccumulatorCount` counts ticks, and battery
power is split by sign into a charge accumulator (`AccumulatedBatteryPower` / `BatteryPowerAccumulatorCount`) and a
discharge accumulator (`AccumulatedBatteryDischarge` / `BatteryDischargeAccumulatorCount`); the split was proven by
an exact identity on all 65 intervals. So Δ(accumulated) ÷ Δ(count) is the mean power in mW over the ticks on which
that sign occurred, and the registered scale is 0.001 W per unit. *Positive control:* between the 2026-09-25 20:47
and 2026-10-01 06:17 publications the discharge accumulator gained 15,043 ticks at a mean of −5,415 mW; the registry
reading inside that interval was −447 mA at 12,180 mV = −5,444 mW; they agree within 0.6%.

*Worked example (synthetic).* A member's measured request runs from 0 to 5 s, with good, fresh B0AC reads at 0, 1, 2,
3 and 4 s of −865, −1,200, −400, −150 and 0 mA, the next read at 5 s, B0AV 12,180 mV, and ExternalConnected Yes and
IsCharging No throughout. Each read holds 1 s inside the request; the read at 5 s belongs to `post_request`. In the
`request` phase: 5 reads belong, 4 are negative, 3 are below −200 mA, the minimum is −1,200 mA, and 3 s are held
below −200 mA. The discharged powers are 10.54, 14.62, 4.87 and 1.83 W, so the discharged energy is
(0.865 + 1.200 + 0.400 + 0.150) A × 12.18 V × 1 s = 31.85 J (to `withheld/`). The member is kept and carries
`battery.assist`; the −150 mA read alone would have made it so. Had the only negative read fallen in the warm-up, the
member would carry `battery.assist_outside_request` and stay in both values of the sensitivity pair. Had the read
at 3 s been +450 mA instead of −150 mA, the member would be removed by `battery.member_span` (rule 1), and the
assist would still be computed, because a current read does not skip it: the flag is still `battery.assist`, and
the discharged energy of the three remaining negative reads, (0.865 + 1.200 + 0.400) A × 12.18 V × 1 s = 30.02 J,
is still written to `withheld/`. Had one registry poll in the span read IsCharging Yes, the member would be removed
by `battery.member_span` (rule 2) and no assist would be computed. If between two in-force publications the charge
accumulator gained 40 ticks totalling +216,000 mW·ticks, its mean is +5,400 mW, above 200 mA × 12.18 V = 2,436 mW,
and the member is removed by `battery.accumulator_excursion`. The same numbers with a negative sign on the
discharge accumulator remove nothing: with SMC coverage the interval is reported in each phase it overlaps, and
only a negative 1 s read in the request decides the marker.

**Thermal.** `thermal.os_level_nonzero`: any in-force 5 s sample of the OS level is nonzero (in force as for the
battery). `thermal.powermetrics_pressure_elevated`: the member's own records show thermal pressure
(`environment_admission.thermal_pressure_elevated_in_window`, unchanged). A gap in the OS-level samples
(`thermal.unmeasured`) is disclosed only, because the member's own records still carry thermal pressure.

**Contention.** Both contention codes are judged over one span: the member's request span (request start to request
end) when it has one, and otherwise the member's whole span (the hull defined at the top of this section).
`contention.request_overlap`: an outside process (not `kernel_task`) exceeds 0.05 CPU-s/s in a 10 s interval that
overlaps that span. `contention.unmeasured`: part of that span is covered by no interval. A member has no request
span when its `sampling_started` or `sampling_stopped` stamp is missing, and also when both exist but the start is
later than the stop (`harvest.member_spans`; the join passes `request or member_span`). Both codes remove the
member, so for such a member a process above the limit, or a gap in the 10 s intervals, anywhere between the start
of its idle baseline and the end of its idle drift sentinel removes it, where the request-only rule would have
looked at the request alone. *Worked example (synthetic):* a member's span is 100–205 s and its request ran from
180 s to 200 s, but its `sampling_stopped` stamp was not recorded, so it has no request span. A process at
0.09 CPU-s/s in the 10 s interval 120–130 s, before the request, would not touch a member judged on 180–200 s;
this member is judged on its whole span and gets `contention.request_overlap`. (Revision 10 gave only the
request-span rule.) This replaces revision 2's environmental-diagnostic trigger with a member rule.

**Clock.** `clock.step_overlap`: a `clock.step` falls inside the span. A gap in the 1 Hz journal (`clock.unmeasured`)
is disclosed only, because the member's own anchor bound stays authoritative and is computed from its own records.

**Instrument.** `instrument.insufficient_in_window_samples` and `instrument.cadence_ratio_below_threshold`: the
member's own records are too few or too slow for its target phase.

### 6.5 Window exclusions

The window is not claim-usable when any of these fired:

- `pack.identity_mismatch`: the pack's plan tree, any configuration, the prompt pin, the extraction spec (a floor
  pack's `extraction_spec.json`, the file that names the pack's cells, each with its metric and the members that
  feed it; GAMMA has no such file), or a NEG-8 or reference manifest differs from its digest in the sealed
  inventory or the plan tree's own pins, recomputed at harvest from preserved bytes; also
  `lineage.plan_tree_digest_differs`.
- `code.executed_differs_from_sealed`: the executed-file inventory differs from the sealed inventory; or the chain
  script's bytes differ from the SHA-256 recorded in its **sidecar** (the small file written beside the chain
  script that holds its digest); or a window input differs between H_claim and the executed head; or the
  measurement checkout has tracked edits, or untracked files under the executed roots (Python could import them).
  *The head comparison.* The **executed head** is the commit the measurement checkout was at when the window armed;
  the driver records it with the executed-file inventory. A **window input** is a tracked file whose bytes a window
  can read while it is planned, armed or run: every file under `joulewise/`, `scripts/` and `configs/` other than
  the ledger pin and the three seal documents (both classed apart, below), and one
  document, `docs/phase_2/window_runbook.md`, whose pre-calibration screen the plan writer copies into the chain. The
  harvest lists the paths that differ between the two commits (`git diff --name-only` from H_claim to the executed
  head, run in the measurement checkout) and gives each path one class (`harvest.head_change_class`). A changed
  window input raises the flag. Three classes are only recorded, in `derived/code-identity.json`: the calibration
  ledger pin (a pin-only commit, §0.18); the three **seal documents**, which are the sealed inventory, this file and
  the analysis plan; and a path no window reads, such as a test or another document. (The harvest program that is
  pinned before ALPHA-1's harvest, §11 item 4, changes two details of these classes. The recorded paths become a
  named list, so that a path on no list counts as a window input. And a change confined to the directory of
  another of the three packs, which this window never reads, becomes a record; at H_claim it still raises the
  flag.)
  *Why the rule has this form:*
  the sealed inventory names H_claim as its `head`, and a file cannot name the commit that contains it, so the
  filled inventory and the sealed text of this file and of the analysis plan are committed one commit after
  H_claim, in the **seal commit**. Every window therefore runs from the seal commit or from a pin-only commit after
  it, never from H_claim itself (§11, §12). (Revision 11 gave this condition as "the measurement checkout's HEAD is
  neither H_claim nor H_claim plus pin-only commits", which would have removed every window of the block. The
  comparison was changed before H_claim, by the int5 merge `9395cecfb`.) When `git diff` cannot run, the window is
  `code.identity_unmeasured` instead (below). The arm's own collector applies the same classes and also raises the
  flag when the checkout's HEAD does not descend from the commit it is given to compare with. In a window that
  commit is the plan's own `measurement_head` (the field in which a window plan records the measurement checkout's
  HEAD at the time the plan was written), and the install program that sets up the window's launchd job
  (`scripts/install_night_agent.sh`, which runs `joulewise/night_agent_install.py`; the job is built in §0.17)
  refuses unless that field equals the measurement checkout's HEAD. So the arm compares a commit with itself, and
  the comparison that ties a window to H_claim is the harvest's (§11).
  *One more difference, decided at the harvest.* The driver, the hazard modules, the monitor and the arm's
  collectors run from the checkout whose copy of that install program set up the job. The registered procedure
  installs the job from the measurement checkout (§11, §12), so there is one checkout and its files are the
  executed-file inventory. If the job was installed from another checkout, the driver also records that
  checkout's files (`driver_checkout`), and a code file among them that differs from the sealed inventory is a
  difference under this code. The harvest at H_claim only writes the list of such files into
  `derived/code-identity.json`; the flag is raised by the harvest program that an addendum to the seal record
  pins before ALPHA-1's harvest (§11 item 4), and identical bytes in a second checkout stay a record.
- `model.identity_mismatch` (the model, tokenizer or runtime realized at the arm or recorded in any bundle differs
  from the pins of `identity_pins.json`, §4.6 item 3), `model.identity_inconsistent_in_window` (two identities within
  one identity unit), and `model.identity_unpinned` (no pin to compare against, which happens when the measurement
  checkout lacks `identity_pins.json`; the members' recorded hashes still exist, and a harvest that is given the
  pins compares them, so since the seal gate's stage 1 this code is a harvest problem first, like the
  `*.identity_unmeasured` codes below: when it is an attempt's only window-removing code, the attempt is
  re-harvested on the same bytes before any decision to re-arm, §7.2). The first two remove the window even when
  the flag is member-level,
  and that includes a NEG-8 reference or spare that ran another model than the sealed `neg8_reference` pin: the
  window is excluded, not handed to the survivors screen, because the pack that executed differs from the sealed
  one (orchestrator call (ii), 2026-10-07, confirmed by the seal gate at its stage 1; §0.12).
- `*.identity_unmeasured` for pack, code or model: a number-protecting identity check could not run. This is a
  harvest problem first (§7.2).
- `calibration.capture_invalid`, `calibration.capture_battery_pair_failed` (a calibration capture's #421 pair failed,
  other than on discharge alone with the journal confirming it, below), `calibration.bracket_acceptance_failed`
  (evaluated with the acceptance's ledger-cutoff baseline), `calibration.acceptance_mismatch` (the acceptance bytes
  differ from the plan tree's pin), `calibration.session_not_bound` (the bracket session names another plan, window or
  runs root), `calibration.binding_failed`, and `calibration.no_bracket`. The last fires when the window's bracket
  session cannot be found in the ledger or was never finalized (both captures recorded against it, §5.1). That
  covers every chain that did not reach the end of its post calibration: the chain's own three stops, at exit 10
  (the reservation failed), exit 11 (the pre capture failed) and exit 12 (the pre fiducial bound was above the pre
  screen), §5.1; and a chain the driver stopped before its post calibration, on `disk.low`, on the census, on a
  monitor outage or at the deadline. (Revision 10 named only the driver's stops here.)
- `calibration.ledger_snapshot_refused`: the calibration ledger, read up to this window's terminal entry, fails its
  own integrity checks. That means a missing or malformed ledger, a broken digest chain, or the acceptance's cutoff
  entry (the ledger's entry number 376, with its recorded head digest; an entry's number is its **sequence**, its
  position in the append-only ledger) not found in the chain. The bracket's captures and the acceptance's screens
  are authenticated through this ledger. The bracket evaluation reads the same snapshot and refuses with the same
  reasons, so `calibration.bracket_acceptance_failed` fires as well. Classing this code as window-removing
  therefore costs no extra window, and it keeps the window removed even if that propagation changed.
- `calibration.capture_battery_span` and `calibration.capture_battery_unmeasured`: the battery rule of §6.4 applied
  to each calibration capture's span, as to a member's (`harvest._capture_battery_joins`, at `a434e363d`). A capture
  has no request inside it, so its whole span is one deciding phase. `battery.member_span` or
  `battery.accumulator_excursion` over the span gives `calibration.capture_battery_span`. A capture whose #421 pair
  did not pass and whose span the journal cannot stand in for gives `calibration.capture_battery_unmeasured`: no
  capture span, no battery journal, a join that could not run, or `battery.unmeasured` over the span. (A capture
  whose pair passed is not removed for a gap in the journal.) Discharge alone is disclosed:
  `calibration.capture_battery_assist` (DISCLOSE), with the capture's discharged energy in
  `withheld/battery-assist.json`. A capture pair that failed on its endpoint current alone, with every failed endpoint
  reading a negative InstantAmperage from its raw bytes, an SMC-covered span and none of the three excluding battery
  codes, is `calibration.capture_battery_pair_assist` (DISCLOSE) in place of `calibration.capture_battery_pair_failed`
  (the member rule of §6.3, applied to a capture). *Forcing problem for the 1 s reads* (finding 5 of the third
  round of the mock rehearsal, written R3-5 in the code and the records; that "R3" numbers the round and is not
  the fix route R3 of §0.1): when this join read the registry, the monitor stopped right after the chain exited,
  before the registry's next publication, so the post capture's last in-force publication never existed and every
  window got `calibration.capture_battery_unmeasured`. *Mechanism at `a434e363d`:* the join judges the current on
  the 1 s SMC reads, the state-hole rule of §6.4 measures the trailing stretch only to the span's end, and the
  driver stops the monitor no sooner than 5 s after the chain exits (§0.17).
- `calibration.historical_custody_mismatch`: a file of an earlier calibration capture that this window's acceptance
  relies on, re-hashed by the harvest, differs from the SHA-256 its ledger entry recorded (§6.10). A changed capture
  the acceptance does not rely on is `calibration.historical_custody_mismatch_unused` (DISCLOSE).
- `clock.step_overlap_calibration`: a clock step inside a calibration capture.
- `neg8.bound_not_derived` (§5.3) and `neg8.screen_failed`; also `whole_window.verdict_absent`, because the NEG-8
  screen's result is held in the whole-window verdict. The screen runs on the surviving references (§0.12, "The
  screen on the survivors"): a lost reference never removes the window by itself, and a reference whose energy
  cannot be read is lost, not handed to the screen (`energy_unreadable`, §0.12; the stored row's own failure for it
  decides nothing: the harvest's survivor screen decides); fewer than two survivors at an
  endpoint does (`observed.reason` `references_insufficient`, also when the missing references never ran). Lost
  references and a lost midpoint are disclosed (`neg8.reference_lost`, `neg8.midpoint_lost`; on GAMMA a lost
  midpoint also removes the window, §0.12); a corpus member dropped for physics is disclosed
  (`neg8.corpus_member_dropped`, §5.3). *Which references the harvest names* (cold pass 2 N1; Sol delta audit A3).
  The harvest finds the window's references in the verdict's own source manifests, and since A3 it always adds every
  planned reference and spare of the sealed roster as well. Before N1, when the source manifests did not
  authenticate it found no references, so a loss flag on a reference went unseen and the stored screen, which still
  held that reference's energy, stood; before A3, the same happened when the fallback manifests were absent or
  unreadable. Now, when the verdict's sources do not authenticate, the harvest also names references from the claim
  root's campaign manifests as written (`campaign_manifests/*.json`, unauthenticated, used only to name references,
  never for an energy or a passing screen), does not trust the stored bracket's own list of the references it
  dropped, and so sends every known loss to the re-screen, which cannot run on unauthenticated sources:
  `neg8.screen_failed` is emitted, with `observed.reference_source` recording which source named the references.
  (Fable cold pass 4, note N-2, records this as the delta's one widened exclusion: a window whose sources do not
  authenticate and whose writer-dropped reference carries a loss flag used to keep its stored screen and is now
  removed. The bracket's provenance cannot be checked there, so whose energy it holds cannot be known.)
- `whole_window.member_failures_unreadable` (NEG8, NUMBER; orchestrator item P4, at `a434e363d`): the whole-window
  verdict did not pass, and its `member_failures` list is absent or rejected by the verdict's own validator
  (`whole_window._validated_member_failures`). Then no failed member can be named, so
  `member.whole_window_member_failure` (§6.3) cannot remove the members the verdict failed, and keeping every member
  would keep numbers the verdict rejected. A verdict that passed, or a well-formed list (an empty one included), does
  not emit it. An absent verdict file is `whole_window.verdict_absent` instead, and an unparseable one is
  `neg8.screen_failed` (the screen it holds cannot be read) beside `whole_window.verdict_unauthenticated` (DISCLOSE);
  `whole_window.verdict_absent` and `neg8.screen_failed` each remove the window already.
- A failed pre-calibration screen removes the window through `calibration.no_bracket`, above. The catalog's code
  for it, `instrument.precal_screen_failed`, is reserved and never written (§6.2).
- `clock.systematic`. A member's metadata records the outcome of its anchor bound (§0.14) as one status word, its
  **anchor status**: `bounded`, or another word when the bound failed or could not be computed. A calibration
  capture has a sampler stream of its own and records the same word in its evidence file,
  `instrument_evidence.json`. A status is **recorded** when that field holds a value. The harvest takes the anchor
  status of every member of the window and, when the window's bracket session was finalized (§5.1), of each of
  its calibration captures: the pre and the post, so at most two. (A window whose session was not finalized is
  already removed by `calibration.no_bracket`, and only its members are counted.) The flag fires when at least 5
  of those members and captures together have a recorded status and more than half of the recorded ones are not
  `bounded` (`harvest.clock_systematic`, threshold `clock_systematic_min_recorded` = 5, §6.9). A member or
  capture with no status, and a capture whose evidence file cannot be read, is not recorded and is left out of
  both counts; a status word the harvest does not recognise counts as recorded and not bounded. *Worked example
  (synthetic):* a window that lost most of its members has 3 members with a recorded status, all `bounded`, and
  both captures recorded, neither `bounded`: 5 are recorded, 2 are not bounded, 2 is not more than half of 5, no
  flag. With one of the three members also not `bounded`, 3 of 5 are not bounded and the window is removed.
  (Revision 10 counted members only; a calibration capture is not a member, §0.3.)
- `cell.below_minimum` (§6.6) and `roster.no_science_bundles`.
- `roster.duplicate_run_id`: the pack's plan tree launches, or lists, one run id more than once (window level;
  `harvest.roster_dispatch`). *Why it removes the window:* a runs root holds one bundle directory for each run id,
  and the campaign runner skips a run id whose complete bundle already exists. Every launch of that run id after the
  first is therefore never measured, and the roster, which is keyed by run id, cannot show which planned positions
  are missing. (Earlier revisions named this code only in §2; it is one of the catalog's 32 window-removing codes.)
- `records.source_changed_during_harvest`: bytes the harvest reads changed while it read them. Operating-system
  metadata files that no reducer, validator or harvest step reads (`.DS_Store`, `.localized` and AppleDouble `._*`
  files, which Finder writes when a person browses a runs root) are ignored by all three of its comparisons (Opus
  audit F7); any other added, removed or changed file still fires it.

**Two aggregate codes are disclosed, not window-removing:** `whole_window.not_passed` (the stored whole-window verdict
did not pass) and `g3.recompute_failed` (check F5-2 of G3, the desk provenance checker
`scripts/check_window_provenance.py`, which independently recomputes that verdict, did not find a clean pass). The
verdict passes only if every member passed, so both codes fire when a single member failed admission or its
environment guard. Making them window-removing would restore "one aborted member voids the window", which Ed's
2026-10-05 ruling removed. The verdict's checks are not lost: each part acts at its own level through its own code.
(The seal gate confirmed both effects at its stage 1, 2026-10-07, after walking every condition that makes the
verdict other than passed: each has a code of its own in the list below, or is disclosed for the physical reason
the list gives.)

- *The NEG-8 screen* (window level): `neg8.screen_failed`. The harvest emits it from the verdict's NEG-8 bracket:
  a decision other than passed, or any NEG-8 condition (`neg8_bracket_abs_delta_exceeded`, the screen failed on the
  gross energies; `neg8_bracket_idle_sub_abs_delta_exceeded`, it failed on the idle-subtracted energies;
  `neg8_bracket_missing`; `neg8_bracket_reference_invalid`; `neg8_drift_bound_stale`; the bound-underived
  conditions). The exceptions are the harvest's re-screens of §5.3 (the collected-subset bound, a reference lost at
  harvest, a corpus member dropped for physics), whose result decides alone. (Revision 10 printed the first two
  conditions as `neg8_gross_point_drift_exceeded` and `neg8_idle_sub_point_drift_exceeded`. Those are the names of
  the code's constants in lower case; the strings a verdict carries are the two above.)
  `neg8_bracket_reference_invalid` has four causes. Three of them, (a), (c) and (d) below, remove the window
  through `neg8.screen_failed`. The fourth, (b), is a reference whose energy cannot be read, and since the seal
  gate's stage 1 that is a lost reference, not a failed screen (the paragraph after the list of causes).
  Two are found by the evaluator (`whole_window.evaluate_neg8_point_drift`): (a) the
  surviving references fit no accepted shape, which means fewer than two at an endpoint, more than three at an
  endpoint, or more than one at the midpoint (the one accepted shape with fewer than two is the legacy single
  pair, one start and one end reference with no midpoint, and only when no reference was recorded as lost; §0.12);
  (b) a reference the shape requires (start, end, or a midpoint that is present) has a gross energy that is not a
  finite positive point lying between its lower and upper values, or an idle-subtracted energy that is not finite.
  Two are found by the verdict writer (`scripts/run_campaign.py`): (c) a member declared as a NEG-8 reference
  whose declared role and declared position disagree, or whose position is none of start, midpoint and end; (d)
  surviving references whose scientific-configuration digests (the SHA-256 of a member's configuration without its
  run id, test vi of §5.3) are not all present and equal; a reference has no digest when it is not the canonical
  condition or its `config.json` does not reproduce the digest recorded for it. (Revision 10 gave cause (a)
  only.)
  *What happens in case (b)* (seal gate, stage 1, 2026-10-07, its item RF-1). *Forcing problem:* the verdict writer
  hands the evaluator every reference that succeeded and passed the strict check, including one whose summary holds
  no usable request energy. The reducer records a member's request energy with an **envelope**: a lower and an
  upper value, between which that energy stays when the member's power records are shifted in time by as much as
  its timing bounds allow, the anchor bound of §0.14 among them. A reference whose anchor is not `bounded` is one
  case in which the reducer records no envelope. The evaluator then fails the whole screen for that one reference,
  so a window would be removed for an event that costs one unit when it happens to a science member
  (`member.anchor_not_bounded`, §6.3).
  *Rule:* the harvest names such a reference lost, with the reason `energy_unreadable` (§0.12, "Lost references"),
  by the verdict writer's own test of the summary. The test passes a summary that holds a finite gross energy, a
  finite envelope consistent with it, and a finite idle-subtracted energy. It asks whether a usable energy record
  exists; it decides nothing by the energy's value. The re-screen of §5.3 then runs on the surviving references and
  decides alone, and the stored row's `neg8_bracket_reference_invalid` for that reference decides nothing. The
  window is removed only when that re-screen fails or cannot run, which includes fewer than two survivors at an
  endpoint.
  *Worked example (synthetic):* all three start references and the midpoint are sound, and of the three end
  references one has an anchor that is not `bounded`. The stored row reads failed, with
  `neg8_bracket_reference_invalid`. The harvest names that end reference lost (`neg8.reference_lost`, DISCLOSE)
  and re-screens with three start and two end references against bound(3, 2) (§0.12); if that passes, the window
  is kept. *Code state:* this handling is part of the harvest program that an
  addendum to the seal record pins before ALPHA-1's harvest (§11 item 4). The harvest at H_claim does not name the
  loss; it lets the stored failure stand and removes the window, which errs toward removing, and no block-5 window
  is harvested with it. (Revision 11 said that each of the four causes removes the window.)
- *The calibration bracket* (window level): `calibration.bracket_acceptance_failed`, which the harvest evaluates
  itself.
- *Each member's own failures* (member level): `member.whole_window_member_failure` (§6.3), which removes only the
  members the verdict names. In-window thermal pressure and an invalid bundle are carried by their existing member
  codes.
- *The AC adapter's wattage continuity* is disclosed only. The battery rule (§6.4) measures directly whether the
  battery supplied any of the load, which is the way a weaker or reconnected adapter could change a measurement.

### 6.6 Cells, units and the minimum

This amends D-179 ruling 1 and D-078's no-reduced-mean text, as Ed's 2026-10-05 ruling requires (§10).

- **Which units a flag removes.** A removed repeat member removes that repeat. A removed quad member removes its
  whole quad, so the A, B, B, A drift cancellation is kept. In GAMMA a quad with any removed member is dropped from
  its contrast.
- **Minimum.** Every target cell keeps at least 5 of its 10 units in each stratum: floor cells in both the repeat and
  the quad stratum, GAMMA's contrasts in the quad stratum. Otherwise `cell.below_minimum` removes the window. The p42
  cells are not target cells. (Revision 9 said 8; the seal gate set 5, below.)
- **What the reduced cell computes.** The stratified mean, variance and half-width of analysis plan §4, which equal
  D-179's when all 20 units are kept; floors with the small-sample guard of analysis plan §5; contrasts over the kept
  quads (analysis plan §7).
- **Why 5.** The seal gate (stage 1, 2026-10-07) set the minimum where the registered estimators stop producing a
  number, not where their precision falls: `small_sample_guard_factor` (analysis plan §5) is defined for 5 ≤ n < 10
  and undefined below 5, so with fewer than 5 units in a stratum a floor cell has no floor and every contrast judged
  against it is not resolvable. Above 5 a short stratum gives a correct, wider interval, which the doctrine of §6.11
  does not allow to remove a window. The reported-cell half-width grows by the factor t(0.975, n − 1) / t(0.975, 9) ×
  √(10 / n): 1.169 at 8, 1.293 at 7, 1.467 at 6, 1.736 at 5; the floor guard g(n) is 1.134, 1.225, 1.342 and 1.5. The
  kept n is printed beside every cell (analysis plan §8).
- **Planning figure.** If each member is lost independently with probability p, a floor window keeps both target
  cells at or above the minimum m with probability P(m, p) (a repeat is lost with probability p, a quad with
  1 − (1 − p)⁴; the four strata multiply): at p = 1/37 (the idle-admission abort rate of blocks 2 and 3, the only
  measured cause), P = 0.849 at m = 8, 0.971 at 7, 0.996 at 6 and 1.000 at 5; at p = 0.05, 0.508, 0.814, 0.952,
  0.991; at p = 0.08, 0.169, 0.474, 0.767, 0.929. Under revision 2's rule that any aborted member aborts the window
  the figure was (36/37)¹¹⁹ ≈ 0.04. Forty codes remove a member and only one cause has a measured rate. Bursts that
  hit consecutive members make losses cluster within a quad, which this figure ignores.
- **Disclosed beside every cell:** the kept units of each stratum, n_r kept repeats and n_b kept quads (`n_repeats`
  and `n_quads` in the exclusion function's record of the cell), the exclusions by family and their positions in the
  window, and the attempts of the pack with their causes (analysis plan §8).

### 6.7 Roster

*Which bundles count.* The exclusion function (§0.16) is given every bundle directory found in the two runs roots
(a directory that holds a `metadata.json`) and tests each against four conditions, in this order; the first that
holds makes the bundle **ignored** (not used for any member), under the label named:

1. its run id is not in the plan's roster: `roster.not_in_plan`;
2. it is bound to another attempt than this one: `roster.foreign_attempt`;
3. `chain.started` carries a monotonic time stamp and the bundle has no stamp that places it against that moment:
   `roster.creation_unplaced`. The stamp that places a bundle is the start of its member span (§6.4); failing that,
   the earliest monotonic stamp its controller recorded; failing that, the wall time of its run-start event,
   mapped through the wall and monotonic stamps `chain.started` took at one instant;
4. that stamp is earlier than `chain.started`'s: `roster.before_chain_started`.

A bundle that meets none of the four is admissible. A roster member left without an admissible bundle is removed
as `member.bytes_missing`, and one with two admissible bundles as `member.bytes_ambiguous` (§6.3). The ignored
bundles, with their labels, are listed in `derived/exclusions.json` (`bundles_ignored`).

*What the four codes do, against their catalog effect.* The catalog gives all four the effect EXCLUDE_MEMBER. The
label path above never removes a member under one of these four names: the member is removed as
`member.bytes_missing`. A code can remove a member under its own name only when it is also written as a flag, and
only two of the four are (`harvest.roster_checks`):

- `roster.before_chain_started` is emitted on a roster member whose run started before `chain.started` (by wall
  time), and that member is removed under this code. It is the only one of the four that ever removes a member
  under its own name;
- `roster.not_in_plan` is emitted naming a bundle directory whose run id is outside the roster. The flag names no
  roster member, so the exclusion function counts it as unmatched and it removes nothing;
- `roster.foreign_attempt` and `roster.creation_unplaced` are never written as flags; they exist only as labels.
  `roster.foreign_attempt` cannot arise in a harvest: the harvest binds every bundle in a runs root the plan created
  for this attempt to this attempt, gives a bundle in any other root no attempt at all, and an unknown attempt
  matches.

(Revision 10 listed three conditions, without `roster.creation_unplaced`, and did not say which codes act.)

A bundle whose recorded `run_id` (in `metadata.json`) differs from its directory (`roster.run_id_mismatch`) is
removed. The harvest places a bundle in a cell, a unit and a quad position by its directory name. Each planned member
has its own config, which carries its `run_id`, so a bundle filed under another member's directory already fails the
config check (`member.config_not_in_inventory`). This code covers the remaining case: a bundle whose own records
disagree about which member it is. A kept member must have one identity in every record a later program may key on,
or the same energy could be counted under two units or in the wrong quad position. The catalog classes it NUMBER for
that reason, and since audit-fix item 7 the emitter and the test fixture do too (revision 6 recorded the emitter's
REPRESENTATION as a restatement). It costs one unit and should never fire.

### 6.8 Disclosed only

All REPRESENTATION flags: lineage formalities other than the configuration bytes (`lineage.*` except the
plan-tree digest), the pin ledger, missing or malformed monitor journals, missing arm or terminal records,
collector failures; the OFF action's output (`network_time.off_output`). (Earlier revisions also listed here
receipts, attempt history, provenance digests, naming and notices, the time-server offset, and monitor probes
falling inside phases. Their codes are DISCLOSE in the catalog, but no program writes them: with
`battery.accumulator_diagnostic` they are eight of the nine reserved codes of §6.2 and cannot fire.) Also
disclosed only: a missing #421 per-capture pair
(`battery.capture_pair_missing_covered` when the continuous journal covers the span; `battery.capture_pair_missing`
otherwise, beside the `battery.unmeasured` that then removes the member); `battery.accumulator_unavailable` (the
accumulator rule could not run on an interval; the publication rule still applies); clock steps and frequency
changes outside any span; `disk.low` (its effect arrives through `calibration.no_bracket`); the desk's ledger
readiness checks before an arm (`calibration.ledger_not_ready`, `calibration.ledger_readiness_unmeasured`); the G10
result; the s1-structural diagnostics; the battery-temperature diagnostic of §0.6 (`thermal.stage_battery_rise`,
`thermal.battery_temperature_unmeasured`), reported beside the window's NEG-8 result; battery assist
(`battery.assist`, `battery.assist_outside_request`, §6.4; `calibration.capture_battery_assist`, §6.5), the #421
pairs that failed on discharge alone (`battery.capture_pair_assist`, §6.3; `calibration.capture_battery_pair_assist`,
§6.5) and the SMC fallback (`battery.smc_unavailable`); clock samples too skewed to use (`clock.unmeasured`,
`read_skew`, §4.2); the whole-machine meter's flags (`meter.*`, §5.8); the yield flags (§5.7); G3 not applying to a
floor pack (`g3.not_applicable`); the driver's pre-launch lineage check (`records.lineage_prelaunch_mismatch`,
§0.17); a member's error output not copied into the stage log (`member.stderr_uncopied`, §6.3); a changed historical
capture the acceptance does not rely on, and a historical file that could not be read
(`calibration.historical_custody_mismatch_unused`, `calibration.historical_custody_unmeasured`, §6.10); an arm
probe of the clock, battery, thermal, contention or disk hazard that returned UNMEASURED (`<module>.arm_unmeasured`,
§4.1); an in-window census that could not be read (`census.unmeasured`, §4.5); a re-derived powermetrics digest
(`instrument.binary_identity_rederived`, §6.3); lost NEG-8 references, a lost midpoint and a corpus member dropped for
physics (`neg8.reference_lost`, `neg8.midpoint_lost`, `neg8.corpus_member_dropped`, §0.12, §5.3; on GAMMA
`neg8.midpoint_lost` also makes the attempt not claim-usable, §0.16, §7.2); a flag line that failed validation,
a writer's stand-in line rebuilt into its flag, and an operator log that could not be read (`records.malformed_flag`,
`records.flag_unbuilt`, `records.operator_log_unreadable`, §6.2, §6.10); a monitor restart (`monitor.restarted`) and a
recorded monitor or meter group the dead-man left unsignalled (`monitor.orphan_unverified`, §5.4); and the records of
§6.10.

`contention.kernel_task_share` stays in the catalog but cannot fire today: an unprivileged `ps` never lists
`kernel_task` (process id 0; checked 2026-10-05), so neither the arm nor the monitor sees its CPU time by name. Its
work is inside the host's total busy time, which the monitor journals every 10 s and nothing judges in the window
(§4.2, Contention). It is to be removed in the prune after block 5 (orchestrator ruling of 2026-10-06).
`monitor.restarted` is now written (audit-fix item 8): the hazard monitor's supervisor calls the driver on each
restart, and the driver writes one window flag with the restart's process id, start count and previous exit, its
interval the gap between the old monitor's death and the new one's start. The gap also shows as the modules'
unmeasured flags over the member spans it touched, and a monitor that keeps dying reaches the flags as
`monitor.crash_loop` and `monitor.outage` (§5.1). (At `a434e363d` no production path wrote it.) The meter's restarts
stay `meter.supervision_fault` (§5.8).

### 6.9 Harvest thresholds

The harvest reads its own copy of the in-window thresholds. The window plan carries this block as well; its values
are the same physical limits as §4.3 under the harvest's names.

```json
{
  "battery_limit_ma": 200,
  "battery_unmeasured_gap_s": 120.0,
  "battery_accumulator_watts_per_unit": 0.001,
  "thermal_unmeasured_gap_s": 15.0,
  "contention_cpu_s_per_s": 0.05,
  "clock_step_ns": 1000000,
  "clock_unmeasured_gap_s": 3.0,
  "disk_low_bytes": 10737418240,
  "clock_systematic_min_recorded": 5
}
```

### 6.10 Checks the writers record instead of refusing

Ed's ruling of 2026-10-05 (§0, revision 3) turned every check that is not a physical hazard into a flag. Inside the
protected measurement code (the controller, the campaign runner, the calibration writer and the bracket reservation)
that was done by the core-prune lanes (`/Users/edr/night-archive/gate-prune/core-prune/DESIGN.md` §3) and the round-2
lanes, and finished by the refusal census and its triage, all at `a434e363d`. Each row below says what used to
refuse, what is recorded now, and what still decides the claim. A refusal that protects integrity stays a refusal;
those are named, and §6.11 says how the whole list is enforced.

**The controller, once per member** (`joulewise/controller.py`):

| What used to refuse the member | Recorded now | What decides the claim |
|---|---|---|
| the pre-slot calibration's #421 battery pair did not pass (A1) | `calibration.capture_battery_pair_unverified` (DISCLOSE) | the harvest re-derives the pair from the same bytes (`calibration.capture_battery_pair_failed`) and joins the battery journal over the capture (§6.5) |
| `git` or the ledger's shape could not be read per member (A5) | `records.pin_ledger` (DISCLOSE) | the harvest's ledger integrity check (`calibration.ledger_snapshot_refused`, EXCLUDE_WINDOW) |
| the pack's directory was not at `<repo>/configs/campaigns/<pack>`, so the repository could not be found from the path (refusal census) | the repository is found with one `git` lookup and `records.pin_ledger` (DISCLOSE, `kind` `pack_root_layout`) is recorded | the session, slot, plan, custody and digest checks that bind the member to the ledger still refuse |
| the member's environment guard failed (A11) | a measured quiet-state violation (display awake, screensaver, Low Power Mode): `env.member_quiet_state_violated` (EXCLUDE_MEMBER); an unknown field, or AC or thermal failures that the hazard journals measure directly: `env.member_guard_flagged` (DISCLOSE) | the reducer's environment barrier is unchanged, so a member whose own environment evaluation failed is still removed through `member.target_phase_precheck_failed` |
| the guard's observation collector raised an exception (refusal-census triage c; `controller._hazard_guard_observation`) | that one observation is recorded as unmeasured (every reading null, `collector_error` naming the exception) and the member runs; the finding `collector_raised` is added to `env.member_guard_flagged` (DISCLOSE), at idle admission and, since audit-fix item 6, after the run (phase `post_run`) | the other observations' readings still apply. A post-run observation recorded this way is no longer missing evidence to the whole-window verdict (`environment_admission.post_run_observation_collector_raised`, read only on the verdict path by the orchestrator's ruling), but the pinned reducer's environment barrier still marks it `environment_admission_failed` on the member's target prechecks, so the member is removed by `member.target_phase_precheck_failed` (§6.3): an unmeasured post-run environment cannot show the member clean |
| the power-policy label or the runtime power observation differed from the calibration's (A14) | `calibration.power_policy_unverified` (DISCLOSE) | a label is not a measurement; the battery and thermal hazards measure the power state |
| the `powermetrics` binary's digest could not be read (A14) | `instrument.binary_identity_unmeasured` (EXCLUDE_MEMBER), superseded by `instrument.binary_identity_rederived` (DISCLOSE) when the harvest, on the member's collection boot, hashes the recorded executable and finds the calibrated digest (§6.3) | a present, different digest still refuses (the binary must be the calibrated one) |
| sampler or runtime processes survived the member's teardown (A17) | `teardown.survivors` (DISCLOSE) | the next members' contention is measured directly (`contention.request_overlap`) |
| idle admission's telemetry was missing or short (A18) | `member.idle_admission_telemetry_missing` (EXCLUDE_MEMBER) | a failed threshold (CPU busy, power, GPU) still retries and aborts as before |
| the window calibration verdict did not match (J1, §5.1) | `calibration.refit_cache_miss` (DISCLOSE); the member refits | the harvest's own refit from the raw bytes |
| the auxiliary-config comparison raised an exception, and the exception was swallowed. An **auxiliary** member is one whose config is not among the pack's own science configs: a NEG-8 corpus member, a reference, or one of GAMMA's diagnostic references. Before such a member runs, the controller compares its config with the plan tree's pinned list of external members and with their stage's runs root (`controller._g2b_auxiliary_config_matches`) | the member **still refuses**, before its bundle is created: when the calibration evidence is of revision five or carries the #421 battery record, and no provenance was authenticated for it, the controller raises "revision_five evidence cannot be attached as instrument calibration (auxiliary member match raised <error>)". Only the record is new: `records.auxiliary_match_raised` (DISCLOSE) carries the exception text, and the refusal message names it | the refusal itself: the member leaves no bundle, so it is lost like any other member that did not run (`member.bytes_missing`; a corpus member by §5.3, a reference by §0.12). (Revision 10 listed this row as a refusal turned into a record, decided by "the pack-identity check at harvest"; the refusal was never removed.) |

**The campaign runner, once per stage or member** (`scripts/run_campaign.py`): a member whose child left no readable
metadata (A4), a stale `campaign.lock` reclaimed under a directory lock after proving its owner dead (A9, V3), the
campaign-log identity check (A13), a failed record write before or inside the member loop (A16), and a failed stage
verdict (A20) are each `campaign.runner_record_flagged` (DISCLOSE) with a `kind`; a lock owned by a live process, or
any lock-ownership error, still ends the stage. Two kinds were added by the Opus audit (F4, 2026-10-07). The runner
publishes each running campaign in an **active-campaign registry** (`joulewise/measurement_liveness.py`
`publish_campaign`: its process id and start time, so that a later campaign can tell a live owner from a dead one);
when the `ps` identity probe returns UNKNOWN, the entry is published with no start time and the stage runs, recorded as
`kind: registry_start_time_unavailable` (it used to end the stage). An empty or unparseable `campaign.lock` (a lock
file whose writer died before writing it) is reclaimed only when three facts are proven: the file is at least 30 s
old, `lsof` shows no process holding it open (its content can be written only through its creator's open file, so
with no holder nothing can complete it), and no active-campaign entry naming the runs root belongs to a live process
or one whose state is unknown; it is then reclaimed under the existing directory lock and recorded as
`kind: torn_lock_cleared` with that evidence. Any probe that fails keeps the lock. A stage environment preflight that raised or did not admit (A10) is
`env.stage_preflight_not_admitted` (DISCLOSE); its members carry the failed evaluation, which the reducer's barrier
judges. A cooldown whose result is unknown (A2, A19) is `cooldown.result_unknown` (DISCLOSE) and the member runs; its
claim status is `member.cooldown_evidence_unverified` (EXCLUDE_MEMBER) unless the cooldown was measured.

**The cooldown fallback reference** (PLAN2 s2-05). *Forcing problem:* a cooldown is judged against the previous
member's idle baseline (§0.6). When none is eligible (the stage's first measured member after a refused one, or a
reference that failed its own quiet checks), revision 4's runner either blocked the next member or ran it with an
unknown cooldown, which the harvest then removes. *Mechanism:* the runner measures the cooldown anyway, against a
fallback reference. One kind of fallback is a **frozen anchor**: an idle baseline that an earlier stage of the
window stored once as a cooldown reference (under `cooldown_anchor` in its campaign manifest, the record the
campaign runner writes for a stage under `campaign_manifests/`), marked `immutable_after_freeze` and never
updated. A frozen anchor is eligible when it carries that mark, was stored under the same campaign policy, by
SHA-256, as this stage runs under, comes from a member whose own reference checks passed with their provenance
recorded, and its idle window was not suspect (`joulewise/cooldown_anchor.py` `cooldown_anchor_eligibility`). The
runner takes the first reference available in this order: the last eligible idle baseline of this session; else
an eligible frozen anchor anywhere in the window, the NEG-8 start reference's first; else a **self-referenced**
test that needs no outside reference: two adjacent windows of max(the policy's window, 30 s), each with the
policy's coverage, the newest window's mean power the reference, and the window before it within min(the policy's
tolerance, 10%) of it, with thermal state nominal and the policy's 300 s cap. The self-referenced test never runs
looser than the cooldown-v2 defaults (30 s, 10%), because without an idle level a 5 s window cannot tell a slow
decay from a plateau. The result is an ordinary cooldown record with its raw trace, verified at harvest like any
other, and `campaign.runner_record_flagged` (`kind: cooldown_fallback_reference`, DISCLOSE) names the reference
used. *Worked example (synthetic):* no eligible baseline exists; the newest 30 s window averages 0.040 W and the
one before it 0.043 W, 7.5% apart, at most 10%: the next member starts. Had the earlier window averaged 0.050 W
(25% apart), power would still be falling and the test would keep waiting, up to 300 s.

**The calibration writer and the bracket reservation** (`scripts/validate_powermetrics_fiducial.py`,
`scripts/reserve_calibration_window_bracket.py`, `joulewise/calibration_ledger.py`). Every row is
`calibration.writer_record_flagged` (DISCLOSE) with the `kind` named:

- `desk_identity_differs` (A6-R1): the reservation now measures the OS build, the machine model and the T1 bindings
  (the digest of the sampler binary and the MLX version a capture is bound to) itself, instead of copying a
  prediction typed at the desk, and records any difference. The prediction is two files prepared at the desk and
  handed to the reservation: the **desk identity epoch** (`--identity-epoch-json`: the OS build, the machine model,
  a power-policy label, the sampling interval, the estimator revision and the pulse protocol's id) and the **desk
  T1 bindings** (`--t1-bindings-json`: the same fields, with the digest of the sampler binary, the MLX version, the
  anchor method's version and the digest of the pulse protocol file). The writer's own comparison of two
  measurements stays a refusal: within one boot minutes apart, a difference is a real identity change.
- `historical_custody_unverified` (A6-R2/R3): the writer and the reservation skip the committed-pin check and the
  re-hash of every historical calibration file. *Forcing problem:* the reservation re-verified 190 historical files,
  3.33 GB, in iCloud Drive with optimize-storage on, under a 120 s budget; an evicted file would time out and stop the
  chain at exit 10 with nothing collected (PLAN2 row 4; other files in the same backup tree were already evicted). This window's own capture files are still verified at
  finalization, under their own deadline.
- `head_pin_stale` (PLAN2 row 4): the committed ledger pin lags the ledger's physical tail. The reservation appends
  the session to the physical tail and records how the pin relates to it, instead of refusing; a stale pin is cured by
  the next pin-only commit (§4.6 item 6).
- `session_custody_unverified`: the writer's check of this session's own custody could not complete inside its
  deadline; a session-custody worker still running past it refuses (`session_custody_worker_not_quiescent`).
- `display_sleep_action_failed` (A7): `pmset displaysleepnow` failed; the capture's own fit and the pre screen judge
  any effect.
- `binding_read_substituted` (A8): the sampler's header lacked the machine model or OS build, and the values the
  writer read at its start were used.
- `desk_identity_unreadable` (audit A6, 2026-10-07): on the `HAZARD_PACK` path a desk identity file the reservation
  reads was missing or malformed. The reservation used to exit 2 (`calibration_reservation_json_invalid`) and the
  chain stopped at the reservation before any measurement; now it measures the identity itself with an empty desk
  fallback and records the file, path and reason. The power-policy label, which cannot be measured, is the desk
  identity epoch's when that file gives one, else the desk T1 bindings', else the plan's constant `ac_high_power`.
  A live read that fails with no desk fallback still refuses.

The executed estimator code differing from the acceptance's (A15) is not a record: it is
`code.executed_differs_from_sealed` (EXCLUDE_WINDOW). The ledger's integrity refusals stay: a malformed ledger, a
broken hash chain, a rollback, an identity conflict, a held lease, an unfinished recovery. The **lease** is the
ledger's writer lock: a kernel file lock (`flock`) on the ledger's lock file that one writer holds for its whole
run, so that two writers never append at once; a writer that finds it held by another refuses
(`calibration_ledger.CalibrationWriterLease`, refusal `LIVE_WRITER_CONTENTION`). An **unfinished recovery** is a
ledger that ends in bytes that are not a complete entry, or that records an append begun and not completed
(`calibration_ledger_recovery_required`); nothing may be appended until those bytes are repaired.

**Historical custody is re-verified at the harvest, once** (`calibration_ledger.historical_custody_report`, lane
P2-VPF; called by `harvest._Harvest.historical_custody`, at `a434e363d`; the report goes to
`derived/historical-custody.json`). Because the slots skip the historical re-hash, the harvest re-hashes every
historical calibration file the archived ledger records, once per window, against the SHA-256 in its ledger entry.
This window's own bracket session is left out, because its files are verified at finalization. Each ledger row gets
one outcome: **changed** (a present file's bytes differ from its recorded digest, or a row that was not abandoned
records no file hashes), **unreadable** (a present file could not be read), **absent** (a file is missing, for
example evicted from local iCloud storage, while its present siblings match), **absent_or_unreachable** (the capture
directory is missing, or did not answer a 2 s probe), or **verified**. A digest mismatch is never downgraded to an
absence.

*Which captures the window relies on* (refusal-census triage d, 2026-10-07). *Forcing problem:* the first version of
this pass removed the window for a changed file in any earlier capture, including another window's bracket, which no
number of this window uses, so the removal protected no number of the window it removed. *Mechanism:* the
harvest reads the window's acceptance (§0.11) and takes the attempt ids of the captures it was derived from (its
`derivation_corpus` members, which set the pre screen and the bracket screen) and of the captures it judged before
issuance (its `prior_observation_set`). On the real acceptance these are 110 captures: the 110 of its prior
observation set, among which are the 24 of its derivation corpus (counted by this author from the acceptance
file). The integrator's triage reports that they are every capture the ledger holds up to its entry number 376,
the acceptance's cutoff (`FROZEN_HEAD.md`: "all 110 governed rows up to sequence 376"; an entry's number is its
sequence, §6.5, and the triage's governed rows are the ledger's capture entries, each of which records the
SHA-256 of its capture's files). Then:

- **changed, and relied on:** `calibration.historical_custody_mismatch` (EXCLUDE_WINDOW, `observed.scope`
  `acceptance_relied`). The acceptance's screens are numbers computed from those captures; changed bytes mean the
  evidence the screens rest on is not the evidence that was judged. If the acceptance cannot be read, nothing can be
  scoped, and every changed row counts (`observed.scope` `acceptance_unreadable`).
- **changed, not relied on:** `calibration.historical_custody_mismatch_unused` (DISCLOSE; `observed.attempt_ids`
  names the captures). Both codes can fire in one pass.
- **no row changed, but some row is unreadable, absent or unreachable, the ledger could not be read, or no row was
  verified:** `calibration.historical_custody_unmeasured` (DISCLOSE). Its `observed.evicted` counts captures, not
  files: one for each ledger capture whose outcome is **absent**, however many of its files are missing. A capture
  with a missing file and an unreadable one (outcome unreadable), or with its whole directory missing (outcome
  absent_or_unreachable), is not in that count; `observed.unmeasured` counts every capture that could not be
  checked, and each capture's per-file states are in its entry's `artifacts` map in
  `derived/historical-custody.json`. (Revision 10 said `observed.evicted` "counts the evicted files".) A
  file that cannot be read is not evidence of a change, and the ledger's hash chain and pin are still checked. Its
  class is NUMBER, as the emitter gives it (revision 5 had restated it as REPRESENTATION); only its effect is
  DISCLOSE.

*Worked example (synthetic):* of 190 historical files, 189 re-hash to their recorded digests and one cannot be read
because iCloud evicted it: the window is kept, `calibration.historical_custody_unmeasured` lists it. Had that file
read back with a different digest, the window would be removed if the file belongs to a capture in the acceptance's
derivation corpus or prior observations, and kept with `calibration.historical_custody_mismatch_unused` if it belongs
to, say, an earlier window's bracket.

**Recovering flags a writer could not write** (core-prune N8). A core writer that cannot write its flag file prints
the whole flag behind a fixed marker (`JOULEWISE_UNWRITTEN_FLAG `) on its error output. The harvest scans the stage
logs (`operator-logs/*.log`), each member's own error-output file (`operator-logs/member-stderr/*.stderr`), the planned
operator-log root and the desk transcript for the marker, and absorbs each flag as if written
(`harvest._unwritten_core_flags`, at `fe28e5a0c`, unchanged since `43ac12d0c`). Three outcomes (audit-fix 2, Opus audit F2): a writer's designed
stand-in line (`{code, level, run_id, [observed,] unbuilt}`, printed by `joulewise.flags.core.emit` or the chain's
flag writer when the flag could not be built or written) is rebuilt as the flag it names, so that flag's catalog
effect applies and no exclusion is lost, and `records.flag_unbuilt` (DISCLOSE) records the rebuild (a stage or quad
fact, or a member fact with no run id, is applied to the whole window); any other marker line that is not a valid
flag is `records.malformed_flag` under the rule of §6.2; and a log or log directory that cannot be read is
`records.operator_log_unreadable` (DISCLOSE). Revision 6's "never classified, so it blocks the release event" is
withdrawn: none of these blocks the release event.

### 6.11 Which refusals remain, and how that is enforced

*The rule* (Ed, 2026-10-05; `CLAUDE.local.md`, "Physics refuses; everything else is a flag"): a refusal, a stop or
an exclusion is allowed for exactly two reasons. **PHYSICS**: a physical hazard, measured directly, would corrupt the
energy (§4.2, §6.4). **NUMBER_INTEGRITY**: a number would be wrong or could not be attributed to what it claims to
measure (an identity, a calibration, a screen, a roster position). Anything else (a receipt's wording, a record's
format, a missing log) is a flag that removes nothing.

*How the code enforces it* (refusal census, lane `6fab71954`, merged at `a434e363d`, kept current by every lane
since). The file `configs/gates/hazard_refusals.json` (schema `joulewise.hazard_refusals.v1`) lists every **refusal
site**: each place in the 93 files it scans (91 Python files the hazard path imports or runs, `scripts/backup_runs.sh`,
and the runbook
whose shell functions the chain copies) where the code raises or asserts, exits nonzero, returns a nonzero code or a
blocking status, writes a refusal reason, kills a process, or (in the chain's shell text) stops the chain. Each site
carries a **category**:

| Category | Meaning (the file's own definition) | Entries | Sites |
|---|---|---|---|
| PHYSICS | refuses on a measured physical hazard; names the quantity | 30 | 31 |
| NUMBER_INTEGRITY | refuses because a number would be wrong or unattributable; names the number | 35 | 58 |
| INTERNAL | never stops collection or excludes a window (for example an import-time constant check); names why | 91 | 117 |
| BASELINE | present at the sweep base `e6b6a0ce` and unchanged; not individually reviewed; frozen | 2,593 | 3,663 |
| DEFERRED_REPRESENTATION | a representation refusal another lane is converting | 0 | 0 |

(Counts computed by this author from the file at `fe28e5a0c`, which is byte-identical to the file at `43ac12d0c`:
entries are list items, sites the sum of their `count` fields; 2,749 entries and 3,869 sites in all. From `d3c107f2f` one entry changed category: the
publisher's raise for an unusable pack inventory, retyped `PackInventoryUnusableError` (§0.17), moved from BASELINE
to NUMBER_INTEGRITY. At `d3c107f2f` the counts were 30/31, 34/57, 91/117 and 2,594/3,664. At `a434e363d` they
were 27/28, 33/56, 90/116 and 2,598/3,668, 2,748 entries and 3,868 sites. Comparing the files at `a434e363d` and
`d3c107f2f` entry by entry: three BASELINE entries were
reviewed into PHYSICS (the arm's dwell refusal, its instrument refusal and the driver's GO-without-PASS reason, §4.1);
two entries were removed (the in-window census stop on unreadable censuses, PHYSICS, §4.5, and the raise on an
unknown registry start identity, BASELINE, §6.10); and three were added: the refusal of an unusable pack inventory,
`night_refused_pack_inventory_unusable`, NUMBER_INTEGRITY (§0.17), the 1,500 s cap on G10's supervised wait, PHYSICS
(a hung process, §5.4), and the spare-retry helper's exit on an unknown mode, INTERNAL. The four rows of the table
are the same at the int5 head `9395cecfb` and at `a0920cb8c`, the head of the lane named below, recomputed by this
author the same way.) The file
also lists every flag code the catalogs mark EXCLUDE_WINDOW, and every pack-scoped window reason (§0.16), under
`window_exclusions` (33 entries: 29 NUMBER_INTEGRITY, 4 PHYSICS, none BASELINE; `whole_window.verdict_absent` was
relabelled from BASELINE to NUMBER_INTEGRITY), and every EXCLUDE_MEMBER code under `member_exclusions` (40: 20
NUMBER_INTEGRITY, 16 PHYSICS, 4 BASELINE). The 33 window entries and the 36 PHYSICS and NUMBER_INTEGRITY member
entries each carry a `protects` text that names the quantity or number protected. The four BASELINE member entries
do not: `member.admission_aborted`, `member.cooldown_evidence_unverified`, `member.strict_validation_failed` and
`member.target_phase_precheck_failed` carry only a `note`. Two notes say "not reviewed by the census"; the other
two defer the review to `LANE_BARRIER`, the lane the core-prune design names for reviewing the reducer's
environment barrier (§6.3). The test admits these four by name (below). All four are live member exclusions
(§6.3), so they are a standing exception to the rule above: four exclusions whose reason has not been reviewed
into one of the two classes. (Revision 10 said every listed exclusion names what it protects.) The 33 are the
catalog's 32 window-removing codes and the one pack-scoped reason, `neg8.midpoint_lost_primary` (NUMBER_INTEGRITY,
pack GAMMA).

*What the seal gate changed in this list* (stage 1, 2026-10-07). Three entries of `window_exclusions` changed and
no refusal site did. The changes are commits `9980d6296` and `7b88e835a` of the int5 lane
`lane/2026-10-07-seal-rulings`, which lands in the integration before H_claim together with the catalog's new
minimum; the counts above are this author's, from the file at that lane's head `a0920cb8c`.

- `cell.below_minimum` used to give "statistical power of the reported number" as what it protects. Precision is
  neither of the two reasons of the rule above, which is why the gate moved the minimum to the point where a number
  stops existing (§6.6). The entry now reads: "fewer than 5 kept units in a stratum of a target cell: the
  registered floor estimator's guard (small_sample_guard_factor) is undefined below 5, so the cell's floor and
  every contrast judged against it have no number".
- `neg8.midpoint_lost_primary` used to say that GAMMA's contrasts then carry a drift allowance "with no
  interior-excursion evidence". That overstated the case: GAMMA records two diagnostic interior references, which
  by rule the allowance does not read (§0.12). The entry now reads: "GAMMA's primary contrasts' deterministic bound
  D carries a drift allowance whose interior spread was not measured when the arm-boundary midpoint reference is
  lost (the two diagnostic interior references enter neither the screen nor the allowance by rule); a decision
  rests on D". D is the total of a contrast's recorded deterministic bounds, by which its interval is widened
  before the contrast's direction is decided (analysis plan §7.1 step 5).
- `g3.recompute_failed` left the list. The list had held it, as a 34th entry, only because the test fixture
  catalog (`tests/fixtures/b5_harvest/flag_catalog.json`) still marked that code EXCLUDE_WINDOW while this catalog
  makes it DISCLOSE (§6.5). The gate confirmed DISCLOSE, the fixture now says DISCLOSE as well, and a test holds the
  fixture equal to this catalog, in family, class, effect and blinding, for every code both files list. (Revision
  11 gave 34 entries, 30 of them NUMBER_INTEGRITY, and named this one disagreement.)

The test `tests/hazards/test_refusal_allowlist.py` scans those modules' syntax trees on every run and fails when:
a refusal site appears that the file does not list, or a listed site changes its count or its guarding conditions;
a non-BASELINE entry does not say in at least 30 characters what it protects; a BASELINE entry is new, moved,
re-guarded or more frequent than in the frozen list `tests/hazards/refusal_baseline_frozen.txt` (whose own SHA-256
the test pins), so BASELINE can only shrink; a module the hazard path imports is neither scanned nor listed as
deliberately unscanned; or an excluding catalog code or a pack-scoped window reason is missing from the file,
carries another category, or is BASELINE outside six named codes (`calibration.ledger_snapshot_refused`, `whole_window.verdict_absent`,
`member.admission_aborted`, `member.cooldown_evidence_unverified`, `member.strict_validation_failed`,
`member.target_phase_precheck_failed`). So a new refusal site cannot enter the hazard path without one of four
classes: PHYSICS or NUMBER_INTEGRITY, saying what it protects; INTERNAL, which by definition stops nothing; or
**DEFERRED_REPRESENTATION**. That fourth class is for a refusal known to protect neither a physical quantity nor a
number, which a named lane (a line of work with its own branch and review) is already converting into a flag: the
test admits it only when the entry names that lane in an `owner` field and still gives a `protects` text of at
least 30 characters. The same holds for a new excluding code, which may be PHYSICS, NUMBER_INTEGRITY or
DEFERRED_REPRESENTATION with an owner, and never BASELINE. The file holds no DEFERRED_REPRESENTATION entry at
`9b0c680ed` (the table's last row), so today every non-BASELINE refusal and exclusion is PHYSICS, NUMBER_INTEGRITY
or INTERNAL. (Revision 10 named three classes; the test admits the fourth.)

*What the scan does not see* (its own docstring): a bare `return False` from an admission predicate, a `continue`
that skips a member, and a new call to an existing raising function. Those are checked by hand in review
(`/Users/edr/night-archive/gate-prune/REVIEW_BRIEF_RULE.md`).

*Seal-time item, closed in revision 7.* The test reads this directory's `flag_catalog.json` once it is in the code
tree, and a test added by audit-fix item 7 already reads it from this design branch. Revision 6 found that the file
did not list `roster.run_id_mismatch`, which this catalog marks EXCLUDE_MEMBER (§6.7). The file now lists it as a
NUMBER_INTEGRITY member exclusion ("the member's records disagree about which member it is"), and every excluding
code of this catalog, including the two malformed-flag exclusions of §6.2, is listed (checked by this author against
revision 7's catalog).

## 7. Verdicts, re-arming and END STATE

### 7.1 Four verdicts per attempt

The harvest opens when the driver's terminal record exists (§5.4), works from an archive copy of the window, and
writes one verdict:

- **COLLECTED:** `night/chain.started` exists, and the stage journal does not show the NO_COLLECTION case below. The
  numbers (into restricted custody) and the flags are emitted whatever the flags say, and the exclusion function
  computes `claim_usable`. If the exclusion function is absent or raises an error, the numbers and the flags still
  stand, `records.collector_failed` (DISCLOSE) is recorded, and `claim_usable` is false with the single reason
  `exclusions.function_unavailable` in the `reasons` list of the function's output (§0.16). (When the function
  could not be called because the harvest itself failed to build its inputs, the same reason is written, and the
  verdict is not COLLECTED but HARVEST_FAULT, below.)
- **NULL:** no chain start: the arm refused, or the driver failed before the chain. `claim_usable` is false, with the
  single reason `window.null`.
- **NO_COLLECTION:** the chain started and its record of stages shows that no collection stage ran to its end. That
  record is the **stage journal**, `night/chain-stages.jsonl`: the chain appends one line to it each time one of its
  stages ends, giving the stage's id, its kind and its return code. (It also writes a line of another kind when it
  stops itself, and one for each stage it skips at the collection deadline, §5.1.) The verdict is NO_COLLECTION when
  the file exists and holds no line of kind `campaign_collection`, the kind of a collection stage that ended. That
  covers every chain that stopped itself at exit 10, 11 or 12, because all three stops come before the first collection
  stage (§5.1), and also a chain that the driver stopped from outside (§5.1) after the first stage had ended and
  before the first collection stage had. Every collector still runs, `chain.stopped_before_collection` is recorded
  (DISCLOSE), and `claim_usable` is false whatever the flags say, because only a COLLECTED window can be
  claim-usable.
  *The case the journal cannot show.* A chain that started and was stopped before its first stage, the bracket
  reservation, had ended has written no journal. The harvest reads a missing journal as no evidence against
  collection, so this window's verdict is COLLECTED and `chain.stopped_before_collection` is not recorded. The
  window is still not claim-usable: its bracket session was never finalized, so `calibration.no_bracket` removes it
  (§6.5), and `collection.zero_yield` (DISCLOSE) records that none of its planned bundles is present.
- **HARVEST_FAULT:** the harvest program failed on bytes that are present. `claim_usable` is false, and the reason
  `harvest.fault` is added to the window's reasons. Cured by R3 and re-harvested from identical bytes into a
  distinct derived directory; never a science outcome.

`window.null`, `exclusions.function_unavailable` and `harvest.fault` are reasons the harvest writes itself. Like the
pack-scoped window reason of §0.16, they are not catalog codes. The harvest's record `harvest.json` carries the
verdict, `claim_usable`, the window's reasons (`exclude_window_reasons`: these three, the window-removing codes that
fired, any pack-scoped reason and `cell.below_minimum`) and the yield counts, and the harvest command prints them.

### 7.2 What happens next

**Who applies these rules.** No program schedules the block. The harvest writes each attempt's verdict,
`claim_usable` and reasons into `harvest.json` (§7.1). The rules of this section, of §7.4 and of §7.6 are then
applied to those records by the lead: in an unattended run, by the magistrate, the headless lead session that the
watchdog launches (§5.7). They are rules a session follows, not code, like the process rule of §7.3, and the written
brief the magistrate is launched with carries them. Wherever this file says "the scheduler", it means the lead
applying these rules. The code holds a function for the first rule below, `first_claim_usable` in
`joulewise/flags/exclusions.py`, which returns the number of a pack's first claim-usable attempt, or nothing while
that attempt still carries an unclassified code; it is tested, and no block-5 program calls it.

- **The analysed window of each pack is its first claim-usable attempt** in arm order. All of a model's cells come
  from that one window, so attempts are never mixed: no member, quad or cell is pooled, topped up or replaced across
  attempts (D-078).
- A pack is re-armed, with a new attempt number, plan, fresh roots and bracket session, until it has a claim-usable
  attempt; then the next pack in the fixed order ALPHA, BETA, GAMMA arms. A pack is never armed again after a
  claim-usable attempt. The scheduler reads only `claim_usable`, never an energy.
- **A GAMMA attempt that lost its midpoint is re-armed** (orchestrator ruling Q11, 2026-10-07; confirmed at the seal
  gate, stage 1, ruling SG-5). *Forcing problem:* GAMMA's window exists for its two primary contrasts, and a lost
  midpoint leaves their drift allowance with no evidence about an excursion inside the window (§0.12). Had the
  attempt counted as claim-usable, the scheduler would have stopped arming GAMMA and the block would have had no
  claim-bearing contrast. *Rule:* on GAMMA, `neg8.midpoint_lost` adds the window reason `neg8.midpoint_lost_primary`
  (§0.16), so the attempt is not claim-usable, both for scheduling and for choosing the analysed window, and GAMMA
  is re-armed. The rule reads only the roster's pack id and the flag's code, never an energy, so re-arming cannot
  select on an outcome. On ALPHA and BETA the flag stays disclosed only. *How often:* the midpoint is lost when it
  and its one spare both fail at run time, which at the recorded loss rate of 1 member in 37 is about (1/37)² ≈
  0.07% of windows, or when a physics flag found at harvest contaminates it (no spare runs then), for which the
  block has no rate yet.
- **Harvest problems first.** When an attempt's only window-removing codes are `*.identity_unmeasured`,
  `model.identity_unpinned`, `whole_window.verdict_absent` or `records.source_changed_during_harvest` (checks that did not run, had no pin to compare against, or ran on moving
  bytes), the cause is the harvest, not the window: R3 and re-harvest on identical bytes before deciding whether to
  re-arm. *Supersession* (PLAN2 row 12): when an arm collector recorded `pack.identity_unmeasured` or
  `code.identity_unmeasured` because it errored or timed out, and the harvest itself re-derived every check that
  collector performs (pack: the pins, the config run ids and the registered digests; checkout: HEAD, tracked edits
  and untracked files under the executed roots; executed code: the executed inventory and the chain sidecar), the
  harvest's own result stands and the arm's flag is moved, whole, into `records.identity_unmeasured_superseded`
  (DISCLOSE). Without this, a collector that errors deterministically would remove every re-armed window.
  *Two more conditions for the pack collector.* The three pack checks named above are needed and are not enough.
  The arm's pack collector also checks that the pack files in the checkout are the committed ones and that no run id
  is used twice, and the harvest can stand in for those two checks only through two of its other steps. (i) The
  harvest ran the checkout's tracked-edits check and its untracked-files check. It can run them only when the
  listing of the working tree taken at the arm is present: the output of `git status --porcelain`, which the driver
  saves in the executed-file inventory. (ii) The harvest resolved the **member dispatch** of every collection stage,
  that is, the list of run ids the stage launches. A stage whose list the harvest cannot read is named in
  `roster.dispatch_unresolved` (DISCLOSE), and the check for a run id that two stages launch
  (`roster.duplicate_run_id`, which removes the window) then lacks that stage's run ids. If (i) or (ii) fails, the
  arm's `pack.identity_unmeasured` stays and removes the window. Condition (ii) is the one that changes an outcome:
  `roster.dispatch_unresolved` alone is only disclosed, so the window would otherwise have been kept. When the
  listing of (i) is missing, the harvest's own `code.identity_unmeasured` normally removes the window anyway. The
  checkout and executed-code collectors carry no further condition (`harvest.supersede_identity_unmeasured`).
  *Where the harvest reads a stage's dispatch, and what follows for each pack* (found when revision 11 checked this
  passage against the code at `9b0c680ed`). The chain launches a collection stage from the stage's **order
  manifest**: the file `order_manifest.json` in the directory of the stage's member configurations, which lists the
  stage's members in launch order. The plan writer and the driver read the dispatch from that same file
  (`plan.resolve_stage_dispatches`, `driver._local_stage_dispatch`). The harvest does not. It asks the plan module
  (`joulewise/b5/plan.py`) for a per-stage reader named `resolve_stage_dispatch`; the module has no function of that
  name, so the harvest falls back to the plan tree's own entry for the stage, `input_ref`, which names either a list
  of member rows held in the plan tree or a manifest file of the pack (`harvest.stage_dispatches`). GAMMA's plan
  tree carries an `input_ref` on each of its ten collection stages, and the 101 run ids read through them are the
  ones its order manifests list, so GAMMA's dispatch resolves. ALPHA's and BETA's plan trees carry none: `input_ref`
  is null on all ten collection stages of each. So on every ALPHA and BETA harvest all ten stages are unresolved,
  `roster.dispatch_unresolved` is recorded once in each harvest, condition (ii) fails, and an arm's
  `pack.identity_unmeasured` is never superseded. An ALPHA or BETA window whose arm left that flag is therefore
  removed. When the flag is its only window-removing code, the rule at the head of this item applies: the cause is
  the harvest, so R3 and a re-harvest of the same bytes come before any decision to re-arm. Two more effects on
  every ALPHA and BETA harvest touch no number and remove nothing. The harvest's own count of members per collection
  stage is empty, so each stage the driver counted (§5.7) is recorded as `yield.harvest_disagrees_with_window`
  (DISCLOSE). And the check for a run id that two stages launch has no run id to compare; the plan writer's own
  check, which reads the order manifests, refuses a plan in which two stages launch one run id into one runs root,
  before any arm.
  *Model identity* is superseded the same way since Opus audit F5 (commit `a28e8611e`): the arm's model-identity
  collector has a 55 s budget, and a slow one left `model.identity_unmeasured`, which removed the window. Every
  member's metadata carries the content hash of the model tree its own process loaded and its runtime stack, and the
  harvest compares them with the pins (`harvest.model_identity`). When the harvest read the pins and compared the
  identity of every succeeded science member (at least one) with a pin, its own result (a mismatch, or clean) stands
  and the arm's flag moves into `records.identity_unmeasured_superseded`; a science member whose identity cannot be
  derived keeps the arm's flag (`IDENTITY_SUPERSESSION_CHECKS` `model_identity`: `pins`, `members_compared`). Revision
  6 said model identity was never superseded because the harvest does not re-hash the model files; it still does not,
  but each member's own recorded hash is the evidence the comparison needs.
- **UNCLASSIFIED codes** block only the release event. For scheduling, an attempt with an unclassified code but no
  classified window-removing code counts as claim-usable. The code is classified blind (from its definition and
  emitter, reading no energy) by a cold erratum to the catalog before the release event. If that makes the attempt
  not claim-usable, its pack is re-armed after the packs already scheduled, and the changed order is disclosed.
- **A re-harvest that changes `claim_usable`.** An R3 re-harvest on identical bytes with a repaired program (§7.1,
  §11 item 4) may change a completed attempt's `claim_usable`. The same rule applies as for a late classification: a
  pack whose analysed attempt becomes not claim-usable is re-armed after the packs already scheduled, and the changed
  order is disclosed; an attempt that becomes claim-usable is the analysed attempt only if it is the pack's first
  claim-usable attempt in arm order (`first_claim_usable`), and any later attempt of that pack is listed in the
  attempt history as not analysed. Each attempt's `exclusions.json` records the catalog digest and the harvest
  program's commit, so which program decided is always on record.
- **NULL:** re-arm after the named hazard is gone (a contention dwell timeout: identify the process; charging: wait
  until the arm's battery rule of §4.2 would pass, which is the adapter connected, IsCharging No and a battery
  current of at most 200 mA in either direction, the state this file calls battery float; the frequency gate: the
  desk redraw of §3; disk: offload).
- Ed's NO, on the arm notice before each arm, stops that arm.

### 7.3 Anti-spiral routing

Each attempt that is not claim-usable has a **cause key**: the hazard modules that refused (NULL), or the families of
its window-removing codes. The key is built only from records that are released during the block (§8). The arm
record (`hazards/arm.json`, §4.1) names the hazard modules that refused. `harvest.json` lists the window-removing
codes that fired (`exclude_window_reasons`, §7.1), and the catalog gives each code's family. An attempt removed by
`cell.below_minimum` is keyed by that code. Which member exclusions removed the cell's units is written only in
the three `derived/` files that §8 item 2 restricts (`derived/exclusions.json` names each excluded member's
codes), and that item, as the seal gate's stage 1 wrote it, allows one read of those files during the block, the
read of `claim_usable`. So two consecutive attempts of a pack that both fall below the cell minimum share a cause
key, whatever removed their units. (Revisions up to 11 keyed such an attempt by the families of the member
exclusions that removed the units, which would need a second read of those restricted files.) When two
consecutive attempts of the same pack share a cause key family, the next spend goes to a consult, not
a third arm; the consult may authorize another unchanged attempt, a prospective change (cold erratum), or END STATE.
A consult that cannot settle goes to a cold gate; a cold-gate refusal goes to Ed. None of these is a cap on attempts.

**Process rule for empty and short windows** (PLAN2 §2.2 H; not code). The orchestrator does not arm window N + 1 on
unchanged code when window N's yield status (§5.7) is EMPTY, or LOW with one shared pre-bundle cause. The sign of a
shared cause is the driver's flag `stage.members_refused_pre_bundle_identical` (three consecutive members that
ended without a bundle for one cause, §5.7). The driver lists the codes of the flags it emitted in its terminal
record (`night/hazard_result.json`, field `flags_emitted`), which is a released record. The orchestrator fixes the
cause first, by the R3 route. *Why:* a deterministic refusal repeats identically in every window; under
back-to-back cadence each repeat costs a whole arm and chain and teaches nothing new. (Revisions up to 11 named a
second sign: every lost member of the short stages sharing one cause in the harvest's
`collection.failure_histogram`. The content of that flag is written only to `derived/flags.jsonl`, one of those
three restricted files, so this rule does not read it during the block.)

*One LOW that does not hold the next arm* (orchestrator ruling of 2026-10-07, on a case found when revision 11 checked
this file against the code). On GAMMA, each of the two diagnostic interior references (§0.12) is a stage of one
member, and the driver counts such a stage as a science stage, whose minimum is then 1 of 1 (§5.7). So one lost
diagnostic member makes the window's yield status LOW, and a single lost member always "shares one cause" with itself.
At the recorded loss rate of 1 member in 37 this happens by chance in 1 − (36/37)² ≈ 5.3% of GAMMA windows, so for
these two stages a LOW does not indicate a systematic cause. The diagnostic member is no NEG-8 reference and enters no
reported cell and no contrast. A LOW that comes from one lost diagnostic member alone therefore does not hold the next
arm. The yield status itself stops nothing and removes nothing in any case; it sends a notice (§5.7). The magistrate's
brief carries this rule. Giving the diagnostic role its own minimum in the driver is deferred until after block 5.

### 7.4 END STATE

*What is counted.* A member's metadata records the outcome of its per-member anchor bound (§0.14) as one status
word, its **anchor status**: `bounded`, or another word when the bound failed or could not be computed. A
calibration capture has a sampler stream of its own and records the same status in its evidence file,
`instrument_evidence.json`. A status is **recorded** when that field holds a value; a member or capture with no
value, or a capture whose evidence file cannot be read, is left out of the count, and any word other than `bounded`
counts as not bounded. Captures are counted only for a window whose bracket session was finalized: its pre
and post slots, at most two per window. A calibration capture is not a member (§0.3), but the code counts members
and captures together.

*The rule.* Counting across every started attempt of this measurement block: if at least 5 members and captures
together have a recorded anchor status and more than half of those are not `bounded`, the clock instrument is
failing and re-arming cannot cure it; the measurement block goes to **END STATE** at once. (A single window meeting
the same rule is already `clock.systematic`, §6.5, which counts the same way: three members and two captures reach
its minimum of 5, and a capture that is not `bounded` counts toward the majority.) END STATE also follows a
cold-gate ruling to stop. At END STATE no further window arms, Ed is emailed, and the next step is a design record
naming the cause, with a consult and a cold gate. Claim-usable windows keep their bytes; their analysis is fixed in
analysis plan §2.3.

*Who counts.* The harvest applies the rule to one window only (`harvest.clock_systematic`). No program adds the
counts of several attempts: this is a rule the lead applies (§7.2). Its inputs are status words, not energies. The
harvest writes a window's two counts (`recorded`, `non_bounded`) only into the `observed` of `clock.systematic`,
when that window's own rule fired. For any other window the statuses are the per-member `anchor_recorded` values of
the harvest's `withheld/member-assessments.json` (restricted custody, so read by automation, §0.1) and the
`clock_anchor.status` of each capture's `instrument_evidence.json`.

### 7.5 A defect found in the middle of the block

**Collection code** is any file in the sealed inventory as the measurement checkout executes it during a window, or
any change to how a window's bytes are produced. The measurement checkout's HEAD stays H_claim plus pin-only commits
for the whole block (§11), so a desk program's repair (harvest, replay, extraction, mint, analysis) that lands in a
desk checkout changes no collection code even when the file it changes is also imported inside a window from the
measurement checkout; §11 item 4 names what the harvest lane may change. GAMMA's contrasts are judged against floors
from ALPHA and BETA, so all three windows must share one
acceptance, one macOS build and the same collection code: no collection-code file that a completed window executed
may differ, byte for byte, in the commit a later window runs.

*How to read "H_claim plus pin-only commits".* One more commit lies between H_claim and the first pin-only commit:
the **seal commit**, the child of H_claim that carries the filled sealed inventory and the sealed text of this file
and of the analysis plan (§11). It changes those three files and nothing else, so it changes no file that the sealed
inventory lists, and the measurement checkout is checked out at it before ALPHA-1 arms. Where this section and §14
Q13 say that the measurement checkout stays at H_claim, the commits it holds are therefore H_claim, the seal commit,
and the pin-only commits made after it.

- A cure confined to collection code that no completed window executed (for example GAMMA-only stages) does not
  supersede completed windows. The cure carries a **changed-path map**: the list of files that differ between
  H_claim and the cure's commit, as `git diff --name-only` prints it. The map must show that no file executed by a
  completed window changed, and a diff-scoped #416 re-audit covers the change. Every cured file is a window input
  (§9.1), so a window armed after the cure would differ from the sealed inventory and be removed
  (`code.executed_differs_from_sealed`). The cure therefore re-issues the seal: its commit becomes the new H_claim,
  and a new seal commit carries a sealed inventory generated from it (§11). A re-harvest of a window completed
  before the cure is given the inventory that was in force when that window was armed, or it would be compared
  with the new one. The harvest command takes it as `--sealed-inventory-path`, and the window's first harvest kept
  a copy in its archive, `sources/inputs/sealed_inventory.json`.
- A cure touching collection code that a completed window executed **supersedes the whole block**: completed windows
  are retained and disclosed structurally, their energies are never analysed, a new registration or a cold erratum is
  written, and the block restarts at ALPHA.
- A defect in code that does not run during collection (harvest, extraction, mint, analysis) is cured by R3 and re-run
  on identical bytes; the block continues.
- **Fresh-stream admission retry** (lane L11: restarting the sampler stream for the retry, so a wait between attempts
  fits the clock budget) is an option after ALPHA-1 if its admission aborts cost a cell. It changes collection code,
  so it needs a prospective cold erratum and follows this section.

### 7.6 What re-arming can and cannot select on

The decision to re-arm is a rule the lead applies (§7.2), not code. The rules of §7.2 to §7.4 read each attempt's
verdict, `claim_usable`, reasons and yield counts (all in `harvest.json`, §7.1), the families of its
window-removing codes (those reasons, with the catalog; §7.3), the hazard modules that refused an arm and the
codes of the flags the driver emitted (the arm record and the driver's terminal record, §7.3), and anchor status
words (§7.4). None of these is an energy. So an energy can bear on re-arming only through what `claim_usable`
itself reads.
`claim_usable` reads no science member's energy except the single pass/fail precheck ratio of §6.3, which is
RESTRICTED. It does read reference-workload energies (the NEG-8 screen), power (idle admission, the bracket), timing,
and the physical hazards. So re-arming cannot select on the science outcome, but every reported number is
**conditional on a window that passed these quiet, timing and drift predicates**, and the analysis plan prints,
beside every reported cell and contrast, the number of attempts of its pack and their causes.

## 8. Blinding

1. **Before seal.** No claim-eligible `_v5` byte exists. The authors of this file read none (§16).
2. **During the block.** From ALPHA-1's arm until the block closes (every pack claim-usable, or END STATE), every
   harvest, courier record, email and public summary releases **structure** only: verdicts, `claim_usable`, flag
   counts by code and family, kept-unit counts, paths, hashes, hazard measurements, and timing that is not a phase
   duration (member cycles and cooldown waits are releasable). **Restricted:** energies, powers, phase durations,
   floor values, reported means, dominance ratios, calibration numeric diagnostics, any pass/fail derived from a
   science energy, and every flag whose `blinding` is RESTRICTED. The harvest writes every flag with its code, the
   RESTRICTED ones included, into `derived/flags.jsonl`, names each excluded member's codes in
   `derived/exclusions.json` and counts flags by code in `derived/window_flags.json`; those three files are restricted
   until the release event and are listed in the custody map, and their only in-block reader is the scheduler's read
   of `claim_usable`. Everything released before the release event (courier records, emails, summaries) shows a member
   removed by a RESTRICTED code as "removed (restricted code)", without the code, and omits the per-code count of any
   RESTRICTED code; that redaction is a step of the release, done by lane L9's disclosure producer (analysis plan §8.1),
   not by the harvest. The driver's courier for `HAZARD_PACK` sends structure only: no
   chain or campaign logs, no runs-root files. The custody map at the end of this section (`B5-BLIND-CUSTODY-MAP`)
   lists the restricted paths, these three files among them.
3. **Unblinding.** After the block closes and the blind dry run of analysis plan §3.2 has completed, the lead records
   a **release event** tying the sealed SHA-256s of this file, the analysis plan and the catalog to the final harvest
   records; the analysis then runs exactly as registered. Analyses not registered are labelled exploratory. The
   release event is not written into this file, whose bytes cannot change after the seal: each window
   plan records this file's SHA-256, the plan writer refuses a file that does not hash to the digest it is given,
   and the harvest faults when the file differs from the digest its plan recorded. It is written as a section
   appended to the seal record (§12), the section named `FILL[B5-RELEASE-EVENT]`.

**The custody map** (`B5-BLIND-CUSTODY-MAP`, filled in revision 12).

*Forcing problem.* Item 2 says what kind of value is restricted. It does not say which files hold such values, and
restricted custody is kept by rule, not by the file system: the harvest creates every file with ordinary
permissions, so nothing stops a seat from opening one. A seat that has read an energy can no longer write or repair
analysis code blind, that is, without the outcome in view (analysis plan §3.2). The list of paths a seat must not
open therefore has to be complete, and it has to exist before the first window does.

*How to read it.* No window exists at the seal, so the map cannot name files. It gives **path patterns** under four
directories that every attempt has, and it is applied to an attempt by putting that attempt's four directories in
place of the names in angle brackets:

- the **claim runs root** and the **bound runs root** (§0.17), which the window plan names as `runs_roots.claim` and
  `runs_roots.bound`;
- the **custody root**, the directory into which the driver, the arm, the monitor, the meter and the chain write
  their own records of the window, which the window plan names as `custody_root`;
- the **archive root**, the directory one harvest writes. It holds a copy of the window's bytes under `sources/`
  (`sources/claim-runs/` and `sources/bound-runs/` for the two runs roots, `sources/night-custody/` for the custody
  root, `sources/ledger/`, `sources/inputs/` for the sealed documents the harvest read, `sources/repo/` for the pack,
  and the list of digests `sources/SHA256SUMS`), the harvest's outputs under `derived/` and `withheld/`, and
  `harvest.json`. A re-harvest writes a new archive root, and the map applies to each.

In a pattern, `**` stands for every file below the directory named.

| Restricted until the release event | What it holds |
|---|---|
| `<claim runs root>/**` | every member bundle (energies, powers and phase durations) and the calibration captures |
| `<bound runs root>/**` | the NEG-8 corpus bundles and the drift bound derived from them |
| `<custody root>/hazards/monitor/battery.jsonl` and `<custody root>/hazards/monitor/raw/battery/**` | the battery's current and voltage through the window, read every second; their product is a power |
| `<custody root>/hazards/meter/**` | the whole-machine meter's power samples (§5.8) |
| `<custody root>/night/chain.stdout.log`, `night/chain.stderr.log` and `night/transcript/**`; `<custody root>/night.log`; `<custody root>/operator-logs/**` | the logs of the driver, of the chain, of its tools and of the members, which can quote energies and durations |
| `<archive root>/sources/**`, except `sources/SHA256SUMS` and `sources/inputs/**` | the harvest's copy of everything above |
| `<archive root>/withheld/**` | the numbers: the re-reduced member summaries, the member spans, the bracket evaluation, the re-derived NEG-8 bracket and bound, the battery-assist energies, the meter record, and the full texts of errors |
| `<archive root>/derived/flags.jsonl`, `derived/exclusions.json` and `derived/window_flags.json` | the flags and the exclusions by code, the RESTRICTED codes included (item 2) |
| every backup and offload copy of a path above (§5.6) | the same bytes |
| what the harvest command prints when its verdict is HARVEST_FAULT | an error message, which can quote a data value |

*Releasable during the block,* listed so that nobody has to guess: `harvest.json`; every file under `derived/` other
than the three above; the record files the driver pushes to the results branch `night-results/<plan id>`
(`scripts/run_night.py` `HAZARD_ARTIFACTS`: the arm decision, the per-stage yield counts, the supervision journals
and the G10 record among them); the courier's email; the monitor's clock, thermal, contention and disk journals and
the arm record `hazards/arm.json`, which are hazard measurements; what the harvest command prints on any other
verdict; and the attempt history of §7. A file the map does not name is released only if it holds nothing that item 2
restricts; in doubt it is treated as restricted.

*Who may read a restricted path.* Until the release event, automation only (§0.1): the harvest, the blind dry run of
analysis plan §3.2 and, for the three `derived/` files, the scheduler's read of `claim_usable` (item 2). The rules
by which the lead re-arms read nothing else from those three files: the cause key and the short-window rule of
§7.3 are built from released records. One of those rules does take a value from other restricted paths, by
automation: the END STATE count of §7.4, which takes anchor status words, and nothing else, from
`withheld/member-assessments.json` and from the calibration captures' evidence files. None of
them prints, emails or commits a restricted value. After the release event: the lead, and the results cold gate
that re-derives every printed number (analysis plan §3.1 step 12). A seat that will write or review a repair after
the release reads no restricted path even then, because analysis plan §3.2 allows such a repair only from seats that
have read no released number.

*Two channels a list of paths misses.* The body of a pull request that carries a harvest or a fix to one can quote
what replaying real bytes gave, so a blind seat does not open it. And three analysis programs print a science result
to the terminal on an ordinary successful run (analysis plan §3.1 steps 6, 9 and 11: the dominance close-out
`scripts/build_d165_dominance_closeout.py` when it is given no `--output`, the claim gate
`python -m joulewise analyze-claims`, and the fill renderer `scripts/render_results_fills.py`). Before the release
event they run only inside the blind dry run, which keeps every output in restricted custody and writes out
structure only (analysis plan §3.2).

*Worked example (a GAMMA attempt; the four directory names are invented).* Its window plan names the claim runs root
`/runs/gamma-1/claim`, the bound runs root `/runs/gamma-1/bound` and the custody root `/custody/gamma-1`, and its
harvest wrote the archive root `/archive/gamma-1-h1`. GAMMA plans 101 members (§4.2): 80 science members, the 7
NEG-8 references and the 2 diagnostic interior references, which go to the claim runs root, and the 12 NEG-8 corpus
members, which go to the bound runs root; up to 7 spares can join the claim runs root (§0.12). Restricted: every
file under the two runs roots (one bundle directory for each member that ran, and in the bound root the bound
derived from the corpus); `/custody/gamma-1/hazards/monitor/battery.jsonl`; the logs under
`/custody/gamma-1/operator-logs/`; everything under `/archive/gamma-1-h1/withheld/`; and
`/archive/gamma-1-h1/derived/exclusions.json`. Releasable: `/archive/gamma-1-h1/harvest.json`,
`/archive/gamma-1-h1/derived/roster.json` and `/custody/gamma-1/night/stage_yield.jsonl`. An email that reads
"GAMMA-1: COLLECTED, claim-usable; two members removed, one by `member.admission_aborted` and one removed
(restricted code)" is structure. An email that names the one RESTRICTED code of the catalog,
`member.anchor_energy_envelope_exceeded`, or gives its count, is not: the code says that the timing envelope of a
member's phase energy exceeded a quarter of that energy (§6.3), which is a statement about a science energy.

## 9. Directive gates

### 9.1 #416: pre-arm triple audit

Once per frozen code or protocol change, before ALPHA-1 arms: a blind full-system audit by three independent model
families, every BLOCKER and MAJOR finding challenged by a refuter from another family, and each confirmed one fixed
before arm. It never runs per window; a later change to collection code (§7.5) triggers a diff-scoped re-audit of
that change. No audit work runs during a window.

**`416-SEATS`** (filled in revision 8): Astra 6 (`gpt-6-astra`, OpenAI) at effort xhigh, Fable 5.1 (Anthropic) at
effort high and Opus 5.5 (Anthropic) at effort xhigh. Astra's findings went to Fable 5.1 and Opus 5.5 refuters
(workflow `wf_3bdbf778-1ad`); Fable's to Opus 5.5 refuters and Opus's to Fable 5.1 refuters (workflow
`wf_c7886624-d74`), so no finding was judged by its own seat.

**`416-AUDIT-RECORD`** (filled in revision 8). The audit ran on 2026-10-07 at the frozen head
`a434e363d96621318657418e60b8d14410079d82`, before the seal (the order this section first named, after the seal at
H_claim, was changed so that the fixes could land before the seal). Records: Astra
`/Users/edr/night-archive/gate-prune/triple-audit/astra/REPORT.md`, verdict BLOCKERS FOUND; Fable
`triple-audit/fable/REPORT.md`, verdict ARM-READY (no BLOCKER, four MAJOR); Opus, verdict BLOCKERS FOUND, findings in
the result of workflow `wf_c7886624-d74` (the seat's report file was not written) and probes in `triple-audit/opus/`.
Refuter outcomes for every BLOCKER and MAJOR, with the reasons for each refutation in
`/Users/edr/night-archive/gate-prune/INTEGRATION_TODO.md`:

| Finding | Seat's severity | Refuter | Where it went |
|---|---|---|---|
| Astra A1: a contaminated NEG-8 reference kept its weight in the screen and the allowance | BLOCKER | confirmed, MAJOR | NEG-8 council and cold judge (`neg8-council/RULING.md`); lane `neg8-survivors` (§0.12) |
| Astra A2: a missing `chain.started` gives a NULL harvest | BLOCKER | refuted: the driver creates the marker exclusively before the chain spawns | none |
| Astra A3: an unread probe refuses at the arm; four unreadable censuses stop the chain | BLOCKER | confirmed, MINOR | lane `audit-fixes-1` (§4.1, §4.5) |
| Astra A4: a missing journal makes every member `contention.unmeasured` / `battery.unmeasured` | BLOCKER | refuted: a member whose contention or battery was never measured cannot be shown clean; the exclusion is kept | none |
| Astra A5: a missing locator sends members down legacy authentication | MAJOR | confirmed, MINOR | lane `audit-fixes-1` (§0.17: the unusable-inventory refusal, and the lineage flags that name the roots whose members will refuse). One lane is deferred until after block 5: carry the fact that a member runs in a block-5 window (the `HAZARD_PACK` route) by a channel other than the lineage locator file (`.joulewise-launch-lineage.json`, §0.12), so that a missing locator no longer sends the member down the authentication of the retired `TRANSACTION_PACK` route (§11 item 3). Until then such a member refuses itself, and the lineage flags and the yield counts show it (§0.17, §5.7) |
| Astra A6: a missing desk identity file stops the reservation | MAJOR | confirmed, MINOR | lane `audit-fixes-1` (§6.10) |
| Fable F1: an absent verdict removes the window | MAJOR | refuted: a NUMBER_INTEGRITY exclusion with a re-harvest cure (§7.2); allowlist label fixed | lane `audit-fixes-2` (label only) |
| Fable F2: an unreadable failed-member list removes the window | MAJOR | refuted: the writer cannot produce it | none |
| Fable F3: four unreadable censuses stop the chain | MAJOR | confirmed, MINOR; same as A3 | lane `audit-fixes-1` |
| Fable F4: no analysis program reads `exclusions.json` | MAJOR | refuted as a defect of this head: it is the open L9 lane, required before any claim | L9 (analysis plan §11) |
| Opus F1: one lost NEG-8 reference removes the window | BLOCKER | confirmed | NEG-8 council and cold judge; lane `neg8-survivors` (§0.12) |
| Opus F2: one malformed flag line blocks the release for ever | MAJOR | confirmed | lane `audit-fixes-2` (§6.2) |
| Opus F3: the census matched the window's own processes by string | MAJOR | confirmed | lane `audit-fixes-2` (§4.5) |
| Opus F4: an unreadable process identity or a torn lock refuses the campaign | MAJOR | confirmed, MINOR | lane `audit-fixes-2` (§6.10) |

The four lanes that carry the fixes, `lane/2026-10-07-audit-fixes-1` (`01232742e`), `lane/2026-10-07-audit-fixes-2`
(`0571cf8fd`), `lane/2026-10-07-neg8-survivors` (`2011ec285`) and `lane/2026-10-07-coldpass2-fixes` (`d06ab4778`, the
Fable delta cold pass's fixes to the first three), are all ancestors of `43ac12d0c` and of the int5 head `fe28e5a0c`
(`git merge-base --is-ancestor`, checked by this author). Lower-severity findings were triaged in the fix lanes without
refuters. Because the fixes changed collection code after the audit, the rule above calls for a diff-scoped re-audit
of the change.

**`416-DELTA-RECORD`** (filled in revision 9). Four diff-scoped passes, each by one seat that read the diff and ran
its own probes, read-only in the repository:

| Pass | Seat | Diff | Verdict | Record (SHA-256 computed by this author) |
|---|---|---|---|---|
| Delta re-audit | Sol 6.1 (`gpt-6.1-sol`, OpenAI) at effort xhigh, through the audited Codex route | `a434e363d..43ac12d0c` | BLOCKERS FOUND: A1–A5 | `/Users/edr/night-archive/gate-prune/delta-audit-sol/REPORT.md`, `86a8236f519a7740e0da18a2035210ddf58f55fe9dd946dac05c843206694359` |
| Re-verification | Sol 6.1 at effort xhigh | `43ac12d0c..fe28e5a0c` | A1–A5 FIXED; three new findings, which the report numbers R1, R2 and R3 (Sol R1, Sol R2 and Sol R3 below) | `delta-audit-sol-2/REPORT.md`, `f03e949f3276d561000a9f3da0a67a8a2f3ac37470803e6dedca2fedb11f2068` |
| Cold pass 3 | Fable 5.1 (Anthropic) | `821b58f8b..43ac12d0c` | PASS WITH NOTES, no defect | `cold-pass-3/REPORT.md`, `eb78baac58a72cfae9ea060302a4213c598f578e8e051f02a164aed1db09f7a5` |
| Cold pass 4 | Fable 5.1 | `43ac12d0c..fe28e5a0c` | PASS WITH NOTES; one claim-time defect (D1) | `cold-pass-4/REPORT.md`, `4ab433c78c832754ac19f5993ed666a858a045a373e3e20bec2c43e34b937eb7` |

Every finding of the Sol passes was shown by an executed probe (the report marks each EXECUTED). The
re-verification numbers its three new findings R1, R2 and R3. This file writes them **Sol R1**, **Sol R2** and
**Sol R3**, because "R3" alone already names the fix route of §0.1, which has nothing to do with them. Where each
finding went:

| Finding | What it was | Where it went |
|---|---|---|
| A1 (BLOCKER) | an accepted survivor re-screen did not replace the bracket the claims read: 0.5933 J where the survivors' allowance is 0.6383 J (§0.12) | fixed, lane `neg8-delta-fixes` (`6fd863645`): `derived/neg8-allowance.json` and its consumer; re-verified FIXED |
| A2 (BLOCKER) | a spare that ran another model sat in an unpinned group and raised no identity flag | fixed (`66c956dba`, pin `754c8c093`): the `neg8_reference` unit; re-verified FIXED |
| A3 (BLOCKER) | absent or unreadable manifests erased a known reference loss, and the stored passing screen stood | fixed (`3cf9d6b2f`): the sealed roster names the references; re-verified FIXED |
| A4 (should fix) | the census read a `node` option's value as the script, so a live agent read as clean | fixed, lane `census-ancestors` (`ca25d9299`), by parsing options; re-verified FIXED; the parsing was then withdrawn (Sol R1 below) |
| A5 (should fix) | a strict-invalid reference failed the whole screen instead of being lost | fixed (`294f6e573`): reason `strict_invalid` in writer, replay and harvest; re-verified FIXED |
| Sol R1 (should fix) | a second `node` option (`--trace-require-module all`) was read as the script: the same class as A4, a second time | fixed, lane `census-interp` (`2524637ae`, merged into int5 by `84661ddb3`): the option parsing is withdrawn and every argument of a JavaScript runtime is read (§4.5). The merge came after the four passes above. Fable's delta cold pass 5 reviewed it at `9395cecfb` and found it sound (the second part of this record, below) |
| Sol R2 (BLOCKER) | floor extraction cannot pass the harvest archive, so every block-5 floor cell has no allowance (the same defect as cold pass 4 D1) | lane L9-NEG8 (analysis plan §11): claim-time code, safe direction (refuses) |
| Sol R3 (BLOCKER) | the claim validator rejects a row whose stored screen failed before reading the harvest's passing survivor re-screen | lane L9-NEG8: claim-time code, safe direction (refuses) |

Sol R2 and Sol R3 were the third review in a row to find a defect in the NEG-8 survivor logic, which lives in three
places (the verdict writer, the replay that authenticates a verdict row, the harvest). By the rule that sends a
twice-failing defect class to a consult rather than a third fix round, the orchestrator took a consult: Fable's cold
pass 4 view together with Sol R2 and Sol R3. Cold pass 4 called the three places "consistent enough to seal", for two
reasons. First, three parts of the logic already exist once only and are shared: the **evaluator**, the function that
screens the surviving references (`whole_window.evaluate_neg8_point_drift`, called by the verdict writer and by the
re-derivation); the count-adjusted bound, which is bound(n_s, n_e) of §0.12
(`whole_window.neg8_count_adjusted_bound`); and the re-derivation, the function that rebuilds a verdict from the
reference bundles instead of trusting the stored row (`whole_window._derived_neg8_decision`, which the replay and the
harvest both call). Second, every disagreement between the three places ends in an exclusion, never in a passing
screen or a read of a dropped energy. What differs between the places is which losses each one can observe (the
harvest alone sees the physics flags of §6.4, for example) and their test of whether a reference is strict-invalid
(§0.12, "The strict check of a reference"; cold pass 4 note N-3). The decision: seal on this code, and fix Sol R2,
Sol R3, cold pass 4 D1 and the differing strict test (by one test shared by all three places, the shared predicate
of §0.12) in one named lane, L9-NEG8, which runs after the seal and before any claim (§11 item 1 (ii) and item 4),
with one design round by Sol and Fable before code. None of it is collection code: none of it runs during a window or
changes a window's bytes, so it does not block the arm. Cold pass 3's notes (N-A, N-B) and cold pass 4's notes (N-1,
N-2) are catalog questions that this directory's catalog already answers: `model.identity_mismatch` and
`model.identity_inconsistent_in_window` are EXCLUDE_WINDOW (§6.5), `model.identity_underivable` is EXCLUDE_MEMBER, and
`whole_window.verdict_unauthenticated` is DISCLOSE. The seal gate's stage 1 confirmed all four effects (rulings SG-6
and SG-7, 2026-10-07).

**`416-DELTA-RECORD`, second part** (filled in revision 12): the code merged after `fe28e5a0c`. Two changes to code
came after the four passes above. The first is the census interpreter rule (Sol R1 in the table above; §4.5). The
second is the **seal landing**, the lane `lane/2026-10-07-seal-landing`, which changed how a window is compared
with the seal. *Why it was needed:* a file cannot name the commit that contains it, so the sealed
inventory, which names H_claim, is committed one commit after H_claim, and every window runs from that later commit
or a later one (§11). The harvest lists every path that differs between H_claim and the commit a window ran from
(`git diff --name-only`); this is the **head comparison**. Before the lane, every such path except the ledger pin
was `code.executed_differs_from_sealed`, so every block-5 window would have been removed because the seal itself
had landed. *What the lane changed:* only a changed **window input** is now a difference, that is, a tracked file
a window can read while it is planned, armed or run: any file under `joulewise/`, `scripts/` or `configs/` other
than the ledger pin and the three files the seal itself rewrites (the sealed inventory, this file and the analysis
plan), and `docs/phase_2/window_runbook.md`. Every other changed path is recorded in `derived/code-identity.json`
and raises no flag. The lane was merged into the integration branch at
`9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a`. Cold pass 5 covers the whole range `fe28e5a0c..9395cecfb`, and an
independent review covers the lane. Each is the work of one seat that took no part in writing the code, read-only
in the repository, with its own executed probes:

| Pass | Seat | What it read | Verdict | Record (SHA-256 computed by this author with `shasum -a 256`) |
|---|---|---|---|---|
| Cold pass 5 | Fable 5.1 (Anthropic), a cold session | the diff `fe28e5a0c..9395cecfb` (seven files under `joulewise/`, `scripts/` and `configs/`; five test files) | PASS WITH NOTES; one defect, disposed "flag, not refuse" (C6 below) | `/Users/edr/night-archive/gate-prune/cold-pass-5/REPORT.md`, `46446fa429bdceaac91da1bb3916714c3c59fd846c6bf4503bad4462e218e8ad` |
| Seal-landing review | Opus 5.5 (Anthropic), a review seat that did not write the lane | the lane at its head `2737ef88c` (base `9b0c680ed`), by executing it | DEFECTS: one MAJOR (F1), older than the lane and raised by the lane itself as an open question; everything the lane was asked to change behaves as it says; F2 and F3 are MINOR, F4 to F9 notes | `/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/REVIEW.md`, `fec2dc44938731c8528777b66c336df07ca553ff6f43f2bcd146cab641012f0a` |

What the two passes established, each by execution on a real git history. A changed file under `joulewise/`,
`scripts/`, the window's pack, any other path of `configs/` (the catalog, the identity pins and the sizing output
among them) or the runbook, committed after H_claim, still gives `code.executed_differs_from_sealed` at the
harvest (cold pass 5, cases C4 to C10; the review, sixteen cases). The arm's collector gives the same answer when
it is handed H_claim to compare with; in a window it is handed the commit the window runs from, so there the
harvest's comparison is the one that ties the window to the seal. A pin-only commit, the seal's own commit and a
commit confined to documents, tests or `RUN_STATE.md` give no flag (C1 to C3). The census rule classes every
launch shape found on this machine as §4.5 states (36 of 36 rows of the pass's table; a live `node` launch is a
hit; a census line that cannot be decided stays a hit). The commit that reworded the explanatory text of one
harvest function (`455e59b86`) changes no executable code: the syntax trees before and after are equal once such
texts are removed. The four pinned estimator files are byte-identical to the frozen head `a434e363d`, and
`scripts/prewindow_check.sh` is unchanged.

Where each finding went (orchestrator's ruling of 2026-10-07 on the lane and its review,
`/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/ORCHESTRATOR_RULING.md`). No finding changes a window
input before H_claim: each check lives in the harvest, which runs after a window, from a desk checkout (a checkout
of the repository other than the measurement checkout, §7.5). So each goes to the harvest lane, the set of changes
to the harvest that lands after the seal and before ALPHA-1's harvest (§11 item 4; the lane's work list,
`/Users/edr/night-archive/gate-prune/wave-1007b/harvest-lane/WORKLIST.md`, numbers these items H-8 to H-12).

| Finding | What it was | Where it went |
|---|---|---|
| Cold pass 5, C6 (defect) | a commit that changes only another pack's directory is a window input, so it removes a window that never read that pack | harvest lane, H-12: recorded, not a difference. It cannot arise in the registered sequence (the measurement checkout receives only pin-only commits, and the program that makes them, `scripts/advance_b5_ledger_pin.py`, refuses a commit that changes anything else), and when it fires it removes a window, never prints a wrong number |
| Review F1 (MAJOR) | when the launchd job is installed from a checkout other than the measurement checkout, the driver, the hazard modules, the monitor and the collectors are that other checkout's files; if they differ from the sealed inventory the harvest records the differing files and raises no flag | harvest lane, H-8: a differing code file in the driver's checkout becomes `code.executed_differs_from_sealed`; identical bytes stay a record. It cannot arise when the launchd job is installed from the measurement checkout, as §11 requires |
| Review F2 (MINOR) | the paths that raise no flag are "every path not listed", so a tracked file outside `joulewise/`, `scripts/` and `configs/` can change with no flag: for example `env/mac-measurement-lock.txt`, the list of package versions the measurement environment is built from, or `pyproject.toml` | harvest lane, H-9: the harvest's head comparison names the paths that raise no flag (`docs/` except the runbook, `tests/`, directories whose name starts with a dot, and Markdown files at the top of the repository); every other path is a window input |
| Review F3 (MINOR) | a sealed inventory that lists files but names no commit is compared with nothing | harvest lane, H-10: `code.identity_unmeasured`. The committed inventory is covered already: `tests.test_b5_seal_landing` refuses one whose `head` is not a commit |
| Review F4 (note) | a later commit to this file or to the analysis plan is silent in code | by procedure: the seal record's SHA-256s bind both files (§12) |
| Review F5 (note) | a re-harvest after a re-issued seal needs the inventory that was in force when its window was armed | runbook and magistrate brief (§11, §12) |
| Review F6 (note) | a changed path whose name is not UTF-8 faults the harvest | harvest lane, H-11 |
| Review F7 (note) | the catalog, `identity_pins.json` and `sizing_b5.json` carry draft labels in their sealed bytes | the two generated files keep the labels their generators write, and the seal record's digest of each file is what seals it (§12); the catalog's status note is rewritten before H_claim to a sentence that is true before and after the seal |
| Review F8 (note) | the commit after the seal commit must carry any test data file that the sealed text forces to change | accepted: that commit carries it, and the whole suite and CI are required green there (§11, §12) |
| Review F9 (note); cold pass 5 notes | the harvest records nothing about its own program; a stale clause in a harvest comment; the stale catalog note of `code.executed_differs_from_sealed` | the harvest records the commit of the checkout it ran from (the change the seal gate's ruling numbers K-7, in the harvest lane); the comment goes to the same lane; the catalog note is corrected before H_claim, because the catalog is a window input and cannot change in the seal's own commit |

A change to collection code that lands after `9395cecfb` and before H_claim needs a diff-scoped pass of its own
before the seal, by the rule at the head of this section. The changes the seal gate's stage 1 ordered in that range
are not collection code. They are one value and some notes of the flag catalog (the value is the cell minimum of
§6.6, which only the exclusion function reads, at the harvest); three entries of the refusal allowlist, two
reworded and one removed, in a file no program loads during a window (§6.11); and the tests and test data that
follow them (§13, the record of revision 12).

### 9.2 #421: battery float, and the battery-assist ruling of 2026-10-06

**What #421 asked for.** Ed's directive #421 (2026-09-25) made the battery's state mandatory evidence for every
capture: a number taken while the battery was charging, or while the machine was not drawing everything from the
adapter, should not stand unexamined. **Battery float** is the state the directive wants a capture taken in: the
adapter connected and the battery neither charging nor discharging, so that the adapter supplies everything the
machine draws. Its measured form is the arm's battery rule (§4.2): ExternalConnected Yes, IsCharging No and a
battery current of at most 200 mA in either direction. The directive's motivating hazards were two.
*Charging heat:* a change of the battery's charge limit from 80% to 100% would start a long charge, warming the
battery and adding load beside the workload.
*An incomplete wall reading:* a wall or USB-C meter on the adapter does not see energy the battery supplies, so the
machine's total energy cannot be read from the adapter side alone while the battery helps.

**What changed, and why.** Until 2026-10-06 any discharge above 200 mA in a member's span removed the member. Two
measurements on 2026-10-06 showed that this rule had been reading a 60 s snapshot (§4.2) and that the battery
assists under heavy load on the 140 W adapter. In the validation run of §4.2 (25 s idle, 170 s of an
8B-plus-CPU-burner load, 200 s of recovery), B0AC was nonzero at 126 of the 536 distinct SMC publications the run
saw (a publication is one refresh of the SMC's values; the run read them every 0.2 s). All 126 fell among the 270
publications of the load phase, where they cover about 63 s of the 170 s; the lowest read was −5,331 mA. Under the
old rule switched to the 1 s SMC reads, the heaviest members, most of all 8B prefill-p2048, would be removed in
numbers. Ed, 2026-10-06: "'under the existing rule' - should not preclude you from
sensible changes - if the science is improved by a new rule make a new rule or remove the old one - obviously this
needs to be durably remedied" (doctrine item 7 in the ruling). Two blind council seats (Opus 5.5 and Sol 6.1 xhigh)
agreed; the orchestrator ruled
(`/Users/edr/night-archive/wallmeter-probe/verify/RULING_battery_assist_2026-10-06.md`):

1. *The rail number does not depend on the source.* The processor rails are regulated downstream of the supply, so
   the rail energy the sampler reports is the same whether the adapter or the battery delivered it.
2. *Excluding assisted members would bias the result.* Assist happens when the load is highest, so removing those
   members selects members by load and pulls the kept means down, most of all for 8B.
3. *The evidence on hand is benign.* Qwen3-8B decode ran at 69.1–72.6 tokens/s under up to −5.3 A of assist against
   68.9–71.1 tokens/s without it. (The −865 mA reading of the earlier probe was at model load, not during decode.)
4. *#421's two hazards stay covered.* Charging (current above +200 mA, IsCharging, the charge accumulator) and loss
   of AC power still remove the member (§6.4), and the arm still refuses a battery current above 200 mA in either
   direction at idle (§4.2). The wall-reading gap is closed by adding the battery term explicitly to the
   whole-machine energy (§5.8).

So discharge with the adapter connected is disclosed (`battery.assist`), with its counts, minimum, duration and
discharged energy per phase, and every reported cell is printed both with and without the members that carry it
(analysis plan §8.1); neither value is chosen after the fact. The same disposition applies to calibration captures,
to the #421 endpoint pairs and to the accumulator bounds (§6.3, §6.5): a discharge-only failure is disclosed; charging
or AC loss keeps its exclusion. At `a434e363d` no rule removes a member or a window for discharge as such. One case
keeps a pair exclusion: a #421 pair that failed on discharge alone is disclosed only when the SMC reads cover the
span, because only then can the journal show that the span held no charging; without SMC coverage the pair's
exclusion stands, as missing evidence, not as discharge.

**What would reopen the ruling** (by erratum to an exclusion scoped to the affected phase): power-mode or power-limit
transitions that reproducibly accompany assist; lower rail power, frequency or tokens per second in assisted seconds
against matched unassisted seconds; or a battery-temperature rise concentrated in assisted stages (§0.6). GAMMA's 8B
members and the battery-temperature diagnostic are where this is watched. No qualification run is required before
the seal, because the rule does not depend on how often assist occurs.

**Records kept.** Every capture's raw pre/post `ioreg` pair is kept as data and authenticated at harvest; a missing
pair is disclosed. The registry's 60 s snapshot limitation of revision 4 no longer limits the current rule, which
reads the SMC once a second; the registry still supplies the charging and AC state, polled every 5 s.

## 10. Changes after the seal, and registered deviations

None to §§3–9 for an armed or completed attempt. A rule, threshold, catalog effect, roster or blinding change is a
prospective cold erratum (one judge, one refuter), settled in one erratum. The §3 frequency redraw needs no erratum.
A larger per-member time allowance after a deadline stop (§5.5) does need one. The allowance is a value of the sealed
sizing output (`sizing_b5.json`, `member_allowance_s`), and no program derives a new one from an observed member
cycle: the sizer (`scripts/size_b5_window.py`) takes no such input, and its `--check` mode passes only when it
reproduces the sealed file byte for byte. A larger allowance is therefore a cold erratum with a new sizing file. The
new file is pinned by an addendum to the seal record (§12: the record that pins each sealed file by its SHA-256; an
addendum adds a pin to it), and the question goes to a consult first. The new file is a separate file, never an
edit of `sizing_b5.json` committed in the measurement checkout: `sizing_b5.json` is a window input (§9.1), so such
a commit would remove the next window (`code.executed_differs_from_sealed`). The plan writer does not need the
sealed file: it takes an allowance's source as any file inside the measurement checkout, named by its path and its
SHA-256 (`joulewise/b5/plan.py` `read_allowance`), so the new file is placed there untracked, outside `joulewise/`,
`scripts/` and the pack, for example under the ignored `runs/` directory (an untracked file under those three
would itself be a difference, §6.5). A review finding that concerns only how something is recorded (receipts,
naming, schema formality) is dispositioned "flag, not refuse" and never sent to a fix round.

**Registered deviations from committed bytes, made prospectively here:**

1. The chain passes `--max-failures <expected_count>` in place of the packs' literal `1` (§5.2).
2. The plan trees' `attempt_policy` is superseded by the flag catalog (§5.2).
3. The NEG-8 bound may be derived from 10 or 11 corpus members (§5.3).
4. Analysis: D-179 ruling 1 ("no member is excluded after collection"; no reduced mean) and D-078's no-reduced-mean
   text are amended by §6.6 and analysis plan §2.2 and §4, as Ed's 2026-10-05 ruling requires; GAMMA's prospective
   manifest's fixed n = 10 quads becomes "at least 5 kept quads" (analysis plan §7).
5. The chain passes `--arm-countdown-s 0` on every collection stage, in place of the literal 20 that each of a
   pack's ten collection stages carries (§5.1).
6. The chain adds two arguments to both calibration capture stages (the pre and the post slot), which carry neither
   in the packs: `--arm-countdown-s N` and `--sleep-display-before-capture` (§5.1).
   - *The countdown.* N is 0 for the pre slot and 20 for the post slot. With no such argument the capture tool
     (`scripts/validate_powermetrics_fiducial.py`) counts down for its default, 0 s. So against pack bytes the pre
     slot is unchanged at 0 s and the post slot gains 20 s. The 20 is not a pack literal: it is the countdown that
     the block-3 runbook's calibration step passes for every slot (`docs/phase_2/window_runbook.md`,
     `calibrate_slot`). Against that runbook the pre slot drops 20 s, because a 60 s settle already precedes it, and
     the post slot keeps 20 s, because no settle does.
   - *The display sleep.* The second argument makes the capture tool run `pmset displaysleepnow`, the macOS command
     that turns the display off at once, after the countdown, and then wait 5 s before the capture starts. The
     runbook's calibration step passes it too. If the command fails, the capture goes on and the failure is recorded
     as `calibration.writer_record_flagged` with kind `display_sleep_action_failed` (§6.10).
   - The program that writes the chain script refuses a pack whose calibration stage already carries either
     argument (`joulewise/b5/chain.py` `calibration_runbook_flags`, `stage_argv`).
7. Analysis: the number printed beside a reported cell as its attribution floor. D-179 ruling 4 names "the D-078
   approximately 1-J attribution limit" as that number, and the contract `docs/contracts/paper_reported_energy.md`
   "the approximately 1-J D-078 attribution floor".
   Block 5 prints the cell's own value, computed by the formula of §0.10 from the window's own members (§14 Q5).
   What does not change: the floor is labelled beside the cell and never added into its interval, and the
   reported-energy code keeps its label for that rule, `labelled_beside_never_composed`
   (`joulewise/paper_reported_energy.py`).

The chain's other changes of round 2 (the 60 s settles, the window calibration verdict, the wall budgets, the
collection deadline, the corpus retry) and the spare-slot retry of revision 7 are not deviations from pack bytes: they
are the chain's own steps, listed in `joulewise/b5/chain.py` `DEVIATIONS` and registered in §5.1, §0.6 and §0.12.
(That list also carries deviations 1, 3, 5 and 6 above; deviation 6 is its second entry.) The spare members
themselves are committed bytes that each pack's plan tree pins (§0.12).

## 11. Commit rule and the sealed inventory

*The problem this section solves.* Every block-5 number has to come from code and configuration that the seal
fixed. That takes one named commit, H_claim, whose files the windows read, and a comparison of every window with
it. Git puts one obstacle in the way. A commit's name is a hash (a fixed-length digest, like the SHA-256s in this
file) computed over everything the commit contains. So a file cannot hold the name of the commit that contains
it: writing the name into the file would change the hash. The sealed inventory names H_claim in its `head` field.
It can therefore only be committed in a later commit than H_claim, and the commit a window runs from is never
H_claim itself. A comparison that read every difference between those two commits as "the code changed" would
remove every window from the claims, merely because the seal had been committed. This section fixes which commits
may follow H_claim, which differences count, and which program checks each. §12 gives the order in which the
seal's own commits are made. The procedure was written and rehearsed by the seal-landing lane
(`/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/SEAL_LANDING.md`; a path written `seal-land/…` below
is a file of that directory), and that lane's code is part of H_claim.

*Terms.* Three git words first. A file is **tracked** when git records it in commits. A checkout's **HEAD** is the
commit it currently has checked out. A commit's **parent** is the commit it was made on top of, and the later one
is the parent's **child**.

- **Measurement checkout** (§2 item 5): the dedicated clone the windows run from. A **desk checkout** (§0.18) is
  any checkout of the repository other than the measurement checkout. "The desk checkout", here and in the
  passages the seal gate wrote, is no one particular checkout: it is whichever desk checkout a desk program (the
  harvest, the analysis) is run from after a window, and its commit is what an addendum pins (item 4). Under the
  rule of item 2 no part of a window runs from a desk checkout.
- **Window input.** A tracked file whose bytes a window can read while it is planned, armed or run. Item 2 states
  the class by path.
- **Seal documents.** Three files of this directory: `sealed_inventory.json`, this file and
  `analysis_plan_block5.md`. Their final bytes cannot exist at H_claim: the inventory names H_claim, and the two
  texts print H_claim, the seats of the seal gate and the path of the seal record.
- **Seal commit.** The one commit whose only parent is H_claim and which changes only seal documents. It carries
  the inventory in its sealed form (item 2) and the sealed text of this file and of the analysis plan.
- **Seal record** (§12): the file that lists H_claim, the seal commit and the SHA-256 of every sealed file. An
  **addendum** is a section appended to it later. The **record commit** is the child of the seal commit that adds
  the seal record to the repository.
- **Pin-only commit** (§0.18): a commit that changes only the ledger pin,
  `configs/calibration/calibration_ledger_head.json`, which is data that advances after each window.
- **Record-only path.** A tracked path that no window reads: a document, a test, a status file. Item 2 states the
  class by path.
- **Executed head.** The measurement checkout's HEAD as the driver records it at a window's arm (§0.18).
- **The two stages of the seal gate** (§12). Stage 1 ruled on revision 9 of these documents on 2026-10-07 and
  required changes to them and to the harvest program. Stage 2 judges the final text.

*The picture.* Commits run from left to right. A run of dashes joins a parent to its child, `...` stands for
earlier commits, and a vertical line ending in `+--` attaches a label to the commit above it. The case drawn is a
block in which no pack is re-armed and no attempt is abandoned.

```
 main                  ... -- B ---------------------------------------- M
                               \                                        /
 integration branch             ... -- C --------- S --------- R ------+
                                       |           |           |
                                       |           |           +-- R, the record commit: adds the seal record
                                       |           +-- S, the seal commit: changes only the three seal documents
                                       +-- C, H_claim: the last commit that changes a window input

 measurement checkout           ... -- C -- S -- p1 -- p2
                                            ^    ^     ^
                                            |    |     +-- HEAD when GAMMA-1's plan is written
                                            |    +-- HEAD when BETA-1's plan is written
                                            +-- checked out here; HEAD when ALPHA-1's plan is written
```

- *main*: the repository's main branch. *B* is the commit at which the integration branch left it; the `\` under B
  is that parting, and the `/` under M is the integration branch joining main again.
- *integration branch*: `integrate/2026-10-07-int5` (§2 item 1). *C*, *S* and *R* are three consecutive commits on
  it: H_claim, the seal commit and the record commit.
- *M*: the commit that joins R into main when the seal's pull request is merged (§12 step 5). It is a **merge
  commit**, a commit with two parents, so C and S stay in main's history. While main has not moved since B, M holds
  exactly R's files.
- *measurement checkout*: a clone, so it holds the same C and S. It is checked out at S.
- *p1*, *p2*: the pin-only commits that the pin advance makes in the measurement checkout after ALPHA-1 and after
  BETA-1 (§4.6 item 6). A re-armed pack or an abandoned attempt adds one more each.
- *the three carets* (`^`): the measurement checkout's HEAD at the moment each window's plan is written. Each plan
  records that commit as its `measurement_head`, and the driver records the same commit as the executed head when
  the window arms. A harvest compares the head its window ran from (S, p1 or p2) with C.

1. **H_claim** is the commit of §2 item 1: the last commit that changes a window input before the block's first
   window. The seal commit follows it directly and changes no window input, so every window input has the same
   bytes in the seal commit as in H_claim. The measurement checkout is checked out at the seal commit (§12 step 6).
   Wherever this file says that the measurement checkout's HEAD is "H_claim plus pin-only commits", it means this
   chain and no other: H_claim, then the seal commit, then zero or more pin-only commits. An **extension** of
   H_claim is any commit made in the repository after the seal commit and before the block closes, on whichever
   branch and in whichever checkout it is made; it need not lie in that chain. Four classes are allowed. Only
   class (i) is ever committed in the measurement checkout; classes (ii) and (iii) never enter it; class (iv)
   enters it only after the seal has been made again around it, with the cure's commit as the new H_claim (the
   paragraphs after the list say why). After the seal commit, H_claim is extended only by (i) pin-only commits
   from this block's pin advances (§4.6 item 6), each of which changes only
   `configs/calibration/calibration_ledger_head.json`;
   (ii) gated R3 fixes to code that does not run during collection, which land in the desk checkout only: the
   measurement checkout never receives them during the block, the harvest and the analysis run from the desk checkout
   and take the measurement checkout as their input (`measurement_root`: the sealed documents and the verdict writer
   are read and run from there), and the arm's executed inventory is compared with the sealed inventory in the
   measurement checkout, so such a fix raises no `code.executed_differs_from_sealed`; (iii) commits touching only
   `docs/`, `tests/`, `RUN_STATE.md` or `TASK_QUEUE.md`; (iv) a §7.5 cure confined to collection code no completed
   window executed. Each extension carries its changed-path map, checked before the next arm.

   *What the map is, and who checks it.* A **changed-path map** is the list of paths whose committed bytes differ
   between H_claim and a later commit, as `git diff --name-only --no-renames` prints it. (With `--no-renames` git
   lists both the old and the new path of a moved file, so a file moved out of its directory is still listed.) For
   the measurement checkout the map between H_claim and HEAD must name the three seal documents and the ledger pin
   and no other path. Before an arm that is secured in three ways. First, the pin advance commits the ledger pin
   alone and then lists the paths its commit changed; if the list is anything but the ledger pin it stops with an
   error (`joulewise/b5/plan.py` `advance_ledger_pin`). Second, when the measurement checkout is set up, the lead
   checks the map between H_claim and its HEAD (§12 step 6). Third, commits of classes (ii) and (iii) are made in a
   desk checkout, on the main branch or on a branch that is later merged into it, and they are never committed,
   merged, pulled or checked out in the measurement checkout (§12 step 8), so no window can arm from them. That is
   what "land in the desk checkout only" means in (ii): such a fix is pushed and merged like any other commit, and
   the one place it may not reach during the block is the measurement checkout. After the window the
   harvest computes the map between H_claim and the executed head by code and records it (item 2). The harvest's
   computation is the one every claim rests on. The collector that runs inside the arm is not such a check. It is
   given the plan's `measurement_head`, and the installer of the launchd job (§0.17) refuses a plan whose
   `measurement_head` is not the measurement checkout's HEAD (`joulewise/night_agent_install.py`). So a plan's
   `measurement_head` is the seal commit for the first window and the latest pin-only commit afterwards, never
   H_claim, and at the arm that collector compares HEAD with itself.

   *What the comparison of item 2 does with a commit of each class*, if the measurement checkout holds it when a
   window arms:
   - (i) raises nothing. The path is listed in the window's record (`derived/code-identity.json`, item 2).
   - (ii) would be a difference if it ever reached the measurement checkout: the window would be
     `code.executed_differs_from_sealed`. Such a fix changes files under `joulewise/` or `scripts/`, the driver
     inventories every tracked file there whether a window executes it or not, and no program can tell "does not
     run during collection" from "runs". That is why these fixes stay out of the measurement checkout. They never
     need to be in it: `scripts/harvest_b5_window.py` imports the harvest from the checkout that holds the script,
     and reads the pack, the ledger, the ledger pin, the sealed inventory, the catalog, the identity pins and this
     file from the `measurement_root` that the window's plan names. One part of the harvest does run the
     measurement checkout's code: with `--prepare-desk`, the whole-window verdict (§0.17) is written by the
     measurement checkout's `scripts/run_campaign.py`, run with that checkout's Python environment (its `.venv`),
     so the verdict writer is always the sealed one.
   - (iii) raises nothing, and the paths are listed. One file under `docs/` is not of this class:
     `docs/phase_2/window_runbook.md` is a window input (item 2).
   - (iv) is a difference for every window armed after the cure, because the cure changes window inputs and the
     inventory still names the old H_claim. A cure of class (iv) therefore **re-issues the seal**: the cure's commit
     becomes the new H_claim, and a new seal commit, its child, carries an inventory generated from it whose
     `head` names it. An addendum to the seal record lists the new H_claim, the new seal commit and the new
     inventory's SHA-256, beside the changed-path map and the re-audit that §7.5 requires of the cure. For a window
     armed after the re-issue, "H_claim" in item 2 is the `head` of the re-issued inventory.

   *A re-harvest after a re-issue.* The **inventory in force at a window's arm** is the `sealed_inventory.json` that the
   measurement checkout held when that window armed. Every harvest reads the inventory from the measurement checkout
   unless it is told otherwise, and keeps a copy of what it read in its archive, at
   `sources/inputs/sealed_inventory.json`. After a re-issue the measurement checkout holds the new inventory, and a
   window that armed before the re-issue differs from it by the cure itself. So an R3 re-harvest of such a window is
   given the inventory in force at its arm, with `--sealed-inventory-path <that window's first harvest
   archive>/sources/inputs/sealed_inventory.json`. Without it the harvest would exclude a completed window for a cure
   that the window never ran. This is a rule the lead applies, and the magistrate's brief (§7.2) carries it. *Worked
   example (a probe of the independent review of the seal-landing lane, `seal-land/REVIEW.md`, finding F5; a synthetic
   window, harvested by the program at H_claim):* ALPHA-1 ran from the first pin-only commit; then a cure to one file of
   GAMMA's pack and its new seal commit followed. Harvested again with the inventory then in the measurement checkout,
   ALPHA-1 was excluded: the head comparison (comparison (b) of item 2) listed the GAMMA file as a changed window
   input. Harvested again with the inventory in force at its arm, it raised no flag. Under the rule of item 2 a
   change in another pack's directory no
   longer excludes, but a cure to a file under `joulewise/` or `scripts/` that only GAMMA executes still would, because
   every window inventories those two directories whole.
2. **The sealed inventory** (`sealed_inventory.json`) lists, at H_claim, the SHA-256 of every tracked file under
   `joulewise/`, `scripts/` and the three pack directories (§0.7), and of this directory's `flag_catalog.json`,
   and it names H_claim as its `head`. Because it names H_claim it is committed in the seal commit, the child of
   H_claim, and not in H_claim. At H_claim the file is a stub (`status` `STUB_NOT_SEALED`, `head` and `files`
   null). In the seal commit it has `status` `SEALED`, `head` equal to H_claim, and the `files` map. It does not
   list the ledger pin (data). It declares no `roots` key: with that key an inventory could narrow the comparison
   to named directories, and none is needed, because the programs already compare under each window's own roots
   (comparison (a) below). It covers the hazard path: `joulewise/hazards/*`,
   `joulewise/b5/{driver,plan,chain}.py`, `joulewise/window_lineage.py`, `joulewise/flags/*`,
   `scripts/run_night.py`, `scripts/hazard_monitor.py`, `scripts/write_b5_window_plan.py`,
   `scripts/run_campaign.py` and the measurement core (the modules that run one member and reduce its records).
   This directory's `identity_pins.json` and `sizing_b5.json` are not in it; the seal record pins them (§12).

   *How it is made and checked.* On a checkout of H_claim with no uncommitted change, take every tracked path,
   as `git ls-files` prints them, under `joulewise/`, `scripts/` and the three pack directories, add the catalog,
   and record the SHA-256 of each file. The seal commit is then checked by `tests/test_b5_seal_landing.py`, which
   reads the repository's stored commits and never the files on disk. It proves three things: the inventory's
   `head` is a commit, and the last commit that changed the inventory has that commit as its only parent; that
   last commit changes nothing but seal documents; and the inventory lists exactly the tracked files of `head`
   under those five directories plus the catalog, each with the SHA-256 of its bytes at `head`. *Worked count:*
   at commit `9395cecfb`, the integration branch's latest commit when this was written, the five directories hold
   150, 165, 123, 123 and 120 tracked files (`git ls-files`, counted by this author), so an inventory made there
   lists 681 + 1 = 682 files. The count at H_claim is the length of the sealed `files` map.

   *Two comparisons tie a window to it.*

   *(a) File by file.* The window's **executed roots** are `joulewise/`, `scripts/` and the window's own pack. At
   each arm the driver writes the executed-file inventory (§0.18), the SHA-256 of every tracked file under those
   roots, and the arm's executed-code collector hashes the same files for itself. The collector at the arm, and
   the harvest afterwards from the driver's inventory, each compare those digests with the sealed inventory. A
   changed, missing or added file is `code.executed_differs_from_sealed`. The comparison is made under the executed
   roots only, because a window's executed-file inventory covers only its own pack: the other two packs' sealed
   files are not read as missing (§14 Q2). For a floor-pack window that is 150 + 165 + 123 = 438 of the 682 files
   of the worked count, and for GAMMA 435. The other checks behind that flag (the chain's sidecar, tracked edits,
   untracked files under the executed roots) are in §6.5.

   *(b) Head against head.* The harvest runs `git diff --name-only --no-renames -z <the inventory's head>..<the
   executed head>` in the measurement checkout (`-z` makes git print each path unquoted, so a path is classed by
   its real first characters) and puts every path it lists in one class. A **claim pack** is one of the three
   packs of §0.7.

   | Class | Paths | What the harvest does |
   |---|---|---|
   | pin-only | the ledger pin | lists it |
   | seal document | the three seal documents | lists them |
   | record-only | a path under `docs/` other than the runbook named below; a path under `tests/`; a path under a top-level directory whose name begins with a dot (`.github/`, for example); a file at the repository's root whose name ends in `.md` | lists it |
   | another claim pack | for a window of one claim pack, a path in the directory of either of the other two | lists it |
   | window input | every other path: all of `joulewise/`, `scripts/` and `configs/` outside the rows above; the file `docs/phase_2/window_runbook.md`; and any path that no row above names, such as `pyproject.toml`, the environment lock `env/mac-measurement-lock.txt` (the list of Python packages the measurement environment is built from) or a Python file at the repository's root | `code.executed_differs_from_sealed` (EXCLUDE_WINDOW) |

   Why the rows are drawn this way. The runbook is a window input because the plan writer copies the runbook's
   pre-calibration screen, a block of shell text, into the chain (§5.1). Record-only is a list of named places, and
   everything not named is a window input, so that a new kind of file is compared until someone shows that no window
   reads it: a Python file at the repository's root, for example, could be imported by every script. Another claim
   pack's directory is only listed because a window executes its own pack alone. The files a window reads from outside
   its pack (the window references, the spares, the NEG-8 corpus, the policy, the acceptance) are pinned by its own plan
   tree and compared by the pack-identity check (`pack.identity_mismatch`, §6.5), and the places they live in stay
   window inputs. A path that differs from a window input's path only in letter case is itself a window input, because
   the measurement Mac's disk does not distinguish case: a tracked `Joulewise/x.py` lands in `joulewise/`. The ledger
   pin and the three seal documents match by their exact names only.

   For `identity_pins.json`, `sizing_b5.json`, the flag catalog and the runbook, comparison (b) is the only check
   that a program makes of their bytes against H_claim. None of them lies under a window's executed roots, so
   comparison (a) does not reach them (the catalog is listed in the sealed inventory, but (a) covers the executed
   roots only), and no plan tree pins them.

   The harvest writes what it found to `derived/code-identity.json` (schema `joulewise.b5_code_identity.v1`): `h_claim`;
   `h_claim_source` (`sealed_inventory` when the inventory named the head); `plan_measurement_head`; `executed_head`;
   `sealed_inventory_sha256`; `comparison` (`compared` when git listed the changed paths, `identical` when the two heads
   are one commit, `git_diff_unavailable` when git could not make the list, `not_compared` when one of the two heads is
   not known); `changed_paths` by class; and `driver_checkout` (below). When git cannot make the comparison, the window
   is `code.identity_unmeasured` (§6.5), a harvest problem first (§7.2). That happens when H_claim is missing from the
   clone, which is why the measurement checkout is a full clone, one that holds every commit (§12 step 6). A sealed
   inventory that names no `head` is `code.identity_unmeasured` as well: there is then no sealed commit to compare with.

   *The checkout the driver runs from.* The launchd job (§0.17) starts `scripts/run_night.py` in the checkout whose
   `scripts/install_night_agent.sh` installed the job. The driver, the hazard modules of the arm, the monitor, the
   collectors, the G10 program and the meter program are that checkout's files; the programs the chain runs are the
   measurement checkout's. **The launchd job is installed from the measurement checkout**, by that checkout's own
   installer, so the two are one checkout and the executed-file inventory describes all the code a window ran. If the
   job was installed from another checkout, the driver records that checkout in the executed-file inventory under
   `driver_checkout`: its path, its HEAD, its `git status`, and the SHA-256 of each tracked file under its `joulewise/`
   and `scripts/`. The harvest then judges it as it judges the measurement checkout. A code file there that differs from
   the sealed inventory is a difference (`code.executed_differs_from_sealed`), and so is a tracked edit, or an untracked
   file under its `joulewise/` or `scripts/`. A separate checkout whose bytes equal the sealed ones is recorded and is
   no difference. This is decided at the harvest, from bytes. It is not decided at install from where a checkout lives:
   that would be a refusal for a reason that is neither physics nor number integrity (§6.11). *Worked example.* The
   real-model rehearsal of 2026-10-06 (not a claim window) ran with a separate driver checkout: its record lists 304
   code files there, none differing from the inventory (`seal-land/ab-lane-code-identity.json`). In a probe of the same
   review (finding F1) a driver checkout with one line appended to each of `joulewise/b5/driver.py`,
   `joulewise/hazards/clock.py` and `scripts/hazard_monitor.py` was recorded with those three files listed. Under the
   rule above that window is `code.executed_differs_from_sealed`.

   *What the harvest program at H_claim does instead.* The table and the paragraphs above state the rule every
   block-5 harvest applies. Five parts of it are installed by the harvest lane of item 4, after the seal. The
   harvest program listed in the sealed inventory, the one at H_claim, does this in their place:
   - a driver checkout whose code files differ is written to `derived/code-identity.json` with the list of
     differing files, and raises no flag;
   - record-only is every path outside `joulewise/`, `scripts/`, `configs/` and the runbook, so a changed
     `pyproject.toml`, environment lock or root-level Python file raises no flag;
   - with an inventory that names no `head`, the harvest takes the plan's `measurement_head` in its place, compares
     the executed head with itself and records `h_claim_source` `plan`, with no flag;
   - a changed path whose name is not valid UTF-8 text (the encoding the harvest expects of a path) makes the
     harvest fail (HARVEST_FAULT, §7.1);
   - a change confined to another claim pack's directory is a difference.

   No block-5 window is harvested by that program: ALPHA-1's harvest waits for the lane (item 4). The arm's
   collector is collection code and keeps H_claim's classes; as item 1 says, at the arm it compares HEAD with
   itself. None of the five cases can arise in the registered sequence, in which the launchd job is installed
   from the measurement checkout and the pin advance is the only program that commits there.

   *Worked example (a rehearsal on a throw-away clone, not a claim window;
   `/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/proof-landing.log`).* Commit `2737ef88c` stood in for
   H_claim. The inventory made from it listed 682 files. The seal commit changed exactly the three seal documents, and
   an inventory made again at the seal commit had the same `files` map. Then came one commit of two record-only paths
   and one pin-only commit. Given that H_claim, the collectors classed the changed paths as 1 pin-only, 3 seal
   documents, 2 record-only and 0 window inputs, for each pack, and comparison (a) found 438 executed files against 438
   sealed files in the window's roots for each floor pack and 435 for GAMMA, with none changed, missing or added. No
   flag was raised. Each of four further changes, one commit on top, was a difference: an edit to
   `joulewise/b5/harvest.py` by both comparisons (class (ii) reaching the measurement checkout); an edit to the runbook
   and an edit to `identity_pins.json` by comparison (b) alone; and an edit to GAMMA's plan tree by both comparisons for
   a GAMMA window and by (b) alone for an ALPHA window, which is the last case of the list above. The review of item 1
   then repeated the whole sequence (`seal-land/REVIEW.md`). It made sixteen changes to window inputs (an edited byte, a
   new file, a deleted file, a moved file and a changed file mode among them), each of which excluded the window, and
   commits of the permitted kinds (pin-only, the seal documents, documents and tests), none of which did. The Fable
   delta cold pass 5 (`/Users/edr/night-archive/gate-prune/cold-pass-5/REPORT.md`, PASS WITH NOTES) found that same last
   case, in which the program at H_claim excludes a window that read nothing changed, and assigned it to the harvest
   lane.

   *A new sizing file.* `sizing_b5.json` is a window input, so the new sizing file of a §5.5 erratum is never a
   changed `sizing_b5.json` committed in the measurement checkout: that commit would exclude the next window. The
   plan writer accepts as the source of an allowance any file inside the measurement checkout whose bytes hash to
   the digest the plan-input file gives (`joulewise/b5/plan.py` `read_allowance`). The new file is therefore a new,
   untracked file there, outside `joulewise/`, `scripts/` and the pack (under the `runs/` directory, which git
   ignores, for example), and the seal record's addendum pins its SHA-256 (§10).
3. **Retired, not deleted.** The `TRANSACTION_PACK` route (ARM, GO, consumption and lifecycle in
   `joulewise/arm_readiness.py`, except the lineage helpers the hazard lineage dispatches through;
   `arm_readiness_evidence.py`, `arm_readiness_evidence_t0.py`; `scripts/capture_t0_step.py`,
   `author_arm_evidence_t0.py`, `author_arm_readiness_evidence.py`, `generate_arm_readiness.py`,
   `launch_window.py`; the network-time OFF receipt admission and `joulewise/dwell.py`) and the block-4 machinery
   (the plan writer, the harvest scripts and the qualification module of block 4, the separate qualification
   window that §3 folds into block 5) stay in the tree with their tests green. Block 5 does not use that route: a
   block-5 plan carries the receipt class `HAZARD_PACK` (§0.17), and the driver takes its hazard branch for that
   class (`scripts/run_night.py`). What a test proves about this is narrower than revisions 3 to 11 said ("an
   import-graph test proves the hazard path cannot reach them"). The test, `tests/hazards/test_import_graph.py`,
   follows every import, direct or through another module, from two starting sets: the `joulewise/hazards`
   package with `scripts/hazard_monitor.py`, and the `joulewise/flags` package. It proves that neither set reaches
   a retired module, and it runs a complete arm and monitor in a fresh Python process and finds no retired module
   loaded. It names one exception: the arm's instrument cadence probe (§4.1) runs the production sampler adapter
   in a child process, and that adapter imports the measurement core. The test says nothing about the rest of the
   hazard path of item 2, and that rest does import retired modules: `scripts/run_night.py` imports
   `arm_readiness`, `arm_readiness_evidence_t0`, `t0_rehearsal` and `network_time_off` when it is loaded;
   `scripts/run_campaign.py` and `joulewise/bundle.py` import `arm_readiness` when they are loaded; and
   `joulewise/b5/plan.py` and `joulewise/window_lineage.py` import one function from it, the pack-tree digest,
   inside a function. So files of the retired route are loaded during a block-5 window, and they are sealed and
   compared like every other file under `joulewise/` and `scripts/`. Their deletion is proposed to Ed after
   GAMMA's harvest under his pruning rule (a mechanism that has caught nothing bearing on a number in its last
   three sessions is proposed for deletion).
4. **Written blind, pinned before use.** The harvest program (L5) is pinned by an addendum to the seal record before
   ALPHA-1's harvest; the analysis code (L9) before the release event (analysis plan §11). Each addendum names the
   files and their SHA-256s and the desk checkout's commit, and is written by a seat that has read no claim-window
   energy. The harvest lane that the seal gate required (stage 1, 2026-10-07: reference losses `energy_unreadable`,
   `contention.unmeasured`, `battery.unmeasured`, `env.member_quiet_state_violated`, `battery.capture_pair_failed`; the
   malformed-flag candidate list narrowed to pre-harvest writers' codes) may change `joulewise/b5/harvest.py`,
   `joulewise/whole_window.py` (the replay's authenticity pass and `_derived_neg8_decision` only),
   `scripts/harvest_b5_window.py`, their tests and fixtures, and nothing the chain or the members execute. It lands in
   the desk checkout only: the measurement checkout's HEAD stays H_claim plus pin-only commits for the whole block, so
   no completed window executed the changed bytes and §7.5 does not supersede the block. The harvest runs from the
   desk checkout and reads the sealed documents and runs the verdict writer from the measurement checkout
   (`measurement_root`). ALPHA-1's harvest does not run until this addendum exists; `harvest.json` records the desk
   checkout's commit.
   The same lane carries five further changes to the harvest's comparison of a window's code with the seal,
   which item 2 states and which the lane's worklist
   (`/Users/edr/night-archive/gate-prune/wave-1007b/harvest-lane/WORKLIST.md`) numbers H-8 to H-12: a driver
   checkout whose code files differ from the sealed inventory is a difference (H-8); record-only is a list of
   named places (H-9); a sealed inventory with no `head` is `code.identity_unmeasured` (H-10); a changed path
   that is not valid UTF-8 text no longer makes the harvest fail (H-11); and a change confined to another claim
   pack's directory is listed and is no difference (H-12).

   *What pins the program that harvests.* The sealed inventory lists the harvest program's files as they are at
   H_claim. The lane changes those files in the desk checkout, so the inventory does not describe the program that
   harvests a block-5 window; the addendum does. No program reads an addendum. The binding is a rule: the analysis
   admits an attempt only when the harvest commit recorded for it is the commit the addendum pins (analysis plan
   §2.2), and otherwise the attempt is harvested again on identical bytes by the pinned program (R3).
5. **Records of their era are not live pins.** Two older documents carry digests of files as they were when the
   documents were written: revision 6 of the calibration preregistration
   (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, sealed 2026-09-30 at `46643f1d`) records
   `pins.validator_sha256` (`3dc75857…`), the calibration writer that produced block 1's derivation captures; and
   block 4's sizing source (`configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json`, `head`
   `bda1c180`) records the production files it sized from. Those files have changed since, as the gate-prune lanes
   required, so the digests no longer match today's tree, and they are not meant to: they say what ran then. The
   digest census (`scripts/digest_pin_census.py`, `ERA_RECORDS`) resolves each such digest against the file at the
   document's declared commit with `git show`, and the documents are not edited. Revision 6's
   `estimator_code_sha256` pins stay live, because the acceptance re-derives them. **The live pins of block 5 are the
   sealed inventory at H_claim** (item 2): a window is judged against the files H_claim holds, never against an era
   record.

## 12. Seal

*What a seal is.* A seal is a list of SHA-256 digests, each of a named file at a named commit, written after an
independent gate has judged those files. A file is sealed when its digest is in the list: any later change to it
shows as a different digest. This section says who judged, which commits carry the sealed bytes, where the list
lives, and what binds the files that no program compares with the list.

One cold gate (§0.1) seals this file, the analysis plan, the flag catalog and the sealed inventory together. It
has two stages, described next: stage 1 ruled on an earlier revision and required changes, and stage 2 judges
this text. The gate rules in particular on the
cell rule of §6.6, the catalog's effects (especially the two disclosed aggregate codes of §6.5), and the
sensitivity line of analysis plan §8 (adopted as amended at stage 1 of the gate).

- **Why two stages.** When the gate's questions were ready, the commit that would become H_claim was not yet
  fixed: one lane was changing the head comparison of §11, and these documents were being corrected against the
  code. A ruling that requires a code change costs little while that commit is open; once it is fixed, a code
  change costs a new run of the whole test suite and a new cold pass. So the rulings were taken first, and the
  judgment of the final text second.
- **Stage 1** (2026-10-07) judged revision 9 of this file, the analysis plan and the catalog as commit `9b0c680ed` holds
  them (the inventory was then the stub), with the code of that commit. The judge was a Fable 5.1 session. An Opus 5.5
  refuter attacked the same documents and code and reported five breaks, places where it showed a rule or the code to
  give a wrong outcome. The judge ruled on each: four were accepted with a cure, and for the fifth, the lost-midpoint
  rule of §0.12, the rule was confirmed and its stated premise corrected. The ruling is
  `/Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE1.md` (first line `STAGE 1: RULINGS COMPLETE`), and the
  refuter's record is `REFUTER_STAGE1.md` beside it. The ruling requires 48 changes to the text of this file and the
  analysis plan, one change to the catalog (the cell minimum of §6.6, from 8 to 5), and seven changes to code or to
  records in the code tree. Revision 12 applies the text changes as the judge wrote them. The catalog change is made
  before H_claim, because the catalog is a window input and its bytes are fixed there. Of the seven, three (the
  ruling numbers them K-1 to K-3) change entries of the refusal allowlist (§6.11), and one of the three, K-2, also
  changes a test fixture (a data file that a test compares against); no program running inside a window loads
  either file. The other four (K-4 to K-7) are the harvest lane of §11 item 4, which lands after the seal and
  before ALPHA-1's harvest.
- **Stage 2** is a separate session, held on the final text. It judges that text and the inventory made from
  H_claim: that the text differs from what stage 1 ruled on only by changes that each trace to a ruling or to a
  correction of fact, that every digest the seal pins can be computed again from the bytes it names, and that the
  seal's commits can be made as the steps below describe. It ends with one line, `SEAL: ADMIT` or `SEAL: REFUSE`.
  The seal commit is made only after `SEAL: ADMIT`.
- **Seats.** The seats of both stages, with their records: `FILL[B5-SEAL-SEATS]`.

**The order of the seal's commits.** The picture is in §11. Each step names the paths it may change and the check
that proves it.

1. **H_claim.** Its tree holds the final code, packs, flag catalog, identity pins, sizing output and runbook. This
   file and the analysis plan are present there in a draft state, and the inventory is the stub (§11 item 2);
   their sealed bytes exist only from the seal commit on. Checks: the whole test suite; the refusal census of
   §6.11; the `--check` mode of each generator (a program that writes a committed file from its sources, such as
   the sizing program of §5.5: `--check` passes only when it reproduces the committed file byte for byte); and
   CI, the checks GitHub runs on a pushed commit.
2. **The inventory** is made from a checkout of H_claim (§11 item 2).
3. **The seal commit.** Its only parent is H_claim. It changes `sealed_inventory.json`, this file and the analysis
   plan, and no other path. In it this file prints H_claim (§2 item 1), the seats and the path of the seal record,
   and nothing in this file is left to fill afterwards. Checks: `git diff --name-only --no-renames <H_claim>
   <seal commit>` lists only those three paths; `tests.test_b5_seal_landing` passes (§11 item 2); and the
   inventory made again on a checkout of the seal commit has the same `files` map. The last two are independent
   readings: the test reads stored commits, the generator reads files on disk.
4. **The record commit.** The child of the seal commit. It adds the seal record under `docs/process_traces/`,
   which is a record-only path. It also carries any test fixture that the seal commit's text forces to change. A
   fixture under `tests/` that names a line of a seal document, as `tests/fixtures/d165_rationale_allowlist.json`
   names lines of the analysis plan, cannot be corrected in the seal commit, which may change only the three seal
   documents. So the whole test suite and CI are required to pass at the record commit, which is the head of the
   seal's pull request, and not at the seal commit. Check: `git diff --name-only --no-renames <seal commit>
   <record commit>` lists no window input.
5. **The pull request to the main branch** is merged with a merge commit, never by a squash or a rebase. Those
   two methods replace the branch's commits by new ones: H_claim and the seal commit would then be absent from
   main's history, and both the test of step 3 and the harvest's `git diff` need H_claim.
6. **The measurement checkout** is a full clone, made without `--depth`, so that it holds every commit and
   H_claim among them. It is checked out at the seal commit. Checks: `git diff --name-only --no-renames <H_claim>
   HEAD` lists exactly the three seal documents; `git status --porcelain` prints nothing; and the record-only
   collectors of §4.1 step 4, run by the lead at the desk (`scripts/collect_window_flags.py --stage desk`, the first
   row of §6.1's table), given H_claim as `--h-claim` and the sealed inventory as `--sealed-inventory`, raise no
   flag whose code begins with `code.`.
7. **Plans and the launchd job.** Each plan's `measurement_head` and `repo_head` are the measurement checkout's
   HEAD when the plan is written (§11 item 1; `repo_head` is the HEAD of the checkout the installer runs from,
   which is the measurement checkout). The lead writes into each plan-input file the path and SHA-256 of this
   file and, as the source of its two sizing allowances (§5.5), the path and SHA-256 of the sizing output. The
   lead copies those digests from the seal record, not from the files in the checkout. The plan writer refuses
   when a named file does not hash to the digest it was given (`joulewise/b5/plan.py`), so copying the digests
   from the seal record makes the plan writer check both files against the seal. Naming this file is the lead's
   rule: the plan writer also accepts a plan input that names no registration. The launchd job is installed by
   the measurement checkout's own installer (§11 item 2).
8. **Between windows** the desk order is chain exit, pin advance, harvest (§4.6 item 6). Nothing else is ever
   committed, merged, pulled or checked out in the measurement checkout.

**The seal record** is the file `FILL[B5-SEAL-RECORD]`. It lists H_claim, the seal commit, the rulings of both
stages and the refuter's record, the seats, and these SHA-256s:

- at the seal commit: `sealed_inventory.json`, this file and `analysis_plan_block5.md`;
- at H_claim: `flag_catalog.json` (the seal commit does not change it); the three packs' plan trees; the model
  panel `configs/model_panels/qwen3_4bit.json`; the idle policy `configs/campaign_policies/quiet_mac_p2_b5.json`;
  the acceptance `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`; the pin bundle of the
  packs (§4.6 item 4: the prompt pin, the selection record and the ladder in each pack's `prefill_pin/`
  directory, nine files with three distinct digests); the sizing output `sizing_b5.json` (§5.5); the identity pins
  `identity_pins.json` (§4.6 item 3); and the chain-source document `docs/phase_2/window_runbook.md` (the chain
  embeds its pre-calibration screen).

No file lists the SHA-256 of the seal record, so no file has to contain its own digest. This file names the seal
record by its path.

**Two files keep the labels their generators wrote.** `identity_pins.json` and `sizing_b5.json` each carry
`"status": "UNSEALED_DRAFT"`, `"sealed": false` and a `note` that begins "UNSEALED DRAFT". These are labels that
the two generators (`scripts/write_b5_identity_pins.py`, `scripts/size_b5_window.py`) wrote before the seal. No
program reads them, and the seal does not update them: a changed byte would change the file's sealed digest, make
the generator's `--check` fail, and, being a change to a window input after H_claim, exclude every later window
(§11 item 2). Two sentences inside the files are left as written for the same reason: the identity pins' note
says "The seal replaces status", which the seal does not do, and the sizing output's note still carries an
unfilled marker for its own digest (`B5-SIZING-OUTPUTS`, §13). What seals each of the two files is its SHA-256 in
the seal record.

**After the seal commit this file's bytes do not change.** Each plan records this file's SHA-256 (step 7), and
the harvest fails (HARVEST_FAULT, §7.1) when the file it reads differs from the digest its plan recorded. A value
that exists only after the seal commit is therefore never written into this file. It is written as a named
section appended to the seal record: the regenerated plans (`B5-PLANS-REGENERATED`, §13), the release event
(`B5-RELEASE-EVENT`, §8), the pins of the harvest and analysis programs (§11 item 4), a new sizing file (§5.5), a
re-issued seal (§11 item 1), and the head each window ran from. The analysis plan is read by no program. If a
value is filled into it after the seal commit, its SHA-256 changes, and an addendum to the seal record states the
new digest.

**What no program checks, and the rule that covers it.**

1. *The seal documents against the seal record.* The head comparison of §11 lists a changed seal document and
   judges nothing by it, so a second commit to this file or to the analysis plan after the seal commit raises no
   flag. The harvest records the SHA-256 of what it read: this file's in `derived/harvest-thresholds.json`, the
   catalog's in `derived/window_flags.json`, the inventory's in `derived/code-identity.json`. Rule: an attempt is
   analysed only when those three digests equal the seal record's (for the inventory, the one in force at the
   window's arm, §11 item 1). An attempt for which they differ is harvested again on identical bytes with the
   sealed files (R3).
2. *The harvest and analysis programs against their addenda.* §11 item 4 gives the rule.
3. *The seal record.* No program reads it. It binds because anyone who holds the repository can compute every
   digest in it again from the commit it names.

## 13. Binding register

| Binding | FILL | Due |
|---|---|---|
| Commit | `H-CLAIM` | Seal |
| Sealed inventory | `sealed_inventory.json`: generated from the files of H_claim and committed in the seal commit, the commit that follows H_claim. The file names H_claim as its `head`, and a file cannot name the commit that contains it (§9.1, §11) | Seal |
| Dry render, dry arm | `B5-DRY-RENDER-RECORD`, `B5-DRY-ARM-RECORD`: filled in revision 9 (§2 item 6), at `fe28e5a0c`; the render is an L2 harness render. The census matcher changed after `fe28e5a0c`; §2 item 6 says why the dry arm's refusal holds under the merged rule, and §14 Q15 asks whether it is repeated at the final head | Before ALPHA-1 arms |
| Audit, seats | `416-AUDIT-RECORD`, `416-SEATS`: filled in revision 8 (§9.1); `416-DELTA-RECORD` (the diff-scoped passes over `a434e363d..fe28e5a0c`, §9.1): filled in revision 9; its second part (the code merged after `fe28e5a0c`: Fable's delta cold pass 5 at `9395cecfb` and the independent review of the seal-landing lane, §9.1): filled in revision 12; `B5-SEAL-SEATS` | Seal seats at seal |
| Sizing | `B5-SIZING-OUTPUTS`: draft values at `fe28e5a0c` (§5.5), unchanged since `d3c107f2f`, spares included; pinned at H_claim | Seal |
| Cooldown smoke | `B5-COOLDOWN-SMOKE-RECORD` (§2 item 7): filled in revision 6 | Seal |
| Plans | `B5-PLANS-REGENERATED`: every window plan and plan-input file written from the sealed §4.3 block (contention `clean_s` 180). The plans can be written only after the seal, so the record of their regeneration is a section appended to the seal record, not a value in this file, whose bytes are fixed at the seal (§8 item 3) | Before ALPHA-1 arms |
| P3 sync | `P3-SYNC-RECORD` (§2 item 8), with `P3-BATTERY-CODES` (§6.4, and the table below) and `P3-CLOCK-SKEW-BOUND` (§4.2): filled in revision 6 against `a434e363d`; the revision 7, 8, 9 and 10 sync records below cover what was merged since, against `d3c107f2f`, `43ac12d0c`, `fe28e5a0c` and `9b0c680ed`, and the revision 12 record covers the seal landing, against `9395cecfb` | Seal |
| Final hashes | `B5-FINAL-HASHES`: filled in revision 8 at `43ac12d0c`; recomputed in revision 9 at `fe28e5a0c` (`/Users/edr/night-archive/gate-prune/FROZEN_HEAD_4.md`), where only the identity pins changed (§0.7 plan trees, §4.6 item 3 identity pins, §5.5 sizing output). Open again because the head moved after `fe28e5a0c` (the census interpreter rule, §4.5, and what §2 item 1 lists after it): each digest so marked is computed again at one commit, H_claim. The marker stands for those digests only; the commit itself is the marker `H-CLAIM`. Revision 10 found each of them unchanged at the int5 head `9b0c680ed` (`B5-REV10-SYNC` below); the marks stay until H_claim is fixed, and revision 12 leaves them in place | Seal |
| Refusal allowlist | `roster.run_id_mismatch` listed under the member exclusions of `configs/gates/hazard_refusals.json` (§6.11): done at `d3c107f2f` (audit-fix item 7); `neg8.midpoint_lost_primary` listed under the window exclusions: done at `43ac12d0c` (ruling Q11); the file is unchanged at `fe28e5a0c`, at `9b0c680ed` and at `9395cecfb`. The seal gate's stage 1 then reworded two entries (what `cell.below_minimum` and `neg8.midpoint_lost_primary` protect: its changes K-1 and K-3) and ordered `g3.recompute_failed` removed from the window exclusions, where it disagrees with the catalog's DISCLOSE (K-2); the record of revision 12 below says where each stands | Seal |
| Disk | `BACKUP-DESTINATIONS`: filled in revision 4 (§5.6) | Seal |
| Identity pins | `identity_pins.json` (§4.6 item 3): draft at `fe28e5a0c`, with the sealed `neg8_reference` unit (`754c8c093`) and the spares; pinned at H_claim | Seal |
| Blinding | `B5-BLIND-CUSTODY-MAP`: filled in revision 12 (§8). `B5-RELEASE-EVENT`: a section appended to the seal record once the block has closed, not a value in this file (§8 item 3) | Map at seal; release event after the block closes |
| Boundary | `BOUNDARY-LABEL`: filled in revision 4 (§1) | Seal |
| Attribution floor | `ATTRIBUTION-FLOOR-BINDING`: filled in revision 12 by a formula, on the orchestrator's ruling of 2026-10-07; no number and no artifact is bound (§0.10, §14 Q5). The value is computed for each reported cell at the analysis | Formula at seal; value at the analysis |
| Harvest and analysis programs | Two addenda to the seal record (§11 item 4). The first pins the harvest program after the harvest lane that the seal gate required: the changed files, their SHA-256s and the commit of the desk checkout the harvest runs from. The second pins the analysis code (lane L9) | The first before ALPHA-1's harvest; the second before the release event |
| Seal | `B5-SEAL-RECORD`: the path of the seal record, a file committed after the seal commit (§12) | Seal |

Six names are filled last, by a step that runs once H_claim exists and puts each value in place of its marker
without changing another word. `H-CLAIM` is the commit `FILL[H-CLAIM]`: the last commit of the integration branch
that changes a window input (§9.1, §11). It carries `fe28e5a0c`, the census interpreter rule merged at `84661ddb3`,
the seal landing merged at `9395cecfb`, and the catalog change the seal gate's stage 1 ordered (§6.6).
`B5-FINAL-HASHES` marks each digest that is recomputed at that commit. `B5-SEAL-SEATS` and `B5-SEAL-RECORD` are the
seats of the seal gate and the path of the seal record (§12). `B5-PLANS-REGENERATED` and `B5-RELEASE-EVENT` name
records that can exist only after the seal; each is a section appended to the seal record, and its marker is filled
with that section's name (§8 item 3). The sealed inventory is not filled into this file at all: it is generated from
H_claim and committed in the seal commit (§11). `B5-SIZING-OUTPUTS` and the identity pins hold the values the seal
record pins. Filled in revision 6: `B5-COOLDOWN-SMOKE-RECORD`, `P3-SYNC-RECORD`, `P3-BATTERY-CODES`,
`P3-CLOCK-SKEW-BOUND`. Closed in revision 7: the refusal-allowlist item. Filled in revision 8: `B5-FINAL-HASHES` (open
again in revision 9, for the digests at the final head only), `416-AUDIT-RECORD`, `416-SEATS`; Q11 closed (§14).
Filled in revision 9: `416-DELTA-RECORD`, `B5-DRY-RENDER-RECORD`, `B5-DRY-ARM-RECORD`; Q12 closed (§14).
Revision 10 filled nothing: it
restated the census interpreter rule from the merged code, added the sync record `B5-REV10-SYNC`, and opened Q14 and
Q15 (§14). Revision 11 filled nothing: it corrected statements of fact against the code at `9b0c680ed`. Filled in
revision 12: `B5-BLIND-CUSTODY-MAP` (§8), `ATTRIBUTION-FLOOR-BINDING` (a formula; Q5 closed, §14) and the second part
of `416-DELTA-RECORD` (§9.1); Q6 closed, and Q9, Q11 and Q12 confirmed, by the seal gate's stage 1 (§14). The
analysis plan's own FILLs (analysis plan §13), including the L9 adapters and lane L9-NEG8, are listed there.

**P3 sync record** (`P3-SYNC-RECORD`, revision 6). Revision 5 described the behaviour below from the rulings, before
the code had it. Each row was read in the frozen head `a434e363d` (`/Users/edr/code/JouleWise-wt-int4`); the last
column says whether the code matched revision 5's text or the text was changed to match the code.

| Sync point | Code at `a434e363d` | Text |
|---|---|---|
| battery member rule on SMC 1 s reads, assist disclosed, the codes for each predicate (`P3-BATTERY-CODES`) | `harvest.battery_join`, `_battery_assist`, `accumulator_member_flags`. The codes: `battery.member_span` (a charging current; charging or AC lost), `battery.accumulator_excursion` (the charge accumulator; a sign-inconsistent discharge accumulator), `battery.unmeasured` (missing state evidence, including the 120 s state hole under SMC coverage), `battery.smc_unavailable`, `battery.assist` and `battery.assist_outside_request` (any negative read; −200 mA is the report's threshold), `battery.accumulator_activity`, `battery.accumulator_unavailable` | changed: §6.4 rewritten (any negative read; the code's three phases; the excursion code; the state hole; the energy as held time × power) |
| capture battery join on SMC reads; assist for captures and #421 pairs | `harvest._capture_battery_joins`, `_pair_assist`: `calibration.capture_battery_span`, `_unmeasured`, `_assist`, `_pair_assist`; `battery.capture_pair_assist` | changed: §6.3, §6.5 (capture assist has its own code; pair assist needs SMC coverage) |
| monitor and meter stopped no sooner than 5 s after the chain exits | `driver.MONITOR_POST_CHAIN_HOLD_S` = 5.0, `hold_monitors_after_chain`, after G10 | changed: §5.4 order (G10 before the stop) |
| clock samples with a large read skew re-read, then unmeasured, never a step (`P3-CLOCK-SKEW-BOUND`) | `clock.window_skew_max_ns` = step ÷ 4 = 250 µs, `ANCHOR_TRIES` = 5; harvest `_clock_point` applies the same bound | filled: §4.2 |
| meter driver wiring and harvest hook; restricted record; `meter.*` flags | `MonitorSupervisor` named `meter`, no restart on a clean exit; `meter.supervision_fault`; `harvest.meter_joins` | changed: §5.8 (one file `withheld/meter.json`; the request window only, no phases) |
| historical custody re-verified at harvest; the unmeasured code's name | `harvest.historical_custody`; scoped to the acceptance's captures (triage d) | changed: §6.10 (scope; `_mismatch_unused`; class NUMBER) |
| harvest drop reasons imported from the mint's set | imported from `whole_window.NEG8_MINT_DROP_REASONS` | matched: §5.3 |
| terminal ledger pin handed to the desk verdict | the committed pin must already be this session's terminal entry (`harvest._desk_pin_problem`), so the desk order is chain exit, pin advance, harvest | changed: §2, §4.6 item 6 (pin advance before the harvest) |
| member error-output files scanned for unwritten flags | `harvest._unwritten_core_flags` scans `operator-logs/member-stderr/` | matched: §6.10 |
| yield alerts queued by the watchdog | `magistrate_watchdog.queue_yield_alerts` | matched: §5.7 |
| `member.whole_window_member_failure` emitted | `harvest.whole_window_member_failures`; plus `whole_window.member_failures_unreadable` (P4) | matched: §6.3; new code in §6.5 |

**Catalog comparison** (revision 6). A script read, from `a434e363d`, every code named by the harvest's `CODES`
table, `joulewise.flags.catalog.DRAFT_CODES`, `joulewise.flags.core.CORE_FLAG_CODES`, `km003c_parse.CODES`,
`window_lineage.FINDING_CODES` and the literal codes of `joulewise/hazards/monitor.py`, plus the test fixture catalog
`tests/fixtures/b5_harvest/flag_catalog.json`, and compared each with this directory's catalog (family, class,
effect, blinding), then loaded the catalog with `joulewise.flags.catalog.load_catalog`. Before revision 6 (catalog at
commit `f3473b7a`): every emitted code was present, and one disagreement was not documented,
`calibration.historical_custody_unmeasured` classed REPRESENTATION here and NUMBER in the code. After: 178 codes,
none missing, none extra, the two never-classified codes absent, and four documented disagreements only:
`roster.run_id_mismatch` restated NUMBER and EXCLUDE_MEMBER here (§6.7) against the emitter's REPRESENTATION and the
fixture's DISCLOSE, and `g3.recompute_failed`, which the fixture keeps at its earlier effect EXCLUDE_WINDOW
(`tests/fixtures/b5_harvest/README.md`) against DISCLOSE here (§6.5).

**Revision 7 sync record** (`B5-REV7-SYNC`). The source list of required changes was the integration's REG list
(`/Users/edr/night-archive/gate-prune/REG_PENDING.md`: fix lane 2, fix lane 1, the NEG-8 lane) and the NEG-8 ruling.
Each row was read in the int5 head `d3c107f2f` (a read-only shared clone at `/private/tmp/regsync2/repo`, detached at
that commit); the last column says where the text changed, or that it already matched.

| Sync point | Code at `d3c107f2f` | Text |
|---|---|---|
| NEG-8 screen on the survivors; count-adjusted bound | `whole_window.evaluate_neg8_point_drift` (endpoint counts 2–3, midpoint 0–1, protocols `replicated_endpoints_with_midpoint` and `replicated_endpoints`), `neg8_count_adjusted_bound`, `neg8_family_endpoint_bound`; the verdict writer drops status losses (`run_campaign._idle_admission_core_evaluation`); the harvest drops flag losses and discloses (`neg8_screen`, `_neg8_rescreen`, `_neg8_disclose`) | changed: §0.12 (the ruling's text, adapted where the code differs: the retry runs after the 60 s settle; the flag names the record holding the bound instead of carrying it; `neg8.reference_lost` only below (3, 1, 3)), §5.3, §6.5 |
| spare-slot retry | `chain.spare_retry_lines`, `SPARE_RETRY_HELPER`, wall budget `neg8_spare_retry_decision` 300 s, horizon allowance 60 + 180 + 620 × k s; spares in `configs/campaigns/window_reference_spares_v5/`, pinned by each reference stage's `spare_retry` record | changed: §0.12, §5.1, §10 |
| corpus members dropped for physics | `harvest.neg8_corpus_physics` (`derived/neg8-clean-corpus.json`, `withheld/neg8-clean-bound.json`, `derived/neg8-corpus-physics.json`) | changed: §5.3 |
| yield minimums of the reference stages | `driver.REFERENCE_ENDPOINT_MIN_VALID` = 2, `REFERENCE_MIDPOINT_MIN_VALID` = 0; the harvest counts a spare only when it ran | changed: §5.7 |
| sizing and disk for the spares | `size_b5_window` `reference_spare_retry_s` = 5,424 s per pack; `plan.py` planned bytes include the 7 spares | changed: §4.2, §4.3, §5.5 |
| UNMEASURED at the arm | `hazards/arm.py`, `driver.normalize_decision`; `<module>.arm_unmeasured` | changed: §0.15, §4.1 |
| agent census | `agent_identity.filter_census` at every census site; in-window `census.unmeasured` never stops | changed: §4.5, §5.1, §5.7 |
| lineage publication | `driver.run_hazard_night`: `night_refused_pack_inventory_unusable`; `observed.science_members_expected_to_refuse` | changed: §0.17, §6.11 |
| desk identity files at the reservation | `reserve_calibration_window_bracket._hazard_desk_object`, kind `desk_identity_unreadable` | changed: §6.10 |
| malformed and unbuilt flag lines | `harvest._malformed_flag_line`, `_rebuild_unbuilt_flag`, `_unwritten_core_flags`; `NEVER_CLASSIFIED_CODES` empty | changed: §6.2, §6.10 |
| registry start time; torn lock | `measurement_liveness.publish_campaign`; runner kinds `registry_start_time_unavailable`, `torn_lock_cleared` | changed: §6.10 |
| powermetrics digest | harvest step `binary_identity`, `instrument.binary_identity_rederived` | changed: §6.3, §6.10 |
| monitor restarts; orphan groups | `MonitorSupervisor` `on_restart` writes `monitor.restarted`; `reap_orphan_monitor` writes `monitor.orphan_unverified` | changed: §5.4, §6.8 |
| sign-inconsistent discharge accumulator | `harvest.accumulator_member_flags(smc_covered=…)` and `hazards/battery.py`, in parity | changed: §6.4 |
| monitor skew bound | `hazards/monitor.build_config(clock_step_ns)` from the plan | changed: §4.2 |
| post-run guard collector exception | `environment_admission.post_run_observation_collector_raised`, read on the verdict path only (`e0a71cc2f`); the reducer unchanged | changed: §6.3, §6.10 |
| G10 | `driver._run_g10`, `_wait_supervised`, `G10_POLL_S` = 5 under the 1,500 s cap | changed: §3, §5.4 |
| desk pin order | `harvest._desk_pin_problem` kept; `whole_window.verdict_absent` relabelled NUMBER_INTEGRITY in the allowlist | matched: §2; changed: §6.11 |
| model identity supersession | `IDENTITY_SUPERSESSION_CHECKS["model_identity"]` = {`pins`, `members_compared`} | changed: §7.2 |
| OS metadata files in sources | the three source comparisons ignore `.DS_Store`, `.localized`, `._*` | changed: §6.5 |
| member flags scoped by bundle id | `exclusions.compute` resolves bundle ids through the roster | changed: §0.16 |
| `roster.run_id_mismatch` in the allowlist | listed, NUMBER_INTEGRITY; emitter and fixture NUMBER and EXCLUDE_MEMBER | changed: §6.7, §6.11 |

**Catalog comparison** (revision 7). The same script as revision 6, adapted to import the int5 head
(`/private/tmp/claude-501/-Users-edr-code-JouleWise/0a4039c8-3a55-4151-82ba-e66d8a0e9397/scratchpad/regsync7/check_catalog.py`),
read every code named by those tables at `d3c107f2f`, compared each with this directory's catalog, checked that
the superseded A1 window-exclusion code appears in none of them, and loaded the catalog with `load_catalog`. Before revision 7
(catalog at `c6843537`, 178 codes): 14 codes the code emits were missing (the five `*.arm_unmeasured`,
`monitor.orphan_unverified`, `records.malformed_flag`, the two malformed-flag exclusions, `records.flag_unbuilt`,
`records.operator_log_unreadable`, `instrument.binary_identity_rederived`, `neg8.reference_lost`,
`neg8.midpoint_lost`), and the same 14 were in the test fixture but not here; 28 open disagreements in all (14
against the code's tables plus 14 against the fixture; the documented `g3.recompute_failed` disagreement is not
counted among them). After: 192
codes, none missing, none extra, `collector.unmeasured` deliberately absent (§6.2), `load_catalog` OK, and one
documented disagreement only: `g3.recompute_failed`, which the fixture keeps at its earlier effect EXCLUDE_WINDOW
(`tests/fixtures/b5_harvest/README.md`) against DISCLOSE here (§6.5). The `roster.run_id_mismatch` restatement of
revision 6 is gone, because the emitter and the fixture now agree with the catalog.

**Revision 8 sync record** (`B5-REV8-SYNC`). The source list was the last section of the integration's REG list
(`REG_PENDING.md`, "From int5 phase 3 + cold-pass-2 fixes (d06ab4778) + N8 ruling") and the frozen-head record
`FROZEN_HEAD_3.md`. The earlier sections of that list were checked against revision 7's text and found applied. Each
row was read in the candidate H_claim `43ac12d0c` (a fresh read-only shared clone at `/private/tmp/regsync3/repo`,
detached at that commit; the integration worktree was not touched), from the diff `d3c107f2f..43ac12d0c`.

| Sync point | Code at `43ac12d0c` | Text |
|---|---|---|
| Q11: GAMMA attempt with a lost midpoint | `exclusions.PACK_SCOPED_WINDOW_REASONS`, `GAMMA_PACK_ID`; `compute` reads the roster's `pack_id` (`b15ea0b4d`); allowlist `window_exclusions` entry `neg8.midpoint_lost_primary` | changed: §0.12, §0.16, §6.2, §6.5, §6.11, §7.2, §14 Q11; analysis plan §2.4 |
| evidence manifest covers the census decision | `quiet_predicate_campaign.MANIFEST_PATHS` gains `joulewise/agent_identity.py` (`39ac4972d`). That manifest belongs to the quiet-predicate evidence night kind, which block 5 does not run; a block-5 window covers the file through the executed-file inventory and the sealed inventory (§0.18, §11 item 2), which list every file under `joulewise/` | matched: no text change |
| D1: a reference with no readable summary | `run_campaign._idle_admission_core_evaluation` and `whole_window._derived_neg8_decision`: reason `summary_unreadable`; harvest `NEG8_STATUS_LOSS_CODES` puts `member.timeout` first | changed: §0.12 |
| N8: model identity of a reference | `harvest.NEG8_REFERENCE_LOSS_CODES` gains `model.identity_mismatch`, `model.identity_underivable` (`c0b824fba`) | changed: §0.12, §6.3 |
| N2: a reference that never ran | `harvest.build_roster` sets `neg8_slot` from each reference stage's `spare_retry`; `_neg8_lost_rows` adds `bundle_absent` rows | changed: §0.12 |
| N3: never-run references at an endpoint | `whole_window.evaluate_neg8_point_drift` `short_planned_roster`; `run_campaign` `planned_roster_shape` (whole-window mode only) | changed: §0.12, §6.5 |
| N1: verdict sources that do not authenticate | `harvest._claim_campaign_manifests_as_written`, `_neg8_reference_losses`, `observed.reference_source` on `neg8.screen_failed` | changed: §6.5 |
| N5: an agent run by its npm package path | `agent_identity.AGENT_PACKAGE_SCOPES`, `AGENT_PACKAGE_DIRS`, `_agent_package_script` (all three removed at `2524637ae`, where the rule of revision 10 replaced them) | changed: §4.5 |
| N6: the unusable-pack refusal | `window_lineage.PackInventoryUnusableError`; `driver.run_hazard_night` tests the type; allowlist entry moved from BASELINE to NUMBER_INTEGRITY | changed: §0.17, §6.11 |
| N7: an empty salvaged code prefix | `harvest._malformed_flag_line` and `_candidate_codes`: `if not code` | changed: §6.2 |
| N4: which allowance the analysis reads after a re-screen | not code at this head (no analysis consumer exists); an L9 requirement | changed: analysis plan §4 step 4, §11 |
| sizing, pins, plan trees | `sizing_b5.json`, `identity_pins.json`, the three `plan_tree.json`: unchanged bytes; `configs/pins/registry.json` `a4a2be94912c4a3c33b1fb04e0f91e9e691290e2a7b7ee98898783ff307033b2`, unchanged | filled: `B5-FINAL-HASHES` |

**Catalog comparison** (revision 8). The same script, pointed at the new clone
(`/private/tmp/claude-501/-Users-edr-code-JouleWise/0a4039c8-3a55-4151-82ba-e66d8a0e9397/scratchpad/regsync7/check_catalog8.py`),
read every code named by those tables at `43ac12d0c` and compared each with this directory's catalog. Before revision
8 (catalog at `dc046d4d`) and after: 192 codes, none missing, none extra, `collector.unmeasured` deliberately absent,
the superseded A1 code absent, `load_catalog` OK, and the one documented disagreement (`g3.recompute_failed`, §6.5).
The cold-pass-2 fixes and the rulings added no code; only four notes changed (`neg8.reference_lost`,
`neg8.midpoint_lost`, `neg8.screen_failed`, `records.malformed_flag_exclusion_possible`). The GAMMA window reason
`neg8.midpoint_lost_primary` is deliberately not a catalog code (§0.16).

**Revision 9 sync record** (`B5-REV9-SYNC`). The source list was the integration's REG list from the
census-ancestors lane onward (`/Users/edr/night-archive/gate-prune/REG_PENDING.md`: the census-ancestors lane, the
NEG-8 delta-fix lane and the T3 prune), the frozen-head record `FROZEN_HEAD_4.md`, the latest entries of
`INTEGRATION_TODO.md` (cold pass 4, the Sol re-verification, the consult disposition, the second dry records, the
monitor-cost test) and the orchestrator's calls for this revision. Each row was read in the int5 head `fe28e5a0c` (a
fresh read-only shared clone at `/private/tmp/regsync4/repo`, detached at that commit; the integration worktree was
not touched), from the diff `43ac12d0c..fe28e5a0c` (14 commits; 19 files under `joulewise/`, `scripts/` and
`configs/`).

| Sync point | Code at `fe28e5a0c` | Text |
|---|---|---|
| census lists its ancestors | `night_gate.AGENT_CENSUS_ARGV` and `hazards.arm.AGENT_CENSUS_ARGV` = `/usr/bin/pgrep -a -lf '[c]odex\|[c]laude'` (`c0f37974a`); `agent_identity.filter_census` follows the caller's tree downward only; `arm_census` discovery keeps no `-a` (a diagnostic that reads its own ancestors from the kernel) | changed: §4.5 |
| T3 removed from the census | `agent_identity.AGENT_PREFIXES` = (`claude`, `codex`); the T3 rules removed from `arm_census`, `t0_rehearsal`, `prewindow.py` and the generators (`63d2b9bad`); `scripts/prewindow_check.sh` keeps its sealed bytes, `t3` included (`fe28e5a0c`; SHA-256 prefix `d8458eea588a746f`, recomputed by this author) | changed: §4.5 |
| interpreter rule | at `fe28e5a0c` the matcher still parsed options (`agent_identity._VALUE_OPTIONS`, `ca25d9299`); the rule of §4.5 was then a pending commit of `lane/2026-10-07-census-interp`, and this row listed what to confirm when it landed: any command-line element of `node`, `bun` or `deno` that names `@anthropic-ai/claude*`, `@openai/codex*`, `claude-code` or the `claude` or `codex` install directories makes it an agent, with no option parsing; `node /opt/homebrew/bin/codex exec` (an agent in the dry arm) is still an agent; the window's own Python and shell processes are not. Revision 10 confirmed all three at `9b0c680ed` (`B5-REV10-SYNC` below) | changed in revision 9: §4.5 (to the pending rule); restated from the code in revision 10 |
| A1: which bracket carries the allowance | `harvest.neg8_allowance` writes `derived/neg8-allowance.json` (`joulewise.b5_neg8_allowance.v1`); `whole_window.harvest_neg8_allowance_bracket`; `whole_window_drift_allowances(..., neg8_harvest_archive=)`; `analyze-claims --neg8-harvest-archive`; the archive bytes are read through `authentication_io.read_authentication_input`, the read function for files that claim code treats as evidence: inside a session that records what a claim consumed, it parses the file strictly as JSON, registers its SHA-256 at the first read and refuses a later read of the same file whose bytes differ; outside such a session it is a plain file read (`bbdae1e86`) | changed: §0.12; analysis plan §3.1, §4, §7.1, §11 |
| A2: the reference identity unit | `harvest.NEG8_REFERENCE_IDENTITY_UNIT` = `neg8_reference`, `_reference_model_identity` (sealed pin, else strict majority); pin written by `scripts/write_b5_identity_pins.py` (`754c8c093`) | changed: §0.12, §4.6 item 3, §6.3, §6.5 |
| N8 with call (ii): a reference of another model | `model.identity_mismatch` (member level) and `model.identity_inconsistent_in_window` (window level) both emitted; both EXCLUDE_WINDOW in this catalog; `exclusions.compute` applies EXCLUDE_WINDOW at any scope | changed: §0.12, §6.5 ("window excluded", not "survivors decide"); catalog notes |
| A3: references named from the sealed roster | `harvest._neg8_reference_losses` adds every member with `neg8_slot` or `spare_slot`; the stored loss list is trusted only when `neg8_reference_source` is `verdict_sources` | changed: §0.12, §6.5 |
| A5: a strict-invalid reference is lost | `run_campaign._idle_admission_core_evaluation` reason `strict_invalid`; `whole_window._derived_neg8_decision` (`stored_strict_losses`, `unlisted_strict_invalid`); the harvest's exclusion pass always runs | changed: §0.12 |
| Sol R2, Sol R3 (the Sol re-verification's findings, §9.1; not the fix route R3), cold pass 4 D1: claim-time allowance gaps | not fixed at this head: `floor_extraction.extract_cells` has no archive parameter; the claim validator rejects a stored failed screen (`whole_window_neg8_verdict_failed`) before the harvest record is read | changed: §0.12, §9.1; analysis plan §11 (lane L9-NEG8) |
| Q11 and the anti-spiral rule | no code computes the cause key of §7.3 | changed: §7.2 (sentence struck) |
| sizing, pins, plan trees | the three `plan_tree.json` and `sizing_b5.json` unchanged; `identity_pins.json` `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9` (was `f78a27f8…`); `configs/pins/registry.json` `a4a2be94912c4a3c33b1fb04e0f91e9e691290e2a7b7ee98898783ff307033b2`, unchanged | recomputed: `B5-FINAL-HASHES` |
| refusal allowlist | `configs/gates/hazard_refusals.json` byte-identical to `43ac12d0c`; counts unchanged (§6.11) | matched |
| dry records | `dry-records-2/` at `fe28e5a0c` | filled: §2 item 6 |

**Catalog comparison** (revision 9). The same script, pointed at the new clone
(`/private/tmp/claude-501/-Users-edr-code-JouleWise/0a4039c8-3a55-4151-82ba-e66d8a0e9397/scratchpad/regsync9/check_catalog9.py`),
read every code named by those tables at `fe28e5a0c` and compared each with this directory's catalog. Before revision
9 (catalog at `30d92227`) and after: 192 codes, none missing, none extra, `collector.unmeasured` deliberately absent,
the superseded A1 code absent, `load_catalog` OK, and the one documented disagreement (`g3.recompute_failed`, §6.5).
The delta added no code and changed no effect. Five notes changed: `model.identity_mismatch`,
`model.identity_inconsistent_in_window`, `model.identity_underivable` (the reference unit and call (ii)),
`neg8.reference_lost` (reason `strict_invalid`) and `neg8.screen_failed` (references named from the roster; the
allowance record). The code's draft vocabulary (`DRAFT_CODES`) still lacks `model.identity_inconsistent_in_window`,
`model.identity_underivable` and `whole_window.verdict_unauthenticated` (cold pass 3 N-B, cold pass 4 N-1); this
catalog classifies all three, and the seal binds this catalog, not the draft.

**Revision 10 sync record** (`B5-REV10-SYNC`). The source list was the whole of the integration's REG list
(`/Users/edr/night-archive/gate-prune/REG_PENDING.md`, all ten sections; the last gives the orchestrator's final
sentence for the census interpreter rule), the resume and seal-preparation notes beside it (`RESUME_2026-10-07.md`,
`SEAL_PREP.md`), and the diff `fe28e5a0c..9b0c680ed` of the integration branch (five commits, eight files). Each row
was read at the int5 head `9b0c680ed79d5c7b72b4b39ed04b9fe51dd116d4`: in the integration worktree, read only, and in
a copy of that commit's files made with `git archive` (`/private/tmp/w1007-regprep/snap`), from which the probes and
tests named below were run.

| Sync point | Code at `9b0c680ed` | Text |
|---|---|---|
| interpreter rule | `agent_identity.identify`. `SCRIPT_INTERPRETERS` = (`node`, `bun`, `deno`), tested as a prefix of the executable's file name and of the process name. `_names_agent` cuts each argument with `_COMPONENT_SPLIT` and tests each piece against `AGENT_PREFIXES` = (`claude`, `codex`). `UNNAMED_CODE_ARGS` = {`-`, `-e`, `-p`, `-pe`, `--eval`, `--print`, `eval`} and `UNNAMED_CODE_PREFIXES` = (`--eval=`, `--print=`) give `undecided`, which `filter_census` keeps as a hit (reason `undecided_launch`). The option tables and `_interpreter_launch` are removed (`2524637ae`). The three points revision 9 listed hold: an agent's package or install path in any argument gives `agent`; `node /opt/homebrew/bin/codex exec` is `agent`; Python and shell processes with `.claude` paths are `not_agent`. This author probed 46 command lines, and every verdict is as §4.5 states; the lane's test module `tests.test_agent_identity` passes on the copy (12 tests) | changed: §4.5 (the rule rebuilt from the code, which is wider than revision 9's wording), §2 items 1, 6, 7 and 8, §9.1 (R1), §14 Q14 and Q15 |
| the lane's second commit | `455e59b86` changes one explanatory comment, that of `harvest._reference_model_identity`: the block-5 pins carry `neg8_reference`, and a reference of another model excludes the window. Its last clause calls `model.identity_underivable` "not in the flag catalog", which was true of the code's draft vocabulary only: this catalog classes it EXCLUDE_MEMBER, and the harvest loads this catalog, never the draft (`harvest` `catalog_path`, `flags.catalog.load_catalog`) | matched: §0.12, §6.3, §6.5; no text change |
| the documents in the code tree | `763b678a7` places revision 9 of this file, the analysis plan and the catalog, and the stub inventory, under `configs/campaigns/v5_claim_25g83/`, each byte-identical to this branch at `bc8ad4ae` (SHA-256 compared by this author). `9b0c680ed` adds three entries to a test data file, `tests/fixtures/d165_rationale_allowlist.json`, that name line 354 of the analysis plan | no text change here. Revision 10 keeps that sentence of the analysis plan on line 354. §11 and §12 are left to the pass that decides how the sealed inventory lands |
| census sites | `filter_census` is called by `night_gate.decide_census` (the driver's census, the watchdog's, and `quiet_admission`), by `hazards/arm.agent_census` and by `arm_readiness_evidence_t0._agent_lines_decided` | changed: §4.5 (the sites are named) |
| spare retry command line | `chain.spare_argv` replaces the stage's config directory with the spare set's and sets `--max-failures` to k | changed: §0.12 |
| sizing, pins, plan trees | the three `plan_tree.json` (`1d87a309…`, `0cdb3383…`, `8b1d1d71…`), `sizing_b5.json` (`89e7ea70…`), `identity_pins.json` (`a0865895…`) and `configs/pins/registry.json` (`a4a2be94…`) hash as at `fe28e5a0c` (`shasum -a 256` on the copy) | matched; every `B5-FINAL-HASHES` mark is left in place |
| pinned estimator files; `prewindow_check.sh` | `git diff a434e363d 9b0c680ed` over the four pinned files is empty; `scripts/prewindow_check.sh` is unchanged (SHA-256 prefix `d8458eea588a746f`) | matched: §2 item 1, §4.5 |
| cooldown smoke carry-over | `scripts/run_campaign.py`, `joulewise/controller.py` and `configs/campaign_policies/` are unchanged since `fe28e5a0c`; the harvest's one changed comment does not mention the cooldown | changed: §2 item 7 (the carry-over to `9b0c680ed` is stated) |
| refusal allowlist | `configs/gates/hazard_refusals.json` is unchanged since `fe28e5a0c` (2,749 entries; 34 window exclusions and 40 member exclusions). `tests.hazards.test_refusal_allowlist` passes on the copy with this catalog in the tree (23 tests; the one that reads this branch from a clone is skipped there) | matched: §6.11 |
| the REG list's nine earlier sections | every item checked against this file, the analysis plan and the catalog | present, except the gaps of revision 10 item 2, now repaired: §0.12, §4.5, §9.1; analysis plan §8.1 |

**Catalog comparison** (revision 10). The same script, pointed at the copy of `9b0c680ed`
(`/Users/edr/night-archive/gate-prune/wave-1007b/reg-prep/check_catalog10.py`), read every code named by those tables
and compared each with this directory's catalog, and with the copy of the catalog in the integration tree, which is
the same bytes. Before and after revision 10: 192 codes, none missing, none extra, `collector.unmeasured` deliberately
absent, the superseded A1 code absent, `load_catalog` OK, and the one documented disagreement (`g3.recompute_failed`,
§6.5). Nothing merged since `fe28e5a0c` adds a code or changes an effect, and revision 10 changes no note. The
script trusts the code's tables, so a second script (`scan_literal_codes.py`, same directory) searched every string
in the 275 Python files under `joulewise/` and `scripts/` for a token shaped like a flag code whose first part is one
some catalog code uses. It found 187 of the 192 catalog codes written out in full (the other five are the
`<module>.arm_unmeasured` codes, which the code builds from the module's name), and 75 other tokens, none of which is
a flag code: they are function names, field paths, file names, journal stage names, the reason strings of the G10
record, and the pack-scoped window reason `neg8.midpoint_lost_primary` (§0.16). The draft vocabulary still lacks the
three codes named in revision 9's comparison.

**Revision 12 record** (`B5-REV12-SYNC`). Revision 12 applies rulings and records; it follows no new list of code
changes. This record covers §§7–10 and §§13–16, whose writer read each row below at the integration head
`9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a` (the integration worktree, read only) or, for the last row, on the branch
named there.

| Sync point | Code at `9395cecfb` | Text |
|---|---|---|
| the head comparison | `harvest.head_change_class` and `flags.collect.head_change_class` put each path that differs between H_claim and the commit a window ran from in one of four classes: `pin_only` (the ledger pin), `seal_document` (the sealed inventory, this file, the analysis plan), `window_input` (any other path under `joulewise/`, `scripts/` or `configs/`, and `docs/phase_2/window_runbook.md`, matched without regard to letter case) and `record_only` (every other path). Only `window_input` gives `code.executed_differs_from_sealed`; the harvest writes all four lists to `derived/code-identity.json` (schema `joulewise.b5_code_identity.v1`) | changed: §9.1 (second part of the delta record), §7.5, the register above. §2, §11 and §12 state the same facts and belong to other writers of this revision |
| this file's bytes after the seal | `plan._locator` refuses a file whose SHA-256 is not the digest the plan input gives ("sha256 does not match the file"); `harvest.resolve_thresholds` records `registration_digest_differs_from_plan`, and every such problem is a harvest fault | changed: §8 item 3 (the release event is a section of the seal record), the register above |
| the harvest archive and what it withholds | the harvest copies its sources under `sources/` (`night-custody`, `claim-runs`, `bound-runs`, `ledger/`, `inputs/`, `repo/`) with `sources/SHA256SUMS`, and writes `derived/`, `withheld/` and `harvest.json`; `harvest.write_once` creates each file without setting a mode. The directory names were also read in the archive of a desk rehearsal (`/Users/edr/night-archive/gate-prune/rehearsal-real/gamma-2/archive/`, file names only; a rehearsal, not a window) | changed: §8 (the custody map) |
| RESTRICTED flags | three writers, all in the harvest: the catalog default of `member.anchor_energy_envelope_exceeded`; `member.target_phase_precheck_failed` when `harvest.restricted_reason` matches one of its reasons; `diagnostic.s1_structural`. No program that writes flags before the harvest sets RESTRICTED | matched: §6.3; used in §8 |
| what the driver releases | `run_night.HAZARD_ARTIFACTS` (12 record files of `night/`); the courier's instruction for a `HAZARD_PACK` window ("Report structure only ... never state an energy, a power or a duration of a member or a phase") | matched: §8 item 2; used in the custody map |
| GAMMA's planned members | the plan tree's stage graph: 12 corpus members, reference stages of 3, 1 and 3, two diagnostic stages of 1, and four science stages of 20, 101 in all | used in §8 (worked example) |
| three analysis programs print results | `scripts/build_d165_dominance_closeout.py` writes the close-out to standard output when it is given no `--output`; `python -m joulewise analyze-claims` prints each contrast's outcome; `scripts/render_results_fills.py` prints the rendered fills | used in §8 |
| a resized member allowance | `plan.read_allowance` takes the allowance's source as a path relative to the measurement checkout, requires the file to hash to the SHA-256 given and a JSON pointer in it to resolve to exactly the seconds given | changed: §10 |
| the changes the seal gate's stage 1 ordered before the head | not in the integration branch when this was written; on the branch `lane/2026-10-07-seal-rulings` (four commits on `9395cecfb`, read with `git log` and `git diff`): `059fafc55` sets the catalog's `rules.cell_unit_minimum` to 5; `9980d6296` rewords what `cell.below_minimum` and `neg8.midpoint_lost_primary` protect in the refusal allowlist (the gate's K-1 and K-3); `7b88e835a` removes `g3.recompute_failed` from the allowlist's window exclusions, which leaves 33, and sets it to DISCLOSE in the test catalog `tests/fixtures/b5_harvest/flag_catalog.json` (K-2); `a0920cb8c` makes the tests and the test catalog follow the minimum of 5. The four commits change no file under `joulewise/` or `scripts/`. `Catalog.cell_unit_minimum` is read only by `exclusions.compute`, which only the harvest imports | changed: §10 deviation 4, §9.1. With K-2 the "one documented disagreement" that the catalog comparisons above report for `g3.recompute_failed` ends: each comparison states what held at its own commit |

Removed from revision 2 because the mechanism they bound is retired or now measured: `V5-PACK-REGEN-RECORD` and
`V5-IDLE-SECONDS` (done, PR #481), `B4-*`, `L10-A-RATIFICATION-RECORD`, `Q110-CLOSURE`, `A6-AT-H-CLAIM`,
`V5-TRANSACTION-GO-01-DISCHARGE`, `AUTH-<label>`, `CAMPAIGN-PERMITTED-BLOCKS`, `STEP6-RECORD`, `CENSUS-ARGV` (§4.5),
`ANCHOR-RUNTIME-EFFECT` (either way the member is removed), `HARVEST-OPEN-RULE` (§5.4), `CLAIM-CHAIN-SUCCESS-RC`
(§7.1), `CLAIM-HARVEST-CLI` (`scripts/harvest_b5_window.py`), `G3-CLAIM-ARGS` (the harvest runs G3 on GAMMA; floor
packs have no analysis manifest), `ED-PREDICATE` and `ED-DISPOSITION` (§6.4 contention), `SPOTLIGHT-EXCLUSION` and
the disk ledger FILLs (measured by the contention and disk hazards), `B5-ATTEMPT-BUDGET` (attempts are planned, never
capped), `LONGEST-STREAM-SIZING`, `SHORTEST-STREAM-SIZING`, `REF-STREAM-FLOOR` (T_stream_max is committed; the
576 idle records give about 75 s of idle stream at the observed cadence, and at least 57.6 s even if every record
took only the requested 100 ms; every member then adds its warm-up and request, at least 117 more records in block 3,
so each stream exceeds the 60 s minimum of the clock fit), `COURIER-BLINDNESS-CAMPAIGN` (§8 item 2), and the
battery evidence map (§9.2).

## 14. Open questions (each names where it goes)

- **Q1. NEG-8 corpus of 10 or 11. Closed in revision 4.** It was settled by the harvest-side derivation from
  custodied bytes, with the core untouched (fix lane fx-harvest, §5.3).
- **Q2. Sealed-inventory comparison scope. Closed in revision 4.** At `f8164893` the arm's executed-code collector
  (`joulewise/flags/collect.py`, `_window_scope`) and the harvest (`code_identity`) count missing and added files only
  under the window's own roots, so the other two packs' sealed files are not read as missing.
- **Q3. Contention false flags (after ALPHA-1; cold erratum if needed).** "Any outside process above 5% of one core"
  has never been applied to every process on this Mac during a window. If ALPHA-1's flag rate costs cells, a
  prospective erratum retunes the predicate from flag rates, which are structure, not energies. A repeat goes to a
  consult (§7.3).
- **Q4. Paper placement (cold gate, ideally before seal).** D-174's fallback places no `_v5` result; printing needs an
  adoption ruling.
- **Q5. Attribution floor. Closed in revision 12 by orchestrator ruling (2026-10-07): the formula is registered and
  no number is bound.** The question was whether to bind D-078's figure of about 1 J, with an artifact, and whether
  D-078's derivation applies on macOS build 25G83. The ruling
  (`/Users/edr/night-archive/gate-prune/wave-1007b/q5-attribution-floor/RULING.md`): the derivation applies as a
  method and not as a number. The attribution floor of a reported cell is the largest, over the cell's kept members,
  of a bound the reducer already computes for each member and stores in the member's summary
  (`energy_anchor_shift_envelopes`, the entry for the phase, field `max_abs_delta_j`). That bound is the largest
  change in the energy assigned to the phase when each of the phase's two edges is moved, earlier or later and
  independently of the other, by the edge bound, while the whole power trace is shifted by any amount within the
  member's clock bound (§0.14). The edge bound is the window's fiducial bound (§0.11) plus the change, over the
  member's sampler stream, of the wall clock minus the monotonic clock. Each member's bound is read from its summary
  as re-derived under the fiducial bound that the window's own calibration bracket fixes (§0.10 builds the quantity
  in full). It is computed at the analysis from the window's own members and bracket, so `ATTRIBUTION-FLOOR-BINDING`
  is filled by this formula (§13), and no value and no artifact is sealed. *Why no number.* The quantity is not a
  constant of the instrument. D-078's figure was one member's bound on one window of an earlier OS build (window
  a10, macOS 25F84, Qwen2.5-1.5B: 1.016 J, and §0.10 gives the arithmetic. D-078 put it in round figures as a
  timing bound of 31 ms at about 33 W; exactly, the member's whole timing bound is 0.031073829 s, and 1.016 J
  divided by that time is 32.697 W, a quotient and not the power of any one record). On released 25G83 data
  (block 3, not a claim window) the same bound was 1.38 to 2.86 J per member, and it changes with each window's
  bracket. Nothing in block 5 is decided by the number: it is printed beside the four reported cells. Binding the
  old value would print a floor the instrument does not have. The ruling followed an investigation (Opus 5.5) and a
  refutation pass (Fable 5.1), which reproduced every number of the investigation's report from raw bytes and
  returned five corrections; the ruling carries them.
- **Q6. The sensitivity line. Closed at the seal gate (stage 1, 2026-10-07): adopted as amended.** Analysis plan
  §8.1 prints a labelled line over the units removed only by the three load-correlated codes
  (`thermal.os_level_nonzero`, `thermal.powermetrics_pressure_elevated`, `contention.request_overlap`), to expose the
  bias such exclusions can introduce; the other eight PHYSICS_IN_SPAN codes describe an energy that is wrong or
  unmeasured and are never ignored. Battery assist does not belong here: it is disclosed, and its own two-way line is
  registered (§9.2, analysis plan §8.1).
- **Q7. Ed's hardware setting (optional).** A fixed 80% charge limit with Optimized Battery Charging off avoids arms
  refused because the OS chose to charge.
- **Q8. The watchdog held each window open until its deadline. Closed in revision 5.** The watchdog now releases a
  finished window on its terminal evidence (§5.4; P2-WD, at `a434e363d`).
- **Q9. The battery-assist line for GAMMA's contrasts. Closed in revision 6: adopted.** The ruling of 2026-10-06
  prints every reported cell with and without assisted members (analysis plan §8.1). GAMMA's contrasts are not
  reported cells (§0.9), and 8B members, one side of every quad, are the ones that assist most. The orchestrator
  ruled on revision 5's open points (2026-10-06, `/Users/edr/night-archive/gate-prune/INTEGRATION_TODO.md`): GAMMA's
  contrasts get the line too, because 8B is where assist occurs. Analysis plan §8.1 now prints each contrast's
  estimate also without the quads that hold an assist member. The line is descriptive and gates nothing. The seal
  gate kept it (stage 1, 2026-10-07, ruling SG-9): it shows the reader where assist concentrates, the 8B side of
  every quad.
- **Q10. Whole-machine meter, central band (none; recorded).** The band for ρ is set by the first clean window
  (analysis plan §8.2). If no window of the block is clean, no band is set, and the cross-check reports only the hard
  plausibility band and the spreads. Nothing waits on this.
- **Q11. A GAMMA attempt whose midpoint was lost. Closed in revision 8 by orchestrator ruling; confirmed at the seal
  gate (stage 1, 2026-10-07, ruling SG-5).** The question: the NEG-8 ruling makes `neg8.midpoint_lost` DISCLOSE in
  the catalog and claim-excluding for the primary contrasts, but the scheduler reads only `claim_usable`, so a
  claim-usable GAMMA attempt that lost its midpoint would have ended GAMMA's arms with no claim-bearing contrast.
  The ruling (2026-10-07): such an attempt is not claim-usable (window reason `neg8.midpoint_lost_primary`) and
  GAMMA is re-armed; ALPHA and BETA keep the flag disclosed only. Reasons: GAMMA exists for its primary contrasts;
  the selection reads a pre-registered flag and the pack id, never an energy, so it is blind; and the expected cost
  is small (about 0.07% of windows, plus contamination found at harvest). Code: `joulewise/flags/exclusions.py`
  `PACK_SCOPED_WINDOW_REASONS` (commit `b15ea0b4d`), with its allowlist entry (§6.11). Text: §0.12, §0.16, §7.2;
  analysis plan §2.4. Revision 9 strikes revision 8's sentence placing this reason in the NEG8 family for §7.3's
  anti-spiral rule: that rule is applied by the orchestrator, no code computes it, and a registration does not need
  to pre-assign it. The seal gate confirmed the rule and corrected two statements around it. First, the midpoint is
  the only NEG-8 reference inside the window, not the only reference: GAMMA also runs two diagnostic interior
  references, which by rule enter neither the screen nor the allowance (§0.12). Second, a lost midpoint on ALPHA or
  BETA can also understate that window's allowance; it stays disclosed there because no decision rests on a reported
  cell's interval, while on GAMMA a contrast's decision rests on the bound that carries the allowance (analysis plan
  §2.4).
- **Q12. A NEG-8 reference or spare that ran another model. Closed in revision 9 by orchestrator call (ii);
  confirmed at the seal gate (stage 1, 2026-10-07, ruling SG-6).** The question (Fable cold pass 3 N-A, cold pass 4
  N-1): ruling N8 said such a reference is dropped and the survivors decide, but `model.identity_mismatch` and
  `model.identity_inconsistent_in_window` are EXCLUDE_WINDOW in this catalog, and the exclusion function applies
  that effect at any scope, so the window is removed whatever the survivors screen says. The call (2026-10-07): the
  catalog is right and the window is excluded. The pack that executed differs from the sealed one, which is a
  failure of number integrity, not a lost measurement. A reference whose identity cannot be derived
  (`model.identity_underivable`, member-level) is still lost, and the survivors decide. Text: §0.12, §6.5; catalog
  notes. The seal gate's reason for confirming: a reference's configuration is committed and pinned, so it can
  record another model only if the model files on disk or the installed runtime packages changed. That is a change
  to the machine's software, before or during the window, and a science member's own identity check shows it only if
  it touched that member's own files. A record that merely lacks the hash is different: it is a defect of one
  record, with no evidence that anything changed.
- **Q13. One NEG-8 survivor logic instead of three (lane L9-NEG8, after the seal, before any claim).** The survivor
  logic lives in the verdict writer, the replay and the harvest; three reviews in a row found defects in it, and the
  last two (the Sol re-verification's findings Sol R2 and Sol R3, §9.1; cold pass 4 D1) are in claim-time code. A
  consult (§9.1) chose to seal on this code and fix them in one lane, with one design round by Sol and Fable before
  code. Analysis plan §11 lists what the lane must do.
  Until it lands, no block-5 floor and no contrast resting on a recorded survivor re-screen is claimable (§0.12).
  Nothing here changes collection: the lane lands in the desk checkout only (§7.5, §11 items 1 (ii) and 4), the
  measurement checkout stays at H_claim, and the verdict writer's bytes in `scripts/run_campaign.py` do not change.
  The seal gate (stage 1) added to the same lane the harvest-side reference losses of §0.12 (`energy_unreadable`,
  the unmeasured and measured physics codes) and the narrowed malformed-flag candidate list of §6.2.
  The gate confirmed sealing on the present code (ruling SG-8).
- **Q14. What the census's rule for JavaScript runtimes can miss. Set by orchestrator ruling of 2026-10-07. The
  first stage of the seal gate was not asked about it: it judged revision 9, and this question was opened in
  revision 10. The second stage confirms the rule as it stands; or it asks for the tightening below, in which case
  the seal waits for a new H_claim.** §4.5 lists four ways the merged rule can read a live agent as
  none. Three are older than the rule (a name inside a longer piece, an interpreter that is not a JavaScript runtime,
  a command line the probe never lists). One belongs to the rule: a runtime that names no agent and reads its program
  from standard input without the `-` argument is decided not an agent, and the rule cannot see it without parsing
  the runtime's options, which two audits showed to be the wrong mechanism. One tightening needs no parsing: count
  *every* listed JavaScript runtime that names no agent as undecided, and so as a hit, whatever its other arguments.
  Its cost: a window launched by `launchd` runs no JavaScript runtime, so it could refuse or stop a window only while
  some unrelated runtime with `claude` or `codex` somewhere in its command line is alive on the machine; and it
  reverses one of the lane's own test cases, a launch that must not count today
  (`node somescript.js --path …/.claude/…`). It would be a change to collection code (§7.5), and so to a window
  input, which the H_claim that the second stage judges cannot receive. Asked for at the second stage, it
  therefore moves H_claim: the change is made and reviewed, the tests and a delta cold pass over it are run (§2
  item 1), a new inventory is made, and the seal follows. Whichever is chosen, the hazard itself, a process using
  the CPU during a member, stays measured by the contention hazard (§4.2, §6.4).
- **Q15. The desk dry arm after the matcher change (orchestrator, before ALPHA-1 arms).** `B5-DRY-ARM-RECORD` was
  produced at `fe28e5a0c`, with the matcher that parsed options. §2 item 6 gives the reason its refusal holds under
  the merged rule, and the lane's tests include a live `node` launch decided through the production census
  (`tests.test_agent_identity`, the R1 test). The dry arm took 0.177 s and can only refuse. Either it is run again at
  the final head and the record refreshed, or the carry-over reasoning of §2 item 6 is accepted as it stands.

## 15. Where each gate-prune change lives

| Plan §6 item | Change | Here |
|---|---|---|
| 1 | Network time OFF as an action; no wording check; ONs only at G10 and the redraw | §4.4, §3 |
| 2 | Clock gate 3.7 ms + (\|f\| + 0.25 ppm) × 335 s ≤ 5 ms; dwell linearity ±1 ms; 1 ms step; per-member 5 ms bound authoritative | §0.14, §4.2, §6.4 |
| 3 | Idle admission unchanged; `member.admission_aborted` removes the member; stage continues; L11 option | §0.13, §6.3, §5.2, §7.5 |
| 4 | Battery: arm check, 5 s journal, 60 s publication, in-force rule, accumulator rule with units, unmeasured, pairs as data, measured limitation (revision 5: current from the SMC at 1 s; assist disclosed, §9.2) | §4.2, §6.4, §9.2 |
| 5 | Census kept; contention measured directly; load average and name lists recorded only | §4.5, §4.2, §6.4 |
| 6 | Disk arm rule and in-window stop; dwell replaces `prewindow_check.sh` | §4.2, §4.1 |
| 7 | Thermal (OS level and powermetrics); instrument cadence probe | §4.2, §6.4 |
| 8 | Ledger seed at pin 402 at the default path; readiness and abort before each arm | §4.6 item 6 |
| 9 | Validity becomes the catalog; COLLECTED, NULL, HARVEST_FAULT; re-arm until claim-usable; anti-spiral by family; END STATE from flags; §7.4 kept | §6, §7 |
| 10 | Preconditions deleted and kept | §2 |
| 11 | Harvest at chain exit; next arm reads only `claim_usable`; block time recomputed | §5.4, §7.2, §5.5 |
| 12 | Blinding unchanged; flag `blinding` governs release; courier structure only | §8 |
| 13 | H_claim, sealed inventory, pin-only commits, L5 and L9 pinned by addenda | §11 |
| 14 | `attempt_policy` superseded; `--max-failures` override as a registered deviation | §5.2, §10 |
| 15 | Analysis plan amendments | analysis plan §1, §2.2, §4, §5, §7, §8, §11 |

## 16. What the author read

For revision 3: Ed's ruling in `CLAUDE.local.md`; the gate-prune plan and its inventory
(`/Users/edr/night-archive/gate-prune/`); the code of lanes L1–L5 and L8 in their worktrees (hazard modules and
thresholds, the driver, plan writer and chain writer, the hazard lineage, the flag package and its draft catalog, the
harvest's code table, G10); at the integration head `a0a4f5a7`: the packs' plan trees (stage graphs, attempt
policies, identity pins, idle seconds), the production policy, the acceptance and ledger pin digests, the committed
sizing source, `kernel_clock.py`, `whole_window.py`'s verdict conditions, `check_window_provenance.py`'s F5-2 check,
the floor functions and the t table (to compute the synthetic worked examples of the analysis plan); and the
pre-mortem memo `/Users/edr/night-archive/ia-0a40/MEMO.md`. No energy or power value of any block was read, and no
`_v5` claim byte exists. Revision 2's reading record and its disposition of three blind critiques are in commit
`bfd1ee8c` (this file's §16 and the analysis plan's §14 there).

For revision 4, the author read the code at the gate-prune integration head `f8164893`
(`/Users/edr/code/JouleWise-wt-gp-int`):
- the harvest's code table, NEG-8 bound check, re-screen, calibration, roster, member and model-identity steps;
- the flag catalog loader and the harvest's test catalog;
- the battery, thermal, clock and contention span joins, and the disk targets;
- the model-identity collector and `identity_pins.json`;
- `scripts/size_b5_window.py`, `sizing_b5.json` (re-derived with `--check`) and block 4's sizing source;
- the plan writer's inputs, the driver's deadline, and the watchdog's plan-span rule;
- the whole-window verdict writer's per-member failure reasons and `joulewise/environment_admission.py`;
- the ledger snapshot loader and the bracket evaluation's use of it;
- the boundary fields of the powermetrics adapter, the floor packs' extraction specs, decision D-078 item 4, and
  the backup convention of `docs/phase_2/window_runbook.md`.

The author also read the block-3 timing summary that §5.5 cites (scratch `sizing_v2.json`, member-cycle timing
only). The catalog was validated with `joulewise.flags.catalog.load_catalog`. No energy or power value was read.

For the timing edits of revision 4 (item 6 of "What changed in revision 4"), the author read the cold-judge ruling
and the two council reports it judged (`/Users/edr/night-archive/gate-prune/timing/`: the ruling, `council-sol.md`,
`council-opus/council_opus_summary.json`, `timing_analysis.json`); the adapter's record-count rule
(`powermetrics.py` `_idle_count`), the controller's cooldown release loop, the clock fit's 60 s minimum
(`uncertainty_evidence.py` `MIN_RATE_FIT_BASELINE_S`) and the idle trace's three-bandwidth rule
(`idle_dependence.py`); and, from block 3's 37 idle captures, the record durations only, to choose 576 records.
The block-3 power figures quoted in §0.3 and §0.6 are the ruling's and the councils' (block 3 is not a claim
window). No `_v5` claim byte exists.

For revision 5, the author read: the orchestrator's integration list (`/Users/edr/night-archive/gate-prune/
INTEGRATION_TODO.md`); PLAN2 (`prune2/PLAN2.md`, §2.2 and §3.1) and the round-2 lane results (`prune2/P2_RESULTS.md`);
the timing ruling; the battery-assist ruling, the B0AC validation and the meter wiring note
(`/Users/edr/night-archive/wallmeter-probe/`); lane L10's registration erratum; the core-prune design
(`core-prune/DESIGN.md` §3, §5, §7); and the P3 lane briefs. At the integration head `b9d02700a`
(`/Users/edr/code/JouleWise-wt-int3`) it read: the battery hazard module's SMC sources and arm rule; the harvest's
battery member rule, capture join, code table, threshold parser, desk-verdict timeout, identity supersession and
yield summary; `whole_window.py`'s NEG-8 drop verdicts, physical freshness times and disclosed binding changes; the
runner's member cap, strict-validation deferral, cooldown fallback and thermistor reading; the chain's deviations,
wall budgets, collection deadline and corpus retry; the driver's yield plan, counting and terminal verdicts; the
watchdog's leads and release; the contention module's dwell; G10's settle; the arm's identity read; the reservation's
and writer's record kinds; `km003c_parse.py`; `sizing_b5.json` (its totals and conventions) and the scratch sizing
source of §5.5; and the digest census's era records. It compared every code the harvest, the draft vocabulary and
the core table name with the catalog (§13 lists the one code the catalog has and the harvest does not yet emit). No
energy or power value of any window was read; the power figures quoted are the validation runs' and the rulings'.

For revision 6, the author read: the integration list's REG items and the frozen-head record
(`/Users/edr/night-archive/gate-prune/INTEGRATION_TODO.md`, `FROZEN_HEAD.md`); the battery-assist ruling, the meter
wiring note, the timing ruling and lane L10's erratum (all already applied in revision 5, re-checked); the cooldown
smoke's run-4 directory (the join-check record, and the SHA-256 of the four evidence files, computed). At the frozen
head `a434e363d` (`/Users/edr/code/JouleWise-wt-int4`, read only) it read, directly or through three read-only
investigation seats whose citations it spot-checked: the harvest's battery join, assist rule, accumulator rule,
capture join and pair replacement, member spans, meter join, historical custody pass, desk-pin guard and verdict
handling, unwritten-flag scan, drop-reason import and G3 condition; `joulewise/hazards/battery.py` and `clock.py`;
the driver's lineage check, monitor and meter supervision and tail order; the watchdog's leads and yield-alert reader;
`scripts/advance_b5_ledger_pin.py`; the controller's guard-collector wrapper; `whole_window.py`'s change since
`b9d02700a`; the chain's constants; the refusal allowlist and its test (counts recomputed); `sizing_b5.json`
(re-derived with `--check`) and `identity_pins.json` (hashed); and `git diff --stat` between `3a9327e51` and
`a434e363d` and between `b9d02700a` and `a434e363d`. It compared the catalog with the code by script (§13). No energy
or power value of any window was read.

For revision 7, the author read: the integration's REG list (`/Users/edr/night-archive/gate-prune/REG_PENDING.md`)
and the relevant entries of `INTEGRATION_TODO.md`; the NEG-8 cold ruling (`neg8-council/RULING.md`); and, at the int5
head `d3c107f2f` (read through a shared clone at `/private/tmp/regsync2/repo`, detached at that commit; the
integration worktree was not touched): the commit messages and diffs of the two audit-fix lanes and the NEG-8 lane
since `a434e363d`; `whole_window.py`'s survivor evaluator and count-adjusted bound; the verdict writer's status
losses; the harvest's NEG-8 screen, re-screen, disclosure, corpus physics drop, malformed-flag rule, unbuilt-flag
rebuild, binary-identity step, accumulator rule and identity supersession; the chain's spare-retry lines and helper;
the driver's reference minimums, census, G10 wait, lineage refusal and orphan reaping; `agent_identity.py`; the arm's
census and UNMEASURED handling; the reservation's desk-file reader; the plan writer's planned bytes; the sizer; the
spare directory's README; the allowlist file and its test. Every number written in this revision was read from a
file or computed by the author: the plan-tree, sizing and identity-pin digests with `shasum -a 256` (and
`size_b5_window.py --check`, `write_b5_identity_pins.py --check` and `reference_spares --check`, all exit 0 at
`d3c107f2f`); the spans and deadlines from `sizing_b5.json`; the planned disk bytes and their GiB from 182 MiB × the
member counts; the allowlist counts and the entry-by-entry difference from `hazard_refusals.json` at both commits;
the §0.12 worked example with the code's own `neg8_count_adjusted_bound` and `student_t_critical_95`; the §6.2
candidate lists from the catalog; and the catalog comparison by script (§13). No energy or power value of any window
was read.

For revision 8, the author read: the last section of the integration's REG list (`REG_PENDING.md`), checking the
earlier sections against revision 7's text; `FROZEN_HEAD_3.md`; the relevant entries of `INTEGRATION_TODO.md`; the
Fable delta cold pass's report (`cold-pass-2/REPORT.md`, D1 and N1–N9); and, for the #416 record, the Astra seat's
report and run manifest (`triple-audit/astra/`), the Fable seat's report (`triple-audit/fable/REPORT.md`), and the
Opus seat's findings and every refuter verdict in the results of workflows `wf_c7886624-d74` and `wf_3bdbf778-1ad`.
At the candidate H_claim `43ac12d0c` (a fresh read-only shared clone at `/private/tmp/regsync3/repo`, detached at that
commit) it read the commit messages and the diff `d3c107f2f..43ac12d0c` of `joulewise/`, `scripts/` and `configs/`
(nine files), the exclusion function's pack-scoped reasons and output, the harvest's NEG-8 screen around the loss
map, and the refusal allowlist. Every number written in this revision was read from a file or computed by the
author: the plan-tree, sizing, identity-pin and pin-registry digests with `shasum -a 256` at `43ac12d0c`, with the
three packs' `generate_configs.py --check`, `size_b5_window.py --check`, `write_b5_identity_pins.py --check` and
`python -m joulewise.b5.reference_spares --check`, all exit 0 there; the per-pack spans from `sizing_b5.json`; the
allowlist counts by script at both `d3c107f2f` and `43ac12d0c`; the ancestry of the four fix lanes with
`git merge-base --is-ancestor`; the empty diff of the four pinned estimator files from `a434e363d`; and the catalog
comparison by script (§13). No energy or power value of any window was read.

For revision 9, the author read: the integration's REG list from the census-ancestors lane onward (`REG_PENDING.md`:
the census-ancestors lane, the NEG-8 delta-fix lane, the T3 prune); `FROZEN_HEAD_4.md`; the latest entries of
`INTEGRATION_TODO.md` (cold pass 4, the Sol re-verification, the consult disposition, the second dry records, the
monitor-cost test); the Sol delta audit and its re-verification (`delta-audit-sol/REPORT.md` and
`delta-audit-sol-2/REPORT.md`, with their run manifests for the model and effort); Fable's cold passes 3 and 4
(`cold-pass-3/REPORT.md`, `cold-pass-4/REPORT.md`); and the second dry records (`dry-records-2/DRY_RECORDS.md` and the
structure of `dry-arm/dry-arm.json`, read for its fields only; its census output, which holds other sessions' prompt
text, is cited by hash and not quoted). At the int5 head `fe28e5a0c` (a fresh read-only shared clone at
`/private/tmp/regsync4/repo`, detached at that commit) it read the commit list and the diff `43ac12d0c..fe28e5a0c`
of `joulewise/`, `scripts/` and `configs/`; `agent_identity.py`'s header and rules; the census argvs of
`night_gate.py` and `hazards/arm.py`; the harvest's NEG-8 screen, allowance record, reference-loss naming and
reference identity check; the verdict writer's strict loss and its strict predicate; the custody triangle in
`whole_window.py`; the exclusion function's effect order; `identity_pins.json`'s reference unit; and where
`scripts/prewindow_check.sh` is still called. Every number written in this revision was read from a file or computed
by the author: the plan-tree, sizing, identity-pin and pin-registry digests with `shasum -a 256` at `fe28e5a0c`, with
the three packs' `generate_configs.py --check`, `size_b5_window.py --check`, `write_b5_identity_pins.py --check` and
`python -m joulewise.b5.reference_spares --check`, all exit 0 there; the empty diff of the four pinned estimator
files from `a434e363d`; the ancestry of the lanes with `git merge-base --is-ancestor`; the allowlist counts by script;
the SHA-256 of every report and dry record cited (§2 item 6, §9.1); the absence of any cooldown line in the runner,
controller and harvest diff; and the catalog comparison by script (§13). The census interpreter rule is described
from the orchestrator's text of the pending commit, which the author could not read; §13 lists what is to be checked
when it lands. No energy or power value of any window was read. (Revision 10 replaced that description with one read
from the merged code.)

For revision 10, the author read: the whole of the integration's REG list (`REG_PENDING.md`, all ten sections), the
resume and seal-preparation notes (`RESUME_2026-10-07.md`, `SEAL_PREP.md`), the rule carried in review briefs
(`REVIEW_BRIEF_RULE.md`) and the triple-audit dispositions in `INTEGRATION_TODO.md` (for finding A5's deferred lane);
the Sol delta audit's finding A4 and the re-verification's finding R1 in their reports (`delta-audit-sol/REPORT.md`,
`delta-audit-sol-2/REPORT.md`); and this file and the analysis plan from end to end. At the int5 head `9b0c680ed`
(the integration worktree, read only, and a copy of that commit's files made with `git archive` at
`/private/tmp/w1007-regprep/snap`) it read: `joulewise/agent_identity.py` whole, and the same file at `43ac12d0c`
and `fe28e5a0c` for the two mechanisms that failed; the commit messages and the diff `fe28e5a0c..9b0c680ed`; every
caller of the matcher (`night_gate.py`, `hazards/arm.py`, `quiet_admission.py`, `arm_readiness_evidence_t0.py`, the
driver's and the watchdog's census calls); the chain's spare-retry command line; the NEG-8 evaluator's survivor
conditions; the harvest's allowance record writer and its catalog path; the digest census and the D-165 rationale
census, to learn which lines of these documents a test in the integration tree depends on. Every verdict in §4.5's
worked example and in its account of the rule's errors was computed with the merged `identify` function (46 command
lines; the probe scripts are kept beside the catalog scripts in
`/Users/edr/night-archive/gate-prune/wave-1007b/reg-prep/`). The digests of §13's revision 10 record were computed
with `shasum -a 256` on the copy; the empty diffs with `git diff`; `tests.test_agent_identity` and
`tests.hazards.test_refusal_allowlist` were run on the copy with `/opt/homebrew/bin/python3.13 -B`. The dry-arm record's
census output was not read (§2 item 6). No energy or power value of any window was read.

Revision 11 follows a comparison of every checkable statement of this file, the analysis plan and the catalog with
the code at the int5 head `9b0c680ed`; four writers then each corrected one part. This paragraph records the reading
of the writer of §§7–10 and §§13–16. It read the list of mismatches the comparison confirmed and the orchestrator's
rulings on them (`/Users/edr/night-archive/gate-prune/wave-1007b/reg-fidelity/REG_FIDELITY.md` and
`ORCHESTRATOR_RULINGS.md`, with the notes of the two readers who had checked these sections). The writing was done
in two sittings; the second re-read every changed sentence against the code and corrected eight passages, the
dispatch passage of §7.2 among them. At `9b0c680ed` (the files of that commit, read through `git show` and a read-only
worktree at it, because the integration worktree had by then moved on) it read:
- in `joulewise/b5/harvest.py`: how the verdict is chosen and what `finish` writes, the stage-journal reader, the
  call of the exclusion function, the `clock.systematic` rule and the capture assessment that feeds it, the
  identity supersession with its table of checks, the code-identity and roster-dispatch steps, the function that
  reads each stage's dispatch and its lookup of a reader in the plan module, the roster's duplicate listings, the
  yield summary, and the emit sites of `calibration.no_bracket` and `collection.zero_yield`;
- in `joulewise/b5/plan.py`: the dispatch reader and the plan writer's refusal on it;
- in `joulewise/b5/chain.py`: the stage journal, the chain's stops, the calibration arguments, the `DEVIATIONS`
  list and the function that builds each stage's command; and, in the three plan trees, which stages carry a
  countdown;
- in `joulewise/b5/driver.py`: the stage roles, the minimums, the yield status and the driver's own reading of a
  stage's order manifest;
- the arm's battery rule (`joulewise/hazards/battery.py`, `joulewise/battery_float.py`) and the arm's pack collector
  (`joulewise/flags/collect.py`);
- `first_claim_usable` and every place that names it;
- the capture tool's countdown and display-sleep code (`scripts/validate_powermetrics_fiducial.py`) and the
  runbook's `calibrate_slot`;
- the sizer's arguments (`scripts/size_b5_window.py`) and the member allowances of `sizing_b5.json`;
- `joulewise/authentication_io.py`, and the call sites of the NEG-8 evaluator, bound and re-derivation in
  `joulewise/whole_window.py`, `scripts/run_campaign.py` and the harvest;
- `scripts/harvest_b5_window.py` (what the harvest command prints);
- commit `a28e8611e`, and the section of Fable's cold pass 4 report that §9.1 quotes.

It computed five things itself. The role and the minimum of a GAMMA diagnostic stage came from the driver's own
`_stage_role` and `_min_valid` (`science`, 1). The 5.3% of §7.3 is 1 − (36/37)². The publication counts and the
63 s of §9.2 came from the B0AC validation run's SMC reads and phase marks
(`/Users/edr/night-archive/wallmeter-probe/verify/run-20261006T221233Z/`), which is a probe run and not a window:
536 publications (37 idle, 270 load, 229 recovery), 126 of them nonzero, all in the load, covering 63.0 s. The
dispatch facts of §7.2 came from running the harvest's `stage_dispatches` and the plan module's
`resolve_stage_dispatches` on the three plan trees at `9b0c680ed`: ALPHA and BETA, ten of ten collection stages
unresolved by the harvest and 119 run ids each through the order manifests; GAMMA, none unresolved and the same 101
run ids either way. The counts of flags by code in the harvest summaries of the cooldown smoke's runs 3 and 4 (§2
item 7; an ALPHA pack, not a window of this block) show the same on a real harvest: one `roster.dispatch_unresolved`
and ten `yield.harvest_disagrees_with_window` each; only those counts and the list of unresolved stages were read
from them. The count rule of §13's "28" came from comparing the catalog at `c6843537` with the test fixture at
`d3c107f2f` (14 codes in the fixture and not in the catalog; one code, `g3.recompute_failed`, with another effect).
No energy or power value of any window was read.

Revision 12 applies the seal gate's stage-1 rulings, which were made on revision 9, and the orchestrator's rulings
that followed revision 11; five writers each wrote one part. This paragraph records the reading of the writer of
§§7–10 and §§13–16. It read, in full unless a part is named:
- the seal gate's stage-1 ruling (`/Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE1.md`). The judge's
  replacement texts in these sections were copied from that file by a script, not retyped. The stage-1 refuter's
  file was not read: its five challenges are known to this writer through the judge's dispositions only;
- the seal landing's procedure and its list of facts (`/Users/edr/night-archive/gate-prune/wave-1007b/seal-land/`:
  `SEAL_LANDING.md`, `REGISTRATION_FACTS.md`), the independent review of that lane (`REVIEW.md`: its verdict, the
  table of findings and findings F1 to F3 in full) and the orchestrator's ruling on it (`ORCHESTRATOR_RULING.md`);
- Fable's delta cold pass 5 (`/Users/edr/night-archive/gate-prune/cold-pass-5/REPORT.md`);
- the orchestrator's rulings on the comparison that preceded revision 11 (`reg-fidelity/ORCHESTRATOR_RULINGS.md`)
  and on the attribution floor (`q5-attribution-floor/RULING.md`, with sections 1 and 6 of the report it rules on);
- the map of blinding made for the design of the analysis code (`l9/map/x-blinding.md`), from which the custody map
  of §8 is taken, and the work list of the harvest lane (`harvest-lane/WORKLIST.md`).

At the integration head `9395cecfb` (the integration worktree, read only) it read what the revision 12 record of §13
lists row by row: the two functions that class a changed path, the plan writer's and the harvest's check of this
file's digest, the harvest's archive layout and file creation, the three writers of RESTRICTED flags, the list of
record files the driver publishes and the courier's instruction, GAMMA's stage graph, the three analysis programs
that print results, the plan writer's reading of a sizing allowance, and the option by which the harvest command is
given a sealed inventory. On the branch `lane/2026-10-07-seal-rulings` it read the four commits and the files they
change. It computed four things itself: the two SHA-256s of §9.1, with `shasum -a 256`; the 33 window exclusions of
the allowlist on that branch, by loading the file; GAMMA's 101 planned members, by adding the stage graph's counts;
and 0.031073829 s × 32.697 W = 1.016 J in §14 Q5. The other numbers of §14 Q5 are the ruling's; they come from
window a10 and from block 3, neither of which belongs to this block. Of the rehearsal archive named in §13 only
directory and file names were read. No energy or power value of any block-5 window exists, and none was read.
