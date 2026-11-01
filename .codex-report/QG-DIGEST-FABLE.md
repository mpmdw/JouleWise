STATUS: DONE (cold review; report only, no production code changed)

# QG-DIGEST-FABLE: cold review of PR #619 (`ba49cd0c9`, quiet_guard_process `_digest`)

Reviewer: Claude Fable 5.1, non-author, on `review/2026-11-01-qg-digest-fable` cut from the PR
head `ba49cd0c9e1178266dfb287914d9dc3bc3e3c3da` (branch `lane/2026-11-01-trim-b2-qg-digest`).
Synthetic data only (`JW_B5_SYNTHETIC_ONLY=1` in every test process). No restricted or custody
directory was read. The PR branch was not pushed to, edited or merged.

## Verdict: ACCEPT

The new check is correct and strictly narrower than the old one; every value `argv_digest()` can
produce still validates; the regression test kills every behaviour-changing mutant I tried; and no
live (non-retired) code path compares installed quiet-guard bytes against the repo pin, so moving
`QUIET_GUARD_PROCESS_SHA256` cannot break a measurement night. Two Low/Info findings, neither
blocking and neither requiring a change before merge.

## Findings

| # | Severity | Finding | Disposition suggested |
| --- | --- | --- | --- |
| F1 | Low | The regression test asserts only `ProcessIdentityError`, not the error text. Mutant M10 (allowed alphabet narrowed to lowercase hex, so uppercase now raises "contains non-hex characters" instead of "must use lowercase hex") survives. The PR body says "both error texts are unchanged"; the test does not pin that. No code or test outside `quiet_guard_process.py` reads either text (`grep -rn "must use lowercase hex\|contains non-hex characters" joulewise scripts tests configs docs` hits only the module), so this is a test-strength note, not a behaviour risk. | Optional: `assertRaisesRegex` on the two texts, or accept as is. |
| F2 | Info | `joulewise/flags/collect.py:786-820` (live, B5 window flags; driver passes the seal at `joulewise/b5/driver.py:725`) hashes the executed checkout at window time and emits the flag `code.executed_differs_from_sealed` when it differs from `configs/campaigns/v5_claim_25g83/sealed_inventory.json`. That is a flag, not an admit/refuse decision, and the working tree already differs from the seal: 47 of 682 sealed entries on origin/main `8757a6611`, 49 on this head (`joulewise/quiet_guard_process.py` and `scripts/setup_quiet_guard.sh` join the list). The PR body states 47 of 315 code files; the denominator differs from mine (I counted every sealed entry), the conclusion is the same. | None; consistent with every other code PR since H_claim. |

No High or Medium findings. Nothing blocking.

## 1. Correctness of the check and the test

`joulewise/quiet_guard_process.py:78-87` (head). `_plain_nonempty` rejects non-`str` and empty;
the prefix/length test requires `sha256:` (7 chars, `ARGV_DIGEST_PREFIX`, line 25) and total length
71, so the body is exactly 64 chars; the new membership test rejects any body char outside
`[0-9a-fA-F]`; the existing lowercase test then rejects uppercase. Together: accepted iff
`^sha256:[0-9a-f]{64}$`. The old `int(value[7:], 16)` additionally accepted `0x`/`0X`, a leading
`+`/`-`, `_` group separators and surrounding whitespace (including `\n`), all of which the new check
refuses.

Callers of `_digest` (all in the module): `AncestorIdentity.__post_init__` (line 103),
`AncestorIdentity.from_mapping` (126), `ProcessIdentity.__post_init__` (144),
`ProcessIdentity.from_mapping` (185); `validate_identity_mapping` (190) goes through
`ProcessIdentity.from_mapping`. No other module calls `_digest` (`grep -rn "_digest(" joulewise
scripts` outside the module hits only `argv_digest(`). Producers: `argv_digest()` (lines 48-62)
returns `ARGV_DIGEST_PREFIX + hashlib.sha256(...).hexdigest()`, i.e. 64 lowercase hex, for both the
`bytes` ("raw-command") and `Sequence[str]` ("argv-vector") branches; lines 672 and 678 feed it
into `ProcessIdentity`/`AncestorIdentity`.

Executed checks (Python 3.14.6, this machine):

- Property check: 20,000 random argv tuples (0-6 entries, random bytes decoded with
  `surrogateescape`) and 20,000 random `bytes` inputs: all 40,000 `argv_digest()` outputs pass
  `_digest` unchanged and construct an `AncestorIdentity`; empty tuple and empty bytes also pass.
- Exhaustive single-character corruption of a good digest: every position 7..70 replaced by every
  ASCII char outside `[0-9a-f]` (7,168 cases): 7,168 rejected, 0 accepted.
- The test's 12 malformed forms are all length 71 where length matters (`"sha256:0x" + body[2:]`
  etc.), so they exercise the new membership check rather than falling out at the length test;
  the `body[:-1]`, `body + "0"` and `SHA256:` forms cover length and prefix. Test module on head:
  `Ran 20 tests ... OK (skipped=1)`; the skip is `LiveDarwinKernelInventoryTests` behind
  `QG_LIVE_DARWIN=1` (`tests/test_quiet_guard_process.py:418`), unrelated.

### Mutants (applied to `joulewise/quiet_guard_process.py` on the PR head, `python3 -m unittest tests.test_quiet_guard_process` each, file restored and `git status` clean afterwards)

| Mutant | Result |
| --- | --- |
| M1 revert to `int(value[7:], 16)` | FAILED (failures=7) killed; matches the PR's counterfactual |
| M2 drop the hex-character check entirely | FAILED (failures=8) killed |
| M3 drop the lowercase check | FAILED (failures=1) killed |
| M4 `.strip()` the body before the membership test (allow whitespace) | FAILED (failures=3) killed |
| M5 allow `_` in the alphabet | FAILED (failures=1) killed |
| M6 allow `+`/`-` in the alphabet | FAILED (failures=2) killed |
| M7 allow `x` in the alphabet (0x prefix) | FAILED (failures=1) killed |
| M8 drop the `len(value) != 71` test | FAILED (failures=2) killed |
| M9 drop the `startswith(ARGV_DIGEST_PREFIX)` test | FAILED (failures=1) killed |
| M10 alphabet `0123456789abcdef` only (uppercase hits "non-hex" text instead of "lowercase") | OK, SURVIVES (F1: error-text only; acceptance set identical) |
| M11 check `value[8:]` (skip first body char) | FAILED (failures=3) killed |
| M12 check `value[7:70]` (skip last body char) | FAILED (failures=3) killed |

Every mutant that changes which strings are accepted is killed. The single survivor is behaviour-
equivalent for acceptance and differs only in which of two `ProcessIdentityError` texts is raised.

### Pin

`shasum -a 256 joulewise/quiet_guard_process.py` on the head = `0034ddf9f7e7ef981e9d317361371769305a79d32e10de3d51d89b0e45fb40fc`,
equal to the new `QUIET_GUARD_PROCESS_SHA256` at `scripts/setup_quiet_guard.sh:14`. The other two
pins (`quiet_guard.py` `09aa9c1f...`, unchanged) still match. The move is required by
`tests/test_quiet_guard.py:1668` `test_setup_digest_pins_match_every_reviewed_root_executable_artifact`,
which hashes the repo file and compares it to the pin.

## 2. Does any live code path compare installed quiet-guard bytes to the repo pin?

No. Verified, not taken from the PR body.

- The pin variable `QUIET_GUARD_PROCESS_SHA256` appears only in `scripts/setup_quiet_guard.sh:14`
  (consumed at lines 91-93 by the installer's own staged-copy validator, under sudo, one-time) and
  in `tests/test_quiet_guard.py:1672` (the pin test). `grep -rn QUIET_GUARD_PROCESS_SHA256 joulewise
  scripts configs tests` has no other hit. The old digest `6742eec0...` appears in
  `configs/campaigns/v5_claim_25g83/sealed_inventory.json:495` (historical seal, see F2) and in
  `docs/process_traces/**` archives only.
- Nothing in `joulewise/` or `scripts/` reads the installed library path. `quiet-guard-install` /
  `_INSTALLED_LIBRARY` appears only in `scripts/quiet_guard_privileged.py:15-16`, which uses it as a
  `sys.path` root when it is itself running as the installed helper; it does not hash or compare
  anything. `joulewise/quiet_guard.py` hashes canonical JSON state and a command's stdout
  (lines 179-180, 213) and reads only its own JSON state files (`_read_json`, line 606-611); no
  file-digest comparison. `scripts/quiet_guard.py:26` holds the helper path only.
- Importers of `quiet_guard_process` (`grep -rln quiet_guard_process joulewise scripts`):
  `joulewise/quiet_guard.py`, `joulewise/arm_census.py:16` (process-table observation; its only
  `hashlib` use is the plan bytes at lines 308-316), `joulewise/evidence_night.py:1065` (inside an
  embedded census subprocess script; the `installed_bytes` at lines 1504-1519 are LaunchAgent
  plist bytes compared to a fresh render, not guard bytes), `scripts/fixture_orphan_census.py:46`
  (a comment). None hashes the module or an installed copy.
- `joulewise/run_campaign.py`, `scripts/run_campaign.py`, `scripts/install_night_agent.sh`,
  `joulewise/night_kinds.py`: zero references to `quiet_guard` or the setup script.
- The only installed-bytes predicate is `privilege.installed_bytes.v1`
  (`joulewise/arm_readiness.py:1079-1081`, `:1179`; rows in
  `configs/arm_readiness/d117_row_registry_v{1,2}.json`). It is declarative: it requires a
  `PRIVILEGE_INSTALLATION` evidence record carrying
  `installed_digests_match_pack_staged_digests: True`. No module in the repo produces that record
  (`grep -rn installed_digests_match` outside `arm_readiness.py` hits only
  `configs/analysis/b5/step4_reason_classes.json:882`, a reason-class list, and a 2026-08 trace),
  and the predicate compares installed digests to the *pack's staged* digests, not to the repo pin.
  Its `applicability_rule` is `CLOCK_HELPER_ONLY` (`d117_row_registry_v2.json:856-863`), i.e.
  `REQUIRED` only when `arm_context.clock_route == "HELPER"` (`arm_readiness.py:6206`); the t0
  author hard-codes `clock_route="MANUAL"` (`joulewise/arm_readiness_evidence_t0.py:1017`), and no
  config under `configs/` sets a `clock_route`.
- `scripts/run_night.py:49-50` still imports `arm_readiness` and `arm_readiness_evidence_t0` and
  calls `readiness.generate_arm_receipt` (line 2431). I note this because the brief says the arm
  chain is retired (CA-42, `docs/process/pruning_list_2026-10-14.md:253,407`) while the import is
  still present. Even taking that path as live, the installed-bytes row is NOT_APPLICABLE under
  MANUAL and, under HELPER, would compare against pack-staged digests from an externally authored
  receipt, never against `scripts/setup_quiet_guard.sh`. So moving the pin cannot change a night's
  outcome either way.
- The live night chains `scripts/night_chains/quiet_predicate_evidence.zsh` and
  `calibration_derivation_only.zsh` run `joulewise.quiet_predicate_campaign`, which hashes its own
  chain source, manifest, logs and session bytes (lines 78, 127, 161-167, 617, 659) and never
  references the guard.
- F2 above is the one live comparison of repo bytes against a recorded digest; it is a window
  flag against the historical seal, already raised for 47 files on main, and not a decision.

## 3. Whole suite on the merged tree

Worktree `/private/tmp/jwrev619-merged` from the repo at `/Users/edr/jw-b5-analysis/.git`,
checked out at `ba49cd0c9`, `git fetch origin` then `git merge --no-edit origin/main`
(`8757a6611`): "Already up to date", so the merged-tree sha is
**`ba49cd0c9e1178266dfb287914d9dc3bc3e3c3da`** (the head is origin/main plus the one commit).

Module list: `scripts.shard_tests.discover_test_modules()` (the `unittest discover -s tests`
ordering, including the `tests/b5_analysis`, `tests/flags`, `tests/twins`, ... packages). One
`python3 -m unittest <module>` process per module, 4 in parallel via `xargs -P 4`, Python 3.14.6,
environment `TMPDIR=TEMP=TMP=/private/tmp/jwrev619tmp`,
`JOULEWISE_CUSTODY_PARENT=/private/tmp/jwrev619tmp/custody-parent` (fresh),
`JOULEWISE_ADDITIONAL_CUSTODY_PARENTS=[]`, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`,
`R7F_CORPUS_ROOT=<worktree>`.

Result: **466 modules, 465 exit 0, 1 non-zero**; 11,751 tests ran; per-module tails
`400 OK`, `65 OK (skipped=N)`, `1 FAILED (errors=1)`.

The one non-zero exit, exact tail:

```
tests.test_mlx_runtime_detokenizer   rc=1
ERROR: test_mlx_runtime_detokenizer (unittest.loader._FailedTest.test_mlx_runtime_detokenizer)
  File "/private/tmp/jwrev619-merged/tests/test_mlx_runtime_detokenizer.py", line 18, in <module>
    from test_mlx_runtime import make_config, make_suite_manifest, suite_item
ModuleNotFoundError: No module named 'test_mlx_runtime'
Ran 1 test in 0.000s
FAILED (errors=1)
```

This is a harness artefact, not a regression from #619: the module imports a sibling test by bare
name, which only resolves when `tests/` is on `sys.path` (as `unittest discover -s tests` and
`scripts/shard_tests._ensure_import_paths` arrange). The identical `FAILED (errors=1)` reproduces
on origin/main `8757a6611` (worktree `/private/tmp/jwrevmain`, same environment), and with
`PYTHONPATH=<worktree>/tests` the module passes on the merged tree: `Ran 8 tests ... OK`. The
module has no reference to `quiet_guard`. Counting that rerun, 466/466 modules pass.

Modules named in the PR body, from the same run: `tests.test_quiet_guard_process` Ran 20 OK
(skipped=1), `tests.test_quiet_guard` Ran 87 OK, `tests.test_arm_census` Ran 20 OK,
`tests.test_fixture_orphan_census` Ran 14 OK, `tests.test_b5_seal_landing` Ran 9 OK,
`tests.test_repin` Ran 47 OK, `tests.test_digest_pin_census` Ran 22 OK,
`tests.test_docs_freshness` Ran 31 OK. Logs: `/private/tmp/jwrev619tmp/logs/<module>.log`, exit
codes in `/private/tmp/jwrev619tmp/results.txt`.

## Method notes

- Mutants were applied in a separate worktree (`/private/tmp/jwrev619-mut`) so the suite run was
  not disturbed; the module was restored byte-for-byte before this branch was cut.
- I did not run `scripts/setup_quiet_guard.sh` or anything under sudo.
