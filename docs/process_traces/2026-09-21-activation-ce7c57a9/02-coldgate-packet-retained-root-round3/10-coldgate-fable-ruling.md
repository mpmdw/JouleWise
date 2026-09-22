# Cold-gate Fable ruling — RETAINED-ROOT-REFUSAL-CLASS-01, round-3 disposition (activation ce7c57a9)

Judge: Claude Fable 5.1, cold session, worktree `JouleWise-wt-coldgate-ce7c57a9`. Worktree HEAD observed `6c86f7f9` (the packet commit on top of the merge candidate `af85b38a`; `git status` clean). Wall: ~23:4x–23:5x PDT 2026-09-21, foreground only, no subagents, no background tasks.

## Contamination disclosure

Auto-loaded before I could refuse: `~/.claude/CLAUDE.md` (global rules, including the writing standard), the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (one-line pointers; several mention this activation, PR #378 and the earlier packets). I opened no memory file, no `CLAUDE.local.md`, `RUN_STATE.md`, narrative trace, or `TASK_QUEUE.md` beyond the two A263/A264 rows a grep returned (lines 881–882, 1107–1108; the finding A2-F1 is about exactly those rows). I read only this packet directory plus the tracked files named below. I did not read or list `/Users/edr/night-custody`, the canonical root, staging, measurement roots, or LaunchAgents.

## Packet hygiene

- Exhibits A1, A2, C, D, E are verbatim seat outputs or command outputs; questions are atomic; options symmetric. No blocker.
- MATERIAL — A1-F2 is understated by A1 and by the packet. A1 says `RecursionError` escapes "on Python 3.11". Executed here: it escapes on 3.11 **and** 3.13; only 3.14's decoder converts it to `JSONDecodeError` (a `ValueError`, so caught). The entry checkout's interpreter matters; see Q6.
- NIT — the packet's §2 A1-F1 line says the loop prints `retained` for "symlinked `chain.exited`"; A1's own text says the open-chain `-f` test follows symlinks. Both are true; the executed fixture below shows the whole-directory case, which is the operative one.
- NIT — the `pgrep` flag semantics A2 could only take from the manual (its own probe hit `Cannot get process list`, R2) are confirmed live here.

## Executed probes (all read-only; fixtures only under `/private/tmp`, deleted after)

| # | Probe | Result |
|---|---|---|
| P1 | `issubclass(RecursionError, (ValueError, TypeError, OverflowError, OSError))` and `json.loads('[' * 100000)` on python3.11 / 3.13 / 3.14 | `False` on all three. Deep JSON → `RecursionError` on 3.11 and 3.13; `JSONDecodeError` on 3.14. |
| P2 | `sleep 20 &` then `pgrep -lP $$` vs `pgrep -flP $$`; `man pgrep` | `-lP` prints `63864 sleep`; `-flP` prints `63864 sleep 20`. Manual: `-l` = process name, "if used in conjunction with -f, print the process ID" and argument list; `-P ppid` = parent process ID list (immediate parents only). |
| P3 | Nested tree `zsh -c "sleep 15 & wait" &` under `zsh -f`; a recursive `descendants()` helper; `pgrep -P <child>` | `pgrep -flP $$` lists the child with full argv; `descendants $$` lists child **and** grandchild (80863, 80867); `pgrep -P` on the child lists only the immediate `sleep`; `kill -TERM $(descendants $$)` empties the tree. |
| P4 | `python3 -B scripts/gen_state.py --check` in this worktree | `DRIFT: …/TASK_QUEUE.md generated region differs`, rc=1. `state_kernel.json` has no `A263` / `A264` / `RETAINED-ROOT-SPAN-ARITHMETIC-01` / `MAGISTRATE-LAUNCH-WITHOUT-MCP-01` row; `NIGHT-ROOT-RETENTION-DISCOVERY-01` exists (kernel line 4322). |
| P5 | Ruled zsh loop (§0.7 at HEAD, path substituted, `zsh -f`) on a fixture: rootA real `night/refusal.json`; rootB `night` → symlink to a directory elsewhere holding `refusal.json`; rootC `refusal-7.json` + `refusal-123.json` | `rootA: retained refusal.json`, **`rootB: retained refusal.json`**, `rootC: retained refusal-123.json (all: refusal-7.json, refusal-123.json)`. |
| P6 | `evidence_night.retained_roots({'roots_under': fixture})` on the same fixture | With rootB present: `Refused: symlink/path collision: …/rootB/night/courier.sent` (the whole inventory refuses). With rootB removed: rootA and rootC → `UNKNOWN`, reason `plan unreadable: PlanError: plan keys are not exact …`, evidence lists **all** refusal paths (`refusal-123.json`, `refusal-7.json`). Same call under `/tmp` refuses on `/tmp` itself (it is a symlink on macOS). |
| P7 | `env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night -k retained -k discovery -k span` (the one allowed run; python3 = 3.14.7) | `Ran 6 tests in 11.269s — OK`, rc 0. |
| P8 | Code reads | `magistrate_watchdog.py:778-779`: `if now_epoch_s < plan.t0_epoch_s - PLAN_LEAD_S: return False` (`PLAN_LEAD_S = 8*60`, line 86). `evidence_night.py:730`: reason `"terminal record present; plan span over"` is assigned **before** the plan is parsed or the span evaluated. `run_night.py:273`: allocator `f"{path.stem}-{index:02d}{path.suffix}"`; `:282`: glob `refusal-[0-9]*.json`. `tests/test_evidence_night.py:911`: pins the reason string. `evidence_night.py:57-61` `safe_path` refuses any symlink component. |
| — | NOT EXECUTED | Mutation m8 replay (relied on A1 V2 `SURVIVED`); the pre-span fixture at `t0 − 7200` (relied on A2 V4 plus P8's direct code read, which is dispositive: a pre-span plan returns `False` from `plan_span_active` and the reason text is never revisited); the full-suite replay (E4, running at the bench). |

## Q1 — DISPOSITION: (a), fix round 3 at the lead's bench, under a named structural change; every open finding lands in the one merge candidate

Deciding evidence: P4 (the candidate cannot go green: `gen_state.py --check` is a CI step, E2), P8 (a contract sentence certifies something false), P5/P6 (tracked runbook text and the binding code disagree on the same input), A2 Q4 (the same defect class in rounds 1 and 2).

Why not (b): the three "documentation items" are not cosmetics. The contract's certification sentence is binding contract text and is false for a pre-span refusal (Q4). The handbook step is the procedure the next arm executes, and its command does not do what its prose says (Q2). The runbook loop is a second, divergent implementation of the classifier in tracked process text (Q5). Merging the code and deferring these opens a fourth round of the same class under a new lane name; that is the spiral the escalation rule exists to stop. Why (a) is not "round three of the same thing": the recurring signature is *prose authored by the fixing seat beside ruled text, unchecked against the code it describes*. This ruling removes that input entirely.

**The structural change (binding for round 3):**

1. **The fixing seat authors no new prose.** Every documentation sentence in round 3 is copied verbatim from this ruling (Q2, Q3, Q4, Q5 texts). Any sentence the seat believes is still needed and is not in this ruling is a question for the lead, recorded in the round-3 record, not written into a tracked doc.
2. **The manual re-implementation is deleted** (Q5 option (b)). Process text stops re-implementing the classifier, so it cannot drift from it.
3. **Every sentence that states a rule is probed before the round closes.** The round-3 record lists, for each rule sentence changed (contract item 4 certification, handbook step, runbook §0.7), the code line it describes and one executed command whose output shows the sentence is true. P1–P8 above are the model; the seat repeats the relevant ones on the round-3 head.
4. **No round 4.** If either re-audit in Q7 finds a same-signature defect, the lane returns to this gate with a new packet; the lead does not open another fix round.

**Must be in the merge candidate:** A2-F1 (kernel rows + regenerate; `--check` rc 0 in the record), A2-F2 (code reason and contract sentence, Q4; test at line 911 updated), A1-F2 (Q6), A1-F3 (Q6), A2-F3 (handbook, Q2), A2-F4 (contract sentence restored, Q3), A1-F1 (runbook loop replaced, Q5).
**May follow:** nothing from this packet. A264 (launch without MCP) stays its own lane, as packet 05 Q3 already ruled.

## Q2 — RULED HANDBOOK COMMAND (A2-F3): the lead may correct it; the corrected passage is supplied here verbatim

Authority: packet 05 Q3 ruled the *procedure* (own helpers only, session-root boundary, wait until gone, record PIDs, stop rather than relabel). The flag spellings were the ruling's illustration of that procedure and, by P2/P3, two of them do not perform it: `pgrep -lP` cannot show the command line the next sentence tells the operator to read, and `pkill -TERM -P <child>` signals only immediate children (manual, P2), so a helper's grandchildren survive. A ruled passage whose command contradicts its own ruled prose is corrected by the gate that ruled it, which is this ruling; the lead applies it as a dated correction, keeps the "Source" attribution, and does not otherwise re-author the passage. In general: yes, the lead may correct a factual command error inside a ruled passage when the correction preserves every ruled rule and is recorded as a dated correction naming the executed probe; the lead may not change what the passage rules.

Replacement for `docs/process/NIGHT_HANDBACK.md` from "The ruled text:" through the end of the ruled paragraph (line ~304 onward), verbatim:

> The ruled text, with its commands corrected by the cold gate 2026-09-21 (activation ce7c57a9, round-3 packet, Q2; `pgrep -lP` prints process names only and `pkill -P` reaches immediate children only, both verified against the installed manual and a live process tree):
>
> Before running `check` on a real plan, this session terminates its own idle MCP helpers, and nothing else. Let `ROOT` be the session root's PID. List the session root's children with their full command lines: `pgrep -flP $ROOT`. Every child whose command line contains `codex mcp-server` is a helper. For each helper, enumerate all of its descendants, at every depth, and send SIGTERM to the helper and every descendant:
>
> ```zsh
> descendants() { local pid; for pid in $(pgrep -P $1); do print -- $pid; descendants $pid; done }
> for h in $(pgrep -flP $ROOT | grep -F 'codex mcp-server' | cut -d' ' -f1); do
>   victims=($h $(descendants $h)); print -r -- "helper $h: TERM ${(j:,:)victims}"; kill -TERM $victims
> done
> ```
>
> Then wait until no descendant of the session root, at any depth, has `codex mcp-server` in its command line: repeat `for d in $(descendants $ROOT); do ps -o pid=,command= -p $d; done | grep -F 'codex mcp-server'` until it prints nothing. Record every PID terminated, with its command line, in the check record. Terminate nothing that is not a descendant of `ROOT`. Then run `check`. If the census still reports any descendant of the session root as foreign, stop; never relabel it "diagnostic".

Probe that must appear in the round-3 record: P3's shape (a nested `zsh -c "sleep 15 & wait" &` tree, `descendants` listing the grandchild, tree empty after `kill -TERM`). Severity of the defect: MATERIAL (an arm-procedure command that does not perform its prose).

## Q3 — RULED CONTRACT SENTENCE (A2-F4): restore the ruled sentence verbatim; the naming explanation is a separate sentence with this exact wording

The ruled sentence (exhibit C, Q1 replacement) is restored at contract item 4 verbatim, including "`refusal-N.json`". The N1 substitution is not acceptable inside the ruled sentence: it changed ruled text and introduced a claim ("`refusal-01.json` and later numbers") that P8 shows is not the glob's meaning (`refusal-[0-9]*.json` counts `refusal-7.json`, A2 V4 fixture).

Naming explanation, one sentence placed immediately after the ruled sentence in contract item 4 (`docs/contracts/evidence_night_entry.md`), verbatim:

> Here `refusal-N.json` means any name matching `refusal-[0-9]*.json`, the second glob in `run_night._refusal_paths` (`scripts/run_night.py:282`); the driver's allocator writes `N` with a minimum of two digits (`{index:02d}` at `scripts/run_night.py:273`: `refusal-01.json` … `refusal-99.json`, then `refusal-100.json`), and a name with fewer digits, such as `refusal-7.json`, also counts.

Runbook §0.7: delete the sentence "`refusal-N.json` names are two-digit (`refusal-01.json` and later)." and do not replace it; after Q5 the runbook no longer enumerates names, and the contract owns the explanation. The same one-sentence explanation is the only permitted text if the lead judges the runbook must still name the pattern.

## Q4 — REASON STRING (A2-F2): approved with one change to A2's text and one change to where the code assigns it

Deciding evidence: P8. `plan_span_active` returns `False` for any observation earlier than `t0 − PLAN_LEAD_S` (line 778), so "span over" is false for a refusal written before the span begins, which is exactly when an arm-time driver refusal is written. Further, line 730 assigns the reason before parsing the plan, so the string is authored before the fact it asserts is checked; A2's wording alone would leave that order in place.

Code, `joulewise/evidence_night.py` retained branch: the retained reason is assigned only after `plan_span_active` has returned `False`, i.e. in an `else:` of the `elif plan_span_active(...)` (the initial assignment at line 730 becomes `classification, reason = "retained", None` or is removed). The reason string, exact:

```
terminal record present; plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active)
```

It mirrors the ACTIVE reason's form and names the rule it applied. `tests/test_evidence_night.py:911` is updated to the new string; that test plus mutation m12 (reason `None`) remain the pins.

Contract item 4, replace "Classifying a root `retained` certifies only that a terminal record exists and that the plan's span is over; it does not certify that the courier's delivery succeeded." with, verbatim:

> Classifying a root `retained` certifies only that a terminal record exists and that the watchdog's span rule (`scripts/magistrate_watchdog.plan_span_active`) reported the plan's span inactive at observation time, which is also the answer for a plan whose span has not yet begun (observation earlier than `t0 − PLAN_LEAD_S`); it does not certify that the courier's delivery succeeded.

Regression the seat adds (defect-shaped): a sibling root with a terminal refusal record and a parseable plan observed at `t0 − 7200` classifies `retained` with exactly the new reason; a root whose plan is unparseable never carries the retained reason. Kills: reason assigned before the span evaluation.

## Q5 — MANUAL LOOP (A1-F1): (b), replace the loop with the binding code path and delete the zsh loop

Deciding evidence: P5 vs P6. On a root whose `night/` is a symlink, the ruled loop prints `retained` and the classifier refuses the whole inventory. The loop also prints one marker where the classifier lists all (rootC). Option (a) would keep a second implementation in prose and re-open the parity class at the next code change; the replacement below evaluates the span rule too, so the "cannot see the span rule" caveat is deleted rather than kept.

Replacement for `docs/phase_2/derivation_night_runbook.md` §0.7 from "For a manual read:" through the end of the "Source:" paragraph, verbatim:

> For a manual read, run the same classifier the check binds, read-only, from the root of the entry checkout:
>
> ```zsh
> python3 -B -c 'import json; from joulewise import evidence_night as e; print(json.dumps(e.retained_roots({"roots_under": "/Users/edr"}), indent=1))'
> ```
>
> It prints one row per `/Users/edr/night-custody/*/night_plan.json` with `classification`, `reason` and the full paths of every marker found, then `verdict`. Every row must read `retained`; an `ACTIVE` or `UNKNOWN` row, a `Refused:` exit (for example a symlink anywhere under a root), or any installed night plist stops the arm. Do not move or edit a root to change its row. This is the same function `check` runs (contract item 4), evaluated at the current time with the entry checkout's timing constants, so it sees the span rule.
>
> Source: cold-gate ruling 2026-09-21 (packet 05 Q2, lane A230); the shell loop that ruling illustrated was replaced by the direct call on the cold gate's round-3 ruling (activation ce7c57a9, Q5) after it printed `retained` for a symlinked `night/` directory that the classifier refuses.

Probe for the round-3 record: the one-liner run against a `/private/tmp` fixture (P5/P6 shape) showing the `Refused:` line for the symlinked root and the multi-marker evidence list for the numbered-refusal root. Executed here: `retained_roots` performs no write (P6 read of lines 713–747; only `read_text`, `is_file`, `is_symlink`).

## Q6 — MECHANICAL ITEMS: confirmed, with the regressions shaped as follows

All three are executions of settled rules, not rulings; the lead executes them at the bench.

- **A1-F2.** Add `RecursionError` to the except tuple at the plan-parsing boundary. Regression: interpreter-independent, because P1 shows deep JSON is not a `RecursionError` on 3.14. Patch `json.loads` (or `NightPlan.from_mapping`) with `unittest.mock` to raise `RecursionError` for one sibling root with a terminal record; assert the row is `UNKNOWN` with reason starting `plan unreadable: RecursionError`, that `check()` refuses naming `retained_roots`, and that the failing check record is persisted. Kills: `RecursionError` dropped from the tuple. The round-3 record states the entry checkout's interpreter version and, if it is 3.11 or 3.13, additionally runs the raw deep-JSON plan once.
- **A1-F3.** Regression for `os.path.realpath`: write the plan's `custody_root` as two spellings that are realpath-equal to the plan's directory but string-unequal, a trailing slash and a `night/..` segment, and assert each classifies exactly as the plain spelling (retained after the span, ACTIVE inside it). Kills: m8 (realpath dropped → string compare → `UNKNOWN`). A symlink spelling is not required and would collide with `safe_path`'s refusal (P6).
- **A2-F1.** The generated region is not authored by hand. Record A230's closure, A263 (with its Opus residual, N3) and A264 in `docs/process/state_kernel.json` per the kernel's existing row shape (`NIGHT-ROOT-RETENTION-DISCOVERY-01` at kernel line 4322 is the model), regenerate `TASK_QUEUE.md`, and paste `python3 -B scripts/gen_state.py --check` → rc 0 in the round-3 record. Executed here: rc 1, DRIFT (P4).

## Q7 — REVIEW SHAPE AFTER ROUND 3: a distinct-lens pair, and the pedagogy lens is mandatory

Two seats, both on the round-3 head, both fresh:

1. **Sol delta re-audit (high)** in the A2 shape: closure table for every finding in this packet (A1-F1..F3, A2-F1..F4) against the exact texts in Q2–Q5, the six-test filter, the new regressions, mutations m8 and m12 plus a new one that assigns the retained reason before the span evaluation, and `gen_state.py --check`.
2. **Documentation-pedagogy lens**, a distinct model from seat 1 (Opus or a blind Fable seat), whose brief carries the global writing standard verbatim and checks two things only: the first-use test on every changed passage (each term of art built or glossed before use, for a reader without project grounding), and, for every sentence that states a rule, the code line it describes and the executed probe that shows it true. Its verdict is a table: sentence, code line, probe, TRUE/FALSE. Any FALSE is a same-signature recurrence.

This lens is mandatory because the recurrence across rounds 1 and 2 was invisible to fidelity review by construction: every seat compared prose to prose (ruled text to copied text) and passed it, while the prose was false against the code. The lane closes when both seats return no should-fix and the sibling full-suite replay (E4) is green; no third seat and no round 4. A same-signature finding from either seat returns the lane to this gate with a new packet, per Q1 item 4.

## Summary of texts supplied (all verbatim above)

| Item | Where | Text |
|---|---|---|
| Q2 | `docs/process/NIGHT_HANDBACK.md` ruled step | corrected helper-termination passage with `pgrep -flP`, recursive `descendants`, argv-based wait |
| Q3 | `docs/contracts/evidence_night_entry.md` item 4 | ruled sentence restored verbatim + one naming sentence; runbook two-digit sentence deleted |
| Q4 | `joulewise/evidence_night.py` retained branch; contract item 4 | reason `terminal record present; plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active)`, assigned after the span evaluation; certification sentence |
| Q5 | `docs/phase_2/derivation_night_runbook.md` §0.7 | zsh loop deleted; read-only `retained_roots` one-liner + Source paragraph |
