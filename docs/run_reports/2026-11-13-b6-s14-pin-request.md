# Block 6 S-14 pin request (circulating with the closed nine's slots open)

Date: 2026-11-13 06:20 PST (`date`). Assembled by the lead (orchestrator, Claude Opus 5.5) for the research lead
(Fable 5.2) and Ed. Branch `docs/2026-11-13-b6-s14-pin-request`, off `origin/main` @ `0101ee536`.

**Revised 2026-11-13 08:57 PST (`date`) under RL-129, RL-132 and RL-133** (rulings file `origin/audit/2026-11-10-fable` @ `690d25d67`, `68f792208`), applying the
research lead's review `/Volumes/JW-EXT/scratch/fable-rev-s14-pin-request.md`: replacement texts R-1 to R-12 and
findings 2 to 10. Section 0 lists what changed.

**Status: REQUEST, NOT A PIN.** Under RL-126 item 2 this request circulates now, with the R12 closed nine's numbers
left as open ⟨NINE: …⟩ slots. S-14 is cut only after the nine's finisher has run, every slot is filled, and the
RL-113 term 7 check has been run on the nine's output (section 7). The two items that section 9 had marked
**GATING** (G-1, G-2) are ruled: RL-129 §1 and §2.

**Slots filled and term 7 run, 2026-11-13 12:40 PST (`date`).** The seven-session block read under RL-141 is complete
(section 6). Every slot is filled; none departs from its prediction except N-14 (recorded not met before the read)
and N-21 (ruled, RL-141 addendum 2 B1). The term 7 check on the block's restricted output has no stop (section 7a).
RL-141's text corrections are applied to the paragraph (section 4).

**Blind status.** Blind to Block 6. No custody, archive, session or outcome path was opened. The one Block 6 custody
file read is `/Volumes/JW-EXT/b6-custody-run/verify-receipt.json`: its SHA-256 and its non-outcome fields only
(schema, producer, `loop_state_waived`, session count). Everything else is code, rulings, run reports, synthetic R12
reader numbers as the lead verified them, and Block 5's released release-check record as the R3 table report cites
it. Block-5-aware.

**Where this sits, and the precedent.** No earlier pin *request* exists as a document in the repo. The nearest
precedents are the S-1 collection pin (recorded in the registration's S-1 row and in
`docs/registrations/block6_freeze_by_commit_addendum.md` §1, with annotated tag `b6/collection` on `f31aca19f`) and
Block 5's analysis pins (annotated tags `b5/analysis` … `b5/analysis-r4`, each message naming its commit and its
record). The §17 entries that this pin fills are a docs branch off `main` (PR #748,
`docs/2026-11-12-b6-s17-enter`). This request follows that form: a docs-only run report off `main` that cites the
analysis-line commits by full SHA. It is not on the analysis line, because it changes no analysis byte.

## 0. Revision under RL-129

- **G-1 ruled: merged.** Seat 7's fixes are on the new branch `origin/analysis/2026-11-13-b6-s14-merge` @
  `b5ab6a71d798e168209fd66a0832f66f97a0b096`, off `9f1b53767` (`d38495791` plus the R3 generator). Commits: `a282d0bdc`, the merge of
  `7c8251b28` (tree `29e8f1b945d4`, equal to the research lead's trial merge); `27eedc22c`, RL-125 item 4 term 3's
  `disclosure_record_missing` refusal with one test, the one stale option (c) expectation (review finding 3) corrected
  to the two failure names, and the R12 report's "include block rows" sentence (O-9); `91359b2b2`, an R3 table report
  since superseded; `b7c27d1f9`, RL-133 §1's three fixes from the Opus R12 cold review (HIGH-1 in `check_block`,
  HIGH-2 `session_input_unsupplied` and MEDIUM-1 `both_null` in RC-B6-1, the three RL-133 label strings in the R3
  generator, and their tests); `a82e939cd`, the R3 table report regenerated after RL-133; `b5ab6a71d`, one test
  expectation for `both_null` (test file only). Nothing else in the 24-file closure. No `scripts/b6_r12_*.py`, `tests/test_b6_r12_session_fixture.py`,
  runtime, seam or chain-pin byte changed (RL-129 §1 terms 2-3). Nothing was fetched, checked out, committed or edited
  in the generator's checkout `/Volumes/JW-EXT/jw-wt/sol-p1-b6-r12c` (term 1).
- **The pinned bytes.** Rows 1, 3 and 5 of section 2 changed: RC-B6-1 `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759`, `b6_analysis_check.py` `634c991c527106d32a93197dc00af113636ce30789b1080431cfa1750d056b30`,
  `b6_analysis_inputs.py` `283dfc78341742768dc210b9fd46da19cc0b1f883f316db8106e3db79f89219e`. The other 21 rows are unchanged.
- **Term 4.** The seven test modules exit 0 at the merge head (section 3i), with the F2 witness (section 3g).
- **Term 6, as amended by RL-133 §3: done.** After both RL-133 §4 delta checks closed, the three full roots were read
  once on the final bytes, under new stems, and each comparison with its `e17886bf…` output found no unattributed
  difference (section 3a; the agreement table in section 4 is filled). The earlier reads at `2d540a40…` (ALPHA, BETA)
  are kept as records only.
- **Term 9.** The R3 table was regenerated at the merge head: stdout `1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840` (section 2c).
- **Term 7.** Slot N-1's predeclared value is the merge head's RC-B6-1 SHA-256 (section 6). The nine and denied-26
  are read once, by the merged program, from the merge worktree, after the generator parent exits 0. The prepared
  launcher is `/Volumes/JW-EXT/scratch/rl129-read-nine.zsh`; the lead launches it.
- **RL-133.** The Opus cold review found two HIGH issues and one MEDIUM, fixed before the pin (section 0 commit
  `b7c27d1f9`): a GAMMA contrast with two to four quads, `session_input_unsupplied`, and a `both_null` count beside
  `compared`. The agreement sentence, the paragraph and the term 7 checklist change as RL-133 §2 says (sections 4, 6
  and 7).
- **RL-132.** The first comparer stopped on ALPHA on `time_wrapper_exit` (old 1, a `/usr/bin/time -l` sysctl
  failure in the seat sandbox; new 0). RL-132 §1 ruled it a process-wrapper record, predicted 0; the dated amendment
  to the expected-difference document and the amended comparer `compare_rl132.py` came before the BETA read at
  `2d540a40…`, and the rule carries into the final-bytes comparer (section 3a). For term 7, `time_wrapper_exit` is predeclared 0 (slot N-18).
- **RL-133 §4 delta checks: closed.** The research lead (`/Volumes/JW-EXT/scratch/fable-rl133-delta.md`, 07:49 PST)
  and Opus (`/Volumes/JW-EXT/scratch/opus-rl133-delta.md`, 07:59 PST), both CLOSED-WITH-NOTES; no finding changes a
  closure byte (O-15, O-16).
- **Still owed before the cut:** the nine's read and slots (O-1, O-17) and the term 7 check (O-2).

## Contents

0. Revision under RL-129
1. What is being pinned, and at which commit
2. The exact bytes to pin
3. Evidence on the pin candidate
4. Fable's paragraph (verbatim, with the RL-125 and RL-126 replacements)
5. Fable's notes for the lead, as amended
6. The open ⟨NINE⟩ slots and their predeclared values
7. The RL-113 term 7 checklist (verbatim, with the RL-125 replacements)
8. The cut procedure
9. Owed items, with owners
10. Rulings cited, and conflicts found

---

## 1. What is being pinned, and at which commit

S-14 is the Block 6 analysis commit (`docs/registrations/block6_replication_DRAFT.md` §13 and slot S-14; §17-R1,
§17-R4, §17-R10, §17-R11 as entered by PR #748 @ `27b6cacfd`). PR #748's S-14 row reads: "the printing program
RC-B6-1 (`scripts/independent_recompute_b6.py`) and the block-5 script it loads, the E_add code, the vendored S-3,
S-4 and S-18 files, and the precision and comparison-key tables", with
`OPEN[S-14-PIN: commit, tag, sha256 of scripts/independent_recompute_b6.py, sha256 of scripts/independent_recompute_b5.py = d49103e8...a2e4e0, sha256 of precision.json and production_comparison_keys.json]`.

| Role | Ref | Full commit |
|---|---|---|
| Pin candidate (the code the three full reads and the closed nine are read by) | `origin/analysis/2026-11-13-b6-s14-merge` | `b5ab6a71d798e168209fd66a0832f66f97a0b096` |
| Generator of the closed nine and denied-26 (not the pin candidate) | `origin/analysis/2026-11-11-b6-r12` | `d3849579184551c6c3431abd2c6bb65f7a0bd876` |
| R3 table generator (base of the merge branch; regenerated at the merge head, section 2c) | `origin/analysis/2026-11-12-b6-r3-table` | `9f1b537679f17c69535d46f5a3e44af0c686a536` |
| Rulings file cited | `origin/audit/2026-11-10-fable` | `258612016feedb0587a09cfbe58724471b6b77e2`; RL-128 and RL-129 at `690d25d67199831cc5f4f1fc840788f66866d31a`; RL-132 at `68f792208` |
| §17 entries (S-14 "pin OPEN") | PR #748 head | `27b6cacfd420db4bddc2dd0b5c7afa53a107718d` |

The S-14 commit itself is not yet chosen. It is the analysis-line commit at the cut (section 8), and it must hold
every byte in section 2 unchanged.

## 2. The exact bytes to pin

SHA-256 of the file bytes at the merge head `b5ab6a71d`, computed 2026-11-13 from `git show b5ab6a71d:<path>` and
from the merge worktree's files (equal). Rows 1 and 5 changed with the merge (RL-129 §1), rows 1 and 3 with RL-133
§1; the other 21 rows are identical to `d38495791` and `9f1b53767`. "Main" says whether `origin/main` @ `0101ee536` has the same bytes;
"absent" means the path is not on that commit. RC line numbers in this request are at the merge head (`b7c27d1f9` code): the
`disclosure_record_missing` lines moved every citation after RC:1214 down by five, and RL-133 moved some further.

### 2a. The program: RC-B6-1 and every repository file it executes

The closure was taken by importing RC-B6-1 from a `git archive` of `d38495791` under `python3.13 -I`, plus its two
deferred imports (`joulewise.b6_analysis_hazards`, RC:293; `joulewise.b6_analysis_check`, RC:1312), and listing every
loaded module under the tree. The research lead confirmed the list by an open-file trace of a synthetic nine-session
block (RL-129 §5). `scripts/independent_recompute_b5.py` is not imported; RC-B6-1 hashes and `exec`s it
(RC:48-65).

| # | Path | SHA-256 | Role | Self-checked by the program | Main |
|---|---|---|---|---|---|
| 1 | `scripts/independent_recompute_b6.py` | `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759` | RC-B6-1, the printing program and the S-13 gate | recorded as `program_sha256` (RC:1452) | absent |
| 2 | `scripts/independent_recompute_b5.py` | `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0` | Block 5 recompute at its release digest | yes, `B5_SHA256` (RC:50), refuses `b5_script_digest_mismatch`; recorded as `b5_program_sha256` | same |
| 3 | `joulewise/b6_analysis_check.py` | `634c991c527106d32a93197dc00af113636ce30789b1080431cfa1750d056b30` | `check_block`, option (c)'s second side (RL-113, RL-114, RL-133 fixes in) | no | absent |
| 4 | `joulewise/b6_analysis_hazards.py` | `9a907a3671dbe210df4d417428c9108f0fdee1c16531bd0bef2fd39b0f27bb2b` | the E_add code and the P* desk exclusion (§17-R10) | no | absent |
| 5 | `joulewise/b6_analysis_inputs.py` | `283dfc78341742768dc210b9fd46da19cc0b1f883f316db8106e3db79f89219e` | `AuthenticatedInputs` (§17-R11), with seat 7's F3 and F8 | no | absent |
| 6 | `joulewise/twins/__init__.py` | `e717dc7f4b7c3b6006f06763873a70c79d95d9ad7cb3183c21eb5251daffaeb0` | twins package | no | same |
| 7 | `joulewise/twins/engine_twin.py` | `5cd6977d79b2951a6e4351a9e8f95b4f91bc38af50eeb4c5bf2d5115ffedbff8` | engine twin | no | same |
| 8 | `joulewise/twins/harvest_twin.py` | `df39036b24eab0d015c198686e3ed03ae0add341e487636d34ed622fa0695af0` | harvest twin | no | same |
| 9 | `joulewise/flags/__init__.py` | `2ea17e7b30b4101d2149be0a216c82e223b903121f50bda8f0d5665b33378ba2` | flags package | no | same |
| 10 | `joulewise/flags/catalog.py` | `006840601a37009d685db458186492963b15fa7cb9be05a3ae066b9e9ae82ef0` | `load_catalog` (§17-R6) | no | same |
| 11 | `joulewise/flags/exclusions.py` | `ebe1678c0fdd60b1ddd20d432cf07412bd321a8629589f4ce4c6b334378f0ad6` | sealed `compute` (§17-R6, C3) | no | differs |
| 12 | `joulewise/flags/schema.py` | `cd7ce3c00dec53068db4e5c6a41115e264399dbbcc741b96dc8133b67fa1fad8` | flag schema | no | same |
| 13 | `joulewise/desk_compress.py` | `ac770c9407dad936cc742957b6f5673a1b69523156aa2be9baf7de8eb2b56777` | the one read path, `read_bytes` (§17-R11, 9a) | no | absent |
| 14 | `joulewise/__init__.py` | `df98d6ea46fd21ec24bb8fc4c208e4e01f5167e6c7f2af36490781779d5710cc` | package init (loaded by any `joulewise` import) | no | same |
| 15 | `joulewise/schemas.py` | `f47fbf68c2c4a931854995d1258425b476c4bc8a686dfccf011d9caef092cc3b` | loaded by package init | no | same |
| 16 | `joulewise/axi_decode_config.py` | `fab53ea66a636458bb8c36f0c5f5f3f014478db8351e246746c9b6bc7c62dd93` | loaded by package init | no | same |
| 17 | `joulewise/idle_admission.py` | `9dc6b5d45c1dc138a13195b64cd1ca23eac0427c864063f26e274775b5a5a79e` | loaded by package init | no | same |
| 18 | `joulewise/validation.py` | `82bb03f3aed626446298d186e845b7fe75b3371ca6cbabd7160946bd8e7bfcfd` | loaded by package init | no | same |

Rows 14 to 18 are loaded because `import joulewise` runs the package init. I did not check whether any of their
code is reached by the analysis; they are listed so that the pin is the whole executed closure.

### 2b. Tables and vendored registration files the program reads

| # | Path | SHA-256 | Slot / role | Checked by the program at | Main |
|---|---|---|---|---|---|
| 19 | `configs/b6/recompute/precision.json` | `e242cab6bb311a9c23d5c6dc06374ed3094a351e36d6954c3589e2b535cc63b0` | S-13 precision table (§17-R2) | RC:1471-1473, at import | absent |
| 20 | `configs/b6/recompute/production_comparison_keys.json` | `62dbfaef9ebc5cfbbe5a00734f5eb8ad3d82389f54f28473ed63db6135b9174d` | comparison-key registry (§17-R2) | RC:1641-1645 | absent |
| 21 | `configs/b6/recompute/hazard_sizing.json` | `bf399bec4195b9237f53c747c6fc9cd24066610eba933a0fad767534d970d29b` | P* / E_add sizing (§17-R10) | RC:294-295, with `--inputs` | absent |
| 22 | `configs/b6/flag_catalog_b6.json` | `b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b` | **S-3**, vendored; equals the S-3 row and `f31aca19f` | RC:315-317 | absent |
| 23 | `configs/b6/registration/acceptance.json` | `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8` | **S-4**, vendored; equals the S-4 row and `f31aca19f` | RC:1731, with `--inputs` | absent |
| 24 | `configs/b6/registration/identity_pins.json` | `513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d` | **S-18**, vendored; equals the S-18 row and `f31aca19f` | RC:1732, with `--inputs` | absent |

### 2c. The R3 printed-quantity table (cited by commit, not part of the program)

§17-R3 (PR #748): "At the pin it is generated by script from the pinned commit, with no UNSTATED row, and this line
cites it by commit."

| Item | Value |
|---|---|
| Commit | `b5ab6a71d798e168209fd66a0832f66f97a0b096` (`origin/analysis/2026-11-13-b6-s14-merge`), regenerated there under RL-129 §1 term 9. Generator branch `9f1b53767` (`origin/analysis/2026-11-12-b6-r3-table`); Fable delta review ADMIT (RL-125 preamble) |
| Generator | `scripts/b6_r3_table.py` `d3106ecbc37b941b764efd1bbb51ccf3a99928081e324a602a1089616cb90609` at `b5ab6a71d` (`30c31dc9…f712` was `9f1b53767`'s) |
| Its test | `tests/test_b6_r3_table.py` `95cf44148dc9037039be8f3079fc742fa8d3351bad69a434d0b8dcce7baf1f00` at `b5ab6a71d` (`8c9fd275…3565` was `9f1b53767`'s) |
| Stdout SHA-256 | `1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840`, generated 2026-11-13 about 07:30 PST from a `git archive` of `b7c27d1f9` (the same generator inputs as `b5ab6a71d`; `python3.13 -I -B scripts/b6_r3_table.py`, exit 0, "Keys covered: 675 of 675; 149 groups; UNSTATED groups: 0"; 149 groups stated before regenerating) |
| Check against `9f1b53767` (RL-129 §1 term 9 as amended by RL-133 §3 item 8) | Not byte-equal to `9f1b53767`'s `7b7920cf7315d0a435d1eaae2f5bf35e45e8158d4335c83f64aad2828260254c`, as predicted. With the RC-B6-1 and `b6_analysis_check.py` SHA-256 lines and every `RC:`/`CHK:` line number removed, and the label cell of the `contrast/<phase>/p`, `holm_p` and `outcome` rows replaced by a placeholder, the tables are byte-identical (normalised SHA-256 `82a0b33ad920d1d0a6577a4425597231745f8175c61c71c90ed9254441fd51f1`). The "Keys by label" counts follow from those three labels only (the RL-114 contrast label 10 to 6 keys; the new `p` and `holm_p` labels 2 each; the word label renamed, 2 keys). Checker kept outside the repository: `/Volumes/JW-EXT/scratch/rl133/r3_check_rl133.py`, SHA-256 `d4ff2deb6e46779ff8e54a1854e79baa2367bae9832f41ea41da0100f269ef09`. An intermediate table at `27eedc22c` (`7e002000…e565`) is superseded |
| Inputs it prints | rows 1, 3, 19, 20 above, and `scripts/b6_r12_verify.py` `947d1c3d43eccf6ab6f19fb5bed785c2443b69899faa7a5c8efd356f834295c2` (the R12 verify map, the source of the copied-record file names; a fixture tool, not pinned) |
| Report | `docs/run_reports/2026-11-12-b6-r3-table.md` at `b5ab6a71d`: the regenerated table and the term 9 check; the RL-101 and RL-104 sections are as at `9f1b53767` |

### 2d. Not in the pin set

- `scripts/b6_custody_kit.py`: RL-100 item 4, "The kit is not part of the S-14 pin set: the recompute binds its
  output through `--inputs-sha256`."
- The R12 fixture tools (`scripts/b6_r12_*.py`) and their tests: synthetic harness, not analysis code.
- `scripts/compare_b5_recompute.py` (`d12a1652…`): Block 5's comparator, cited for the RL-101 record only.
- The Block 5 script's three reads of the analysis checkout (`flag_catalog.json`, B5:925; `sizing_b5.json`,
  B5:964; the calibration acceptance, B5:2559) are in `Window.__init__` and `sensitivity_bound`, which RC-B6-1
  does not call. A synthetic nine-session block opened only the 24 files above (RL-129 §5).

### 2e. What the recorded hashes bind, and what they do not

The program's own output records `program_sha256` (row 1 only, RC:1452) and `b5_program_sha256` (row 2). It does not
record rows 3 to 18. So "read by program `90e22603…`" binds RC-B6-1 and the Block 5 script, not `check_block`, the
twins, the inputs layer or the hazard code. The binding for those is the commit: the pin names the commit and every
hash in 2a and 2b. RL-129 §6 accepts this, and a read counts as "by the pinned closure" when three things are
recorded for it: (1) the receipt's `verifier_commit` (`b6_r12_verify.py:415, 439`) is the S-14 commit, or a commit
whose 24 files hash the same; (2) the reader worktree is clean (`git status --porcelain` empty) before the first read
and after the last; (3) the 24 SHA-256 values, recomputed from the reader worktree's files at both times, equal the
table above. The same three are recorded for the blind dry run and the release run, from a clean detached checkout
of the S-14 commit. Section 8 step 4 and G-3 apply them.

## 3. Evidence on the pin candidate

### 3a. The three full-volume single-pack roots (RL-98, RL-123 §2)

Read on the Air by the pinned program, RC-B6-1 `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759` (merge head `b5ab6a71d`, after RL-133), under RL-129
§1 term 6 as amended by RL-132 §1 and RL-133 §3, with new stems `full-reader-rl133-<pack>`: the RL-123 reader command
(`scripts/b6_r12_full_verify.py`, the same sanitised wrapper and MBP sidecars) from the merge worktree, one at a time,
`taskpolicy -b`, 2026-11-13 08:00-08:24 PST (ALPHA 08:00-08:08, BETA 08:09-08:17, GAMMA 08:17-08:24). Each root was read once on the final bytes, after both RL-133 §4 delta checks had closed.
The overlap record names the closed nine's root (RL-126 item 7). This table replaces the `e17886bf…` one.

| Full root | Generating host | Program SHA-256 | Keys | Compared rows, agree | Null on both sides | Agreeing on a value | `first_program_only` | Air reader wall s | Air per-process RSS bytes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| ALPHA MBP -1 | MBP | `90e22603…1fb85759` | 122 | 699 | 198 | 501 | 118 | 455.070224958 | 981,516,288 |
| BETA 23 | Air | `90e22603…1fb85759` | 122 | 699 | 198 | 501 | 118 | 457.761211291 | 1,064,140,800 |
| GAMMA MBP -2 | MBP | `90e22603…1fb85759` | 93 | 649 | 234 | 415 | 79 | 381.804106959 | 956,203,008 |

Each: reader parent exit 0, production exit 0, comparator agrees, `FullProductionSessionTests` exit 0, 0 `__block__`
entries in `first_program_only`, no `engine_below_minimum` family.

The base of each comparison is the root's `e17886bf…` read (stems `full-reader-rl123-*`, R12 report @ `d38495791`). The
difference predicted before the reads was the program SHA-256, digests derived from it, a `both_null` key in every
class record equal to counts predeclared from the old outputs, and the process records of section B. Result:
**unattributed = []** for each of the three packs.

- Expected-difference document `/Volumes/JW-EXT/scratch/rl129-expected-diff.md`, with its RL-132 and RL-133
  amendments written before the reads they govern; SHA-256 now `77ccb71dd88f9c5785594c0fdc62f4f70892f7ce2cdf3f27b0f7b1ff9a5a60df`.
- `both_null` predeclared by `/Volumes/JW-EXT/scratch/rl133/predeclare_both_null.py` into `both_null_predeclared.json`
  (`10c9cc21b38737bc20d4174a173c754c217183eb328e3d433fe16212bd8d36f3`): ALPHA 198, BETA 198, GAMMA 234 (inclusive, replication, side_by_side and
  summary block rows).
- Comparer `/Volumes/JW-EXT/scratch/rl133/compare_rl133b.py`, SHA-256 `73b890bc002aa94d53990f7401ead8363d15ba38d6cfb2bc700ac11a4f7d7361`, outside the
  repository: a plain JSON path difference of old against new, with RL-132's wrapper rule and RL-133's `both_null` rule.
- **Comparer fix, recorded.** The first RL-133 comparer (`compare_rl133.py`, `911463db1206612939fc61442eb715389f65b4401e1bbc6982165972be2839cb`) stopped
  on ALPHA (`compare-rl133-alpha.json` `f93f27d9b91c0723393cd13e3bfc03c8eea91f87a9a8d183521f7dbdcaaaad6f`, kept as the stop record) because its
  path pattern for the new key, `[a-z_]+`, did not match the class name `neg8`. That is a comparer bug, not a program
  difference: `neg8`'s `both_null` was 0, equal to its predeclared value. Only that character class was changed, to
  `[a-z0-9_]+` (`compare_rl133b.py`); ALPHA was re-compared from its existing outputs with no re-read and passed, and
  BETA and GAMMA were read and compared with the fixed comparer. Every `both_null` value equalled the predeclaration.
- ALPHA: numbers `98b71de1689c75d02e3120b16b704f8e58469e0e8b681722d0ab5a3f7ba0789b`, observations `6b329c9cadcd479ae1ecbd22d4bdf33fa7aafc961c71c36a0f3f1e1eb22ebe48` (unchanged), program receipt `55d6ca67805376d64e0308dc92f5a35516ca927be776470be7c4d0b0e9af1530`, comparison record `compare-rl133b-alpha.json` `11ae2d16bbd104b00a438e513d2632d56460b3650657653e9bcec2451df307c6`; test exit 0, `time_wrapper_exit` 0, `verifier_commit` `b5ab6a71d`, manifest unchanged `98031e47…`.
- BETA: numbers `c45b067b8c5aea7d109a6adac3057b887cd7388bf2ff75e74dd86b8bbd2116d8`, observations `17df2d661cf13ae971570808fc7e338cc8ec5011c73608ea312866319150a72f` (unchanged), program receipt `a4b581a6954649f10fccc3068e9d4ef901b52b36de5a26fa558b0db13b3273c2`, comparison record `compare-rl133b-beta.json` `3d92f36f361392ea50796ede62f44e4ef1c97f3d963a903fbb2465fb893b62ea`; test exit 0, `time_wrapper_exit` 0, `verifier_commit` `b5ab6a71d`, manifest unchanged `8d3c09a2…`.
- GAMMA: numbers `22e2eb662f4d71a560501958b13027144a5d316ecfff7c555cff2ba65da0f42c`, observations `8553cbc79fbf650e11a5f6c2400b849e480183d83ac77f0fcbadaa4687509e66` (unchanged), program receipt `14e28cb7431b4f263ff115cd2eb097d7ccb71ffd4ca440a0942bc9580d18457a`, comparison record `compare-rl133b-gamma.json` `e071ff1cb68a941a1d7f08cf21f43b59f4f62a3e20a99109237a3d3a62b54a6d`; test exit 0, `time_wrapper_exit` 0, `verifier_commit` `b5ab6a71d`, manifest unchanged `71b6ec28…`.
- History, kept as records and not the base: the first comparer (`compare_rl129.py` `728bd15506c2e910259cb3c07ff6efa062dbf928d783a570c824d76da07a6b45`)
  stopped on ALPHA's `time_wrapper_exit` (`compare-alpha.json` `a5cfc2aa96ccbb472b857ec67147e307a10524de63c3ddd9d9a2d32f557c12dd`); RL-132 ruled it a
  wrapper record (old 1 was `/usr/bin/time -l` failing with the sysctl line in the seat sandbox), and the amended
  comparer `compare_rl132.py` (`14e9d6808cd7a7bfe601996cf1119dee5e0ee40795e719b79feb81a301041559`) passed ALPHA and BETA at `2d540a40…`
  (`compare-rl132-alpha.json`, `compare-rl132-beta.json`). RL-133 then changed two closure files, so those reads are
  pre-fix records.
- RL-129 §6 for these reads: `verifier_commit` is `b5ab6a71d` in all three receipts; before each run the runner asserted
  the head `b5ab6a71d`, a clean worktree and the RC-B6-1 and `b6_analysis_check.py` hashes, and after the last read the
  worktree was clean (`git status --porcelain` empty) and the 24 SHA-256 values recomputed from it equal section 2.

**Lead-verified facts** (from the reader outputs of the three roots, program `e17886bf…`; names and counts only;
they carry to the `90e22603…` re-reads, whose outputs differ from these only in the predicted fields above):

- `first_program_only` holds **0** entries with session `__block__`, in all three roots.
- Every class record with `pass` has `failed` 0 and `unmatched` 0.
- Every class record without `pass` has `compared`, `passed`, `failed` and `unmatched` all 0.
- `run_phase_energy`: `first_program_only` 0 in each root, with `compared` 357, 357 and 297, and `pass` true
  (RL-125 item 1's owed count, discharged for the three roots).
- Compared totals 699, 699 and 649; `first_program_only` 118, 118 and 79; registry keys 122, 122 and 93.

Reconciliation (my arithmetic from these numbers and RL-125 item 1): ALPHA/BETA 357 run-phase-energy + 4 session
quantity + 338 block rows = 699; GAMMA 297 + 14 + 338 = 649. 122 − 4 = 118 and 93 − 14 = 79, so every
`first_program_only` row is a session quantity key.

**Correction to the R12 report: done.** Its pin-candidate section said the first-program-only counts "include block
rows as well as session quantities". That was wrong: there are 0 `__block__` entries on all three full roots. The
sentence is corrected on the merge branch (`27eedc22c`), not in the generator's checkout (RL-129 §1 terms 1-2; O-9).
The table is unchanged.

### 3b. Launchers and exit codes (RL-125 item 4 term 2)

Every R12 launcher treats a nonzero exit as failure: `scripts/b6_r12_finish.py:25`
(`if receipt["exit_code"] != 0 or not receipt…["pass"]: raise RuntimeError(...)`; file SHA-256 `a21f3ec1…9c45`, the
same at `d38495791` and the merge head). So the named refusal `disclosure_record_missing` (exit 4, section 4) cannot
be read as success or as "comparison disagrees" by R12 tooling. The real-run launcher is section 9, O-6.

The nine's finisher is `scripts/b6_r12_reduced_finish.py`, run by `b6_r12_dry_supervise.py --reduced`. It takes its
exit check from `scripts/b6_r12_finish.py:25` (`agree`), so a nonzero exit or a comparator that does not pass raises.
It runs the serial and pool-2 reads, the byte comparison, the single-session shape reads, the denied-26 read, the
seven named `DeclaredShapeTests` and `ReducedSetTests`, and writes `reduced-finish-receipt.json`. It is run from the
merge worktree, after the generator parent has exited 0. Its output names are fixed (`option-c-*`), so a second read
of the same root would overwrite the first; the nine is read once (RL-129 §1 term 7; review finding 8), and the
prepared launcher refuses if any finisher output already exists.

### 3c. Custody (not a pin input)

Custody copy-mode `verify` passed (RUN_STATE 303). Receipt `/Volumes/JW-EXT/b6-custody-run/verify-receipt.json`,
SHA-256 `57df8a76361ba9d299383c2248e3ba6497dd33fd92dd74be33ec5d89a4830c91` (re-hashed 2026-11-13; schema
`joulewise.b6_custody_verify_receipt.v1`, produced by `b6_custody_kit.py verify`, 9 sessions,
`loop_state_waived` false). `inputs` waits for `mapping.json` (RL-100) after the pin. No Block 6 byte is read by the
program before the cut (RL-126 item 4).

### 3d. RL-101 condition and RL-99 item 2: the Block 5 record

Discharged in the R3 table report's section "RL-101 condition: R and R_cm compared on Block 5" (at `9f1b53767`;
Fable re-checked it, RL-125 preamble). Block 5's `release-check-final-20261108T0942Z/comparison.json`, SHA-256
`b12b7e1b32b27159be894221dcde7e334784061314fe91a39166faa36f72f4c9`: family `dominance_ratio`, 12 rows, all `AGREE`,
`counts` `{"fail": 0, "pass": 12}` (8 `R`, 4 `R_cm`); `verdict.json` `c73593f3…` gives `agree`;
`recompute_program_sha256` is `d49103e8…a2e4e0`, the bytes pinned in row 2. Code: CMP:2075,
IR5:2987-2999 (`floor["R"]` at 2987, `floor["R_cm"]` at 2996), `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md:40`. The 12
dominance keys keep `single-source`. This is also the Block 5 record that RL-99 item 2 asks the pin request to cite for
"the same byte-pinned functions agreed with the registered analysis on Block 5 in every compared family".

### 3e. RL-104 check 2

Discharged in the R3 table report's section "RL-104 check 2" (ten files, each with a route into RL-100 item 1's set;
Fable confirmed all ten, RL-125 preamble). Check 3 (the item-83 hand check) is at the release (section 9, O-4).

### 3f. RL-48 F10 and RL-99: L9 audit

L9 audit: **not run** (RL-99, recorded before the blind dry run). The ALPHA and BETA cell and floor estimators print
`single-source`. The run-input document carries `l9_audit: "not_run"`; RC-B6-1 refuses any other value except
`completed` (RC:1712-1713). This answers RL-48 F10's "The pin request tells me which."

### 3g. Decision 7b (RL-30; §17-R8)

The two acceptance tests exist on the pin candidate and pass, run 2026-11-13 07:36-07:38 PST at the merge head
`b5ab6a71d` (merge worktree; `taskpolicy -b python3.13 -B -m unittest -v
tests.independent_recompute.test_b6_production`, 18 tests, 100.1 s, OK):

- `tests.independent_recompute.test_b6_production.Production.test_loaded_b5_is_exactly_the_release_pin_and_tamper_refuses ... ok`
- `tests.independent_recompute.test_b6_production.Production.test_7b_b6_phase_output_equals_b5_own_output_including_corners ... ok`

RL-48's condition for 7b is the strengthened witness of F2, with decode and prefill given different synthetic
values (40 W and 60 W). It is on the pin candidate since the merge of `7c8251b28` (RL-129 §1) and passes: the two
tests above, `ok`, 2026-11-13; SHA-256 at the merge head `b5ab6a71d` of
`tests/independent_recompute/support_b6_production.py` `5e70e2d1c1988a9d4e3223c1a604c1a79199fade7e83c22745aade80546ffc7c`
and `tests/independent_recompute/test_b6_production.py`
`1307ff7e5a5a15b52ba0f8d4d9037572d02325bbb10efb151de14be5f097ed1d` (it gained the RL-133 §1b test and the corrected
comment; the 7b witness is unchanged).
On `d38495791` the same two tests passed with the older 50 W witness.

### 3h. Other R12 obligations already shown (RL-126 §2)

- Denied action (RL-49): `denied-air-26`, generation parent exit 0 (lead, 02:46). Its read by the pin candidate runs
  in the nine's finisher (`--denied-root` 26) and is slot N-12.
- RL-48 item 6, generation bound to real time: root 23, 0.240 native/primary.
- RL-98 term 1, the production-size reader test: passed (R12 report, final section).
- Focused R12 module at the handoff: `tests.test_b6_r12_session_fixture`, 86 tests, 72 passed, 14 integration skips,
  exit 0 (R12 report, "Final notice-8 handoff"). At the merge head: the same, section 3i.

### 3i. RL-129 §1 term 4 (and RL-133 §4 item 1): tests at the merge head

Run 2026-11-13 07:35-07:43 PST, one module at a time, from the merge worktree `/Volumes/JW-EXT/jw-wt/rl129-s14-merge`
at `b5ab6a71d`, `taskpolicy -b`, the sanitised Python 3.13 with `TMPDIR=/Volumes/JW-EXT/tmp`. Worktree clean after
the last. These ran while the nine generated. (A first run at `b7c27d1f9` had one failure: the CLI public comparator
test pinned the class record's key set without `both_null`; `b5ab6a71d` updates that expectation, test file only.)

| Module | Tests | Result | Wall s |
|---|---:|---|---:|
| `tests.independent_recompute.test_b6_production` | 18 | OK, exit 0 | 100.1 |
| `tests.independent_recompute.test_block6` | 42 | OK, exit 0 | 154.4 |
| `tests.flags.test_flags_exclusions` | 34 | OK, exit 0 | 0.9 |
| `tests.twins.test_harvest_twin` | 16 | OK, exit 0 | 0.0 |
| `tests.twins.test_engine_twin` | 12 | OK, exit 0 | 0.2 |
| `tests.test_b6_r12_session_fixture` | 86 | OK (14 integration skips), exit 0 | 202.9 |
| `tests.test_b6_r3_table` | 11 | OK, exit 0 | 8.2 |

RL-129: `test_listed_disclosure_record_absent_refuses_by_name` fails on the pre-fix program (`AttributeError`) and
passes. `test_option_c_second_producer_disagreement_stops_with_exit_three` asserts exactly
`["harvest_energy:neg8-refcorpus-r01/prefill", "comparator:run_phase_energy:b6-alpha-r1:neg8-refcorpus-r01/prefill"]`.
RL-133: `GammaBelowMinimum` (2, 3 and 4 kept quads on each arm: exit 0, gate passes, the short contrast's `p` and
`holm_p` in `first_program_only`, one `engine_below_minimum` check), the sibling-Holm test, the claim-word guard test,
`BothNullCount`, and `test_pinned_session_not_supplied_refuses_by_name` (exit 4, `refused: session_input_unsupplied`).
**Mutant:** with the substitution removed (the short contrast's real p passed to `engine.adjust`),
`test_below_minimum_sibling_holm_uses_the_registered_rule` fails (exit 3; in the probe of the same fixture the other
contrast's twin Holm value is 0.0233 against the registered 0.0467) and the other two below-minimum tests pass; the
file was restored and its SHA-256 re-checked.

---

## 4. Fable's paragraph (verbatim, with the RL-125 and RL-126 replacements)

Source: `/Volumes/JW-EXT/scratch/fable-s14-pin-paragraph.md` (Fable 5.2, 2026-11-13 05:50 PST), with the replacement
texts of `/Volumes/JW-EXT/scratch/fable-rev-r3-table-delta.md` ("Changes to the pin paragraph and the term-7
checklist", RL-125), `/Volumes/JW-EXT/scratch/fable-rl126-proportionality.md` §4 (RL-126) and
`/Volumes/JW-EXT/scratch/fable-rev-s14-pin-request.md` R-7 (RL-129) and `/Volumes/JW-EXT/scratch/fable-rl133.md` §2
(RL-133) applied. Nothing else is changed. The one ⟨LEAD: …⟩ choice is made as the bracketed note after the paragraph says.

> Slots marked ⟨NINE: …⟩ are filled by the lead from the readers' records of `r12-r3-closed-air-25`. The
> request circulates with these slots open and marked outstanding (RL-126). S-14 is not cut until they are
> filled and the term 7 check has been run on the nine's output. A slot that differs from its predeclared
> value comes to me before the cut.

**What the option (c) comparison compares, and what it does not.** Under option (c) the S-13 comparison is
made over the second side's keys only: the first program's table is cut down to the keys the second side
holds, and those rows are compared. A key that only the first program prints is not compared and not counted.
The gate records it as `first_program_only`: in the restricted output as a list of class, session and key
name, with no values, and in the public comparator as a count per class beside `compared`, `passed`,
`failed` and `unmatched`. These keys do not change `pass`, and the gate does not refuse on them, because
most first-program keys have one producer by registered design. Run phase energies are the exception. Every run in the registered run set (each run of a kept unit, the surviving drift-screen references and the clean corpus) is compared at 1 mJ under §17-R2, with no condition, so a run-phase-energy row in `first_program_only` is not an expected state. It is reported like any other, and it stops the agreement sentence until the research lead has ruled on it. A GAMMA contrast with fewer than five kept quads is a registered state: the first program prints p = 1.0 and `not_estimable` for it. With two to four quads the second side still compares the count, the mean difference, its spread and the bounds. It does not compare `p` or `holm_p`, which are listed in `first_program_only`, and it requires that both are 1.0 and the word is `not_estimable`. The Holm value of the session's other contrast is computed on both sides with p = 1.0 for the short one. Two inputs are shared and not independent: the engine twin is given the first program's floor gate (floors are single-source), and the block check takes Block 5 inclusion and the binding-defect mark from the first program. It checks the rule and the arithmetic on those inputs. (RL-133.) On the three full-volume roots every `first_program_only` row is a session quantity key: none is a run phase energy and none is a block row. A class record without `pass` holds only
first-program keys and was not compared. A key that only the second side holds is compared against nothing
and fails the gate, unless the second side's own value for it is null, in which case the row passes as null on
both sides. The cold review found no route to such a key in the pinned code, and with `--inputs` the first
program's keys are checked against the registered list before the comparison. An excluded screen run is read but is not a compared run: its energies are not compared,
and its trace flags do not stop the comparison. A screen run that is not excluded stays a compared run,
and a missing or unreadable trace on it still stops the comparison. (RL-110 term 3, RL-113, RL-121.)

**Agreement.** Agreement is stated over `compared` rows only, with two counts beside it. `both_null` is the
number of compared rows where both sides hold no value: agreement that a quantity is absent, not agreement
on a number. `first_program_only` is the number of rows not compared. It is not a statement that every
class passed, since a class with no compared row carries no verdict. On the pinned program
(`scripts/independent_recompute_b6.py`, SHA-256 `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759`) the three full-volume
single-pack archives were each read on the Air, with production exit 0 and the comparator agreeing:

| Pack (root, generating host) | Registry keys | Compared rows, all agreeing | Null on both sides | Agreeing on a value | `first_program_only` rows |
|---|---:|---:|---:|---:|---:|
| ALPHA (MBP -1, MBP) | 122 | 699 | 198 | 501 | 118 |
| BETA (root 23, Air) | 122 | 699 | 198 | 501 | 118 |
| GAMMA (MBP -2, MBP) | 93 | 649 | 234 | 415 | 79 |

The four right-hand columns count comparison-table rows, not registry keys. On a single-pack root most
block rows are null on both sides by construction: one session gives no between-session spread, the other
two packs have no session, and no Block 5 output was supplied. The closed loop was not obtained. The cohort
`r12-r3-closed-air-25` ran nine sessions through the real chain and stopped at nine attempts with seven counting
(ALPHA 3, BETA 3, GAMMA 1): one GAMMA session was excluded by the chain for an invalid calibration capture and the
next GAMMA smoke failed, both unscripted and with no cause established; the host was under other load. The loop
held GAMMA and did not close. The cohort was not relaunched. Its seven counting sessions were read once as a block
by the pinned program (`90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759`), with pairings made final by argument: option (c)
exit 0, 2,743 compared rows, 0 failed, 0 unmatched, 58 null on both sides; serial and pool outputs byte-identical.
Not shown on chain-written archives: the loop's close, a block with more than one counting GAMMA session, and
nine-session cost. The six shapes of §17-R12 are each covered by this cohort; its cross-session GAMMA unit is
r1-gamma, paired with r2-alpha (rule 2, next counting) and r1-beta (rule 1), and it is the only chain-written one.
The cohort's calibration-excluded session, r2-gamma, was read alone and the program refused it by name
(`calibration_capture_missing`, exit 4): with authenticated inputs it does not take a missing capture from the
acceptance record. It was predicted to exit 0; the prediction was wrong. Dry-run cost on the Air: 100.4 s and
1.24 GiB peak RSS, seven sessions, reduced volume (serial), 82.4 s and 1.28 GiB peak RSS, seven sessions, reduced
volume (pool-2), against the
predeclared 2,400 s / 1,200 s and 2 GiB / 4 GiB; other R12 work running on the Air during these reads:
none.

**What the closed nine does not show.** The canonical closed nine is a reduced-volume cohort (65 s streams in
every ordinary session; RL-123 §1, option (a)). No full-volume session went through a closed loop on it.
Its serial/pool byte equality and its wall time and peak memory are reduced-volume results and are labelled
so. Full volume through the real chain was shown on single-pack roots, one session per pack, 3 of 3 packs on
the pin candidate: BETA generated on the Air, ALPHA and GAMMA on the MBP (1 of 3 and 2 of 3 by host), all
three read on the Air. Those three roots are not a closed loop and were not assembled into one. The first
real-size run of the whole program over a closed block is the blind dry run, which carries the unconditional
stop at 10,800 s of wall time. This departs from §13's "full-size … through the real stage chain" as RL-98
term 3 records; it changes no arithmetic and nothing about blinding, and it was decided after Block 5
outcomes were known. The R12 fixtures, the closed nine among them, were generated and read before S-14 was cut, as §17-R12
requires. Generating the nine took 9 h 18 min on the Air, to the generator's exit 1. That is the chain's own waits and
rotation over nine synthetic sessions; it is not analysis time, which is the dry-run cost above.

[Lead's note, 2026-11-13: the ⟨NINE⟩ slots are filled from section 6. RL-141 §5's replacement text took the place of
the paragraph's nine sentence and its serial/pool sentence, with addendum A4's sentence after "nine-session cost."
and addendum 2 B1's sentence after that, as ruled; no other word of the paragraph changed. RL-141 §5's "Shown" and
"Not shown" lists, as addendum 2 corrected them, are in the R12 report's RL-141 section at the S-14 commit (section
8). Two points for the research lead, not changed here: (1) the replacement sentence carries `both_null` but not the
`first_program_only` count that RL-133's agreement rule puts beside agreement; that count is 787 (slot N-6); (2)
addendum 2's "Not shown" item 5 (a recompute of a calibration-excluded session) is carried by the B1 sentence, not
added to the replacement's "Not shown" list.]

**The copied-record files.** The eight decision 6 (b) rows of the §17-R3 table name their record files from the list the R12 fixtures ran with (`scripts/b6_r12_verify.py:89-97`). The real run reads the list in the run-input document's `copied_records`, which the custody kit writes from the operator's `mapping.json` and refuses unless every path has a source digest. The two lists are required to be equal, family by family. The comparison is owed at the release, with the item-83 hand check, by the lead. If they differ, the run-input document governs, the table rows are reprinted with the names read, and the difference is logged as a deviation.

**A copied-record file that is listed and absent.** If a file listed in `copied_records` is absent from the
archive, the pinned program refuses by name, `disclosure_record_missing`, and writes no output: exit 4, stderr
`refused: disclosure_record_missing` (test `test_listed_disclosure_record_absent_refuses_by_name`). The custody kit
refuses the same condition earlier (`listed_file_missing`), so reaching the program's refusal means the archive
changed after it was verified. (RL-125 item 4 term 3; RL-129.)

**Unnamed refusals.** Three conditions stop the pinned program without a named refusal, and write no
output: a member's `raw/powermetrics_idle.plist` absent (exit 1, a traceback ending
`AttributeError: 'NoneType' object has no attribute 'split'`); a pinned clock journal absent (exit 4,
`refused: TypeError`); a pool worker that died (exit 1, a traceback ending `RuntimeError`). Each is read as
a refusal. The first two mean the archive changed after the custody kit verified it. Any exit other than 0
or 3 is a refusal. (RL-125 item 4, RL-133.)

## 5. Fable's notes for the lead, as amended (not for pasting)

Notes 1 and 3 stand as written; notes 2, 4 and 5 are replaced by RL-125's text.

1. **"3 of 3" is tied to the bytes.** RL-123 §2 items 3 and 5: if any file inside the program hash changes
   before the pin, the three full archives, the nine (serial and pool) and the denied fixture are re-read on
   the final bytes, and the table above is replaced, not edited.
   *[RL-129: the three full archives were re-read on the merge head and section 3a's table replaced; the nine and
   denied-26 are read once, by the merged program, in the finisher (RL-129 §1 terms 6-7).]*
2. **"All agreeing" for the three full roots: confirmed by the lead** (0 failed and 0 unmatched in every class with
   `pass`). One more count is owed from the same public comparators: `run_phase_energy.first_program_only` is 0 in
   each (RL-125 item 1). *[Discharged: 0 in each, compared 357/357/297, `pass` true; section 3a.]*
3. **The MBP registered nine** is reported in the pin request whatever it shows (RL-123 §1 item 1). It is not
   in this paragraph. If it completes and is read before the request goes out, the third part gains one
   sentence: a registered-schedule nine with full A3/B1/G1 went through one closed loop on the MBP and was
   read on the Air, with its own exit, counts and byte equality. Until then the sentence "no full-volume
   session went through a closed loop" stands as written, limited to the canonical cohort.
   *[Status at circulation: the MBP registered nine was not launched. The lead held it at 02:20 for W1 (MBP
   priority), and RL-126 item 5 does not hold the pin for it. Reported here as "not run". The sentence is not
   added.]* *[RL-129 §7: the MBP registered nine was withdrawn. If the Air nine is lost to an infrastructure cause,
   the lead relaunches the same declared command once, under a new root name, and tells the research lead.]*
4. **The term 7 check runs against the table regenerated at the merge head** `b5ab6a71d` on
   `origin/analysis/2026-11-13-b6-s14-merge` (stdout SHA-256 `1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840`; inputs `634c991c…`, `90e22603…`,
   `62dbfaef…`), not the `9f1b53767` table (RL-129 §1 term 9). It carries RL-114's three strings. PR #748 is filled
   from this table.
5. **Block rows in `first_program_only`: checked by the lead, zero** on the three full roots. The R12 report's
   sentence is corrected on the merge branch (`27eedc22c`; O-9 done).

## 6. The open ⟨NINE⟩ slots and their predeclared values

All slots but N-14 are **OUTSTANDING** (RL-141, below). Each is filled from the readers' records of `r12-r3-closed-air-25`, names and numbers
only. A slot that differs from its predeclared value goes to the research lead before the cut (RL-126 §4 (i),
item 3). Predeclarations are from the R12 report @ `d38495791`, "Both nines — role, volume and predicted outcomes
fixed before launch" and "Current pin-candidate result table and final dry-run prediction" (both written before the
nine started), RL-123 and RL-126. N-1 is RL-129 §1 term 7's.

**Amended under RL-141 §4 (2026-11-13), before the read.** The closed nine did not close: the generator parent
exited 1 on its tick bound with the loop at `NEXT` and GAMMA held. The root is retired as a loop and read once as a
seven-session block, with pairings made final by argument (RL-141 §3). N-14 is recorded **not met**; N-3, N-8,
N-9, N-11, N-13 and N-15 are relabelled for seven sessions; N-20 and N-21 are new. N-1, N-2, N-4 to N-7, N-10,
N-12 and N-16 to N-19 are unchanged. Every slot except N-14 is OUTSTANDING. The reduced finisher and the dry-run
supervisor are not used (RL-141 §3 item 1); the slots are filled from the read launcher's step receipts
(`/Volumes/JW-EXT/scratch/rl141-read-seven.zsh`). A slot that departs from these values goes to the research lead
with the names only, and the release holds until the answer (RL-141 §4).

**Filled 2026-11-13 12:40 PST (`date`), after the read.** Every slot below is filled from the two read launchers'
records, names and numbers only: events `/Volumes/JW-EXT/scratch/rl141-read-seven.events`
(`8f0ff2ddb036f5fb566096f5148802d2479c5e7f9704672d668d63078284c352`, steps 1-5, `read end exit=15 hard_stopped=0`, the designed stop
at step 5) and `rl141-read-seven-cont.events` (`72e05c9d2db51a537152ab8618d3e153bcf7031775d4eb1035bbc36e747a7d3c`, steps 6-8, `read end exit=0
hard_stopped=0`); logs `rl141-read-seven.log` (`03bbc8a58519dbfa7f521f6a7a57b5bc1587c2afa7650a9fed661f249e8c364b`) and `rl141-read-seven-cont.log`
(`1a1cfad29cde87e553b1c12b9326f67f66c04f77869ca8d6e5e8e879bdc04ad0`). Files of root 25 are in its main segment directory
(`declaration.json["main"]`); "denied" files are in root 26's. File SHA-256 values: serial receipt
`option-c-receipt.json` `bf08e58e8780fa8accdc4a190aca215ac3d4d10bbb476d8157bff522ea244825`, pool receipt `option-c-pool-receipt.json`
`370058b0c9e4ca94245150d779c4d1398382dab3a2ff49416eaa4272383ea571`, skips receipt `5af039ce08886a6dc58ccc9ff37da8459a1e6a266d7a69eda2eee38d3aa1fde5`, r2-gamma receipt
`33438ddf96964679a25ca256fc2f93c3c291ef89deb7861484856c01fc573539`, denied receipt `option-c-denied-receipt.json`
`186e188a87d15991a7d875952caf2c5766ce776dc484b8c7ce1d85301c015421`, `observations.json` `3cbfecd4de5ae5337320ebaadf2788652167764ba7965bb97bf4cf2668fd7d9d`,
root 25 `parent.json` `737e9b14582688b85bb103970039cd41f2d0790a654062a51635ac5a9bc800fe`. **No slot departs from its prediction** other than
N-14 (recorded not met before the read) and N-21 (ruled, RL-141 addendum 2 B1). Each row below keeps its predeclared
text and gains its observed value.

| # | Slot | Predeclared value | Source |
|---|---|---|---|
| N-1 | program SHA-256 of the reads | `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759`, the RC-B6-1 SHA-256 of the merge head `b5ab6a71d` (after RL-133), written here before the finisher starts (RL-129 §1 term 7; RL-133 §3 item 6) **Observed:** `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759` as `program_sha256` in all five read receipts (serial, pool, skips, r2-gamma, denied), each with `verifier_commit` `b5ab6a71d798e168209fd66a0832f66f97a0b096`. **Met.** | RL-129 §1 term 7; RL-133 §3 item 6; RL-123 §2 items 2-3 |
| N-2 | option (c) exit | `0` **Observed:** `0`, with `option_c.pass` true (serial receipt `bf08e58e…4825`; pool receipt `370058b0…a572` the same). **Met.** | R12 predeclaration ("Each named option (c) exits 0 with comparator agreement"); RL-126 §4 gate |
| N-3 | compared rows | a count above 0 over **seven** sessions, every compared row agreeing. No number was predeclared. **Observed:** 2,743 compared rows over 7 sessions, 2,743 passed (the public comparator, `joulewise.b6_s13_comparison.public.v1`, in the serial receipt `bf08e58e…4825`). **Met.** | R12 predeclaration; RL-113 term 6; RL-141 §4 |
| N-4 | failed | `0` **Observed:** `0` (serial receipt `bf08e58e…4825`). **Met.** | comparator agreement |
| N-5 | unmatched | `0` **Observed:** `0` (serial receipt `bf08e58e…4825`). **Met.** | comparator agreement |
| N-6 | `first_program_only` count | no number predeclared. Every entry a session quantity key carrying a label that allows non-comparison; **0** `run_phase_energy` entries (RL-125 item 1); **0** `__block__` entries. Checked by section 7 **Observed:** 787 (six ALPHA and BETA sessions at 118, r1-gamma at 79); 0 `run_phase_energy` entries; 0 `__block__` entries; every entry's label allowed (section 7 record). **Met.** | RL-113 term 7, RL-125 item 1 |
| N-7 | serial/pool byte equality | identical ("Serial/pool numbers and public bytes are identical within each cohort") **Observed:** identical. `cmp` found `option-c-numbers.json` = `option-c-pool-numbers.json` (both `907ce159d6970f9dbbfd07d3f3add18e0c77c562b8b40ccf365631da47196434`) and `option-c-public.json` = `option-c-pool-public.json` (both `65ed15a0363f5a9fb1dc5ba1f372e464943774eeacc6ae58365ee48c578529e3`) (events, step 3). **Met.** | R12 predeclaration; RL-126 §4 gate |
| N-8 | wall, peak RSS (serial) | ≤ 2,400 s; ≤ 2 GiB. Seven sessions, reduced volume **Observed:** wall 100.40 s (`process_measurement.wall_s` 100.395937959; `/usr/bin/time -l` 100.43 real, `option-c.time` `e82ce4e36079c871654bf74a39a099c21dc9cc4deb6e5c6d01c365ee52839886`); peak RSS 1,330,790,400 bytes (1.24 GiB). Serial receipt `bf08e58e…4825`. **Met.** | R12 final prediction; RL-141 §4 |
| N-9 | wall, peak RSS (pool-2) | ≤ 1,200 s; ≤ 4 GiB (process-group planning budget). Seven sessions, reduced volume **Observed:** wall 82.40 s (`wall_s` 82.395397583; `time -l` 82.42 real, `option-c-pool.time` `5bd9f7fab7ef9d8e1487ce2793b466980e1104b56234c986e75aff49e043faad`); peak RSS 1,378,320,384 bytes (1.28 GiB). Pool receipt `370058b0…a572`. The RSS is the largest single process (`getrusage(RUSAGE_CHILDREN)`, as `time -l`), not a process-group sum; three processes at that peak would be 3.85 GiB, inside 4 GiB. **Met.** | R12 final prediction; RL-141 §4 |
| N-10 | other R12 work on the Air during the reads | none, or named. Overlap is allowed (RL-126 item 7 dropped RL-123 §4's idle condition); the receipt names it. The supervisor receipt's `other_R12_work_allowed: false` is fixed text from before RL-126 and is not an observation (RL-129 §4) **Observed:** none. The overlap census at the start and end of both launchers is empty; the contention check (`pgrep -f 'pytest|unittest|mutmut|xdist'`) found nothing before each; both held `AIR-QUIET.lock` and removed it at exit. **Met.** | RL-126 item 7, §4 (ii); RL-129 §4 |
| N-11 | generation wall | reported: 9 h 18 min to the generator's exit 1. (Forecast before launch: about 12 native hours, R12 predeclaration; RL-126 forecast the end of generation between about 11:30 and 14:00 PST) **Observed:** 33,467.6 s = 9 h 17 min 48 s from `started_native_ns` to `ended_native_ns`, status `failed`, `exit_code` 1 (root 25 `parent.json` `737e9b14…00fe`). **As reported.** | RL-126 §1, §4 (iii); RL-141 §4 |

Cut-gate items read from the same finisher. They are not in Fable's paragraph, but RL-126 §4's gate names them:

| # | Item | Predeclared value | Source |
|---|---|---|---|
| N-12 | denied-26 fixture, read by the pin candidate | OFF rc 126 and `network_time.off_output` retained; single-session option (c) 0, agrees **Observed:** denied-26 r1-alpha read: `exit_code` 0, comparator `pass` true, `time_wrapper_exit` 0 (denied receipt `186e188a…5421`); `observations.json` (`3cbfecd4…7d9d`) `r12-denied-action`: `off_action_returncode` 126, `network_time.off_output` in its flags; `test_denied_action_ordinary_session` ok. **Met.** | R12 predeclaration; RL-49 |
| N-13 | the six shapes | A1 cap/budget skips; A2 waited runs with attempt-N telemetry; B2 `member.anchor_not_bounded`; mixed member and evaluation campaign-log rows; desk-compressed campaign logs and plists; a nonvacuous cross-session GAMMA unit. Each named option (c) exits 0 with comparator agreement, registered flags retained. **RL-141:** all seven shape assertions exit 0. `cross_session_gamma` is predicted to pass on r1-gamma alone: its ALPHA floor must come from another round, because r1-alpha is excluded **Observed:** all seven `DeclaredShapeTests` OK ("Ran 7 tests … OK", step 8 exit 0, continuation log). Each carrier has `production_exit` 0 and `comparator_agrees` true in `observations.json` (`3cbfecd4…7d9d`). `r12-gamma-cross`: r1-gamma, `cross_session_gamma` true, pairing ALPHA r2-alpha `2_next_counting` and BETA r1-beta `1_same_round`, both `provisional` false, kept units non-empty. Skips carrier r1-alpha read alone (skips receipt `5af039ce…66e5`, exit 0, agrees). **Met.** | R12 predeclaration; RL-48 item 2; §17-R12; RL-141 §4 |
| N-14 | loop close | **Not met, recorded before the read:** loop at `NEXT`, nine attempts, seven counting (3/3/1), GAMMA held on `smoke_hold:stage_failed:gamma-reference-start`, generator exit 1. (Predeclared before launch: original DONE with nine counting sessions, possibly ten ordinary attempts, from the skipped A1) | R12 predeclaration; RL-141 §1 item 1, §4 |
| N-15 | read stop | 10,800 s, by the lead's hand (RL-141 §3 item 6): if the read launcher is still running at 10,800 s it is stopped and profiled, never retried **Observed:** not reached. 199 s to the first launcher's designed stop after step 5, and 19 s for the continuation (steps 6-8); `hard_stopped=0` in both. **Met.** | RL-98 term 2, RL-123 §1; RL-141 §3 item 6, §4 |
| N-20 | sessions read by the block (new) | 7: r2-alpha, r3-alpha, r4-alpha, r1-beta, r2-beta, r3-beta and r1-gamma, selected by `prepare_run_inputs` from the attempts file; `closed` true by argument **Observed:** 7: r1-beta, r1-gamma, r2-alpha, r2-beta, r3-alpha, r3-beta, r4-alpha (serial and pool receipts' `archives`; `sessions` 7, `closed` true, `session_id` null); public `counting_by_pack` ALPHA 3, BETA 3, GAMMA 1. **Met.** | RL-141 §3 items 2-3, §4 |
| N-21 | r2-gamma single-session option (c) (new) | Predeclared (RL-141 §4): exit 0, comparator agrees, `calibration.bracket_incomplete` retained. **Observed:** exit 4, `refused: calibration_capture_missing`; no numbers or public output; comparator not reached; `time_wrapper_exit` 4, equal to `exit_code`. **Departed. Ruled a prediction error (RL-141 addendum 2 B1):** the pinned program refuses, by name, a session whose post-session capture is invalid when inputs are authenticated (RC:481). Program `90e22603…`, receipt `33438ddf…3539`. | RL-141 §3 item 4 (read 5), §4; RL-141 addendum 2 B1 |
| N-16 | term 7 check (section 7) on the nine's restricted output | no stop **Observed:** no stop (section 7 record). **Met.** | RL-126 §4 gate |
| N-18 | `time_wrapper_exit` in every term 7 receipt that carries it | `0`, with `exit_code` 0 (the orchestrator launches the read outside any seat sandbox, so `/usr/bin/time -l` works). Nonzero with `exit_code` 0 is a wrapper failure: reported with the `.time` text; it does not trigger term 7's `e17886bf…` differential read and the read is not repeated for it **Observed:** `time_wrapper_exit` 0 with `exit_code` 0 in the serial, pool, skips and denied receipts. (r2-gamma's 4 with `exit_code` 4 is N-21's and does not engage this slot, RL-141 addendum 2.) **Met.** | RL-132 §1 items 6-7 |
| N-19 | `both_null` on the nine (per class and total) | observed and reported, not predeclared; checklist steps 2 and 3's invariants (`both_null` ≤ `passed`; 0 in a class with no compared row). An `engine_below_minimum` family in the nine's output is reported, not a stop **Observed:** `both_null` inclusive 4, replication 2, side_by_side 48, summary 4, every other class 0; total 58. `both_null` ≤ `passed` in every class, and 0 in every class with no compared row. No `engine_below_minimum` family (families: calibration, counting, engine, engine_word, harvest_bound, harvest_drift, harvest_energy, pairing, section10, section11_replication, section11_short). **Reported.** | RL-133 §3 item 6 |
| N-17 | output SHA-256s: restricted, public, serial and pool | recorded (section 7 step 8): the reduced finisher's `option-c-numbers.json`, `option-c-public.json`, `option-c-pool-numbers.json`, `option-c-pool-public.json`, with its `reduced-finish-receipt.json` **Observed:** `option-c-numbers.json` `907ce159d6970f9dbbfd07d3f3add18e0c77c562b8b40ccf365631da47196434`, `option-c-public.json` `65ed15a0363f5a9fb1dc5ba1f372e464943774eeacc6ae58365ee48c578529e3`, `option-c-pool-numbers.json` `907ce159…6434`, `option-c-pool-public.json` `65ed15a0…29e3`; receipts serial `bf08e58e…4825` and pool `370058b0…a572`. There is no `reduced-finish-receipt.json`: the reduced finisher was not used (RL-141 §3 item 1). **Recorded.** | RL-113 term 7 step 8 |

## 7. The RL-113 term 7 checklist (verbatim, with the RL-125 replacements)

Source: Fable's file, section "RL-113 term 7: label check on the nine's output". Steps 1 to 3 and 7 to 9 stand. Steps
4, 5 and 6 are replaced and steps 10 and 11 added, by RL-125's text. RL-133 §2 replaces steps 2, 3 and 11, one bullet
each of steps 5 and 6, adds `both_null` to step 8, and adds steps 12 and 13. The R3 table is the one regenerated at
the merge head `b5ab6a71d`, stdout SHA-256 `1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840` (RL-129 §1 term 9, RL-133 §3 item 8).

> Term 7 is owed on the real block run and does not gate the pin. Running it on the nine is a rehearsal on
> synthetic sessions. It reads key names only.
>
> 1. Take `block.option_c.first_program_only` from the **restricted** output of the nine's serial read. Confirm
>    the pool read's list is identical.
> 2. Count the list per class. Each count must equal that class's `first_program_only` in the public
>    comparator, and the total must equal the number in the agreement sentence. For each class also take
>    `compared` and `both_null`. `both_null` must not exceed `passed`. The agreement sentence's three numbers
>    are the totals of `compared`, `both_null` and their difference.
> 3. Confirm every public class record is one of two kinds: with `pass` and `compared` > 0, or without `pass`
>    and with `compared`, `passed`, `failed`, `unmatched` and `both_null` all 0. Any other record is a stop.
> 4. Split the list by class. Set the `run_phase_energy` entries aside for step 6; they have no R3 row. Reduce the rest to distinct key names (drop the session) and look each one up in the R3 table at `b5ab6a71d` (stdout SHA-256 `1003d87e…9840`).
> 5. A key passes if its label is one of:
>    - `single-source` (RL-99 item 1);
>    - "not independently recomputed";
>    - the §17-R8 literal "single implementation; not independently recomputed" (RL-125 item 3);
>    - a gate label ("computed and compared in the option (c) gate …; not an S-13 table row");
>    - a conditional label, and the session it is listed for meets the label's second clause: for `neg8/*`, that
>      session's NEG-8 verdict is `undefined`; for the contrast fields, the verdict is `undefined` or the twin
>      returned no estimate; for `p` and `holm_p` also when that session's flags carry `cell_below_minimum` for
>      that contrast's cell (code and scope only). Check the condition per session, not per key.
> 6. **Stops, each to me:**
>    - any entry of class `run_phase_energy`, with the run's role and no value (RL-125 item 1);
>    - a key in the list labelled plain "computed and compared (decision 6 (a))";
>    - a key in the list with a block-scope label ("§10-§11 arithmetic computed and compared …"), or any entry with session `__block__`;
>    - a conditional-label key listed for a session whose screen is defined, whose twin estimated and, for `p`
>      and `holm_p`, whose contrast has five or more quads;
>    - a key in the list with no row in the R3 table, or labelled UNSTATED;
>    - a decision 6 (b) copied-family name in the list (those are never comparison-table keys);
>    - in the other direction: a `lines/whole_machine/<model>/<phase>/*` session key in a compared row (RL-125 item 3).
> 7. Cross-check the other direction once: no key that appears in a compared row for a session also appears in
>    `first_program_only` for the same session.
> 8. Record: the output's SHA-256, the program SHA-256, the R3 table's commit (`b5ab6a71d`), the per-class counts with `both_null` per class, and the
>    number of distinct keys under each label kind. No values are copied.
> 9. On the real block run steps 1 to 8 are repeated by whoever writes the agreement sentence, on the
>    restricted output, before that sentence is written.
> 10. Real block run only. Confirm the restricted output's `inputs.host` is `Air`, and that every session carries `copied_disclosures` with the eight families. Compare each family's `path` list with rows 150 to 157 of the R3 table. A difference is handled as RL-125 item 2 says. A session without `copied_disclosures` is a stop.
> 11. If the block command exits with anything other than 0 or 3, that is a refusal, including the three
>     unnamed signatures in the pin request. Stop, check the archive against the kit's verify record, and
>     tell me. Do not edit the program.
> 12. Real block run only. Confirm that the output's session ids are the run-input document's pinned
>     sessions, one for one, and that every attempt row with a counting outcome for a pack has that pack's
>     session of that round in the output. Names only. A missing session is a stop.
> 13. Real block run only. For each session, note whether its pin lists `derived/b6-flags.jsonl`,
>     `withheld/spans.json` and `derived/bracket-binding.json`. A session without one is reported to me with
>     its pack and round. It is not a stop by itself.

[Lead's note: the preface says term 7 "does not gate the pin" (RL-113 term 7, about the real block run). RL-126 §4's
gate makes "the term 7 check on [the nine's] output has no stop" a condition of the **cut**. Both hold: the rehearsal
on the nine gates the cut; the real-run check (step 9) gates the agreement sentence, not the pin.]

### 7a. Term 7 on the seven-session block read: run 2026-11-13, no stop (slot N-16)

Run on the serial block read's restricted output `option-c-numbers.json` (`907ce159d6970f9dbbfd07d3f3add18e0c77c562b8b40ccf365631da47196434`),
program `90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759`, against the R3 table regenerated at `b5ab6a71d`
(`/Volumes/JW-EXT/scratch/rl133/r3/new.out`, stdout SHA-256 `1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840`). Key names and counts only; no
value was read or copied. Steps 2 to 8 by the structure probe B-3 (`scripts/b6_structure_probe.py` on
`/Volumes/JW-EXT/jw-wt/b6-real-run` @ `5c53850f6`, file SHA-256 `185a05059e4bb7afe7fa6bc9091d5621e0a7ec18dcce6f2b71668d0bba7cc922`), whose input shape fits
this output: `python3.13 -I -B scripts/b6_structure_probe.py --restricted … --public option-c-public.json --r3-table
… --inputs option-c-inputs.json --stage gate --term7`, output `/Volumes/JW-EXT/scratch/s14-cut/b3-term7-nine.json`
(`be4fa0d0aa9f6b212fb1044101fb1e1e02336fe98e45f4049adfc1ae9de5ee50`). Stdout `term7: pass`. Its separate structure line, `probe: departs
closed,public_one_session,public_session_shape`, is the gate stage's predeclared one-session shape (runbook step 7)
and does not apply to a closed seven-session block; it is not part of term 7. B-3 skips step 1 (one run), so step 1
was run separately.

1. Step 1. The pool read's `block.option_c.first_program_only` list equals the serial one, entry for entry (787
   and 787; the two restricted files are byte-identical, section 6 N-7).
2. Step 2. Every class's listed count equals its `first_program_only` in the public comparator
   (`joulewise.b6_s13_comparison.public.v1`, serial and pool receipts; equal to the restricted output's records).
   Totals: compared 2,743, `both_null` 58, agreeing on a value 2,685, `first_program_only` 787. `both_null` ≤
   `passed` in every class.
3. Step 3. Every class record is one of the two kinds: with `pass` (calibration, contrast, inclusive, neg8,
   replication, run_phase_energy, side_by_side, summary), each with `compared` > 0; without `pass` (attribution_floor,
   contrast_word, cross_session, descriptive, dominance, floor, lines, per_token, reported), each with all five counts 0.
4. Steps 4 to 6. 0 `run_phase_energy` entries; 0 `__block__` entries; no copied-family name; every listed key has
   an R3 row. Distinct keys by label kind: `single-source` 100, "not independently recomputed" 183, the §17-R8
   literal 24, gate label 8; no plain "computed and compared" label, no block-scope label, no conditional label, no
   UNSTATED. No `lines/whole_machine/…` session key in a compared row.
5. Step 7. Per class, `compared` plus the listed session rows equals the registry's session keys for the seven
   sessions, so no key is both compared and listed for a session. Per session, `first_program_only` is 118 (the six
   ALPHA and BETA sessions) and 79 (r1-gamma), equal to the registry keys less the compared keys (122 and 93).
6. Step 8. Per class (`compared` / `both_null` / listed): attribution_floor 0/0/12, calibration 7/0/0, contrast
   10/0/14, contrast_word 0/0/6, cross_session 0/0/28, descriptive 0/0/8, dominance 0/0/37, floor 0/0/156, inclusive
   144/4/0, lines 0/0/430, neg8 21/0/0, per_token 0/0/12, replication 2/2/0, reported 0/0/84, run_phase_energy
   2,367/0/0, side_by_side 48/48/0, summary 144/4/0. R3 table commit `b5ab6a71d`.

B-3 also ran the real-run steps 10 and 12 as a by-product (host `Air`; copied disclosures with the eight families in
every session; the seven sessions equal the run-input document's pins). They passed and are not part of the
rehearsal's gate.

## 8. The cut procedure

RL-126 items 1-4 and §4's gate; RL-123 §2; freeze-by-commit F1 (`docs/process/freeze_by_commit.md`). Owner: the lead,
unless a step names someone else.

1. **Before the cut, while the nine generates.** This request is read by the research lead and Ed. Every section 9
   item marked GATING is decided; every other "before the cut" item is discharged or carried with its owner. By
   RL-126 item 3, if the request is accepted in every other respect by the time the finisher exits, no further review
   round follows, unless a slot departs from its prediction.
2. **The nine's finisher runs.** The nine's finisher is `scripts/b6_r12_reduced_finish.py`, run by
   `b6_r12_dry_supervise.py --reduced`. It takes its exit check from `scripts/b6_r12_finish.py:25` (`agree`), so a
   nonzero exit or a comparator that does not pass raises. It runs the serial and pool-2 reads, the byte comparison,
   the single-session shape reads, the denied-26 read, the seven named `DeclaredShapeTests` and `ReducedSetTests`,
   and writes `reduced-finish-receipt.json`. It is run from the merge worktree, after the generator parent has exited
   0. It must exit with option (c) 0, comparator agreement, serial/pool byte equality and the six shapes as
   predeclared (RL-126 §4 gate). Under 10,800 s, or stopped and profiled (N-15). The prepared launcher is
   `/Volumes/JW-EXT/scratch/rl129-read-nine.zsh` (hash asserts, the three RL-129 §6 records before and after, start,
   end and exit to `/Volumes/JW-EXT/scratch/rl129-read-nine.events`). The nine is not also read by `e17886bf…`; if a
   slot departs from its prediction, RL-129 §1 term 7's procedure applies.
3. **Fill the slots** N-1 to N-17 from the finisher's records (names and numbers only). Any slot that departs from its
   prediction goes to the research lead before the cut. The MBP registered nine was withdrawn (RL-129 §7). If the Air
   nine is lost to an infrastructure cause, the lead relaunches the same declared command once, under a new root
   name, and tells the research lead.
4. **Re-hash the closure.** At the commit to be cut, recompute every SHA-256 in section 2a and 2b, and record RL-129
   §6's three records for the finisher's reads: the receipts' `verifier_commit` is the S-14 commit or a commit whose 24
   files hash the same; the reader worktree was clean before the first read and after the last; the 24 SHA-256 values
   recomputed from the reader worktree at both times equal section 2. If any byte differs, nothing is cut: RL-123 §2
   item 3's re-reads run on the final bytes (three full archives, the nine serial and pool, the denied fixture), the
   section 3a table is replaced, not edited, and RL-125 item 4 term 3's fix goes in with the change.
5. **Run the term 7 check** (section 7, steps 1 to 8) on the nine's serial restricted output against the R3 table
   regenerated at the merge head `b5ab6a71d` (stdout `1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840`; RL-129 §1 term 9, RL-133 §3 item 8). Any stop goes to the research lead;
   no cut.
6. **Regenerate the R3 table at the commit to be cut.** It is not byte-equal to the table at `9f1b53767`,
   because it prints RC-B6-1's SHA-256 and cites RC-B6-1 line numbers, and both moved with the merge. Remove
   the RC-B6-1 SHA-256 line and every `RC:` line number from the new output and from the `7b7920cf…` output;
   the remainders must be byte-identical, with 675 of 675 keys, 149 groups and 0 UNSTATED. Record the new
   stdout SHA-256. Any other difference means a label or key moved: stop, and tell the research lead.
   *[Done at the merge head `b5ab6a71d`, under RL-133 §3 item 8's rule: stdout `1003d87e7b92bc28a38890d75860e0ea0e47ae65862e6d6dd09641d7b3f29840`, remainders byte-identical (section 2c). Repeated at the
   cut commit; it must give the same stdout while the generator inputs are unchanged.]*
7. **Cut S-14.** The S-14 commit is the merge branch's head after the evidence is committed; it already holds the R3
   generator, so §17-R3's table is generated from the pinned commit. It holds the section 2 bytes unchanged.
   Record its full SHA and tree. Create the annotated tag `b6/analysis` on it; the message names the commit, the tree,
   RC-B6-1's and the Block 5 script's SHA-256, and this request. The SHA is the authority and the tag a convenience
   (F1). Push the tag.
8. **Record the pin.** In `docs/registrations/block6_freeze_by_commit_addendum.md` §1 "Proposed tags", fill the
   `b6/analysis` row (commit, tree, status). In PR #748, fill `OPEN[S-14-PIN]` (commit, tag, the four SHA-256 values
   of rows 1, 2, 19 and 20), `OPEN[R12-FULLSIZE-N]` = 3 ("3 of 3 packs, on single-pack roots, per host"), and
   `OPEN[R3-TABLE]` (the table at the cut commit, checked against `9f1b53767`'s as step 6 says, citing the
   regenerated table's commit and SHA-256). Apply #748's
   deferred LOW 5 (dates) and LOW 6 (the S-14 source cell, `OPEN[S-14]` at REG:908 and REG:1192). Fable checks the
   fill delta before #748 merges.
9. **After the cut.** The blind dry run runs from the S-14 commit with the RL-98 term 2 stop. No Block 6 custody path
   is read by the program before step 7 (RL-126 item 4).

## 9. Owed items, with owners

Every item on the lead's owed list (`/Volumes/JW-EXT/scratch/s14-pin-request-notes.md`) that bears on the pin request
is below, discharged or open. W1, R1 and BYTES items on that list do not bear on S-14 and are not repeated.

### 9a. Formerly GATING: ruled (RL-129 §1 and §2)

G-1: **ruled, RL-129 §1** (merge now; done on `origin/analysis/2026-11-13-b6-s14-merge` @ `b5ab6a71d`, section 0).
G-2: **ruled, RL-129 §2** (the Opus cold review runs now, Block-5-naive, on `d38495791` and the existing evidence, an
executing pass, adding the merge delta; the research lead checks the closure delta in one turn; these two are §13's
blind executing passes; O-15, O-16). The rows below are kept as the request first circulated.

| # | Item | Why it gated | Owner |
|---|---|---|---|
| G-1 | **Seat 7's round-2 and round-3 fixes are not in the pin candidate.** RL-48: "F2 to F5 before the pin, as the review says; F6 to F8 in the same commit", and "the S-14 pin comes to me with the F2 witness". They were made and reviewed on `origin/analysis/2026-11-11-b6-path` @ `7c8251b28` (`fa0373cc9` F2-F8, Opus ADMIT-WITH-FIXES `920fc77c3`; `9fdec5aed` R2-F1 to R2-F3, Fable ADMIT `7c8251b28`). The R12 line branched from seat 7's round 1 (`da0a03145`, the merge base) and never took them: `7c8251b28` is not an ancestor of `d38495791`. At the pin candidate `clock_journal_required` (F8) and the `supplied_archive` root handling (F3) are absent from `joulewise/b6_analysis_inputs.py`, and `tests/independent_recompute/test_b6_production.py` has neither the F5 test (`test_c3_gamma_window_midpoint_loss_has_no_pack_scoped_primary_reason`) nor the F8 test (`test_listed_clock_journal_requires_pin_and_is_authenticated`). The F7 refusal in `MemberPool` is already present at RC:180-181. The 7b witness at the pin candidate is the pre-F2 one, so RL-48's condition for 7b ("shown when the strengthened witness of F2 passes, with decode and prefill given different synthetic values") is not met there. | Taking the fixes changes rows 1 and 5. That triggers RL-123 §2 item 3 (re-read the three full archives, the nine serial and pool, the denied fixture; minutes of reader time) and RL-125 item 4 term 3 (`disclosure_record_missing` goes in with it). Not taking them leaves RL-48's "before the pin" unmet and forces 7b-ii (§10 prints "block 5: not computed" for the per-phase line) unless the research lead rules otherwise. | Research lead (ruling: merge, or rule they are superseded); then the R12 seat (merge `7c8251b28` onto the R12 line, resolve against RL-113-115/121, run seat 7's tests and the 7b tests by id); the lead (re-reads, section 3a table, slots N-1/N-12) |
| G-2 | **The Opus cold review of R12's final implementation and evidence.** RL-48 item 7: "An Opus cold review follows, also Block-5-naive. Then the S-14 pin comes to me". The R12 report's final handoff lists it as "still incomplete". §13 also asks for "one blind executing cold pass by Fable and one by Opus" of the analysis programs. RL-126 item 3 says the cut follows the finisher "with no further review round". | The Opus review can cover the code and the existing evidence now, but not the nine's evidence before the cut, if RL-126 item 3 is read literally. See section 10, conflict C-1. | Research lead (which reviews discharge §13's two blind executing passes, and whether the nine's evidence needs Opus before the cut); the lead (launch the Opus seat now, Block-5-naive, on `d38495791`, or on the merged head if G-1 merges) |

### 9b. Owed before the cut (not gating a decision)

| # | Item | Owner |
|---|---|---|
| G-3 | Confirm the readers ran on the section 2a closure, by RL-129 §6's three records (`verifier_commit`, clean reader worktree before and after, the 24 SHA-256 values before and after; section 2e; section 8 step 4). | Lead |
| O-1 | Fill slots N-1 to N-17 (section 6). | Lead |
| O-2 | The term 7 check on the nine's output, no stop (section 7; RL-126 §4 gate). | Lead |
| O-3 | `classes.run_phase_energy.first_program_only` is 0 in the nine's public comparator (RL-125 item 1). Covered by section 7 step 6. | Lead |
| O-7 | PR #748 fill (section 8 step 8): `OPEN[S-14-PIN]`, `OPEN[R12-FULLSIZE-N]` = 3 (owed-list item 5, RL-98 term 3), `OPEN[R3-TABLE]`, LOW 5 and LOW 6, then Fable checks the fill delta. `OPEN[R7-SESSION-INDEX]` stays open; it is not an S-14 field. | #748 builder seat, then Fable |
| O-8 | `b6/analysis` tag and the freeze-addendum row (section 8 steps 7-8). | Lead |
| O-9 | Correct the R12 report's "include block rows" sentence (section 3a). **Done** on the merge branch (`27eedc22c`); not in the generator's checkout. | Lead (builder seat) |
| O-15 | The Opus cold review (RL-129 §2 item 1): done, `/Volumes/JW-EXT/scratch/opus-cold-review-r12.md`; its findings are ruled in RL-133. Opus re-checks the RL-133 delta `91359b2b2..b5ab6a71d` in one turn, delta only: runs the new tests and the sibling-Holm mutant (RL-133 §4 item 3). **Closed:** `/Volumes/JW-EXT/scratch/opus-rl133-delta.md`, CLOSED-WITH-NOTES (07:59 PST). | Lead (Opus seat) |
| O-16 | The research lead's delta check, one turn, `91359b2b2..b5ab6a71d`: the two program files, the tests and the label strings, the two test modules run and Opus's two probes re-run (RL-133 §4 item 2; with RL-129 §2 item 2's closure delta from `d38495791`). The re-reads start when O-15 and O-16 have both closed (RL-133 §4 item 4). **Closed:** `/Volumes/JW-EXT/scratch/fable-rl133-delta.md`, CLOSED-WITH-NOTES (07:49 PST); the re-reads then ran (section 3a). | Research lead |
| O-17 | The nine and denied-26 read once by the merged program, from the merge worktree, after the generator parent exits 0 (RL-129 §1 term 7). Launcher `/Volumes/JW-EXT/scratch/rl129-read-nine.zsh`. | Lead |

### 9c. Owed at or after the release (do not gate the pin)

| # | Item | Owner |
|---|---|---|
| O-4 | RL-104 check 3, the item-83 hand check of each copied-record file (RL-100 "Still owed"), with the reader's name. | Lead, at the release, restricted side |
| O-5 | RL-125 item 2: compare `mapping.json`'s `copied_records` with the verify map on file names, family by family; on a difference, reprint rows 150 to 157 and log one deviation line. | Lead, at the release (with O-4) |
| O-6 | RL-125 item 4 term 2 for the real run: whatever launches the real `block` command reads any exit other than 0 or 3 as a refusal. Shown for the R12 launchers only (section 3b). | Lead, before the blind dry run |
| O-10 | RL-125 item 4 term 3: `disclosure_record_missing` with one test. **Done in the merge** (`27eedc22c`; section 4). | Builder seat |
| O-11 | RL-113 term 7 on the real block run (section 7 step 9, and steps 10-11). | Whoever writes the agreement sentence |
| O-12 | RL-99 / §17-DLE2 gate on the first counting Block 6 session: exit 0, every family agreeing, 0 unmapped, on that session alone, before the closed run. | Lead, at the blind dry run |
| O-13 | Custody `inputs` with `mapping.json`, complete `relocations` (RL-100). | Lead, after the pin |
| O-14 | `mapping.json` names `clock_journal` for every session whose `SHA256SUMS` lists a `…/monitor/clock.jsonl`. Without it the pinned program refuses `clock_journal_required` (`joulewise/b6_analysis_inputs.py:56-58` at the merge head). The remedy is `mapping.json`; no pinned byte changes. The kit treats the key as optional (`scripts/b6_custody_kit.py:468-469` at `ae7eb01b3`) and may refuse it earlier, as ordinary engineering. | Lead, with O-13 |

### 9d. Discharged in this request

| Owed-list item | Where discharged |
|---|---|
| 1. RL-101 condition (R, R_cm compared on Block 5; 12 rows, AGREE; pinned B5 bytes) | Section 3d; R3 report @ `9f1b53767` |
| 2. RL-104 check 2 (a source digest per copied file) | Section 3e; R3 report @ `9f1b53767` |
| 3. neg8/contrast label ruling applied to the generator | RL-114's three strings at `9f1b53767`, Fable ADMIT (RL-125 preamble) |
| 4. Regenerate the R3 table on R12's final head | Done at `9f1b53767` (merge of `d38495791`); regenerated at the merge head `b5ab6a71d` under RL-129 §1 term 9 and RL-133 §3 item 8 (section 2c); repeated at the cut (section 8 step 6) |
| 5. RL-98 term 3, N of 3 | 3 of 3 on the pin candidate (section 3a; Fable's paragraph). The #748 fill is O-7 |
| 6. RL-110 item 8 / term 3 (a key the first program prints and the second side lacks) | RL-113 paragraph (section 4, first part); code at RC:1311-1345 |
| RL-110 term 5 (GAMMA neg8 halving) | RL-114 fix in `check_block` `c9d0c893…` |
| Loop state pinned but omitted | RL-115 fix in RC-B6-1 (`external_input_missing`, RC:1721) |
| RL-113 term 5 paragraph; RL-121 sentence; RL-113 term 6 agreement sentence | Section 4 |
| RL-113 term 7 post-run check | Section 7 (rehearsal on the nine, a cut gate; real run O-11) |
| RL-125 item 1 count on the three roots | Section 3a |
| RL-125 items 2 and 4: the two sentences | Section 4 |
| RL-125 item 4 term 2 for R12 launchers | Section 3b |
| Fable flags 1, 3 and 5 (block rows; all-agreeing; MBP nine sentence) | Sections 3a and 5 |
| RL-48 F10 / RL-99: which label | Section 3f |
| Open question (00:05): does full volume repeat on the merged program | RL-123 §2, re-read only; done, 3 of 3 on `e17886bf…`, and re-read on `90e22603…` (section 3a) |
| RL-48 F2-F8 before the pin (G-1) | Merged, RL-129 §1 (section 0) |
| RL-125 item 4 term 3, `disclosure_record_missing` (O-10) | In the merge (section 4) |
| Review findings 7-10 (RL-129) | N-10 literal (section 6); finisher names fixed, read once (section 3b); "Main" cells (section 2a); comparer outside the repository (section 3a) |
| MBP registered nine "reported whatever it shows" (RL-123 §1 item 1) | Section 5 note 3: not run |

## 10. Rulings cited, and conflicts found

Rulings file `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` @ `258612016` (line numbers at that
commit): RL-48 :2102, RL-49 :2183, RL-95 :5612, RL-96 :5640, RL-98 :5688, RL-99 :5737, RL-100 :5762, RL-101 :5817,
RL-102 :5848, RL-103 :5881, RL-104 :5903, RL-110 :6196, RL-113 :6354, RL-114 :6412, RL-115 :6482, RL-121 :6827,
RL-123 :7163, RL-125 :7340, RL-126 :7433; at `690d25d67`, RL-128 :7613 and RL-129 :7655; at `68f792208`, RL-132 :8003. There is no RL-97 in the file. RL-95 (BYTES twin) and RL-96 (powermetrics
wrapper) do not bear on S-14. The committed RL-126 points to the scratch file for its §4 replacement texts; this
request quotes them from `/Volumes/JW-EXT/scratch/fable-rl126-proportionality.md` §4.

**C-1. RL-48 item 7 against RL-126 item 3.** RL-48 puts the Opus cold review before the pin request reaches the
research lead. RL-126 sends the request now and lets the cut follow the finisher "with no further review round".
The R12 report counts that review as still owed, over "the final implementation/evidence". Read together, Opus can
review the code and the existing evidence while the nine generates, but nothing reviews the nine's evidence before
the cut except the slot comparison. One ruling settles it (G-2). **Ruled: RL-129 §2.**

**C-2. RL-48 "F2 to F5 before the pin" against RL-126 "the nine now running at `e17886bf…` stands" (RL-125 item 4,
gate) and the request's "3 of 3 on the pin candidate".** Seat 7's fixes (G-1) change RC-B6-1. RL-123 §2 item 3
already says what follows, re-reads on the final bytes and no regeneration, so this is a gap the rulings already
handle, not a contradiction. But no ruling mentions seat 7's rounds 2 and 3 after RL-98 read them, and both the R12
report and the paragraph treat `e17886bf…` as final. **Ruled: RL-129 §1** (merge; the nine stands and is read once
by the merged program).

**C-3. Stale open-items row.** RLD's open-items table still lists "The S-14 pin request for Block 6, under RL-98
(volume, deadline 13 November 20:00 PST)". RL-123 §1 says RL-98 term 2's date "has no further force". Clerical only.
**Ruled: RL-129 §3** (the row is struck and replaced in the rulings file).

**C-4. RL-123 §4 against RL-126 item 7 and the R12 predeclaration.** RL-123 §4 kept "the closed nine's serial and
pool readers … run with no other R12 generator or reader on the Air"; the R12 predeclaration repeats it. RL-126 item 7
drops it. RL-126 is later and says so, so the predeclaration's sentence is superseded and slot N-10 records any
overlap. **Ruled: RL-129 §4** (confirmed; N-10 says the receipt field is a literal).

**C-5. "Program hash" scope.** RL-123 §2 item 3 and Fable's note 1 speak of "any file inside the program hash". The
recorded `program_sha256` covers RC-B6-1 only (RC:1447), and `b5_program_sha256` covers the Block 5 script. This
request reads "inside the program hash" as the whole executed closure of section 2a plus the tables of 2b, so that a
change to `check_block`, the twins or the inputs layer also triggers the re-reads. If the research lead means only
RC-B6-1, G-3 and section 8 step 4 narrow accordingly. **Ruled: RL-129 §5, confirmed** (the 24 files of 2a and 2b).

---

Assembled from: the lead's owed list; `RESEARCH-LEAD-DECISIONS.md` @ `258612016`; Fable's pin paragraph (05:50) with
the RL-125 (06:05) and RL-126 §4 (06:10) replacements; the R3 table report @ `9f1b53767`; the R12 report @
`d38495791`; PR #748 @ `27b6cacfd`; seat 7's reports @ `7c8251b28`; the lead-verified reader facts. Hashes computed on
the Air with `taskpolicy -b`, TMPDIR on JW-EXT, from `git show` and `git archive`; no running job, worktree or custody
path was touched. Revised under RL-129, RL-132 and RL-133 from the merge branch @ `b5ab6a71d`, the term 4 test logs, the term 6 re-reads
and comparison records in `/Volumes/JW-EXT/scratch/rl129-diff/`, and the term 9 check; the generator checkout, the
running generator and the custody directory were not touched.
