# F2 item drafts, revised 2026-11-16 PST

Four complete, synthetically tested drafts cover all twelve legs of the admitted four-piece layout. **Nothing is issued. No item is marked READY to issue before its live prerequisites are recorded.** The original tests remain in [evidence/verification.txt](evidence/verification.txt); the repair evidence is in [evidence/fix-2026-11-16/](evidence/fix-2026-11-16/) and the [fix report](../../../../../run_reports/2026-11-16-f2-item-fixes.md). The lead inserts issued items into RUN_STATE on main; this builder never edits that file or main.

| Item | Roster / predecessor | Status: exactly what is missing before issue |
|---|---|---|
| [ITEM-f2-p01](ITEM-f2-p01.md) | L001–L003 / dev-03-s02 (L004–L012) | **READY as a draft after F1/F2 repair; NOT READY to issue:** dev-03's same-pin first-span clean restore and class A/L002 hand-gate release; lead's adoption of the recorded F2 re-check; MBP staging of the v1.1 kit, committed queue a and worktree. Fill issue time and watcher observation when issuing. The predecessor may still be pending at issue under RL-173 D; its clean close is mandatory at arm. |
| [ITEM-f2-p02](ITEM-f2-p02.md) | L004–L006 / f2-inst-p1 | **READY as a draft after F1/F2 repair; NOT READY to issue:** p01 prerequisites plus piece 1's live PASS hand-read, lead-committed queue b, its exact path/hash, and staging. Do not issue across dev-04's L005 gate; its release or the lead's applicable contingency must already be recorded. Fill its own Wednesday issue/watcher stamps. |
| [ITEM-f2-p03](ITEM-f2-p03.md) | L007–L009 / f2-inst-p2 | **READY as a draft after F1/F2 repair; NOT READY to issue:** the same hand-read, committed queue-b/hash, staging and dev-04 gate prerequisites as p02. p02's clean close is checked at arm; no advance item skips it. Fill its own Wednesday issue/watcher stamps. |
| [ITEM-f2-p04](ITEM-f2-p04.md) | L010–L012 / f2-inst-p3 | **READY as a draft after F1/F2 repair; NOT READY to issue:** the same piece-1 hand-read, committed queue-b/hash and staging prerequisites; no unresolved earlier class A/L002/L005 gate may be crossed when issuing. p03's clean close is checked at arm. Fill Friday's issue/watcher stamps. |

Every arm also needs fresh operational evidence: no READY v4 session, no counted span armable inside the protected horizon, hp-01/P unavailable, lawful F0 ineligibility, all stops cleared, host-event disposition/readback, latest-close restore/process-group absence, the exact campaign span's copy/offload marker or the exact non-campaign Check/copy proof, and off-host key, line 2, campaign line-9 debt, and the complete native checklist (including disk, meter and veto). These are re-read in Start and check and Run. Tests use synthetic observations; none is a live MBP receipt. A one-time yes in a draft is never an observation.

## Re-dated windows (RL-174 B)

The Monday slot is withdrawn. F2 may run on any t0-date, including qualification dates; it remains outside every campaign count. The current ladder is READY v4, counted development/qualification, F0, F2 (`inst-01`, `-02`, `-03`), `hp-02`, DESIGN_QUEUE_LOW. Every item rechecks the READY records and earliest armable counted work at Start and Run; these examples reserve no hour and move no higher rung. Historical hp-01/P must be closed or unavailable as well.

| Piece | Item's t0-date window (PST) | Illustrative t0 | Expected close | Work worst close | Protected next-arm time | Work protected |
|---|---|---|---|---|---|---|
| p01 | 2026-11-17 00:00:00–23:59:59 | Tue 17 16:45:12 | Tue 17 18:49:14 | Tue 17 19:52:42 | Tue 17 20:22:02 | dev-04 and its hand gate first; dev-05 Wed00 protected |
| p02 | 2026-11-18 00:00:00–23:59:59 | Wed 18 16:45:12 | Wed 18 18:49:14 | Wed 18 19:52:42 | Wed 18 20:22:02 | dev-05 first; pending READY qualification/v4 cedes |
| p03 | 2026-11-18 00:00:00–23:59:59 | Wed 18 19:09:14 | Wed 18 21:13:16 | Wed 18 22:16:44 | Wed 18 22:46:04 | piece2 clean close +1200; any READY counted/v4 cedes |
| p04 | 2026-11-20 00:00:00–23:59:59 | Fri 20 17:19:32 | Fri 20 19:23:34 | Fri 20 20:27:02 | Fri 20 20:56:22 | qualification qual-02 first; qual-03 Sat00 protected |

The first three examples retain the original counted/F0 chain but move p01 to Tuesday and p02/p03 to Wednesday. Friday p04 is explicitly on a qualification date: if qual-02-s02 closes at the qualification forecast Fri06:54:32, the campaign interval admits F0 at 06:59:32, 10:59:32 and 14:59:32. Using a rounded two-hour expected F0 duration, the third closes 16:59:32 and F2 may follow at 17:19:32 after 1,200 s. This is a synthetic illustration, not live eligibility or a reservation. A later qualification/F0 close, an open hand gate, or a READY v4/counted item changes the answer; the gates wait or cede. Nothing blocks F2 solely because the date is a qualification date. Missed windows need newly dated lead items, in piece order.

Protection is 11,250 s work worst case +560 s runner/launcher reserve +1,200 s interval =13,010 s after t0, beyond the pin's 12,710 s fence. Expected p03 follows p02's expected close +1,200 s. Each piece adds 7,442 s expected instrument time, 29,768 s over four pieces (8 h 16 min 8 s). Each item expires 24 h after its own issue and at kit expiry; issue p04 on its own fresh stamp, never on a Tuesday/Wednesday stamp. The pinned launch bands are unchanged; new-date CLI proofs are in `evidence/fix-2026-11-16/verify-f2-pNN.txt`.

## F1/F2 disposition

F1 (HIGH): every census now reads only `runner_receipt.json` and selects the greatest valid recorded `ended.epoch_s`. Identity is selected before rounding up; tied latest epochs, missing/invalid/unreadable stamps, missing roots and empty census stop. The selected receipt path supplies the campaign marker id. Restoring an old receipt with unchanged bytes and a newer mtime cannot substitute its marker. Explicit OTHER_CLOSE_EPOCH still covers a session outside the roots.

F2 (MED): campaign closes require their exact `.ok`/`.air.ok` marker. For F0/F2/Part C/session/W1, the issued non-campaign Check route applies. The lead supplies `NONCAMPAIGN_COPY_OK=yes`, `NONCAMPAIGN_COPY_CLOSE_EPOCH=EFF_EPOCH`, `NONCAMPAIGN_COPY_RECEIPT=EFF_PATH` (literal `OTHER` for an outside-root close), and `NONCAMPAIGN_COPY_RECORD` pointing to that Check's verified copy. Missing, stale, wrong-path or placeholder proof holds the arm. No dummy F0 marker or producer is added. Actual restore/group/fence and 1,200 s remain mandatory.

## Source and admission evidence

- Research authority: [RL-169, RL-169a, RL-171, RL-172, RL-173 and RL-174 B/C](../../../RESEARCH-LEAD-DECISIONS.md). The live forms inspected read-only were origin/main RUN_STATE items 346, 354 and 355. No superseded 01:30/02:40 night quiet or 22:13:10 limit is imposed.
- Corrected kit and queue a: `origin/align/2026-11-14-f2-inst`, commit `1f683fc634ed6b8722a3976af400920ee1f7dd7d`, following original kit commit `e6a9cdb9`. Kit path `docs/process/cadence/kits/f2-inst-01.v1.1.json`, SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`. Queue a path `docs/process/cadence/queues/f2-inst-01.v1.1.queue-a.json`, SHA-256 `ca61c3bc09d8a594a60ec058b86d378012a165b44334f4309b4cd7546e842892`.
- Selected measurement pin: `2d347f721552fe03bdd19f113e7bad7a7c24908e`. The kit copy here is byte-identical to the committed corrected kit. Its frozen block is unchanged. Its old clock text is superseded by RL-171/RL-172 in the item, without modifying the kit or re-pinning.
- Independent executing re-check by this item builder (not the original kit builder): [new kit-recheck.json](evidence/fix-2026-11-16/bash/kit-recheck.json), including real `validate-kit` with frozen-path verification under both arguments, exact `gen-legs` equality, layout test, committed queue-a validation, temporary queue-b validation, eight pinned mock spans and the q600 synthetic leg runtime. The pinned `plan` at 22:13:10 and both new band boundaries is in every per-item verification file. No kit diff finding remains from these checks; the lead still owns admission and live gates. The original cold-seat findings are disposed by RL-169a; their full pre-fix seat reports and an earlier final re-check were not found in the inspected Git evidence. They are not represented as newly obtained passes.
- Warm-up observation required by RL-169a §1: 256 nominal tokens / 526 prompt characters; one warm-up; completion log timestamp `303.712000`; stage completion and sampling start `308.712` after a 5 s settling delay; G0 release `320000000000` ns; quiet span 600 s; decode 512. **All values are synthetic.** The stage-completed event includes settling. The completion log and stage event are recorded separately for the manifest's cold pass; this builder does not choose the analyst's recovery origin.
- Queue b is intentionally **not committed here**. Only a disposable synthetic queue b is validated. The stager refuses p2–p4 without a PASS hand-read observation and a lead-supplied committed queue source/hash. It stages only the v1.1 variant. F2 is never inserted into BLOCK-QUEUE's `blocks[]`.

## Verification and reproduction

From any clean local clone containing the source commits and a detached worktree at the measurement pin:

```sh
python3 -B build_items.py /path/to/pin-worktree
bash tests/run_all_gates.sh /path/to/pin-worktree /path/to/local-clone
zsh tests/run_all_gates.sh /path/to/pin-worktree /path/to/local-clone
```

The runner is portable: no hard-coded scratch directory, Python minor version, pre-existing mock output or MBP connection. Both bash and zsh are required. Staging uses a disposable local clone and env overrides only, without network; its queue-b commit is synthetic and never published. The gate runner extracts the functions from each item, checks the complete shell blocks' syntax after filling the two placeholders, and exercises the actual functions with a fixed clock. The pinned runner and all measurement paths remain unchanged, so this docs/tooling-only change uses targeted checks instead of the canonical multi-hour full suite.

## Open questions and next exact step

**One question to carry to the research lead at the existing `lm-inst-01` cold pass:** which persisted warm-up stamp defines the recovery origin? Options: the runtime completion-log timestamp, or a stage boundary with the 5 s settling gap explicitly accounted for. Recommendation: name the completion log and print the gap; the research lead decides. Blocked work: choosing that analyst rule, which is outside this drafting task. The event alone is not silently treated as native inference completion. RL-169a §1 requires this observation to be reported; no new measurement, re-pin or early energy read is proposed.

No other new ruling is identified. Existing reservations remain: a second F2 stop, a required kit-field change, or the later manifest/output goes to the research lead under RL-169a.

The lead first records dev-03's clean same-pin smoke and L002/class A release, adopts the re-check, and stages p01 in a clean close interval. Issue p01 only with fresh issue/watcher stamps and the live arm-record evidence. After piece 1's live hand-read PASS, the lead commits queue b and stages/issues the later dated items without crossing an outstanding hand gate. READY v4 or counted work always takes precedence.

Workspace for this repair: `/Volumes/JW-EXT/jw-wt/sol-f2-fix`, detached on `origin/audit/2026-11-10-fable`, successfully pulled/rebased before edits. No MBP contact, main/RUN_STATE edit, external message, real measurement/custody read or integration installation occurred. Earlier build evidence is retained unchanged.
