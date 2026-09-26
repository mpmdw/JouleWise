# BFG-S design consult — charge (blind, one round, license to disagree)

**Lane:** BATTERY-FLOAT-GATE-01, PR "BFG-S" (JouleWise). It extends Ed's binding battery-float gate (directive #421) from derivation windows (BFG-D, merged in `64e39bb9`) to every other measurement-window kind.

**Why you are asked:** the ruled BFG-S row does not determine the implementation at several points. The magistrate needs independent design answers from four model families before a cold gate rules on the final texts. You are one seat. You cannot see the others. You may disagree with the scout's recommendations and with each other; state your reasons.

## Read, in full (absolute paths; the repository at `64e39bb9` is your working tree)

- **Scout packet** (the insertion sites, pins and ambiguity table this consult answers): `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-8e43cfa7/20-bfgs/11-scout-report-relaunch-6bec2aa6.md`
- **Ruled text:** `.../20-bfgs/ex-01-bfg-final-texts-v1.1.md`. The authority is §5.3 BFG-S row, §5.4 schema, §5.5 consumers and issuer, §5.6 tests, and X2.
- **Harvest addendum:** `.../20-bfgs/ex-02-harvest-final-addendum.md`, §3.7 and §4.11 (custody clause, predicate change, gating event).
- **BFG-D final pass:** `.../20-bfgs/ex-03-bfgd-fable-final-pass.md`, §8 F-1.
- **Consumer-drift final texts:** `.../20-bfgs/ex-04-consumer-drift-final-texts.md` (the one seam plus the AST guard).
- **Code:** `joulewise/battery_float.py` and its consumers; `joulewise/controller.py`; `joulewise/bundle_read.py`; `joulewise/calibration_bracketing.py`; `joulewise/quiet_predicate_campaign.py`; `joulewise/scored_reduce.py`; `scripts/sample_quiet_predicate_evidence.py`; `configs/campaigns/quiet_predicate_evidence_01/`; `docs/phase_2/window_runbook.md` §284–323.

## Binding constraints (not up for redesign)

- **Directive #421.** At arm and immediately before t0/publication, the gate requires external power connected, not charging, |InstantAmperage| ≤ 200 mA and a fresh gauge reading. Failure postpones the arm. A window with a non-float slot is confounded and never claim-bearing. Anything germane to whether a number is true is mandatory.
- **ex-02 §4.11 is a later PR.** The `abs(update_age_s) ≤ 180` predicate, the custody clause in "Window verdict", and the registration code pin land only after the Revision 5 epoch issues or stops.
- **No rewriting of frozen artefacts.** Frozen pack bytes, freeze receipts and registered digests stay untouched. Any change to a registered protocol (e.g. QPE-01 `pilot_protocol_v3.json`) needs its own cold-gate registration.
- **Byte-identical files.** `joulewise/reduce.py`, `joulewise/bundle.py`, the four estimator code paths and the paper-pinned scripts stay byte-identical (scout §pins).

## Questions: answer each with a decision, a one-paragraph reason and the failure mode it prevents

- **Q1.** Observation `phase` values for non-derivation windows: reuse `slot_pre/post` with a null slot identity, or add explicit phases (e.g. `quiet_pre/post`, `bundle_pre/post`)? Give the exact enumeration.
- **Q2.** Non-derivation verdict and custody: which object authenticates a raw pre/post pair to its session or bundle when there is no terminal ledger session or committed harvest file? Name the helper, its inputs and its refusal reasons. Say how ex-02's digest-recorded custody distinction applies.
- **Q3.** Quiet-predicate collector bracket unit: every 30 s round, the 600 s envelope, or both? Specify the behaviour when the pre read fails, and when the collector exits before the post read.
- **Q4.** QPE-01's frozen exclusions have no battery reason. Choose among:
  - (a) register v4 through a cold gate;
  - (b) fail closed: a non-pass envelope makes the pilot's claim refuse, and the list is unchanged;
  - (c) diagnostic only.

  Which do you choose, and why is that not a silent change to a frozen protocol?
- **Q5.** Controller: define the outcome for failure after the pre read and before the post read, and for non-Mac or mock targets. Must every finalized bundle carry a post read, or only bundles whose measured window is claimed?
- **Q6.** `BundleReader.metadata()` must fail closed for new bundles, but historical bundles lack the key. Choose among:
  - reject every historical re-reduction;
  - exempt a fixed, authenticated historical set (how is it authenticated?);
  - version the contract by trusted provenance.

  Define the prospective boundary exactly. Never infer it from a freely writable flag.
- **Q7.** `scored_reduce.reduce` receives `bundle_sha256` only. What authenticated evidence object does it take, and which code produces it? Specify the refusals for missing, duplicate or mismatched entries.
- **Q8.** `calibration_bracketing`: gate at the loader before physics, or at the evaluator? What is the historical/genesis candidate boundary?
- **Q9.** Transaction packs: nine d117 packs are frozen with no-clobber receipts, and three `_v5` packs have no sources yet. Is "re-freeze" to mean successor generations? Which of the nine should get a successor and which should be retired? Propose the successor naming and the authoring order.
- **Q10.** Wall-meter windows: is float sufficient on its own, or does the separate wall-meter bar (WALL-METER-GAIN-01) remain?
- **Q11.** The PR split: is the scout's proposal (code first, then successor packs, then the later §4.11 amendment) right?
- **Q12.** Anything the scout missed that bears on whether a number is TRUE.

## Output

A markdown report with one section per question. End with a short table of Qn → decision → confidence (high/med/low). Do not edit any repository file. Scratch files go under `/tmp` only.
