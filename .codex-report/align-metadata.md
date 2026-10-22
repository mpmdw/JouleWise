# Metadata baseline lane

## SUMMARY

Work in progress: contracts and repository intake reviewed.
The metadata lane starts from the alignment spine.
The implementation will use the standard library only.
Statistics live in stats.py and are re-exported by metadata_baseline.py.
The local execution environment is pending; no tests have run yet.

## FILES

- .codex-report/align-metadata.md: lane checkpoint and eventual verification record.

## PUBLIC API

The seven exact signatures in the build brief govern implementation.

## TESTS RUN

None yet; execution environment pending.

## END-TO-END

Pending implementation and execution.

## DECISIONS I MADE

- The user brief is the authority for this bounded synthetic-only task; no queue or state-kernel writes are authorized.
- Preserve all three frozen shared contract files.
- Follow Episode.totals for decode counts, including its recorded hidden-token component; set only the logged-only hidden_tokens feature to zero.
- No heavy dependency is needed.

## CONTRACT-CHANGE

The records contract retains hidden tokens inside logged decode counts. The brief's description of hidden work invisible to the log therefore needs explicit synthetic records whose visible decode totals match; do not silently subtract from Episode.totals. A future visible_decode_tokens convenience field could make this distinction clearer. No contract files changed.

## OPEN ISSUES

Implementation, tests, and final verification pending.

## NEEDS_RULING

none
