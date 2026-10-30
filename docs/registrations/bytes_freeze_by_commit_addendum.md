# BYTES: freeze-by-commit addendum (clerical; collection in progress)

**What this is.** A clerical record kept beside the BYTES registration `docs/registrations/bytes_pack_v1.md`. It is
not an amendment to that file, and it does not edit it. That file is not on `main`. Its current text is on
`lane/2026-10-28-bytes-pass2-open`: last changed in `7b622eb95`, unchanged at the lane head `ee4ce93fc`, SHA-256
`1dc6105a4fc0210cbb6860cf41ff882161e21b76729dd3614e432bcdabb909a5`. Its dated amendments on main are
`bytes_end_date_amendment_2026-10-27.md` and `bytes_extension_models_2026-10-27.md`.

**Authority.** Ed's adoption of freeze-by-commit (`docs/process/freeze_by_commit.md`, PR #606, F1, F4, F6) and his ruling
of 2026-10-30, relayed verbatim in `RUN_STATE.md` item 146: "bytes is already collecting and block six is finished
collecting - i think we can safely make the book keeping changes to block six, yeah it's technically against freezing
but nothing we're doing touches any numbers, literally all clerical stuff on the repo". The ruling gives BYTES the same
bookkeeping.

**What it changes.** Nothing that bears on a number. No number, rule, threshold, exclusion, pack registration, sidecar,
identity pin, calibration acceptance or code is changed, and nothing on the measurement Mac is touched.

**Source rules.** Every sha below is cited to the file and line, or the commit, where the repo records it. Tree hashes
are `git rev-parse <sha>^{tree}` from a full fetch of the named branches on 2026-10-30. A commit that is not on GitHub
has no tree here and is marked UNRECORDED. Nothing is inferred. No BYTES measurement data was opened, and no
`night-results/*` branch was fetched.

**BYTES is collecting.** This addendum covers the sessions recorded up to `RUN_STATE.md:578` (2026-10-30: s2-p2 and
s1-p2 remain; no t0 after 2026-11-05 00:00 PST). Later sessions and later measurement-checkout commits are appended
in §5. Nothing above §5 is rewritten.

## 1. Collection (F1): the measurement line, state by state

BYTES runs from a measurement checkout whose HEAD moves in two ways:
- by **pin-only** commits that the chain desk makes after each session (`configs/calibration/calibration_ledger_head.json`
  only);
- by **installs** (cherry-picks of reviewed lane commits at a loop hold).

Each install starts a new code state. The repo does not record each session's executed sha; the harvest records it in
session data that is not in the repo. So below, sessions are placed in the code state the records put them in.

### n1: pass 1 as registered

| Commit | Tree | Where recorded |
| --- | --- | --- |
| `6731d524907a9c9f77eb51a5380410a705ffc657` "BYTES pass 1 registered: the six pass-1 packs flip to registered" | `5899b72a4e510016502451430df4450a1650427e` | `RUN_STATE.md:263` (item 70: "Measurement checkout built at 6731d5249", `/Users/edr/night-custody/measurement/JouleWise-measurement-20261025T0853Z-bytes`, relock, ledger row 402) |

Session: `r1-bytes-s1-p1`, which collected zero data (all 143 member runs refused on a missing plan-tree sidecar;
`RUN_STATE.md:265`). Pin after it: `786ecd968ca5384516e204e333b8467a555397b8` (tree
`d6453927973c4e7339101175eb5d3e307ac85506`, ledger 412, parent `6731d5249`; it diffs from its parent in the ledger head
file only).

### n2: plan-tree sidecar fix

| Commit | Tree | Where recorded |
| --- | --- | --- |
| `8e097d020879c95df9a87f4376cff36abea22ac6` | `122c054035421ebc32a41f2373a1e069b6fc869e` | `RUN_STATE.md:265` (item 71: `537180b78` and `991358f73` cherry-picked onto the pin `786ecd968`, "HEAD 8e097d020, tree equal to 991358f73 plus the pin"). Checked: `git diff 991358f73 8e097d020` is the ledger head file only. The intermediate cherry-pick is `30c5dedd7c6cf2fc6d2ffd89a0b740dbb05cf532` (tree `24a25acb089aa81b6975200dcd22afa1cc826290`) |

Sessions:
- `r1-bytes-s2-p1` (`RUN_STATE.md:267`);
- `r1-bytes-s3-p1` (`:269`);
- `r1-bytes-s4-p1` (`:273`);
- `r1-bytes-s5-p1` (`:275`);
- `r1-bytes-s6-p1`, which aborted (`:284`);
- `r2-bytes-s6-p1` (`:312`).

The pin-only commits that follow are on GitHub (`ci/2026-10-27-bytes-enddate-base`). `git diff 8e097d020 264d58d9a`
changes only `configs/calibration/calibration_ledger_head.json`, so all of them carry n2's code.

| Pin commit | Tree | Ledger, after session (from its subject) |
| --- | --- | --- |
| `5e769307c1050b99450456f052154d41b8d826e7` | `456c49fbbfcee45ada6cacddf4f99e5de3adb20a` | 422, r1-bytes-s2-p1 |
| `1df97f50ed3b00d0e3074196c9475b416852ab1a` | `7ac088c16ca7a7a9c210a300ceb50691566ebb1a` | 432, r1-bytes-s3-p1 |
| `10ffc5b9e2d153458c50cc9ce8cba4b121f0103b` | `397087b22f9b1a1202ef4966dd7ee83172a1d97e` | 442, r1-bytes-s4-p1 |
| `e092b1b1c5095fd6dd8ae57befecad002a984afe` | `9192137a9e5af46acfd4f3feaafdfd2d2f8ec2e9` | 452, r1-bytes-s5-p1 |
| `29971907f160db9d0a47360eaed6cd64af2d65c8` | `862739ba179427d6179f65ecb178cb6ef715bb20` | 460, r1-bytes-s6-p1 |
| `264d58d9a6615763ad20138958eae314c66c8b6d` | `b86bdce1727037ead9860b31d1a0d59b68ac3666` | 470, r2-bytes-s6-p1 |

### n3: end date (Ed, directive #589 item 4)

| Commit | Tree | Where recorded |
| --- | --- | --- |
| `e624d67c7ca154c67df77f105b6aa8adcad047a4` | `900b84305dfe853c6272c25d72d43233d0c8d036` | `RUN_STATE.md:313` ("one measurement-checkout commit, `e624d67c7` on `264d58d9a`"); `bytes_end_date_amendment_2026-10-27.md` |

Session: `r2-bytes-s1-p1`, which completes pass 1 (`RUN_STATE.md:347`). The pin after it, `69bc0c93a`, is the base of
the n4 install (`docs/process_traces/2026-10-28-magistrate-39206674/RECORD.md:65`). It is **not on GitHub**, so its
full sha and tree are UNRECORDED.

### n4: pass 2 as registered

- **The install.** At 05:52-06:15 PDT on 2026-10-28, these were cherry-picked onto `69bc0c93a`
  (`39206674/RECORD.md:65`): the registration (`de35f6403`, `93aad7b19`), the loop test (`95c8ebbe6`), the
  BY-P2-THERM merge (`c6f138a6f`) and the emitter-test fix (`4487c2218`). The record says "Measurement HEAD equals lane
  `4487c2218` plus the ledger pin".
- **The sizing fix.** `7b622eb95` and `2649fad54` were installed by 06:21:26 (`39206674/RECORD.md:68`).
- **The HEAD that ran pass 2.** The measurement HEAD is named `f0300a579` (`docs/process_traces/2026-10-28-magistrate-caa9ff66/RECORD.md:13`;
  `RUN_STATE.md:383`).
- **Not on GitHub.** `f0300a579`, `69bc0c93a` and `2649fad54` cannot be found there (GitHub API lookup on 2026-10-30)
  or in this clone. Their full shas and trees are **UNRECORDED**.

The nearest pushed lane commits (`lane/2026-10-28-bytes-pass2-open`), for reference only:

| Commit | Tree | Note |
| --- | --- | --- |
| `de35f6403e2e9e7ef335b92379b65a759a26e95c` | `dbe579c2a875e55d28e90fbc89ae9f9bf6f12741` | pass 2 registered; cold gate ran on it (`bytes_pack_v1.md` §21 item 7) |
| `93aad7b197b908b98682cbd0c508ac0ac4aa80fa` | `605c47e1936a130fa87700032e5605d61f7e481b` | cold-gate corrections |
| `4487c2218cd03c5c377c2abe52b9b1b142ed3379` | `be3fabeef35e88f874e82eea1424f359c48138bf` | lane state named in the install record |
| `7b622eb957b3b49a34ca9405ea1384939ed1f0fe` | `e5a601879d3dc182f990f8bd2b546adaae915c97` | pass-2 sizing rows |
| `aa6cdce3e53215307dd1c627ad9a200e14a247c0` | `47e94532409d3e681e52e4f2005a1193723a8632` | test only (`tests/b6/test_bytes_packs.py`), 06:21:14; the lane carries this where the records name `2649fad54` |
| `ee4ce93fc7a1e4d77bc54d2085337b122448c334` | `d66007ab3af38636c7f0be3b82fd5ae81bfd3fcc` | lane head; adds an `executing_reviews.json` row only; "the measurement checkout needs no change" (`caa9ff66/RECORD.md:13`) |

Pass-2 sessions so far:
- `r2-bytes-s6-p2-n3` (`RUN_STATE.md:382`);
- `r2-bytes-s5-p2` (`:416`);
- `r2-bytes-s4-p2` (`:442`);
- `r2-bytes-s3-p2` (`:572`).

Remaining: s2-p2 and s1-p2 (`:578`).

### Proposed tags

The scheme is one tag per code state; pin-only commits are listed above and get no tag.

| Tag | Commit | Tree | Status |
| --- | --- | --- | --- |
| `bytes/collection-n1` | `6731d524907a9c9f77eb51a5380410a705ffc657` | `5899b72a4e510016502451430df4450a1650427e` | ready |
| `bytes/collection-n2` | `8e097d020879c95df9a87f4376cff36abea22ac6` | `122c054035421ebc32a41f2373a1e069b6fc869e` | ready |
| `bytes/collection-n3` | `e624d67c7ca154c67df77f105b6aa8adcad047a4` | `900b84305dfe853c6272c25d72d43233d0c8d036` | ready |
| `bytes/collection-n4` | `f0300a579…` | UNRECORDED | **pending**: the Mac lead must push the measurement line (`69bc0c93a` to `f0300a579`) first |
| `bytes/collection` | (one of the above, or none) | none | not proposed; needs Ed (see the report) |
| `bytes/analysis` | UNRECORDED | UNRECORDED | later: stage 1 has not run |

## 2. Calibration acceptance (F4)

- **The registration names no acceptance file.** `bytes_pack_v1.md` at `ee4ce93fc` has no `acceptance.json`, no
  calibration-acceptance digest and no `estimator_code_sha256`; checked by search.
- **What the code reads.** The block-6 code that BYTES runs on loads `<registration dir>/acceptance.json`
  (`joulewise/b6/registration.py:58-61` at `ee4ce93fc`). Every BYTES code state above carries
  `configs/b6/registration/acceptance.json` with SHA-256
  `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8` unchanged. That is block 6's acceptance: issued in
  `5ffbe15c4`, tree `a4ebc35522b6450ce220fbf2eea73566f7bcd6b3` (see `block6_freeze_by_commit_addendum.md` §2).
- **Recomputed at `6731d5249`, `8e097d020`, `e624d67c7` and `ee4ce93fc`.** The four `ESTIMATOR_CODE_PATHS` have the
  same SHA-256 as at block 6's pin:
  - `powermetrics_fiducial.py` `bcdfeec0…5bd30c`;
  - `uncertainty_evidence.py` `b583f35a…cd94ae8`;
  - `adapters/powermetrics.py` `70f47086…5116e5e4`;
  - `reduce.py` `7b9c0d28…ff9fcc`.

  These are the bytes last changed by `34bfea7c90226509df661c2437eec74228152caa` (tree `f1f718bb4be971b26fd647d1961f890724b0b43b`).
- **Not determinable from the repo.** That the BYTES sessions' acceptance is this file is shown by its presence in
  the tree and by the loader. It is not stated by the registration, so the record treats it as **unconfirmed**; the
  session archives' `derived/b6-acceptance.json` would confirm it. The latest commit at or before the acceptance's issue
  where all four estimator files match is `5ffbe15c4` itself.
- **Separate analysis estimator bytes.** The BYTES analysis library is `joulewise/bytes_analysis.py`, SHA-256
  `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`, bound in each pack registration
  (`bytes_pack_v1.md:384`, `:444`, `:513`). That is an analysis pin, not a calibration acceptance.
- **Proposed commit-scoped record (F4).** `{commit: <each bytes/collection-n<k>>, acceptance: configs/b6/registration/acceptance.json
  sha256 ea130c87…539ce2a8, estimator paths: the four digests above}`. This is a proposal only.

## 3. Environment (F6)

| Fact | Value | Where recorded |
| --- | --- | --- |
| Checkout build | relock, ledger row 402 | `RUN_STATE.md:263`; procedure `docs/process_traces/2026-10-07-block5-seal/30-post-seal-runbook.md` steps 3-5, as for block 6 |
| Python | 3.13.1 | `configs/b6/registration/identity_pins.json` `/runtime_versions/python` at `6731d5249` and `ee4ce93fc` |
| Runtime package digest | `runtime_versions_sha256` `9033a69906aab1f0ff5724b5a6c2f3efd623512ee49a7048713e2410e701c794` (mlx 0.31.2, mlx-lm 0.31.3, mlx-metal 0.31.2, numpy 2.5.1, safetensors 0.8.0, tokenizers 0.22.2, transformers 5.12.1) | same file, same commits; the pinned runtime is also stated at `bytes_pack_v1.md:69` |
| Identity pins file | SHA-256 `95d07401…af2efc6e` (n1, n2); `48c8947a…dbdbc66be` (n3); `e78d7ae5…2752b03f` (lane `aa6cdce3e`; n4 UNRECORDED) | the files. They re-issue per state as their records say; the runtime digest is unchanged |
| Constraints lock | `env/mac-measurement-lock.txt`, SHA-256 `ced3df78d1a87231636b8e83ab5cc42c8cf4755385baed3e3e81ea4378e51062` at every state above (no hashes) | the file |
| `pyproject.toml` | SHA-256 `0d42bfcba53128c44a493a7b1e716b6baf9d387a1ffc881e0c624703326911d4` at every state above | the file |
| OS build per session | **UNRECORDED** in the repo (session data). Standing rule: no macOS or app updates on the measurement Mac until 30 Nov (`RUN_STATE.md:856`) | — |
| Resolved, hashed lock | **UNRECORDED**: none exists | — |

## 4. What later nights add

For each later session, and each later install or pin commit, the Mac collection lead appends a row to §5:
- the session id;
- the measurement HEAD it ran;
- the tree hash, once the commit is pushed;
- the OS build.

A new code state gets the next `bytes/collection-n<k>`.

## 5. Appended records

None yet.
