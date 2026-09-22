# 11 — Opus contract-lens refuter, packet 06 (RETAINED-ROOT-REFUSAL-CLASS-01, activation ce7c57a9)

Session: single non-interactive Opus 5 seat, foreground only, no subagents, no background tasks. Worktree `/Users/edr/code/JouleWise-wt-coldgate-ce7c57a9` at `5aa0acd8` (clean). The judge's ruling was not read and not looked for. Wall budget 20 min; the end of this file lists what was NOT EXECUTED.

## Disclosure: auto-loaded files

Loaded by the harness before any action of mine: `~/.claude/CLAUDE.md` (global rules incl. the writing standard), the worktree's tracked `CLAUDE.md`, and the memory index `MEMORY.md` (one-line pointers; no memory bodies opened). Not read: `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any process trace outside `docs/process_traces/2026-09-21-activation-ce7c57a9/`, any narrative state doc. Read for this lens: `00-PACKET.md`, exhibits A, B, D (C not read — time), the packet-02 ruling (`10-coldgate-fable-ruling.md`, Q1 items 3–4, Q4, Q5 replacement, Q7), `joulewise/evidence_night.py:55–61, 706–746, 796–802`, `joulewise/arm_census.py:62–68, 116–124, 196–240`, `joulewise/night_gate.py:88–90`, `scripts/magistrate_watchdog.py:84–90, 771–790`, `scripts/run_night.py:67, 83, 1621`, the runbook lines 736–749, the handbook lines 296–304, `tests/test_evidence_night.py:638–658` (fixture shape only). Fixtures only under `/private/tmp/opus-contract-69305/` and `/private/tmp/opus-r6-*/`; nothing else written.

## Executed probes (my own, this session)

**Probe R (symlink matrix), `python3 -B /private/tmp/opus-contract-69305/probe.py`** — one root `night-custody/A` with a parseable ten-day-old v2 plan and a regular `night/courier.sent`, then one symbolic link added per case, then `evidence_night.retained_roots({"roots_under": …})`:

```
S1_unrelated_under_root          -> retained verdict=pass        (<root>/scratch -> /etc/hosts)
S2_unrelated_under_night         -> retained verdict=pass        (<root>/night/notes -> /etc/hosts)
S3_unrelated_dir_symlink         -> retained verdict=pass        (<root>/logs -> /etc)
S4_plan_symlink                  -> Refused: symlink/path collision: …/A/night_plan.json
S5_courier_symlink               -> Refused: symlink/path collision: …/A/night/courier.sent
S6_chain_started_symlink         -> Refused: symlink/path collision: …/A/night/chain.started
S7_refusal_symlink               -> Refused: symlink/path collision: …/A/night/refusal-01.json
S8_night_dir_symlink             -> Refused: symlink/path collision: …/A/night/courier.sent   (night -> /etc)
S9_ancestor_symlink              -> Refused: symlink/path collision: …/link/night-custody/A/night_plan.json   (night-custody itself is a link)
```

Code the matrix exercises: `safe_path` (`evidence_night.py:57–60`) refuses if the path **or any of its parents** is a symlink; it is called only at `:716` (`roots_under`), `:717` (plan), `:721` (`night/<courier.sent|result.json|chain.exited>`), `:722` (refusal-glob hits), `:723–724` (`night/chain.started`, `night/chain.exited`). Nothing walks the rest of the root.

**Probe C (census population), `python3 -B /private/tmp/opus-contract-69305/census.py`** — synthetic tree `1 → {100 claude → {200 python -m joulewise.evidence_night check, 300 codex mcp-server → 310 sleep, 400 zsh}, 500 sleep, 600 codex exec}`, `hit_pids=(100,300,600)` (what `pgrep -lf '[c]odex|[c]laude|[t]3'` would return for those argvs), `caller_pid=200`, receipt class `DIAGNOSTIC_NO_PACK`:

```
AGENT_CENSUS_ARGV = ('/usr/bin/pgrep', '-lf', '[c]odex|[c]laude|[t]3')
caller=200 own(ancestors incl. self)= (100, 200) foreign= (300, 600) diagnostics= ()
outside ancestor chain of 200: [300, 310, 400, 500, 600] -> only argv-matched ones are foreign: (300, 600)
hit 700 without a readable record -> foreign= (300, 600) diagnostics= ('pid 700 unreadable',)
```

Code: `foreign = (set(observation.hit_pids) & records.keys()) - exempt` (`arm_census.py:237`), `exempt = set(own)` where `own = _ancestors(inventory, caller_pid)` (`:198, :222`; `_ancestors` includes the caller, `:62–68`). `check` fails the census item on `foreign_pids` **or** `diagnostics` **or** `workloads` or an unresolved raw hit (`evidence_night.py:800–801`).

## Q1 — EXACT TEXT for R6 (runbook §0.7)

My answer. Replace the sentence "Every row must read `retained`; an `ACTIVE` or `UNKNOWN` row, a `Refused:` exit (for example a symlink anywhere under a root), or any installed night plist stops the arm." with, verbatim:

> Every row must read `retained`; an `ACTIVE` or `UNKNOWN` row, a `Refused:` exit, or any installed night plist stops the arm. The classifier exits `Refused:` when a path it reads is a symbolic link or sits below one: the `night_plan.json` file, `night/courier.sent`, `night/result.json`, `night/chain.exited`, `night/chain.started`, any `night/refusal*.json` name it matches (contract item 4), and every directory above them, `night/`, the root and `night-custody/` included. A symbolic link anywhere else under a root, such as `<root>/scratch` or `night/notes`, is never read and does not refuse.

Probe: R above — S1–S3 (`retained`, `pass`) show the last sentence; S4–S7 show the file list; S8 and S9 show "every directory above them". First-use test on the proposed text: "symbolic link" is plain English; "classifier" was introduced by the command two sentences earlier ("the direct call"); "contract item 4" is the cross-reference already used in the paragraph; no other term of art is introduced.

Refutation of the other plausible answer (exhibit A §4's wording, "any path it inspects, or any directory above it"): it is TRUE (probe R agrees with probe S/N/W) but leaves "inspects" doing unpaid work — the reader cannot tell whether `night/` is "inspected" as a directory or only reached as a parent; S8 shows the refusal message names `night/courier.sent`, not `night/`. My text says "sits below one" and lists the directories explicitly, so the reader can predict the message they will see. Refutation of keeping the ruled sentence with a narrower example ("for example a symlinked `night/`"): an example does not fix a false generalisation; "anywhere under a root" is the false clause and must go. One caveat on my own text: `_refusal_paths` is the driver's glob (`run_night.py:282`); I wrote "any `night/refusal*.json` name it matches" — the exact set is the second glob at that line, and the sentence defers to contract item 4 for it rather than restating it (restating it here would reintroduce the round-2 divergence class).

## Q2 — EXACT TEXT for H1 (handbook preamble)

My answer. Replace "the census classifies every process outside the caller's ancestor chain as foreign, and the tracked check refuses on any foreign PID, so the session's own MCP helpers must be gone first." with, verbatim:

> the census runs `/usr/bin/pgrep -lf '[c]odex|[c]laude|[t]3'` (`night_gate.AGENT_CENSUS_ARGV`), so it sees only processes whose full command line contains `codex`, `claude` or `t3`; of those, every one that is not the checking process or one of its ancestors is foreign (`arm_census.classify_arm_census`), a matched process it cannot read is a diagnostic, and the tracked check refuses on any foreign PID and on any diagnostic, so the session's own MCP helpers (`codex mcp-server` children of this session) must be gone first.

Probe: C above — 300 and 600 (argv-matched, not ancestors) are foreign; 310, 400, 500 (outside the ancestor chain, argv unmatched) are not; 700 (matched, unreadable) lands in `diagnostics`; `evidence_night.py:800–801` shows `check` fails on either list. First-use test: "full command line" glosses `-f`; "checking process" glosses the caller; "diagnostic" is now defined at its first use (which also cures the ninth FAIL in Q3 below); "MCP helpers" is glossed in the same clause.

Refutation of the other plausible answer (exhibit A §4's H1): it is TRUE as far as it goes, but its last sentence — "Processes whose command line matches none of the three words are not listed and are not foreign, whatever their ancestry" — invites the false inference that such a process cannot stop the check. `check` also fails on `workloads` (`:801`): a `vllm serve` or `codex exec` descendant of an interactive `claude` root is a workload, listed under the root, and refuses without ever being "foreign" (`arm_census.py:196–206, :225–232`). I did not add a workloads clause to my text because the handbook step is about the session's helpers; but the gate should not adopt a sentence whose contrapositive is false. Refutation of "leave the preamble and rely on the ruled text below it": the preamble is the sentence a reader meets first and the ruled text below never restates the population; a FALSE first sentence fails the class this lane exists for regardless of what follows.

## Q3 — FIRST-USE FAILS: which must land in this merge candidate

Contract lens: the contract (P1 item 4) is the text a reader is entitled to replicate from; the runbook and handbook are procedures that cite it. So the fails split by whether the missing definition changes what the contract *certifies*.

MUST land now (three), with text:

1. **"plan span" (P1, P2, P4)** — the certification sentence says `retained` means "span inactive"; without the rule the certification is unverifiable. Adopt exhibit A's gloss with one amendment (the dead-man grace is a derived constant, not a literal): in contract item 4, at the first "plan span", append in parentheses, verbatim:
   > (the span is the interval in which the watchdog treats the plan as live: it begins `PLAN_LEAD_S` = 480 s before `t0`; it is active while `night/chain.started` exists without `night/chain.exited`, and otherwise until `t0 + window_max_s + COURIER_DEADLINE_S` (300 s); after that it stays active until the plan's dead-man bound (`scripts/run_night.deadman_epoch`) plus `COURIER_LOCK_FRESH_S` unless `night/courier.sent` exists — `scripts/magistrate_watchdog.plan_span_active`)

   Evidence: line read `magistrate_watchdog.py:775–790` (four branches in that order), `:86` `PLAN_LEAD_S = 8 * 60`, `run_night.py:67` `COURIER_DEADLINE_S = 300`, `:83` `COURIER_LOCK_FRESH_S = COURIER_DEADLINE_S + max(COURIER_BACKOFF_S)`; exhibit A read the live value 900. Probe of the first clause: exhibit A probe F/G (t0 − PLAN_LEAD_S boundary) — NOT re-executed by me.
2. **"timing constants" (P1)** — resolved by item 1: the four names now appear at first use; replace "the entry checkout's timing constants" with "the entry checkout's timing constants (`PLAN_LEAD_S`, `COURIER_DEADLINE_S`, `COURIER_LOCK_FRESH_S`, `deadman_epoch`)". Evidence: same line reads.
3. **"diagnostic" (P3)** — cured by the Q2 text above; no separate gloss needed. If the gate prefers exhibit A's appended parenthesis, amend it: "a listed process it could not read" is right, but "the relabel would not clear it" should cite `evidence_night.py:801`.

SHOULD land now, one clause each (cheap, contract-local, no cross-document home):
4. **"older sibling plan" (P1)** — adopt exhibit A: "another `night-custody/<plan-id>/night_plan.json` beside the candidate's, authored by an earlier checkout". Evidence: `evidence_night.py:716` glob.
5. **"custody root" (P1)** — "the plan's `custody_root` field, which must name the directory the plan lives in" — evidence probe H (exhibit A) / code `:733`. NOT re-executed by me.
6. **"entry checkout" (P1)** — adopt exhibit A. Evidence: `:712–713` imports resolve in the running checkout.
7. **"session root" (P3)** — adopt exhibit A's `ROOT` sentence, amended: drop "`echo $PPID` from the session's shell" (the shell's parent may be a terminal multiplexer, not `claude`) and keep only the `pgrep -lf claude` form with the no-`-p` rule (`arm_census.py:116–124`). NOT executed live (pgrep against the real process list would census my own session).

Follow-up lane (two): **"arm"** and **"every process"-style operator vocabulary** ("arm", "check" as a verb) are used across many documents; a local gloss in §0.7 would be the third definition of "arm" in the runbook. Lane goal, one sentence: *give every operator-facing document one glossary anchor per project verb ("arm", "check", "census", "diagnostic") and make each first use link to it, so no procedure paragraph carries its own definition.*

Refutation of "gloss all nine now": the Q1-item-3 rule (every rule sentence probed) makes each added sentence a probe obligation; nine glosses in one candidate is the round-1 failure shape (seat-authored prose at scale). Refutation of "gloss none now, all to the lane": the contract's certification sentence is unreplicable without the span rule; that is not a pedagogy nicety, it is the contract not saying what `retained` means.

## Q4 — m16: withdraw the assignment-order requirement; keep m12/m15

My answer: **withdrawn as unobservable.** Reading `evidence_night.py:729–742`: the `retained` reason string is reached only in the `else:` after `plan_span_active` returned `False`; every other path (custody mismatch `:734`, span active `:737`, any exception `:741`) overwrites `reason`. m16 (assign the correct string at `:730`, delete the `else:`) therefore produces byte-identical `inventory` rows on every input, because no path returns with the early string except the one that would have assigned it anyway. A regression that "observes the order" can only inspect source text (AST/grep), which pins a shape rather than a behaviour — the exact prose-vs-code divergence class this lane is escalated for. Probe: none needed beyond exhibit B V3 (`m16 SURVIVED rc=0` with the five tests OK); I did not re-run mutations (budget).

Refutation of "the requirement stands": packet 02 Q4's motive was "the string is authored before the fact it asserts is checked" — a code-hygiene motive, satisfied by the current source and enforced by review, not by a test. Keeping it as a *regression requirement* forces an AST test; keeping it as a *code-shape note* in the ruling costs nothing. Rule the latter. m12 (reason `None`) and m15 (string changed) remain the pins.

## Q5 — closing shape

My answer: **(a) with one addition.** The gate's own executed probe of each supplied sentence (paste command + output) plus the bench's whitespace-normalized fidelity MATCH closes the R6/H1 items; but the Q3 glosses are *new rule sentences* and Q1 item 3 of packet 02 requires each to be probed on the round head, not on the gate's worktree. So: the merge record must carry (i) the gate's probe outputs for Q1/Q2 texts, (ii) a bench re-execution of the same probe script against the merge head (paste output), (iii) fidelity MATCH lines for every supplied passage, (iv) the filtered unittest run output (`Ran 9 tests … OK`), (v) `gen_state.py --check` rc 0, (vi) the sibling full-suite replay result. No new seat pass: both lenses have run, both found only the ruling's own text and pre-existing round-1 text, and the fix is gate-authored — a third seat would compare prose to prose again (the packet-02 Q7 reasoning).

Refutation of (b): another Fable pedagogy pass on gate-authored text is the gate reviewing itself; a Sol delta re-audit found nothing beyond F1/F2 already. The only thing a seat could add is a live process-tree probe of the handbook (exhibit B G2 could not read the process list) — that is a bench obligation (ii), not a seat.

## Q6 — items a merge reviewer should refuse that §2 does not list

1. **Exhibit A's proposed H1 last sentence** ("… not foreign, whatever their ancestry"): true of "foreign", false as a reader's inference about the check (workloads, `evidence_night.py:801`). Refuse if adopted verbatim.
2. **Runbook R10 shape** (exhibit A): the manual `-c` command exits with a Python traceback and status 1, not the CLI's `REFUSED:`/rc 2. The runbook says "a `Refused:` exit"; my Q1 text keeps that wording because the traceback's last line does read `joulewise.evidence_night.Refused: …` (probe R output). A reviewer should refuse any edit that changes it to `REFUSED:`.
3. **Exhibit A K4** notes the installer's re-admission list (`receipt.json, courier.json, chain.started` too) is a superset of `TERMINAL_NIGHT_RECORDS`; the P4 comment's "the same names" is loose, not false — do not let a fix round "align" the two lists.
4. **`_refusal_paths` glob admits `refusal-7x.json`** (exhibit A C8, probe V): contract item 4's naming sentence does not exclude it, so it is not FALSE; but the gate's Q1 text must not say "`refusal-N.json` with N digits" as if the glob were digit-only. My text says "any `night/refusal*.json` name it matches" and defers to item 4.

## NOT EXECUTED

- Filtered unittest run (`… -k retained -k discovery -k span -k realpath -k deep_json`): not run; exhibit B V1 (`Ran 9 tests … OK`) relied on.
- Mutation replay (m16): not re-run; exhibit B V3 relied on.
- Live `pgrep`/process-tree probe of the handbook: not run (would census this session); exhibit A's live run and exhibit B V8 fixture relied on.
- `plan_span_active` boundary probes (t0 − PLAN_LEAD_S, courier.sent branch): line-read only (`magistrate_watchdog.py:775–790`); exhibit A probes F/G relied on.
- Exhibit C (round-3 diff): not read.

Fixtures left under `/private/tmp/opus-contract-69305/` and `/private/tmp/opus-r6-*/` for inspection. Wall time ≈ 19 min.
