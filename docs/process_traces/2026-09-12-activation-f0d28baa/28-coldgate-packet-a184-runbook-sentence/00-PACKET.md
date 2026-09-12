# Cold-gate packet 28 — the A184 runbook sentence about `session-refusal` (rule 11: two consecutive rounds, same signature)

Assembled 2026-09-12 ~04:30 PDT by the resident magistrate (activation f0d28baa). Mechanically assembled: exhibits are verbatim copies of the two
refuter reports and `git` output; the magistrate wrote only this file.

## Trigger

Kernel lane A184 (RECOVER-SESSION-REFUSAL-WINDOW-EXHAUSTED-01, PR #325, branch `fix/2026-09-12-recover-window-exhausted`, HEAD ca7346e4) adds a
refusal code `calibration_window_exhausted` so the desk recovery tool's `session-refusal` subcommand names the reason a derivation session was
aborted by the night chain (`abort-session --reason window_exhausted`). The code change is clean on both refuter lenses (reports 13, 14). The lane's
kernel acceptance also says "the runbook's harvest section cites it", so the seat added ONE sentence to
`docs/phase_2/derivation_night_runbook.md` §"The other early end: `window_exhausted`" (~line 1665).

- Round 0 (seat, 7014dd0e): "The desk tool's `session-refusal` reports this reason as `calibration_window_exhausted`." Contract refuter 14 (Exhibit A)
  found B1: the harvest operator runs the desk tool FROM THE ARMED NIGHT'S FROZEN CLONE at H f90cb8c0, which predates this code and prints
  `calibration_session_not_open`; the sentence is true for main and false for the checkout the operator actually uses.
- Round 1 (magistrate, at the bench, ca7346e4; Exhibit C): replaced the sentence with a seven-line paragraph that names the clone's older behaviour
  and ends "Harvest always uses the night's frozen clone, never main." Delta re-audit 22 (Exhibit B) found B2: that last sentence contradicts §2.5
  (Exhibit E), which requires the equivalence tool to be run a SECOND time from another checkout at the same head; plus S1 (the "(main after
  2026-09-12)" parenthesis substitutes a date for merge state) and S2 ("refusal code" undefined before use). Its same-signature statement: YES — a
  statement true for one checkout and false for the one the operator must actually use, the same class as B1.

Two consecutive rounds, same signature. The magistrate does not run round three. It asks the cold gate to rule the text.

## Q1 — what the runbook section may say (rule the exact text)

Constraints that bind the answer:
- The armed night (t0 2026-09-13 02:56 PDT, frozen triple at H f90cb8c0) is NOT affected by anything merged to main; its clone prints
  `calibration_session_not_open` for a `window_exhausted` abort (Exhibit B confirms from `git show f90cb8c0:scripts/recover_calibration_ledger.py`).
- §2.4 (Exhibit D, lines ~1641–1643) defines desk recovery as the recovery tool run at the desk against the measurement clone. §2.5 (Exhibit E)
  requires the equivalence check to run twice, once from the clone and once from a second checkout at the same head.
- Kernel acceptance for A184: "…the runbook's harvest section cites it."
- Writing standard (binding on all runbook prose): every term of art is defined at first use or earlier in the document; no sentence makes a claim
  that is true for one checkout and false for the checkout the operator is told to use.

Options considered (rule one, or write a better one):
- (i) Exhibit B's three exact replacements applied to the round-1 paragraph (B2, S1, S2 wording).
- (ii) A minimal citation with NO harvest-procedure claim: e.g. "`session-refusal` (the recovery tool's subcommand that prints a stored abort as a
  refusal code — the machine-readable name for why a session ended) reports this reason as `calibration_window_exhausted` in checkouts that contain
  that code; the frozen clone at H f90cb8c0 predates it and prints `calibration_session_not_open` for the same session, so on that clone read the
  reason from the `slot_unused` line above."
- (iii) Remove the runbook change from PR #325 entirely and register a follow-up kernel row for the citation, leaving A184's acceptance partially met
  ("cites it" open) until the next runbook revision.

Deliver: the exact final text of the paragraph (or "none" for (iii)), each term's first-use location in the runbook (line numbers from
`git show ca7346e4:docs/phase_2/derivation_night_runbook.md`), and the one-sentence reason the ruled text cannot fail the B1/B2 signature.

## Q2 — the classification (for the record)

Was delta 22's same-signature call correct (B2 is the same defect class as B1), or is B2 a new class (a scope over-reach: a recovery-tool sentence
generalised to "harvest")? The answer changes nothing about Q1 but is recorded against the escalation rule.

## Constraints on the judge

Read-only. Probes: `git show ca7346e4:<path>`, `git show f90cb8c0:<path>`, `grep`, `sed -n`. Do not edit any tracked file. Never touch
`/Users/edr/code/JouleWise`, `/Users/edr/JouleWise-measurement-20260913-derivation`, or `/Users/edr/night-custody`. Ruling file:
`10-coldgate-fable-ruling.md` in this packet directory — sections: Contamination disclosure; Q1 (ruled text verbatim in a fenced block; first-use
table; the one-sentence reason); Q2; Executed probes (commands and the lines they returned). Plain words; define terms at first use.
