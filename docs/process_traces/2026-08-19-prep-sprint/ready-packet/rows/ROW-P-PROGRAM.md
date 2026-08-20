# ROW P — PROGRAM-LEVEL ROWS (not seat rows; the sitting must adjudicate these too)

Assembled read-only at `impl/r2-s0-mint-resolver` HEAD **4597ad4** against council audit baseline
**8937dec**. These rows come from the 2026-08-15 verdict's ADJUDICATED DISPOSITIONS, PROCESS
RULINGS, and the four-phase work-order program — none of them belong to a single lens seat, and
all of them condition whether any seat-level READY can aggregate into a council READY.

Candidate dispositions below are **assembled, not adjudicated**. The sitting rules.

---

## P-1 — "The work-order program is NOT CERTIFIED COMPLETE"

### (a) Original finding, verbatim

> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every
> seat's evidence universe was self-nominated, and the one denominator adversarially tested fell.
> Closing all listed work orders does not entitle READY; the READY-candidate re-audit must
> re-enumerate every universe independently and run the adversarial coverage attack as a standing
> packet element.

— `docs/process_traces/2026-08-15-readiness-council/council-verdict.md:18-22`

Supporting source caution, `docs/council_log.md:3760`:

> The fleet's aggregate coverage (219/253 across eleven seats) is arithmetic over self-nominated
> denominators and is NOT an audit-coverage figure. The one denominator adversarially tested went
> from a claimed 16 to a real 251. Both cold seats ruled every other denominator suspect for
> exactly this reason. Do not quote 219/253 as coverage; the honest statement is that coverage is
> unquantified pending the Phase-3 re-enumeration.

### (b) What changed since

- **One universe re-enumerated: L2's only.** `WO-L2-REAUDIT` delivered same-day; custody
  `docs/process_traces/2026-08-15-l2-reaudit/` (commit `0f886d3`), recorded at `TASK_QUEUE.md:103`:
  "Coverage VERIFIED — 251/251 test IDs independently enumerated (procedure sensitivity-probed ×3),
  247/251 current-head executed (242 pass, 5 declared skips, 4 crash-matrix IDs attributed to the
  registered WO-DETECT-PULSES-BUDGET limitation)". That re-audit's "current head" is a 2026-08-15
  head, not 4597ad4.
- **The other ten universes: no re-enumeration located.** Searched `docs/process_traces/` (all 37
  dirs), `docs/run_reports/2026-08-16-t9`, `-08-18-t10`, `-08-19-t12-t13`, `TASK_QUEUE.md`,
  `docs/council_log.md` for any Phase-3 coverage re-enumeration artifact. **EVIDENCE NOT LOCATED.**
- The adversarial coverage attack has **not** been re-run as a "standing packet element" for this
  candidate sitting by any artifact found in-repo.

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN.** What remains: independent re-enumeration of ten evidence universes at the current
head, plus at least one executed falsely-clean/adversarial coverage attack against this sitting's
own packet. Note the structural asymmetry the cold seats recorded: coverage error is conservative
under NOT-READY but **fail-open under READY** — the risk transfers entirely to this sitting.

### (d) What a skeptical seat should probe

1. Ask for the re-enumeration artifact per seat. Absent one, treat the seat's coverage figure as
   the self-nomination the cold pairing already ruled suspect (`cold-fable-ruling.md` §E).
2. Pick the seat with the highest claimed coverage ratio and independently count its denominator
   at 4597ad4 — the L2 attack found 16 claimed vs 251 real.
3. Check whether 214 commits of new code added producers/tests/artifact kinds that no 2026-08-15
   universe could have contained. `git diff --stat 8937dec..HEAD` is the starting probe.
4. Demand the falsely-clean attack be run against whichever row now reads cleanest — that is
   exactly the shape that failed last time.

---

## P-2 — Audit-baseline manifest: final-head invalidation and the ordered SUPERSESSION

### (a) Original finding, verbatim

Charter, `docs/process/instrument-readiness-audit-charter.md:88-91`:

> final-head invalidation — any repo change after the baseline manifest voids affected lens
> results.

Verdict, `council-verdict.md:68-70`:

> **Manifest conditions at supersession** (cold §B.2, Opus S11): add `pack_digest_algorithm`,
> the chain-template coverage note (embedded in runbook §6, covered by runbook_sha256), and
> paths for all bindings. The magistrate's earlier "manifest requires NO fix" is rejected.

Verdict, `council-verdict.md:30-32` (wording rule):

> Future manifest changes are worded as SUPERSESSION, never re-pin (charter calls the manifest
> immutable).

Verdict, `council-verdict.md:102-104` (Phase 3):

> **Phase 3:** baseline-manifest SUPERSESSION (with the ruled fields) + focused re-audit of
> pack/custody-bearing seats (L1, L5, L7 minimum) + adversarial coverage re-enumeration of all
> universes; delta re-audits per C-028 on every fix round.

### (b) What changed since

- **The manifest has not been superseded.** `git log -- docs/process/audit-baseline-manifest.json`
  returns exactly one commit: `694442c` ("Audit-baseline manifest committed at the readiness-tooling
  head (charter amendment 2)"). At 4597ad4 the file still reads:
  - `head_commit` / `origin_main` = `ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b`
  - `pack_digests` = the three **_v1** packs (`d117_floor_qwen25_1p5b_v1`,
    `d117_floor_qwen25_7b_v1`, `d117_contrast_qwen25_1p5b_vs_7b_v1`)
  - **no** `pack_digest_algorithm` field, **no** chain-template coverage note, **no** paths for
    bindings — i.e. none of the three ruled supersession conditions are present.
- Meanwhile the pack family advanced **two generations**: `_v2` (D-138 head, freeze-0002 — commits
  `1e63568`, `f153271`, `75f22a0`) and `_v3` (freeze-0003 — commits `5e38f1e`, `eb7f6c6`,
  `94dc3b3`; U11 identity-pin projections `3d05982`, `6fd8bce`, `74632e3`; S5 confirmation table
  `8b2b021`).
- **No focused re-audit of L1, L5, or L7 located.** Searched process_traces, run reports,
  TASK_QUEUE. **EVIDENCE NOT LOCATED.**
- Related sweep finding B4 ("`audit-baseline-manifest.json` pack digests reproduce under no
  algorithm and match no revision", `consistency-sweep-findings.md:51`) was **REFUTED** — the
  verdict records the digests recompute byte-identical at 8937dec via
  `joulewise.arm_readiness.committed_pack_tree_sha256` (`council-verdict.md:26-32`; both cold
  seats verified). The refutation concerns *correctness at the baseline*, not the missing
  supersession fields.

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN.** What remains: the Phase-3 supersession has not been performed, so at this sitting
the governing baseline document pins a dead head and a two-generations-stale pack family, and
charter amendment 12's final-head invalidation is live against **every** 2026-08-15 lens result
(214 commits since). A seat must decide whether a READY-candidate sitting can be held at all
against a manifest in this state, or whether supersession is a precondition to the sitting.

### (d) What a skeptical seat should probe

1. Recompute all three current `_v3` pack digests and compare to the manifest — expect a mismatch
   by construction; the question is whether any live gate or script still reads the stale values.
2. `grep -rn "audit-baseline-manifest" --include=*.py --include=*.sh --include=*.md .` — find every
   consumer of the stale manifest and ask what each does with a two-generation-old digest.
3. Ask which lens results survive amendment 12 at 4597ad4. The verdict's Disposition 1 established
   survival *at 8937dec*; nothing establishes it at the current head.
4. Verify the wording rule is honored if a supersession is proposed at this sitting (SUPERSESSION,
   never re-pin) and that all three ruled fields are present.

---

## P-3 — M-2 remand (Disposition 2)

### (a) Original finding, verbatim

> **M-2 retroactive review — REMANDED, not adjudicated** (Opus B3 adopted over the cold
> adjudicator's completed §C analysis; magistrate synthesis: the pairing split on adjudicability,
> and the conservative composition prevails). M-2 will be re-submitted as its own cold-gate
> artifact with primaries attached (decision-log entry, the overridden §5C gate text, the #149
> generator diff, L5's independent finding, sweep-S3). The cold adjudicator's §C analysis is
> custodied as ADVISORY INPUT to that gate, not as a verdict. Operationally M-2 remains in force
> on its own scoped terms until that gate rules; the successor arm packet must cite it until the
> re-freeze retires it.

— `council-verdict.md:33-40`

### (b) What changed since

- **The remanded gate ran.** Custody `docs/process_traces/2026-08-15-m2-coldgate/` — `packet.md`
  (mechanically assembled with primaries attached, `62d4479`, explicitly curing Opus B3),
  `coldgate-adjudicator-ruling.md` (`f758368`), `coldgate-opus-refuter-findings.md`, and
  `composed-verdict.md` (`6760a9b`).
- Composed verdict outcome (`composed-verdict.md:9-38`): engineering core **UPHELD**; the
  instrument **NARROWED** — the "overrode a NO-GO reading" premise **STRICKEN**, the
  every-arm-packet citation duty **STRICKEN** as phantom authority, the retirement clause
  **CORRECTED** with a real mechanism, scope pinned to three receipt hashes
  (`ddbbb409…1738 / a6dec2c2…7870 / 2ef73bf0…106f`), retiring per pack at successor freeze.
- Decision log amended in the same commit — `docs/decision_log.md:9406` "### M-2 GATE AMENDMENT —
  separate entry", body at `:9408-9418`.
- Downstream: D-140 (`docs/decision_log.md:173`) extends the receipts-govern core to **all**
  successor packs by its own authority, explicitly noting M-2 clause (d) bars citing the
  2026-08-13 override beyond its three receipt hashes.
- Item 2d of the composed verdict left a **RULING-REQUIRED** row (the contrast pack's
  PROPOSED-PENDING-LEAD-RATIFICATION / TODO(lead) / "EMPTY pending U11" markers, "likely
  Ed-adjacent") — locate its ruling or record it open.
- The M-2 gate also adopted a standing protocol relevant to *this* packet
  (`composed-verdict.md:37-41`): "any future cold-gate packet whose reviewed party is the
  magistrate is assembled by a NON-AUTHOR (Opus mechanic) with the extraction script committed
  beside the packet."

### (c) Candidate disposition a seat must adjudicate

**READY-evidence-attached for the remand itself** (the gate ran, composed verdict recorded,
decision log amended) — **with two residues STILL-OPEN**: (i) composed-verdict item 2d's
RULING-REQUIRED row on the contrast pack's pending-ratification markers; (ii) whether the
freeze-0003 re-freeze actually retired M-2 per its per-pack retirement mechanism, and whether any
successor arm packet still needs to cite it.

### (d) What a skeptical seat should probe

1. Check whether the three pinned receipt hashes still correspond to live packs after the _v2 and
   _v3 supersessions — M-2 retires *per pack at successor freeze*, so ask which of the three are
   now retired and by which receipt.
2. Find the ruling for composed-verdict item 2d, or record it as an open ruling row.
3. Verify the "make draft_status genuinely freeze-aware in all three generators (or remove/rename
   under the successor schema)" item actually landed — D-140 rules the semantics; confirm the code.
4. Apply the non-author-assembly protocol to this very sitting: ask who assembled this packet and
   whether an extraction script is committed beside it.

---

## P-4 — The sitting-type charter amendment is not in the charter

### (a) Original finding, verbatim

> **Charter amendment (Opus S12, adopted at the pairing — the correct venue for a proposed
> process rule):** sittings divide into ENUMERATING sittings (first-pass; output includes the
> ED-QUALIFICATION universe; charter:77-78 does not bind) and READY-CANDIDATE sittings (charter
> 77-78 binds: only T0 rows may remain open). This sitting is an ENUMERATING sitting.

— `council-verdict.md:54-57`

Origin, `opus-contract-refuter-findings.md:51` (S12): charter:77-78 was found both violated
(23 ED-QUALIFICATION rows open, none performed) **and unsatisfiable as written** on a first
sitting, because the fleet is what enumerates the ED-QUAL universe.

### (b) What changed since

- **The charter file was not amended.** `git log -- docs/process/instrument-readiness-audit-charter.md`
  returns one commit, `6a7849c` (v2 ratification, pre-council). At 4597ad4 the charter contains no
  occurrence of "READY-CANDIDATE" or "ENUMERATING"; `charter:77` still reads flatly "Only T0 rows
  may remain open at the sitting."
- The amendment lives only in: `council-verdict.md:54-57`, `docs/council_log.md:3693`, and — as
  *clearance text* — `docs/process/state_kernel.json:9`, `TASK_QUEUE.md:598`, `RUN_STATE.md:4054`.
- Consequence for this sitting: the rule that binds it (charter:77-78 binds a READY-CANDIDATE
  sitting: only T0 rows may remain open) is cited by the gate's clearance line but is **not present
  in the document the clearance line points at** — the kernel/queue clearance strings cite
  `instrument-readiness-audit-charter.md#verdict-form-amendments-11-12` for language the charter
  does not contain.

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN (process-hygiene, but binding on this sitting's own form).** What remains: fold the
S12 amendment (and the S11 manifest conditions) into a charter v3, or record explicitly that the
verdict document is the operative amendment carrier. A seat should decide which document governs
before ruling any row under charter:77-78.

### (d) What a skeptical seat should probe

1. Read charter:77-78 as literally written and ask whether this sitting satisfies it — every
   ED-QUALIFICATION row must be closed with evidence; only T0 rows may remain open.
2. Ask whether any ED row has been silently reclassified from ED-QUALIFICATION (stable, must close)
   to T0 (perishable, may stay open). Reclassification is the cheapest way to fake this gate.
3. Check the coldgate charter registry (`docs/process/coldgate_charter_registry.md`) for whether a
   charter digest is pinned for the Phase-4 cold pairing, and whether it is the v2 digest.

---

## P-5 — Same-signature structural finding: the three adopted consequences

### (a) Original finding, verbatim

> **Same-signature structural finding (Opus S13, cold §G.3 concurring):** twice in one cycle a
> stop-signal question was ruled unilaterally under packet-finalization pressure and referred
> after the fact (M-2; the baseline-drift disposition acted on before cold review). Rule 11's
> standing escalation trigger is MET and recorded as structural for C-058. Consequences adopted:
> (a) the drafting-mechanic checklist gains a mechanical rule-11 trigger enumeration over every
> decision-log ruling, blocking packet finalization until a cold-gate artifact or written dissent
> exists (cold §C.iv); (b) refuter fleets get output-keyed liveness checks with a bounded
> first-checkpoint deadline as standing protocol (cold §G.3); (c) stop-signal questions arising
> at packet time are ruled AFTER cold review, not before, unless delay itself destroys evidence —
> in which case written dissent to Ed accompanies the action.

— `council-verdict.md:58-67`

The council log flagged (a) as the highest-value prospective fix: "**Adopt consequence (a) into the
drafting-mechanic checklist now** — the mechanical rule-11 trigger enumeration over the decision
log, blocking packet finalization. It is the one consequence that would have caught this cycle's
failure prospectively." (`docs/council_log.md:3748`)

### (b) What changed since

- **(a) No drafting-mechanic checklist document located.** `grep -rln "drafting-mechanic"` over
  `docs/` and `.claude/` returns only `docs/council_log.md` and files inside the
  2026-08-15-readiness-council directory. `find docs .claude -iname "*checklist*"` returns nine
  files, all phase/operator/publication checklists — none is a drafting-mechanic checklist. **The
  mechanical rule-11 trigger enumeration over the decision log has no located home.**
- **(b) No output-keyed liveness-check protocol document located** in the skills or process docs
  (searched `docs/process/`, `docs/orchestration.md` was not found under that name in this tree's
  process set — flag for the seat).
- **(c)** No artifact located that records the stop-signal timing rule as standing protocol outside
  the verdict itself.
- Note the same-signature trigger's own terms: it is a **structural** finding, and rule 11 makes a
  repeat "evidence of a structural problem" where "the next spend is a CONSULT, not round three."

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN (all three consequences).** What remains: a located, citable home for each adopted
consequence. A seat should also ask whether the absence of (a) means *this* packet was finalized
without the mechanical rule-11 trigger enumeration the council ordered — which would be the same
signature a third time.

### (d) What a skeptical seat should probe

1. Enumerate every decision-log ruling entered since 2026-08-15 (D-137…D-149) and ask, for each,
   whether it contains an override, reversal, or reinterpretation of a stop signal or verdict — and
   whether a cold-gate artifact or written dissent exists for it. That is consequence (a) executed
   by hand; it is the probe the council said would have caught the failure.
2. D-148 (Ed's seven rulings) and D-149 (standing conditional T-0 GO) deserve that test explicitly:
   they change authority and the window-arming posture.
3. Ask whether any refuter/seat fleet run for this candidate sitting had a bounded first-checkpoint
   deadline (consequence (b)) — the 2026-08-15 cycle lost ~7 hours to an unmonitored relay.

---

## P-6 — Consistency sweep: 23 findings, formally UNVERIFIED

### (a) Original finding, verbatim

Packet index, `packet-index.md:19-21`:

> consistency-sweep-findings.md — the full 23-finding sweep (7 blockers / 10 should-fix /
> 6 nits) WITH the magistrate's appended digest-refutation note. Triage state: sweep-B4
> (digests) REFUTED (verified by both cold seats); all other findings UNVERIFIED, routed to
> the Phase-1 verify-and-fix work order.

Council log, `docs/council_log.md:3750`: "The sweep's own findings remain formally UNVERIFIED; the
work order is verify-and-fix." — including "**B7, the paper's floor-regime contradiction, which is
claim-bearing and P1**."

Sweep blockers (headings verbatim, `consistency-sweep-findings.md:18-85`): B1 alpha_arm_readiness
anchored at T4-late asserting NO-GO for closed gates; B2 three completed work orders written as
OPEN in TASK_QUEUE, one "LAUNCH-BLOCKING"; B3 WO-CI-RESTRUCTURE / D-130 closure recorded nowhere;
B4 manifest pack digests reproduce under no algorithm (**REFUTED**); B5 the generated state kernel
stale since 2026-08-08 declaring no gates active; B6 README activity blurb stale; B7 the paper's
mainline floor regime contradicts the frozen instrument, swap block has no live owner.

### (b) What changed since

- Partial, and traceable in commit `76f6861` ("Consistency sweep must-fixes: r5→r6 supersession
  recorded …, README volatile count removed per policy, CLAIMS_STATUS mechanical-barrier note,
  WINDOW_STATUS evidence-expiry hazard, packet head update, guide bind-at-birth precision").
- B5 (stale kernel / no gates active) is addressed by WO-KERNEL-RECONCILE — `TASK_QUEUE.md:104`,
  merged via **#150 (`47d2645`)**: WINDOW-COUNCIL-GATE live, P2-006 retired by supersession,
  kernel truth pass in one transaction. The gate is present at `docs/process/state_kernel.json:9`.
- B2/B3 (queue closures + D-130 disposition): completed-WO rows now exist at `TASK_QUEUE.md:102-110`
  with merge SHAs; `TASK_QUEUE.md:193` carries "WO-CI-RESTRUCTURE — CLOSED (D-130 condition;
  recorded 2026-08-15)".
- B7 (paper floor-regime contradiction, **P1 claim-bearing**): routed to the Phase-1 should-fix
  batch; the paper saw several passes (`2952226`, `3efea49`, `53e480e`, `76f6861`). Whether B7's
  specific contradiction (8.611855 J vs 1.869502 J mainline floor regime, per
  `docs/council_log.md:3687`) is resolved is a **row for L11/L4 assemblers to evidence**; not
  independently confirmed here.
- **No verify-and-fix completion artifact located** that walks all 22 remaining sweep findings and
  records each as verified-and-fixed or dismissed. **EVIDENCE NOT LOCATED.**

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN.** What remains: the sweep findings are formally UNVERIFIED as a body; individual
fixes landed without a per-finding verification ledger. The charter's own anti-ritual rule
(`charter:66-68`) says an unverified item is UNVERIFIED, not READY — and amendment 11 makes
UNVERIFIED independently disqualifying for a council READY.

### (d) What a skeptical seat should probe

1. Demand a per-finding disposition table for all 23 sweep findings. Absent it, each unresolved
   finding is a candidate UNVERIFIED row in its own right.
2. B7 specifically: read the paper's floor-regime passage at the current head and check it against
   the frozen instrument's floors. It is claim-bearing and P1.
3. Re-run a sweep at 4597ad4 — the previous sweep is 214 commits stale and the docs surface moved
   substantially (README blurb policy, RUN_STATE rewrites, CLAIMS_STATUS, WINDOW_STATUS).

---

## P-7 — Phase-2 sequencing: the re-freeze had to be LAST, once, atomically

### (a) Original finding, verbatim

> **Phase 2 — sequential:** re-freeze via the R1-ruled route ONCE, atomically, LAST among pack-byte
> changes (Opus W2; irreversible ⇒ magistrate+Ed), regenerating truthful freeze-aware status text
> (retires M-2); then the successor arm packet ONLY after the T-0 repair passes end-to-end at the
> exact reviewed head (Opus W8).

— `council-verdict.md:97-100`

Rationale, `docs/council_log.md:3749`: "**Sequence the re-freeze last** (W2). Any earlier pack-byte
change forces an extra baseline supersession and re-audit round."

### (b) What changed since

- Phase 0 rulings landed: **R1 → D-146** ("R1 ruling — production capture-pipeline v3 adoption",
  `docs/decision_log.md:8844`) and **R2 → D-147** ("R2 ruling — mint-lane fan-out composite",
  `:8850`), both from the co-design custody `docs/process_traces/2026-08-19-r1-r2-codesign/`
  (`13-r1-ruling.md`, `14-r2-ruling.md`, ratified in commit `7d4454e`).
- A re-freeze **did** occur — but the record shows **more than one pack-byte generation**:
  - `_v2` family generated (`6d66439`), frozen as **freeze-0002** (`8d854f1`, `e179b2c`,
    `28a0daa`) — then **reverted** (`98265d4`, `db8307a`, `55be7d5`), re-minted (`3ab56e5`,
    `1b5b16e`, `fb1320b`), **reverted again** (`eb603a9`, `bdc5562`, `db30f41`), and re-minted a
    third time on the D-138 budget head (`1e63568`, `f153271`, `75f22a0`).
  - `_v3` family emitted (`1d3873b`), freeze evidence authored (`3a75a77`), U11 projections frozen
    (`3d05982`, `6fd8bce`, `74632e3`), **freeze-0003** minted (`5e38f1e`, `eb7f6c6`, `94dc3b3`),
    confirmation table filled (`8b2b021`).
- Whether that sequence satisfies "ONCE, atomically, LAST among pack-byte changes" is exactly the
  question. It is also unresolved whether the T-0 repair **passed end-to-end at the exact reviewed
  head** before any successor arm packet (Opus W8) — no successor arm packet was located.
- Ed's authority posture changed underneath this: **D-148** (seven Ed rulings, `:8856`) and
  **D-149** (standing conditional T-0 GO / full no-hands window automation, `:8865`, commit
  `0e96dbb`) — the verdict's "irreversible ⇒ magistrate+Ed" clause should be read against them.

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN / partially satisfied.** What remains: a seat must rule (i) whether the multi-revert,
two-generation freeze history violates the ONCE-atomically-LAST ordering and therefore forces the
extra baseline supersession + re-audit round W2 predicted; (ii) whether any pack-byte change is
still pending after freeze-0003; (iii) whether D-149's standing GO alters the magistrate+Ed
requirement for the irreversible step, and by what authority.

### (d) What a skeptical seat should probe

1. `git log --oneline 8937dec..HEAD -- configs/campaigns/` — enumerate every pack-byte change and
   ask which came after the final freeze. Any post-freeze pack-byte change re-opens W2.
2. Ask for the end-to-end T-0 pass receipt at the exact reviewed head (Opus W8's precondition).
   Absence blocks the successor arm packet regardless of every other row.
3. Test the reverted freeze receipts: confirm no consumer can still authenticate a reverted
   freeze-0002 receipt.
4. Ask whether the re-freeze regenerated **truthful freeze-aware status text** (the clause that
   retires M-2) or whether M-2 is still operative.

---

## P-8 — The ED-QUALIFICATION universe as a gate (23 rows)

### (a) Original requirement, verbatim

Charter, `docs/process/instrument-readiness-audit-charter.md:70-77` (Ed rows, amendment 10):

> Hardware/privilege rows split into: ED-QUALIFICATION (stable capabilities — sudo powermetrics
> behavior, sampler child supervision live, the JW-MET-3 rail probe — performed BEFORE the sitting,
> in any tap block; stable evidence cannot be deferred) and T0 (genuinely perishable same-night
> observations — live census at arm, clock stabilization). Only T0 rows may remain open at the
> sitting.

Charter, `:79-83` (verdict form): "Council READY requires: no NOT-READY, no UNVERIFIED, all
ED-QUALIFICATION rows closed with evidence."

The fleet emitted **23 ED-QUALIFICATION rows**: L1×2, L2×2, L3×4, L4×1, L5×1, L6×2, L7×3, L8×4,
L9×3, L10×1, L11×0 (`triage.json`; count corroborated by `opus-contract-refuter-findings.md:51`).

### (b) What changed since

Per-row closure evidence is assembled in the individual seat rows (`ROW-L1.md` … `ROW-L11.md`
§3). The program-level facts:

- The operator session is defined at `docs/phase_2/ed-qualification-session.md` (six steps:
  privilege grant; production sampler live checklist; JW-MET-3 rail probe ABBA; keyboard-backlight
  conservative control; §5A tap walkthrough; "IF the council is READY: chain into ALPHA arm").
  Supporting scripts: `scripts/ed_session/{sampler-checklist.sh,rail-probe.sh,build_rehearsal_env.sh}`.
- Operator-facing artifacts built since: `docs/process/rehearsal-operator-card.md` + the
  dress-rehearsal builder (`ad14ac4`), `docs/process/ed-batch-packet.md`,
  `docs/process/ed-evening-checklist.md`, `docs/process/ed-morning-packet-2026-08-18.md`,
  `docs/process/d149-go-receipt-template.md` (`79a4cd0`).
- D-139 shakedown first light custody: `docs/process_traces/2026-08-18-shakedown-first-light/`.
- **The distinction that decides this row: a script or card existing is not a closure receipt.**
  Each seat row states, per ED row, whether live execution with a durable recorded artifact was
  located.

### (c) Candidate disposition a seat must adjudicate

**ED-ROW ROLL-UP — see `../OPEN-ITEMS.md` for the consolidated closed/open tally.** Under
charter:77-83 as amended, a single ED-QUALIFICATION row lacking closure evidence is sufficient to
deny council READY; only T0 rows may remain open.

### (d) What a skeptical seat should probe

1. For each of the 23 rows demand the *artifact*: date, machine, command, captured output, custody
   path. Reject session-narrative assertions as closure.
2. Watch for reclassification of a stable-capability row into T0 to make it "allowed open."
3. Rows whose text says "unexercisable without sudo" or "cannot run while an agent fleet runs"
   (e.g. ED-L7-1, ED-L7-3) are structurally hard to close during an agent-driven program — ask how
   and when they were closed, and whether the [QUIET-MAC] gate was respected.
4. Cross-check against the CLAUDE.md standing rule: no `[QUIET-MAC]` measurement while an agent
   session is active. If an ED row claims live measurement during a fleet run, something is wrong.

---

## P-9 — This sitting's own form (assembly, cold pairing, non-author rule)

### (a) Original requirements, verbatim

Charter, `:84-91`:

> EVERY council READY verdict requires the rule-11 cold pairing (fresh Fable adjudicator + Opus
> contract refuter) over a sealed, mechanically-assembled packet; sealed-packet custody under
> docs/process_traces/<date>-readiness-council/ with mandatory contents enumerated in the packet
> index; final-head invalidation — any repo change after the baseline manifest voids affected lens
> results.

Verdict, `:106`: "**Phase 4:** reconvened READY-CANDIDATE sitting, fresh cold pairing."

M-2 gate composed verdict, `composed-verdict.md:37-41`: "any future cold-gate packet whose reviewed
party is the magistrate is assembled by a NON-AUTHOR (Opus mechanic) with the extraction script
committed beside the packet."

### (b) What changed since / status for this sitting

- This packet is assembled read-only by a non-author assembler into session scratch, per the
  assembler discipline recorded at `RUN_STATE.md:52-57` ("packet assemblers run read-only and write
  to session scratch; the LEAD lands their outputs into docs/process_traces/... serially").
- The mechanical extraction script for the seat-row raw material is
  `raw/*-triage.md` derived from `triage.json`; the extraction logic must be **committed beside the
  packet** when the lead lands it (M-2 protocol) — not yet committed at 4597ad4.
- Sealed-packet custody under `docs/process_traces/<date>-readiness-council/` for the new sitting
  does **not** yet exist; this scratch tree is a candidate, not custody.
- A fresh cold pairing (cold Fable adjudicator + Opus contract refuter) has **not** been convened
  for the READY-candidate sitting; the coldgate convening procedure is at
  `docs/process/coldgate_charter_registry.md` (clean launch environment, contamination disclosure,
  trust anchors at launch, the unbuilt `scripts/validate_gate_packet.py`).

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN (form preconditions).** What remains before any READY can be recorded: sealed packet
custody committed; extraction script committed beside it; fresh cold pairing convened per the
registry's procedure; charter digest supplied to the cold judge from an immutable revision.

### (d) What a skeptical seat should probe

1. Verify the packet you are reading is the sealed one, and that its index enumerates mandatory
   contents (charter:88) — the last sitting had no index at seal (Opus N3).
2. Check the sealed packet's own internal consistency: last time the sealed packet's §2 seat table
   was **stale against its own §9** and showed the wrong aggregate (`docs/council_log.md:3759`).
3. Confirm the cold judge's environment is doctrine-free per the convening procedure, and that the
   contamination disclosure opens the ruling.
4. Note `scripts/validate_gate_packet.py` is still unbuilt — the trust anchor is manual.

---

## P-10 — Phase-1 completion state per the state kernel (the declared SOLE work-selection authority)

### (a) Original requirement, verbatim

`council-verdict.md:80-87` lists the Phase-1 parallel code work orders that must close before the
program reaches Phase 2/3/4:

> **Phase 1 — parallel code WOs:** WO-KERNEL-RECONCILE (first; magistrate-supervised — meta-process
> edit, lieutenant-forbidden alone) · WO-T0-PRODUCER (integrated: nine-input capture tool, ≥10-min
> dwell, D-127 clock route landing, env/chain/manifest + doubled-plan-path fix w/ real-pack
> regression, terminal-review-trailer producer [second lens first]) · WO-LAUNCH-BINDING ·
> WO-CONSUMPTION-EDGE · WO-MARGIN-RECORDER-AUTHZ · WO-CENSUS-SEMANTICS (gated on ED-Q-L9-3) ·
> WO-DETECT-PULSES-BUDGET (second lens first) · WO-L2-REAUDIT · should-fix batch …

### (b) What the kernel says at 4597ad4

`docs/process/state_kernel.json` (`updated: 2026-08-19`, `active_stop_card: null`) — task statuses
verbatim from `/tasks/<id>/status` and `/tasks/<id>/status_note`:

| WO | `status` | `status_note` (verbatim) |
|---|---|---|
| WO-CENSUS-SEMANTICS | **blocked** | "Council Phase 1 parallel code work, deliberately held until Ed supplies ED-Q-L9-3 early in the batched qualification session." |
| WO-CONSUMPTION-EDGE | **partial** | "Code MERGED #155 (d54db78). D-139 rules delivered: Holm m=2 family (decode+prefill, alpha=0.05, two-sided) adopted; p256 floor = dedicated artifact (cells already frozen, #138). Remaining before close: the production freeze (rides Phase 2) + the same-head production-pack L10 replay" |
| WO-DETECT-PULSES-BUDGET | **partial** | "COMPLETE Phase-2 payload on impl/wo-detect-pulses-budget @ e22e658 (main-synced): detection budget + calexits flake fix + calibration-side launch-lineage stage 2 — each delta-ACCEPTED (final: 9/9 settle, 81/81 focused). MERGE-STAGED for the atomic re-freeze (D-138); plan custodied docs/process_traces/2026-08-16-phase2-plan-consult/" |
| WO-LAUNCH-BINDING | **queued** | "Stages 1-3 MERGED (#156 f392ff6, #157 bd333de); calibration-side stage 2 DONE on the staged estimator branch @ e22e658 (delta-ACCEPTED, rides the re-freeze per the Phase-2 plan); remaining: stage 4 successor flag inside the transaction. **Launch stays NO-GO**" |

Closed per `TASK_QUEUE.md:103-107`: WO-L2-REAUDIT (`0f886d3`), WO-KERNEL-RECONCILE (#150
`47d2645`), WO-MARGIN-RECORDER-AUTHZ (#151 `00ec3b7`), WO-T0-PRODUCER (#152 `a61ac92`).
WO-RECORDER-GRANT-IDENTITY was **RETIRED WITHOUT IMPLEMENTATION** by D-139 A1 (`TASK_QUEUE.md:102`),
leaving the check-to-grant race as a permanent registered limitation.

The `WINDOW-COUNCIL-GATE` remains the only active global gate, with `allowed_task_ids: []`.

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN.** Four Phase-1 work orders are not closed on the authority the project declares sole:
one **blocked** on an unsupplied ED row (ED-Q-L9-3), two **partial**, one **queued** with its own
note reading "Launch stays NO-GO". A seat should decide whether a READY-candidate sitting can rule
any dependent row READY while the kernel itself records the underlying repair incomplete — and
whether ruling otherwise would contradict the sole work-selection authority.

### (d) What a skeptical seat should probe

1. Re-read the four `status_note` fields at the head you are ruling on; if any narrative in this
   packet conflicts with the kernel, the kernel is the declared authority — ask which is wrong.
2. WO-DETECT-PULSES-BUDGET and WO-LAUNCH-BINDING stage 2 both sit **on branch
   `impl/wo-detect-pulses-budget @ e22e658`, merge-staged for the atomic re-freeze** — but the
   re-freeze (freeze-0003) already happened on 2026-08-19. Ask whether the staged payload landed
   before that freeze or is still unmerged after it; if the latter, the ONCE-atomically-LAST
   ordering (P-7) is broken and the staged work needs another pack-byte change.
3. WO-CENSUS-SEMANTICS's hard dependency `ED-Q-L9-3` is recorded `state: pending`. Verify against
   the L9 row's §3 — if the row claims closure and the kernel says pending, one is stale.
4. WO-CONSUMPTION-EDGE's remaining item is "the same-head production-pack L10 replay". Cross-check
   directly against `rows/ROW-L10.md` §2 — that replay is the L10 seat's own gating evidence.

### (e) Assembler check on the staged payload (executed, read-only)

`git merge-base --is-ancestor e22e658 HEAD` → **true**; `git branch -a --contains e22e658` lists
**main**, `integration/phase2-transaction`, and `impl/r2-s0-mint-resolver` among others. So the
"MERGE-STAGED" payload (detection budget + calexits flake fix + calibration-side launch-lineage
stage 2) **is** in the current history — the kernel's staging language is stale on that point,
while its residual items (WO-LAUNCH-BINDING **stage 4 successor flag inside the transaction**;
WO-CONSUMPTION-EDGE's **production freeze + same-head production-pack L10 replay**;
WO-CENSUS-SEMANTICS's **ED-Q-L9-3 precondition**) are what a seat must still resolve. A stale
authority record is itself a finding: the kernel is the declared sole work-selection authority, and
it currently describes a merge state that no longer matches the tree.

---

## P-11 — The queue's own window rows: stale pack identities and a stated re-audit precondition

### (a) What the queue says at 4597ad4 (verbatim fragments, `TASK_QUEUE.md` [QUIET-MAC] lane)

- Q2 `D117-W-ALPHA` — **task text**: "Run the frozen ALPHA pack **d117_floor_qwen25_1p5b_v1** …";
  **evidence text**: "Exact frozen pack **d117_floor_qwen25_1p5b_v3** is used only after council
  READY and separate T-0 GO". The same row names two different pack generations.
  Same pattern in Q3 (`d117_floor_qwen25_7b_v1` vs `_v3`) and Q4
  (`d117_contrast_qwen25_1p5b_vs_7b_v1` vs `_v3`).
- Q2 note, verbatim: "The pack is frozen but not selectable: WINDOW-COUNCIL-GATE admits no
  quiet-mac task, and **council Phase 2 requires the ruled successor re-freeze before the re-audit
  and READY-candidate sitting**."
- Q3/Q4 notes, verbatim: "The pack remains behind WINDOW-COUNCIL-GATE and the ruled Phase-2
  successor re-freeze, **Phase-3 re-audit**, and READY-candidate sitting."
- Q2/Q3/Q4 fences, verbatim: "No arm or collection before a READY-candidate council verdict and the
  separate perishable T-0 GO; **T-0 GO auto-issues per D-149 when its five recorded conditions
  pass** (no-hands windows); hands-required work remains Ed's".

### (b) Why a seat must rule on this

1. **The project's own queue states the Phase-3 re-audit as a precondition to this sitting.** P-1
   and P-2 record that neither the supersession nor the focused re-audit has been located. If the
   queue text is right, this sitting is being convened out of order.
2. **Pack-identity drift inside a single row** is the exact class of record defect the consistency
   sweep found last cycle (B1, B2, B6). A row naming `_v1` in its task and `_v3` in its acceptance
   cannot both be right, and the arm path binds on exact pack identity.
3. **D-149 changes the meaning of the T-0 GO the charter kept separate.** Charter amendment 12 says
   "T-0 GO is a SEPARATE, later closure … the council's READY never implies it." With D-149 the GO
   auto-issues on five recorded conditions once council READY exists — so a READY here is
   materially closer to authorizing a window than it was when the charter was written. A seat
   should decide, explicitly, whether the separation the charter guarantees still holds in practice.

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN (record integrity + sequencing).**

### (d) What a skeptical seat should probe

1. Ask which pack identity the arm path actually resolves at 4597ad4, and whether any tooling still
   accepts the `_v1` ids named in the queue rows.
2. Read D-149's five conditions and ask what stands between a council READY and an automatically
   issued T-0 GO on an unattended night.
3. Ask for the artifact that discharges the "Phase-3 re-audit before the READY-candidate sitting"
   precondition the queue itself asserts.

### (e) D-149's five auto-GO conditions, verbatim (`docs/decision_log.md:172`)

> For any quiet-Mac measurement window requiring NO physical presence, T-0 GO is AUTO-ISSUED when
> ALL of the following hold, evaluated mechanically at T-0 and written into the window's custody
> record as a GO receipt: (1) a READY-candidate council verdict stands (charter form: no NOT-READY,
> no UNVERIFIED, ED-QUALIFICATION rows closed) — this clears WINDOW-COUNCIL-GATE per its recorded
> clearance rule; (2) the frozen pack's arm ceremony passes every gate with freshness horizons
> honored; (3) the machine is quiet: census clean, fleet quiesced, no interactive use, single
> writer; (4) boot-session and clock-discipline checks pass at T-0; (5) the D-078 no-retry
> discipline binds — a refused capture ends that lane with diagnosis, never re-arm-and-hope.
> REMAINS ED'S: anything needing hands (cables, backlight, reboots, new sudo), claim publication,
> exact-byte confirmation. … Supersedes the per-window "separate perishable T-0 GO from Ed" fence
> for no-hands windows; kernel fences updated this commit.

**Read condition (1) carefully before ruling any row.** Under D-149 this sitting's verdict is
condition one of an automatic, unattended window launch: the remaining four conditions are
machine-evaluated. The charter's guarantee that "the council's READY never implies T-0 GO" is
preserved in letter — a separate mechanical evaluation still occurs — but the human separation the
2026-08-15 seats assumed (Ed issuing a perishable GO) is **explicitly superseded for no-hands
windows**. Whatever margin the seats were counting on from a human at the arm is no longer there.

---

## P-12 — Findings retired by RULING or RISK ACCEPTANCE rather than by repair

A seat must decide, as a matter of form, whether an accepted limitation discharges a NOT-READY
finding or merely relabels it. These are the items in that class at 4597ad4.

### (a) The rulings, verbatim

**D-139 A1** (`docs/decision_log.md:164`):

> A1 in-process adversary OUT of the threat model (registered limitation, family-wide)

**D-148 ruling 6** (`docs/decision_log.md:171`):

> the risk-appetite family (recorder race / T-0 capture provenance / hostile same-UID injection /
> forged launch-context) is ACCEPTED AS REGISTERED LIMITATIONS — in-process adversary out of model,
> per D-139 A1

**D-148 ruling 7** (same row):

> the stored anchor-v2 population (748 repo-tree bundles) gets a REGISTERED LIMITATION paragraph:
> permanently non-claim-bearing on estimator grounds, mechanically enforced by the D-146 barrier

**Registration surface** — `CLAIMS_STATUS.md:9-19`, verbatim:

> **Registered limitations (Ed rulings D-148.6/.7, 2026-08-19):** (a) the stored anchor-v2
> population — 748 bundles in the repository tree — is PERMANENTLY non-claim-bearing on estimator
> grounds (the v2 rate=1 model was falsified); replay/audit value retained forever; enforcement is
> the mechanical D-146 claim barrier. (b) The in-process-adversary family (recorder check-to-grant
> race, T-0 capture provenance, hostile same-UID injection, forged launch-context) is accepted as a
> registered limitation: the threat model assumes no adversarial process on the measurement
> machine (D-139 A1). Both belong in the paper's limitations section — the anchor-v2 paragraph is
> already drafted there.

**Work order retired without implementation** — `TASK_QUEUE.md:102`, verbatim:

> WO-RECORDER-GRANT-IDENTITY … RETIRED WITHOUT IMPLEMENTATION by D-139 A1 (Ed: in-process adversary
> out of model) — the registered check-to-grant limitation stands as the permanent disposition;
> design consult custodied `docs/process_traces/2026-08-16-grant-identity-consult/` should appetite
> change.

**Struck / re-severitied at the 2026-08-15 sitting itself** (`council-verdict.md:41-47`):

> 3. **L1-B3 severity — should_fix**, remedy subsumed into the blocker-gated kernel-reconciliation
>    transaction (cold §D; discharges Opus S10). P2-006 is retired only by formal ruling, never
>    silent deletion.
> 4. **Struck findings:** L8-B4 (both lenses: wrong-path artifact; correct fail-closed refusal),
>    WO-L2-4 (phantom), F4's timing premise (privilege gap survives inside WO-T0-PRODUCER).

### (b) What this changes about the row set

Four seat findings and one full work order leave the program without code. The struck findings
(L8-B4, WO-L2-4, F4's timing premise) were struck **on executed refuter evidence** at the sitting —
a different and stronger basis than risk acceptance. The D-139/D-148 family is retired on **Ed's
threat-model authority**, which is legitimate authority for risk appetite but is not a finding that
the instrument fails closed.

### (c) Candidate disposition a seat must adjudicate

**FORM QUESTION, seat must rule.** Two defensible positions, and the sitting should state which it
takes rather than let it pass silently:

- *Acceptance discharges*: the charter question is whether required outputs trace or fail closed
  **under the declared threat model**; Ed narrowed the model; the findings fall outside it.
- *Acceptance relabels*: the finding still describes real machine behavior; it is now an
  acknowledged hole that must appear in the paper's limitations and must not be counted as a
  repair. Under this reading the row is neither READY nor NOT-READY but a recorded limitation
  attached to the verdict.

### (d) What a skeptical seat should probe

1. For each accepted limitation, verify it is actually **registered where it must be read**: the
   paper's limitations section, `CLAIMS_STATUS.md`, and the pack/window custody a reviewer sees.
   `CLAIMS_STATUS.md:9-19` registers both families; the paper text should be checked directly.
   Note `CLAIMS_STATUS.md` also reads "Last updated: **2026-08-16** (T9 close)" while carrying a
   2026-08-19 banner — check whether the file is current.
2. Ask whether any accepted limitation is load-bearing for a **claim**, not merely for the
   instrument's integrity. A limitation in the threat model is acceptable; a limitation that
   silently widens a published interval is not.
3. Confirm the D-146 claim barrier **mechanically** enforces the anchor-v2 exclusion (D-148.7 says
   it does) rather than relying on the protocol note — run or read the barrier's refusal path.
4. Check that P2-006 was retired **by formal ruling, never silent deletion** (Disposition 3's
   explicit condition) — find the ruling.
5. Re-read the struck findings' refuter evidence rather than the strike itself. A strike recorded
   at a sitting whose baseline is now 214 commits stale should be re-tested if the underlying code
   moved — specifically L8-B4's canonical-path counter-probe and F4's timing premise, since
   WO-T0-PRODUCER rewrote that surface.

---

## P-13 — WHICH HEAD IS THIS SITTING ABOUT? (branch/main divergence + a moving tip)

This row was added by the assembler after two independent seat assemblers (L2, L4) flagged the same
problem from different directions. It is a **precondition question**: it conditions every other row.

### (a) The governing rule, verbatim

Charter, `docs/process/instrument-readiness-audit-charter.md:88-91`:

> final-head invalidation — any repo change after the baseline manifest voids affected lens
> results.

### (b) Measured facts (executed read-only in `wtS0`, 2026-08-19 evening)

```
git rev-parse main origin/main HEAD
  main        = 0099382088a37f4b227d89082c209173e3b421d6
  origin/main = 0099382088a37f4b227d89082c209173e3b421d6
  HEAD        = 7305e0d (impl/r2-s0-mint-resolver)

git rev-list --left-right --count origin/main...HEAD
  10   52          # main has 10 commits the branch lacks; branch has 52 main lacks
```

**Merge state of the repairs this packet credits** (`git merge-base --is-ancestor <c> main`):

| Commit | What it is | In `main`? |
|---|---|---|
| `47d2645` | WO-KERNEL-RECONCILE (#150) — WINDOW-COUNCIL-GATE install | **YES** |
| `a61ac92` | WO-T0-PRODUCER (#152) — the nine-input T-0 capture producer | **YES** |
| `b7e5730` | D-146 claim barrier + anchor-v3 production flip | **NO** |
| `5e38f1e` | freeze-0003 mint, `d117_floor_qwen25_1p5b_v3` | **NO** |
| `94dc3b3` | freeze-0003 mint, `d117_contrast_qwen25_1p5b_vs_7b_v3` | **NO** |
| `0e96dbb` | D-149 standing conditional T-0 GO + kernel fence updates | **NO** |

**The head also moved during assembly.** The task brief pinned `4597ad4`; a sibling assembler brief
pinned `d10881b`; the tip was `b92b43d` mid-assembly and `7305e0d` at this writing. Two seat
assemblers recorded the discrepancy independently (`rows/ROW-L2.md` §"HEAD DISCREPANCY",
`rows/ROW-L4.md` §6).

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN — and logically prior to every other row.** The sitting must rule, in writing, which
head its verdict attaches to, and must state the consequence:

- If the verdict attaches to **main (`0099382`)**: the Phase-2 transaction — the `_v3` family,
  freeze-0003, the D-146 claim barrier, the D-149 fences — **is not there**. Most of what this
  packet credits as "changed since" is absent from the head the verdict would govern.
- If it attaches to the **branch tip**: the verdict governs an unmerged branch that is *behind main
  by 10 commits*, has not been through the merge gate, and is still advancing commit by commit.
  A verdict against a moving tip is void the moment the next commit lands.

Neither reading is comfortable. Charter amendment 12 was written for exactly this: a repo change
after the pinned baseline voids affected lens results.

### (d) What a skeptical seat should probe

1. Demand a **frozen, named head** for the sitting, recorded in the sealed packet, with the fleet
   quiesced so it cannot advance during adjudication.
2. Ask what is in main's 10 branch-absent commits — if any of them touch instrument scope, the
   branch's own evidence is stale in the other direction.
3. For every row credited READY on a branch-only commit, ask whether the merge gate (D-148.2 gate
   shape: council/lead review, CI green, fresh pass over post-review commits) has been discharged.
   An unmerged repair is a proposal.
4. Re-run any coverage or census count at the ruled head. Counts taken at `b92b43d`, `4597ad4`, and
   `d10881b` are three different measurements in this packet already.

---

## P-14 — D-149 deleted the physical-launch-authority clause from the kernel; the runbook never heard about it

Surfaced by the L3/L9 assembler, verified independently by the packet assembler.

### (a) Executed evidence (read-only)

```
git show 0e96dbb -- docs/process/state_kernel.json | grep -c "physical launch authority"
  3      # three deletions, one per window task

  -  "rule": "No arm or collection before a READY-candidate council verdict and the separate
             perishable T-0 GO; Ed remains the physical launch authority"      (× D117-W-ALPHA/BETA/GAMMA)

grep -rn "D-149|no-hands|unattended" docs/phase_2/*.md | wc -l
  0
```

So the D-149 commit **removed "Ed remains the physical launch authority" from all three window-task
fences in the state kernel**, while every Phase-2 operator document — `window_runbook.md` included —
contains **zero** references to D-149, "no-hands", or "unattended", and still describes Ed's §5A tap
and E-10 physical launch.

### (b) Why this is a council row and not a docs nit

The two documents now disagree about **who launches a measurement window**. The kernel is the
declared sole work-selection authority; the runbook is what an operator actually follows at 2am.
Every L8/L3/L9 operator finding was written against the runbook's model. And D-149's condition (1)
is *this sitting's verdict* — so a READY here activates an automation path whose governing
documents contradict each other, and which no seat in the fleet has audited.

### (c) Candidate disposition a seat must adjudicate

**STILL-OPEN.** What remains: reconcile the kernel fences and the Phase-2 runbook into one stated
launch model, and decide whether the unattended path requires its own lens before it can carry a
funded window.

### (d) What a skeptical seat should probe

1. Read `window_runbook.md` §5A and E-10 as an operator would, then read the kernel fences. Ask
   which one a tired operator or an automated driver actually obeys.
2. Ask which seat audited the no-hands path end to end. If the answer is none, the automation is
   unaudited surface introduced *after* the audit that this sitting is closing.
3. Ask what happens to the D-078 no-retry discipline (D-149 condition 5) when there is no human
   present to observe a refusal.
