# Magistrate synthesis — ICLOUD-CUSTODY-LOCATOR-01 issuing boundary (interactive magistrate, 2026-09-08 ~10:35 PDT)

Inputs: cold Fable ruling (10) and Opus contract-lens refutation (11), both on packet sha f42565ba… at ae09cad7. They
converge: F1 is a blocker (no issuing path reaches a guard); disposition 3 (issuing default at
`load_calibration_ledger_snapshot` and `_custody_reasons`) is the mechanism that makes OMISSION fail-closed; the
empty-override refuse-only behaviour is acceptable. Where they differ, the synthesis adopts the stricter text:

1. Disposition 3 is adopted (both seats). The judge's eight replay opt-ins are adopted EXCEPT the three shared
   validators Opus proved reachable from mint/finalization paths — `joulewise/whole_window.py:512`,
   `joulewise/analysis_engine/inputs.py:1630` (and :3125 by the same reasoning), and the mint module's own loads at
   `scripts/mint_floor_artifact.py:969/:1745` — which take a caller-supplied `mode` defaulting to `issuing`; only
   genuinely-replay callers pass `read_replay` through them. (Opus finding 5 governs; the judge listed
   whole_window.py:512 as a plain opt-in, which would re-open the hole on four issuing constructors.)
2. Disposition 2 is adopted as defence in depth (Opus recommends; the judge allows): `_refuse_custody_override_mint()`
   at the four unguarded issuing entries. It is NOT the invariant and its list is not a census.
3. Pins (the judge's three, with the census in Opus's inventory shape): signature-default pin for the five
   functions; an AST inventory over joulewise/ and scripts/ in which every `load_calibration_ledger_snapshot` /
   `probe_custody` / `_custody_state` / `_custody_reasons` call site either omits `mode` or appears in a frozen
   `read_replay` allowlist (a new opt-in must edit the allowlist); the planted-replacement fixture on the bare
   snapshot load (issuing → `calibration_ledger_custody_invalid`, zero opens under the replacement root;
   `read_replay` → valid) plus one such fixture per issuing entry (Opus).
4. Empty override: unchanged; add a stderr diagnostic line naming the empty override when an issuing probe returns
   absent (Opus 6, judge 6); document in the contract addendum.
5. F2 (census scope) is resolved by the inventory pin; the contract addendum lists the allowlist as the census.

Disposition: part 5 seat at high effort on the lane worktree; then Astra delta re-audit + Opus contract re-refutation
(both, since the round changes twelve files); terminal review; PR + replay; merge.
