## D-180: Arm recoverability and steerability (Ed, 2026-09-10)

**Status:** ratified by Ed, 2026-09-10 ~03:30 PDT, verbatim in
`docs/process_traces/2026-09-09-rehearsal-harvest/121-ed-rulings-2026-09-10-recoverability-steerability.md`
("1, yes to all 3" to the three proposals quoted there; "4. yeah get that working so
inbetween windows you can relaunch and be accessible"). Recorded by the interactive
magistrate; nothing below is installed in code or runbooks by this entry — each clause
names its implementation lane, and until that lane lands the prior rule stands
(decided ≠ done). Forcing problem: on 2026-09-10 the resident activation could not arm
rehearsal-20260911 because two idle interactive Claude sessions were alive at the
arm-time census, and the only documented recovery was a new plan for the next night.

1. **Install windows recur within a day.** The install span for a stub or real night
   is no longer a single 03:00–06:30 block; the schedule may name several bounded
   install spans per day, each with the same "never install after the span closes"
   dead-man rule. Lane `INSTALL-WINDOWS-MULTI-01` lands the constants and the
   runbook/plan-writer changes; the ruled 2026-09-10 03:00–06:30 window stands for
   rehearsal-20260911.
2. **Pre-authorized retry class for non-physics arm aborts.** An arm abort whose
   recorded cause is one of: an idle interactive agent session in the arm-time census;
   a stale or mismatched notice hash; a watchdog CLOCK_UNCERTAIN or NETWORK_UNCERTAIN
   tick; or a transport failure, may be retried in the same or the next install span
   without a cold gate, with a refreshed notice email (new notice, same plan class,
   Ed's NO still overrides). Physics and evidence refusals — a non-empty census inside
   the plan span, any capture, clock, custody or ledger guard, any receipt refusal —
   stay fail-closed and keep the cold-gate path. Lane `ARM-RETRY-CLASS-01` writes the
   clause into NIGHT_HANDBACK and the runbook template.
3. **Idle interactive sessions are not foreign at the arm-time census of stub
   nights.** For REHEARSAL_STUB plans only, the runbook step-3b foreign-agent check may
   classify an interactive `claude`/T3 session as not foreign when it has no child test,
   measurement, or capture process. The plan span is unchanged: any agent process from
   t0 − 25 min until the chain exits refuses the night, so a session left open through
   t0 still refuses it. Lane `ARM-CENSUS-IDLE-INTERACTIVE-01`.
4. **Remote control between windows.** Ed wants the magistrate reachable live between
   plan spans. Lane `REMOTE-CONTROL-BETWEEN-WINDOWS-01`: test whether `claude
   --remote-control` starts under a pty wrapper from launchd, design how a relaunched
   magistrate can run remote-controllable between spans and exit before every span,
   and land it under the gates; until then the GitHub-issue directive channel (PR #313)
   is the steering path and email plus the pushed repository are the observation path.

Standing direction recorded with the rulings: Ed accepts the loss of live
observability for the issue channel ("KILL as long as you can keep experimenting and
have all the tools to keep running windows until you have a paper"), and the target is
a minimum viable paper ("i just want a minimum viable paper already").

### D-124 dated addendum — 2026-09-13 (cold gate 47, GATE-SENSIBILITY-SWEEP-01 B1): the zero-point provenance band is scale-bounded, and its re-set is ruled but not yet installed

Round 4's `isclose(rel_tol=1e-9, abs_tol=1e-12)` band compares the stored ABBA delta
`(B1+B2-A1-A2)/2` with the zero-shift contrast `z` (a coefficient-weighted `fsum` of
freshly re-integrated member energies). These are two different binary64 routes over
the same four numbers: the sequential route rounds once when it forms `B1+B2` (and
once more if the members straddle a power of two), so `|z - delta| <= 0.375 x
ulp(B1+B2)`, a quantity that steps in powers of two. Consequences, bench-derived: the
band CANNOT refuse identical operands while the largest member is below 8,192 J,
whatever the operand pattern, nor below 16,384 J when the four members lie in one
binade; the first refusal on the packet's pattern is at exactly 16,384 J per member
(demonstrated at 20,000 J: sequential 1.8189894035458565e-12 J against `fsum` 0.0),
and an any-pattern refusal is demonstrated at a largest member of 8,625.6 J. A second
condition must hold for any refusal at all: `rel_tol` rescues the block unless its
true delta is smaller than about 1.7e-7 of the member scale (about 1.8 mJ at 20,000 J
members), so only blocks whose members nearly cancel are exposed. G2-a member
energies are tens of joules, three orders below the lowest refusing scale, so B1 is
not G2-a-blocking.
RULED, NOT YET INSTALLED (option (ii)): both sites -- `dominance_closeout.py` (the
D-165 replay consumer) and `floor_extraction.py` (the upstream duplicate) -- are to
call one shared predicate with `abs_tol = max(1e-12, 64u x S)`, `u = 2^-53`,
`S = max(1, member envelope integral sum, |delta|, |z|, every |onset| and |offset|
sweep value)`, `rel_tol = 1e-9` unchanged and the once-only outward `|z - delta|`
charge unchanged. `S` and the `64u` factor are not new: `split_common_mode_block_width`
already computes exactly this scale and pad for the registered member-envelope term,
and the shared predicate is to be factored out of it, so no constant is added and the
registered parameter hash `dd61d388...` (which enumerates no tolerance) does not move.
The guard remains a pure provenance guard, not load-bearing for soundness; a delta
moved by 1e-6 J still refuses. The code change and its regressions R-B1-ADMIT /
R-B1-REFUSE / R-B1-ONE-PREDICATE are tracked as GATE-B1-PROVENANCE-BAND-01 and are
not a fence on G2-a. Option (iii), deriving `z` through `abba_delta`, was rejected:
the stored member energies are `summary.json` `phase_energy_j` reducer fields
(`floor_extraction.py:1839-1845`, consumed at 2710-2713) while `z` re-integrates the
trace curve (2534-2543), so no construction makes them byte-identical. The same
`1e-9/1e-12` band at `floor_extraction.py:2092` is unaffected: there both operands
are of member-energy magnitude, so `rel_tol` governs.

## TEST-SPEED-01 addendum (2026-09-13, activation 24b9d3dd, transcribing cold-gate ruling 17 Q2(b) as amended by its Opus pairing refuter 12 §3; the magistrate records, it does not amend)

**TEST-SPEED-01 addendum (2026-09-13): the PR-fast/full tier split is
retired.** Ed ratified three levers on 2026-08-03 (suite-speed priority, a
PR-fast/full tier split, a Blacksmith runner evaluation). The tier split
shipped 2026-08-23 in commit 349e06f4 as the additive `pr-fast` job in
`.github/workflows/ci.yml` and the `pr_fast_tier` block in
`scripts/test_timings.json`. Naming note: this row's status_note and that
commit subject both use "lever 2" for the unit-atomic sharding and crash-matrix
split that landed the same day; those stay, and only the tier split is retired.
The shipped tier was never a required check (main carries no branch protection
and no rulesets, verified 2026-09-13), although acceptance-evidence row 2 as
ratified says "the fast tier gates PRs"; that gating clause was never
implemented and is withdrawn with the tier. On 2026-09-12 Ed accepted PR #317
"as proposed" (Gmail 1a0969ba0b31c2b2), whose decision 2 proposed deleting
`pr-fast`, retiring `pr_fast_tier`, and amending this task's kernel text. The
retirement deletes zero tests. Row 2 becomes "Shard-runner implemented from the data;
the ratified PR-fast/full tier split implemented 2026-08-23 and retired
2026-09-13 by owner acceptance; the FULL suite remains the gate for merges,
verdicts, and audited heads; zero test deletions", and the goal sentence drops
"and the PR-fast/full tier split". The fence is unchanged and remains literally
true. Cold gate 17 (2026-09-13) ruled option A on PR #317 T2, so no path-based
skipping narrows it. Levers 1 and 3 are unaffected.

## D-181: Windows run whenever the machine is quiet; Fable 5.1 is the final eyes on every merge; the owner's hands step is prepared now (Ed, 2026-09-14)

**Status:** ratified by Ed, 2026-09-14 16:43 PDT, as directive issue #337 (owner, at the
machine), verbatim in
`docs/process_traces/2026-09-13-activation-24b9d3dd/55-ed-directive-337-verbatim.md`.
Recorded by the headless magistrate (activation `24b9d3dd`) through this PR, the same
way issue #316 became D-180 (Ed's words: "Record this ruling as a dated decision-log
entry through a PR under the normal gate, the same way #316 became D-180; do not amend
rule text yourself outside that PR"); nothing below is installed in code, runbooks or
the night machinery by this entry — each clause names its implementation lane, and
until that lane lands the existing mechanism's limits remain facts, not rules (decided
≠ done: the ruling is in force from the moment it names; what the machinery cannot yet
do is a mechanism limit, as Ed's clause 1 says). The ruling is standing;
by its own text it applies after the night armed under directive #336
(`d079-epoch-25g83-derivation-n1-20260915`, t0 2026-09-15 02:56 PDT) and to every
window after it, and it does not touch that night. Forcing context (factual, no rule):
the 2026-09-13 night fired and was refused by its own t0 census (an interactive session
and agent desktop apps present); the 2026-09-14 morning install span closed without an
arm because the arm-time census never cleared; the ordinary documented recovery was a
new plan for the next calendar night, until directive #336's one-night owner
authorization of an evening install. Ed rules that the spacing was never a scientific
requirement.

1. **Windows run as soon as the machine is quiet; no cadence rule.** Whenever the
   census is clean, day or night, several windows per day if the gates pass, with no
   artificial spacing (no "one night in three", no "only at 02:56", no minimum gap
   between windows). Ed keeps the machine quiet whenever he is not using it and will
   close every interactive session and quit the agent desktop apps on request; a
   notice email is enough. The soundness fences stay exactly as they are: physics and
   evidence refusals, pre-registration before data, the census at arm and at t0, the
   twelve-row gate, email-then-arm with Ed's NO overriding. Nothing else about timing
   is a rule. Implementation: the current machinery pins one plan at a fixed daily
   launchd minute inside the 02:45–03:30 belt with a single 07:00 dead-man and a
   calendar-day install span — a mechanism limit, not a scientific one. Lanes
   `INSTALL-WINDOWS-MULTI-01` (install spans as a list, dead-man per span),
   `ARM-RETRY-CLASS-01` and `ARM-CENSUS-IDLE-INTERACTIVE-01` are promoted to the top of
   the queue in that order, immediately after tonight's harvest and the §2.5 outcome
   action; they are designed so a plan can carry a t0 at any clock time and so a second
   window can be armed as soon as the previous harvest is done. (This supersedes the D-180 sequencing note "after G2-a
   instrument validation" on those three rows.) Queue mechanism, describing the kernel
   edit: `INSTALL-WINDOWS-MULTI-01` takes the agent lane's rank 0 (the lane head, ahead
   of every rank-1-and-up row) and is blocked on a hard start EVENT dependency — the
   09-15 night harvested and its §2.5 action taken — released in the bookkeeping that
   records both; the other two are blocked on their predecessor by a hard start
   dependency and take rank 0 in the bookkeeping that closes it — so the kernel refuses
   the first lane before the harvest event and refuses a successor before its
   predecessor closes; the head position of each successor is carried by the rank edit
   in that closing bookkeeping, not by the kernel on its own.
2. **Fable 5.1 is the final eyes on every merge.** Every PR that merges carries a
   terminal review by Fable 5.1 — the magistrate at the pinned model, reading the final
   head itself, not a delegate's summary — as its last review before merge. The
   twelve-row gate already requires this (row 7, the apex Fable code-reading diff gate;
   row 12, the magistrate's non-delegable terminal review of the final head sha). Both
   rows stay exactly as they are; never downgraded or delegated; the final head sha is
   cited in row 12 on every PR. No lane: this clause changes no text.
3. **Clear the owner's hands step for the first pack night now.** Lane
