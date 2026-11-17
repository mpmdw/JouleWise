# R1 arm checklist — preparation, not a READY declaration

Intake: Mon 16 Nov 2026, 18:09:52 PST (`date`). User task and RL-174 B/E
select this [AGENT] preparation ahead of fillers. No active stop card in the
worktree. No measurement Mac contact or measured data read. RUN_STATE is
lead-owned and was not edited. Evidence below is source/operational prose,
never a new hardware validation. `DONE` closes only the named sub-line;
every fresh check marked OPEN must still be recorded by its owner.

Source keys (immutable snapshots):

- **R:** `ebff15ad27e831499dd65796b3727d8c5d451e21`,
  `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
  RL-174 was read in full first, then RL-172, RL-173 and the cited
  R1 authorities. RL-174 supersedes the older census on host/storage/dates.
- **S:** `origin/main@0656dfe3a4263629e1d752933d386b99145fe8ac:RUN_STATE.md`,
  items 344–376; also the referenced items 306, 314, 328, 329.
  Item 376 lifts the offload-window hold at 18:01:50. No inference about
  what the Mac has done after that snapshot is made.
- **S+:** final fetch 2026-11-16 18:33:20 PST (`date`): main `6fc02b192`,
  item 377 records F0 run 6 launching around 18:20, expected close ~20:20,
  worst ~21:45, fence ~22:20. It must finish before native staging.
  The old R0 path is archived; the magistrate restored a hash-verified
  R0 file for the 60-key check. This is a prose update only, no file opened.
- **P:** `b2e01464d6d4fbf2901ff4d4154df9455104a12a`, tree
  `c904864e46879a4adfbdf0b467d4da1ee5928285`; owning procedure
  `docs/align/r1_arm_runbook.md`, runtime contract, and R1-to-W1 chain.
- **C:** `/Volumes/JW-EXT/scratch/mbp-plan-1116/seat-census/FINAL-MESSAGE.md`
  §3, older refs `38aa22e50` / `8fd5c8cc5`; useful inventory, not later authority.
- **V:** [VERIFICATION.md](VERIFICATION.md), fresh off-host checks and source
  census; [SOURCES.sha256](SOURCES.sha256) lists ten condition-13 paths,
  seven additional Part C paths, then eight route/input paths.

The inherited checklist is RL-122 §7, replaced by RL-145 §5 step 4,
supplemented by RL-145 close §10 / RL-148 §6, and restored with amendments
by RL-149 §5.12. The following retains each line, including supersessions.

| ID | Checklist line and current reading | Status, evidence, exact remaining action / owner |
|---|---|---|
| A01 | Round closed; adopted values named | **DONE.** R RL-149 §1.1: no-hold D, N_chunk 4096, Automatic, TV0h/TV1h. KIT records these; no new design choice. |
| A02 | Ed's answer recorded; subsequent ruling names design, chunk, series mode (close §10) | **DONE.** S 314 records Ed's (c) “Keep K, reword”; R RL-149 explicitly takes that answer and adopts the design. |
| A03 | PR diff is the ruled build rows, nothing wider; kit change merged | **DONE at P.** #777 merge `f30a97d00`, #783 merge `c3f4bacd8`; #790/#798 repairs admitted by RL-170/172b/172c. These are ancestors of P. **OPEN — lead:** dispose the apparent #734/main-merge prerequisite in S 355; question Q1 in forecast. No merge performed here. |
| A04 | `thermal_gates.py` and `thermal.py` equal `a6a09e6d7` | **DONE at P.** Exact hashes in SOURCES; protected-file test passes (V). Staging rechecks working bytes. |
| A05 | Ten condition-13 hashes listed; prior nine-unchanged / one-token table (RL-122) | **DONE, superseded table made explicit.** SOURCES has the current ten. The old `99622e96c`/TVh0 one-token test is historical, not required against the ruled #777/#783 build. Protected gates remain unchanged. |
| A06 | Cold review has no open finding; CI green | **DONE for build/repairs at P.** #777 RL-153; #783 RL-156/159; #790 RL-170 extended by RL-172c, tree equals P. GitHub API `ci` run 43712204542 at P completed success. **OPEN — lead:** adopt V and this package's final diff; resolve carried text/record conditions A19. |
| A07 | Script-derived second pick; regenerated table accepted | **DONE as selection authority.** R RL-145 §3, RL-156 §2; P pins `sensor_ruling_rl145.json` and `smoke_part_b.rl145.json` (SOURCES). TVh0 retired; TV1h chosen once from saved classification. No new hand pick. |
| A08 | Part A passed, G0/release values stated (old RL-122) | **DONE by supersession.** RL-145 close §8 substitutes Part C for Part A; RL-149 §5.11–12 requires the counted Part C. Do not schedule a new Part A as preparation. |
| A09 | Fixed Part C at adopted commit, desk exclusion verdict per turn | **DONE as recorded, no measured file reopened.** S 328: counted second Part C `c3f4bacd8`, pass; desk excludes D_bank for `thermal.powermetrics_non_nominal`. RL-170 §2, RL-172b §2 and RL-172c carry it to P. Later standing F0 is not a new prerequisite. |
| A10 | Carry at merge: ten + seventeen-path census; changed imports explicitly accounted | **DONE source census and text preparation:** ten unchanged; only `v4_registration.py` differs within seventeen paths, +1 desk-seal closure entry. [CARRY-RECORD-DRAFT.md](CARRY-RECORD-DRAFT.md) supplies the imported-module accounting and S 329 correction. **OPEN — lead:** adopt/publish the correction required by RL-172b; the path-only census does not discharge it. |
| A11 | Ruling 1(f) evaluated on Part C seconds; B_D ≥6144 or ruling replaces it | **DONE by replacement, not a fresh 1(f) receipt.** RL-148 §2 / RL-149 §1.5 replace the admission bar with the typical case; R gives passing Part C table. RL-170 retires receipt route; source checks refuse a receipt file/key. **OPEN — lead:** point the arm item to the adopted Part C typical-case table including recorded tool seconds; this session may not read those records. |
| A12 | Typical-case bar implemented in kit and evaluates session's own seconds | **DONE implementation** in merged #777/#783/#790; V synthetic acceptance/refusal tests. **OPEN after R1 — lead:** evaluate its own record before W1 fills. This is not a requirement to possess future R1 results before R1. |
| A13 | Amendment constants in a draft; DEVIATIONS rows in PR | **DONE preparation:** [AMENDMENT-R1-DRAFT.md](AMENDMENT-R1-DRAFT.md) supplies ruled constants, outcome/duty/U1/blackout text and precise existing-row map. P DEVIATIONS already has duty, pair, stamp, blackout rows. **OPEN — lead:** place/adopt this text in the actual B-S-admit amendment PR and record its head/path; no speculative registered-text rewrite made. Draft need not be merged for R1 (RL-149 §5.12). |
| A14 | Mac 60-key/config/classes check with the new pair | **OPEN — magistrate:** run P's R0 `check` on the verified restored R0 path from S+ 377 at the final worktree, fatal on failure; assert TV0h/TV1h/[Tf08], 60 keys, 16 die / 44 heatsink, source sha `e6231a8f…769b`, config sha `272aecb8…32f46`; record full output. V checks committed config only; S/S+ native checks were for F0, not this session. |
| A15 | D-7 fresh packet, actual weights/stack, hash comparison | **OPEN — magistrate:** archive prior fixed packet if present, remove fixed name, prepare on final P with real weight/stack checks; record actual packet SHA; arm record must match with no packet-absent flag. P runtime contract D-7; commands in ITEM. No dependency installation. |
| A16 | W1 kit accepts pair given `ok` night confirmation | **DONE off-host synthetic:** V `test_w1_rl122_kit.RebindPairDryCheck`; **OPEN — lead:** adopt output in session checklist. Actual session thermometry still must be `ok`. |
| A17 | N_chunk binds from slots | **DONE off-host synthetic:** V `test_v4_kit.R1BudgetBindingTests.test_thermal_policy_binds_n_chunk_s6_and_s7`; **OPEN — lead:** cite the tested P bytes. No numeric slot fill attempted. |
| A18 | Kit takes 3(a) planning release | **DONE off-host synthetic:** V `test_w1_rl122_kit.PlanningReleaseTests`; RL-152 §1.1 applies pattern to TV1h. **OPEN — lead:** adopt in checklist. No threshold/segment change. |
| A19 | Dispositions in arm item; carried repair conditions | **DONE text preparation:** ITEM and CARRY-RECORD-DRAFT list dispositions/correction; AMENDMENT names #790's retirement merge. **OPEN — lead:** adopt/publish the record and issue dispositions. RL-170 note 3's contract wording is explicitly non-gating and prepared in CARRY for its next owning PR. S 346 already reissued F0 at P; no further F0 is required. |
| A20 | Thermometry `ok`; duty as restated; any gated D H record is a defect | **DONE draft disposition, OPEN outcome — lead after R1.** Exact pair by name, own classification/ok confirmation (RL-156 §2); extra alias keys report only. Duty own-stop exception needs all four conditions (RL-156 §1), and at least one valid three-turn run. Any H comes to research lead. |
| A21 | Constants/design draft cold attacks, research-lead cold pass, Ed merge | **OPEN — lead commissions seats / research lead / Ed, for W1.** These are not invented as new R1 arm gates: RL-149 §5.12 permits unmerged amendment draft; §5.13 owns W1 signing. No seats or merges performed here. |

Runbook procedural lines are itemized below so a green build is not mistaken
for a complete arm. All host actions are for a separate, clean lead/magistrate
session, never this preparation session.

| ID | Runbook/checklist line | Status and exact owner/action |
|---|---|---|
| B01 | Existing pinned environment, clean final measurement checkout | **DONE script preparation**, `stage_mbp_r1.sh`; **OPEN — lead/magistrate:** run at a close, preserve local work, detached P at KIT path, source/stage record and package commit. Keeps the existing venv; does not move a possibly armed checkout. |
| B02 | Dependency files unchanged, imports/version check | **DONE source comparison to `9c40e4e5d`** (V). **OPEN — magistrate:** real imports print `0.31.2 0.31.3 5.12.1`, existing pinned venv. No pip/install. |
| B03 | R0 host route: Mac15,9, AC, not charging, no external volume | **OPEN — magistrate:** fresh readbacks; keep-awake job remains loaded; unplugged SSD is part of notice, not this session's contact. |
| B04 | Narrow sudo pmset 0/2, network-time permission, working powermetrics | **OPEN — magistrate:** read sudo rules and normal preflight; powermetrics is exercised only by authorized route. Never run a live capture/probe from this session. |
| B05 | `pmset custom/assertions`, no owed High Power marker, host lock untouched | **OPEN — magistrate:** read fresh, resolve owed restore through owner; do not delete marker or lock by hand; Automatic admission. |
| B06 | Network time OFF, frequency word zero; clear replay/runtime override environment | **OPEN — magistrate:** use established zero-step route; unset all seven runbook variables before prepare. Follow issue-time restore text Q6. |
| B07 | Latest close clean, reported Check, fence gone, copy/offload verified, close interval | **OPEN — lead/magistrate:** identify newest host work at issue/arm, never rely on S's old close. 300 s after campaign; 1200 s after F0/F2/other. No unproven process group/restore, no open hold. RL-173 A / RL-174 D offload failure holds every next arm. |
| B08 | No agents/R12/builds/analysis/monitors competing; no live packer/transfers | **OPEN — magistrate:** fresh process/agent/volume census, no loaded night/smoke job, no pending iCloud transfer; RL-174 four host lines. S 376 closed the old packer window, not a future host readback. |
| B09 | Select t0 after maintenance, notify if quiet segments cannot avoid listed jobs | **OPEN — lead/magistrate:** issue-time expected-duration print and scheduling notice; retain R1's 02:00–02:35 rule. RL-172(f) does not change it. **DONE** bounds in KIT/PLAN draft/V; expected runtime remains UNKNOWN (Q4). |
| B10 | Whole-minute t0 ≥15 min ahead, fresh custody, installer cutoff/budget | **DONE preparation:** PLAN inputs and tested route. **OPEN — magistrate:** final t0 only after review/notice ready; install cutoff t0−300, reserve installer 180 s before cutoff; move t0 if needed. |
| B11 | `size`, `prepare`, disk print, inspect arm record and plan | **DONE off-host sizing; OPEN — magistrate:** native fresh plan/arm record with actual paths/t0 and packet binding. No `ac_powermode` key; HAZARD_PACK, no W1 roster. Never install the draft JSON. |
| B12 | Default disk allocation unsized; ≥20 GiB arm headroom / ≥10 GiB live floor | **DONE disclosure** in plan/item. **OPEN — lead/magistrate:** optional sourced R1 estimate, disk readback. RL-174's 40 GB kit line concerns campaign kits; retain the actual R1 route's thresholds; do not import Block 5's 182 MiB/member. |
| B13 | Driver/window/bookend/clock sizing intact | **DONE source/synthetic:** 102168 s driver, 119880 s outer +300 shutdown, sampler 5764 s; S-7 5 ms/span−0.25 ppm, own-fit placement, diagnostic bookends. Ceiling is not expected time. |
| B14 | Render/review both plists; chain-source literal; plan head checked at install | **OPEN — magistrate:** render fresh, inspect launch and deadman, verify all paths/head/packet SHA, record digest. V synthetic mutated-chain exit-65 and multi-day tests pass. |
| B15 | Send full ordinary notice; receive/read veto; no new approval protocol | **DONE text preparation** in ITEM. **OPEN — lead/magistrate:** use existing authorized route, record send/interval/fresh Ed directive read (Q5). This worker sent nothing. |
| B16 | Lead records READY; typed session selects own route | **DONE typed preparation:** ENTRY-DRAFT; **OPEN — lead only:** all outstanding checklist evidence adopted, actual item/kit/worktree staged, READY record on main. It preempts lower-priority arms at next clean close. Never feed draft to campaign controller. |
| B17 | Install, launchctl readback both jobs, sleep display, all agents exit | **OPEN — magistrate only after notice/veto:** run runbook install; record return codes and jobs, sleep display and leave before t0. No driver or live `--dry-arm` under an agent. |
| B18 | No Git operation in measurement checkout install→t0 | **OPEN — all operators:** enforce through t0, including status/fetch. Staging and tests precede install; no suite runs on MBP while queue live (RL-172(i)). |
| B19 | Post-return terminal + chain exit first, not launcher's GO | **OPEN after R1 — lead:** apply registered read boundary in actual issued item; preserve custody. This worker opens neither result nor slots. |
| B20 | Restore network time / before-next-arm zero step; observed Automatic | **OPEN after R1 — lead/magistrate:** exact restore readbacks, no unproven group. Runbook says network time ON on return, current campaign arms require OFF/zero; lead reconciles explicitly at issue (Q6). |
| B21 | R_op after step-30b redo; A–B–A releases G0, 600 s caps | **OPEN after R1 — lead:** flag redo-derived R_op to research lead before using it; hand-read three releases, no change to caps. |
| B22 | Uninstall, preserve rejects/bookends, stray meter/hazard process checks | **OPEN after R1 — magistrate:** use route uninstall, verify actual process absence separately from Automatic restore; retain recovery markers if termination unproven. |
| B23 | Post-R1 kit fill and W1 signing | **OPEN after successful R1 — lead/Ed:** R1-to-W1 chain, U3/WP19, amendment/seal/receipt and one final closure regeneration. No W1 claim or 12.4 h sizing borrowed for R1. |

Remaining preparation has owners above; no open pure text/script/test task is
left as an offer. Native staging, real D-7/host/notice work, item issuance,
authority adjudication and future outcome checks remain explicitly open.
