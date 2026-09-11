# 07 — Opus contract-lens refuter, cold gate on item 6 after the interpreter cure

Seat: Opus 5 (1M), paired with an unseen cold Fable judge under
`docs/process/coldgate_charter.md` §5. Worktree
`/Users/edr/code/JouleWise-wt-bk-58a3bcfc`, branch
`bookkeeping/2026-09-11-activation-58a3bcfc`. No file modified; no git
state-changing command run; no launchctl, no `~/night-custody`, no network.

**Packet digest, verified before reading the merits** (charter §7 discipline,
applied to the packet rather than the charter since the charter digest was not
supplied to me independently):

```
$ shasum -a 256 docs/process_traces/2026-09-11-activation-58a3bcfc/05-coldgate-packet-item6-after-interpreter-cure.md
44e914d7fc52e7ea8e7f6e2ef08bdf826f90728291ff4cd7ce51fe5f25e416b6
```
Expected `44e914d7fc52e7ea8e7f6e2ef08bdf826f90728291ff4cd7ce51fe5f25e416b6` —
MATCH. Charter digest: NOT EXECUTED (no expected value was supplied to this
seat independently of the packet; charter §7's own instruction is addressed to
the judge, and I record the gap rather than fabricate a comparison).

My charge is falsification of the packet's claims, of the lead's labelled
disposition, and of the asserted application of the controlling contract — not
of the judge's unseen ruling.

---

## 1. What the contract words actually say

### 1.1 Kernel acceptance item 6 — the operative text

`docs/process/state_kernel.json` → `/tasks/NIGHT-REHEARSAL-01/acceptance/evidence[5]`
(read via `json.load`, key path `tasks.NIGHT-REHEARSAL-01.acceptance.evidence`;
the object begins at `docs/process/state_kernel.json:3636`):

> "After WATCHDOG-INSTALL-01, one fresh REHEARSAL_STUB night fires through the
> night driver's own courier before any real plan is armed"

Five load-bearing words, each doing separable work:

| word | what it requires | option (b) |
|---|---|---|
| `REHEARSAL_STUB` | a named receipt class, enumerated at `joulewise/night_gate.py:29` and branched on at `scripts/run_night.py:1545,1572-1575` | an equivalence night is `DIAGNOSTIC_NO_PACK` (`docs/phase_2/derivation_night_runbook.md:734,750`). **Different class.** |
| `fresh` | a new plan, not a re-arm; synthesis 65 spells this as "New plan_id, fresh custody root, fresh checkout path" (`…/65-magistrate-synthesis-second-stub-night.md:13-14`) | the 09-09 night is not fresh relative to 65, which was issued *knowing* about it |
| `night` | a night | a daytime `rehearse` firing — the packet's own (c) example — is not one |
| `fires` | the driver runs | 09-11 did not: the process died at `scripts/run_night.py:1417` (`from joulewise import arm_readiness`) before any census or gate (record 01:12) |
| `before any real plan is armed` | ordering | F6 is right that the equivalence night IS a real plan: it captures real powermetrics under sudo, class `DIAGNOSTIC_NO_PACK` |

**Finding C-1 (MATERIAL).** On its own words item 6 cannot be satisfied by a
`DIAGNOSTIC_NO_PACK` night. Option (b) therefore does not *satisfy* item 6; it
can only *waive* it by asserting the 09-09 night already discharged it. The
packet is honest about this (line 33: "if (b) or (c) is chosen, state it as a
waiver/reading"). No hygiene defect here.

### 1.2 The kernel's own pending dependency is now unsatisfiable as written

`docs/process/state_kernel.json`, `/tasks/NIGHT-REHEARSAL-01/dependencies`,
target `REHEARSAL-20260911-HARVESTED`, `state: "pending"`, `strength: "hard"`:

> "rehearsal-20260911 (REHEARSAL_STUB, agents installed 2026-09-10 03:00–06:30
> PDT, t0 2026-09-11 02:56 PDT) fired and harvested: receipt not refused
> (item 6) and the pre-night 07:00 dead-man stand-down observed with nothing
> written into night/ (item 5); a night_refused_agent_present receipt closes
> item 5 only"

That hard dependency names a specific plan at a specific `t0` that can never
recur: record 01:59 — "Never re-arm this plan on this signature" — and
synthesis 65:13-14 ("21i's plan is never re-armed").

**Finding C-2 (MATERIAL, independent of Q).** The pending hard dependency is
now unsatisfiable on its face and must be re-targeted by the magistrate
whatever the verdict. It is *not* a licence to delete the obligation: the
adjacent prose "receipt not refused (item 6)" is the kernel's own gloss of item
6 and survives re-targeting. A ruling that quietly lets this dependency lapse
would be the "decided ≠ done" failure, not a cure.

### 1.3 The one text that arguably favours (b) — and why it does not carry

The same dependency block, target `SECOND-STUB-NIGHT-RULING`, `required`:

> "…whether the merged gate cure requires a second REHEARSAL_STUB night through
> the installed LaunchAgent before any DIAGNOSTIC_NO_PACK plan (**21i acceptance
> item 6 was MET conditional on the cure landing**; items 1/4/5 remain open)"

Read alone, that parenthetical says item 6 was MET by rehearsal-20260909
conditional on PR #309 landing — and #309 has landed (`a52810c9`, per
NIGHT_HANDBACK:87-88 and 65:18). That is the strongest textual argument for (b)
anywhere in the corpus, and the packet **does not quote it**.

**Finding H-1 (MATERIAL, packet hygiene, charter §6).** The packet's F8 lists
Ed-standing directions favouring speed but omits the one *kernel* clause that
favours (b). The omission is not fatal — the clause is superseded in the same
object — but a neutrally assembled packet would have quoted it and explained
the supersession. Effect on Q: none, for the reason below; effect on the
record: the judge was denied the best version of (b)'s case.

Why it does not carry: that parenthetical is the *question presented to* the
ruling, not its answer. The answer is the adjacent `evidence` label on the same
dependency — "Cold gate 61 + Opus refuter 62 → magistrate synthesis 65: second
REHEARSAL_STUB night REQUIRED" — with `state: "satisfied"`. Synthesis 65:3
reads "Both seats rule (c): a second REHEARSAL_STUB night is REQUIRED". Under
charter §9, "a prior governed verdict remains as issued and must not be
converted into its opposite by reinterpretation." Reading the 09-09 night as
satisfying item 6 is exactly that conversion.

### 1.4 What 65's ground was, and how much of it 09-11 discharged

Synthesis 65:5-7, verbatim:

> "The ground is item 5 and the un-exercised class-independent gate rows
> (refuter 62: the 09-09 gate returned at the C5 chain read, so C1/C4 and the
> tail of C3 never ran live), not the cure's own branch"

I verified 62's structural claim against the code rather than the paraphrase.
In `joulewise/night_gate.py` the evaluation order is: C5 window/freshness/HEAD
(≈972-1031) → C3's census (1033-1041) → C5 chain read (1043-1108) → C3 tail,
HID/AC/display/load/thermal (1136-1253) → C4 boot+clock (1255-1298) → C1
registration (1300-1328). The 09-09 refusal came from the chain read at 1057
(`probes.read_text(plan.chain_path)`), which sits **before** 1136/1255/1300.
62's claim is correct as a matter of code order.

- **Item 5: DISCHARGED.** Record 01:45-51, predicates P1–P4 all HOLD; the
  record states "Item 5 MET on rehearsal-20260911".
- **C1 / C3-tail / C4: NOT DISCHARGED.** Record 01:11 — "No gate row C1–C5 was
  exercised on this night either." The gate never ran; there is no
  `night gate verdict=` line (record 01:15, 01:41).

So one of 65's two grounds is discharged and the other is untouched. That is
**partial discharge, not a change of ground**. A requirement resting on two
grounds survives the loss of one. Any ruling for (b) must therefore explain
why the surviving ground evaporated — and nothing in the 09-11 record does
that; the 09-11 night made the surviving ground *older*, not weaker.

---

## 2. My independent verdict on Q

**(c)** — with a shape that preserves item 6's words. Reasons, in order of
weight, are §3 (a live blocker that both (a)-as-written and (b) would sail
past) and §1.4.

### The shape

A `REHEARSAL_STUB` **night** at `t0` 2026-09-13 02:56 PDT — agents installed
09-12 between 03:00 and 06:30 PDT per `docs/phase_2/derivation_night_runbook.md:1194`
("Install BOTH agents on the calendar day BEFORE `t0`, between **03:00 and
06:30 local**") — so item 6's literal "night" is satisfied rather than waived.
Three conditions, because **(a) as the packet words it is satisfiable while
leaving the blocker of §3 alive**, and that is why my answer is (c) and not (a):

1. **Land the C1 registration conflict cure first** (§3). It is design-bearing,
   not clerical: it decides *which registration the night is bound to*.
2. **The stub plan must carry the same `registration_path` the equivalence
   night will carry.** rehearsal-20260911's plan carried
   `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`
   (verified: `01-harvest-evidence/night_plan.json`, key `registration_path`).
   A stub that exercises C1 against *that* file proves nothing about the
   equivalence night's C1. This is the single change that turns the stub from
   ceremony into a test.
3. **NIGHT-INTERPRETER-PIN-01 merged with tests green**, its `preflight` run by
   the installer under the plist's exact PATH (packet F4), and the rendered
   interpreter recorded in the arm record.

Green = `receipt.json` verdict `REHEARSAL_ONLY`; C1 PASS, C2 NOT_APPLICABLE,
C3 PASS, C4 PASS, C5 PASS with `chain_stub: built_in_stub_by_design` and null
digests (`joulewise/night_gate.py:1043-1052`); `launchd.night.err` 0 bytes at
`t0`; courier delivered.

**Earliest t0 permitted: stub 2026-09-13 02:56 PDT; equivalence night
2026-09-14 02:56 PDT** — both subject to F9's orphan-daemon blocker, which
refuses every census while it lives (`joulewise/night_gate.py:525`,
`scripts/run_night.py:1419,1466`) and which no ruling of mine can clear.

---

## 3. BLOCKER found at the desk: C1 refuses the equivalence night as the runbook arms it

This is the finding that decides my verdict, and neither the packet nor 65
contains it.

**The gate's expected value** — `joulewise/night_gate.py:32-41`:

```
32  # 2026-09-05: D-165 v2 relabel supersedes the v1 registration digest
34  D166_REGISTRATION_SHA256 = (
35      "dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265"
36  )
39  D166_REGISTRATION_PATH = (
40      "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"
41  )
```

**C1's test** — `joulewise/night_gate.py:1300-1326`: for
`receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}` it reads
`plan.registration_path`, hashes the UTF-8 bytes, and

```
1315  if registration_sha256 != D166_REGISTRATION_SHA256:
1321      Refusal("night_refused_registration", ...)
```

**What the runbook tells the equivalence night to put there** —
`docs/phase_2/derivation_night_runbook.md:484-489`:

> "`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` must be
> committed inside H … The plan's `registration_path` points at this file"

`:760` — table row for night 1: "`registration_path` | the committed
pre-registration of §0.5". And the arm block's own assertion, `:1283-1284`:

```
assert plan.registration_path.endswith(
    'configs/calibration/preregistration_d079_epoch_25g83_rev1.md')
```

**Executed evidence (this session, this worktree, read-only):**

```
$ shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json
dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265

$ shasum -a 256 configs/calibration/preregistration_d079_epoch_25g83_rev1.md
ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7
```

The first matches `D166_REGISTRATION_SHA256` exactly. The second does not.

**Finding B-1 (BLOCKER).** Armed exactly as its own runbook's foreground block
asserts, the equivalence night refuses at C1 with `night_refused_registration`
and captures nothing. The conflict is between two tracked authorities —
`joulewise/night_gate.py:34-41` and `derivation_night_runbook.md:484-489/760/1283-1284`
— and it is unresolved at this worktree's head. It also has a moving part: the
pre-registration's bytes changed on 09-10/09-11 when revision 2 was recorded
(`git log --oneline -- configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
→ `07995051`, `12162263`, "Record Ed's ruling (directive issue 316):
pre-registration revision 2"), and §0.5:526-528 says of that digest "a change
between nights is a stop, not a new pin."

Minimum cure, to be decided by PR before *either* night: either (i) the
equivalence plan's `registration_path` is `D166_REGISTRATION_PATH` and the
runbook's §0.5/§1.1/arm-assert are wrong, or (ii) C1 must accept the 25G83
pre-registration's digest. These bind the night to *different documents*, so
this is a design decision, not a typo fix.

**Effect on Q.** (b) walks straight into B-1 and loses the night. (a) *as the
packet words it* — "C1/C3/C4/C5 PASS" on a stub whose plan carries the d166
path — would go green **and still leave B-1 alive**, because the stub's C1
would hash the d166 file and pass. That is precisely why my verdict is (c):
(a)'s acceptance criteria are satisfiable without testing the thing that is
broken.

### 3.1 A hypothesis I raised and then refuted (recorded because charter §8 forbids silent disagreement)

I predicted a second defect: C1 reads a *repo-relative* path through
`read_text=lambda path: Path(path).read_text(encoding="utf-8")`
(`scripts/run_night.py:296`), which resolves against process CWD — desk-
unreachable if launchd's CWD differs. **Refuted:**
`configs/launchd/com.joulewise.night.plist.template:18-19` sets
`<key>WorkingDirectory</key><string>@@REPO@@</string>`. CWD is the measurement
clone. The relative path resolves. No finding.

---

## 4. Every way a judge choosing (b) could be WRONG under the contract words

1. **Class substitution.** Item 6 says `REHEARSAL_STUB`; the equivalence night
   is `DIAGNOSTIC_NO_PACK` (`runbook:734,750`). (b) does not satisfy the text;
   it waives it. If the judge writes (b) as a satisfaction rather than a
   labelled waiver, the ruling amends kernel text, which the packet itself
   forbids at line 33 and the charter forbids at §7.
2. **Charter §9 conversion.** 65:3 ruled "REQUIRED". (b) converts a governed
   REQUIRED into NOT REQUIRED by reinterpretation, on facts (a night that did
   not run) that discharged only the *other* ground.
3. **Surviving ground untouched.** Record 01:11 — "No gate row C1–C5 was
   exercised on this night either." (b) must assert the un-exercised rows are
   acceptable to run first on the night that matters; nothing in the packet
   argues that, and §3 shows the first live C1 would refuse.
4. **B-1 makes (b) near-certainly a wasted night anyway.** (b)'s whole case is
   schedule; B-1 destroys the schedule case unless cured first, and if it is
   cured first then (b) is resting on a desk cure of a defect nobody had found
   when the packet was written — i.e. on luck.
5. **Misreads what the 09-09 night proved.** 09-09 exercised launchd firing,
   the courier, the push, C5's head and C3's census. It never reached C1, C3's
   tail, or C4 (§1.4). "The launchd path works" is true of the *first third* of
   the gate only.
6. **Two failures, one signature.** 09-09 refused before the gate's tail
   (`night_probe_error` at the chain read); 09-11 died before the gate entirely
   (interpreter). Both are process-environment defects at the launchd boundary,
   neither a logic defect. Charter §9: "Two consecutive rounds failing with the
   same signature is a structural problem… If the packet shows this pattern,
   licensing another same-shape round requires explicit justification." (b)
   licenses the *most expensive possible* same-shape round.
7. **Desk `preflight` is not the launchd boundary.** F4's preflight runs from
   the installer under the plist's PATH. `launchd` supplies more than PATH; the
   plist (template:7-24) is the full contract, and only launchd instantiates it.
   Treating preflight as equivalent is the same substitution that failed twice.

## 5. Every way a judge choosing (c) could be WRONG

1. **"Night" waived for convenience.** The packet's *example* (c) — a daytime
   `rehearse` firing — is not a "night." If the judge adopts that example, it is
   a waiver of item 6's word and must be labelled as one, with Ed's veto
   preserved. (My (c) keeps the night and so avoids this.)
2. **Daytime C3 is not diagnostic.** A daytime firing must pass HID idle
   exactly `"0"` (`night_gate.py:1144`), `"AC Power"` in `pmset -g batt`
   (:1162), a `displaysleep` match (:1178-1182), `load_1m <= LOAD_MAX` (:1206)
   and every `CPU_Speed_Limit` equal to `"100"` (:1239). A daytime REFUSAL on
   any of these is environmental, proves nothing, and burns the install span
   for nothing. I did NOT execute these probes: **NOT EXECUTED.**
3. **Scope creep.** If (c) accretes conditions beyond what 65's ground needs,
   it becomes the over-gating (a) is accused of. My (c) adds exactly one
   substantive condition to (a) — condition 2, the shared `registration_path` —
   plus the B-1 cure that is mandatory on any route.
4. **Same-day rehearse collides with the 09-12 install span.** Installing a
   daytime rehearse, harvesting it, uninstalling, and re-installing for 09-13
   inside one day is three launchctl transactions in a window where an orphan
   daemon (F9) already refuses censuses. Higher operational risk than the thing
   it de-risks.

## 6. Every way a judge choosing (a) could be OVER-GATING under D-161

D-161's exact words, `docs/decision_log.md:207` (I read this row and no other
beyond D-161):

> "custody mechanisms whose ONLY defended-against actor is the trusted operator
> touching a file are over-engineering; this week they cost the operator three
> hand edits and blocked the mint twice"

and, in ruling (2):

> "enumerate from code (three-seat consult) every refusal whose only actor is
> the trusted operator and downgrade it to WARN-AND-RECORD or retire it;
> **fail-closed STAYS where the failure is PHYSICS/EVIDENCE or PRE-REGISTRATION**
> (missing calibration, unresolved anchor, absent floor, stale drift evidence,
> unfrozen plan, post-hoc analysis choice)"

The honest over-gating arguments against (a):

1. **D-161 preserves fences; it does not mandate rehearsals of fences.** Even
   granting §7's classification that C1/C3-tail/C4 are all physics/evidence
   fences, "fail-closed STAYS" says the *refusal* stays. It says nothing that
   requires a dress rehearsal. Requiring one is a **process rule**, and by
   CLAUDE.local.md rule 11 a process rule is exactly what the magistrate may
   not adopt alone — which is why this gate exists, but also why its cost must
   be justified on its own merits, not borrowed from D-161.
2. **The failure (a) prevents costs the same as (a) itself.** If a row refuses
   on the equivalence night, `scripts/run_night.py:1546-1570` writes
   `refusal.json`, logs "night gate refused", couriers the refusal, and returns
   `EXIT_REFUSED`. No sudo, no capture, no corruption, nothing irreversible.
   Cost: one calendar day. (a)'s cost: one calendar day, guaranteed (F7: "Each
   stub night costs one calendar day of the paper's measurement schedule and
   nothing else"). A gate that spends a certain day to avoid a possible day is
   value-negative whenever P(refusal) < 1.
3. **Ed's standing words cut against ritual.** "no silly gates on accepting
   numbers … physics/evidence refusals stay" (D-161 / F8); "docs are context,
   code is truth — don't bind to stale doc gates". A REQUIRED-second-night rule
   issued on 09-09, applied to a 09-11 night that never ran, is close to a
   stale doc gate applied by inertia.
4. **A stub cannot exercise the equivalence night's C5.** The stub takes the
   built-in branch (`night_gate.py:1043-1052`, `run_night.py:1572-1575`:
   `command = ["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]`), so the wrapper,
   its sidecar, the digest comparison (:1053-1108) and the chain are never
   touched. The stub buys three rows and leaves the highest-complexity row
   untested — an unflattering cost-per-row.

**Why these do not move me.** Argument 2 collapses on §3: B-1 makes
P(refusal) ≈ 1 on present code, not < 1. And argument 4 is an argument for
*strengthening* the stub's plan (my condition 2), not for skipping it.

## 7. Classification of each un-exercised row

| row | code that implements it | refusal | class under D-161 |
|---|---|---|---|
| **C1** | `joulewise/night_gate.py:1300-1328`; test at **:1315** `if registration_sha256 != D166_REGISTRATION_SHA256` | `night_refused_registration` (:1321) | **PRE-REGISTRATION fence.** D-161 names "PRE-REGISTRATION" and "unfrozen plan" in the preserved fail-closed list verbatim. Not prunable, not process. |
| **C3 tail** | HID **:1138-1154**; AC power **:1158-1172**; displaysleep **:1174-1192**; load **:1194-1216**; thermal **:1218-1249**; PASS at **:1252** | `night_refused_hid_idle` (:1150), `night_refused_not_quiet` (:1168,1188,1212,1245) | **PHYSICS fence.** Battery, thermal throttle, display wake and load change the electrical state during capture; a capture taken outside them is a different physical measurement. |
| **C4** | boot UUID **:1256-1280**; epoch/monotonic **:1281-1298**; PASS at **:1292** | `night_refused_boot_clock` (:1276) | **EVIDENCE fence on a real night** — it binds captures to one boot session and one clock pair, which is what makes the clock-anchor bound the equivalence night measures attributable at all. On a `REHEARSAL_STUB`, where nothing is measured, C4 defends no evidence and is a **process/self-test fence**. |

Note the asymmetry, which is the packet's most interesting un-asked question:
the rows are physics/evidence fences **on the night they matter** and process
fences **on the stub**. That is not an argument against the stub — you cannot
test a fence by breaking the thing it guards — but a judge should state it
rather than call all three "physics fences" flatly.

## 8. What a launchd-started night produces that no desk run can

Cited to `scripts/run_night.py` and the plist template, which is the actual
contract launchd executes.

1. **The plist's own interpreter resolution at `t0`.**
   `configs/launchd/com.joulewise.night.plist.template:7-17` —
   `/usr/bin/env`, `python3`, `@@REPO@@/scripts/run_night.py` — under
   `EnvironmentVariables/PATH = @@PATH@@` (:20-24) and nothing else. This is
   the exact mechanism that killed 09-11 at `scripts/run_night.py:1417`
   (`from joulewise import arm_readiness`), per record 01:12. A desk run
   inherits the operator's full environment; an installer-run preflight
   inherits it too, with PATH overridden. Only launchd starts a process from
   launchd's environment.
2. **Proof the driver was launchd-started, which the kernel demands by name.**
   Item 2 (`evidence[1]`): "produced by a **launchd-started driver (not a
   shell-started one)**". The only artefacts that prove it are the plist's
   `StandardOutPath`/`StandardErrorPath` handles (template:32-35), born at
   exactly `t0` — record 01:32-33 shows `launchd.night.out`/`.err` with birth
   `1789120560.022` = `t0`. A shell run produces no such handles.
3. **`StartCalendarInterval` firing at a real `t0`** (template:25-31) against
   the driver's real-time arithmetic: `_next_deadman_epoch(plan.t0_epoch_s)`
   (`run_night.py:1463`), `_completion_epoch_s(plan)` (:1464), the
   overrun refusal at :1465-1488, and the plan's 36-hour authoring-age bound.
   A desk run at an arbitrary hour exercises none of these against the clock
   the night will actually run on.
4. **The `t0` census in an agent-free machine state** — `run_night.py:1419`
   `agent_census(probes)`, journalled at :1435 — as opposed to a desk census
   taken while the operating session is, by construction, present.
5. **The courier launched from a launchd job with no TTY and no login shell** —
   `_resolve_courier_bin` (:600-627), `run_courier` (:774-870), the lock at
   :759-772, `_wait_for_courier` (:688). PARTIALLY DISCHARGED: 09-11's dead-man
   path exercised exactly this and delivered (record 01:13, message
   `1a090c8424231111`), as did 09-09.
6. **The results-branch push from a launchd context** — `run_night.py:542-569`,
   branch `night-results/{_night_date(plan)}` (:561). PARTIALLY DISCHARGED:
   record 01:13 and 01:23, `night-results/20260911` tip `37876416`, artefacts
   `cmp`-identical to custody.

Items 5 and 6 are genuinely discharged by the 09-11 dead-man and should be
struck from any list of reasons for another night. Items 1–4 are not, and items
1 and 2 are the two that a desk preflight structurally cannot reach.

## 9. What the magistrate must write to Ed

Whatever the verdict, the note must contain: (i) B-1 — the runbook's
`registration_path` conflicts with C1's pinned digest, with both observed
digests, and the two mutually exclusive cures, flagged as a decision that
changes which registration the night is bound to; (ii) C-2 — the kernel's hard
dependency `REHEARSAL-20260911-HARVESTED` names a plan that can never re-arm
and must be re-targeted, not dropped; (iii) the exact calendar arithmetic and
its cost (stub 09-13 → equivalence 09-14, versus equivalence 09-13, i.e. one
day of measurement schedule, no quota, no hardware wear); (iv) that item 6's
words name the class `REHEARSAL_STUB`, so (b) and the packet's daytime (c) are
**waivers** and are Ed's to veto; (v) F9 — the orphan daemon pid 83102 refuses
every census and only Ed or an interactive session can clear it, so no t0 is
reachable until it is dead; (vi) if the cold judge and I split, both sealed
outputs verbatim, per charter §5.

## 10. Summary of findings

| id | tier | finding |
|---|---|---|
| **B-1** | BLOCKER | `registration_path` per runbook §0.5:484-489 / §1.1:760 / arm-assert :1283-1284 hashes to `ca2430dd…`; C1 (`night_gate.py:1315`) demands `dfe55f8d…`. The equivalence night refuses at C1 as currently specified. |
| C-1 | MATERIAL | Item 6 names class `REHEARSAL_STUB`; (b) is a waiver, not a satisfaction. |
| C-2 | MATERIAL | Kernel hard dependency `REHEARSAL-20260911-HARVESTED` is unsatisfiable as written and must be re-targeted. |
| H-1 | MATERIAL | Packet hygiene: omits the kernel clause "21i acceptance item 6 was MET conditional on the cure landing" — the best text for (b). |
| C-3 | MATERIAL | (a) as worded is satisfiable without exercising C1 against the equivalence night's registration; the stub plan must carry the same `registration_path`. |
| N-1 | NIT | C4 is an evidence fence on a real night and a process fence on a stub; a ruling should say so rather than classify it flatly. |
| N-2 | NIT | The launchd courier (`run_night.py:774-870`) and results-branch push (:542-569) ARE discharged by the 09-11 dead-man and should be struck from the reasons for another night. |

Where I disagree with the lead's labelled disposition: the packet frames the
choice as (a) vs (b) with (c) as a residual. On the evidence, (a) as worded is
**insufficient**, not merely expensive — which no part of the packet
anticipates.

Not executed: the charter digest comparison; any HID/pmset/thermal/load probe;
any launchctl, network, or `~/night-custody` operation; any test suite; the
NIGHT-INTERPRETER-PIN-01 seat's result (still running at packet time, F4).

REFUTER VERDICT: (c) — a REHEARSAL_STUB night at t0 2026-09-13 02:56 PDT (install 09-12 03:00–06:30) carrying the equivalence night's own registration_path, after the B-1 cure and NIGHT-INTERPRETER-PIN-01 land; earliest equivalence night t0 2026-09-14 02:56 PDT. Strongest objection to my own verdict: B-1 was found read-only at a desk in minutes, which is itself evidence that desk audit — not a calendar night — is the efficient instrument for this defect class, and a judge could fairly hold that curing B-1 plus a full desk gate-replay discharges 65's remaining ground at zero schedule cost.
