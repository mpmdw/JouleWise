ADDENDUM: NTP-ENFORCE-DESIGN-01-A2 ISSUED

# Cold ruling NTP-ENFORCE-DESIGN-01-A2 — R3 is E2 again; fix round 2c may proceed with a narrow scope and a restated record rule

Judge: Claude Fable 5.1, cold seat, one foreground non-interactive session, 2026-09-29, about 11:50 to 12:45 PDT, inside the 60 budgeted minutes.
Candidate judged: branch `feat/2026-09-28-ntp-n1`, head `36e8ba6e`, read in the detached audit copy `/Users/edr/code/JouleWise-wt-ntp-n1delta2-d528efb2` (clean before and after; head did not move) and executed from a `git archive` copy in `/tmp/cg-ntpfix2c-d528efb2/cand`.

**Result in one paragraph** (every term is defined in §1). R3 is the same defect as E2: after a failed capture proof, a document the driver wrote names a cause other than `night_chain_alive`, so a reader of that document alone does not learn that a capture may still be running and that ON is still owed. I reproduced it with the production helpers (§2, probe R3-A). It cannot make the query or ON run beside a capture; it makes the record misleading. **Fix round 2c may proceed**, with three cures: R3 (the early clean-up step writes no refusal document; the record rule is restated in §3.3 so that it covers every writer, including the chain's own document), R1 (both identity keys must be present and null) and R2 (an ambiguous batch census is not proof). R4, R5, NIT-1 and NIT-2 are registered limits for this round; NIT-3 is seat N3's. NIT-1 should be widened toward 5 s by the "reserve one listing" form of §5, in its own small round after N1 merges and before the lead's bench checks, not inside 2c. If E2's signature survives 2c, there is no round 2d: a bounded consult on the refusal-record model, then a cold gate (§6.3). After 2c and a clean delta, N1 is ready for the full gate; nothing in N5 or N3's scope stands in the way (§7).

## 0. Contamination disclosure

Written to scratch before I read any record (`/tmp/cg-ntpfix2c-d528efb2/00-contamination-disclosure.md`); repeated here with what happened later.

1. **Put into my context by the harness, not opened by me:** the owner's global instruction file (a writing standard and skill names); the project instruction file of my worktree (bridge notes); the one-line index of the owner's memory store; five commit subjects. The index carries one line saying "NTP N1" was in flight before the 09-28 pause and general directives on gates (proportionate, sized to physics, no artificial owner stops). I took the writing standard as form and no fact from the rest.
2. **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file, record 48. The scratch archive contains some of these files; I did not read them there.
3. **One glimpse, disclosed.** A `grep` for "118" in the activation record (record 00, which the charge cites) also returned one line of a later item in which the orchestrator sketches proposed 2c content and stop conditions for this judge. I read that one line as it scrolled past and did not open the item. My rulings below were reasoned from the code and the record; where they agree with that sketch (the early [K] writing no document; R1's two keys; NIT-1 as a limit) the agreement is convergence, and where they differ (I keep round 2b's supersede for the watchdog's document and do not adopt "earlier documents unchanged" for driver-written documents; I specify the horizon widening) the difference is mine.
4. **Same model family.** I am Fable 5.1, as were the judges of the ruling in force and of A1. I sat on neither.
5. **Read in full:** A1 (record 38); records 42, 44, 45, 46, 47; the three probes in `46-probes/`; item 118 of record 00. **Read in part:** the ruling in force (record 21) §4 and §6–§7; the contract lens (33) at its item N5 only. **Not read:** records 11, 13, 31, 32, 34–36, 39–41, 43, 48.
6. **Executed:** read-only `git`, `grep`, `sed`, `ls`, `date`; `git archive` into scratch; `/usr/bin/pgrep` and `/bin/ps` (they list processes and change nothing); two probe files under `/opt/homebrew/bin/python3 -B` with the required guard on `PYTHONPATH`. The guard blocks any command whose text contains the battery probe's name; nothing tried to start one. **Not executed:** `sudo`, `systemsetup`, `sntp`, `/usr/bin/log`, any capture, any power sampler, any battery read, any subagent, any background task, any test module whole (the two delta seats ran them; §8).
7. **Probe processes:** six sleeping Python processes of 0 to 3.5 s, started by my second probe, each killed by it. A `pgrep -f cg_sleeper.py` after the last case found none.
8. **A mistake of mine, corrected.** In my first probe I entered a `mock.patch` on `subprocess.run` without leaving it, so the "real pgrep" line and the NIT-1 rows of that run were answered by my own stand-in. I re-ran both in a clean process (`probe_nit1_pgrep.py`). Only the second run's numbers are used below; the first run's log keeps the wrong lines for the record.
9. **Files.** I changed no repository file except this ruling. Scratch: `/tmp/cg-ntpfix2c-d528efb2/` (`probe_r1_r5.py`, `probe_r1_r5.log`, `probe_nit1_pgrep.py`, `probe_nit1_pgrep.log`, `00-contamination-disclosure.md`, `cand/`).

## 1. Words used

Terms of the ruling in force and of A1 keep their meanings; the ones this addendum leans on are restated.

| Term | Meaning |
|---|---|
| **Driver** | `scripts/run_night.py`, the program that launches every night. **Chain**: the one child program the driver starts, which takes the captures. |
| **Capture process** | A sampler, a collector, a recorder or a capture writer (A1 §1). **Capture signature**: text in a process's command line that marks it as one: the sampler's file name or a path of the night. |
| **OFF, ON, query** | The two commands that switch "set time automatically", and the driver's one reading of the clock daemon's log. **Marker file**: the file that says ON is still owed. |
| **Proof** | `_prove_capture_absent`: the three checks P1 (the chain's group is empty), P2 (every registered group is empty), P3 (no process on the machine carries a capture signature), repeated inside a window of 5 s. **Pass**: one run of P1, P2, P3. **Listing**: one `pgrep` or `ps` call inside a pass; each gets a timeout of 1 s. |
| **Retry horizon** | The latest moment, from the start of the proof, at which another pass may still start. |
| **[K]** | The clean-up step of A1 §4.3: the driver signals and censuses the groups the chain journaled, before the proof. In the candidate it is the call of `_evidence_cleanup_error` at `run_night.py:3346–3347`. |
| **Refusal document** | A file `night/refusal.json` or `night/refusal-NN.json` that says why a night was refused. Created exclusively (a name is never overwritten), with one exception introduced by round 2b: the driver may replace in place the document the deadline watchdog wrote. **Result record**: `night/result.json`, which carries the night's verdict, its `aborted_reason`, and the list `refusal_documents`. |
| **Driver-written / chain-written document** | A refusal document written by the driver process (the watchdog thread, the result step, [K]) versus one written by the chain process itself (the idle-night program's `write_refusal`, `quiet_predicate_campaign.py:327`, used at its `:1602` path). |
| **Start claim** | `chain.started`. **Never-launched claim**: a start claim saying no chain process was ever created, which recovery accepts without a proof (A1 §5). |
| **E1, E2, E3** | The three defects the lead found after round 2 (record 00, item 118; record 44). **E2**: after a failed proof, `result.json` and `refusal.json` named different causes. |
| **R1–R5** | The five should-fixes of the contract-lens delta (record 46). **NIT-1 to NIT-3**: the executing delta's nits (record 45). |
| **Signature (of a defect)** | The observable behaviour by which a defect is recognised again after a repair (A1 §1). E2's is defined in §3.1. |
| **Registered limit** | A behaviour that stays, is written down in the PR's gate ledger and the hand-back document, and is not a merge condition. |
| **Cold gate, consult, seat, WRITE_SCOPE, delta re-audit, fix round** | As in A1 §1. |

## 2. What I verified

### 2.1 Executed by me

All in `/tmp/cg-ntpfix2c-d528efb2/`; "today" means head `36e8ba6e`.

| # | Probe | What it did | Result today |
|---|---|---|---|
| X1 | `probe_r1_r5.py` R1 | `_chain_never_launched` and `recover_network_time` (injected runner, a proof that would refuse) on four start claims, each with an exit record `{"launch_failed": true}` | `{"popen_attempted": false}` (no `pid`, no `pgid`): accepted, `restored`, **ON ran, the proof was never called**. `{"pgid": null, "launch_error": "failed"}` (no `pid`): the same. Complete nulls: accepted (correct). `pid` 123: refused, `chain_unproved`, no ON (correct). The dead-man's own test at `run_night.py:3603–3607` reads the same way (`.get(...) is None`). |
| X2 | R2 | `_capture_proof_pass` with an injected batch census answering exit 0 and no output, for two registered groups; P1 and P3 clear | **`(True, {'checks': ['P1','P2','P3']})`: proved.** `_census_chunk` alone returns every group absent. |
| X3 | R2, the real tool | `/usr/bin/pgrep -lf -g 999999 .`, `-g 999998,999999`, `-g 999999,<my group>`, `-g <my group>`; and the production `_group_census`, `_group_census_batch` on the same | Absent groups: **exit 1, no output**, single and batched alike. A live group: exit 0 with lines. The production functions answer absent/absent and present/absent. The real tool never produced R2's input. |
| X4 | R3-A | An idle-shaped night: start claim, empty registry, a receipt whose C5 says `quiet_predicate_evidence` (receipt validation stubbed to "valid", `cleanup_record` stubbed so no signal is sent), **no** `evidence_outcome.json`; then [K] as the driver calls it; then a failing proof (P3 match) into `_capture_unproved_abort` with no prior stop; then the result step's write and `_write_result` | After [K]: `refusal.json` = `night_probe_error`. Final: `refusal.json` = `night_probe_error`, `refusal-01.json` = `night_chain_alive`, `result.json` = REFUSED / `night_chain_alive`, `refusal_documents` lists both. **Reproduced.** |
| X5 | R3-B | The same, but the chain's own `write_refusal` had already written `refusal.json` (`night_probe_error`) before [K] | The same two documents; [K] wrote nothing (a document existed). The disagreement here is between a **chain-written** document and the driver's. |
| X6 | R3-C, control | The same with `evidence_outcome.json` = `complete` | [K] writes nothing; the only document is `refusal.json` = `night_chain_alive`; the records agree. |
| X7 | R4 | Virtual clock; every listing charged 0.9 s and answering "absent"; registries of 2, 300 and 769 groups | Proved after 2.7 s, 3.6 s and **5.4 s** (window 5 s). The first pass never checks the deadline. Reproduced; needs more than 256 groups with listings near their 1 s timeout. |
| X8 | R5 | `_finish_reporting(..., allow_courier=False, courier_error="chain termination was not proven")` with the durable-record and courier-outcome writers stubbed | Returns **6** (`EXIT_COURIER_FAILED`), not 3. |
| X9 | NIT-2 | `_capture_signature` with the night path `/Users/edr/code/JouleWise` | `/bin/zsh /Users/edr/code/JouleWise-wt-other/run.sh`: **matched**. `python3 -B /Users/edr/code/JouleWiseX/x.py`: matched. Prefix match confirmed. |
| X10 | NIT-1, `probe_nit1_pgrep.py` | The production proof with a **real** census and sweep; the chain's group empty; a registry of 0, 1 or 2 groups that cannot exist; a sleeping child in its own session whose script lives under the night's measurement root (a path signature), ending on its own after 0, 0.5, 2.0 or 3.5 s | 2 groups: a child with 0.5 s left is waited for (proved, 3 passes, 0.62 s); a child with 2.0 s left is **refused at 0.91 s after 4 passes**, P3 naming the child, the child alive at the return. 1 group: refused at 2.02 s (8 passes). 0 groups: 2.0 s waited for (proved at 2.15 s, 9 passes); 3.5 s refused at 2.94 s (12 passes). A child already ended: proved in 0.07 s in one pass. **Record 45 §4's horizon (0.8 / 1.8 / 2.8 s) is confirmed on this machine.** |

### 2.2 Read by me, in the candidate

| # | Fact | Where |
|---|---|---|
| F1 | The early [K] call runs only when a registry file exists, and it is the whole of `_evidence_cleanup_error`: it also repairs `evidence_outcome.json` and, when the chain left no valid outcome and no refusal document exists, writes `refusal.json` as `night_probe_error` through the chain's `write_refusal`. | `run_night.py:3346–3347`, `:1377–1430`; `quiet_predicate_campaign.py:327–340` |
| F2 | The same function is called a second time from the courier's preparation step, and only there before N1. | `run_night.py:1453`; A1 §2.2 R5 |
| F3 | A failed proof becomes `night_chain_alive` through `_capture_unproved_abort`; it supersedes in place only a document named by the earlier driver stop (`prior["document"]`); otherwise the result step allocates a document exclusively, and a name already taken becomes `refusal-01.json`. | `:3511–3545`, `:3417–3424`, `:294–345` |
| F4 | The result record's `refusal_documents` is every refusal document present, in name order. The courier is told to read `result.json`, then every listed document, and to take the verdict from `result.json`. | `:1666–1667`; `docs/process/NIGHT_COURIER_PROMPT.md:10–18` |
| F5 | Every production writer of the start claim emits both `pid` and `pgid` explicitly: the launch-failure claim (`:611–612`), the never-launched claim (`:624–628`), and the normal start. | `run_night.py` |
| F6 | `_census_chunk` and `_group_census_batch` came in with A269 (commit `3eea83ef1`); in the candidate their only caller is P2. `_attribute_pids` ignores its command's exit status. | `:3721–3797`; `git log -S` |
| F7 | The "termination not proven" return through `_finish_reporting(allow_courier=False)` and its status 6 date from the first night driver (commit `8c802bde0`, NIGHT-DRIVER-01). Four inherited tests pin that status, and round 2b's same-group live test pins it too. | `:3471–3483`, `:1893–1907`; `tests/test_run_night.py:2381, 2424, 2461, 2613, 1161` |
| F8 | `NETWORK_TIME_ENFORCED_KINDS` is empty on the candidate, so no night of any kind launches through the driver after N1 merges until a consumer lands. | `network_time_window.py:28`; ruling §4.4, §6.6 step 2 |
| F9 | A1 §7.5 item 2, the desk action for a stuck empty start claim, is not in the hand-back document as far as a search for "restore-pending", "desk action", "by hand" and "remove the marker" shows. | `docs/process/NIGHT_HANDBACK.md` |

## 3. Ruling 1 — R3 is E2; round 2c may proceed, with this scope

### 3.1 E2's signature

Item 118's ruling was: when the proof fails, both records carry `night_chain_alive`, with any earlier abort reason kept inside the evidence. The reason behind it: `night_chain_alive` is the cause that leaves the machine in a state a person must act on (a capture may be alive; ON is owed; the marker stays). Whatever stopped the night first is history; the live hazard is the cause of record.

**E2's signature, for every later audit:** *after a failed capture proof, a document the driver wrote names a cause other than `night_chain_alive`, or `result.json` does not name it.*

R3 fits it exactly. The code path is the same (a failed proof, `_capture_unproved_abort`, the result step); the violated rule is the same (item 118); only the earlier writer differs: the [K] step instead of the deadline watchdog. Round 2b fixed the watchdog's document by superseding it and gave the census stop a document of its own, and did not look at the third driver-side writer that runs between OFF and the proof. So a round to fix R3 is the second fix round on E2, and this gate is the one the rules require. Round 2c **may proceed**.

### 3.2 When R3 happens on a real night, and what it damages

[K] writes its document only for an idle night whose chain left no valid `evidence_outcome.json` and for which no refusal document exists yet (F1). That is the night whose chain was killed or crashed, which is the very night in which a capture process is likeliest to survive. The deadline stop is already covered: the watchdog's document exists first, [K] then writes nothing, and round 2b supersedes that document. The uncovered cases are the agent-census stop and a chain that crashed on its own: no document exists, [K] writes `night_probe_error`, the proof fails, and the night ends with `refusal.json` saying "the chain's probe failed" while `refusal-01.json` and `result.json` say "a capture may be alive".

It **cannot** make the query or ON run: in X4 and X5 the proof still refused, no query and no ON ran, and the marker stays (the driver's code at `:3357–3381` gates both on the proof, unchanged). It makes the record **misleading rather than false**: both documents state true facts, but the one named `refusal.json` is the wrong one for a reader who opens only it. It costs no window by itself.

### 3.3 The cure for R3, and the record rule restated

**Ruled.** The early [K] call performs the clean-up only: `cleanup_record` (signal, then census, the registered groups; its saved record is what the later call finds). It **does not** repair `evidence_outcome.json` and **does not** write a refusal document. The later call from the courier's preparation step (`:1453`) keeps today's whole behaviour, which is the behaviour of main before N1 (F2). Implementation: split `_evidence_cleanup_error` into the clean-up part and the outcome-repair part, or give it a flag; the seat chooses.

Then, after a failed proof with no earlier driver stop, no document exists when the result step runs, and it writes `refusal.json` as `night_chain_alive` (X6 shows this shape already works). After a failed proof with an earlier driver stop, round 2b's rule stands unchanged: the census stop's document is written as `night_chain_alive` with `prior_abort`; the watchdog's document is superseded in place. I do **not** widen the supersede exception to any other document, and I do not reverse it: it is implemented, tested, and confined to the driver's own document.

**The record rule, restated so that it covers every writer.** After a failed capture proof:

1. `result.json` says REFUSED and `aborted_reason` = `night_chain_alive`.
2. Every refusal document **the driver wrote** for the night names `night_chain_alive`. There is exactly one such document; it carries the proof's evidence, and any earlier driver stop inside it as `prior_abort`. It is `refusal.json` unless a chain-written document already holds that name.
3. A document **the chain wrote** is never rewritten by the driver. It stays listed in `refusal_documents`, and the driver's `night_chain_alive` document names it in its evidence under `prior_documents` (a list of the refusal document names that existed when the driver's document was written). Nothing else about the chain's document changes.

X5's shape (the chain's own `refusal.json` = `night_probe_error`, the driver's `refusal-01.json` = `night_chain_alive`) is therefore **lawful and not E2**: two authors, two true facts, the result record pointing at the live hazard, and the driver's document naming the chain's. A reader who opens only a chain-written `refusal.json` is a reader the courier prompt already tells to read everything listed (F4).

**Why not "one document, always `refusal.json`".** It would require the driver to rewrite a record another program wrote, which is the one thing an immutable record must never suffer, and the driver has no way to tell a chain-written `refusal.json` from a foreign one.

### 3.4 R1 and R2 join the round

**R1.** A never-launched claim is accepted only when the keys `pid` and `pgid` are **present and null**, at all three sites: recovery (`network_time_window.py:384`), the driver (`run_night.py:3553`) and the dead-man job (`:3603–3607`). One predicate in `network_time_window.py` (the module imports nothing from the project; the driver imports it already), taking the start claim only; the exit-record clause stays at each site as today. X1 shows the counterfactual: today `{"popen_attempted": false}` restores ON with no proof.

**R2.** In `_census_chunk`, exit 0 with no lines is **not proved**, with an evidence line `census_ambiguous`; in `_attribute_pids`, a non-zero exit makes every pid unresolved. P2 is the only caller (F6), so nothing else changes. X3 shows the real tool answers exit 1 for absent groups, so no clean night is affected. X2 is the counterfactual.

### 3.5 Scope, in full

- **WRITE_SCOPE:** the nine files of A1 §7.2, unchanged.
- **In:** R3 (§3.3), R1, R2 (§3.4). A docstring correction for R4 is allowed if the seat is already in that function; **no loop change**.
- **Out:** R4, R5, NIT-1, NIT-2 (registered limits, §4), NIT-3 (N3).
- **Regressions, each failing by assertion on `36e8ba6e`:**
  - R3-A through the production helpers as in X4: after [K], no refusal document; final `refusal.json` = `night_chain_alive`, `result.json` agrees, `refusal_documents` = one name.
  - R3-B as in X5: the chain's document untouched (`night_probe_error`), the driver's `refusal-01.json` = `night_chain_alive` naming `refusal.json` in `prior_documents`, `result.json` = `night_chain_alive`.
  - R3-C (X6) unchanged, as a control on both heads.
  - One case through the **real driver** where [K] fires: a chain that journals a separately grouped, path-signature child and exits leaving no outcome, on an idle-shaped plan whose receipt says `quiet_predicate_evidence`. If the test fixtures cannot produce such a receipt, the seat says so and the helper-level tests stand; the delta then decides (§6.2 row 3).
  - Round 2b's `_assert_one_chain_alive_cause` for the deadline and census stops: unchanged and still green.
  - R1: the two malformed claims of X1 → `chain_unproved`, no ON, at recovery and in `_chain_never_launched`; the dead-man's test likewise; complete nulls still accepted.
  - R2: X2's input → `(False, {"check": "P2", ...})`; a batch answering exit 1 and empty still proved.
- **Red by deletion:** restoring the document write in the early [K] turns R3-A red; dropping the key-presence test turns R1 red; dropping the exit-0-empty clause turns R2 red.

### 3.6 The seat's stop conditions

A1 §7.2's five stand. Added:

6. the cure needs the driver to rewrite a document the driver process did not write, or a second `supersede=True` call site;
7. the cure needs any change to `_prove_capture_absent`, `_capture_proof_pass` or `_capture_pass_calls` (NIT-1 and R4 are not this round);
8. the seat finds another writer of a refusal document that can run between OFF and the result step, other than the watchdog, the census stop, [K] and the chain itself; that is a finding for the lead, and the seat does not cure it;
9. an inherited assertion must change (R5's four, F7).

## 4. Ruling 2 — each finding placed

"Beside a capture" means: can it let the query or ON run while a process with a capture signature is alive. "Record false" means: can it make a record say something untrue.

| Finding | Whose, when | Beside a capture? | Record false? | Costs a window? | Why placed there |
|---|---|---|---|---|---|
| **R1** | **N1, round 2c** | Only through a start claim no production writer produces (F5): a foreign or hand-edited claim would restore ON with no proof (X1). | No production path. | No. | Three-site predicate, a few lines, contract text explicit (A1 §5). |
| **R2** | **N1, round 2c** | Not with the real tool (X3). Even if a census lied, P3 follows P2, so only a journaled child **without** a signature could slip: the recorder of NIT-3, which writes covariate rows, not power samples. | No. | No. | One clause, sole caller is P2. |
| **R3** | **N1, round 2c** | No (X4, X5: proof refused, no query, no ON). | Misleading, not false (§3.2). | No. | E2's signature; this gate's subject. |
| **R4** | Registered limit | No: every check of the long first pass is fresh; the overrun delays the query. | No. | No. | Needs more than 256 journaled groups **and** listings near their 1 s timeout (X7); a night of N captures journals about 2N+1 groups. The docstring already states the bound as max(5 s, first pass). |
| **R5** | Registered limit; lead's lane if anyone reads the driver's exit status for decisions | No: on that path no proof runs, and neither query nor ON. | No: both records say `night_chain_alive`; only the exit status says "courier suppressed", which is also true. | No. | Status 6 predates N1 (F7); four inherited assertions pin it; changing it is A1 §7.2 stop condition 3. I did not find a reader of the driver's exit status beyond the launch log (not verified; §8). |
| **NIT-1** | Registered limit now; **its own round after merge** (§5) | No: the narrow horizon refuses more, never less (X10). | No. | **Yes, rarely:** an unjournaled, signature-bearing process that ends on its own between about 0.9 s and 5 s after the proof starts is refused; the night ends REFUSED, the marker stays, recovery restores ON at the next driver run or the dead-man job. Journaled groups are already waited for up to 30 s by [K]. | A lawful reading of "up to 5 s" (record 46 E1 judgment, which I share), but not the reading A1 intended, and cheap to widen with a virtual-clock test. |
| **NIT-2** | Registered limit | No: over-matching refuses. | No: the refusal names the process. | Yes, when a live process in a sibling directory with the night path as prefix runs during a night. Such a machine has a shell or an agent session in it and is not quiet in any case (A1 §9). | A boundary rule that under-matches (a path inside quotes, after `=`, before `,`) loses safety; not worth the risk in this round. |
| **NIT-3** | **Seat N3** | Only P2 sees the recorder while it is journaled; the gap between `:1610` and `:1612` is A1's E6, a stated limit. The recorder admits nothing (record 45). | No. | No. | The recorder's command line is N3's file. |

## 5. Ruling 3 — NIT-1: widen the horizon, in this form, in its own round

### 5.1 The forcing problem, with numbers

Round 2b charges each listing its whole 1 s timeout when deciding whether another pass fits, so with two or more registered groups (every idle night) a pass "costs" 4 s and no pass may start after 0.8 s; real passes take about 0.05 s (X10: 4 passes in 0.91 s). A1 designed the 5 s "to let a process that is already ending finish". A sampler that takes 2 s to flush its recording after its signal is refused today (X10, row 1) and the night is lost, though the refusal is true and safe.

### 5.2 The form ruled

Of the three forms the charge names, the first is the right one; the second is a consequence of it; the third is already implemented.

- **Keep:** every listing gets the whole `CAPTURE_CHECK_TIMEOUT_S`, never a remainder (E1's cure). The first pass always completes (R4 stays a limit; document it).
- **Change:** the question "may this listing start?" is asked before **each listing**, not before each pass: a listing starts only if now + `CAPTURE_CHECK_TIMEOUT_S` ≤ deadline. When a listing may not start, the proof stops: **not proved**, returning the evidence of the **last complete pass** (which was a failure, or the proof would have returned), plus `passes`, `horizon_exhausted: true` and the check the abandoned pass had reached. A pass abandoned this way contributes no evidence.
- **Bound:** 5 s plus the reaping of one timed-out listing, for every pass after the first; tighter than today's max(5 s, first pass).
- **Horizon:** a listing may start until 4.0 s; with real passes of 0.05 s the last complete pass starts at about 3.9 s, against 0.8 s today. A process alive at 4 to 5 s is refused, as A1 allows.

**Weighed.** A lost window costs a night and an owner notice; the widening costs about ten lines in a loop that has been wrong once (E1), plus a virtual-clock test. The widening is worth doing, but **not in round 2c**: 2c's delta must be able to say "E2 is gone" without a loop change beside it, and the narrow horizon is safe. So: **its own round, after N1 merges and before the lead's bench checks** (ruling §7.2, B7 and B8), so those checks run on the final loop; the merge itself must not wait, because seats N2 and N3 wait on it (ruling §6.6 step 4).

### 5.3 The tests that round must carry (virtual clock, as round 2b's E1 tests)

1. Listings of 0.05 s, two groups, a survivor that ends at 3.5 s → proved, more than ten passes. Fails today (refused at about 0.8 s).
2. Listings that each spend their whole 1 s, two groups → the first pass completes (4 s, P1 not proved), no second listing starts, total at most 5 s plus one reap.
3. A survivor alive throughout → not proved; evidence P3 with its pid; `horizon_exhausted` true; total at most 5 s.
4. Listings of 0.9 s: the second pass starts at about 3.7 s, its P1 ends at 4.6 s, P2 may not start → abandoned; the returned evidence is the first pass's.
5. Round 2b's live E1 test, unchanged.
6. X10's real-process rows, with the 2 s survivor now waited for.

## 6. Ruling 4 — stop conditions for 2c and its delta

### 6.1 The seat

§3.6.

### 6.2 The delta re-audit after 2c

A fresh seat that wrote no part of the fix, on a host where `ps` and `pgrep` list processes, on a machine where **no other capture is running** (record 45 §6: a foreign real sampler makes every clean-path test refuse).

| # | Must execute | Pass |
|---|---|---|
| 1 | My probes on the new head: `probe_r1_r5.py` (R1, R2, R3-A/B/C, R4, R5, NIT-2) and `probe_nit1_pgrep.py`, copied into the record first | R1 malformed claims: refused, no ON. R2: `(False, P2)`. R3-A: no document after [K]; one document, `night_chain_alive`; records agree. R3-B: the chain's document untouched, the driver's names it, `result.json` = `night_chain_alive`. R3-C: unchanged. R4, R5, NIT-1, NIT-2: unchanged (limits). |
| 2 | Every regression of §3.5 on `36e8ba6e` and on the new head | fails by assertion on the old, passes on the new; the controls pass on both |
| 3 | The real-driver [K] case of §3.5, or a statement that the fixture cannot produce it, with the call chain `:3346 → :3347 → :3357 → :3359 → :3417` read on the new head | executed, or stated with the reading |
| 4 | The three deletions of §3.5 | each turns its named test red by assertion |
| 5 | All 35 regressions of rounds 2 and 2b, the seven deletions of record 45 row 3, and rows 5 and 6 of A1 §7.3 (the 42 tests; the modules whole, outside the sandbox) | still green; no failure absent on `36e8ba6e` |
| 6 | **A hunt of its own** over every writer of a refusal document reachable between OFF and the result step: the watchdog, the census stop, [K], the chain's own `write_refusal`, `calibration_refusal` (written only when there is no abort, `:3405–3409`), and any other it finds | for each: after a failed proof, the rule of §3.3 holds, or the writer is reported under stop condition 8 |
| 7 | A statement for E2 and for D1: does the signature survive in any form? | stated yes or no, with the executed case |

### 6.3 If E2's signature survives 2c

**No round 2d.** N1 does not merge. The next spend is a **bounded design consult** on the refusal-record model, one question: *one designated verdict document per night, kept by whom, with what ledger of the others?* — followed by a cold gate. A second recurrence would show that "one cause of record" cannot be kept by adjusting writers one at a time, and the durable answer (an append-only ledger with one designated verdict entry, read by the courier and the retained-roots classifier) touches the courier prompt and readers outside N1's nine files.

**Not the owner.** Nothing needs hardware, `sudo`, money or a sealed registration; the owner receives a plain notice. **Not an emergency:** the proof still refuses (X4, X5), the enforced-kinds set is empty (F8), and no night launches under this code until a consumer merges.

**A defect of a new kind** that 2c introduces: one fix round of its own with no cold gate (A1 §7.4, unchanged). **D1's signature** ever recurring: A1 §7.4 stands (consult on process custody).

## 7. Ruling 5 — after 2c and a clean delta, N1 is ready for the full gate

**Ready:** the Opus counter-review, the cold Fable final pass, the PR with its gate ledger, and merge. The ledger must carry the registered limits by name: R4, R5, NIT-1 (with §5 as the scheduled follow-up), NIT-2, NIT-3 (to N3), the E6 journal gap, the stuck-empty-claim desk action (A1 §5), the four inherited status-6 assertions, and the run condition "no foreign capture during live tests".

**Not in the way:**

- **N5** (record 33: `OLD_IDLE_PLANS` must be filled when the idle consumer lands, but N3's scope lacks the module). It is a scope line in N3's brief, lead-owned (A1 §7.5 item 3). It changes nothing in N1's PR.
- **N3's scope** (the chain's own ON before its clean-up, A1 §8 §4.5; NIT-3). N1's proof gates the driver's query and ON regardless of the chain's order. The chain's ordering defect stays until N3 lands, and until N3 merges no idle night launches (F8). It is not a condition on N1's merge; it is a condition on N3's.
- **R5**: a limit, not a gate.

**Owed by the lead, with or right after the PR:** A1 §7.5 items 1, 2 (F9: the desk action is not yet in the hand-back document), 3 and 4; my probes copied into the record (§6.2 row 1); the horizon round of §5 scheduled before the bench checks of ruling §7.2; and, for the counter-review, the rule of §3.3 stated as one of its checks.

## 8. Left unchecked, stated plainly

- **NOT EXECUTED through the real driver:** R3. I ran the production helpers in the driver's order and read the call chain; the delta's row 3 closes this.
- **NOT EXECUTED:** any test module whole. Records 44 and 45 ran them outside the sandbox at `36e8ba6e` with zero failures; I did not repeat that.
- **NOT READ:** who, beyond the launch log, reads the driver's exit status (R5). If `arm_retry` or a launcher branches on it, the lead says so in the ledger.
- **NOT READ:** records 11, 13, 31, 32, 34–36, 39–41, 43, 48.
- **ONE MACHINE, ONE NOON:** X10's pass times (about 0.05 s per pass, 0.91 s to four passes) and X3's `pgrep` exit statuses are from this machine today.
- **MY FIRST PROBE RUN WAS PARTLY WRONG** (§0 item 8). The corrected numbers are the second file's.
- **THE PROTOTYPE OF §5 IS NOT WRITTEN.** §5 is a specification with its tests; it shows the shape, not code.

## Summary

1. R3 is E2 again: after a failed capture proof, the clean-up step's own refusal document leaves `refusal.json` naming the chain's probe failure while the result names a live capture. It cannot let the query or ON run, but it misleads a reader. Round 2c may proceed: the early clean-up writes no document, chain-written documents are never rewritten and are named by the driver's, and R1 (both keys present and null) and R2 (an ambiguous census is not proof) ride along; R4, R5, NIT-1 and NIT-2 are registered limits, NIT-3 is N3's.
2. The retry horizon should widen from about 0.8 s to about 4 s by asking "does one more listing fit?" before each listing and returning the last complete pass, in its own small round after N1 merges and before the lead's bench checks, never inside 2c.
3. If E2 survives 2c there is no round 2d: a bounded consult on the refusal-record model, then a cold gate; the owner has nothing to decide. After 2c and a clean delta, N1 is ready for the full gate; N5 and N3's scope are conditions on N3, not on N1.
