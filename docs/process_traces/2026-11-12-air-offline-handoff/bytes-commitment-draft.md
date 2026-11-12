<!-- DRAFT for the orchestrator. Item 285 is the R1 Part A smoke; this is 286 or later (shown as <<N>>; the magistrate's reply is <<N+1>>). Replace every <<...>> before posting.
     Conditions are RL-92 section 1 as amended by RL-95 (audit/2026-11-10-fable @ a7593b50e). -->

<<N>>. **Laptop lead (interactive session <<session>>, Opus 5.5), 2026-11-12 <<HH:MM>> PST: BYTES stage-1 COMMITMENT (the 12 Nov checkpoint). RL-92 section 1, with condition 4 as amended by RL-95. MAGISTRATE: check every gate below, then commit and push the item-284 predictions to `records/2026-11-bytes-stage1`. The lead runs `record-push`. You run `check`. Then stop. No held-out operation of any kind.**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-12T<<HH:MM>>-08:00
on_early_or_refused: any gate G1-G8 not exactly as stated: STOP before `git switch -c`, commit nothing, record which gate failed and its printed output (hashes, rc, counts, names only), mail the lead. RL-92: if any condition fails, nothing is committed and it goes back to the research lead.
next_observable: protected branch records/2026-11-bytes-stage1 on origin with the stage-1 commit (docs/bytes/stage1/predictions.json, predictions.sha256, unblinding.jsonl) plus the receipt commit (push-receipt.json); bytes_commitment.py check rc 0; RUN_STATE <<N+1>> from the magistrate
```

- **Authority.**
  - RL-92 section 1 lets the commitment proceed today, without returning to the research lead, if all seven conditions hold. Text: `audit/2026-11-10-fable` @ `f89488aec`.
  - RL-95 replaces condition 4's "the twin on `main`" with "the twin on the commitment line" (@ `a7593b50e`).
  - The procedure is plan §3.9 plus its "RL-7a preflight update" (`docs/run_reports/2026-11-07-bytes-stage1-plan.md`) and `docs/design/bytes_commitment.md`, with the changes below:
    - the source dir is `run-sesscodes`;
    - the census is re-run;
    - both hashes are recorded.
- **Already met on the Air (lead). Each line has the evidence the magistrate re-checks in G-steps.**
  - **RL-92 4 / RL-95, the twin on the commitment line.**
    - PR #738 (`fix/2026-11-12-bytes-neg8-guard` → `lane/2026-11-07-bytes-stage1-run`) merged as a true fast-forward, at `<<RUN_LINE_HEAD>>`. The push of the CI-tested head means the run-line tip is the tested SHA.
    - It carries `1e78224cd`, the twin that ran item 284, plus five commits that move no code under `joulewise/` or `scripts/`: `89e06a64b`, `8041c288c`, `b490b40a4`, `569646b68` and `000a716de`. They fix the run line's pre-existing CI failures:
      - NEG-8 under the RL-7a guard;
      - the twin's B-lexeme classification;
      - D-188 copied from main;
      - the b6 round fixture clock;
      - the roster chain on the RL-7a fixture;
      - the hazard refusal allowlist brought up to date with RL-7a (`configs/gates/hazard_refusals.json`, text edits only);
      - #712's deterministic agent-identity test, taken verbatim from main;
      - the remaining BYTES test chains moved onto the RL-7a synthetic commitment fixture, and the coverage map brought up to date;
      - the BYTES rehearsal's loop clock moved off the packs' 2026-11-05 close.
    - Fable 5.2 cold reviews: `89e06a64b` ADMIT, `8041c288c` ADMIT-WITH-FIXES (wording, applied in `b490b40a4`), `b490b40a4` ADMIT, `569646b68` ADMIT, `000a716de` ADMIT. Recorded in `docs/run_reports/2026-11-12-bytes-run-line-ci-coldreview.md`.
    - CI is green on that head, `<<CI_RUN_ID>>`, every shard. That includes `tests.test_bytes_agreement`: the nineteen campaigns and NEG-8.
    - Then the docs-only BY-AGREE-1 PR #<<PR2>> fast-forwards on top, to `<<RUN_LINE_HEAD_AFTER_BY_AGREE>>`.
  - **RL-92 4, the nineteen campaigns at `1e78224cd`.** The Air ran the full `tests.test_bytes_agreement` at `1e78224cd` (log `/Volumes/JW-EXT/scratch/bytes-agree19/agreement.log`). Result: 51 tests in 4,835 s, 50 OK. The "agreement" lines show all nineteen campaigns with 0 above the bar: bytes, compressed, defects, edge_locked, marker_incomplete, late_start, empty_payload_n, replayed_batch, replayed_tail, first_batch_tail_replayed, minimum, anchor_narrow, anchor_wide, resident, time, polls_only, header_closed, invalid_anchor and withheld. The only failure is `test_neg8_reference_battery_omission_is_detected`, a known pre-existing failure:
    - it is not a campaign;
    - it was refused by the RL-7a guard before comparing (cold review F3; also at `df4c73e55`);
    - it was repaired, test-only, in `89e06a64b`, and passes in #738's CI.
  - **RL-92 5, the deviation rows.** `docs/registrations/bytes_deviation_log.md` on the run line now holds two rows:
    - BY-BLIND-1: RL-44 with RL-45's two sentences, verbatim. Entered 2026-11-11 at `df4c73e55`.
    - BY-AGREE-1: RL-82's text with RL-92's sentence after "Ruled: a cell's flags are the codes on its kept runs and on its session." Entered 2026-11-12 at `<<BY_AGREE_SHA>>`, after item 284 met RL-82 condition 4 and after the nineteen-campaign result.
    - The row text's own "(entered 2026-11-11 …" is RL-82's wording and is kept verbatim. The Entered column and the file's authority note record 2026-11-12.
  - **#701 note (RL-95).** #701 may not change `scripts/bytes_twin.py` or `joulewise/bytes_analysis.py`. When it merges, both hashes are re-checked on `main` and recorded. Any difference goes to the research lead BEFORE the merge.
- **Setup.** Use `$W`, `$S1`, `$PY` and `$LOOP` as in item 283: `W=/Users/edr/code/jw-wt/bytes-stage1`, `S1=/Users/edr/night-archive/bytes-stage1-20261111`, `PY=/opt/homebrew/bin/python3.13`. Then set:
  ```zsh
  export RUN=$S1/run-sesscodes
  export PIN=18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71
  export PRED=a6cb172c58462b76609be5ec532f1a9bcfbe474ea64d7e004e948b3ffaeb5f19
  export TWIN=4820dc2e4d6c2b717ae7d1e70c9d66bc28b3c2ad622497604d3ea487b10a03de   # scripts/bytes_twin.py at 1e78224cd
  export RL=origin/lane/2026-11-07-bytes-stage1-run
  ```
- **Gates. Run them in order and record each output. The first gate that fails stops everything.**
  - **G1, RL-92 1: item 284 is clean.** Item 284 on main reports rc 0 and verdict `READY_TO_COMMIT`, with 0 fields above the bar at the blinded stage and 0 at fit. Then:
    ```zsh
    tail -1 $S1/run-sesscodes.log                                     # rc=0
    $PY -c 'import json,sys; s=json.load(open(sys.argv[1])); print(s["verdict"], s["exit"], s["producing_commit"], s["producing_tree_dirty"], s["bytes_analysis_sha256"]==sys.argv[2])' $RUN/stage1-summary.json $PIN
    ```
    Expected: `READY_TO_COMMIT 0 1e78224cd… False True`. Then print the two above-bar NAME counts, and nothing else:
    ```zsh
    $PY -c 'import json,sys; s=json.load(open(sys.argv[1])); print([len(s[k].get("above_bar_fields",[]) or []) for k in ("blinded_agreement","stage1_agreement")])' $RUN/stage1-summary.json
    ```
    Expected: `[0, 0]`. If the summary's keys differ, use the names item 284 recorded. A 7, any other rc, or any above-bar field: STOP.
  - **G2, RL-92 2: byte identity, and the re-run's file is the one committed.**
    ```zsh
    shasum -a 256 $RUN/out/a-fit/predictions.json; cat $RUN/out/a-fit/predictions.sha256
    cmp $RUN/out/a-fit/predictions.json $S1/run-twinfix/out/a-fit/predictions.json && echo IDENTICAL
    ```
    Expected: both digests equal `$PRED`, and `IDENTICAL`. Every later copy reads from `$RUN`, never from `$S1/run` or `$S1/run-twinfix`.
  - **G3, RL-92 3: the estimator in the tree that ran.**
    ```zsh
    git -C $W rev-parse HEAD
    git -C $W status --porcelain | wc -l
    shasum -a 256 $W/joulewise/bytes_analysis.py $W/scripts/bytes_twin.py
    ```
    Expected, BEFORE moving `$W`:
    - HEAD `1e78224cd…`;
    - `0` changed paths;
    - `$PIN`, then `$TWIN`.

    This is the twin that ran item 284 (RL-95). If the twin's hash is not `$TWIN`, STOP.
  - **G4, RL-95: the commitment line carries the same bytes.**
    ```zsh
    git -C $W fetch -q origin lane/2026-11-07-bytes-stage1-run
    git -C $W rev-parse $RL                                           # <<RUN_LINE_HEAD_AFTER_BY_AGREE>>
    git -C $W merge-base --is-ancestor 1e78224cd $RL && echo ANCESTOR
    git -C $W diff --quiet 1e78224cd $RL -- scripts/bytes_twin.py joulewise/bytes_analysis.py && echo SAME_BYTES
    git -C $W diff --name-only 1e78224cd $RL -- joulewise scripts | wc -l           # 0: no code under joulewise/ or scripts/ moved
    git -C $W diff --name-only 1e78224cd $RL                          # expect exactly the list below
    ```
    Expected:
    - `ANCESTOR`;
    - `SAME_BYTES`;
    - `0`;
    - the path list is exactly these 13 paths: `configs/gates/hazard_refusals.json`, `docs/decision_log.md`, `docs/registrations/bytes_deviation_log.md`, `docs/run_reports/2026-11-12-bytes-run-line-ci-coldreview.md`, `tests/b6/round_support.py`, `tests/bytes_commitment_support.py`, `tests/fixtures/bytes/output_coverage.json`, `tests/fixtures/bytes/repro/harness.py`, `tests/test_agent_identity.py`, `tests/test_battery_float_sweep.py`, `tests/test_bytes_agreement.py`, `tests/test_bytes_analysis.py`, `tests/test_bytes_roster_drop.py`.

    Then `git -C $W checkout --detach $RL` and re-run G3's `shasum`. It must again print `$PIN` and `$TWIN`.

    CI evidence: the lead's item names run `<<CI_RUN_ID>>` on head `<<RUN_LINE_HEAD>>`. If `gh` works on the MBP, also run `gh run view <<CI_RUN_ID>> -R mpmdw/JouleWise --json conclusion,headSha` and expect `success` on that head.
  - **G5, RL-92 5: both rows are entered before this commit.**
    ```zsh
    grep -c '^| BY-BLIND-1 |' $W/docs/registrations/bytes_deviation_log.md      # 1
    grep -c '^| BY-AGREE-1 |' $W/docs/registrations/bytes_deviation_log.md      # 1
    grep -c 'For a cell that cannot be computed, they are the codes on all of its planned runs and on its session.' $W/docs/registrations/bytes_deviation_log.md   # 1
    ```
  - **G6, RL-92 6 / RL-44 (b) 3: the census, from a fresh fetch, as close to the commit as possible.** Run it from `$W`. It prints paths, commits and counts only, never content.
    ```zsh
    cd $W
    git config --get-all remote.origin.fetch     # must include +refs/heads/*:refs/remotes/origin/*
    git fetch -q origin; echo fetch_rc=$?
    mkdir -p $S1/census-recheck
    $PY -I docs/process_traces/2026-11-11-bytes-blindcheck/tools/census.py 2026-11-11T00:00 > $S1/census-recheck/hits.tsv; echo rc=$?
    awk -F'\t' '{print $2":"$6}' $S1/census-recheck/hits.tsv | xargs $PY -I docs/process_traces/2026-11-11-bytes-blindcheck/tools/duration_scan.py > $S1/census-recheck/duration.tsv; echo rc=$?
    wc -l < $S1/census-recheck/hits.tsv; wc -l < $S1/census-recheck/duration.tsv
    ```
    - Expected: both rc 0. The Air's pre-qualification at 04:3x PST gave 130 hits and 107 duration-scan rows. Every hit is new against `census_hits.tsv`, since that census predates 2026-11-11.
    - A higher count is expected, because each new RUN_STATE, ruling or paper commit is a new blob. It is not a stop: RL-44 asks that the new hits are recorded, not classified.
    - Do NOT open any hit file, and do not run `masked.py` or `maskl.py`.
    - Until the commitment, no seat opens `M2.md`, the M1 brief, or the `m1/` and `m2-scripts/` files, and no seat derives stage durations from the `night-results/r{1,2}-bytes-*` branches (RL-44 (b) 4, RL-45).
  - **G7, RL-7(a) preflight: no earlier commitment, and no held-out attempt to reconcile.**
    ```zsh
    git -C $W ls-remote origin 'refs/heads/records/2026-11-bytes-stage1' | wc -l   # 0
    git -C $W log --all --oneline -- docs/bytes/stage1/unblinding.jsonl docs/bytes/stage1/heldout-release.json | wc -l   # 0
    ls -d $S1/post $S1/release-heldout 2>/dev/null | wc -l   # 0
    ```
    All three must print 0. Otherwise STOP: a journal must be reconciled first (design doc step 1).
  - **G8, the session.**
    - Nothing is armed, and no smoke or capture is running or due within 1 h.
    - `$S1` has ≥ 5 GiB free.
    - Network time stays OFF.
    - This is a desk step, not a capture.
- **Steps (only after G1-G8).**
  1. Write the commit message to `$S1/commit-msg.txt`. Its lines:
     - `BYTES stage-1 commitment: predictions.sha256 a6cb172c58462b76`
     - a blank line;
     - `predictions.sha256 $PRED (byte-identical to the item-268 file, cmp; source $RUN, item 284)`;
     - `bytes_analysis.py sha256 $PIN`;
     - `bytes_twin.py sha256 $TWIN (the twin that ran item 284 at 1e78224cd; RL-95)`;
     - `run line head <<RUN_LINE_HEAD_AFTER_BY_AGREE>>; PR #738 (fast-forward); CI <<CI_RUN_ID>> green incl. the nineteen campaigns`;
     - `RL-92 conditions 1-7 (RL-95 for 4): see RUN_STATE <<N>>/<<N+1>>`;
     - `RL-44 census re-run <<UTC>> from a fresh fetch: <<n>> hits since 2026-11-11T00:00, all new against census_hits.tsv; duration scan <<m>>. Record: docs/process_traces/2026-11-11-bytes-blindcheck/BLINDCHECK.md @ df4c73e55`;
     - a blank line;
     - `New census hits (date, commit, session-token count, model-token count, size, path):`;
     - then the full `hits.tsv`;
     - then `Duration-scan rows (count, commit:path, line numbers):`;
     - then the full `duration.tsv`.

     These are counts and paths only.
  2. Plan §3.9, with the source dir `$RUN`, and the journal created here (design doc step 2):
     ```zsh
     cd $W
     git switch -c records/2026-11-bytes-stage1
     mkdir -p docs/bytes/stage1
     cp $RUN/out/a-fit/predictions.json $RUN/out/a-fit/predictions.sha256 docs/bytes/stage1/
     cp $S1/manifest.json $S1/census.json $RUN/stage1-summary.json $S1/lines-summary.txt docs/bytes/stage1/
     cp $RUN/released-keys/release.json docs/bytes/stage1/stage1-release.json
     : > docs/bytes/stage1/unblinding.jsonl
     cat docs/bytes/stage1/predictions.sha256; shasum -a 256 docs/bytes/stage1/predictions.json     # both $PRED
     git add docs/bytes/stage1
     git diff --cached --name-only        # exactly the 8 files under docs/bytes/stage1/; NO key file, export CSV, withheld store, fit_pass_estimates.json, a-blinded/ or agreement rows
     git -c user.name=mpmdw -c user.email=<your usual> commit -F $S1/commit-msg.txt
     git rev-parse HEAD                   # THE STAGE-1 COMMIT
     git show HEAD:joulewise/bytes_analysis.py | shasum -a 256; git show HEAD:scripts/bytes_twin.py | shasum -a 256   # $PIN, $TWIN
     git push -u origin records/2026-11-bytes-stage1; echo push_rc=$?
     git fetch -q origin records/2026-11-bytes-stage1
     git rev-parse origin/records/2026-11-bytes-stage1      # equals the stage-1 commit
     ```
  3. **`record-push`, at once.** GitHub's activity API is the only source of the push time.
     - If `gh auth status` succeeds on the MBP, run this in `$W`:
       ```zsh
       $PY scripts/bytes_commitment.py record-push --stage1-commit <STAGE1>; echo rc=$?
       ```
       Then `git push origin records/2026-11-bytes-stage1` (the receipt commit) and `git fetch -q origin records/2026-11-bytes-stage1`.
     - Otherwise, mail the lead the stage-1 sha now. The lead runs the same `record-push` and receipt push from a fresh Air checkout of the records branch, then mails back the receipt commit. You then run `git fetch -q origin records/2026-11-bytes-stage1 && git -C $W merge --ff-only origin/records/2026-11-bytes-stage1`.
  4. **G9, RL-92 7, the RL-7(a) gate.**
     ```zsh
     $PY scripts/bytes_commitment.py check --stage1-commit <STAGE1> > $S1/commitment-check.json; echo rc=$?
     $PY -c 'import json,sys; r=json.load(open(sys.argv[1])); print(sorted(r))' $S1/commitment-check.json
     ```
     Expected: rc 0, with a JSON receipt. That receipt shows the commit exists, its predictions blob hashes to `predictions.sha256`, it is reachable from `origin/records/2026-11-bytes-stage1`, and `pushed_utc` is recorded. Print and record `pushed_utc` and the receipt commit. If rc is 1, STOP and record the refusal line: the commitment then exists without a valid gate, and the lead takes it to the research lead.
  5. **Record.**
     - Put `commitment-check.json`, `hits.tsv`, `duration.tsv` and the G1-G9 outputs under `docs/process_traces/2026-11-12-bytes-stage1-commitment/` on main. These are hashes, rcs, counts and names only.
     - Write RUN_STATE <<N+1>> (owner: lead) with:
       - the stage-1 commit;
       - the receipt commit;
       - `pushed_utc`;
       - `$PRED`, `$PIN` and `$TWIN`;
       - the run-line head;
       - the census counts.
     - Mail Ed one line, and mail the lead. Open a docs-only draft PR of `records/2026-11-bytes-stage1` into `main` (the lead merges it). Leave `$W` at the stage-1 commit, because the held-out agreement runs from it.
- **Do not:**
  - run anything with `--stage heldout`, `--stage 2`, `--stage all` or `--stage1-commit` other than `bytes_commitment.py check`;
  - release or copy a held-out key, or open a withheld store;
  - read the numbers in `$RUN/out/a-fit/`, `t-1.json` or the agreement files;
  - commit a key file.
- **After this item: the next BYTES task, which is NOT authorized here.** RL-92 sections 3-5, the P1/M1 twin change. It is built after the commitment and before the held-out agreement or any held-out key release:
  - `_missing_labels` in `scripts/bytes_analyze.py` relabels only when every pass is withheld-missing;
  - the twin's H1 `missing` row prints the reason and flags;
  - the active-or-resident answer prints `missing` with fewer than three MoE points;
  - the M1 flags union covers refused passes;
  - the test is failing first, on a new synthetic campaign joining the agreement set;
  - all campaigns have 0 above the bar;
  - the library digest is unchanged;
  - a `--stage fit` re-run is byte-identical to `$PRED`;
  - it gets a cold review, and the BY-LABEL-1 row is entered with the change.

  RL-82's "before the held-out agreement" item (one campaign with a nonzero anchor profile plus a session code) is checked in the same step.
- **Host.** Nothing is armed. Network time stays OFF. The canonical root is untouched. Run nothing else on the MBP.
