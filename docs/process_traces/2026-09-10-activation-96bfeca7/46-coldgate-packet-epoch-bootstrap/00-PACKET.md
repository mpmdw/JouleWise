# Cold-gate packet 46 — adjudicate the new-epoch calibration bootstrap mechanism (rule 11: proposed contract/process mechanism)

Assembled 2026-09-10 ~08:30 PDT by the resident magistrate (activation 96bfeca7). Read in this order: `exhibit-45-magistrate-synthesis-epoch-bootstrap.md`
(the synthesis and the questions R-a…R-e), then the three blind design memos (`exhibit-41-…astra`, `exhibit-42-cold-fable…`, `exhibit-43b-opus…`),
then the consult `exhibit-38-…` and the lead record `exhibit-39-…`; the brief `exhibit-40-…` is the question the seats answered. Verify every
mechanism claim you rely on against the code on this worktree (refs shared; cited files are unchanged between 58d4696b and origin/main for the
regions cited — check with `git diff 58d4696b origin/main -- <path>` if in doubt).

## What you rule

R-a. The mechanism (D1 derivation-only writer mode under DIAGNOSTIC_NO_PACK with a new chain; D2 canonical ledger + generation-keyed issuance
     validation; D4 parameterized prospective-corpus issuer + D-138 atomic transaction; D5 template + daily desk epoch watch), with the three
     decisive catches: Opus R1 (advance the successor's cutoff past the bootstrap rows), Opus membership (corpus = every valid observation of the
     registration), Astra extension admission (`append_pending_receipt` head==pin — VERIFY in `joulewise/calibration_ledger.py` ~5459–5600 and in the
     bracket-session path whether two or more observations in one night already work, and rule the exact extension rule).
R-b. Divergences V1, V2, V4, V5, V6 (synthesis table) — rule each. V3 (corpus size/nights) and V7 (D-125 floor) are Ed's: rule only the DEFAULT
     text to propose to Ed and the veto mechanism (email + directive issue; the default binds if no NO arrives before the first capture's arm).
R-c. The pre-registration text (synthesis §Pre-registration) — approve, amend, or replace, verbatim-ready to commit.
R-d. Implementation decomposition: disjoint-footprint seats (writer mode + refusals + tests; ledger extension rule + tests; validator relaxation +
     generation rows + corpus verifier; issuer + tests; chain + plan-class wiring + desk epoch watch; contracts/docs), gate shape (C-028 gauntlet:
     execution + contract refuters, delta re-audit per fix round, cold science gate before issuance, replay), and what may start today.
R-e. Authority: which parts the cold gate adopts now (rule 11: it adjudicates packets, Ed may veto) vs which must wait for Ed (scientific rules;
     the D-102 dated addendum wording; the calibration_ledger.md contract section). State plainly.

Constraints: keep every physics/evidence refusal fail-closed (D-161); no diagnostic exemption for G2-a; nothing here licenses a G2-a window; the
existing r6 artifact and the 76-row prefix stay byte-identical; historical generations validate unchanged.

Ruling file: `10-coldgate-fable-ruling.md` here — R-a…R-e with reasoning, the exact minimal change map (file:function) you adopt, the
pre-registration text verbatim in a fenced block, the seat decomposition table, and an Executed probes section (commands + outputs; `python3 -c`
arithmetic and read-only git/grep/sed only; no edits; no git writes; never touch /Users/edr/night-custody or the rehearsal checkout).
