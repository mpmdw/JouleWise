# Run report — 2026-08-12 T5 window session (ten merges, a cold gate, and a 60-minute wall)

> **STATUS: FINAL — closed at Ed's stop order.** Everything from §Session shape
> through §Restart instructions is the drafting-time snapshot (~2026-08-12
> 11:05Z, ~7.6 h into a ~12 h window), corrected in place against primary
> sources; everything between that cutoff and the stop order is in the final
> section **§Tail outcomes**, which supersedes **§Still in flight** and the
> provisional restart list. Every number is verified against a primary source at
> the stated time.

> **Evidence base (successor-assembled, dictated-fills verified):**
> `git log origin/main 4cce475..30ef012` with committer timestamps
> (`2b43de8`, `b670c8f`, `b32220e`, `10578fc`, `14879e4`, `5060189`, `529188a`,
> `ed26a29`, `60d9e42`, `f4aa138`, `7a76a29`, `c3b2c79`, `525cc85`, `521ebeb`,
> `4dffa12`, `30ef012`, `dc3421f`) and the merge-commit bodies of each PR;
> `gh pr list/view` for #131–#139 (state, `mergedAt`, `statusCheckRollup`,
> bodies); `RUN_STATE.md` §“T5 MID-SESSION STATE” (written `ed26a29`, 04:59Z);
> `docs/decision_log.md` D-133/D-134/D-135/D-136 index rows and bodies;
> `docs/process_traces/2026-08-12-mintvocab-coldgate/` (4 files);
> `docs/process_traces/2026-08-12-calexits-mutation-consult/consult.md`;
> `TASK_QUEUE.md` §WO-CRASHMATRIX-RELIABILITY;
> `origin/impl/crashmatrix-exclusive` and `origin/impl/q8-p256-floor-cells`
> branch logs and `.github/workflows/ci.yml` at those heads;
> and the session scratchpad run set
> (`/private/tmp/claude-501/-Users-edr-code-JouleWise/7c344e29-…/scratchpad/`:
> `out-5c-impl{,-r2,-r3}`, `out-5c-lens{A,B,C}`, `out-5c-{doctrine,fixcode,fixdocs}`,
> `mintvocab-{out,fix-out,fix2-out,attest-out}`, `q8-out{,2}`,
> `out/{implB-d135,implB2-d135,reviewB-d135,deltaB-d135,implC-flake,implI-calexits,reviewF-crashmx,reviewG-q8,consult-calexits}`,
> each with its `.status` and `.md`). **Manifest caveat:** three Sol reports —
> `out-5c-lensA`, `out-5c-lensC` and (post-cutoff) `out-5c-delta` — have a
> `.md` and a `.status` but **no `.manifest.jsonl` at all**, so any
> manifest-based census of this session's Sol runs undercounts them by at
> least three, and any effort/rc distribution drawn from manifests covers only
> the manifested set.

## Session shape

T5 is Ed's ~12 h autonomous window, opened ~2026-08-12 03:30Z with the standing
order **“fan out, same goal, presentable paper.”** The session inherited the
T4-late merge queue (six PRs, all audited, all waiting on CI wall-clock) and
executed it, then opened **six** further PRs — **#135, #136, #137, #138, #139,
#140** — landed **four** of them (#136, #137, #139, #138) and left #135 and #140
open at the stop order. (#134 was created 02:57Z but was already listed open in
the T4-late checkpoint, so it belongs to that queue, not to T5's opened tally.)
The scratchpad was created 03:34Z; the first mainline commit landed 03:41Z.
All times in this report are UTC; in the PT convention the council log uses, the
window opens on the evening of **2026-08-11 (~20:35 PT)**.

Topology: magistrate (Fable) plus Opus directors per stream, Sol as execution
workhorse, worktree per stream (`wtD-5c`, `wtE-mintvocab`, `wtF-crashmx`,
`wtG-q8`, `wtB-d135`, `wtC-p2038flake`, `wtH-consult`, `wtI-calexits`, `wt138`,
plus the review/fix siblings — 18 worktree directories at the time of writing).

**D-136 was minted mid-session on an Ed in-thread ruling: the site lane is
retired from all automatic processes** — no session spends tokens on
Lakebed/capsule size, packing, deploy failure or site-chain diagnosis; the site
workflow runs on manual dispatch only and its results never gate anything or
prompt session work. It extends D-135 and the D-101 addendum II.
(Evidence: `docs/decision_log.md` D-136 index row + body §8561; commit `f4aa138`,
06:50:22Z.)

## Product outcomes

### Mainline landings — ten merges

| Order | PR | Branch | Merged (UTC) | Squash commit |
|---|---|---|---|---|
| 1 | #132 | `respec/d124-withdrawn` | 03:41:14Z | `2b43de8` |
| 2 | #133 | `paper/train-g` | 04:04:33Z | `dc3421f` |
| 3 | #131 | `impl/u11-idpin-projection` | 04:38:21Z | `10578fc` |
| 4 | #127 | `impl/calexits-reliability` | 04:53:53Z | `5060189` |
| 5 | #134 | `impl/floor-commonmode-01` | 05:03:26Z | `60d9e42` |
| 6 | #129 | `impl/ci-proof-restructure` | 06:51:39Z | `7a76a29` |
| 7 | #137 | `impl/p2038-clock-phase-flake` | 07:29:20Z | `521ebeb` |
| 8 | #136 | `impl/d135-advisory-budgets` | 07:47:50Z | `4dffa12` |
| 9 | #139 | `impl/calexits-mutation-classifier` | 10:03:12Z | `30ef012` |
| 10 | #138 | `impl/q8-p256-floor-cells` | 14:13:52Z | `27b0c14` |

Merges 1–6 discharge the **T4-late merge queue COMPLETE, 6/6**; merges 7–10 are
PRs opened and landed inside this session. Each carried a D-121 terminal review
at its final head under the D-072 standing self-merge. **Merge 10 (#138) landed
after this report's drafting cutoff** — it is described as open in §Open PRs and
§Still in flight below, and its outcome is in §Tail outcomes.
(Evidence: `gh pr list --state all --json number,mergedAt`; `git log origin/main`
committer timestamps.)

Substance of the T5-originated work:

- **#131 (U11 identity-pin projection)** landed the last unbuilt arm-critical
  tool under the D-131 contract — `joulewise/identity_pins.py` +
  `scripts/project_identity_pins.py`, one shared never-operator-entered
  derivation imported by mint, analysis, runtime collection and the projector,
  exact-key `joulewise.identity_pin_projection_receipt.v1` receipts, the
  canonical `identity_units` pack shape (alpha/beta one unit, gamma four).
  **D-131 flipped PROPOSED → ADOPTED on main at the merge** (`14879e4`,
  04:38:49Z), curing the T4-late addendum's anomaly 1.
- **#134 (FCM-01 / D-133 ALT-D120)** landed the registered common-mode
  estimator with the serialized-registration vocabulary deleted and the
  relocated arithmetic terminally audited. **Incident: the first fix-round push
  (`cbf609f`) claimed the a5-corpus domain-inventory portability guard in its
  message but its tree had lost that hunk in a verification swap-file sequence**
  — the fix round's other three seams landed intact. It was re-applied and the
  committed bytes verified to contain the guard; the integration delta re-audit
  returned ACCEPT with zero findings.
  (Evidence: the `Restore the a5-corpus CI guard the merge commit dropped`
  commit in `60d9e42`'s body; `RUN_STATE.md` T5 block.)
- **#129 (WO-CI-RESTRUCTURE)** turned the monolithic decisive proof into a
  registry-certified 22-leg hosted matrix plus a plan job under the hosted cap,
  with a literally-pinned core-leg certificate (the refuter's delete-core and
  phantom-core mutations both went SURVIVED → KILLED post-fix) and an honest
  retraction of the prior commit's false “monolithic entry point byte-preserved”
  claim (27,395 → 30,301 bytes).
- **#137 (p2038 clock-phase flake)** root-fixed the ~1.6 %/CI-run flake that hit
  #121 and #127, with exact drift arithmetic on the record: repeated float `+0.1`
  advances exactly `209715/2097152 s`, error `-1/10485760 s` per addition,
  `-275/2097152 s = -131130.218505859375 ns` after 1,375 additions; at the
  reproduced `+65 µs` phase this shifted 69 whole-second labels from record index
  690. Records now derive from `first_endpoint_ns + i*100_000_000`; a 70-case
  regression sweeps ten boundaries at 0/±65/±130/±200 µs.
- **#136 (D-135 advisory budgets)** made all conservative site budgets WARN-only,
  leaving the physical 1,048,576-byte Lakebed cap (real validator, CI-only) as
  the sole hard failure, and stopped `build_site.py` trimming decision/council
  bodies. **Gate shape: refuter REJECT round 1** (`reviewB-d135`: blocker R1 —
  the implementation added a raw-Markdown 1,048,576-byte failure gate, i.e. a
  raw-source proxy for the physical cap, contrary to D-135) → **R1 fix**
  (`0bf0a8a`) → **delta re-audit ACCEPT** (`deltaB-d135`: “R1 is fixed; two
  nonblocking wording inconsistencies remain”). Its red site-chain was voided by
  D-136, ruled irrelevant rather than diagnosed.
- **#139 (calexits mutation classifier)** replaced a structurally-impossible
  assertion (the forced-maintenance regression asserted the maintenance
  *parent's* `child_exit` while the pack child dies exit-128/SIGPIPE against an
  already-removed repo) with newline-safe Trace2 polling, exact-argv child
  location, own-SID correlation and a three-way printed classifier that cannot
  go vacuous silently. Design came from a **consult adopted as terminating**
  after the same signature fired three times (on #135/#136/#137). Sol 10-run
  census `RACE_EXERCISED=8 NO_RACE_PRE_WRITE=2 TRACE_INCOMPLETE=0`; lead-verified
  full module 29 tests OK in 309 s.

### The mintvocab cold gate

WO-MINT-ESTIMATOR-VOCAB's F1-seam question went to a cold gate whose **packet
and all three rulings were custodied BEFORE execution** at
`docs/process_traces/2026-08-12-mintvocab-coldgate/` (commit `529188a`,
04:54:31Z; 1,767 lines across `packet.md` 39,698 B, `ruling-1-original.md`
14,790 B, `ruling-2-refuter-brief.md` 31,539 B, `ruling-3-FINAL.md` 19,246 B).

The decisive layer was the **paired Opus contract-lens refuter**, and the final
ruling records the catch in its own words: *“the provisional five and ruling-1's
C1–C10 — would have certified the binding-seam fail-open as closed. The
provisional set never saw it; ruling-1 saw it and prescribed an inert remedy.”*
Both prior condition sets would have certified a live fail-open. The refuter
also proved ruling-1's first remedy **inert**: v2 forces both components onto
one producer `evidence_root_id`, so the pinned binder's absolute-width and
comparative-width refusals are the byte-identical string, and ruling-1's
exact-match-with-comparative-prefix condition closes nothing. The adjudicator
adopted the refutation, rejected the refuter's own “minimum acceptable
alternative” as a standing option, and re-verified every load-bearing refuter
claim by its own execution before adoption.

**FINAL: option A authorized under F1–F12, all merge-gating, none advisory;
options B, C and D barred.** Fix rounds followed; both were killed by
infrastructure (see §Infrastructure discovery), and the tree they left is being
attested by an independent read-only run in flight.

### The §5C readiness-record stream (D-134)

Run 1-of-2 (registry / CLI / schemas / pack slots / Markdown views) was pinned at
head `3a140bb` and put through a **three-lens gauntlet**:

- **Lens A (contract)** found a **LIVE derive-never-enter defect, blocker F1**:
  the generic `_predicate_passes` accepts any fact whose ID matches the
  `predicate_id` and takes its truthiness, so an **operator-attested conclusion
  is accepted where the contract names machine-produced receipt content**.
  **Executed in-process**: an exact-key `LEDGER_RESERVATION` receipt carrying an
  `OPERATOR_ATTESTATION` boolean marks `t0.ledger_reservation` PASS
  (`validator_status=PASS`, `operator_source=OPERATOR_ATTESTATION`) without a
  live `--execute` reservation or `status: reserved`. The escalation from that
  PASS predicate to a **forged GO is the lens's stated reachability, not an
  executed end-to-end result** — the read-only sandbox says so explicitly
  (“Write-dependent end-to-end scenarios were not recreated”). Lens A also found F2
  (Git commit/tree digests checked only as non-empty strings, so uppercase
  digests are admitted) and F3 (reboot invalidation).
- **Reboot-invalidation blocker corroborated by two lenses (A + C):** expiry
  compares only the current monotonic counter against the prior value, so a GO
  receipt issued at ten days' uptime with five minutes remaining survives a
  reboot and can be consumed.
- **Lens C (operator-safety, docs)** reported **seven blockers** plus two clarity
  defects. The fix contract the director wrote carries four of them as blockers,
  one as a must-fix omission and two as clarity defects, but **that triage is not
  a verification pass**: `out-5c-lensC.md` contains exactly one verification
  entry (a clean-tree `git diff --check`) and no per-finding verification or
  4-of-7 tally, and all seven were ultimately carried into the fix round as
  FIX-D1..D7. Among them: **the rewrite dropped “Do not kill a running verdict,
  even if it takes more than two minutes”** — carried inside lens C's F6 table
  row rather than as a standalone blocker, verified present once at base
  `0415f37` and absent at head; killing a running verdict can destroy a
  measurement window.
  Also: ALPHA states a false `NOT_APPLICABLE` rule against its own registry
  (`ALWAYS` 30, `CLOCK_HELPER_ONLY` 4, `SUCCESSOR_ACCEPTANCE_ONLY` 1), and
  ~11 established status-history facts were lost under a heading claiming
  preservation.
- **Lens B (mutation census)** ran 25 mutants and **killed 21**, leaving four
  regression-protection gaps: submodule mode `160000` admitted (the existing test
  covers tracked symlink mode `120000` only), replay against a receipt-bound old
  pack digest, duplicate parsed receipt-slot numbers silently skipped, and
  non-UTF-8 path bytes unprovable on APFS.

Two fix runs (code, docs — deliberately parallel with disjoint WRITE_SCOPEs) and
the run-2 doctrine run are in flight.

**Two magistrate rulings settled during the gauntlet:**
- **Q1 — boot-session identifier code enforcement now**, as a v1 schema amendment
  issued pre-issuance rather than a post-hoc patch.
- **Q2 — keep the defensive code, pin its unreachability by test, and put the
  annotation in the doctrine prose, never in the registry** (the registry's key
  sets are contract-normative and were just certified clean).

### Open PRs

*(State at the 11:05Z drafting cutoff. #138 merged later the same session and
#135 was pushed again; see §Tail outcomes.)*

- **#135 — crash-matrix exclusive CI job** (`impl/crashmatrix-exclusive`,
  stacked on #127). **Refuter REJECT** (`reviewF-crashmx`): the exact command the
  new job adds failed locally with three 600-second per-case timeouts, and the
  timeout rationale overstated headroom. Fix `acd17ab` replaced it with an
  **honest 120-minute ceiling** — “120 min covers the ~89-min hosted standalone;
  exclusivity buys early ordinary-shard signal, not total wall-clock” — and named
  both exclusions in the shard comment. The module's reliability was registered
  as **WO-CRASHMATRIX-RELIABILITY** in `TASK_QUEUE.md` (`525cc85`): bench
  standalone 145.911 s vs hosted shard 5,317.216 s (run 31536564643), a standalone
  hosted attempt exceeded a 60-minute job ceiling, and a loaded-bench refuter run
  hit three internal 600-second ceilings; closure is the module under 15 minutes
  hosted with no internal per-case timeout. Head `15784d2` is a CI re-trigger
  (“no run materialized for `acd17ab`”); **zero checks registered at the time of
  writing**.
- **#138 — Q8 p256 prefill floor cells** (`impl/q8-p256-floor-cells`,
  director-run stream). Both floor packs gain a dedicated p256 prefill domain,
  50 new bundles each, 50→100 science members, 63→117 files; new spec shas
  `e665727a…` (1.5B) / `501d77e9…` (7B). Load-bearing property verified
  independently by the director and the refuter: the floor p256 workload is
  byte-identical to the gamma contrast arm's p256 prefill workload per model and
  hashes to the frozen Q1 prompt artifact's UTF-8 sha `f149dddc…`. **Independent
  Sol xhigh refuter ACCEPT** (`reviewG-q8`) with one benign nit. Head `5214109`
  is the **domain-inventory re-pin fix** (merge current main; re-pin the
  candidate set, +2 p256 comparative cells); CI re-riding.
  **Ed ratification owed: the quiet-window budget roughly doubles — 6.28 h (1.5B)
  and 6.48 h (7B) per pack**, back-derived at 20 % margin from
  `188.4/50 = 3.768` and `194.4/50 = 3.888` margin-inclusive minutes/member ×100.
  Reference cadence unchanged at 3+1+3 = 7 with the midpoint moved to the new
  decode/p256 boundary.
  **Outcome after this cutoff: MERGED 14:13:52Z as `27b0c14`, the session's tenth
  merge; the budget ratification was still owed to Ed at the stop order.**

## Still in flight

**Nothing in this section has an outcome at the drafting cutoff. Do not cite any
of it as a result — the outcomes are in §Tail outcomes, which supersedes this
table.**

| Lane | Artifact | State at 11:05Z |
|---|---|---|
| mintvocab F1–F12 attestation | `mintvocab-attest-out` | RUNNING, started 11:00:14Z; independent read-only attestor, `WRITE_SCOPE: []`, 40-minute cap |
| §5C run-2 doctrine prose | `out-5c-doctrine` | RUNNING, started 10:01:59Z (61.9 min elapsed — already past the subagent kill boundary, so main-session-owned) |
| §5C fix round — code | `out-5c-fixcode` | RUNNING, started 10:58:24Z; xhigh, 8-file WRITE_SCOPE, registry deliberately excluded |
| §5C fix round — docs | `out-5c-fixdocs` | RUNNING, started 10:58:26Z; 3-file WRITE_SCOPE, no code |
| PR #135 | `impl/crashmatrix-exclusive` @ `15784d2` | OPEN; no checks registered yet |
| PR #138 | `impl/q8-p256-floor-cells` @ `5214109` | OPEN; 9 SUCCESS, 2 IN_PROGRESS, **1 FAILURE — `calibration-exits-exclusive (3.11)`** |

Also owed before wrap: the T5 council entry (no `C-057` exists yet), the T5
skill-usage rows, `RUN_STATE.md` refresh (see anomalies), and finalization of
this report.

## Verification evidence — claim ledger

| Claim | Result | Primary evidence |
|---|---|---|
| Ten PRs merged this session | PASS: #132/#133/#131/#127/#134/#129/#137/#136/#139/#138, 03:41:14Z → 14:13:52Z (#138 after the drafting cutoff) | `gh pr list --state all`; `git log origin/main` |
| Six PRs opened this session | PASS: #135, #136, #137, #138, #139, #140 (all created 2026-08-12 UTC); four merged, two open at stop | `gh pr list --state all --json number,createdAt` |
| T4-late queue complete | PASS: 6/6 (#132, #131, #127, #133, #134, #129) | T4-late addendum §Merge queue; the six squash commits |
| D-131 ratified on main | PASS: PROPOSED → ADOPTED at the #131 merge | `14879e4` (04:38:49Z), 28 s after `10578fc` |
| D-136 minted | PASS: index row + body; site workflow manual-dispatch only | `docs/decision_log.md` D-136; `f4aa138` |
| #134 lost guard hunk | CONFIRMED and CURED: `cbf609f`'s message claimed the guard, its tree lost it; re-applied, committed bytes verified | `Restore the a5-corpus CI guard…` commit in `60d9e42` |
| #136 gate shape | PASS: refuter REJECT (R1 blocker) → fix `0bf0a8a` → delta ACCEPT | `reviewB-d135.md`; `deltaB-d135.md` |
| #137 drift arithmetic | PASS, exact: `-275/2097152 s = -131130.218505859375 ns` over 1,375 additions; 69 wrong labels at +65 µs; lead-verified 130 tests OK | `521ebeb` message; `implC-flake.md` |
| #139 design provenance | PASS: consult custodied pre-implementation; 10-run census 8/2/0; module 29 OK in 309 s | `docs/process_traces/2026-08-12-calexits-mutation-consult/consult.md`; `c3b2c79`; `30ef012` |
| mintvocab cold gate | PASS: option A authorized under F1–F12, all merge-gating; options B/C/D barred | `ruling-3-FINAL.md` PART C + FINAL |
| Refuter's unique catch | CONFIRMED: “the provisional five and ruling-1's C1–C10 — would have certified the binding-seam fail-open as closed” | `ruling-3-FINAL.md` §PART A closing |
| §5C lens A live defect | CONFIRMED, executed to a PASS predicate: `validate_evidence_receipt` prints `PASS OPERATOR_ATTESTATION True` for a hand-authored boolean. The onward **forged GO is asserted-reachable, NOT executed** (read-only sandbox; write-dependent end-to-end not recreated) | `out-5c-lensA.md` F1/V2; the repro in `prompt-5c-fixcode.md` FIX-1 |
| §5C lens B census | PASS: 25 mutants, 21 killed, 4 gaps (F1 `160000`, F2 stale pack digest, F3 duplicate slot, F4 non-UTF-8 on APFS) | `out-5c-lensB.md` census table |
| §5C lens C triage | 7 blockers reported; the fix contract re-tiers them as 4 blockers + 1 must-fix + 2 clarity. **NOT a verification pass**: lens C holds one verification entry total (clean-tree `git diff --check`), no per-finding verification, no 4-of-7 tally; all seven were fixed as FIX-D1..D7 | `out-5c-lensC.md`; `prompt-5c-fixdocs.md` preamble + FIX-D1..D3 |
| Dropped safety instruction | CONFIRMED: “Do not kill a running verdict…” present once at base `0415f37`, absent at head | `out-5c-lensC.md` F6; `prompt-5c-fixdocs.md` FIX-D2 |
| §5C run-1 pin | PASS: `head_start == head_end == 3a140bb` in all three lens envelopes | `out-5c-lens{A,B,C}.md` `workspace` blocks |
| #135 refuter | REJECT: exact added command failed locally, three 600 s timeouts; ceiling rationale overstated | `reviewF-crashmx.md` |
| #135 remedy | 120-min ceiling + WO-CRASHMATRIX-RELIABILITY registered | `acd17ab`; `TASK_QUEUE.md` §WO-CRASHMATRIX-RELIABILITY; `525cc85` |
| #138 refuter | ACCEPT, one nit (literal hygiene grep returns five benign matches) | `reviewG-q8.md` |
| #138 budget | 6.28 h / 6.48 h per pack, 20 % margin; cadence unchanged | `q8-out2.md` §RATIFICATION-REQUIRED; PR #138 body |
| Subagent shell kill boundary | CONFIRMED, 4/4 at 59.8–60.0 min | run-key start times vs `.log` mtimes (table below) |
| Attestation independence | PASS by construction: `WRITE_SCOPE: []`, NEEDS_SCOPE-and-stop instruction, no full-suite permission | `mintvocab-attest-prompt.md` §1, §3 |
| This report | Docs-only draft; no suite run; nothing committed | working tree |

## Infrastructure discovery — the 60-minute wall

**Subagent-owned background shells are killed at ~58–60 minutes; main-session
background shells are not.** Four occurrences this session, all with the same
signature: the process dies mid-turn, no `task_complete`, no envelope, `.status`
frozen at `RUNNING`, and the work recoverable only as a partial patch.

| Run | Start (run_key) | Last log write | Elapsed | Status file |
|---|---|---|---|---|
| `out-5c-impl` (§5C run 1) | 04:07:56Z | 05:07:46Z | **59.8 min** | RUNNING |
| `out-5c-impl-r2` (§5C run 1 retry) | 05:10:44Z | 06:10:35Z | **59.9 min** | RUNNING |
| `mintvocab-fix-out` (fix round 1) | 05:54:57Z | 06:54:47Z | **59.8 min** | RUNNING |
| `mintvocab-fix2-out` (fix round 2) | 06:58:53Z | 07:58:52Z | **60.0 min** | RUNNING |

Against the main-session control group:

| Run | Start | End | Elapsed | Status |
|---|---|---|---|---|
| `mintvocab-out` | 04:05:10Z | 05:48:17Z | **103.1 min** | OK, envelope complete |
| `out-5c-impl-r3` | 08:04:09Z | 09:25:40Z | **81.5 min** | OK, envelope complete |
| `out-5c-doctrine` | 10:01:59Z | in flight | 61.9 min+ | RUNNING (alive) |

**Standing route adjustment adopted:** any Sol launch expected to exceed
~45 minutes runs from the magistrate's shell; directors keep contract authoring,
monitoring and triage (and hold themselves to a ~20-minute envelope). **This
route ruling is magistrate-reported; no artifact in the repo or the scratchpad
records it [UNVERIFIED-BY-MECHANIC]** — the four 59.8–60.0-minute kills that
motivate it are fully verified. The consequence is visible in the record — the mintvocab
tree reaching the attestation run *had never been attested by any envelope*,
because both runs that produced it died before their acceptance proofs. The
attestation prompt states this to the attestor verbatim: *“two consecutive Sol
runs that were both killed by infrastructure at ~59 minutes… No envelope has
ever attested this work.”*
(Evidence: the two tables above, derived from `run_key` timestamps in each
`.manifest.jsonl` first record and `.log` mtimes; `mintvocab-fix-PARTIAL-killed.patch`
62,126 B and `mintvocab-fix2-PARTIAL-killed.patch` 91,520 B;
`mintvocab-attest-prompt.md` §2.)

## Process notes — Sol tooling (for the skill log)

1. **The piped-suite near-miss.** The magistrate launched suite gates twice with
   `| tail -3` — the standing rule is *never gate on a piped test*. Caught before
   either verdict was consumed and both redone unpiped. The rule exists because a
   pipe can truncate at a buffer boundary and return rc 0 (the T3 site-renderer
   64 KiB truncation is the same family). **Note: this item is magistrate-reported;
   no launch artifact in the scratchpad corroborates it.**
2. **The read-only-sandbox spuriously-red attestation trap.** A read-only
   sandbox denies temp dirs, so a suite-executing review dies mid-turn or reports
   environment failures that read as defects in the code under review. The
   mintvocab director caught this **pre-flight** and shaped the attestation
   contract around it: `WRITE_SCOPE: []` with an explicit *“if you believe you
   cannot complete the attestation without writing, emit NEEDS_SCOPE and stop”*,
   a 40-minute cap, focused-tests-only, and an explicit prohibition on running
   the canonical suite (which the magistrate owns). (Evidence:
   `mintvocab-attest-prompt.md` lines 18–29, 84–95, 436–438.)
3. **`codex-run-v3`'s resume path is not resumable from `NEEDS_SCOPE` or
   `ACCEPTANCE_FAILED` states.** Two occurrences this session; fresh continuation
   runs were used instead of resumes. (Evidence: `q8-out.status`
   `semantic_status=blocked / completion=none`, followed by the independent
   `q8-out2` rather than a resume; the §5C run-1 continuation `out-5c-impl-r3`.)
4. **Envelope-parse `unknown` on review-genre reports carrying a
   `verdict.findings[]` shape** — the report body is complete and correct, the
   decision is legible, but the wrapper records
   `semantic_status=unknown / completion=unknown / run_status=ACCEPTANCE_FAILED`.
   Cosmetic; three occurrences: `out-5c-lensC` (46 B status),
   `reviewG-q8` and `deltaB-d135` (both ACCEPT decisions). Not all review runs
   hit it — `out-5c-lensA`, `out-5c-lensB`, `reviewB-d135` and `reviewF-crashmx`
   parsed cleanly, so the trigger is a specific field shape, not the genre.

## Delegation calibration

| Stream / run | Mechanism / tier | Outcome | Evidence |
|---|---|---|---|
| Merge queue execution (6 PRs) | Magistrate, D-121 terminal review each | 6/6 landed 03:41Z → 06:51Z | the six squash commits |
| mintvocab F1 seam | Cold Fable adjudicator + paired Opus contract-lens refuter, packet mechanically assembled | Ruling-1 withdrawn; F1–F12 replaces both prior sets; live fail-open + inert remedy caught | `ruling-1-original.md`; `ruling-2-refuter-brief.md`; `ruling-3-FINAL.md` |
| mintvocab implementation | Sol under enforced WRITE_SCOPE, subagent-launched | Clean envelope run 1 (103.1 min); fix rounds 1+2 both infrastructure-killed | `mintvocab-out.status`; the two PARTIAL patches |
| mintvocab attestation | Independent Sol, `WRITE_SCOPE: []`, 40-min cap | IN FLIGHT | `mintvocab-attest-out.status` |
| §5C run 1 | Sol xhigh implementation, three attempts | r1/r2 killed at 60 min; r3 OK at 81.5 min, pinned `3a140bb` | `out-5c-impl{,-r2,-r3}.status` |
| §5C gauntlet | Three distinct lenses (contract / mutation / operator-safety docs) | 1 live derive-never-enter blocker (executed to a PASS predicate; GO reachability asserted, not executed), 1 two-lens-corroborated blocker, 7 doc blockers (re-tiered by the director as 4 + 1 must-fix + 2 clarity), 4 mutation gaps | `out-5c-lens{A,B,C}.md` |
| §5C fix rounds | Two parallel Sol runs, disjoint WRITE_SCOPEs (code vs the three doc pages), registry excluded | IN FLIGHT | `prompt-5c-fix{code,docs}.md`; `.status` |
| D-135 implementation | Sol two-part under WRITE_SCOPE (part-2 scope extension approved after a correct NEEDS_SCOPE) → refuter → fix → delta | REJECT → ACCEPT, merged #136 | `implB-d135.md`; `implB2-d135.md`; `reviewB-d135.md`; `deltaB-d135.md` |
| p2038 flake | Sol implementation, clean envelope | Implemented + 70-phase regression; merged #137 | `implC-flake.md` |
| calexits mutation | Sol root-cause consult (custodied) → Sol implementation → lead verification | Terminating classifier design; merged #139 | `consult-calexits.md`; `implI-calexits.md` |
| Q8 p256 cells | Opus director stream + Sol rounds + independent Sol xhigh refuter | Round-1 correct early return on an impossible acceptance proof → ratified proof repair → round 2 → ACCEPT | `q8-out.md`; `q8-out2.md`; `reviewG-q8.md` |
| Crash-matrix job | Sol implementation + Sol refuter | REJECT → honest ceiling + work order | `reviewF-crashmx.md`; `acd17ab` |

## Ed-owed

Carried from `RUN_STATE.md` plus new this session:

1. **Gamma-arm premise shift (flagged, not decided).** D-133's default — freeze
   doesn't wait, the tighter floor banks for ICPE — was priced on freeze
   imminence. The freeze now waits on §5C + Q8 regardless (days, not hours), while
   **D-133 cl.4's re-spec-back conditional may fire mechanically on its own ruled
   terms**: it requires ALT-D120 + the full fresh delta + WO-MINT-ESTIMATOR-VOCAB
   all landing pre-freeze-wave. The first two landed with #134; **mintvocab is one
   gate from landing.** If it fires, packs freeze at 1.869502 J instead of
   8.611855 J and the funded p256 arm likely publishes instead of reading
   not-resolvable. No reinterpretation is being made — the session is simply
   executing fast enough that the ruled conditional may fire. PR #133's merged
   `CONDITIONAL-INSERT-TIGHTER-FLOOR` block makes the paper swap mechanical either
   way. (Evidence: D-133 index row cl.4; `RUN_STATE.md` T5 ED-OWED; `dc3421f`.)
2. **Q8 quiet-window budget ratification** — 6.28 h (1.5B) / 6.48 h (7B) per pack;
   p256 cells are REAL new bundles (50→100 members/pack), not a rider like p128.
3. **Live sudo/powermetrics checklist** before relying on #127's production
   sampler commit at arm time; the checklist is carried in the module docstring
   and the production commit's merge was held on it.
4. **§5A taps** on the quiet night.
5. Standing: the extension-axes roadmap review.

## Custody trace

| Trace | Path | Landed |
|---|---|---|
| mintvocab cold gate (packet + 3 rulings, BEFORE execution) | `docs/process_traces/2026-08-12-mintvocab-coldgate/` | `529188a`, 04:54:31Z |
| calexits mutation consult (same-signature ×3 escalation) | `docs/process_traces/2026-08-12-calexits-mutation-consult/consult.md` | `c3b2c79`, 06:59:44Z |

Two further bookkeeping landings: the **T4-late run-report addendum**
(`b670c8f`, 04:08:48Z — six record anomalies surfaced, including D-131's
branch-only PROPOSED status and the C-056 span boundary) and the **control-doc
staleness batch** (`b32220e`, 04:25:34Z) carrying the **freeze-lane ordering
correction**: the T4-late lane “freeze → U11 projections → arm packet” was
inverted, because D-134's §5C registry/receipts and the Q8 cells are pack
CONTENT. True order: **#134 + mintvocab (if in time) → §5C run 1+2 → Q8 cells →
regenerate → FREEZE → U11 freeze projections → arm packet.** Both control docs
were re-cut and freeze-plan WOs 1–4 closed.
(Evidence: `RUN_STATE.md` §“Freeze-lane ORDER CORRECTION”; `b32220e`.)

## Source anomalies and UNVERIFIED items

1. **`RUN_STATE.md` is stale relative to main.** Its T5 block was written at
   `ed26a29` (04:59Z) and still says “#134 (one CI check pending) … then #129
   (pre-reviewed, merges last).” Both merged, as did #137, #136 and #139. Anyone
   restarting from `RUN_STATE.md` alone will under-count the session by five
   merges. Refresh is owed before wrap. **Discharged at the stop order:** the
   T5 FINAL CHECKPOINT block (commit `72b8427`) records all ten merges — see
   §Tail outcomes.
2. **Dictated merge ordering had #136 before #137; the record is the reverse** —
   #137 merged 07:29:20Z, #136 07:47:50Z. Content is unaffected.
3. **#138 carried a red check at the cutoff** — `calibration-exits-exclusive
   (3.11)` FAILURE, alongside 9 SUCCESS and 2 IN_PROGRESS. Described in dictation
   as simply “CI re-riding.” The failure is in the module lineage this session
   fixed twice (#127, #139); whether it was the known flake or a real regression
   on the re-pin head was **UNVERIFIED** at the cutoff and had to be triaged
   before merge. **Resolved after the cutoff: #138 merged 14:13:52Z** — see
   §Tail outcomes.
4. **#135 has zero checks registered at head `15784d2`.** Consistent with the
   head commit's own message (“CI trigger — no run materialized for `acd17ab`”),
   but “CI re-riding” is an inference from the commit message, not an observed
   run.
5. **#135's PR body is stale against its head.** The body still describes “a
   dedicated 60-min-ceiling job” and “bounded by the existing 30-min calexits
   ceiling”; `acd17ab` moved the ceiling to 120 min after the refuter. The body
   should be corrected before merge.
6. **The Q8 round-1 early return is labelled two ways.** Its envelope records
   `status: blocked / completion: none` (“stopped before edits because P3 byte
   identity conflicts with the required root order-manifest expansion”), while PR
   #138's body calls it a `NEEDS_RULING` early return. Both describe the same
   correct refusal; the wrapper state was `blocked`, not `needs_ruling`.
7. **Lens C's blocker count is not the director's, and the difference is not a
   verification.** Lens C reported seven operator-safety blockers; the fix
   contract carries four blockers, one must-fix omission and two clarity defects.
   The reconciliation (which three were re-tiered and why) is **not recorded in
   any custodied artifact** — it exists only as the difference between
   `out-5c-lensC.md` and `prompt-5c-fixdocs.md`. Nothing anywhere supports a
   “4 of 7 verified” reading: lens C contains a single verification entry (a
   clean-tree `git diff --check`) and no per-finding verification pass. All seven
   were fixed downstream as FIX-D1..D7.
8. **The piped-suite near-miss has no artifact.** See process note 1. It is
   recorded on the magistrate's report alone.
9. **No council entry and no skill-usage rows exist for T5.** The council log
   ends at C-056 (T4-late) and `skill-usage-log.md`'s only 2026-08-12 row belongs
   to the T4-late block.
10. **Nothing measured this session.** No quiet-window collection, no arming, no
    claim publication; the machine ran agent sessions throughout, which forbids
    `[QUIET-MAC]` measurement by contract.
11. **Three Sol reports have no manifest.** `out-5c-lensA`, `out-5c-lensC` and
    `out-5c-delta` carry a `.md` and a `.status` but no `*.manifest.jsonl`, so
    any manifest-derived run count, effort split or rc distribution for T5
    **undercounts the session's Sol runs by at least three** and must carry that
    caveat.
12. **The stop-order wall-clock label does not match the commit record.**
    `RUN_STATE.md`'s header dates the stop order “~17:45Z”, but the final
    checkpoint commit `72b8427` is timestamped **2026-08-12T15:01:29Z
    (08:01:29 PT)**, and #138's merge — the last product event of the session —
    is 14:13:52Z. This report uses the commit timestamps; the “~17:45Z” label is
    **[UNVERIFIED-BY-MECHANIC]** and appears to be off by ~2 h 45 m.

## Restart instructions (provisional, as of the 11:05Z cutoff — SUPERSEDED by §Tail outcomes)

1. **Harvest the four in-flight runs from disk** (`mintvocab-attest-out`,
   `out-5c-doctrine`, `out-5c-fixcode`, `out-5c-fixdocs`) — status files, then
   `.md` envelopes. Do not relaunch a killed run verbatim; check the elapsed time
   against the 60-minute boundary first.
2. **mintvocab merges only on the attestation.** F1–F12 are all merge-gating,
   none advisory, and the tree has never been attested by an envelope. If the
   attestor returns findings, they are the magistrate's to dispose of — the
   attestor is forbidden to repair.
3. **§5C needs a delta re-audit of both fix rounds** before run-2 doctrine can be
   consumed; fix rounds introduce defects (proven twice in this project).
4. **Triage #138's red 3.11 exclusive job** before merge, then merge #138 BEFORE
   `impl/5c-readiness-records` (magistrate ruling); §5C rebases with mandatory
   regeneration — source-hunk merge + regenerate, never hand-merge.
5. **#135** wants its body corrected to the 120-minute ceiling and a CI run that
   actually materializes.
6. **Freeze lane order** is `#134 + mintvocab → §5C 1+2 → Q8 → regenerate →
   FREEZE → U11 projections → arm packet`. Do not re-invert it.

## Tail outcomes (drafting cutoff → Ed stop order)

Everything below happened after the 11:05Z drafting cutoff and at or before Ed's
stop order. It supersedes §Still in flight and the provisional restart list.
Facts here are verified against the **T5 FINAL CHECKPOINT** block of
`RUN_STATE.md` (lines 15–104, written at the stop order) and, where a hash or a
time is given, against the commit record. Nothing that happened *after* the stop
order is included.

**#138 merged — the session's tenth merge.** `impl/q8-p256-floor-cells` landed
at **14:13:52Z as `27b0c14`**, carrying the dedicated p256 prefill floor cells
into both D-117 floor packs. The packs are now **100 science members per pack**
(50 → 100). **Ed's quiet-window budget ratification was still owed at the stop
order** and is unchanged in substance: ~6.28 h (1.5B) / ~6.48 h (7B) per pack at
20 % margin, REAL new bundles rather than a p128-style rider.

**#140 (WO-MINT-ESTIMATOR-VOCAB) reached gate-complete, still open.** The cold
gate's **F1–F12 are all met** — custody at
`docs/process_traces/2026-08-12-mintvocab-coldgate/` (packet + three rulings) —
with an **independent attestation plus a focused re-attestation**, and the
magistrate's canonical suites green at **`a15fe02`** outside the registered
WO-CRASHMATRIX class (whose failing modules are byte-identical to main). CI at
the stop order: **10 checks passed, 2 pending**. The successor's path is
confirm-green → D-121 comment → merge; **on that merge D-133 cl.4's re-spec-back
conditional fires on its own ruled terms** (ALT-D120 + terminal delta + mintvocab
all landed pre-freeze-wave), which is why the gamma-arm call below is now live
rather than hypothetical.

**§5C readiness stream fully verified, awaiting a PR.**
`integration/5c-readiness` is pushed at **`5a80e39`**, with the three branches
merged in the ruled order (`fix/5c-code` `4ff4072` → `impl/5c-readiness-records`
`46eb6a9` → `fix/5c-docs` `fc4095f`). The magistrate's own Q2 suite at that head:
**3,031 OK, rc=0, zero failures.** **LC-1 was applied and verified** — the
branch's own newly-minted `D-136` renumbered to **D-137**, because main had
minted a *different* D-136 (the site-lane retirement, `f4aa138`) after this
stream's base at `0415f37`. The integration tree is the only place that defect
was visible, and the commit states the hazard for the record: *“a branch cannot
mint a globally unique identifier from a stale base, and no in-branch check can
catch it — the doctrine session's ‘exactly one D-136’ proof was correct on its
branch and still wrong at the union.”* At the stop order the stream was awaiting
rebase onto post-#140 main (re-running the LC-1 number check) and then a PR.

**#135 is content-done but its CI would not trigger.** After the refuter fix the
crash-matrix job's content was settled (120-minute honest ceiling,
WO-CRASHMATRIX-RELIABILITY registered); what failed repeatedly was the *trigger*
— **three pushes plus a close/reopen produced no run**. Head **`66f6129`** (“CI
trigger — no run materialized for `acd17ab`”, 14:09:13Z) was force-pushed at the
stop order as a further retrigger attempt. Low stakes; it merges when CI finally
runs green under D-121.

**Stop state.** The final checkpoint was committed and pushed as **`72b8427`**
(“T5 FINAL CHECKPOINT (Ed stop order): /clear-safe — a fresh session starts at
RUN_STATE”, 15:01:29Z). At that point **zero live Sol runs, monitors or watchers
remained** — all runs harvested, all load-bearing work pushed, two bookkeeping
drafts (this report and the C-057 council draft) left on local disk.

**Ed-owed at the stop order** (superseding §Ed-owed's list only in status, not in
substance):

1. **The gamma-arm call, now LIVE with its premise updated** — see #140 above.
2. **Q8 quiet-window budget ratification** — ~6.28 h (1.5B) / ~6.48 h (7B) per
   pack at 20 % margin; REAL new bundles, not a rider.
3. **Live sudo/powermetrics checklist** before relying on #127's production
   sampler commit at arm time.
4. **§5A taps** on the quiet night.

**Sol/infra lessons recorded at the checkpoint** (for the skill log, in the
checkpoint's own terms):

- Subagent-shell background jobs are killed at **~60 min** (4 timed occurrences
  this session); runs expected to exceed ~45 min launch from the lead shell; a
  `.status` of `RUNNING` is **not** evidence of liveness.
- **`NEEDS_SCOPE` early returns are not resumable** — a fresh run re-spends the
  time already burned.
- **Scope diffs anchor to the merge-base**, never to live `origin/main`.
- A **read-only sandbox makes attestations spuriously red**; use workspace-write
  with an empty write-scope instead.
- **Never gate on piped suite output** (near-missed twice this session, caught
  both times).
- **Never assert git state without checking it in the same turn.**
- **A branch cannot mint a globally-unique ID from a stale base** — the
  integration-tree union check is mandatory.
