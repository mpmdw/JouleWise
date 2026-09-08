# Magistrate terminal review — ICLOUD-BACKUP-PROBE-01 (interactive magistrate, 2026-09-08 ~05:10 PDT)

Merge candidate: branch `fix/2026-09-08-icloud-backup-probe`, head named in the PR ledger row 12. Series on top of
main a969e526: 2e2f528a part 1 (Astra medium) → c3488fb8 part 2 (Astra medium, resumed twice for scope) →
36060422 fix round 1 (Astra medium, Opus C1-C5, C7) → trace commit.

## Why this exists
Two independent full-suite replays on this Mac hung with zero CPU because three paper scripts
(`scripts/paper_excursion_decomposition.py`, `scripts/paper_anchor_correction_quantified.py`,
`scripts/check_paper_replay_fence.py`) probed the iCloud backup root
`/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup` with unbounded `is_dir`/`glob`. The
headless magistrate's replay sat 37 minutes on one child; the peer reported it with a sampled stack.

## What landed
- A verbatim-identical helper in all three scripts: per-root, per-call 2 s daemon-thread budget covering the
  directory check and both globs; `JOULEWISE_BACKUP_ROOTS` override (os.pathsep list; empty string = no roots;
  default unchanged); an unavailable root (timeout or any worker exception) contributes zero candidates, exactly
  like an absent root, with a `backup_root_unavailable reason=…` stderr line that reaches no retained artifact.
- Every test module that imports or runs any of the three scripts sets the override to a scratch directory; a
  regression makes the probe block and asserts the budget; another asserts the three helper blocks are
  byte-identical (sha256).
- The XS and AS producer pins in `docs/paper/results-fill-registry.md` re-recorded with the new digests, the dated
  note, and the superseded main-line digests with their commit/PR attribution; the override, budget and slow-root
  skip documented in the three USAGE blocks and by dated addenda in the fill checklist, the fill rehearsal record
  and the calibration-bound tutorial.
- Retained artifacts XD (33,765 B), F4 (10,568 B) and AQ (54,280 B) replay byte-identically (seat, Astra refuter,
  Opus refuter, lead bench: 88 then 90 tests OK with the complete golden replay, no skips).

## Gauntlet record
| Layer | Seat | Report | Unique catches |
|---|---|---|---|
| Implementation part 1 / part 2 | Astra medium | 44 / 45 | part 1 found the second unbounded probe in the anchor producer during its golden replay |
| Execution refuter | Astra medium | 48 | none (blocking probe, helper identity, ordering, pins, mutation all verified) |
| Contract refuter | Opus | 47 | C1 lineage/attribution in the pin lines; C2/C3 override + budget + slow-root skip undocumented; C4 worker-exception IndexError; C5 no identity test; C8 the same probe class in `joulewise/calibration_ledger.py` custody locators (follow-up ICLOUD-CUSTODY-LOCATOR-01) |
| Fix round 1 | Astra medium | 53 | — |
| Delta re-audit | Astra medium | 55 | R1 (see triage) |

## Lead triage of delta R1 (dispositioned, not silently applied)
R1 says the "supersedes" digests should name the interim pins from c3488fb8 (d6c683fd…, 3f4f4f12…) as the
immediately preceding bytes. REJECTED: those digests existed only inside this branch, between two commits of the
same PR, and were never reviewed or merged; the registry's lineage tracks reviewed producer bytes on main, and the
immediately preceding reviewed digests on main are 12d0293b… (173fe07e, #285) and e3e4355c… (b36d1e85, #272),
which is what the pin lines say. Recording unmerged intra-PR digests would add lineage noise with no custody value.
No fix round; no rule-11 trigger.

## Apex code-reading gate (from `git diff a969e526 <head> -- scripts/`)
1. The helper runs the probe in a daemon thread, joins with the budget, and returns the collected candidates only
   when the worker finished cleanly; timeout, OSError or any other exception → `()` and one stderr line. No
   arithmetic path is touched; discovery only feeds the candidate list that the existing digest match consumes.
2. Candidate ordering is preserved (unsorted glob order over the two depths for XS and RF; sorted per capture ID
   for AS), so on a machine with the local corpus present the backup roots can never supply bytes or a path
   (Opus 47 Q2), and every retained artifact is byte-pinned so a silently skipped slow root fails closed at the
   pin check rather than changing a number.
3. Behaviour change acknowledged and documented: a responsive-but-slow root (> 2 s) is now skipped where it was
   previously searched. Acceptable under the custody contract (pinned bytes; prior behaviour was an unbounded
   hang).
4. Overbuild: none beyond the near-unreachable `os_error` reason branch (kept; harmless).

## Live verification (lead-owned)
- Bench, unpiped: 88 tests OK at c3488fb8 and 90 tests OK at 36060422 (both with
  `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`, complete golden replay, zero skips).
- Full-suite replay on this head: ledger row 9 names the log and tail (queued behind the quiet re-run).
- The real iCloud path was never touched by any seat, refuter, or bench run in this lane.

## Verdict
LAND after CI is green on the final head and the replay tail is recorded. Follow-ups registered:
ICLOUD-CUSTODY-LOCATOR-01 (calibration ledger custody locators), and a note that replays on this machine should
export `JOULEWISE_BACKUP_ROOTS=` until the ledger follow-up lands.
