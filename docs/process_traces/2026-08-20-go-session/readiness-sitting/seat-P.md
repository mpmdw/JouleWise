# SEAT P — PROGRAM ROWS + ED ROLL-UP

READY-CANDIDATE council sitting. Ruled head **5bd7acf** (`main == origin/main == HEAD`).
Baseline **8937dec**; **237** commits between them (the packet says 214 — corrected on the record).
Seat: Opus 5. Read-only worktree `wtRC-OPUS`. All probes below executed at 5bd7acf unless dated.

---

## 0. Charter-required seat preamble

**Enumerated evidence universe (independent, not inherited):** 54 adjudicable items —
14 program rows (`grep -c "^## P-" rows/ROW-P-PROGRAM.md` → **14**, not the 13 the index claims),
23 ED-QUALIFICATION rows (counted from the summary table), 17 OPEN-ITEMS
(A-1…A-15 + A-2b + A-14b).

**Coverage: 54/54 dispositioned. 36/54 carry an executed probe at 5bd7acf** — all 14 program
rows, all 17 open items, and 5 of 23 ED rows spot-verified against primary custody
(ED-QUAL-L1-2, ED-QUAL-L4-1, ED-Q-L9-1, ED-Q-L8-2, ED-Q-L9-3). The remaining 18 ED rows are
adopted from the sibling assembly's walk, with its "custody unreadable" caveat **lifted** for the
rows I opened — I can read `~/JouleWise-window-custody/` and did.

**Mandatory READY-falsification attempts** are recorded inline at P-3, P-7, P-11, P-12, P-13 —
the only rows I was minded to pass. One succeeded (P-13, below); it downgraded the row.

**Unexecuted obligations (listed, per charter:59-68):**
1. I did not re-enumerate any seat's evidence universe. That is P-1's work order; a seat cannot
   discharge it as a side effect, and its absence is why P-1 blocks.
2. No canonical-suite run at 5bd7acf.
3. No arm / dry-run / consume against `_v3` — barred by WINDOW-COUNCIL-GATE, by the [QUIET-MAC]
   rule while an agent fleet is live, and by D-131 cl.4 attempt-ID burn.
4. I did not read the 11 seat row files. These grades are program-level and pre-empt no seat verdict.
5. I opened 5 of ~14 off-repo custody artifacts.

---

## 1. PER-ROW GRADES — P-1 … P-14

### P-1 — "the work-order program is NOT CERTIFIED COMPLETE" → **BLOCKING**

`ls docs/process_traces/ | grep -i reaudit` → **one** directory, `2026-08-15-l2-reaudit`. No
re-enumeration exists for the other ten universes; no adversarial coverage attack has been run
against this sitting's packet. The verdict made both a *condition* of the READY-candidate
re-audit (`council-verdict.md:18-22`), and the one universe that was re-enumerated was measured at
`fac87d1` — its 251 denominator is 289 at the current head by the re-audit's own method.

*Why blocking, not conditioned:* the cold pairing ruled every un-retested denominator suspect.
Under NOT-READY that error was conservative; under READY it is fail-open. Passing seat rows on
self-nominated coverage is the exact failure the last sitting recorded one-for-one against.

*Failure scenario:* a seat passes on a denominator of 20 when the real universe is 200; the ten
un-enumerated hazards ride into a funded, unattended window.

### P-2 — audit-baseline manifest supersession → **BLOCKING** (executed, upgraded)

`git log -- docs/process/audit-baseline-manifest.json` → one commit (`694442c`). It still pins
`head_commit`/`origin_main` = `ac3fe1d…`, and carries **none** of the three ruled supersession
fields (`pack_digest_algorithm` absent; no chain-template note; no per-binding paths — verified by
key walk).

**I recomputed all three pinned digests** via `joulewise.arm_readiness.committed_pack_tree_sha256`
at 5bd7acf:

| pack | manifest | recomputed | |
|---|---|---|---|
| `d117_floor_qwen25_1p5b_v1` | `f4c02c8a…` | `5def6e51…` | **MISMATCH** |
| `d117_floor_qwen25_7b_v1` | `6a8a3bf6…` | `2091df58…` | **MISMATCH** |
| `d117_contrast_qwen25_1p5b_vs_7b_v1` | `1cc0c784…` | `878f16ea…` | **MISMATCH** |

Cause confirmed: `generate_configs.py` inside each frozen `_v1` pack changed after the freeze
(`git diff --stat ac3fe1d..HEAD` → 3 files, +1734/−215). This upgrades OPEN-ITEM A-2b from a
static finding to executed proof at the ruling head. Verdict Disposition 1 established
byte-identical recompute *at 8937dec*; that is no longer the state. Charter amendment 12's
final-head invalidation is live against **every** 2026-08-15 lens result.

*Failure scenario:* the sitting rules against a governing baseline document that authenticates
nothing — the integrity binding a reviewer would check is already broken, silently.

### P-3 — M-2 remand → **CONDITIONED**

Satisfied limb: the remanded gate ran with primaries attached (`2026-08-15-m2-coldgate/packet.md`
`62d4479`; composed verdict `6760a9b`), and the decision log carries the amendment as its own
entry (`docs/decision_log.md:9406-9418`).

*Falsification attempt (executed):* I tested whether freeze-0003 actually retired M-2 under
clause (c) ("retirement occurs at successor freeze ONLY IF the Phase-2 generator work makes
draft_status freeze-aware"). Result — **the strike fails halfway.** The `_v3` `plan_tree.json`
now reads `"draft_status": "as_generated_pre_d134_freeze"` (bytes cured), but the generator's own
`--check` message still prints *"verified d117_floor_qwen25_1p5b_v3 **unfrozen draft**"*
(`docs/process_traces/2026-08-19-refreeze-execution/s4/check-preauthor-1p5b_v3.log:1`) — the
human-operator ambiguity M-2 exists to resolve survives in the tool's own words. `_v1` bytes
remain `"unfrozen_draft"` permanently, so M-2 stays operative for `_v1`/`_v2` for their lifetime.

Second residue: composed-verdict item 2d's **RULING-REQUIRED** row. Clause (e) puts the contrast
pack's pending-ratification/TODO markers **outside** M-2 and gives them their own ruling row; no
such ruling exists anywhere in `docs/` outside the m2-coldgate directory.

**Condition:** a written 2d ruling, plus a stated per-pack M-2 retirement determination for `_v3`
(and for the compelled `_v4`), plus the generator message corrected or the ambiguity re-registered.

### P-4 — the sitting-type amendment is not in the charter → **BLOCKING (form; cheap to cure)**

`git log -- docs/process/instrument-readiness-audit-charter.md` → one commit (`6a7849c`).
`grep -c "READY-CANDIDATE\|ENUMERATING"` → **0**. The live `WINDOW-COUNCIL-GATE` clearance string
in `state_kernel.json` cites
`instrument-readiness-audit-charter.md#verdict-form-amendments-11-12` for language that document
does not contain. Charter:77 still reads flatly "Only T0 rows may remain open at the sitting."

*Why this blocks rather than annoys:* the amendment is the only thing that would let a sitting hold
with non-T0 rows open, and it has no home in the authority the gate points at. The sitting cannot
rule *under* a rule that is not in the ruled document. Cure is cheap (charter v3, or a recorded
ruling that `council-verdict.md` is the operative amendment carrier, plus a repointed clearance
string) — but until then charter:77 binds literally, and 20 of 23 ED rows violate it.

### P-5 — same-signature consequences (a)(b)(c) → **BLOCKING (process integrity)**

`grep -rln "drafting-mechanic" docs/ .claude/` at 5bd7acf → only `docs/council_log.md` and the two
council packet directories. All three adopted consequences remain unhomed. Consequence (a) — the
mechanical rule-11 trigger enumeration over the decision log, blocking packet finalization — is the
one the council named as "the one consequence that would have caught this cycle's failure
prospectively" (`council_log.md:3748`), and its absence means **this packet was finalized without
it**. That is the same signature a third time.

**Escalation notice to the magistrate (rule 11, standing trigger):** two consecutive rounds with
the same signature means the next spend is a CONSULT, not another round. This is round three of
"stop-signal question ruled under packet-finalization pressure, consequence adopted, consequence
never homed." I record it as met and refer it rather than absorbing it.

### P-6 — the 23-finding sweep, formally UNVERIFIED → **BLOCKING**

No per-finding verification ledger exists at 5bd7acf. Only B4 was ever adjudicated (REFUTED).
Under charter:66-68 an unverified item is UNVERIFIED, and amendment 11 makes UNVERIFIED
**independently disqualifying** — this row alone denies a council READY.

B7 (claim-bearing, P1) confirmed live: `docs/paper/draft-v1.md` carries the conservative regime at
`:124/:364/:388` (8.611855 J) and the tighter one at `:367/:375` (1.869502 J), with `:272` stating
the swap "executes at the first post-freeze mint … and has not been applied here." The
contradiction is documented as pending, not resolved.

**Two new same-class defects I found at the ruling head, which no sweep has caught:**
1. `WINDOW_STATUS.md:2-4` asserts *"RESOLVED (2026-08-19 night): … the evidence-expiry/no-reboot
   hazard is closed."* **This is false at 5bd7acf.** The `_v3` arm evidence dies ~17:00Z today and
   the D-148.5 ruling (`2026-08-20-go-session/MAGISTRATE-RULING.md` R-2) rules the fuse **LAPSES**
   and compels a `_v4` re-freeze. An operator-facing status document declaring a live hazard closed,
   at the sitting that would clear the window gate, is precisely the B1 defect class.
2. `docs/paper/draft-v1.md:189` still carries *"NOTE: freeze-0003 itself is not yet minted"*,
   contradicted by `5e38f1e`/`eb7f6c6`/`94dc3b3`/`8b2b021`, all now on main.

Also: `CLAIMS_STATUS.md:38` reads "Last updated: **2026-08-16** (T9 close)" under a 2026-08-19
banner. The sweep itself is 237 commits stale.

### P-7 — re-freeze ONCE, atomically, LAST → **BLOCKING** (and worsening prospectively)

*Falsification attempt (executed):* `git log --oneline 94dc3b3..HEAD -- configs/campaigns/` →
**0 commits**. So **LAST is satisfied at 5bd7acf** — no pack-byte change follows the final
freeze-0003 mint. That is the one limb that passes.

ONCE does not: `_v2` frozen → reverted → re-minted → reverted → re-minted a third time → a whole
`_v3` family → freeze-0003.

And the decisive post-packet fact: **a fourth pack-byte generation is now compelled.** D-148.5 R-2
(`MAGISTRATE-RULING.md:23-42`): *"the fuse LAPSES … The `_v4` re-freeze is compelled by the fuse
regardless."* Opus W2's warning — "any earlier pack-byte change forces an extra baseline
supersession and re-audit round" — is therefore not a hypothetical; it is scheduled. Any row this
sitting passes against `_v3` is a row passed against a family the project has already decided to
replace.

Unsatisfied throughout: no end-to-end T-0 pass at the exact reviewed head (Opus W8), and no
successor arm packet — both preconditions to the successor arm packet regardless of every other row.

### P-8 — the ED-QUALIFICATION gate (23 rows) → **BLOCKING**

Re-tally at §2 below: **3 CLOSED / 12 PARTIAL / 8 OPEN**, unchanged in substance from assembly, and
independently confirmed: `find ~/JouleWise-window-custody -maxdepth 2 -newermt "2026-08-19"` →
**empty**. No ED row has closed since the packet was assembled.

Charter:79-83 requires all ED-QUALIFICATION rows closed with evidence for a council READY. 20 of
23 are not. This is dispositive on its own face, independent of every seat row.

### P-9 — this sitting's own form → **BLOCKING** (with one strike in the packet's favour)

**STRIKE — the packet is wrong on one point:** `scripts/validate_gate_packet.py` **EXISTS** at
5bd7acf (580 lines; committed at `3835288` and predecessors). The claim that it is "still unbuilt,
so the trust anchor is manual" is false. The trust anchor is available.

Everything else stands, and the strike makes one item worse:
- The packet **does not conform to the validator's grammar** — `grep -rl "Charter pin\|Exhibit
  manifest"` over `ready-packet/` → **zero hits**; the validator refuses it. A conformant packet
  was buildable and was not built.
- **No sealed custody** under `docs/process_traces/<date>-readiness-council/` — only the 2026-08-15
  directory exists. This packet lives under `2026-08-19-prep-sprint/ready-packet/`, which is not
  the charter-mandated path.
- **No extraction script committed beside the packet** (`ls ready-packet/*.py` → none), violating
  the M-2 gate's non-author-assembly protocol, whose whole point is that the reviewed party here is
  the magistrate.
- **No fresh rule-11 cold pairing convened** for this sitting.
- **The packet is internally inconsistent, in the exact class Opus N3 flagged last time:**
  `00-INDEX.md` says "the thirteen program-level rows (P-1…P-13)" — twice — while
  `rows/ROW-P-PROGRAM.md` contains **14**. P-14 is un-indexed, and my own seat charter inherited the
  undercount. A row that exists in the packet and in no index is a row that gets adjudicated by
  nobody.
- **Two independent, unreconciled assemblies** ship in the same custody (`ready-packet/` and
  `ready-packet-rows/`). Useful as divergence evidence; not a sealed packet.

### P-10 — Phase-1 completion per the state kernel → **BLOCKING**

Read at 5bd7acf from `docs/process/state_kernel.json` (`updated: 2026-08-19` — already stale
against this head's 2026-08-20 landings; `active_stop_card: null`; `WINDOW-COUNCIL-GATE` live with
`allowed_task_ids: []`):

| WO | status | residue (verbatim) |
|---|---|---|
| WO-CENSUS-SEMANTICS | **blocked** | held until Ed supplies ED-Q-L9-3 |
| WO-CONSUMPTION-EDGE | **partial** | "the production freeze (rides Phase 2) + the same-head production-pack L10 replay" |
| WO-DETECT-PULSES-BUDGET | **partial** | still "MERGE-STAGED for the atomic re-freeze" — stale; `e22e658` is an ancestor of HEAD (A-8 confirmed) |
| WO-LAUNCH-BINDING | **queued** | "remaining: stage 4 successor flag inside the transaction. **Launch stays NO-GO**" |

The project's declared sole work-selection authority records the underlying repair incomplete and
launch explicitly NO-GO. A council READY that is condition (1) of an automatic launch cannot
coexist with it.

### P-11 — queue pack identities, the Phase-3 precondition, D-149 → **BLOCKING** (one limb struck)

**STRIKE — A-13 is CURED at 5bd7acf.** `TASK_QUEUE.md` Q2/Q3/Q4 now name `d117_*_v3` in *both*
task text and acceptance evidence (`grep` for the `_v1` ids in those rows → no hits), and the kernel
window rows' `goal` fields name `_v3`. The intra-row pack-identity drift is gone.

The row still blocks on three other limbs:
1. **The queue itself asserts the Phase-3 re-audit as a precondition to this sitting**, and it does
   not exist (P-1, P-2, A-3). If the queue text is right, this sitting is convened out of order.
2. **The cured identity is about to go stale again.** `_v3` is a dead family within hours (fuse
   LAPSE + compelled `_v4`, D-148.5 R-2). The fix landed one generation before the generation it
   fixes is retired.
3. **D-149's circularity plus an unbuilt evaluator.** Condition (1) of auto-GO *is* this sitting's
   verdict; conditions (2)-(5) are "evaluated mechanically at T-0" — but no evaluator exists
   (`ls scripts/*d149*` → none; `d149-go-receipt-template.md:63` says one "MAY be built"). So
   "mechanical evaluation" is today a markdown checklist filled by the issuing agent. A READY here
   arms an unattended window whose four remaining gates are self-attested prose.

### P-12 — findings retired by ruling / risk acceptance → **CONDITIONED (form question, ruled)**

The row asks the sitting to state which position it takes. **I rule: acceptance RELABELS; it does
not DISCHARGE.** Three grounds:
1. The charter's clearance form admits three verdicts. "Accepted limitation" is not one of them,
   and a fourth informal category is how a deleted conditional pass returns through the back door.
2. The struck findings (L8-B4, WO-L2-4, F4's timing premise) were struck on **executed refuter
   evidence** — a different and stronger basis. Blurring the two would let authority-retired rows
   inherit evidence-retired rows' standing.
3. Ed's threat-model authority is legitimate for **risk appetite**. It is not an assertion that the
   instrument fails closed, which is what the charter asks.

Operative effect: these rows are neither READY nor NOT-READY. They attach to the verdict as
recorded limitations and must appear in the paper's limitations section, `CLAIMS_STATUS.md`, and the
pack/window custody a reviewer sees.

*Falsification attempts on the two probes I could execute — both STRIKE in the project's favour:*
- **D-146 barrier enforcement is executed-verified**, not asserted: the D-144 seat pass records
  terra's executed walk — "the stored-v2 claim-barrier walk refuses in all three lanes"
  (`d144-seatpass-ruling.md`). D-148.7's "mechanically enforced" claim is corroborated. Probe struck.
- **P2-006 was retired by formal ruling, not silent deletion**: `docs/decision_log.md:9037`,
  "R3 RULED (magistrate, 2026-08-15; council-verdict Phase 0): P2-006 formally RETIRED from window
  selection." Probe struck.

**Conditions:** state this ruling in the verdict; refresh `CLAIMS_STATUS.md` (still stamped
2026-08-16); register the check-to-grant limitation in `docs/risk_register.md`, where L4 found it
absent.

### P-13 — which head is this sitting about → **CONDITIONED** (substance cured; discipline falsified)

Substance is cured by the merge wave. At 5bd7acf, `main == origin/main == HEAD`, and every commit
the packet listed as branch-only is an ancestor:

```
47d2645 YES   a61ac92 YES   b7e5730 YES
5e38f1e YES   94dc3b3 YES   0e96dbb YES
```

The D-148.2 merge gate was discharged, not waived: gate 3 (D-144 pre-merge seat pass) returned
**GO with zero blockers from both seats** (`d144-seatpass-ruling.md` — the r5→r6 drift class it was
convened to hunt "DOES NOT RECUR at the merge head, proven by recomputation"); gate 2 fresh-pass
CLEAN; gate 1's canonical residue fixed at `60ddb03`. P-13's head question is answerable and
answered: **the sitting attaches to 5bd7acf.**

***READY-falsification attempt — SUCCEEDED, and it downgrades the row.*** The row's own demand was
"a frozen, named head … with the fleet quiesced so it cannot advance during adjudication." I tested
it. The primary worktree `/Users/edr/code/JouleWise` is at **`b9e197a`** — one commit past the
sitting's head, landed **during this sitting**. The head is still moving.

Mitigating and verified: `git diff --stat 5bd7acf..b9e197a` → `README.md`, `RUN_STATE.md` only
(2 files, +95/−15). Instrument scope is empty, so no lens result is invalidated.

**Condition:** record 5bd7acf as the ruled head in the sealed packet, with the executed statement
that `b9e197a` is bookkeeping-only and instrument-scope-empty, and impose a writer freeze for the
remainder of the sitting. Correct "214 commits" to **237**.

### P-14 — D-149 deleted the launch-authority clause; the runbook never heard → **BLOCKING**

*(Present in `rows/ROW-P-PROGRAM.md`; absent from `00-INDEX.md` and from this seat's charter. I
grade it because an un-indexed row is otherwise adjudicated by nobody — see P-9.)*

Verified at 5bd7acf: `grep -rn "D-149\|no-hands\|unattended" docs/phase_2/*.md` → **0**. The
runbook still reads "Ed's decision; no automated word performs or authorizes the physical launch"
(`:786`), "E-10 — Ed's deliberate physical launch" (`:1055`), "not current authority to launch …
E-10 remains NO-GO" (`:1086`, `:1129`).

**And the contradiction is now internal to the kernel too**, which the packet did not catch: the
three window rows carry the D-149 auto-GO fence with the physical-launch-authority clause deleted,
while `WO-LAUNCH-BINDING`'s own fence at `state_kernel.json:3338` still reads *"The launcher
enforces admission but never becomes physical launch authority; **Ed still launches**"* — citing the
same council verdict as its authority. Three operative documents, two incompatible launch models,
one of them self-contradictory.

No seat has audited the no-hands path. `WINDOW_STATUS.md` contains zero D-149 references. The
automation is unaudited surface introduced *after* the audit this sitting is closing, and D-149's
own condition (1) is this sitting's verdict.

*Failure scenario:* an automated driver at 02:00 obeys the kernel fence and launches; the runbook
Ed would have followed says E-10 is NO-GO; the D-078 no-retry discipline (D-149 condition 5) has no
human present to observe the refusal it governs.

---

## 2. ED-QUALIFICATION ROLL-UP, RE-TALLIED AT 5bd7acf

**Tally: 3 CLOSED · 12 PARTIAL · 8 OPEN · 0 SUPERSEDED — unchanged in substance from assembly.**

Independently verified: `find ~/JouleWise-window-custody -maxdepth 2 -newermt "2026-08-19"` →
**empty**. Zero rows closed since the packet was assembled.

**What the merge changed (one row improves):**
- **ED-QUAL-L1-2** — the "branch-only" caveat is **CURED**. `freeze-0003.json` ×3 and the U11
  projections are on main at 5bd7acf. Stays CLOSED.
- **ED-QUAL-L4-1**, **ED-Q-L9-1** — unchanged CLOSED. I opened both primaries the assembler could
  not: `ed-qual-20260817/decisive-replay.log` tails `DECISIVE REPLAY: OK`;
  `keyboard-backlight.txt` present, 2026-08-17 18:00:42. The custody-unreadability caveat lifts for
  these two; their *substantive* caveats (pre-r5/r6 head; mutable setting with no T-0 re-check) stand.

**What I confirmed independently for the two most consequential OPEN/PARTIAL rows:**
- **ED-Q-L8-2 (the dress rehearsal — "the program's most valuable Ed hour") — OPEN.**
  `ls -d ~/JouleWise-window-custody/*rehearsal*` → **no matches**. Never run. Its mechanism
  (`ad14ac4`) is `_v2`-bound and will need rebuilding `_v4`-bound.
- **ED-Q-L9-3 — PARTIAL.** The capture is real and complete on its first clause (4 process censuses
  + 1 maintenance census, 2026-08-17 23:51). The second clause — commit them as the regression
  fixture — has **no artifact**: `find . -name "*quiet*census*"` → nothing;
  `git grep -l watchdogd -- tests/ configs/` → nothing. `WO-CENSUS-SEMANTICS` stays blocked, and
  with it the L8/L9 census blockers.

**The forward-looking correction the packet could not make.** The compelled `_v4` re-freeze
(D-148.5 R-2) **reopens the pack-bearing closures by construction**. ED-QUAL-L1-2 is a re-author of
*pack-side freeze evidence*; on a `_v4` family it must be re-executed. ED-QUAL-L1-1, ED-QUAL-L6-2,
EDQ-L2-2 and ED-L7-2 all bind pack identity or a reviewed-head dry-run and are likewise
`_v4`-invalidated.

> **Honest forward tally: 2 durable CLOSED / 21 not.** The single CLOSED row the merge cured is the
> single CLOSED row the `_v4` re-freeze will uncure.

Under charter:79-83 a **single** unclosed ED row denies council READY. There are twenty.

---

## 3. DISPOSITIONS — ALL 17 OPEN ITEMS

| # | Item | Disposition at 5bd7acf |
|---|---|---|
| A-1 | Ten of eleven universes never re-enumerated | **STANDS — blocking.** One re-audit dir only; its own 251 denominator is 289 at head. |
| A-2 | Manifest not superseded | **STANDS — blocking.** One commit; dead head; none of the 3 ruled fields. |
| A-2b | `_v1` pack bytes changed; digest binding broken | **STANDS — UPGRADED to executed proof.** All three digests recomputed **MISMATCH** at the ruling head. |
| A-3 | Phase-3 focused re-audit of L1/L5/L7 | **STANDS — blocking.** Does not exist. |
| A-4 | Charter never amended | **STANDS — blocking (form).** 0 hits for READY-CANDIDATE/ENUMERATING; clearance string cites absent language. |
| A-5 | Three same-signature consequences unhomed | **STANDS — blocking.** All three; (a) absent means this packet was finalized uncertified. **Escalation trigger referred.** |
| A-6 | 23-finding sweep formally UNVERIFIED | **STANDS — blocking (UNVERIFIED is independently disqualifying).** B7 live; +2 new defects found (`WINDOW_STATUS.md:2-4` false; `draft-v1.md:189` stale). |
| A-7 | Four Phase-1 WOs not closed on the kernel | **STANDS — blocking.** All four verbatim unchanged; "Launch stays NO-GO". |
| A-8 | Kernel merge-state narrative stale | **STANDS — finding.** Still "MERGE-STAGED"; kernel `updated: 2026-08-19` at a 2026-08-20 head. |
| A-9 | ONCE/atomically/LAST not evidently satisfied | **STANDS and WORSENS — blocking.** LAST verified satisfied (0 pack commits after `94dc3b3`); ONCE violated; a **`_v4` re-freeze is now compelled**, so W2's extra round is scheduled, not hypothetical. |
| A-10 | No end-to-end T-0 pass at the reviewed head; no successor arm packet | **STANDS — blocking.** Neither located. |
| A-11 | M-2 residues | **STANDS — specified.** 2d ruling absent; `_v3` bytes freeze-aware but the `--check` message still says "unfrozen draft"; `_v1` permanently not. |
| A-12 | This sitting's form preconditions unmet | **STANDS — blocking, with ONE STRIKE.** `validate_gate_packet.py` **exists** (strike the "unbuilt" limb) — which makes it worse: the packet fails its grammar (no Charter pin / Exhibit manifest), has no sealed custody, no extraction script, no cold pairing, a 13-vs-14 row-count error, and two unreconciled assemblies. |
| A-13 | Queue rows name two pack generations | **STRUCK — cured.** Q2/Q3/Q4 and kernel goals name `_v3` in both limbs. Superseded by a larger problem: `_v3` is itself the about-to-be-stale generation. |
| A-14 | D-149 removed the human margin | **STANDS — blocking.** Plus: evaluator unbuilt; `WINDOW_STATUS.md` never reconciled (0 D-149 refs); kernel now self-contradictory at `:3338`. |
| A-14b | ED roll-up: 20 of 23 not in an acceptable state | **STANDS — blocking.** Re-tallied and independently confirmed from the custody root; forward tally 2 durable CLOSED. |
| A-15 | Findings retired by risk acceptance | **STANDS as a FORM RULING (P-12): acceptance relabels, does not discharge.** Two probes struck in the project's favour (D-146 barrier executed-verified; P2-006 retired by formal ruling `decision_log.md:9037`). |

Net: **15 stand, 1 struck (A-13), 1 stands-with-a-strike (A-12).** Two are upgraded from static to
executed (A-2b, A-9). Three new defects added under A-6/A-12/A-14.

---

## 4. THE CHARTER'S AGGREGATION PRECONDITIONS — ANSWERED

### Does any path to READY exist at 5bd7acf? **No.**

Amendment 11 requires three things conjunctively. Each fails independently, on program evidence
alone, before a single seat row is read:

1. **"all ED-QUALIFICATION rows closed with evidence"** — 20 of 23 are not (P-8, A-14b). Dispositive
   on its face.
2. **"no UNVERIFIED"** — 22 sweep findings are formally UNVERIFIED as a body (P-6), and every seat's
   coverage denominator remains self-nominated with no independent re-enumeration (P-1), which the
   cold pairing already ruled makes them suspect. UNVERIFIED is independently disqualifying.
3. **Form preconditions** — no sealed custody, no packet in the validator's grammar, no extraction
   script beside it, no fresh rule-11 cold pairing (P-9).

Any one of these denies READY. All three hold.

### Does a CONDITIONALLY-READY aggregate exist? **No — and the sitting must not invent one.**

READY-WITH-CONDITIONS is **DELETED** by amendment 11, and the brief records exactly why: a fleet
that returns one READY makes a conditional option a live fail-open hazard. The available verdict
forms are READY / NOT-READY(+work orders) / UNVERIFIED per component, and a council READY or
nothing. **A "conditionally-ready" aggregate would be the deleted verdict returning under a new
name**, at the sitting where it is most dangerous — because under D-149 this verdict is condition
(1) of an automatic, unattended window launch whose other four conditions are an unbuilt evaluator's
markdown checklist.

My conditioned grades on P-3, P-11, P-12, P-13 are **per-row work orders**, not a conditional pass.
They do not aggregate.

### Recommended aggregate: **NOT-READY**, with the UNVERIFIED coverage finding carried distinctly.

The distinction matters: NOT-READY carries work orders; UNVERIFIED carries a mandatory re-audit.
Coverage (P-1) is the second, not the first, and must be recorded as such so the re-audit obligation
survives the work orders.

### Minimal condition set

**Preconditions to *holding* a READY-candidate sitting at all:**

1. **Hold the sitting AFTER the `_v4` transaction, not before.** D-148.5 R-2 sequences
   "merge wave → READY-candidate sitting → `_v4` transaction". *I dissent on that ordering and would
   invert the last two* — the fuse compels a `_v4` re-freeze, so a sitting held now rules every
   pack-bearing row and one of the three closed ED rows against a family already decided dead, and
   guarantees the extra baseline supersession + re-audit round Opus W2 warned of. Ruling `_v3`
   READY today buys a verdict with a known expiry.
2. **Supersede the audit-baseline manifest** — worded as SUPERSESSION, never re-pin — pinning the
   ruled head and live pack digests, carrying all three ruled fields. Executed justification: three
   digest MISMATCHes at 5bd7acf.
3. **Fold S12 + S11 into a charter v3** (or record that `council-verdict.md` is the operative
   amendment carrier) and repoint the kernel clearance string at language that exists.
4. **Seal the packet properly:** custody under `docs/process_traces/<date>-readiness-council/`, in
   `validate_gate_packet.py`'s grammar (Charter pin + Exhibit manifest), extraction script committed
   beside it, dual assemblies reconciled, the 13-vs-14 program-row count fixed, fresh rule-11 cold
   pairing convened.
5. **Freeze the head with the fleet quiesced** for the sitting's duration and record the SHA.

**Preconditions to *passing*:**

6. **Re-enumerate all eleven evidence universes at the ruled head** and execute one adversarial
   falsely-clean attack against whichever row reads cleanest. Re-run L2's specifically — its
   denominator moved 251 → 289.
7. **Per-finding disposition ledger for all 23 sweep findings**; resolve B7 (claim-bearing, P1);
   re-run the sweep at the ruled head — the last one is 237 commits stale and already misses
   `WINDOW_STATUS.md:2-4` and `draft-v1.md:189`.
8. **Close the ED gate — 20 rows.** Non-negotiable. Critical path: ED-Q-L8-2 (never run; mechanism
   must be rebuilt `_v4`-bound); ED-Q-L9-3's committed fixture (unblocks WO-CENSUS-SEMANTICS, which
   unblocks the L8/L9 census blockers); ED-L3-2 (≈1 minute of machine time); ED-Q-L8-4; ED-L7-1/-2;
   EDQ-L2-2; and **ED-L10-1, which needs a scope ruling first** — D-148.7 may have made it
   structurally unpassable, and nobody has adjudicated that.
9. **Close or formally re-dispose the four Phase-1 WOs on the kernel.** At minimum, "Launch stays
   NO-GO" cannot coexist with a verdict that is condition (1) of an automatic launch.
10. **Audit the D-149 no-hands path as its own lens, build the mechanical evaluator, and reconcile
    the kernel and the runbook into one stated launch model** (including the self-contradictory
    `WO-LAUNCH-BINDING` fence at `state_kernel.json:3338`). Automation introduced after the audit is
    unaudited surface, not a discharge.
11. **Home the three same-signature consequences, (a) first** — and refer the third occurrence to a
    consult per rule 11 rather than absorbing it.
12. **Rule the two M-2 residues in writing** (item 2d; per-pack retirement for `_v3`/`_v4`).
13. **End-to-end T-0 pass at the exact reviewed head** (Opus W8) before any successor arm packet.
14. **Record the P-12 form ruling** — acceptance relabels, does not discharge — in the verdict.

Items 1-5 gate the sitting; 6-14 gate the verdict. Nothing here is discretionary under the charter
as written.
