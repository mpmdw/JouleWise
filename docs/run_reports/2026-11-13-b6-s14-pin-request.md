# Block 6 S-14 pin request (circulating with the closed nine's slots open)

Date: 2026-11-13 06:20 PST (`date`). Assembled by the lead (orchestrator, Claude Opus 5.5) for the research lead
(Fable 5.2) and Ed. Branch `docs/2026-11-13-b6-s14-pin-request`, off `origin/main` @ `0101ee536`.

**Status: REQUEST, NOT A PIN.** Under RL-126 item 2 this request circulates now, with the R12 closed nine's numbers
left as open ⟨NINE: …⟩ slots. S-14 is cut only after the nine's finisher has run, every slot is filled, and the
RL-113 term 7 check has been run on the nine's output (section 7). Two items in section 9 are marked **GATING** and
need a decision before the cut.

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

## Contents

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
| Pin candidate (the code the three full reads and the closed nine run) | `origin/analysis/2026-11-11-b6-r12` | `d3849579184551c6c3431abd2c6bb65f7a0bd876` |
| R3 table (generator merged onto the pin candidate; no pinned file touched) | `origin/analysis/2026-11-12-b6-r3-table` | `9f1b537679f17c69535d46f5a3e44af0c686a536` |
| Rulings file cited | `origin/audit/2026-11-10-fable` | `258612016feedb0587a09cfbe58724471b6b77e2` |
| §17 entries (S-14 "pin OPEN") | PR #748 head | `27b6cacfd420db4bddc2dd0b5c7afa53a107718d` |

The S-14 commit itself is not yet chosen. It is the analysis-line commit at the cut (section 8), and it must hold
every byte in section 2 unchanged.

## 2. The exact bytes to pin

SHA-256 of the file bytes, computed 2026-11-13 from `git show <commit>:<path>` at `d38495791` and again at
`9f1b53767`; every row below is identical at both commits. "Main" says whether `origin/main` @ `0101ee536` has the
same bytes (the R12 line is not merged to `main`).

### 2a. The program: RC-B6-1 and every repository file it executes

The closure was taken by importing RC-B6-1 from a `git archive` of `d38495791` under `python3.13 -I`, plus its two
deferred imports (`joulewise.b6_analysis_hazards`, RC:293; `joulewise.b6_analysis_check`, RC:1307), and listing every
loaded module under the tree. `scripts/independent_recompute_b5.py` is not imported; RC-B6-1 hashes and `exec`s it
(RC:48-65).

| # | Path | SHA-256 | Role | Self-checked by the program | Main |
|---|---|---|---|---|---|
| 1 | `scripts/independent_recompute_b6.py` | `e17886bfefd066f1962357cede777568bf033898351d29365e2d0cdd22d423e3` | RC-B6-1, the printing program and the S-13 gate | recorded as `program_sha256` (RC:1447) | differs |
| 2 | `scripts/independent_recompute_b5.py` | `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0` | Block 5 recompute at its release digest | yes, `B5_SHA256` (RC:50), refuses `b5_script_digest_mismatch`; recorded as `b5_program_sha256` | same |
| 3 | `joulewise/b6_analysis_check.py` | `c9d0c893c97eafc28ea3de689671a0e3f0f34f83fb766d28e0165c3bb9f87f5d` | `check_block`, option (c)'s second side (RL-113, RL-114 fixes in) | no | differs |
| 4 | `joulewise/b6_analysis_hazards.py` | `9a907a3671dbe210df4d417428c9108f0fdee1c16531bd0bef2fd39b0f27bb2b` | the E_add code and the P* desk exclusion (§17-R10) | no | differs |
| 5 | `joulewise/b6_analysis_inputs.py` | `f46367d5ffe666c40d479b24340e32fe5dd32dcd7f0fb8818cbb9a8da0022ca9` | `AuthenticatedInputs` (§17-R11) | no | differs |
| 6 | `joulewise/twins/__init__.py` | `e717dc7f4b7c3b6006f06763873a70c79d95d9ad7cb3183c21eb5251daffaeb0` | twins package | no | same |
| 7 | `joulewise/twins/engine_twin.py` | `5cd6977d79b2951a6e4351a9e8f95b4f91bc38af50eeb4c5bf2d5115ffedbff8` | engine twin | no | same |
| 8 | `joulewise/twins/harvest_twin.py` | `df39036b24eab0d015c198686e3ed03ae0add341e487636d34ed622fa0695af0` | harvest twin | no | same |
| 9 | `joulewise/flags/__init__.py` | `2ea17e7b30b4101d2149be0a216c82e223b903121f50bda8f0d5665b33378ba2` | flags package | no | same |
| 10 | `joulewise/flags/catalog.py` | `006840601a37009d685db458186492963b15fa7cb9be05a3ae066b9e9ae82ef0` | `load_catalog` (§17-R6) | no | same |
| 11 | `joulewise/flags/exclusions.py` | `ebe1678c0fdd60b1ddd20d432cf07412bd321a8629589f4ce4c6b334378f0ad6` | sealed `compute` (§17-R6, C3) | no | differs |
| 12 | `joulewise/flags/schema.py` | `cd7ce3c00dec53068db4e5c6a41115e264399dbbcc741b96dc8133b67fa1fad8` | flag schema | no | same |
| 13 | `joulewise/desk_compress.py` | `ac770c9407dad936cc742957b6f5673a1b69523156aa2be9baf7de8eb2b56777` | the one read path, `read_bytes` (§17-R11, 9a) | no | differs |
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
| 19 | `configs/b6/recompute/precision.json` | `e242cab6bb311a9c23d5c6dc06374ed3094a351e36d6954c3589e2b535cc63b0` | S-13 precision table (§17-R2) | RC:1466-1468, at import | absent |
| 20 | `configs/b6/recompute/production_comparison_keys.json` | `62dbfaef9ebc5cfbbe5a00734f5eb8ad3d82389f54f28473ed63db6135b9174d` | comparison-key registry (§17-R2) | RC:1636-1640 | absent |
| 21 | `configs/b6/recompute/hazard_sizing.json` | `bf399bec4195b9237f53c747c6fc9cd24066610eba933a0fad767534d970d29b` | P* / E_add sizing (§17-R10) | RC:294-295, with `--inputs` | absent |
| 22 | `configs/b6/flag_catalog_b6.json` | `b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b` | **S-3**, vendored; equals the S-3 row and `f31aca19f` | RC:315-317 | absent |
| 23 | `configs/b6/registration/acceptance.json` | `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8` | **S-4**, vendored; equals the S-4 row and `f31aca19f` | RC:1726, with `--inputs` | absent |
| 24 | `configs/b6/registration/identity_pins.json` | `513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d` | **S-18**, vendored; equals the S-18 row and `f31aca19f` | RC:1727, with `--inputs` | absent |

### 2c. The R3 printed-quantity table (cited by commit, not part of the program)

§17-R3 (PR #748): "At the pin it is generated by script from the pinned commit, with no UNSTATED row, and this line
cites it by commit."

| Item | Value |
|---|---|
| Commit | `9f1b537679f17c69535d46f5a3e44af0c686a536` (`origin/analysis/2026-11-12-b6-r3-table`); Fable delta review ADMIT (RL-125 preamble) |
| Generator | `scripts/b6_r3_table.py` `30c31dc92c0342683edd7addd8084028af5a90b0aa553930e545660b3199f712` |
| Its test | `tests/test_b6_r3_table.py` `8c9fd27511087eeda427923a39da7b87957277a947e52c467bee843c7e0b3565` |
| Stdout SHA-256 | `7b7920cf7315d0a435d1eaae2f5bf35e45e8158d4335c83f64aad2828260254c`, re-run 2026-11-13 about 06:15 PST from a `git archive` of `9f1b53767` (`python3.13 -I -B scripts/b6_r3_table.py`, exit 0, "Keys covered: 675 of 675; 149 groups; UNSTATED groups: 0") |
| Inputs it prints | rows 1, 3, 19, 20 above, and `scripts/b6_r12_verify.py` `947d1c3d43eccf6ab6f19fb5bed785c2443b69899faa7a5c8efd356f834295c2` (the R12 verify map, the source of the copied-record file names; a fixture tool, not pinned) |
| Report | `docs/run_reports/2026-11-12-b6-r3-table.md` at `9f1b53767`, with the RL-101 and RL-104 sections |

### 2d. Not in the pin set

- `scripts/b6_custody_kit.py`: RL-100 item 4, "The kit is not part of the S-14 pin set: the recompute binds its
  output through `--inputs-sha256`."
- The R12 fixture tools (`scripts/b6_r12_*.py`) and their tests: synthetic harness, not analysis code.
- `scripts/compare_b5_recompute.py` (`d12a1652…`): Block 5's comparator, cited for the RL-101 record only.

### 2e. What the recorded hashes bind, and what they do not

The program's own output records `program_sha256` (row 1 only, RC:1447) and `b5_program_sha256` (row 2). It does not
record rows 3 to 18. So "read by program `e17886bf…`" binds RC-B6-1 and the Block 5 script, not `check_block`, the
twins, the inputs layer or the hazard code. The binding for those is the commit: the pin names the commit and every
hash in 2a and 2b. Section 8 step 4 and section 9 item G-3 cover the check that the readers ran on that closure.

## 3. Evidence on the pin candidate

### 3a. The three full-volume single-pack roots (RL-98, RL-123 §2)

Read on the Air by program `e17886bf…` (R12 report `docs/run_reports/2026-11-11-p1-b6-r12-r3.md` @ `d38495791`,
"Current pin-candidate result table"):

| Full root | Generating host | Program SHA-256 | Keys | Compared rows, agree | `first_program_only` | Air reader wall s | Air per-process RSS bytes |
|---|---|---|---:|---:|---:|---:|---:|
| ALPHA MBP -1 | MBP | `e17886bf…22d423e3` | 122 | 699 | 118 | 165.098371416 | 1,314,619,392 |
| BETA 23 | Air | `e17886bf…22d423e3` | 122 | 699 | 118 | 164.283753667 | 1,275,412,480 |
| GAMMA MBP -2 | MBP | `e17886bf…22d423e3` | 93 | 649 | 79 | 143.271753333 | 1,277,083,648 |

Each: reader parent exit 0, production exit 0, comparator agrees, its predeclared volume and reader tests passed.
Root 23's re-read was compared with its pre-merge receipt: `unattributed=[]` (RL-123 §2 item 4). Walls are under
overlap with denied-26 and are labelled so.

**Lead-verified facts** (from the reader outputs of the three roots, program `e17886bf…`; names and counts only):

- `first_program_only` holds **0** entries with session `__block__`, in all three roots.
- Every class record with `pass` has `failed` 0 and `unmatched` 0.
- Every class record without `pass` has `compared`, `passed`, `failed` and `unmatched` all 0.
- `run_phase_energy`: `first_program_only` 0 in each root, with `compared` 357, 357 and 297, and `pass` true
  (RL-125 item 1's owed count, discharged for the three roots).
- Compared totals 699, 699 and 649; `first_program_only` 118, 118 and 79; registry keys 122, 122 and 93.

Reconciliation (my arithmetic from these numbers and RL-125 item 1): ALPHA/BETA 357 run-phase-energy + 4 session
quantity + 338 block rows = 699; GAMMA 297 + 14 + 338 = 649. 122 − 4 = 118 and 93 − 14 = 79, so every
`first_program_only` row is a session quantity key.

**Correction to the R12 report.** Its pin-candidate section says the first-program-only counts "include block rows as
well as session quantities". That is wrong: there are 0 `__block__` entries on all three full roots. The R12 seat
corrects the sentence at its next resume (section 9, O-9). The table is unchanged.

### 3b. Launchers and exit codes (RL-125 item 4 term 2)

Every R12 launcher treats a nonzero exit as failure: `scripts/b6_r12_finish.py:25` at `d38495791`
(`if receipt["exit_code"] != 0 or not receipt…["pass"]: raise RuntimeError(...)`; file SHA-256 `a21f3ec1…9c45`).
So exit 1 from the missing-copied-file defect (section 4) cannot be read as success or as "comparison disagrees" by
R12 tooling. The real-run launcher is section 9, O-6.

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
`completed` (RC:1707-1708). This answers RL-48 F10's "The pin request tells me which."

### 3g. Decision 7b (RL-30; §17-R8)

The two acceptance tests exist on the pin candidate and pass, run 2026-11-13 from a `git archive` of `d38495791`
(`JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest`, 2 tests, 43.6 s, OK):

- `tests.independent_recompute.test_b6_production.Production.test_loaded_b5_is_exactly_the_release_pin_and_tamper_refuses ... ok`
- `tests.independent_recompute.test_b6_production.Production.test_7b_b6_phase_output_equals_b5_own_output_including_corners ... ok`

But RL-48 says 7b "is shown when the strengthened witness of F2 passes, with decode and prefill given different
synthetic values". The strengthened witness is **not** on the pin candidate. See section 9, G-1.

### 3h. Other R12 obligations already shown (RL-126 §2)

- Denied action (RL-49): `denied-air-26`, generation parent exit 0 (lead, 02:46). Its read by the pin candidate runs
  in the nine's finisher (`--denied-root` 26) and is slot N-12.
- RL-48 item 6, generation bound to real time: root 23, 0.240 native/primary.
- RL-98 term 1, the production-size reader test: passed (R12 report, final section).
- Focused R12 module at the handoff: `tests.test_b6_r12_session_fixture`, 86 tests, 72 passed, 14 integration skips,
  exit 0 (R12 report, "Final notice-8 handoff").

---

## 4. Fable's paragraph (verbatim, with the RL-125 and RL-126 replacements)

Source: `/Volumes/JW-EXT/scratch/fable-s14-pin-paragraph.md` (Fable 5.2, 2026-11-13 05:50 PST), with the replacement
texts of `/Volumes/JW-EXT/scratch/fable-rev-r3-table-delta.md` ("Changes to the pin paragraph and the term-7
checklist", RL-125) and `/Volumes/JW-EXT/scratch/fable-rl126-proportionality.md` §4 (RL-126) applied. Nothing else is
changed. The one ⟨LEAD: …⟩ choice is made as the bracketed note after the paragraph says.

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
most first-program keys have one producer by registered design. Run phase energies are the exception. Every run in the registered run set (each run of a kept unit, the surviving drift-screen references and the clean corpus) is compared at 1 mJ under §17-R2, with no condition, so a run-phase-energy row in `first_program_only` is not an expected state. It is reported like any other, and it stops the agreement sentence until the research lead has ruled on it. On the three full-volume roots every `first_program_only` row is a session quantity key: none is a run phase energy and none is a block row. A class record without `pass` holds only
first-program keys and was not compared. A key that only the second side holds is compared against nothing
and fails the gate. An excluded screen run is read but is not a compared run: its energies are not compared,
and its trace flags do not stop the comparison. A screen run that is not excluded stays a compared run,
and a missing or unreadable trace on it still stops the comparison. (RL-110 term 3, RL-113, RL-121.)

**Agreement.** Agreement is stated over `compared` rows only, with the `first_program_only` count beside it.
It is not a statement that every class passed, since a class with no compared row carries no verdict. On the
pin candidate (`scripts/independent_recompute_b6.py`, SHA-256
`e17886bfefd066f1962357cede777568bf033898351d29365e2d0cdd22d423e3`) the three full-volume single-pack
archives were each read on the Air, with production exit 0 and the comparator agreeing:

| Pack (root, generating host) | Registry keys | Compared rows, all agreeing | `first_program_only` rows |
|---|---:|---:|---:|
| ALPHA (MBP -1, MBP) | 122 | 699 | 118 |
| BETA (root 23, Air) | 122 | 699 | 118 |
| GAMMA (MBP -2, MBP) | 93 | 649 | 79 |

The two right-hand columns count comparison-table rows, not registry keys, and neither is subtracted from
the key column. On the closed nine
(`r12-r3-closed-air-25`, program ⟨NINE: program SHA-256 of the reads⟩): option (c) ⟨NINE: option (c) exit⟩,
⟨NINE: compared rows⟩ compared rows with ⟨NINE: failed⟩ failed and ⟨NINE: unmatched⟩ unmatched, and
⟨NINE: first_program_only count⟩ `first_program_only` rows. Serial and pool outputs:
⟨NINE: serial/pool byte equality⟩. Dry-run cost on the Air: ⟨NINE: wall, peak RSS⟩ (serial), ⟨NINE: wall, peak RSS⟩ (pool-2), against the
predeclared 2,400 s / 1,200 s and 2 GiB / 4 GiB; other R12 work running on the Air during these reads:
⟨NINE: none, or named⟩.

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
requires. Generating the nine took ⟨NINE: generation wall⟩ on the Air. That is the chain's own waits and
rotation over nine synthetic sessions; it is not analysis time, which is the dry-run cost above.

**The copied-record files.** The eight decision 6 (b) rows of the §17-R3 table name their record files from the list the R12 fixtures ran with (`scripts/b6_r12_verify.py:89-97`). The real run reads the list in the run-input document's `copied_records`, which the custody kit writes from the operator's `mapping.json` and refuses unless every path has a source digest. The two lists are required to be equal, family by family. The comparison is owed at the release, with the item-83 hand check, by the lead. If they differ, the run-input document governs, the table rows are reprinted with the names read, and the difference is logged as a deviation.

**Known defect, not fixed before the pin.** If a file listed in `copied_records` is absent from the archive, the pinned program does not print a named refusal. It exits 1 with a Python traceback ending `AttributeError: 'NoneType' object has no attribute 'decode'` in `compute_session`, and writes no output. This is a stop, and it is read as a refusal. The custody kit refuses the same condition by name (`listed_file_missing`) before the program runs, so reaching it means the archive changed after it was verified. The fix, a named refusal `disclosure_record_missing`, changes the program hash and is made after the release (RL-125 item 4).

[Lead's choice in the ⟨LEAD⟩ slot: "owed at the release … by the lead". RL-125 item 2 lets the request say "equal"
only if someone compared the lists. `mapping.json` did not exist when this was assembled: the lead's note of
2026-11-12 23:20 says `inputs` waits for it after the pin. I did not open the custody directory to check. If
`mapping.json` exists when the request goes out, the lead compares its `copied_records` with the verify map on file
names and replaces the sentence with "They were compared on file names on ⟨date⟩ and are equal."]

[Lead's note on the "Known defect" sentence: RL-125 item 4 term 3 says the `disclosure_record_missing` fix goes in
*before* the pin if any file inside the program hash changes for another reason. Section 9 G-1 may cause that. If it
does, this sentence is replaced: the defect is then fixed in the pinned bytes.]

## 5. Fable's notes for the lead, as amended (not for pasting)

Notes 1 and 3 stand as written; notes 2, 4 and 5 are replaced by RL-125's text.

1. **"3 of 3" is tied to the bytes.** RL-123 §2 items 3 and 5: if any file inside the program hash changes
   before the pin, the three full archives, the nine (serial and pool) and the denied fixture are re-read on
   the final bytes, and the table above is replaced, not edited.
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
   added.]*
4. **The term 7 check runs against the table at `9f1b53767`** on `origin/analysis/2026-11-12-b6-r3-table` (stdout
   SHA-256 `7b7920cf…254c`; inputs `c9d0c893…`, `e17886bf…`, `62dbfaef…`). It carries RL-114's three strings. PR #748
   is filled from this table.
5. **Block rows in `first_program_only`: checked by the lead, zero** on the three full roots. The R12 report's
   sentence is corrected by the R12 seat.

## 6. The open ⟨NINE⟩ slots and their predeclared values

All slots are **OUTSTANDING**. Each is filled from the readers' records of `r12-r3-closed-air-25`, names and numbers
only. A slot that differs from its predeclared value goes to the research lead before the cut (RL-126 §4 (i),
item 3). Predeclarations are from the R12 report @ `d38495791`, "Both nines — role, volume and predicted outcomes
fixed before launch" and "Current pin-candidate result table and final dry-run prediction" (both written before the
nine started), RL-123 and RL-126.

| # | Slot | Predeclared value | Source |
|---|---|---|---|
| N-1 | program SHA-256 of the reads | `e17886bfefd066f1962357cede777568bf033898351d29365e2d0cdd22d423e3`, unless a file inside the program changes before the pin (then the final bytes, after RL-123 §2 item 3's re-reads) | RL-123 §2 items 2-3 |
| N-2 | option (c) exit | `0` | R12 predeclaration ("Each named option (c) exits 0 with comparator agreement"); RL-126 §4 gate |
| N-3 | compared rows | a count > 0, every compared row agreeing. No number was predeclared. | R12 predeclaration; RL-113 term 6 |
| N-4 | failed | `0` | comparator agreement |
| N-5 | unmatched | `0` | comparator agreement |
| N-6 | `first_program_only` count | no number predeclared. Every entry a session quantity key carrying a label that allows non-comparison; **0** `run_phase_energy` entries (RL-125 item 1); **0** `__block__` entries. Checked by section 7 | RL-113 term 7, RL-125 item 1 |
| N-7 | serial/pool byte equality | identical ("Serial/pool numbers and public bytes are identical within each cohort") | R12 predeclaration; RL-126 §4 gate |
| N-8 | wall, peak RSS (serial) | ≤ 2,400 s; ≤ 2 GiB | R12 final prediction |
| N-9 | wall, peak RSS (pool-2) | ≤ 1,200 s; ≤ 4 GiB (process-group planning budget) | R12 final prediction |
| N-10 | other R12 work on the Air during the reads | none, or named. Overlap is allowed (RL-126 item 7 dropped RL-123 §4's idle condition); the receipt names it | RL-126 item 7, §4 (ii) |
| N-11 | generation wall | reported, not a pass condition. Forecast about 12 native hours (R12 predeclaration); RL-126 forecasts the end of generation between about 11:30 and 14:00 PST | RL-126 §1, §4 (iii) |

Cut-gate items read from the same finisher. They are not in Fable's paragraph, but RL-126 §4's gate names them:

| # | Item | Predeclared value | Source |
|---|---|---|---|
| N-12 | denied-26 fixture, read by the pin candidate | OFF rc 126 and `network_time.off_output` retained; single-session option (c) 0, agrees | R12 predeclaration; RL-49 |
| N-13 | the six shapes | A1 cap/budget skips; A2 waited runs with attempt-N telemetry; B2 `member.anchor_not_bounded`; mixed member and evaluation campaign-log rows; desk-compressed campaign logs and plists; a nonvacuous cross-session GAMMA unit. Each named option (c) exits 0 with comparator agreement, registered flags retained | R12 predeclaration; RL-48 item 2; §17-R12 |
| N-14 | loop close | original DONE with **nine counting sessions** (possibly ten ordinary attempts, from the skipped A1) | R12 predeclaration |
| N-15 | dry-run stop | under 10,800 s; otherwise stopped and profiled, never retried (`b6_r12_dry_supervise.py`, `stopped_profile_required`/124) | RL-98 term 2, RL-123 §1 |
| N-16 | term 7 check (section 7) on the nine's restricted output | no stop | RL-126 §4 gate |
| N-17 | output SHA-256s: restricted, public, serial and pool | recorded (section 7 step 8) | RL-113 term 7 step 8 |

## 7. The RL-113 term 7 checklist (verbatim, with the RL-125 replacements)

Source: Fable's file, section "RL-113 term 7: label check on the nine's output". Steps 1 to 3 and 7 to 9 stand. Steps
4, 5 and 6 are replaced and steps 10 and 11 added, by RL-125's text. In step 8, "the R3 table's commit" is `9f1b53767`.

> Term 7 is owed on the real block run and does not gate the pin. Running it on the nine is a rehearsal on
> synthetic sessions. It reads key names only.
>
> 1. Take `block.option_c.first_program_only` from the **restricted** output of the nine's serial read. Confirm
>    the pool read's list is identical.
> 2. Count the list per class. Each count must equal that class's `first_program_only` in the public
>    comparator, and the total must equal the number written in the agreement sentence.
> 3. Confirm every public class record is one of two kinds: with `pass` and `compared` > 0, or without `pass`
>    and with `compared`, `passed`, `failed`, `unmatched` all 0. Any other record is a stop.
> 4. Split the list by class. Set the `run_phase_energy` entries aside for step 6; they have no R3 row. Reduce the rest to distinct key names (drop the session) and look each one up in the R3 table at `9f1b53767` (stdout SHA-256 `7b7920cf…254c`).
> 5. A key passes if its label is one of:
>    - `single-source` (RL-99 item 1);
>    - "not independently recomputed";
>    - the §17-R8 literal "single implementation; not independently recomputed" (RL-125 item 3);
>    - a gate label ("computed and compared in the option (c) gate …; not an S-13 table row");
>    - a conditional label, and the session it is listed for meets the label's second clause: for `neg8/*`, that session's NEG-8 verdict is `undefined`; for the contrast fields, the verdict is `undefined` or the twin returned no estimate. Check the condition per session, not per key.
> 6. **Stops, each to me:**
>    - any entry of class `run_phase_energy`, with the run's role and no value (RL-125 item 1);
>    - a key in the list labelled plain "computed and compared (decision 6 (a))";
>    - a key in the list with a block-scope label ("§10-§11 arithmetic computed and compared …"), or any entry with session `__block__`;
>    - a conditional-label key listed for a session whose screen is defined and whose twin estimated;
>    - a key in the list with no row in the R3 table, or labelled UNSTATED;
>    - a decision 6 (b) copied-family name in the list (those are never comparison-table keys);
>    - in the other direction: a `lines/whole_machine/<model>/<phase>/*` session key in a compared row (RL-125 item 3).
> 7. Cross-check the other direction once: no key that appears in a compared row for a session also appears in
>    `first_program_only` for the same session.
> 8. Record: the output's SHA-256, the program SHA-256, the R3 table's commit (`9f1b53767`), the per-class counts, and the
>    number of distinct keys under each label kind. No values are copied.
> 9. On the real block run steps 1 to 8 are repeated by whoever writes the agreement sentence, on the
>    restricted output, before that sentence is written.
> 10. Real block run only. Confirm the restricted output's `inputs.host` is `Air`, and that every session carries `copied_disclosures` with the eight families. Compare each family's `path` list with rows 150 to 157 of the R3 table. A difference is handled as RL-125 item 2 says. A session without `copied_disclosures` is a stop.
> 11. If the block command exits 1 with the traceback of RL-125 item 4, that is a refusal. Stop, check the archive against the kit's verify record, and tell me. Do not edit the program.

[Lead's note: the preface says term 7 "does not gate the pin" (RL-113 term 7, about the real block run). RL-126 §4's
gate makes "the term 7 check on [the nine's] output has no stop" a condition of the **cut**. Both hold: the rehearsal
on the nine gates the cut; the real-run check (step 9) gates the agreement sentence, not the pin.]

## 8. The cut procedure

RL-126 items 1-4 and §4's gate; RL-123 §2; freeze-by-commit F1 (`docs/process/freeze_by_commit.md`). Owner: the lead,
unless a step names someone else.

1. **Before the cut, while the nine generates.** This request is read by the research lead and Ed. Every section 9
   item marked GATING is decided; every other "before the cut" item is discharged or carried with its owner. By
   RL-126 item 3, if the request is accepted in every other respect by the time the finisher exits, no further review
   round follows, unless a slot departs from its prediction.
2. **The nine's finisher runs** (`b6_r12_dry_supervise.py` around `b6_r12_finish.py`, as the R12 report's
   orchestrator commands give it): serial and pool-2 reads, the shape checks, the denied-26 read. It must exit with
   option (c) 0, comparator agreement, serial/pool byte equality and the six shapes as predeclared (RL-126 §4 gate).
   Under 10,800 s, or stopped and profiled (N-15).
3. **Fill the slots** N-1 to N-17 from the finisher's records (names and numbers only). Any slot that departs from its
   prediction goes to the research lead before the cut. If the Air nine is retired for an **infrastructure** cause,
   RL-123 §1 item 4 lets a completed MBP nine stand in, but none was launched (section 5 note 3), so by RL-126
   item 6 no nine is relaunched without a ruling.
4. **Re-hash the closure.** At the commit to be cut, recompute every SHA-256 in section 2a and 2b, and confirm the
   finisher's checkout had the same closure: the reader receipts' commit or tree if they record one, otherwise a
   re-hash of the reader worktree's files after the finisher exits. If any byte differs, nothing is cut: RL-123 §2
   item 3's re-reads run on the final bytes (three full archives, the nine serial and pool, the denied fixture), the
   section 3a table is replaced, not edited, and RL-125 item 4 term 3's fix goes in with the change.
5. **Run the term 7 check** (section 7, steps 1 to 8) on the nine's serial restricted output against the R3 table at
   `9f1b53767`. Any stop goes to the research lead; no cut.
6. **Regenerate the R3 table at the commit to be cut** (`python3.13 scripts/b6_r3_table.py`, with the generator
   merged in). The stdout SHA-256 must be `7b7920cf7315d0a435d1eaae2f5bf35e45e8158d4335c83f64aad2828260254c`. A
   difference means the inputs moved: back to step 4.
7. **Cut S-14.** Choose the S-14 commit: the R12 line's head after the nine's evidence is committed, with the R3 table
   branch merged so that §17-R3's table is generated from the pinned commit. It holds the section 2 bytes unchanged.
   Record its full SHA and tree. Create the annotated tag `b6/analysis` on it; the message names the commit, the tree,
   RC-B6-1's and the Block 5 script's SHA-256, and this request. The SHA is the authority and the tag a convenience
   (F1). Push the tag.
8. **Record the pin.** In `docs/registrations/block6_freeze_by_commit_addendum.md` §1 "Proposed tags", fill the
   `b6/analysis` row (commit, tree, status). In PR #748, fill `OPEN[S-14-PIN]` (commit, tag, the four SHA-256 values
   of rows 1, 2, 19 and 20), `OPEN[R12-FULLSIZE-N]` = 3 ("3 of 3 packs, on single-pack roots, per host"), and
   `OPEN[R3-TABLE]` (the table at the cut commit, which must equal `9f1b53767`'s output byte for byte). Apply #748's
   deferred LOW 5 (dates) and LOW 6 (the S-14 source cell, `OPEN[S-14]` at REG:908 and REG:1192). Fable checks the
   fill delta before #748 merges.
9. **After the cut.** The blind dry run runs from the S-14 commit with the RL-98 term 2 stop. No Block 6 custody path
   is read by the program before step 7 (RL-126 item 4).

## 9. Owed items, with owners

Every item on the lead's owed list (`/Volumes/JW-EXT/scratch/s14-pin-request-notes.md`) that bears on the pin request
is below, discharged or open. W1, R1 and BYTES items on that list do not bear on S-14 and are not repeated.

### 9a. GATING: needs a decision before the cut

| # | Item | Why it gates | Owner |
|---|---|---|---|
| G-1 | **Seat 7's round-2 and round-3 fixes are not in the pin candidate.** RL-48: "F2 to F5 before the pin, as the review says; F6 to F8 in the same commit", and "the S-14 pin comes to me with the F2 witness". They were made and reviewed on `origin/analysis/2026-11-11-b6-path` @ `7c8251b28` (`fa0373cc9` F2-F8, Opus ADMIT-WITH-FIXES `920fc77c3`; `9fdec5aed` R2-F1 to R2-F3, Fable ADMIT `7c8251b28`). The R12 line branched from seat 7's round 1 (`da0a03145`, the merge base) and never took them: `7c8251b28` is not an ancestor of `d38495791`. At the pin candidate `clock_journal_required` (F8) and the `supplied_archive` root handling (F3) are absent from `joulewise/b6_analysis_inputs.py`, and `tests/independent_recompute/test_b6_production.py` has neither the F5 test (`test_c3_gamma_window_midpoint_loss_has_no_pack_scoped_primary_reason`) nor the F8 test (`test_listed_clock_journal_requires_pin_and_is_authenticated`). The F7 refusal in `MemberPool` is already present at RC:180-181. The 7b witness at the pin candidate is the pre-F2 one, so RL-48's condition for 7b ("shown when the strengthened witness of F2 passes, with decode and prefill given different synthetic values") is not met there. | Taking the fixes changes rows 1 and 5. That triggers RL-123 §2 item 3 (re-read the three full archives, the nine serial and pool, the denied fixture; minutes of reader time) and RL-125 item 4 term 3 (`disclosure_record_missing` goes in with it). Not taking them leaves RL-48's "before the pin" unmet and forces 7b-ii (§10 prints "block 5: not computed" for the per-phase line) unless the research lead rules otherwise. | Research lead (ruling: merge, or rule they are superseded); then the R12 seat (merge `7c8251b28` onto the R12 line, resolve against RL-113-115/121, run seat 7's tests and the 7b tests by id); the lead (re-reads, section 3a table, slots N-1/N-12) |
| G-2 | **The Opus cold review of R12's final implementation and evidence.** RL-48 item 7: "An Opus cold review follows, also Block-5-naive. Then the S-14 pin comes to me". The R12 report's final handoff lists it as "still incomplete". §13 also asks for "one blind executing cold pass by Fable and one by Opus" of the analysis programs. RL-126 item 3 says the cut follows the finisher "with no further review round". | The Opus review can cover the code and the existing evidence now, but not the nine's evidence before the cut, if RL-126 item 3 is read literally. See section 10, conflict C-1. | Research lead (which reviews discharge §13's two blind executing passes, and whether the nine's evidence needs Opus before the cut); the lead (launch the Opus seat now, Block-5-naive, on `d38495791`, or on the merged head if G-1 merges) |

### 9b. Owed before the cut (not gating a decision)

| # | Item | Owner |
|---|---|---|
| G-3 | Confirm the readers ran on the section 2a closure, not only on RC-B6-1's hash (section 2e; section 8 step 4). | Lead |
| O-1 | Fill slots N-1 to N-17 (section 6). | Lead |
| O-2 | The term 7 check on the nine's output, no stop (section 7; RL-126 §4 gate). | Lead |
| O-3 | `classes.run_phase_energy.first_program_only` is 0 in the nine's public comparator (RL-125 item 1). Covered by section 7 step 6. | Lead |
| O-7 | PR #748 fill (section 8 step 8): `OPEN[S-14-PIN]`, `OPEN[R12-FULLSIZE-N]` = 3 (owed-list item 5, RL-98 term 3), `OPEN[R3-TABLE]`, LOW 5 and LOW 6, then Fable checks the fill delta. `OPEN[R7-SESSION-INDEX]` stays open; it is not an S-14 field. | #748 builder seat, then Fable |
| O-8 | `b6/analysis` tag and the freeze-addendum row (section 8 steps 7-8). | Lead |
| O-9 | Correct the R12 report's "include block rows" sentence (section 3a). | R12 seat, next resume |

### 9c. Owed at or after the release (do not gate the pin)

| # | Item | Owner |
|---|---|---|
| O-4 | RL-104 check 3, the item-83 hand check of each copied-record file (RL-100 "Still owed"), with the reader's name. | Lead, at the release, restricted side |
| O-5 | RL-125 item 2: compare `mapping.json`'s `copied_records` with the verify map on file names, family by family; on a difference, reprint rows 150 to 157 and log one deviation line. | Lead, at the release (with O-4) |
| O-6 | RL-125 item 4 term 2 for the real run: whatever launches the real `block` command reads any exit other than 0 or 3 as a refusal. Shown for the R12 launchers only (section 3b). | Lead, before the blind dry run |
| O-10 | RL-125 item 4 term 3: `disclosure_record_missing` with one test, after the release, unless G-1 changes the program first. | R12 seat |
| O-11 | RL-113 term 7 on the real block run (section 7 step 9, and steps 10-11). | Whoever writes the agreement sentence |
| O-12 | RL-99 / §17-DLE2 gate on the first counting Block 6 session: exit 0, every family agreeing, 0 unmapped, on that session alone, before the closed run. | Lead, at the blind dry run |
| O-13 | Custody `inputs` with `mapping.json`, complete `relocations` (RL-100). | Lead, after the pin |

### 9d. Discharged in this request

| Owed-list item | Where discharged |
|---|---|
| 1. RL-101 condition (R, R_cm compared on Block 5; 12 rows, AGREE; pinned B5 bytes) | Section 3d; R3 report @ `9f1b53767` |
| 2. RL-104 check 2 (a source digest per copied file) | Section 3e; R3 report @ `9f1b53767` |
| 3. neg8/contrast label ruling applied to the generator | RL-114's three strings at `9f1b53767`, Fable ADMIT (RL-125 preamble) |
| 4. Regenerate the R3 table on R12's final head | Done at `9f1b53767` (merge of `d38495791`); re-checked at the cut (section 8 step 6) |
| 5. RL-98 term 3, N of 3 | 3 of 3 on the pin candidate (section 3a; Fable's paragraph). The #748 fill is O-7 |
| 6. RL-110 item 8 / term 3 (a key the first program prints and the second side lacks) | RL-113 paragraph (section 4, first part); code at RC:1306-1340 |
| RL-110 term 5 (GAMMA neg8 halving) | RL-114 fix in `check_block` `c9d0c893…` |
| Loop state pinned but omitted | RL-115 fix in RC-B6-1 (`external_input_missing`, RC:1716) |
| RL-113 term 5 paragraph; RL-121 sentence; RL-113 term 6 agreement sentence | Section 4 |
| RL-113 term 7 post-run check | Section 7 (rehearsal on the nine, a cut gate; real run O-11) |
| RL-125 item 1 count on the three roots | Section 3a |
| RL-125 items 2 and 4: the two sentences | Section 4 |
| RL-125 item 4 term 2 for R12 launchers | Section 3b |
| Fable flags 1, 3 and 5 (block rows; all-agreeing; MBP nine sentence) | Sections 3a and 5 |
| RL-48 F10 / RL-99: which label | Section 3f |
| Open question (00:05): does full volume repeat on the merged program | RL-123 §2, re-read only; done, 3 of 3 on `e17886bf…` |
| MBP registered nine "reported whatever it shows" (RL-123 §1 item 1) | Section 5 note 3: not run |

## 10. Rulings cited, and conflicts found

Rulings file `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` @ `258612016` (line numbers at that
commit): RL-48 :2102, RL-49 :2183, RL-95 :5612, RL-96 :5640, RL-98 :5688, RL-99 :5737, RL-100 :5762, RL-101 :5817,
RL-102 :5848, RL-103 :5881, RL-104 :5903, RL-110 :6196, RL-113 :6354, RL-114 :6412, RL-115 :6482, RL-121 :6827,
RL-123 :7163, RL-125 :7340, RL-126 :7433. There is no RL-97 in the file. RL-95 (BYTES twin) and RL-96 (powermetrics
wrapper) do not bear on S-14. The committed RL-126 points to the scratch file for its §4 replacement texts; this
request quotes them from `/Volumes/JW-EXT/scratch/fable-rl126-proportionality.md` §4.

**C-1. RL-48 item 7 against RL-126 item 3.** RL-48 puts the Opus cold review before the pin request reaches the
research lead. RL-126 sends the request now and lets the cut follow the finisher "with no further review round".
The R12 report counts that review as still owed, over "the final implementation/evidence". Read together, Opus can
review the code and the existing evidence while the nine generates, but nothing reviews the nine's evidence before
the cut except the slot comparison. One ruling settles it (G-2).

**C-2. RL-48 "F2 to F5 before the pin" against RL-126 "the nine now running at `e17886bf…` stands" (RL-125 item 4,
gate) and the request's "3 of 3 on the pin candidate".** Seat 7's fixes (G-1) change RC-B6-1. RL-123 §2 item 3
already says what follows, re-reads on the final bytes and no regeneration, so this is a gap the rulings already
handle, not a contradiction. But no ruling mentions seat 7's rounds 2 and 3 after RL-98 read them, and both the R12
report and the paragraph treat `e17886bf…` as final.

**C-3. Stale open-items row.** RLD's open-items table still lists "The S-14 pin request for Block 6, under RL-98
(volume, deadline 13 November 20:00 PST)". RL-123 §1 says RL-98 term 2's date "has no further force". Clerical only.

**C-4. RL-123 §4 against RL-126 item 7 and the R12 predeclaration.** RL-123 §4 kept "the closed nine's serial and
pool readers … run with no other R12 generator or reader on the Air"; the R12 predeclaration repeats it. RL-126 item 7
drops it. RL-126 is later and says so, so the predeclaration's sentence is superseded and slot N-10 records any
overlap. No ruling needed.

**C-5. "Program hash" scope.** RL-123 §2 item 3 and Fable's note 1 speak of "any file inside the program hash". The
recorded `program_sha256` covers RC-B6-1 only (RC:1447), and `b5_program_sha256` covers the Block 5 script. This
request reads "inside the program hash" as the whole executed closure of section 2a plus the tables of 2b, so that a
change to `check_block`, the twins or the inputs layer also triggers the re-reads. If the research lead means only
RC-B6-1, G-3 and section 8 step 4 narrow accordingly.

---

Assembled from: the lead's owed list; `RESEARCH-LEAD-DECISIONS.md` @ `258612016`; Fable's pin paragraph (05:50) with
the RL-125 (06:05) and RL-126 §4 (06:10) replacements; the R3 table report @ `9f1b53767`; the R12 report @
`d38495791`; PR #748 @ `27b6cacfd`; seat 7's reports @ `7c8251b28`; the lead-verified reader facts. Hashes computed on
the Air with `taskpolicy -b`, TMPDIR on JW-EXT, from `git show` and `git archive`; no running job, worktree or custody
path was touched.
