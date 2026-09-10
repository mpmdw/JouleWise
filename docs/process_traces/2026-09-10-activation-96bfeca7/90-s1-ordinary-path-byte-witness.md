# S1 ordinary writer path — byte witness (base 1e43d1cc vs HEAD 12f1d1cf)

Seat S1 witness, execution only. Verdict for the ordinary (non-`--derivation-only`)
writer path, bracket-kind slot, valid disposition: **IDENTICAL — every compared
artifact byte-for-byte equal across the two trees, including stdout and stderr,
with no timestamp stripping needed.**

Worktree `/Users/edr/code/JouleWise-wt-s1-writer-derivation` was used read-only
(no edits, no git state changes). It was clean at start and at end; all writing
happened under `/tmp/s1witness` and `/tmp/s1base`.

## 1. Trees

```
git -C /Users/edr/code/JouleWise-wt-s1-writer-derivation rev-parse HEAD
# 12f1d1cf4a5a3d9f4c9d94566b47b1dbbfb588c2
mkdir -p /tmp/s1base
git -C /Users/edr/code/JouleWise-wt-s1-writer-derivation archive 1e43d1cc | tar -x -C /tmp/s1base
```

Diff under witness (5 files): `scripts/validate_powermetrics_fiducial.py` (+189/-…),
`joulewise/calibration_exits.py`, `docs/contracts/calibration_ledger_append.md`,
`tests/test_calibration_exits.py`, and the new derivation-only test file.

## 2. Harness

Driver: `/tmp/s1witness/driver.py` (written for this witness). It reproduces the
shape of `tests/test_validate_powermetrics_fiducial_derivation_only.py ::
DerivationOnlyLiveCaptureTests` — synthetic repo copy, fixture sampler
(`tests/calibration_exits_fixtures/fake_sampler.py` via `--sampler-direct-for-test`),
fake `mlx.core`, acceptance re-key to the copied estimator bytes, and a bracket
session reserved through the public reservation API
`joulewise.calibration_ledger.append_bracket_session_receipt`. No live
powermetrics, no `sudo`.

Path-dependence control (the point of the exercise): every path is a FIXED
absolute path, identical for both runs, and re-created from scratch before each
run.

- synthetic repo: `/tmp/s1witness/repo` (rm -rf'd and rebuilt per run)
- ledger P: `/tmp/s1witness/repo/sessions/ord/ledger.jsonl`; head pin
  `/tmp/s1witness/repo/sessions/ord/head.json`
- output/custody root: `/tmp/s1witness/runs/instrument_validation` (rm -rf'd per run);
  slot custody `/tmp/s1witness/runs/instrument_validation/session-ord-pre`

Seed bytes: the ledger + pin were built ONCE (first run) and snapshotted to
`/tmp/s1witness/seed/`; every subsequent run copies those exact bytes into P
before invoking the writer. Seed identity is proved in the sha table below
(`ledger.jsonl` pre-run = `1d423a21…62` in all runs).

Determinism knobs (all identical across runs): `PYTHONDONTWRITEBYTECODE=1`,
`--time-scale-for-test 0.001` with `JW_FAKE_TIME_ORIGIN=1757000000.0` (the writer
seeds `_LogicalTestClock` from that env var, so every `clock.now()` timestamp is
logical and reproducible), `JW_FAKE_SAMPLER_ELAPSED_NS=200000`,
`JW_FAKE_SAMPLER_MODE=normal`, `--attempt-id` passed explicitly (otherwise
`validation_id` would be `strftime + uuid4`).

Identical argv for both trees (`/tmp/s1witness/out/*/argv.txt`, sha
`fa4f3f17…46` in all runs):

```
<python3> /tmp/s1witness/repo/scripts/validate_powermetrics_fiducial.py \
  --allow-live --power-policy ac_high_power \
  --ledger  /tmp/s1witness/repo/sessions/ord/ledger.jsonl \
  --head-pin /tmp/s1witness/repo/sessions/ord/head.json \
  --session-id session-ord --slot pre --attempt-id session-ord-pre \
  --output-root /tmp/s1witness/runs/instrument_validation \
  --sampler-binary /tmp/s1witness/repo/writer-fixtures/fake_sampler.py \
  --sampler-direct-for-test --time-scale-for-test 0.001 \
  --sampler-ready-timeout-s 30.0 --rollover-timeout-s 1.0 \
  --identity-epoch-json-for-test \
    /tmp/s1witness/runs/instrument_validation/session-ord-pre-identity.json
```

(no `--derivation-only` — this is the ordinary path.)

Commands run:

```
python3 /tmp/s1witness/driver.py /Users/edr/code/JouleWise-wt-s1-writer-derivation head --build-seed
python3 /tmp/s1witness/driver.py /Users/edr/code/JouleWise-wt-s1-writer-derivation head2
python3 /tmp/s1witness/driver.py /tmp/s1base base
```

`head2` is a same-tree replicate: it establishes that the harness itself is
byte-deterministic, so an IDENTICAL base-vs-head result is a real negative and
not a comparison that could never have differed.

## 3. Case A — ordinary bracket-kind slot, valid disposition

Both trees: `returncode 0`, stdout status `valid`,
`b_fiducial_s = 9.298188781738281e-05`, ledger grew from 2 to 6 rows ending in
`bracket-session-slot-finalization` / `disposition: valid` / `slot: pre`.
Custody dir contains `events.jsonl instrument_evidence.json manifest.json
power_trace.csv raw`.

`cmp` results (`cmp base/<f> head/<f>` and `cmp head/<f> head2/<f>`):

| artifact | base vs HEAD | HEAD vs HEAD-replicate |
|---|---|---|
| `ledger.jsonl` (P, post-run) | IDENTICAL | IDENTICAL |
| `instrument_evidence.json` | IDENTICAL | IDENTICAL |
| `manifest.json` | IDENTICAL | IDENTICAL |
| stdout | IDENTICAL | IDENTICAL |
| stderr | IDENTICAL | IDENTICAL |
| `head.json` (pin) | IDENTICAL | IDENTICAL |
| custody dir listing | IDENTICAL | IDENTICAL |

No DIFFER, therefore no offsets or hexdumps to report.

**No timestamp stripping was applied — none was needed.** The comparison is of
raw bytes. This is possible because the only wall-clock values the code itself
generates on this path (`timestamp_s`, `capture_wall_time_s`, sample interval
stamps) come from `_LogicalTestClock`, seeded from the pinned
`JW_FAKE_TIME_ORIGIN`, and `validation_id` is supplied via `--attempt-id`.

### sha256 table (base / HEAD / HEAD-replicate — all three columns equal)

| artifact | sha256 (identical in all three runs) |
|---|---|
| `ledger.jsonl` (pre-run seed) | `1d423a215b7c2e7c254616b4d6fcee1c1c47941e9e0fb4961f94fd84d7f49862` |
| `ledger.jsonl` (post-run) | `e4bb4176b46ff45db4db559fe42257d8df8609d24bab24f8305aeaed030dd351` |
| `instrument_evidence.json` | `a8c634ecc5f6a1957b4f1e63c343e921c77d545d346ae587449b0febcd7362cd` |
| `manifest.json` | `3dc052bbebee3665c72f799486544deea977c9b2fcd44b75aa022a5ebfaa78d5` |
| stdout | `b8de09161b2469f7d50b7a6d676dba706104a34a85a2dd7c869bd2888de5412f` |
| stderr | `9da8a61f6c12cab6eae862f027516fe6bd418d074e67fbc1f38f3f0df4f01ab9` |
| `head.json` | `a59f8a617ca3a3779d12b6ec59bc6c9c00b4d87d80a5de51fc01bec3c4f1fb78` |
| argv | `fa4f3f1734fd5e1676781a5d3f95130d28df5d4d106db8e72bf37877d9129f46` |

Corroborating content check on the HEAD-tree artifacts: neither
`instrument_evidence.json` nor `manifest.json` carries `derivation_only`,
`screen_basis`, or `exceeds_prior_level_screen` — the new keys stay off the
ordinary path, as the guard `if screen_basis is not None` in
`scripts/validate_powermetrics_fiducial.py` (evidence and manifest blocks) intends.

Artifacts kept at `/tmp/s1witness/out/{base,head,head2}/`.

## 4. Case B — ordinary systematic-invalid: NOT PRODUCED

Attempted and abandoned. `disposition = "systematic-invalid"` requires
`b_fiducial_s > preflight_systematic_screen_s`, and that comparator is derived
from the acceptance artifact's
`decimal_derivation.ratified_operatives.preflight_level_screen_s`. Driving it
below the fixture bound means rewriting the acceptance, which is what the
project's own `_rekey_acceptance(maximum_s=...)` helper does (three fields:
`source_statistics.maximum_s`, `rounding.preflight_level_screen.value_s`,
`ratified_operatives.preflight_level_screen_s`). Reproducing exactly that
rewrite in the driver — with both `0.000010000000000` and the test's own
`0.000000000000001` — made the writer refuse at preflight with

```
{"code": "calibration_frozen_protocol_invalid",
 "context": {"reason": "acceptance_artifact_unauthenticated"}, ...}
```

i.e. `load_calibration_acceptance_bound` rejected my re-keyed artifact, so the
capture never reached the disposition branch. Some further consistency the
in-test helper satisfies (and my standalone reproduction does not) is involved;
running that down was not cheap within the time box, so the case is reported as
not produced rather than guessed at. Both attempts are at
`/tmp/s1witness/out/base-sysinv/` (`returncode 2`, empty stdout).

## 5. Caveats

1. **Scope.** The witness covers exactly one ordinary invocation shape: a
   bracket-kind session, slot `pre`, matching identity epoch, healthy fixture
   sampler, valid disposition. It says nothing about the ordinary path under
   crash/rollback stages, the standalone (non-bracket) path, ordinary-invalid,
   or systematic-invalid (§4).
2. **Fixture repo, not the real checkout.** Runs are against a synthetic copy
   holding only `joulewise/`, three `scripts/`, the protocol configs, and a
   re-keyed acceptance, per the existing tests' pattern. The re-key rewrites the
   acceptance's `estimator_code_sha256` and the digest pin in
   `joulewise/calibration_bracketing.py` inside that copy only.
3. **stderr is environment-sensitive.** The `powermetrics_post_teardown_census`
   line in stderr enumerates foreign `powermetrics`-shaped processes on the
   machine. During these runs it consistently found one stray fixture sampler
   from another agent's test tree, so the byte-identical stderr result holds
   only because that finding was stable across all three runs; a different
   machine state would change stderr bytes without any code change. The four
   artifacts that matter (ledger, evidence, manifest, stdout) are free of this.
4. **Determinism is conditional on the knobs** in §2. Without
   `JW_FAKE_TIME_ORIGIN` and an explicit `--attempt-id` the writer emits
   wall-clock timestamps and a `uuid4` validation id and no byte comparison is
   possible.
5. The base tree was extracted with `git archive`, so it carries no `.git` and
   no untracked files; the HEAD side was read from the (clean) worktree.
