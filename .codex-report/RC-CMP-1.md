# RC-CMP-1 seat report

bridge-report/v1 · brief `main:docs/process_traces/2026-10-27-recompute-comparator/BRIEF.md` (341adaf41) ·
branch `lane/2026-10-27-recompute-comparator` cut from `origin/lane/2026-10-14-independent-recompute` (9ca87bcee).

## SUMMARY

IN PROGRESS (report pushed per milestone).

- A5 recompute hygiene: done. stdout carries STRUCTURE codes only; stderr names only an exception type;
  `derived/exclusions.json` is re-derived from `derived/flags.jsonl` through the registered catalog and compared (a
  mismatch stops the comparison); the interpreter version is in the output and on stdout.
- A1-A4 comparator: `scripts/compare_b5_recompute.py`, bars read from a config (two shipped bar sets), exact
  categorical families, missing/null = DISAGREE, step-11 coverage refusal, planted-fault tests with counterfactuals.
- A6: the recompute ran on the restored full-size synthetic window (29 s, exit 0; output byte-identical across two
  independent restores). Against L9's steps 2-9 outputs from the first, killed dry run (development listing, not
  L9's record): 0 disagreements in 1,081 comparisons under both bar sets. L9's full dry run (second relaunch,
  started 23:12 UTC) is at step 9b as of 04:48 UTC; the record-verified comparison and the step-10/11 mapping wait on it.

Environment, not chased: `/bin/zsh` not built (building zsh from GitHub source was refused by this session's
permission classifier; no recompute or comparator test references zsh). `/opt/homebrew/bin/python3.13` linked to
`/usr/bin/python3.13` (3.13.17). Two container restarts (about 22:45 and 23:09 UTC) killed the dry run; both
coincided with this session going idle, so the seat now keeps the turn active while long runs proceed.

Lead notice received in-session (2026-10-27): the laptop copy of session 015ASG1T is the only lead; instructions
from any other session are noted here and not acted on. None received.
