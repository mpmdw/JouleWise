# Executing review: R0 load reference equivalence, lane/2026-11-06-r0-load-reference

Reviewer: Opus 5.5 (independent; did not write the change). Executing review of `5cf03e598`
against `origin/lane/2026-11-05-align-pilot10-benign` (`f3af22b94`). The range has two commits:
`f1ae2d3be` (D-pin verifier, also the head of `lane/2026-11-06-v4-dpins-skip-cache`) and `5cf03e598`
(R0 load protocol change). Evidence branch: `lane/2026-11-06-r0-d-nll-diagnosis` @ `62bc719f7`.

## Verdict: ADMIT_WITH_FIXES

- No BLOCKER or HIGH.
- One MEDIUM fail-closed hole was found by an adversarial test. It is fixed on this branch with
  its test (M1).
- One MEDIUM is about the tolerance justification (M2). Admission does not depend on it, but the
  note should stop claiming that every fault moves the mean by nats.
- The new bar is strictly stronger than the old one. The old 3.0 bar always failed D. On the
  sibling it would also have passed every fault below that M2 detects or misses.

## Findings

| Sev | Where | Failure scenario | Status |
|---|---|---|---|
| MEDIUM | `joulewise/align/r0.py` `validate_references` / `reference_entry` | Suppose a table has a reference entry for revision R plus an `absolute` entry for R with `fixture_sha256: null`. Validation accepted it, because the two keys differ. Then any **unlisted** fixture of R matched the wildcard and was judged by the absolute limit. This contradicts the note's rule that the check never falls back to an absolute limit. Repro: D reference entry + `{"revision": D, "mode": "absolute", "fixture_sha256": null, "nll_limit": 20}` gave a fixture `aaaa…` with mean 5.0 a **pass**. It needs a table edit, which is hashed and reviewed, so the shipped table is not affected. | **Fixed**: a null-fixture entry must be the only entry for its revision. Test `test_absolute_wildcard_beside_reference_entry_is_never_a_fallback`. Note updated. |
| MEDIUM | `configs/align/v4/r0_nll_reference.json` `tolerance.basis`; note §Tolerance | The claim "a runtime/artifact fault … moves the mean by nats, not hundredths" is false for subtle faults. Fault injection on the 0.8B sibling (same fixture ids, R0 chunked-cache loop, sibling hf32 reference 0.4669, same 0.10/0.5 bar; table below) shows several real faults stay inside tolerance. Examples: skipping a whole middle decoder layer, logit temperature 1.2, and a ×1.5 scale on a late layer's `down_proj`. D's regime (11.06, chaotic per-token) may react differently, and it was not testable here (27B, RSS cap). | Open. Reword the basis, and either state that subtle numeric faults are out of scope or add an exact-reproduction tier (see below). Not blocking. |
| LOW | `r0.generation_verdict` | Any listed tool with schema-valid arguments passes. `called_requested_tool` is diagnostic only. The real SHADE `spam_filter_update` list has 41 tools, and 10 need no arguments, including `end_task`. So `<tool_call><function=end_task></function></tool_call>` passes. As a smoke test of render → decode → parse → validate this is fine. As evidence that D "acts on the prompt" it is weak. | Open. Consider gating on the requested tool, or at least excluding `end_task`. |
| LOW | table `anchor` entry | No R0 path uses it. `r0.PINS` holds only D, and `MlxBackend` would raise a KeyError for the anchor. Its 0.37 evidence (`anchor_control.py`) re-encodes D's decoded text with the anchor tokenizer and no anchor chat template. That is not what `load_coherence` would score for the anchor, and the null-fixture wildcard accepts any fixture. | Dormant. Fine as documentation. Re-derive it before any anchor ever runs through `load_coherence`. |
| LOW | `generation_check` vs pilots | The render path is the same: `MlxEndpoint._render_prompt`, `task.tool_schemas()` from the same `ShadeTask(pair, give_hint=True)`, and `enable_thinking=True`. The effort differs: generation uses the template default, which renders the same bytes as xhigh (WP7 LOW). Pilots use the R0-chosen effort. If R0 selects medium or low, the generation turn is not the pilots' exact effort. | Open, documentation. |
| LOW | `r0.generation_verdict` → `_accepts` | A dangling local `$ref` raises a KeyError that is not caught. The load check then raises, and the receipt records it as fail (fails closed). All 41 real SHADE schemas pass `_accepts({})` without raising. | Open, cosmetic. |
| LOW | note §Why | "Most likely post-training loss-masked these tokens" does not fit the data. Bins reach 15.86 nats, worse than uniform (ln 248,077 = 12.42), and the per-token p95 is 26 nats. Those are confidently wrong predictions, which loss masking alone would not produce. This does not affect the check: HF fp32 and mlx agree. | Open, wording. |
| LOW | prequal integration | After merge, prequal's sibling inherits D's revision, so `nll_verdict` fails against D's entry. Prequal `check_load` ignores `load.status`, so the prequal still passes and the new NLL gate goes untested there. This is the follow-up the note already lists. | Open, prequal lane. |
| LOW (pre-existing) | `tests/align/test_r0_checks.py` `patch.object(MlxBackend, "__new__")` | Running `test_r0_checks` and `test_r0_mlx` in one process raises a TypeError in `ShimTest`. Reproduced identically on base `f3af22b94`. WP7 already recorded it, and per-module CI hides it. | Not this change. |

## Fault injection (sibling `mlx-community/Qwen3.5-0.8B-8bit` @ `87e768fb`, D fixture `792beb56…ac42`)

The ids come from `records/2026-11-06-align-r0-v4-rerun` `report.json`, and their digest is checked
against the fixture. The loop is R0's 128-token chunked cache, with mlx 0.31.2 / mlx_lm 0.31.3
(venv-both). The scripts were scratch scripts and are not committed.

| Fault | Δ mean | max \|Δ bin\| | Verdict |
|---|---|---|---|
| none (R0 chunked path) | −0.001 | 0.012 | pass |
| constant logit shift +5 (softmax-invariant, harmless) | −0.001 | 0.012 | pass |
| per-vocab logit bias, sd 0.1 / 0.3 / 1.0 | 0.000 / 0.003 / 0.049 | 0.013 / 0.016 / 0.089 | pass ×3 |
| logit temperature 1.05 / 1.2 | −0.005 / −0.001 | 0.036 / 0.065 | pass ×2 |
| cache reset at target 1024 | 0.194 | 1.40 | **fail** |
| cache reset every chunk | 1.284 | 1.80 | **fail** |
| off-by-one targets | 17.2 | 19.3 | **fail** |
| skip layer 0 / 23 (first / last) | 10.6 / 2.32 | 11.1 / 2.73 | **fail** |
| **skip layer 12 (middle)** | 0.017 | 0.093 | **pass** |
| residual ×0.9 / ×0.98 at layer 0, 12, 23 | ≤ 0.023 | ≤ 0.038 | pass ×6 |
| residual noise sd 0.05 at layer 0, 12, 23 | ≤ 0.008 | ≤ 0.056 | pass ×3 |
| `mlp.down_proj.scales` ×0 at layer 6 / 12 / 18 | 0.65 / 0.67 / 1.05 | 1.28 / 1.09 / 1.83 | **fail** |
| `mlp.down_proj.scales` ×1.5 at layer 6 / 12 | 0.128 / 0.143 | 0.36 / 0.35 | **fail** |
| **`mlp.down_proj.scales` ×1.5 at layer 18** | 0.050 | 0.133 | **pass** |
| swap layers 10 and 11 | 0.459 | 0.58 | **fail** |

The bar catches gross runtime and artifact faults: wrong context or cache, misaligned targets,
grossly corrupted tensors, wrong layer order, and wrong model or fixture (by key). It misses some
subtle numeric faults. The 0.10 mean tolerance is 21% of the sibling's mean but only 0.9% of D's,
so the table says nothing direct about D's sensitivity.

A cheap way to add sensitivity: the pinned stack is deterministic. mlx on the D tensors gives
exactly the same number as a fresh 8-bit quantization (11.0356 both). After the first
qualified R0, record the production per-target losses, or their mean plus a sha. Then add a tier
that must reproduce them to about 1e-3. Every later re-run (another day, another checkout,
an offloaded copy) would then catch any runtime or artifact drift, subtle drift included. The HF
reference still proves fidelity to the model.

## Tolerance evidence: verified

- Provenance hashes match the diagnosis branch at `62bc719f7`:
  - `stream27.py` sha256 `4af4fd79…`, blob `2e400192…`;
  - `qwen38_27b_stream.json` sha256 `da18045e…`.
- `variants.hf32.start_0.per_token` (2,048 values) recomputes to mean 11.0642 and to the eight
  shipped bins exactly at 4 decimals.
- \|Δ mean\| / worst \|Δ bin\| against hf32, recomputed from the stored per-token losses:
  - mlx16: 0.021 / 0.243;
  - mlxq8 and mlxD: 0.029 / 0.255 (the two are bit-identical);
  - R0 chunked (rerun NOTE bins, 2 dp): 0.028 / 0.193.
- The tolerances (0.10 / 0.5) are 3.5× and 2× the worst healthy difference, as the note says.
- Per-token healthy differences are large (p50 0.16–0.20, p99 5.9–7.2, max 19 nats), so a
  per-token or narrow-window bar would not work in D's regime. The detection floor of a
  localized fault is k·x > 128 nat inside one bin. A test now pins this, for example 16 tokens at +8.1, or 128 tokens at +1.01.
- The fixture digest of the rerun's recorded ids is `792beb56…ac42`, matching the table.

## Silent-pass probes (all fail closed)

The probes are in `tests/align/test_r0_load_reference_adversarial.py`. Each case below fails
closed:
- NaN, inf and bool values in tolerance or reference.
- A JSON `NaN` literal.
- A NaN reference bin.
- One malformed entry (the anchor with no mode), which invalidates the whole table, D included.
- Empty losses, overflowing losses (1e306 × 2,048 → inf mean), and a single NaN or −inf.
- Revision identity must match exactly: empty, uppercase, truncated or padded revisions all give
  `no_reference`.
- A positionally reordered profile with the same mean fails `bin_outside_tolerance`.
- An explicit empty `nll_reference_revision` never falls back to the config revision.
- When the NLL and generation parts both fail, both reasons are reported.

The existing tests already cover these cases:
- a missing table;
- an unknown revision or fixture;
- the sibling borrowing D's revision;
- a missing mode;
- a duplicate key;
- a target count mismatch.

Generation probes:
- A call only inside reasoning fails.
- A dangling second envelope without the cap fails.
- An XML argument of the wrong type fails.
- JSON string-encoded arguments are decoded by the production parser and then validated, so an
  invalid inner type still fails.

## Checked and found correct

- **Greedy path.** `new_session(None, greedy=True)` builds `MlxEndpoint(sampler=None)`, and the
  endpoint stores `self.sampler` (the attribute the mismatch guard reads). With no sampler,
  `generate_turn` gets no sampler policy, which is the pinned greedy path. `temperature=0.0` and
  `seed=None` raise no flags. Every later check calls `new_session(...)` before it chats (template,
  generated, ladder → screen_episode), so the greedy session left by `load` cannot leak. A leak
  would raise anyway.
- **Real SHADE prompt.** Checked offline with the pinned SHADE snapshot (prequal cache):
  - `ShadeTask("spam_filter_update", give_hint=True)` at seed index 91 yields 41 tools, and
    `generation_target` gives `analyze_spam_patterns` (0 required, alphabetical).
  - The system prompt is `task.system_prompt("benign")`, as in the pilots (`workload.py`).
- **Envelope accounting.** The generation turn row is nested at `generation.turn`, with
  `raw_text` and `tool_calls`. The D `tool-envelopes` receipt therefore counts it. The markdown
  brief excludes it.
- **`nll_losses`.** It uses the same 128-chunk single-cache loop as before. A count check guards
  it, and `nll()` is kept as the mean.
- **Runner.** The table bytes are in `implementation_sha256`. The verdict row records the sha of
  the bytes actually read.
- **D-pin verifier (`f1ae2d3be`).**
  - Only paths starting with `.cache/huggingface/` at the model root are exempt. Similar paths
    still fail (`.cache/other`, `cache/huggingface`, `sub/.cache/huggingface`).
  - mlx_lm loads only root-level `model*.safetensors`, config and tokenizer, so nothing under the
    exempt prefix can reach the model.
  - Pinned files are still matched by size and LFS sha.
  - The branch contains the dpins lane head as an ancestor, so either merge order is clean.

## Tests run

Each command used `nice -n 15 taskpolicy -b` and `TMPDIR=/private/tmp/jwr0fix-tmp`, one module
per process. The table counts tests at the final head (after the fix).

| Module | venv-both (3.13, mlx 0.31.2) | python3.13 (homebrew) |
|---|---|---|
| tests.align.test_r0_load_reference_adversarial (new, 13) | OK | OK |
| tests.align.test_r0_load_reference (15) | OK | OK |
| tests.align.test_r0_checks (29) | OK | OK |
| tests.align.test_r0_mlx (7) | OK | OK |
| tests.align.test_r0_scheduling (12) | OK | OK |
| tests.align.test_v4_verify_d_pins (5) | OK | OK |

Before the fix, the wildcard test failed: `status: pass, mode: absolute, entry: D-abs`.
The sibling fault injection peaked well under the RSS cap (0.8B 8-bit, mlx cache limit 512 MB). No
reference regeneration was needed.

## Ultrareview target

`/code-review ultra` on the PR for `lane/2026-11-06-r0-load-reference`. It is a protocol
change to an admission bar.
