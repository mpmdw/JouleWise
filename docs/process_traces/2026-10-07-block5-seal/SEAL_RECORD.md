# Seal record of measurement block 5 (registration V5-CLAIM-25G83-B5)

Written on 2026-10-08 by an Opus 5.5 seat for the orchestrator of interactive session e4fc0437. This is the file
that the sealed registration names in its section 12 as the seal record:
`docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`. A **seat** is one model session working to a written
brief; the **orchestrator** is the session that leads the work.

## 1. What a seal is, and what this record is for

Measurement block 5 is three unattended measurement runs on one Mac, called **windows**, whose numbers are meant
to carry claims in a paper. Each window runs one **pack**, a fixed, committed set of experiment inputs; the three
packs are called ALPHA, BETA and GAMMA. Before any window runs, the rules are fixed in files. Three documents
state them: the **registration** fixes what is measured and which recorded conditions remove data; the **analysis
plan** fixes how the numbers are computed; and the **flag catalog** lists every recorded condition (a **flag**)
by its code and says what each does: nothing, a disclosure, the removal of one measurement, or the removal of a
whole window. The fourth thing fixed is the exact code and configuration a window may read. A **seal** is a list of SHA-256 digests, each of a named file at a named commit, written after an
independent gate has judged those files; a file is **sealed** when its digest is in the list, because any later
change to it shows as a different digest. (A SHA-256 digest is a 64-character fingerprint of a file's bytes. A
commit is one stored state of the repository, named by 40 hexadecimal characters.) This record is that list. With
it, anyone who holds the repository can compute each digest again from the commit named beside it, and so check
that the rules and the code were fixed before the data existed. The registration says of itself that it binds
nothing until this record exists.

## 2. The commits

```
 integration branch   ... -- C ------------ S ------------ R
                             |              |              |
                             |              |              +-- R, the record commit: adds this record
                             |              +-- S, the seal commit: changes only the three seal documents
                             +-- C, H_claim: holds the final bytes of everything a window reads
```

Commits run from left to right; a run of dashes joins a commit to the next one made on top of it (its **child**);
`...` stands for earlier commits; a vertical line ending in `+--` attaches a label to the commit above it. The
integration branch is `integrate/2026-10-07-int5`, the branch of pull request #489.

| Name | Commit | What it is |
|---|---|---|
| **H_claim** (C) | `a64000884ef5bb4b76415835f02f39803f6eb620` | The commit every window is compared with. A **window input** is a tracked file a window can read while it is planned, armed or run: every file under `joulewise/`, `scripts/` and `configs/`, and the one document `docs/phase_2/window_runbook.md`. H_claim holds the final bytes of every window input. |
| **The seal commit** (S) | `ab7b21e576a2d74f0b25d9a26b463d6934588368` | The only child of H_claim on the integration branch. It changes three files and nothing else, the **seal documents**: `sealed_inventory.json`, `registration_block5.md` and `analysis_plan_block5.md` in `configs/campaigns/v5_claim_25g83/`. |
| **The record commit** (R) | not printed here | The child of the seal commit that adds this record. A file cannot contain the name of the commit that adds it, because a commit's name is a hash computed over everything the commit contains. `git log --diff-filter=A --format=%H -- docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` prints it. |

Why the seal needs a commit of its own: the **sealed inventory** lists the SHA-256 of every code and pack file at
H_claim and names H_claim in its `head` field, and for the reason just given a file that names H_claim cannot be
part of H_claim. So the inventory, and the registration and analysis plan that print H_claim and digests computed
at it, are committed one commit later.

Read from the repository by the script that wrote this record (section 4.3 says how):

- `git rev-list --parents -n 1 ab7b21e576a2d74f0b25d9a26b463d6934588368` prints the seal commit followed by
  `a64000884ef5bb4b76415835f02f39803f6eb620`: one parent, and it is H_claim.
- `git diff --name-only --no-renames a64000884ef5bb4b76415835f02f39803f6eb620 ab7b21e576a2d74f0b25d9a26b463d6934588368`
  prints exactly these paths:
  `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`,
  `configs/campaigns/v5_claim_25g83/registration_block5.md`,
  `configs/campaigns/v5_claim_25g83/sealed_inventory.json`.
- The sealed inventory at the seal commit has `status` `SEALED`, `head` `a64000884ef5bb4b76415835f02f39803f6eb620`, and
  682 entries in its `files` map; it has no `roots` key, and it does not list the ledger pin
  (`configs/calibration/calibration_ledger_head.json`, the committed file that names the last row of the
  calibration ledger; it is data, and it advances after each window).

**How H_claim relates to the last change of a window input** (a fact the seal gate's last session required this
record to state; `RULING_STAGE2.md`, part B, section 4 and condition 5). The registration defines H_claim as the
last commit that changes a window input. This H_claim is a **merge commit**, a commit with two parents. Its first
parent is `1704059cc98334a9c402390ad041e1199e2c8936`, the commit that made the last change to a window input: it
changed the flag catalog (the file that says what each recorded condition does) and one sentence of the refusal
allowlist (the file that lists every place where code may stop collection or remove data). Its second parent is
`3ff380b74ff3f549ba7038a241c485e15e46638f`, the head of the branch `lane/2026-10-07-ci-linux-fixes`, which had
already merged that first parent and added changes to seven test files. So H_claim is the merge, two test-only
commits later, that holds the same window-input bytes:

- `git rev-parse <commit>^{tree}` (the one hash that names all the files of a commit) prints
  `96178f01902ad751d5e62e6ad01e6fb83af44611` for H_claim and `96178f01902ad751d5e62e6ad01e6fb83af44611` for
  its second parent: the two hold identical files.
- `git diff --name-only 1704059cc a64000884 -- joulewise/ scripts/ configs/ docs/phase_2/window_runbook.md` prints
  nothing.

Every digest in this record and in the sealed texts was computed at `a64000884`. The program that checks a
finished window (the harvest, section 3) compares the commit the window ran from with `a64000884`, as the
inventory's `head` says. The naming touches no byte a window reads.

## 3. The gate that judged the files

One **cold gate** sealed the registration, the analysis plan, the flag catalog and the sealed inventory together.
A cold gate is a judgment by a model session that took no part in writing or reviewing what it judges and that
starts with no knowledge of the work.

Three terms recur in the rulings. Each quantity the block reports is measured in 10 planned **units**, and a unit
is **kept** when no flag removes it. A **reference** is one run of a small fixed workload placed at the start,
the middle and the end of a window; the **drift screen** compares the references' energies to decide whether the
instrument drifted during the window, and a reference that cannot be used is **lost**. The **harvest** is the
program that runs at the desk after a window has ended: it checks the window's bytes, applies the drift screen
and the catalog, and writes which measurements are kept.

The gate ran in two stages. When its questions were ready, the commit that became H_claim was not yet fixed, and
a ruling that needs a code change is cheap only while that commit is open. So the rulings were taken first, on an
earlier revision (stage 1), and the judgment of the final text second (stage 2).

| Stage | Seat | What it judged | Record (in this directory) |
|---|---|---|---|
| 1, judge | Fable 5.1 | revision 9 of the registration, the plan and the catalog, with the code, all at commit `9b0c680ed` | `RULING_STAGE1.md` |
| 1, refuter | Opus 5.5 | the same documents and code, attacked: a **refuter** is a seat whose brief is to show a rule or the code giving a wrong outcome | `REFUTER_STAGE1.md` |
| 2, part A, judge | Fable 5.1, a new session | the final text, before H_claim existed | `RULING_STAGE2.md`, under "Part A" |
| 2, part B, judge | Fable 5.1, another new session | the digests and the seal's commits, once the seal commit existed | `RULING_STAGE2.md`, under "Part B" |

The two stage-1 files are byte copies of `/Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE1.md` and
`REFUTER_STAGE1.md`; their SHA-256 are in section 5. `RULING_STAGE2.md` holds both parts of stage 2 byte for byte,
each between two marker lines that carry its SHA-256.

**Stage 1** (2026-10-07; first line of the ruling: `STAGE 1: RULINGS COMPLETE`). The judge ruled on every question
put to the gate except the table of pinned digests, which was left to stage 2, and on each of the refuter's five
breaks. It required 48 changes to the text of the registration and the plan, written out word for word (the
ruling numbers them T-1 to T-48); one change to the catalog (C-1: the smallest number of kept units a reported
quantity may have goes from 8 to 5, the point below which the registered estimator can no longer compute its
result); and seven changes to code or to records in the code tree (K-1 to K-7). The rest it
confirmed, or corrected to what the code does: the catalog's effects as a whole; the two codes that only
summarise conditions other codes already act on (both stay disclosures); the rule for a reference that ran another model than the sealed one; a
proposed sensitivity line in the plan (a second figure printed beside a result, computed without the exclusions
for thermal pressure and for a competing process), adopted for three codes only; and the interval of GAMMA's two
contrasts (GAMMA compares two models, and the plan had registered a term the code does not compute). It ruled that three files the harvest writes
(`derived/flags.jsonl`, `derived/exclusions.json`, `derived/window_flags.json`) stay closed until the measured
values are released. It required no change to any code that runs during a window. Where the changes landed: the
catalog change and K-1 to K-3 (entries of the refusal allowlist, and one test fixture) before H_claim, through the
branch `lane/2026-10-07-seal-rulings`; the 48 text changes in revision 12 of the two texts; K-4 to K-7 in the
**harvest lane**, the branch that carries the gate's changes to the harvest (condition 3 of section 6, and
Addendum 1 below).

The refuter's record ends before the ruling existed: its second line still reads that its comment on the ruling
is pending. The five breaks it reported, and what the judge did with each:

| Break | What the refuter showed | The judge's disposition |
|---|---|---|
| RF-1 | A reference that ran but whose energy could not be read was not treated as lost: it failed the whole drift screen and removed a clean window. | Accepted. Such a reference is lost and the surviving references decide (text T-27, T-28; harvest change K-4). |
| RF-2 | When a window loses its midpoint reference, the rule removes a GAMMA window and keeps an ALPHA or BETA window, although GAMMA is the one pack with further references inside the window. | Rule confirmed, its stated reason corrected. GAMMA's results are decisions about which of two models uses more energy, and each decision's interval is widened by a drift allowance computed from the references; without the midpoint that allowance can only come out smaller. On ALPHA and BETA nothing is decided by it, and the loss is disclosed (text T-21 to T-25; allowlist K-3; no code change). |
| RF-3 | A damaged line in a flag file removed the window when the part still readable matched a code that only the harvest can write, and so cannot have been lost from a file written before the harvest. | Accepted. Candidates are limited to codes a program writing before the harvest can emit (text T-29, T-30; harvest change K-5). |
| RF-4 | The rule that removed a window when a reported quantity kept fewer than 8 of its 10 units discards clean windows for precision, not for a wrong number. | Accepted. The minimum is 5 (catalog C-1; allowlist K-1; text T-1 to T-18). |
| RF-5 | A reference during which contention (other processes competing for the machine) or the battery was not measured stayed in the drift screen, where an unseen background process can hide a real drift. | Accepted. Such a reference is lost, as is one whose quiet state was violated or whose battery readings failed; unmeasured clock or thermal evidence loses nothing (text T-31; harvest change K-6). |

**Stage 2, part A** (session of 2026-10-07 23:55 to 2026-10-08 00:05 PDT; first line:
`STAGE 2A: TEXT ADMITTED WITH REQUIRED CHANGES`). The judge read revision 12 at commit `c7408819c` of the design
branch `design/2026-10-05-v5-claim-block-draft`, the branch on which the documents were drafted. It found all 48 stage-1 changes present: 44 byte-exact by
script, and four read by hand (three that a writer had merged with other edits, each keeping the ruling whole,
and one whose old text is a prefix of its new text). It confirmed the four rulings the orchestrator had made after
stage 1: how it is decided that two failed attempts of a pack share a cause; that five changes to the harvest's
comparison of a window's code with the seal belong in the harvest lane; that the registration's question on the
limits of the agent census (a window's listing of Claude and Codex processes, which stops the window when it finds
one) is closed; and that the attribution floor (a bound on how exactly an energy can be assigned to one phase of a
run) is registered as a formula, with no number bound. It recomputed every number the rulings had changed, and admitted the catalog
unchanged (192 codes, the minimum at 5). It ruled on two places where stage 1's text and the harvest lane
disagreed, and required four small changes: three to the registration's text (T-S2A-1 to T-S2A-3) and one
sentence of the refusal allowlist (K-S2A-1). All four were applied word for word (design branch `9864f7163`;
integration branch `1704059cc`), before H_claim. The places in the text that waited for H_claim (its name, and
digests computed at it) were then filled by script, and the final text is commit `cf92f73ec207634d5b2b3a76cae41d3e626befee` of the design branch, whose registration
and plan are byte for byte the ones in the seal commit.

**Stage 2, part B** (session ended 2026-10-08 01:26 PDT; first line of the ruling: `SEAL: ADMIT`). The judge worked
from the stored commits and from a scratch clone at the seal commit. It recomputed the digests of the three seal
documents and the catalog; read every difference between the text part A admitted and the sealed text, and found
only part A's three required changes, the filled places, the sentences that had said those places were still
open, and one sentence of section 0.18 corrected to a fact it verified by digest; checked that H_claim holds, beyond what
part A saw, exactly the admitted catalog, the one allowlist sentence, four documents and seven tests; rebuilt the
inventory's 682 entries twice, from the stored commit and from a clean checkout, and found both equal to the
committed map; checked the seal commit's one parent and three-file change; ran, at the seal commit, the test that checks the
seal's commits (`tests.test_b5_seal_landing`), the repository's two consistency checks (`scripts/gen_state.py
--check`, `scripts/repin.py --check`) and the harvest's own parser of the registration's thresholds; and
recomputed every digest of the tables in section 4. Its ruling is **`SEAL: ADMIT`, subject to five conditions**,
which section 6 lists.

## 4. The sealed digests

### 4.1 At the seal commit `ab7b21e576a2d74f0b25d9a26b463d6934588368`

| File | SHA-256 |
|---|---|
| `configs/campaigns/v5_claim_25g83/sealed_inventory.json` | `57ee5d4a8ce632dfca7858f8f834d75dce463276b35fffc4edad91af2d76312a` |
| `configs/campaigns/v5_claim_25g83/registration_block5.md` | `4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841` |
| `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` | `1172a4501e2311a98508e6102420de657daa88c8c455603717b8ff7b2a1e1b8a` |

### 4.2 At H_claim `a64000884ef5bb4b76415835f02f39803f6eb620`

The seal commit changes none of these files, so each has the same bytes at the seal commit. In the first column a
**member** is one measured model run, a **prefill** member is one that measures the model reading a long fixed
prompt, and a window's **chain** is the shell program that runs its members between two calibration captures.

| What it is | File | SHA-256 |
|---|---|---|
| the flag catalog: every recorded condition by its code, with what it does | `configs/campaigns/v5_claim_25g83/flag_catalog.json` | `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d` |
| the plan tree of pack ALPHA: the file that lists the pack's stages in order, with each stage's inputs, command line and expected number of members | `configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json` | `1d87a30955fa978d3a3a22dc0048720691e0128e4a3fe83477fc375d13dd031a` |
| the plan tree of pack BETA: the file that lists the pack's stages in order, with each stage's inputs, command line and expected number of members | `configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json` | `0cdb33836f4632827bc74be194e388450c53b3314db1c72d9e9904e625868670` |
| the plan tree of pack GAMMA: the file that lists the pack's stages in order, with each stage's inputs, command line and expected number of members | `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json` | `8b1d1d7176f5ee2286038e91df6427e47476c3a4bdee45a1c24687d49d80e3bf` |
| the model panel: the list of models the packs draw on | `configs/model_panels/qwen3_4bit.json` | `78875a0e8b2c6d9f573cd42b0d27de6498cdfc8de57af4b4a502e1f93a02513a` |
| the idle policy: the block's campaign policy, which sets the cool-down and the idle check a member must pass before it runs | `configs/campaign_policies/quiet_mac_p2_b5.json` | `ba0f7b7f1538fe87f6281362efbba4b05f7dff74b4bfd78e84c98b9e8859bc60` |
| the calibration acceptance for macOS build 25G83: the issued record of the calibration bound the windows are judged against | `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` | `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660` |
| the prompt pin: the exact prompt text and token ids of the prefill workload (pack ALPHA) | `configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/prefill_prompt_pin.json` | `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb` |
| the selection record: how the prefill length was chosen (pack ALPHA) | `configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/selection.json` | `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222` |
| the ladder: the prompt lengths the selection drew from (pack ALPHA) | `configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/prefill-prompt-ladder.json` | `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885` |
| the prompt pin: the exact prompt text and token ids of the prefill workload (pack BETA) | `configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/prefill_prompt_pin.json` | `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb` |
| the selection record: how the prefill length was chosen (pack BETA) | `configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/selection.json` | `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222` |
| the ladder: the prompt lengths the selection drew from (pack BETA) | `configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/prefill-prompt-ladder.json` | `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885` |
| the prompt pin: the exact prompt text and token ids of the prefill workload (pack GAMMA) | `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/prefill_prompt_pin.json` | `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb` |
| the selection record: how the prefill length was chosen (pack GAMMA) | `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/selection.json` | `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222` |
| the ladder: the prompt lengths the selection drew from (pack GAMMA) | `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/prefill-prompt-ladder.json` | `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885` |
| the sizing output: each window's planned length and the allowances a plan copies from it | `configs/campaigns/v5_claim_25g83/sizing_b5.json` | `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa` |
| the identity pins: the digests of the models and of the Python packages a window must be running | `configs/campaigns/v5_claim_25g83/identity_pins.json` | `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9` |
| the chain-source document: the plan writer copies its pre-calibration screen, a block of shell text, into every window's chain | `docs/phase_2/window_runbook.md` | `c4e8bf416269ba3a9fb5ffda3404414ce7227d162c1329cea92817a38ea384c5` |

The nine `prefill_pin/` files carry three distinct digests, one for each kind of file: the three packs share one
prompt pin, one selection record and one ladder. A fourth `prefill_pin/` directory exists at H_claim under
`configs/campaigns/d117_contrast_v5/`; that directory is not one of the three packs and is not pinned.

`sizing_b5.json` and `identity_pins.json` still carry `"status": "UNSEALED_DRAFT"` and `"sealed": false` in their
bytes. Those are labels their generators wrote before the seal; no program reads them, and changing them would
change a window input after H_claim. What seals each of the two files is its digest in the table above
(registration section 12).

### 4.3 How these digests were computed, and how to check them

Every digest in sections 2, 4 and 5, and every commit name and count in section 2, was computed by a script when
this record was written and inserted by that script; none was typed or copied by hand. For a file at a commit the
script ran exactly

```
git show <commit>:<path> | shasum -a 256
```

and it refused to write the record unless each result equalled the value that three other readings give: the
table in part B of the gate's ruling (`RULING_STAGE2.md`), the values the sealed registration prints for the plan
trees, the sizing output and the identity pins, and the values the runbook's values file holds for the three seal
documents and the catalog. For the seal documents the registration cannot print its own digest; the comparison
there is with part B's table and the values file.

To check the record from the repository, run the checker that is committed beside it. It reads the two tables of
this section and the table of section 5 out of this file, recomputes every digest from the commit or file named,
and prints one line for each:

```
python3 docs/process_traces/2026-10-07-block5-seal/bench/check_seal_record.py
```

It ends with `seal record: every digest recomputed and equal` and exit status 0, or names each difference and
exits 1.

## 5. Records of the gates, copied into this directory

The sealed registration prints the SHA-256 of three records that it cites from outside the repository (its
section 2 item 1), and names the two stage-1 files of the gate. Their copies here are byte copies; the digests
below were computed from the copies by the same script, which also required the first three to equal the values
the registration prints.

| Record | Copy in this directory | SHA-256 of the copy |
|---|---|---|
| The seal gate's stage-1 ruling | `RULING_STAGE1.md` | `954ac12e9136bd29fdcc5979e654149fd51ca9490d7ded142010efba184d1279` |
| The stage-1 refuter's record | `REFUTER_STAGE1.md` | `f4a42b19c3edf3dd5c71a6ea1f9a817625387499c39a9f12a61d961fc228bdf8` |
| Fable delta cold pass 5 (on `fe28e5a0c..9395cecfb`) | `gates/40-cold-pass-5.md` | `46446fa429bdceaac91da1bb3916714c3c59fd846c6bf4503bad4462e218e8ad` |
| The independent executing review of the seal-landing lane | `gates/10-seal-landing-review.md` | `fec2dc44938731c8528777b66c336df07ca553ff6f43f2bcd146cab641012f0a` |
| The orchestrator's ruling on that review | `gates/50-seal-landing-dispositions.md` | `92ba27dc49ce205e76111a46bdddda6450ba21863feb8f5d1177527be27fde4e` |

The other gate records are under `gates/`; `00-seal-and-arm-record.md` lists each with what it found.

## 6. Conditions of the seal

The seal stands on the following. Conditions 1 to 5 are the five that part B attached to `SEAL: ADMIT`
(`RULING_STAGE2.md`, part B, section 8), restated here: the gate admitted the seal subject to them. Condition 6
is the registration's own (its section 12).

1. **The record commit.** It is a child of the seal commit on the integration branch. The paths that differ
   between the seal commit and it lie under `docs/` and `tests/` only; none is a window input. It adds this record
   and the gate's records, and its copies of the two stage-1 files hash to the values of section 5. The whole test
   suite and CI (the checks GitHub runs on a pushed commit) pass at it. The whole suite: run 9 at the seal commit, 9,853 tests (9,785 in six shards and 68 in the two exclusive modules); five tests failed inside the shards, and every one passes when its module is run alone and when the runner is saved as a file (four are an artefact of feeding the runner on standard input; one is a test-order defect in which an earlier test module leaves termination signals ignored); the record is `gates/20-whole-suite.md`. The record commit adds documents and one test module to the seal commit; the modules that read those documents were run at the record commit and pass, and the full Linux matrix runs on the record commit in CI; the orchestrator ruled on 2026-10-08 that this meets the condition. CI: a
   commit cannot hold the result of the checks that run on it, so that result is not written here; it is
   recorded in the pull request's ledger, whose row 3 names the head at which CI passed. The pull request is merged with a merge commit, never squashed or rebased, so that
   H_claim and the seal commit stay in the main branch's history, and the merge commit holds exactly the record
   commit's files. `RUN_STATE.md`, the file that carries the hand-off block read by the magistrate (the unattended
   session that arms and harvests the windows), is a document at the repository's root; under this condition it is not part of the record commit:
   the orchestrator ruled on 2026-10-08 that its new block is committed to the main branch as a documents-only commit directly after the pull request's merge and before the stop ref is deleted (registration section 11 item 1, class iii).
2. **The measurement clone**, the one checkout every window of the block runs from, is a full clone checked out at
   the seal commit: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5`. In it
   `git diff --name-only --no-renames <H_claim> HEAD` lists exactly the three seal documents, `git status
   --porcelain` prints nothing, and the identity checks a window makes at its start, run at the desk with H_claim
   as the reference, raise no flag whose code begins with `code.` for any of the three packs (the section "Plans
   written after the seal" records that run). Afterwards the only commits ever made in it are **pin advances**,
   each changing `configs/calibration/calibration_ledger_head.json` alone; nothing is merged, pulled or checked
   out there.
3. **The harvest lane stays at the desk.** The changes the gate required of the harvest (K-4 to K-7, and five changes to
   its comparison of a window's code with the seal) are on the branch `lane/2026-10-07-harvest-lane`. That branch
   reaches only the checkout the harvest runs from, never the measurement clone, and not the integration branch or
   the main branch before Addendum 1 below pins it. Its difference from H_claim lists only
   `joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `scripts/harvest_b5_window.py` and paths under
   `tests/`. Part B also required that the lane's tests hold a synthetic window for each of the three breaks
   the harvest cures (RF-1, RF-3 and RF-5 of section 3), and that its test of path classes assert the lane's own
   table. When this record was
   written, `git grep` at the commit Addendum 1 pins found these five tests by name:
   `test_a_succeeded_reference_with_no_energy_envelope_is_lost_and_the_survivors_decide` (RF-1),
   `test_a_flag_file_line_torn_inside_calibration_capt_is_disclosed_and_removes_nothing` (RF-3),
   `test_a_journal_gap_over_one_reference_loses_it_and_the_survivors_decide` (RF-5), and
   `test_the_harvest_and_the_collector_class_paths_alike_but_for_the_harvests_positive_list` with
   `test_on_every_tracked_path_the_harvests_window_inputs_contain_the_collectors` (the table of path classes).
   No window is harvested before Addendum 1 names the commit, the files and their digests.
4. **The analysis plan's eleven open markers** belong to the analysis code, which is written after the windows and
   before any measured value is opened. Each is filled only after the seal, and each fill is recorded in an
   addendum to this record that states the plan's new SHA-256. The registration's bytes never change.
5. **The naming of H_claim** is stated in this record: section 2.
6. **What no program checks.** No program compares a later commit to the registration or the plan with this
   record, and no program reads this record. The rule that covers it (registration section 12): an attempt (one
   window of a pack) is analysed only when the digests the harvest recorded for the registration, the catalog and the inventory equal
   the ones in section 4; otherwise the attempt is harvested again on the same bytes with the sealed files.

## 7. Sections appended after the seal commit

The registration's bytes cannot change after the seal commit: every window's plan (the file that fixes one
window's start time, directories and thresholds) records the registration's SHA-256, and the harvest fails when
the file differs from it. A value that comes into being only after the seal
commit is therefore never written into the registration. It is written here, as a named section. The registration
names these in advance: the plans, the pins of the harvest program and of the analysis program, the release event,
the commit each window ran from, a new sizing file, and a re-issued seal. Three of them follow. The others are
appended when their values exist, each with the date and the seat that wrote it.

## Plans written after the seal

A **plan** is the file `night_plan.json` that fixes one window: its start time, its directories and its
thresholds. The registration requires that every plan, and every plan-input file a plan is written from, be
written after the seal commit from the sealed threshold block of its section 4.3, in which the time the machine
must stay free of competing processes before a window may start (`contention.clean_s`) is 180 seconds. A plan written before the seal cannot be
used: it would carry the earlier value of 600 seconds, it would name an earlier commit than the one the
measurement clone is at, and it could not hold the sealed registration's digest.

The windows' own plans do not exist yet. To **arm** a window is to write its plan and schedule it. Each plan is
written at its window's arm by the magistrate, from the measurement clone, and its plan id and the digests of its plan and plan-input file go
into that window's arm record on the branch `records/2026-10-block5`. What this section records is the proof,
made after the seal commit and before the first arm, that a plan for each pack can be written from the sealed
files, and that no earlier plan exists.

**The proof** (runbook step 6, run on 2026-10-08 by the seat that built the measurement clone; its notes are
`/Users/edr/night-archive/gate-prune/wave-1007b/landing/NOTES.md`). For each of the three packs a plan was written
in a scratch directory, `/private/tmp/b5-seal/planproof-1791447652`, from the measurement clone at the seal commit, with a
stand-in plan id (`PROOF-b5-<pack>`) and nothing created under `/Users/edr/night-custody`, the only place a
window's plan is ever looked for. Each plan record has the status `STAGED`, lists no threshold that differs from
the sealed block and no key outside it, and holds `contention.clean_s` 180. The digests of the six files, computed
by the script that wrote this record from the files themselves:

| Pack | Members | `window_max_s` | `plan-inputs.json` SHA-256 | `plan-record.json` SHA-256 |
|---|---|---|---|---|
| ALPHA | 119 | 102,180 | `d84c0d83bc76a178430f6c9b10971dbef8e62bc30bb775bd427e99b3b5babdcf` | `0c59c26d80fcb30306c866f6fa4a49843455c29d40928de73dd95bf0e59dd441` |
| BETA | 119 | 104,580 | `014b0956bd5fb0a3f294763804ddcc7a53b26f75dbd1ebaff7da6fc78d154d6c` | `65a8453aec68ca9cf0b636dd161c7f16815fa4c38cabacc51ce27ee1107afbc5` |
| GAMMA | 101 | 91,020 | `e9c51ddb569cc2770a218472164cbd610e2ff5f644d112c232be0e583efa65c0` | `d6168bdd4ff40bc84335864e5fac62e142fa1a42865a4e564111829e8e0ebd98` |

`Members` is the number of measured model runs the plan holds; `window_max_s` is the window's deadline in seconds
after its start, with every member on its longest allowed path. Both were read from each plan record by the same
script. For each pack the chain passed the repository's static check, the scheduler job that would start the window
(a macOS launchd job) was rendered without being installed, and the desk seal check (the four identity checks a window makes at its start, run with H_claim as the
reference) printed that it raised no flag. These scratch plans prove the path and are never armed: a real plan has
its own id, its own start time and its own directories, so its digests differ.

**The helpers.** Four small programs write a plan's inputs and make the checks before an arm. They are kept
outside the repository's `scripts/` directory, because a new file there would be a file the sealed inventory does
not list; byte copies are in `bench/` beside this record. Their SHA-256, and that of the program that generated
the sealed inventory, computed from those copies:

| Helper | SHA-256 |
|---|---|
| `b5_plan_inputs.py` | `f77f60c16e2122e1aa0cfe1ef2eb47fb88808e969cc8f5c7319766d664420f3b` |
| `b5_desk_identity.py` | `6c46fab80ed8f6d9b1d57949211a8197f70dd510e4559eeeb6415ab44dea48cf` |
| `b5_desk_seal_check.sh` | `c609714cb3eb745e474870295fe47b93f040e2a46d7bfd5f126e5d32fac5b381` |
| `b5_agent_check.py` | `5d6fac1279430998cc3219a73d4a02914479443a342ebe594ad01c364d14080d` |
| `make_sealed_inventory.py` (the generator of the sealed inventory; not used at an arm) | `617554f5cf6fab2f45ee04705c1138daacef1faf387826b30f3efd48a7d92de0` |

**No plan written before the seal exists outside the rehearsal archives.** When this record was written,
`/Users/edr/night-custody` held 0 directories whose names begin with `v5-b5-`, the prefix of every
block-5 plan id, and `/Users/edr/night-plan-staging` held 0 (both counted by the same script). The plans
written for the rehearsals of 2026-10-06 are in the rehearsal archives under
`/Users/edr/night-archive/gate-prune/rehearsal-*`; they are not claim windows and are not used.

## Erratum 1: the second seal (written 2026-10-09, by a seat that has read no claim-window energy)

**Why there is a second seal.** A seal fixes the bytes a window may read and the two documents that say what
will be measured and how it will be analysed. The first seal's reference corpus (the short runs of one fixed
small workload at the start of every window, from whose spread the drift bound is computed) had 12 members
and needs 10. Both ALPHA windows that ran a chain lost it: one kept 10 at run time with no margin, the other
kept 9. A prospective cold erratum, ruled on 2026-10-09 before any further arm, enlarges the committed corpus
to 18 members. Because that changes files a window reads, registration section 7.5 supersedes the block: the
three ALPHA attempts of the first seal are kept and disclosed and their energies are never analysed, and the
block restarts at ALPHA attempt 1 under this seal. Sections 2 to 6 above describe the first seal and stand
as its record.

**The gate.** Papers in `docs/process_traces/2026-10-block5/`: the consult on ALPHA attempt 3 and its cold
ruling (`alpha-a3-consult.md`, `alpha-a3-consult/RULING.md`); the erratum, its refutation, the cold ruling
that admitted it with corrections, the corrections as applied, the seal-text edits and the text gate
(`corpus18-erratum/ERRATUM.md`, `REFUTATION.md`, `RULING.md`, `CORRECTIONS-APPLIED.md`, `SEAL-TEXT-EDITS.md`,
`TEXT-GATE.md`); the window-side build's gate record (`corpus18-erratum/pr492-gates.md`). Judge: Fable 5.1,
cold. Refuter: Opus 5.5. Last line of the ruling: `ERRATUM: ADMIT-WITH-CORRECTIONS`.

**The commits.**

| Name | Commit | What it is |
|---|---|---|
| H_claim (second seal) | `c27485347c9629b857df81665b5b1b8d10dcd36a` | the merge of pull request #492; the last commit that changes a window input |
| seal commit (second seal) | `be6525e5a6511adf882282e404e163e14dbb738b` | its only child; changes only the three seal documents |

Against the first seal's H_claim `a64000884ef5bb4b76415835f02f39803f6eb620`, no file under `joulewise/` or
`scripts/` differs at the new H_claim (`git diff --stat a64000884 c27485347 -- joulewise scripts` is empty).
What differs under `configs/`: nine files of `configs/campaigns/neg8_reference_corpus_v5/`, one literal or a
few in each of four pack generators, the three packs' `plan_tree.json` and `plan_tree.sha256`,
`sizing_b5.json`, `identity_pins.json` (the three plan-tree digests only) and `configs/pins/registry.json`.

**The sealed digests of the second seal** (each computed with `shasum -a 256` at the seal commit).

| File | SHA-256 |
|---|---|
| `configs/campaigns/v5_claim_25g83/registration_block5.md` | `c7b3fdf78dde0a403bbc0b63262d1f8b1a697695bdeb2fb737a90cedde1ddb3f` |
| `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` | `23ef67f56cc3cd2346e3ace87ec1d9390ef8b5727bd3bad169ea66d30a374859` |
| `configs/campaigns/v5_claim_25g83/sealed_inventory.json` (682 files, generated from a clean checkout of H_claim) | `80852d98c13472e502411c2131d420b442fec2852350c3c520b2666a6826c4dc` |
| `configs/campaigns/v5_claim_25g83/flag_catalog.json` (unchanged) | `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d` |
| `configs/campaigns/v5_claim_25g83/sizing_b5.json` | `a8e8d53036f08b5d6edc648ec77f01f75890ae904a817204600d6daac912cfad` |
| `configs/campaigns/v5_claim_25g83/identity_pins.json` | `513d7d4a98f464c7236b34c53f51cd523a9f45b4d9f05f2282a4a22424b4841d` |
| `configs/campaigns/neg8_reference_corpus_v5/order_manifest.json` (18 rows) | `9cad99874d11a194eec5f56964a7d9a7f4ae361f6ff1f95e1a55dfe3216ff36f` |
| `configs/campaigns/neg8_reference_corpus_v5/derivation/settled_corpus.json` (18 members) | `c957880aef0d3b99f82cc917eb3f3e8a24a5aca2665134b19430b89e0f553304` |
| ALPHA `plan_tree.json` (`d117_floor_qwen3-1p7b_v5`) | `2ec3625a31b796e3fa37e2c39f37508618b649d0d9f61ddbd3fdfe2c5a282809` |
| BETA `plan_tree.json` (`d117_floor_qwen3-8b_v5`) | `e77e4f6e74f663190d1acfe95c3e2499ec69c1b27ba9e3564c531affee980707` |
| GAMMA `plan_tree.json` (`d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`) | `da8028977dfe44b3bf1d13e79e7bfea2b1390aa985bef7faa891369c8e3985bc` |
| `configs/pins/registry.json` | `64930f7521d9b447269fd24e06531b735655a2163e3ac30f40791f35add6491a` |

`python3.13 -m unittest tests.test_b5_seal_landing tests.test_digest_pin_census` passes at the seal commit
(28 tests), and the sizer's and the identity-pin writer's check modes exit 0 there.

**What is not yet done when this section is written,** and is recorded in later sections as it is done: the
harvest program for the second seal (the desk rule that derives the deciding bound from the first 12 clean
corpus members in committed order; branch `lane/2026-10-09-harvest-corpus-cap`) and its `B5-HARVEST-PIN`
addendum; the second measurement clone; the 18-member rehearsal. Until a later addendum names a harvest pin
built on this seal, no window of the second seal is harvested, and none is armed before the rehearsal has
been harvested by that program (the erratum ruling's section D, gates 5 to 7). Addendum 1 below pins the
harvest program of the first seal's three attempts and stays in force for them.

## Addendum 1: the harvest program (written 2026-10-08, by a seat that has read no claim-window energy)

B5-HARVEST-PIN: 7e6158d669cbb6fb35761aee18abf363f07c5d36

Desk clone: /Users/edr/night-custody/desk/b5-harvest. Files at that commit, with their SHA-256:
joulewise/b5/harvest.py f68e53d4e84292c182772a20edf2e3649c7470a7113ff87ebdec6f91208c9bc2; joulewise/whole_window.py ee107b1e5f7eab306192c78d43171de828c290158bd3dc6fb5e63c229a1c25a5; scripts/harvest_b5_window.py 88ac1164e729691e4db249b77ebbd17072dbcd3f514499840a56f56576d66d45.
The lane: lane/2026-10-07-harvest-lane, items K-4 to K-7 and H-8 to H-13. Its independent executing review:
docs/process_traces/2026-10-07-block5-seal/gates/13-harvest-lane-executing-review.md. Its cold Fable pass:
docs/process_traces/2026-10-07-block5-seal/gates/14-harvest-lane-cold-pass.md. git diff --name-only
a64000884ef5bb4b76415835f02f39803f6eb620 7e6158d669cbb6fb35761aee18abf363f07c5d36 lists only those three
files and paths under tests/.

## Addendum 2: the harvest program of the second seal (written 2026-10-09, by a seat that has read no claim-window energy)

B5-HARVEST-PIN: 224a264c5faaae90cdf56118df37e773a932700b

Desk clone: /Users/edr/night-custody/desk/b5-harvest. Files at that commit, with their SHA-256:
joulewise/b5/harvest.py 8aaaf96f4e3212e9c6544aa9908006d4a3cde794a61e3dff2106d677bd28dd2a; joulewise/whole_window.py ee107b1e5f7eab306192c78d43171de828c290158bd3dc6fb5e63c229a1c25a5; scripts/harvest_b5_window.py 88ac1164e729691e4db249b77ebbd17072dbcd3f514499840a56f56576d66d45.
The lane: lane/2026-10-09-harvest-corpus-cap, cut from the first harvest pin 7e6158d669cbb6fb35761aee18abf363f07c5d36
and merged with the second seal commit be6525e5a6511adf882282e404e163e14dbb738b, so it descends from the second
seal's claim head c27485347c9629b857df81665b5b1b8d10dcd36a. git diff --name-only be6525e5a 224a264c5 lists only
those three files and paths under tests/. The last two files are unchanged from the first pin.

What changed in the harvest program: the method that builds the clean bound (the drift bound that decides the
screen and the allowance) now runs on every window and keeps the first 12 members, in the committed order of
order_manifest.json, that are in the validated in-window bound and carry none of the six physics codes; all of
them if 10 or 11 remain; fewer than 10 gives neg8.bound_not_derived. Members beyond the twelfth are listed in
the record under beyond_cap and are used by nothing. A stored NEG-8 condition is cleared by a re-screen only
after a real loss (a newly lost reference, or a bound rebuilt after a corpus member was dropped for physics),
as the sealed text says; a re-screen that cannot run, or a clean bound that cannot be built or validated,
leaves the screen failed and supplies no allowance. This is registration section 5.3 as amended by the erratum
of 2026-10-09 (section 14 Q16).

Its gates: docs/process_traces/2026-10-block5/corpus18-erratum/harvest-pin2-gates.md (the builder, the second
seat that corrected and reviewed it by executing, two cold Fable passes, the whole suite on the lane's tree).

Like the first harvest lane, this lane is not merged into main: main holds the sealed bytes of
joulewise/whole_window.py and joulewise/b5/harvest.py, which are the files a window executes, and the desk
root is a separate checkout at the pinned commit. The branch is kept on the remote.

This pin is for windows of the second seal. Addendum 1 stays the record of the program that harvested the first
seal's three ALPHA attempts; a re-harvest of one of them by this program passes the first clone's path, its
sealed inventory and that attempt's archived ledger copies.

## Addendum 3: Erratum 2 of block 5, and the harvest program for the attempts it governs

### Step 1, written 2026-10-10 before the arm of any attempt Erratum 2 governs (by a seat that has read no claim-window energy)

Erratum 2 (prospective): `docs/process_traces/2026-10-block5/sources-erratum/ERRATUM.md`, SHA-256 of the admitted
text as committed on main `b85105457cb6da00f26eb92de594311e0e3aa497de8365cb2dc2dc234307188a`. It was admitted with
corrections by a cold gate under registration section 10: the ruling is `RULING.md` beside it (a Fable 5.1 judge,
last line `RULING: ADMIT-WITH-CORRECTIONS`), the refutation `REFUTATION.md` (an Opus 5.5 refuter). What it
changes: when the whole-window verdict stored in a window's claim runs root records no source campaign
manifests, and only in the diagnosed state its item 0 defines, the harvest takes the list of the window's
reference runs from the authenticated campaign catalog of that runs root and runs the registered drift screen on
the references that survive. No threshold, flag code, roster, blinding rule or window input changes. The
registration's bytes are not edited and the seal is not re-issued.

ERRATUM-2-ADMITTED-AT: 2026-10-10T16:30:00Z

Pin scoping. An attempt is governed by Erratum 2 when its plan's `t0_epoch_s` is later than
`ERRATUM-2-ADMITTED-AT` (epoch 1791649800). Addendum 2's pin `224a264c5faaae90cdf56118df37e773a932700b` remains
the pin for every attempt that is not governed, which includes ALPHA attempt 1 and BETA attempt 1 of the second
seal; the pin of step 2 below governs only governed attempts. No attempt that is not governed is harvested by
the new program for a deciding record; a run of the new program over such an attempt, if ever made after the
release event, is exploratory, labelled so, and changes no verdict, `claim_usable`, cause key or attempt
history. The analysis checks each attempt's recorded harvest commit against the pin that governs that attempt.

BETA attempt 1 of the second seal (`v5-b5-beta-a1-20261010T0742Z`, `harvest.json` SHA-256
`f0d72323b67d075db29a5c136d087222284a6d4651d130549f9dbd5a82d6ec7d`) stays collected and not claim-usable
(`neg8.screen_failed`), kept and disclosed, its energies never analysed.

The release event ties Erratum 2's SHA-256 beside those of the registration, the analysis plan and the catalog.

### Step 2, written 2026-10-10 before any governed attempt was armed or harvested (by a seat that has read no claim-window energy)

B5-HARVEST-PIN: 0699abbb0881ce64b39c46ba07de568cc3848260

This pin governs only attempts governed by Erratum 2 (plan `t0_epoch_s` later than 1791649800). Addendum 2's pin
`224a264c5faaae90cdf56118df37e773a932700b` remains the pin of every other attempt of the second seal.

Desk clone: /Users/edr/night-custody/desk/b5-harvest. Files at that commit, with their SHA-256:
joulewise/b5/harvest.py 96edd7ec6d57102060bef28c61561597d1c8144c412f6eb99d7d6d4cd0e9d463; joulewise/whole_window.py 2e03abc8b90088401df9fd86b511dcb783e4a67913e49ac441e326caa603b86b; scripts/harvest_b5_window.py 88ac1164e729691e4db249b77ebbd17072dbcd3f514499840a56f56576d66d45.
The lane: lane/2026-10-10-harvest-screen-sources, cut from the second pin 224a264c5faaae90cdf56118df37e773a932700b, so
it descends from the second seal's claim head c27485347c9629b857df81665b5b1b8d10dcd36a. git diff --name-only
224a264c5 0699abbb0 lists only the first two of those files and paths under tests/; the third file is unchanged
from both earlier pins.

What changed in the harvest program: items 0 to 8 of Erratum 2 and its admission-time gate. When the stored
verdict records no source list, the attempt is governed, and the diagnosed state of item 0 holds, the harvest
takes the window's reference list from the authenticated campaign catalog, applies the loss rules, requires the
clean bound and every surviving reference's membership in the verdict's evaluation basis and in the sealed
roster, and lets the registered evaluator decide on the survivors. A verdict that records sources is handled
byte for byte as under 224a264c5. Item 9 (the claim consumer) is lane L9-NEG8's, before any claim is computed.

Its gates: docs/process_traces/2026-10-block5/sources-erratum/harvest-pin3-gates.md (the builder in two rounds;
a cold Fable 5.1 pass, last line PASS; an independent executing review, approve with test fixes, all made; the
whole suite on the lane's tree; the before/after comparison on the real rehearsal copy, executed and passing).

Like the earlier harvest lanes, this lane is not merged into main; the branch is kept on the remote.

## Addendum 4: Erratum 3 of block 5, and the harvest program for the attempts it governs

### Step 1, written 2026-10-11 before the arm of any attempt Erratum 3 governs (by a seat that has read no claim-window energy)

Erratum 3 (prospective): `docs/process_traces/2026-10-block5/trigger-erratum/ERRATUM.md`, SHA-256 of the admitted
text as committed on main `71deca18d8fbae283afe15dca4f5f36850c22f303077a859800e142577b3ac89`. It was admitted with
corrections by a cold gate under registration section 10: the ruling is `RULING.md` beside it (a Fable 5.1 judge,
SHA-256 `becbf587bb84a61954060a19dc54f78517c088c8710e514d73bb31af0cdea260`, last line
`RULING: ADMIT-WITH-CORRECTIONS`), the refutation `REFUTATION.md` (an Opus 5.5 refuter). What it changes, for
governed attempts only: at the harvest's evaluation of a window's calibration bracket (the comparison of the
window's opening and closing calibration captures with the calibration acceptance), three events elsewhere in
the calibration ledger are recorded and no longer fail the bracket: a capture of another session classed
`systematic-invalid`, a valid capture outside the range of the acceptance's 24 captures (the window's own
included), and the count of valid captures reaching 48. Every comparison of the window's own two captures with
the screen and the drift ceiling, and the identity, byte, binding, ledger integrity and custody checks, stay as
sealed. It also admits, as rules to be built in analysis lane L9-BRACKET before the release event, how claim
consumers evaluate each window's bracket over that window's archived ledger copy (item 10) and a sensitivity
bound printed for every analysed window of the block (item 14); a lead's rule for a repeated systematic capture
and a pre-arm run (item 13); and a retention rule for capture directories. No threshold, flag code, roster,
blinding rule or window input changes. The acceptance file's bytes, the registration's bytes and the seal are
not changed.

ERRATUM-3-ADMITTED-AT: 2026-10-11T17:00:00Z

Pin scoping. An attempt is governed by Erratum 3 when its plan's `t0_epoch_s` is later than
`ERRATUM-3-ADMITTED-AT` (epoch 1791738000). Three pins stand. Addendum 2's pin
`224a264c5faaae90cdf56118df37e773a932700b` for attempts with t0 at or before `ERRATUM-2-ADMITTED-AT` (epoch
1791649800). Addendum 3's pin `0699abbb0881ce64b39c46ba07de568cc3848260` for attempts with t0 after that and at
or before `ERRATUM-3-ADMITTED-AT` (BETA attempts 2 to 5). The pin of step 2 below for governed attempts. No
attempt that is not governed is harvested by the new program for a deciding record; before the release event
the only run of the new program over such an attempt is the one item 12 of the erratum allows (the bracket
evaluation alone, labelled exploratory, printing status words, reason codes and trigger names), and it changes
no verdict, `claim_usable`, cause key or attempt history. The analysis checks each attempt's recorded harvest
commit against the pin that governs that attempt.

Pin before arm. No governed attempt is armed until step 2 of this addendum is on main. If the gates on the
implementing program find that the admitted text cannot be implemented exactly, a corrected erratum is admitted
under registration section 10 before any governed attempt is armed.

Registration section 11 item 4, amended for this lane only. The harvest lane of Erratum 3 may also change
`joulewise/calibration_bracketing.py`, in the desk checkout only, and only as section 4 item 1 of the erratum
describes: one keyword argument `trigger_scope` on `evaluate_calibration_bracket` and
`calibration_bracket_for_bundles`, whose default value `"sealed"` returns exactly what the pinned program
`0699abbb0` returns. The change is never committed, merged, pulled or checked out in the measurement clone.

BETA attempts 4 and 5 of the second seal (`v5-b5-beta-a4-20261010T2237Z`, `harvest.json` SHA-256
`b4aa474b1ebc4eefc0a8b5f4b9d6975544578113583d0da10fa410a9f139d5b6`; `v5-b5-beta-a5-20261011T0739Z`,
`harvest.json` SHA-256 `8e69f3ef88b932a4b5e0f6a56816e2c1e45d5a64d19595bebf88c02f9a76170d`) stay collected and
not claim-usable (`calibration.bracket_acceptance_failed`), kept and disclosed, their energies never analysed.

The release event ties Erratum 3's SHA-256 beside those of the registration, the analysis plan, the catalog and
Erratum 2.

### Step 2, written 2026-10-11 before any governed attempt was armed or harvested (by a seat that has read no claim-window energy)

B5-HARVEST-PIN: b039c0257d1b1d407ee9598222db3f78f6ad7beb

This pin governs only attempts governed by Erratum 3 (plan `t0_epoch_s` later than 1791738000). Addendum 3's pin
`0699abbb0881ce64b39c46ba07de568cc3848260` remains the pin of attempts with t0 after 1791649800 and at or before
1791738000, and Addendum 2's pin `224a264c5faaae90cdf56118df37e773a932700b` of every earlier attempt of the second
seal.

Desk clone: /Users/edr/night-custody/desk/b5-harvest. Files at that commit, with their SHA-256:
joulewise/b5/harvest.py 68d219478edb3d40a1d1a0a4cfd2fb7100421f09b5c8e681ec48c6acab0c73af; joulewise/calibration_bracketing.py 5474902deb5c3b834bffe11da6698f40216ba978248a8457f09db0077eaaf3ff; joulewise/whole_window.py 2e03abc8b90088401df9fd86b511dcb783e4a67913e49ac441e326caa603b86b; scripts/harvest_b5_window.py 88ac1164e729691e4db249b77ebbd17072dbcd3f514499840a56f56576d66d45.
The lane: lane/2026-10-11-harvest-trigger-scope, cut from the third pin 0699abbb0881ce64b39c46ba07de568cc3848260, so
it descends from the second seal's claim head c27485347c9629b857df81665b5b1b8d10dcd36a. git diff --name-only
0699abbb0 b039c0257 lists only the first two of those files and paths under tests/; the last two files are
unchanged from the third pin.

What changed in the harvest program: items 0 to 8 of Erratum 3. The bracket evaluation
(`evaluate_calibration_bracket`, `calibration_bracket_for_bundles`) takes the argument `trigger_scope`; the
harvest passes `"window_evidence"` when and only when the attempt is governed; under it a systematic capture of
another session, a valid capture outside the range of the acceptance's 24 and the count of valid captures
reaching 48 are recorded and do not fail the bracket, and every other check is as sealed. With the argument
omitted or `"sealed"` both functions return what they return at 0699abbb0. `harvest.json` gains the object
`calibration_bracket` and the digest of `withheld/bracket-evaluation.json`, and the recorded program file list
gains `joulewise/calibration_bracketing.py`. Items 10 and 14 (claim consumers; the sensitivity bound) are lane
L9-BRACKET's, before any claim is computed.

Its gates: docs/process_traces/2026-10-block5/trigger-erratum/harvest-pin4-gates.md (the builder; a cold Fable
5.1 pass, last line PASS; an independent executing review, approve with test fixes, all made; the whole suite
on the lane's tree; the before/after comparison on the real rehearsal copy, executed and byte-identical; the
limited exploratory run of the erratum's item 12 over BETA attempt 5's archived ledger copy). One gate is owed
before a governed GAMMA attempt is armed and does not hold BETA: the sealed verdict writer and the real
provenance checker run over a GAMMA-shaped rehearsal window whose ledger holds a systematic capture of another
session (finding F3 of the cold pass).

Like the earlier harvest lanes, this lane is not merged into main; the branch is kept on the remote.

## Release event

Nothing is recorded here yet. This section is written when the withheld energies are opened: after the block has
closed, and after the analysis has been run end to end on the real bytes with every output kept closed (the blind
dry run of the analysis plan's section 3.2). It will tie the digests of section 4 to the final harvest records.

## Addendum 5: F7 meter cross-check by a resolved PDTR-on-meter slope (2026-10-22)

Appended by the lead (Opus 5.5, interactive session 8a9fb7fe) under the §12 convention: addenda are appended to this seal record. Drafted by the Sol 6.1 seat FIX-565; the lead changed the `slope_undetermined` criterion after the real-stream replay and re-ran the replay.

Authority: the seven binding lead rulings in
`/Users/edr/night-archive/forward-20261021/coldpass-audit/FIX-565.md`, addressing
F7 in `/Users/edr/night-archive/forward-20261021/audit/REPORT.md:255-272` and the
Fable and Opus cold reports beside the assignment. This changes only the meter
agreement diagnostic. Its effect stays DISCLOSE. It changes no energy estimator,
printed outcome, exclusion rule, or rule deciding which data count. Historical
block-5 captures and deciding harvests retain their original pins.

### Definition and sealed text

The superseded definition in
`configs/campaigns/v5_claim_25g83/registration_block5.md:3560` is:

> the median over 1 s bins of mean PDTR ÷ mean meter power is outside 0.95–1.02, or cannot be computed

The sealed registration, `configs/campaigns/v5_claim_25g83/flag_catalog.json`, and
`tests/fixtures/b5_harvest/flag_catalog.json` remain byte-for-byte unchanged.

For this correction, `meter.pdtr_gain_out_of_band` fires when the ordinary-least-squares
slope of mean PDTR on mean meter power, with a free intercept over paired 20 s bins,
is outside the inclusive band **[0.951364, 0.984889]**, or gain is unconfirmed.
Each paired bin has a PDTR reading and more than half its nominal meter samples;
this is the capture-C2 majority rule, scaled by the device sample period. The strict
majority gives a retained bin more observed than missing nominal samples and prevents
a sparse final bin from receiving full-bin weight. The intercept absorbs the fixed
sensor offset that invalidated the idle-dominated median ratio.

The record now carries `r`, `sxx` (W²), `meter_power_range_W` (the minimum and maximum
paired bin-mean meter powers), and `slope_se`. For n paired bins,
`SE(slope) = sqrt(SSE / (n - 2) / sxx)`, with residuals from the fitted intercept
and slope. Its two-sided 95 % half-width is `t(0.975, n - 2) × SE` (Student t; the record carries it
as `slope_half_width_95`). The cross-check exists to see a meter gain fault of 5 % (`PDTR_FAULT_FRACTION`,
audit F7). Such a fault moves a healthy slope c to c/1.05 or c/0.95, and the flag fires only once that
lands outside the band, so the fit must resolve the fault's distance beyond the band edge: with c the
band centre (0.968), d = min(0.951364 − c/1.05, c/0.95 − 0.984889) ≈ 0.029. When the 95 % half-width is
not below d, the stream cannot tell a healthy meter from a faulted one: the reason is `slope_undetermined`,
and the flag discloses unconfirmed agreement even when the fitted slope lies inside the band. The distance
is taken at the band centre, not at the observed slope, because an idle-dominated stream's slope is biased
by meter noise and cannot vouch for itself. What this buys, measured on synthetic streams (cold Opus delta re-check,
2026-10-23, i.i.d. Gaussian bin noise, n = 3..40): with the healthy slope at the band centre a ±5 % fault reads
clear in at most 2.5 % of streams per direction (observed 0.2–1.2 %); at the measured healthy extremes and at the
2 s-lag slope 0.9534 the distance to the nearer edge is smaller (0.019–0.021), and a fault in that direction reads
clear in up to about 4–6 % of streams. The flag is DISCLOSE either way. Using the worst-case distance (0.0134) would
remove that gap at the cost of marking more short healthy streams undetermined; the lead kept the centre distance. (History of this bar: the seat first compared 2 SE with the
band half-width, which marked 11 healthy short smokes; the lead then compared 2 SE with the raw 5 % shift;
a cold Fable delta check showed that bar let a faulted 4-bin stream read clear and that 2 SE under-covers
at few bins, so the final bar is the t half-width against the distance beyond the band.) Two bins
leave zero residual degrees of freedom, so also give `slope_undetermined`. The fitted
slope remains in the diagnostic record. Exact `sxx == 0` is only a division guard;
near-constant power is judged by slope uncertainty. Other unavailable/nonfinite
conditions remain unconfirmed DISCLOSE flags. A nonpositive caller-supplied bin
duration remains an internal programming error, now registered as INTERNAL in the
hazard refusal allowlist; stream data never select it.

The descriptive median is now named `median_ratio_20s` to distinguish it from the
old 1 s field. It includes only positive-meter-power bins, where the ratio is
defined; the arbitrary 1 W floor and `PDTR_MIN_W` were removed. It decides no flag.

### Derivation and pin

Recomputed from the twelve whole-session meter hazard streams named by audit
`capture/verify-capture-C2/blind_slope.py`, without rounding the slopes before
aggregation: mean **0.9681264838730295**, sample SD **0.0033525440726185764** (n − 1),
minimum **0.9629625068075808**, maximum **0.9740307606199866**.
Mean ± 5 SD is [0.9513637635099366, 0.9848892042361224]; the implemented endpoints
round to six decimal places, changing each by less than 1e-6 relative. The band is
an engineering margin, not a confidence interval. The registration's 0.955 probe
is 0.003636 above its lower edge; the cold Opus replay's lagged probe slope 0.95437
also has margin. A ±5% meter gain error still moves the observed extremes outside:
0.9740307606199866 / 1.05 = 0.9276483434476063 below the band, and
0.9629625068075808 / 0.95 = 1.0136447440079799 above it. The cold Opus synthetic
replay gave 0.9674 at a 1 s PDTR refresh lag and 0.9534 at 2 s, a shape-dependent
shift of about −0.014 slope per extra second; added lag can still disclose.

File to pin: `joulewise/external/km003c_parse.py`, SHA-256 `7d51ed8ebdfad76fdd58f6dd9df90d118576153ce22619ab62a35b512f4f7cbf`, in the commit that appends this addendum (branch `fix/2026-10-22-audit-f7-meter`, PR #565).

### Verification and replay

`PYTHONDONTWRITEBYTECODE=1 JW_B5_SYNTHETIC_ONLY=1 python3 -B -m unittest tests.external.test_km003c_parse tests.test_harvest_b5_p3harv tests.hazards.test_refusal_allowlist tests.external.test_km003c_monitor`
passed 127 tests at the pinned commit with three environmental skips (CommonCrypto is macOS-only; the real-meter smoke is barred by JW_B5_SYNTHETIC_ONLY; one design-branch test): test_km003c_parse 43, test_refusal_allowlist 23, test_harvest_b5_p3harv 48, test_km003c_monitor 13. These are all three test modules importing
`km003c_parse`, plus the required hazard allowlist gate. The whole suite was not run,
as the assignment explicitly forbids it. The baseline failed only the unlisted
bin-duration guard; the updated gate passes. The rewritten gain-band test, replayed
against the pre-F7 parser at c21c52dfa, gives exactly one expected failure at scale
0.98, proving the revised idle-dominated fixture discriminates the correction.

The replay reads only complete session/smoke meter hazard records. Compressed inputs
are decompressed in memory; custody files are never written. Every stream source
directory named by the audit meter census contains exactly one stream file. The
census names **27 streams**, two more than F7's stated 25-stream target; all 27 were
replayed. Under the final rule **0 of 27** healthy real streams fire (each 95 % half-width is below the
~0.029 distance), and both ±5% meter-gain counterfactuals disclose on **27/27** streams (one −5 % case as
`slope_undetermined`, the rest out of band), always DISCLOSE. The slope and r agree with an independent
copy of the audit formula within COMMON's 1e-6 relative fallback bar.

The script and per-stream outputs are kept off the repository at
`/Users/edr/night-archive/forward-20261021/coldpass-audit/replay-565/` (`replay.py`, `calibration.jsonl`,
`replay.jsonl` for the seat's run, `replay-lead.jsonl` for the final rule).
The following table prints slope and r rounded to six decimal places for display;
all replay assertions and aggregate calculations used full precision. Correlation
is unchanged by a positive gain scaling, apart from float rounding. Both
counterfactual verdict columns are DISCLOSE for every row.

| Stream | Real slope | r | Real verdict | −5% slope | +5% slope |
|---|---:|---:|---|---:|---:|
| b5-alpha-a1 | 0.970861 | 0.996176 | clear | 1.021959 | 0.924630 |
| b5-beta-a6 | 0.965836 | 0.994331 | clear | 1.016670 | 0.919844 |
| b5-gamma-a1 | 0.968834 | 0.995771 | clear | 1.019825 | 0.922699 |
| b6-r1-alpha | 0.970518 | 0.994984 | clear | 1.021598 | 0.924303 |
| b6-r1-beta | 0.965673 | 0.994943 | clear | 1.016498 | 0.919689 |
| b6-r1-gamma | 0.970666 | 0.994194 | clear | 1.021754 | 0.924444 |
| b6-r2-beta | 0.962963 | 0.994182 | clear | 1.013645 | 0.917107 |
| b6-r2-gamma | 0.974031 | 0.994935 | clear | 1.025296 | 0.927648 |
| b6-r3-alpha | 0.970147 | 0.993449 | clear | 1.021208 | 0.923950 |
| b6-r3-beta | 0.964824 | 0.994363 | clear | 1.015604 | 0.918880 |
| b6-r3-gamma | 0.964244 | 0.994501 | clear | 1.014994 | 0.918328 |
| b6-r4-alpha | 0.968921 | 0.994184 | clear | 1.019916 | 0.922782 |
| rehearsal-1949Z | 0.969942 | 0.995314 | clear | 1.020991 | 0.923754 |
| smoke-r1-alpha | 0.967188 | 0.993458 | clear | 1.018093 | 0.921132 |
| smoke-r1-beta | 0.970668 | 0.997225 | clear | 1.021756 | 0.924446 |
| smoke-r1-gamma | 0.967795 | 0.994354 | clear | 1.018732 | 0.921710 |
| smoke-r2-alpha | 0.964875 | 0.993994 | clear | 1.015658 | 0.918929 |
| smoke-r2-beta | 0.975080 | 0.996955 | clear | 1.026400 | 0.928648 |
| smoke-r2-gamma | 0.970760 | 0.994594 | clear | 1.021853 | 0.924533 |
| smoke-r3-alpha | 0.966029 | 0.995046 | clear | 1.016872 | 0.920027 |
| smoke-r3-beta | 0.976939 | 0.996514 | clear | 1.028357 | 0.930418 |
| smoke-r3-gamma | 0.962936 | 0.994835 | clear | 1.013617 | 0.917082 |
| smoke-r4-alpha | 0.963394 | 0.995451 | clear | 1.014099 | 0.917518 |
| MT-20261016T2114Z | 0.965430 | 0.997488 | clear | 1.016242 | 0.919457 |
| MT-20261017T1735Z | 0.965767 | 0.995379 | clear | 1.016596 | 0.919778 |
| MT-20261017T2215Z | 0.967264 | 0.996421 | clear | 1.018173 | 0.921204 |
| open:bytes-h | 0.973831 | 0.998549 | clear | 1.025085 | 0.927458 |

### Decisions I made

- Used the sample SD (n − 1), as the audit's `statistics.stdev` source specifies.
- Rounded the final band to six decimals after full-precision aggregation, within
  the 1e-6 relative fallback agreement bar, and kept the unrounded derivation.
- Retained an uncertain fitted slope for diagnosis and explicitly made the flag
  honor `slope_undetermined`; treated n = 2 as unresolved because SE has no degrees
  of freedom, without introducing any additional spread threshold.
- Removed the descriptive ratio's 1 W floor, retaining only its positive-power
  domain guard; it changes no decision.
- Replayed all 27 streams named by the audit census and reported the count
  difference explicitly rather than silently dropping two streams.

### Open issues

1. The block-6 review-ledger row belongs on the b6 lane, not main: it must record this parser digest
   and the F7 definition there.
