# Charge: cold gate HARVEST-VERDICT-FINAL-01. Close the route by which a clean window could be dropped after B is seen (A-R5b / BFG-D).

Assembled on 2026-09-25 at about 17:40 PDT by the resident magistrate (Opus 5.5, activation ed17a643). Nothing is armed.

## Background

Registration amendment A-R5b v1.1 is in PR #423 (`ad7565a7`); its text is at `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, the last section, in that commit. It says every window gets a battery verdict computed from raw bytes before any B value is read. A window whose verdict is `battery_float_confounded` or `battery_float_evidence_missing` is excluded and replaced at most once per epoch.

The BFG-D implementation is on branch `origin/feat/2026-09-25-bfg-d` at `06671b69`. Its issuer recomputes that verdict at issuance time, from raw bytes.

The Opus contract lens on #423 (ex-01, finding M1) found a route. W1 and W2 both pass at harvest. The caller then prepares a candidate and sees every B. If the caller dislikes the result, they delete or alter one raw battery file in a W2 slot; honest custody loss has the same effect. The issuer then recomputes W2 as `evidence_missing`, requires W2 to be declared excluded, and accepts a replacement W2′. That is an exclusion driven by B plus a top-up driven by outcome, which Revision 5 forbids. At `main` today, the same custody loss on a member REFUSES issuance, so the asymmetry is new. The lens proposed cures (a), (b) and (c). Cure (a) is a binding reading recorded in the decision log. Cure (b) makes BFG-D commit each session's harvest verdict durably before the count-only dry run and has the issuer refuse on disagreement. Cure (c) is a test.

The lens and the seat report (ex-02) are arguments, not authorities. The magistrate may not author decision-log rules alone (rule 11), which is why this question comes to you.

## Questions

- **H1.** Verify M1 yourself at `06671b69`: read the issuer's battery contract, and check whether and where a harvest verdict is recorded durably today. Is the route real?
- **H2.** Rule the cure. Say exactly where a harvest verdict is recorded durably and by which code: the ledger, the pin commit, a harvest record file, or the cadence report output. Say how it is authenticated, when it is written relative to the cadence report and the count-only dry run, and what the issuer does when its recomputation disagrees with that record. Issue exact text for any decision-log record, and state whether the A-R5b registration text needs any change. It should not, unless you find it must; say which.
- **H3.** The seat's F-1: a slot whose writer died before the post-observation has no finalized row, so it carries no battery obligation. The seat's F-2: an `UpdateTime` in the future passes. Its F-6: the issuer enforces the one-replacement bound. The lens's N1: the one-replacement stop is not enforced for a failing window with zero valid rows. For each, AFFIRM the current behaviour or rule a change, and say whether any change must land before W1.
- **H4.** Give the implementation obligations for BFG-D as a numbered list: sites, names, tests (defect-shaped, at production call sites). Then give a plain summary for Ed of at most 5 lines.

## Constraints

- Work in one non-interactive foreground session. Start no background tasks, watchers or subagents. If the session ends before the ruling file exists, that is a protocol failure. Budget about 25 minutes.
- Stay read-only apart from the ruling file. Never run `sudo`, `launchctl`, `powermetrics`, the installer or model inference.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` or `~/Library/LaunchAgents`.
- You may run focused unit tests; do not run test discovery.
- Write only `20-coldgate-fable-harvest-final-ruling.md` in this packet directory.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory. Do not read `docs/process_traces` files outside this packet, except the BATTERY-FLOAT-01 packet `../10-coldgate-packet-bfg/` (its final texts are `30-addendum/21-…addendum-ruling.md` §5).
- Begin with a contamination disclosure.

Charter: `docs/process/coldgate_charter.md` sha256 `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.

## Exhibit manifest
```
10d34333bc7bbfa3a69d957e15eb2f2bee8f1e6b0ee2ba97470a440a32a72b78  ex-01-opus-lens-ar5b.md
3277bd1732787f7ef243bdabee66493b510185c8221e3d2d0185fc592668b186  ex-02-bfgd-seat-report-r3.md
```
