# 13 — Merge of origin/main into feat/2026-09-05-d165-relabel (Opus lieutenant)

Merge base `7792fc57`; branch head `ebb52191`; `origin/main` `434568f0`
(paper-K #288, custody seam #289, paper-L context). Two content conflicts.

## Conflict 1 — `joulewise/dominance_closeout.py`

Main refactored refusal reason strings into `D165_CLOSEOUT_REFUSAL_ENUMERATION`
and derived ~18 private `_UPPER_SNAKE` constants from it; the branch replaced
the single active rule id with the v1/v2 pair plus the verbatim legacy block.

Resolved at `joulewise/dominance_closeout.py:112-181` (pre-resolution numbering)
by keeping **both**:

- kept every one of main's enumeration-derived constants
  (`_CELL_NOT_COMMON_MODE` … `_REPLAY_SIDECAR_IDENTITY_MISMATCH`), now
  `joulewise/dominance_closeout.py:113-166`;
- kept the branch's relabel constants, now
  `joulewise/dominance_closeout.py:167-186`:
  `LEGACY_COMMON_MODE_REPLAY_RULE_ID = "…replay.v1"`,
  `COMMON_MODE_REPLAY_RULE_ID = "…replay.v2"`, `COMMON_MODE_REPLAY_RULE_IDS`,
  the `# LEGACY v1 BEGIN/END` block holding `LEGACY_ABSOLUTE_COMMON_MODE_REASON`
  verbatim, and the new `ABSOLUTE_COMMON_MODE_REASON`;
- dropped the branch side's `CLOSEOUT_INPUT_MALFORMED_ADAPTER = "closeout_input
  _malformed: replay.block_ids"` literal (base text the branch never edited).
  Main's enumeration entry carries the byte-identical value and is already
  bound at `joulewise/dominance_closeout.py:104-106`, so no reason string moved.

Main's era-independent `"reason": ABSOLUTE_COMMON_MODE_REASON` sidecar path
auto-merged into the branch's era-selecting form at
`joulewise/dominance_closeout.py:1165-1175` — branch semantics intact.

## Conflict 2 — `docs/paper/results-fill-registry.md`

Main had performed a *partial*, pre-relabel-aware edit of the same paragraph and
the same eight R_cm rows: `.v2` naming plus a `SUPPLIER_PENDING: the producer
emits .v1 until the D-165 relabel lands` disclosure. The branch resolves that
pending state — the producer now emits `.v2` — so the branch text wins.

- Rationale paragraph `docs/paper/results-fill-registry.md:224-231`: branch text
  kept verbatim, including the frozen registered absolute rationale.
- Table rows `docs/paper/results-fill-registry.md:235-266`: branch rows kept;
  **row sets on the two sides were verified identical** (29 rows, same tokens,
  same order) — no row dropped, none added, none reactivated.
- Every `SUPPLIER_PENDING` clause is gone from the registry (0 occurrences).
- Main's non-overlapping registry edits auto-merged and were kept: the expanded
  `D165` source bullet, and rows `V5-WL-001` / `V5-WL-004`.

**SUPPLIER_PENDING grep (requested):** the phrase survives only in process
traces (`2026-09-04-paper-k/{05,07,08,99}`, `2026-09-05-d165-relabel/{07,08}`).
It appears **nowhere** in `docs/paper/draft-v2-skeleton.md`, which also carries
no `.v1` rule token — the paper-K/L draft does not expect the pending wording.
This matches the merge guidance already recorded in `08-fix-round-4-report.md`.

## Allowlist re-pin (not a widening)

`tests/fixtures/d165_rationale_allowlist.json` pins `(path, line, phrase)`. The
merge shifted lines, so 10 entries went stale and the census *errored* instead of
reporting. Each was re-pinned to the byte-identical occurrence, same phrase, same
reason, no entry added or removed: registry 229→231, 244→246, 260→262 (uniform
+2); `dominance_closeout.py` 50→167, 59→176 (×3), 65→182, 606→874;
`draft-v2-skeleton.md` 221→253 (Figure-2 ABBA caption, line text identical).

## Test tails (one module at a time, `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`)

- `tests.test_d165_rationale_census` — **Ran 8 tests, FAILED (failures=1)**.
  RED *only* on paper-K/L-owned `docs/paper/draft-v2-skeleton.md`: 13
  occurrences on lines 156 (×2), 157, 637, 902 (×3), 1174 (×3), 1888 (×2), 1889.
  No non-draft line is RED. The allowlist was **not** widened to hide these.
- `tests.test_d165_dominance_closeout` — Ran 59 tests, OK.
- `tests.test_dominance_closeout` — Ran 3 tests, OK.
- `tests.test_paper_terms_lint` (registry integrity) — Ran 4 tests, OK.
- `tests.test_paper_round7_artifacts` (registry integrity) — Ran 55 tests, OK.
- `tests.test_d117_contrast_v5_pack` — Ran 40 tests, OK.
- `tests.test_night_gate` — Ran 47 tests, OK.
- `tests.test_paper_custody` — **Ran 29 tests, FAILED (failures=10)**, all from
  one fixture assertion: `stale supply-map receipt digest: d165_closeout`.

## Unresolved — escalated, not fixed

PR #289's custody seam pins `_validator_source_sha256("d165_closeout")`, which
hashes the source of `joulewise/dominance_closeout.py`. The D-165 relabel edits
that source, so the digests recorded in `configs/paper_supply/supply_map.json`
under `roles["fixture.d165_closeout"]` no longer reproduce. Bench-verified this
session: a read-only `git archive origin/main` snapshot recomputes the recorded
receipt `1a10b387…a05f53` exactly (MATCH True), so the break is merge-induced,
not pre-existing.

Resolving arithmetic, computed but **deliberately not applied**:

- `validator_source_sha256`: `43c46acd…6489a8` (main) → `9a3b66d0…524814` (merged)
- `receipt.expected_sha256`: `1a10b387…a05f53` → `efde2f12…cfc450`
- `inventory.expected_sha256`: `50ed99c0…254815` → `44360110…3a06d7`

The entry is `mode: test_fixture_non_issuing` with marker
`synthetic-no-measurement-value`, so no measurement value rides on it. It is
nonetheless a fail-closed custody anchor with no documented refresh lane in
`docs/contracts/paper_supply_custody.md` and no regeneration script; re-anchoring
it is a magistrate call under D-161, not a lieutenant one. Left RED.
