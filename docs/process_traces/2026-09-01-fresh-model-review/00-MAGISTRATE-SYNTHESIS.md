# Fresh-model repository review — magistrate synthesis and disposition

Date: 2026-09-01. Magistrate: Claude Fable 5 (new lead model, first session in
this repository). Seats: terra (code + tests, `01-terra-code-tests.md`), luna
(process, `02-luna-process.md`, pending at synthesis time — addendum below when
it lands), Sol (paper + research questions, `03-sol-paper-rq.md`), Opus 5
(cross-cutting, `04-opus-crosscutting.md`). Three model families, blind to each
other, same common brief (scratchpad `common-brief.md`, lens sheets per seat).

Ed's direction received during the review, binding on this disposition:
"live state of code is ground truth, paper and research questions are the goal
… don't stick too hard to deadlines by possibly stale docs that may have
drifted. those are meant to be context." And: "just do smart work and progress
the paper as you think best"; "fanning out is allowed, workflows, etc."

## 1. Verdict

All three delivered seats answer the headline question the same way:
**yes, conditionally — the repository can produce a defensible capstone paper.**
The condition differs by lens and the differences are the useful content:

- terra: the physics/evidence path is unusually defensible; the code must now be
  treated as a *frozen instrument* — no refactor, no new process framework
  before the transaction. One real inconsistency: the `_v5` common-mode replay
  accepts up to 20 blocks while the canonical exact-corner cap is 16.
- Sol: the answer set (attribution dominance, one fixed-pair demonstration, the
  37/50 negative) is the right paper; the headline is defensible *inside the
  registered envelopes* but not as an unconditional transfer claim until the
  inserted-gap fiducial runs; the Student-t inference on ten blocks from one
  session is the second-weakest sentence in the draft.
- Opus: the method sections are already written to a replication standard, so
  what remains is filling numbers into a finished argument — but the two pages
  an advisor is told to read first contradict the live campaign, and the
  process "has no stopping rule" (31 idle machine-days against 1,111 commits;
  the month nonetheless bought D-165 and D-166, both of which would have sunk
  the paper).

The magistrate verified each load-bearing claim against the code before
accepting it (see §4). Nothing any seat asserted about the code was wrong.

## 2. Consensus findings (two or more seats, independently)

| # | Finding | Seats | Verified by magistrate |
|---|---|---|---|
| C1 | The kernel / `WINDOW-COUNCIL-GATE` / `[QUIET-MAC]` rows describe the retired Qwen2.5 `_v3` packs and a NOT-READY gate (08-15, 08-20) that was never cleared; the live campaign is `_v5` under D-162/D-164–166. `gen_state.py --check` proves only that text matches the stale kernel. | Sol F2, Opus #3, terra (implicit) | Yes — `state_kernel.json` Q2–Q4, A67–A69; no `_v5` rows. |
| C2 | The frozen draft is `_v4`/Qwen2.5 throughout (falsifier at lines 21/185/356, fixed-p256 at 198/260, §6 retired by D-166); mechanical substitution of 81 governed blocks is the wrong instrument — write `_v5` results sections fresh from a survival map. | Sol F3, Opus #1 | Yes — `_v4` ×8, `_v5` ×0 in `draft-v1.md`; round-7 parked at 59/81 (`12-PARK-DISPOSITION.md`). |
| C3 | The dominance ratio R / R_cm exists as a registration and a predicate in the pack generator + its test, and in fill-registry rows; **nothing in `joulewise/` computes it from real floor artifacts at close-out**. "Who computes R, and when" is unanswered. | Sol F5, Opus #4, terra open-q 2 | Yes — grep: `dominance_ratio` only in `generate_configs.py` and `tests/test_d117_contrast_v5_pack.py`. |
| C4 | The transfer fiducial (D-163, TRANSFER-FIDUCIAL-01, PR #239) should gate any unconditional headline; if it cannot run, the title/conclusion must be conditional. | Sol F1, Opus (seams), all three blind PC reviewers on 08-28 | Yes — `wt-fiducial` branch exists at b1bf81ae; runnability post-campaign not yet confirmed. |
| C5 | Dependence of the ten A/B/B/A blocks is undefended; "95/95" assumes 59 independent pulse draws. | Sol F4, Opus (seams) | Yes — `draft-v1.md:260-264`, `:642-652`; `excursion-decomposition.md:133-140` says so itself. |
| C6 | Advisor-facing pages (README "Now", PROJECT_STATUS, RUN_STATE intake) contradicted the live campaign. | Opus #2, Sol F2 | README + RUN_STATE T29 refreshed this session (commit 3b3839c0); PROJECT_STATUS still owed. |

Single-seat findings the magistrate accepts: terra F1 (20-vs-16 cap), terra F2
(one-page `_v5` artifact-flow run-sheet map), Sol F6 (rename C5-1.1 as a
fixed-pair demonstration in reader-facing prose), Sol F7 (auditability
packaging, post-campaign, time permitting), Opus #6 (branch protection — Ed's
call), Opus #7 (operating model into a tracked file; rotate `RUN_STATE.md`).

Single-seat findings the magistrate declines for this submission: terra F3/F4
(CI timing map, D-161 prune waves — post-campaign, correctly self-labelled);
Sol F6's inverse (no new measurement question — agreed, and declined *as a
change* because the coverage map already fixes the answer set).

## 3. Disposition — what was launched today

Ed's direction resolves the one seat disagreement (Sol F2 wanted a
"lead-issued readiness card" reconciling kernel, queue, gate, G2-b supply;
Opus #3 wanted the kernel reconciled "with the night that is about to happen").
Both are the same work; the magistrate's ruling is D-167 (below), and the
kernel is reconciled TO live state rather than live state being made to satisfy
a 13-seat sitting that the charter would otherwise demand.

Streams launched 2026-09-01 (each in its own worktree with an exhaustive
`WRITE_SCOPE`; reports land in this directory as `05`–`09`):

| Stream | Seat | Delivers | Answers |
|---|---|---|---|
| 05 kernel reconcile + D-167 | Sol high | `state_kernel.json` `_v5` rows (G2-a evening → desk day → G2-b/transaction → nightly G3 → fiducial → `_v6`), Q2–Q4 + A67–A69 retired, `WINDOW-COUNCIL-GATE` retired by supersession, D-167 index+body, charter banner, regenerated `RUN_STATE`/`TASK_QUEUE` | C1, C6 |
| 06 ratio close-out scout | Sol xhigh, read-only | Artifact→function→artifact chain from a real `_v5` collection to R per component/cell, R_cm, branch A/B, renderer fills; the one design decision the magistrate must make; Sol-day estimate | C3 |
| 07 dependence sensitivity | terra xhigh | Pre-registered `docs/paper/round7/dependence-sensitivity.md` (unit/DoF table, AR(1) and effective-n sensitivity, the disagreement sentence, 95/95 relabel, worked example) + `scripts/dependence_sensitivity.py` + tests | C5 |
| 08 survival map + `_v5` skeleton | Sol xhigh, writer | `docs/paper/round7/survival-map.md` (KEEP / KEEP-WITH-EDITS / REWRITE per section, known frozen-draft defects) + `docs/paper/draft-v2-skeleton.md` (KEEP text carried, REWRITE sections as ordered build notes with `[FILL:row]` slots, both ratio branches, Methods passage that builds R before first use) | C2, Sol F5/F6 |
| 09 small fixes | terra high | Cap aligned to `MAX_EXACT_ADMISSIBLE_CORNER_N` + 17-block refusal test; registry row `RQ-ATTRIBUTION-DOMINANCE` → `_v5`/ratio; C5-1.1 row names the Qwen3 pair; fill-checklist DG-071/075 status; M0 `skipped=10` de-numbered | terra F1, Sol anomalies 1–2, terra anomaly 1 |

Gate shape for the four write streams: lead diff review → refuter (Sol xhigh,
contract lens) on 07 and 08 because they are claim-bearing; 05 and 09 get a
lead review plus CI; delta re-audit on any fix round; separate PRs; the lead
runs the live verification (`gen_state.py --check`, the targeted unittest
modules, `paper_terms_lint.py` on the new sheets) before merge.

Not launched, deliberately: the ratio close-out *implementation* waits for the
scout's design decision (stream 06); the advisor-facing PROJECT_STATUS rewrite
and the one-page artifact-flow map wait for 05 so they can cite the reconciled
kernel; the `_v5` results prose waits for data by design.

## 4. Magistrate verification log

- `dominance_criterion_registration` / `dominance_ratio` /
  `replay_common_mode_dominance`: `configs/campaigns/d117_contrast_v5/generate_configs.py:514, 591, 683`; the 20-block cap at `:689`; canonical 16 at `joulewise/detection_floor.py:110`. Confirmed.
- No consumer of the ratio in `joulewise/` or `scripts/render_results_fills.py` (its `derive_numeric` carries fixed pre-`_v5` vocabulary). Confirmed.
- Kernel: `WINDOW-COUNCIL-GATE` blocks all quiet-mac rows; readiness sittings
  08-15 and 08-20 both NOT-READY (13/13); A67–A69 READY, unstarted; no `_v5`
  window row. Confirmed.
- Registry row `docs/research_question_registry.md:82` still `_v4`/any-exceedance. Confirmed.
- Frozen draft line 256 vs ratification note on record tiling. Confirmed.
- Fresh-review seats ran the full unittest suite under the read-only Codex
  sandbox and saw ~1,787 errors: no writable temp dir. Environment artifact,
  not repo health; targeted modules pass. Recorded so nobody re-diagnoses it.

## 5. Where the magistrate disagrees with a seat

- Opus #7 proposes rotating `RUN_STATE.md` and tracking the operating model.
  Agreed in principle, deferred: the operating model changed today (Ed's
  direction) and should be written down once the wave lands, not before.
- Sol's F2 "do not begin G2-b until all resolve to the same Qwen3 pack" is
  right as engineering and is implemented by D-167's dependency chain; the
  magistrate does not adopt its framing of a *new* readiness instrument (a
  "readiness card") — that is the drift pattern the review itself diagnosed.
- terra's "frozen instrument" is adopted with one exception: the cap alignment
  (its own F1) is a pre-campaign code change, justified because the current
  10-block design is inside both caps and the test makes the change
  self-evidencing.

## 6. Open questions carried to Ed (report-only; none block the wave)

1. Branch protection on `main` (Opus #6) — a GitHub setting only Ed can flip.
2. Whether the advisor version needs a public, independently re-reducible
   evidence archive (Sol F7 / open-q 4) — decides whether FLOOR-BIND-01 is a
   release task or a limitations paragraph.
3. Machine windows: G2-a evening → desk day → G2-b/transaction, then the
   fiducial night. The kernel rows from stream 05 will state the order; the
   dates are Ed's.

## Addendum — luna (process seat, `02-luna-process.md`, landed 13:14)

Verdict: the same conditional yes, with the sharpest statement of the C1
danger of any seat — the kernel "is fail-closed enough to stop a silent wrong
run, but unclear enough to cause delay or invite a manual bypass." Its F1
(reconcile the live work selector before G2-a, then require one independent
review of the resulting state) is exactly stream 05 / D-167, whose PR #250
received that review (Sol implementation in two sessions + lead verification).
Open question 1 (is `WINDOW-COUNCIL-GATE` intentionally still absolute for
G2-a?) is answered by D-167: no — retired by supersession, G2-a is a kernel
row with its own gate.

Findings the magistrate adopts:

- F3 (tier the review by consequence: full chain only for physics / claim /
  pre-registration changes, targeted review + tests for ordinary code, one
  light review for bookkeeping). Adopted as the operating rule for this wave
  — it is what the stream table in §3 already does (refuters on 07/08/12/13,
  lead+CI on 05/09/11) and it now has a written justification. luna's
  spend evidence (711 first-parent commits since 08-01: 146 code/config/paper,
  559 process docs; the two layers that paid — C-058 arm-author delta, T28
  contract+delta reviews — and the two that did not — C-039's dead
  background refuter, C-058's seven wedged relay hours) is the first
  quantified instrumentation of rule 5 in the doctrine.
- F4 (one immutable manifest per G2-a run: head, pack digest, raw-root
  digest, command, verdict, producer checks). Folded into the G2-a
  executability work now scouting (stream 16); the release-check half waits
  for post-campaign.
- F2 narrowed: not "close the 460 T26 clauses" but "audit only the
  transaction-relevant `_v5` clauses at current head". Queued behind the
  executability ledger; the ledger will show which clauses touch the
  transaction path.
- Anomaly: `git log --merges` is not a PR counter here (squash landings) —
  recorded so nobody re-derives it.

Declined for this submission: F5 (newcomer reader path + archive), F6
(semantic kernel check), both correctly self-labelled post-campaign; F7 is a
prohibition the magistrate already operates under (no new orchestration
layer). Open questions 3 (advisor's bar = the D-164/165/166 set?) and 4
(process traces in Git vs archived copy) are Ed's and join §6.

Where luna and the magistrate disagree: luna would add "a time-bounded
exception" to the kernel as an alternative to a real `_v5` row. Rejected —
an exception is the bypass its own verdict warns about; D-167 installed the
rows.
