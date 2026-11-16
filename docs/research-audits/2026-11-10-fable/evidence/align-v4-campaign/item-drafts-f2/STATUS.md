# F2 item drafts, 2026-11-15 PST

Four complete, synthetically tested drafts cover all twelve legs of the admitted four-piece layout. **Nothing is issued. No item is marked READY to issue before its live prerequisites are recorded.** The timestamp and final test totals are in [evidence/verification.txt](evidence/verification.txt). The lead inserts issued items into RUN_STATE on main; this builder never edits that file or main.

| Item | Roster / predecessor | Status: exactly what is missing before issue |
|---|---|---|
| [ITEM-f2-p01](ITEM-f2-p01.md) | L001–L003 / dev-03-s02 (L004–L012) | NOT READY: dev-03's same-pin first-span clean restore and class A/L002 hand-gate release; lead's adoption of the recorded F2 re-check; MBP staging of the v1.1 kit, committed queue a and worktree. Fill issue time and watcher observation when issuing. The predecessor may still be pending at issue under RL-173 D; its clean close is mandatory at arm. |
| [ITEM-f2-p02](ITEM-f2-p02.md) | L004–L006 / f2-inst-p1 | NOT READY: p01 prerequisites plus piece 1's live PASS hand-read, lead-committed queue b, its exact path/hash, and staging. Do not issue across dev-04's L005 gate; its release or the lead's applicable contingency must already be recorded. Fill the Tuesday issue/watcher stamps. |
| [ITEM-f2-p03](ITEM-f2-p03.md) | L007–L009 / f2-inst-p2 | NOT READY: the same hand-read, committed queue-b/hash, staging and dev-04 gate prerequisites as p02. p02's clean close is checked at arm; no advance item skips it. Fill its own Tuesday issue/watcher stamps. |
| [ITEM-f2-p04](ITEM-f2-p04.md) | L010–L012 / f2-inst-p3 | NOT READY: the same piece-1 hand-read, committed queue-b/hash and staging prerequisites; no unresolved earlier class A/L002/L005 gate may be crossed when issuing. p03's clean close is checked at arm. Fill Wednesday's issue/watcher stamps. |

Every arm also needs fresh operational evidence: no READY v4 session, no counted span armable inside the protected horizon, hp-01/P unavailable, lawful F0 ineligibility, all stops cleared, host-event disposition/readback, latest-close restore/process-group absence, copy/offload marker and off-host key, line 2, campaign line-9 debt, and the complete native checklist (including disk, meter and veto). These are re-read in Start and check and Run. Tests use synthetic observations; none is a live MBP receipt. A one-time yes in a draft is never an observation.

## Windows filled

Forecasts retain [the RL-172 chain](../item-drafts-rl172/PLAN.md)'s counted spans and higher-priority F0 starts. F2 follows each day's third F0, after its close plus 1,200 s, when F0's daily cap refuses another. No four-hour F0 spacing slot is shortened to make F2 fit. The admitted three-leg pieces fit without a re-cut.

| Piece | Item's t0-date window (PST) | Forecast t0 | Expected close | Work worst-case close | Protected next-arm time* | Higher-priority work protected |
|---|---|---|---|---|---|---|
| p01 | Mon 16, 00:00:00–23:59:59 | Mon 19:56:17 | Mon 22:00:19 | Mon 23:03:47 | Mon 23:33:07 | dev-03 has closed; dev-04 Tue 00:00 |
| p02 | Tue 17, 00:00:00–23:59:59 | Tue 16:45:12 | Tue 18:49:14 | Tue 19:52:42 | Tue 20:22:02 | dev-04 has closed; dev-05 Wed 00:00 |
| p03 | Tue 17, 00:00:00–23:59:59 | Tue 19:09:14 | Tue 21:13:16 | Tue 22:16:44 | Tue 22:46:04 | dev-05 Wed 00:00 |
| p04 | Wed 18, 00:00:00–23:59:59 | Wed 16:45:12 | Wed 18:49:14 | Wed 19:52:42 | Wed 20:22:02 | any newly READY counted/qualification work or v4 session cedes the slot |

\* 11,250 s work worst case + 560 s runner/launcher reserve + 1,200 s close interval = 13,010 s after t0. This exceeds the pin's 12,710 s fence span. It is a conservative scheduling protection, not a new physics wait. Expected p03 starts after p02's expected close plus 1,200 s. Actual close, fence disappearance, copy and higher-rung eligibility always govern. If p02 slips, p03 must still fit before dev-05's earliest arm; it cannot consume Wednesday's counted start.

Each piece adds 7,442 s expected instrument time; all four add 29,768 s (8 h 16 min 8 s). These are planner predictions, not hardware measurements. Each item expires 24 h after its own issue; neither a Mon issue for Wednesday nor a stale Tuesday item is usable. A missed window needs a newly dated lead item, in kit order. The per-pin midday refusal remains; all four forecasts use `02:00-02:35`. Their full band ends and one-second neighbors are checked in `evidence/verify-f2-pNN.txt`.

## Source and admission evidence

- Research authority: [RL-169, RL-169a, RL-171, RL-172 and RL-173](../../../RESEARCH-LEAD-DECISIONS.md). The live forms inspected read-only were origin/main RUN_STATE items 346, 354 and 355. No superseded 01:30/02:40 night quiet or 22:13:10 limit is imposed.
- Corrected kit and queue a: `origin/align/2026-11-14-f2-inst`, commit `1f683fc634ed6b8722a3976af400920ee1f7dd7d`, following original kit commit `e6a9cdb9`. Kit path `docs/process/cadence/kits/f2-inst-01.v1.1.json`, SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`. Queue a path `docs/process/cadence/queues/f2-inst-01.v1.1.queue-a.json`, SHA-256 `ca61c3bc09d8a594a60ec058b86d378012a165b44334f4309b4cd7546e842892`.
- Selected measurement pin: `2d347f721552fe03bdd19f113e7bad7a7c24908e`. The kit copy here is byte-identical to the committed corrected kit. Its frozen block is unchanged. Its old clock text is superseded by RL-171/RL-172 in the item, without modifying the kit or re-pinning.
- Independent executing re-check by this item builder (not the original kit builder): [kit-recheck.json](evidence/kit-recheck.json), including real `validate-kit` with frozen-path verification under both arguments, exact `gen-legs` equality, layout test, committed queue-a validation, temporary queue-b validation, eight pinned mock spans and the q600 synthetic leg runtime. The pinned `plan` at 22:13:10 and both new band boundaries is in every per-item verification file. No kit diff finding remains from these checks; the lead still owns admission and live gates. The original cold-seat findings are disposed by RL-169a; their full pre-fix seat reports and an earlier final re-check were not found in the inspected Git evidence. They are not represented as newly obtained passes.
- Warm-up observation required by RL-169a §1: 256 nominal tokens / 526 prompt characters; one warm-up; completion log timestamp `303.712000`; stage completion and sampling start `308.712` after a 5 s settling delay; G0 release `320000000000` ns; quiet span 600 s; decode 512. **All values are synthetic.** The stage-completed event includes settling. The completion log and stage event are recorded separately for the manifest's cold pass; this builder does not choose the analyst's recovery origin.
- Queue b is intentionally **not committed here**. Only a disposable synthetic queue b is validated. The stager refuses p2–p4 without a PASS hand-read observation and a lead-supplied committed queue source/hash. It stages only the v1.1 variant. F2 is never inserted into BLOCK-QUEUE's `blocks[]`.

## Verification and reproduction

From any clean local clone containing the source commits and a detached worktree at the measurement pin:

```sh
python3 -B build_items.py /path/to/pin-worktree
bash tests/run_all_gates.sh /path/to/pin-worktree /path/to/local-clone
```

The runner is portable: no hard-coded scratch directory, Python minor version, pre-existing mock output or MBP connection. Both bash and zsh are required. Staging uses a disposable local clone and env overrides only, without network; its queue-b commit is synthetic and never published. The gate runner extracts the functions from each item, checks the complete shell blocks' syntax after filling the two placeholders, and exercises the actual functions with a fixed clock. The pinned runner and all measurement paths remain unchanged, so this docs/tooling-only change uses targeted checks instead of the canonical multi-hour full suite.

## Open questions and next exact step

**One question to carry to the research lead at the existing `lm-inst-01` cold pass:** which persisted warm-up stamp defines the recovery origin? Options: the runtime completion-log timestamp, or a stage boundary with the 5 s settling gap explicitly accounted for. Recommendation: name the completion log and print the gap; the research lead decides. Blocked work: choosing that analyst rule, which is outside this drafting task. The event alone is not silently treated as native inference completion. RL-169a §1 requires this observation to be reported; no new measurement, re-pin or early energy read is proposed.

No other new ruling is identified. Existing reservations remain: a second F2 stop, a required kit-field change, or the later manifest/output goes to the research lead under RL-169a.

The lead first records dev-03's clean same-pin smoke and L002/class A release, adopts the re-check, and stages p01 in a clean close interval. Issue p01 only with fresh issue/watcher stamps and the live arm-record evidence. After piece 1's live hand-read PASS, the lead commits queue b and stages/issues the later dated items without crossing an outstanding hand gate. READY v4 or counted work always takes precedence.

Workspace note: the supplied worktree's `.git` points to an inaccessible old-volume path. Work was prepared and verified in a separate local clone; Git metadata at that denied path was neither repaired nor bypassed. The delivered draft folder is also copied back to the requested workspace. No MBP contact, main/RUN_STATE edit, external message, real measurement/custody read, or integration installation occurred.
