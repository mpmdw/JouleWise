# Pilot-4 verification journal

Every unittest invocation during implementation is recorded below. Commands use a fresh TMPDIR. All cwd values are `/Users/edr/code/jw-wt/align-pilot4`. The final source tree is uncommitted. Source logs are temporary; their tails and SHA-256 receipts are promoted here. Earlier failures are superseded by the final focused runs. The first combined run used the original test expectations while the v3 migrations were still in progress; it also exposed the detokenizer test's pre-existing top-level import requirement, fixed by adding the tests directory to PYTHONPATH without editing that module.

## T1: p4-focused.8EixlQ

```sh
P4_TMP=$(mktemp -d /tmp/p4-focused.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.align.test_pilot4 > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -80 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 9 tests in 4.915s

FAILED (errors=1)
```

Source: `/tmp/p4-focused.8EixlQ/tests.log`; SHA-256 `f5336be5953d61d37c75bd7af20022b7eecfa7c808f818936243874696854511`.

## T2: p4-focused.EAZoBH

```sh
P4_TMP=$(mktemp -d /tmp/p4-focused.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.align.test_pilot4 > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -45 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 9 tests in 6.710s

FAILED (failures=1)
```

Source: `/tmp/p4-focused.EAZoBH/tests.log`; SHA-256 `323c1e25f82964d3a5dd8801b7c0ebb84fbee5299f5ae9d8ae137ceeb046303f`.

## T3: p4-baseline.fIElWm

```sh
P4_TMP=$(mktemp -d /tmp/p4-baseline.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_apple_endpoint tests.align.test_apple_campaign tests.align.test_pilot3 tests.test_align_pilot_session > "$P4_TMP/tests.log" 2>&1; tail -85 "$P4_TMP/tests.log"; exit ${pipestatus[1]}
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 87 tests in 237.714s

FAILED (failures=8, errors=5)
```

Source: `/tmp/p4-baseline.fIElWm/tests.log`; SHA-256 `5cfecd07e33979f1bb5ea8978c1187c3f4cee19537998bbccffa7547719180c6`.

## T4: p4-focused.keTsE7

```sh
P4_TMP=$(mktemp -d /tmp/p4-focused.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.align.test_pilot4 > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -16 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 9 tests in 7.279s

FAILED (errors=1)
```

Source: `/tmp/p4-focused.keTsE7/tests.log`; SHA-256 `3311fd2254178e746244d5a74a70c70a71a19e6b16da1a13e5935430fff86272`.

## T5: p4-fast.zIiN4I

```sh
P4_TMP=$(mktemp -d /tmp/p4-fast.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot4/tests:/Users/edr/code/jw-wt/align-pilot4 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_pilot4 tests.align.test_pilot3 tests.align.test_pilot3_cache > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -36 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 79 tests in 10.857s

FAILED (failures=2)
```

Source: `/tmp/p4-fast.zIiN4I/tests.log`; SHA-256 `b629c1206a653142ba8509a80f89ce255160af09b736f22138160f6b59221421`.

## T6: p4-fast.WwBdYN

```sh
P4_TMP=$(mktemp -d /tmp/p4-fast.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot4/tests:/Users/edr/code/jw-wt/align-pilot4 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_pilot4 tests.align.test_pilot3 tests.align.test_pilot3_cache > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -10 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 79 tests in 10.921s

OK
```

Source: `/tmp/p4-fast.WwBdYN/tests.log`; SHA-256 `89b3159fb7e663b19ea1a24348707a9febc7293f606e09b546295df381615e57`.

## T7: p4-known.P84lSv

```sh
P4_TMP=$(mktemp -d /tmp/p4-known.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.align.test_pilot4 > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -20 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 9 tests in 6.375s

FAILED (errors=1)
```

Source: `/tmp/p4-known.P84lSv/tests.log`; SHA-256 `aaaf07988842bb1e1ea6581e3345ebf54e07c9574fc6cb579c4056faed4ef3f1`.

## T8: p4-known.5uRmur

```sh
P4_TMP=$(mktemp -d /tmp/p4-known.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.align.test_pilot4.AnalysisTests.test_known_coefficients_loo_no_replay_leakage_transfer_and_tamper > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -22 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 1 test in 0.729s

OK
```

Source: `/tmp/p4-known.5uRmur/tests.log`; SHA-256 `fb4d1e56593a4f2fdac8ca411aa518a144ee70c4f3e3680e6e0b7f5e708fc809`.

## T9: p4-fast-final.6VWsW5

```sh
P4_TMP=$(mktemp -d /tmp/p4-fast-final.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot4/tests:/Users/edr/code/jw-wt/align-pilot4 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_pilot4 tests.align.test_pilot3 tests.align.test_pilot3_cache > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -10 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 79 tests in 6.598s

FAILED (failures=2, errors=2)
```

Source: `/tmp/p4-fast-final.6VWsW5/tests.log`; SHA-256 `aaad8e06b422602772b05327f398b497ad9669284ad688f778d50fd8539b184a`.

## T10: p4-analysis-final.Y21Vko

```sh
P4_TMP=$(mktemp -d /tmp/p4-analysis-final.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.align.test_pilot4 > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -16 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 10 tests in 2.680s

FAILED (failures=2, errors=2)
```

Source: `/tmp/p4-analysis-final.Y21Vko/tests.log`; SHA-256 `453a3e4340aba027eef34eac8daa5ca64753187f5470b32e72733ca7e753acc1`.

## T11: p4-fast-final.TmRpug

```sh
P4_TMP=$(mktemp -d /tmp/p4-fast-final.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot4/tests:/Users/edr/code/jw-wt/align-pilot4 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_pilot4 tests.align.test_pilot3 tests.align.test_pilot3_cache > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -12 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 80 tests in 10.774s

OK
```

Source: `/tmp/p4-fast-final.TmRpug/tests.log`; SHA-256 `f6c2350f7f4112ffff829801b19b83687a413b28405e40b544f90ec8627e5194`.

## T12: p4-analysis-final.E1v3bi

```sh
P4_TMP=$(mktemp -d /tmp/p4-analysis-final.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.align.test_pilot4 > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -17 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 11 tests in 7.170s

OK
```

Source: `/tmp/p4-analysis-final.E1v3bi/tests.log`; SHA-256 `6a8675b790d4acc95f2a4b1b55539d478eebaffd779284f99284d2a3c712060e`.

## T13: p4-endpoint.t5LZE3

```sh
P4_TMP=$(mktemp -d /tmp/p4-endpoint.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot4/tests:/Users/edr/code/jw-wt/align-pilot4 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.align.test_apple_endpoint tests.align.test_apple_campaign tests.test_align_pilot_session > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -30 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 36 tests in 233.014s

OK
```

Source: `/tmp/p4-endpoint.t5LZE3/tests.log`; SHA-256 `6cf0bbb849dace1486f0f89d39ab1e10198f84750808f1f2520539745bc1cf4a`.

## T14: p4-final-tests.bQ14B2

```sh
P4_TMP=$(mktemp -d /tmp/p4-final-tests.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot4/tests:/Users/edr/code/jw-wt/align-pilot4 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_pilot4 tests.align.test_pilot3 tests.align.test_pilot3_cache > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -9 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 81 tests in 10.662s

OK
```

Source: `/tmp/p4-final-tests.bQ14B2/tests.log`; SHA-256 `150f573418bb9a3f1000be3d153dae22546b49df3fb3f007579dd4c68e8ce40d`.

## T15: p4-seed-policy.7TyPGh

```sh
P4_TMP=$(mktemp -d /tmp/p4-seed-policy.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.align.test_pilot4 tests.align.test_pilot3_cache > "$P4_TMP/tests.log" 2>&1; P4_RC=$?; tail -9 "$P4_TMP/tests.log"; exit "$P4_RC"
```

Observed output tail:

```text
----------------------------------------------------------------------
Ran 23 tests in 7.436s

OK
```

Source: `/tmp/p4-seed-policy.7TyPGh/tests.log`; SHA-256 `0a3461b8fd1321ff56477d53a08ba260cf96c83aedf09d67dd3d70f2d35d408b`.

## Interpretation of intermediate failures

- Old v2 roster assertions (24 members, A/C, 49 total), old greedy-I4 names and old spec optional-field lists were migrated to v3 or redirected to the frozen v2 pack.
- The first synthetic sampled desk fixture reused one run ID; distinct fixture IDs fixed its copy collision.
- GPU-specific fit extraction correctly ignored mock-only power. The sampled fixture now declares explicitly synthetic GPU-labelled samples; unavailable uncertainty remains flagged and JSON-safe.
- A hand-authored known-coefficient bundle initially retained the mutually exclusive prompt_tokens field; clearing it made the real bundle reader accept the config.
- A core-loader helper was initially misspelled during hardening; the sampled tests caught it. Reseeding now uses the existing `_resolve_mlx_core` loader, preserving extension-cache safety.
- The collision fixture now uses a deliberately degenerate sampled distribution with correct per-turn seeds. Independent-seed equality alone leaves all sampler/accounting/replay checks passing.
- Final passing runs: 81 tests across runtime, detokenizer, pilot4, pilot3 and cache modules; 36 across endpoint, campaign and session modules; 23 sampler-policy/cache tests after binding seed inputs into identity. These are 117 distinct tests. No whole-suite invocation was made.

## Kit and sizing commands

```sh
P4_TMP=$(mktemp -d /tmp/p4-sizing.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /Users/edr/code/jw-wt/align-pilot4/configs/campaigns/align_pilot_v3/registration/derive_sizing.py --pilot-session /Users/edr/night-align/pilot-v2-20261103T035512Z
```

Tail: `derived pilot3 sizing evidence (no model work)`; exit 0.

```sh
P4_TMP=$(mktemp -d /tmp/p4-kitgen.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /Users/edr/code/jw-wt/align-pilot4/scripts/align_pilot_kit.py
```

Tail: `generated align pilot kit`; exit 0. The kit tests also generated to a fresh temporary output root and checked identical bytes.

```sh
P4_TMP=$(mktemp -d /tmp/p4-kit-check.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /Users/edr/code/jw-wt/align-pilot4/scripts/align_pilot_kit.py --check
```

Tail: `verified align pilot kit`; exit 0.

## Real pilot-3 desk

The executed helper is preserved byte-identically as `real_pilot3_desk.py` beside this journal. It copies session/plan/derived receipts into TMPDIR and reads source bundles and custody paths without writing them. It never harvests the source.

```sh
P4_TMP=$(mktemp -d /tmp/p4-realdesk.XXXXXX); TMPDIR="$P4_TMP" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot4 /opt/homebrew/bin/python3.13 -B /tmp/p4-real-desk.py > "$P4_TMP/desk.log" 2>&1; P4_RC=$?; tail -3 "$P4_TMP/desk.log"; exit "$P4_RC"
```

Tail:

```text
harvest_status: not_run
REAL_PILOT3_DESK_OK members=24 configurations=2 sampled_replays=not_evaluated
REPORT_PATH=/private/tmp/p4-realdesk.y3Hjqr/session/inspection/20261103T120217.984885Z-69gl_5zs/PILOT.json
```

Exit 0. The report records 18 registered-eligible members and 21 under the episode-scope alternative; replay spreads are empty. GPU MHz is present per turn. Benign greedy trajectories count once (A: one eligible benign trajectory, C: two), so these historical coefficients differ from the design reports' fits over three measurement copies. LOO and s_r are unavailable or zero-df where independent benign trajectories are insufficient; no sampled variance is inferred. The later final change makes the aggregate legacy sampler check `not_evaluated` instead of false; the focused greedy desk regression verifies that presentation.

## Installed seed binding inspection

The measurement interpreter was used only for imports/seed argument boundary inspection, never model loading or generation. Importing mlx_lm triggered the sandbox's `No Metal device available` error. A second probe importing only mlx.core (CPU default) found that 2^32−1, 2^32 and 2^64−1 pass integer argument conversion and reach Metal initialization, while 2^64 fails with TypeError. Installed `mlx_lm/sample_utils.py` was read directly: nonzero temp constructs a categorical sampler with top-p/min-p/top-k filtering. Native RNG success remains a rehearsal gate.

## Scope and whitespace inspection

```sh
git -C /Users/edr/code/jw-wt/align-pilot4 diff --check
git -C /Users/edr/code/jw-wt/align-pilot4 diff --exit-code HEAD -- configs/campaigns/align_pilot_v0 configs/campaigns/align_pilot_v1 configs/campaigns/align_pilot_v2 joulewise/flags joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/reduce.py joulewise/uncertainty_evidence.py joulewise/align/energy_residual.py
```

Both exit 0 with no output. No staging, commits, pushes, model loads, sudo, powermetrics processes or quiet-machine collection were performed.
