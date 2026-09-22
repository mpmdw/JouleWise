# 10 — Cold Fable gate ruling, packet 06 (RETAINED-ROOT-REFUSAL-CLASS-01 returns after round 3)

Judge: fresh non-interactive Fable 5.1 session, no loop context, foreground only, no subagents.
Worktree `/Users/edr/code/JouleWise-wt-coldgate-ce7c57a9` at `5aa0acd8c289506477775395ad96c4a98cc089fe` (branch `coldgate/2026-09-21-ce7c57a9-retained-root-round3`). Started 23:50 PDT 2026-09-21; probes finished 23:53; file written before the 20-minute bound.

## Contamination disclosure

Auto-loaded by the harness before any action: `~/.claude/CLAUDE.md` (global rules incl. the writing standard), the worktree's tracked `CLAUDE.md`, and the memory index `MEMORY.md` (one-line pointers; no memory body opened). Not read: `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any trace outside `docs/process_traces/2026-09-21-activation-ce7c57a9/`, any narrative state doc. Read for this ruling: `00-PACKET.md`, exhibits A, B, D in full, exhibit C head only (first 30 lines), the packet-02 ruling sections Q1, Q4, Q7, and tracked files at the head: runbook §0.7 (`docs/phase_2/derivation_night_runbook.md:725–749`), handbook (`docs/process/NIGHT_HANDBACK.md:296–326`), contract item 4 (`docs/contracts/evidence_night_entry.md:218–250`), `joulewise/evidence_night.py` (`:55–62`, `:700–745`, `:795–805`, `:766`), `joulewise/arm_census.py` (`:27`, `:110–126`, `:206–281`), `joulewise/night_gate.py:90`, `scripts/magistrate_watchdog.py` (`:84–90`, `:771–790`), `scripts/run_night.py` (`:67`, `:82–84`, `:268–284`, `:1621`), `tests/test_evidence_night.py` (`:650–672`, `:940–960`), `joulewise/quiet_guard_process.py` (`:196–245`). Record `../03-round3-under-the-gate.md` was NOT read (budget); where this ruling relies on its content (the live `descendants()` run) it says so.

## Executed evidence (all read-only against the repo; fixtures only under `/private/tmp/coldgate06-70017/`, left in place for the bench)

E1 — symlink refusal map, `python3 -B /private/tmp/coldgate06-70017/probe.py` (fixture: v2 plan ten days old, `receipt_class` `DIAGNOSTIC_NO_PACK`, `window_max_s` 9000; `retained_roots({"roots_under": <fixture>/roots})`):

```
S unrelated symlinks night/stray, <root>/unrelated, <root>/scratch/x -> [('S', 'retained')] verdict pass
W night/courier.sent is a symlink -> Refused: symlink/path collision: …/night-custody/W/night/courier.sent
N night/ is a symlink -> Refused: symlink/path collision: …/night-custody/N/night/courier.sent
K night_plan.json is a symlink -> Refused: symlink/path collision: …/night-custody/K/night_plan.json
Z the root directory itself is a symlink (ancestor of the plan) -> Refused: symlink/path collision: …/night-custody/Z/night_plan.json
R7 refusal-7.json regular + result.json symlink -> Refused: symlink/path collision: …/night-custody/R7/night/result.json
Q refusal-02.json is a symlink (refusal-glob hit) -> Refused: symlink/path collision: …/night-custody/Q/night/refusal-02.json
rc=0
```

Code it exercises: `safe_path` (`evidence_night.py:57–61`) raises when the path or any parent is a symlink; it is called on the plan (`:717`), on `night/<courier.sent|result.json|chain.exited>` (`:721`), on every `_refusal_paths` hit (`:722`), and on `night/chain.started`, `night/chain.exited` (`:723–724`). No other path under a root is touched. R6 is FALSE as written and E1 fixes exactly what is true.

E2 — census foreign rule, `python3 -B /private/tmp/coldgate06-70017/census.py` (synthetic tree 1→100 `claude`→{200 `python3 -m joulewise.evidence_night check` (caller), 300 `codex mcp-server`→310 `sleep 9`, 400 `zsh`}, 1→500 `sleep 99`, 1→600 `codex exec`; `hit_pids` = the argv matches (100, 300, 600); `classify_arm_census(..., caller_pid=200)` with `receipt_class` `DIAGNOSTIC_NO_PACK`, which is what `evidence_night.py:766` passes):

```
own_pids (100, 200) foreign_pids (300, 600) diagnostics ()
outside ancestor chain of 200: [1, 300, 310, 400, 500, 600] -> foreign: [300, 600]
unreadable hit 700: foreign (300, 600) diagnostics ('pid=700 unknown: no exact record',)
```

Code: `foreign = (set(observation.hit_pids) & records.keys()) - exempt` (`arm_census.py:237`), `exempt = set(own)` (`:222`), hits from `AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3")` (`night_gate.py:90`; `ARM_DISCOVERY_ARGV` reuses it at `arm_census.py:27`). H1 is FALSE as written: 310, 400, 500 are outside the ancestor chain and are not foreign.

E3 — timing constants, live:

```
PLAN_LEAD_S 480 COURIER_DEADLINE_S 300 COURIER_LOCK_FRESH_S 900 DEADMAN_GRACE_S 3600
```

`plan_span_active` (`magistrate_watchdog.py:775–790`): `False` before `t0 − PLAN_LEAD_S`; then `True` while `chain.started` exists without `chain.exited`; `True` until `t0 + window_max_s + COURIER_DEADLINE_S` (`plan_completion_epoch`, `:771–772`); after that `False` if `night/courier.sent` exists, else `True` until `deadman_epoch(plan) + COURIER_LOCK_FRESH_S`; `deadman_epoch` = completion + `DEADMAN_GRACE_S` rounded up to the minute (`run_night.py:1621–1626`).

E4 — the single permitted unittest run on the head:

```
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night -k retained -k discovery -k span -k realpath -k deep_json
Ran 9 tests in 12.513s
OK
```

E5 — census diagnostics population (line read, not executed beyond E2's injected diagnostic): `arm_census.py:250` (discovery exit not 0/1), `:260` (unparsable discovery rows), `:262` (discovery OSError/timeout), `:277` (hit with no exact record), `:281` (record read error); the check's census verdict fails on `diagnostics` as on `foreign_pids` (`evidence_night.py:800–801`).

## Q1 — EXACT TEXT for R6 (runbook §0.7)

Replace the whole sentence

> Every row must read `retained`; an `ACTIVE` or `UNKNOWN` row, a `Refused:` exit (for example a symlink anywhere under a root), or any installed night plist stops the arm.

with, verbatim (three sentences; they replace the one):

> Every row must read `retained`; an `ACTIVE` or `UNKNOWN` row, a `Refused:` exit, or any installed night plist stops the arm. The classifier raises `Refused` when a path it inspects, or any directory above that path, is a symbolic link: the root's `night_plan.json`, its `night/` directory, `night/courier.sent`, `night/result.json`, `night/chain.exited`, `night/chain.started`, or any file in `night/` matched by the refusal names in contract item 4. A symbolic link elsewhere under a root, such as `night/notes` or `<root>/scratch`, is not inspected and does not refuse.

Evidence: E1 rows K (plan), N (`night/`), W (`courier.sent`), R7 (`result.json`), Q (refusal-glob hit), Z (directory above the plan) all refuse; row S (`night/stray`, `<root>/unrelated`, `<root>/scratch/x`) classifies `retained`, verdict `pass`. `chain.started`/`chain.exited` are inspected at `evidence_night.py:723–724` through the same `safe_path` (line read; not separately probed, same call shape as W).

Exhibit A's proposed R6 text is adopted in substance; the em-dash construction is replaced by separate sentences and "the refusal name patterns" becomes "the refusal names in contract item 4", which is where they are enumerated.

## Q2 — EXACT TEXT for H1 (handbook preamble)

Replace the sentence that begins "Pre-check step, ruled by the cold gate 2026-09-21 (packet 05 Q3): the census classifies every process outside the caller's ancestor chain as foreign, and the tracked check refuses on any foreign PID, so the session's own MCP helpers must be gone first." with, verbatim:

> Pre-check step, ruled by the cold gate 2026-09-21 (packet 05 Q3, wording corrected by the cold gate's packet 06 ruling): the census lists every process whose full command line matches `codex`, `claude` or `t3` (the exact command is `night_gate.AGENT_CENSUS_ARGV`, a `pgrep -lf` over those three words) and classifies each listed process that is neither the checking process nor one of its ancestors as foreign (`arm_census.classify_arm_census`); a process whose command line matches none of the three words is never foreign, whatever its ancestry. The tracked check refuses on any foreign PID, so the session's own MCP helpers, which match `codex`, must be gone first.

Evidence: E2 (300 and 600 foreign, both argv matches; 310, 400, 500 outside the chain and not foreign; 100 and 200 own). Exhibit A's proposed middle sentence ("A listed process that cannot be read is reported as unknown, which the check also refuses") is TRUE (E2 line 3, E5) but moves to the "diagnostic" gloss in Q3, where the word is used; H1 stays a one-rule sentence.

## Q3 — FIRST-USE FAILS: six glossed in this merge candidate, three to a follow-up lane

Rule: a term is glossed here when the passage cannot be executed or replicated without it (the contract is binding text; the handbook is the procedure an operator runs). A term is deferred when it is project-wide vocabulary whose home is a glossary, not a clause in every document.

**Glossed in this candidate (texts verbatim; each replaces the quoted span).**

1. "plan span" and "timing constants" (contract item 4). Insert this sentence immediately before "A retained root whose plan span is still active by the watchdog's rule":

> The plan span is the interval in which the watchdog treats a plan as live, computed from that plan's own `t0_epoch_s` and `window_max_s` with the constants `PLAN_LEAD_S` (480 s), `COURIER_DEADLINE_S` (300 s), `COURIER_LOCK_FRESH_S` (900 s) and `DEADMAN_GRACE_S` (3600 s): it has not begun before `t0 − PLAN_LEAD_S`; once begun it is active while `night/chain.started` exists without `night/chain.exited`, and otherwise until `t0 + window_max_s + COURIER_DEADLINE_S` has passed; after that it is over if `night/courier.sent` exists, else it stays active until the dead-man bound (`t0 + window_max_s + COURIER_DEADLINE_S + DEADMAN_GRACE_S`, rounded up to the minute) plus `COURIER_LOCK_FRESH_S`.

Evidence: E3 values and the function text at `magistrate_watchdog.py:775–790`, `run_night.py:1621–1626`. Exhibit A's proposed clause is amended: it omitted `DEADMAN_GRACE_S` and the rounding, and "until the chain has exited and … has passed" misstated the chain clause (an open chain alone keeps the span active; a closed chain does not end it early).

2. "entry checkout" and "older sibling plan" (contract item 4). Replace "with the entry checkout's timing constants, which may differ from the head that authored an older sibling plan)" with:

> with the timing constants of the entry checkout, the git checkout whose `joulewise/evidence_night.py` is executing rather than the measurement clone the plan names, which may differ from the head that authored an older sibling plan, another `<roots_under>/night-custody/*/night_plan.json` beside the candidate's written by an earlier checkout)

Evidence: `retained_roots` imports `scripts.magistrate_watchdog` and `scripts.run_night` from the running checkout (`evidence_night.py:712–713`); siblings are the glob at `:716` (E1 inventories every fixture root by that glob). Exhibit A's two proposed clauses are adopted, merged into the existing sentence so no new sentence is authored.

3. "custody_root" (contract item 4). Replace "or whose `custody_root` is not its own directory, is UNKNOWN and refuses" with:

> or whose `custody_root` field (the plan's own record of the directory it must live in) does not name its own directory, is UNKNOWN and refuses

Evidence: `evidence_night.py:733–735` compares `os.path.realpath(parsed.custody_root)` to the plan's parent; exhibit A probe H and the head test `test_custody_root_spellings_equal_under_realpath_classify_alike` (E4, passing).

4. "session root" (handbook). Replace "Let `ROOT` be the session root's PID." with:

> Let `ROOT` be the PID of the session root: the interactive `claude` process this session is running in, which the census recognises by executable basename `claude` and an argv carrying no `-p` or `--print` (`arm_census._interactive_root`). Find it with `pgrep -lf claude`, take the PID whose command line carries no `-p`, and confirm it with `ps -o pid=,command= -p $ROOT` before using it.

Evidence: `arm_census.py:116–124` (line read: basename `claude`, role not a daemon/bg role, no `-p`/`--print`). Exhibit A's proposed "`echo $PPID` from the session's shell" clause is REJECTED: unverified (this judge's shell parent is a `zsh -c source …` wrapper, `ps -o pid=,command= -p $$`), and a wrong PID here selects the wrong kill root.

5. "diagnostic" (handbook, last sentence). Replace `never relabel it "diagnostic".` with:

> never relabel it "diagnostic" (a diagnostic is the census's own report that it could not observe something: a discovery command that failed or printed an unparsable row, or a listed PID with no readable process record; the check refuses on diagnostics exactly as on foreign PIDs, so the relabel would not clear it).

Evidence: E5 line reads; E2 line 3 shows a diagnostic carried through the verdict unchanged. Exhibit A's proposed text is amended to cover the discovery-failure diagnostics (`arm_census.py:250–262`), which "a listed process it could not read" omitted.

6. "every process" (handbook): cured by Q2. No separate gloss.

**Deferred to a registered follow-up lane** (the magistrate registers the row; goal in one sentence): *Give the arm vocabulary one glossary home, the runbook's Terms table, and make the first use of "arm", "retained" and "chain is open" in the contract, runbook §0.7, handbook and the `TERMINAL_NIGHT_RECORDS` comment point at that table or at contract item 4 by section, so no document glosses project-wide words locally.* Deferred items: "arm"/"arming" (runbook, handbook: project-wide; a local gloss would be one of many and drift); "retained" in P2/P4 and "chain is open" in P2 (borderline per exhibit A; P1 builds both and P2 already cites "contract item 4"). Exhibit A's implicit proposal to gloss "arm" locally is REJECTED for that reason. Nothing else from the nine FAILS is deferred.

## Q4 — m16: the assignment-order requirement is WITHDRAWN as unobservable; the string and classification pins stand

Packet 02 Q4 required the retained reason to be assigned only after `plan_span_active` returned `False`, so that the string would not be authored before the fact it asserts was checked. Production code at the head does that (`evidence_night.py:730` assigns `None`, `:739–740` assigns the string in the `else:`; fidelity MATCH per exhibit B V2). But every path that overrides the early assignment in m16 (custody mismatch `:733–735`, span active `:736–738`, any parse exception `:741–742`) also overwrites the reason, so no input distinguishes "assigned early then replaced" from "assigned in the else". Exhibit B shows m16 surviving the five tests; I find no assertion that could kill it without asserting on code structure, which is not a behaviour pin. The observable contract, which the pins already hold, is: the retained reason string appears if and only if the row classifies `retained`, and never on an `UNKNOWN` or `ACTIVE` row (test at `tests/test_evidence_night.py:944–958`, E4 passing; m12 and m15 KILLED per exhibit B V3). Ruling: the order clause is withdrawn as a regression requirement; the head's `else:` form stays as written (no code change); no test is added; exhibit B F2 closes as "withdrawn by the gate".

## Q5 — CLOSING SHAPE: (a), no further seat pass, with the evidence listed here

The escalation reason of packet 02 (prose authored beside ruled text, unchecked against code) is absent from this round: every sentence in Q1–Q3 is gate-authored and gate-probed above (E1, E2, E3, E5). A further seat pass would compare prose to prose again, which is the review shape that missed rounds 1–2. So the lane closes on (a), under these conditions, all carried in the merge record:

1. Fidelity: whitespace-normalized MATCH for each of the eight texts above (Q1, Q2, Q3 items 1–5) against the tracked files, table with file:line per text. A single differing word returns the lane to this gate; the bench authors no word not in this ruling. If the bench finds a sentence it believes is still needed, it goes in the merge record as a question, not into a tracked file.
2. The two probe scripts re-run on the merge head from the bench (copy `/private/tmp/coldgate06-70017/probe.py` and `census.py` into the record verbatim, paste the outputs); outputs must match E1 and E2 row for row.
3. The filtered unittest (E4 command) on the merge head, `OK`; the full sharded replay green with its run identifier; `python3 -B scripts/gen_state.py --check` rc 0.
4. Exhibit B G2: the live `descendants()` run that record 03 §4 reports (the Sol sandbox could not read the process list) pasted in the merge record with PIDs and command lines; if it is not in record 03 verbatim, the bench re-runs it on a throwaway `zsh -c 'sleep … & wait'` tree, kill line replaced by print, and pastes it.
5. The m16 disposition (Q4, withdrawn) and the follow-up lane's kernel row id (Q3).
6. Merge on the standing post-merge CI ruling; no round 4, no third seat.

## Q6 — Items a merge reviewer should refuse that §2 does not list

1. REFUSE any change to the `_refusal_paths` glob or to contract C8 on the ground that `refusal-7x.json` also matches (exhibit A probe V). The glob `refusal-[0-9]*.json` admits it, the contract sentence says "any name matching refusal-[0-9]*.json", both agree; a "fix" would be a new prose/code divergence.
2. REFUSE any rewording of "a `Refused:` exit" in the runbook to `REFUSED:`/rc 2 (exhibit A R10). The manual `-c` form raises through Python and prints `joulewise.evidence_night.Refused: …` with exit 1 (exhibit A §3, exhibit B V4/V5); the runbook's word is the one the reader sees.
3. REFUSE the two exhibit A proposals rejected above if they reappear: the `echo $PPID` clause and a local gloss of "arm".
4. REFUSE the merge if the handbook's corrected preamble still attributes its wording only to packet 05 Q3; the Q2 text carries the packet 06 attribution so the doc's own source line stays true.
5. Note, not a refusal: exhibit A rows R1 (installed-agents clause), H2, K4 rest on line reads in every seat including this one; they are outside this packet's questions and were not made worse by round 3.

## Not executed

- `check` end-to-end and `night_agents` (needs a prepared candidate, clone `.venv`, LaunchAgents listing): NOT EXECUTED.
- Record `../03-round3-under-the-gate.md` and exhibit C beyond its head: NOT READ (budget); Q5 item 4 covers the dependency.
- `night/chain.started` symlink case: not separately probed (same `safe_path` call shape as E1 row W, `evidence_night.py:723`).

## Summary of texts supplied (all verbatim above)

Q1 runbook sentence (three sentences); Q2 handbook preamble sentence; Q3 items 1–5: plan-span sentence, entry-checkout/sibling clause, `custody_root` clause, session-root sentences, diagnostic parenthesis. Eight fidelity rows. Q4 withdrawn. Q5 (a). Follow-up lane goal in Q3.
