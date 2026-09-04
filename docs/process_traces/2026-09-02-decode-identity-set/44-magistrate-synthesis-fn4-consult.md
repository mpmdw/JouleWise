# Magistrate synthesis of the F-N4 consult (files 38, 40, 41, 42), 2026-09-02

Written by the magistrate (session `joulewise-60`) at branch head `fc52bda6`.
Three seats read packet file 38: luna 268 (gpt-5.6-luna xhigh, file 40),
an Opus 5 contract-lens seat (file 41), a blind fresh Fable seat (file 42).
This synthesis records what they agreed on, where they split, what the
magistrate adopts, and what goes to the cold gate. Nothing here lands text.

## 1. Facts the consult established (all three seats, bench-executed by two)

| # | Fact | Evidence |
|---|---|---|
| E1 | The landed paragraph (`docs/contracts/identity_pin_projection.md:609-621`) names the wrong refusal label for two of the five artifacts it binds: a missing launch manifest emits `launch_consumption_invalid` (`joulewise/arm_readiness.py` `_read_exact_launch_reference`, ~:8996-9013), and missing lifecycle receipts emit `launch_lifecycle_incomplete` (`_read_lifecycle_receipt`, ~:9794-9798). Only the consumption receipt (`launch_consumption_missing`) and the pack root / window plan root (`launch_binding_mismatch`) match the paragraph. | Opus §0 B5 and blind Fable X1, both EXECUTED with pasted output; terra 267 (file 37) had executed only the two agreeing hops and cited lines for the other two. Named **F-N5**. |
| E2 | The pack root is recorded at ARM time in the arm receipt (`_pack_record`, ~:5242-5264, key `pack_root`), not "when the arm was consumed" as `:609` says; the consumption receipt carries no pack root (`CONSUMPTION_RECEIPT_KEYS`, ~:694-697). | Opus §1 F-N6; blind Fable X2. Named **F-N6**. |
| E3 | Both candidate cures in the packet fail on fact: Cure A says "EVERY path recorded at arming time" (only the pack root is arm-time; the rest are launch-time), Cure B restates F-N5's wrong labels and mis-glosses the window root (it is the frozen window PLAN directory, `window_plan_root`, holding `window.env` and `window-chain.zsh`, not "the directory the window's evidence is written under"). | luna Q2 (window-root gloss contradicted at ~:8939, :9781-9786); Opus §3; blind Fable §2.1-2.2. |
| E4 | The magistrate's mechanical first-use table catches F-N4 (and six to eight more undefined terms in the same paragraph the packet missed) and does not catch S1, F-N5 or F-N6, which are behavioural claims. | luna Q3 (table pasted), Opus §4 B4 (executed), blind Fable Q3 (script in its Executed evidence). |
| E5 | The contract already has a defined-terms bullet block at `:580-594` (U8, U11, Launch lineage, exact-cell route, condition-family transport, transport group) sixteen lines above the paragraph. | Opus §3 Cure C, B2. |

E1 and E2 falsify the packet's own premise (§2: "the corrective … fixed the
FACTUAL class"). The magistrate-dictated round-3 text was factually wrong
twice in the consult packet (S1) and twice again at landing (F-N5, F-N6).

## 2. Where the seats split

| Question | luna (40) | Opus (41) | blind Fable (42) |
|---|---|---|---|
| Q1 classification | (b): distinct defect, same class; this consult suffices; one changed-formulation round; cold gate if it fails again | (a): second fix round on the first-use defect (round 3 was its fix round) AND on the dictated-text-wrong defect (E1/E2); moot anyway because Q4 is a proposed process rule | (c): distinct defect, but the escalation ladder is spent (round 3 WAS the consult) and the cure is a process rule; cold gate either way |
| Q2 cure | third cure: Cure A minus the last label, path claim narrowed | Cure C: five bullets into the `:580-594` block, paragraph rewritten with "the launch-lineage reason code belonging to the artifact that failed" (no per-hop code map), delete `replays`/`strictly`/`arming time`, demote `:671-672` bold marks | Cure C: five bullets into the same block, paragraph rewritten with the five resolves IN EXECUTION ORDER, each with its true per-hop code |
| Q3 formulation | two-pass gate: mechanical first-use table + clause-to-code ledger with executed ordering probe | change the axis of proof, not the author: diff-scoped first-use table for vocabulary clauses; EXECUTED probe with counterfactual for behavioural clauses (mechanical trigger: backticked identifier or before/after/first/then/only/never/always/every/all/each/strictly/exactly); verifier re-derives/re-executes | three parts: author ≠ magistrate (magistrate specifies the claim list, a seat writes); writer runs the first-use script and pastes the triaged table; every code/order clause carries an executed probe, verifier re-executes |
| Q4 process rule | propose to Ed, narrow scope (edits adding/moving/renaming defined terms or code literals), two-session drop test, no auto-delete | yes but ONLY paired with the executed-behavioural-clause rule (alone it produces green records for factually wrong text); adds a noise-rate condition to the drop test | to Ed via the cold gate |

## 3. What the magistrate adopts

**Routing: the cold gate is mandatory before any round-4 text lands.** Two of
three seats reach it on independent grounds and the third concedes the
cold-gate trigger fires "if it fails again"; the decisive ground is Opus
Ground 2, which luna could not see: F-N5/F-N6 make round 4 the second fix
round on the "dictated text is factually wrong" defect. luna's (b) is
recorded as dissent on classification only; it does not change routing,
because packet Q4 is an enumerated trigger ("any proposed process rule") on
its own. Ed ruled tonight (D-171) that the first-use table becomes a
mandatory gate paired per Opus; the ratified text still needs the cold
gate's reading before it is installed, so Q4 is carried in the packet as an
exhibit of Ed's exact words, not decided by any seat.

**Cure: Cure C, in the blind-Fable per-hop form, verified by execution.**
Both fresh seats independently arrived at the same shape (define the
vocabulary in the existing block; rewrite the paragraph from defined terms;
delete the unbuilt process words). They differ on whether the paragraph
should name each hop's reason code. The magistrate recommends the per-hop
form to the cold gate: the paragraph exists to state a limitation precisely,
the standard is replication from the text, and a per-hop code is what a
seam test pins — drift is caught by the test, not by prose maintenance. The
Opus family-level form is carried as the alternative. The cold gate decides
between them; it may also reject both.

**Formulation 4 (the shape of round 4), adopted from Opus and the blind seat
jointly:**

1. The magistrate does not author the prose. It writes a CLAIM LIST (each
   claim = one sentence-sized proposition + the proving callable + the
   probe that falsifies it); a seat writes the text from defined terms.
2. Vocabulary clauses: the writer runs the mechanical first-use script on
   the diff (blind Fable's script, file 42 Executed evidence) and pastes the
   triaged table in the landing record BEFORE any verifier sees it.
3. Behavioural clauses (mechanical trigger per Opus §4): the writer pastes
   an EXECUTED probe with its counterfactual for each; a `file:line` cite
   is not admissible proof of a reason code, an order, or a provenance.
4. A different-model verifying seat re-runs the script and re-executes
   every probe, and diffs against the writer's tables.
5. The delta re-audit executes refusals; it does not cite lines.

**Not adopted:** another authorship variant (a cold seat writing the prose,
two seats writing it); Cure A and Cure B; lowering F-N4's severity. With
F-N5/F-N6 the paragraph's severity is higher than the packet stated.

## 4. Packet defects the seats found (fixed in file 45)

- File 38 was authored by the magistrate in prose, not assembled
  mechanically (Opus A4); file 45 follows `scripts/validate_gate_packet.py`'s
  grammar: a Charter pin section, an Exhibit manifest with SHA-256 digests
  of every exhibit, atomic questions only, no diagnosis.
- Packet §1 contradicts itself about `launch manifest` (Opus A1): it is
  bold-defined at `:671`, i.e. defined LATER, not undefined.
- F-N4's extent is understated (Opus A2, blind Fable §2.0): eight to twelve
  undefined or later-defined terms, not six.
- `consumption receipt` vs `one-use consumption record` is a synonym
  collision with `:672` (Opus A3); Cure C reconciles it in the bullet.
- The packet attributed the missing first-use table to Sol 266; the brief
  (file 33) had asked for it under R3-B only (blind Fable Q3 item 1). The
  omission was brief-shaped, i.e. the magistrate's.

## 5. Dissent recorded

luna (b) on Q1. The magistrate notes that luna's answer was the one
convenient for the branch and was reached without the bench evidence E1/E2;
it is recorded, not adopted.

## 6. Next

File 45 (mechanical packet) → cold Fable seat + Opus refuter → magistrate
synthesis (file 48) → round 4 under formulation 4 → different-model
verification → §5 fresh pass on the final head → integration replay → PR.
