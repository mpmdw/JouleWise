FINAL PASS: FAIL

Cold final pass on c3f4ea14 (PR #481, parent b2ff2f36). Detached checkout
/Users/edr/code/JouleWise-wt-dd5-rgfable, scratch /tmp/dd5-fable-rg, venv python.
Two blockers. Both are narrow and fixable; everything about the 75 s change
itself (questions 1 and 2) checks out.

## Verdict by question

1. 75 s at the source, nothing else changed: YES.
2. Regenerated packs authenticate: YES (all three `--check` runs succeed).
3. Historical pins: BROKEN in at least one place the change did not repair
   (finding F1, blocker).
4. Run-id fix: the ids are distinct and the configs are otherwise identical,
   but the fix is INCOMPLETE: the whole-window NEG-8 verdict cannot accept the
   three interior references it now produces (finding F2, blocker for the full
   GAMMA window; the one-block G2-b chain is not affected).

## Findings

### F1 — BLOCKER — a historical member-level pin test now fails

`tests/test_d117_floor_qwen25_1p5b_plan.py:1524`
(`D117FloorQwen251p5BPlanTests::test_external_inputs_are_member_level_sha_pinned`)
fails on this commit:

    AssertionError: '08ad3cf5b1f39339cc1c226856b92e17d8d03b72397c9b366f4f56418161ef0e'
                 != '6bccecc46fe1bd093357d4aa270c19325af28084c6b5bacd0cc3cc6630dd893e'

`08ad3cf5…` is the b2ff2f36 hash of
`configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r01.json`; `6bccecc4…`
is its hash on this commit. The v1 floor plan tree pins each of the 19
reference configs by sha256, and the test recomputes them from disk.

Run: `pytest -q -p no:cacheprovider -x tests/test_v5_pack_regen.py
tests/test_gen_g2_phase_d.py tests/test_d117_decode_contrast_plan.py
tests/test_d117_floor_qwen25_1p5b_plan.py tests/test_run_campaign_max_blocks.py
tests/test_summarize_g2a_prefill_probe.py` -> `1 failed, 45 passed, 1 skipped`
(stopped at first failure, 191 s).

The change did repair the equivalent assertion for the v1 contrast pack
(`tests/test_d117_decode_contrast_plan.py:2260-2268`, which now rewrites
`75.0` back to `30.0` before hashing), so the author knew the pattern and
missed this sibling.

Extent of the stale pins (old hashes of all 19 edited reference configs still
appear, 19 lines each, in):

- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v{1,2,3}/plan_tree.json`
- `configs/campaigns/d117_floor_qwen25_1p5b_v{1,2,3}/plan_tree.json`
- `configs/campaigns/d117_floor_qwen25_7b_v{1,2,3}/plan_tree.json`
- `docs/process_traces/2026-10-02-design-block2/windows/d117-g2a-prefill-probe-20261003T0820Z/SHA256SUMS`
  and `…T1748Z/SHA256SUMS`
- `docs/process_traces/2026-10-03-design-block3/windows/d117-g2a-prefill-probe-20261004T0526Z/SHA256SUMS`
  and `…T1305Z/SHA256SUMS`
- `docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T0617Z/harvest.json`
  and `…T2252Z/harvest.json`

The new hashes appear only in the three `_v5` plan trees. So nine older plan
trees and six window records now name bytes that no longer exist at those
paths in the working tree (they remain recoverable from git at b2ff2f36).

Not verified (ran out of budget): whether `tests/test_d117_floor_qwen25_7b_plan.py`,
`tests/test_d117_v3_family.py`, the `--check` of the v1–v3 generators, and
`scripts/check_window_provenance.py` / replay verifiers over the six window
records also fail. Given the identical pin shape, assume the 7B floor test
does until run. The full suite must be run before merge.

Why this matters beyond a red test: editing the shared reference configs in
place means every earlier window's receipt points at a path whose bytes have
changed. The test edit for the v1 contrast pack papers over that by
reconstructing the old bytes with a string replace. A cleaner cure, which also
removes F1 outright, is to leave `neg8_reference_corpus/` and
`window_references/` untouched as the historical 30 s inputs and emit 75 s
copies for prospective use (new directories, or inside each `_v5` pack as was
done for the two new interior references). If the in-place edit is kept, every
consumer listed above needs the same explicit treatment, not just one test.

### F2 — BLOCKER for the full GAMMA window — three midpoint-role references fail the NEG-8 verdict

The fix gives `gamma-reference-arm-boundary` and
`gamma-reference-prefill-midpoint` their own configs
(`configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/references/*/`),
with run ids `neg8-window-arm-boundary` and `neg8-window-prefill-midpoint`.
Both new order manifests keep `"role": "neg8_daily_reference_midpoint"` and
`"sentinel_position": "midpoint"` (copied from the source row by
`generate_interior_references`, `configs/campaigns/d117_contrast_v5/generate_configs.py:1254-1287`).

The whole-window verdict classifies references by role, not run id, and
accepts exactly two shapes: 1 start + 0 midpoint + 1 end, or 3 + 1 + 3.

- `scripts/run_campaign.py:5290-5302`: `complete_replicated_trajectory = counts == (3, 1, 3)`;
  anything else with a start or end present adds `neg8_bracket_ambiguous_reference`.
- `joulewise/whole_window.py:1990-2007`: protocol is `invalid` unless counts are
  `(1,0,1)` or `(3,1,3)`; `invalid` adds `neg8_bracket_reference_invalid`.
- `joulewise/whole_window.py:3954-3958`: the offline re-derivation has the same
  `len(references["midpoint"]) == 1` requirement.

A full GAMMA window now writes 3 start + 3 midpoint-role + 3 end bundles into
`claim_runs_root`, and `gamma-whole-window-verdict` derives from that root.

Evidence (scratch probe `/tmp/dd5-fable-rg/probe_three_midpoints.py`, which
reuses `IdleAdmissionCoreVerdictTests._member/_binding/_drift_bound` and calls
`idle_admission_core_verdict(..., whole_window=True)` with benign, near-equal
energies):

    PROBE 1 midpoints -> passed replicated_endpoints_with_midpoint [] []
    PROBE 3 midpoints -> failed invalid
        ['neg8_bracket_ambiguous_reference', 'neg8_bracket_missing', 'neg8_bracket_reference_invalid']

So after roughly a full window of measurement the verdict stage would fail on
reference shape alone.

Before this change the three stages all dispatched
`configs/campaigns/window_references/midpoint` with run id
`neg8-window-midpoint`; the second and third dispatch hit
`scripts/run_campaign.py:8665` ("skipped …: complete bundle already exists"),
so only one interior reference was ever measured and the verdict saw (3,1,3).
The run-id fix is therefore right to exist — the old behaviour silently
dropped two of the three registered references — but it converts a silent
under-measurement into a certain verdict failure. It needs a matching
evaluator change (define how three interior points enter the trajectory
excursion, and accept the 3+3+3 shape) plus a test that runs the verdict over
the full GAMMA roster. `tests/test_v5_pack_regen.py:57-113` checks only that
the ids are distinct and the science fields equal; nothing exercises the
verdict.

Scope note: the one-block G2-b chain dispatches bound corpus (12), start
triplet (3), one science block (4), `$REF_ROOT/midpoint` (1) and end triplet
(3) — one midpoint, shape (3,1,3). F2 does not block G2-b. I did not trace the
membership-resolution step (`scripts/run_campaign.py:5880-6080`) end to end
for a real GAMMA root; the probe is at the evaluator, one level below it. The
two new references also carry the GAMMA plan id and plan sha while the
decode-midpoint reference keeps the window-reference plan
(`e529a062…`); whether that split matters to membership grouping is unchecked.

### F3 — MINOR — interior references are asymmetric

`gamma-reference-decode-midpoint` stays an `external_input` pinned to
`window_references/midpoint` (plan sha `e529a062…`, manifest id
`neg8-window-reference-midpoint-v1`), while the other two are `pack_manifest`
stages under the GAMMA plan (`75fe8d58…`). Deliberate ("Keep the G2-b midpoint
route"), and the test asserts it, but three same-purpose stages now have two
provenance shapes. The manifest ids of the new two are
`neg8-window-reference-midpoint-v1-gamma-reference-<stage>` and their
`ordering_note` still says "One same-condition midpoint reference", which is
no longer true of the arm-boundary reference.

### F4 — MINOR, unverified — time budgets not revisited

Every member is 45 s longer. No file under `scripts/`, `joulewise/`, `docs/` or
`configs/campaign_policies/` changed. `scripts/gen_g2_phase_d.py:30-62` sizes
the G2-a span from the producer's own 75 s, so G2-a is fine; I did not confirm
that the G2-b one-block span, the floor windows (100 members, +75 min) or the
GAMMA window (80 members + 9 references, +67 min) still fit their reserved
windows. An overrun is refused by window expiry rather than producing a wrong
number, so this costs a window, not correctness.

## What checked out

- Source constant: `SAMPLING` is 75.0 in
  `configs/campaigns/d117_contrast_v5/generate_configs.py:542`, the emitted
  contrast generator `:542`, and both floor generators `:607`. The source and
  emitted contrast generators differ only on line 21 (`EMITTED_REPLAY_INPUTS`).
  The two floor generators differ only in model identity strings and the
  planning seconds-per-token constant.
- Member configs: 299 modified configs carrying `sampling` and `run_id`
  (100 + 100 + 80 + 19). Field-by-field against b2ff2f36: all 299 change
  `sampling.idle_seconds` 30.0 -> 75.0; 280 pack members also change the
  `calibration-plan-sha256=` tag; zero other differing fields (prompts, token
  ids, lengths, output budgets, model, revision all identical).
- Pin bytes: no file under `prefill_pin/` or `generator_inputs/` is in the diff.
- No `"idle_seconds": 30` remains under any `*_v5` pack,
  `neg8_reference_corpus/` or `window_references/`.
- `--check` on committed bytes, each emitted generator, default arguments:
  - floor 1p7b: verified, 100 science configs, plan `9128800e…`, tree `6a609c86…`
  - floor 8b: verified, 100 science configs, plan `246af375…`, tree `29b756f6…`
  - contrast: checked, 40 + 40 members, plan `75fe8d58…`, tree `fa88a09c…`
- New interior reference configs differ from `neg8-window-midpoint.json` only
  in `run_id` and the plan-sha tag.
- In the first test batch, `tests/test_v5_pack_regen.py`,
  `tests/test_gen_g2_phase_d.py` (including the new 23-run-id G2-b roster
  test) and `tests/test_d117_decode_contrast_plan.py` passed before the F1
  failure stopped the run.

## Not done

- `tests/test_d117_contrast_v5_pack.py`, `tests/test_d117_floor_qwen3_v5_generate.py`,
  `tests/test_d117_floor_qwen25_7b_plan.py`, `tests/test_d117_v3_family.py`,
  `tests/test_whole_window*.py`, `tests/test_run_campaign.py`,
  `tests/test_analysis_*.py` were not run in this pass (budget).
- Fresh generation into scratch with `--no-preserve-current-frozen-bytes` was
  not run by hand; `tests/test_v5_pack_regen.py` does exactly that and passed.
