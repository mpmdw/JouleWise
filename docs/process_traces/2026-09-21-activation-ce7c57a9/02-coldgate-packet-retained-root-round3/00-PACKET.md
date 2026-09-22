# Cold-gate packet — RETAINED-ROOT-REFUSAL-CLASS-01, round-3 disposition (activation ce7c57a9)

Assembled mechanically by the magistrate at 23:2x PDT 2026-09-21. Every exhibit is a verbatim copy or a command output; the magistrate's own view is confined to §3 and is labelled.

## §1 Why this gate is mandatory

Lane RETAINED-ROOT-REFUSAL-CLASS-01 (branch `fix/2026-09-21-retained-root-terminal-markers`, merge candidate `af85b38a`, base main `9e0a4995`, main now `ecefd46a`) has been through: cold gate (exhibit C) → implementation `fc28d782` → two refuters (exhibit D1, D2) → fix round 1 `518a65a8` → merge with main `bd671744` → Opus counter-review (exhibit D3) → fix round 2 `af85b38a` → two delta re-audits (exhibits A1 on `bd671744`, A2 on `af85b38a`).

Neither delta re-audit established a blocker. Both report the same defect class recurring across rounds 1 and 2: documentation that contradicts the rule it sits beside, and ruled text copied with a latent defect (A1 Q6; A2 Q4). The standing escalation trigger (two consecutive rounds failing with the same signature → the next spend is a consult, not round three) and the gate ledger's row 5 both bind. Separately, curing A1-F1 (the manual loop's symlink parity, = round-1 Sol F1 still OPEN) would be a second fix round on the same defect, itself a mandatory cold-gate trigger.

## §2 The open findings (all should-fix or nit; none blocker)

| id | source | location | one line |
|---|---|---|---|
| A1-F1 | A1 (bd671744) | runbook manual loop §0.7 | zsh loop still prints `retained` for symlinked `night/`, symlinked plan parent, symlinked `chain.exited`; Python refuses those; round-1 Sol F1 OPEN |
| A1-F2 | A1 | evidence_night.py except tuple | `RecursionError` from deep JSON plan escapes on Python 3.11; check aborts without its record (fail-closed but not UNKNOWN) |
| A1-F3 | A1 | tests | mutation m8 (drop `realpath`) survives; no equivalent-spelling regression |
| A2-F1 | A2 (af85b38a) | TASK_QUEUE.md generated region | `gen_state.py --check` DRIFT (exhibit E1); CI runs that check (E2) → the PR cannot go green as is |
| A2-F2 | A2 | evidence_night.py:730 + contract item 4 | reason/certification "plan span over" is false before `t0 − PLAN_LEAD_S` (watchdog returns inactive pre-span) |
| A2-F3 | A2 | NIGHT_HANDBACK.md ruled passage (packet 05 Q3) | `pgrep -lP` prints names not command lines; `pkill -TERM -P` is not recursive; inherited from the ruled text |
| A2-F4 (nit) | A2 | contract item 4 + runbook | ruled Q1 sentence no longer verbatim (`refusal-N.json` → `refusal-01.json and later numbers`); "two-digit" overstates `{index:02d}` |

Closure of everything earlier: A1 Q1 table (Astra F1–F6 CLOSED, Sol F1 OPEN, A263 CLOSED); A2 Q1 table (S1, S3, S4 CLOSED; S2, N1, N2 REGRESSED in wording only; N3 OPEN via the queue drift). Mutation kills: A1 m7/m9/m10 KILLED, m8 SURVIVED; A2 m11/m12/m13 KILLED. Real-root inventory on this machine: all three harvested roots `retained`, verdict `pass` (A1 Q3 verbatim).

## §3 Questions for the judge (rule on each; the magistrate may overrule only with written dissent Ed sees)

Q1 DISPOSITION. Choose and justify: (a) fix round 3 at the lead's bench under a named structural change that breaks the recurring class (say what the change is, e.g. "no prose beside ruled text is authored by the fixing seat; every sentence that states a rule is checked against the code path it describes by an executed probe before the round closes"); (b) merge `af85b38a` now with the code items only (A1-F2, A1-F3, A2-F1, A2-F2 code string) and open a follow-up lane for the documentation items; (c) something else. State which findings MUST be in the merge candidate and which may follow.

Q2 RULED HANDBOOK COMMAND (A2-F3). The passage was ruled by packet 05 Q3 (exhibit C). Does the lead have authority to correct a factual command error inside a ruled passage, and what is the EXACT replacement text? Proposed by A2: full-argv inspection (`pgrep -flP <session-root-pid>` or `ps -o pid=,command= -p …`) and explicit recursive descendant enumeration before `kill -TERM`, preserving the session-root boundary. Give the replacement passage verbatim or rule that it stays as ruled with a dated correction beside it.

Q3 RULED CONTRACT SENTENCE (A2-F4). Packet 05 Q1's exact contract sentence: must it be restored verbatim at item 4 (with the naming explanation moved out of the sentence), or is the N1 substitution acceptable? Give the exact wording for the naming explanation ("`refusal-{index:02d}.json`, minimum two digits" or your own).

Q4 REASON STRING (A2-F2). Approve exact replacement text for the code reason at evidence_night.py:730 and for the contract's certification sentence. A2 proposes "terminal record present; plan span inactive under the watchdog rule" and "certifies only that a terminal record exists and that the plan's span is inactive under the watchdog's rule at observation time".

Q5 MANUAL LOOP (A1-F1). Rule: (a) harden the zsh loop (realpath checks on `${p:h}` and `$n`, `-L` tests) with a parity probe, or (b) replace the manual loop with a one-line read-only Python call to `retained_roots` (the binding code path) and delete the zsh loop. Give the exact text.

Q6 MECHANICAL ITEMS. Confirm that A1-F2 (add `RecursionError` to the except tuple + a 3.11 regression), A1-F3 (equivalent-spelling regression for `realpath`), and A2-F1 (record A230's closure, A263, A264 in `docs/process/state_kernel.json` and regenerate `TASK_QUEUE.md`) are mechanical fixes the lead may execute at the bench with defect-shaped regressions, not rulings.

Q7 REVIEW SHAPE AFTER ROUND 3. Given the recurrence, what re-audit shape closes the lane: one Sol delta re-audit on the round-3 head, or a distinct-lens pair, and must a documentation-pedagogy lens (first-use test; rule sentences checked against code by executed probe) be one of them?

## §4 Hard limits on the judge
Read only this packet directory and the worktree's tracked files at `af85b38a`; do not read RUN_STATE.md, TASK_QUEUE.md beyond its generated-region header, or docs/process_traces outside this packet. Never touch /Users/edr/code/JouleWise, /Users/edr/night-custody, /Users/edr/night-plan-staging, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents. Foreground only; no subagents; 20-minute wall budget; write the ruling to `10-coldgate-fable-ruling.md` in this directory with the Write tool; items not executed in budget are marked NOT EXECUTED.
