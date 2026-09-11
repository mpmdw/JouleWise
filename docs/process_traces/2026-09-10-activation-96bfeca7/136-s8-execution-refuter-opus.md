# 136 — S8 EXECUTION-LENS refuter (Opus)

Worktree `/Users/edr/code/JouleWise-wt-s8-night-inputs`, branch
`feat/2026-09-10-derivation-night-inputs`, HEAD `ba106c1f`, base `d18bc2b3`.
Read-only except three mutation cut rounds, each restored byte-for-byte
(`PYTHONDONTWRITEBYTECODE=1`, sha256 before == after, recorded below). No git
state changed. No live capture, no `[QUIET-MAC]` work, no sudo. Canonical
`/Users/edr/code/JouleWise` and `/Users/edr/night-custody` untouched.

## VERDICT: MERGEABLE AFTER FIXES

The load-bearing non-divergence claim is **TRUE and executed** — the desk
writer's bytes are byte-identical to what the capture-time path produces, and
its stale-field diagnostic is literally the night's own d01 comparison. Every
brief-enumerated refusal fires, writes nothing, and is killed by a cut. The
five test modules pass (205 tests, rc 0) and the module is CI-safe.

Two SHOULD-FIX items, both bench-sized (one 1-line import, two small tests),
plus one doc follow-up outside this diff. No blockers.

---

## 1. NON-DIVERGENCE — PROVEN (by construction and by execution)

### By construction: same functions, same call shape

| Value | Capture-time producer | Desk writer |
| --- | --- | --- |
| `os_build` | `validate_powermetrics_fiducial.py:1906-1907` `_sysctl_identity("kern.osversion")` | `write_derivation_night_inputs.py:95` same |
| `hardware_model` | `:1908-1909` `_sysctl_identity("hw.model")` | `:96` same |
| `power_policy` | `:1910` `args.power_policy` (chain hardcodes `ac_high_power`, `gen_derivation_night.py:177-180,222-225`) | `:97`, default `CHAIN_POWER_POLICY` imported from the generator (`:62`, `:264-269`) |
| `sampling_interval_ms` / `estimator_revision` / `pulse_protocol_id` | `:1911-1913`, the writer's own module constants | `:98-100`, **imported** from the same module (`:86-92`) |
| T1 block | `:2003-2007` `_planned_t1_bindings(planned_epoch=…, sampler_binary=args.sampler_binary, mlx_version=getattr(mx,"__version__",None))` | `:103-107` same helper, same kwargs |
| `powermetrics_sha256`, `protocol_sha256` | computed INSIDE `_planned_t1_bindings` (`:765-776`) by its own `sha256_path` | same — not recomputed here |
| `mlx_version` | `:1995` `import mlx.core as mx`; `:2006` `getattr(mx,"__version__",None)` | `:102,106` `importlib.import_module("mlx.core")`, same `getattr` default |

The imports are deferred to call time (`:86-92`, `:149-152`) exactly as
`generate_g2a_probe_inputs._derive_live_vectors:641-666` does, so a constant
change in the writer moves this script with it. Nothing is restated as a
literal **except the sampler path** — see F2.

### By execution: byte-for-byte identity

```
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B \
    scripts/write_derivation_night_inputs.py --out-dir /tmp/s8ref/out
stale identity fields vs …/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json: os_build
IDENTITY_EPOCH_JSON=/tmp/s8ref/out/identity-epoch.json sha256=b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607
T1_BINDINGS_JSON=/tmp/s8ref/out/t1-bindings.json     sha256=8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98
rc=0
```

Then, in-process, I rebuilt the **capture-time** vectors from the writer's own
helpers — reproducing `validate_powermetrics_fiducial.py:1905-1914` and
`:2003-2007` verbatim, including `sampler_binary=Path(POWER_METRICS)` (the
`--sampler-binary` default, `:1717-1721`) rather than the desk script's own
constant — and diffed the serialized bytes against the files on disk:

```
POWER_METRICS = '/usr/bin/powermetrics'
identity bytes equal: True  b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607
t1 bytes equal:       True  8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98
```

**Diff output: EMPTY on both vectors.** (The unified-diff branch never ran.)

`shasum -a 256` on the written files reproduces both printed digests exactly:

```
b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607  /tmp/s8ref/out/identity-epoch.json
8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98  /tmp/s8ref/out/t1-bindings.json
```

### The generator accepts both files

```
$ … -c "import scripts.gen_derivation_night as g; g._validated_identity_epoch(…); g._validated_json_object(…)"
identity epoch ACCEPTED: ['estimator_revision','hardware_model','os_build','power_policy','pulse_protocol_id','sampling_interval_ms']
t1 ACCEPTED: ['anchor_method_version','estimator_revision','hardware_model','mlx_version','os_build','power_policy','powermetrics_sha256','protocol_sha256','pulse_protocol_id','sampling_interval_ms']
```

Six keys == `IDENTITY_EPOCH_FIELDS` (`joulewise/calibration_ledger.py:110-117`);
ten keys == `T1_FIELDS` (`:118`).

---

## 2. STALE-FIELD DIAGNOSTIC — the refusal's `context` does carry the list, and
## the comparison IS the night's own

`_AcceptancePreflightError.__init__` stores `**context` as `self.context`
(`validate_powermetrics_fiducial.py:357-364`); the epoch branch raises
`_AcceptancePreflightError("acceptance_artifact_epoch_mismatch",
stale_fields=stale_fields)` at `:399-408`. The desk script reads exactly that
(`write_derivation_night_inputs.py:166`).

**Stronger than the seat claimed:** the night's own derivation-only gate
(`validate_powermetrics_fiducial.py:1917-1941`) computes its stale list from
`_derivation_only_screen_basis()["epoch"]` with the identical comprehension,
and `_derivation_only_screen_basis` (`:497-535`) is the SAME
`_derive_preflight_systematic_screen_s` with `identity_epoch=None` — i.e. every
authentication check identical, epoch equality skipped. So the desk refusal
("nothing stale ⇒ ORDINARY night") is bit-for-bit the night's
`DERIVATION_ONLY_EPOCH_UNCHANGED` test. The diagnostic cannot drift.

**Executed refusals (nothing written in any case):**

| Case | Command | Result |
| --- | --- | --- |
| Machine epoch == acceptance | `mocked_machine(os_build=ACCEPTANCE_EPOCH["os_build"])` via `tests…test_refuses_when_no_identity_field_differs_from_the_acceptance` | rc 2, `no identity field differs … ORDINARY night`, `sorted(Path(raw).iterdir()) == []` |
| Corrupted acceptance (`printf '{ not json'`) | `--acceptance /tmp/s8ref/corrupt.json` | rc 2, `refused: the acceptance at … could not be read as an issued artifact (acceptance_artifact_unauthenticated) …` — **refuses, does not crash**; `/tmp/s8ref/out2` empty |
| Absent acceptance | `--acceptance /tmp/s8ref/nope.json` | rc 2, `… (acceptance_artifact_missing) …`; out dir still empty |

No partial pair in any refusal: every check runs before either
`write_bytes` (`:216-226`, comment at `:223-224`).

---

## 3. CUT TABLE (killed)

Source `scripts/write_derivation_night_inputs.py`
sha256 before **and after** all rounds:
`e6a0ccc49e5fe9f086d1d181d8bc0865304cd6b88ca291b65db0090a17f226cc` — RESTORED.
`scripts/issue_calibration_acceptance_generation.py` before/after:
`2b35e28af8d228528cf079f75b30b3dda2ef81e8e2d33836810b245c5a6256a8` — RESTORED.

| # | Cut (single term) | file:line | Test | Result |
| --- | --- | --- | --- | --- |
| C1 | `if force:` → `if force or True:` | `:194` | `test_refuses_an_existing_file_without_force_and_rewrites_with_force` | **KILLED** Ran 1, FAILED (failures=1) |
| C2 | `if not out_dir.is_dir():` → `if False and …` | `:184` | `test_refuses_when_the_out_dir_does_not_exist` | **KILLED** Ran 1, FAILED (errors=1) |
| C3 | empty-policy guard → `if False:` | `:210` | `test_refuses_an_empty_power_policy` | **KILLED** Ran 1, FAILED (failures=1) |
| C4 | `empty = sorted(… in (None, ""))` → `empty = []` | `:129` | `test_refuses_when_the_mlx_version_is_absent` (`mlx_version None`) | **KILLED** Ran 1, FAILED (failures=1) |
| C5 | none-differ refusal → early `return ["os_build"]` | `:173` | `test_refuses_when_no_identity_field_differs_from_the_acceptance` | **KILLED** Ran 1, FAILED (failures=1) |
| C6 | `RULED_ALTERNATIVE_CORPUS_SIZE = ENVELOPE_MINIMUM_CORPUS_N` → `= 17` | `issue_calibration_acceptance_generation.py:379` | `PrepareCandidateTest.test_the_ruled_alternative_floor_has_one_home` | **KILLED** Ran 1, FAILED (failures=1) |

`ENVELOPE_MINIMUM_CORPUS_N == 17` confirmed by import, so C6 is behaviour-neutral
and the test is a pure source pin — correct for a one-home guard.

### Survivor cuts (coverage gaps — see F2, F3)

| # | Cut | Whole module (13 tests) |
| --- | --- | --- |
| S1 | `if getattr(exc,"reason",None) != "acceptance_artifact_epoch_mismatch":` → `if False:` (`:159`) | **SURVIVED** — Ran 13, OK |
| S2 | `SAMPLER_BINARY = Path("/usr/bin/powermetrics")` → `Path("/bin/ls")` (`:70`) | **SURVIVED** — Ran 13, OK |

---

## 4. CI SAFETY — PASS

- MLX-free modern interpreter (`/opt/homebrew/bin/python3`, 3.14.7,
  `import mlx` → `ModuleNotFoundError`): `Ran 13 tests in 0.014s / OK`.
- `/usr/bin/python3` is 3.9.6 and cannot import `joulewise.calibration_ledger`
  at all (`joulewise/calibration_ledger.py:3128`, PEP-604 alias) — a
  **pre-existing repo-wide floor**, not a seat defect. CI pins 3.11/3.14
  (`.github/workflows/ci.yml:22,128,192`).
- `grep` for real-machine reads in `tests/test_write_derivation_night_inputs.py`:
  the only hits are `script.SAMPLER_BINARY` inside the mock's dispatch (`:57`)
  and the two `patch.object(validation_script, "_sysctl_identity", …)` sites
  (`:70`, `:277`). **No `subprocess`, no `importlib.import_module`, no literal
  `/usr/bin/powermetrics`, no unmocked `sysctl`.** `mocked_machine` (`:45-81`)
  patches `sys.modules["mlx.core"]`, `_sysctl_identity`, and `sha256_path`
  selectively — the tracked protocol file keeps its real digest, which is
  necessary or the acceptance preflight would refuse for the wrong reason.
  The two module-level reads are of tracked repo files
  (`ACCEPTANCE_PATH.read_text`, `:36`) — clone-safe.

---

## 5. SERIALIZATION / NAMES — PASS

- Bytes equal `generate_g2a_probe_inputs._json_bytes(dict)` (asserted at
  `tests:123-127`; independently reproduced in §1's in-process diff).
- Printed digests match `shasum -a 256` (§1).
- Exactly 3 stdout lines; line 2 begins `IDENTITY_EPOCH_JSON=`, line 3
  `T1_BINDINGS_JSON=` (`script.py:313-315`) — the runbook's own export names
  (`SHAKEDOWN-G2-RUNSHEET.md:1776-1777` post-commit). Both are absolute paths,
  so the two lines paste as shell assignments.
- Filenames are `IDENTITY_EPOCH_NAME` / `T1_BINDINGS_NAME` imported from
  `generate_g2a_probe_inputs` (`:63-68`, used at `:218-219`), which resolve to
  the hyphenated `identity-epoch.json` / `t1-bindings.json` — confirmed by the
  files on disk and by the generator's example after the bench commit.

---

## 6. BENCH COMMIT — PASS

- C6 above kills the one-home cut.
- `scripts/gen_derivation_night.py --check` → `PASS generated derivation-night
  wrapper region matches`, rc 0 (the regenerated runsheet region is in sync).
- Underscore-spelling sweep, exactly the brief's three targets:
  `grep -rn --include='*.py' -e 'identity_epoch\.json' -e 't1_bindings\.json'
  scripts/` → **zero**; `docs/phase_2/` → **zero**;
  `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` →
  **zero**. Clean.
- The `ENVELOPE_MINIMUM_CORPUS_N` import is inserted out of alphabetical order
  in the import block (`issue_calibration_acceptance_generation.py:84-86`:
  `ACTIVE_ACCEPTANCE_ID, ENVELOPE_MINIMUM_CORPUS_N, ACCEPTANCE_BOUND_SCHEMA`).
  Cosmetic; `ruff`'s isort rules are not enabled on this block. **NIT.**

---

## 7. `--help` FIRST-USE TEST — PASS

Full `--help` rendered and read. *Derivation night* is built from physical
reality before first use (macOS updated ⇒ the ratified numbers were measured on
a machine that no longer exists). *Identity epoch* is glossed AT first use with
all six fields named in plain words and the pooling rule stated. *T1 bindings*
is glossed as "the identity epoch plus the four execution pins", all four
named. *Stale field* gets its own paragraph with the refusal rule and its
reason. The output contract appears verbatim in the epilog. The `--acceptance`
help re-glosses STALE FIELDS at its own first use.

Residual: "in force" and "pooled" are used unglossed, but both read plainly in
context. No ask-worthy defect found.

---

## 8. TEST RUN — PASS

```
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest \
    tests.test_write_derivation_night_inputs tests.test_gen_derivation_night \
    tests.test_issue_calibration_acceptance_generation tests.test_custody_mode_inventory \
    tests.test_docs_freshness
Ran 205 tests in 101.333s
OK
rc=0
```

---

## FINDINGS

### SHOULD-FIX

**F1 — `SAMPLER_BINARY` is a second home for the sampler path, and no test
guards it.** `scripts/write_derivation_night_inputs.py:70` restates
`Path("/usr/bin/powermetrics")` instead of importing
`validate_powermetrics_fiducial.POWER_METRICS` (`:57`, the value behind
`--sampler-binary`'s default at `:1717-1721`). Today the two agree, so §1's
byte diff is empty. But this is the ONE value in the whole script that is a
literal rather than an import, and it feeds `powermetrics_sha256` — the single
field whose divergence produces a T1 mismatch discovered only at reserve time,
mid-night. Cut S2 (`→ Path("/bin/ls")`) **survives all 13 tests**, and it
survives because `mocked_machine:57` keys the sampler mock off
`script.SAMPLER_BINARY` itself, so the test follows the defect.
*Fix (1 line + 1 assert):* `from scripts.validate_powermetrics_fiducial import
POWER_METRICS` at call time in `_derive_planned_vectors`, set
`SAMPLER_BINARY = Path(POWER_METRICS)`, and assert
`script.SAMPLER_BINARY == Path(validation_script.POWER_METRICS)` in the
existing one-home test. This is exactly the fix the lead just applied to
`RULED_ALTERNATIVE_CORPUS_SIZE` in the same commit.
*Repro:* `sed -i '' 's|/usr/bin/powermetrics|/bin/ls|' scripts/write_derivation_night_inputs.py && python -B -m unittest tests.test_write_derivation_night_inputs` → `Ran 13 … OK`.

**F2 — the unauthenticated-acceptance refusal branch has no regression.**
`scripts/write_derivation_night_inputs.py:158-165` is the branch that turns
every non-epoch preflight failure into a named desk refusal; I confirmed by
execution that it fires (§2, corrupt + missing acceptance). Cut S1 (`:159` →
`if False:`) **survives all 13 tests**. Under that cut an unauthenticated
acceptance still exits 2, but with the misleading message "reported an epoch
mismatch without naming a field", pointing the night operator at the wrong
problem at 02:00. Also, **no test passes `--acceptance` at all** — the flag's
plumbing is exercised only through its default.
*Fix (1 test):* write a bad-JSON file into the tmp dir, run with
`--acceptance` pointed at it, assert rc 2 and
`"could not be read as an issued artifact"` in stderr and an empty out dir.

### NITS

**N1 — the operator runbook still carries the underscore spelling and the
`[UNVERIFIED: which tool produces …]` marker this seat resolves.** Outside the
brief's scope-6 targets (those are clean) and outside this diff, but it is the
doc the 09-11/09-12 arm is driven from:
`docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md:349-350,
356-357, 522-523, 584-585, 1345-1346`. An operator pasting §step-3's command
after running this script gets `identity epoch json is missing` from
`gen_derivation_night.py` — a loud refusal, not a wrong pin, so this is
friction rather than an evidence hazard. §0.8's `[UNVERIFIED: … is the
producer `generate_g2a_probe_inputs.py bind-window` … or a third desk tool?]`
is now answered by this seat and should be closed in the same pass.

**N2 —** `write_derivation_night_inputs.py:149-152`: the deferred import in
`_stale_identity_fields` is not inside a `try`, unlike the one in
`_derive_planned_vectors:85-111`. An import failure there is a raw traceback
rather than a named `refused:` line. Cosmetic on a path that cannot realistically
fail once `_derive_planned_vectors` has already imported the same module.

**N3 —** import ordering in `issue_calibration_acceptance_generation.py:84-86`
(see §6).

---

## WHAT I DID NOT FIND

No defect in the load-bearing claim. No partial write on any refusal path. No
ledger access (`test_never_reads_or_writes_the_calibration_ledger:231-242` pins
the absence of five ledger symbols in the source; I re-grepped and confirm).
No real-machine read in any test. No serialization divergence. No filename
divergence in the three swept trees. The seat's report 135 is accurate on every
claim I checked, including the 11-cut table's semantics and the live smoke
digests, which I reproduced independently (§1).
