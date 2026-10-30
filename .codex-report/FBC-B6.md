STATUS: DONE

# FBC-B6: freeze-by-commit bookkeeping for block 6 and BYTES

Seat FBC-B6 (scheduled routine `trig_01CvoYc8x2cHXwe4fUgHMMWf`, 2026-10-30), branch `lane/2026-10-30-fbc-b6-bytes` from
`origin/main` `37c8079`. Lead: joulewise-28. Docs only; no tests run, none needed.

## SUMMARY

- **Two clerical addenda written:**
  - `docs/registrations/block6_freeze_by_commit_addendum.md`;
  - `docs/registrations/bytes_freeze_by_commit_addendum.md`.
- **Neither registration file was edited.** `block6_replication_DRAFT.md` is byte-identical to `2a4e5149c`.
- **Block 6 has one collection code state.** All nine counting sessions ran from the checkout at the registered pin
  `f31aca19f`, plus pin-only ledger commits that were never pushed.
- **Ready tags:**
  - `b6/collection`;
  - `bytes/collection-n1`, `-n2` and `-n3`.
- **Pending tag:** `bytes/collection-n4` (pass 2). It cannot be cut because the pass-2 measurement HEAD `f0300a579`
  (and its base `69bc0c93a`, and `2649fad54`) is not on GitHub.
- **Block 6's acceptance carries no estimator digests.** The F4 scope comes from registration §7 item 5 plus recomputed
  digests.
- **BYTES's registration names no acceptance file.**
- **Not touched:** any number, code, sealed inventory, seal or identity pin, or acceptance. No measurement data or
  `night-results/*` branch was opened.

## B1. Block 6, from the repo's records

| Item | Value | Citation | Tree |
| --- | --- | --- | --- |
| (a) Collection commit | `f31aca19f90473231c41cb31643afb0d6c85d355` (S-1 pin) | `docs/registrations/block6_replication_DRAFT.md:519`, `:1194`; `RUN_STATE.md:124-125`; `docs/process_traces/2026-10-17-magistrate-52d50d1f/RECORD.md:54` | `db97a5409ecd3d99872ed725735bc02551a4eb76` |
| (a) Machine-test commit standing for it | `6849cb7e37ec4a26c237d923efef55d196f5d47d` | registration `:1194`; `reg-ruling-fable.md:67` | `8a88eec702ea48f25486f40f44fdeb8b10307b77` |

**(a) Per-night commits.** The checkout is `f31aca19f` plus the desk's pin-only ledger commits:
- `docs/process/block6_machine_test.md` at `f31aca19f`, lines 46-47;
- `docs/process_traces/2026-10-20-magistrate-4b350f47/RECORD.md:77`.

No re-pin happened during collection: `RUN_STATE.md:130` and `:139` say "no re-pin", and `:144` and `:163` keep the
fixes queued. The pin commits' shas and each session's executed sha are **UNRECORDED** (not pushed; kept in session
data). The sessions are r1 to r4, closed 2026-10-21 (`RUN_STATE.md:203`).

**(b) Acceptance.**
- **File:** `configs/b6/registration/acceptance.json`, SHA-256 `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8`
  (registration `:368-369`, `:1197`).
- **Issued in** `5ffbe15c410d0314b18cf5861a5657c35366f156`, tree `a4ebc35522b6450ce220fbf2eea73566f7bcd6b3`; registered
  by D31 (`:1323`). The bytes are identical at `f31aca19f`.
- **`registered_commit`:** `3bb305d7a62eaec772f04ddb67aaf51f8de526a0`, tree `720356cc6e3ac892511616ff99d0661a5a82476b`.
- **No `estimator_code_sha256`.** So, by the F4 recipe:
  - The four `ESTIMATOR_CODE_PATHS` at `5ffbe15c4` and `f31aca19f` equal block 5's acceptance
    `calibration_acceptance_d079_v2_n24_25g83_r2.json` digests and `a434e363d` (tree
    `0ce6bbaf48cf264e4e8a6b3bb217b51aade6d72b`, an ancestor of the pin).
  - The latest commit at or before the issue that matches is `5ffbe15c4` itself.
  - The bytes were last changed by `34bfea7c90226509df661c2437eec74228152caa` (tree
    `f1f718bb4be971b26fd647d1961f890724b0b43b`).

**(c) Environment.**
- **Interpreter:** relock `/opt/homebrew/bin/python3.13 -m venv` plus `pip install -c env/mac-measurement-lock.txt`
  (`block6_machine_test.md` at `f31aca19f`, lines 50-51).
- **Python 3.13.1, runtime digest `9033a699…e701c794`:** `identity_pins.json` at `f31aca19f`, lines 9-21; checked at
  checkout build, `52d50d1f/RECORD.md:54`.
- **Lock SHA-256 `ced3df78…`.**
- **Per-session OS build and a hashed lock:** **UNRECORDED**.

**(d) Analysis commit.** **UNRECORDED.** S-14 is OPEN (registration `:1207`).

## B2. The block-6 addendum

`docs/registrations/block6_freeze_by_commit_addendum.md` records:
- Ed's ruling;
- `b6/collection` with its commit, tree and citations;
- no per-night tags (one code state) and `b6/analysis` for later;
- the F4 record;
- the F6 table;
- an append section for the Mac lead.

## B3. The BYTES addendum

`docs/registrations/bytes_freeze_by_commit_addendum.md` records the code states and the sessions in each:

| State | Commit | Tree | Sessions | Citation |
| --- | --- | --- | --- | --- |
| n1 | `6731d5249` | `5899b72a…` | r1-s1-p1 (zero data) | `RUN_STATE.md:263`, `:265` |
| n2 | `8e097d020` | `122c0540…` | r1-s2..s6-p1, r2-s6-p1 | `RUN_STATE.md:265`; pin-only commits `5e769307c`..`264d58d9a`, all pushed and listed with trees |
| n3 | `e624d67c7` | `900b8430…` | r2-s1-p1 | `RUN_STATE.md:313`, `:347` |
| n4 | `f0300a579`, UNRECORDED tree | — | r2-s6-p2-n3, s5-p2, s4-p2, s3-p2 | `39206674/RECORD.md:65`, `:68`; `caa9ff66/RECORD.md:13` |

For n4 the addendum also lists the pushed lane commits that went in, each with its tree.

It also records:
- the F4 facts: the acceptance in the tree is `ea130c87…`, the loader is `joulewise/b6/registration.py:58-61`, and the
  registration names no acceptance;
- the F6 facts;
- that later nights append in §5.

## B4. Commands for the lead

Run these from a clone that has fetched `lane/2026-10-17-b6-packs-registered`, `ci/2026-10-27-bytes-enddate-base` and
`ci/2026-10-27-bytes-enddate`. That covers every commit below: `6731d5249` and `8e097d020` are ancestors of
`264d58d9a`.

```bash
git tag -a b6/collection f31aca19f90473231c41cb31643afb0d6c85d355 -m "Block 6 collection commit: registered pin S-1 (B6-REPL §7 item 2, S-1); tree db97a5409ecd3d99872ed725735bc02551a4eb76; nine sessions r1-r4 ran from a checkout at this commit plus pin-only ledger commits. Freeze-by-commit F1; docs/registrations/block6_freeze_by_commit_addendum.md"
git tag -a bytes/collection-n1 6731d524907a9c9f77eb51a5380410a705ffc657 -m "BYTES collection code state n1: pass 1 registered; tree 5899b72a4e510016502451430df4450a1650427e; session r1-bytes-s1-p1 (zero data). RUN_STATE item 70. docs/registrations/bytes_freeze_by_commit_addendum.md"
git tag -a bytes/collection-n2 8e097d020879c95df9a87f4376cff36abea22ac6 -m "BYTES collection code state n2: plan-tree sidecar fix on the measurement line; tree 122c054035421ebc32a41f2373a1e069b6fc869e; sessions r1-bytes-s2..s6-p1, r2-bytes-s6-p1 (with pin-only descendants). RUN_STATE item 71. docs/registrations/bytes_freeze_by_commit_addendum.md"
git tag -a bytes/collection-n3 e624d67c7ca154c67df77f105b6aa8adcad047a4 -m "BYTES collection code state n3: end date 2026-11-05 PST (directive #589 item 4); tree 900b84305dfe853c6272c25d72d43233d0c8d036; session r2-bytes-s1-p1. docs/registrations/bytes_freeze_by_commit_addendum.md"
# Verify each before pushing (should print the tree recorded in the addendum):
for t in b6/collection bytes/collection-n1 bytes/collection-n2 bytes/collection-n3; do echo "$t $(git rev-parse "$t^{tree}")"; done
git push origin b6/collection bytes/collection-n1 bytes/collection-n2 bytes/collection-n3
```

**Pending.** First the Mac lead pushes the pass-2 measurement line to a branch (for example
`ci/2026-10-28-bytes-pass2-measurement`), between sessions with the loop held or idle. Then:

```bash
git tag -a bytes/collection-n4 <full sha of f0300a579> -m "BYTES collection code state n4: pass 2 registered (de35f6403, 93aad7b19) with BY-P2-THERM and the sizing fix, on the measurement line; tree <tree>; sessions r2-bytes-s6-p2-n3, s5-p2, s4-p2, s3-p2 and later. docs/registrations/bytes_freeze_by_commit_addendum.md"
```

## OPEN ISSUES

1. **The pass-2 measurement HEAD is not on GitHub.** `f0300a579`, `69bc0c93a` and `2649fad54` are not there, so
   `bytes/collection-n4` cannot be tagged and its tree is UNRECORDED. The Mac lead pushes them (step (1e)).
2. **`2649fad54` is not on the lane.** `RUN_STATE.md:348`, `:355` and `39206674/RECORD.md:68` name `2649fad54` as the
   head of `lane/2026-10-28-bytes-pass2-open`. The lane on origin carries `aa6cdce3e` (a test-only change after
   `7b622eb95`), then `ee4ce93fc`. Either the lane was rewritten, or `2649fad54` exists only on the Mac. It is test-only
   if it matches `aa6cdce3e`, but this is unverified.
3. **The block-6 pin-only ledger commits were never pushed.** Their shas, and each session's executed sha, are
   UNRECORDED in the repo. By the records they change only the ledger head file, which is not code.
4. **F6 has no hashed lock.** Only the pip-freeze constraints file exists, and per-session OS builds are recorded only
   in session data. Both are UNRECORDED in the repo for both blocks.
5. **`b6/collection` points at a commit that is not on `main`.** `f31aca19f` is reachable only from lane branches. Once
   the tag is pushed, it keeps the commit alive.
6. **`1c1bc3204`** (the quiet-kit commit named in the block-6 acceptance's derivation) is not in the fetched branches.
   Its tree is not recorded here.

## NEEDS_RULING

1. **BYTES tag naming** (Ed or the lead). Should there be a `bytes/collection` tag at all, given that BYTES has
   several code states? If so, which state does it name: n1, the registered pass-1 commit; or the latest state? The
   alternative is to keep only `bytes/collection-n<k>`. The seat proposes `-n<k>` only.
2. **Per-HEAD or per-code-state tags** (Ed or the lead). F1's "per distinct night commit" can be read literally. Every
   session ran on a distinct pin-only HEAD, and for BYTES n2 those HEADs are pushed. The seat tags code states only
   and lists the pin commits with their trees. Tag each pin commit too only if Ed wants it.
3. **The F4 scope commit.** The seat proposes the collection commit as the scope, and records the issue commit
   `5ffbe15c4` and the estimator-byte origin `34bfea7c9` beside it. This needs Ed or the lead to confirm when phase 1
   makes acceptance commit-scoped.
4. **Which acceptance BYTES uses.** The BYTES registration names no calibration acceptance. The code and tree imply
   block 6's `acceptance.json` (`ea130c87…`), but that is unconfirmed. Ed or the lead should confirm it, from a session
   archive's `derived/b6-acceptance.json` (a metadata read, by the Mac lead), and say whether a BYTES-side note is
   wanted.
