# 25 — Legacy L1 cure: Opus counter-review (CONTRACT lens)

Seat: Opus 5, contract lens. Worktree `/Users/edr/code/JouleWise-wt-legacy-l1`,
branch `feat/2026-09-04-legacy-l1` (5 ahead of, **14 behind**, `origin/main` at
`92350cad`; merge-base `5e416c47`). Read: reports 20–24, the branch log/diff,
the RPT-001 spec, `docs/specs/c027/ADJUDICATION.md`, the three producers, and
all 30 changed files.

**Verdict: LANDABLE**, with one should-fix landing condition (C1) and three
nits. No blocker; the route closure is sound and independently re-verified.

---

## Executed evidence (this session, this worktree)

All with `PYTHONDONTWRITEBYTECODE=1 python3 -B`.

```
git diff --exit-code --stat origin/main      -- analysis/rpt001-v1 figures/rpt001-v1 → rc 0
git diff --exit-code --stat origin/main...HEAD -- (same two paths)                   → rc 0
unittest tests.test_build_capstone      → Ran 2,  OK
unittest tests.test_claims_index_lint   → Ran 30, OK
unittest tests.test_rpt001_report_slice → Ran 19, OK (skipped=2)
scripts/claims_lint.py --mode phase4    → claims_lint: clean (rc 0)
grep -aE '<4 full-precision means|4 rounded forms|retired label|primary basis>'
         over the 10 tracked files the profile writes                            → rc 1 (clean)
lint_claim_index(v1 grandfather, write_projection=True) → projects `L1 / voided`, sanitized text
```

---

## Q1 — Contract impact beyond the ruled D-161 one-liner

**Yes: one addendum entry is needed.** The ruled D-161 line records the
*policy* ("closed publication route… producers emit void placeholders…
regeneration cannot reopen it"). It does not amend the four RPT-001 spec
clauses the cure contradicts — none of which carries a supersession note
(§5.2, §5.3 and §6.1 do carry one; these four do not):

- **§7 "The report vertical-slice page"** — twelve mandatory, ordered page
  contents. The void page satisfies items 2 and 11 only; it drops the required
  heading ("Legacy vertical-slice instrument results"), the exact legacy-L1
  label, Figure F1 + caption, Table T1, the quality-waiver paragraph, Table S1,
  the D-052/D-058 limitation language, the claims row ID, and the
  `artifact_manifest.json` link. Largest live conflict.
- **§6.2 Full-build order, steps 3–5** — "validate the six real bundles and
  regenerate dataset/aggregate artifacts; render SVG and tables". The route now
  authenticates inputs but deliberately does not extract or aggregate.
- **§6.3 Offline-build boundary** — "uses the committed sealed `dataset.csv`
  and `aggregates.json`". Those files are no longer sealed measurements.
- **§6.4 Byte-stability contract** — requires an "explicit build mode
  (`real-bundles` or `offline-derived`)". The branch writes a third,
  unenumerated `voided-placeholder` and adds two top-level fields (`status`,
  `void_reason_codes`) under the unchanged schema id
  `joulewise.report_artifact_manifest.v1`.

The claims-index side is *weaker* and needs no ruling of its own: §5.2's row
shape and §5.3's status enumeration (`supported`, `weak`, `refuted`,
`out-of-data`) are both explicitly Superseded, and §5.3 delegates current
authority to `claims_lint.py lint_claim_index`. The `voided-legacy` dialect
sits inside that delegation — but still deserves a clause, since no contract
doc anywhere now records that `voided` is a legal status.

**Remedy (~10 lines, same PR).** The vehicle exists and is named by the spec
header: `docs/specs/c027/ADJUDICATION.md` — "WHERE A RULING BELOW CONFLICTS
WITH A SPEC'S BODY TEXT, THE RULING WINS; specs are not re-edited item-by-item".
Add one RPT-001 row: under D-078 / D-161 the profile is a voided historical
demonstration, so §7's twelve-item page contract, §6.2 steps 3–5, §6.3's
sealed-artifact wording and §6.4's build-mode enumeration are amended;
`voided-placeholder` is a legal build mode and `voided` a legal claims-index
status. Do **not** edit the spec body.

## Q2 — v1 immutability

**Byte-identical.** `git diff --exit-code --stat` against `origin/main` over
`analysis/rpt001-v1` and `figures/rpt001-v1` returns rc 0 on both the two-dot
and three-dot forms. Neither tree appears in `git diff --name-only`.

## Q3 — Leakage into tracked files the profile writes

**No leak.** My independent grep over all ten tracked files the route writes
returns rc 1. The void artifacts carry only `artifact_version / artifact_id /
status / disposition`; the SVG is a 6-element notice; the manifest hashes only
void bytes; the Phase-4 projection reads `L1 / voided`.

All 30 changed files, classified (3 + 11 + 3 + 8 + 5 = 30):

- **Producer (3):** `scripts/build_capstone.py`, `scripts/make_figures.py`,
  `scripts/claims_lint.py`.
- **Generated-void (11):** `analysis/rpt001-v2/{dataset.csv, aggregates.json,
  claims_index.jsonl, artifact_manifest.json, tables/T1_*.csv, tables/T1_*.md,
  tables/S1_*.csv, tables/S1_*.md}`,
  `figures/rpt001-v2/F1_legacy_l1_instrument_results.svg`,
  `docs/phase_4/claims_index.md`,
  `docs/report_src/generated/rpt001_vertical_slice.md`.
- **Test (3):** `tests/test_build_capstone.py`, `tests/test_claims_index_lint.py`,
  `tests/test_rpt001_report_slice.py`.
- **Doc (8):** `docs/report_src/README.md`, appendices `A`/`B`/`C`, chapters
  `03`/`06`/`07`/`08`.
- **Process trace (5):** `20`–`24`.

One caveat, source not artifact: **`make_figures.py` still contains the retired
producer**. `render_figure` (lines 420–488, including the literal
`idle-subtracted energy_request_j (primary basis)` at :478), `per_stack_metrics`,
`t1_rows`, `s1_rows`, `write_dataset`, `stats3` and `T1_COLUMNS` survive
unreachable from `main()`; `extract_rows` is reached only from
`tests/test_rpt001_report_slice.py:250`. Nothing writes their output, so this is
not a leak — but it is the reopening surface a future edit would reach for.

## Q4 — Overbuild / out-of-scope

- **Not overbuild:** the `voided-legacy` dialect's exhaustive field pinning in
  `claims_lint.py` — it is what makes the supported-flip kill bite.
- **Out of scope but correct — keep:** `06_methodology.md` flipping the
  headline basis from idle-subtracted to gross. Not a new position; it repairs
  a stale chapter that contradicted the ratified one
  (`docs/decision_log.md:3711`, `README.md:72`,
  `docs/contracts/token_normalization.md:23`). Name it in the PR body so it
  does not read as a silent methodology change.
- **Housekeeping (nit):** `docs/report_src/README.md` also swapped two stale
  "not yet implemented" bullets for a PDF-renderer line. Harmless, not closure.
- **Under-removal (nit):** the dead producer code in Q3.

## Findings list

- **C1 · should-fix (landing condition).** Add the RPT-001 row to
  `docs/specs/c027/ADJUDICATION.md` amending §7, §6.2 (3–5), §6.3 and §6.4 and
  recording `voided-placeholder` / `voided` as legal values. The D-161 one-liner
  alone leaves four live spec clauses contradicted by shipped code.
- **C2 · nit.** §7 item 12 (link to `artifact_manifest.json`) was dropped from
  the page. It carries no joule value; one line restores it at zero risk.
- **C3 · nit.** Retire or annotate the unreachable value-producing functions in
  `make_figures.py`; move `extract_rows` behind its only caller, the test.
- **C4 · observation, no action.** `_voided_legacy_projection_row` sanitizes
  even the exact-legacy grandfather, so the Markdown projection intentionally
  diverges *in meaning* from the canonical v1 JSONL, while §5.3 lists
  "generated Markdown view diverging from canonical JSONL" as a hard error.
  The mechanical invariant still holds (`PROJECTION_DRIFT` compares against a
  deterministic render). Bench-verified above. Defensible belt-and-braces; give
  it one clause in the C1 entry.
- **Landing hygiene.** The branch is 14 behind `origin/main` and does not
  contain ruling `17` itself. Merge/rebase before the PR so the ruling and the
  cure land in one lineage.

## Verdict

**LANDABLE** — closure verified independently (v1 byte-identical, zero leakage
in every written artifact, lint clean, all three modules green). Land with C1
in the same PR; C2–C4 are nits and may follow.
