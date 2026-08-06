## Positions

1. **Recommend Option 2: close historical claim consumption and recollect prospectively.** Do this as three compact, claim-coherent windows—not one catch-all “Window D”:

   1. Fresh 1.5B decode-floor window: 10 absolute repeats plus 10 same-condition null-ABBA blocks/40 members.
   2. Fresh 7B decode-floor window: the same 10 absolute plus 40 null-ABBA design.
   3. Fresh 1.5B-versus-7B contrast window: 10 ABBA blocks/40 members.

   Each window receives its own fresh §5A preparation, live reservation-first pre/post calibration receipts, 3+1+3 references, in-window dual-family NEG-8 bound, whole-window verdict, committed ledger-head pin, and custody backup. The existing plans estimate the 7B floor at about 3.0 hours and contrast at 2.6 hours including 20% margin; combining those was already rejected by D-085. A similarly focused 1.5B decode-floor window should fit the same compact shape and avoids replaying a10’s irrelevant prefill/short-prefill cells.

   This produces the clean paper chain:

   `historical development corpus → issued D-079 acceptance rule → prospective live window brackets → prospective stack-specific floors → prospective contrast`

   That is materially stronger than amending a just-issued contract to salvage known outcomes. It also matches the current paper text, which says calibrations bracket the science “in-session,” and D-113’s standing rule that feasible fresh collection is the default when it improves epistemic quality.

2. **The present refusal is real, but Option 1 is physically plausible.** The [candidate discovery code](/Users/edr/code/JouleWise/joulewise/calibration_bracketing.py:712), [universe equality check](/Users/edr/code/JouleWise/joulewise/calibration_bracketing.py:971), and [bundle wrapper](/Users/edr/code/JouleWise/joulewise/calibration_bracketing.py:1316) all exclude imports. The [ledger contract](/Users/edr/code/JouleWise/docs/contracts/calibration_ledger.md:48) explicitly says imports are neither fresh observations nor bracket endpoints. With zero live observations, every historical evaluation must therefore refuse.

   A read-only comparison of authenticated ledger receipt fields against bundle windows nevertheless found complete matching historical pairs:

   | Historical basis | Selected pre/post attempts | Drift |
   |---|---|---:|
   | a10 | `20260725T030533-d3f076e5` / `20260725T060617-97c5cba6` | 0.000166803 s |
   | Window C | `20260726T225920-ab4272f5` / `20260727T015824-45feb516` | 0.001279584 s |
   | old Window D | `20260727T020611-4a409a30` / `20260727T050047-95e2f87e` | 0.000484439 s |
   | 7B floor | `20260729T204105-39d25f8a` / `20260730T014035-124df355` | 0.003679572 s |
   | contrast | `20260730T210703-f76b5771` / `20260731T012210-374020b6` | 0.001280874 s |

   All are below the 0.010818 s screen; their pre endpoints are below the 0.033558756679900 s level screen. Thus the objection to Option 1 is not physical causality—the capture times genuinely bracket the windows. It is contemporaneous completeness and contract provenance.

3. **If Option 1 is chosen despite that recommendation, the generic proposal is too broad.** “Any window entirely preceding the ledger cutoff” is not a sound predicate: the cutoff is a ledger sequence and digest, not a wall-clock instant, and receipts contain no import/issuance timestamp. Use a new, finite historical-closure authorization instead:

   - Preserve `d078_authenticated_max_bracket_rederivation_v1` unchanged as live-only.
   - Mint a new semantics identity, such as `d079_authenticated_cutoff_import_bracket_rederivation_v1`.
   - Bind an exact-byte authorization artifact to the issued acceptance artifact, cutoff 76/head digest, and a finite allowlist of historical evaluation-basis digests. Do not authorize arbitrary pre-genesis windows.
   - Define the candidate universe as **every** valid import-marked observation at or before the issued cutoff—30 candidates—not merely matching or causal candidates.
   - Require exact equality between supplied candidate triples `(attempt_id, content_id, receipt_digest)` and that complete universe. The existing prior-prefix equality separately authenticates all 38 valid and invalid observations.
   - Authenticate every valid candidate from primary custody; any one invalid custody tree refuses the whole universe.
   - After universe authentication, filter by v3 protocol and full T1 equality, then retain the existing causal/freshness rules:
     `pre.capture <= window_start`,
     `post.capture >= window_end`,
     `window_end <= pre.capture + MAX_AGE_S`,
     `post.capture - window_start <= MAX_AGE_S`.
   - Select nearest endpoints deterministically, with an explicit tie rule or tie refusal.
   - Keep all live post-cutoff observations active in D-102 trigger evaluation. Historical imports remain prior observations and never become “new.”
   - Persist the new semantics ID, authorization digest, candidate role, cutoff, and selected receipt digests in whole-window and per-member consumption provenance. Never mix live and historical endpoints implicitly.

   Mandatory regressions include:

   - Existing live semantics still excludes all imports.
   - Historical semantics accepts only allowlisted basis digests and refuses altered bundle times/membership.
   - Omitted, added, duplicated, or unauthenticated valid imports refuse the anti-narrowing check.
   - Mixed live/import candidacy, post-cutoff imports, wrong cutoff/head, or absent authorization refuse.
   - Full-T1, epoch, v3 protocol, freshness, preflight, screen, and budget boundaries remain exact.
   - New live range expansion, systematic failure, or 38-valid trigger still stales the acceptance artifact.
   - Real-vector regressions pin the pairs and drift values above; Window B remains prohibited.
   - End-to-end runner, extraction, mint, rebinding, and tamper regressions prove the historical semantics cannot be selected by changing only a report field.

   Estimated blast radius is medium in `calibration_bracketing.py`—roughly a new role/authorization layer plus universe and provenance helpers—and medium-high in `whole_window.py`, whose semantics dispatch, session preparation, evaluation-basis construction, and provenance validation all assume the current closed set. Expect approximately 250–450 production lines across those two files, additional changes in the runner/mint/extraction registries, and several hundred lines of regressions. This requires a rule-11 cold gate.

   Security properties preserved: primary-byte hashes, physics replay, custody, exact identity/T1, protocol identity, ledger chain and committed head, issued cutoff, prior-set completeness, anti-narrowing, 24-hour freshness, deterministic causality, D-079 screens/budget, and decimal arithmetic.

   Property weakened—but only bounded, not eliminated—is reservation-first contemporaneous completeness. Historical import can prove “every reviewed surviving governed observation was imported”; it cannot prove that no pre-ledger crash or abandoned capture vanished without an artifact. It also introduces a retrospectively authorized consumption mode after outcomes are known. A finite allowlist and distinct semantics identity contain that weakness but cannot erase it.

4. **Option 2’s desk work remains substantial and valuable.**

   - Freeze three exact plans and runtime budgets, using immutable plan/root identifiers rather than “Window C/D.”
   - Build the 1.5B decode-only floor plan from the proven 10-absolute/40-null design.
   - Finish or verify generalized mint pinsets for both fresh floors. The six-decimal operative literal must be supplied as a reviewed per-plan integrity pin; the mint path must not derive it.
   - Freeze extraction specs, order manifests, evidence-root IDs, and contrast manifest before collection.
   - Add a synthetic three-window live-ledger integration regression.
   - Prepare the D-102 successor-artifact path before collection. Three ideal windows add six valid observations, taking the corpus from 30 to 36—below the 38 trigger—but any range-expanding valid calibration or new systematic failure stales the anchor immediately.
   - Prepare results-table and methods prose with placeholders, not numbers.

   Historical corpora remain useful as the D-079 derivation/prior-observation corpus, instrument characterization, selector regression vectors, reproducibility tests, method-development narrative, and labelled diagnostic comparison against fresh results. They should not supply Phase-3 claim numbers or outcome-dependent sample-size changes.

5. **7B impact.**

   - Under Option 1, the old 7B floor is mechanically salvageable only through the new historical semantics. Its historical pair implies an operative fiducial bound of `0.031467745880268516 + 0.010818 = 0.042285745880268516 s`; the joule floor must then be governedly rederived. The old 13.998036715 J result and its literal cannot be presumed unchanged.
   - Under Option 2, `window_7bfloor_20260729` remains diagnostic/non-claim evidence. The fresh 7B window recollects both absolute and null-comparative floor cells; the fresh contrast is collected separately. This follows D-085’s original floor-first structure.
   - Per-bundle embedded `b_fiducial` is not an acceptable intermediate claim route. It is hash- and physics-authenticated—not literally self-attested—but it supplies neither a post-window endpoint nor the D-102 stability allowance and does not discharge ledger-universe completeness.

## Disagreements

- The exclusion was introduced by commit `63f43a68` in the CAL-BRACKET/ledger arc and later retained by the issuance reconciliation; attributing its origin solely to PR #109 is imprecise. The operative fact is unchanged.
- Fresh collection does **not** remove historical imports from the entire claims chain: the issued D-079 acceptance rule still derives from the historical n=19 corpus and 38-member imported prior set. The stronger, accurate paper claim is that historical data establish the acceptance rule while prospective live receipts bracket all claim-bearing science.
- The fork misses `window_contrast_20260730`, which is also pre-genesis and is essential to the MVP demonstration. Closing historical consumption therefore invalidates more than a10, Window C, and the 7B mint.
- Option 2 cannot be represented honestly as one fresh “Window D.” The identifier already refers to `runs_window_d_20260726`, while D-113 separately reserves future C/D terminology for Window-B replacement work.
- Closing the historical re-mint supersedes D-110’s explicit re-mint order and requires rewiring D-113’s readiness dependency, which currently expects that re-mint to complete before later fresh-claim collection.
- The existing [hard literal](/Users/edr/code/JouleWise/scripts/mint_floor_artifact.py:91) is an independent refusal exactly as reported. It should be replaced by per-plan pin supply through the generalized path, not loosened into data-derived mint behavior.

## Open questions

1. Does the lead want the three-window P1 decode closure to supersede or precede the broader D-113 `MET-WINDOW-C-01` C2/C4/C5 replacement campaign?
2. Will Ed ratify superseding D-110 with fresh replacement, including the corresponding D-113 dependency rewrite?
3. Is the MVP claim set limited to the decode contrast? If more phase cells are required, the fresh floor scope and window count increase.
4. Should a successor D-079 rederivation packet be fully prepared before the first fresh window, so a range-expanding or systematic live observation does not strand the campaign?
5. If schedule pressure later changes materially, is the acceptable fallback the finite, explicitly disclosed historical-closure semantics above—not a generic import-candidacy rule?

## Recommendation

Adopt Option 2 and record the old historical mint chain as closed for claim use. Recollect a fresh 1.5B floor window, a fresh 7B floor window, and then the fresh cross-model contrast, each independently live-bracketed and claim-coherent. Preserve Option 1 only as a separately versioned, finite-allowlist contingency requiring a rule-11 cold gate.

This costs three quiet windows, but it removes the only material provenance weakness the imported endpoints cannot repair, matches the paper’s stated method, avoids mutating newly issued semantics, stays below the corpus-doubling trigger on the ideal six-endpoint path, and gives the metrology-expert advisor the cleanest defensible Phase-3 claims chain.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Recommend superseding historical re-mint with three prospective live-bracketed windows; a finite, separately versioned historical-closure mode is defensible only as a cold-gated fallback.","pathspec":[],"verification":["HEAD c5373862c488f7c8f20d9f42e7ae341f52f98fd5; tracked worktree clean","Inspected calibration_bracketing.py, calibration_ledger.py and contract, whole_window.py, test_calibration_bracketing.py, issued D-079 artifact, ledger snapshot, and mint paths","Loaded ledger snapshot successfully: 38 historical observations, 30 valid, 2 systematic-invalid, 6 ordinary-invalid, zero live","Read-only bundle/ledger temporal analysis identified complete matching historical pairs for a10, Window C, old Window D, 7B floor, and contrast","No test suite executed; discussion/source-inspection lane only"],"flags":["no_edits","read_only","full_suite_not_run"]}