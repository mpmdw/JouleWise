# Cold final pass: PR #821, the registered `lm-qual-01` manifest

Research lead (Fable 5.2), Wed Nov 18 02:20 PST 2026 (from `date`). RL-181 §1.0 step 1.

**Verdict: PASS.** Every scientific clause is as I ruled. No change is required before merge. Five notes for the lead and the builder follow the table; none blocks.

**Read.** PR head `0b09bee24eb4981aa6da9cb18f991eb0e676b67c` against `origin/main` `490395f15`. The manifest (sha256 `57ee6b131cf680a1a4bf76866e3d764961510c0b4d26254c5adaaad716d8b795`, recomputed), the v2 schema, the validator, the nine tests, the ledger row, the kit commitments. Both Astra audits. RL-179 F-12, RL-180 §1, RL-181 §0, §1, §4, RL-183 §2.3, §2.4, §2.9 on the audit branch at `286062767`. The three kit documents (design files) and the interim manifest at `f09469894`. Nothing sealed, measured or restricted was opened. Blind.

Cites: `M:n` is the manifest, `V:n` is `joulewise/cadence_looks/qualification_manifest.py`, `T:n` is `tests/test_qualification_manifest.py`, all at the PR head. `RLD:n` is `RESEARCH-LEAD-DECISIONS.md` at `286062767`.

| Clause | Ruled | Registered | Result |
|---|---|---|---|
| The ±0.10 word | RLD:19316-19322 | M:365-405. GPU rail, 1.10, type A, included only, 4,096 against own first 3,724 (M:367-376). Separate SDs, ddof 1, once on the full roster, floor 1e-12 J (M:377-381). d = long/SD_long − short/SD_short; mean of day means, equal day weight, local t0-date as run; t(0.95, D − 1), sample SD of day means (M:382-389). 3 legs, 3 days (M:390-393). Inclusive, unrounded (M:394-399). L pairs do not gate (M:375) | As ruled |
| The tails | RLD:19338 | M:349-363. 3,583 to 3,723 with 140 gaps; 3,071 to 3,150 with 79; both sides, once; n = gaps, c = P + (first + last)/2; for the L-pair prints | As ruled |
| The scorer pin | RLD:19344 | M:347-348 | As ruled |
| Eleven fields, two energy words | RLD:19360 | M:434-496. The eleven of the spec's table, same sources. `qualified_qualification` and `stage2_error` (M:493-496). Destinations M:498-519 hold every listed number in `RESTRICTED/scores.json` | As ruled |
| No twin; the oracle | RLD:19367-19371 | `twin: false` (M:527); no `twin_agrees` among the fields, and the schema closes the field set. Oracle by another family, without sight of `qual_score.py`, the five named tests (M:545-554) | As ruled |
| Custody names | RLD:19377 | `scores.json`, `stdout`, `stderr` (M:522-526); coefficients read in the interim location (M:205-206) | As ruled |
| §4(a) hand-read | RLD:19512-19516 | M:106. G0 record, each consumer's release and wait, each decode count against 4,096, 3,724 or 3,151; close interval, template, operational records; s02 waits; the re-date rule; the prior q0 run | As ruled |
| Paper sentences | RLD:19332, RL-175 C.1 | M:556-557 | Byte-equal to the log (checked by string search) |
| Inclusion rules | "Stand unchanged", RLD:19545 | M:108-197 | Equal to the interim manifest's at `f09469894`, code hashes apart |
| Pair print | RLD:19351-19356 | M:406-431. The design rows match the three kits' leg order | As ruled |
| Kit hashes | RLD:19303 | M:39, 54, 69 | Equal to the sha256 of `cl-qual-0{1,2,3}.v1.1.json` on the audit branch, recomputed |
| `PENDING:CODE` | RLD:19303: "every code, schema and scorer hash" | 32 slots: 1 scorer (M:218), 25 code (M:223-319), 2 rule-code (M:139, 155), 4 schema (M:325-337). The string occurs nowhere else; no `OPEN-n` remains | As ruled. The four schema slots are in my text |
| `validate --final` | RLD:19303 | V:159-175 rebuilds the only allowed byte stream from the registration and the candidate's slot values, and compares bytes. V:90 refuses the sentinel outside a hash slot; V:145-149 refuses a registration with a filled or mis-spelled slot | Holds. See below |

**The validator, tested by me.** The nine tests pass. On a hash-only final I made every single-byte substitution, blanking and deletion outside the 32 filled slots: 62,046 candidates, none accepted, none crashed. An added pin, a dropped pin, an upper-case hash, CRLF, a BOM, the registration offered as final and a pre-filled registration are each refused. The allowed positions are fixed by the registration's own bytes (V:147-149), so a later schema edit cannot widen them.

## Notes. None is a required change

1. **"or an undefined interval" (M:401)** is not in my sentence at RLD:19322. It is what `test_qual_undefined_interval` already presumes, and it can only turn a `yes` or `no` into `not_evaluable`. Accepted as registered.
2. **"before Friday" (M:106)** is my own wording. It reads: before qual-01-s01 arms.
3. **The kit hashes carry the frozen pin `0d03cb783`.** A changed qualification pin (RL-183 §2.9) changes the kit bytes. Before qual-01-s01 arms, the issue step compares each issued kit's sha256 with M:39, 54 and 69. A difference found then is a re-registration (manifest, commitments file, ledger row) and is free. A difference in qual-02 or qual-03 after the first receipt comes to me.
4. **The path list is registered too.** 27 of the 30 pinned paths exist on the interim branch or in this PR. `qual_score.py` and the two `lm-qual-01` schemas are still to be written (M:250, 328, 332). The builder keeps to these 30 paths. A path added or renamed after the first receipt is not a scientific change, but `validate --final` will refuse it, so it comes to me with the diff.
5. **`validate --final` trusts its first argument (V:182).** The build's preflight must hand it the bytes at the registration commit and check them against `57ee6b13…b795`, and the ledger must keep that hash when the row moves to final. That is owed by the scorer build, not by this PR.

Freeze 2 is named as `lm-interim-01` (M:198-214). No qualification span arms before freeze 2 is effective (RL-180 amendment 3), so a successor id would be known before the first receipt and is a re-registration, not a deviation.

**VERDICT: PASS. Merge #821 at `0b09bee24`; it must be on main before the first qualification receipt.**

/Volumes/JW-EXT/scratch/fable-821-cold.md
