FINAL PASS: PASS

Cold final pass on `fd0b08db` (parent `784d12f1`), branch
fix/2026-10-04-v5-floor-decode-identity. Reviewer: Fable 5.1, one session, no
prior context. Checkout left untouched (`git status` clean at the end, HEAD
still `fd0b08db`). All scratch under /tmp/dd5-fable-flid/.

No blocking or major findings. Three informational notes at the bottom.

## What was checked, and how

The change is three files: one added line in each floor generator
(`"prompt_tokens": None` in the decode unit's declared workload profile) and one
new test. Both floor generators were run at the parent commit and at head, with
the same fixture pin (prefill length 2048), into separate scratch roots, and the
246 emitted files per side were compared byte for byte. The parent tree was
obtained with `git archive 784d12f1` into scratch; `joulewise/` and `scripts/`
are byte-identical between the two trees, so any output difference comes from
the generators alone.

## Question 1 — is `prompt_tokens: None` the correct declaration? YES

The freeze step compares two dictionaries for exact equality
(`joulewise/identity_pins.py:1656-1674`): the declaration written by the
generator, and the "typed projection" of each config, meaning the config parsed
into the `BenchmarkConfig` dataclass and serialized back
(`identity_pins.py:1282-1299`). The serializer keeps `prompt_tokens`,
`prompt_text` and `dataset_ref` even when they are null, and drops only five
other optional keys when null (`joulewise/schemas.py:1143-1153`; field
defaults at `schemas.py:915-918`). So a config with no prompt length always
projects to `prompt_tokens: null`, and a declaration that omits the key can
never be equal.

Evidence that null is the true value and not a cover for a real number:

- The floor decode config builder never sets the field
  (`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:1552-1561`,
  same lines in the 8B generator): the decode workload is name, repetitions,
  warmup runs, output tokens, and the prompt-suite manifest reference and hash.
- Measured on the generated head packs: in each floor, 0 of the 50 decode
  configs carry a raw `prompt_tokens` key, the typed projection of all 50 is
  `None`, and 50 of 50 equal the declaration exactly. Same 50 of 50 for the
  long-prefill unit (which already declared the field before this change). The
  two units' inventories cover 100 distinct configs per pack, which is every run
  config; the six JSON files not inventoried are the per-stage
  `order_manifest.json` files.
- A decode config that did set a prompt length cannot exist in this pack.
  Mutation M3 (below) added `prompt_tokens: 42` to the decode configs; the
  schema rejects a config that carries both a suite manifest and a prompt
  length ("identity-unit config is invalid"), so there is no reachable state in
  which the null declaration hides a set value.
- The `WORKLOAD["prompt_tokens"] = 42` constant at generator line 603 is used
  only by the condition-family definitions (lines 802, 818) and the rendering
  cross-check (line 927), never by a run config.
- The contrast generator declares the same three nulls for decode
  (`configs/campaigns/d117_contrast_v5/generate_configs.py:1568-1571`). The
  floor's own long-prefill unit already did (floor generator line 2477).
- On the parent packs, the only key by which declaration and projection differ
  is `prompt_tokens` (assertion diff in M0 shows a single differing line), and
  the real deriver `_derive_projection_units` refuses both parent packs with
  `readiness_identity_environment_dirty: identity unit 'alpha' config
  declaration differs from pack` (and `'beta'` for 8B) — the reported failure,
  reproduced.

## Question 2 — does any science config byte change? NO

Per pack, 246 files on each side; exactly four differ:

| File | Difference |
|---|---|
| `generate_configs.py` (the pack's copy of its generator) | the one added line; byte-identical to the head source |
| `producer_contract.json` | one added line, `"prompt_tokens": null`, at line 766 |
| `plan_tree.json` | the same added line (it embeds the contract) plus two SHA-256 values that hash the changed files |
| `plan_tree.sha256` | follows `plan_tree.json` |

Byte-identical on both sides: all 100 run configs per pack,
`calibration_plan.json` and its `.sha256`, the pack `order_manifest.json` and
the six per-stage ones, `extraction_spec.json`, the three condition-family
files, `decode_prompt_manifest.json`, `decode_workload_candidate.json`, the
prefill pin copies, and the README. Nothing measured, ordered, or extracted
changes; only the identity declaration and the digests that cover it.

No tracked file pins the changed digests: the only tracked file in either floor
pack directory is `generate_configs.py`, and a repo-wide search for the old
contract and plan-tree digests found nothing.

## Question 3 — does the test kill the regression? YES

The new test (`tests/test_d117_floor_qwen3_v5_generate.py:369-412`) generates
each floor, then for every config of every identity unit asserts the same exact
equality that freeze uses; then it removes `prompt_tokens` from the decode
declaration and asserts the real deriver raises the named refusal with the exact
message.

Runs (head test file copied into the scratch parent tree for the mutations):

| Case | Generators | Result |
|---|---|---|
| Head | both fixed | 1 passed, 2 subtests passed |
| M0 | neither fixed (parent) | both subtests fail at line 388 |
| M1 | only 1.7B fixed | 8B subtest fails, 1.7B passes |
| M2 | only 8B fixed | 1.7B subtest fails, 8B passes |
| M3 | fixed, but 1.7B decode configs set `prompt_tokens: 42` | 1.7B subtest fails |
| M4 | fixed, but 1.7B decode declaration says `42` | 1.7B subtest fails |
| Control | scratch tree restored to head generators | 1 passed, 2 subtests passed |

Each floor is killed independently, in both directions (declaration drifts, or
configs drift). Full file at head:
`tests/test_d117_floor_qwen3_v5_generate.py` — 22 passed, 78 subtests passed,
150 s.

## Findings

1. INFO — `tests/test_d117_floor_qwen3_v5_generate.py:384-391`. The loop uses
   plain equality, which is freeze's comparison only for units that declare a
   single suite manifest (`identity_pins.py:1657-1658`). Units that declare a
   `suite_manifest_set`, as the contrast decode units do, go through a
   different comparison (`identity_pins.py:1659-1669`). Correct for the floors
   today. If a floor ever moves to a manifest set, this loop will fail loudly
   rather than pass wrongly, so it is safe; it would just need updating.

2. INFO — same test, lines 380-411. It reaches into four private functions of
   `identity_pins`. A rename breaks the test noisily, not silently. Acceptable;
   the second half does call the real deriver, which is what gives the test its
   force.

3. INFO — coverage boundary, not a defect. The test proves the declaration
   comparison and the refusal. It does not run the rest of freeze, which goes on
   to inventory the model files and probe the runtime
   (`identity_pins.py:1746-1758`). I did not run `project_identity_pins.py
   freeze` either, to stay clear of the runtime probe. The positive end-to-end
   result therefore rests on the lead's fresh-clone check with the issued pin.
   My runs used a fixture pin at length 2048, not the issued pin; the changed
   line does not depend on the pin.

Not a finding, recorded so nobody chases it: `arm_readiness_evidence.py:2279-2290`
requires floor and contrast declarations to be exactly equal, and the v5 floor
and contrast decode declarations are not (single manifest versus manifest set).
That check is bound to the older Qwen2.5 v1 packs
(`arm_readiness_evidence.py:58-62`) and does not read the v5 packs.
