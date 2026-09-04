# Durable pause state, 2026-09-02 late (Ed: "pause all work ... persist so we can fix" the CLI Gmail connector)

Written by the magistrate (session `joulewise-b2`, successor of `joulewise-30`)
at ~21:05 PDT. Supersedes file 39 for every lane below. Ed ordered a pause
with no new launches; in-flight agents finish and land in the scratchpad
(paths below die with the session, so their reports are custodied here or in
the trace directory as they arrive).

## Why paused

The claude.ai Gmail MCP connector expired inside this CLI session and did
not come back after `/mcp` (tools failed to fetch). Gmail works for Ed in
the web and desktop apps, so the fault is on the CLI side. Email is the
only channel to Ed while he is away for ~a week (mobile push never
arrives), so nothing proceeds until the channel is fixed. A GitHub-issue
fallback (`gh issue create`) was tried and is blocked by the auto-mode
classifier; no allow rule for it exists in any settings file yet.

## Ed rulings tonight (at the machine, 2026-09-02 ~20:10-20:30 PDT)

1. Leave rehearsal-20260903 (02:56) ARMED. Relayed to `joulewise-83`, which
   re-armed the plan against canonical HEAD `33290b8b` after the stale-pin
   finding below (courier plist re-rendered to claude 2.1.259).
2. The magistrate MAY kill its own session and codex children before a real
   measurement window; a relaunch agent is the way back (D-169
   `UNATTENDED-LAUNCH-01` shape). Design consult launched (three seats,
   below); NOT built, NOT installed.
3. Ed ran the worktree cleanup: 25 worktrees + 20 merged branches removed;
   18 worktrees remain (all live or held).
4. Ed ran `sudo pmset -b sleep 0 disksleep 0` (battery no-sleep).
5. Ed is away ~1 week from 2026-09-02; hands-free is REQUIRED.

## Freeze agreement with `joulewise-83`

No git operations in the canonical checkout `/Users/edr/code/JouleWise`
(no pull, checkout, commit) by either session until after 03:30 on
2026-09-03; worktree and origin operations are fine. The night gate reads
the canonical HEAD. Night fences for main pushes: 02:45-03:30 and the
07:00 minute.

## Lanes

**#274** merged to main `b81a2ac5` (20:01 PDT). Post-push notice sent.

**Decode-identity branch** `fix/2026-09-02-decode-identity-set` (this
worktree). F-N4 consult COMPLETE: luna (file 40), Opus (file 41), blind
Fable (file 42). Headlines: all three reject Cures A and B; both fresh seats
found NEW factual defects in the landed lineage paragraph
(`identity_pin_projection.md` ~:609-621): F-N5 = a missing launch manifest
emits `launch_consumption_invalid` and missing lifecycle receipts emit
`launch_lifecycle_incomplete`, not the two codes the paragraph names; F-N6 =
the pack root is recorded at ARM (`_pack_record`), not at consumption. Both
propose a Cure C: define the five terms in the contract's existing
defined-terms block (~:580-594), relocate the :671 definitions, delete
`replays`/`strictly`/`arming time`, and state the reason code as "the
launch-lineage code belonging to the artifact that failed". Routing split:
Opus (a) mandatory cold gate; blind Fable (c) -> cold gate because the cure
is a process rule; luna (b). Magistrate synthesis (file 44) NOT written.
Resume: write the synthesis; assemble a MECHANICAL cold-gate packet carrying
Cure C plus F-N5/F-N6 (Opus notes the file-38 packet is authored, not
mechanical); cold seat + Opus refuter; then round 4 with executed probes for
every behavioural clause (before/after/only/never/every/strictly/backticked
codes) and the writer-side first-use table pasted before landing.

**Fresh Fable audit fleet** (Ed: "launch a fresh audit to investigate
everything"), reports in the session scratchpad
`/private/tmp/claude-501/-Users-edr-code-JouleWise/59b55324-ee87-44fe-bab4-af77ab717514/scratchpad/`:
- `audit-night-loop.md` DONE (3 blockers, 6 should-fix, 3 nits): plan pins
  the moving dev-tree HEAD (stale refusal; cured for tonight by re-arm,
  structural fix = pin the measurement checkout); no runtime bound on the
  chain (`window_max_s` unused); day-2 dead-man over a live chain crashes on
  write-once `refusal.json`; census `pgrep -lf "codex|claude|t3"` matches
  Claude Code background shells via `~/.claude/shell-snapshots`; courier is
  the only relaunch and chains nights with no wake source; blockers B1-B10
  for the first pack-bound night (B3 = E-10 amendment, Ed by email; B4 =
  `hC` custody route, magistrate ruling).
- `audit-docs-vs-truth.md` DONE: 26 ranked corrections; top: RUN_STATE
  resume pointer is off-main; RUN_STATE still says merge #274; D-170 shown
  open though installed (#273/#274/#275), 9 kernel rows spuriously blocked
  on it; `V4-TRANSACTION-01` READY though `_v4` is never collected (D-164);
  `PIPELINE-SMOKE-LIVE-01` blocks on a ghost event; NEXT MACHINE STEP stale
  in three places; four ruled-not-installed rows; `feat/2026-09-02-paper-c`
  has 2 unmerged commits with no PR.
- `audit-paper-rq.md` DONE: 115 `[FILL]` markers; no claim-eligible
  collected data (all corpora predate anchor-v3); §3 promises four
  instrument characterizations `_v5` does not collect (Ed ruling needed);
  24 first-use failures in the draft; 100 ms cadence never justified;
  transfer fiducial not runnable; 20-hour work list ranked (§6 negative from
  data on disk first).
- `audit-measurement-path.md` DONE (12 findings, 18 prerequisites): BLOCKER
  no generator exists for the `_v5` floor packs
  `d117_floor_qwen3-{1p7b,8b}_v5` (ruled 171a R-6, owned by no kernel row);
  BLOCKER the measurement checkout `3c96b18f` is 412 commits behind main and
  lacks every G2-a producer (fast-forward + venv relock before G2-a);
  should-fix: weight bytes never compared to a pre-declared hash (pin the
  folded-weights sha in the panel), `launch_window.py` never re-verifies
  model bytes between arm and launch, summarizer trusts a reduce-layer label
  (`CUSTODY-HARDEN-01`). CONFIRMED sound: G2-a selector/checker per D-166,
  tokenizer/chat-template pins, D-078 time anchoring, downstream binding
  end to end.
- `audit-code-tests.md` IN FLIGHT (Fable).

Peer `joulewise-83` became unreachable at ~21:10 (after confirming the
re-arm); whether it exited deliberately as its own stand-down is unknown.
- Watchdog design consult IN FLIGHT: `sol-watchdog-design.md` (Sol xhigh),
  `opus-watchdog-design.md`, `blind-fable-watchdog-design.md`.
Custody all five audits + three designs into a trace directory
`docs/process_traces/2026-09-02-fresh-fable-audit/` on resume (worktree,
not the canonical checkout, until the freeze lifts).

**Owed Ed email (batch 2):** drafted and verified at
`scratchpad/ed-email-batch2.md` (six decisions with defaults). NOT SENT:
connector down. Send first thing after the channel is fixed.

**Post-merge kernel batch** (bench, main): unchanged from file 39, plus the
docs-audit corrections above and the missing rows it names
(`LINEAGE-RELOCATABLE-01`, `R7F-EXIT3-SEMANTICS-01`, D-170 close, V4
retirement, ghost-dep retarget). Not started.

## Resume sequence

1. Verify the Gmail tools are back (ToolSearch `gmail`); send batch-2 email.
2. Harvest the in-flight agent reports from the scratchpad (or their task
   output files) and custody them.
3. Respect the canonical-checkout freeze until 03:30; then RUN_STATE T31
   (pointer to this file; #274 merged; unattended lane first).
4. Watchdog: synthesize the three designs -> cold gate -> build (Sol) ->
   gauntlet -> Ed's install approval by email.
5. Decode-identity: synthesis file 44 -> mechanical cold-gate packet.
6. Paper: the audit's 20-hour list, Sol/Opus seats in worktrees.
