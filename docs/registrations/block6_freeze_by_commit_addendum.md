# Block 6 (B6-REPL): freeze-by-commit addendum (clerical)

**What this is.** A clerical record kept beside the registration `docs/registrations/block6_replication_DRAFT.md`.
It is not an amendment to that file, and it does not edit it. The registration is REGISTERED at `2a4e5149c`; its bytes
are unchanged on `origin/main` `37c8079` (`git diff 2a4e5149c 37c8079 -- docs/registrations/block6_replication_DRAFT.md`
is empty; SHA-256 `c6a6581e77f9ff724db20683c28c1ec1b12bb42a3bdea66fd840a56d0d084034`).

**Authority.** Ed's adoption of freeze-by-commit (`docs/process/freeze_by_commit.md`, PR #606, F1, F4, F6) and his ruling
of 2026-10-30, relayed verbatim in `RUN_STATE.md` item 146: "bytes is already collecting and block six is finished
collecting - i think we can safely make the book keeping changes to block six, yeah it's technically against freezing
but nothing we're doing touches any numbers, literally all clerical stuff on the repo".

**What it changes.** Nothing that bears on a number. No number, rule, threshold, exclusion, slot value, sealed
inventory, seal pin, identity pin, calibration acceptance or code is changed. It records which commits, acceptance and
environment block 6 already used, so that tags can be cut (F1) and the acceptance can later be read commit-scoped (F4).
The sha written here is the authority; a tag is a convenience (F1).

**Source rules.** Every sha below is cited to the file and line, or the commit, where the repo records it. Tree hashes
are `git rev-parse <sha>^{tree}`, computed 2026-10-30 from a full clone. Where the repo does not record a fact, it says
UNRECORDED; nothing is inferred. No block-6 measurement data was opened; none is in the repo.

## 1. Collection (F1)

Block 6 collected nine sessions, all counting: alpha r1, r3, r4; beta r1, r2, r3; gamma r1, r2, r3, from 2026-10-17 to
the close at 2026-10-21 02:54 PDT (`RUN_STATE.md:203`, item 59).

| Role | Commit | Tree | Where recorded |
| --- | --- | --- | --- |
| Registered pin (S-1), the collection commit | `f31aca19f90473231c41cb31643afb0d6c85d355` | `db97a5409ecd3d99872ed725735bc02551a4eb76` | registration `block6_replication_DRAFT.md:519` (§7 item 2) and `:1194` (S-1); `RUN_STATE.md:124` |
| Machine-test commit that stands for the pin | `6849cb7e37ec4a26c237d923efef55d196f5d47d` | `8a88eec702ea48f25486f40f44fdeb8b10307b77` | `block6_replication_DRAFT.md:1194`; `docs/process_traces/2026-10-17-magistrate-52d50d1f/reg-ruling-fable.md:67` |

- **The measurement checkout.** `/Users/edr/night-custody/measurement/JouleWise-measurement-20261018T0023Z-b6`, built at
  `f31aca19f` (`RUN_STATE.md:125`; `docs/process_traces/2026-10-17-magistrate-52d50d1f/RECORD.md:54`). Every round-1
  to round-4 session ran from it; the repo records no rebuild and no re-pin during collection.
- **Later commits on the lane were not installed as executed code.** `28f29119c` (test only, `RUN_STATE.md:130`: "no
  re-pin, since the executed code at `f31aca19f` is unchanged") and `1706257c4` (launchd template Interactive,
  `RUN_STATE.md:139`: "no executed Python changes, no re-pin"). The smoke-yield and `stages_succeeded` fixes stayed
  queued for "the next re-pin" (`RUN_STATE.md:144`, `:163`), which the record does not show happening before the close.
- **Per-night HEADs.** The checkout's only later commits are the chain desk's pin-only ledger advances
  (`docs/process/block6_machine_test.md` at `f31aca19f`, lines 46-47; `docs/process_traces/2026-10-20-magistrate-4b350f47/RECORD.md:77`:
  "the loop's measurement root is `f31aca19f` plus pin-only ledger commits"). Those pin commits' shas, and each
  session's executed commit as its harvest recorded it (§7 item 4), are **UNRECORDED** in the repo. They were never
  pushed; they live in the measurement checkout and the session archives. By the cited records they differ from
  `f31aca19f` only in `configs/calibration/calibration_ledger_head.json`. So one code state is known, and no
  per-night tag `b6/collection-n<k>` is proposed. If the Mac lead pushes those pin commits (RUN_STATE next-activation
  step (1e)), they are appended below.

**Note.** `f31aca19f` is not contained in `origin/main`. It lives only on `lane/2026-10-17-b6-packs-registered` (and on
branches built from it). The annotated tag is what keeps it reachable if those branches are pruned.

### Proposed tags

| Tag | Commit | Tree | Status |
| --- | --- | --- | --- |
| `b6/collection` | `f31aca19f90473231c41cb31643afb0d6c85d355` | `db97a5409ecd3d99872ed725735bc02551a4eb76` | ready |
| `b6/collection-n<k>` | none | none | not proposed: one code state (above) |
| `b6/analysis` | UNRECORDED | UNRECORDED | later: S-14 is `OPEN` (`block6_replication_DRAFT.md:1207`; §13 line 1186). It is cut when the analysis commit is pinned before the blind dry run |

## 2. Calibration acceptance (F4)

- **File:** `configs/b6/registration/acceptance.json`, SHA-256
  `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8` (`block6_replication_DRAFT.md:368-369`, §3.3;
  S-4 at `:1197`). Issued in `5ffbe15c410d0314b18cf5861a5657c35366f156` (tree `a4ebc35522b6450ce220fbf2eea73566f7bcd6b3`,
  2026-10-17 07:25 PDT, `reg/2026-10-17-b6-acceptance`; the commit that adds the file); registered "at `5ffbe15c4`, no
  change" by D31 (`block6_replication_DRAFT.md:1323`). Its bytes are identical at `5ffbe15c4`, `6849cb7e3` and `f31aca19f`
  (SHA-256 recomputed at each).
- **Its own identity fields.** `registered_commit` = `3bb305d7a62eaec772f04ddb67aaf51f8de526a0` (tree
  `720356cc6e3ac892511616ff99d0661a5a82476b`; main, the base of `configs/b6/executing_reviews.json`, D30 at
  `block6_replication_DRAFT.md:1313-1316`); `derivation.sources.kit_commit` = `1c1bc3204c8ba8fa6d880b9b9a920362bd01fa4c`
  (the quiet-machine kit; not present in this clone, so its tree is UNRECORDED here).
- **Estimator bytes.** The file carries **no `estimator_code_sha256`** (checked: its keys are `schema`, `pack_id`,
  `registered_commit`, `catalog`, `neg8`, `cell_unit_minimum`, `number_bearing_paths`, `reviewed_commits_path`,
  `calibration`, `status`, `derivation`). So the commit it pins cannot be read from its own digests. What the repo does
  fix is §7 item 5 (`block6_replication_DRAFT.md:536-538`): the four `ESTIMATOR_CODE_PATHS`
  (`joulewise/calibration_bracketing.py:239-244` at `f31aca19f`) are byte-identical to block 5's frozen head
  `a434e363d`. Recomputed:

  | Path | SHA-256 (same at `a434e363d`, `5ffbe15c4`, `6849cb7e3`, `f31aca19f`) |
  | --- | --- |
  | `joulewise/powermetrics_fiducial.py` | `bcdfeec06a03525cc6f6c700f2e2e6d10341af1323e4f9355b68ee47eb5bd30c` |
  | `joulewise/uncertainty_evidence.py` | `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8` |
  | `joulewise/adapters/powermetrics.py` | `70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4` |
  | `joulewise/reduce.py` | `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc` |

  These four equal `prospective_rederivation.estimator_code_sha256` of block 5's acceptance
  `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` (read at `f31aca19f`).
  - The latest commit at or before the acceptance's issue (`5ffbe15c4`) where all four match is `5ffbe15c4` itself.
  - The bytes were last changed in its ancestry by `34bfea7c90226509df661c2437eec74228152caa` (tree
    `f1f718bb4be971b26fd647d1961f890724b0b43b`, 2026-09-30, on main). That commit changed `powermetrics_fiducial.py`
    only; its parent already held the other three.
  - `a434e363d96621318657418e60b8d14410079d82` (tree `0ce6bbaf48cf264e4e8a6b3bb217b51aade6d72b`) is an ancestor of
    `f31aca19f`.
- **Proposed commit-scoped record (F4), for phase 1.** `{commit: f31aca19f, acceptance: configs/b6/registration/acceptance.json
  sha256 ea130c87…539ce2a8, estimator paths: the four digests above}`, evaluated in a checkout of `b6/collection`.
  `f31aca19f` is the collection commit, and both the acceptance bytes and the estimator bytes are identical there to
  their issue commit. This is a proposal for the lead; it changes no file.

## 3. Environment (F6)

| Fact | Value | Where recorded |
| --- | --- | --- |
| Interpreter build | `/opt/homebrew/bin/python3.13 -m venv .venv`, then `pip install -c env/mac-measurement-lock.txt` (twice); `brew pin python@3.13` | `docs/process/block6_machine_test.md` at `f31aca19f`, lines 50-51 |
| Python | 3.13.1 | `configs/b6/registration/identity_pins.json` at `f31aca19f`, `/runtime_versions/python` (line 19) |
| Runtime package digest | `runtime_versions_sha256` `9033a69906aab1f0ff5724b5a6c2f3efd623512ee49a7048713e2410e701c794` (Python 3.13.1, mlx 0.31.2, mlx-lm 0.31.3, mlx-metal 0.31.2, numpy 2.5.1, safetensors 0.8.0, tokenizers 0.22.2, transformers 5.12.1) | `identity_pins.json` at `f31aca19f`, lines 9-21; checkout check "interpreter digest `9033a699…`", `docs/process_traces/2026-10-17-magistrate-52d50d1f/RECORD.md:54` |
| Constraints lock | `env/mac-measurement-lock.txt`, SHA-256 `ced3df78d1a87231636b8e83ab5cc42c8cf4755385baed3e3e81ea4378e51062` at `f31aca19f` (a `pip freeze` constraints file, versions without hashes) | the file; "lock equal", `52d50d1f/RECORD.md:54` |
| `pyproject.toml` | SHA-256 `0d42bfcba53128c44a493a7b1e716b6baf9d387a1ffc881e0c624703326911d4` at `f31aca19f` | the file |
| Model and runtime pins | `configs/b6/registration/identity_pins.json`, SHA-256 `513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d` (S-18) | `block6_replication_DRAFT.md:1211` |
| Machine | Apple M3 Max, Mac15,9, 140 W adapter | `block6_replication_DRAFT.md:104-105` |
| OS build per session | **UNRECORDED** in the repo. The registration records it with every session (§3.2 item 6, line 105), in session data that is not in the repo. The only OS string in the repo's pins is the block-5 pin generation probe `macOS-26.6.2-arm64-arm-64bit-Mach-O` (`identity_pins.json` line 298), which is not a block-6 session record | — |
| Resolved, hashed lock (F6 "resolved lock file") | **UNRECORDED**: no hashed lock exists at `f31aca19f`, only the constraints file above | — |

## 4. Appended records

None yet. The Mac collection lead appends per-night records that are not in the repo (pin-only ledger commits,
frozen-checkout heads, per-session OS builds), or commits them under `docs/process_traces/` and names them here
(RUN_STATE next-activation step (1e)).
