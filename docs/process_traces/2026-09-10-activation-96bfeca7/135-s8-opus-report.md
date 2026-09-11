# 135 — S8 (implementation): derivation-night desk inputs writer

Lane ACCEPTANCE-EPOCH-25G83-01. Worktree
`/Users/edr/code/JouleWise-wt-s8-night-inputs`, branch
`feat/2026-09-10-derivation-night-inputs`, HEAD `d18bc2b3`. No git state
changed; both files are untracked and left for the lead to commit.

## What landed

`scripts/write_derivation_night_inputs.py` (new, 320 lines)

| Clause | file:line |
| --- | --- |
| Module docstring = the `--help` body; glosses derivation night / identity epoch / T1 bindings / stale field before first use | :1-41 |
| Import of the canonical names and serializer (`IDENTITY_EPOCH_NAME`, `T1_BINDINGS_NAME`, `_json_bytes`, `_sha256_bytes`) | :53-68 |
| `_derive_planned_vectors` — deferred, call-time import of the writer's own helpers, then the six-field epoch + `_planned_t1_bindings` | :77-115 |
| `_refuse_incomplete_vector` — exact field set + non-empty, for both vectors | :117-136 |
| `_stale_identity_fields` — stale list from the live preflight's own comparison; refusal when nothing differs | :138-180 |
| `_resolved_out_dir` — `--out-dir` must be an existing directory | :182-191 |
| `_refuse_overwrite` — existing file is a refusal without `--force` | :193-203 |
| `write_night_inputs` — empty `--power-policy` refusal, then every refusal before either write (no half pair) | :205-237 |
| `_build_parser` — `--out-dir/--power-policy/--acceptance/--force`, paste-format epilog | :239-294 |
| `main` — refusal → `refused: …` on stderr, rc 2; success → 1 diagnostic line + the 2 fixed paste lines, rc 0 | :296-317 |

`tests/test_write_derivation_night_inputs.py` (new, 13 tests, all defect-named).

Output format (verified live at the desk on the real 25G83 machine):

```
stale identity fields vs /…/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json: os_build
IDENTITY_EPOCH_JSON=/tmp/s8-smoke/identity-epoch.json sha256=b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607
T1_BINDINGS_JSON=/tmp/s8-smoke/t1-bindings.json sha256=8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98
```

The variable names match `docs/phase_2/window_runbook.md:206`'s
`IDENTITY_EPOCH_JSON`, so the two lines paste as shell assignments.

## Import table — every value comes from the writer's own source

| Imported | From | Why it is the writer's own source |
| --- | --- | --- |
| `_sysctl_identity` | `scripts.validate_powermetrics_fiducial` | The identical call the live producer makes (`generate_g2a_probe_inputs._derive_live_vectors` :655-656): `kern.osversion`, `hw.model` |
| `SAMPLING_INTERVAL_MS`, `RESIDUAL_REGION_METHOD`, `PROTOCOL_ID` | same module | The three non-machine epoch fields are the writer's module constants, not literals; a constant change moves both this script and the writer together |
| `_planned_t1_bindings` | same module | The single projection of capture-time T1 bindings; also the one the writer itself calls at `validate_powermetrics_fiducial.py:2003`. Sampler digest and protocol digest are computed inside it, by its own `sha256_path` |
| `_derive_preflight_systematic_screen_s` + `_AcceptancePreflightError` | same module | The live preflight's own epoch comparison (`:395-408`). Stale fields are read out of its `acceptance_artifact_epoch_mismatch` context, so the diagnostic cannot drift from the check the night actually fails |
| `mlx.core.__version__` via `importlib.import_module` | runtime | Same lookup and same `getattr(..., None)` default as the producer (:665-670) |
| `_json_bytes`, `_sha256_bytes`, `IDENTITY_EPOCH_NAME`, `T1_BINDINGS_NAME` | `scripts.generate_g2a_probe_inputs` | Canonical serialization (`indent=2, sort_keys=True`, trailing newline) and the canonical file names `identity-epoch.json` / `t1-bindings.json` |
| `IDENTITY_EPOCH_FIELDS`, `T1_FIELDS` | `joulewise.calibration_ledger` | The ledger's own field tuples |
| `CHAIN_POWER_POLICY` | `scripts.gen_derivation_night` | The generator's own `ac_high_power`, so the default cannot diverge from what it enforces |

The imports inside `_derive_planned_vectors` / `_stale_identity_fields` are
deferred to call time (the producer's pattern), which is also what lets the
tests patch the writer's module attributes and reach this script.

Deliberately NOT reused: `_derive_live_vectors` itself and
`_authenticate_ledger_and_acceptance`. The former calls
`_derive_preflight_systematic_screen_s(planned_epoch)` as a **gate** and so
raises `acceptance_artifact_epoch_mismatch` on exactly the epoch change a
derivation night exists for; the latter opens the ledger. This script calls
the same preflight but treats that refusal as the expected signal, and never
opens the ledger (no `read_replay`, so no allowlist row was needed — the
fixture was not touched).

## Cut table (mutation, one test each, source sha256-restored)

Source sha256 before and after: `e6a0ccc49e5fe9f086d1d181d8bc0865304cd6b88ca291b65db0090a17f226cc` — RESTORED.

| Cut | Test | Result |
| --- | --- | --- |
| drop `pulse_protocol_id` from the epoch | `test_writes_exactly_the_six_scalar_identity_fields_and_the_t1_superset` | KILLED rc=1, Ran 1 |
| `json.dumps(...)` instead of `_json_bytes` | `test_bytes_are_the_probe_generator_canonical_serialization` | KILLED rc=1, Ran 1 |
| print the identity digest on the T1 line | `test_printed_sha256_lines_match_the_written_files` | KILLED rc=1, Ran 1 |
| overwrite guard always returns | `test_refuses_an_existing_file_without_force_and_rewrites_with_force` | KILLED rc=1, Ran 1 |
| none-differ refusal becomes `return []` | `test_refuses_when_no_identity_field_differs_from_the_acceptance` | KILLED rc=1, Ran 1 |
| empty `--power-policy` check disabled | `test_refuses_an_empty_power_policy` | KILLED rc=1, Ran 1 |
| `--out-dir` existence check disabled | `test_refuses_when_the_out_dir_does_not_exist` | KILLED rc=1, Ran 1 |
| T1 completeness check removed | `test_refuses_when_the_mlx_version_is_absent` | KILLED rc=1, Ran 1 |
| default power policy `"battery"` | `test_written_files_pass_the_wrapper_generator_validators` | KILLED rc=1, Ran 1 |
| `description=__doc__` → one-liner | `test_help_glosses_every_term_of_art_at_first_use` | KILLED rc=1, Ran 1 |
| add a `DEFAULT_LEDGER_PATH` import | `test_never_reads_or_writes_the_calibration_ledger` | KILLED rc=1, Ran 1 |

11 of 13 tests carry a cut. The two structural guards without one —
`test_module_imports_the_writers_own_helpers_rather_than_copying_them` (which
does also assert, through a patched `_sysctl_identity`, that the patch reaches
this script's output) and `test_script_module_is_importable_by_path_…` — are
existence assertions whose only mutation is deleting the feature they assert.

## Runs

CI-independence (the lane's two CI-only defects came from real-machine reads):
every test mocks `_sysctl_identity`, the sampler digest (selectively — the
tracked protocol file keeps its real digest) and `mlx.core`, and the whole
module passes under the **system python3 that has no MLX installed**:

```
Ran 13 tests in 0.024s
OK
```

`python3 -m compileall -q scripts` → rc 0.

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest \
    tests.test_write_derivation_night_inputs tests.test_gen_derivation_night \
    tests.test_custody_mode_inventory tests.test_docs_freshness \
    tests.test_git_fixture_maintenance
Ran 96 tests in 46.799s
OK
rc=0
```

Live desk smoke (real machine, project venv interpreter): rc 0, stale field
`os_build` (`25G83` vs the acceptance's `25F84`), both files written with the
digests quoted above; `mlx_version 0.31.2`, `powermetrics_sha256
b762e5bf…30c5`.

Footprint (`git status --short`):

```
?? scripts/write_derivation_night_inputs.py
?? tests/test_write_derivation_night_inputs.py
```

## Decisions

1. **File names are hyphenated** — `identity-epoch.json`, `t1-bindings.json`,
   taken from `generate_g2a_probe_inputs.IDENTITY_EPOCH_NAME/T1_BINDINGS_NAME`
   and `docs/phase_2/window_runbook.md:206`. **Finding for the lead:**
   `gen_derivation_night.py`'s own `--help` worked example (:764-765) and
   `docs/process_traces/2026-09-01…/SHAKEDOWN-G2-RUNSHEET.md:1700,1776` use
   the UNDERSCORE spelling `identity_epoch.json` / `t1_bindings.json`. An
   operator pasting that example after running this script gets "a pinned
   input is unreadable" at arm time. Both are outside WRITE_SCOPE; the paste
   lines emit absolute paths, which is the mitigation available here.
2. **Acceptance read is a gate for one case only.** Nothing stale → refusal
   (the brief's requirement). If the acceptance cannot be authenticated for
   any *other* reason (not issued, stale estimator pin, unreadable), the
   script also refuses, because it then cannot establish a stale field at all;
   the refusal prints the preflight's reason and points at `--acceptance`.
3. **Both files are written only after every refusal passes**, so a refusal
   never leaves half a pair for a later run to pin. Asserted in the
   force/overwrite test.
4. **Extra clause beyond the brief:** both vectors are refused when any field
   is empty or `None`. Concretely, an interpreter without MLX yields
   `mlx_version = None`, which the night's reserve step refuses — better a
   desk refusal than a burned night. This bit in practice: the worktree's
   default `python3` has no MLX, so this script must be run with the project
   venv interpreter (`/Users/edr/code/JouleWise/.venv/bin/python`, the
   runbook's `$PY`); otherwise it refuses with
   `machine vector derivation failed: ModuleNotFoundError: No module named 'mlx'`.
   Worth one line in the arm materials.
5. `configs/calibration` untouched, no ledger access, no powermetrics
   execution, no `[QUIET-MAC]` activity. The desk smoke wrote only to
   `/tmp/s8-smoke`.
