# 04 — Cold Fable 5.1 final pass on PR #389 (head 2ddf85ae), verbatim stdout

Prompt: `~/.claude/jobs/4158e658/tmp/fable-finalpass-handback.txt` (reproduced below). Command: `claude -p --model fable --effort high --permission-mode plan --allowedTools Read,Glob,Grep,Bash` from a detached worktree at the head.

```
**Verdict: APPROVE.** No cures.

**(1) Truth against code and records.** I found no false sentence. Spot-checks beyond the lens's list, all executed this session:

- **Expected stop cause.** The stop-branch function compares the observer floor against the registered smallest holdable share of 0.05 and appends `observer_floor_above_smallest_holdable_share`. The summary calls it on every run, SPREAD_RECORDED or INCONCLUSIVE, so the "evaluated on every summary" sentence holds. The registration lists three stop branches; the handback correctly says a pilot can reach two.
- **0.5-core predicate.** The gate constant is 0.5, the offender test is "at or above", the refusal text matches word for word, and the observation is rooted at the checking process's own pid. The arm check is scoped to evidence chains only.
- **Two-consecutive abort, no successor.** The executor raises the typed abort at two consecutive exclusions and the marking guard runs before the per-envelope rule, so a marking failure carries `night_probe_error`. When the guard fires at envelope 1 nothing has been appended, so `envelopes_attempted` is 0 and the envelopes file is never written. The arm-retry text says "until that lane lands the chain ends with no successor". The D-182 addendum is recorded verbatim with Ed's 01:06 message id.
- **Timeline.** Recomputed from epoch 1790172000: 06:50, 06:52, 06:54, 06:55, 09:30, 09:35, dead-man 1790184900 at 10:35. The gate's 30 s observation precedes the chain launch in the driver, so 07:31:10 and 09:14:10 are right.
- **Numbers in records.** XprotectService 0.353 in one row and corespotlightd 0.104 over 14 rows are in harvest §6; ruling 10 §3(i) does say "5×"; 0.5/0.353 is 1.4×. Ruling 10's 270 J is "1.1 W × 240 s", which the fixed sentence renders faithfully. Ruling 21 gives 0.3194 W as 153.3338/480. Synthesis 35 item 3 has "not holdable above this apparatus".
- **Registration and pins.** v3 digest recomputed and matches the gate constant; every quoted number matches the file; v2 differs only by the three added rules and the 0.5 bar; chain-source digest matches the live script. The four estimator files are byte-identical between the attempt-2 arm head and the v3 merge. Slot arithmetic is untouched in the v3 delta.

**(2) Fix round.** All six material findings and nine nits were applied correctly. M3 is better than the lens's proposed wording. The chi-square example reproduces from the production functions (1.6103, 1.762, 7 pairs). No new defect introduced; protected sections unchanged.

**(3) Pins check.** The diff over `joulewise scripts configs` from 3a411784 to 2ddf85ae prints nothing, exit 0. This head is admissible as the measurement head.

**(4) Kernel.** Four registrations plus one dependency marked satisfied. No process rule ratified or amended; THROUGHPUT-01's note states this explicitly. Kernel check rc 0, 44 tests OK.

One non-blocking observation: the rule-3 sentence "t0 + 1,840 s after the chain starts" reads awkwardly, but the clause that follows makes the instant unambiguous.
rc=0
```

## Prompt

```
COLD FABLE 5.1 FINAL PASS (read-only; you are a fresh instance with no loop context). Single non-interactive session: no background tasks, no subagents, foreground probes only, 20-minute budget. Do not modify anything; only Read/Glob/Grep and read-only Bash. Never run launchctl, sudo, powermetrics, systemsetup, or any `joulewise.evidence_night` subcommand other than `prepare --help`.

Merge candidate: branch `docs/2026-09-23-4158e658-handback-v3` in worktree /Users/edr/code/JouleWise-wt-handback-4158e658, HEAD 2ddf85ae60416969fb5cb9b12b30b4d0d82e54c4, base main 3d668e98. Review `git -C /Users/edr/code/JouleWise-wt-handback-4158e658 diff 3d668e98..2ddf85ae60416969fb5cb9b12b30b4d0d82e54c4`. It is docs + bookkeeping only: (1) docs/process/NIGHT_HANDBACK.md §"Purpose of this night", §"Where the results are" and the head of §"Next lane" rewritten for the next armed night — the QPE-01 idle-variance pilot re-run under registration v3 (configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json, merged in PR #387 at 3a411784), plan id qpe01-pilot-n1-20260923-0700, t0 07:00 PDT 2026-09-23 (epoch 1790172000); the night courier (a Claude model) reads this file from the measurement clone at this head when reporting the night, and this head becomes the night's pinned measurement_head; (2) state-kernel registration of four lanes (THROUGHPUT-01, BLOCK-TWO-DESIGN-01, PROMPT-AUDIT-01, CENSUS-MULTILINE-ARGV-01) and QPE01-ABORT-SUCCESSOR-01 moved to ready, with generated regions and a test inventory.

A non-author Opus 5.5 lens already reviewed it: /Users/edr/.claude/jobs/4158e658/tmp/lens-opus-handback.md (MERGEABLE AFTER FIXES; no blockers). The author then applied a fix round; the author's disposition is /Users/edr/.claude/jobs/4158e658/tmp/fixround1-disposition.md. Read the lens and the disposition, then the diff.

Answer, under 400 words:
(1) Is any sentence in the rewritten handback false against the merged code (joulewise/quiet_predicate_campaign.py, joulewise/night_gate.py, joulewise/evidence_night.py, joulewise/arm_retry.py) or the ruled records it cites (docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/ rulings 10/21/31, syntheses 15/25/35)? Spot-check the lens's claims and at least five of your own choosing — especially the expected stop cause observer_floor_above_smallest_holdable_share, the 0.5-core arm/t0 predicate, the two-consecutive abort with no successor, and the timeline instants.
(2) Were the lens findings resolved correctly (applied or declined for a sound reason)? Did the fix round introduce any new defect?
(3) Does `git diff --stat 3a411784..2ddf85ae60416969fb5cb9b12b30b4d0d82e54c4 -- joulewise scripts configs` print nothing (the pins check that makes this head admissible as the night's measurement head)? Run it.
(4) Does the kernel registration ratify or amend any process rule (it must not)?
Verdict: APPROVE / APPROVE WITH CURES (exact cures) / REFUSE.
```
