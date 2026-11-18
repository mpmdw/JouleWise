# Qualification drafts at the PR #812 merge pin

**DRAFT / HOLD_FOR_FIT_FREEZE.** The qualification pin is
`6e9d42f1dd3d308bc9239143d0d634ab965e50e1`. Its 38 frozen path entries
match PR #812’s reviewed head `0d03cb7833bb8b15bc391127a7fe5519b7d98602`.
The three kits use the PR #794 source and the merged runner’s `pin-kit`.
W1-line comparison baseline remains `c3f4bacd8013ca98c19cf8d41f830c701930cd41`.

| Block | t0-date (PST) | Kit SHA-256 | Expected seconds s01 / s02 |
|---|---|---|---|
| qual-01 | Fri 20 Nov | `ce5c16d221f838ca8f06af68aa7380a4cb0d6fb4b5b5825444db6c7433fd40c7` | 12262 / 12310 |
| qual-02 | Sat 21 Nov | `f421d6a4c9a7214a1c220e4009619c7ea02590031a25122b6f379dab8fec7f75` | 12262 / 12310 |
| qual-03 | Sun 22 Nov | `9c4396ea1cff66fc4bbcf944ee2142bfb8b18f3a8547269c163faee9a3e03e88` | 12310 / 12262 |

Each span has a 24,750 s work bound and 2,510 s of retry and cleanup
reserve. The launcher minimum is 27,260 s and the item adds a 900 s
margin. The finite queues expire Mon 23 Nov at 00:00 PST. The predicted
batch, including overlap during soak, can tighten that window at arm.

The lead stages the kit and authenticated queue, supplies freeze 2 and the
per-kit exact-pin admission records, and verifies the fresh host readbacks
and applicable stops. Before qual-01-s01, the registered `lm-qual-01`
manifest and its ledger row belong on main with the exact kit hashes. The
lead seeds the sequenced attempt ledger and stages the latest predecessor’s
identity-bound close Check if its older receipt lacks a span id. Before
qual-01-s02 the RL-172a soak comparison and RL-181 §4(a) hand-read must
pass. See [record shapes](evidence/record-shapes.md) for prior same-pin q0
evidence or recovery after a child t0 refusal. The first native run on this
pin is a separate lead-controlled prerequisite under RL-179 F-11.
[Same-pin filler drafts](../f2-stab/qual-pin/README.md)

The build and regression suite operate on pinned source, configs and
synthetic fixtures. Run from this folder with a seat-local evidence directory.

```sh
python3 -B build_items.py --dates qual-01=2026-11-20,qual-02=2026-11-21,qual-03=2026-11-22
bash tests/run_all_gates.sh
```

[Qualification handoff and verification](../../../../../run_reports/2026-11-18-qual-items-merged.md)
· [PR #812 ledger authority](../../../../../run_reports/2026-11-18-pr812-ledger-required.md)

## Close-census repair — 2026-11-16

All unissued item copies now select the latest close by the receipt's recorded `ended.epoch_s`, never filesystem mtime. Identity is chosen before ceiling to whole seconds; missing/unreadable/invalid stamps and equal latest epochs stop. The exact selected campaign span's marker remains mandatory. The non-campaign Check rule is unchanged. Generators carry the same repair; the 1118 standing-F0 renewal is included. Earlier test captures and source-item evidence are preserved.

New tests execute the embedded functions in bash and zsh, keeping an older receipt's bytes unchanged while giving it a later mtime; its marker cannot authorize a newer uncopied campaign. The actual latest marker passes. New evidence lives under `evidence/fix-2026-11-16/{bash,zsh}/`; the current standing renewal's derivative comparison is `evidence/fix-2026-11-16/standing-f0-r2.diff`. See `docs/run_reports/2026-11-16-f2-item-fixes.md` for results and the issued-item assessment. This repair issues no item and clears no live prerequisite.

## Round 10 (Astra audit)

- **Preflight.** Start and Run perform the native checklist before the gate consumes `CHECKLIST_OK`. Each call clears any supplied flag. The full Start regression runs with it unset and stubs the native commands.
- **Pair cutoff.** Each s01 prints the D8 ceiling of 16:32:00 PST. For a full date and no tighter queue or batch bound, backing 27,260 s out of s02’s 23:59:59 latest t0 yields an effective s01 last second of **16:25:39**.
- **Recorded t0.** The launch blocks pass the authorized date and exclusive cutoff to the pinned child, which validates the exact start before span work.
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

**PR #812 delta audit.** Run forwards the maximum of window start, issue, watcher observation, queue commit, predecessor and latest proven closes, and batch release. The pinned sampler and child both read a sleep-inclusive monotonic clock. RL-179 F-2 replaces timed waits with proof bound to the actual latest receipt. The relevant close epochs still establish the earliest permissible start. [Delta-audit repair report](../../../../../run_reports/2026-11-17-pr812-delta-repair.md)

**PR #812 round 3.** Start and Run select the latest attempted span from the launch/start-plan ledger. Its own receipt must match the span id and show passing restore readbacks. The launcher rechecks the proof and records its new attempt before bootstrap. Run and the child compare the selected close stamp at nanosecond resolution. [Attempt ledger and close receipt shapes](evidence/record-shapes.md) · [Round-3 report](../../../../../run_reports/2026-11-18-pr812-close-proof.md)

**PR #812 pipeline round 1.** Every qualification launch must supply the attempt ledger and prior close receipt before bootstrap. A bootstrap failure with valid authority leaves a pending attempt that blocks its successor. [Ledger authority report](../../../../../run_reports/2026-11-18-pr812-ledger-required.md)
