FINAL PASS: PASS

Cold, delta-limited final pass on cfd51a96 (PR #481, base b2ff2f36, previous
head c3f4ea14). Detached checkout /Users/edr/code/JouleWise-wt-dd5-rgfab2,
scratch /tmp/dd5-fable-rg2, venv python. The checkout is still clean
(`git status --short` prints nothing) after every probe below.

F1 and F2 are closed. No blocker. One finding (N1) must be closed before a
G2-b night is armed, but it does not make this merge wrong.

## Verdict by question

1. F1 closed: YES. The two shared directories are byte-identical to the base.
2. F2 closed: YES. The run-id change is fully reverted; the GAMMA window is
   back to the shape the verdict accepts.
3. Every config the `_v5` packs dispatch uses 75 s: YES (3 packs, 28
   dispatched directories, zero members at any other value).
4. Every config the one-block G2-b chain dispatches uses 75 s, when rendered
   with the opt-in: YES. Without the opt-in it does not (finding N1).
5. Every historical consumer reads unchanged bytes: YES.
6. Anything about the workload other than idle seconds changed: NO.

## Evidence

### F1 — closed

- `git rev-parse` of the two directory trees at base and head:
  `configs/campaigns/neg8_reference_corpus` is `9aca0031…` at both b2ff2f36
  and cfd51a96; `configs/campaigns/window_references` is `32b7525c…` at both.
  `git diff b2ff2f36..cfd51a96 --stat` over those two paths is empty.
- The 19 round-1 "old" hashes in `/tmp/dd5-fable-rg/hashes.tsv`, recomputed
  from the working tree: 19 checked, 0 mismatches. So the nine v1–v3 plan
  trees and six window records listed in round 1 name bytes that exist again.
- The test that failed in round 1,
  `tests/test_d117_floor_qwen25_1p5b_plan.py::test_external_inputs_are_member_level_sha_pinned`,
  passes. The round-1 workaround in `tests/test_d117_decode_contrast_plan.py`
  (rewrite 75.0 back to 30.0 before hashing) is gone: line 2260 is again a
  plain `sha256(ROOT / member["path"]) == member["sha256"]`, and that file has
  no diff against the base.
- Files changed against the base outside `*_v5/` directories: exactly five —
  `scripts/gen_g2_phase_d.py` and four test files. No doc, no historical pack,
  no file under `prefill_pin/`, `generator_inputs/`, `decode_prompt_manifests/`
  or `condition_families/`.
- `scripts/gen_g2_phase_d.py --check` prints `PASS generated Phase D matches
  pinned runbook bytes`: the tracked runsheet region still equals the default
  (historical) rendering.

### F2 — closed

- `generate_interior_references` and `INTERIOR_REFERENCE_STAGES` are deleted
  from both the source and the emitted contrast generator. The three interior
  stages are all `{"kind": "external_input", "input_id": "midpoint_reference"}`
  (`configs/campaigns/d117_contrast_v5/generate_configs.py:2280,2290,2311`).
  The pack has no `references/` directory.
- Stage graph of each `_v5` plan tree compared against the base tree
  (`/tmp/dd5-fable-rg2/tree_probe.py`): 16 stages in each, identical
  (stage id, kind, input kind, input id) sequence, and zero `launch` blocks
  differ once `_v5` is stripped from the two directory names. The only thing
  that moved is where the reference directories live.
- The GAMMA tree dispatches `window_references_v5/midpoint` three times, all
  with run id `neg8-window-midpoint`. The second and third hit the existing
  skip at `scripts/run_campaign.py:8665` ("complete bundle already exists"),
  so the claim root holds 3 start + 1 midpoint + 3 end — the base behaviour.
- Round-1 evaluator probe rerun against this checkout
  (`/tmp/dd5-fable-rg2/probe_three_midpoints.py`):

      PROBE 1 midpoints -> passed replicated_endpoints_with_midpoint [] []
      PROBE 3 midpoints -> failed invalid [...]

  The evaluator is unchanged and still rejects three midpoints; the pack no
  longer produces three. The deferral to GAMMA-INTERIOR-REFERENCES-01 is
  recorded in `tests/test_v5_pack_regen.py:89-122`, which asserts 101 roster
  rows, 99 distinct run ids, and `neg8-window-midpoint` appearing 3 times.
- F3 (asymmetric provenance) is moot: all three stages now have one shape.

Carried forward, not a defect of this change: two of the three registered
interior references are still never measured (they are skipped as already
complete). That was true at the base and is what the deferred lane owns.

### 75 s everywhere the `_v5` work dispatches

- For each plan tree, every `campaign_collection` stage's config directory was
  resolved, its `order_manifest.json` read, and each member config loaded:
  contrast 8 directories, each floor pack 10 directories; zero members with
  `sampling.idle_seconds != 75.0`.
- Every external-input pin in the three trees re-hashed from disk: manifest
  hashes match, all 19 member hashes match in each tree, and every pinned
  member reads 75.0.
- No `"idle_seconds": 30` remains under any `configs/campaigns/*_v5`
  directory; no `"idle_seconds": 75` exists under the two historical ones.
- G2-b chain rendered both ways (`/tmp/dd5-fable-rg2/chain_probe.py`). The
  opt-in rendering differs from the historical one in exactly two lines:

      REF_ROOT="$REPO/configs/campaigns/window_references_v5"
      BOUND_CONFIG_ROOT="$REPO/configs/campaigns/neg8_reference_corpus_v5"

  `BOUND_MANIFEST` derives from `$BOUND_CONFIG_ROOT`, and the four reference
  dispatches (bound corpus, `start_triplet`, `midpoint`, `end_triplet`) all go
  through those two variables. No other line of the chain names a config root.
  The roster test (`tests/test_gen_g2_phase_d.py:253-300`) now executes the
  renderer's own root assignments instead of injecting them by environment,
  which is the right fix: an environment override would have hidden a 30 s
  route.

### Workload unchanged apart from idle seconds

- `/tmp/dd5-fable-rg2/fieldcmp.py`, every modified JSON carrying `sampling`
  and `run_id`, flattened and compared against b2ff2f36: 280 member configs;
  280 change `sampling.idle_seconds` 30.0 -> 75.0; 280 change the
  `calibration-plan-sha256=` tag; zero other differing fields.
- The 19 `_v5` reference configs against their historical originals: each
  differs in `sampling.idle_seconds` only. Their hashes equal the round-1
  "new" column exactly (19 of 19), i.e. they are the same bytes round 1
  reviewed, moved to new directories.
- The seven non-config files in the two `_v5` reference directories (four
  order manifests, the settled-corpus manifest) are byte-identical to the
  originals; the two READMEs gain a three-line note and one path.
- Generators against the base: `SAMPLING` 30.0 -> 75.0 and the five reference
  path constants; nothing else. Source and emitted contrast generators differ
  only on line 21 (`EMITTED_REPLAY_INPUTS`); the two floor generators differ
  only in model identity strings and the planning seconds-per-token constant.
- Calibration plan hashes are the same as round 1 (`9128800e…`, `246af375…`,
  `75fe8d58…`); only the plan-tree hashes moved, as they must when the
  external-input paths change (`a0076ae7…`, `ebd8c160…`, `7cdf1891…`, each
  equal to its committed `plan_tree.sha256`).

### Tests and checks run

- `tests/test_v5_pack_regen.py tests/test_gen_g2_phase_d.py
  tests/test_d117_decode_contrast_plan.py tests/test_d117_floor_qwen25_1p5b_plan.py`
  -> 65 passed, 1 skipped, 65 subtests passed (178 s).
- `tests/test_d117_contrast_v5_pack.py tests/test_d117_floor_qwen3_v5_generate.py
  tests/test_run_campaign_max_blocks.py tests/test_summarize_g2a_prefill_probe.py`
  -> 111 passed, 214 subtests passed (192 s).
- `generate_configs.py --check` for all three emitted `_v5` generators: rc 0.

## Findings

### N1 — MAJOR for the next G2-b night, not blocking this merge — the 75 s G2-b route has no production caller

`scripts/gen_g2_phase_d.py:515` adds `v5_references: bool = False`. The only
callers that pass `True` are two tests (`tests/test_gen_g2_phase_d.py:232,259`).
`main()` renders the tracked runsheet without it
(`scripts/gen_g2_phase_d.py:681`), and `build_parser()` (`:627-646`) has no
flag for it. The tracked runbook still assigns the historical roots
(`docs/phase_2/window_runbook.md:1496-1497`).

Consequence: a G2-b night taken from the tracked chain as it stands would
measure one 75 s science block bracketed by a 30 s bound corpus and 30 s
references. Nothing downstream would refuse it — `scripts/run_campaign.py:3212`
notes that G2-b's bracket reference configs are not authenticated, and the
arm-readiness re-verification
(`joulewise/arm_readiness_evidence_t0.py:1749-1772`) checks the pins named in
the plan tree against committed bytes, not the directories the chain actually
dispatches. So this would be a silent departure from the 75 s ruling, not a
refused window.

Keeping the default historical is correct (it is what keeps the pinned
runsheet authenticating, and is why F1 stays closed). What is missing is the
other half: a CLI flag or a night-chain producer that passes the opt-in, and a
check at arm time that the chain's `REF_ROOT` and `BOUND_CONFIG_ROOT` equal
the directories the pack's plan tree pins. I did not find such a producer in
this repository; one may exist in tooling outside it, which I did not look at.

### N2 — MINOR — the 75 s and 30 s references are indistinguishable by identity fields

The `_v5` copies keep the originals' run ids, manifest ids, plan ids, corpus
id and the `calibration-plan-sha256=e529a062…` tag, and the order manifests
are byte-identical (`neg8_reference_corpus*/order_manifest.json` both hash to
`0ec9d68a…`) because those manifests carry no config hashes. Only the config
bytes tell the two apart. The separation therefore rests on the plan-tree
member pins and on the README instruction never to point a v5 window at a
runs root holding 30 s bundles; the skip at `scripts/run_campaign.py:8665`
keys on run id. I did not check whether that skip also compares config
hashes. Every prospective window is said to get fresh roots, so this is a
latent hazard rather than a live one.

### N3 — MINOR — bound authentication depends on two files staying identical

The drift-bound artifact is authenticated against the registered manifest at
`configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json`
(`joulewise/whole_window.py:136-143, 1625-1644`), by sha256 of the manifest
bytes. The v5 chain derives its bound from the `_v5` copy. This works today
only because the two files are byte-identical (both `74ccdaec…`).
`tests/test_v5_pack_regen.py:48-66` does assert that equality, so a divergence
would go red in the suite rather than at bound derivation during a window.
Adequate; worth a one-line comment at the constant.

### F4 from round 1 — still open, still MINOR

Every member is 45 s longer and no time budget was revisited in this delta.
Unchanged from round 1: an overrun costs a window, not a wrong number.

## Not done

- The full suite was not run; only the eight files above. `tests/test_whole_window*.py`,
  `tests/test_run_campaign.py`, `tests/test_check_window_provenance.py` and
  `tests/test_analysis_*.py` were not run in this pass.
- `scripts/check_window_provenance.py` was not run over the six historical
  window records. Its inputs are byte-identical to the base, so its result
  cannot have changed, but that is an inference, not a run. Its
  `DEFAULT_NULL_BOUND_STAGES` (`:63-75`) lists only the historical directory
  names; whether a future v5 window's provenance check needs the `_v5` names
  added was not traced.
- The membership-resolution step for a real GAMMA claim root
  (`scripts/run_campaign.py:5880-6080`) was not traced end to end; the F2
  evidence is the evaluator probe plus the unchanged stage graph.
