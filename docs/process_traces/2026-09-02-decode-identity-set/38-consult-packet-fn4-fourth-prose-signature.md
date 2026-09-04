# Consult packet: F-N4 and the fourth consecutive prose signature, 2026-09-02

Assembled by the magistrate at `fbedfb04` (branch
`fix/2026-09-02-decode-identity-set`). This packet exists because the standing
escalation trigger fired: the same defect class has now appeared in four
consecutive rounds of the same contract section under three different
formulations, and the doctrine says the next spend is a consult, not another
round. The magistrate is the party proposing to continue and therefore does
NOT classify the defect below; the classification question is asked, not
answered. Seats read only this packet and primary evidence.

## 1. The finding (terra 267, file 37, should-fix F-N4)

`docs/contracts/identity_pin_projection.md:609–621` (the lineage paragraph the
magistrate dictated in file 33 §R3-C and Sol 266 landed verbatim) introduces,
before any definition, the terms **consumption receipt**, **launch manifest**
(bold-defined only later, at :671–673), **window root**, **lifecycle
receipts**, and the reason codes `launch_binding_mismatch` and
`launch_consumption_missing`. Sol 266's first-use table (file 34) omitted the
paragraph entirely; terra built its own table and found it.

Executed evidence (bench, this session):

```
$ grep -rln "launch_binding_mismatch\|launch_consumption_missing" docs/contracts
docs/contracts/identity_pin_projection.md
$ grep -rn "lifecycle receipt\|window root" docs/contracts/*.md
docs/contracts/identity_pin_projection.md:613:lifecycle receipts, so a bundle whose arming-time paths no longer exist is
docs/contracts/identity_pin_projection.md:612:resolves the consumption receipt, the launch manifest, the window root and the
```

So none of the four nouns is defined in ANY contract; the two reason codes
appear in no contract but this paragraph. The definitions live only in code:
`joulewise/arm_readiness.py` (`_replay_consumed_arm` ~:9333–9352 emits
`launch_binding_mismatch`; `_read_v2_consumption` ~:8960–8985 emits
`launch_consumption_missing`; launch manifest ~:10187–10198/:10222; window
root ~:10200–10205; lifecycle receipts ~:10233–10252) and
`joulewise/analysis_engine/inputs.py:2773–2782` (`_read_bundle` →
`authenticate_bundle_launch_lineage`). Verify these lines yourself; do not
trust the ranges.

## 2. The history (four rounds, three formulations)

| Round | Formulation | Defect | Found by |
| --- | --- | --- | --- |
| 1 | seat-written prose (Sol) | F-N: contract sentence not matching the code's order | luna 261 |
| 2 | seat-written with first-use guidance in the brief | R-M5/F2: first-use/ordering defect in the rewrite | luna 263 |
| 3 (consult) | magistrate-DICTATED paragraph in packet Q3 | S1: dictated text wrong twice ("before any configuration is read"; "refuses before step 1") | Sol 265 + blind Fable (files 30–31) |
| 3 (landing) | magistrate-dictated with proving lines; seat verifies clause-by-clause | F-N4: six terms introduced before definition; seat's first-use table skipped the paragraph | terra 267 |

The corrective adopted after round 2 (file 22: dictation with proving lines,
seat verification) fixed the FACTUAL class (every clause of the round-3 texts
was PROVEN by terra against the code) and did not touch the PEDAGOGY class:
first-use checking was done after landing, by the auditor, never before
landing, by the writer. Ed's global writing standard says the first-use test
is run "mechanically before delivering".

## 3. Questions for the seats

**Q1 (classification — the seats answer, the magistrate does not).** Is F-N4
(a) the same defect as F-N/F2/S1 in the sense of rule 11 (a second fix round
on the SAME defect → mandatory cold gate before it lands), or (b) the same
CLASS but a distinct defect in a distinct paragraph (standing escalation
trigger → this consult suffices, then one changed-formulation round), or
(c) something else? Give the reading of rule 11's trigger text that your
answer rests on. Do not choose the answer that is convenient for the branch.

**Q2 (cure for the paragraph itself).** Both candidates below are UNTESTED
prose (no seat has verified them); grade each against the first-use test
(built before use / glossed at first use / deleted) and the replication bar,
and say which you would land or write a third:

- **Cure A — delete the upstream vocabulary (first-use option (c)).** Rewrite
  so the paragraph names only what this contract can define: "Bundle loading
  authenticates the launch lineage before any evidence row exists: it replays
  the consumed arm and resolves EVERY path recorded at arming time — the pack
  root among them — strictly, so a bundle whose arming-time paths no longer
  exist is refused at input loading with a launch-lineage reason code and
  never reaches this gate (`joulewise/analysis_engine/inputs.py`
  `_read_bundle`; `joulewise/arm_readiness.py` `_replay_consumed_arm`)."
  Keep the "runs on the filesystem that armed them / separate design lane /
  direct-call label" sentences. Cost: the two reason codes leave the
  contract; the reader who wants them follows the code cite.
- **Cure B — gloss at first use.** Keep the enumeration but gloss each term
  inline in plain words ("the consumption receipt — the durable one-use
  record that this launch authorization was spent; the launch manifest — the
  JSON declaration of the reviewed command and its inputs, defined in §What
  happens after arm; the window root — the directory the window's evidence
  is written under; the lifecycle receipts — the per-stage records written
  as the window runs"), and gloss the two codes as "the reason codes bundle
  loading emits when the replayed lineage does not resolve / when the
  consumption receipt itself is gone". Cost: ~6 lines; every gloss is a new
  factual claim that must be PROVEN against `arm_readiness.py` lines, and
  this contract then defines terms it does not own.

**Q3 (the formulation for round 4 — what breaks the pattern).** Three
formulations have failed on this section. Propose the fourth. The
magistrate's candidate, offered as one option among yours: the writer (bench
or seat) builds the first-use table BEFORE landing, mechanically — for each
noun phrase and code literal in the new text, `grep -n` the contract for a
definition line and require it to precede the first-use line or an inline
gloss to exist — and pastes that table under Executed evidence in the landing
record; the verifying seat re-derives the table independently. Say whether
this would have caught F-N4 (test it: run it on the current paragraph) and
whether it would have caught S1 (it would not; S1 was factual — say what
would).

**Q4 (process rule — for Ed, not for installation by any seat).** Should the
pre-landing first-use table become a mandatory gate for contract-prose
edits (a process rule; rule 11 says proposed process rules go to the cold
gate/Ed, and the magistrate does not install them)? Give the cost per edit
and the two-session drop test (rule 5) you would attach.

## 4. What the seats must not do

Do not write under the checkout (read-only). Do not re-litigate S3's ruling
(d) (file 32) — the paragraph's CONTENT was proven by terra; only its
pedagogy is in question. Do not lower F-N4's severity. Do not end mid-flight.
