# ALIGN v4 — WP14 protocol rulings: (a) thermal sensor selection, (b) window-reference custody, (c) how ThermalRegistry reaches run_benchmark

Chair: Opus 5.5 (`claude-opus-5-5`), 2026-11-05. Protocol chair for ALIGN v4 under the v4 execution plan's WP14 (`/private/tmp/jwsol/v4-plan-synth.md`).
Proposed location: `docs/align/council-2026-11-05/WP14-RULINGS.md`, beside `FINAL-DESIGN-AMENDMENT-1.md`.

**Status.** These are protocol-v4 rulings. They do not authorize arming anything. Where they differ from `FINAL-DESIGN.md` §2.6 (`219fb1515`), Amendment 1 §A5 R0.3 (`6eb1ff5be`) or `docs/align/r0_step_test_ruling.md`, these rulings win, to the extent stated below. Everything else stands.

**Sources read.**
- Council lane `origin/lane/2026-11-05-align-window-council` @ `6eb1ff5be`: `FINAL-DESIGN.md`, `FINAL-DESIGN-AMENDMENT-1.md`, and the r1/r2 seat files (Opus r1 l.228-229 and r2 l.22, l.132 give the original intent of S_fast and S_slow).
- Integration lane `origin/lane/2026-11-05-align-v4-integration` @ `c8ef6b2f6`:
  - `joulewise/align/apple/smc_enumeration.py`: `rank`, `select_keys`, l.225-321;
  - `joulewise/align/r0_step.py`;
  - `joulewise/align/r0_host.py`: `smc_enumeration`, l.232-290;
  - `docs/align/{r0_step_test_ruling,smc_temperature,thermal_gates,r0_desk_runbook}.md`;
  - `joulewise/align/apple/thermal_gates.py`: `validate_gate_policy` l.58-88, `capture_reference` l.237-252, `ThermalRegistry` l.451-485;
  - `joulewise/align/apple/workload.py`: prepare l.197-260, capture call l.373, G0 l.402;
  - `joulewise/cli.py`: `_cmd_run_body` l.323-440;
  - `scripts/run_campaign.py`: `command_for` l.1566-1600, `--cli-cmd` l.732;
  - `joulewise/__main__.py`;
  - `joulewise/adapters/__init__.py`: `resolve_runtime` l.117-133;
  - `joulewise/controller.py`: `AdapterRegistry` l.236, `run_benchmark` l.252/286, `run_experiment` l.4399-4403;
  - `joulewise/bundle.py`: `RunBundleWriter.create` l.939-975, `_cli_config_source` l.88;
  - `joulewise/b6/registration.py`: `NUMBER_BEARING_PATHS` l.22-29;
  - `configs/pins/registry.json`.
- In-flight drafts (read only): the WP16 kit skeleton (`jw-wt/sol-v4-wp16` @ `0fc67734e`) and the WP20 protocol skeleton (`jw-wt/sol-v4-wp20` @ `262ff28a4`), whose PENDING-RULING sections these rulings close.

**What was not done.** I ran no hardware. Numbers marked *synthetic* come from a two-pole model I computed on the laptop; they show the logic of the rules and are not measurements of the Mac15,9. I opened nothing under `/Users/edr/jw-b5-*`, `night-*` or `restricted/`. Nothing was committed or pushed.

---

## (a) The thermal sensor-selection rule

### Question
Two rules exist, and both are implemented:
- **Council §2.6**, implemented in `smc_enumeration.rank(stage="r1")` / `select_keys`:
  - S_fast = the largest ΔT among keys with t63 ≤ 5 s;
  - S_slow = the longest cooling τ ≤ 300 s among keys with ΔT ≥ 3 °C;
  - keys with τ > 300 s are recorded and not gated;
  - R1's planning-turn step classifies.
- **The R0 step ruling and #658 at `274fec2cb`**, implemented in `r0_step.rank_response`, which `r0_host` uses to set the R0 status:
  - S_fast = a first-order fit with τ < 30 s over the first 120 s of load;
  - S_slow = a first-order fit with τ in (120, 900) s over the 900 s load, confirmed on recovery with R² ≥ 0.8.

R0 needs exactly one rule, and so do R1 and every later window.

### Options
1. **Council §2.6 as written.**
2. **The R0 ruling's fitted rule** for R0 and R1.
3. **One model-free classifier**: council §2.6 plus two physical corrections. R0 uses it as a bar and R1 uses it to select. **Chosen.**

### Defects found

**In the R0 fitted rule:**
- **The 900 s ceiling has no link to the gate.** It is what a 900 s load can resolve, not what a gate can use. The per-turn cap G_turn is at most 300 s (`validate_gate_policy` refuses `turn_cap_s > 300`), and the G0 cap is 600 s. A key with τ = 600 s passes this rule, but after a heavy turn it cannot get back within δ inside one cap. G1/H then time out and stop the episode (X2). Selecting such a key would turn thermal control into lost data.
- **It fits heating; the gate waits on cooling.** On the MacBook Pro the fans ramp up under load and spin down during recovery, so heating τ and cooling τ differ. Confirming recovery against the load-fitted τ (R² ≥ 0.8) rejects exactly the keys whose cooling differs from their heating. It does not measure the quantity the gate depends on.
- **The 120 s floor rejects fan-cooled heatsink keys** with cooling τ of 30-120 s. Those are the keys a 300 s gate tracks best.
- **It fits one exponential to a multi-pole system** (die → heatsink → chassis). A fit over the first 120 s lands somewhere between the poles, and eligibility ends up depending on R² rather than on physics.
- **It classifies on a matmul.** The council's rule is that the R1 planning turn, the real workload, classifies.

**In council §2.6 as written:**
- **t63 is measured against the end-of-load ΔT.** That mixes the die's fast pole with the heatsink pole underneath it. Die temperature ≈ heatsink temperature + P·θ_jc, and on a long load the heatsink term keeps growing for minutes.
  - *Synthetic* two-pole die key: 20 °C at τ = 1.5 s plus 20 °C at τ = 200 s.
  - Its t63 against end-of-load ΔT is 59 s on a 900 s load and 38 s on a 400 s load.
  - So the obvious die key is not "fast". S_fast comes back null, and both R0 and R1 fail their bar on a healthy machine.
- **S_slow has no lower τ bound and no class separation.** It takes the longest τ ≤ 300 s even if that is a die-like key with τ ≈ 10 s. `select_keys` never requires `s_fast ≠ s_slow`, and a single key can qualify for both roles.

### Decision: the v4 classifier
One pure function in `joulewise/align/apple/smc_enumeration.py`. R0 calls it to produce candidates and the bar; R1 calls it to select.

**Input.** A 1 Hz journal of every inventoried T\*/F\* key, with phases `idle` (≥ 300 s), `load` and `recovery` (≥ 600 s).

**Per-key quality gate** (unchanged from the current `rank`):
- unit °C (F\* and non-temperature keys are never selected);
- per phase: coverage ≥ 99 %, failed reads < 1 %, at least 5 valid samples;
- at least 3 distinct idle values;
- noise floor q = max(0.05 °C, type quantum, smallest observed idle step, idle SD).

**Quantities.** All are model-free. Crossings are interpolated between valid samples, and nothing is fitted.
- T0 = the idle median.
- **ΔT** = median over the last 10 % of load − T0. Unchanged.
- **ΔT60** = median over valid samples with load-relative t ∈ [50 s, 60 s] − T0. Needs at least 5 samples. **New.**
- **t63** = the first time after load onset that T crosses T0 + 0.632·ΔT60. **Changed reference.** The old end-of-load value stays in the record as `t63_end_s`, for information only.
- **τc** = the cooling 1/e crossing of (T_rec0 − T0), measured from the first observed recovery sample, as implemented now. If it does not cross within the recovery phase, τc = None.

**Classes.** They are disjoint, because the t63 split puts every key on one side of 5 s.

| Class | Conditions (all must hold) | Use |
|---|---|---|
| die (fast) | ΔT > 3q; ΔT60 > 3q; **t63 ≤ 5 s**; τc resolved and **≤ 300 s** | S_fast = the key with the largest ΔT |
| heatsink (slow) | **ΔT ≥ 3.0 °C**; **t63 > 5 s**; τc resolved and **30 s < τc ≤ 300 s** | S_slow = the key with the longest τc |
| record-only (chassis, battery, unresolved) | everything else, including τc > 300 s or unresolved | recorded with a reason; never gated |

- Ties break lexically.
- Boundaries are inclusive at 5 s, 300 s and 3.0 °C, and strict at 30 s.
- A null pick in either class means **no selection**. Nobody substitutes a key by hand; the council's IOHID / X4 ruling applies instead.

### Why these numbers
- **t63 against the 60 s rise, cut at 5 s.**
  - The die/package pole is about 1-2 s (silicon plus package mass). The heatsink pole is tens to hundreds of seconds.
  - Measured against ΔT60 (*synthetic*):
    - the two-pole die key gives t63 = 2-3 s;
    - single-pole keys give t63 ≈ 18 s at τ = 20 s and ≥ 25 s at τ ≥ 40 s.
  - So 5 s falls in an empty gap between the classes. It also matches G1's release on 5 consecutive 1 Hz samples.
- **τc ≤ 300 s.** A gated key has to be able to return within one G_turn cap, which is at most 300 s. The value is cooling τ, measured while the fans actually spin down, because that is the regime every gate wait happens in.
- **τc > 30 s for heatsink.** Below about 30 s a key holds no state across turn gaps, which last seconds to tens of seconds. 30 s is also the R0 ruling's die boundary. Together with t63 > 5 s, this means nothing in between gets labelled "heatsink".
- **ΔT ≥ 3 °C.** Kept from the council. With δ ≥ 1 °C, a key that moves less than 3δ over a whole planning turn cannot resolve a recovery.

### What R0 computes (by day, no window armed)
1. The idle inventory, unchanged.
2. **The step test at 300/900/600 s with the matmul load.** The profile ruling is kept, with a new reason: 900 s = 3 × the 300 s τ ceiling. A heatsink with τ ≤ 300 s therefore reaches at least 95 % of its plateau, ΔT is an honest plateau value, and recovery starts close to steady state. The `smc_step.load_below_tau_upper_bound` refusal stays.
3. The v4 classifier runs on the SHA-256-authenticated journal and outputs `die_candidates`, `heatsink_candidates`, `record_only`, and one provisional top pick per class.
4. **Thermometry bar** (A5 R0.3), which **passes** only if all of these hold:
   - at least one die candidate and at least one heatsink candidate exist;
   - each top pick has more than 99 % valid 1 Hz slots over at least 600 s;
   - each top pick has fewer than 1 % failed reads (the existing `readability_bar_met` code).

   Otherwise the receipt says `inconclusive`.
5. `r0_step.rank_response` is kept only as a recorded diagnostic, `exponential_fit_diagnostic`. It has no effect on status, and its output is never called `s_fast`/`s_slow`.
6. R0's picks are **PROVISIONAL**. They do not fill a slot. Their only use is to configure R1's own gated runs (see R1 below).

**For WP13 / R0 tonight.** The input to the disposition "SMC roles inconclusive → stop and mail" is the **v4 classifier's** bar, not the R0 receipt's `status` as currently coded. If R0 runs before the classifier change lands (WP4c below), the lead evaluates the bar offline from the authenticated `samples.jsonl`. The journal holds all the data, so that evaluation loses nothing. It is not a re-run. A bar failure goes to the council's IOHID-reader / X4 choice.

### What R1 computes
1. **Step journals.** A full-inventory 1 Hz capture (every R0-inventoried T\*/F\* key, the same row schema as R0) brackets each planning-turn step:
   - `idle` = the last 300 s before prefill dispatch, quiet, after the soak or the previous cooldown;
   - `load` = from prefill dispatch to the last decode token;
   - `recovery` = the 600 s cooldown.
2. **Selection runs on D's step** (10k fed prefill + 4,096 seeded decode), under the series power mode. That is Automatic, or the High Power step if the A-B-A adopts the lever. D is the heavy production cell and the closest load to W1's.
3. The 30B step is classified and recorded only.
4. The results fill the sensor slots S1-S4 (S_fast, S_slow, fan keys) and record the classification table.
5. If either pick is null, R1 fails its thermometry bar and the council's IOHID / X4 ruling applies.
6. **If R1's picks differ from the R0 picks used to configure R1's gated runs:**
   - record `r1.sensor_pick_changed`;
   - the gated runs still count for token identity under holds;
   - S6 (δ_slow tuning) and S7 (G_turn) are computed for the R1 picks from the full-inventory step and cooldown journals;
   - the lead verifies before W1 is frozen.

### Implementation consequences
- **WP4c** (R0 path; small; land before R0 if possible, otherwise the offline evaluation above):
  - `r0_host.smc_enumeration` takes its `status`, `selection` and `readability_bar_met` from the v4 classifier, with picks labelled provisional;
  - the `rank_response` output moves to `exponential_fit_diagnostic`;
  - update `r0_step_test_ruling.md` (selection bullets superseded; profile retained) and the runbook's l.95-108.
- **WP15:**
  - in `smc_enumeration.py`, add ΔT60, t63-on-ΔT60, `t63_end_s`, the disjoint classes, the τc > 30 s floor, and R0-stage candidate output (R0 no longer returns all-null);
  - `select_keys` must make distinct picks by construction;
  - update `RULE` and `docs/align/smc_temperature.md`.
- **WP16.** The kit takes sensor keys only from R1's `r1_slots.json`. `--check` refuses unless the R0 provenance digest (`r0_sha256`) and the R1 classification digest are both present, and refuses any key absent from R1's die/heatsink class lists.
- **WP17.**
  - The R1 driver records full-inventory journals around both step tests, runs the classifier on D's step, and writes the classification table and its digest into `r1_slots.json`.
  - R1's gated runs are configured from R0's provisional picks, and mismatches are handled as above.
- **WP20.** Replace the PENDING-RULING WP14(a) section with this rule.

### Tests that must exist
`tests/align/test_smc_classifier_v4.py`, using synthetic journals:
1. A two-pole die (20 °C at 1.5 s + 20 °C at 200 s, 900 s load):
   - classified as die;
   - `t63_end_s` > 5 s while t63 ≤ 5 s;
   - it is the regression case for the council wording.
2. A single-pole heatsink with τ_heat = 60 s and τc = 90 s → heatsink. Another with τc = 250 s → it wins S_slow over the τc = 90 s key.
3. τc = 600 s or unresolved → record-only, and never selected.
4. Boundaries:
   - t63 = 5.0 → die;
   - t63 = 5.01 → not die;
   - τc = 300.0 → eligible;
   - τc = 30.0 → not heatsink;
   - ΔT = 2.99 °C → not heatsink.
5. The same key can never be both S_fast and S_slow (property test over random two-pole parameters).
6. Only die-class keys → `s_slow` null, bar fails, no fallback pick.
7. F\* and non-°C keys are never selected. A phase with ≥ 1 % read errors excludes the key.
8. R0 path: `r0_host.smc_enumeration` on a fixture journal produces a status from the classifier, with `exponential_fit_diagnostic` present and status-neutral (flipping its values changes nothing).
9. A 300/900/600 profile still refuses loads below 900 s.

---

## (b) Window-reference R: custody across member processes

### Question
R is the median of S_fast and S_slow over the last 60 s of idle before warmup in the window's first sidecar member (W1 ordinal 5). Every later sidecar member needs the identical R:
- in a fresh process;
- possibly in another `run_campaign` stage (episodes-a / episodes-b, with the neg8 midpoint stage between them);
- always under the same `claim_runs_root`.

How does R get to those members with verifiable custody?

### Options
1. **Inline values in later specs** (the current `window_reference` temperature form in `validate_gate_policy`). **Rejected and retired.** The values do not exist when the kit is frozen. Writing them into configs during the window would change the plan tree and generator hashes and break the launch-lineage equality in `bundle._cli_config_source`.
2. **The plan's recommendation**: member 5 writes a custody file, and later specs carry its path plus a digest. **Adopted with two corrections:**
   - No content digest can sit in a spec, because the content is unknown at kit freeze. The spec's digest is therefore the **source member's config SHA-256**, the only binding digest that exists at freeze. Content integrity is verified at read time against member 5's own journal.
   - No path is stored. The file location is derived from a run id under the runs root. This keeps the `thermal_gates` rule that no path stored in an episode spec is followed.
3. **A window-level file in the runs root or a custody parent.** Rejected:
   - it sits outside bundle custody, harvest and backup;
   - it adds an entry to the root that whole-window membership checks inventory;
   - it needs a path binding.
4. **Consumers recompute R directly from member 5's journal, with no file.** Rejected on its own, because the journal does not mark the capture span (warmup entry). Kept as the verification step.
5. **Each member captures its own reference.** Prohibited: the reference would ratchet, which the council forbids and WP20 flags.

### Decision

**Spec fields.** These are part of the gate map and therefore of execution identity. `window_reference` becomes **required** in every gate-map thermal policy. Exactly one of these forms is valid:

```json
{"role": "capture"}
{"role": "consume", "source_run_id": "align-v4-episodes-a-e05", "source_config_sha256": "<64 hex>"}
```

`source_config_sha256` is the SHA-256 of the source member's `config.json` **bundle bytes**, i.e. `json.dumps(BenchmarkConfig.from_mapping(cfg).to_dict(), indent=2, sort_keys=True) + "\n"`, the value `RunBundleWriter.create` writes and records as `config_sha256`. The inline temperature form is refused.

**Writer: the capture member, in `ThermalSession.capture_reference`, at warmup entry.**
- It always writes `<own bundle>/outputs/align_window_reference.json`.
  - The write is exclusive: a temp file in the same directory, then `os.link` to the final name (which fails if the name exists), then fsync of the file and the directory.
  - The file bytes are the canonical JSON of the full record followed by `"\n"`.
- If coverage is at least 90 % over the 60 s window, the status is `captured`. Otherwise it is `unobserved`, the values are null, and the existing `thermal.state_unobserved` (X4) flag is set.
- If the write fails, the member fails with `thermal.window_reference_write_failed`, so later members cannot run on a reference that was never recorded.

**File schema `joulewise.align_window_reference.v1`.**

| Field | Content |
|---|---|
| `schema` | `"joulewise.align_window_reference.v1"` |
| `status` | `"captured"` or `"unobserved"` |
| `source` | `{"run_id", "config_sha256"}`, where config_sha256 is the SHA-256 of its own bundle `config.json` bytes |
| `sensors` | `{"s_fast", "s_slow"}` |
| `sensors_policy_sha256` | SHA-256 of canonical JSON of the policy's `sensors` map |
| `rule` | `{"anchor": "warmup_entry", "window_s": 60, "statistic": "median", "min_coverage": 0.9}` |
| `span_ns` / `span_epoch_ns` | `[start, end)` on the source member's monotonic clock, plus epoch |
| `coverage_fraction` | float, or null |
| `samples` | `[[monotonic_ns, fast_c, slow_c], …]`, exactly the rows `_good_window_rows` used, in journal order (`[]` if unobserved) |
| `fast_c`, `slow_c` | medians, or null if unobserved |
| `journal` | `"outputs/align_thermal.jsonl"` |
| `record_sha256` | SHA-256 of the canonical JSON of every other field |

Canonical JSON = `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)`.

**Reader: the consumer, in `EpisodeRuntimeAdapter.prepare`.**
- It runs only when `context is not None`, so identity readiness reads nothing.
- It runs **before `runtime.prepare`**, so no model is loaded when a check fails.
- It takes the checks in this order. A failure refuses with the flag shown:

| # | Check | Flag on failure |
|---|---|---|
| 1 | `source_run_id` sanitizes to itself (`bundle.sanitize_id_component`) and differs from the member's own run id | `thermal.window_reference_path_refused` |
| 2 | The path is `context.bundle_path.parent / source_run_id / "outputs" / "align_window_reference.json"`. Neither the bundle directory, `outputs/` nor the file is a symlink, and the resolved path lies inside the runs root | `…_path_refused` |
| 3 | The file exists | `…_missing` |
| 4 | It parses with the exact schema; its bytes equal canonical(record) + `"\n"`; `record_sha256` recomputes | `…_corrupt` |
| 5 | All of these agree: `source.run_id` and `source.config_sha256` with the spec; the source config SHA-256 with the SHA-256 of `<source bundle>/config.json` bytes; `sensors` and `sensors_policy_sha256` with this member's policy | `…_binding_mismatch` |
| 6 | If `captured`: reload the source journal through `sample_rows`, recompute with `_good_window_rows` and `_window_coverage` over `span_ns`, and require coverage ≥ 0.9, `samples` identical, and both medians **exactly** equal | `…_unverified` |

- **On success,** the session's `reference` = `{fast_c, slow_c, source_member, span_ns}`, the shape it already uses internally. `thermal.record()` adds `custody: {record_sha256, source_run_id, source_config_sha256, source_journal_sha256}`, where the last is the SHA-256 of the whole source journal, which is final once the source member has exited.
- **If the status is `unobserved`** and checks 1-5 pass, the member proceeds with reference = None. G0 takes the existing unobserved path (timed 300 s wait, X4), and the member is flagged `thermal.window_reference_unobserved`. It never captures a reference of its own.
- **Any refusal** returns `AdapterResult(ok=False, RUNTIME_UNAVAILABLE)` carrying the flag. With `--max-failures 1` the stage stops. That is intended: an integrity failure must not silently degrade every remaining member.
- **On resume:** if a window is resumed after member 5 failed before capturing, it is a new window. A rerun never creates a second reference within the same window.

### Rationale
- The file lives in the source bundle. It therefore inherits the bundle's custody: create-once directory, harvest, backup and offload hashing. No new root-level artifact or custody path is introduced.
- Consumers locate the file from a run id the kit already knows, confined to the runs root, so no arbitrary path is followed.
- The config digest binds "who wrote it". Journal recomputation binds "what it says": the medians must follow from member 5's append-only 1 Hz journal. Together they detect a stale file from another window or attempt, edited values, and a substituted source.
- A physical failure (unobserved) is kept apart from an integrity failure (refuse). This matches the council: an unobserved state gives a timed wait plus X4, and a custody break means the reference does not exist.

### Implementation consequences
- **WP15** (`thermal_gates.py`, `workload.py`):
  - `validate_gate_policy` requires the role form and retires inline temperatures;
  - add `write_window_reference(context, …)` and `load_window_reference(policy, context)` raising `WindowReferenceRefused(code)`;
  - `capture_reference` takes `context`;
  - `prepare` calls the loader before `runtime.prepare`;
  - `record()` includes `custody`;
  - update `thermal_gates.md` (replace "Kit v4 must persist that reference…") and remove the inline form from its example.
- **WP16** (`align_v4_kit.py`):
  - the first sidecar member by ordinal (W1: e05) gets `{"role": "capture"}`;
  - every other thermal member (contrast S and G arms and D, in both stages) gets `consume` with `source_run_id` = that member's run id and `source_config_sha256` computed from that member's generated config by the library function above;
  - anchors carry no `thermal`.
  - `--check` asserts:
    - exactly one capture member, and it is the first thermal ordinal;
    - every consumer's digest matches an independent recomputation;
    - the sensor maps are identical across thermal members.
  - Changing member 5's config (e.g., after R1 fills its slots) regenerates every consumer. That is expected.
  - In D_k windows the early sentinel at ordinal 5 is the capture member.
- **WP17.** The R1 window uses the same mechanism. R1's first sidecar member is its capture member, and the R1 rehearsal must exercise one consumer in a second `run_campaign` stage.
- **Desk (B9/WP21, noted for completeness).** For each window, check:
  - exactly one capture member;
  - all consumers cite the same `record_sha256`;
  - R recomputes from the final source journal.

  Any mismatch sets `instrument_ok` false.
- **WP20.** Replace PENDING-RULING WP14(b) with this section.

### Tests that must exist
In `tests/align/test_window_reference_custody.py` (mock runtime, fake SMC and clock):
1. **Capture writes a valid file.** Schema valid, `record_sha256` valid, medians equal the in-memory reference. A second write to the same bundle refuses, and no file is ever overwritten.
2. **Capture below 90 % coverage** writes `unobserved` with null values. The consumer proceeds: G0 does the timed unobserved wait, and both `thermal.window_reference_unobserved` and `thermal.state_unobserved` are flagged. No fresh capture happens.
3. **A valid consumer** uses exactly the file's values, and `thermal.record()["custody"]` holds the record and journal digests.
4. **Each refusal** gives its own flag, the mock `runtime.prepare` is never called, and no `align_window_reference.json` is created in the consumer's bundle:
   - missing file;
   - a one-bit flip in `fast_c` (corrupt);
   - spec config digest ≠ file digest (binding);
   - file digest ≠ source `config.json` (binding);
   - sensors mismatch (binding);
   - a sample row absent from the source journal, or a median off by 1 ulp (unverified);
   - a symlinked file or bundle (path);
   - `source_run_id` of `../x` or equal to the member's own id (path).
5. `validate_gate_policy` refuses: a missing `window_reference`; `capture` with source fields; `consume` without both fields; and the inline temperature form.
6. **Identity readiness** (context None) reads no custody and opens no sensor.
7. **Cross-stage:** two `run_benchmark` invocations in separate processes, sharing one runs root, verify successfully. This simulates episodes-a → episodes-b.
8. **WP16** `test_v4_kit.py`: single capture at e05; consumer digests recomputed independently from the generated e05 config; anchors carry no thermal.

---

## (c) How ThermalRegistry reaches `run_benchmark`

### Question
`ThermalRegistry` must be the `registry=` for gated members. It binds `EpisodeRuntimeAdapter.thermal_status_reader` to the live powermetrics telemetry adapter (`PowermetricsStatus`). The question is how it reaches `run_benchmark`. The two candidates are an align-local entry point and a cited rebind of the pinned `run_campaign.py`.

### The call path in the code
- `scripts/run_campaign.py` never calls `run_benchmark` and never holds an adapter object. `command_for` (l.1566-1600) spawns a **fresh process** per member: `[cli_cmd or <python> -m joulewise] run <config> --runs-dir <root> …`. The prefix can be replaced only with `--cli-cmd`, which applies to the whole campaign stage, anchors included.
- In the member process:
  1. `joulewise/__main__.py` calls `cli.main`.
  2. `cli._cmd_run_body` calls `run_benchmark(config, runs_dir, clock, instrument_…, post_window_…)` (l.421) **with no `registry`**. The `repetitions > 1` branch calls `run_experiment`, also with no registry.
  3. `run_benchmark` falls back to `joulewise.adapters` when `registry is None` (controller l.286).
- `registry` is already a public Protocol seam on `run_benchmark` (`AdapterRegistry`, controller l.236). The CLI simply never sets it.
- A registry is a Python object. It can only be chosen **inside the member process**, and the only code between process entry and `run_benchmark` is `__main__.py` → `cli.py`. Rebinding `run_campaign.py` therefore cannot deliver it.

### Options
1. **An align-local entry point**, `--cli-cmd "python -m joulewise.align.…"`. **Rejected.**
   - To inject a registry it must either copy all of `_cmd_run_body` (about 120 lines: frozen cooldown anchor, instrument calibration, the dwell rule, hazard SIGTERM salvage, the repetitions branch), which drifts from the pinned CLI on a measurement path, or monkeypatch `cli.run_benchmark`, which fails the standard of plan ruling 4.
   - `--cli-cmd` is per stage, so the **anchors** would also launch through the new entry point, changing their process entry.
   - It is engineering around a gap rather than fixing it.
2. **A cited rebind of `run_campaign.py`.** Rejected: it is not on the object path, as shown above. It is also a number-bearing path (`NUMBER_BEARING_PATHS`), which would need an executing-review ledger row for no benefit.
3. **A rebind of `adapters/__init__.py`.** Rejected. The default registry is a stateless module. It resolves the runtime and the telemetry in separate calls, so binding them would need module-global state.
4. **A cited in-place fix of the pinned `joulewise/cli.py`, run verb only**, with the decision made by a small align-local selector. **Chosen.**

### Decision
- **New align-local module `joulewise/align/apple/registry_select.py`.** It imports only `json` at module level, and exposes `registry_for_config(config) -> ThermalRegistry | None`, which **never raises**.
  - It returns `ThermalRegistry()` only if all of these hold: `workload_profile.name == "align_episode"`; the `prompt_text` parses as JSON; and `thermal` is a mapping containing `"sensors"` (the gate map).
  - Every other config (anchors, every v3 config, sensor-only diagnostic thermal, unparseable text, non-align workloads) gets `None`. `thermal_gates` is imported lazily, and only in the gate-map case.
- **`cli._cmd_run_body`.** After `config` is loaded:

  ```python
  registry = None
  if config.workload_profile.name == "align_episode":
      # WP14(c) cited rebind: docs/align/council-2026-11-05/WP14-RULINGS.md
      from joulewise.align.apple.registry_select import registry_for_config
      registry = registry_for_config(config)
  if registry is not None and config.workload_profile.repetitions > 1:
      raise SchemaError("thermal gate cells require repetitions == 1 (fresh process per member)")
  ```

  Then pass `registry=registry` to the existing `run_benchmark(...)` call. With `None` it behaves exactly as before. Nothing else in `cli.py` changes.
- **Unchanged:** `run_campaign.py`, `controller.py`, `adapters/__init__.py`, `__main__.py`, `bundle.py` and `mlx_runtime.py`.
- **Citation and review.**
  - Cite the rebind at the call site, in the commit message, and in this document.
  - `cli.py` is not in `NUMBER_BEARING_PATHS`, so **no** `executing_reviews.json` row is required. Do not add `cli.py` to that tuple, because doing so would alter the b6 registration defaults.
  - The Opus executing review of WP15 must cover this hunk explicitly, and its paper is cited in the commit.
  - The `configs/pins/registry.json` entry `file@c27485347…:joulewise/cli.py` pins historical bytes and is untouched. The working `cli.py` already differs from those bytes by +60/−47 lines through earlier reviewed commits.

### Rationale
- This is the smallest change that puts the registry on the actual path. It fills a gap in the CLI, which never forwarded an existing public seam, in place. That is the "frozen is not sacred" standard.
- **v3 anchors stay byte-identical:**
  - their configs are untouched;
  - the selector returns `None` for them, so `run_benchmark` receives `registry=None`, the same default object, and the same adapter calls;
  - the process entry is still `python -m joulewise run`.
- Gated members get the registry wherever they are launched (`run_campaign`, R1, or by hand), so there is no second, hidden route to execution.

### Implementation consequences
- **WP15.** Add `registry_select.py` and the `cli.py` hunk. Extend `tests/align/test_measurement_core_boundary.py` with whole-file SHA-256 assertions that `scripts/run_campaign.py`, `joulewise/controller.py`, `joulewise/adapters/__init__.py`, `joulewise/__main__.py` and `joulewise/bundle.py` equal their bytes at the WP6 head.
- **WP16.** Nothing to wire. The kit must not set `--cli-cmd` in any v4 stage `argv_template`, and `--check` refuses one if present.
- **WP17.** The R1 window runs through the same CLI and needs no launcher-specific registry code. The rehearsal asserts that the gated members' bundles record a bound status reader, i.e. that `PowermetricsStatus` observations appear in the thermal record.

### Tests that must exist
1. `test_registry_select.py`:
   - `None` for: all four anchor configs (committed bytes of a-e01..e04); every committed `align_pilot_v3` config; a sensor-only thermal spec; malformed `prompt_text`; a non-align workload. For these cases `joulewise.align.apple.thermal_gates` is not imported (checked via `sys.modules` in a subprocess).
   - `ThermalRegistry` for a gate-map D spec.
2. `test_cli_registry_selection.py`, patching `joulewise.cli.run_benchmark` and calling `cli.main(["run", cfg, "--runs-dir", tmp])`:
   - an anchor-shaped config → called with `registry=None`;
   - a gated config → called with a `ThermalRegistry` instance;
   - all other kwargs identical between the two calls.
3. A gated config with `repetitions = 2` → `SchemaError` and no bundle directory.
4. The extended `test_measurement_core_boundary` (above).
5. WP2's existing acceptance still holds: `scripts/align_pilot_kit.py --check` is clean, and `plan_tree.json`, `identity_pins.json` and `local_file_verification.json` are byte-identical to `83e2dac59`.

---

## Supersession summary

| Document / code | What changes |
|---|---|
| FINAL-DESIGN §2.6 "Sensors" | t63 is measured against ΔT60; disjoint die and heatsink classes; heatsink floor τc > 30 s. Everything else stands. |
| Amendment 1 §A5 R0.3 | The bar = the v4 classifier finds at least one die and one heatsink candidate, plus readability. The R0 step profile is 300/900/600 s (unchanged from the R0 ruling). |
| `docs/align/r0_step_test_ruling.md` | Selection bullets (S_fast τ < 30 s; S_slow τ ∈ (120, 900) s) are superseded. The profile and its refusal are retained, with the new reason (3 × the 300 s τ ceiling). |
| `r0_step.rank_response` | Diagnostic only, under `exponential_fit_diagnostic`. |
| `thermal_gates.validate_gate_policy` inline `window_reference` | Retired. Replaced by the `capture`/`consume` roles and the custody file. |
| `joulewise/cli.py` `_cmd_run_body` | Cited rebind: forwards the `registry` chosen by `registry_select`. |
| `scripts/run_campaign.py` | No change. |
