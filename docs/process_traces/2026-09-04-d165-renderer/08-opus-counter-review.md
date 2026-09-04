# D165-OUTCOME-RENDERER-01 — Opus counter-review (gate ledger row 6, contract lens)

Date: 2026-09-04
Seat: Opus counter-review, read-only except this file
Worktree: `/Users/edr/code/JouleWise-wt-d165-renderer`, branch
`feat/2026-09-04-d165-outcome-renderer`, head `a75c2854`
Inputs read: paper-I `06-magistrate-contract-rulings.md` (R4),
`07-magistrate-rulings-addendum.md` (R4-F1 replaced), this mission's traces
01–07, `docs/paper/results-fill-registry.md` OB-01/OR-01 (diffed against
`origin/main`), `docs/paper/fill-rehearsal/branch-selection.md`,
`joulewise/results_fill_outcome.py`, `tests/test_results_fill_outcome.py`,
`tests/fixtures/results_fill_outcome/*.json`,
`joulewise/dominance_closeout.py`, `scripts/render_results_fills.py`,
`TASK_QUEUE.md` A71/A72.

## Verdict

**LANDABLE — with one blocking consumption fence that only the magistrate can
lift.**

The seat's code faithfully implements R4 as ruled and as amended by the
replaced R4-F1. No contract regression: the frozen producers, validators, the
frozen `scripts/render_results_fills.py`, and `branch-selection.md` are
untouched, and the only registry edit is the one R4-B1 authorised. The branch
may merge.

**Fence (B-1, blocker severity, ruling-level not seat-level):** the OR-01
close-out rendering rule the registry now carries pipes an *unbounded internal
diagnostic string* into professor-facing paper bytes. I bench-verified a
rendered OR-01 containing a Python list index, an internal schema path, and a
quoted `repr`. `[FILL:OR-01]` must not be consumed until the magistrate rules
on a registered reason vocabulary. Because the defect is in the ruled contract
rather than in the seat's fidelity to it, I do not grade the seat NOT LANDABLE;
I escalate B-1 to the magistrate, per the rule that a counter-review seat does
not adjudicate blocker severity downward on its own.

Two further should-fix items (S-1 identity gate, S-2 close-out authority
asymmetry) are fences the successor mission must inherit; four nits follow.

## Executed evidence (this session, this worktree)

| # | Command / probe | Observed |
|---|---|---|
| E1 | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome tests.test_d165_dominance_closeout` | `Ran 55 tests in 12.043s` / `OK` |
| E2 | `git diff --stat origin/main...HEAD` | 22 files; sole implementation module `joulewise/results_fill_outcome.py`; sole registered-contract edit `docs/paper/results-fill-registry.md` (preamble + OB-01 + OR-01 rows only; TR-01 and every other row byte-identical) |
| E3 | Probe 1 — build `branch_b` sources, rename one `cell_id` to `Qwen3-8B beats Qwen3-1.7B by 41x (fabricated)` everywhere it is referenced, reseal, render | `OB-01` = `'Qwen3-8B beats Qwen3-1.7B by 41x (fabricated) absolute, … and synthetic-floor-1-1 comparative common-mode'` |
| E4 | Probe 2 — genuine Qwen2.5 manifest (Qwen2.5 `model.source`, Qwen2.5 tokenizer identifier, vocab 151665, fabricated tokenizer revision) with only `realized_stack_identity.model.{name,revision,family}` renamed to the Qwen3 pins; reseal; render | full eight-item `OB-01` list rendered; **no** `identity_not_v5` |
| E5 | Probe 5 — duplicate a sidecar `cell_id`, reseal, render | `OR-01` = `"at close-out: d165_replay_sidecar_invalid: sidecar.cells[1].cell_id: duplicate 'synthetic-floor-0-0'; affected: synthetic-floor-0-1 comparative common-mode"` |
| E6 | Probes 3/4 — corrupt floor-artifact bytes without resealing | build raises `floor_artifact_source_hash_mismatch`; the manifest digest seal holds (negative result, recorded for completeness) |

Probe scripts were written to `/tmp`, not to the repository. No commit, no push.

## Findings

### B-1 — BLOCKER (contract): OR-01 renders an unbounded machine diagnostic as paper prose

`joulewise/results_fill_outcome.py:633-655` (`_render_closeout_refusal`) takes
`closeout["refusal_reason"]` through `_safe_public_string`
(`joulewise/results_fill_outcome.py:74-79`), which rejects only empty strings,
newlines, and four markers. Everything else is emitted verbatim into the
Abstract, Section 7, and Section 10 Refusal paragraphs.

The value on the other side of that pipe is not an enum. It is
`_expected_global_fields`'s `source_errors[0]` or a record's
`refusal_reason` — i.e. validator diagnostic text built by f-strings at
`joulewise/dominance_closeout.py:726` (`missing keys {missing!r}`), `:728`
(`extra keys {extra!r}`), `:870` (`duplicate {cell_id!r}`), `:992`
(`block_id: duplicate {block_id!r}`), `:1031` (`invalid replay inputs ({exc})`),
`:1206`, `:1248`–`:1254` (`floor_artifact.cells[{index}]…`), `:1659`
(`d165_replay_sidecar_invalid: {sidecar_errors[0]}`), and
`joulewise/dominance_closeout.py:784` (`point_floor_parent_missing:{exc.args[0]}`,
reached through `:763` `"refusal_reason": str(exc)`).

Counterfactual (E5, executed): a close-out built over a sidecar with a
duplicated cell id renders

```
at close-out: d165_replay_sidecar_invalid: sidecar.cells[1].cell_id: duplicate 'synthetic-floor-0-0'; affected: synthetic-floor-0-1 comparative common-mode
```

into three paper placements. That string contains a **number the paper never
issued** (the list index `1`), an internal schema path, and a Python `repr`.
This is the exact question the two Sol lenses did not ask, and it also
breaches the standing plain-language rule for professor-facing surfaces
(defined terms, no internal shorthand): the registry's own
`closeout_census` oracle, `at close-out: replay_sidecar.cells: cell census does
not match floor artifact`, is already internal shorthand shipped as paper text.

The registry pins three exemplar reasons (`closeout_zero`, `closeout_source`,
`closeout_census`) as acceptance oracles, so the tests are green while the
reason *space* is unbounded — the oracles cannot detect the class.

Cure (small, and it belongs to the magistrate because it amends a registered
row): OR-01 renders from a registered `reason_code → registered plain-language
sentence` map, byte-exact in the R2 style, and returns `STOP_FILL` for any
code not in the map. Until that ruling, `[FILL:OR-01]` stays unconsumable even
after an authenticated close-out issues.

### S-1 — SHOULD-FIX: the `_v5` identity gate is three string comparisons; a renamed Qwen2.5 manifest passes

`joulewise/results_fill_outcome.py:571-599` (`_v5_manifest_model_names`) reads
only `arms[].realized_stack_identity.model.{name,revision,family}` and compares
the tuple against the two literals at `:36-47`. It ignores every other identity
field the manifest already carries — `model.source`, `model.context_window`,
`tokenizer.identifier`, `tokenizer.revision`, `tokenizer.vocab_size`,
`floor_stack_identity.tokenizer_identity`, and the `stack_identity_sha256`
derivation available from `joulewise.identity_pins`.

Counterfactual (E4, executed): a manifest whose model source path is
`/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`, whose
tokenizer identifier and vocab size are Qwen2.5's, and whose tokenizer revision
is fabricated, renders the full OB-01 below-two list once those three strings
are renamed. R4-F4 requires "a Qwen2.5 manifest returns STOP_FILL with reason
`identity_not_v5`"; a Qwen2.5 manifest with three renamed fields does not.

This is not only an adversary story: partial identity drift (a `model.name`
bumped while the tokenizer/artifact behind it was not) is an ordinary
operations failure, and the gate is blind to it. The two pinned revision
literals are also copied into the module rather than imported from a frozen
pinset, so they can drift from `tests/test_model_panel.py:58-59` and the G2-a
fixtures silently.

Test-strength corollary: the suite's own `_switch_sources_to_qwen3`
(`tests/test_results_fill_outcome.py:58-98`) *is* this rename applied to a
Qwen2.5 fixture. The F4 test therefore proves only that an *unrenamed* wrong
manifest stops — it cannot distinguish "gate checks identity" from "gate
checks three strings".

### S-2 — SHOULD-FIX: the close-out lane has no path-and-digest boundary; the cured F1 signature survives on the lane that actually renders

R4-F1 was replaced precisely so that before-comparison evidence crosses a
path + expected-digest boundary and is reopened from governed bytes
(`joulewise/results_fill_outcome.py:154-207, 400-568`). The close-out lane —
the only lane that emits professor-facing bytes today — still takes a
caller-authored `Mapping` plus three caller-authored `bytes` blobs
(`:658-673`), with no path, no external digest anchor, and no on-disk
content-addressed artifact. `validate_d165_closeout` is *self*-consistency:
every digest it checks is computed over the caller's own bytes.

Counterfactual (E3, executed): `OB-01` rendered
`'Qwen3-8B beats Qwen3-1.7B by 41x (fabricated) absolute, …'`. Arbitrary
caller-chosen text, including a fabricated numeric claim, reaches the paper
string because `cell_id` has no shape constraint anywhere in the chain and
`_safe_public_string` blocks only markers and newlines.

I do not ask the seat to re-plumb the close-out lane in this mission — the
module is fixture-only and its production output is `STOP_FILL`. I ask that the
asymmetry be written down as a **fence on RENDERER-V5-SUCCESSOR-01**: the
successor must read the three source files from governed paths with expected
digests supplied out of band, exactly as the before-comparison lane does, and
must not hand this API bytes it constructed. Without that written fence this is
a textbook ruled-not-installed candidate.

### S-3 — SHOULD-FIX: `STOP_FILL` is an in-band sentinel here and out-of-band in the frozen renderer

`scripts/render_results_fills.py:30-35` states the frozen discipline: rendered
prose goes to stdout, `STOP_FILL` goes to **stderr with exit code 2**, and "it
is never represented by a placeholder in prose." The new module inverts that:
`STOP_FILL` is a `str` in the same `dict`, under the same keys, with the same
type as a rendered sentence (`joulewise/results_fill_outcome.py:67-71,
726-731`). Nothing raises, nothing signals out of band.

Counterfactual: a successor that does
`draft.replace("[FILL:OB-01]", render_outcome_fills(...)["OB-01"])` — the
obvious call shape — publishes the literal token `STOP_FILL` into the Abstract.
`_safe_public_string` forbids `STOP_FILL` inside *rendered* values
(`:35`, `:77-78`) but cannot police the sentinel itself. The selector in
`docs/paper/fill-rehearsal/branch-selection.md` does not help: it only keeps or
deletes `[FILL:…]` markers, so the leak would occur at the later fill step
where nothing is checking.

Cure: either raise a dedicated exception for the stopped case, or document the
sentinel contract at the import seam (see N-1) so the successor's own tests
assert "stopped ⇒ nothing substituted".

### N-1 — NIT: the successor import seam is undocumented anywhere a successor will look

No contradiction exists with the frozen renderer or with `TASK_QUEUE.md` A71
(the frozen 109-key script is untouched; A71's "reads the close-out artifact
and the other governed fill sources" is compatible). But nothing outside this
mission's traces names `joulewise/results_fill_outcome.py` at all: not the
module docstring, not the OB-01/OR-01 registry rows, not A71's note. The
scout's instruction to "coordinate the future import seam with
RENDERER-V5-SUCCESSOR-01" (`docs/process_traces/2026-09-04-paper-i/01-supplier-gap-scout.md:131`)
has no landing site. Add one sentence to A71 and to each registry row naming
the module and the three seam facts: the caller supplies governed bytes (S-2),
`STOP_FILL` is in-band (S-3), and `_stop_reason` / `_secondary_closeout_reason`
are non-paper metadata.

### N-2 — NIT: the OR-01 row labels unissuable future oracles identically to live ones

The preamble added at `docs/paper/results-fill-registry.md:917-931` says the
before-comparison templates are not currently issuable and names
`whole_window_current` / `verdict_absent_current` as `STOP_FILL`. But the OR-01
row (`:937`) still lists `Acceptance oracle before_window:` and
`Acceptance oracle before_verdict:` with rendered sentences, in the same
sentence form as the three live close-out oracles, with no marker separating
future from current. A successor implementing to the row alone would build the
unissuable sentence. Mark the two as `future, blocked on
WHOLE-WINDOW-STOP-RECEIPT-01 / CLAIM-NONISSUANCE-RECEIPT-01`.

### N-3 — NIT: an undefined status token was introduced and `TOKEN_MISSING` was dropped

Beyond the ruled rendering text, the amendment changed the status column of
both rows: `TOKEN_MISSING` removed, new token `RENDERER_ISSUED` added, freeze
status reworded (`:935`, `:937`). `RENDERER_ISSUED` appears nowhere else in the
repository, the registry has no status-vocabulary legend, and no test lints
these tokens. Dropping `TOKEN_MISSING` from OR-01 also overstates the state:
its before-comparison token is explicitly *not* issuable. Either define
`RENDERER_ISSUED` where the vocabulary lives or revert to the existing tokens.
(Registry-consuming tests outside my run fence —
`tests/test_paper_round7_artifacts.py` — were not executed; see the gap list.)

### N-4 — NIT: fixture fields that are decorative or that name the removed channel

`tests/fixtures/results_fill_outcome/{branch_a,branch_b,closeout_refusal}.json`
carry `"before_comparison_sources": []`, and the two before fixtures carry
`"before_comparison_case"`. Neither key is read by
`tests/test_results_fill_outcome.py` (the B1 test at `:426-455` uses only
`builder`, `expected`, and `registry_oracles`). `before_comparison_sources` is
the name of the caller byte channel that R4-F1 was replaced to abolish — a
stale invitation to re-add it.

Related and worth stating plainly: because `builder` is `"none"` for both
before fixtures, `before_comparison_refusal.json` reaches `STOP_FILL` through
the trivial *no inputs at all* path, not through an authenticated whole-window
stop. The registered `whole_window_current` oracle is therefore satisfied by an
empty input. The real guard does exist —
`test_f1_path_chain_replays_owning_validators_but_ambiguous_result_stops`
(`:457`) plus the seat's `F1_AMBIGUOUS_STOP_MUTANT_KILLED` proof — so this is a
naming/fidelity nit, not an unguarded path.

## Lens-by-lens answers

1. **Can any rendered string contain a number, model name, or reason not read
   from an authenticated issued field?** Yes — B-1, executed. Every f-string in
   the module was traced: `:87` (`_english_list`), `:608` (`_record_label`),
   `:655` (`_render_closeout_refusal`). `_record_label`'s common-mode suffix is
   a literal and is safe: `comparative_common_mode_ratios` records always carry
   `component == "comparative"` (`joulewise/dominance_closeout.py:1134-1166`).
   The two live channels are `cell_id` (S-2) and `refusal_reason` (B-1).
2. **Did the registry amendment change any value, digest, or status beyond the
   ruled rendering text?** No value and no digest — E2 confirms TR-01 and every
   other row are byte-identical. Status *did* change: see N-3.
3. **Does the before-comparison path refuse everything but the real row schema
   bound to the log?** The chain is genuinely strict (path+digest reads with
   `O_NOFOLLOW` and per-component symlink checks `:154-207`, writer-exact
   canonical bytes and exactly-once occurrence in the bound log `:228-239,
   466-478`, prospective-manifest and plan-tree replay `:242-327`, census and
   custody joins `:330-397`, validator replay then reopen `:542-568`). I did
   **not** need to hand-build a row to reach a verdict, because *every*
   before-comparison outcome is `STOP_FILL` for both fills; the only
   observable difference between a forged and an authentic chain today is the
   presence of `_stop_reason` / `_secondary_closeout_reason`. The strength of
   this lane has no paper-visible consequence until
   `WHOLE-WINDOW-STOP-RECEIPT-01` lands, and it must be re-reviewed then.
   Recorded gap, deliberate.
4. **Which manifest fields does the `_v5` gate trust; can a Qwen2.5 manifest
   pass renamed?** Three fields; yes — S-1, executed.
5. **Could a `STOP_FILL` leak into a selected draft as literal text?** Not via
   the selector, which only keeps/deletes `[FILL:…]` markers. Via the fill step,
   yes — S-3.
6. **Does the documented import seam contradict the frozen renderer or A71?**
   No contradiction; the seam is simply undocumented — N-1.

## Verification gaps in this review

- Per the brief I ran only `tests.test_results_fill_outcome` and
  `tests.test_d165_dominance_closeout`. `tests/test_paper_round7_artifacts.py`
  reads the registry and was **not** run; N-3's status-token edit is unproven
  against it.
- I did not execute a hand-built before-comparison chain (lens 3), for the
  reason stated above.
- I did not re-run the seat's mutation harness; I relied on trace 06's
  reported kills for the eight guards and did not independently reproduce them.

## Recommended disposition

1. Merge the branch. The seat's fidelity to R4 and to the replaced R4-F1 is
   sound and the test evidence reproduces.
2. Magistrate ruling required on B-1 (registered reason vocabulary for OR-01)
   before `[FILL:OR-01]` is consumed. `[FILL:OB-01]` is unaffected by B-1.
3. Fold S-1 (identity gate breadth), S-2 (governed-bytes fence), S-3 (sentinel
   contract) and N-1 (seam documentation) into the
   `RENDERER-V5-SUCCESSOR-01` row as written acceptance clauses, so they cannot
   become ruled-not-installed.
4. N-2, N-3, N-4 are desk edits inside the already-granted registry and fixture
   scope.
