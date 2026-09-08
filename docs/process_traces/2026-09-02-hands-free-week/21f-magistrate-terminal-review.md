# 21f — Magistrate terminal review of PR #295 (headless activation 784a764e)

Written 1788861553 2026-09-08 02:59:13 PDT; merge candidate reviewed: `083ce8ae` (this file is committed on top of it as the final head; rows 11/12 of
the ledger name that final sha). Docs-only PR; GitHub reports mergeable/state `MERGEABLE/UNSTABLE` against main (main moved to a969e526 with PR #296
while this PR was in review; no overlapping paths).

## What I read myself (rule 1: final verification is not delegated)
- The three zsh blocks of the amended arm-time sequence in 21b in full, after every round (A: steps 0–3; manual 3b/5; B: steps 4–7), and
  ran `zsh -n` on each and `compile()` on the four PY heredocs at the final head (all pass; the same checks are in 21e3/21e4).
- The NIGHT_HANDBACK.md diff main..head: the three per-night sections rewritten at H=ae8f074f (unchanged since), the four standing
  sentences restored verbatim (21e N6 → 21e2/21e3 confirm 1/1/1 counts), one whitespace refill.
- Trace 21 diff and the copied artifacts for both activations (`21-activation-1ef89702/`, `21-activation-784a764e/`).
- Every review round: 21c (Opus, F1–F15), 21d (astra fix round 1), 21e (Opus delta 1, N1–N11), 21e2 (Opus delta 2, D1–D6), 21e3 (astra
  delta 3, E1), 21e4 (Opus delta 4, LANDABLE).

## Design-level questions and answers
1. Is the twin validation sound? Yes. The twin is `dataclasses.replace` of the real plan on exactly the three custody-derived fields;
   `--render-only` validates pins/schema/hour/courier binary against the twin from the H checkout; the json diff aborts on any other
   difference. Executed by me twice (21b §Bench pass 2 with `pass2-*` artifacts) and reproduced by 21e (Opus) and 21e3/21e4.
2. Is authority intact? No process rule, decision-log entry or skill doctrine is amended by this PR. H is untouched. Condition 1 of D-175 is
   judged on the consolidated notice per ruling B (21c §Ruling of record), issued by the D-175 synthesis author; D-175 itself is now on
   main (a969e526). The un-publish clause acts only on the plan this session authored (D-175 line 19 (a) / cond. 8).
3. Are the failure modes closed? Abort cleanup covers checkout, staging and scratch; install failure after the move un-publishes the plan
   (uninstall before rm, because the installer rejects `--uninstall` without the plan file: `pass3-lead-benches.txt` bench 2); the arm
   window is enforced in both blocks (`pass3-lead-benches.txt` bench 1); block B re-checks standdown.request and the plan glob.
4. Is the arm reachable by the arming session? Yes: the keepalive Monitor is a direct child of the session pid
   (`pass3-process-tree-keepalive.txt`), step 3b stops it and every Codex child before the census, and the census bench shows own-tree →
   exit 0, reparented foreign → exit 1 (`pass3-lead-benches.txt` bench 3).
5. Same-signature across the gauntlet: the hand-typed-time class survived two consecutive rounds in text the magistrate itself wrote
   (21e N1/N2, 21e2 D3). Under rule 11's standing trigger the next spend was a consult, not round three
   (`/private/tmp/mag784/consult-295-time-signature.md`, copied below as 21f-consult); its mechanical rule (R1–R4) governed rounds 3–4, and
   21e3/21e4 report no category-(iv) time and no new defect. Remaining untokened HH:MM strings are verbatim quotes (headings, email
   subjects), artifact-naming lines, or window constants derived on the same page (21e4 task 2). The hard-coded pid 48645 check is a
   deliberate fail-closed guard against a named leaked process, not an operative identity.

## Overbuild / merge-ability prune
Nothing pruned: the superseded original sequence is retained for the record behind an `exit 1` first line; the historical bench pass 1
artifacts stay beside pass 2/3. Docs only; no code, no tests, no CI change.

## What this PR does NOT do
It arms nothing. The consolidated arm notice (ruling B) is sent only after this PR's ledger is green; the arm itself needs
joulewise-53's stand-down message, an empty foreign census, no NO on thread 1a0800cdb282c3f1, and the enforced window.
