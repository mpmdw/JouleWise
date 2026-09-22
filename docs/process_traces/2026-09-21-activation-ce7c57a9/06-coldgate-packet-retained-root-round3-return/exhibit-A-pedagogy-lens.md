# 04 — Blind Fable pedagogy-and-contract lens, fix round 3 (RETAINED-ROOT-REFUSAL-CLASS-01)

Session: fresh non-interactive Fable 5.1 seat, no loop context, foreground only, no subagents.
Worktree `/Users/edr/code/JouleWise-wt-pedagogy-ce7c57a9` at `cfc569213f3f4a9b900f73564d1f76c43101a4f7` (clean).
Wall budget 20 min; everything below was executed in budget except where marked NOT EXECUTED.

## Disclosure: auto-loaded files

Loaded into context by the harness before any action of mine: `~/.claude/CLAUDE.md` (global rules, incl. the writing standard), the worktree's tracked `CLAUDE.md`, and the memory index `~/.claude/projects/-Users-edr-code-JouleWise/memory/MEMORY.md` (one-line pointers only; no memory file bodies were opened). Not read: `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any process trace outside `docs/process_traces/2026-09-21-activation-ce7c57a9/`, any narrative state doc. Files read for the checks: the four passages, `joulewise/evidence_night.py`, `scripts/magistrate_watchdog.py` (Storage, span rule, constants, plist `--plan` parse), `scripts/run_night.py` (`_write_refusal_bytes`, `_refusal_paths`, `--plan` argparse), `joulewise/night_gate.py` (`AGENT_CENSUS_ARGV`, `NightPlan` fields), `joulewise/arm_census.py` (`classify_arm_census`), `joulewise/quiet_guard_process.py` (record dataclasses), `joulewise/night_agent_install.py` (grep only), `tests/test_evidence_night.py` (fixture helper `sibling_plan` only, to build a parseable v2 plan). Probe fixtures lived under `/private/tmp/pedlens-15800/`; nothing was written anywhere else.

## Passages audited (verbatim scope)

- P1 `docs/contracts/evidence_night_entry.md` Slice B1 item 4 (lines 220–250).
- P2 `docs/phase_2/derivation_night_runbook.md` §0.7 from "Check it." (line 725) through the "Source:" paragraph (line 746–749).
- P3 `docs/process/NIGHT_HANDBACK.md` lines 298–326, "Pre-check step, ruled by the cold gate" through `never relabel it "diagnostic".`
- P4 `joulewise/evidence_night.py` lines 699–707, the comment block above `TERMINAL_NIGHT_RECORDS`.

## Headline

Two FALSE rule sentences, both same-signature recurrences of the class this lane is escalated for (a doc sentence contradicting the rule beside it, i.e. the code it cites):

1. **P2, runbook §0.7:** "a `Refused:` exit (for example a symlink anywhere under a root) … stops the arm." The classifier refuses a symlink only on the paths it inspects (the plan file, `night/`, the three terminal names, the refusal-glob hits, `chain.started`/`chain.exited`) and their ancestors. A symlink at `<root>/night/stray` or `<root>/unrelated` classifies the root `retained`, verdict `pass` (probe S). "Anywhere under a root" is false.
2. **P3, handback pre-check:** "the census classifies every process outside the caller's ancestor chain as foreign." Foreign is `(hit_pids ∩ readable records) − own ancestors` (`arm_census.py:237`), and hit PIDs come only from `pgrep -lf '[c]odex|[c]laude|[t]3'` (`night_gate.py:90`). A `zsh` child of the session root outside the ancestor chain is not foreign (probe Y). This is exactly the refuter's candidate; it is confirmed FALSE at the bench.

Everything else stated as a rule in the four passages was shown TRUE by an executed probe or a line read (table below). The first-use test fails on nine terms (table in §1), of which the two that most block replication are "plan span" (the span rule is never stated in prose anywhere in the four passages, only cited by function name) and "session root" (never defined).

## 1. FIRST-USE TEST

Reader model: technical, has never seen this repository. Order of reading assumed: P1 (contract) → P2 (runbook) → P3 (handback) → P4 (code comment), each passage judged on its own text plus whatever it explicitly points at, since a reader lands on any one of them alone.

| Term | Passage(s) | Verdict | Sentence of first use in scope, and why |
|---|---|---|---|
| "every process" | P3 | **FAILS (and FALSE, see §2 row H1)** | "the census classifies every process outside the caller's ancestor chain as foreign" — the reader will take "every process" literally; the census only sees processes whose argv matches codex/claude/t3. |
| "plan span" / "span is active" | P1, P2, P4 | **FAILS** | P1: "A retained root whose plan span is still active by the watchdog's rule (`scripts/magistrate_watchdog.plan_span_active`, …)". The term is named and pointed at code, but nowhere in the four passages is the rule built: span begins at t0 − 480 s (`PLAN_LEAD_S`), is active while the chain is open or until t0 + window_max_s + 300 s (`COURIER_DEADLINE_S`), and after that until the dead-man bound + 900 s unless `courier.sent` exists. A reader cannot rebuild "active" from the text; they can only follow the gist ("some time window around t0"). |
| "older sibling plan" | P1 | **FAILS** | "which may differ from the head that authored an older sibling plan" — "sibling" is never glossed in P1 (P2 does gloss it: "sibling plans by globbing `*/night_plan.json` in the PARENT"). In P1 the reader has no way to know a sibling is another `night-custody/<id>/` directory beside the candidate's. |
| "session root" | P3 | **FAILS** | "Let `ROOT` be the session root's PID." — never said what process that is (the interactive `claude` process the operator is typing into, which the census recognises by executable basename `claude` and non-`-p` argv, `arm_census.py:116–124`). The reader can't pick the PID. |
| "foreign" | P3 | GLOSSED-AT-FIRST-USE (but the gloss is FALSE) | "classifies every process outside the caller's ancestor chain as foreign" — a definition is given at first use, so it passes the mechanical test; the definition is wrong (§2 H1). |
| "custody root" / `custody_root` | P1, P4 | **FAILS in P1**; GLOSSED in P2 | P1: "a root whose plan does not parse, or whose `custody_root` is not its own directory, is UNKNOWN" — the reader sees a JSON field name and "root" used for the directory; that the plan carries a field naming the directory it must live in is never stated in P1. P2's §Terms table (line 410) glosses it, but that is outside the audited span. |
| "retained" | P1, P2, P4 | BUILT in P1 (late), FAILS in P2/P4 | P1 builds it: "…classifies its root as retained; the record lists every marker found" then "Classifying a root `retained` certifies only that a terminal record exists and that … the plan's span [is] inactive". Acceptable for P1. P2's heading "every discoverable root is retained" and P4's "a retained root whose plan span is still active … is ACTIVE too" use it unbuilt; P4 is a code comment so the bar is lower, but P2 is operator prose. |
| "arm" / "arming" | P2, P3 | **FAILS** | P2: "what stops an arm is any root whose…" — "arm" (install the night's launchd agents so the night fires at t0 unattended) is never glossed inside the audited span. Project-native reader knows it; the audience defined by the standard does not. |
| "check" | P1, P2, P3 | GLOSSED | P2: "The executable form is `python -m joulewise.evidence_night check --candidate STAGING`" — the command is shown at first use, which is a usable gloss. P1 item 4 does not name `check` at all (fine). |
| "entry checkout" | P1, P2, P4 | **FAILS** | P1: "with the entry checkout's timing constants" — never said that "entry checkout" = the git checkout whose `joulewise/evidence_night.py` is running (the one the operator is `cd`'d into), as opposed to the measurement clone. P2 says "from the root of the entry checkout" as if known. |
| "timing constants" | P1, P2 | **FAILS** | P1: "…with the entry checkout's timing constants, which may differ from the head that authored an older sibling plan" — which constants? (`PLAN_LEAD_S`, `COURIER_DEADLINE_S`, `COURIER_LOCK_FRESH_S`, and the dead-man bound). None is named in prose; only `PLAN_LEAD_S` appears, later, inside a parenthesis. |
| "dead-man" | P4 only (docstring of `plan_span_active` is outside scope; P4 does not use the word) | not in scope | Checked: the word does not occur in P1–P4. No verdict. |
| "terminal record" / "terminal state" | P1, P2, P4 | GLOSSED in P1 (by enumeration), FAILS in P2 | P1 enumerates the names before saying "terminal record exists". P2: "whose records show no terminal state" — the enumeration is in P1, cross-referenced only as "contract item 4". |
| "marker" | P1, P2 | GLOSSED | P1: "the record lists every marker found" immediately after the enumeration — a reader maps "marker" to those files. OK. |
| "chain is open" (P2) / "open chain" (P4) | P2, P4 | GLOSSED in P1 only | P1: "`night/chain.started` … without a regular `night/chain.exited` is ACTIVE". P2 says "whose chain is open" without the two filenames. Reader of P2 alone fails; with P1 adjacent, passes. Borderline; flagging. |
| `Refused:` | P2 | GLOSSED, but see §2 row R6 | "a `Refused:` exit" — the reader is told it is an exit shape. The actual shape for the manual command is a Python traceback ending `joulewise.evidence_night.Refused: …`, exit status 1 (probe N-cmd). Close enough to recognise; not FALSE. |
| "roots_under" | P2 | GLOSSED by the command | The dict literal `{"roots_under": "/Users/edr"}` and the next sentence "one row per `/Users/edr/night-custody/*/night_plan.json`" together let the reader rebuild the path construction (`<roots_under>/night-custody/*/night_plan.json`, `evidence_night.py:716`). OK. |
| "MCP helpers" / `codex mcp-server` | P3 | GLOSSED | "Every child whose command line contains `codex mcp-server` is a helper." Mechanically defined. OK. |
| "diagnostic" (in `never relabel it "diagnostic"`) | P3 | **FAILS** | Last sentence of the span. A reader does not know that "diagnostic" is a census output category (`observation.diagnostics`, `arm_census.py:239`) that the check also refuses on (`evidence_night.py:801`), nor why relabelling would be tempting. |

Summary: FAILS = 9 (every process; plan span; older sibling plan; session root; custody root [P1]; arm; entry checkout; timing constants; diagnostic), plus two borderline (retained in P2/P4; chain is open in P2). GLOSSED/BUILT = 7.

## 2. RULE-SENTENCE AUDIT

Notation: `probe X` refers to fixture cases in `/private/tmp/pedlens-15800/probe.py` (contents reproduced in §3). All fixture plans are schema v2, `receipt_class` `DIAGNOSTIC_NO_PACK`, `window_max_s` 9000, t0 ten days old unless stated. Constants read live: `PLAN_LEAD_S=480`, `COURIER_DEADLINE_S=300`, `COURIER_LOCK_FRESH_S=900`.

### P1 — contract item 4

| # | Sentence (condensed) | Code line | Probe | Verdict |
|---|---|---|---|---|
| C1 | Every `<roots_under>/night-custody/*/night_plan.json` is inventoried | `evidence_night.py:716` `glob("*/night_plan.json")` under `roots_under/night-custody` | probe B1: 16 fixture roots → 16 rows | TRUE |
| C2 | must be a regular non-symlink file; directories and special files refuse | `:717–719` `safe_path(plan)`; `if not plan.is_file(): raise Refused(...)` | probe J (dir) → `Refused: retained plan is not a regular non-symlink file`; probe L (FIFO) → same; probe K (symlink) → `Refused: symlink/path collision` | TRUE |
| C3 | `chain.started` regular file without regular `chain.exited` → ACTIVE and refuses | `:723–727` | probe B → `ACTIVE | chain.started without chain.exited`; verdict `fail` | TRUE |
| C4 | Otherwise an existing regular `courier.sent`/`result.json`/`chain.exited` or any regular `_refusal_paths` hit classifies retained; record lists every marker | `:707, :721–722, :729–730`, row `evidence` | probe A (courier.sent), R (result.json only), O (refusal.json + chain.exited → evidence lists both), Q (`calibration-refusal.json.x.json`) all `retained`; probe T (`courier.sent` is a directory) → not a marker → `UNKNOWN` | TRUE |
| C5 | Otherwise it is UNKNOWN and refuses | `:728` | probe C → `UNKNOWN | no terminal night record`, verdict `fail` | TRUE |
| C6 | `refusal-N.json` = any name matching `refusal-[0-9]*.json`, second glob at `run_night.py:282` | `run_night.py:282` (the `return sorted({…"refusal-[0-9]*.json"…` line) | `sed -n 282p` shows the glob on that line | TRUE |
| C7 | allocator writes N with min two digits, `{index:02d}` at `run_night.py:273`; `refusal-01.json`…`refusal-99.json`, then `refusal-100.json` | `run_night.py:273` `f"{path.stem}-{index:02d}{path.suffix}"` | line read; `f"{100:02d}"` = `100` | TRUE |
| C8 | a name with fewer digits, such as `refusal-7.json`, also counts | `run_night.py:282` glob | probe D → `retained`, evidence `['refusal-7.json']` (also probe V: `refusal-7x.json` counts, which the glob admits and the sentence does not exclude) | TRUE |
| C9 | retained root whose plan span is active by `plan_span_active`, evaluated on its own `night_plan.json` at observation time with the entry checkout's constants → ACTIVE and refuses | `:736–738`; `Storage(plan.parent)`; `from scripts.magistrate_watchdog import … plan_span_active` at `:712` resolves in the running checkout | probe G (t0 = now+300 s, `courier.sent`) → `ACTIVE | plan span active (scripts/magistrate_watchdog.plan_span_active)` | TRUE |
| C10 | plan does not parse, or `custody_root` not its own directory → UNKNOWN and refuses | `:733–735, :739–740` | probe H → `UNKNOWN | plan custody_root /private/tmp/elsewhere/H_moved is not …/H_moved`; probe I (`{not json`) → `UNKNOWN | plan unreadable: JSONDecodeError…`; deep-JSON probe (200 000 nested objects) → `UNKNOWN | plan unreadable: RecursionError: Stack overflow…` | TRUE |
| C11 | Each row records its reason | `:741–742`; retained reason set at `:737` | every B1 row prints a non-null `reason` | TRUE |
| C12 | Discovery never removes a root, and has no fixed root count | no `unlink`/`rmtree` in `retained_roots` | probe B1: `rglob` listing identical before/after (`True`), 16 roots inventoried | TRUE |
| C13 | Classifying `retained` certifies only a terminal record + span inactive at observation time | `:729–738` | probe R (`result.json` alone → retained) shows no courier evidence is required | TRUE |
| C14 | …which is also the answer for a plan whose span has not yet begun (observation earlier than t0 − PLAN_LEAD_S) | `magistrate_watchdog.py:778` `if now < t0 - PLAN_LEAD_S: return False` | probe F (t0 = now+3600 s, `courier.sent`) → `retained`, same reason string | TRUE |
| C15 | it does not certify that the courier's delivery succeeded | same as C13 | probe R | TRUE |

### P2 — runbook §0.7, "Check it." through "Source:"

| # | Sentence (condensed) | Code line | Probe | Verdict |
|---|---|---|---|---|
| R1 | what stops an arm is any root whose chain is open, whose span is active, whose night agents are installed, or whose records show no terminal state | `evidence_night.py:723–738` (three of four); `:807–836` `night_agents` / `require_no_night_agents` (installed) | probes B, G, C; `night_agents` NOT EXECUTED (needs the clone's `.venv` and `launchctl`; out of budget and touches real LaunchAgents listing) | TRUE for the three classifier clauses; installed-agents clause read only |
| R2 | executable form is `python -m joulewise.evidence_night check --candidate STAGING`, whose `night_agents` and `retained_roots` items must both pass | `:911` `inspect("night_agents", …)`, `:918` `inspect("retained_roots", …)`; `:1394,1404` register `check` | `grep -n 'inspect("night_agents"\|inspect("retained_roots"'` → 911, 918 | TRUE |
| R3 | with every inventoried root classified `retained` (`ACTIVE` and `UNKNOWN` refuse) | `:743–744` verdict = all rows `retained` | probe B1 verdict `fail` with mixed rows; probe A-only verdict `pass` | TRUE |
| R4 | manual command `python3 -B -c '… e.retained_roots({"roots_under": "/Users/edr"}) …'` prints one row per plan with `classification`, `reason`, full marker paths, then `verdict` | `:741–744` | ran the command verbatim with `roots_under` = fixture (output in §3): keys `plan, classification, reason, evidence` per row; top-level `inventory, now_epoch_s, verdict` | TRUE (`now_epoch_s` also printed; omission, not contradiction) |
| R5 | Every row must read `retained`; an `ACTIVE` or `UNKNOWN` row … stops the arm | `:743–744`; `check` marks `retained_roots` fail → `armable` False (`:923–924`) | probe B1 | TRUE |
| **R6** | **a `Refused:` exit (for example a symlink anywhere under a root) … stops the arm** | `safe_path` (`:57–61`) is applied only to: the plan path (`:717`), `night/<terminal name>` (`:721`), refusal-glob hits (`:722`), `night/chain.started`, `night/chain.exited` (`:723–724`) — and their ancestors | probe S: `<root>/night/stray → /etc/hosts` and `<root>/unrelated → /etc/hosts` with `courier.sent` present → row `retained`, verdict **`pass`**, no refusal. Probe N (symlinked `night/` dir) and probe W (symlinked `courier.sent`) do refuse. | **FALSE.** Same-signature recurrence: the sentence states a broader refusal than the classifier beside it implements. A symlink is refused only if it is the plan file, `night/`, a checked marker name, a refusal-glob hit, `chain.started`/`chain.exited`, the root directory itself, or an ancestor of any of those. |
| R7 | Do not move or edit a root to change its row | policy, not code | n/a | not a behaviour claim |
| R8 | This is the same function `check` runs (contract item 4), evaluated at the current time with the entry checkout's timing constants, so it sees the span rule | `:918` calls `retained_roots(state)` with `now_epoch_s=None` → `time.time()` (`:714`); manual call likewise | `:918` read; manual run printed `now_epoch_s` ≈ wall clock | TRUE |
| R9 | Source: … the shell loop … was replaced by the direct call … after it printed `retained` for a symlinked `night/` directory that the classifier refuses | `:721` `safe_path(night / name)` walks ancestors, so a symlinked `night/` refuses | probe N → `Refused: symlink/path collision: …/N/night/courier.sent`; the runbook command form exits status 1 with that message as the traceback's last line | TRUE (for the "classifier refuses" clause; the historical clause about the old loop is not testable here) |
| R10 | (manual `Refused:` shape) | `main()` at `:1410` prints `REFUSED: …` and returns 2 only for the CLI; the manual `-c` form bypasses `main` | ran the manual form on probe N: Python traceback, last line `joulewise.evidence_night.Refused: symlink/path collision: …`, exit status 1 | TRUE-ish: the word `Refused:` does appear; the exit is an uncaught exception, not the CLI's `REFUSED:`/rc 2. Not a contradiction, but the reader who expects a one-line `REFUSED:` will see a traceback. |

Sentences in the P2 span before "Check it." (glob, staging, `--plan required=True`, installer path rule) were outside the ruled scope but were spot-read: `magistrate_watchdog.py:286` `self.root.parent.glob("*/night_plan.json")`; `run_night.py:3697` `required=True`; `night_agent_install.py:588` resolved plan path must equal `<custody_root>/night_plan.json`. All TRUE by line read; not probed.

### P3 — handback pre-check step

| # | Sentence (condensed) | Code line | Probe | Verdict |
|---|---|---|---|---|
| **H1** | **the census classifies every process outside the caller's ancestor chain as foreign** | `arm_census.py:237` `foreign = (set(observation.hit_pids) & records.keys()) - exempt`; hit PIDs come from `night_gate.py:90` `AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3")`; `exempt = set(own)` (`:222`) plus REHEARSAL_STUB idle exemptions (`:230–234`), inactive here because `clone_census` classifies with `receipt_class='DIAGNOSTIC_NO_PACK'` (`evidence_night.py:762`) | probe Y: synthetic tree root `claude` 100 → caller 200, `codex mcp-server` 300 (child 310 `sleep`), `zsh` 400, unrelated `sleep` 500; `hit_pids=(100,300)`. Result: `own_pids=(100,200)`, `foreign_pids=(300,)`. PIDs outside the ancestor chain: `[1,300,310,400,500]`; classified foreign: `[300]` only. | **FALSE.** Same-signature recurrence (doc states a rule the cited code does not implement). Correct rule: every process whose full command line matches `codex`, `claude` or `t3` (the census argv), that has a readable process record, and that is not an ancestor of the caller, is foreign. Also worth saying: a helper's *descendants* (310) are not themselves foreign unless they match the argv; they are killed only because the handback's procedure walks descendants. |
| H2 | the tracked check refuses on any foreign PID | `evidence_night.py:800–801` verdict `fail` if `verdict["foreign_pids"]`; `:929–932` re-raises the census reason as `Refused` | line read; NOT EXECUTED end-to-end (needs a prepared candidate + clone `.venv`) | TRUE by line read |
| H3 | `pgrep -lP` prints process names only | `man pgrep` `-l`: "print the process name … If used in conjunction with -f, print … the full argument list" | live: `pgrep -lP <pid>` → `23712 sleep`; `pgrep -flP <pid>` → `23712 sleep 40` | TRUE |
| H4 | `pkill -P` reaches immediate children only | `man pgrep`/`pkill` `-P ppid`: "Restrict matches to processes with a parent process ID in the … list" | manual read; not executed (no kill wanted) | TRUE by manual |
| H5 | `pgrep -flP $ROOT` lists the session root's children with full command lines | as H3 | live output `23709 zsh -c sleep 40 & sleep 41 & wait` for a child of this shell | TRUE |
| H6 | `descendants()` enumerates all descendants at every depth | zsh function in the passage | ran verbatim against a live tree (zsh 23709 → sleep 23712, sleep 23713): printed all three with correct ppids | TRUE |
| H7 | helper loop: `victims=($h $(descendants $h))`, prints `helper $h: TERM a,b,c` | zsh in the passage | ran verbatim with the kill replaced by print: `helper 23709: TERM 23709,23712,23713` | TRUE (kill line not executed by design) |
| H8 | wait loop `for d in $(descendants $ROOT); do ps -o pid=,command= -p $d; done \| grep -F 'codex mcp-server'` | as H6 | same descendants function; `ps -o pid=,ppid=,command=` form executed on each descendant | TRUE |
| H9 | If the census still reports any descendant of the session root as foreign, stop | policy sentence; the check already refuses (H2) | n/a | consistent with H2 |
| H10 | never relabel it "diagnostic" | `arm_census.py:239` diagnostics tuple; `evidence_night.py:801` refuses on `verdict["diagnostics"]` too, so relabelling would not even clear the check | line read | consistent (the sentence's motivation is not stated; see first-use row) |

### P4 — code comment above `TERMINAL_NIGHT_RECORDS`

| # | Sentence (condensed) | Code line | Probe | Verdict |
|---|---|---|---|---|
| K1 | Several families can coexist (a refusal written mid-chain, then chain.exited) | `:721–722` markers list concatenates both families | probe O → evidence `['chain.exited', 'refusal.json']` | TRUE |
| K2 | an open chain takes precedence over every marker | `:725–726` chain_open branch first | probe P (`courier.sent` + `result.json` + `chain.started`) → `ACTIVE | chain.started without chain.exited` | TRUE |
| K3 | a retained root whose plan span is still active by the watchdog's rule is ACTIVE too | `:736–738` | probe G | TRUE |
| K4 | The installer refuses re-admission on the same names (night_agent_install) | `night_agent_install.py:1134–1135` lists `receipt.json, result.json, chain.started, chain.exited, courier.json, courier.sent` | grep only; NOT EXECUTED | TRUE by grep, noting the installer's list is a superset (`receipt.json`, `courier.json`, `chain.started`) of the three names here; "the same names" reads as "these three among others" |
| K5 | the refusal names come from the driver's own `run_night._refusal_paths`, and the span rule from the watchdog's `plan_span_active` — both entry-checkout modules, evaluated with the entry checkout's constants | `:712–713` imports; constants at `magistrate_watchdog.py:86–89` | probe script imported the same modules from cwd and printed `PLAN_LEAD_S 480` | TRUE |

### Unittest (single permitted run)

```
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night -k retained -k discovery -k span -k realpath -k deep_json
Ran 9 tests in 10.804s
OK
```

## 3. Executed evidence (verbatim excerpts)

Probe script `/private/tmp/pedlens-15800/probe.py` output (batch 1, 16 roots, `now` fixed):

```
PLAN_LEAD_S 480 COURIER_DEADLINE_S 300 COURIER_LOCK_FRESH_S 900
[B1] A_courier: retained | reason=terminal record present; plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active) | evidence=['courier.sent']
[B1] B_chain_open: ACTIVE | reason=chain.started without chain.exited | evidence=[]
[B1] C_no_markers: UNKNOWN | reason=no terminal night record | evidence=[]
[B1] D_refusal7: retained | reason=terminal record present; ... | evidence=['refusal-7.json']
[B1] E_refusal01: retained | ... | evidence=['refusal-01.json']
[B1] F_future_far: retained | reason=terminal record present; plan span inactive at observation time (...) | evidence=['courier.sent']     # t0 = now+3600
[B1] G_future_near: ACTIVE | reason=plan span active (scripts/magistrate_watchdog.plan_span_active) | evidence=['courier.sent']         # t0 = now+300
[B1] H_moved: UNKNOWN | reason=plan custody_root /private/tmp/elsewhere/H_moved is not /private/tmp/pedlens-15800/roots/night-custody/H_moved | evidence=['courier.sent']
[B1] I_badjson: UNKNOWN | reason=plan unreadable: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1) | evidence=['courier.sent']
[B1] O_coexist: retained | ... | evidence=['chain.exited', 'refusal.json']
[B1] P_open_wins: ACTIVE | reason=chain.started without chain.exited | evidence=['courier.sent', 'result.json']
[B1] Q_calib: retained | ... | evidence=['calibration-refusal.json.x.json']
[B1] R_result_only: retained | ... | evidence=['result.json']
[B1] T_marker_dir: UNKNOWN | reason=no terminal night record | evidence=[]
[B1] V_refusal_7x: retained | ... | evidence=['refusal-7x.json']
[B1] verdict=fail keys=['inventory', 'now_epoch_s', 'verdict']
[B1] tree unchanged after discovery: True roots: 16
[J_plan_is_dir] Refused: retained plan is not a regular non-symlink file: .../J_dir/night_plan.json
[K_plan_symlink] Refused: symlink/path collision: .../K_link/night_plan.json
[L_plan_fifo] Refused: retained plan is not a regular non-symlink file: .../L_fifo/night_plan.json
[N_night_dir_symlink] Refused: symlink/path collision: .../N_nightlink/night/courier.sent
[S_symlink_elsewhere_under_root] S_stray: retained | reason=terminal record present; plan span inactive ... | evidence=['courier.sent']
[S_symlink_elsewhere_under_root] verdict=pass keys=['inventory', 'now_epoch_s', 'verdict']
[W_marker_is_symlink] Refused: symlink/path collision: .../W_marker_link/night/courier.sent
[X_tmp_ancestor] Refused: symlink/path collision: /tmp/pedlens-x
[Y_census] own_pids (100, 200) foreign_pids (300,) workloads ()
[Y_census] pids outside ancestor chain of 200: [1, 300, 310, 400, 500] -> classified foreign: [300]
```

Deep-JSON plan (`{"a":` × 200 000), root A alone:

```
[('UNKNOWN', 'plan unreadable: RecursionError: Stack overflow (used 16352 kB) while ')]
```

Runbook manual command, verbatim form with `roots_under` = fixture, retained-only root:

```
{
 "inventory": [
  {
   "plan": "/private/tmp/pedlens-15800/roots/night-custody/A/night_plan.json",
   "classification": "retained",
   "reason": "terminal record present; plan span inactive at observation time (scripts/magistrate_watchdog.plan_span_active)",
   "evidence": ["/private/tmp/pedlens-15800/roots/night-custody/A/night/courier.sent"]
  }
 ],
 "now_epoch_s": 1790059453.950698,
 "verdict": "pass"
}
rc=0
```

Same command with a symlinked `night/` root present:

```
  File ".../joulewise/evidence_night.py", line 60, in safe_path
    raise Refused(f"symlink/path collision: {path}")
joulewise.evidence_night.Refused: symlink/path collision: /private/tmp/pedlens-15800/roots/night-custody/N/night/courier.sent
rc=1
```

Handback shell commands, live tree (`ROOT` = this shell, child `zsh -c 'sleep 40 & sleep 41 & wait'`):

```
-lP:   23712 sleep / 23713 sleep
-flP:  23712 sleep 40 / 23713 sleep 41
root children (pgrep -flP): 23709 zsh -c sleep 40 & sleep 41 & wait
all descendants at every depth:
23709 23506 zsh -c sleep 40 & sleep 41 & wait
23712 23709 sleep 40
23713 23709 sleep 41
helper loop (dry: echo instead of kill): helper 23709: TERM 23709,23712,23713
```

Fixture construction for probe S (the FALSE case for R6): root `S_stray` with a valid ten-day-old plan, `night/courier.sent` regular file, plus `night/stray -> /etc/hosts` and `<root>/unrelated -> /etc/hosts`. Fixture for probe Y: `KernelProcessRecord` rows `(1,0) (100,1) (200,100) (300,100) (310,300) (400,100) (500,1)`; `DarwinProcessRecord`s for 100 (`/usr/local/bin/claude`, argv `claude`), 200 (`python3 -m joulewise.evidence_night check`), 300 (`/usr/local/bin/codex`, argv `codex mcp-server`), 310 (`sleep 9`), 400 (`zsh`), 500 (`sleep 99`); `hit_pids=(100,300)`; `diagnostics=()`; classified with `receipt_class='DIAGNOSTIC_NO_PACK'`, `caller_pid=200`.

## 4. PROPOSED wording (for the cold gate; the lead does not author these)

**PROPOSED for R6 (runbook §0.7):** replace "a `Refused:` exit (for example a symlink anywhere under a root)" with: "a `Refused:` exit — the classifier refuses when any path it inspects, or any directory above it, is a symbolic link: the `night_plan.json` file, the root's `night/` directory, `night/courier.sent`, `night/result.json`, `night/chain.exited`, `night/chain.started`, or any file matched by the refusal name patterns (contract item 4). A symbolic link elsewhere under a root, such as `night/notes` or `<root>/scratch`, is not inspected and does not refuse."

**PROPOSED for H1 (handback pre-check):** replace "the census classifies every process outside the caller's ancestor chain as foreign" with: "the census lists every process whose full command line contains `codex`, `claude` or `t3` (the exact argv is `night_gate.AGENT_CENSUS_ARGV`), and classifies each listed process that is not an ancestor of the checking process as foreign (`arm_census.classify_arm_census`). A listed process that cannot be read is reported as unknown, which the check also refuses. Processes whose command line matches none of the three words are not listed and are not foreign, whatever their ancestry."

**PROPOSED first-use glosses (P1 item 4), each one clause:**
- "plan span": "the interval in which the watchdog treats the plan as live: from 480 s before `t0` (`PLAN_LEAD_S`) until the chain has exited and `t0 + window_max_s + 300 s` has passed, extended to the plan's dead-man bound + 900 s unless `night/courier.sent` exists (`scripts/magistrate_watchdog.plan_span_active`)."
- "older sibling plan": "another `night-custody/<plan-id>/night_plan.json` beside the candidate's, authored by an earlier checkout."
- "entry checkout": "the git checkout whose `joulewise/evidence_night.py` is executing, as opposed to the measurement clone the plan points at."
- "timing constants": name the four (`PLAN_LEAD_S`, `COURIER_DEADLINE_S`, `COURIER_LOCK_FRESH_S`, and the dead-man bound) at first use.

**PROPOSED for P3 "session root":** "Let `ROOT` be the PID of the interactive `claude` process this session is running in (`echo $PPID` from the session's shell, or the outermost `claude` in `pgrep -lf claude` whose argv carries no `-p`)."

**PROPOSED for P3 `never relabel it "diagnostic"`:** append "(`diagnostic` is the census's own category for a listed process it could not read; the check refuses on diagnostics as well as on foreign PIDs, so the relabel would not clear it)."

## 5. Not executed

- `check` end-to-end (needs a prepared candidate, the measurement clone's `.venv`, and `launchctl`): NOT EXECUTED; rows R2, H2 rest on line reads.
- `night_agents` / installed-plist fence: NOT EXECUTED (touches the real LaunchAgents listing).
- The handback's `kill -TERM` line: deliberately replaced by `print` in the live run.
- Installer re-admission refusal (K4): grep only.

Fixtures under `/private/tmp/pedlens-15800/` left in place for the gate's inspection; nothing else on disk was created or modified. Wall time ≈ 16 min.
