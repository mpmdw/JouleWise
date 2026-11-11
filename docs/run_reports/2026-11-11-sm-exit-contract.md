# sm-exit-contract — 2026-11-11

Built audit §8.2 items 6 and 9 as new, read-only shadow code. No driver or
existing module imports it. No host, custody, results branch, real restricted
directory, network or model weights were accessed. Coordination state was not
edited. The supplied branch was already `feat/2026-11-11-sm-exit-contract` and
the initial working tree was clean. M0 found no active stop card; the explicit
seat brief selects this AGENT task over the older generated queue pointers.

## Sources

Read audit §§2, 4.2, 7.19 and 8, and the state-machine lane plan, from their
specified local remote-tracking refs. Inspected code with `git show`, without
checkout or execution. Both required generations were checked for every path.
Missing files were recorded rather than inferred from the other generation.

| Citation ref | Commit inspected |
|---|---|
| `origin/main` | `54eb4ba3020eb0b23a62bdf48e788efd3770d0fe` |
| `origin/align/2026-11-08-v4-r11` | `b4a6c217f0285a20aff33a8407160dd77af2a8a6` |
| `origin/ops/2026-11-08-air-offload-merged` | `b5af05e12a0407b11ace28a53431537a8341f882` |
| `origin/align/2026-11-08-v4-release-tools` | `b2c0681cd651263df7b14f005a1ea1dfe44e1fd9` |

All nine vocabularies are code-verified. Each entry carries ref:path:line
citations. None requires `verified=False`. The classifier and projection also
refuse an unverified contract, for future entries that lack evidence.

| Key | Vocabulary found | Difference or qualification relative to audit §7.19 |
|---|---|---|
| `night_driver` | 0 GO; 3 REFUSED; 4 ABORTED; 5 CHAIN_FAILED; 6 COURIER_FAILED | Same constants on main and W1. GO describes admission, not payload success. |
| `r1_driver` | 0 complete; 3 refused; 4 aborted | Same listed vocabulary. File exists on W1 only. |
| `r1_runtime` | 0 complete; 2 refused; 3 failed; 128+n aborted | W1 only. The table bounds the signal convention to 129..255 (n=1..127). The runtime installs HUP/INT/TERM, not every signal in that convention. Negative subprocess signals remain undeclared. |
| `b5_chain` | 0 completed; 10 reservation_failed; 11 pre_calibration_capture_failed; 12 pre_calibration_screen_failed; 13 operative_bound_above_stop; 64 inspection_refused; 75 horizon_skipped | Main lacks the W1-only declaration of 13. This table is the union. Code 75 belongs to the stage journal; the chain continues to post capture and can terminate at 0. It is not a terminal chain-exit declaration. |
| `dry_run` | 2 tooling_refusal > 3 outcome_class > 0 completed_without_tooling_refusal with no outcome_class step | Same precedence. File exists on main only. Outcome_class is HOLD, not SUCCESS. |
| `release_check` | 2 refused > 1 hold > 0 agree | Verified from main's release_b5 and the release-tools ref's release_v4. Block-5 calls a refusal a hold in its verdict; v4 calls it refused. Exit 1 can also be an uncaught crash. Neither source is on the W1 ref. |
| `harvest` | 0 COLLECTED/NO_COLLECTION/NULL; 2 HARVEST_FAULT; 3 unresolved inputs or unusable archive; 4 NOT_READY; 6 planned members with none present | Same numbers on both refs. W1 additionally returns 3 for StorageStop. The ordinary exit-3 exception branch prints HARVEST_FAULT without writing harvest.json. Zero is process completion, not claim usability. |
| `offload` | 0 ok; 2 Refusal; 3 Mismatch; 4 DeadlineStop/Interrupted; 5 TransportError; 6 io_error | Verified on both offload and W1 refs, absent on main. Zero can include a held release. The code is no proof of two copies or deletion. |
| `prequal` | 0 pass; 1 fail; 3 incomplete; 2 usage | Same list, W1 only. 2 is argparse's usage error. |

These tables describe declared vocabularies, not every incidental interpreter
exit. For example, argparse can exit 2 in the night and R1 drivers although
their declared audit vocabularies omit it. Those cases remain UNDECLARED.
Argparse usage also collides with declared 2 in some other tools. A return code
alone cannot resolve those ambiguities. No extra success code was inferred.

## Design

- Frozen dataclasses, tuples, ranges and mapping proxies keep the declarations
  immutable. The seven requested classes suffice; the enum docstring explains
  each. The original words and important ambiguities remain in the data.
- `classify` accepts a tool key or a parsed Contract. Unknown tool keys raise
  KeyError. Only exact ints in 0..255 can match a verified declaration. Bool,
  int subclasses, other types, negative signals and unknown codes return
  UNDECLARED, word `undeclared`, declared=False and is_success=False.
- The plan parser accepts the value of a future exit_contract key. It accepts
  integer keys and canonical ASCII decimal string keys. It refuses duplicate
  normalized codes, aliases, invalid words and missing zero or success. Its
  named ValueError subtype has stable reason identifiers. `complete` is the
  sole success word; refused/failed/stopped/usage/hold form the rest of the
  closed set. Multiple complete codes are allowed. Zero need only be declared,
  as specified; it need not be the success code.
- `as_outcome_map` returns a fresh plain dict and expands ranges. No window_state
  import or real-plan reader was added. Precedence is immutable data; no combine
  helper or adoption was added.
- Drift tests parse source ASTs, never operational imports. They check named
  constants or condition-linked literal returns. Missing baseline source paths
  and moved owners fail with the entry name. Branch-only files are checked if
  present at HEAD. W1-only 13 has an explicit main-generation absence check;
  when that symbol arrives, its value must be 13. A separate local-ref AST pass
  checked all 65 cited declarations, including every file absent on main.

## Files

Added `joulewise/exit_contract.py`, `tests/test_exit_contract.py` and this report.
Existing-file changes are exactly one tool-map row in `CANONICAL.md` and one
alphabetically inserted timing line in `scripts/test_timings.json`. The timing
is a local scheduling hint, not a hosted estimate. No coordination-state edits.

## Verification

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_exit_contract` | Initial 24 tests passed in 0.338 s. After guard/drift additions, 26 tests passed in 0.328 s; final run passed all 26 in 0.335 s. |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | 14 tests, OK in 0.271 s; 2 skipped because the sandbox denies ps. The existing live census smoke remains PROVISIONAL. |
| `python3.13 -B -m unittest tests.test_gen_state` | 44 tests passed in 3.633 s. |
| `python3.13 -m compileall -q joulewise/exit_contract.py tests/test_exit_contract.py` | Passed on both touched Python files. No existing Python source needed compilation. |
| `python3.13 -B -` (one-off AST provenance script) | All 65 unique ref/path/entry probes passed using the test module's independent PROBES table and git-show text. No cited tool imported. |
| `python3.13 -B -` (one-off in-memory classifier mutations) | Tests rejected all 10 mutations: verified/type/lower/upper guards removed; range removed; equality ignored; match inverted; declared flag removed; fallback success; unknown tool tolerated. |
| `python3.13 -B -` (grammar and timing-map checks) | Both Python files parsed with feature_version=(3, 11). Timing JSON parsed and differed from HEAD by exactly the one alphabetically inserted line. |
| `git diff --check` | Passed. |

The new tests exhaust every declared code, every undeclared exit byte per tool,
negative signals, type abuse, bounds, unknown tools, both success guards,
immutability, precedence, map projection and each parser refusal. Temporary
source fixtures are generated within TemporaryDirectory, never committed.

The full suite was prohibited because the blinded analysis job is active.
No measurement pipeline or native MLX code ran. This module is standard-library
only and needs no MLX-native gate. Python 3.11 runtime execution was not run;
CI must exercise its normal 3.11/3.13 matrix. The grammar check is not runtime evidence.

## Handoff

No blocking question. The union table, signal-range convention and code-only
ambiguities above are the limits of the evidence, not hardware validation.
The lead should cold-review the commit, then integrate this shadow module.
The lead must run the two skipped live census checks outside the sandbox if
that existing smoke is required. Writer/driver adoption stays out of scope.
No push, PR or merge was made. The final response identifies the local commit.
