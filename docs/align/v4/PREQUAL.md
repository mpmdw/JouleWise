# ALIGN v4 off-Mac pre-qualification (PREQUAL)

Authority: RUN_STATE item 183 (Ed): no check is pinned to the measurement MacBook Pro
(Mac15,9, M3 Max, 128 GB) if it can run ahead of time or faster on another machine.
Ed's clarification, 2026-11-06: **a check whose purpose is to measure or validate the
measurement Mac itself stays on the Mac, even if it could technically run elsewhere.**
That covers SMC/thermal behaviour, power, powermode, Metal memory, throughput and
timing, effort-rung selection by speed, decode budgets, peak memory on that GPU, and
B7 timing. Only checks about the software, model, config and fixtures are
pre-qualified here.

Why this exists: on 2026-11-06, R0 used two measurement-Mac attempts. The first failed
on a launcher bug: `Path.resolve()` turned the venv interpreter into bare Homebrew
Python (#684). The second failed on a model fault: D scored NLL 11.04 on the `load`
fixture (`records/2026-11-06-align-r0-v4-rerun`). The runner now catches the first
class off the Mac (see the `launcher` check). The second class needs the real D
weights; the "Remaining" section below gives the off-Mac design for it.

## Boundary

| Class | Meaning |
|---|---|
| **MAC** | Measures or validates the Mac itself, or reads state that exists only there (its disk, launchd, process table, real D in Metal). Stays on the Mac. |
| **PRE** | Software, model, config or fixture only. Run before any Mac launch. |
| **SPLIT** | The logic and inputs are PRE (the runner covers them); the verdict needs Mac evidence. |

## Inventory

"Runner" names the `scripts/align_v4_prequal.py` check that covers the PRE part.
Where it can run:
- **Air**: the M4 Air, natively, with small fixtures.
- **Air+sib**: the Air, with the Qwen3.5-0.8B-8bit sibling backend.
- **Air+LS**: the Air, with a layer-streamed D (designed, not built).
- **cloud**: Codex cloud CPU. It has no network, sees only its base branch and runs stdlib-only code.

### R0 (`joulewise/align/r0*.py`, `scripts/align_r0_checks.py`; launcher on `origin/main`)

| # | Check | What it verifies | Class | Runner | Where | Fidelity lost off-Mac |
|---|---|---|---|---|---|---|
| 1 | `validate_config` | R0 config schema; D only; absolute unrestricted paths; SMC step profile | PRE | `r0-config` | Air, cloud | None. It also cross-checks the config against the kit's D_SOURCE and D_REVISION, the anchor revision, and the absence of offloads. The Mac's own paths are not checked. |
| 2 | `QuietGuard` census | No agents, chains, armed night agent or custody on the Mac | MAC | – | Mac | Reads the live Mac state. The logic has offline tests (`test_r0_host.py`). |
| 3 | `host` | AC power, powermode, thermal notes, wired limit, memory | MAC | – | Mac | Validates the Mac itself. |
| 4 | `host-identity` | `hw.model == Mac15,9`, ≥128 GiB | MAC | – | Mac | Validates the Mac itself. |
| 5 | `disk` (inventory + free space) | Local D and anchor file hashes; free bytes; SMC journal estimate | SPLIT | `d-pins`, `d-pin-verifier` | Air, cloud (verifier self-test only) | Only the Mac can hash its own copy. The remote listing (revision, sizes, LFS sha256, blob IDs) and the verifier logic are checked off the Mac. |
| 6 | `align_v4_verify_d_pins.py` | Local inventory equals the pins | SPLIT | `d-pin-verifier` | Air, cloud | It self-tests on exact and tampered inventories. Given `--r0-report`, it classifies a real report. |
| 7 | `MlxBackend` stack pins | mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1 | SPLIT | `stack`, `launcher` | Air | Proves the runner and launcher interpreter logic. The Mac's `$M/.venv` contents are still checked on the Mac at model-load. |
| 8 | `model-load` (D) | D loads into Metal; device info; artifact identity | SPLIT | `model-load` | Air+sib | Exercises the production `MlxBackend` code path with sibling weights. Loading the real 29.5 GB D is MAC (or Air+LS). |
| 9 | `load`: NLL fixture IDs | The 2,049 pinned SHADE IDs (spam_filter_update, seed 91, benign) | PRE | `nll-fixture-ids` | Air | None. The IDs equal the Mac's 2026-11-06 IDs (sha256 `792beb56…`) and are canonical under encode(decode()). |
| 10 | `load`: NLL ≤ 3.0 on D | D's forward pass on the fixture | SPLIT | `load` | Air+sib now; Air+LS later | The sibling checks the code path and returns its own value, which does not qualify D. The D verdict needs the D weights (MAC, or Air+LS). |
| 11 | `load`: coherence + echo round trip | Short prompt answers 42; one `r0_echo` call and a second turn | SPLIT | `load`, `tool-roundtrip` | Air, Air+sib | `tool-roundtrip` replays the Mac's recorded D turns through parse, tool, history and render, and reproduces the Mac's second-turn prompt IDs exactly. Live D sampling stays on the Mac. |
| 12 | `template` (synthetic rewrites) | Template re-render of closed-reasoning history | PRE | `template-rewrites` | Air | None. This is R0's own function, run with no model. As in R0, it is a diagnostic only. |
| 13 | `generated` + `checkpoint` (B7) | Prefix rewrites on real generated turns; B7 verdict | SPLIT | `generated`, `checkpoint-native` | Air+sib, Air | The code path and tiny-model restore exactness run off the Mac. **The B7 verdict and B7 timing for D stay on the Mac.** |
| 14 | `memory` | Peak Metal memory and swap at the 40,960 cap | MAC | – | Mac | Validates the Mac's GPU memory. |
| 15 | `smc` | SMC enumeration and GPU step response (S_fast/S_slow) | MAC | – | Mac | Validates the Mac's sensors. |
| 16 | `ladder` | Effort rung by cap and reasoning tokens | MAC | `template-render` (prompts only) | Mac | Rung selection by decode cost stays on the Mac. The runner renders every rung's prompts. |
| 17 | `long-decode` | 40,960-position memory growth | MAC | – | Mac | Validates the Mac's GPU memory. |
| 18 | `tool-envelopes` | ≥95% of emitted envelopes parse | SPLIT | `tool-roundtrip` | Air | The accounting logic and parser run on canned and real Mac turns. The D fraction itself comes from the Mac run. |
| 19 | `launch_align_r0.py launch` (main) | Argument resolution, `runner.json`, plist, fence, unresolved `--python-bin` | PRE | `launcher` | Air (cloud for logic only) | Runs the real `launch()`, with launchd replaced by a claimer that takes the fence. It then runs the real `run` subcommand with the spec's interpreter (`--help`) and probes that interpreter's stack and venv prefix. |
| 20 | `launch_align_r0.py preflight` | AC power, free disk | MAC | – | Mac | Validates the Mac itself. |
| 21 | LaunchAgent bootstrap, desk-fence handoff, Spotlight pause | Real launchd on the Mac | MAC | – | Mac | Reads the live Mac state. |

### W1 pre-arm (`align_v4_session.py` → `align_pilot_session` → `bytes_h_session`)

| # | Check | What it verifies | Class | Runner | Where | Fidelity lost off-Mac |
|---|---|---|---|---|---|---|
| 22 | `kit.generate(check=True)` drift | Committed kit bytes equal regenerated bytes | PRE | `kit` | Air, cloud (needs git history) | None. |
| 23 | Plan and hash chain | Plan tree → collection plan, member config sha, manifests, identity-pins derivation | PRE | `kit` | Air, cloud | None. Re-derived independently of the generator. |
| 24 | `kit.require_w1_ready` | All inputs filled and valid (WP18, R0 effort, R1 slots), D identity bound to the HF pins, R1-derived `sizing_b5.json` present | PRE | `kit` (fails unless `--stage w1` is ready) | Air, cloud | None. Pending inputs are expected before R0 and R1. A filled WP11 that does not bind the pins fails at every stage. |
| 25 | `thermal_gates.validate_gate_policy` | Gate policy fields and bands | PRE | via `require_ready` | Air, cloud | None. |
| 26 | W1 D-member prompts | Every D member's (pair, condition, seed) renders at the selected effort, or at every rung while R0 is pending | PRE | `template-render` | Air | None. |
| 27 | `registration.load_sizing` / `load_identity_pins` | `sizing_b5.json`; 64-hex sha per unit | PRE | `kit`, `w1-plan` | Air, cloud | None. The D sha is filled (WP11, folded `a8d1c5c9…6b30`). `sizing_b5.json` is derived by the kit from the R1-filled `registration/w1_plan.json`; until R1 supplies that file, `--check` and `prepare` refuse and say so. |
| 28 | Model presence on host paths | `model_source` directories and inventories exist | MAC | – | Mac | Reads the Mac's disk. |
| 29 | `disk_snapshot` / `w1_disk_gate` | ≥80 GB free; offload re-hash | MAC | – | Mac | Reads the Mac's disk. `align_v4_session.py install --w1-disk-config <R0 config>` calls `w1_disk_gate` before the installer and refuses on anything but pass; R0's disk row reports the same requirement (`w1_requirement`). |
| 30 | `desk_identity.collect` | Runs `$M/.venv/bin/python scripts/write_derivation_night_inputs.py` | MAC | – | Mac | Needs the Mac's venv. Can be faked with `run=`. |
| 31 | `b5.plan.write_window_plan` / `chain.stage_plan` | Plan writer invariants, ledger head pin, runbook | PRE | – (tests; blocked by #27) | Air | None once the inputs exist. |
| 32 | `install` (launchd census, plists) | `com.joulewise.night` absent; plan sha and t0 | MAC | – | Mac | Uses the real launchd. |
| 33 | R1 `arm_powermode_check` | Observed AC powermode equals the frozen value | SPLIT | – | Mac (observation) | The comparison is pure. The observation needs the Mac. |
| 34 | `launch_window._recheck_identity_projection` | Re-derives identity units, may hash model artifacts | MAC | – | Mac | Reads the Mac's model artifacts. |
| 35 | `run_night._launcher_barrier` | AST literal check of `launch_window.py` | PRE | – (tests) | Air, cloud | None. |

### R1 (`lane/2026-11-06-v4-r1-integrated`, in progress; read-only here)

| # | Check | Class | Note |
|---|---|---|---|
| 36 | `PowerModeGuard`, A-B-A powermode readback, power marker | MAC | Validates the Mac's power behaviour. |
| 37 | `high_power_adoption`, `planning_temperature_summary`, `u5_verdict`, `soak_detrended`, `deadman_summary`, `os_load_verdict` | MAC | Pure functions, but their purpose is to measure the Mac. They stay with R1 on the Mac. |
| 38 | `r1_runtime_contract.missing_fields` | PRE | Runtime field contract; covered by R1's own tests. |
| 39 | `kit.require_ready(inputs, r1_slots)`, `l1_t_dead`, `check_l1_member_fit`, `fit_roster` | PRE | The runner's `kit` check calls the two-argument `require_ready` when the kit has `read_r1_slots`. |
| 40 | `validate_align_v4_w1_plan.py` | PRE | `w1-plan`: template drift, refusal of the PENDING_R1 template, L1 and fit-rule self-tests; at `--stage w1` the R1-filled plan must validate. |
| 41 | `align_v4_w1_synthetic.py` (WP22) | PRE | Synthetic end-to-end W1 with injected faults. Air or cloud. |

### Magistrate preflights (`scripts/magistrate_watchdog.py:decide`)

| # | Check | Class | Note |
|---|---|---|---|
| 42 | Clock sanity, `load_plans`, desk fence, release and liveness census, plan conflicts, lock, remote stop, plan span, `_launch_fence` | MAC | Each one reads the Mac's live process table, LaunchAgents and custody. Their logic is covered offline by `tests/test_magistrate_*.py`. |

**Counts (42 rows):**

| Class | Count | Rows |
|---|---|---|
| MAC | 17 | 2, 3, 4, 14, 15, 16, 17, 20, 21, 28, 29, 30, 32, 34, 36, 37, 42 |
| PRE | 16 | 1, 9, 12, 19, 22, 23, 24, 25, 26, 27, 31, 35, 38, 39, 40, 41 |
| SPLIT | 9 | 5, 6, 7, 8, 10, 11, 13, 18, 33 |

On the R0 path alone (rows 1–21): 9 MAC, 4 PRE and 8 SPLIT. Twelve of those 21 rows are
now fully or partly qualified off the Mac. The runner covers every PRE row except 31,
35, 38 and 41 (see Remaining).

## What the runner covers

`scripts/align_v4_prequal.py` writes `prequal.json` and `prequal.md` to a new
directory and fails closed:
- Any exception is a `fail`, never a skip.
- A required check that did not run makes the report `incomplete`. Exit codes: 0 pass, 1 fail, 3 incomplete.

| Check | Runs | Pass condition |
|---|---|---|
| `stack` | Air | The prequal interpreter has the pinned mlx, mlx-lm and transformers. |
| `r0-config` | Air, cloud | The real `configs/align/v4/r0_desk.json` passes `validate_config`, and its cross-references agree. |
| `launcher` | Air | The real `launch()` writes `runner.json` with the **unresolved** `--python-bin`. The interpreter imports the pinned stack inside its own venv. The real `run` subcommand executes the runner. This is the #684 regression class; `tests/align/test_v4_prequal.py` shows that a resolving launcher fails it. |
| `kit` | Air, cloud | No drift, the hash chain holds, a filled WP11 binds the HF pins, and readiness (`require_w1_ready`: inputs, D identity, R1 sizing) is reported (it must pass for `--stage w1`). |
| `w1-plan` | Air, cloud | The W1 template has no drift from `collection_plan.json` and is refused only for its PENDING_R1 placeholders; L1 and the A1 fit rule reproduce the planning arithmetic (span 26,927 s). At `--stage w1` the R1-filled `registration/w1_plan.json` must validate against inputs and r1_slots, with `sizing_b5.json` beside it. |
| `d-pins` | Air (network) | The HF listing at the pinned revision equals the pins file. No weights are downloaded. |
| `d-pin-verifier` | Air, cloud | The verifier accepts an exact inventory and rejects a tampered one. Top-level `.cache/huggingface/` bookkeeping is counted, not compared (PR #686); a nested one still fails. |
| `d-tokenizer-files` | Air | D's non-weight files (29 MB) download at the revision and match every pin (size, plus LFS sha256 or git blob sha1). |
| `template-render` | Air | Renders 27 prompts: R0 short, echo and both ladder pairs at xhigh, medium and low, plus every W1 D member. Each must render with the generation prompt, fit the context cap and be canonical, with the right effort line. The pinned template writes **no** effort line for `medium`. R0 short and echo IDs must equal the Mac's. |
| `nll-fixture-ids` | Air | The 2,049 IDs equal the Mac's (`configs/align/v4/prequal_r0_reference.json`). |
| `template-rewrites` | Air | R0's synthetic B7 diagnostic, run with no model. |
| `tool-roundtrip` | Air | Replays the Mac's real echo turn 1 through parse, `EchoTask`, history and render, and must reproduce the Mac's turn-2 prompt IDs. Also checks every recorded turn's call count; all 41 SHADE tools with schema-typed arguments through parse, history and render; rejection of truncated, unknown-tool and JSON envelopes; and `tool_envelopes` accounting. |
| `checkpoint-native` | Air (Metal) | `align_cache_checkpoint_native.py` exactness on tiny qwen3_5 and qwen3_next. It does not run the `--benchmark` timing. |
| `model-load`, `load`, `generated` | Air+sib | The production `MlxBackend` runs over a hybrid directory: sibling weights plus D's tokenizer, template and EOS IDs. R0's own `load_coherence` (PR #686: NLL reference equivalence plus the SHADE generation check) and `generated_rewrites` run on it. The NLL IDs and short-prompt IDs must equal the Mac's. The sibling names its own revision, so its NLL is judged against its own entry (`configs/align/v4/prequal_sibling_nll_reference.json`: HF fp32 0.4669 on the same ids, mode `reference`, ±0.10 mean / ±0.5 per bin), and that verdict must pass. The generation check must run end to end (render, greedy decode, parse, `tool_envelopes`, schema validation); its outcome, coherence, echo success and the sibling's B7 verdict are diagnostics. |

The sibling is `mlx-community/Qwen3.5-0.8B-8bit@87e768fb` (1.03 GB). It matches D in:
- mlx_lm class: `qwen3_5` / `qwen3_5_text`
- quantization: 8-bit affine, group size 64
- `vocab_size`: 248,320
- `vocab.json` blob

It has 24 layers where D has 64. There is no small Qwen3.8 on the hub.
`build_sibling_dir` refuses a sibling that differs in model type, vocab or
quantization, and refuses any artifact over 2 GB.

## How to run before any measurement-Mac launch

On the Air (or any Apple-silicon machine that is not the Mac):

```sh
# one-time: the pinned stack plus the SHADE deps, in a throwaway venv
python3.13 -m venv /private/tmp/jwprequal-venv
/private/tmp/jwprequal-venv/bin/pip install 'mlx==0.31.2' 'mlx-lm==0.31.3' 'transformers==5.12.1' \
  'pydantic>=2' pyyaml docstring-parser typing-extensions rich pandas openai anthropic matplotlib seaborn email-validator

# at the exact commit the Mac will run (the measurement checkout head)
HF_HOME=/private/tmp/jwprequal-hf TMPDIR=/private/tmp/jwprequal-tmp nice -n 15 taskpolicy -b \
  /private/tmp/jwprequal-venv/bin/python -B scripts/align_v4_prequal.py \
  --output /private/tmp/jwprequal-runs/<commit>-r0 --hf-cache /private/tmp/jwprequal-hf \
  --launcher-ref origin/main --python-bin /private/tmp/jwprequal-venv/bin/python \
  --model-backend sibling --stage r0
```

- `--launcher-ref origin/main` is needed while `launch_align_r0.py` lives only on `main`,
  not on the v4 lane. Use `--launcher PATH` for a specific file.
- `--python-bin` stands in for the Mac's `$M/.venv/bin/python`. Pass a venv interpreter
  so the venv-resolution regression is actually exercised.
- `--stage w1` additionally requires `require_ready` to pass.
- `--r0-report REPORT_JSON` runs the D pin verifier against a real report.
- `--offline` uses caches only. The HF listing is then `not_run` and the report is
  `incomplete`.
- Wall time on the Air is about 4–6 min with the sibling: SHADE fetch, tokenizer renders,
  tiny checkpoint exactness and roughly 2 min of 0.8B generation. Peak RSS is about 2 GB.

**Rule for the magistrate:** a measurement-Mac R0, R1 or W1 launch must cite a `prequal.json`
with `status: pass`. It must have been produced at the same `checkout.head` as the
measurement checkout, with `checkout.dirty: false`, and with `implementation_sha256` entries
matching that commit. An `incomplete` report is not a pass.

Cloud (Codex, CPU, no network) can run the stdlib subset:

```sh
python3 -B scripts/align_v4_prequal.py --output OUT --offline --only r0-config,kit,w1-plan,d-pin-verifier
```

That run is `incomplete` by design. It is useful as an early CI-style gate on a branch.

## What R0 still must do on the Mac

host, host-identity, the census, disk (its own hashes and free space), model-load of
the real D, the `load` NLL verdict on D, the live coherence and echo with D, generated
turns and the B7 verdict and timing for D, memory, SMC, ladder, long-decode, the
launcher preflight, and the LaunchAgent and fence handoff. None of these measure
anything the Air can stand in for.

## Remaining

1. **Layer-streamed D backend (Air+LS), designed but not built.** It would have caught the
   2026-11-06 `load` failure off the Mac. Design:
   - Download D's 29.5 GB once to the Air. This exceeds today's 2 GB rule and needs a ruling.
   - Load the embedding, final norm and `lm_head`.
   - For each of the 64 layers in order: `mx.load` only that layer's tensors from its shard,
     run all 2,049 positions through the layer, keep the hidden states (about 21 MB in bf16),
     then free the layer.
   - Score the final logits in 128-token chunks.

   Peak memory is about one layer (≈0.45 GB) plus activations. That fits in 6 GB with the
   same mlx kernels.

   Fidelity lost:
   - It runs on the M4 GPU family (`applegpu_g16`) instead of the M3 Max (`g15s`): same
     kernels, not bitwise identical.
   - It uses a single full-sequence prefill per layer, not R0's chunked cache path. The
     2026-11-06 diagnostic shows those agree (11.07 vs 11.04).
   - Generation-dependent checks stay sibling-only.

   Implement it as a `BACKENDS["layer_stream"]` exposing `nll(ids)`. `check_load`
   would then use the D limit as a gate.
2. Done on `lane/2026-11-06-v4-w1-blockers`: `validate_align_v4_w1_plan.py` and the R1
   kit checks run as the `w1-plan` check.
3. **W1 blockers found by the inventory**, closed on `lane/2026-11-06-v4-w1-blockers`
   (`docs/run_reports/2026-11-06-align-v4-w1-blockers.md`):
   - `w1_disk_gate` now runs at W1 arm (`align_v4_session.py install --w1-disk-config`).
   - `sizing_b5.json` is derived by the kit from the R1-filled `registration/w1_plan.json`;
     before that file exists, `--check` and `prepare` refuse with that reason.
   - The D `model_artifact_sha256` is the folded sha `a8d1c5c9…6b30`, bound shard by shard
     to the HF LFS pins.
   - Still open, by design: WP18 (Mac-side pilot-7 turn counts and token fixture),
     `R0.reasoning_effort` (until R0 passes), the R1 values and WP15's entrypoint. The kit
     message names what each one waits for.
4. The R0 synthetic `template` diagnostic shows `prefix_stable: false`: the pinned D template
   rewrites 12 tokens at every one of the 12 synthetic transitions. The sibling's real
   generated turns show 0, so expect this R0 diagnostic row to read false on the Mac. It
   cannot decide B7, and it is not investigated here.
5. Fixed by PR #686 (`f1ae2d3be`): the D pin verifier counts and reports top-level
   `.cache/huggingface/` bookkeeping without comparing it. The `d-pin-verifier` check
   asserts that, and that a nested `.cache/huggingface/` path still fails.
6. The Mac's `$M/.venv` contents (versions beyond the three pins, such as `tokenizers`) are
   not visible off the Mac. A venv lockfile recorded by R0 would let the prequal match it.

## W1 and next-arm extension (RUN_STATE 219/220, merged smoke kit)

`scripts/align_v4_prequal.py --w1-next {r1,w1}` (module `joulewise/align/w1_prequal.py`) runs every code
path the next window executes, off the Mac, with a fake host. It covers:
- the production arm CLI and its required evidence;
- the next-arm triage, including the packet-as-pointer rebuild (G1: `packet-rebuild`, G1b:
  `packet-tamper`);
- the fixed-8 calibration stop and its lead-ruling exit;
- the receipt: executed-closure coverage and the candidate commit;
- the series projection;
- the installed-plan deadline;
- the R1 -> W1 chain as documented;
- the KM003C launch and crash radius;
- W1 `window_max_s` sizing;
- the full WP22 dry run;
- the isolated native smoke kit;
- "an arm route exists end to end for the next measurement" (`configs/align/v4/arm_routes.json`);
- a WARN-only row for required tests that run only behind an opt-in (opt-in audit ledger).

The command, check table and expected greens are in `docs/align/v4/W1-SMOKE.md`.

**Rule for the magistrate:**
- An R1 arm cites a `--w1-next r1` report, and a W1 arm cites a `--w1-next w1` report.
- Each report must have `status: PASS` at the measurement checkout's commit, with `checkout_dirty: false`.
- These reports are in addition to the R0-style `prequal.json` above.

**Launcher check (opt-in audit 2026-11-08).** `launcher` compares `runner.json` semantically:
- the unresolved venv interpreter;
- the runner script;
- the required `--config` and `--output` values;
- only the allowed optional flags `--keep-going` and `--checks`;
- no forbidden flag.

It is not an exact argv list, so `origin/main`'s default `--keep-going` passes. For dwell launchers, the
`run --help` probe uses the launcher's test dwell seam and a no-op `pmset`.
