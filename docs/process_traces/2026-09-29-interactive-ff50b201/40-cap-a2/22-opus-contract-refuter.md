REFUTER: DISSENT

Ruling: CAP-COUNCIL-25G83-01-A2, sha256 ccef94f0546cde88 (recomputed; matches). Code: origin/main 9eab16f8, exported read-only to scratch/capa2ref/main; mutated copy in scratch/capa2ref/capmod. The shape holds (R8 as default, interim dropped, H1 by absence). But three steps cannot be carried out as written, and each would send the matter back to council for reasons unrelated to the science.

BLOCKERS
B1. The named R8 tool refuses R7. Ruling §3.5 and §4.1 step 8 say to use `scripts/reissue_calibration_acceptance.py`. V2 says r7 was made by that tool.
 - Executed: the tool on unmodified main, `--corpus-root /Users/edr/code/JouleWise`. Result: CORPUS_AUTHENTICATION=FAIL 0/17, VERDICT=STOP. The same run with the cap raised to 400_000 gives the same result. The failure is in `b_fiducial=FAIL` for every member (for example, R7 stores 0.030067931757111657 while instrument_evidence.json stores 0.03018980442653224).
 - Cause: the tool requires R7's member B to equal the B stored in each capture's evidence file (reissue_calibration_acceptance.py:201-203). The n17 generations re-derived those values, and `tests/verify_calibration_acceptance_corpus.py:19-24` says in so many words that equality "would be a defect".
 - The r7 file was a bench edit ("pure pin delta from r6", commit 1b8a076be), not tool output.
 - Fix: step 8 prepares R8 the way r7 was actually made: a bench pin-delta from R7, checked by `_valid_acceptance_bound`. I did that in scratch and it validates True once a generation row is added.
B2. Step 13 hits an issuer refusal that no step fixes (the S5 mechanism). Ruling §3.5 and §4.3 S5 claim the (a) disposition registry lets the issuer recognise the 12 W1/W2 rows.
 - On main, `_registered_dispositions` (issue_calibration_acceptance_generation.py:1325-1356) accepts exactly one decision ID and one mechanism text, "...disposed as diagnostic, never a member...". The registry is also pinned by digest (:516).
 - At b953f4b0, `calibration_dispositions.py` hard-codes `DISPOSITION_DECISIONS` with that single decision and 11 content IDs (the 2026-09-19 captures). It checks the table equals the code at the production pin.
 - So the 12 valid W1/W2 rows at REVISION_FIVE_EPOCH (calibration_bracketing.py:279) remain foreign under `_foreign_rows` (:1430-1442), and the issuer refuses (:1905-1910).
 - Admitting them needs a new decision entry in code plus a new registry digest. The only mechanism text that exists labels them diagnostic, which S5 forbids.
 - A1 step 10 required "a reviewed change gives the issuer a way to recognise them". A2's step 11 lists only the issuer change for the third-window rule (item 7), so the S5 lane has dropped out of the sequence. It must be put back as a named lane that lands before step 11.
B3. N-1's precondition is false: raw bytes are missing for 3 of the 17 members.
 - Executed: listed every R7 member's `raw/`. Members 20260725T005132-a64711b7, 20260725T011533-0b5ec77c and 20260725T022712-0a9534f5 have empty `raw/` directories (mtime Jul 28). Their manifests still list `raw/powermetrics.plist`. The files are not in any /Users/edr/code/JouleWise* checkout.
 - V4 checked only that the directories exist.
 - The claim "as it was for r7" does not hold. R7's recorded evidence is an anchor-record replay ("35 bounded, 3 unknown") plus the verify script. That script recomputes statistics from R7's own values and hashes and replays no B (verify_calibration_acceptance_corpus.py:95-150).
 - As written, N-1 fails and §4.4 sends the matter to council.
 - Fix: step 7 or 8 first recovers the three plists by manifest sha256 from archive, or the ruling states what N-1 means for members without raw bytes.

SHOULD-FIX
S1. The option (a) lane can break step 13. At b953f4b0 the issuer hard-wires `ANCHOR_V3_R7_ACCEPTANCE_ID` for the Revision 5 predecessor, and the `--predecessor-acceptance` default becomes R7's path (diff hunks at :1773 and :2528). If action 1 keeps those hunks, a successor with R8 as predecessor is refused ("requires r7 predecessor"). The ruling's V7 reads main (ACTIVE_ACCEPTANCE_ID) and never tells the (a) re-scope to drop them. Say so in §3.7 action 1.
S2. N-1 says "equals its stored value". Name the target as R7's `derivation_corpus.members[].b_fiducial_s`, not instrument_evidence.json. Read literally, that is the tool's meaning, and all 17 fail (see B1).
S3. The `cap_change` note must state that under the new cap probe a7e8b412 "completes and trips the R8(a) tripwire". That is a prediction about code no one has executed, and no N-check verifies it. Either replay it and record the result, or drop the sentence; otherwise the fix for one false statement adds another.
S4. The name "R8" collides with A1 rule R8 (the tripwire; 31-addendum-ruling.md:170). Step 12 "the harness report (R8)" and §3.6 row 12 "R8(a)/(b)" can each be read either way. Rename the file's short name.
S5. N-5's wiring list omits `EXPECTED_BY_ACCEPTANCE_ID` in tests/verify_calibration_acceptance_corpus.py and the `_D102_GENERATION_DERIVATIONS` row. Executed: without the row, `_valid_acceptance_bound(R8)` returns False.

CONFIRMED (executed in scratch)
- The #421 test on pins: the derivation-only path enforces pins equal to the running code (validate_powermetrics_fiducial.py:547, which calls :397-402). With the cap raised and R7 as default, both the derivation-only and the ordinary preflight refuse `acceptance_artifact_stale`. So no derivation window can run on a default with stale pins.
- N-4: with a bench-built R8, registered, generation row added and set as default, under the raised cap: the derivation-only basis names R8, and the ordinary preflight at 25G83 refuses `acceptance_artifact_epoch_mismatch`.
- R8 does change the number the claim path uses: operatives, members and statistics are identical. N-3's diff shape matches r6→r7; I recomputed the recursive diff and only the ID, derivation digest, one pin and derivation_notes changed.
- H1 by absence holds in code:
  - `EPOCH_CONTINUATION_REGISTRY` is empty, and continuations come only from it (calibration_epoch_continuation.py:326).
  - Bracket freshness is by identity only (calibration_bracketing.py:2117-2182), so 25G83 always evaluates stale.
  - Production configs require the bracket (schemas.py:708-711).
- The main issuer accepts R8 as predecessor: it must equal ACTIVE (:1798), be of a different epoch (:1982), and R8's maximum plus range equals the ruled R6 constant.
- The identity-seam finding (:2046-2059, no sampler requirement) is accurate.
