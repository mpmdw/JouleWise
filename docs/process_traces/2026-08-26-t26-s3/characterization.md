# A93/A94 executed characterization

Date: 2026-08-26  
Source HEAD: `2fd7c920314333535ea2631bec887a19b964f834`  
Python: `/Users/edr/code/JouleWise/.venv/bin/python`  
Rows: `FROZEN-RECEIPT-CONSTANT-STALE-01` (A93) and
`PACKAUTH-PRESERVE-TAUTOLOGY-01` (A94)

## Reproduction discipline

`replay-characterization.sh` exports the source HEAD with `git archive` into a
new `/private/tmp/jw-packauth-matrix.*` repository, commits that exact copy, and
runs every generator there with isolated, bytecode-disabled Python. The three
commands for each table row are exactly:

```text
/Users/edr/code/JouleWise/.venv/bin/python -I -B configs/campaigns/<PACK>/generate_configs.py --check
/Users/edr/code/JouleWise/.venv/bin/python -I -B configs/campaigns/<PACK>/generate_configs.py --check --preserve-current-frozen-bytes
/Users/edr/code/JouleWise/.venv/bin/python -I -B configs/campaigns/<PACK>/generate_configs.py --check --no-preserve-current-frozen-bytes
```

The fully expanded command, stdout, stderr, return code, and exact final line
for every invocation are under `raw/matrix/<PACK>/`. The compiled constant is
read by `ast.parse`/`ast.literal_eval`; the current receipt digest is computed
from receipt bytes and independently checked against the plan-tree reference.
Replay the matrix with:

```sh
sh docs/process_traces/2026-08-26-t26-s3/replay-characterization.sh
```

## Nine-pack matrix

In the result columns, the text after `rc=` is the exact final nonempty output
line. `PRESERVE_REQUIRED` expands to the exact line
`generation failed: the current frozen identity requires preserve mode`.

| Pack | Compiled `CURRENT_FROZEN_RECEIPT_SHA256` | Actual committed receipt SHA-256 | Match | Bare `--check` | Explicit preserve | Explicit no-preserve |
|---|---|---|---:|---|---|---|
| `d117_floor_qwen25_1p5b_v1` | `ddbbb40974c1b747516f403b3d319079519269892ee48e052a028d9f16b1e738` | `ddbbb40974c1b747516f403b3d319079519269892ee48e052a028d9f16b1e738` | yes | rc=0 `verified unfrozen draft: 100 science configs; calibration_plan_sha256=2afabe9854a8ac8c9d3d212bb0236fa787d660cf5ef452c66f2d84f97d4f227d; plan_tree_sha256=3e725c047c9850d507564e4a5131d1b65a739d2e452aab209652db05433bad6c` | rc=0, same final line | rc=1 `PRESERVE_REQUIRED` |
| `d117_floor_qwen25_1p5b_v2` | `ddbbb40974c1b747516f403b3d319079519269892ee48e052a028d9f16b1e738` | `1277103b42090f3ce41df0e030a2a5f2a3998598efec12fef812ca5b36b89666` | no | rc=1 `PRESERVE_REQUIRED` | rc=0 `verified d117_floor_qwen25_1p5b_v2 frozen by d134 receipt: 100 science configs; calibration_plan_sha256=ac7bd19fb538aa678b33d71bfbab6a0893b7ecbd6231323b9e9eebf2e30bb545; plan_tree_sha256=13dc41bb6c8de306e258c9ded6c1e050a258a6f1ce7ebf6a32574910c3c96eba` | rc=1 `PRESERVE_REQUIRED` |
| `d117_floor_qwen25_1p5b_v3` | `1277103b42090f3ce41df0e030a2a5f2a3998598efec12fef812ca5b36b89666` | `0abfddb13fe8c5e69df3e6be5e2e7efe28d3690b6947d5ed850fcb9652f6ec64` | no | rc=1 `PRESERVE_REQUIRED` | rc=0 `verified d117_floor_qwen25_1p5b_v3 frozen by d134 receipt: 100 science configs; calibration_plan_sha256=9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072; plan_tree_sha256=2b3fefc8e04c32b29b26c720643c5b2b842f332ff3e2bfbeaf4aa7adf1b954a7` | rc=1 `PRESERVE_REQUIRED` |
| `d117_floor_qwen25_7b_v1` | `a6dec2c238e5a5cb8a181ac1abd898943238c21edeb4d111ead0cd3b00df7870` | `a6dec2c238e5a5cb8a181ac1abd898943238c21edeb4d111ead0cd3b00df7870` | yes | rc=0 `unfrozen draft check passed: 100 science configs, 6 floor cells, 3 reporting cells` | rc=0, same final line | rc=1 `PRESERVE_REQUIRED` |
| `d117_floor_qwen25_7b_v2` | `a6dec2c238e5a5cb8a181ac1abd898943238c21edeb4d111ead0cd3b00df7870` | `decd8cdc6a589397e28240b33b97e1b38575be860490a2c6de31be51611842d0` | no | rc=1 `PRESERVE_REQUIRED` | rc=0 `d117_floor_qwen25_7b_v2 frozen by d134 receipt check passed: 100 science configs, 6 floor cells, 3 reporting cells` | rc=1 `PRESERVE_REQUIRED` |
| `d117_floor_qwen25_7b_v3` | `decd8cdc6a589397e28240b33b97e1b38575be860490a2c6de31be51611842d0` | `f232d076d54408851e5728b3f14e9b04e086d809bca3e1cdac0c3641e072578c` | no | rc=1 `PRESERVE_REQUIRED` | rc=0 `d117_floor_qwen25_7b_v3 frozen by d134 receipt check passed: 100 science configs, 6 floor cells, 3 reporting cells` | rc=1 `PRESERVE_REQUIRED` |
| `d117_contrast_qwen25_1p5b_vs_7b_v1` | `2ef73bf042f2f0e43d4e65fa4658f82c242269478cf68de05494456ba3d3106f` | `2ef73bf042f2f0e43d4e65fa4658f82c242269478cf68de05494456ba3d3106f` | yes | rc=0 `checked D-117 gamma unfrozen draft: decode_members=40 prefill_p256_members=40 plan_sha256=4609b74f5b1b40eb4576a1f389c5d90be3edde532bdc017314cdb300c485a218 tree_sha256=8c53a834d78c81145b8f35b25f8d50182d596dc82c171e815f8a160117ab525d` | rc=0, same final line | rc=1 `PRESERVE_REQUIRED` |
| `d117_contrast_qwen25_1p5b_vs_7b_v2` | `2ef73bf042f2f0e43d4e65fa4658f82c242269478cf68de05494456ba3d3106f` | `18855647c38ec8cf521167fcaae62a06914a8ab7087aeded96835cb418f9607e` | no | rc=1 `PRESERVE_REQUIRED` | rc=0 `checked D-117 gamma d117_contrast_qwen25_1p5b_vs_7b_v2: decode_members=40 prefill_p256_members=40 plan_sha256=cf0fe853088fe3d8c21c59359fcf3824dd2d10e539fbeba1162e00de6c297b51 tree_sha256=12ef6c10f9fa415702d0fecab90596afb5c6fedde614ee4e5b867d485a981197` | rc=1 `PRESERVE_REQUIRED` |
| `d117_contrast_qwen25_1p5b_vs_7b_v3` | `18855647c38ec8cf521167fcaae62a06914a8ab7087aeded96835cb418f9607e` | `f32bd3a8e4dbd04bc5b1635818ba34394984d1d201d16f02efc21f0b01f31c73` | no | rc=1 `PRESERVE_REQUIRED` | rc=0 `checked D-117 gamma d117_contrast_qwen25_1p5b_vs_7b_v3: decode_members=40 prefill_p256_members=40 plan_sha256=56ed0e534f102ad6e0a1da12a4e2f9856ce4fe17e9d8af546bf2323f9d70bcb5 tree_sha256=788f1a20bc5a22f073539e2d0b4df5ffd0b3e82d8b78015c7e668c0cbda8b5a7` | rc=1 `PRESERVE_REQUIRED` |

This is a generation-shaped invariant, not a family accident: ordinal 1 has
constant=current receipt and defaults to preserve/echo; each ordinal 2 or 3
constant equals its predecessor receipt and bare/no-preserve refuses. The
successor source construction at `generate_configs.py:384-394` rewrites only
`CURRENT_FAMILY_SUFFIX`, leaving the receipt constant untouched.

## Code-path findings

1. `joulewise/arm_readiness_evidence.py:1647-1669` selects projected
   authentication when `arm_attachments.identity_pin_projection.state` is
   `frozen`; otherwise it calls `_recorded_generator_check` at `:1052-1075`.
   The bare recorder runs the repository-root generator and records only the
   command, exit code, and stdout/stderr digests.
2. The projected path at `:1078-1098` and `:1387-1544` composes an anchored
   pre-projection generator check with a fenced byte replay of the U11 write
   set. The focused test
   `ProjectedPackAuthenticationTests.test_projected_pack_authenticates_through_the_composed_check`
   passed; raw output is under `raw/focused-tests/`.
3. In every current generator, `_generate` takes the preserve branch before
   the pinned external-input checks and returns. The executed
   `external-acceptance` mutation in `raw/mutations/` passed in both bare and
   explicit preserve modes. This confirms that the acceptance/policy/ledger/
   NEG8/P256 drift checks below the branch are unreachable in echo mode.
4. `freeze_aware_status` returns `FROZEN_STATUS` whenever the plan-pinned
   receipt digest differs from the compiled constant (`generate_configs.py:
   185-192`). `GenerationIdentity.__init__` then refuses a current,
   no-preserve target when either the module default preserves or target status
   is frozen (`:269-278`).

## `_v4` transition probe

`replay-v4-transition.sh` emitted an `_v4` 1.5B pack in a full-history `/tmp`
clone. Before a current receipt existed, bare `--check` returned 0 and ended:

```text
verified d117_floor_qwen25_1p5b_v4 unfrozen draft: 100 science configs; calibration_plan_sha256=f91d58ea106dd63a4497904d8f6d568ce82a06ef82b6301f96fc94494e4d06b9; plan_tree_sha256=7859cb3298335e98b7e60cd8638a535192b5b8c36ca667efa08cde818769c24b
```

Generic evidence authoring then returned PASS with all eleven kinds. This
scratch lane deliberately omitted the U11 projection receipt, so its attempted
freeze-0004 correctly returned REFUSE with
`readiness_identity_pinset_frozen_mismatch`; it is not evidence of a full
§3.2/§3.6 mint. It nevertheless created and plan-pinned a schema-valid current
receipt. After that commit, bare `--check` returned 1 with the exact preserve
message. The AST-derived `_v4` constant was the `_v2` receipt SHA
`1277103b...9666`, while the current receipt was
`e4e76207...639a`. Thus the pre-/post-receipt control-flow prediction is
confirmed. The real projected path is separately covered by the focused test
and the existing S0 estate evidence; this probe does not substitute for the
operator's real `_v4` transaction.

## Pin correction to premise 6

The generator is a committed pack member, but the claimed pins are not uniform:

* Every plan tree names a generator path and SHA. The current `_v2` and `_v3`
  generator bytes match those pins. The current `_v1` bytes do **not**: 1.5B
  pins `ea0d93...` versus current `82d263...`; 7B pins `5519b1...` versus
  current `a3f652...`; contrast pins `550035...` versus current `e6a0ac...`.
  Their governed historical-to-current deltas explicitly license modifications
  to `generate_configs.py`, `plan_tree.json`, and `plan_tree.sha256` in
  `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`.
* Each freeze receipt pins the PACK_AUTHENTICATION evidence receipt; that
  receipt pins the source SHA and the historical `pack_sha256`. These chains
  match for all nine packs (`raw/pins/generator-and-pack-pins.json`).
* No current freeze receipt contains its own final committed-pack-tree digest.
  `_v2`/`_v3` receipts contain `predecessor.pack_sha256`, which names only the
  predecessor; `_v1` has no predecessor. A receipt cannot non-circularly embed
  a digest over a tree that includes itself.
* The S5 confirmation table at `docs/process/ed-s5-mint-decision-2026-08-19.md:
  83-85` records the three final `_v3` tree digests, not all nine. The legacy
  historical-semantics pinset is the present nine-pack current-tree authority.

Therefore editing any current generator is a current committed-pack-tree
change; for `_v2`/`_v3` it also breaks the direct plan generator pin. It is not
accurate to say every current generator byte sequence is directly pinned by
its current plan tree or that every current final tree digest appears in its
own freeze receipt/S5.

## Hygiene

All generator executions and mutations occurred in `/tmp` copies. The
worktree status after each replay, excluding this authorized trace directory,
was empty. No `__pycache__` or other residue was written into a worktree pack.

