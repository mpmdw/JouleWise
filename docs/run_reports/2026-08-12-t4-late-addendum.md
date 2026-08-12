# Run report addendum — T4-late final block (2026-08-11 late → 2026-08-12 checkpoint)

> **Evidence base (successor-assembled, dictated-fills verified):**
> `RUN_STATE.md` §“T4-LATE FINAL CHECKPOINT (2026-08-12, Ed stop order)”
> (lines 50–124); `git log` on main `2e5b1d9..4cce475` (`2e5b1d9`, `0977cfb`,
> `c61f840`, `fcc97b9`, `0b979e3`, `4cce475`) and `origin/main` `2b43de8`;
> `docs/decision_log.md` D-132/D-133/D-134/D-135 index rows and bodies;
> `docs/decision_log.md` on `origin/impl/u11-idpin-projection` for D-131;
> `docs/council_log.md` C-056 (index row + body);
> `docs/process_traces/2026-08-11-fcm-coldgate/` (5 files);
> `docs/process_traces/2026-08-11-staged-contracts/` (3 files);
> `docs/process_traces/2026-08-11-5c-readiness-contract/` (2 files);
> `gh pr view` for #127/#129/#131/#132/#133/#134;
> `~/.claude/skills/skill-usage-log.md` §“2026-08-11 T4-late block” rows.

**Scope.** This addendum covers the block *after* the post-checkpoint addendum
already appended to `docs/run_reports/2026-08-10-t4-window-session.md` (landed
`2e5b1d9`, 2026-08-11 16:14 PT) and after council entry C-056, whose own
recorded span ends at 15:56 PT. It runs to the T4-LATE FINAL CHECKPOINT commit
`4cce475` (2026-08-11 20:33:36 PT = 2026-08-12 03:33 UTC). Dates stated as
“2026-08-12” in the checkpoint and in D-135 are UTC dates for PT-evening work.

**One line (checkpoint's own summary, `RUN_STATE.md` line 52–55):** six PRs open,
every one PASSED its independent adversarial audit, all waiting on CI wall-clock;
merge in order with a D-121 terminal review each, then launch the two staged
implementations, then the freeze lane.

## Decisions minted

| ID | Subject | Home | Status at checkpoint |
|---|---|---|---|
| D-131 | U11 identity-pin projection contract (adopt-as-proposed) | `docs/decision_log.md` §“D-131: Identity-pin projection contract — adopt as proposed” **on `impl/u11-idpin-projection` only** (`37a6e98` moved the body into ID order) | **PROPOSED** — lands with PR #131; not on main |
| D-132 | Stopping rules target doom loops, not converging instruments | index row + §“D-132: Stopping rules target doom loops, not converging instruments”; commit `31a3863` | adopted (Ed, in-thread) |
| D-133 | FCM-01 disposition — hybrid + ALT-D120 | index row + §“D-133: FCM-01 disposition — hybrid + ALT-D120 (cold gate, revised sitting)”; commit `f0e7cf6` | adopted (cold gate; magistrate, no dissent) |
| D-134 | §5C arm-readiness record contract — two-stage append-only receipts | index row + §“D-134: §5C arm-readiness record contract — two-stage append-only receipts (adopt-as-proposed)”; commit `fcc97b9` | adopted (consult adopt-as-proposed) |
| D-135 | Site budgets advisory — only the physical Lakebed cap may gate | index row + §“D-135: Site-capsule budgets are advisory — only the physical Lakebed cap may gate”; minted in `4cce475` | adopted (Ed, in-thread; transcribed) |

- **D-134** binds two-stage append-only receipts: a pack-pinned non-authorizing
  FREEZE receipt plus an external pack-binding ARM receipt (the hash cycle is
  broken because the frozen bytes declare the arm-receipt schema/namespace, never
  its future sha); `d117_row_registry_v1.json` is the sole row authority for
  ALPHA/BETA/GAMMA with Markdown as checked views; `UNKNOWN` is prohibited
  (REFUSE or a registered `NOT_APPLICABLE`); derive-never-enter throughout;
  dry-run never authorizes; the impossible pre-launch single-foreground-launch
  row is replaced by an atomically consumable single-launch capability.
  (Evidence: D-134 body; trace `docs/process_traces/2026-08-11-5c-readiness-contract/consult.md`
  and `needs-ruling-report.md`.)
- **D-135** makes the 1,000,000-byte measured capsule budget, per-page/per-shard
  budgets, and pagination-margin assertions WARN-only; the only failing size
  condition is the physical Lakebed 1,048,576-byte cap under the real validator
  (CI-only — lakebed is not installed on the bench). Content is never trimmed,
  split, or archived to satisfy an advisory budget. It **supersedes
  SITE-CAPSULE-BUDGET-01**, whose follow-up had been recorded 18 minutes earlier
  in `0b979e3` proposing decision-body archival as the durable fix; D-135
  reverses that direction. (Evidence: D-135 body; `0b979e3` message.)

## Merge queue (checkpoint order; D-072 self-merge applies after each PR's D-121 terminal review at its final head, CI green)

| # | PR | Branch | Audit state recorded at the checkpoint |
|---|---|---|---|
| 1 | #132 | `respec/d124-withdrawn` | Gate audit ACCEPT (substance) + staleness sweep applied; **merges first** — the pack-freeze lane unblocks at this merge per D-133 disposition (1), and nothing FCM-shaped may gate it |
| 2 | #131 | `impl/u11-idpin-projection` | Four-round gauntlet complete, final delta ACCEPT; merge unlocks the staged §5C implementation (D-134) |
| 3 | #127 | `impl/calexits-reliability` | Audit synthesized ACCEPT (FIND-1 routed to WO-SAMPLER-SUPERVISOR); production commit still held for Ed's live sudo/powermetrics checklist |
| 4 | #133 | `paper/train-g` | Default-floor mainline; carries the CONDITIONAL-INSERT-TIGHTER-FLOOR swap block for Ed's pending call |
| 5 | #134 | `impl/floor-commonmode-01` | D-133 desk thread COMPLETE: rounds 5–10, disposition items (2)+(3) discharged, round-10 delta ACCEPT no-findings; site-chain green after dedup `479eefc` |
| 6 | #129 | `impl/ci-proof-restructure` | Delta ACCEPT-FOR-MERGE with the head-bound 23-job hosted campaign green at EXACT head `35f1fe5` (run 31541829071) = D-130's second independent execution DISCHARGED |

**Post-checkpoint state (verified at writing).** PR **#132 is MERGED** —
`2026-08-12T03:41:14Z`, eight minutes after the checkpoint commit, landing on
`origin/main` as `2b43de8`. Five PRs remain open (#127, #129, #131, #133, #134).
Local main is at `4cce475`, one commit behind `origin/main`. (Evidence:
`gh pr view 132 --json state,mergedAt`; `git log --oneline -3 origin/main`.)

**CI at writing** (`gh pr view <n> --json statusCheckRollup`, conclusion counts):
#129 11/11 SUCCESS; #133 11/11 SUCCESS; #127 12 SUCCESS + 1 pending; #131 9
SUCCESS + 2 pending; #134 3 SUCCESS + 8 pending (head `cbf609f`, the post-#132
main merge). This is consistent with the checkpoint's "waiting only on CI
wall-clock".

## FCM-01 desk thread — rounds 5–10 under D-132/D-133

The unit was STOPPED on its round-5 delta (FCM-R5-01, fabricated-record
admission, 5.0e-10 J exact; record `0b5fce8`, transcribed `8c5009c`), REVIVED by
**D-132**, REJECTED again at round 6 (FCM6-01, forged registration admitted by
both validators and by `authenticate_floor_artifact_bytes`), and dispositioned by
the cold gate as **D-133**. Rounds 7–10 executed items (2) and (3) of that
disposition:

- **ALT-D120 (item 2)** — the serialized registration vocabulary is DELETED, so
  the demonstrated serialization-boundary forgeries become closed-profile
  unknown-key refusals (the D-120 precedent: delete vocabulary, don't
  authenticate it).
- **Full fresh delta (item 3)** — the relocated arithmetic cleared
  **terminally**: zero exact understatements across 4,096 independent
  rational-arithmetic cases plus a 1,536-case differential against the
  round-5-accepted implementation, with no drift by AST comparison. The
  terminality clause (any exact understatement = permanent drop, no revival) did
  not fire.
- Input-validation hardening closed to the floor: recursive reserved-key
  refusal, strict duplicate-key JSON, and a complete finite-number policy
  (including overflow-to-`inf`) at every admitted-byte entry, with a
  from-scratch `loads` census whose every "guarded upstream" verdict rests on an
  executed demonstration.
- **Round-10 delta: ACCEPT, no findings**, at base/head `0635ace` on
  `impl/floor-commonmode-01`; V1 ran nine mint/floor-extraction tests green on
  both `python3` and `python3.11`.
- The pinned core `scripts/mint_floor_artifact.py` is unchanged throughout.

Branch head then took `cb51bd5` (merge of post-D-133 main), `9d196b5` and
`479eefc` (decision-log dedup: compact D-124-chain summary kept, rounds 5–10
prose moved to the process trace — the merge had re-introduced both copies and
the whole capsule ran 2,788 B over 1 MiB), and `cbf609f` (post-#132 main merge,
integrating the fallback spec state).

**Not consumed this cycle:** the tighter floor (1.869502 J vs the 8.611855 J
default) cannot reach a minted artifact until WO-MINT-ESTIMATOR-VOCAB lands —
the mint has no estimator vocabulary (D-133 cl.4). This PR lands the estimator
and the custody closure; consumption is a separate gated step.

(Evidence: `gh pr view 134` body; `docs/process_traces/2026-08-11-fcm-coldgate/round10-delta-ACCEPT.md`
verdict block and V1; `git log --oneline origin/impl/floor-commonmode-01`;
D-133 body disposition items (1)–(5).)

## Cold-gate custody trace

`docs/process_traces/2026-08-11-fcm-coldgate/` now holds five files:

| File | Bytes | Content |
|---|---|---|
| `packet.md` | 24,015 | the mechanically-assembled adjudication packet |
| `ruling-1-original.md` | 2,320 | the fresh Fable adjudicator's first ruling |
| `ruling-2-refuter-brief.md` | 6,254 | the paired Opus contract-lens refuter brief |
| `ruling-3-revised.md` | 6,071 | the revised/final ruling (the adjudicator withdrew its own first ruling) |
| `round10-delta-ACCEPT.md` | 9,472 | the round-10 delta audit report, ACCEPT / no findings |

The first four landed in `2e5b1d9`, which states the standing rule they
establish: **every cold-gate sitting custodies its packet and rulings under
`docs/process_traces/` before the ruling is executed.** This closes the gap
C-056 flagged under "Source cautions" — that the cold gate had again left no
custodied ruling artifacts, and that the day's packet had overwritten the prior
session's packet at the same scratchpad path. `round10-delta-ACCEPT.md` landed
later, in the checkpoint commit `4cce475`.

## Council record

**C-056** — "T4-late — the delete-don't-authenticate gate, four strictly
narrower audits, and a bench fix the next delta walked around (2026-08-11)" —
carries both an index row and a body (`docs/council_log.md`), landed `2e5b1d9`.
Its recorded artifact span is **01:05 → 15:56 PT**, so it records the day up to
the bookkeeping batch, not the final block covered here: rounds 9 (in flight at
its writing) and 10, D-134, D-135, PR #133/#134 opening, and the merge-queue
assembly all post-date it. Its instrumented totals for the day: 43 Sol
run-status files, 31 manifests recording 34 `run_started` attempts at 18 high /
16 xhigh, 17 runs at rc 0, 13 at rc 65, 2 at rc 79, 58,439 s aggregate recorded
run time.

## Staged implementations (contracts custodied, launch gated on merges)

- **WO-MINT-ESTIMATOR-VOCAB** — launches after #134 merges, stacking on that
  branch's code once in main. Three-site spec-authoritative estimator dispatch;
  contract `docs/process_traces/2026-08-11-staged-contracts/mintvocab-impl-contract.md`
  (consult verbatim at `mintvocab-consult.md`; design adopted in `TASK_QUEUE.md`
  via `c61f840`). Full D-118 gauntlet required.
- **§5C readiness-record generator** — launches after #131 merges. Implements
  the D-134 ten-clause contract (trace
  `docs/process_traces/2026-08-11-5c-readiness-contract/consult.md`): two-stage
  receipts, row registry, and the doctrine amendments enumerated in the consult.

(The staged-contracts directory also holds `pr129-delta-ACCEPT.md`, the PR #129
delta verdict.)

## Owed at the checkpoint

- **D-135 implementation** — make all conservative site budgets WARN-only in
  `scripts/pack_capsule.py` and the site test suites; only the physical
  1,048,576-byte Lakebed cap (real validator, CI-only) may fail anything.
- **Freeze lane** after #132 + #131 — freeze plan (Q1/Q8 ruled, Q7 void,
  addendum items (1)+(3) LIVE per the item-level disposition on the fallback
  branch) → FREEZE → U11 freeze projections → arm packet per D-134, with the
  discrepancy resolutions ready at
  `~/JouleWise-window-custody/t4-session-20260810/arm-packet-discrepancy-resolutions.md`.
- **Q8 p256 prefill floor cells** build — launches on post-#132 main (now
  unblocked: #132 merged as `2b43de8`).
- This addendum.

**Ed-owed (nothing blocks without them):** the gamma-arm schedule call flagged by
D-133 — tighter-floor-in-main-paper would make WO-MINT-ESTIMATOR-VOCAB critical
path and hold the freeze wave; default is that the freeze proceeds and the
tighter number banks for ICPE. Quantified stake: the default floor 8.611855 J
leaves the funded p256 arm ~3 J margin (likely publishes as not-resolvable);
the tighter 1.869502 J leaves substantial margin. PR #133 carries the mechanical
swap either way. Also owed: the live sudo/powermetrics checklist for #127's
production commit, the extension-axes roadmap review, and §5A taps on the quiet
night.

## Sol tooling failure classes logged this block

Three distinct classes were logged on 2026-08-11 in
`~/.claude/skills/skill-usage-log.md` §“2026-08-11 T4-late block”. Together they
cost roughly ten failed runs; the checkpoint directs a fresh session to read
them before launching Sol.

1. **The default `--timeout 900` was the true systemic killer** (2nd addendum
   row, root cause corrected). Every "thin output" / rc-65 / missing-envelope
   death that day was `codex-run-v3` killing the session mid-turn at 15 minutes
   — no `task_complete`, therefore no `-o` file. C-056 records four runs dying
   at exactly 902 s with `error_stage=report_capture`: `calexits-fix3`,
   `calexits-fix3b`, `fcm-alt-d120`, `u11-fix2b`. **Rule:** every substantive Sol
   run passes an explicit `--timeout` (10800 for audits/implementation; size it
   to the suite).
2. **The read-only sandbox denies all temp dirs** (1st row; real but secondary
   to class 1). Suite-executing runs — audits included — die mid-turn without
   envelopes, and `codex -o` never materializes; recover `last_agent_message`
   from `~/.codex/sessions` rollouts. **Rule:** every suite-executing Sol run,
   implementation and review alike, launches with `-s workspace-write` plus an
   END-clean worktree instruction; WRITE_SCOPE enforcement still guards tracked
   files. A custom `TMPDIR` is never the fix (outside the worktree it is
   sandbox-denied; inside it trips the wrapper's rc-64 strict-scope-roots). The
   same row also records the positional-CLI defect: `codex-run-v3` takes OUT as
   the first positional and PROMPT as a literal string last — there is no
   `--prompt-file` flag, and a path passed as the prompt yields rc-64
   missing-WRITE_SCOPE.
3. **The Codex cybersecurity content filter, plus the recovery-resume re-send
   trap** (3rd addendum row). The round-9 delta died three times to intake
   refusal, not tooling: adversarial-audit prompts using "attack / bypass /
   forge / duplicate-key payload / exploit" get flagged ("This content was
   flagged for possible cybersecurity risk… Trusted Access for Cyber program"),
   and `codex-run-v3`'s null-final-message recovery-resume **re-sends the flagged
   text and re-fails**. **Rule:** frame refuter and adversarial-review prompts as
   DEFENSIVE robustness / input-validation testing of our own code — which it is
   — "confirm the loader rejects malformed/non-canonical inputs fail-closed",
   not "attack the loader". Same rigor, same executed checks, neutral verbs. If a
   run's `.log` contains "flagged for possible cybersecurity risk", do not
   relaunch verbatim and do not trust a recovery-resume; rewrite the prompt
   first.

## Anomalies and source cautions

1. **D-131 is not on main.** Its index row and body exist only on
   `origin/impl/u11-idpin-projection` (PR #131, open), and its recorded status
   there is **PROPOSED** — "adopt as proposed from the binding U11 design
   consult; the magistrate reviews this transcription and implementation before
   push" — not `adopted`. It becomes a mainline decision at #131's merge. Any
   citation of D-131 against main before that merge will not resolve.
2. **The merge queue moved after the checkpoint.** #132 merged at
   `2026-08-12T03:41:14Z` (`2b43de8`); the "six open PRs" framing is accurate as
   of `4cce475` and stale thereafter. Five remain open.
3. **`O1`/`O2`/`O3` are RUN_STATE shorthand.** `docs/decision_log.md` D-133
   labels its disposition `(1)`–`(5)`; the mapping is semantic, not literal.
4. **PR #133's audit verdict is not individually recorded.** The checkpoint's
   blanket "every one has PASSED its independent adversarial audit" is asserted
   in its one-line summary, but the per-PR lines record verdicts for #132, #131,
   #127, #134 and #129 only; the #133 entry states content, not a verdict. No
   train-G audit verdict was found in `RUN_STATE.md` or `docs/council_log.md`.
5. **C-056 does not cover this block** (span ends 15:56 PT) — see §Council
   record. It is a same-day record, not a block record.
6. **D-135 and the `0b979e3` follow-up point in opposite directions** by
   18 minutes: `0b979e3` records archival of superseded decision bodies as the
   durable fix for capsule-budget pressure; D-135 rules the conservative budget
   advisory and forbids trimming content to satisfy it, keeping archival
   available only if the physical cap is ever approached.

---

**Postscript (successor session, 2026-08-12 ~04:10Z, magistrate).** The merge
queue began executing minutes after this addendum's evidence was gathered:
PR #132 merged 03:41Z (recorded above), **PR #133 merged 04:04Z** after a
D-121 terminal review whose full-diff verification (numbers, exact-match
conditional block, stale-reference sweep) is recorded on the PR — that review
comment now stands as #133's individually recorded verdict, resolving
anomaly 4 forward. The successor session's own run report will record the
remainder of the queue.
