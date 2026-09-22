# Opus contract-lens refuter — RETAINED-ROOT-REFUSAL-CLASS-01 round-3 packet (activation ce7c57a9)

Refuter: Claude Opus 5, single foreground session, worktree `JouleWise-wt-coldgate-ce7c57a9` (HEAD `6c86f7f9` = the packet commit on top of the merge candidate `af85b38a`; every code/doc citation below is `git show af85b38a:<path>`). Wall 23:3x–23:5x PDT 2026-09-21, inside the 20-minute budget. No subagents, no background jobs, no edits to any tracked file except this one. I did not look for, and have not seen, the judge's ruling.

**Contamination disclosure.** Auto-loaded before I could refuse: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (one-line pointers; several mention this activation). I opened no memory file, no `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, or any trace outside this packet directory.

**Lens.** The contract: `docs/contracts/evidence_night_entry.md` item 4, the ruled passages in exhibit C, `docs/process/NIGHT_HANDBACK.md` lines 298–311, runbook §0.7, all at `af85b38a`; each rule-stating sentence in exhibit B checked against the code path it names.

## Executed probes (all read-only; fixtures under /private/tmp, deleted after)

| # | probe | result |
|---|---|---|
| P1 | `env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night -k retained -k discovery -k span` (the one permitted run) | `Ran 6 tests in 11.341s — OK` |
| P2 | `MANPAGER=cat man pgrep \| col -b` | `-l` "print the process name … If used in conjunction with -f, print the process ID [and full argument list]"; `-f` "Match against full argument lists. The default is to match against process names."; `-P ppid` "Restrict matches to processes with a parent process ID in the comma-separated list" |
| P3 | Runbook §0.7 zsh loop (exact text at `af85b38a`, run under `/bin/zsh -f`) on a fixture root `real/` holding regular `night_plan.json`, `night/chain.started`, `night/refusal.json` and a **symlinked** `night/chain.exited`, plus `linked -> real` (a symlinked root) | prints `linked: retained refusal.json` and `real: retained refusal.json` |
| P4 | `evidence_night.retained_roots({'roots_under': <same fixture>})` from this checkout | `Refused: symlink/path collision: …/night-custody/linked/night_plan.json` (the whole item refuses; the symlinked `chain.exited` under `real/` would refuse the same way via `safe_path(night / "chain.exited")`) |
| P5 | First attempt of P4 with the fixture under `/tmp` | `Refused: symlink/path collision: /tmp/…` — `/tmp` is itself a symlink on macOS; `safe_path` rejects any symlinked ancestor, so a manual Python read must be given a real path (`/Users/edr/night-custody` is one) |
| P6 | Code reads: `scripts/run_night.py:273,281-284`; `scripts/magistrate_watchdog.py:775-790`; `joulewise/evidence_night.py:57-61,599-650,690-745,880-934`; `joulewise/night_agent_install.py:1128-1142`; `joulewise/arm_census.py:26,135,206-211`; `joulewise/night_gate.py:90`; `tests/test_evidence_night.py:916-942` | cited inline below |

NOT EXECUTED: a pre-span fixture run for A2-F2 (code reading is conclusive: `plan_span_active` line 1 returns `False` when `now < t0 − PLAN_LEAD_S`); no live `pgrep -P` on a real session tree (A2 got exit 3 in its sandbox; P2's manual is enough for the flag semantics).

## Rule-sentence audit of exhibit B (every sentence that states a rule, against the code path it describes)

Legend: ✓ matches code; ✗ contradicts code; ⚠ passes the code check but fails the first-use test (a reader without project grounding would misread it).

### `docs/contracts/evidence_night_entry.md`

1. "No command repairs a checkout. The one move any command makes is `check`'s fast-forward-only pull …" — ✓ (`canonical_fast_forward` is the only mutating git call). ⚠ "move" is unglossed on first use; a reader cannot tell whether it means a filesystem write or a git ref change. Say "the one write to any checkout".
2. Item 1, D-183 paragraph: "item 0 passed (no night label loaded, no plist or sidecar present, label discovery known)" — ✓ `nothing_loaded = inspect("night_agents", …)` (`inspect` returns a bool, `:894`) gates `may_fast_forward`. ⚠ "sidecar" and "label discovery known" are project shorthand not built in this paragraph; "item 0" is never enumerated as an item in this list. (Out of this lane's authorship — merged from PR #378 — but it is in exhibit B.)
3. Item 1: "A dirty tree, a missing or divergent upstream, a timeout, or a pull that still lacks H refuses with `canonical fast-forward failed: …`" — **✗ for the dirty-tree case.** `canonical_fast_forward` calls `canonical_status` first (`:614`), which raises `canonical checkout is dirty or unreadable: …`, not `canonical fast-forward failed: …`. Two further refusal strings the sentence omits: `cannot read canonical HEAD: …` (`:617`) and `cannot read canonical HEAD after fast-forward: …` (`:630`). Same defect class as this lane's recurrence (contract sentence disagrees with the code path it names), arrived via the merge with main, not authored here. Not this packet's lane; the judge should know it exists because a "check every rule sentence against code" round 3 will find it and must know whether it is in scope.
4. Item 1: "records `fast_forward: {before, after, pull, clean_before}`" ✓ (`:631-632`); "A checkout that already contains H records `fast_forward: null`" ✓ (`:641,648`); "`check` re-raises that stale case as its own cause (other supervisor causes stay under the generic `pre-arm checks failed` line)" ✓ (`:927-932`, after the `night_agents`/`census` loop).
5. Item 4: "must be a regular non-symlink file; directories and special files refuse" ✓ (`safe_path` + `is_file`, `:717-719`; P4 shows a symlinked root refuses the whole item, not a row).
6. Item 4: "A root whose `night/chain.started` is a regular file without a regular `night/chain.exited` is ACTIVE and refuses" ✓ (`:723-726`).
7. Item 4: "any regular file matched by `run_night._refusal_paths` (`refusal.json`, `refusal-01.json` and later numbers, …)" — **✗ as a gloss.** The function's glob is `refusal-[0-9]*.json` (`run_night.py:282`), which matches `refusal-7.json` (A2 V4 executed). "`refusal-01.json` and later numbers" is narrower than the function it glosses; a reader would conclude `refusal-7.json` is not a marker. A2-F4 confirmed.
8. Item 4: "the record lists every marker found" ✓ (`evidence=[str(p) for p in markers]`, `:744`). Note the markers are collected before the plan parse, so an `UNKNOWN`-by-parse row still lists them — consistent with the sentence.
9. Item 4: "A retained root whose plan span is still active by the watchdog's rule (`scripts/magistrate_watchdog.plan_span_active`, evaluated on that root's own `night_plan.json` at observation time with the entry checkout's timing constants …) is ACTIVE and refuses" ✓ (`:733-739`; `now` is `time.time()` unless injected). ⚠ "plan span" is first used here without being built; the contract's only earlier "span" is "install-span" (line 74), a different interval. One clause suffices: "the plan's span — the interval from `t0 − PLAN_LEAD_S` through the watchdog's completion, courier and dead-man bounds — …". "an older sibling plan" is also unglossed (sibling = another root under the same `night-custody/`).
10. Item 4: "a root whose plan does not parse … is UNKNOWN and refuses" — **✗ for one input class.** The except tuple (`:740`) is `(PlanError, ValueError, TypeError, OverflowError, OSError)`; `RecursionError` (a `RuntimeError`) from `json.loads` on a deeply nested plan escapes both it and `check.inspect`'s tuple (`:891`), so the check aborts with no `check.json` written. The contract promises `UNKNOWN`; the code delivers a crash. This makes A1-F2 a contract-vs-code contradiction, not only a robustness nit — see Q1.
11. Item 4: "Classifying a root `retained` certifies only that a terminal record exists and that the plan's span is over" — **✗.** `plan_span_active` returns `False` when `now_epoch_s < plan.t0_epoch_s − PLAN_LEAD_S` (`magistrate_watchdog.py:778-779`), i.e. before the span begins; the code then keeps `reason = "terminal record present; plan span over"` (`:730`). A root with a terminal record and a future `t0` is certified "over" while its span has not started. A2-F2 confirmed. The test at `tests/test_evidence_night.py:916-942` never observes before `t0 − PLAN_LEAD_S` with a terminal record, so nothing pins the reason's truth.

### `docs/phase_2/derivation_night_runbook.md` §0.7

12. "what stops an arm is any root whose chain is open, whose span is active, whose night agents are installed, or whose records show no terminal state" — ✓ as a summary of `retained_roots` + `night_agents`. ⚠ "chain is open" is glossed only implicitly by the loop's test two paragraphs later; "span" is built at runbook line 233, far above — acceptable.
13. "`night_agents` and `retained_roots` items must both pass with every inventoried root classified `retained`" ✓ (`verdict="pass" if all(... == "retained")`, `:745-746`).
14. The zsh loop — **✗ parity with contract item 4 (A1-F1 confirmed by P3/P4).** `[[ ! -f $p || -L $p ]]` tests the leaf only; `-f $n/chain.exited` follows a symlink; `(N.)` rejects a symlinked marker but not a symlinked `night/` or root. Python refuses every one of those.
15. "The `(N.)` qualifier restricts each glob to regular files, matching contract item 4's regular-file rule" — **✗.** Item 4's rule is `safe_path(...).is_file()`: no symlink at the path *or any ancestor*. `(N.)` enforces the leaf only. This sentence asserts a parity the code does not have — the exact "doc contradicts adjacent rule" signature, authored in round 1.
16. "This loop reads records only and cannot see the span rule; `check` binds." ✓ and honest.
17. "`refusal-N.json` names are two-digit (`refusal-01.json` and later)." — **✗** (`{index:02d}`, `run_night.py:273`, is a *minimum* width) and ⚠ ("N" is never defined; nothing on disk is literally named `refusal-N.json`).

### `docs/process/NIGHT_HANDBACK.md` pre-check step

18. "the census classifies every process outside the caller's ancestor chain as foreign" — ⚠ overstated. The census inventories only processes whose argument list matches `[c]odex|[c]laude|[t]3` (`night_gate.py:90`, `arm_census.py:27`); "every process" would make a reader expect their editor or browser to refuse the arm. Say "every `codex`/`claude`/`t3` process".
19. Ruled text: "List the children of the session root: `pgrep -lP <session-root-pid>`. For every child whose command line contains `codex mcp-server` …" — **✗.** Per P2, `-l` without `-f` prints the process *name*, so the listing cannot show the command line the next clause asks the operator to inspect; `-flP` would. "`pkill -TERM -P <child-pid>`" signals direct children only (P2: `-P` restricts to parent pid), so "that child and its descendants" is not what the command does. A2-F3 confirmed; the defect is in exhibit C's ruled text verbatim.

### `joulewise/evidence_night.py` comment block (`:694-701`)

20. "The installer refuses re-admission on the same names (night_agent_install)" ✓ (`night_agent_install.py:1133-1137`: the six record names plus `_refusal_paths`). Note the installer's set also includes `receipt.json` and `courier.json`, which `retained_roots` does not treat as terminal — consistent with the ruling (it chose the terminal subset), but "the same names" is loose.

## §3 Q1–Q7 — my answer and the strongest refutation of the other plausible answer

### Q1 Disposition

**My answer: (c) — one round 3 in which the fixing seat authors no rule-stating prose at all.** Every doc sentence that changes in round 3 is text ruled verbatim by this gate (Q2–Q5 below supply it); the seat's work is limited to (i) pasting ruled text, (ii) code and test changes with defect-shaped regressions (Q6), (iii) the kernel/queue regeneration. The delta re-audit then checks each pasted sentence against the code path by executed probe (Q7). This is (a)'s "named structural change" made enforceable: "no prose beside ruled text is authored by the fixing seat" cannot be verified after the fact unless the gate supplied the prose, so (a) as worded collapses into (c).

MUST be in the merge candidate (each is a contract-vs-code contradiction or an inexecutable procedure in tracked text):
- A2-F2 — contract certification sentence (item 11) and the code reason at `:730` (Q4 text).
- A1-F2 — `RecursionError` in the except tuple + 3.11 regression: the contract's "does not parse → UNKNOWN" is false without it (item 10).
- A2-F1 — kernel backing + regeneration: CI runs `gen_state.py --check` (exhibit E2), so without it the PR cannot merge on green anyway.
- A2-F3 — handback command (Q2 text): an operator executing the step as written cannot perform the inspection it prescribes.
- A1-F1 — runbook manual read (Q5 text): P3/P4 prove it prints `retained` where the binding check refuses, beside a sentence claiming parity (item 15).
- A2-F4 — contract gloss (Q3 text): a marker-set description narrower than the function it names.

MAY follow in a later lane: A1-F3 (a test-only regression for `realpath`; m8 surviving is a verification gap, not a false rule) — but it is five minutes of work and belongs in the same round; item 3 above (the dirty-tree message in the D-183 paragraph, not this lane's authorship) — record it, do not fix it here.

Strongest refutation of (b) "merge now, docs follow": (b) is not available — the candidate cannot go green (A2-F1), and the contract at `af85b38a` makes two false certifications (items 10, 11) in the very item this lane exists to make true; merging known-false contract text on the promise of a follow-up is the "ruled-not-installed" shape. Strongest refutation of a pure (a): a third lead-authored prose round under a rule the re-audit cannot check mechanically has the same expected outcome as rounds 1 and 2 — both rounds' defects were introduced while the seat was *explaining* a correct code change (items 15, 17, 11).

### Q2 Ruled handbook command (A2-F3)

**My answer: the lead alone does not have authority to rewrite exact ruled text; this gate does, and should rule the replacement now rather than leave the wrong command in place with a note beside it.** Exhibit C labels the step "exact text" and makes its acceptance "the check record listing the terminated PIDs". The runbook's round-1 precedent (the `(N.)` "one correction to the ruled loop") shows what a lead-authored correction inside ruled text produces: item 15. Strongest refutation of "stays as ruled with a dated correction beside it": an operator runs commands, not addenda; two versions of one command in a step, one of them wrong, is the doc-contradicts-adjacent-rule class in its purest form. Strongest refutation of "the lead may correct it freely": the ruled text was wrong *because* an unexecuted command was written into a ruling — the cure is an executed probe attached to the corrected text, and the gate is the party that can require it.

Replacement passage (exact, replaces `NIGHT_HANDBACK.md` lines 303–311 at `af85b38a`, i.e. from "Before running `check` on a real plan" to "never relabel it \"diagnostic\"."):

> Before running `check` on a real plan, this session terminates its own idle
> MCP helpers. Let `R` be the session root's PID. List `R`'s children with
> their full argument lists: `pgrep -flP R` (`-P R` restricts to children of
> `R`; `-f` matches on the full argument list; `-l` with `-f` prints it). For
> every listed child whose argument list contains `codex mcp-server`, first
> enumerate its descendants to any depth — `pgrep -P` reaches one level only,
> so walk it:
>
> ```zsh
> descendants() { local c; for c in $(pgrep -P "$1"); do descendants "$c"; print -r -- "$c"; done }
> ```
>
> Send SIGTERM to each PID the walk prints, in the order printed (deepest
> first), then to the child itself (`kill -TERM <pid>`). Wait until
> `pgrep -flP R` lists no child whose argument list contains `codex mcp-server`
> and `descendants <child-pid>` prints nothing for each child terminated.
> Record every PID terminated in the check record. Terminate nothing that is
> not a descendant of `R`. Then run `check`. If the census still reports any
> descendant of `R` as foreign, stop; never relabel it "diagnostic".

The lead's round-3 acceptance for this passage: run `pgrep -flP $$` and the `descendants` function against a throwaway `sleep` tree (`zsh -c 'sleep 300 & sleep 300 & wait' &`) under /tmp and paste the output; nothing else is terminated.

### Q3 Ruled contract sentence (A2-F4)

**My answer: not verbatim; the gloss inside the ruled sentence must spell the function's globs, and the allocator note goes in a separate sentence.** The sentence's authority is "any regular file matched by `run_night._refusal_paths`"; the parenthetical is a gloss of that function and a gloss must be replicable from the function. The ruled `refusal-N.json` fails the first-use test (no "N" is ever defined) and the N1 substitution is narrower than the glob (item 7). Strongest refutation of "restore verbatim": verbatim restores an unglossed placeholder that no file is ever named — the reader cannot rebuild the marker set from it, and this gate is entitled to fix its own gloss. Strongest refutation of "keep N1": A2's fixture proves `refusal-7.json` counts; a contract that says otherwise is false in the direction of *missing* a retained root — the fail-open direction.

Exact wording for the parenthetical: "(`refusal.json`, `refusal-[0-9]*.json`, `calibration-refusal.json`, `calibration-refusal.json.*.json` — the function's own glob spellings)". Exact wording for the naming explanation, as its own sentence after "Otherwise it is UNKNOWN and refuses.": "The driver's allocator writes `refusal.json` first and, when that name already exists, `refusal-01.json`, `refusal-02.json`, … (`{index:02d}`: at least two digits, more after 99); the glob accepts any run of digits, so a hand-written `refusal-7.json` is also a marker." The runbook's "names are two-digit" sentence is deleted and replaced by a pointer: "Refusal file names: contract item 4."

### Q4 Reason string (A2-F2)

**My answer: approve A2's proposal with one change — the retained reason names the function the way the ACTIVE reason already does, so the two rows are symmetric and a reader can find the rule.** Code at `:730`: `"terminal record present; plan span inactive (scripts/magistrate_watchdog.plan_span_active)"`. Contract sentence (replaces "Classifying a root `retained` certifies only that a terminal record exists and that the plan's span is over; it does not certify that the courier's delivery succeeded."): "Classifying a root `retained` certifies only that a terminal record exists and that the plan's span is inactive under the watchdog's rule at observation time — inactive covers both a span that has ended and one that has not yet begun; it does not certify that the courier's delivery succeeded." Regression: a valid plan with `t0 = now + 7200`, terminal `refusal.json` → `retained` with that exact reason (kills a reversion to "over" only if the string is asserted; assert it). Strongest refutation of keeping "span over": there is no reading of "over" that includes "not started"; the sentence is a certification, and a certification false on any input is a contract defect regardless of how rare a future-`t0` root with a terminal record is (a dry-check refusal in a real root would produce one).

### Q5 Manual loop (A1-F1)

**My answer: (b) — delete the zsh loop; replace it with a read-only call to the binding code path.** P3/P4 show the loop and the code disagree on symlinked roots and records today; items 15 and 16 show the runbook already concedes the loop cannot see the span rule, the plan parse, or `custody_root`. Any hardening (a) is a second implementation of item 4 in a second language, maintained by hand, and the parity probe becomes a permanent test of a doc — the recurring class institutionalised. Strongest refutation of (b): an operator without the entry checkout cannot run Python — but the same paragraph already requires the entry checkout for `check`, and (b) needs no candidate, which is the one thing the manual read adds over `check`. Strongest refutation of (a): four parity dimensions (ancestor symlinks, `is_file`, span, `custody_root` realpath + parse) each need a zsh reimplementation and a fixture; the round-1 attempt at one of them produced item 15.

Exact replacement for the runbook block from "For a manual read:" through "`refusal-01.json` and later)." (lines 729–754 at `af85b38a`):

> For a manual read without a candidate, run the binding classifier itself
> from the entry checkout (read-only; it writes nothing):
>
> ```zsh
> python3 -B -c 'import json; from joulewise.evidence_night import retained_roots; print(json.dumps(retained_roots({"roots_under": "/Users/edr"}), indent=1))'
> ```
>
> Every `classification` must read `retained`; an `ACTIVE` or `UNKNOWN` row,
> a `Refused` (for example `symlink/path collision`), or any installed night
> plist stops the arm. Do not move or edit a root to change its row. This is
> the same function `check` runs for its `retained_roots` item (contract item
> 4), so the two cannot disagree.
>
> Source: cold-gate rulings 2026-09-21 (packet 05 Q2, lane A230; round-3
> packet Q5 replaced the ruled zsh loop, which could not see symlinked
> ancestors, the span rule, or the plan's `custody_root`).

Executed here: the same call on a /private/tmp fixture (P4) refuses on the symlinked root exactly as `check` would. Note for the seat (P5): the call must be given a real path; `/tmp` is a symlink on macOS and `safe_path` refuses it.

### Q6 Mechanical items

**My answer: A1-F2 and A1-F3 yes; A2-F1 yes with one condition.**
- A1-F2: add `RecursionError` to the tuple at `:740`; regression = a plan of 2,000 nested arrays → row `UNKNOWN`, reason starts `plan unreadable: RecursionError`, and `check.json` exists. Keep the cure at the parse boundary; widening `check.inspect`'s tuple (`:891`) is a design choice about every item, not this lane.
- A1-F3: equivalent-spelling regression (`custody_root` with a trailing slash and through a symlink component → still the normal span classification, not `UNKNOWN`) kills m8. Test-only.
- A2-F1: recording rows in `docs/process/state_kernel.json` and regenerating is mechanical *provided the recorded A230 status is the one true at merge time*. Marking A230 closed in the same PR that delivers it is the ordinary shape; marking it closed in a PR that is then not merged is the decided≠done pattern — so the kernel edit is mechanical, the status word is the lead's factual claim and the delta re-audit must check `gen_state.py --check` rc 0 on the round-3 head (exhibit E1 shows rc 1 today).

Strongest refutation of "these are rulings": none of the three changes any classification, contract sentence, or marker set; each has a defect-shaped regression that fails on the current head. The only judgment call is the A230 status word, named above.

### Q7 Review shape after round 3

**My answer: a distinct-lens pair, and yes, the documentation-pedagogy/contract lens must be one of them.** Lens 1: Sol delta re-audit of the round-3 head (code, tests, mutations m8 re-run, `gen_state.py --check`, the single-module run). Lens 2: a contract lens that reads every rule-stating sentence in the round-3 diff *and* in the three ruled passages, and for each either cites the code line it matches or executes a probe (items 3, 10, 11, 15, 17, 19 above are the proof this lens finds what the code lens does not: A1 and A2 each found the class, but only after it had been authored; a lens that runs the first-use test *before* the round closes is the only shape that stops authoring it). Strongest refutation of "one Sol delta re-audit suffices": Sol found the class in both rounds and the lane still recurred — detection is not the failing step; the failing step is prose authored without a code check, and lens 2 is the check. Strongest refutation of "the gate's own text needs no lens": exhibit C's ruled `pgrep -lP` line (item 19) is the counter-example — ruled text carried an unexecuted command for a full round; gate-supplied text is checked the same way as seat-supplied text.

## Findings the packet does not list

- **N-1 (should-fix, out of lane, in exhibit B):** contract item 1's dirty-tree refusal string does not match `canonical_status` (item 3). Record for the D-183 lane; do not fix under this lane's WRITE_SCOPE.
- **N-2 (nit):** handback "every process outside the caller's ancestor chain" overstates the census population (item 18); fold into the Q2 replacement's preamble as "every `codex`/`claude`/`t3` process".
- **N-3 (nit):** contract item 4's "plan span" and "older sibling plan" are unglossed on first use (item 9).
- **N-4 (test gap, supports Q4):** the span-fence test asserts the `ACTIVE` reason string verbatim but never asserts the `retained` reason on a pre-span root, so the false "over" is unpinned; the Q4 regression closes it.
