# Cold-gate packet: skill-distill doctrine landing (2026-09-04)

Assembled at branch `feat/2026-09-04-packet-skill-distill`, candidate head
`6ebdba4d08857f17cb67d4bb90639aeb17873157`. The comparison base is the
computed merge base of `origin/main` and the candidate,
`b0ed6991c11f3a515ad293760c6dfc031adda8e1`. The questions below grade the
candidate delta after the first ruling's cures, not the superseded intermediate
wording. Exhibits 06–07 preserve the original implementation and first fix;
exhibits 26–29 preserve the first ruling, its cure report, and the current
rule-bearing files for this second convening.

## 1. Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## 2. Convening trigger and file census

The landing changes standing process doctrine, so rule 11 requires a cold
instance before acceptance. The complete rule-bearing file census from
`git diff $(git merge-base origin/main HEAD)..HEAD` is:

- `docs/agent_playbook.md`
- `docs/orchestration.md`

No skill file changes. The other changed paths are custody rather than doctrine.
Exhibits 01–04 are the seat, lesson, refuter, and first-fix reports. Exhibit 05
is the complete computed-base delta at `6ebdba4d`; exhibits 06–07 are the
original implementation and first-fix deltas. Exhibits 08–11 preserve the
merge-base and first-convening bytes of both rule-bearing files. Exhibits 12–25
are authority or incident evidence. Exhibits 26–27 are verbatim copies of the
first ruling and cure report. Exhibits 28–29 are verbatim current bytes of every
changed doctrine or skill file (the two doctrine files above; no skill file
changed). All line citations below refer to those copies.

## 3. Verdict instructions

For every numbered question answer exactly one of **AFFIRM**, **AMEND**, or
**REFUSE**. AFFIRM installs the quoted after text unchanged. AMEND supplies
exact replacement text and identifies every affected question. REFUSE retains
the before state. Grade each question independently; do not infer that one
verdict controls another. The shared exact before state is absence: exhibit 08
ends at lines 472–477 and exhibit 10 ends at lines 346–352, so none of the
quoted rules existed at the merge base.

## Second convening — what changed

The first ruling (exhibit 26) refused merge as-is, AMENDed Q1/Q3/Q4, and
AFFIRMed Q2/Q5–Q11. The cure report is exhibit 27. Per question:

- **Q1 — AMEND.** Cure: moved the merge-readiness requirement into Mission M0
  step 5 and left the task-local focused-check rule plus incident pointer in the
  addendum (exhibit 28:70–76, 483–492).

  Exact before:

  ```text
  Record the broader suite as deliberately not run and leave any required merge-wide replay to the lead; do not spend the seat on a default discovery run that the task cannot use.
  ```

  Exact after:

  ```text
  Record the broader suite as deliberately not run. A landing whose seat skipped discovery is not merge-ready until the lead has run the full suite green at the candidate head; do not spend the seat on a default discovery run that the task cannot use.
  ```

- **Q2 — AFFIRM.** Cure: none; text unchanged.
- **Q3 — AMEND.** Cure: removed volatile model assignments and retained the
  D-129 authority pointer (exhibit 29:356–361).

  Exact before:

  ```text
  It does not supersede D-129: Opus-directed Sol lanes remain the standing default.
  ```

  Exact after:

  ```text
  It does not supersede D-129: lieutenant-directed executor lanes remain the standing default (model assignments live in D-129, not here).
  ```

- **Q4 — AMEND.** Cure: replaced the two volatile model-specific phrases in
  the dated-exception paragraph (exhibit 29:365–375).

  Exact before:

  ```text
  directed the lead to start bounded Sol seats directly after fixing their role,
  prompt, authority, and review lens. This was a dated exception to D-129, not a
  repository-wide replacement for its standing Opus-directed default.
  ```

  Exact after:

  ```text
  directed the lead to start bounded executor seats directly after fixing their
  role, prompt, authority, and review lens. This was a dated exception to D-129,
  not a repository-wide replacement for its standing lieutenant-directed
  default.
  ```

- **Q5 — AFFIRM.** Cure: none; text unchanged.
- **Q6 — AFFIRM.** Cure: none; text unchanged.
- **Q7 — AFFIRM.** Cure: none; text unchanged.
- **Q8 — AFFIRM.** Cure: none; text unchanged.
- **Q9 — AFFIRM.** Cure: none; text unchanged.
- **Q10 — AFFIRM.** Cure: none; text unchanged.
- **Q11 — AFFIRM.** Cure: none; text unchanged.

## 4. `docs/agent_playbook.md` questions

### Q1 — task-local verification precedence

**Before:** no text followed the exact final sentence “A mission whose
bookkeeping is missing is not done.” (exhibit 08:472–477).

**After (exact, exhibit 28:73–76 and 485–492):**

> Record the broader suite as deliberately not run. A landing whose seat
> skipped discovery is not merge-ready until the lead has run the full suite
> green at the candidate head; do not spend the seat on a default discovery
> run that the task cannot use.
>
> Mission M0's default suite command applies only when the task does not issue a
> narrower verification rule. If the task says to edit first, names focused test
> modules, prohibits repository-wide discovery, or makes the seat read-only,
> obey that rule: perform the intake and workspace checks, make the authorized
> edit when applicable, and run only the named checks afterward. The watchdog
> contract review demonstrated the trap: broad discovery
> ended in an interrupted calibration test while the focused module completed
> cleanly (`docs/process_traces/2026-09-02-hands-free-week/17k-watchdog-05-refuter-contract.md`).

**Claimed authority:** a task's explicit verification contract takes precedence
over Mission M0's default; incident evidence is exhibit 14:35–42, 65–67 and
exhibit 15:24–27. **AFFIRM / AMEND / REFUSE?**

### Q2 — verification-generated dirt

**Before:** no text followed exhibit 08:472–477.

**After (exact, exhibit 28:494–500):**

> Verification must not manufacture workspace dirt that the runner later
> misclassifies as the seat's change. Set `PYTHONDONTWRITEBYTECODE=1` for Python
> tests and direct compilation caches and other generated output to a disposable
> directory unless the task explicitly owns those artifacts. The watchdog build
> and fix reports provide the executed pattern
> (`docs/process_traces/2026-09-02-hands-free-week/17f-watchdog-01-landing.md`;
> `docs/process_traces/2026-09-02-hands-free-week/17h-watchdog-03-fix-round-1.md`).

**Claimed authority:** runner attribution integrity plus executed examples in
exhibit 15:24–52 and exhibit 16:28–52. **AFFIRM / AMEND / REFUSE?**

## 5. `docs/orchestration.md` questions

### Q3 — D-129 remains the standing default

**Before:** exhibit 10 ended at the exact line “- Per-decision, in-stream
reasoning: `docs/stream_logs/`.” (lines 346–352).

**After (exact, exhibit 29:356–361):**

> This addendum records execution details exposed by the 2026-09-02/03
> hands-free work. It does not supersede D-129: lieutenant-directed executor lanes
> remain the standing default (model assignments live in D-129, not here). The
> direct-seat account below is limited to Ed's recorded
> 2026-09-03 budget regime, while its launch and recovery safeguards
> apply whenever separate authority permits a direct invocation.

**Claimed authority:** D-129 assigns launch/poll/harvest ceremony to Opus 5 and
makes Opus-directed Sol lanes the default (exhibit 12:8318–8332); the direct-seat
regime is dated evidence, not a superseding ruling (exhibit 13:42–45). **AFFIRM /
AMEND / REFUSE?**

### Q4 — direct-seat definition and dated exception

**Before:** no counterpart after exhibit 10:346–352.

**After (exact, exhibit 29:365–375):**

> A *direct seat* is a bounded model invocation started by the lead through the
> runner, without a second model session whose only job is to start and watch it.
> During the specifically recorded 2026-09-03 budget regime, Ed
> directed the lead to start bounded executor seats directly after fixing their
> role, prompt, authority, and review lens. This was a dated exception to D-129,
> not a repository-wide replacement for its standing lieutenant-directed
> default. It avoided
> the passive wrapper's cost during that regime while preserving lead review of
> every merge-bound result
> (`docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`,
> “2026-09-03 21:05 update”).

**Claimed authority:** the direct-seat default existed only inside Ed's dated
budget regime (exhibit 13:42–45); D-129 otherwise controls (exhibit
12:8318–8332). The original overbroad default and its cure are visible in
exhibits 06–07; refuter F2 and the cure are exhibits 03:109–117 and 04:80.
**AFFIRM / AMEND / REFUSE?**

### Q5 — direct-run launch and report safeguards

**Before:** no counterpart after exhibit 10:346–352.

**After (exact, exhibit 29:377–388):**

> Before a direct runner invocation, record its checkout, starting revision,
> comparison base, write scope, output path, report genre, and expected
> verification. Put a read-only seat in a clean disposable checkout or archive,
> because lead-created untracked files can make the runner report a scope failure
> even when the seat changed nothing. Keep the machine-readable report envelope
> within its declared byte limit and put detailed audits in the prose body. A
> runner failure caused only by pre-existing, explicitly attributed dirt is not a
> semantic verdict; the lead records and adjudicates the mismatch before using
> the result
> (`docs/process_traces/2026-09-02-dx-registry/MAGISTRATE-NOTES.md`;
> `docs/process_traces/2026-09-02-dx-registry/22a-terra-243-protocol-failure.md`;
> `docs/process_traces/2026-09-02-hands-free-week/17i-watchdog-04-refuter-execution.md`).

**Claimed authority:** observed runner scope and envelope failures, with lead
adjudication retained (exhibit 17:23–28, exhibit 18 in full, exhibit 19:1–7).
**AFFIRM / AMEND / REFUSE?**

### Q6 — harvest before retry

**Before:** no counterpart after exhibit 10:346–352.

**After (exact, exhibit 29:390–395):**

> After an interrupted wrapper or usage cutoff, inspect the named worktree,
> branch, report, status file, and log before launching a replacement. A finished
> model run may outlive the wrapper that started it; harvesting that evidence is
> the first recovery action, and blind relaunch is prohibited
> (`docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`,
> “Resume sequence after a usage stall”).

**Claimed authority:** observed wrapper/child lifetime divergence and the dated
recovery procedure (exhibit 13:77–86). **AFFIRM / AMEND / REFUSE?**

### Q7 — replay custody

**Before:** no counterpart after exhibit 10:346–352.

**After (exact, exhibit 29:399–408):**

> A *replay* is a repeated check used to show that a reviewed result still holds
> at a named candidate revision or integration tree. Run a merge-bearing replay
> in a clean disposable tree, record the exact revision and merge parents, the
> working directory, full command, unpiped log, exit status, and stable tail. Run
> each mutation from a fresh baseline or verify the restored file digest before
> the next mutation. When reproducibility of a generated artifact is claimed,
> reissue it at the candidate revision and compare bytes with the issued artifact
> (`docs/process_traces/2026-09-02-hands-free-week/17c-planpin-06-fix-round-1.md`;
> `docs/process_traces/2026-09-02-hands-free-week/17h-watchdog-03-fix-round-1.md`;
> `docs/process_traces/2026-09-02-paper-d-dg071/43-integration-replay-and-terminal-review-e7425eef.md`).

**Claimed authority:** executed mutation restoration and final-head replay
custody (exhibit 20:91–147, exhibit 16:50–52, exhibit 21:1–54). **AFFIRM /
AMEND / REFUSE?**

### Q8 — cold-gate packet hygiene

**Before:** no counterpart after exhibit 10:346–352.

**After (exact, exhibit 29:412–422):**

> A *cold gate* is an independent review performed before an irreversible process
> mechanism is accepted or installed. Its packet must use neutral, separable
> questions; distinguish executed observations from proposals; time- or
> revision-pin volatile facts; and list every load-bearing source or bounded
> excerpt with its path, digest, and relevant span. Commands in the packet must
> be checked for side effects: a mode-changing option followed by `--help` is not
> assumed to be read-only. Contrary evidence and competing positions receive the
> same level of detail
> (`docs/process_traces/2026-09-02-hands-free-week/12-coldgate-opus-refutation-packet-11.md`,
> “Q8 — Packet hygiene”; `docs/process_traces/2026-09-02-hands-free-week/14-coldgate-fable-ruling-packet-11.md`,
> “Q8 — Packet hygiene”).

**Claimed authority:** independent packet-hygiene findings on side effects,
missing evidence, volatility, atomicity, and asymmetry (exhibit 22:704–789;
exhibit 23:149–162). **AFFIRM / AMEND / REFUSE?**

### Q9 — cold-seat isolation

**Before:** no counterpart after exhibit 10:346–352.

**After (exact, exhibit 29:424–429):**

> Every cold-gate seat receives a distinct scratch directory and sealed output.
> It must not read another seat's scratch material or answer before its prescribed
> independent read order is complete; the lead opens and compares the outputs
> only after both are sealed. The first watchdog convening shared scratch space,
> and the relaunch cured that defect by separating the seats
> (`docs/process_traces/2026-09-02-hands-free-week/15-watchdog-gate-synthesis.md`).

**Claimed authority:** independence semantics plus the recorded shared-scratch
defect and relaunch cure (exhibit 24:19). **AFFIRM / AMEND / REFUSE?**

### Q10 — D-171 first-use table boundary

**Before:** no counterpart after exhibit 10:346–352.

**After (exact, exhibit 29:433–435):**

> A *first-use review* checks that a defined term or code literal is built or
> glossed before a reader must rely on it. For contract edits that add, move, or
> rename such terms, the pre-landing first-use table is mandatory.

**Claimed authority:** D-171's original item 6 and corrective addendum ratify
the table half (exhibit 12:10649–10655, 10663–10688). **AFFIRM / AMEND /
REFUSE?**

### Q11 — executed-probe authority per behavioural clause

**Before:** no counterpart after exhibit 10:346–352; no repository-wide probe
requirement existed.

**After (exact, exhibit 29:435–444, beginning after “mandatory.”):**

> D-171's dated
> addendum separates that ratified table rule from the executed-probe proposal:
> the latter remains PROPOSAL PENDING ED and does not bind a behavioral contract
> edit outside a magistrate-commissioned brief. The magistrate may require an
> executed first-real-use probe as evidence for a brief it commissions under its
> own authority; that local requirement must be labelled as such and must not be
> cited as a generally ratified repository rule
> (`docs/process_traces/2026-09-03-kernel-batch/01-lieutenant-report.md`,
> “Item 1 — the D-171 addendum”; `docs/process_traces/2026-09-02-hands-free-week/17k-watchdog-05-refuter-contract.md`,
> finding F4).

**Claimed authority:** D-171 says the executed-probe half is PROPOSAL PENDING
ED and binds only magistrate-commissioned briefs when the magistrate requires
it (exhibit 12:10667–10693); exhibit 25:1–22 traces the overstatement; refuter
F1 and its fix are exhibits 03:101–108 and 04:79. Does the exact after text
preserve that boundary without installing the pending per-behavioural-clause
proposal? **AFFIRM / AMEND / REFUSE?**

## 6. Q-SCOPE — ONE-home placement

For every Q1–Q11 text you would AFFIRM or AMEND, decide whether it belongs in
the named changed file or is merely a restatement that should live in its ONE
home. In particular test Q1–Q2 against Mission M0 itself; Q3–Q9 against the
external skill-only mechanics identified by `docs/orchestration.md`; and
Q10–Q11 against D-171 in `docs/decision_log.md`. Answer **KEEP HERE** or
**ONE-HOME MOVE** per question. For every move, name the exact authoritative
home and the deletion or one-line pointer that should replace the quoted text.

## 7. Seat constraints

Read the charter first, then exhibits 08–12, 26–29, and the two candidate deltas
before the seat/refuter/fix reports. Keep Q1–Q11 independent. Do not write, run
tests, start agents, use network commands, or inspect another seat's scratch.
Treat the validator receipt only as validation-time byte observation, never as
judge handoff or launch authorization.

## 8. Exhibit manifest

```
5cb626e45b4d53decbda8162de6a041c89941de4627460831c178ebaba3db4d5  packet-exhibits/01-seat-report.md
faa0e0590a90b0e7799d4e526685a2c4fafda1d791b79ef62b4e5fd5c799d91d  packet-exhibits/02-lessons.md
85f0a211f6c30788241a868e18b1099a0004edd2f0731946b7e6272dc32deb75  packet-exhibits/03-refuter-merge-base.md
df00c7e04ec309d142418bd75eb012c0a27753eafa503b0dd17b716f592040d2  packet-exhibits/04-fix-round-1-report.md
b12a579a2ca65880a344c420f4a2671158f68f791f69ed9190761c4e4fb09c6d  packet-exhibits/05-delta-merge-base-to-head.patch
c8d8e47a0b1f724f6f2c75527feab7d7d2713c97c113f725dc9713fc84f0bed4  packet-exhibits/06-delta-original-implementation.patch
3afbd2cdad4017060c4674bac9c3494a0b4b5752b2add00613c63341dcd88e60  packet-exhibits/07-delta-fix-round-1.patch
29ae2d19f06579d48a4c77637f597c91165f97424cf5c7634dae962b91cf7dab  packet-exhibits/08-agent-playbook-before.md
73fab80a352fa307f5394a69456df9032af9ee12b6f408b5fa026e78e6cd87e2  packet-exhibits/09-agent-playbook-after.md
5cafad4ae327532053e2393b06683a21994eb610b7ff88efee1ad86dc0a772eb  packet-exhibits/10-orchestration-before.md
3122791681e9c9e0edfa7a413b310254d1e73d5f8f79a7c64f2569149addbb45  packet-exhibits/11-orchestration-after.md
8e21ad8c3756fd292cd590718cd7f6923a146a9b78ea7501f94d5c55eb6e58de  packet-exhibits/12-authority-decision-log.md
357dde6d9f23074cbcb7ec2c00937870f4811ce11560dcc077fa7ac29d313e13  packet-exhibits/13-authority-durable-state.md
d3e8771765d0a9e3bc040164049c0b134b3854ba5525823ff99c747fa3fe3149  packet-exhibits/14-evidence-watchdog-contract-refuter.md
e63fcd15672147aa556890a19f3a40cacebde24a049b10e71c6a26f4747d45db  packet-exhibits/15-evidence-watchdog-landing.md
9ec2fd7952ad3187be1749b65babc2e8e86ad7b2cb0297f3edba709f65e5e470  packet-exhibits/16-evidence-watchdog-fix-round-1.md
4ca3fbe0ed0a6eae85c03f2c317dbdf98d16f1fad5d58af913ee4c45f26175d4  packet-exhibits/17-evidence-dx-magistrate-notes.md
4d1d7e030326c3de8f31e7cf1e0d9cf10986fc324379d6ef3f057a3bdfc474e1  packet-exhibits/18-evidence-dx-protocol-failure.md
d90a2b52a85f550405ed67969549783eeb5406cb484647c3a82126444fa42db1  packet-exhibits/19-evidence-watchdog-execution-refuter.md
71d589a64af2d8314a95b813a41f9550ac1827353c9a906a7dd3d324b0e4e087  packet-exhibits/20-evidence-planpin-fix-round-1.md
9f489e8bee0a889163e2569b8a0100c278dd15fc75a31c2fac55f779d1ef66e6  packet-exhibits/21-evidence-paper-d-integration-replay.md
b8ce42d3b6d21d78d7d26543e526ed51d9fb777745089ee1a16d490b782c142c  packet-exhibits/22-evidence-watchdog-coldgate-refutation.md
7a5ece363feb4c82458e5c8ce71c8ea2044a67ff4f57c83aa901b412d4316895  packet-exhibits/23-evidence-watchdog-coldgate-fable-ruling.md
f6c80cbaff8a03d4c56a1e93608d661cf853624565a679c8a6d5db5964dd17f2  packet-exhibits/24-evidence-watchdog-gate-synthesis.md
1081d1e97b38ddd390ba8ed351cccc5d95bc1d62a5a10a43b478096088064c95  packet-exhibits/25-evidence-kernel-batch-lieutenant-report.md
627b4433faa99bec21abab67a4f8b05e4de3932014f4b5707c38da1c32821600  packet-exhibits/26-coldgate-ruling-fable.md
34d298bbe5c38eaa707809e313015c5bad1df4bdf46474ea30edd57643adec26  packet-exhibits/27-coldgate-cure-report.md
40f8fec1826e3957cce935c6c8ebb22c149fafa4d2b9de92a63ab27ad3f1d734  packet-exhibits/28-agent-playbook-current.md
d2d3bea84993f09eda9292c18307f70b6002206e878d340be27f81f60079f870  packet-exhibits/29-orchestration-current.md
```
