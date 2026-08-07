# Opus 5 examination — DRAFT-QUANT_GATES / DRAFT-MOE_GATES (v2, complete files)

Date: 2026-08-07. Repo ground truth: `scratchpad/desk` @ `3b3e2e1` (main, up to date).
Plans extracted from the final message echo after the last `tokens used` marker:
QUANT = `DRAFT-QUANT_GATES.md:23824-24327` (504 lines), MOE = `DRAFT-MOE_GATES.md:5701-6067` (367 lines).
Both are complete final plans; the truncation that voided the prior examination is gone.

---

## 0. Carried facts — confirmed / corrected

| Carried fact | Status |
|---|---|
| `schema_v2` pins exactly 2 producer plans and 4 cells/transport groups; a 3-rung ladder is unmintable without a schema_v3; touches U3's file set | **CONFIRMED AND WORSE.** At `origin/impl/d117-u3-pinset-v2` (`dea7c87`), `scripts/floor_mint_pinsets/schema_v2.json` pins `producer_plans` 2/2, per-component `cells` 2/2, aggregate `cells` 4/4, `transport_allowlists` 4/4, `component_artifacts` 2/2. The same literals are hardcoded in `scripts/mint_floor_artifact_generalized.py` (579, 696, 837, 839, 879, 904, 2695) **and in the consumer `joulewise/detection_floor.py`** (1660, 1671-1672, 1707, 1900-1914), which additionally requires `set(roles) == {"decode","prefill"}` per component (1893) and pins `consumer_floor_rule == "cross_stack_armwise_max.v1"` as a const (1672). A three-**decode**-cell aggregate violates cardinality *and* the decode+prefill role pairing. U10 ("postcollection pin closure", sequential after alpha and beta pass) writes `scripts/floor_mint_pinsets/*_v2.json` and `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.json`. |
| MoE interception at `models/qwen3_moe.py:110-140`, `inds` ~L131, not `qwen3_next.py` | **CONFIRMED EXACTLY.** `Qwen3MoeSparseMoeBlock` L110; `self.top_k` L117; `norm_topk_prob` L118; `gates` L127-128; `inds = mx.argpartition(...)` L131; `scores = mx.take_along_axis(...)` L132; normalization L133-134; `y = self.switch_mlp(x, inds)` L136. |
| `Qwen3-30B-A3B-4bit` not local; ~28 GiB free on a 97%-full disk; a cache-then-mirror needs ~34 GB and would fail | **CONFIRMED (artifact + disk); the doubling risk CORRECTED for this plan.** `df`: 28 GiB avail, 97% on `/System/Volumes/Data`. Not in `/Users/edr/jw_models` nor `~/.cache/huggingface/hub`. `Qwen3-4B-4bit` local, 2.1 GB, revision `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25` — matches the plan's table. **But** the plan uses `hf download --local-dir`, which at hub 1.22.0 stages into `local_dir/.cache/huggingface/download/` and renames into place on the same filesystem — no cache-then-copy transient doubling. The doubling hazard applies to a `snapshot_download`-then-mirror protocol, which this plan does not use. The *second* mirror (another 17.2 GB) remains impossible on this volume. |
| `mlx_lm.convert` at 0.31.3 has no `--revision`; any `--hf-path/--revision` protocol is unexecutable; `--dtype bfloat16` and `-q --q-bits 8 --q-group-size 64 --q-mode affine` are valid | **CONFIRMED (`revision` is a Python kwarg only, `convert.py:94,114`; absent from the CLI parser at 189-250). The QUANT plan does NOT commit this error** — it resolves the SHA via `HfApi().model_info(...).sha`, downloads with `hf download --revision`, and passes the local snapshot dir to `--hf-path`. That is the correct workaround. All other flags valid; `--quantize` long form exists (`-q, --quantize`). |
| Sizing must be ≥3× a PROJECTED floor from the one measured precedent (13.998 J comparative on a 192.386 J member mean = 7.3%), not the generic ~5 J bar | **CONFIRMED** at `docs/decision_log.md:5290-5291`, `rev-moe-routing-energy.md:134,304`. **Neither plan applies it.** QUANT Gate 2 fires `Go` at 1×; MoE has no sizing gate at all in DG1-DG4. |
| MoE needs independent floors for all THREE arms (k=8, k=4, dense) under `cross_stack_armwise_max.v1`; an instrumented runtime is a new stack identity needing its own floors | **CONFIRMED.** The MoE plan *does* carry the new-stack-identity rule correctly ("do not inherit any stock-runtime floor"), and its DG2 timing probe covers dense/k8/k4. It does **not** carry the three-arm mint/consume blocker, and its night budget is sized for two. |

### New verified fact (decisive for QUANT)

Alpha's Q4 artifact `/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit/model.safetensors`
stores **every non-quantized parameter as `F16`** (e.g. `model.layers.0.input_layernorm.weight F16 [1536]`;
`scales`/`biases` `F16`; packed `weight` `U32`), header `__metadata__ = {'format': 'mlx'}`, 732 tensors,
no `lm_head` (tied). Its `config.json` carries `"quantization": {"group_size": 64, "bits": 4}` with
**no `"mode"` key**. `mlx_lm 0.31.3` `quantize_model()` writes
`quant_params = {"group_size":…, "bits":…, "mode": mode}` unconditionally (`utils.py:814,821`).
The plan converts all three rungs with `--dtype bfloat16`.
**Byte-identity with Alpha's Q4 is therefore impossible by construction, on two independent grounds,
before converter-version packing differences are even considered.**

---

# Plan 1 — DRAFT-QUANT_GATES.md

## VERDICT: **REWORK** (bounded — the rework spec is A1-A8 below; the receipt discipline, D-016 rider shape, and three-cell composition design survive intact)

Grounds: the plan has exactly two kill gates and **neither can return a decision.**
Gate 1 cannot pass (its `PASS` list requires a byte-identity that the on-disk evidence forecloses).
Gate 2's most likely branch is "Hold for Ed" (below). A gate that cannot fail is broken; a gate that
cannot pass is equally broken. Fixing them changes the plan's headline night count, which is a
portfolio number in `ADJUDICATION.md` — so this is not an amendment-in-place.

Everything else is strong: the provenance/receipt machinery is the best in the corpus, the D-016
narrow-rider framing is right, the model choice (1.5B not 7B) is right, the referee's quality-gate
deletion is honoured verbatim (§2.2: "No internal accuracy or quality-equivalence claim under D-041"),
Holm `m=2` is correct, `F_ij = max(F_i,F_j)` matches `cross_stack_armwise_max.v1` semantics, and
the reserve night the referee demanded is present.

## Amendments

**Q-A1 — Replace the `FAIL_ALPHA_TRANSPORT` byte-identity criterion; it is a determined outcome, not a risk.**
Evidence (verified 2026-08-07 against the on-disk artifact and the installed converter):
(i) Alpha stores non-quantized params as `F16`; the plan converts with `--dtype bfloat16`.
(ii) Alpha's `config.json` quantization block has no `"mode"` key; 0.31.3 always writes `"mode": "affine"`.
(iii) Alpha's documented converter is `mlx-lm 0.18.1` and it records **no** upstream source revision, so
input-weight identity is unverifiable in principle.
Replace the single pass/fail with a three-way verdict:
- `Q4_EQUIV_STRICT` — every quantized tensor (packed `weight` `U32`, `scales`, `biases`) is **bit-identical**
  to Alpha's, and all remaining differences fall inside an enumerated metadata allowlist
  `{quantization.mode, transformers_version, non-quantized-parameter dtype}`. Testable only if Gate 1 adds a
  **fourth conversion at `--dtype float16`** to match Alpha's lineage. Add it.
- `Q4_EQUIV_NUMERIC` — strict fails, but both artifacts emit identical output-token SHA-256 on the frozen
  128/512 workload and identical logits to a preregistered tolerance.
- `Q4_DISTINCT` — neither holds.
Only `Q4_EQUIV_STRICT` permits reusing Alpha's minted Q4 floor. The other two require a third fresh floor night.

**Q-A2 — Put the four-night branch in front of Ed BEFORE Gate 1 spends anything.**
§6 Q1 currently frames it as a contingency. On Q-A1's evidence it is the **expected** branch. The packet must
present: (a) the three-night ladder, conditional on `Q4_EQUIV_STRICT`; (b) the four-night one-lineage ladder
(BF16 + Q4 + Q8 floors, one source SHA, one converter) as the default; and (c) an explicit note that
`ADJUDICATION.md`'s "P2 quantization BF16/Q4/Q8 | 3 nights" row is being amended. Do not let a 2-hour smoke
be the discovery mechanism for a portfolio-level number that is knowable today.

**Q-A3 — Move the four-hour occupancy projection from Gate 2 to Gate 1, and compute it in the plan.**
Gate 1 already measures per-rung 128/512 durations at 01:25-01:50. Combined with DESIGN-MEMO's published
Alpha structure (1.5B decode member 92.7 s, n=40; campaign subtotal 147 min; base occupancy 157 min;
×1.2 = 188.4 min), `T_50` for BF16 and Q8 is computable at Gate 1 — before the D-016 ruling, before the
Alpha night, one to two months earlier than Gate 2 as scheduled. Add the same computation for the
**60-member contrast window**: Gamma's 40-member baseline is subtotal 130 / base 140 / ×1.2 = 168 min, so
60 members plus the slower BF16 arm lands near 3.5-3.7 h. §4 asserts the 20%-margin launch rule for that
window but never evaluates it — evaluate it at Gate 1.

**Q-A4 — Apply the referee's ≥3× rule to Gate 2's `Go` criterion.**
`Go: C_near > B_48,hi` is 1× the projected bar. `rev-moe-routing-energy.md:304` requires
"≥3× the projected floor for this cell", projected from the one measured precedent
(7B comparative floor `13.998036715259254` J on absolute-cell member mean `192.38623252628366` J = 7.3% of
member energy), stated as a range. Replace with `Go: C_near > 3·B_48,hi`; the hold band becomes
`B_48,hi < C_near ≤ 3·B_48,hi`; and Ed's decision rule for that band is pre-registered in the D-016 packet,
not deferred to the gate (§6 Q5 currently defers it).

**Q-A5 — Add a precision precondition to Gate 2, or it cannot return a verdict.**
With five off-window ABBA blocks the diagnostic interval will be wide, so `C_far` will exceed `B_48,lo`
(no Kill) while `C_near` will be small or zero (no Go). "Hold for Ed" is the near-certain branch, which
makes Gate 2 a consultation, not a kill gate. Add:
`FAIL_PRECISION` if the diagnostic half-width exceeds `F_4` — the probe is then uninformative, and either
the block count rises prospectively or Gate 2 is declared non-decisive and the Q4-Q8 arm is pre-registered
as a published refusal.

**Q-A6 — Re-gate the schema work on U10 CLOSED, not "U3 merged and stable", and name the consumer file.**
§4's finding is right but incomplete: it inspects `schema_v2.json` only. The identical cardinalities are
hardcoded in `scripts/mint_floor_artifact_generalized.py` **and in `joulewise/detection_floor.py`**, which also
requires `set(roles) == {"decode","prefill"}` per component (L1893) and pins `cross_stack_armwise_max.v1`
as a const (L1672). So the plan's "Reject prefill cells / three decode cells" design cannot be consumed
without a new branch inside `detection_floor.py` — U3's exact file set — and U10 rewrites
`scripts/floor_mint_pinsets/*_v2.json` and `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.json`
only *after alpha and beta pass*. Change dependency-table row 7's precondition from
"U3 merged and stable" to **"U10 closed (post-beta)"**, and add a hard rule: no P2 commit may touch
`scripts/floor_mint_pinsets/**`, `scripts/mint_floor_artifact_generalized.py`, or `joulewise/detection_floor.py`
while any D-117 window is unfired.

**Q-A7 — Add the internal-validity caveat the referee demanded.**
`rev-quantization-ladder.md` §3 requires an explicit statement that rung differences may reflect **MLX kernel
maturity rather than precision**. It applies to the shrunk ladder too: BF16 runs plain matmuls, Q4 is MLX's
most-exercised `quantized_matmul` path, affine-G64 Q8 materially less so. The plan states it nowhere.
Add it to §2's scope boundaries and to the paper's title-level framing.

**Q-A8 — (minor, receipts hygiene)** `python -m mlx_lm.convert` emits
`RuntimeWarning: 'mlx_lm.convert' found in sys.modules…` plus
`Calling 'python -m mlx_lm.convert ...' directly is deprecated`. Use `python -m mlx_lm convert …` so the
captured stderr in the conversion receipt is clean and the invocation survives the next pin bump.

**Verified-correct — do not re-litigate:** the SHA-resolution + `hf download --revision` + `--hf-path <local dir>`
sequence is the right workaround for the missing `--revision` CLI flag; `--dtype`, `-q/--quantize`,
`--q-bits`, `--q-group-size`, `--q-mode affine` all exist and take the given values; the 20 GiB disk
precondition is satisfiable (28 GiB free; actual need ≈ 9 GB for source + three rungs).

## Three highest-risk gaps

1. **Both kill gates are non-functional as written** — Gate 1 cannot pass (Q-A1), Gate 2 cannot decide (Q-A5).
   The plan's entire claim to be a "kill schedule" rests on two gates that return no verdict.
2. **The night budget is wrong in the direction that matters, and it is knowable today.** A one-lineage
   three-rung ladder is four nights, not the three banked in `ADJUDICATION.md`. Discovering that inside
   Gate 1 spends Ed's ruling cycle twice.
3. **The mint/consumer blocker lands in U10's file set.** The plan under-scopes it (schema only, not the
   consumer) and gates it on the wrong milestone ("U3 merged"). A P2 branch editing `detection_floor.py`
   between beta and gamma is a live threat to the capstone's three nights — the exact risk the carried
   fact warned about.

## Advisor-scrutiny survival

Rivoire will accept the provenance and receipt discipline without argument — it is JouleSort-grade — but
will ask what the BF16↔Q4 gap measures when the two rungs run different kernels and, as currently written,
different non-quantized dtypes; the plan has no answer today, and Q-A1 + Q-A7 are what buy one.

---

# Plan 2 — DRAFT-MOE_GATES.md

## VERDICT: **ACCEPT-WITH-AMENDMENTS**

The gates here genuinely kill: DG2's `H ≥ 19.2 GiB` worst-of-three memory rule and its
`T_plan ≤ 192 min` packing rule (240 × 0.8 — arithmetic checks) are falsifiable and fire before any night;
DG3's "**upper** 95% bound ≤ 2%, do not subtract overhead" is the right shape and the right refusal;
DG4's `PASS-QE / PASS-TRADEOFF / FAIL` trichotomy is pre-authorized rather than adjudicated after the fact.
The source citations are exact (verified line-by-line against the installed runtime), the
`qwen3_next`/`qwen3_5` correction is right, the "monkey-patch that recomputes routing is not acceptable
evidence" rule is right, and the new-stack-identity rule ("do not inherit any stock-runtime floor") is
present and correctly stated. The disk precondition is *correctly failed* against real numbers.

What it lacks is the one gate most likely to end the study, and an honest night count.

## Amendments

**M-A1 — Add the missing effect-size kill gate and place it BEFORE DG3.**
DG1-DG4 contain no sizing test whatsoever; sizing is deferred to gate 5, i.e. *after* the 32-48 focused-hour
runtime fork — the single most expensive item in the plan. Insert **DG2.5 — projected-floor sizing**, run on
DG2's existing timing members with an off-window power proxy:
- project member energy for dense, k=8, k=4 at the `moe-routing-fixed1024-v1` policy;
- project each arm's comparative floor as **7.3% of its projected member mean**, scaled from the one measured
  precedent (7B comparative `13.998036715259254` J on member mean `192.38623252628366` J), and stated as a
  range (3-15%), per `rev-moe-routing-energy.md:134,304`;
- **kill unless** the projected `k8−k4` effect and the projected `dense−MoE` effect each exceed
  **3× the larger of the two relevant arms' projected floors**.
This is the cheapest decisive gate available and it currently does not exist anywhere in the plan.

**M-A2 — Move the `d_active ≤ 0.30` pair-match test into DG1, before acquisition.**
It is computable from the remote `model.safetensors.index.json` + `config.json` alone (hundreds of KB) —
no 17.2 GB download, no disk sacrifice, no Ed ruling spent. It is also likely **marginal**: `Qwen3-4B-4bit`
is `tie_word_embeddings: true` (verified locally: `model_type qwen3`, 36 layers, vocab 151936, quantization
`{group_size 64, bits 4}`, no `lm_head` tensors) while Qwen3-30B-A3B is untied and carries a separate LM head,
so whether the gate passes depends on an accounting choice the plan has not frozen. Pre-register the exact
ledger rules **and the computed `d_active`** in the DG1 packet, so the premise of the whole pair is settled
before anything is downloaded.

**M-A3 — Correct the night budget before it re-enters the portfolio table.**
"Two-night minimum: independently governed floor night plus science night" is not arithmetically reachable
for three independently-floored arms. Under D-117's proven 10-absolute/40-null design that is 150 floor
members; DESIGN-MEMO's 50-member Alpha window is already 147 min campaign subtotal / 157 min base occupancy /
188.4 min with margin against a 240-min envelope, at a **512**-token 1.5B member. Three 1024-token 30B-A3B
arms in one night cannot fit. State the honest floor: **three arm-floor nights + one science night = four**,
with the two- and three-night schedules retained only as *outcomes* of DG2's own `T_plan ≤ 192 min`
arithmetic. This is also the correction owed to `ADJUDICATION.md`'s "Stretch MoE | 2-3" row and to open
question 8.

**M-A4 — Name the mint/consumer blocker; the MoE arc inherits it worse than quantization does.**
Verified at `origin/impl/d117-u3-pinset-v2` (`dea7c87`): `schema_v2.json`,
`scripts/mint_floor_artifact_generalized.py`, and `joulewise/detection_floor.py` all hardcode exactly
2 producer plans, 2 cells per component, 4 aggregate cells, 4 transport allowlists, 2 component artifacts,
per-component roles exactly `{"decode","prefill"}`, and `consumer_floor_rule == "cross_stack_armwise_max.v1"`
as a const. **Three** independently-floored arms on a **decode-only** metric are therefore neither mintable
nor consumable without a generalized N-cell schema, composer, and consumer branch. Add this to the gate list
as an explicit desk dependency with its own week count, and hard-gate it behind **U10 closing** — it lands in
U3's exact file set, and the D-117 nights have priority.

**M-A5 — Budget and validate the teacher-forced decode harness; DG4 does not currently contain it.**
The `MOE-TF-K8K4` estimand requires stepping decode token-by-token with a **forced** next token.
`mlx_lm` exposes no such API, and a single parallel forward over the fixed sequence measures **prefill**
(compute-bound), not decode (bandwidth-bound) — a different energy regime entirely. The forced-decode loop
must be built *and demonstrated path-identical to the production generate path*, or it becomes a fourth
stack identity whose timings cannot be compared with the free-running arms. DG4's 24-36 focused hours does
not contain this build; either budget it or fold it into DG3's runtime-derivative work.

**M-A6 — Verify, do not assume, the 48-MoE-layer reconciliation denominator.**
`mlx_lm/models/qwen3_moe.py:155` makes a layer sparse only when
`args.num_experts > 0 and (layer_idx + 1) % args.decoder_sparse_step == 0`. Derive the expected record count
from `decoder_sparse_step` and `num_experts` **read off the loaded model**; a hardcoded 48 converts a config
surprise into a silent 100%-reconciliation pass — the exact failure the gate exists to prevent.

**M-A7 — Say which digest carries `routing_top_k_override`.**
Overriding `self.top_k` at runtime (`qwen3_moe.py:117`, consumed at `:130`) keeps the artifact bytes identical —
correct, and better than a `config.json` edit. But it must then be pinned in the **scientific-config identity**,
not the model-artifact identity, or the k=8 and k=4 arms hash identically. State which.

**M-A8 — Name the space, and move open question 7 to a hard precondition.**
DG2 correctly fails its own precondition (verified: 28 GiB avail, 97% full). "Freeing space is Ed-owned" is
left abstract. The only candidate on the volume is `/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit`
(65 GB) — the artifact this portfolio retired as a claim vehicle but which `rev-moe-routing-energy` move 1
wanted retained as a scale-context diagnostic. Put that trade in the DG1 packet as an explicit Ed ruling
conditioned on a verified external mirror, and state plainly that the required second 17.2 GB mirror
**cannot** live on this volume under any outcome.

**M-A9 — (minor)** Use `hw.memsize_usable` (127.13 GiB) rather than the nominal 128 GiB in the headroom
formula; `hw.memsize` is exactly 128.00 GiB so the formula is sound, but the usable figure is 0.87 GiB
tighter and the plan's own precision standard warrants it.

**Verified-correct — do not re-litigate:** `hf` at hub 1.22.0 supports `--revision`, `--local-dir`,
`--dry-run`, `--format json`; `--local-dir` renames into place on the same filesystem, so there is no
transient doubling. The `.metadata`-first-line-equals-revision check is real (verified against
`/Users/edr/jw_models/mlx-community/Qwen3-4B-4bit/.cache/huggingface/download/*.metadata`).
`mx.get_peak_memory()` exists at mlx 0.31.2. The dense revision `4dcb3d10…` matches the local artifact.
`192 = 240 × 0.8` checks. The "retain lazy on-device references, no host readback or `mx.eval` for tracing
inside the measured interval" design is the right MLX instinct.

## Three highest-risk gaps

1. **No effect-size gate anywhere in DG1-DG4.** The study's most likely failure mode — the k8−k4 effect
   sitting near or below the projected floor, exactly what `rev-moe-routing-energy` BLOCKER 2 predicts —
   stays invisible until after the plan's most expensive desk build.
2. **The three-arm floor set is unmintable and unconsumable under the frozen toolchain, and the plan never
   says so.** A multi-week schema/composer/consumer dependency is hidden inside a document that presents
   itself as bounded desk gates, and it collides with U3/U10.
3. **Two nights is not a schedule for three floored arms** — and two is the number that reached
   `ADJUDICATION.md`. DG2's own arithmetic will refute it, but only after DG1's ruling and the 17 GB
   acquisition have been spent.

## Advisor-scrutiny survival

Rivoire will like the sublinearity preregistration and the `ρ < 1` upper-bound endpoint — predicting your own
floor from a prior cell and publishing the comparison is a genuine metrology contribution — but she will ask
for the projected floor of each of the three arms in the first five minutes, and the plan has no number to
show her until M-A1 exists.

---

## Cross-cutting note for the fix contract

Both plans independently rediscover the same blocker (`schema_v2` cardinality) and both under-scope it the
same way — schema only, not `joulewise/detection_floor.py`. Both also omit the ≥3× projected-floor rule that
the referees imposed on the portfolio as a whole. Fix those two once, as portfolio-level rules, rather than
twice as per-plan amendments:

- **R1.** No P2/stretch commit may touch `scripts/floor_mint_pinsets/**`,
  `scripts/mint_floor_artifact_generalized.py`, or `joulewise/detection_floor.py` until U10 closes.
  Generalized N-cell mint + multi-arm estimator + Holm is a single scoped desk unit with its own week count,
  serving both papers.
- **R2.** Every sizing/kill threshold in every extension plan is expressed as a multiple of a **projected
  floor for that cell** (projection = 7.3% of projected member mean, range 3-15%, precedent
  `13.998036715259254` J / `192.38623252628366` J), never as a joule literal and never at 1×. The
  publish-the-projection-then-compare-the-mint move is free and is itself a methodological contribution.
