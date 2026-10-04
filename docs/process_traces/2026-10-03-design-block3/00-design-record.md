# Block 3 design record (headless orchestrator seat, Opus 5.5, 2026-10-03)

Seat brief: `docs/process_traces/2026-10-03-activation-5145800b/40-design-block3-seat-brief.md`.
State: `~/night-archive/design-block3/`. Base: main `871a43f6`. Branch `design/2026-10-03-block3`.

## 1. The orchestrator's ruling under block 2 §7

Inputs: consult brief `30-consult-brief.md`; Sol 6.1 seat `31-sol-consult.md`; Opus 5.5 seat
`32-opus-consult.md` (both in `docs/process_traces/2026-10-03-activation-5145800b/`), answered blind
to each other. Block 2's per-member overlap counts, summary rows and selection replay were not read
by this seat, and are not read by any seat until block 3 ends.

**Ruling.**

1. **Block 2 is closed.** Its §7 stop holds: no third block-2 window, no selection from `w2`'s
   partial rungs (only a SELECT window supplies the selection input; `w2` has no post bracket),
   no pooling of block-2 members with any later window.
2. **The prefill-length question goes to a new, separately sealed block 3** (both seats' option a)
   with block 2's window shape, one window plus at most one recovery window, and the changes in §2.
   Block 2 §7 "It never goes to a third blind window" binds block 2's seal; block 3 is not a third
   window of block 2 but a new registration whose cause analysis and code change precede its data.
   The block-3 seal charge asks the cold gate to rule on this explicitly (Opus seat).
3. **Option b (collect `_v5` at 4096 now, without a completed probe) is refused.** Both seats: D-166
   as amended makes the G2-a sweep the precondition of selection and 4096 the outcome only when no
   rung of an evaluated ladder qualifies; doing it now would need a cold amendment of D-166 for no
   gain over one more sealed sweep.
4. **Cause.** Both: a transient machine state (macOS maintenance released by `dasd`, about six
   minutes long, inside which both of `g2a-small-p2048-r03`'s idle-admission attempts fell) **and**
   a retry-design limit (attempt 2 starts about 0.5 s after attempt 1, so the one retry cannot
   outwait a multi-minute burst). Re-arming alone does not remove it.
5. **No systematic, non-removable cause** (both): every valid `w2` member's clock anchor is
   `bounded`; the 12 members not run have no anchor, which is absence, not a defect; `w1`'s loss was
   a code defect fixed by #461.
6. **Remedy: a delayed idle-admission retry** (both). A default-zero policy field
   `idle_admission.retry_backoff_s`; when attempt 1 is rejected, the controller waits that long,
   then runs the same environment guard and the same one retry under unchanged criteria
   (CPU busy-ratio p95 ≤ 0.5, ≥ 30 samples, GPU idle check, abort on the second rejection). It is
   set non-zero only in block 3's own policy file; the production policy file's bytes, and so
   every existing campaign, are unchanged.
7. **`--max-failures 1` stays** (both): each rung needs all five members; continuing after a lost
   small member cannot make the window SELECT.

**Where the seats differed, and what I decided.**

| Question | Sol | Opus | Ruling | Why |
|---|---|---|---|---|
| Wait length | 300 s | 600 s | **600 s** | The one observed burst lasted about 6 min (12:55-13:01 local). With 300 s after attempt 1 ends (≈12:57), attempt 2 starts ≈13:02, at the burst's edge; 600 s puts it ≈13:07. The wait is spent only on a rejected first attempt (2 of 13 first attempts in `w2`), so the cost is bounded by the retry budget below. |
| Span | waits consume the existing allowance | budget the waits | **budget 4 waits explicitly** | A window that runs past its end is RECOVER and costs a full window (≈6 h); budgeting 4 delayed retries costs ≈47 min more machine hold per window. The 4 is the rate seen in `w2` (2 of 13) scaled to 24 members, rounded up. |
| Large-model stages after the post bracket (block-2 seal T2b) | not raised | adopt | **not adopted** | It changes the chain, the summarizer and the harvest's SELECT condition (block-2 refuter D4) for a failure mode with no observed case; the one observed failure class (idle admission) is treated for large members by the same delayed retry. New chain plumbing is what lost `w1`; minimizing chain change protects the window. Dissent recorded. |
| Pre-committed end state | not raised | if block 3 does not reach SELECT, D-166's 4096 branch applies, ruled by the same cold gate | **adopted** | It fixes before data what happens if the probe cannot complete twice more, so no further probe loop follows. 4096 is D-166's own conservative outcome (longest prefill, most records), and the `_v5` reporting of each member's count (D-166 two-way wording) keeps any shortfall visible. The block-3 cold gate rules on it as a prospective amendment of D-166's precondition. |
| Block-2 counts | (blind) | stay unread until block 3 ends | **adopted** | Keeps block 3's design independent of what block 2's partial data would select. |

None of the differences is a science disagreement about what a number is or whether it is true:
wait length, span and stage order change only the chance of losing a window, and the end-state
clause is adopted from one seat with no opposing view. No cold Fable judge is convened for the
ruling itself; the block-3 seal is the cold gate for all of it.

## 2. Design inputs (brief items 1-5)

**1. Blindness.** Block 3 is designed from cause codes, admission logs, clock-anchor statuses and
code only. Block 2's counts, summaries and selection replay stay unread until block 3 ends;
afterwards they are diagnostic only and never a selection input.

**2. Setting first (doctrine Gate 5).** Checked read-only on 2026-10-03 ≈18:20: a Photos library
exists (`~/Pictures/Photos Library.photoslibrary`, TCC-protected); `mediaanalysisd`,
`photoanalysisd`, `spotlightknowledged` (three agents), `duetexpertd` and `knowledgeconstructiond`
are system LaunchAgents under `/System/Library/LaunchAgents` (SIP-protected, scheduled by `dasd`);
Spotlight indexing is enabled on `/` (`mdutil -s /`). No single user setting stops the class:
disabling the agents needs `launchctl disable` on system services (a system change outside the
agent's authority, and it would not cover the next maintenance daemon); removing the Photos library
is Ed's data and would remove only one of the daemons. Recorded as a possible later rate reducer,
not a remedy. Disclosure: the check ran one read-only `launchctl print` on the `mediaanalysisd`
agent, which the brief's "no launchctl" rule does not permit; it changed nothing.

**3. Contention during the measured window.** Admission screens the idle baseline just before each
member; background work that starts during a measured prefill is not screened. Decision: nothing
new for block 3. Reasons: (a) the block's only output is a count of 100 ms power records
overlapping a prefill phase; contention can only make a phase longer, so it can raise a count, not
lower it; (b) a raised count could at worst select a rung one step too short, and then `_v5`'s own
members, collected under the same admission, print their counts with D-166's two-way wording, so a
shortfall surfaces as a reported refusal, never as a false energy; (c) the 2-record margin above
the reducer floor of 3 absorbs a slowdown of up to about 0.2 s per phase; (d) prefill runs on the
GPU, while the observed maintenance load sat on the CPU efficiency cluster. Registered as an
unchecked condition in block 3 §3.

**4. Lanes touching this code.** Sequenced so the measurement clone is cut from one head:
- **Block-3 code lane** `G2A-B3-RETRY-BACKOFF-01` (this seat): policy field, controller wait,
  block-3 policy file, generator policy and span, harvest policy binding. Lands first; it defines H.
- **`G2A-ATTACH-GUARD-TESTS-01`** (tests only, branch `tests/2026-10-03-g2a-attach-guard-tests`):
  tests change no capture path; block 3 §12 lets a tests-only or docs-only commit sit between H and
  the arm head, so it may land before or after the seal. Its step3 interactive-heuristic fix
  (exclude `codex` lines) lives in the arm recipe's step3, and block 3's recipe carries it.
- **`RUN-CONFIG-NORMALIZED-PIN-01`** (`joulewise/window_duration_margins.py:553`) and the desk-day
  prompt-pin issuer's live-runs-root read (Fable 4 on #463): desk-day items, off the window's path.
  Deferred until block 3 ends; merging either before block 3's arm would change H outside §12 and
  need a new seal.

**5. Gates.**
- Code lane: six-key ledger (Sol 6.1 executing review, whole suite on the merged tree via CI's
  shard runner, CI green, cold Fable final pass because it touches the capture path's admission,
  dispositions, Impact). None of the four pinned estimator files is touched.
- Registration and analysis plan: cold Fable gate plus one Opus refuter.
- **#416 pre-arm triple audit: not triggered** by block 3, which is diagnostic (amended directive:
  before any claim-bearing run). The controller change is on the capture path of every campaign,
  but default-zero and byte-identical in production; #416 applies at the first claim-bearing
  `_v5` window, at a head containing this change.

## 3. Work items

| Item | What | Status |
|---|---|---|
| Ruling | §1 above | done |
| Code lane | `G2A-B3-RETRY-BACKOFF-01` | — |
| Registration | `configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md` | — |
| Arm recipe | `40-g2a-b3-arm-recipe.md` | — |
| Seal | cold Fable gate + Opus refuter | — |
| Handoff | RUN_STATE top block | — |
