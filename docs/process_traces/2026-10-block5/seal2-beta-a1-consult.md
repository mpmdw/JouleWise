# Block 5, second seal, BETA attempt 1: consult, structural counts and decision

Magistrate activation cbe4230e (Opus 5.5, headless), 2026-10-10. Structure only. This record follows
`seal2-beta-a1-window.md`. The papers are in `seal2-beta-a1-consult/` beside this file (and in
`/Users/edr/night-archive/b5-consults/beta-a1/`): `BRIEF-body.md` (the brief both seats had),
`sol-consult.md`, `opus-consult.md`, and four count programs with their outputs.

## Why a consult

The harvest gave BETA attempt 1 one window reason, `neg8.screen_failed`, with the drift bound derived and
validated. Brief section 6 sends that code to two blind seats at once, on the first occurrence.

## The two seats (about 07:27 to 07:38 PDT)

- **Sol 6.1**, effort high, through `codex-run-v3`, empty write scope, working directory the harvest
  lane's worktree at `224a264c5`. Recommendation (a): arm BETA attempt 2 unchanged at the next permitted
  t0, provisionally, unless a structural count shows that the re-screen could not be evaluated; in that
  case diagnose that failure first. As on both earlier consults the launcher exited rc=65
  (`run_status=ACCEPTANCE_FAILED`: the report's JSON header did not pass its parse); the body is complete
  and was read as a consult answer.
- **Opus 5.5** agent, read-only. Recommendation (b): arm BETA attempt 2 unchanged today, with a rule that
  no later chain runs between 05:15 and 06:45 local; but first run one count program, and if it shows the
  re-screen was not evaluated, the answer becomes (d): fix the harvest, pin it, harvest attempt 1 again
  from the same bytes, and do not arm attempt 2 before that.

What both found. With a derived bound the harvest always re-runs the reference screen itself (the stored
verdict's screen never decides alone), so `neg8.screen_failed` means one of three things: too few
references survive at an endpoint (the screen needs 2 at the start and 2 at the end); the screen ran and
the reference workload's start-to-end change exceeded the bound; or the re-run could not be evaluated.
The permitted evidence cannot tell them apart; one count over `derived/neg8-screen.json` can. Both say:
no change to anything a window reads, no END STATE, and GAMMA may not be armed before BETA (the
registration fixes the order, section 7.2). Both read the scan job's launchd files: `XProtectRemediator`
is started by repeating system activities with minimum spacings of 6 hours, 1 day and 7 days and no fixed
clock time, so no t0 avoids it with certainty. The reference spare that ran after the end stage left no
bundle (the harvest's counts show no spare stage), so it added nothing to the end endpoint.

The seats agree on every point that decides the next step, so no cold judge was convened.

## The counts (run once each by the magistrate, outputs verbatim)

Each program prints fixed labels, words from closed lists in the code, and integers; none prints a
member's name or a measured value. Their SHA-256: `screen_branch_count.py` `8c618e47…4fc0` (the Opus
seat's program A, unchanged), `loss_position_count.py` `bdfbb648…2598`, `verdict_shape.py`
`582c2357…bb20`, `catalog_auth_count.py` `d37f2339…bf7a`.

`screen_branch_count.py` (reads `derived/neg8-screen.json`):

```
bound_used corpus_physics_clean
stored.decision failed
stored.other_conditions ['neg8_bracket_missing', 'neg8_bracket_reference_invalid']
rescreen.evaluated False
rescreen.decision null
rescreen.conditions []
rescreen.problems ['source_manifests_unrecorded']
freshness null 0
survivor_screen null
endpoint_protocol null
reference_counts {}
losses_by_position_reason []
harvest_losses_by_code [('contention.request_overlap', 1), ('member.admission_aborted', 1)]
```

`loss_position_count.py` (maps each of the two lost references to its endpoint through the plan-time
reference packs):

```
[(('end', 'member.admission_aborted'), 1), (('start', 'contention.request_overlap'), 1)]
```

`verdict_shape.py` (key names, types and list lengths of the stored whole-window verdict, for ALPHA
attempt 1 and this window): the two files have the same keys. In ALPHA's, `source_campaign_manifests` has
9 entries (top level and under `row_provenance`) and `neg8_bracket.claim_families` has 2. In BETA's, both
`source_campaign_manifests` lists are empty, `neg8_bracket.claim_families` is empty, and the bracket's
numeric fields are null.

`catalog_auth_count.py` (the desk root's own authentication functions over each claim runs root):

```
v5-b5-alpha-a1-20261009T2312Z manifest_files 9 pointwise_ok 9 pointwise_bad 0 bad_unreadable 0 bad_mentions_spare 0 catalog 9 log_rows 261 attestations 144
v5-b5-beta-a1-20261010T0742Z manifest_files 10 pointwise_ok 10 pointwise_bad 0 bad_unreadable 0 bad_mentions_spare 0 catalog 10 log_rows 268 attestations 149
v5-b5-alpha-a3-20261009T0644Z manifest_files 10 pointwise_ok 10 pointwise_bad 0 bad_unreadable 0 bad_mentions_spare 0 catalog 10 log_rows 268 attestations 149
```

## What the counts say

- The screen was **not evaluated**. The harvest stopped at `source_manifests_unrecorded`: the stored
  verdict (written by the clone's verdict writer at the harvest) names no source campaign manifest, so
  the harvest had no authenticated list of the window's references to re-run the screen on.
- The references that survive are 2 at the start (3 succeeded, 1 dropped at the harvest for a competing
  process that overlapped its request), 1 at the midpoint and 2 at the end (1 aborted at idle admission
  at run time). The registration's screen is defined for that shape (at least 2 at each endpoint,
  section 6.5). So no physical measurement removed this window: a record did.
- Every campaign manifest in the runs root authenticates, 10 of 10. The window that harvested cleanly
  has 9; this one has a tenth, and the one extra campaign invocation here is the reference spare, which
  ran and left no bundle. The first seal's attempt 3 also has 10 and also ran a spare that failed. The
  working hypothesis, to be proved from the code: a spare invocation that leaves a manifest and no bundle
  makes the verdict writer record no sources at all, and the harvest then cannot re-run the screen. If
  so, every window that loses a reference at run time is removed whatever its physics.
- Separate, and not fixable without a new seal: the spare itself appears not to run live (it exited
  within about ten seconds in both windows that started one). It restores margin only; its fix would
  change code a window executes and is kept for a later erratum, if one is needed.

## Decision

This is the table's "harvest problems first" case in substance (registration 7.2) and both seats'
conditional answer (d). **BETA attempt 2 is not armed now.** The harvest program is diagnosed and, if the
defect is in the desk program, fixed by the route of brief section 9 for code that does not run during a
window (a fix seat, an independent executing review, the whole suite, CI, a cold Fable 5.1 pass, a new
harvest pin by addendum); then attempt 1 is harvested again from the same bytes into
`/Users/edr/night-archive/harvest-v5-b5-beta-a1-20261010T0742Z-r2`, and the decision is taken from that
harvest: claim-usable means BETA is done and GAMMA attempt 1 is next; otherwise BETA attempt 2.

Why not arm attempt 2 meanwhile: no agent may run while a window runs, so a window and the fix cannot
overlap; a second window that loses a reference would meet the same defect; and if the re-harvest makes
attempt 1 claim-usable it is the analysed window and attempt 2 would have been six hours for nothing.

Limit on the wait: an arm needs t0 between 00:10 and 17:15 local (RUN_STATE item 4). If the fix cannot be
merged and pinned in time for a t0 by 17:15 today, the activation at that point arms BETA attempt 2
unchanged instead (both seats' default answer), and the fix continues after that window.

For later arms, from the Opus seat and adopted as procedure (it changes nothing a window reads): prefer a
t0 whose chain is not running between 05:15 and 06:45 local, until journals show the scan is not daily
at that hour.

## Next action

The fix lane: branch `lane/2026-10-10-harvest-screen-sources` from `224a264c5`, worktree
`/Users/edr/code/JouleWise-wt-harvest-sources`; papers in
`/Users/edr/night-archive/b5-consults/beta-a1/fix/`. If that directory has no `sol-fix.md`, launch the
seat from `fix/BRIEF-sol-fix.md` (write it from this record if absent). Then the gates above, the
addendum, the desk root move, the re-harvest, and brief section 6.
