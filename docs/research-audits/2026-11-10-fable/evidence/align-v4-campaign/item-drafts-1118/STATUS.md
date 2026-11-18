# Qualification and STANDING-F0 r2 drafts — 2026-11-16 PST

**DRAFT / HOLD_FOR_FIT_FREEZE. Nothing issued.** These items carry the PR #812 audit-repair pin. The [original admission record](../qual-lines-794/LINES.md) and [earlier successor report](../../../../../run_reports/2026-11-17-qual-pin-t0guard.md) document their respective pins. The [audit-repair report](../../../../../run_reports/2026-11-17-pr812-audit-repair.md) records the checks on this pin.

The forecast below predates C.4. Recompute arm and close times at issue using the fresh boot prediction. With a 02:08:39 batch, the forecast midnight arm holds until 02:35:39.

| Item | t0-date window, PST (00:00:00–23:59:59) | Forecast t0: freeze Thu19 12:00 / slip Fri20 12:00 | Expected / work-worst close at those forecast starts | Exactly missing before issue; owner |
|---|---|---|---|---|
| qual01-s01 | Thu19; slip requires Fri20 re-date | Thu19 12:00 / Fri20 12:00 | Thu15:24:22 / Thu18:52:30; slip Fri same times | Lead: freeze2 commit/coefficient path/hash, per-kit admission pointers and exact line2 equality, four host-state lines/readback, queue commit/staging, prior dev-05-s02 confirmation, lines6/7/9 and issue fills. INCLUSION_RECORD filled by RL-174 B.5; dev-05-s01 desk-final + typed Q1 record required (RL-174 E.5). Magistrate: live arm observations. Builder: no remaining prerequisite after verification. |
| qual01-s02 | Thu19; slip Fri20 | Thu19 15:29:22 / Fri20 15:29:22 | Thu18:54:32 / Thu22:21:52; slip Fri same times | Same shared prerequisites; dev-05-s02 desk-final + typed Q1 record required (RL-174 E.5); lead also records qual01-s01 soak/reference-schema hand comparison SAME against dev-05 (RL-172a F1), then issues inside three-ahead/24 h limits. Magistrate checks predecessor clean at arm. |
| qual02-s01 | Fri20; slip Sat21 | Fri20 00:00 / Sat21 00:00 | Fri03:24:22 / Fri06:52:30; slip Sat same times | Shared prerequisites, qual01 soak hand record, qual-02 cold seat pointer, dated queue/staging and own issue/watch fills (lead). Predecessor qual01-s02 clean at arm (magistrate); actual k−2 desk + typed Q1 debt paid (lead). |
| qual02-s02 | Fri20; slip Sat21 | Fri20 03:29:22 / Sat21 03:29:22 | Fri06:54:32 / Fri10:21:52; slip Sat same times | Same, with predecessor qual02-s01; own issue/watch fills and actual cross-block debt (lead); all fresh operational checks (magistrate). |
| qual03-s01 | Sat21; slip Sun22 | Sat21 00:00 / Sun22 00:00 | Sat03:25:10 / Sat06:52:30; slip Sun same times | Shared prerequisites, qual01 soak hand record, qual-03 cold seat pointer, dated queue/staging and own issue/watch fills (lead); predecessor qual02-s02 and fresh checks (magistrate); actual k−2 desk/Q1 debt (lead). |
| qual03-s02 | Sat21; slip Sun22 | Sat21 03:30:10 / Sun22 03:30:10 | Sat06:54:32 / Sat10:22:40; slip Sun same times | Same, with predecessor qual03-s01; own issue/watch fills and actual cross-block debt (lead); fresh checks (magistrate). |
| STANDING-F0-r2 | Opens Sun22 11:51:24; outer expiry Sun29 11:51:24; daily launch 02:35–22:40 | ≥Sun22 11:51:24 in either case, subject to live ladder/ledger | At that start: ~13:51:24 / 15:14:24; shared desk deadline 15:51:24 | Lead can issue ahead for activation at the planned start (later issue needs re-dating), rechecks current W1 head/hash qualification and any hold; magistrate checks all standing triggers/spacing/day/restore/copy/READY gates. Optional hold is inactive until lead issues it. |

Forecast assumptions: dev-05-s02 closes Wed18 ~07:00; all operational/desk/admission records ready at the assumed freeze; no intervening F0/F2/v4 occupation. Expected successors use expected close +300 s. Worst-close cells are **each span's work bound from its forecast start**, not a promise all six start at those times under worst cases. qual01-s02 after both first spans' work-worst durations would instead start Thu18:57:30 and close Fri01:50:00; qual02-s01 then waits for the actual fence/copy/close interval. F0/F2/non-campaign close adds 1,200 s. Actual fence disappearance and every gate govern.

Planner expected sums: 24,572 s per block, 73,716 s (20:28:36) over six spans, plus three internal 300 s gaps and date waits. Each work bound is 24,750 s (6:52:30); **launcher minimum 27,260 s** adds 1,950 s retry +560 s reserves; items allow +900 s start slack (28,160 s desk deadline). A shared desk fence remains. The pinned runner has no batch-window fence. `evidence/plan-*.json` contains the six actual pinned plans.

## Frozen facts and admission

| Block | Exact kit SHA-256 | Law spans / short leg | Expected s, s01 / s02 |
|---|---|---|---|
| qual-01 | 8d9ec7143d2e7b60d303a52ede374075bdaf807c4bbb214b418c269dba2dabbc | L001–L006 / L007–L012; L004=3151, L010=3724 | 12262 / 12310 |
| qual-02 | 612327b4fe5bbbcb0da28676a4d54e92c7d855a4c286157dbb3f4cc6073f923b | L001–L006 / L007–L012; L003=3151, L011=3724 | 12262 / 12310 |
| qual-03 | 85dfa025a84c7bdbcb79ecd0fa87bd52d1ffc7624e40fa94c5877646abd03bf9 | L001–L006 / L007–L012; L003=3724, L010=3151 | 12310 / 12262 |

The three kit documents in this folder derive from #794's kit source `6010985a3312c77bb8e4bb4bf5c920c4d49b8512` using the successor's `pin-kit`. Frozen checkout **`57ed7334ea7dbc24ed47dfbf70c29c41197c9f01`**, runner `cadence-legs-v1.1`. W1-line baseline **`c3f4bacd8013ca98c19cf8d41f830c701930cd41`**. Seeds 2026111422/23/28. Every span captures at its first own-shaped leg (L001/L007), with five span-shaped consumers, one A cell at 2k, one at 10k, two at 19458 and an adjacent 19458 L pair. The items omit `--batch-window`. Plan and launcher-plan probes include the retired midday and night boundaries.

No qualification span queues are on #794's source branch; `BLOCK-QUEUE.json` is a block ledger, not a span queue. Three finite queues are drafted **only here** and validated against the pinned law. Their expiry is Nov23 00:00 PST, ≤7 days after a Nov16 commit, checked against the authenticated queue commit at arm (RL-149 §2.8 line3). They grant no authority. No builder writes a READY/cold-seat/CI admission stamp; those record pointers remain lead fills. Full placeholder and observation shapes: [record-shapes.md](evidence/record-shapes.md).

F0 renewal: item346 ISSUED Nov15 11:51:24 +7 days = **Nov22 11:51:24 PST, epoch1795377084**. Planned renewal ends Nov29 11:51:24, epoch1795981884. Fetched W1 head remains **`b2e01464d6d4fbf2901ff4d4154df9455104a12a`**; main's item346 still names it. Pin/hash table/launch/Check rules carry unchanged; four-hour spacing, three per date, 02:35–22:40 latest-launch rule and 1,200 s after F0 persist. Existing ledger continues across renewal. Current derivative: [standing-f0-r2.diff](../qual-lines-794/verification/rebased-final/standing-f0-r2.diff); historical diff captures stay unchanged. The optional item374-form hold uses lead fills; item374's Mon16-only hold is not carried forward.

## RL-174 dispositions and remaining gates

**Former Q1 is ruled by RL-174 B.3.** Three distinct t0-dates, one qualification block each; two L pairs per block. The two-block/24-leg/10 h cap applies, is unused by this plan and is never a slip remedy. The generator and runtime gate reject a shared-date plan. Fewer than three pair-days gives `not_evaluable` for the ±0.10 word (RL-166b §4); more legs on another date cannot create a missing day.

**Former Q2 is ruled by RL-174 B.5.** `INCLUSION_RECORD` is filled with that ruling and its full audit commit. Six rules unchanged; maintenance overlaps print-only. `lm-qual-01` prints flagged/unflagged errors side by side and by-job counts, description only with no word. The lead appends the by-job count through dev-05 after its desk is final; the count gates nothing. No kit bytes or frozen path change.

**Host action is not a freeze-2 gate (RL-174 C).** Qualification runs on the host as it is. Each arm records service present/absent, corespotlightd present, indexing off, Time Machine destination none. The hygiene-state identity excludes boot time; an unplanned restart needs an event and refreshed four lines, with no restart hold. The maintenance print dates the spotlightknowledged stop to Sun15 15:32. Nobody changes hygiene settings from freeze 2 through qual-03 close.

**Expiry and debt.** All three queues already expire **Mon23 00:00 PST**, epoch 1795420800; those bytes are unchanged. The Fri20/Sat21/Sun22 slip leaves qual-03 no margin: a missed t0-date invokes the recovery instructions below. qual-01-s01 needs dev-05-s01’s desk-final and typed Q1 records, and qual-01-s02 needs dev-05-s02’s. Those named debts are checked in addition to k−2 debt across queues; a census that omits dev-05 cannot discharge them.

**Admission remains lead-owned.** RL-175 C.1 closes M0-F7 for all kits. Line 1 still needs the named Mythos Q2 confirmation and the lead's retry-reader evidence and signoff (LQ1/LQ2). Line 2 needs the exact-pin test comparison for this successor. Freeze 2’s coefficient commit/path/hash, queue commit/staging, actual desk/Q1/soak-hand records, current operational checks and issue stamps remain required. If #794 is integrated into W1 and moves its head, item346 and this same-pin F0 renewal are void and must be reissued (RL-174 E.2).

## Verification and reproduction

The earlier pin `0576ed76d` passed 21 CI jobs and matched the merged W1 baseline's empty failing-test set. Its draft wrappers passed 1,336 gate checks and 91 pinned checks. The audit-repair pin has its own verification record. [Earlier successor report](../../../../../run_reports/2026-11-17-qual-pin-t0guard.md) · [Audit-repair report](../../../../../run_reports/2026-11-17-pr812-audit-repair.md)

Original `80969605d` verification (before RL-174): **1092 gate, 91 pinned, 21 F0, 6 generator, 74 shell syntax and 60 Python compile checks; all pass**. These historical logs are preserved. Current RL-174 verification and its limits are in [LINES.md](../qual-lines-794/LINES.md) and `../qual-lines-794/verification/`. This update changes draft tooling and records only; production runner, kit and frozen paths are unchanged. Original logs: `evidence/lint.log`, `pinned-checks.log`, `gates.log`, `standing-f0-tests.log`, `redate-tests.log`; pinned re-check detail in `kit-recheck.json`. Read-only fresh peer review and lead disposition are recorded in `evidence/review.md`; this builder retains final diff/verification responsibility.

```sh
cd docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118
python3 -B build_items.py
bash tests/run_all_gates.sh
```

For a freeze-2 slip before any qualification t0, the lead regenerates all six items/queues/plans with one argument, commits the new bytes and issues fresh items:

```sh
python3 -B build_items.py --dates qual-01=2026-11-20,qual-02=2026-11-21,qual-03=2026-11-22
```

Fetch the source refs first if absent. The generator extracts allowlisted Python and shell source and two configs into a disposable directory inside this folder. Runner tests create labeled synthetic Git coefficients, queues and mock spans there, then remove them. Run the wrapper under both bash and zsh with a fresh `JW_DRAFT_EVIDENCE_DIR` for each. The lead obtains the remaining line 1 records, records both lines against the exact kit hashes and supplies the live prerequisites before issuing any span. The renewal names the item 377 verified R0 path and treats check failure as fatal (LQ5). The source digest and 60-key checks remain required.

## Close-census repair — 2026-11-16

All unissued item copies now select the latest close by the receipt's recorded `ended.epoch_s`, never filesystem mtime. Identity is chosen before ceiling to whole seconds; missing/unreadable/invalid stamps and equal latest epochs stop. The exact selected campaign span's marker remains mandatory. The non-campaign Check rule is unchanged. Generators carry the same repair; the 1118 standing-F0 renewal is included. Earlier test captures and source-item evidence are preserved.

New tests execute the embedded functions in bash and zsh, keeping an older receipt's bytes unchanged while giving it a later mtime; its marker cannot authorize a newer uncopied campaign. The actual latest marker passes. New evidence lives under `evidence/fix-2026-11-16/{bash,zsh}/`; the current standing renewal's derivative comparison is `evidence/fix-2026-11-16/standing-f0-r2.diff`. See `docs/run_reports/2026-11-16-f2-item-fixes.md` for results and the issued-item assessment. This repair issues no item and clears no live prerequisite.

## Round 10 (Astra audit)

- **Preflight.** Start and Run perform the native checklist before the gate consumes `CHECKLIST_OK`. Each call clears any supplied flag. The full Start regression runs with it unset and stubs the native commands.
- **Pair cutoff.** Each s01 prints the D8 ceiling of 16:32:00 PST. With the 24,750 s work bound, 1,950 s soak retry, 560 s cleanup reserve and 300 s close floor, a 23:59:59 s02 deadline yields an effective s01 last second of **16:20:39**. Earlier item or queue expiry moves it earlier still. The renewal computes the same dependent-pair bound in rule 7. The actual desk fence, verified copy, soak comparison and READY checks still govern.
- **Recorded t0.** The six launch blocks pass the armed date and exclusive earliest effective expiry to the child. The successor validates the exact receipt epoch before span work. The regression suite executes the successor bytes against all three kits.
- **F0 renewal.** Opens at item 346's expiry and can be issued ahead. RL-165 §3 rule 2 still expires it seven days after actual issue, so early issue shortens the new active interval. The renewal follows RL-174's ladder and removes the retired restart hold. [Current derivative comparison](evidence/round10/standing-f0-r2.diff).
- **Maintenance.** The pending F0 and twelve F2 checks share qualification's process predicate. For checks previously captured without it, `bird`, `cloudd` and `fileproviderd` are **unobserved**. Dev-05's variant B was already issued as main items 393–394. The counts remain print-only.

### Missed-date recovery

**Untouched block.** Verify that neither span has a recorded t0. Re-date both spans together onto a valid unused t0-date, commit a new finite queue, and issue fresh items. Supply a new finite expiry if the old one cannot cover the schedule. Preserve the three distinct dates and the predecessor order.

**Partially run block.** The span-keyed date gate implements RL-175 C.3 at `b26c0d0e7`. Preserve s01's recorded t0, original queue and receipts. The lead assigns only missing s02 to the next unused legal date, moves later untouched blocks whole, and issues only the remaining spans. The same kit binds the original legs and seeds. Each receipt must match its own span's date. A recorded t0 prevents re-arm. Under RL-175 A.2 a READY record cannot take effect between the halves.

If qual-01-s01 ran Thu19 and qual-01-s02 missed Thu19, use this date plan.

```sh
python3 -B build_items.py --dates qual-01-s02=2026-11-20,qual-02=2026-11-21,qual-03=2026-11-22
```

If recovery needs a later expiry, pass `--queue-expiry` with an explicit UTC offset, commit the new queue, and issue fresh items. The queue gate enforces the seven-day ceiling from the authenticated commit. The look uses each span's actual t0-date.

**Successor qualification pin (WS 5).** The lead's 2026-11-17 decision admits a successor containing Builder C's tested guard. The three draft kits move to that pin. Each kit changes its frozen commit and the two entry-script hashes. The per-kit admission checks still govern issue.

**RL-175 C.4.** All six items read boot time independently in Start and Run. The predicted OS batch uses boot + 12 h + 48 s, recurring every 24 hours. The hold starts when the pinned expected close reaches the predicted batch and lasts until batch start plus 27 minutes. Run forwards the authorized Los Angeles date, earliest start, exclusive cutoff and its bracketed clock anchor. The cutoff includes watcher expiry. The child checks the projected start interval and its wall sample before creating output and records the admitted t0 and authority. C.3 reads nanoseconds when present and floors legacy decimal epoch seconds before looking up the local date.
