# Cold Fable final pass BK1-FINALPASS-01 — ruling

Judge: Claude Fable 5.1, fresh session, worktree `JouleWise-wt-coldgate-152c9255-bk1` at `91921075d981c0456051947e14ca176b700f88f4` (the charge's own commit; detached HEAD). Started 07:12:05 PDT, written ≈07:20 PDT 2026-09-25. Foreground only; no subagents, no background tasks, no sudo/launchctl/powermetrics/systemsetup/pmset, no discovery suite. Read-only apart from this file.

## 0. Disclosure and trust anchors

- **Auto-loaded context (not requested, not relied on):** the harness injected `~/.claude/CLAUDE.md`, the worktree's tracked `CLAUDE.md`, and the memory index `MEMORY.md` (truncated). No memory topic file, `CLAUDE.local.md`, `RUN_STATE.md` history, `TASK_QUEUE.md` history, council log, run report, or process trace outside the packet directory was read, except the files the charge's questions require (RUN_STATE top block and its cited primary files; record 00 item 52 and item 26; the kernel; the lens-cited rulings).
- **Charter digest.** Method: `scripts/validate_gate_packet.py` (receipt schema `coldgate-validator-receipt/v2`), then an independent `shasum -a 256`. Run 1 with the deliberate typo `…5d82`: `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, observed `099de884…5d81`, rc 2. Run 2 with expected `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`: `result: PASS`, rc 0; exhibit `ex-22-fidelity-lens.md` observed = expected `b804919a…6456`; manifest sha `197d20e9…918e`. `shasum` observed charter `099de884…5d81`, packet `6e14787e…5079`. Both equal the expected values supplied to me independently of the packet. Merits read only after this.
- **Packet hygiene (charter §6).** The packet is one charge plus one exhibit, which is byte-identical to the tracked `22-bk1-fidelity-lens.md` (`cmp` clean). The questions are atomic and executable. Two small defects, neither affecting any verdict: the charge says "About 193 files" (actual 195: 191 at `b41ccd57` + 2 in `ca79f629` + 2 in `91921075`), and the charge's "Assembled 07:16 PDT (clock-read)" post-dates both the packet commit (`91921075`, 07:11:37) and this judge's first clock read (07:12:05). Recorded as NIT N-3 below.
- **Merge candidate identity.** `origin/main` = `c034a56f` as the charge says. `origin/docs/2026-09-25-152c9255-bk1` = `91921075` (the charge's head). The older `docs/2026-09-25-152c9255` branch tip (`57957b33`) is not the candidate.

## 1. V1 — the two hard checks: AFFIRM

**(a) No MATH problem text.** Executed myself on `git diff c034a56f..91921075` (22,817 lines), added lines only. Patterns: `\frac`, `\boxed`, `\sqrt`, `\left/\right`, `\begin{`, `Problem:`, `Solution:`, `"problem"`, `"solution"`, `gold_answer`, `Answer:`, "common fraction", "How many", "Find the", "Compute the", "Express your answer", `test/<subject>/N.json`, the seven MATH subject names, `hendrycks`, `MATH-500`, `problem_id`, `\pi`, `\angle`, `\triangle`, `polynomial`, `Let $`, `\(`, `\[`, and inline `$…$`.
Hits, all accounted for: the LaTeX is the J/correct floor statistics (`u_{ce}`, `f_c^J`, `F_{θ,L}`, `g(k)`, `\theta_L`, `M_L`, `k_{\rm cal}`; diff lines 14985–15451 and their duplicate exhibit copy 17115–17581); the 173 `\(` and 22 `\[` hits are those formulas plus JSON-escaped `tail_regex` strings (e.g. `"FAILED \\(failures=2\\)"`, `"unlisted uncovered arcs: \\[\\]"`); "How many" appears once in a council question about quiet-window count (line 14882 and its copy); the only inline `$…$` matches are shell variables in a launch script (`$P/00-charge.md`, `$OUT`); `"Problem"` matches only the lens report's own description of its search. No problem statement, solution, or gold answer anywhere. **PASS**, matching the charge's criterion (ids and hashes only).

**(b) Only the allowed paths change.** `git diff --name-status c034a56f..91921075` outside `docs/process_traces/`: exactly `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, `tests/test_gen_state.py` (all M). Inside: 42 files under `2026-09-24-activation-278ebc9e/`, 149 under `2026-09-25-activation-152c9255/`. Nothing else. The `tests/test_gen_state.py` diff is the live-id set (+12 registered ids, −HEADLINE-PACKER-RECUT-01), `len(tasks) == 255`, `len(quiet) == 16`; no behaviour beyond the counts. **PASS.**

## 2. V2 — every lens finding closed as item 52 says; post-lens commit introduced nothing else: AFFIRM

Post-lens commits on the candidate: `ca79f629` (6 files: RUN_STATE.md, TASK_QUEUE.md, state_kernel.json, record 00, `11-prl-bench-smoke/default-context-negative-control.json`, `22-bk1-fidelity-lens.md`) and `91921075` (2 files: the packet charge and its exhibit). I read every hunk of `ca79f629`.

| Lens finding | Closed? | Deciding evidence |
|---|---|---|
| S1 scorecard overstated | Yes, different wording than the lens's proposed text (see NIT N-1) | RUN_STATE.md:13 now reads "In two of the four first cold rulings (acceptance, wiring)…". Primary check: 05/30/21:56–57 affirm B1, B2 BLOCKER; 06/30/21:37 "C-1 — AFFIRM, BLOCKER"; 09/30/21:15 "B1 … tier MATERIAL, not BLOCKER", :21 "B2 … INSTALLED"; 13/21 §1 affirmed P-0 which the judge already carried as BLOCKER at 13/20:33. The count "two of four" is correct. |
| S2 stale top block (PR-0, POWER, PR-L) | Yes | RUN_STATE.md:19 (PR-R delta clean, PR-L FIX-FIRST B1/S1, fix round 1), :20 (R-6 failed 840/1,112, re-scope gate link), :23 (18/10 decision, packet 21 pending), :25 (successor order includes "PR-0 re-scope ruling and round"). |
| S3 kernel HEADLINE-POWER-01 note; CLAIMGATE-V2-IMPL-01 deps | Yes | `state_kernel.json` HEADLINE-POWER-01 `status_note` carries "Magistrate decision 18/10: census, floor 128, Holm m = 5, SESOI Δ_L = 0.3 … packet 21 (sha 59aefd07…)"; CLAIMGATE-V2-IMPL-01 has the WIRING dependency `satisfied` with the 06/30/21 path as evidence and a new `pending` hard dependency `CLAIMGATE-PR0-GOLDEN-MERGED`. TASK_QUEUE.md A298 row regenerated accordingly; `gen_state --check` rc 0. |
| N1 items 1–122 | Yes | RUN_STATE.md:27; 278ebc9e record last item is 122 (line 353). |
| N2 negative control | Yes, by the lens's first option | `default-context-negative-control.json` exists (median 173.201833, p95 259.285708, max 262.295583, 300 frames, elapsed 54.68 s, `passed: false`). Matches record item 26 sub-bullet (173.2 / 259.3 / 262.3 / 54.68 s) and 17/02:132 (173.202 / 262.296). See NIT N-2 on provenance labelling. |
| N3 ≈0 power qualifier | Yes | RUN_STATE.md:23 "and ≈0 at a hard level with a cell near p = 0.05"; source 13/30/21:39. |

Item 52's eight sub-bullets describe exactly these six closures plus the test re-run; nothing in `ca79f629` falls outside them. `91921075` adds only the packet.

## 3. V3 — tests: AFFIRM (executed)

In this worktree at `91921075`: `python3 scripts/gen_state.py --check` → rc 0 (no output). `python3 -m unittest tests.test_gen_state` → "Ran 44 tests in 2.304s — OK".

## 4. V4 — RUN_STATE top block spot-checks against primary files: AFFIRM (14 checked, 14 match)

1. L13 two-of-four scorecard — 05/30/21:56–57; 06/30/21:37; 09/30/21:15,21; 13/20:33 + 13/21 §1. Match (wording NIT N-1).
2. L15 cure = `ProcessType=Interactive` on both night templates — 05/30/21:67 R1. Match.
3. L16 probe 300 frames under the 55 s production bound — 05/30/21:72 R6; the 150/200 ms sizing is the lens's cite 05/30/21:36 ("keep ex-20's sizing"). Match.
4. L16 default 173 ms refuse / Interactive 125.6 ms pass — both JSON artifacts; 17/02:132. Match.
5. L18 equivalence path not taken; W2 ≥ 6 h; n ≥ 12 — 05/30/21:41–43, :80, :91. Match.
6. L19 PR-L Opus lens FIX-FIRST, B1 `COLD_GATE_CODES` missing `measurement_root_outside_custody`, S1 T0-rehearsal — 17/01:3,32–33,43–47. Match. PR-R delta re-audit file exists (15-prr-review/05-delta-reaudit.md).
7. L20 R-6 failed 840/1,112 (271 killed, 1 listed-equivalent) — 19/01:41,99 and 20/ex-01 raw tail. Match.
8. L20 "770 in `validate_claim_verdicts`" — I counted 770 `artifact.py:` survivors in 20/ex-01; their line range is 997–3475; `validate_claim_verdicts` spans `artifact.py:981–3485` (next `def` at 3485). All 770 lie inside it. Match.
9. L21 harness `4bcddb49`, implementation `8d06633e` — both resolve as commits. Match.
10. L22 25–89 % false admission; Welch SE² = s_d²/k + V_acc; 20 windows — 13/20:22,25,31 (0.890, 0.250); 13/30/21:69 (SE²), :45 ("k_cal = 5 each, 20 window[s]"). Match.
11. L23 power 0.20–0.37 at n = 128, ≈0 near p = 0.05; census, floor 128, Holm m = 5, SESOI 0.3 — 13/30/21:39; 18/10:7–8,14,21–24,33. Match.
12. L24 A283 seeded sampler prerequisite; MATH window class vs 600 s; V1-ISSUANCE-GATE-EVIDENCE-CLASS-01 — 13/30/21:89(a); kernel note "a 10-block envelope fits 600 s only with thinking off"; kernel task V1-ISSUANCE-GATE-EVIDENCE-CLASS-01 (rank 302, queued). Match.
13. L27 278ebc9e items 1–122 — record line 353. Match.
14. L37–39 248 ms default cadence, ~130 ms Interactive, `ea10e3c8` probably superseded — 05/20:26–27,96 (131.6 ms, 243–248 ms); 278ebc9e record :170,:216,:336. Match.

## 5. V5 — disposition: MERGE

0 BLOCKER, 0 MATERIAL, 3 NIT. Merge `91921075` as it stands. The NIT texts below are optional and may be applied in the next bookkeeping commit; none requires a re-gate of this candidate. I concur with the lens's labeled disposition as applied (FIX-FIRST → fixed) and with item 52.

## 6. Findings (severity independent of verdict)

**BLOCKER:** none.

**MATERIAL:** none.

**N-1 (NIT) — RUN_STATE.md:13, second clause is imprecise.** "in the other two (A292, J/correct) its findings were affirmed as MATERIAL" is not what the rulings say: at A292 refuter B2 was "INSTALLED with one addition" (09/30/21:21), not tiered MATERIAL; at J/correct the refuter's P-0 was affirmed as a BLOCKER (13/21 §1) that the judge already carried (13/20:33), and its new findings were MATERIAL (13/30/21:106–107). The scorecard number (two of four) is right. Exact replacement for the bold sentence: "**In two of the four first cold rulings (acceptance, wiring), the paired Opus refuter caught a BLOCKER that the judge missed. At A292 the refuter's two BLOCKERs were ruled MATERIAL or installed as text; at J/correct the refuter affirmed the BLOCKER already before the judge and added MATERIAL findings only.**"

**N-2 (NIT) — `11-prl-bench-smoke/default-context-negative-control.json` is a transcription, not a capture output.** The positive-control file is the probe's own emitted record (argv as a list, `qos_class_hex`); the negative-control file is a hand-written summary (argv as a string, `code`/`record` fields, no QoS field). Its numbers match item 26 and 17/02 to the decimal, so the fact is sound, but RUN_STATE.md:16 "Both controls are committed" reads as two like artifacts. Exact text for RUN_STATE.md:16, replacing the last sentence: "The positive control is committed as the probe's own record and the negative control as a transcribed summary of item 26, both under `11-prl-bench-smoke/`." Optionally add `"provenance": "transcribed from 00-activation-record.md item 26; raw plist not retained"` to the JSON.

**N-3 (NIT) — charge and kernel text hygiene.** (a) Charge "About 193 files" → "195 files"; "Assembled 07:16" precedes neither commit (07:11) nor this judge's start (07:12), so it is a wall-clock read after the commit, not an assembly time; state "Committed 07:11:37, convened ≈07:16". (b) `state_kernel.json` CLAIMGATE-V2-IMPL-01 `goal` still says "after the CLAIMGATE-WIRING-01 design consult resolves end-to-end wiring", which is now satisfied; exact text: "Resume the one-PR full-tier claim-gate v2 implementation under ruled CG-1 through CG-4 and wiring rulings WR-0..WR-10, after PR-0 (WR-7) merges." Then regenerate. No verdict depends on any of these.

## 7. Not executed

Nothing. Every probe the charge asks for was run in budget.
