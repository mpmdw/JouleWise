# Block 6: predeclaration of the gate run and the blind dry run (runbook step 6)

Draft, 2026-11-13 09:46 PST (`date`). Builder seat (Claude Opus 5.5) for the lead. Branch
`docs/2026-11-13-b6-s17-fill-staged`. This is the record that runbook step 6 calls
`docs/run_reports/2026-11-13-b6-blind-dry-run.md`. It is written and pushed before the first launch of the pinned
program on real custody (step 7). It holds every value predeclared for steps 7 to 10.

**Filled 2026-11-13 12:53 PST (`date`)** by the builder seat for the lead (runbook steps 2 to 6): every `⟨CUT⟩` and
`⟨LEAD-CONFIRM⟩` blank. The `⟨GATE⟩` blanks stay open until step 7. Steps 4 and 5 touched custody through the kit
and `b6_mapping_build.py` only: names, digests and the session index fields. No session content was opened and
the pinned program has not been run on real custody.

**Amended 2026-11-13 13:28 PST (`date`) after gate attempt 1** (class A, section 2a): `D_gate`, `D_block`, the
mapping digest, the step 7 to 9 argv lists (new documents; gate out-dir `$RUN/gate-2`) and the attempts ledger.
Nothing predeclared for steps 7 to 10 changes.

**Blanks.** A value that exists only after the S-14 cut and steps 1 to 5 is written `⟨CUT: …⟩`. One that exists
only after the gate run is written `⟨GATE: …⟩`. `⟨LEAD-CONFIRM: …⟩` marks a value taken from a plan, which the
lead confirms against the record named. Before the push, every `⟨CUT⟩` and `⟨LEAD-CONFIRM⟩` blank is filled.
`⟨GATE⟩` blanks are filled after step 7, in a second commit pushed before step 8.

**Blind status.** Blind to Block 6. This draft holds no Block 6 outcome and no Block 6 number. I opened no
`/Volumes/JW-EXT/b6-custody*` path, and I listed none. Sources:
- the runbook `/Volumes/JW-EXT/scratch/fable-b6-post-pin-runbook.md` and the corrected commands
  `/Volumes/JW-EXT/scratch/b6-real-run-commands.md`;
- RL-134 at `b19e813f7` and RL-139 at `9d4e7bd1a` (`origin/audit/2026-11-10-fable`);
- the pin request at `31072f2a6`, and the registration and §17 entries at PR #748's `27b6cacfd`;
- the real-run tools at `5c53850f6` (`analysis/2026-11-13-b6-real-run`).

One Block 5 file was hashed, not opened: `b5-probe.json`. Its counts below are as the lead's probe printed them.
Block-5-aware.

## 1. Identity: the S-14 pin

| Item | Value | Check |
|---|---|---|
| `$S14` | `3551e1a7d4f3bb455b8bfb810d2f406b0fb4b93b` | `git rev-parse b6/analysis^{commit}` |
| Tree | `27770d960cc403989189e7fbfa2077ab2ef65225` | `git rev-parse $S14^{tree}` |
| Tag | `b6/analysis`, annotated, object `082652f25983ccd335acd834861f19455b9ff6fe` | `git rev-parse refs/tags/b6/analysis` |
| Pin candidate it must equal on the 24 files | `b5ab6a71d798e168209fd66a0832f66f97a0b096` | `git show <commit>:<path> \| shasum -a 256`: 24 of 24 equal the table below at `b5ab6a71d` (recomputed 09:45) |
| Pin request with the nine's slots filled | `docs/run_reports/2026-11-13-b6-s14-pin-request.md` @ `9a98eb5b1043643562f772b418cf92a4bce3d1f6` | |
| R3 table (step 7 and 9 `--r3-table`) | stdout of `scripts/b6_r3_table.py` at `$S14`: SHA-256 `1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840`, "Keys covered: 675 of 675; 149 groups; UNSTATED groups: 0." The file is `$R3` = `/Volumes/JW-EXT/b6-custody-run/r3-table-s14.txt`, generated 12:52 PST with `$PY -I -B scripts/b6_r3_table.py` on a `git archive` of `$S14`: exit 0, SHA-256 `1003d87e…9840`, that "Keys covered" line; generator `d3106ecb…0609` at `$S14` | regenerated at `b5ab6a71d` 09:39: the same SHA-256 |
| R3 generator | `scripts/b6_r3_table.py` `d3106ecbc37b941b764efd1bbb51ccf3a99928081e324a602a1089616cb90609` at `b5ab6a71d` | Note: the pin request's §2c gives `30c31dc9…`. That is the generator's digest at `9f1b53767`, before RL-133 changed its label strings |

### The 24 closure hashes (pin request §2a and §2b; RL-129 §6)

These are recorded before the gate run and again after step 9, from the run checkout `$W`. They are also the
launcher's `PIN_TABLE`.

| # | Path | SHA-256 |
|---|---|---|
| 1 | `scripts/independent_recompute_b6.py` | `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759` |
| 2 | `scripts/independent_recompute_b5.py` | `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0` |
| 3 | `joulewise/b6_analysis_check.py` | `634c991c527106d32a93197dc00af113636ce30789b1080431cfa1750d056b30` |
| 4 | `joulewise/b6_analysis_hazards.py` | `9a907a3671dbe210df4d417428c9108f0fdee1c16531bd0bef2fd39b0f27bb2b` |
| 5 | `joulewise/b6_analysis_inputs.py` | `283dfc78341742768dc210b9fd46da19cc0b1f883f316db8106e3db79f89219e` |
| 6 | `joulewise/twins/__init__.py` | `e717dc7f4b7c3b6006f06763873a70c79d95d9ad7cb3183c21eb5251daffaeb0` |
| 7 | `joulewise/twins/engine_twin.py` | `5cd6977d79b2951a6e4351a9e8f95b4f91bc38af50eeb4c5bf2d5115ffedbff8` |
| 8 | `joulewise/twins/harvest_twin.py` | `df39036b24eab0d015c198686e3ed03ae0add341e487636d34ed622fa0695af0` |
| 9 | `joulewise/flags/__init__.py` | `2ea17e7b30b4101d2149be0a216c82e223b903121f50bda8f0d5665b33378ba2` |
| 10 | `joulewise/flags/catalog.py` | `006840601a37009d685db458186492963b15fa7cb9be05a3ae066b9e9ae82ef0` |
| 11 | `joulewise/flags/exclusions.py` | `ebe1678c0fdd60b1ddd20d432cf07412bd321a8629589f4ce4c6b334378f0ad6` |
| 12 | `joulewise/flags/schema.py` | `cd7ce3c00dec53068db4e5c6a41115e264399dbbcc741b96dc8133b67fa1fad8` |
| 13 | `joulewise/desk_compress.py` | `ac770c9407dad936cc742957b6f5673a1b69523156aa2be9baf7de8eb2b56777` |
| 14 | `joulewise/__init__.py` | `df98d6ea46fd21ec24bb8fc4c208e4e01f5167e6c7f2af36490781779d5710cc` |
| 15 | `joulewise/schemas.py` | `f47fbf68c2c4a931854995d1258425b476c4bc8a686dfccf011d9caef092cc3b` |
| 16 | `joulewise/axi_decode_config.py` | `fab53ea66a636458bb8c36f0c5f5f3f014478db8351e246746c9b6bc7c62dd93` |
| 17 | `joulewise/idle_admission.py` | `9dc6b5d45c1dc138a13195b64cd1ca23eac0427c864063f26e274775b5a5a79e` |
| 18 | `joulewise/validation.py` | `82bb03f3aed626446298d186e845b7fe75b3371ca6cbabd7160946bd8e7bfcfd` |
| 19 | `configs/b6/recompute/precision.json` | `e242cab6bb311a9c23d5c6dc06374ed3094a351e36d6954c3589e2b535cc63b0` |
| 20 | `configs/b6/recompute/production_comparison_keys.json` | `62dbfaef9ebc5cfbbe5a00734f5eb8ad3d82389f54f28473ed63db6135b9174d` |
| 21 | `configs/b6/recompute/hazard_sizing.json` | `bf399bec4195b9237f53c747c6fc9cd24066610eba933a0fad767534d970d29b` |
| 22 | `configs/b6/flag_catalog_b6.json` | `b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b` |
| 23 | `configs/b6/registration/acceptance.json` | `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8` |
| 24 | `configs/b6/registration/identity_pins.json` | `513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d` |

**Step 2 record (before step 7).** Checkout `$W` is detached at `$S14`. `git status --porcelain` is empty, and
24 of 24 hashes are equal: 2026-11-13 12:46 PST (`date` 12:46:39, after the hashes); porcelain empty: yes; 24 of 24: yes (`/Volumes/JW-EXT/scratch/rl129-diff/closure_hashes.zsh $W $S14`, every row `wt-ok`; the 24 also equal the launcher's `PIN_TABLE` at `5c53850f6` and appear in the pin request at `9a98eb5b1`).

**The closed nine's slots** (pin request §6, N-1 to N-19), as filled at the cut. They are context here and are not
re-predicted:
pin request §6 at `9a98eb5b1`, filled 2026-11-13 12:40 PST. N-1 to N-13, N-15 to N-20 are met or as reported. N-14 (loop close) is not met, recorded before the read (RL-141 §1 item 1, §4). N-21 (r2-gamma) departed: exit 4, `refused: calibration_capture_missing`, ruled a prediction error (RL-141 addendum 2 B1). The cut is §8a of that request.

## 2. Inputs and their digests

| Variable | Value |
|---|---|
| `W` | `/Volumes/JW-EXT/jw-wt/b6-s14-run` (clean detached checkout of `$S14`) |
| `KITW` | `/Volumes/JW-EXT/jw-wt/b6-custody-kit-r3` (kit at `e1f4f805288ede026980852814af2512a58b4c74`, porcelain empty) |
| `TOOLS` | `/Volumes/JW-EXT/jw-wt/b6-real-run/scripts` at `5c53850f6aad6301b2c74cb0cf0c03fdc404eee8` ("RL-139 fixes 1-7 and the Opus kit review F3"; porcelain empty) |
| `PY` | `/opt/homebrew/opt/python@3.13/bin/python3.13` (`Python 3.13.18`) |
| `ROOT` | `/Volumes/JW-EXT/b6-custody` |
| `RUN` | `/Volumes/JW-EXT/b6-custody-run` (mode 700; it holds `.metadata_never_index`, or Ed has run `mdutil -i off`: `.metadata_never_index`, created 12:46 PST) |
| `MANIFEST` | `/Volumes/JW-EXT/b6-custody/b6-custody-manifest.json`. Confirmed: the custody kit report's verify command (`docs/run_reports/2026-11-12-b6-custody-kit.md:182` at the kit commit) names it, RUN_STATE 302 puts the manifest at `/Volumes/JW-EXT/b6-custody`, and it re-hashed to `MSHA` at 12:46 PST |
| `MSHA` | `b2901d51990812f6c2dadce1a763d90502d85b58a9d5b5b358d4cbb2ba9a9d6b` (RUN_STATE 302) |
| `RSHA` (verify receipt 1) | `57df8a76361ba9d299383c2248e3ba6497dd33fd92dd74be33ec5d89a4830c91` (RUN_STATE 303) |
| `LOOP` | `/Volumes/JW-EXT/b6-custody`. Confirmed: the kit report's line 182 gives it as `--loop-dir`; RUN_STATE 302 puts both loop files there; receipt 1 (`RSHA`, re-hashed 12:46 PST, the RUN_STATE 303 verify) lists `loop_files` `attempts.jsonl`, `state.json`, `loop_state_waived` false. It is not `$RUN` (RL-139 fix 4) |
| `B5OUT` | `/Volumes/JW-EXT/air-home/jw-b5-custody/release-check-final-20261108T0942Z/recompute.json` |
| `B5SHA` | `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc` (`docs/analysis/b5/RESULTS.md`, row RC; RL-134 item 2) |
| `D_gate` | `ace8bfb4f8ceb0b007d0641933ad78f2d469f73af3f159feb63b617bdebf7b9a` (13:26 PST, exit 0: `inputs sessions=1 sha256=ace8bfb4…7b9a`; `$RUN/run-inputs-gate-2.json`, mode 600). Attempt 1's document, superseded: `3bea5b2a…2d9d`, now `$RUN/run-inputs-gate.attempt1.json` |
| `D_block` | `0a1a149cc9403e956121eec2daaf7c852eae1a83ea1c079562c80c4e4cc66a8e` (13:26 PST, exit 0: `inputs sessions=9 block5=pinned sha256=0a1a149c…6a8e`; `$RUN/run-inputs-block-2.json`, mode 600). Superseded, never launched: `eb834c47…4c8f`, now `$RUN/run-inputs-block.attempt1.json` |
| `ORDER` | `r1-alpha r1-beta r1-gamma r2-beta r2-gamma r3-gamma r3-alpha r3-beta r4-alpha` (the order of the arguments only) |

**Step 4 record (structure, before step 6).** The runbook's step 4 and the corrected commands predeclare these
values:
- `mapping sessions=9`;
- `clock_journal: 9 of 9`;
- `copied_records_equal: true`;
- exit 0.

Observed (2026-11-13 12:49 PST, after the nine kit `--list-names` calls, each exit 0): exit 0, and stdout
`mapping sessions=9`, `clock_journal: 9 of 9`, `copied_records_equal: true`, `session_index: r1-alpha then r1-beta
then r1-gamma then r2-beta then r2-gamma then r3-gamma then r3-alpha then r3-beta then r4-alpha`. Report
`$RUN/mapping-report.json` SHA-256 `562f65f146cc414bc504541b252960d1ba88a06982ebc88ccc0d0d5a3ad082eb`; `$RUN/mapping.json`
SHA-256 `79fbf41168049d44ca017c1617b11a1e15c7a453215014a4d562354c97319cf6`. The report's §17-R7 fields:
`stated_order_holds`, `pairing_equals_r7` and `nine_counting` true, no contradiction, the implied pairing equal to
§17-R7's; one meter stream per session; every family equal to the verify map; no flags-file substitution. The
`session_index:` line fills `OPEN[R7-SESSION-INDEX]` (RL-134 item 9; `scripts/b6_s17_fill_check.py r7-text`).
That `mapping.json` is attempt 1's, now `$RUN/mapping.attempt1.json`; section 2a gives the current one.

### 2a. Gate attempt 1 and the relocation correction (class A; RL-134 item 11, RL-139 reading 9)

**Attempt 1.** Launched by the lead 2026-11-13 13:24:02 PST (wrapper `/Volumes/JW-EXT/scratch/b6-gate-launch.zsh`,
out-dir `$RUN/gate`, `D_gate` `3bea5b2a…2d9d`): exit 4, `refused: compression_relocation_ambiguous class=A`, wall
0.331 s, peak RSS 64.5 MB, closure unchanged, stdout empty. The refusal is raised in input authentication
(`joulewise/b6_analysis_inputs.py:86-99` at `$S14`) before any session is read. No restricted or public output was
written. Class A attempts so far: 1 of 3.

**Cause.** Each session's desk log (`<archive>.desk/compression.jsonl`) holds two `compress` rows per file. One
row has the sealed archive path, which the kit relocates (`<source_path>` → `.`). The other has the live,
pre-harvest path under `/Users/edr/night-b6/sessions/<id>/runs-parent/<runs root>` or `…/<id>/custody`. The
program never probes an absolute path, and that second row matched no relocation, so it had 0 matches. No row
matched two.

**Correction.** The per-session entries follow R12's own rule (`archive_pin`, `scripts/b6_r12_verify.py:98-104` at
`$S14`, the form the program was exercised on): custody → `sources/night-custody`, the `_bound` runs root →
`sources/bound-runs`, the other runs root → `sources/claim-runs`. They were written by hand into `mapping.json`
under each session's `relocations`; the kit adds `<source_path>` → `.` itself. The B-4 output was rebuilt first
and is byte-equal to attempt 1's (`mapping-report.json` unchanged, `562f65f1…82eb`, so `OPEN[R7-SESSION-INDEX]`'s
fill stands). The new `$RUN/mapping.json` is SHA-256
`fb6271d209e50322a99c156ec939160b9ac6f99685abd41a2eac818045de0d2f`. It equals attempt 1's apart from the
`relocations` keys. Each new document equals attempt 1's apart from `compression.relocations`.

| Session | `…/sessions/<id>/custody` → | runs root → `sources/claim-runs` | `<runs root>_bound` → `sources/bound-runs` |
|---|---|---|---|
| `r1-alpha`, `r3-alpha`, `r4-alpha` | `sources/night-custody` | `…/<id>/runs-parent/runs_d117_floor_qwen3-1p7b_v5` | `…_v5_bound` |
| `r1-beta`, `r2-beta`, `r3-beta` | `sources/night-custody` | `…/<id>/runs-parent/runs_d117_floor_qwen3-8b_v5` | `…_v5_bound` |
| `r1-gamma`, `r2-gamma`, `r3-gamma` | `sources/night-custody` | `…/<id>/runs-parent/runs_d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` | `…_v5_bound` |

`…` is `/Users/edr/night-b6/sessions`. Each session's entries name only its own `<id>`.

**Offline resolution (not RC-B6-1).** A copy of `:86-99`, with `relative()` from `:25-29`, read only each row's
`event` and `path`. The new gate document resolves 1,628 of 1,628 `r1-alpha` rows to exactly one path (814
distinct). The new block document resolves every row of the nine to exactly one path (14,426 rows; 0 with 0 or
2+ matches). Every relocated name is in that session's kit `--list-names` list.

**Disclosure.** To find the prefixes, the builder seat read the `event` and `path` fields of the nine desk logs
under `$ROOT`, on the lead's instruction under RL-139 reading 9. These are file names, which is structure. No
digest, size or other field was read.

### Block 5's input, predeclared (RL-134 item 2 term 2; build B-5)

| Item | Value |
|---|---|
| Probe | `$PY -I -B $TOOLS/b6_release_record.py b5-probe --checkout <checkout> --block5 $B5OUT --block5-sha256 $B5SHA --out <file>`, run by the lead 2026-11-13 09:30 PST |
| Output | `/Volumes/JW-EXT/scratch/b6-run-prep/b5-probe.json`, SHA-256 `aa120b23c051a77ff01da0778bf469447e577362e1339d735ff0dfb50ed208a1` (re-hashed by me before 09:38, equal) |
| `block5_included` count | **total 44: ALPHA 20, BETA 20, GAMMA 4** (from the probe's stdout `b5-probe total=44`) |
| Step 9's `--block5-expected` | this file, or a copy in `$RUN` that hashes to `aa120b23…08a1`. **Used:** `$RUN/b5-probe.json`, re-run 12:47 PST from `$W` at `$S14` by the corrected command: exit 0, `b5-probe total=44 ALPHA=20 BETA=20 GAMMA=4`, byte-identical to the file above (`aa120b23…08a1`) |
| Hold rule | an observed count below 44 holds the release and goes to the research lead (RL-134 item 2 term 2; item 14). A total of 0 is a hold whether predeclared or observed (Opus F3; probe `block5_included`) |

## 3. The two argv lists, verbatim

The corrected commands of `/Volumes/JW-EXT/scratch/b6-real-run-commands.md` (RL-139), with the variables of
section 2. A relaunch uses a new `--out-dir` (`$RUN/gate-2`, `$RUN/dry-2`, …), and step 11 names that directory.
As amended after attempt 1 (section 2a), the gate run uses `$RUN/gate-2` and the `-2` documents.

**Step 7, the gate run** (one-session `block` on `r1-alpha`, not `--closed`, no `--block5`; RL-134 item 1):

```
nohup $PY -I -B $TOOLS/b6_real_run.py --checkout $W --expect-commit $S14 --stem gate --limit-s 1800 \
    --out-dir $RUN/gate-2 -- block --session $ROOT/r1-alpha/archive --loop-attempts $LOOP/attempts.jsonl \
    --loop-state $LOOP/state.json --inputs $RUN/run-inputs-gate-2.json --inputs-sha256 <D_gate> --workers 1 \
    --restricted-out $RUN/gate-2/restricted.json --public-out $RUN/gate-2/public.json &
$PY -I -B $TOOLS/b6_structure_probe.py --stage gate --restricted $RUN/gate-2/restricted.json \
    --public $RUN/gate-2/public.json --r3-table $R3 --inputs $RUN/run-inputs-gate-2.json \
    --out $RUN/gate-2/structure.json
```

**Step 8, the dry run** (closed nine, serial, normal priority, Block 5 pinned; RL-134 items 2 and 5):

```
nohup $PY -I -B $TOOLS/b6_real_run.py --checkout $W --expect-commit $S14 --stem dry --limit-s <2 × W_pred> \
    --out-dir $RUN/dry -- block $(for s in $ORDER; do echo --session $ROOT/$s/archive; done) --closed \
    --loop-attempts $LOOP/attempts.jsonl --loop-state $LOOP/state.json --block5 $B5OUT \
    --inputs $RUN/run-inputs-block-2.json --inputs-sha256 <D_block> --workers 1 \
    --restricted-out $RUN/dry/restricted.json --public-out $RUN/dry/public.json &
```

The `--session` arguments expand, in order, to: `$ROOT/r1-alpha/archive`, `$ROOT/r1-beta/archive`,
`$ROOT/r1-gamma/archive`, `$ROOT/r2-beta/archive`, `$ROOT/r2-gamma/archive`, `$ROOT/r3-gamma/archive`,
`$ROOT/r3-alpha/archive`, `$ROOT/r3-beta/archive`, `$ROOT/r4-alpha/archive`.

**Step 9, the probe and term 7:**

```
$PY -I -B $TOOLS/b6_structure_probe.py --stage dry --restricted $RUN/dry/restricted.json \
    --public $RUN/dry/public.json --r3-table $R3 --inputs $RUN/run-inputs-block-2.json \
    --loop-attempts $LOOP/attempts.jsonl --block5-expected $RUN/b5-probe.json --term7 \
    --out $RUN/dry/structure.json
```

**Environment of both launches** (RL-134 item 5; build B-2):
- `JW_B5_SYNTHETIC_ONLY` is unset;
- `TMPDIR` is `<out-dir>/analysis-tmp` (mode 700), created by the launcher and removed after the exit is recorded;
- normal priority, with no `taskpolicy -b` and no `nice`;
- no other heavy job on the Air, Dropbox quit, and the MBP not used.

## 4. Step 7: the gate run, predeclared

| Kind | Predeclared |
|---|---|
| Program exit | 0 |
| Launcher stdout | `complete`, then `recompute sessions=1 flags=<n> comparison_stopped=false restricted_sha256=<hex>` |
| Probe stdout, exit | `probe: ok`, exit 0 |
| Wall | predicted 400 s (range 316 to 460). Stop at 1,800 s (`--limit-s 1800`) |

**Probe rows, each `ok`.** These are the 16 check rows of `b6_structure_probe.py --stage gate`:

| Row | Predeclared value |
|---|---|
| `program_sha256` | `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759` |
| `b5_program_sha256` | `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0` |
| `inputs_host` | `Air` |
| `l9_audit` | `not_run` |
| `run_inputs_sha256` | `D_gate` |
| `external_supplied` | `{loop_attempts: true, loop_state: true, block5: false}` |
| `closed` | false |
| `comparison_stopped` | false |
| `option_c_pass` | true |
| `failures_empty` | 0 failure names |
| `compared_classes_clean` | every class with `pass`: `failed` 0 and `unmatched` 0 ("0 unmapped") |
| `run_phase_energy_first_program_only` | 0 |
| `no_block_entry` | 0 `__block__` entries in `first_program_only` |
| `public_one_session` | one public session |
| `public_session_shape` | `r1-alpha`: pack ALPHA, round 1, `counting` true |
| `public_binds_restricted` | the public `restricted_sha256` equals the restricted file's SHA-256 |

**Reported, not a stop.** The quantity accounting for `r1-alpha` (ALPHA): 122 registry keys = compared +
`first_program_only`. That is 4 and 118 when the screen is defined, and 1 and 121 when it is `undefined`.

**Then.** A pass launches step 8. Any other exit, or any row not `ok`, means the nine-session run is not
launched. RL-134 items 11 to 15 then apply (section 7).

## 5. Step 8: the dry run, predeclared

| Kind | Predeclared |
|---|---|
| Before launch | PR #748 merged with the fill and the session index (RL-134 item 9). `W_pred` and the stop are entered in this file and pushed |
| Program exit | 0 |
| Launcher stdout | `complete`, then `recompute sessions=9 flags=<n> comparison_stopped=false restricted_sha256=<hex>` |
| `time_wrapper_exit` | 0 |
| Peak RSS | at most 2 GiB (pin request slot N-8's prediction; reported, not a stop) |

### Wall prediction and stop (RL-134 item 5)

| Item | Rule | Value |
|---|---|---|
| `w_gate` | measured wall of the passing gate run (its `record.json`, `wall_s`; `$RUN/gate-2/record.json` if attempt 2 passes) | `**322.427 s** (`$RUN/gate-2/record.json` `wall_s`; gate attempt 2, exit 0, `probe: ok`, 2026-11-13 13:29:31-13:34:53 PST)` |
| `W_pred` | 9.9 × `w_gate`, rounded up to the next 100 s; **3,400 s** if `w_gate` is missing | `**3200 s** (9.9 × 322.427 = 3,192.0, rounded up)` |
| Alarm | 1.5 × `W_pred`. Nothing is done on the alarm | `**4800 s**` |
| Stop (`--limit-s`) | 2 × `W_pred` (with no `w_gate`: 6,800 s). This replaces the 10,800 s stop for the real run | `**6400 s** (`--limit-s 6400`)` |

For example, `w_gate` = 400 s gives `W_pred` 4,000 s, an alarm at 6,000 s and a stop at 8,000 s.

**At the stop.** The launcher stops the child's process group and exits 124 (`stopped_profile_required`). There
is no relaunch before the sampler profile, and at most one pre-authorised relaunch (RL-134 item 13).

## 6. Step 9: the probe and term 7 on the dry run, predeclared

| Kind | Predeclared |
|---|---|
| Probe stdout | `probe: ok`, then `term7: pass`, exit 0 |
| Closure | step 2's record again after step 9: porcelain empty, 24 of 24 |

**Probe rows, each `ok`.** These are the 28 check rows of `b6_structure_probe.py --stage dry`:

| Row | Predeclared value |
|---|---|
| `program_sha256`, `b5_program_sha256`, `inputs_host`, `l9_audit` | as in step 7 |
| `run_inputs_sha256` | `D_block` |
| `external_supplied` | `{loop_attempts: true, loop_state: true, block5: true}` |
| `closed` | true |
| `comparison_stopped` | false |
| `block5_input` | true |
| `block5_supplied` | `inputs.external_supplied.block5` true |
| `option_c_pass` | true |
| `failures_empty` | 0 failure names |
| `compared_classes_clean` | every class with `pass`: `failed` 0, `unmatched` 0 |
| `class_record_kinds` | every class record has `pass` and `compared` > 0, or no `pass` and all counts 0 (checklist step 3) |
| `both_null_at_most_passed` | `both_null` ≤ `passed` in every class |
| `run_phase_energy_first_program_only` | 0 |
| `no_block_entry` | 0 `__block__` entries |
| `nine_sessions` | exactly `r1-alpha`, `r3-alpha`, `r4-alpha`, `r1-beta`, `r2-beta`, `r3-beta`, `r1-gamma`, `r2-gamma`, `r3-gamma` |
| `sessions_equal_pins` | the nine equal the run-input document's pins |
| `counting_attempts_present` | every counting row of `attempts.jsonl` has its session (checklist step 12) |
| `counting_by_pack` | **ALPHA 3, BETA 3, GAMMA 3** |
| `pairing_not_provisional` | every `pairing` row `provisional: false` |
| `pairing_as_r7` | **§17-R7's pairing:** `r1-gamma` with (`r1-alpha`, `r1-beta`); `r2-gamma` with (`r3-alpha`, `r2-beta`); `r3-gamma` with (`r3-alpha`, `r3-beta`); `r4-alpha` floor-only |
| `pairing_flags_zero` | `pairing_floor_unavailable` 0, `pairing_floor_from_block5` 0, `pairing_provisional` 0 |
| `copied_disclosures_eight_families` | every session carries `copied_disclosures` with the eight families: `monitor_cost`, `arm_host`, `battery_phase`, `subject_temperature`, `reference_history`, `attempt_history`, `g10_history`, `block5_codes_carried` |
| `block5_included` | **44** between-session rows with `block5_included` true. The predeclared count from section 2 is **ALPHA 20, BETA 20, GAMMA 4**, and the count must be above 0 |
| `pstar_desk_removals` | **P\* desk removals 0 of 840 science runs** over the nine: `power_removed` sums to 0 and `records` sums to 840 (§17-R10's registered replay; RL-139 reading 7) |
| `public_binds_restricted` | the public `restricted_sha256` equals the restricted file's SHA-256 |

**Reported, not a stop:**
- `copied_paths_equal_r3`: each family's paths against R3 rows 150 to 157. A difference is ruled by RL-125 item 2: the
  run-input document governs, and a deviation line is added.
- `pins_list_step13_files`: each pin lists `derived/b6-flags.jsonl`, `withheld/spans.json` and
  `derived/bracket-binding.json` (checklist step 13).
- The per-session quantity accounting. The formula: `first_program_only` = 118 (ALPHA, BETA) or 79 (GAMMA); +3 if
  the screen is undefined, and +10 more for GAMMA; otherwise for GAMMA, +5 per contrast with *n* below 2 and +2 per
  contrast with *n* from 2 to 4.
- An `engine_screen_undefined` or `engine_below_minimum` family.

**Term 7** (RL-134 item 8; checklist steps 1 to 8, 10, 12 and 13). The predeclared result is `term7: pass`. The
following are reported with it and not predicted:
- the per-class counts;
- the three totals of the agreement sentence (`compared`, `both_null`, their difference);
- the `first_program_only` total;
- the distinct-key count per label kind.

Step 1's serial-against-pool comparison is skipped: there is one run. The `run_phase_energy` entries in
`first_program_only` are 0.

**Then.** Any `departs` or `not_checked` row, or a `term7: stop <class>`, holds the release (RL-134 items 8 and 14).

## 7. Step 10, and the failure handling by reference

- **S-16** (RL-134 item 17). Block 5's replay counts of each changed §8 rule are entered as one dated §17 line of
  kind "slot fill". If they are not ready, the release record carries `OPEN[S-16]` as a dated deviation.
- **RL-6 (d)** (RL-134 item 10). One `RUN_STATE.md` line, written before any Block 6 number is read: "Block 6 is
  released under its registration on <date>; Paper 1 prints the replication".
- **Failures.** These are handled by RL-134 items 11 to 15 as RL-139 readings 2 to 4 amend them:
  - class A: invocation or document;
  - class B: pin closure;
  - class C: custody (`refused: TypeError` is C first, then E);
  - class D: process (`RuntimeError` counts as D only in a pool run);
  - class E: an unhandled state;
  - exit 3: a hold;
  - over budget: item 13;
  - a term 7 stop or a structure departure: item 14;
  - the gate run and dry run disagreeing: item 15.

  Every launch goes in the ledger (RL-134 item 6).
- **Unblinding** (RL-134 item 10). The release event is the commit of the release record on `main`. Until then,
  nobody opens the following, except through the pinned program, the kit and the probe:
  - every gate and dry attempt's `restricted.json` (`$RUN/gate-2/…`, `$RUN/dry/…` and any later out-dir);
  - either run's `stdout` or `stderr`;
  - `analysis-tmp`;
  - any file under `$ROOT`.

## 8. Attempts ledger (RL-134 item 6)

The launcher appends one line per launch to `$RUN/attempts.jsonl`. It is copied here after each attempt.

| # | Stem, out-dir | Start (`date`) | argv SHA-256 | Exit | Refusal code, class | Wall s | Restricted, public SHA-256 |
|---|---|---|---|---|---|---|---|
| 1 | `gate`, `$RUN/gate` | 2026-11-13 13:24:02 PST (`time_ns` 1794605042392810000) | `e8efd54fa133a891a78e17ac63f48fce141a0dac9bfa6f6536c7f2b27b48df85` | 4 | `compression_relocation_ambiguous`, A (status `refused`) | 0.331 | none written (stdout `e3b0c442…b855`, empty; stderr `4ccb1393…fc12`) |

Row 1 is copied from `$RUN/attempts.jsonl` line 1 (`joulewise.b6_real_run.attempt.v1`) and `$RUN/gate/record.json`
(`closure_unchanged` true, `time_wrapper_exit` 0). Section 2a gives the remedy.
