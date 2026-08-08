# RESULTS_PROSE re-examination — verdict of record (2026-08-08)

Ordered re-run of the VOID first examination (see
MAGISTRATE-DISPOSITIONS.md §"RESULTS_PROSE — examination VOID"). Fresh
Opus examiner, isolated worktree, read-only, against the COMPLETED
deliverable (the void exam read a truncated mid-write snapshot).
Contract: the void exam's derived P1–P13, adopted by the magistrate.

## 1. Completeness verdict: COMPLETE

DRAFT-RESULTS_PROSE.md (5,576 lines) terminates properly; all six
sections present: §7 Variants A/B/C + §6 compressed A/B/C. Two
structural notes: (a) the deliverable appears TWICE, byte-identical
(in-transcript copy + harvested final message) — a filler could edit
the wrong copy; (b) the actual placeholder count is 105 `[VALUE]`s
(A=38, B=27, C=17, §6A=11, §6B=7, §6C=5) plus 9 placeholders in a
second family (`[1.5B/7B]`×2, `[7B/1.5B]`×1, `[REFUSAL REASON]`×2,
`[supported/refused]`×4, `[supported/refused/failed expected
behavior]`×1) — not the "35" recorded in the disposition.

## 2. Verdict table (per variant, per P-item)

| Item | §7 A | §7 B | §7 C | §6 shell |
|---|---|---|---|---|
| P1 summed-threshold | PASS | FAIL | PASS | N/A |
| P2 unbound magnitude adjectives | PASS | FAIL | FAIL | PASS (nit) |
| P3 attribution-limited conditional | FAIL | FAIL | FAIL | N/A |
| P4 dominance is a landed fact | FAIL | FAIL | FAIL | N/A |
| P5 "not resolvable" ≠ "no difference" | N/A | PASS | PASS | PASS |
| P6 B must split B1/B2 | N/A | FAIL | N/A | N/A |
| P7 C no partial claimability | N/A | N/A | PASS | N/A |
| P8 prefill floors-only | PASS (nit) | PASS (nit) | PASS | N/A |
| P9 tokenizer companion — say WHY admissible | FAIL | FAIL | FAIL | N/A |
| P10 never-zero drift | PASS | PASS | PASS | PASS |
| P11 n = bundles | PASS | PASS | PASS | PASS |
| P12 §6 defaults to unfunded branch | N/A | N/A | N/A | FAIL |
| P13a plain language / no shorthand | PASS | PASS | FAIL | FAIL |
| P13b tense + lead-in rewrite | FAIL | FAIL | FAIL | FAIL |
| placeholder binding unambiguous | FAIL | FAIL | PASS | FAIL |

P1 headline: Variant A is CORRECT (states floor gate alone, direction
gate alone, then the sizing disclosure last with its own denial,
tracking draft-v1.md §4's authorized sentence). Variant C's P7 is
CORRECT ("The decode contrast was consequently not evaluated…" — all
four illegal repairs named and refused). The P1 leak is in B only.

## 3. Findings

### BLOCKERS

- **B1 (P3+P4)** — *attribution-limited* asserted FLATLY in all three
  variants; the paper licenses it only doubly-conditionally
  (draft-v1.md:116 — dominance the SOLE otherwise-refusing condition
  AND an exact corner-widened floor exists); the word "sole" appears
  zero times in the deliverable; dominance stated as fact, not
  placeholdered. Quotes: A "All four floors are labelled
  *attribution-limited*. In each cell, uncertainty from shifting the
  phase edges within the calibrated clock-anchor bound exceeded the
  smaller point-only repeatability diagnostic."; B "All four floors
  carry the *attribution-limited* label."; C "Both are labelled
  *attribution-limited*: …". Fix: explicit IF/ELSE branch per cell
  ([IF sole otherwise-refusing condition AND exact corner-widened
  floor exists] label; [ELSE publish unlabelled at point-only
  [VALUE] J]) and a placeholdered comparison, never "exceeded".
- **B2 (P12)** — §6 shell has NO unfunded branch and is written as
  past-tense results; Window C is Ed ruling #1 PENDING and every
  paper §6 row reads [PENDING WINDOW C]. Fix: add §6 Variant 0
  (default, unfunded — §6 remains declared future work; abstract/
  contributions adjusted), and mark A/B/C conditional on the night
  being funded and run.
- **B3 (P6)** — Variant B is ONE variant with two in-line
  conditionals; shared paragraph 4 quotes a signed direction ("The
  registered token-generation contrast estimated 7B minus 1.5B energy
  at [VALUE] J per request, with a fully composed interval of
  [VALUE]–[VALUE] J.") which the B1 (floor-gate refusal) branch may
  not quote. Fix: two complete standalone drop-ins — §7 Variant B1
  (floor-gate refusal; magnitude-only, no signed estimate, no
  interval endpoints in directional language) and §7 Variant B2
  (direction-gate refusal) — each with its own preamble.
- **B4 (P1 in B)** — "That sum explains why the observed effect was
  difficult to adjudicate; it is not an acceptance threshold and was
  never compared directly with the estimate." The first clause
  performs the forbidden comparison; "directly" is a weasel
  qualifier. Fix: replace with Variant A's compliant form (denial of
  both the summed threshold AND interval-vs-sum comparison).

### SHOULD-FIX

- **S1 (P9)** — no variant states WHY the intra-family per-token
  comparison is admissible (both arms record the SAME tokenizer
  identity). Add the one-clause affirmative licence per variant.
- **S2 (binding)** — a filler cannot bind unambiguously: three names
  for F_cell across variants ("operative floor" / "claim-level floor"
  / "component maxima"); "operative floor" overloaded in B1 (denotes
  the claim-level armwise-max gate); "clearance" used where a
  floor-gate refusal makes it a SHORTFALL; unlabeled positional runs
  of 4 (A) and 8 (B) values; arity collapse in §6B (7 slots for
  quantities incl. two fitted slopes + a two-ended range); §6C values
  carry no units; duplicate bindings unmarked; no fill key; `[1.5B/
  7B]`/`[7B/1.5B]` coupled-pair rule unstated. Fix: fill-key header +
  named tokens (or inline labels), expand §6B arity, rename
  clearance→shortfall in refusal branch, standardize "operative
  floor" (cells) vs "claim-level floor gate" (armwise max).
- **S3 (P13b)** — all six sections past tense vs the paper's
  uniformly future §6/§7; no lead-in rewrite shipped. Fix: attach a
  one-paragraph lead-in rewrite per variant (or an explicit fill-time
  conversion note).
- **S4** — correct the "35 placeholders" figure (used as a
  completeness signal) to 105 + 9; as a dated ADDENDUM to
  MAGISTRATE-DISPOSITIONS.md, not a rewrite.

### NITS

- N1 (P13a): internal shorthand in professor-facing prose — "D-117
  chain" (C), "BOS handling" (C), "exact-basis" (C), "micro-delta"
  (§6A/B/C; the paper says "micro-differences"), "identity-matched"
  (§6A/B). Cleared on inspection: ABBA, corner-widened,
  sub-floor/super-floor (all glossed paper vocabulary).
- N2 (P2/D-119): editorializing — "difficult to adjudicate" (B);
  "limited but useful", "correctly refused", "precisely" (C). Take
  the weaker phrasing.
- N3: A's disclosure drops the second half of the paper's denial
  ("and the decision interval is not compared with the sum") —
  restore both halves.
- N4 (P5): B's "not resolvable on this instrument under the
  registered workload" vs required "not resolvable at the stated
  floor under the recorded conditions" — align.
- N5 (P10): add the pre-authored positive drift sentence to the §6
  drift row ("the drift screen passed; the allowance remains positive
  by construction").
- N6 (P8): move the floors-only disclaimer to immediately follow the
  prefill numbers in A and B.

## 4. Overall verdict

NOT ready to receive alpha numbers as-is; ONE revision round required
(B1–B4 + S1–S2 together, S3/S4 riding), then a DELTA RE-AUDIT of the
revised Variant B split and the new §6 Variant 0 — fix rounds on
conditional prose are exactly where new unconditional assertions get
introduced.
