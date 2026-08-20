# SESSION BRIEF — READY-CANDIDATE INSTRUMENT-READINESS COUNCIL

For every seat sitting on the reconvened instrument-readiness council. Read this before any row.

---

## 1. What you are being asked

The 2026-08-15 sitting returned **NOT-READY, 0 READY / 11 NOT-READY**, with L2 additionally
carrying a distinct **UNVERIFIED** on coverage. That verdict armed the `WINDOW-COUNCIL-GATE`: no
quiet-mac task may start or resume, and no funded measurement window may be armed, until a
reconvened **READY-CANDIDATE** council verdict clears it.

You are sitting on that reconvened sitting. Your job is to rule, row by row, on whether the
2026-08-15 findings are discharged **with evidence** at the current head.

**This packet does not grade anything.** Every row was assembled mechanically: the original finding
verbatim, what changed with exact pointers, a *candidate* disposition, and probes. Candidate
dispositions are drafting aids. You rule.

---

## 2. The clearance rule, verbatim

`docs/process/instrument-readiness-audit-charter.md`, **§ Verdict form (amendments 11-12)**,
lines 79-91, reproduced in full:

> ## Verdict form (amendments 11-12)
>
> READY-WITH-CONDITIONS is DELETED. Per component: READY / NOT-READY(+work
> orders) / UNVERIFIED. Council READY requires: no NOT-READY, no
> UNVERIFIED, all ED-QUALIFICATION rows closed with evidence. T-0 GO is a
> SEPARATE, later closure bound to the arm-night's perishable rows — the
> council's READY never implies it. EVERY council READY verdict requires
> the rule-11 cold pairing (fresh Fable adjudicator + Opus contract
> refuter) over a sealed, mechanically-assembled packet; sealed-packet
> custody under docs/process_traces/<date>-readiness-council/ with
> mandatory contents enumerated in the packet index; final-head
> invalidation — any repo change after the baseline manifest voids
> affected lens results.

Three consequences you should hold in front of you:

1. **There is no conditional pass.** READY-WITH-CONDITIONS was deleted precisely because a fleet
   that returns one READY makes a conditional option a live fail-open hazard.
2. **UNVERIFIED is independently disqualifying.** Charter amendment 11 treats NOT-READY and
   UNVERIFIED as distinct verdicts: the NOT-READY carries work orders, the UNVERIFIED carries a
   mandatory re-audit. A row you cannot verify is UNVERIFIED — not a lenient READY.
3. **READY is not GO.** T-0 GO is a separate, later closure bound to the arm-night's perishable
   rows. Nothing you rule here authorizes arming a window on its own.

---

## 3. The sitting-type amendment that makes charter:77-78 bind here

Entered at the 2026-08-15 pairing (`council-verdict.md:54-57`), verbatim:

> **Charter amendment (Opus S12, adopted at the pairing — the correct venue for a proposed
> process rule):** sittings divide into ENUMERATING sittings (first-pass; output includes the
> ED-QUALIFICATION universe; charter:77-78 does not bind) and READY-CANDIDATE sittings (charter
> 77-78 binds: only T0 rows may remain open). This sitting is an ENUMERATING sitting.

The 2026-08-15 sitting was ENUMERATING. **This one is READY-CANDIDATE, so charter:77-78 binds you.**

Charter § Ed rows (amendment 10), lines 70-77, verbatim:

> Hardware/privilege rows split into: ED-QUALIFICATION (stable
> capabilities — sudo powermetrics behavior, sampler child supervision
> live, the JW-MET-3 rail probe — performed BEFORE the sitting, in any tap
> block; stable evidence cannot be deferred) and T0 (genuinely perishable
> same-night observations — live census at arm, clock stabilization).
> Only T0 rows may remain open at the sitting.

The fleet enumerated **23 ED-QUALIFICATION rows**. Each seat row's §3 states, per row, whether
live-execution closure evidence was located. Note: the amendment is recorded in the verdict and
council log but was **never folded into the charter file** — see `rows/ROW-P-PROGRAM.md` P-4.

---

## 4. The anti-ritual discipline you must apply to every row

Charter § Anti-ritual discipline (F8, binding on every lens), lines 59-68, verbatim:

> Every lens report must carry: its enumerated evidence universe; a
> coverage numerator/denominator; executed POSITIVE and NEGATIVE probes
> (minimum executed falsifiers — a READY-falsification attempt is
> mandatory); unexecuted obligations listed; concrete failure scenarios
> per finding. A zero-finding report without the full packet is
> UNVERIFIED, not READY. C-028 refuters verify findings; the sitting
> additionally adjudicates COVERAGE and the falsely-clean risk on primary
> evidence.

A **READY-falsification attempt is mandatory** — for each row you are minded to pass, you must
first try to break it and record the attempt.

---

## 5. The standing warning from the last sitting

`council-verdict.md:18-22`, verbatim:

> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every
> seat's evidence universe was self-nominated, and the one denominator adversarially tested fell.
> Closing all listed work orders does not entitle READY; the READY-candidate re-audit must
> re-enumerate every universe independently and run the adversarial coverage attack as a standing
> packet element.

The one seat that self-reported READY (L2) was the one seat adversarially attacked, and its READY
did not survive: a self-nominated coverage denominator of **16** against a real universe of **251**.
One for one against the method.

Both cold seats ruled every other denominator suspect for the same reason. The honest statement of
fleet coverage is that **it is unquantified pending re-enumeration** — do not quote the 219/253
aggregate (`docs/council_log.md:3760`).

**Coverage error was conservative under NOT-READY. Under a READY it is fail-open. The risk
transferred to this sitting.**

---

## 6. Baseline and final-head invalidation

- 2026-08-15 audit baseline: **8937dec** (= manifest head `ac3fe1d` + `audit-baseline-manifest.json`,
  `README.md`, `RUN_STATE.md`, pinned by the cold adjudicator's §B condition 1).
- This packet was assembled at **4597ad4** on `impl/r2-s0-mint-resolver`.
- **214 commits** separate them.
- The audit-baseline manifest at `docs/process/audit-baseline-manifest.json` has **not** been
  superseded: it still pins `ac3fe1d` and the **_v1** pack digests, while the live family is **_v3**
  under freeze-0003. Charter amendment 12's final-head invalidation is therefore live against every
  2026-08-15 lens result. See `rows/ROW-P-PROGRAM.md` P-2 before ruling any pack- or custody-bearing
  row.

---

## 7. What changed since the last sitting (orientation only — verify, don't trust)

- **Phase 0 rulings**: R1 → D-146 (production capture-pipeline v3), R2 → D-147 (mint-lane fan-out),
  R3 (P2-006 retirement, via WO-KERNEL-RECONCILE), R4 + the remanded **M-2 cold gate** (ran;
  composed verdict `6760a9b`).
- **Phase 1 code wave (T9)**: WO-KERNEL-RECONCILE (#150 `47d2645`), WO-T0-PRODUCER (#152 `a61ac92`),
  WO-MARGIN-RECORDER-AUTHZ (#151 `00ec3b7`), WO-L2-REAUDIT (`0f886d3`), and others; see
  `TASK_QUEUE.md:102-110`.
- **Phase 2 transaction (T10 + 2026-08-19)**: S0–S5, the `_v3` pack family, the **freeze-0003**
  family, r5→r6 acceptance supersession, the capture-era system, the claim barrier (D-146).
- **Operator qualification / shakedown first light (D-139)**:
  `docs/process_traces/2026-08-18-shakedown-first-light/`.
- **Authority changes**: **D-148** (Ed's seven rulings, 2026-08-19) and **D-149** (standing
  conditional T-0 GO — full no-hands window automation). D-149 materially changes the operator
  model that the L3/L8/L9 findings were written against; treat automation introduced after the
  audit as **unaudited surface**, not as a discharge.

---

## 8. How to read the packet

Reading order is in `00-INDEX.md`. Every row file has the same six sections:

0. Seat identity and 2026-08-15 result
1. **FINDINGS — original text verbatim, with citation** (the record; do not accept paraphrase)
2. **WHAT CHANGED SINCE** (commit SHAs, PRs, custody paths, decision IDs)
3. **ED-QUALIFICATION ROWS** (verbatim row text + located closure evidence, or an explicit
   "EVIDENCE NOT LOCATED — searched: …")
4. **CANDIDATE DISPOSITIONS** (assembled, not adjudicated)
5. **WHAT A SKEPTICAL SEAT SHOULD PROBE**
6. **OPEN ITEMS FROM THIS ROW**

`OPEN-ITEMS.md` consolidates everything no repair addressed and everything the assemblers could not
locate. It is deliberately not a comfortable document. An assembler writing "EVIDENCE NOT LOCATED"
is reporting a fact about the repository, not confessing a search failure — treat it as a finding.

---

## 9. What your seat must produce

Per the charter's own report requirements (§4 above), your seat report must carry:

1. Your **enumerated evidence universe** — independently enumerated, not inherited from the 2026-08-15
   seat report. That is the specific instruction of the not-certified-complete ruling.
2. A **coverage numerator/denominator** you can defend against an adversarial re-count.
3. **Executed positive and negative probes**, including a mandatory **READY-falsification attempt**
   for every row you would pass.
4. Your **unexecuted obligations**, listed.
5. A **concrete failure scenario** per finding you keep open.
6. A verdict per row: **READY / NOT-READY (+work orders) / UNVERIFIED** — and nothing else. There is
   no conditional pass.

---

## 10. Form preconditions before any READY can be recorded

Even a unanimously clean row-by-row result does not clear the gate until:

- the packet is **sealed** and custodied under `docs/process_traces/<date>-readiness-council/` with
  a **packet index** enumerating mandatory contents (charter:88 — the last sitting had no index at
  seal);
- the **mechanical extraction script is committed beside the packet** (M-2 gate protocol: any
  cold-gate packet whose reviewed party is the magistrate is assembled by a non-author);
- a **fresh rule-11 cold pairing** (cold Fable adjudicator + Opus contract refuter) is convened per
  `docs/process/coldgate_charter_registry.md` — clean doctrine-free launch environment,
  contamination disclosure opening the ruling, charter digest supplied from an immutable revision
  independently of the packet. Note `scripts/validate_gate_packet.py` is still unbuilt, so the trust
  anchor is manual;
- the **ED-QUALIFICATION** roll-up shows every stable-capability row closed **with evidence**.

Details and current status: `rows/ROW-P-PROGRAM.md` P-9.
