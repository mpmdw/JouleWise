# BFG-S S0 PR (full tier): gate-ledger evidence, merge candidate `747596a3`

The candidate is branch `feat/2026-09-26-bfgs-s0-helper-fence` @ `747596a3`. It contains main `5d5a0b75`, which contains A309 (#426).
- Seat rounds: 1, 2, 3, 3b and 4 (Sol 6.0 xhigh).
- Lead bench commits: `783a09be` (restored the frozen `CustodyFailure`; `CustodyUnreadable`; base-derived pins), `b7df341b` (a strict UTF-8 decode of the containers) and `747596a3` (the test row dictated by the Fable final pass).

Paths below are relative to `docs/process_traces/`.

| # | Gate item | Evidence |
|---|---|---|
| 1 | Independent audit | The non-author lenses on every round. Rounds 1–2: `2026-09-26-activation-6bec2aa6/60-bfgs-s0/31`, `32`, `33`. Rounds 3/3b: `2026-09-26-activation-f8d6cab1/10-s0-delta/10` (Sol) and `11` (Opus). Round 4: `.../51` (Astra) and `.../52` (Opus). |
| 2 | Paired distinct lenses | Execution plus contract at every round, cross-family. Rounds 1–2: Sol + Astra + Opus. Rounds 3/3b: Sol + Opus. Round 4: Astra + Opus (a different family from the Sol implementer). |
| 3 | Lead FIX contract; findings dispositioned | Round 3: the contract `6bec2aa6/60-bfgs-s0/41` and rulings `44`. Round 4: brief `f8d6cab1/10-s0-delta/40`, which quotes the cold-gate texts verbatim. Dispositions: record 00 items 9, 10, 11, 13, 18 and 19 (`2026-09-26-activation-f8d6cab1/00-activation-record.md`). |
| 4 | Delta re-audit of every fix round | Rounds 3/3b plus bench `783a09be`: `10`, `11`. Round 4: `51`, `52`. Bench `b7df341b`: the Fable final pass Q3 (`60-s0-gate/21`, E4/E5). `747596a3`: that pass's own dictated body, executed as E15 before it was committed. |
| 5 | Same-signature statement; a surviving class goes to a consult | The rounds 3/3b split (Sol "yes", Opus "no") went to cold gate addendum 3 (`10-s0-delta/20-coldgate/10`), its paired Opus refuter (`11`), and the erratum (`30-erratum/21`). That satisfies rule 11's mandatory trigger. Round 4: Opus "no" and Astra "yes" (R1). The magistrate synthesized R1 as an amendment-29 conformance gap, not the ruled idiom (record item 18). The Fable final pass confirms that no reader converts a read or decode failure into an empty value (§2). |
| 6 | Opus counter-review of the near-final head | `10-s0-delta/52`: Opus contract lens on `c9081c6e`, PASS, five NITs, "same signature: no". |
| 7 | Apex Fable diff gate | `60-s0-gate/21-fable-final-pass.md`: cold Fable 5.1 on `b7df341b`, FIX-FIRST (one test-only row), then **MERGE without a further lens round**. It rules the R2 reading, accepts the NIT deferrals, and raises no design stop. |
| 8 | Overbuild / merge-ability prune | Magistrate: production is +373 lines across `battery_float.py` (+358), `evidence_night.py` (+12) and `night_kinds.py` (+3). Every hunk maps to a ruled text in the Fable Q1 closure table, and nothing lies outside WRITE_SCOPE. The deferred NITs are not built. |
| 9 | Full suite on the integration tree | See the row-9 addendum below. |
| 10 | Final-head fresh-eyes review after every post-review commit | `b7df341b` was reviewed fresh by the Fable final pass (row-10 charge, Q3). `747596a3` is exactly the body that pass dictated and executed (E15). `tests.test_battery_float` is green at `747596a3`. |
| 11 | CI | See the addendum below. |
| 12 | Magistrate terminal review | See the addendum below. |

**Deferred to follow-up lanes (Fable-accepted):** Opus NITs 1–4 (whitespace-only journal lines; `RecursionError` mapped to `CustodyUnreadable`; `match`/`case` rebinding in S-1; "missing" versus "unreadable" wording). S1/S2 brief notes: D-1, pass the real envelope and bundle directories and never a symlink. Also the erratum's flagged text-6 asymmetry: one timed-out collector blanks a night.

**A309 Fable obligation 3.** No harvest battery-float verdict has been committed to any branch between the A309 merge (`5d5a0b75`) and this PR: `git log 5d5a0b75..747596a3` touches no verdict directory, and main has not moved since `5d5a0b75`.
