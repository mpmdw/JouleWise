Opus 5.5 contract-lens refuter for cold gate NTP-ENFORCE-DESIGN-01-A2 (09-28, Opus-only deskwork session under Ed's order). The Fable JUDGE half was NOT run in this session (Ed: Opus only); this file is the refuter half only and is not a ruling.

# A2 refuter: is R3 the same defect as E2, and what a fix round 2c must contain

**Verdict.** CONCUR that R3 is E2 again and that one fix round 2c is warranted. DISSENT from a 2c scoped to the one call site R3 names. The same disagreement between the two records has a third writer, the chain's own refusal (finding 2). It also has a variant in which the proof passes (finding 3). A 2c that patches only the clean-up step would leave the chain's own refusal for a third round, so 2c must be scoped by one rule over every refusal document, as §6 sets out.

## 0. Contamination disclosure

1. **Put into my context before the task.** The owner's global instruction file, the project's instruction files, and the index of the owner's memory store. I also received the lieutenant's brief for this task, which names the charge and the artefacts. I took the writing standard from these as form. Every finding below rests on a file I read or a command I ran.
2. **Read.** The charge (47). Addendum A1 (38) in full. Ruling 21: §4.3 and a search for exit-status text. Reports 44, 45 and 46 in full. Items 115–127 of the activation record (00). Astra's probe `46-probes/probe_refusal.py`, which I read and did not run. In the candidate I read the head code named below, from a copy made with `git archive`.
3. **Not opened.** `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, skill files and memory files.
4. **Executed.**
   - Read-only `git` in the N1 worktree: `rev-parse`, `show`, `log`, `diff --stat`, `archive`.
   - `git archive` of `36e8ba6e` into `p1/tree` and of `3ad82b43` into `p1/old`.
   - My probes, run as `python3 -B` (Homebrew 3.14.7) with the guard of record 30 on `PYTHONPATH`. They also install an audit hook that raises before any `sudo`, `powermetrics`, `systemsetup`, `sntp`, `/usr/bin/log`, `ioreg` or `pmset` can start.
   - One unit module run whole, and two live tests run by ID, under a stricter guard of my own in `p1/guard`.
   - `ps` and `pgrep` listings.
   - One sleeper, 3 s long, started through the repository's `.venv` interpreter, then killed.
   - Read-only `plutil` on the magistrate's launch-agent file.
   - `json` reads of five `night_plan.json` files under `/Users/edr/night-custody`, to learn their measurement roots.
5. **Not executed.** Any real sampler, `sudo`, network-time command, log query or battery read. No `launchctl`, no subagent. No repository file was written.
6. **Head verified.** `git -C …/JouleWise-wt-ntp-n1-d528efb2 rev-parse HEAD` printed `36e8ba6e345653e4fb4ac54f711dc49b27c1d30c`.
7. **Where things are.** Scratch, probes and logs are all in `…/scratchpad/p1/`: `probe_p1.py`, `probe_r2.py`, `probe_r2b.py`, `probe_r3_base.py`, and the `*.log` files. Every line number below is at `36e8ba6e` unless it names another commit.

## 1. Words used

| Term | Meaning |
|---|---|
| **Query, ON, OFF** | The driver's one reading of the clock daemon's log, and the two commands that switch "set time automatically" on and off. |
| **Proof** | `_prove_capture_absent` (`run_night.py:3939`). It asks whether any process that can write a recording is still running. **P1**: the chain's own process group is empty. **P2**: every group in the night's registry file is empty. **P3**: one listing of every process on the machine (a **sweep**) shows no command line naming the sampler or a path of the night. |
| **[K]** | The driver's clean-up of an idle night's registered children, `_evidence_cleanup_error` (`:1377`). Round 2 moved it before the proof (`:3347`), as A1 C3 ordered. Besides signalling groups, it can **write a refusal document** (`:1423–1424`). |
| **Refusal document** | `refusal.json`, or a numbered sibling `refusal-NN.json`. Each is created exclusively, so a second writer gets the next number (`:280–285`). |
| **The two records** | `result.json`, which holds the night's verdict and `aborted_reason`, and `refusal.json`. |
| **E2** | Round 2b's defect: after a failed proof, `result.json` said `night_chain_alive` while `refusal.json` kept an earlier cause. The lead's ruling in item 118 was that **both records carry `night_chain_alive`, and any earlier cause is kept inside the evidence**. |
| **E2's signature** | The records name different causes after a failed proof. |
| **C7 path** | The path taken when the driver cannot prove that the chain itself ended (`termination_proven` is false). There the proof never runs (`:3345`). |
| **Idle route** | A night whose receipt row C5 says `quiet_predicate_evidence`. Only on this route does [K] act (`:1397–1401`). |

## 2. Findings

Each finding has a location at `36e8ba6e`, a command I ran, and an excerpt of what it printed.

**F1. R3 is real, and it is E2's signature at another writer.** When [K] finds that the idle chain left no outcome, it writes `refusal.json` itself (`:1414–1424`). The proof then fails. `_capture_unproved_abort` finds an earlier document only through `prior["document"]` (`:3531`), and only the deadline watchdog sets that key. So the result step allocates a second, numbered document (`:3417–3424`).

- Command: `probe_p1.py <tree> R3`, case R3a. It calls the production [K], `_capture_unproved_abort`, `_write_driver_refusal` and `_write_result` in the order of `:3345–3458`.
- Output (`probe_p1-head.log`): `refusals: [('refusal-01.json','night_chain_alive'), ('refusal.json','night_probe_error')] | result: REFUSED night_chain_alive`. The output is the same whether [K]'s clean-up is proven or not.
- Control, the watchdog case R3d that round 2b fixed: `[('refusal.json','night_chain_alive')]`.

This is the E2 signature, and it escapes the same mechanism E2's fix relies on. **A 2c on it is the second fix round on E2.**

**F2. The same signature has a third writer, the chain itself, and neither R3 nor 2b names it.** The idle-night chain writes `refusal.json` with the reason `night_probe_error` whenever its own final clean-up is not proven (`quiet_predicate_campaign.py:1802–1805`). An unproven clean-up is the likeliest real case in which a capture process survives, so it is exactly when the driver's proof fails: A1 §3.3, third bullet.

- Command: case R3b. The production `q.write_refusal` writes the chain's document, then the proof fails.
- Output: `refusals: [('refusal-01.json','night_chain_alive'), ('refusal.json','night_probe_error')]`. The chain-alive document's evidence keys are `['check','matches']`, with no `prior_abort`, so **nothing in the new document points to the earlier one**.

A 2c patched at [K] alone leaves this instance, and it would be found as round 3.

**F3. Moving [K] earlier (A1 C3) also changes which document is named `refusal.json` when the proof passes.** On `3ad82b43`, the result step wrote first (`:3414`) and [K] ran later, in the courier's preparation (`:1426`). By then a document existed, so [K] wrote none.

- Command: `probe_r3_base.py` on the `3ad82b43` copy, for an agent-census stop of an idle chain that left no outcome.
- Output (`probe_r3-base.log`): `[('refusal.json','night_aborted_agent_present')]`.
- The same stop on the head (R3c, proof passes): `[('refusal-01.json','night_aborted_agent_present'), ('refusal.json','night_probe_error')]`, with result `ABORTED night_aborted_agent_present`.

This is not E2's signature, because no proof failed. It has the same root: C3 moved a refusal writer ahead of the result step. The cure of F1 should remove this root, not only its symptom.

**F4. No existing test reaches [K] on a failed proof.** I ran `tests.test_run_night.NightDriverTests.test_{deadline,census}_stop_with_detached_child_blocks_query_and_on` under `p1/guard`: `Ran 2 tests … OK` (`t4-head.log`).

Their helper asserts a single document (`tests/test_run_night.py:1197`). They pass only because their receipt does not satisfy [K]'s idle-route condition: `grep quiet_predicate_evidence tests/test_run_night.py` finds no such receipt fixture. That last point is read, not executed.

**F5. The disagreement makes no record false, costs no window, and cannot put the query or ON beside a capture.**

- No query or ON can run: F1–F3 all occur after the proof decided, and the query and ON are gated at `:3362` and `:3378`.
- Each document is true of its own writer.
- `result.json` lists every document in `refusal_documents` (`:1671`). F1's output shows both documents listed.
- Every consumer I read treats the documents as a set: the courier prompt (`docs/process/NIGHT_COURIER_PROMPT.md:10–15`, "read every path in `refusal_documents` … discover all `refusal*.json`"), the installer (`night_agent_install.py:1231–1241`) and the retained-root inventory (`evidence_night.py:806–815`). These were read, not executed.
- The retry licence reads `result.json` and the gate receipt, never `refusal.json` (`arm_retry.py:213–226`).

So E2 is a defect in how complete and linked the records are, measured against the lead's item-118 rule. It is not D1. D1 is the query or ON running while a process that can write a recording is alive (A1 §3.4).

**F6. R1 is real at the head. No production writer can reach it.**

- **Where.** The driver's `_chain_never_launched` (`run_night.py:3553`) and recovery (`network_time_window.py:384`) both test `.get("pid") is None`, which a missing key also satisfies.
- **Command.** `probe_p1.py … R1`.
- **Output.**
  - `missing_both: driver …=True recovery=restored calls=['ON']`
  - `missing_pid: …=True recovery=restored calls=['ON']`
  - `pid_present: …=False recovery=chain_unproved calls=[]`

  The proof was never consulted, and ON ran.
- **Why no production writer reaches it.** All three production writers of a failed or never-launched claim write explicit nulls (`:611–612`, `:626`). The claim's file is created 0600 by the driver (`:577–580`). Only a foreign or forged claim can take this route, and deliberate forgery is out of scope (A1 §4.4).
- **Where it comes from.** It came in with round 2 (A1 §5 is new there). A1 §7.4 gives such a defect one fix round of its own without a cold gate.
- **The fix.** It is two conditions per site. The dead-man's copy of the same test (`:3611–3612`) is inherited and feeds the same recovery.

**F7. R2 is real only against a stand-in. On this machine it fails closed, by accident.**

- **The contract.** A **census** is one `pgrep -g` listing of process groups. By A1 §1, only "exit status 1 with empty output" means the group is empty.
- **The defect.** `_census_chunk` (`:3760–3775`) passes an exit-0 empty answer on to attribution, which runs `ps -p ""`, and `_attribute_pids` ignores that command's exit status (`:3784–3797`).
- **The real programs.**
  - Real `pgrep -lf -g 99990,99991 .` gives `exit 1 stdout ''`, so it never produces the case.
  - Real `ps -p ""` prints `ps: Invalid process id: <uninitialised bytes>` and exits 1 (seen with `xxd`).
  - In Python, that output raised `UnicodeDecodeError` in 200 of 200 runs (`probe_r2-head.log`). The proof pass then returns `(None, {'check':'P2','error':"UnicodeDecodeError…"})`, which means not proved.
- **With the stand-in.** With an injected `ps` that exits 1 with empty output, the same pass returns `(True, …)`, which reproduces Astra's result.
- **The single-group path** (`_group_census`, `:3700–3709`) is correct: `(False, [])`.
- **Worst case.** Even if P2 passed wrongly, P3 still runs. Only a journaled process with no capture signature would slip through, and that is A1's stated limit. The recorder is one such process (F12).
- **Summary.** R2 is inherited, can make no record false, and costs no window.

**F8. R4 is real by text and has no bearing on safety.**

- **Command.** `probe_p1.py … R4`.
- **Output.** A first pass whose clock reads +5.4 s gives `(True, {…,'passes':1})`. The worst-case budget is 4 s for up to 256 registered groups and 6 s from 257 groups.
- **Size.** The largest registry the code names is 113 journaled groups (`run_night.py:3712–3714`, A269). Real passes take 0.04–0.06 s (45 §4).
- **Freshness.** A late success is still fresh evidence. Each check is taken when it runs, P3 last, and P1 found the chain's group empty, so nothing can join it afterwards.
- **The text.** A1 §4.2's "repeated for up to 5 s" bounds the repeats; it does not bound one pass. The docstring states the bound (`:3948–3951`).
- **Disposition.** Not N1's to fix. It is at most a nit.

**F9. R5 is real at the head, inherited from main, and outside A1's exit-status rule.**

- **Command.** `probe_p1.py … R5`.
- **Output.** `_finish_reporting(EXIT_REFUSED, allow_courier=False) -> 6` (`:1896–1907`, reached from `:3475–3486`).
- **Inherited.** `git show <c>:tests/test_run_night.py | grep -c EXIT_COURIER_FAILED` counts 6 on `e7371399`, 7 on `3ad82b43`, 7 on the head and 6 on `origin/main`. The C7 return is on main at `run_night.py:3325`.
- **Outside A1.** On the C7 path the proof never runs (`:3345`). So A1 §4.2's sentence "the driver's exit status is the refusal status" does not reach it, and A1 C7 says **unchanged**.
- **Nothing downstream is wrong.** `result.json` is already REFUSED on this path (`:3425–3427`). No query or ON runs. The retry licence does not read the exit status.
- **Disposition.** Changing it would flip six assertions that existed before N1, which is A1 §7.2 stop condition 3. Not N1's.

**F10. NIT-1 is confirmed by arithmetic and costs liveness only.** `probe_p1.py … R4` prints the latest start of a further pass as 2.8 s with no registry, 1.8 s with one group, and 0.8 s with two to 256 groups. This agrees with 45 §4. A refusal it causes is not false, because the process was alive when the proof refused.

**F11. NIT-2 is confirmed, and matters less on real plans than 45's example suggests.**

- **Command.** `probe_p1.py … NIT2`.
- **Output.** `True` for `/bin/zsh /Users/edr/code/JouleWise-wt-other/run.sh` and for `vim /Users/edr/code/JouleWiseNotes.txt`, both matched through `:3825`.
- **Real roots.** The five newest real plans have dedicated measurement roots under `/Users/edr/night-custody/measurement/…` or `/Users/edr/JouleWise-measurement-…`, not the canonical repository.
- **The magistrate watchdog.** It names `/Users/edr/code/JouleWise/scripts/magistrate_watchdog.py` (launch-agent file), so it would not match.
- **Disposition.** It fails in the safe direction. A boundary check is a nit.

**F12. NIT-3 is confirmed.**

- **Command.** A sleeper started through `/Users/edr/code/JouleWise/.venv/bin/python`.
- **Output.** `ps` shows `/opt/homebrew/Cellar/python@3.13/…/Python.app/Contents/MacOS/Python -B -c …` (`nit3.log`).
- **Consequence.** The recorder, started at `quiet_predicate_campaign.py:1633`, carries no capture signature, so only P2 sees it.
- **Disposition.** It belongs to seat N3's lane, as 45 says.

**F13. Nothing blocks the full gate's substance, but four conditions stand in its way.**

- **(a) The powermetrics fence must land first** (item 124). Without it, a whole-suite run for the gate ledger can start a real sampler.
- **(b) The lead still owes A1 §7.5's bookkeeping** (item 115): the desk step in the night hand-back document, and `network_time_window.py` added to N3's scope.
- **(c) The branch diff is wider than N1.** `git diff --stat origin/main...36e8ba6e` shows 193 files across 61 commits. They include a records-branch merge (`0c2b1fbb`) and a lead bookkeeping commit (`fbf0007d`) that edits `tests/test_gen_state.py`, which is outside the nine files. The PR must be scoped, or the records must land first, before the ledger's scope row can be checked.
- **(d) N3's chain-side ON is not in N1's way.** Its ON before clean-up (`quiet_predicate_campaign.py:1767–1768`) does not block N1, because `NETWORK_TIME_ENFORCED_KINDS` is empty at the head (`network_time_window.py:28`). Every night that is not a rehearsal is then refused as `route_unenforced` (`run_night.py:3256–3269`). The lead should tell the owner plainly that **merging N1 stops real windows until a kind's consumer lands** (ruling 21 §4.4 rules this; it is not new). N3's ordering must be fixed before `quiet_predicate_evidence` enters that set.

## 3. Report 46's five findings

| Finding | Real at the head? | Can it let a query or ON run beside a capture? | Can it make a record false? | Whose |
|---|---|---|---|---|
| R1 | Yes (F6) | Only with a claim no production writer makes | No, in production | **N1, in 2c** (cheap; it came in with round 2) |
| R2 | Yes, against a stand-in; fails closed with the real `ps` (F7) | No: P3 still runs | No | Optional in 2c (fails closed only), otherwise a registered limit. It is inherited from A269. |
| R3 | Yes (F1), and wider (F2, F3) | No | No: incomplete linkage (F5) | **N1, in 2c**, scoped by the rule of §6 |
| R4 | Yes by text (F8) | No | No | Not N1's; nit |
| R5 | Yes (F9) | No | No | Not N1's; a lane for exit-status meanings, or a registered limit |

**Is R3 genuinely E2 at another call site?** Yes. It has the same signature and escapes the same discovery key (`:3531`). The same holds for F2's writer, which R3 did not name. It is the "another missed call site" pattern, so this cold gate is correctly convened.

## 4. Report 45's three nits

| Nit | Status |
|---|---|
| NIT-1 | Confirmed (F10). Liveness only. **Not in 2c**, for the reasons of §5, question 3. |
| NIT-2 | Confirmed (F11). Safe direction; the real measurement roots do not collide. Nit. |
| NIT-3 | Confirmed (F12). N3's lane. |

## 5. The charge's five questions, from the contract lens

**1. Is R3 the same defect as E2, and may 2c proceed?** Yes to both, with the scope of §6.

**2. Which findings are N1's now?** R1 and R3 (with F2 and F3) belong in 2c, and R2 optionally. R4, R5, NIT-1, NIT-2 and NIT-3 are registered limits or belong to other lanes. None of the eight can put the query or ON beside a process with a capture signature. None makes a record false; E2's class leaves the records incompletely linked (F5).

**3. Should the retry horizon be widened?** Not in 2c. Changing the loop at `:3961–3974` would be a second fix round on **E1**, round 2b's starved-timeout defect, stacked into a round that is already the second on E2. The case for waiting also rests on [K]:

- [K] runs first, and waits for the registered groups to vanish.
- A sampler started as `sudo -n powermetrics` is journaled under the `sudo` group. `sudo` waits for its command to end.
- So a sampler that is already ending should be gone before the proof starts.

That argument is NOT EXECUTED: no real `sudo`, and A1 §9 left `sudo`'s grouping untested.

- **Recommended now.** Register the horizon (0.8, 1.8 and 2.8 s) as a limit, and record the proof's `passes` and duration on the first real nights.
- **If a refusal ever shows a process that ended within 5 s,** widen with Astra's form: reserve one full 1 s listing before each listing, abandon a pass that cannot fit, return the last complete pass's evidence, and check the deadline before accepting success. That keeps E1's rule that no listing gets less than 1 s, and keeps the bound near 5 s. It is better than 45's "overrun by one pass", which is bounded by 9 s per proof, and so 18 s per night, since the proof runs twice.

**4. The stop conditions for 2c and its delta.**

- **If E2's signature recurs after 2c** (a refusal document present when the result is written that neither carries `night_chain_alive` nor is linked from the document that does), that is two consecutive rounds with the same signature. There is no 2d. The next spend is a **bounded consult** on the meaning of the records: is `refusal.json` the night's one cause, or one member of a set? It is not the custody redesign, because E2 cannot reach a capture (F5).
- **If D1's signature appears,** A1 §7.4 applies unchanged: no round, and a consult on who owns the capture processes.
- **A defect of a new kind that 2c introduces** gets one round of its own (A1 §7.4).
- **Nothing here goes to the owner.**

**5. After 2c and a clean delta, is N1 ready for the full gate?** Yes on substance, once F13's conditions (a) to (c) are met, and with (d) disclosed to the owner.

## 6. What a 2c round must contain

**Scope.** WRITE_SCOPE is `scripts/run_night.py`, `joulewise/network_time_window.py`, `tests/test_run_night.py` and `tests/test_network_time_window.py`, all within A1's nine files.

**A. The E2 class, R3 with F2 and F3: scope by one rule, not by call site.** The judge must first pick the rule. This lens proposes **(ii)**.

- **(i) The lead's item-118 rule, read literally:** `refusal.json` itself says `night_chain_alive`. That means replacing any earlier `refusal.json`, including one the chain wrote (F2). It widens the one exception to "refusal documents are never rewritten" from the driver's own watchdog document to documents that other programs wrote.
- **(ii) Proposed:**
  - `result.json` names `night_chain_alive`.
  - Exactly one document the driver writes carries `night_chain_alive`, and it is listed in `refusal_documents`.
  - Every refusal document already present is kept byte for byte and **named in that document's evidence**, for example as `prior_documents` holding each name and reason.
  - The watchdog's replacement from round 2b stays as it is.

  This meets A1 §4.2's literal text, which requires "the night's result" to carry the reason. Every consumer already reads the documents as a set (F5). Under (ii), the fallback for a failed replacement (`:3537–3544`) is consistent. Adopting (ii) amends the lead's item-118 ruling, which is the judge's call and not mine.
- **Under either rule:** the early call of [K] at `:3347` must **not write a refusal document**. The later call (`:1453`) still guarantees that one exists, as it did on `3ad82b43`. That removes F3's root and F1's writer together.
- **Regressions.** Each goes through `run_night` with an **idle-route receipt**, so that [K] really runs, and with a real separately grouped child that carries a signature (A1 §4.7's rules). Each must fail by assertion on `36e8ba6e`.
  - (a) An agent-census stop of a chain that leaves no outcome, while the child lives.
  - (b) A chain that writes its own refusal (the unproven-clean-up path) and exits, while the child lives.
  - (c) An agent-census stop with no survivor: `refusal.json` gives `night_aborted_agent_present`, as on `3ad82b43`.
  - Removing the link, or restoring [K]'s early write, must turn (a) to (c) red by assertion.

**B. R1: require both keys to exist and to be null.** Do this at `run_night.py:3553` and `network_time_window.py:384`, and preferably at the dead-man's copy (`:3611–3612`). Regression: my R1 missing-key cases give `chain_unproved` with no ON; on the head they give `restored` (F6).

**C. R2, optional:**

- An exit-0 empty census is not proved.
- No attribution call with an empty list of process numbers.
- `_attribute_pids` checks its exit status.

It fails closed only, but it tightens A269's clean-up helper too. Regression: F7's injected case gives not proved.

**D. Stop conditions for the seat.** The seat keeps A1 §7.2's conditions 1–5 and adds three:

- (6) The rule needs a document the driver did not write to be rewritten (unless the judge picks (i)).
- (7) Any change to the retry loop of the proof (`:3961–3974`).
- (8) The seat finds a refusal writer that can precede the result at a failed proof other than the watchdog, [K] (`run_night.py:1424`) and the chain (`quiet_predicate_campaign.py:1804`, `:1865`).

**E. The delta must execute:**

- The regressions of A and B on `36e8ba6e` (red) and on the new head (green).
- My `probe_p1.py` R1 and R3 cases.
- A search of `write_refusal(` and `_write_driver_refusal(` that places every writer as before or after the result.
- A1 §7.3 rows 3 and 6, after the powermetrics fence has landed.

## Plain summary

1. R3 is E2 again: after a failed proof, `refusal.json` and `result.json` name different causes. The chain's own refusal is a third writer of the same kind that nobody had named, and moving the clean-up step earlier also changes which document is named `refusal.json` when the proof passes. None of this lets the query or ON run beside a capture, or makes a record false.
2. Fix round 2c should state one rule for every refusal document, stop the early clean-up step from writing one, and close R1's missing-key hole. R2 is optional. R4, R5 and the three nits are not N1's to fix now.
3. If the same disagreement shows up after 2c, the next step is a short consult on what the records mean, not a round 2d. Once 2c is clean, N1 can go to the full gate after the powermetrics fence lands and the branch is scoped, and the lead must tell the owner that merging N1 stops real windows until a kind's consumer lands.
