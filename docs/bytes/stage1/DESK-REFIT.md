# BYTES §4.2(2) desk re-fit: magistrate runbook

RL-201 §4.2(2) requires a desk `--stage fit` re-run on the same inputs. Its
predictions file must be byte-identical to the committed one. This runbook
gives that run for the magistrate, on the head that fixes the cold review of
PR #949 (RL-201 §4.2(1), 2026-11-24).

**Blinding.** It was written from the code, the registered configs, the
7 November stage-1 plan (`docs/run_reports/2026-11-07-bytes-stage1-plan.md`)
and the research lead's cold review. No real export, archive, key, custody
directory or stage-1 record content was opened. Per RL-201 §4.4, the
magistrate reports exit codes, verdicts, counts, hashes and names only. Do not
read the numbers in `$D/out/`, `t-1.json` or the agreement files. Compare the
committed files with `cmp -s` only.

## Why the run is the stage-1 driver

Since PR #949, every keyed fit, `bytes_commitment.py check`, admission and
held-out key release verifies a private export seal
(`bytes-export-integrity.json`). Only the stage-1 driver creates that seal.
So the re-fit is a driver run on the fixed head, followed by two `cmp` checks
against the committed blobs. A bare `bytes_analyze.py --stage fit` or `check`
without a seal refuses with `BYTES export manifest: private repository is
required`. The 22 November desk draft therefore no longer runs as written.

The fixed head reads harvest-shaped rosters, which have no member role. It
also requires `--export-seal-repo`, a new directory outside every export
directory. Capture refuses a seal repository inside an export directory. The
driver no longer defaults the seal repository to the export directory.

## 0. Values

```zsh
# From the lead's hand-over and a names-only listing. Fill before step 1.
export FIXED='<FIXED: full SHA of this fix merged into ops/2026-11-22-bytes-p1m1-base, from the lead>'
export S1='/Users/edr/night-archive/bytes-stage1-<YYYYMMDD>'   # <YYYYMMDD>: the 12 Nov stage-1 directory, from `ls -1 /Users/edr/night-archive`

# Fixed by the repository.
export PY=/opt/homebrew/bin/python3.13
export C=569591e53ffcd91efbab7a9ebaff1d580bbc78ba    # the stage-1 commitment (RL-201 §4.1, event A)
export PACK=/Users/edr/night-b6/loop-bytes/packs      # pack records root (bytes_pack_v1.md §11; plan §3.1 $LOOP/packs)
export M="$S1/manifest.json"                          # the analysis manifest written by plan §3.7
export E="$S1/export"                                 # the stage-1 export written by plan §3.4

# New for this run. Each must not exist yet. If one does, take the next number. Never reuse one.
export W=/Users/edr/code/jw-wt/bytes-refit-1          # clean checkout detached at $FIXED
export D="$S1/refit-1"                                # driver output directory
export SEAL="$S1/refit-1.seal"                        # private seal repository, outside $E and outside $W
```

The canonical clone is `/Users/edr/code/JouleWise`. If it is not your
canonical clone on the MBP, use the one from the 12 November run (plan §3.1).

## 1. Preconditions

- No measurement window is armed or running, and none is due within 4 h. No
  agent session is busy on the Mac. Free space is at least 80 GiB
  (plan §3.1).
- **Names-only listing**, sent to the lead before step 4:

  ```zsh
  ( cd "$E" && find . -print | sort ) > "$S1/refit-1.export-names.txt"
  ls -1A "$PACK/bytes/blinding-sessions" > "$S1/refit-1.bindings-names.txt"
  ```

  Capture demands exact membership of both.
  - `$E` must hold only the twelve `<pack>/<session>.runs.csv` and
    `<pack>/<session>.session.json` pairs and their pack directories. Any
    other file stops capture, even a `.DS_Store`.
  - `blinding-sessions` must hold exactly the twelve `<session>.json` files,
    plus an optional `<session>.lock` for each of those twelve sessions.
  - If either listing shows anything else, stop. Send the lead the two name
    files. Other BYTES-group bindings need one more line in the code before
    this run.

## 2. Checkout at the fixed head

```zsh
git -C /Users/edr/code/JouleWise fetch origin ops/2026-11-22-bytes-p1m1-base records/2026-11-bytes-stage1
git -C /Users/edr/code/JouleWise worktree add --detach "$W" "$FIXED"
cd "$W"
test "$(git rev-parse HEAD)" = "$FIXED"; echo head rc=$?                                         # 0
git merge-base --is-ancestor 765f28644706f1033b5b12ee177e6ff7fe5f4e75 HEAD; echo ancestor rc=$?   # 0
git cat-file -e "${C}^{commit}"; echo commitment rc=$?                                           # 0
shasum -a 256 joulewise/bytes_analysis.py   # 18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71
test -z "$(git status --porcelain)"; echo clean rc=$?                                            # 0
```

## 3. Same campaign manifest as committed

```zsh
git cat-file blob "${C}:docs/bytes/stage1/manifest.json" | cmp -s - "$M"; echo manifest-cmp rc=$?   # 0
```

## 4. The re-fit

```zsh
test ! -e "$D" && test ! -e "$SEAL"; echo fresh rc=$?    # 0
mkdir -p /private/tmp/jwbytes-tmp
cd "$W"
TMPDIR=/private/tmp/jwbytes-tmp nohup nice -n 5 "$PY" -B scripts/bytes_stage1.py run \
  --manifest "$M" --export "$E" --pack-records-root "$PACK" \
  --export-seal-repo "$SEAL" --out "$D" > "$S1/refit-1.log" 2>&1
echo rc=$? >> "$S1/refit-1.log"; tail -2 "$S1/refit-1.log"
```

The driver must exit 0 with verdict `READY_TO_COMMIT`. Its last JSON line
names `export_seal_repo` and `export_seal_commit`. This run appends no
journal line. It releases only the fit and reference keys again, into
`$D/released-keys`.

## 5. Byte identity (RL-201 §4.2(2))

```zsh
git cat-file blob "${C}:docs/bytes/stage1/predictions.json"   | cmp -s - "$D/out/a-fit/predictions.json";   echo predictions-cmp rc=$?   # 0
git cat-file blob "${C}:docs/bytes/stage1/predictions.sha256" | cmp -s - "$D/out/a-fit/predictions.sha256"; echo sidecar-cmp rc=$?       # 0
export SEALC=$(git -C "$SEAL" rev-parse HEAD)
git -C "$SEAL" log --format=%s                     # "Record BYTES finalized export inventory", then "... captured ..."
shasum -a 256 "$SEAL/bytes-export-integrity.json"
```

Report the following to the lead:
- the driver's rc, verdict and six exits
- the blinded and stage-1 `compared` and `above_bar` counts
- `predictions_sha256`
- the two `cmp` return codes
- `$SEALC` and the seal manifest's SHA-256
- the paths `$D` and `$SEAL`

A `cmp` failure means §4.2(2) fails. Nothing is pushed, and it goes to the
research lead. The research lead reads RL-201 §4.3's "frozen input
inventory's digest" as the seal manifest's SHA-256 with `$SEALC`.

## What makes "same inputs" checkable

- **The campaign manifest** is the committed one (step 3). It names the
  twelve archive roots and the registered models. Its digest is inside the
  predictions file.
- **The library.** The driver refuses unless `joulewise/bytes_analysis.py`
  is `18582818…0a71`. The predictions file also carries the digest of
  `joulewise/desk_restore.py`.
- **The keys.** `finalize` proves that the released key bytes equal the
  digests each export sidecar bound at export time.
- **Tables and archives.** The 12 November run recorded no digest of these.
  The predictions `cmp` is the test: the fit is deterministic, so identical
  predictions are the evidence. If a custody inventory from 12 November
  exists on the MBP, compare it as well.
- **Across the chain.** The finalized seal lists every fit input by path,
  length and SHA-256. Every later guarded command carries
  `--export-seal-repo "$SEAL" --export-seal-commit "$SEALC"`. Each one
  re-verifies the seal before it appends or reads.

## What refuses, in order

All of these come before any journal line. Steps 2 to 4 and step 6 print
`bytes stage 1 refused: <reason>` and exit 1. Steps 5 and 7 end with the
driver's own verdict and the exit code shown.

1. **Arguments.** No `--export-seal-repo` gives an argparse usage error with
   exit 2, before anything runs. It is told apart from verdict 2 by its
   usage text.
2. **Census.** Any of these refuses:
   - a `withheld` path under `$E`
   - a held-out row visible in a table, or a clock column
   - a missing or extra sub-pack, or two sessions for one sub-pack
   - an export that is not blinded in group `bytes`, is non-claim or is not
     counting
   - a missing withheld locator

   A withheld store missing at its locator is a warning, not a refusal.
3. **Driver checks.**
   - an output directory that exists
   - a library digest other than the pin
   - manifest models that differ from the registered ones
   - manifest sessions that differ from the census
   - no seal repository
4. **Capture** (`BYTES export manifest: …`).
   - The seal repository is inside an export directory (new on this head),
     inside the checkout, or has a JouleWise remote.
   - `$E` holds a file other than the twelve table and sidecar pairs, or a
     symlink.
   - `blinding-sessions` holds any name other than the twelve bindings and
     their locks.
   - The roster differs from its harvest receipt.
   - A session binding differs from its export sidecar.
   - A fit key has no session binding.
   - A table row is one the roster does not authorize: a run outside the
     roster, cells other than its units, a held-out cell, or a cell-less row
     without a reference role.
   - A sealed input is a symlink, or a `withheld` name appears inside
     `derived/` or a fit bundle.
   - The seal repository already holds a capture.
5. **Agreement and probes.**
   - exit 2: a blinded refusal
   - exit 3: a field above the bar at the blinded stage
   - exit 8: incomplete blinded products
   - exit 4: a no-key probe that runs
   - exit 9: a no-key probe that refuses with the wrong text

   Exits 2, 3, 4, 8 and 9 release no key.
6. **Release and finalize.**
   - The release refuses a held-out key.
   - `finalize` refuses any sealed file changed since capture.
   - `finalize` refuses a released directory that is not exactly the fit
     set.
   - `finalize` refuses a released key that differs from its session
     binding.
7. **Keyed fit.**
   - exit 10: incomplete fit products
   - exit 5: a refused stage-1 analysis
   - exit 6: a predictions hash mismatch
   - exit 7: a twin refusal or disagreement
8. **Identity.** A `cmp` return code other than 0 (step 5).

For any refusal, keep `$D`, `$SEAL` and the log. Send the lead the reason
line, not file contents.

## For the later desk steps

- **The seal.** Every guarded command takes
  `--export-seal-repo "$SEAL" --export-seal-commit "$SEALC"`. These are the
  primary and twin post-commit blinded calls, the held-out key release,
  stage 2 and `bytes_commitment.py check`.
- **`$D/released-keys`** is the sealed fit key directory. A keyed fit must
  name exactly it, or it refuses with `fit key directory differs`. Do not add,
  remove or edit a file in it. The held-out release goes to its own fresh
  directory.
- **`$D/out/t-1.json`** is the fit output of the twin that will evaluate.
  `$D/out/a-fit/` holds the matching primary output. Later comparisons use
  these. They do not use the 12 November `$S1/run/out/t-1.json`, which came
  from the twin before the P1/M1 change.
- **The twin's blinded-post call needs all twelve archive roots.** With
  `--stage1-commit`, the twin reads withheld rows. The seal then compares
  its `--archive` set with the sealed archive roots. A missing root refuses
  with `archive roots differ` before admission. The 22 November draft passed
  none. The roots are exactly the twelve `sessions[].archive` of `$M`, in any
  order:

  ```zsh
  ARCHIVES=(); for A in ${(f)"$("$PY" -c 'import json,sys; print("\n".join(s["archive"] for s in json.load(open(sys.argv[1]))["sessions"]))' "$M")"}; do ARCHIVES+=(--archive "$A"); done
  (( ${#ARCHIVES} == 24 )); echo twelve-roots rc=$?   # 0
  cd "$W"
  "$PY" -B scripts/bytes_twin.py --export-dir "$E" --manifest "$M" "${ARCHIVES[@]}" \
    --stage blinded --stage1-commit "$C" \
    --export-seal-repo "$SEAL" --export-seal-commit "$SEALC" \
    --out '<fresh post-commit directory>/t-blinded-post.json'
  ```

  The primary's blinded-post call takes no `--archive`. The lead's desk brief
  gives the rest of the post-commit sequence.

  For a names-only cross-check, each root is the session's harvest archive:
  `/Users/edr/night-b6/sessions/<session>/archive`, or a `.reharvest-N` path
  where plan §3.2 recorded one. The plan spells out five of the twelve
  session ids. Fill in the rest from `ls -1 /Users/edr/night-b6/sessions`
  and `$S1/archives.txt`.

  | Sub-pack | Session id | Archive root |
  |---|---|---|
  | bytes-s1-p1 | `r2-bytes-s1-p1` | `/Users/edr/night-b6/sessions/r2-bytes-s1-p1/archive` |
  | bytes-s2-p1 | `r1-bytes-s2-p1` | `/Users/edr/night-b6/sessions/r1-bytes-s2-p1/archive` |
  | bytes-s3-p1 | `<SID s3-p1>` | `/Users/edr/night-b6/sessions/<SID s3-p1>/archive` |
  | bytes-s4-p1 | `<SID s4-p1>` | `/Users/edr/night-b6/sessions/<SID s4-p1>/archive` |
  | bytes-s5-p1 | `<SID s5-p1>` | `/Users/edr/night-b6/sessions/<SID s5-p1>/archive` |
  | bytes-s6-p1 | `r2-bytes-s6-p1` | `/Users/edr/night-b6/sessions/r2-bytes-s6-p1/archive` |
  | bytes-s1-p2 | `r2-bytes-s1-p2` | `/Users/edr/night-b6/sessions/r2-bytes-s1-p2/archive` |
  | bytes-s2-p2 | `<SID s2-p2>` | `/Users/edr/night-b6/sessions/<SID s2-p2>/archive` |
  | bytes-s3-p2 | `<SID s3-p2>` | `/Users/edr/night-b6/sessions/<SID s3-p2>/archive` |
  | bytes-s4-p2 | `<SID s4-p2>` | `/Users/edr/night-b6/sessions/<SID s4-p2>/archive` |
  | bytes-s5-p2 | `<SID s5-p2>` | `/Users/edr/night-b6/sessions/<SID s5-p2>/archive` |
  | bytes-s6-p2 | `r2-bytes-s6-p2-n3` | `/Users/edr/night-b6/sessions/r2-bytes-s6-p2-n3/archive` |

  The command above reads the roots from `$M`. The table is a check, not an
  input. If a row and `$M` disagree, `$M` governs, and the lead hears of it.
