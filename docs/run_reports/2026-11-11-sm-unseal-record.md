# sm-unseal-record — 2026-11-11

Branch: `feat/2026-11-11-sm-unseal-record` (already created at intake).
Base: `origin/main` at `6a7493f403b70228efebe2c262f1272d7fe33596`.
Authority: RL-53 W-8 and audit section 8.2 item 7.
The task brief selects this read-only lane over historical generated queue work.
There was no active stop card. Coordination state was left to the lead.

## Built

- `joulewise/unseal_record.py`: the exact v1 schema, validation, strict JSON
  loading, canonical bytes, record digest, and verdict-bound permission check.
- `scripts/show_outcomes_guard.py`: opt-in `check --block B --verdict V [--path P]`.
  It hashes the explicit verdict file without parsing or printing its contents.
  Exit 0 is silent permission, exit 1 prints a refusal code on stderr, exit 2 is usage.
- `docs/unseals/README.md`: 36 lines. No actual or example record was added.
- `tests/test_unseal_record.py`: synthetic records and disposable local Git repos.
- `CANONICAL.md`: one row for the module and one for the guard.
- `scripts/test_timings.json`: one alphabetically placed line, measured at 21.977 s.
- This report. No other tracked file was changed.

## Decisions

The required `schema` key is `joulewise.unseal_record.v1`. Every listed field is
mandatory, including an empty `stays_sealed`. Extra keys and duplicate JSON keys
refuse. Owner words remain verbatim. Times require a date, seconds and an offset
(including Z); no ordering between the two timestamps is inferred.

Canonical bytes are compact, key-sorted UTF-8 JSON, with no trailing newline.
The record digest hashes those bytes. Verdict digest comparisons accept either
hex case. The guard hashes the verdict file's exact bytes, including any newline.

Paths are inert relative text. Matching normalizes backslashes, repeated slashes
and dot segments, without resolving paths. Empty paths, control characters,
absolute paths, drive prefixes and every `..` segment refuse. fnmatch is case
sensitive and `*` spans `/`. `stays_sealed` wins over every opened pattern.
No path supplied inside a record is opened, statted, resolved or globbed.

“Committed” is checked mechanically against a regular-file blob at local Git
HEAD. Matching untracked, staged-only or byte-edited records refuse. Git commands
are local, bounded and disable global/system config, fsmonitor and lazy fetching.
A fresh verdict digest needs a fresh matching record. Multiple matches refuse as
ambiguous. Any invalid JSON record in the directory refuses the directory check.
Filenames must match the block and a real YYYYMMDD calendar date.

The seat list records the owner's scope. The API has no caller identity input
and does not authenticate seats, attest the owner's identity, or add a digital
signature. This implements W-8's accident guard under the existing custody rule.
Omitting `path` checks only block and digest, not permission for a particular file.

## Release-tools follow-up (no branch edits)

Read `origin/align/2026-11-08-v4-release-tools` at
`b2c0681cd651263df7b14f005a1ea1dfe44e1fd9`. Lines below refer to that commit.

| Tool | Guard boundary and recommendation |
|---|---|
| `scripts/release_v4.py` | Lines 492–493: the verdict file has been written and stdout follows. Put the guard here in a future opt-in outcome-display path, before any restricted outcome is displayed. Its present `print(text)` is a blinded, structure-only verdict. Keep the sealed computation and that blinded protocol usable before unseal; otherwise the verdict needed for the record could never be produced. The runbook must call the guard before opening the restricted files. |
| `scripts/compare_v4_recompute.py` | Lines 2230–2231: restricted output is written, then the blinded public summary is printed. Put the guard before any future outcome-display branch here. Line 2228 is the other public-print branch and must share that check if it ever displays outcomes. Do not gate `compare()` at line 2220 or the sealed write at 2230: `release_v4` needs them to create its verdict. Present stdout contains no outcome values. |
| `scripts/b6_unblind.py` | After argument parsing at line 29, before the try block at line 30: a non-BYTES Block 6 unblind should check the release verdict and authorized relative paths before key-directory resolution at lines 37–38, export reads at 39, withheld reads at 46–49, unblinding at 55–56, or writing at 63. BYTES retains its commitment-journal authority; do not add a second record requirement to that path. |

Those integrations need explicit block/release-verdict inputs and, where relevant,
a display-only selector. The current scripts do not expose that complete interface.
The lead owns that follow-up on the release-tools branch. In particular, the
Block 6/BYTES authority choice must be explicit, not guessed from a path name.
`scripts/release_b5.py` is byte-unchanged. Block 5 predates the record rule.

Read the arm stack on both `origin/main` and W1
`origin/align/2026-11-08-v4-r11` at `b4a6c217f0285a20aff33a8407160dd77af2a8a6`:
`run_night.py`, `magistrate_watchdog.py`, and `joulewise/b5/driver.py`.
The W1 courier receipt and nonzero-chain fault differences require no adaptation:
this module reads neither generation's night/result files and depends on no arm
schema. Existing modules import none of this new code.

## Verification

All tests ran one module at a time. Combined test time was under two minutes.
The full suite was deliberately not run because the brief forbids it during the
existing blinded analysis job. No model weights or packages were downloaded.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_unseal_record` (initial) | 30 tests; 7 failures and 11 errors, 18.274 s. The Git lookup used a pathspec that found no blob. One test also supplied the wrong synthetic digest. Both were corrected. |
| Same command (after correction) | 30 tests passed, 26.344 s. |
| Same command (metadata/entry-point coverage added) | 31 tests passed, 26.433 s. |
| Same command (final code, resolve-failure coverage added) | 31 tests passed, 21.977 s. |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | 14 tests, OK, 2 skips; 0.572 s. The sandbox denies ps for the two live census checks. |
| `python3.13 -B -m unittest tests.test_gen_state` | 44 tests passed, 10.738 s. |
| `python3.13 -m compileall -q joulewise/unseal_record.py tests/test_unseal_record.py scripts/show_outcomes_guard.py` | Passed twice, including after the final code change. Compilation was limited to the touched Python files. |
| `git diff --cached --check` | Passed before commit. |

Tests cover each field, malformed/duplicate JSON, exact canonical bytes, digest
binding, absent/mismatched/invalid/uncommitted/ambiguous records, path escapes,
denial precedence, Git failures, CLI exits 0/1/2 in a disposable repo, and the empty
repository directory. Patched builtins.open, io.open, os.open, stat and lstat count
accesses and reject record-named paths. No mutation campaign was run here.

## Limits, incident and handoff

Python 3.11 was not installed. CI or the lead must run the new module there.
No new MLX or hardware tests are involved. For the existing census gate, the lead
must run `tests.test_fixture_orphan_census` outside the sandbox to cover its two
skipped live tests. No live hardware or real custody validation is claimed.

Intake mistake: the initial decision-file read was broader than W-8. A later
heading-range read also continued into subsequent rulings and exposed Block 5
prose. No values were copied into implementation or fixtures. No real custody,
measurement, night-results or records ref was opened. No forbidden filesystem
path was followed, no network was used, and no measurement job was controlled.

No implementation blocker remains. Uncertainty is limited to the future release
tool interface and its explicit BYTES routing, described above. Next: lead cold
review and Python 3.11 replay, then integrate the opt-in display checks on the
release-tools line. This seat leaves all coordination files and bound files alone.
The implementation and this report are committed together locally; no push.
