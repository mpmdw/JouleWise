# Alignment metadata baseline — fix round 1 (fix1e)

## SUMMARY

Continued from the existing metadata lane head, without rewriting history.
Logged decode features now subtract hidden tokens in logged turns.
Turn timestamps remain visible; the all-work view keeps full decode counts.
Added CI ports of the reviewer's exact-equality repros for both timing cases.
Normalised the discovery registry prefix to cover all alignment subpackages.
F1/F3 implementation is saved; CI verification is pending.
The remaining statistical fixes are prepared for the next meaningful step.
No shared contracts, twin files, or review_repro files were committed.

## FILES

- joulewise/align/metadata_baseline.py: logged-view hidden-token correction.
- tests/align/test_metadata_baseline.py: hand-computed visible counts and stripped-log equality.
- tests/align/test_metadata_baseline_review.py: independent reviewer worlds and F1 repros ported into CI.
- tests/test_shard_tests.py: minimal existing registry exception, prefix changed to "align.".
- .codex-report/align-metadata.md: this progress record.

## PUBLIC API

The original seven signatures remain unchanged. The refitted-procedure API will be documented with F2.

## TESTS RUN

The first command attempted was `python3 --version`. The shell repeatedly returned
"No usable execution environment is available." No Python result is claimed.
F1 repros are committed as unittest cases so draft PR #523 CI can execute them.
CI results will be recorded after the run completes.

## END-TO-END

The ported reviewer worlds exercise real records, feature extraction, grouped
training, probabilities, AUC, and DeLong intervals. Printed results are pending CI.

## DECISIONS I MADE

F1 follows the records' definition of hidden tokens and the explicit lead ruling:
subtract hidden tokens from every logged decode-derived feature; keep timestamps.
F3 uses the sibling lanes' "align." prefix and stays within the registry exception.

## CONTRACT-CHANGE

none. Episode.totals is unchanged; features adapts the full decode count to the logged view.

## OPEN ISSUES

F2, F4 and N1–N5 implementation and verification remain in progress.
The final report will carry the uncommitted twin patch and full null_cov2 extension.

## NEEDS_RULING

none

## FIX LOG

- F1: implementation saved; awaiting CI before recording fixed commit.
- F2: in progress.
- F3: implementation saved; twin-present repro requires a VM.
- F4: in progress.
- N1: in progress.
- N2: in progress.
- N3: in progress.
- N4: in progress (F4).
- N5: in progress.
