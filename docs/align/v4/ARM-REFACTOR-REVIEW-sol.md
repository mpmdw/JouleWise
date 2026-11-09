# ARM terminal refactor review — Sol, 2026-11-08

**Verdict: ADMIT** for the terminal-helper extraction. No behavior change found;
no production fixes applied. This is a synthetic code-equivalence review, not
approval of live collection, sealed analysis, exporter semantics or a merged head.

Reviewed exporter `4c4b76e3a31549fab57b25dd6c5d537a0bb39582` against the
locally available latest r11 head `52f36f1d8d718f90d3e0d390c53275bce5f3e9c1`.
Work branch: `align/2026-11-08-armrefactor-sol`. Initial tree was clean.

## Equivalence finding

The complete old `terminal()` body is frozen in
`tests/align/test_v4_terminal_equivalence.py`; a separate local AST comparison
confirmed it matches r11 exactly. Both `GitEvidence` and `WindowRecord` also
match r11's AST exactly. The witness extracts the current nested `terminal()`
from `build_packet`, rather than maintaining a second candidate implementation.

Expanding the two helpers reproduces the old ordered statements, with these
reviewed substitutions:

- The old tuple assignment reads plan then result; the new code reads plan
  then immediately enters the release helper to read result.
- The release helper retains schema validation, marker-presence booleans,
  courier and empty sent-marker authentication, literal `sent is True`, the
  unchanged `terminal_window_release` arguments/refusal reason, and the
  conditional chain-exit agreement check.
- Release still precedes the watchdog latch. The latch's raw result lookup
  now uses `WindowRecord.source('result', json_value=False)`. `result` is not
  one of `FINAL_SOURCES`, so this delegates to the same commit and descriptor
  as the old direct `evidence.source` call. Earlier successful result reads
  guarantee that descriptor exists; the decoded record is not mutated.
- `started` is restored in the caller before `captures()`. Re-reading the
  same JSON source map preserves its value. Capture authentication and
  `null window carries captured members` remain after the latch. The success
  basis and `decision.reason` are unchanged.

Thus decisions, refusal text and precedence, authenticated source reads, and
returned details are equivalent for inputs through the production JSON/Git
evidence contract, including malformed evidence. This conclusion rests on the
statement comparison and accessor analysis; the finite grid alone is not an
exhaustive proof over all possible JSON values or arbitrary Python test doubles.

The committed witness adds 5 tests: the helper-expansion AST comparison and
5,340 differential cases (5,184 Cartesian variants, 56 source faults, 96
field/clock faults, and 4 explicit controls). It compares serialized return or
exception type/text, ordered source/release/Git operations, inventories, accesses
and input state. It uses production decode/digest/source/capture/release code
with only Git reads replaced by synthetic in-memory blobs. Controls cover all
three allowed release kinds and the restored null-window capture refusal.

## Other arm files and branch history

**No other existing ARM-PATH file changes in the exporter-side delta.**
`git diff --name-status origin/align/2026-11-08-v4-r11...4c4b76e3a` has exactly
one modified existing file: `scripts/align_v4_next_arm_packet.py`. All other
entries are added analysis/exporter/release files. The script's diff from the
common ancestor `e8ea97d22db98365d0da90ea974cb8134c116de5` contains only the
two helper extractions and caller replacement.

**Literal tree equality with latest r11 cannot be confirmed.** r11 has six
later commits absent from this exporter snapshot. Its `f45536616` changes the
desk-exclusion factoring in this same file and other timing/finality code.
Consequently a two-tip diff also differs in `scripts/align_v4_session.py`,
`scripts/run_night.py`, `joulewise/hazards/arm.py`,
`joulewise/timing_receipts.py`, `joulewise/align/apple/light_triage.py` and
`joulewise/align/apple/v4_contention.py`. Those are branch-history differences,
not changes introduced by the terminal extraction. Neither
`joulewise/arm_retry.py` nor the existing 45-test module differs between tips.
The terminal finding is against latest r11, not merely the common ancestor.
This ADMIT does not adjudicate the absent r11 changes.

## Executed evidence

Python 3.13; modules ran sequentially, synthetic evidence only:

- `python3.13 -B -m unittest tests.align.test_v4_next_arm_packet` — **45 passed**,
  119.802 s.
- `python3.13 -B -m unittest tests.align.test_v4_terminal_equivalence` — final
  **5 passed**, 7.251 s. An earlier four-test version also passed (7.195 s).
- Local `git show`/AST comparison against the pinned r11 commit — exact match
  for the frozen terminal body, `GitEvidence` and `WindowRecord`.
- In-memory `compile()` of the production script and new witness — passed,
  with no bytecode writes.
- `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` — exit 2:
  `PermissionError: [Errno 1] Operation not permitted: 'ps'`. Census was not
  observed; no clean-census claim or process action.

Full-suite execution was explicitly prohibited. No network, real measurement
data, sealed custody, analysis pipeline, model download or MLX execution was
used. No native MLX test is required by this pure refactor review. Lead-owned
coordination/state files were preserved. This report and the new witness are
the only review writes; the local review commit carries both.

No open terminal-equivalence question. Next exact step: lead reviews this
report and witness, preserves the latest r11 follow-ups during integration,
then reruns the two targeted modules on that integrated head. A clean fixture
census remains unverified in this sandbox.
