# BYTES stage 1: plan, magistrate instructions and timeline (to the 12 Nov checkpoint)

Written 2026-11-07 by the laptop lead's BYTES subagent (Opus 5.5, session 1544c617). It
answers decision 1 of the research-program audit
(`docs/research-audits/2026-11-07/research-program.md`, branch
`research/2026-11-07-research-program`) and its finding H1: BYTES stage 1 had no owner, no
pointer and no tool. The checkpoint is **12 Nov: BYTES stage 1 committed**; if stage 1 cannot
finish by **15 Nov**, Part 2 of Paper 1 drops to Tier D
(`docs/strategy/2026-10-27-paper1-contingency.md:40`).

**Blinding of this document.** Written without reading any BYTES energy, any held-out or
stage-2 outcome, any withheld store, `/Users/edr/night-*`, night-custody, night-archive,
`restricted/` or `night-results/*`. Every fact about the real sessions below comes from
`RUN_STATE.md` items 150-156 and the magistrate record
`docs/process_traces/2026-10-31-magistrate-39cdeb12/RECORD.md` on `main`.

## 1. What stage 1 is (registration `docs/registrations/bytes_pack_v1.md` §11)

| Step | What | Keys released | Owner | Window? |
|---|---|---|---|---|
| export | One blinded export per counting session; held-out rows go to the withheld store, never to the export (§11 item 1); no clock column (item 2) | none | magistrate | no |
| blinded agreement | `bytes_analyze.py --stage blinded` and `bytes_twin.py --stage blinded`, rails only; the registered comparer (§12) | none | magistrate | no |
| **stage 1 (fit)** | release the fit set's three configurations plus `neg8_reference`; `--stage fit` writes `predictions.json` + `predictions.sha256`; twin `--stage 1`; comparer | fit + NEG-8 only | magistrate | no |
| **commitment** | `predictions.json` and `predictions.sha256` committed in git and the hash recorded, **before any held-out row enters the export** | — | magistrate commits, lead records | no |
| held-out agreement | both implementations `--stage blinded --stage1-commit <hash>` on the withheld rows; attribute any difference before release (§11 table) | none further | magistrate, after the commit | no |
| stage 2 | `b6_release_subset.py --stage heldout --stage1-commit <hash>`, then `--stage heldout --predictions` and twin `--stage 2` | every held-out key | magistrate, after held-out agreement | no |

Stage 1 is the prediction step. The 12 Nov checkpoint is the **commitment** row. Held-out
agreement and stage 2 follow it and must be done by 15 Nov for Part 2 to stay out of Tier D.
None of it needs a quiet window. It does load the CPU and disk for one to a few hours, so it
**must not overlap an armed or running measurement window** (ALIGN R0/R1/W1, items 202-204).

## 2. Code state

- **Run from branch `lane/2026-11-07-bytes-stage1-run`** (its head when the lead hands this
  over; the PR body names it). It is `4e29114ea` (the admitted BY-THERM-LINES head: the
  measurement line's pass-2 code `2649fad54` plus the thermal-lines tool, its tests and a
  report, no other code change) plus `scripts/bytes_stage1.py`, `tests/test_bytes_stage1.py`
  and this document.
  - So the export and the analysis run on the code that collected and harvested BYTES, and
    `joulewise/bytes_analysis.py` is the registered estimator,
    SHA-256 `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71` (§13, §21 item 2).
    The driver refuses to run on any other digest.
  - **Do not run stage 1 from `main`** or from the merge PR's head. That tree also carries
    main's block-5 evolution of shared modules (`joulewise/whole_window.py`, `joulewise/cli.py`,
    `joulewise/b5/harvest.py`, `joulewise/authentication_io.py`) that the registered agreement
    never ran on.
- `scripts/bytes_stage1.py` adds no arithmetic. `census` reads identity columns only;
  `manifest` is the registered §4 manifest plus a `sessions` list; `run` is the
  `tests/test_bytes_agreement.py` `run_both` order up to the commitment, with the registered
  comparer (`compare_campaign`). Tested on the synthetic twelve-sub-pack campaign
  (`tests.test_bytes_stage1`, 16 tests, about a minute on the Air).

## 3. Magistrate instructions (copy-paste; MBP, by day)

**Preconditions.** No measurement window armed or running, and none due to start within 4 h;
no agent of yours or of Ed's busy on the Mac. At least 80 GiB free on the data volume (the
compressed-archive restore keeps a 40 GiB reserve). These are desk steps on blinded data you
already hold; nothing here changes `night-b6` except what step 3.4 says.

**What you must not read or run.**
- Do not open, `cat`, `head`, copy into git, or parse any withheld store
  (`/Users/edr/night-b6/loop-bytes/packs/bytes/withheld/**`, `$S1/lines/*/*/export/withheld/**`).
  Hashing a whole file with `shasum` is allowed (step 3.4).
- Do not release or copy any held-out key, and do not run anything with `--stage heldout`,
  `--stage 2`, `--stage all` or `--stage1-commit` in this session. Those come after the
  commitment is recorded (§4).
- Do not read the numbers in `$S1/run/out/a-fit/`, `t-1.json` or the agreement files; the
  driver's verdict, exit codes and counts are what you report. (The fit set is unblinded by
  design at stage 1, but nobody needs its numbers before stage 2.)
- The usual: no `/Users/edr/jw-b5-*`, no `restricted/`, no `night-results/*` content outside
  the BYTES paths named here.

### 3.1 Checkout and self-test (about 5 min)

```zsh
export PY=/opt/homebrew/bin/python3.13
export W=/Users/edr/code/jw-wt/bytes-stage1
export S1=/Users/edr/night-archive/bytes-stage1-$(date +%Y%m%d)
export LOOP=/Users/edr/night-b6/loop-bytes
export SESSIONS=/Users/edr/night-b6/sessions
git -C /Users/edr/code/JouleWise fetch origin lane/2026-11-07-bytes-stage1-run
git -C /Users/edr/code/JouleWise worktree add --detach "$W" origin/lane/2026-11-07-bytes-stage1-run
cd "$W"
git rev-parse HEAD                      # record it; it must be the head the PR body names
shasum -a 256 joulewise/bytes_analysis.py   # must print 18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71
mkdir -p "$S1" /private/tmp/jwbytes-tmp
TMPDIR=/private/tmp/jwbytes-tmp nice -n 10 $PY -m unittest tests.test_bytes_stage1 2>&1 | tail -3   # OK, 16 tests
```

(If `/Users/edr/code/JouleWise` is not your canonical clone on the MBP, use the one you used
for `therm-lines-39cd`.)

### 3.2 The twelve counting sessions

They are the session directories of the thermal-lines run (item 155; record 39cdeb12):

```zsh
ls /Users/edr/night-archive/bytes-thermal-lines-39cd/hull-p2 /Users/edr/night-archive/bytes-thermal-lines-39cd/request-end-p1
```

Pass 2 (`hull-p2`): `r2-bytes-s1-p2`, s2-p2, s3-p2, s4-p2, s5-p2, `r2-bytes-s6-p2-n3`.
Pass 1 (`request-end-p1`): `r2-bytes-s1-p1`, `r1-bytes-s2-p1`, s3-p1, s4-p1, s5-p1, `r2-bytes-s6-p1`.
Write the twelve ids, exactly as listed, one per line, to `$S1/sessions.txt`, pass-2 ids first.
For each, the archive is the session's current harvest archive:

```zsh
for SID in $(cat $S1/sessions.txt); do
  $PY -c 'import json,sys; print(sys.argv[1], json.load(open(sys.argv[2]))["paths"]["archive"])' \
      "$SID" "$SESSIONS/$SID/session.json"
done | tee $S1/archives.txt
```

Each line should end in `$SESSIONS/<id>/archive` (the path record 39cdeb12 used). If one ends
in `.reharvest-N`, use that path and say so in the record.

### 3.3 Hash the withheld stores that exist now (structure only)

```zsh
( cd $LOOP/packs/bytes && find withheld -type f -name '*.runs.csv' -exec shasum -a 256 {} + 2>/dev/null | sort ) > $S1/withheld-before.sha256
wc -l $S1/withheld-before.sha256
```

Zero lines is a valid outcome (record 39cdeb12: "each session's `export/<pack>/` holds only the
calibration CSV while BYTES is blinded", so the science export may never have been written).

### 3.4 The stage-1 export (fresh, into `$S1/export`; about 5-20 min per session)

The loop's own export directories are not used: their layout is not known to the lead, and a
census of a mixed directory refuses. One fresh export per session, from the archive, with the
measured code:

```zsh
while read SID ARCHIVE; do
  TMPDIR=/private/tmp/jwbytes-tmp $PY scripts/b6_export_runs.py \
    --archive "$ARCHIVE" --plan "$SESSIONS/$SID/custody/night_plan.json" \
    --registration-dir configs/b6/registration --pack-records-root $LOOP/packs \
    --export-dir $S1/export > $S1/export-$SID.stdout 2> $S1/export-$SID.stderr
  echo "$SID rc=$?" | tee -a $S1/export-rc.txt
done < $S1/archives.txt
( cd $LOOP/packs/bytes && find withheld -type f -name '*.runs.csv' -exec shasum -a 256 {} + | sort ) > $S1/withheld-after.sha256
comm -23 $S1/withheld-before.sha256 $S1/withheld-after.sha256   # must print nothing
```

- Every `rc` must be 0. An `rc=5` is an export program fault: stop, keep the stderr, report.
- The exporter writes each session's withheld store to its registered place
  (`$LOOP/packs/bytes/withheld/<pack>/<session>.runs.csv`, §11 item 1) and binds the session's
  key digests (a changed digest refuses, by design). **If `comm` prints any line**, a store that
  existed before was rewritten with different bytes: stop and report the paths (not the
  content). That would mean the export does not reproduce what the loop wrote.
- The hidden factors already exist (12 counting sessions were exported under them); no key is
  drawn. If stderr mentions drawing or creating a key, stop.

### 3.5 Census (seconds)

```zsh
$PY scripts/bytes_stage1.py census --export $S1/export --out $S1/census.json; echo rc=$?
```

`rc=0` and `"verdict": "OK"`: twelve sessions, one per sub-pack, pass ids agree, blinded in
group `bytes`, counting, withheld locator present, no clock column,
and **no held-out row visible** (only `Qwen3-1.7B-4bit`, `Qwen3-4B-4bit`, `Qwen3-8B-4bit` and
references). Any other result: stop and send the lead `census.json` (it holds no energy).
A withheld store that is missing at its locator is not a refusal (registration §11 item 4): the census
prints it under `warnings` as `bytes.withheld_missing`, `run` carries it into `stage1-summary.json`, and
it goes in the record; explain it before the commit.

### 3.6 Thermal lines with `--export` (stage-2 inputs; about 10 min)

Item 155 asks for this before any analysis that uses the export, into new directories:

```zsh
while read SID ARCHIVE; do
  PACK=$($PY -c 'import json,sys; print(json.load(open(sys.argv[1]))["pack_id"])' $S1/export/*/$SID.session.json)
  case $PACK in *-p2) MODE=hull-p2;; *-p1) MODE=request-end-p1;; esac
  $PY scripts/bytes_thermal_lines.py $MODE "$ARCHIVE" $S1/lines/$MODE/$SID --export $S1/export/$PACK > $S1/lines-$SID.json; echo "$SID $MODE rc=$?"
  $PY scripts/bytes_thermal_lines.py verify $S1/lines/$MODE/$SID
done < $S1/archives.txt
for F in $S1/lines/*/*/thermal_line.json; do
  $PY -c 'import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1].split("/")[-2], d["status"], len(d["changes"]), d["producing_tree_dirty"])' $F
done | tee $S1/lines-summary.txt
```

Expected (record 39cdeb12): every line `equals registered line` with 0 changes, except the
s5-p2 hull line (23 changes, all Llama-70B) and the s5-p1 request-end line (10 changes). Each
`verify` prints `view verified`; `producing_tree_dirty` is `False`. **If any s1 or s2 session
(the fit-set sessions) shows a change, or any line is `not defined (...)`, stop and report**:
the fit points would carry a side line the plan did not expect. A refusal reading
`CSV/archive code disagreement` means the fresh export's exclusion codes differ from the
harvest's acceptance: stop and report.

### 3.7 Analysis manifest (seconds)

```zsh
ARGS=(); while read SID ARCHIVE; do ARGS+=(--session "$SID=$ARCHIVE:$S1/export"); done < $S1/archives.txt
$PY scripts/bytes_stage1.py manifest "${ARGS[@]}" --out $S1/manifest.json
```

It prints the manifest digest and the twelve ids in pass order. The `models` block is the
registered manifest's, byte for byte; `test7_passed` is false everywhere (§7, P0 ruling 3).

### 3.8 Stage 1 (one command; expect one to a few hours)

```zsh
cd "$W"
TMPDIR=/private/tmp/jwbytes-tmp nohup nice -n 5 $PY scripts/bytes_stage1.py run \
  --manifest $S1/manifest.json --export $S1/export \
  --pack-records-root $LOOP/packs --out $S1/run > $S1/run.log 2>&1
echo rc=$? >> $S1/run.log; tail -2 $S1/run.log
```

It runs, in order: blinded analysis and twin; the comparer (stops with **rc 3** on any field
above §12's bar, **rc 2** if either side refused); stage 1 with no keys on both sides (both must
produce the intended missing-key refusals with equal exit 1 and the expected diagnostics;
otherwise **rc 4/9**, with no release); the stage-1 release (`b6_release_subset.release`, stage `fit`, keys
`neg8_reference` and the three fit configurations, into `$S1/run/released-keys`; it refuses a
held-out key by construction); stage 1 on both sides; the comparer again.

| rc | verdict | what to do |
|---|---|---|
| 0 | `READY_TO_COMMIT` | §3.9 |
| 1 | refused before starting (census, manifest, estimator digest, existing output) | fix the named input; new `--out` |
| 2 / 3 | blinded stage refused / blinded disagreement | stop; send the lead `stage1-summary.json` (field names and counts only). No key was released. |
| 4 / 9 | stage 1 ran without keys / no-key probe execution or diagnostic fault | stop; report. No key was released. |
| 8 / 10 | blinded / fit comparison products or substantive comparisons missing | stop; no commitment; rc 8 releases no key |
| 5 / 6 | stage-1 analysis refused / hash file mismatch | stop; report stderr of `out/a-fit.stderr` |
| 7 | predictions written, but the twin refused or disagreed at stage 1 | **do not commit**; report the field names in `stage1-summary.json` `stage1_agreement.above_bar_fields` |

### 3.9 Commit the commitment (the 12 Nov checkpoint)

RL-7a update: reconcile any earlier unblinding metadata and initialize/track the
canonical journal **before** this commit, following
[the preflight sequence](../design/bytes_commitment.md). Do not erase an existing
journal. The date in this historical heading is superseded by RL-7(e).

```zsh
cd "$W"
git switch -c records/2026-11-bytes-stage1
mkdir -p docs/bytes/stage1
cp $S1/run/out/a-fit/predictions.json $S1/run/out/a-fit/predictions.sha256 docs/bytes/stage1/
cp $S1/manifest.json $S1/census.json $S1/run/stage1-summary.json $S1/lines-summary.txt docs/bytes/stage1/
cp $S1/run/released-keys/release.json docs/bytes/stage1/stage1-release.json
cat docs/bytes/stage1/predictions.sha256; shasum -a 256 docs/bytes/stage1/predictions.json
git add docs/bytes/stage1
git -c user.name=mpmdw -c user.email=<your usual> commit -m "BYTES stage-1 commitment: predictions.sha256 $(cut -c1-16 docs/bytes/stage1/predictions.sha256)"
git push -u origin records/2026-11-bytes-stage1
git rev-parse HEAD     # THE STAGE-1 COMMIT (40 hex)
```

- Commit exactly these files plus the canonical `unblinding.jsonl`. **Never** commit a key file (only `release.json`, which holds key
  file digests, not factors), an export CSV, a withheld store, `fit_pass_estimates.json`,
  `a-blinded/` or the agreement row files. They stay in `$S1`, which is retained.
- Record in your RUN_STATE item: the stage-1 commit hash, the `predictions.sha256` value, the
  run checkout head, `stage1-summary.json`'s verdict and agreement counts, the census verdict,
  the lines summary, and `$S1`. Email Ed one line. Open a docs-only draft PR of the records
  branch into `main` (the lead merges it).
- Then uninstall nothing (nothing was installed) and leave `$W` in place until the held-out
  agreement has run from the same checkout.

### RL-7a preflight update (2026-11-10)

Before the original commitment, initialize and track the canonical unblinding
journal. After the lead's authorized push, record the push-time attestation with
`scripts/bytes_commitment.py record-push`, then run its read-only `check` command.
[Exact inputs, limitations and commands](../design/bytes_commitment.md) govern this
preflight. The stage-2 analysis and twin commands below additionally require the
real `--stage1-commit HASH`; all four heldout entry points now check the same Git
and metadata evidence before admitting rows/keys. Existing date text in this
historical plan is superseded by research lead RL-7(e), not re-ruled here.

## 4. After the commitment (by 15 Nov; same checkout `$W`, same `$S1`)

Not part of the 12 Nov checkpoint; written here so nobody waits on a second brief.

1. **Held-out agreement** (§11 table; ruling item 3), about the same run time as §3.8:
   `bytes_analyze.py --export $S1/export --manifest $S1/manifest.json --stage blinded --stage1-commit <HASH> --out $S1/post/a-blinded-post`
   and `bytes_twin.py --export-dir $S1/export --manifest $S1/manifest.json --archive <each archive> --stage blinded --stage1-commit <HASH> --out $S1/post/t-blinded-post.json`,
   then the comparer (`tests.test_bytes_agreement.compare_campaign` on a root laid out like
   `$S1/run`). A difference above the bar goes to the lead for attribution before any release.
2. **Stage 2**: `scripts/b6_release_subset.py --pack-records-root $LOOP/packs --blinding-group bytes --keys <every held-out config key> --stage heldout --stage1-commit <HASH> --out $S1/release-heldout`,
   then `bytes_analyze.py --stage heldout --key-dir $S1/release-heldout --predictions docs/bytes/stage1/predictions.json ...`
   and the twin `--stage 2`, with the thermal-line views of §3.6 for the printed-beside lines
   (s5-p2 member-hull, s5-p1 request-end). The lead writes the exact stage-2 brief after the
   held-out agreement (it depends on whether a post-agreement fix and second commitment are
   needed, §11).

## 5. Timeline to 12 Nov, and owners

| When | What | Owner |
|---|---|---|
| Sat 11-07 (done) | Lineage PR opened (lane + thermal lines + stage-1 driver + KB slot fill + CANONICAL row); `lane/2026-11-07-bytes-stage1-run` pushed; CI started | laptop lead (subagent) |
| Sat 11-07 to Sun 11-08 | CI on the PR (the `test_bytes_analysis` shard alone is about 2.5 h); executing review and cold pass on the PR; lead decisions (§6) | laptop lead |
| **Sun 11-08 or Mon 11-09, by day** | §3.1-§3.9 on the MBP, between windows. Hands-on time about 1 h; wall time one to a few hours | **magistrate** |
| Same day | Stage-1 commit hash recorded in RUN_STATE; Ed told in one line | magistrate; lead checks |
| Mon 11-09 to Tue 11-10 | Held-out agreement (§4.1), by day | magistrate |
| Tue 11-10 to Wed 11-11 | Lead attributes any difference; stage-2 brief; stage 2 (§4.2) | lead, then magistrate |
| **Thu 11-12** | Checkpoint: stage 1 committed (met as soon as §3.9 is done) | lead records the call |
| Sun 11-15 | Stage 2 done or Part 2 to Tier D (contingency plan) | lead |

The run does not need the lineage PR merged: it runs from the run branch. Slack: three days
between the planned run (11-08/09) and the checkpoint, for one re-run after a stop.

**Ed:** nothing is required of him for stage 1. He is told the stage-1 hash in one line. He
may overrule E3 (§6).

## 6. Go / no-go: the bandwidth-bound KB repeat (E3, about 1.3 h, exploratory)

**Recommendation: no-go before the 15 Nov scope freeze. Report the KB result with its regime
limit** (`KB-SLOT-FILL.md`, "Regime": the 32 MiB matched dispatch reads at 106-116 GB/s,
latency-bound, so transfer to bandwidth-bound decode traffic is a stated limit).

Why:
- **Stage 1 does not need it.** The registered precondition (§1, §19) is the KB outcome
  itself, which is filled (rails, GPU rail and rest all RESOLVED; nothing prints beside the
  claim lines). E3 changes no registered number, class or estimator.
- **It is not a re-run, it is a new geometry.** The admitted matched-geometry rule chose
  b = 32 MiB as the first resolved rung (64 MiB was not resolved). A bandwidth-bound repeat needs
  a rule variant (dispatch size, ring size, resolution check), a kit, a desk rehearsal and a
  cold science gate before any number is read: design work, not a magistrate re-arm.
- **It competes for the quiet Mac** with ALIGN R1/W1 and the windows Ed approved on 11-07
  (items 202-204), in the same days stage 1 and stage 2 need the MBP by day.

**Go only if all hold by Tue 11-10:** (a) the KB lineage already runs the bandwidth-bound
geometry by a parameter change alone, with no new code; (b) a free quiet slot exists that
displaces no ALIGN window; (c) stage 1 is committed and the held-out agreement has run; (d) the
result is labelled exploratory and is read only after the 15 Nov freeze if it lands later.
Otherwise schedule it after 15 Nov as an exploratory addendum. Owner of the call: the lead
(design change, so not the magistrate's alone); Ed may overrule.

## 7. What the lead must decide

1. **Merge order against the block-5 release.** The lineage PR changes shared modules on `main`
   (§2). Block-5 r3 is not yet tagged (PR #693: "the rebind is the tag `b5/analysis-r3` on the
   merge commit ... Not tagged here"). Either tag `b5/analysis-r3` (and any later r-version) on a
   commit before this PR merges, or accept that a later tag includes the BYTES lineage and
   re-run the D-188 comparator on it.
2. **The frozen-file rebinds** in the lineage PR (`joulewise/flags/{catalog,core,exclusions}.py`,
   `scripts/run_campaign.py`, `scripts/harvest_b5_window.py`): accept the cited in-place rebind
   (behaviour-preserving for block 5; see the PR body), and whether it wants a DLE entry in
   `docs/analysis/b5/DEVIATION-LOG.md` (lead-signed; not written here).
3. **E3**: §6.
4. **Who records the stage-1 hash in RUN_STATE**: this plan says the magistrate, as for every
   MBP desk step; the lead checks.
