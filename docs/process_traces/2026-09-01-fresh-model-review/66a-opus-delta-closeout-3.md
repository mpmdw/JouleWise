# 66a — Opus 5 delta re-audit over close-out r3 (trace 52) — CLEAN, four nits

Seat: Opus 5 (Agent, contract + execution lens, read-only) over
`feat/d165-dominance-closeout-core` @ `eba1b62c`. Brief: replay the r3
mutation list (12 mutations: floor-seal digest flip, forged sidecar/manifest
pair in both directions, census duplicate/missing cell, component swap,
decode-boundary malformed bytes on each of the three entry paths, builder
bypass of the bytes-only channel, …) on a scratchpad copy; verify ruling 40b
as amended by 48d §Packet 1 clause by clause.

## Verdict
`VERDICT: CLEAN`. All 12 mutations killed by a named test; forged pair refused
in both directions; floor-seal mismatch selects the neither branch with
`floor_artifact_source_hash_mismatch`; one `try/except TypeError` per entry
path → `closeout_input_malformed: <path>`.

## Nits and magistrate disposition (bench, commit `140ec4cc`)
1. Decode-boundary refusal at `joulewise/dominance_closeout.py:1404` names a
   string outside the `closeout_input_malformed` family. **Recorded, not
   changed** — the boundary refusal names the malformed source itself, which
   is what the ruled family is for; a second family for the same boundary
   would be a synonym.
2. Contract CLI line (`docs/contracts/d165_dominance_closeout.md:282`) not
   test-bound; the CLI test re-typed the flags. **Cured**:
   `test_contract_runnable_command_names_exactly_the_parser_flags` extracts
   the fenced command and compares its flags, order, and optional-bracketing
   to `argparse` (probe: renaming `--replay-sidecar` in the doc alone → FAIL).
3. "the already-defined …" meta-commentary at contract :90/:328/:357.
   **Cured** — deleted.
4. `mint` / `stage-2 mint` unglossed at first use (:102-104). **Cured** —
   glossed in the glossary paragraph as the program owed by
   `D165-SIDECAR-EMIT-01`, the only producer of a sidecar.

PR: #254. Paper cannot cite a close-out until the stage-2 mint lands.
