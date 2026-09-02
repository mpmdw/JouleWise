# Cold gate #3 — packet (mechanically assembled, 2026-09-01)

Two mandatory triggers fired in the same hour. Each packet lists the files a cold seat reads,
in order, plus the bench facts the magistrate measured. No magistrate opinion is included beyond
the labelled "Magistrate's proposed cure" lines, which the cold seat is free to strike.

## Packet A — dependence-sensitivity sheet: FOURTH round, same signature

Trigger: STANDING ESCALATION (two consecutive rounds failing with the same signature) — actually
four: reports 26 → 32 → 45 → 53 each certified the enumerated surfaces while the adjacent
un-enumerated surface failed (constants → delta list → CLI/anchors/cells → prose gate-outcome
words, stored fingerprint, name-existence binding). Cold gate #2 (48d §Packet 2) already
reshaped this stream once ("the sheet is the fixture"); the reshape failed with the same signature.

Read, in order (all on main unless stated):
1. `45b-RULING-dependence-delta.md` and `48d-COLD-GATE-2-verdict-40b-45b.md` §Packet 2.
2. The round-3 brief: scratchpad `run-fix-dep-3.md` (copied below as §A.1).
3. `53-terra-fix-dep-3.md` (fixer report) and `58-opus-delta-dependence-3.md` (delta: 8 survivors,
   5 of them prose gate-outcome words; rule 2 is a stored fingerprint with a 1309-string allowed
   set; rule 4 binding is name-existence; two citations at sheet :11/:13 name non-existent paths).
4. Branch `feat/2026-09-01-dependence` @ `8de7a9d7` (worktree `~/code/JouleWise-wt-dependence`):
   `docs/paper/round7/dependence-sensitivity.md`, `scripts/dependence_sensitivity.py`,
   `tests/test_dependence_sensitivity.py`.

Question for the seat: is another enumerated-surface round the right spend, or is the mechanism
wrong? Magistrate's proposed cure (strike if wrong): **the script RENDERS the sheet** — every
number, every gate-outcome word ("passes"/"fails"), every command line and its claimed stdout
fragment come from `scripts/dependence_sensitivity.py --render-sheet`, and the ONE test asserts
`docs/paper/round7/dependence-sensitivity.md` is byte-equal to the rendering; hand-written prose
lives in a template whose slots are filled from the payload, so there is no hand-typed number or
outcome anywhere. Rule 3 (draft anchors) and rule 4 (refusal rows) stay as tests. Citations by
function name resolved by AST at render time. Decide: RESHAPE to that / a different reshape /
ROUND 5 as enumerated.

## Packet B — TRANSFER-FIDUCIAL-01 receipt inventory: SECOND round on the same defect

Trigger: second fix round on the same defect (import-closure over-freeze). Round 1 (Sol, report
~38?/42 delta) walked transitive imports → 62/85 modules → cold gate #1 (48c §Packet 1) reshaped to
a curated list + execution-closed drift test. Round 2 (luna, `50-luna-fix-fiducial-2.md`,
branch `feat/transfer-fiducial-01` @ `a7a2917c`, worktree `~/code/JouleWise-wt-fiducial`)
implemented that — and the trace captured the LAZY IMPORT CLOSURE as "execution": the inventory
grew to 24 modules including `adapters/mock_runtime.py`, `adapters/mock_telemetry.py`,
`adapters/mock_spec_runtime.py`, `suite.py`, `bundle.py`, `cooldown_anchor.py`, … Receipts are
non-reissuable after data, so an edit to a mock adapter now invalidates a receipt: the deadlock
in miniature.

Bench facts (magistrate, this checkout, `sys.settrace` on `transfer_fiducial.fit_run` over the
synthetic fixture bundle, counting a module when any frame in it receives a `call` event):
- trace as luna's test runs it (lazy imports unresolved): 20–24 modules, ORDER-DEPENDENT (the
  set depends on what the process imported earlier; the drift assertion is `⊆`, so it never fails
  when the set shrinks — the fence is not reproducible).
- trace with `joulewise.bundle_read`, `joulewise.adapters` (package), `joulewise.schemas`,
  `joulewise.adapters.powermetrics` imported BEFORE tracing: **7 modules** —
  `adapters/powermetrics.py`, `authentication_io.py`, `bundle_read.py`, `powermetrics_fiducial.py`,
  `transfer_fiducial.py`, `uncertainty_evidence.py`, `validation.py`.
  Of the ruled starting eight, `clock.py` never executes on this path and `schemas.py` executes
  only on a branch at `transfer_fiducial.py:1312`.
- lazy imports at `transfer_fiducial.py:364-365, 1312`.

Read: `42b-RULING-fiducial-delta.md` (with its cold-gate section), `48c-COLD-GATE-1-verdict-42b-36b.md`
§Packet 1, the round-2 brief (scratchpad `run-fix-fiducial-2.md`, §B.1 below), `50-luna-fix-fiducial-2.md`,
and on the branch `joulewise/transfer_fiducial.py:47-83,205-243`, `tests/test_transfer_fiducial.py:339-474,574-620`.

Question for the seat: define "closed by execution" so it is reproducible, and rule the inventory.
Magistrate's proposed cure (strike if wrong): the drift test pre-imports the whole `joulewise`
package tree (`pkgutil.walk_packages`) before tracing so only function-body execution counts;
inventory = the 7 runtime modules ∪ the ruled `clock.py`/`schemas.py` (9), mocks and `bundle.py`
struck; contract states the definition. Also rule whether this is a third round for the fiducial
fixer or a bench edit (the change is the pre-import block + the constant + contract sentence).
### A.1 round-3 brief (dependence)
ORIGIN: claude-code lead (Fable magistrate), JouleWise repo, worktree `feat/2026-09-01-dependence` @ `35716229`.
HOP: 1 (you must not call Claude by MCP, `claude -p`, or any launcher).
GENRE: implementation — dependence-sensitivity sheet fix round 3, under ruling `docs/process_traces/2026-09-01-fresh-model-review/45b-RULING-dependence-delta.md` AS AMENDED by its "## Cold-gate verdict" section (binding) and `48d-COLD-GATE-2-verdict-40b-45b.md` §Packet 2.

WRITE_SCOPE: ["docs/paper/round7/dependence-sensitivity.md", "scripts/dependence_sensitivity.py", "tests/test_dependence_sensitivity.py"]

`docs/paper/draft-v1.md` is FROZEN (read-only anchor target). No `git rebase`/merge. Leave the tree dirty; the lead commits.

## Why this round exists (read, then internalise)
Three rounds on this stream (reports 26 → 32 → 45) each certified the ENUMERATED surfaces while the next un-enumerated surface failed (constants, then the delta list, then the CLI line / draft anchors / table cells / meta-test direction). The documented R7 command at sheet :97 exits 2, and its `tr -d '\\140'` inside single quotes also deletes the digits 0/1/4 from the data. Report 37 certified a RE-TYPED command, not the sheet's. This round replaces enumeration with a RULE.

## THE RULE — "the sheet is the fixture" (implement as tests; this is the acceptance)
1. **Every fenced/indented command line in the sheet is extracted by the test (regex over the doc) and executed via `subprocess` from the worktree root, verbatim, never re-typed.** Each must exit 0 and its stdout must contain the outcome the surrounding prose claims (e.g. `"direction_gate_outcomes_agree": false` for the :97 command). 
2. **Every number in the sheet — prose and table — is matched to a rendered field of the script's output** (or to a declared input constant). Parse the three worked-example table rows and every numeric token in the replication paragraphs; assert each equals the corresponding rendered value at the sheet's stated precision. Numbers that are inputs (the ten deltas, floor 3.5, se_metrology 0.2, etc.) match the script's constants.
3. **Every `draft-v1.md` line anchor in the sheet is resolved**: the test opens the frozen draft at that line and asserts the named sentence (or its first ~40 characters, quoted in the sheet) is on that line. Fix A2 now: rows DS-SENS-02 / PG-SENS-02 anchor line 294 (the Limitation 1 sentence), not 292 (the heading).
4. **The refusal-row set is asserted two-way**: the mandated set of row names is asserted EXACTLY (no extra, no missing), and each row binds to a source site in the script.
5. **Every bracketed ten-number list in the sheet equals `EXAMPLE_BLOCK_DELTAS_J`** (cold gate 32 Q4.4 "one list", enforced by test).

## Content cures
- **A1 cure (ii)**: rewrite the :97 command to print the literal list — `--block-deltas '[5.0, 7.6, 5.5, 4.2, 4.7, 6.8, 5.5, 3.6, 3.9, 3.2]'` — drop the grep/cut/tr pipeline entirely. Rule 1 then executes it.
- **C1**: print the two-sided tail formula `p = I_x(ν/2, 1/2)` with `x = ν/(ν + t²)`, gloss `I_x` in plain words (the regularized incomplete beta function: the fraction of a Beta(ν/2, 1/2) distribution's probability lying below x), print the three worked x values (`0.078307034361`, `0.057315253936`, `0.064651302005`) so each printed p replays with any library, and name the implementing routines: `joulewise/analysis_engine/distributions.py:166` (`two_sided_student_t_p_value`, Lentz continued fraction at :49-115) and `:131` (`student_t_quantile`, behind 2.262 / 2.776, rounded to 3 dp at `scripts/dependence_sensitivity.py:194`, documented at sheet :35). Verify each line number at HEAD and cite by FUNCTION NAME (line numbers in parentheses only).
- **C2**: two-sentence Holm summary at first use (:11). **C3**: one sentence each for `KEY_FROZEN`, `VALUE_UNISSUED`, "insertion anchor".
- **Missed 2**: at sheet :11 drop the generator LINE numbers (1859, 2578) — cite field names (the `multiplicity` block / `alpha`) per cold gate 32 Q4.2.
- **Missed 4**: one clause at :79 noting "critical value 2.262000" is the 3-dp quantile rendered at 6 dp, and which precision entered the half-width.
- **A3**: covered by rules 2–3 (no per-item enumerated assertions needed beyond the rule's implementation).
- **B1, B2**: covered by rules 2 and 4.

## Acceptance
A mutation table with ZERO survivors across the four surfaces: (i) change any digit in a sheet number → a test fails; (ii) change any command line in the sheet → a test fails; (iii) change any draft anchor line number → a test fails; (iv) delete or add a refusal row → a test fails. Run it, paste it. The delta seat will re-run it.

Verification of documented commands by you: `sed -n '<N>p' docs/paper/round7/dependence-sensitivity.md | bash` (or the extraction the test uses), stdout pasted — never re-typed.

## Writing standard (binding)
First-use test on every added term; replication bar; no word does unpaid work.

## Verify (paste tails)
- `python3 -m unittest tests.test_dependence_sensitivity tests.test_paper_terms_lint`
- the `sed | bash` replay of the :97 command (post-fix line number) with its stdout
- `git diff --check`; `git status --short` (only WRITE_SCOPE paths dirty)

## Report
`claude-codex-report/v1` envelope. Findings: rule → test name(s) → mutation-table rows; content cure → sheet line. Any number you cannot source → NEEDS_RULING; never invent one.

### B.1 round-2 brief (fiducial)
ORIGIN: claude-code lead (Fable magistrate), JouleWise repo, worktree `feat/transfer-fiducial-01` (PR #239, HOLD MERGE) @ `aa2a7d89`.
HOP: 1 (you must not call Claude by MCP, `claude -p`, or any launcher).
GENRE: implementation — TRANSFER-FIDUCIAL-01 fix round 2, under ruling `docs/process_traces/2026-09-01-fresh-model-review/42b-RULING-fiducial-delta.md` AS AMENDED by the cold-gate verdict appended to it (read the whole file, including "## Cold-gate verdict" — the amendments override the table where they conflict) and `48c-COLD-GATE-1-verdict-42b-36b.md` (packet 1).

WRITE_SCOPE: ["joulewise/transfer_fiducial.py", "tests/test_transfer_fiducial.py", "tests/test_transfer_fiducial_v2_plan.py", "docs/contracts/transfer_fiducial.md"]

Nothing else. No `git rebase`, no merges, no edits under `runs*/`, `docs/paper/draft-v1.md`, or any config directory. Do not touch `scripts/`. Commit is done by the lead — leave the tree dirty.

## Context you need (read first, in this order)

1. `docs/process_traces/2026-09-01-fresh-model-review/42b-RULING-fiducial-delta.md` (ruling + cold-gate amendments).
2. `docs/process_traces/2026-09-01-fresh-model-review/48c-COLD-GATE-1-verdict-42b-36b.md` §Packet 1 and §Missed (42b).
3. `docs/process_traces/2026-09-01-fresh-model-review/42-terra-delta-fiducial.md` (the delta report whose findings you are curing: A2, B1, C2, C1-line, A3).
4. `joulewise/transfer_fiducial.py` (esp. `issue_pre_data_receipt` ~:940-1050, `fit_run` :284-300, `build_capture` :1185+, `TRANSFER_FIDUCIAL_PRE_DATA_RECEIPT_SCHEMA` :47-49, `expected_keys` :1001-1011).
5. `joulewise/calibration_bracketing.py:180-186` — `ESTIMATOR_CODE_PATHS`, the existing curated-closed-list pattern to imitate.
6. `docs/contracts/transfer_fiducial.md` (esp. :53-55 and :251-257).

## Items (all mandatory; each names its regression)

### A2 — closed, CURATED receipt source inventory (cold-gate cure; the transitive-import walk in the 42b table is OVERRULED — do not implement it)

Forcing problem: the pre-data receipt digests `fitter_module_source` + `estimator_source` only; `uncertainty_evidence.py` and `schemas.py` change the verdict without changing the receipt. A transitive import walk over-freezes (the closure from `transfer_fiducial` + `powermetrics_fiducial` reaches 62 of 85 `joulewise/` modules through `bundle_read → … → cli`) and creates a deadlock: an unrelated edit invalidates a receipt that `issue_pre_data_receipt` refuses to reissue after data.

Cure:
- Add `RECEIPT_SOURCE_MODULES: tuple[str, ...]` in `joulewise/transfer_fiducial.py` — a hand-curated closed list of repo-relative paths, exactly:
  `joulewise/transfer_fiducial.py`, `joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/clock.py`, `joulewise/schemas.py`, `joulewise/validation.py`, `joulewise/adapters/powermetrics.py`, `joulewise/bundle_read.py`.
  If one of these does not exist at HEAD, say so in the report and drop it; if the execution-trace test (below) shows a further `joulewise/` module executing during the fixture fit, ADD it and say so — the trace is the authority, the list above is the starting point.
- The receipt records one `sha256` per inventory path under a new closed mapping (e.g. `source_inventory: {<path>: <sha256>}`) and records the inventory's own canonical digest. Keep `fitter_module_source` / `estimator_source` only if they remain meaningful; if you remove or rename keys, the closed `expected_keys` set changes accordingly.
- Bump `TRANSFER_FIDUCIAL_PRE_DATA_RECEIPT_SCHEMA` (new version string). A receipt carrying the old schema string must be refused BY NAME (`pre_data_receipt_schema_unsupported` or the existing naming pattern), not by a key-set mismatch. Regression: feed an old-schema receipt → exact reason.
- Each inventory mismatch at verification time refuses with the existing `pre_data_receipt_*_source_sha256_mismatch` pattern naming the module path. Regression: ONE mutation test per inventory module (write a temp copy? no — monkeypatch the digest reader or the recorded hash so the test does not edit tracked files) asserting the exact reason names that module.
- Drift test (closed by execution): run the ONE end-to-end fixture fit (see C2) under `sys.settrace` (or `sys.monitoring` / `trace`), collect every file under `joulewise/` that executes at least one line, and assert that set ⊆ `RECEIPT_SOURCE_MODULES`. Failure message lists the missing module names. Also assert the inventory has no duplicates and every path exists.

Timing note for the contract: the fence closes before the FIRST RECEIPT ISSUANCE (receipts are not reissuable after data), and the contract must say so.

### B1 — runtime-ids mismatch test asserts the named reason
`prefill_prompt_pin_runtime_token_ids_mismatch` must be asserted on stderr (or the returned reasons list), not exit status alone.

### C2 — suite cost
Keep exactly ONE end-to-end detector test that runs a real capture through `fit_run`. Every receipt-only source/hash mutation test uses a fixture `fit_run` (monkeypatched, or a capture built once per module via a cached fixture). Target: `python3 -m unittest tests.test_transfer_fiducial tests.test_transfer_fiducial_v2_plan` under 60 s. Report the measured wall time.

### C1 — one-line contract correction (no re-sequencing)
`docs/contracts/transfer_fiducial.md:251-257` asserts "No flag below is marked UNVERIFIED" while omitting the seven producer flags (`--config-root --input-inventory --runs-root --counts-output --summary-output` of `scripts/summarize_g2a_prefill_probe.py`; `--selection-record --summary --prompt-ladder --ruling-trace --output` of `scripts/issue_g2a_prefill_prompt_pin.py`). Add them, marked: "verified against `feat/2026-09-01-g2a-probe` @ `82e7519d`; absent from this branch until that branch merges". Also: soften `transfer_fiducial.md:53-55` — the generator's check is a regex SHAPE check until the ruling-39b construction check lands; say exactly that.

### A1 — record only (deferred)
Add to the contract's Sequencing note: pin→ladder binding (ruling 39b loader) lands in the post-probe-merge round; the deferral reason is sequencing (loader absent on this branch, no data, merge held), NOT threat model — the ladder is the pre-registration record and the check sits inside D-161's fail-closed carve-out. State that the run-time re-tokenization is retained because it is the only fence across the two tokenizer loader paths (issuer: `transformers.AutoTokenizer`; generator/runtime: `mlx_lm.load`). Note that the post-merge round's WRITE_SCOPE must include the plan generator and `tests/test_transfer_fiducial_v2_plan.py` (the 39b loader signature changes).

### A3 — record correction
Nothing to implement; do not rewrite trace files.

## Writing standard (binding for every contract sentence you add)
A reader should be able to REPLICATE the mechanism from the text alone. Every term of art ("receipt", "inventory", "closed by execution", "fence") is built from physical reality or glossed in plain words at first use, or deleted. Give the forcing problem and a concrete example (e.g. "an edit to `uncertainty_evidence.py` on the day after the receipt is issued changes `se_metrology` but not the receipt — the receipt no longer identifies the program that fit the data").

## Verify (run all, paste tails)
- `python3 -m unittest tests.test_transfer_fiducial tests.test_transfer_fiducial_v2_plan` (with wall time)
- `python3 -m unittest tests.test_powermetrics_fiducial tests.test_calibration_bracketing tests.test_paper_terms_lint`
- `git diff --check`; `git status --short` (only WRITE_SCOPE paths dirty)
- The mutation table: for each inventory module, the exact refusal reason observed.

## Report
`claude-codex-report/v1` envelope. Findings table: item → what changed (file:line) → regression name → observed tail. State explicitly which inventory modules were added/dropped and why (from the trace). Flag anything you could not do inside WRITE_SCOPE as NEEDS_SCOPE with the exact path — never widen scope yourself.
