# Revision 6 block 1: `prepare-candidate` invocation record (2026-10-02)

Operator: Claude Opus 5.5 subagent, dispatched by the interactive orchestrator. Worktree
`/Users/edr/code/JouleWise-derive-rev6b1`, branch `derive/2026-10-02-rev6-block1`, cut from
`origin/main` `420e1f07`. Interpreter: the C2 measurement clone's `.venv/bin/python` (3.13.1).
The issuer run is the worktree's `scripts/issue_calibration_acceptance_generation.py` (main,
which contains the #454 prior-record fix; the C2 measurement clone at `47e16dcc` does not).

## Arguments and where each came from

- `--preregistration-sha256 d0034003…7b78`: sha256 of the registration file at main, equal to
  `preregistration_sha256` in both harvest records.
- `--ledger`: the C2 measurement clone's ledger (376 rows); head pin is the default
  `configs/calibration/calibration_ledger_head.json` at main (sequence 376, `a5b825b7…7014`).
- `--harvest-record`: the two archived harvest records, byte-identical to the landed copies under
  `docs/process_traces/rev6-windows/<session>/harvest.json` (c1 `b4c49a56…d548`, c2 `820a97f6…fbdc`).
- `--cap-rule-text`, `--roster`: the tracked files whose sha256 equal the sealed
  `pins.cap_rule_text_sha256` (`6b4bcaea…a4bf`) and `pins.roster_sha256` (`d8fbb403…75e7`).
- `--corpus-root /Users/edr/night-custody`: the custody parent of the members' ledger
  `custody_locator` paths (the Revision 5 practice).
- `--d125-ruling`: the 2026-09-25 D-125 addendum string fixed for Revision 5, with a pointer to
  Revision 6 §8-§9, which carry that envelope plus the window-blocked Q99.
- No `--battery-confounded-session-id` (both battery verdicts pass); predecessor left at its
  default (P8, `calibration_acceptance_d079_v2_n17_r8.json`, sha256 `52e3d18a…a13`).

## Exact argv (identical for both runs)

```
cwd: /Users/edr/code/JouleWise-derive-rev6b1
/Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/.venv/bin/python scripts/issue_calibration_acceptance_generation.py prepare-candidate --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md --preregistration-sha256 d0034003a7e61683696b88662825d909dc4bb8ad23678edad6bbc8dfd4877b78 --ledger /Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/runs/calibration_observation_ledger.jsonl --corpus-root /Users/edr/night-custody --registration-session-id d079-epoch-25g83-r6-20261001T0617Z --registration-session-id d079-epoch-25g83-r6-20261001T2252Z --harvest-record /Users/edr/night-archive/harvest-d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/harvest.json --harvest-record /Users/edr/night-archive/harvest-d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/harvest.json --cap-rule-text docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/31-addendum-ruling.md --roster docs/process_traces/2026-09-29-interactive-ff50b201/130-cap-roster.md --r9-record docs/process_traces/rev6-derivation-block1/r9_campaign.json --d125-ruling 'docs/decision_log.md, D-125 addendum (2026-09-25): Revision 5 screen and ceiling for epoch 25G83/v3 (ACCEPTANCE-25G83-02 §5 R5(i), R9), as carried by Revision 6 §8-§9 of configs/calibration/preregistration_d079_epoch_25g83_rev1.md' --out docs/process_traces/rev6-derivation-block1/candidate_acceptance_25g83_rev6.json
```

## Run 1 (before the R9 commit)

- exit code: 3
- stdout: `REFUSED: Revision 6 campaign R9 bytes are not committed at HEAD`
- stderr: (empty)
- wrote: `docs/process_traces/rev6-derivation-block1/r9_campaign.json`, sha256 `8be16a2038ec60ef525766f2914d50c00002a9fa279323d06b3d7c98690318a2`
  (top level: counted 24, valid 24, members 24; all five R9 clauses true; no clock-movement or
  empty-fit refusals). Committed alone as `344e63fc6f9a541fab2e4574ea0e634ebd1c77a4` ("Rev6 block 1: blind campaign R9 record").

## Run 2 (same argv, after the R9 commit)

- exit code: 3
- stdout: `REFUSED: member d079-epoch-25g83-r6-20261001T0617Z-d01: custody /Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d01: first path part does not equal the session id`
- stderr: (empty)
- wrote: nothing. No candidate exists.

## Diagnosis of run 2 (report only; no code changed)

Raised by `_corpus_relative_custody` (`scripts/issue_calibration_acceptance_generation.py`, the
`parts[0] != session_id` check), called from `_select_members` before any member evidence is
opened. The rule (added in `cc8346c2`, ISSUANCE-CUSTODY-OUTSIDE-REPO-01, for Revision 5) requires
each member's custody path to be `<corpus_root>/<session_id>/runs/instrument_validation/<attempt_id>`.
Revision 5 custody directories were named by session id. Revision 6 custody directories are named
by the night plan id (`d079-epoch-25g83-r6-derivation-c1-20261001T0617Z`), while the session id is
`d079-epoch-25g83-r6-20261001T0617Z`. The ledger's absolute `custody_locator` fixes the path, so no
`--corpus-root` satisfies the check, and omitting `--corpus-root` fails the repo-relative route
(`_repo_relative_custody`: custody lies outside the repository). `verify-members` applies the same
session-id rule. This is a code defect in the issuer's Revision 6 member-path handling (the same
plan-id versus session-id class as #454), not an argument error. The refusal came before any
member value was read or printed.
