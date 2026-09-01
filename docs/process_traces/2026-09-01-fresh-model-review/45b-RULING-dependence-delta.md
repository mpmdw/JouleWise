# Ruling 45b — dependence-sensitivity sheet delta re-audit (Sol xhigh, report 45: REFUTE)

Magistrate ruling, 2026-09-01, on `feat/2026-09-01-dependence` @ `35716229`. Delta seat: Sol
(report `45-sol-delta-dep2.md`); fixer of round 2 was luna (report 37) under rulings R1–R8.
The arithmetic is now fully replicated by hand (s = 1.4, ρ̂ = 0.3, V = 1.734695,
n_eff = 5.764703, all three t statistics) — the round-2 goal. This is the THIRD round on the
sheet → cold-gate trigger; the cold seat's verdict is appended below.

## Dispositions

| Finding | Severity claimed | Ruling |
|---|---|---|
| A1 — R7's documented CLI is over-escaped (`tr -d '\\140'`) and exits 2; the golden test bypasses the CLI | blocker | **ACCEPTED as blocker.** The R7 command IS the replication promise; a reader who runs it fails. Cure exactly as the seat verified: `tr -d '\140'`, and the golden test executes the documented command line via `subprocess` and parses `direction_gate_outcomes_agree: false` from its stdout. |
| A2 — DS-SENS-02 / PG-SENS-02 anchor line 292 (the heading) but name the sentence at 294 | should-fix | **ACCEPTED.** Anchor at frozen line 294 (the Limitation 1 sentence they precede). |
| A3 — R4/R5/R6/R8 document cures have no regression assertions | should-fix | **ACCEPTED, bounded.** One assertion per ruled item that resolves every claimed `draft-v1.md` line against the named frozen sentence (so A2's class cannot recur) and checks the seven-column shape of the four rows; do not lock prose verbatim beyond the sentences the rulings name. |
| B1 — a worked-example TABLE value can change with all tests green | should-fix | **ACCEPTED.** Parse the three worked-example rows and compare each field to the rendered model output. |
| B2 — deleting the `overflow` / `finite_string` refusal rows survives the meta-test | should-fix | **ACCEPTED.** Two-way coverage: the mandated row-name set is asserted exactly, and each row binds to a source site. |
| C1 — p-values not derivable from the sheet (no Student-t tail formula) | should-fix | **ACCEPTED.** Print the two-sided tail `p = I_x(ν/2, 1/2)`, `x = ν/(ν + t²)`, with the regularized incomplete beta named in plain words and the three worked x values (`0.078307034361`, `0.057315253936`, `0.064651302005`) so the printed p-values replay. |
| C2 — Holm used before defined | nit | ACCEPTED: two-sentence summary at first use (line 11). |
| C3 — `KEY_FROZEN` / `VALUE_UNISSUED` and "insertion anchor" unglossed | nit | ACCEPTED: one sentence each. |

## Round-3 shape

Fixer: terra xhigh (round 1 Sol, round 2 luna, delta Sol — terra has not touched this stream).
WRITE_SCOPE `docs/paper/round7/dependence-sensitivity.md`, `scripts/dependence_sensitivity.py`,
`tests/test_dependence_sensitivity.py`. The fixer must run the documented R7 command from a
shell, verbatim, and paste its stdout. Delta: Opus 5 (contract + pedagogy, fourth family).

## Cold-gate verdict

Cold Fable seat (fresh session): **RESHAPE** — full text in `48d-COLD-GATE-2-verdict-40b-45b.md`.
Bench-reproduced: the documented R7 command exits 2, and `tr -d '\\140'` inside single quotes
also DELETES the digits 0/1/4 from the data (`[5.,7.6,5.5,.2,.7,…]`), so the fragility is the
shell-extraction pipeline itself. Report 37's V3 ran a re-typed working form, not the sheet's.
Magistrate disposition (2026-09-01, adopted):

- **A1 label**: "ruled-item-unmet, must-fix" (numbers are right; the replication promise fails).
  **Cure (ii) adopted**: drop the grep/cut/tr pipeline — the command prints the literal list; the
  golden test parses EVERY bracketed ten-number list in the sheet and asserts each equals
  `EXAMPLE_BLOCK_DELTAS_J`, and executes every fenced command AS EXTRACTED from the sheet via
  `subprocess` (never re-typed).
- **The rule "the sheet is the fixture"** replaces per-item enumeration (the signature DID repeat
  three times — 26 → 32 → 45 — each round certifying the enumerated surfaces while the next
  un-enumerated surface failed): every fenced command extracted and executed; every number in
  prose and table matched to a rendered field; every `draft-v1.md` anchor resolved against the
  named sentence; refusal-row set asserted two-way. Acceptance = mutation table with zero
  survivors across those four surfaces, run by the fixer and RE-RUN by the delta seat.
- C1: agreed, plus name the implementing routines (`joulewise/analysis_engine/distributions.py:166`
  two-sided tail; `:131` quantile behind 2.262/2.776) so sheet and script visibly share one
  routine. A2, A3 (as a rule), B1, B2, C2, C3: agreed.
- Missed items adopted: drop generator LINE numbers at sheet `:11` (cold gate 32 Q4.2 — cite field
  names); one clause on "critical value 2.262000" precision; cross-stream rule: fixer reports
  verify documented commands by `sed -n 'Np' sheet | bash`, stdout pasted.
- Seats: terra xhigh fixer (test design + C1 + the bench-sized items in one round), Opus delta.
