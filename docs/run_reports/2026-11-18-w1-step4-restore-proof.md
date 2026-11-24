# RL-184 step 4 and same-path restore proof

| Obligation | Result | Evidence |
| --- | --- | --- |
| RL-184 §4.1, compare the step 4 checkout with the signing pin | **PASS** | The documented checker accepted equal blobs across distinct commits and identified each of three independent single-file changes. |
| RL-184 §4.2, desk an invented window from its own pack | **PASS** | The actual Air CLI finalized, packed, restored at the original absolute path and ran the desk and harvest on the restored tree. Final eligibility accepted the restore receipt and refused missing and wrong-window receipts. |

## Authority and checkout

Mission M0 found no active stop card. The lead assigned this documentation and
synthetic verification as Tier 0 Air work. RL-184 §4 places the comparison
before signing and the rehearsal before W1 arms. PR #826, the remote
`align/2026-11-18-desk-seal-successor` branch and the initial clean worktree
all resolved to `3dfeadc0cd9448b664541407153941a27664fea7`. The production CLI
and desk child used that source revision throughout. The ruling was read from
`origin/audit/2026-11-10-fable` at
`61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc`. [RL-184 §4](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21171-L21175)

The report pin `3dfeadc0c` differs from `1fc28324d` only in three test files:
`tests/align/test_smoke_delta3_sol1.py`, `tests/align/test_smoke_delta3_sol2.py`,
and `tests/test_offload_window.py`.

## Step 4 blob comparison

The [signing checklist](../align/v4/W1-BLOCKERS-merged.md#w1-signing-checklist-additions)
records the commit from the checkout that actually runs step 4. The checker
resolves committed object IDs for the exporter, selection and collection
plan. It uses Git object types and IDs throughout. Any changed blob requires
a new step 4 run at the signing pin.

I extracted the checklist shell block unchanged into `check-final/check-blobs.sh`
in the disposable seat directory. `/bin/sh "$D/check-cases.sh" "$D/check-final"`
created an invented Git repository and invoked the block as
`J="$repo" STEP4_CHECKOUT="$step4" SIGNING_COMMIT="$signing" /bin/sh check-blobs.sh`
with the script's absolute path. Each case started from the same synthetic
step 4 commit `40c756a890538976f2ef49fbeb1320eca713a960`. Git confirmed the
one-path diff for each changed case.

| Proposed signing commit | Committed change | Exit | Checker output |
| --- | --- | ---: | --- |
| `c5c925d5d08808dc45a0e44203533ea0e1062821` | Empty commit | 0 | Empty |
| `a3036452aa68dcbb4a0d9f6080f7f98237ada4de` | Exporter only | 1 | `Changed blob: scripts/align_v4_u3_export.py` |
| `d9992f8dd3292f8affd6d2cf84b562df5e1ed56b` | Selection only | 1 | `Changed blob: configs/campaigns/align_v4/registration/u3_sources/selection.json` |
| `4949b4fc0a7c905df1cfdda23c983a365603e5f2` | Collection plan only | 1 | `Changed blob: configs/campaigns/align_v4/collection_plan.json` |
| `9e7e4d4b4cf3c2cf2becf526a7f449ba38cd2368` | Exporter absent | 2 | Git refused to resolve the path |

The checker ran only in the invented repository. No exporter command ran.

## Synthetic Air restore

Air model `Mac16,13`, Darwin arm64, Python 3.13.18 and zstd 1.5.7. The
invented attempt used the `C3` window label with
`session_id=align-v4-c3-synthetic-rl184`. The clean synthetic measurement
mirror's Git head was `157a8c103dca5737178524762dfb50fd68ddd49d`. Its
interpreter wrapper ran the local Python and its harvest entry point
resolved to the unchanged script at the reviewed source checkout.

The seat-local builder adapted the six-member join and window construction
from `tests/align/test_v4_desk_real_harvest.py`. It generated native-shaped
bundles with the fake-MLX endpoint, generated raw plists with the sampler
test helper, and generated its own ledger, terminal evidence and
registration. It supplied an invented corpus in place of the shared B5
builder's import-time corpus read and used invented calibration fixtures.
The custody fence was active in the builder and in CLI children. The
window-specific files were under the packed session tree. There was no
transfer, hardware collection or real evidence access.

The table records the actual commands with their absolute paths factored
into variables. The seat harness invoked the scripts in fresh processes
and captured stdout, stderr and exit codes.

```sh
J=/Volumes/JW-EXT/jw-wt/d-w1-step4-and-restore-proof
D="$J/.desk/rl184.59RLz6aM"
F="$D/fixture2"
S="$F/session"
OUT="$F/out"
K=C3
H=eca857636917631cc1edade7ac2743bd0e6ad323e9efe9dd25c34ca053823443
run() { /opt/homebrew/bin/python3.13 -B "$J/scripts/align_v4_harvest_off.py" "$@"; }
```

| Executed command | Exit | Observation |
| --- | ---: | --- |
| `run finalize-manifest --session-root "$S" --out "$OUT/finalized_manifest.json"` | 0 | Printed only `sha256`. Independent hash of the manifest equaled `H`. |
| `run pack --session-root "$S" --out "$OUT/offload" --finalized-manifest "$OUT/finalized_manifest.json" --level 3 --threads 4` | 0 | Pack bound the same digest and source path. The pre-desk source inventory was unchanged. |
| `s.rename(originals)` in `exercise-cli.py` | OK | Moved `$S` to `$F/originals`. The original absolute path was absent. |
| `run unpack --offload "$OUT/corrupt-copy" --finalized-manifest "$OUT/finalized_manifest.json" --finalized-sha256 "$H" --window-id "$K" --receipt-out "$OUT/unpack_receipt.json"` | 1 | As in `test_rl183b_failed_unpack_leaves_no_receipt`, replacing the payload of a disposable pack copy caused `payload digest mismatch`. Stdout was empty, and both the source path and receipt remained absent. |
| `run unpack --offload "$OUT/offload" --finalized-manifest "$OUT/finalized_manifest.json" --finalized-sha256 "$H" --window-id "$K" --receipt-out "$OUT/unpack_receipt.json"` | 0 | This window's intact pack recreated `$S`. Paths, link targets, file modes and file digests matched the pre-pack inventory. The canonical four-field receipt was created outside `$S`. |
| `run desk --session-root "$S" --workers auto` | 0 | The wrapper reported `desk_exit=2` with one worker. The real harvest exited 0. The desk wrote `PILOT.json`, `desk.json` and `exclusions.json`, with `harvest_status=members_excluded`, `pilot_status=instrument_incomplete` and `full_desk_gate.pass=false`. The originals still matched their pre-pack inventory. |
| `run final --session-root "$S" --window-id "$K"` | 1 | Empty stdout. `final eligibility refused: unpack receipt missing for a window with captures`. |
| `run final --session-root "$S" --window-id "$K" --unpack-receipt "$OUT/wrong-window.json" --finalized-sha256 "$H"` | 1 | Empty stdout. `final eligibility refused: unpack receipt names another window`. The control changed only `window` to `C4`. |
| `run final --session-root "$S" --window-id "$K" --unpack-receipt "$OUT/unpack_receipt.json" --finalized-sha256 "$H"` | 0 | Returned `member_eligibility.stage=final` and the SHA-256 of the actual unpack receipt, `f917ceb32625c08a0b15e6b95bf5b5c61a14cc260a1d9d608d2ecc5db90c420f`. |
| `run reduce --session-root "$S" --out "$S/archive/withheld/reduced" --workers 2` | 0 | Reduced all six synthetic members. |

The instrument and full-desk gate results describe the invented inputs.
The restore proof passes because the original path was recreated from the
pack, the real desk reached a completed adjudication on that restore and
`final` verified the receipt binding. The Python child statuses and the
wrapper status are recorded separately above.

## Verification and handoff

- The stock modules `tests.align.test_v4_desk_real_harvest` and
  `tests.align.test_harvest_off` share a fixture that reads the committed
  settled corpus at import and uses a production seed bundle in full runs.
  The full stock modules were left unrun. The fixture fence and invented
  corpus substitution allowed the wholly synthetic `RunnerTests`,
  `FreshAirRestoreTests` and `SyntheticV4SessionE2ETests` from
  `test_harvest_off` to run with
  `/opt/homebrew/bin/python3.13 -B "$D/check-focused.py"`. All 11 tests
  passed with zero forbidden custody accesses recorded by the module.
- `git diff --check` passed. The two-file diff is the signing checklist and
  this report. The full repository suite was outside the synthetic
  verification scope of this documentation change.
- The prescribed fixture orphan census returned exit 2 with
  `PermissionError: [Errno 1] Operation not permitted: 'ps'`. The CLI and
  regression harness child invocations returned their own statuses.
- Keep the PR in draft against `align/2026-11-18-desk-seal-successor`.
  The lead retargets it after PR #826 lands. The signing comparison still
  requires the lead's actual step 4 checkout and proposed signing commit.
- **NEEDS_SPEC:** None.
