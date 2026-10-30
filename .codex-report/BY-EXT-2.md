# BY-EXT-2 — manifest support and resolvability kit

2026-10-30. Branch `desk/2026-10-29-byext-slots`, starting at `4119e14bf`.
Implementation commits: `b0a3ef0aa` (A), `37b6881ec` (B), both pushed.
No hardware, inference, power capture, slot fill, registration or measurement-checkout integration occurred.

## Delivered

Admitted `qwen3_5` and `qwen3_5_text`. The new test runs real `headers()` against sparse files containing all six committed shard headers and the committed config. Its independent census sums stored spans without calling `classify()`; every category and W/R compares exactly:

- embed: 1,350,860,800 bytes
- lm_head: 1,350,860,800 bytes
- always_active: 25,877,756,928 bytes
- routed_experts and shared_experts: 0 bytes each
- not_loaded: 921,460,192 bytes
- W: 27,228,623,168 bytes; R: 28,579,478,528 bytes

Added analysis identity `qwen38-27b-8bit`, role `extension_held_out`, dense, non-tier. Existing `registered_config_key()` already scans draft BYTES pack config_dirs, including bytes-s7-p1; the new test proves it resolves this identity. No registered-set addition was necessary. Extension CLI merge requires an explicit separate output and refuses the frozen manifest destination.

The registered manifest remerges byte-identically from its existing header/KV records and pilot inputs. The frozen manifest and all registered records remain untouched. Filled-state tests now recognize revision, download, hf_repo, config_model_type and group_size; manifest, resolvability and pack slots remain pending.

Created `configs/campaigns/bytes_mac_check_ext/` behind `--extension qwen38-27b-8bit`: five source absolute IDs r01..r05, split 3/2 around the midpoint, inherited corpus/start/midpoint/end references and calibration scaffold. Only this directory is generated in extension mode; no smoke-keep, registration or loop write occurs. README supplies verification, non-claim harvest and evaluation commands, plus lead-owned launch prerequisites.

The checker consumes native CSV plus matching session sidecar and measured timing receipts. It checks five succeeded, unexcluded, 512-emitted-token runs with finite positive decode duration contained in its request, rejects claim/foreign/duplicate rows, and reports runs_checked, decode_phase_s_range, verdict, member walls, stream spans, S and T_stream_max. Missing scaffold/sizing operands leave S unavailable. S uses the registered single-model-pack formula (50 science, 25 references, seven collections). Receipt and plan hashes are recorded. It never fills slots.

## Pinned cache verification

Read upstream v0.31.3 source, matching `env/mac-measurement-lock.txt`: `mlx_lm/models/qwen3_5.py`, `qwen3_5_moe.py`, `gated_delta.py`, and `cache.py` at https://github.com/ml-explore/mlx-lm/tree/v0.31.3/mlx_lm/models .

`TextModel.make_cache()` returns ArraysCache(size=2) for linear layers and KVCache for full attention. The convolution state retains kernel_size−1 positions; recurrent state has shape (B,Hv,Dv,Dk), independent of sequence length. ArraysCache.state exposes both arrays. qwen3_5_moe.Model inherits this same model/cache implementation. Existing cache_snapshot/kv_record therefore handles the 48 constant-state and 16 growing-KV layers unchanged. Actual KV values remain Mac-pending.

## Decisions I made

- Preserve source absolute run IDs and the existing corpus scaffold, including its 18-planned/12-valid stop convention.
- No soaks/test-7: the existing kit quotes R8.6 as “five structural runs per model and twelve additional soak runs for 70B/122B”; its threshold-note §4 row-7 implementation uses “two large runs at each end” for 70B, 122B and Next-80B. A 27B dense model is outside those regimes.
- Use extension_held_out and non-tier, consistent with the extension roster and registered four-bit tier definition.
- Introduce no numerical threshold or tolerance. Byte counts and synthetic arithmetic assertions use exact equality.

## Verification and limits

Python 3.13.5; JW_B5_SYNTHETIC_ONLY=1, PYTHONDONTWRITEBYTECODE=1, temporary fixtures under /tmp.

- Required three unittest modules: 39 tests, PASS.
- Extension generator --check: PASS.
- Documented check_b5_chain.py static check: clean, zero errors.
- scripts/repin.py --check: PASS, 16 families; existing sealed-inventory difference warning remains.
- git diff --check: PASS.
- Required original scripts/bytes_mac_kit.py --check: FAIL both before and after changes, at the same pre-existing check-qwen3-8b-8bit r01 config drift. Existing tests explicitly describe this kit as frozen after its inputs moved. Repair would require the protected `configs/campaigns/bytes_mac_check/`; no repair or repin was attempted.

`scripts/bytes_mac_kit.py` is a pin-registry target in family `pack_config_bytes`, referenced by the original frozen tree's /generator/sha256. That historical digest is unchanged. The other changed source/test paths are not registry targets. Treat this script change as fingerprint-sensitive; the lead must review pins before any measurement checkout integration. No out-of-scope file changed. Protected configs/bytes, configs/b6, original kit, registration and extension receipt/slot trees have empty diffs against the starting commit.

The registration text was read in the initial origin/main checkout; its named file is absent on this requested branch. BY-EXT-1 and the committed extension roster provide the local authority pointers.

Focused tooling checks were used; the repository-wide suite was not run. No PR exists for this branch; CI was not run. Mac lead next: rerun headers, collect KV, merge to an explicit separate output, then run/harvest the non-claim extension kit with the loop held and no agent alive. Fill slots only from those Mac receipts. No NEEDS_RULING was introduced.
