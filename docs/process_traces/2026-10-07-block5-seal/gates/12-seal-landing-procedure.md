# Where the block-5 seal lands: commits, documents, checks

Lane SEAL-LAND, 2026-10-07. Written by the lane agent (Opus 5.5) for the orchestrator and for the writer of
registration sections 2, 11 and 12. Code citations are `file:line` at the lane head `2737ef88c`
(branch `lane/2026-10-07-seal-landing`, base int5 `9b0c680ed`).

## 1. The problem this procedure solves

Two facts about git and one fact about the installer force the shape of the landing.

**Fact 1. A file cannot name the commit that contains it.** A commit's name is a hash computed over its content. If a
file inside the commit held that name, changing the file to write the name would change the hash. The sealed
inventory (`configs/campaigns/v5_claim_25g83/sealed_inventory.json`) names, in its `head` field, the commit whose
file bytes it lists. So the filled inventory can only be committed in a later commit than the one it names. The same
holds for any registration sentence that prints that commit's name.

**Fact 2. The harvest compares the head a window ran from with the inventory's `head`, path by path.** A window is
one unattended measurement run of one pack. At its start the driver records the name of the commit the measurement
checkout was at (the *executed head*) and the SHA-256 of every tracked file under `joulewise/`, `scripts/` and the
window's pack (the *executed inventory*). The harvest, the program that turns a finished window's bytes into numbers
and flags, later runs `git diff --name-only <inventory head>..<executed head>` (`joulewise/b5/harvest.py:5736`). Before
this lane, every listed path except the ledger pin was a difference, and a difference is the flag
`code.executed_differs_from_sealed`, whose catalog effect removes the whole window from every claim
(`EXCLUDE_WINDOW`). By fact 1 the executed head always differs from the inventory's `head` by at least the
inventory file itself. So every block-5 window would have been excluded because the seal landed.

**Fact 3. A plan cannot carry the comparison instead.** Each window has a plan file with a `measurement_head` field.
The installer of the launch agents refuses unless that field equals the measurement checkout's HEAD at install
(`joulewise/night_agent_install.py:1235-1242`, which runs before the block-5 branch at `:1276`). The driver passes the
plan's `measurement_head` to the arm-time collector as `--h-claim` (`joulewise/b5/driver.py:712`), so at the arm the
collector compares HEAD with itself. If the inventory's `head` were null, the harvest would fall back to the same
plan field (`harvest.py:1513`, `:5658`) and would also compare the executed head with itself. The only comparison that
ties a window to the seal is the harvest's, and it needs a non-null `head` in the sealed inventory. This rules out the
shape the 2026-10-06 rehearsal used (`scripts/rehearse_b5_real.py:285-341`: one commit holding code, documents and an
inventory with `head` null).

## 2. Terms

- **Window input.** A tracked file whose bytes a window can read while it is planned, armed or run: every file under
  `joulewise/` and `scripts/` (code), every file under `configs/` (the packs, the files a pack's plan tree pins, the
  flag catalog, the identity pins, the sizing output, policies, calibration artifacts), and one document,
  `docs/phase_2/window_runbook.md`, because the plan writer copies its pre-calibration screen into the chain
  (`joulewise/b5/plan.py:854`, `joulewise/b5/chain.py:110`). The chain is the shell script a window executes.
- **H_claim.** The last commit that changes any window input before the block's first window. Called C below.
- **Seal documents.** Three files in `configs/campaigns/v5_claim_25g83/`: `sealed_inventory.json`,
  `registration_block5.md`, `analysis_plan_block5.md`. They are under `configs/` but are not window inputs in the
  sense above for the head comparison: their final bytes cannot exist at C (fact 1), and their SHA-256s are pinned by
  the seal record. (The registration is read by the harvest for its thresholds; section 7 says what protects that.)
- **Seal commit.** The single commit, child of C, that changes only seal documents. Called S below.
- **Seal record.** A document under `docs/` that lists the SHA-256 of every sealed file, C, S and the gate's records.
  Nothing lists the seal record's own hash, so no file has to contain its own hash.
- **Pin-only commit.** A commit that changes only `configs/calibration/calibration_ledger_head.json`, the calibration
  ledger pin. The pin is data that advances after each window, not code.
- **Record-only path.** Any tracked path that is not a window input, not a seal document and not the pin: other
  documents, tests, `RUN_STATE.md`, `TASK_QUEUE.md`, and files outside those three top-level directories.
- **Measurement clone.** The dedicated git clone the windows run from.

## 3. The picture

```
main      ... ── 7cd23b914 ──────────────────────────────────────────── M
                      \                                                 /
int5                   ... ── C ─────────── S ─────────── R ───────────
                              │             │             │
                              │             │             └─ R: adds the seal record under docs/ (record-only paths)
                              │             └─ S: the seal commit; changes only the three seal documents
                              └─ C = H_claim: the last commit that changes a window input

measurement clone      ... ── C ── S ── p1 ── p2
                                   ▲     ▲     ▲
                                   │     │     └─ p2: pin-only commit after BETA-1; HEAD when GAMMA-1's plan is written
                                   │     └─ p1: pin-only commit after ALPHA-1; HEAD when BETA-1's plan is written
                                   └─ S: the clone is checked out here; HEAD when ALPHA-1's plan is written
```

Every element: `7cd23b914` is today's `origin/main`, an ancestor of int5. C, S, R are consecutive commits on the
integration branch. M is the merge commit GitHub creates for the seal pull request; its tree equals R's tree while
main has not moved. `p1`, `p2` exist only in the clone until they are pushed. Each window's harvest compares the head
that window ran from (S, p1, p2, ...) with C.

## 4. The procedure, as an ordered list of commits

Each step gives the paths it may touch, what is computed from what, and the check that proves it.

**Step 0. The seal cold gate judges candidates.** Inputs: the registration, analysis plan and flag catalog on the
design branch; a candidate inventory generated from the candidate code head. If the gate requires a change that
touches a window input (code, a pack, the catalog, the identity pins, the sizing output, the runbook), that change
lands before C and the candidate is regenerated. Text-only changes to the registration or analysis plan land in S.

**Step 1. C, the last code commit (H_claim).**
- Tree at C: final code, final packs, final `flag_catalog.json`, `identity_pins.json`, `sizing_b5.json` and
  `docs/phase_2/window_runbook.md`. The registration and analysis plan are the judged text, still marked DRAFT and
  still holding the seal-time `FILL` tokens. `sealed_inventory.json` is the stub (`status` `STUB_NOT_SEALED`, `head`
  null, `files` null).
- Checks: the whole suite on C; the refusal census; the generators' `--check`; CI. `tests.test_b5_seal_landing`
  passes in the stub state.

**Step 2. Generate the inventory from C.** On a clean checkout of C:
`/opt/homebrew/bin/python3.13 -B /Users/edr/night-archive/gate-prune/wave-1007b/seal-land/make_sealed_inventory.py <checkout> <out.json>`.
It refuses a checkout that is not clean, then uses the repository's own generator
(`scripts/rehearse_b5_real.py:285`): `git ls-files` under `joulewise/`, `scripts/` and the three pack directories, the
SHA-256 of each file, plus `flag_catalog.json`. It writes `status` `SEALED`, `head` = C and `files`. No `roots` key.
The ledger pin is not listed.

**Step 3. Write the final document text.** In the registration: the status line, C printed as H_claim, the seal seats,
and the path of the seal record (the path, not a hash). Nothing in the registration may be left to fill after S
(section 7, rule 4). The analysis plan is read by no program; a value filled into it after S changes its SHA-256,
so either the value goes into the seal record instead, or the seal record gains an addendum with the new digest.

**Step 4. S, the seal commit.** One commit whose only parent is C.
- Paths: `sealed_inventory.json` (always), `registration_block5.md`, `analysis_plan_block5.md`. Nothing else.
- Checks, all mechanical:
  1. `git diff --name-only --no-renames C S` lists only those paths.
  2. `python -m unittest tests.test_b5_seal_landing` passes. It reads git objects, not the working tree, and proves:
     the inventory's `head` is a commit; the last commit that changed the inventory has that commit as its only
     parent; that commit changes only seal documents; the inventory lists exactly the tracked files of `head` under
     the sealed roots plus the catalog, each with the SHA-256 of its bytes at `head`.
  3. Running step 2's generator on a clean checkout of S gives the same `files` map (the generator reads the working
     tree; check 2 reads git objects; two independent readings).

**Step 5. R, the seal record commit.** Child of S.
- Paths: only record-only paths. The seal record, by the precedent of blocks 2 and 3, is
  `docs/process_traces/<seal session>/52-seal-record.md`, beside the gate's ruling and the refuter's record.
- Content: C; S; the SHA-256 at S of the four sealed documents (inventory, registration, analysis plan, catalog);
  the SHA-256 at C of the three plan trees, `identity_pins.json`, `sizing_b5.json`, `docs/phase_2/window_runbook.md`,
  the panel, the policy, the acceptance and the pin bundle; the seats; and, appended later, every value that is
  only known after S (section 7, rule 4).
- Check: `git diff --name-only --no-renames S R` lists no path under `joulewise/`, `scripts/` or `configs/`, and not
  `docs/phase_2/window_runbook.md`.

**Step 6. The pull request to main.** CI green on the final head. The pull request is merged with a merge commit
(`gh pr merge --merge`), never squashed or rebased: a squash would replace C and S by one new commit, C would not be
in main's history, and both the landing test and the harvest's `git diff` need C. The merge commit M has R's tree
while main has not moved (`git diff --name-only R M` is empty).

**Step 7. The measurement clone.** A full clone (no `--depth`: the harvest's `git diff` needs C), checked out
detached at S. Any descendant of S that differs from it only in record-only paths (R, M) is accepted by the code
too; S is recommended because `git diff --name-only C HEAD` then lists exactly the seal documents.
- Checks: `git -C <clone> diff --name-only --no-renames C HEAD`; `git -C <clone> status --porcelain` empty; the desk
  collectors raise no `code.*` flag:
  `scripts/collect_window_flags.py --stage desk --h-claim C --sealed-inventory <clone>/configs/campaigns/v5_claim_25g83/sealed_inventory.json --collector checkout_identity --collector executed_code ...`.

**Step 8. Plans and launch agents.** Each plan's `measurement_head` and `repo_head` are the clone's HEAD when the plan
is written (S for the first window, then the latest pin-only commit). The plan inputs carry two digests that are
copied from the seal record, not computed from the clone: the registration's SHA-256 and the sizing output's
SHA-256. The plan writer refuses when the clone's file does not hash to the digest it is given
(`joulewise/b5/plan.py:298`), so copying them from the seal record makes the plan writer check those two files
against the seal. The launch agents are installed by the clone's own `scripts/install_night_agent.sh`, so the driver,
the hazard modules, the monitor and the collectors are the clone's files (section 7, rule 2).

**Step 9. Between windows.** Chain exit, pin advance (`scripts/advance_b5_ledger_pin.py`: a pin-only commit in the
clone; it refuses a commit that changes anything else, `joulewise/b5/plan.py:721`), harvest. Nothing else is ever
committed, merged, pulled or checked out in the clone.

## 5. Answers to the brief's five questions

1. **Which commit is H_claim?** C, the parent of the seal commit: the last commit that changes a window input.
2. **What state do the three documents and the stub have at H_claim?** The registration and analysis plan are the
   judged text, marked DRAFT, with seal-time FILL tokens open. The inventory is the stub. The flag catalog is final
   at H_claim (it is listed in the inventory).
3. **Which commit carries the filled inventory and the final document text?** S, the seal commit, the child of
   H_claim. It changes those three files and nothing else.
4. **Where does the seal record live?** Under `docs/process_traces/<seal session>/`, committed in R, after S. It
   holds every hash; no file holds its hash. The registration names its path.
5. **Which head is the measurement clone at?** S, detached, in a full clone. Pin-only commits follow in the clone.

## 6. What the code does with each kind of later commit

The harvest (`harvest.py:5597`, `code_identity`) and the arm-time collector
(`joulewise/flags/collect.py:558`, `collect_checkout_identity`) put every path that differs between H_claim and the
head in one class (`head_change_class`, `harvest.py:184`, `collect.py:543`; a test keeps the two identical).

| Class | Paths | Head comparison | Per-file inventory comparison | Catalog effect |
|---|---|---|---|---|
| `pin_only` | the ledger pin | listed, no flag | not listed in the inventory | none |
| `seal_document` | the three seal documents | listed, no flag | not listed in the inventory | none |
| `record_only` | everything not below | listed, no flag | not in the executed roots | none |
| `window_input` | `joulewise/`, `scripts/`, `configs/` (except the two rows above), `docs/phase_2/window_runbook.md` | `code.executed_differs_from_sealed` | also flagged when the file is under `joulewise/`, `scripts/` or the window's pack | `EXCLUDE_WINDOW` |

Before this lane every row except `pin_only` was `EXCLUDE_WINDOW`. The harvest writes the comparison to
`derived/code-identity.json` (schema `joulewise.b5_code_identity.v1`): H_claim and where it came from
(`sealed_inventory` or `plan`), the plan's `measurement_head`, the executed head, the SHA-256 of the sealed
inventory it read, the changed paths by class, and `driver_checkout` (section 7, rule 2). The collector lists the
changed paths in its run record. If `git diff` cannot run, the window is `code.identity_unmeasured`, as before. A
path is classed as a window input without regard to letter case, because the measurement Mac's volume does not
distinguish case; the pin and the seal documents match by exact name.

The four extension classes of registration section 11 item 1, for a window armed from a clone that holds such a
commit:

- **(i) pin-only commits.** No flag. Unchanged.
- **(ii) gated fixes to code that does not run during collection** (the harvest, extraction, mint, analysis). These
  files are under `joulewise/` and `scripts/`, and the driver inventories every tracked file there, executed or not.
  If the clone holds such a commit at an arm, the arm collector's per-file check, the harvest's per-file check and
  the head comparison all flag it, and the window is excluded. The code cannot tell "does not run during
  collection" from "runs". So class (ii) is permitted on main and forbidden in the clone. It never needs to be in
  the clone: `scripts/harvest_b5_window.py` imports the harvest from its own checkout (`:29-33`) and reads the pack,
  ledger, pin, sealed inventory, catalog, identity pins and registration from the plan's `measurement_root`
  (`harvest.py:1465-1525`, `resolve_inputs`). One part of the harvest does run the clone's code: with `--prepare-desk`, the
  whole-window verdict is written by `<clone>/scripts/run_campaign.py --whole-window-verdict` under the clone's
  interpreter (`harvest.py:5159`, `start_desk_verdict`), so that writer is always the sealed one.
- **(iii) commits touching only `docs/`, `tests/`, `RUN_STATE.md`, `TASK_QUEUE.md`.** No flag now, recorded. One
  exception: `docs/phase_2/window_runbook.md` is a window input and is flagged.
- **(iv) a section 7.5 cure to collection code.** Any cured file is a window input, so every window armed after the
  cure is flagged against the old inventory, by the head comparison and (inside the window's roots) by the per-file
  check. A cure therefore re-issues the seal: the cure commit becomes a new C′, and a new seal commit S′ = C′ plus a
  re-generated inventory whose `head` is C′, under the erratum section 7.5 already requires. A re-harvest of a
  window completed before the cure must be given the inventory that was in force at its arm
  (`--sealed-inventory-path <first harvest archive>/sources/inputs/sealed_inventory.json`).

Section 11 item 4 says the harvest and analysis programs are pinned by addenda to the seal record. No code reads
such an addendum, and the harvest does not record the commit or the digests of its own program. The binding is
procedural.

## 7. What the code does not check, and the rule that covers it

1. **The seal documents' own bytes.** The head comparison lists them and judges nothing by them. The harvest records
   what it read: the registration's SHA-256 in `derived/harvest-thresholds.json` (and it faults if the registration
   differs from the digest the plan recorded, `harvest.py:1414`), the catalog's in `derived/window_flags.json`, the
   inventory's in `derived/code-identity.json`. Rule: the analysis admits a window only when those three digests
   equal the seal record's.
2. **The checkout the driver runs from.** The launch agent runs `<installer's checkout>/scripts/run_night.py`, and the
   driver, hazard modules, monitor and collectors are that checkout's files (`scripts/run_night.py:3964`,
   `driver.py:676`). When that checkout is not the measurement clone the driver records its files under
   `driver_checkout` (`driver.py:1833`), and no code flags a difference between them and the sealed inventory. The
   2026-10-06 real-model rehearsal ran this way (driver in `/Users/edr/code/JouleWise-wt-real-reh`, 304 code files,
   none differing). The harvest now writes the block into `derived/code-identity.json` with the list of its code
   files that differ from the sealed inventory (`harvest.py:5722`); the field is null when there was one checkout.
   Rule: install from the clone (block 3's recipe did), so there is one checkout and its files are the executed
   inventory. Whether a differing driver checkout should exclude a window is an open question for the seal gate.
3. **The harvest program's identity** (section 6, last paragraph). Rule: the seal record's addendum names the commit
   and file digests of the harvest checkout before each harvest whose code differs from S.
4. **Values known only after S.** The registration's bytes are fixed at S: each plan records the registration's
   SHA-256 and the harvest faults on a difference, and the seal record pins the same digest. So
   `FILL[B5-PLANS-REGENERATED]`, `FILL[B5-BLIND-CUSTODY-MAP]` and `FILL[B5-RELEASE-EVENT]` cannot be filled in the
   registration. Rule: each is a named section appended to the seal record.
5. **A resized sizing allowance (registration 5.5).** `sizing_b5.json` is a window input; a changed copy committed in
   the clone excludes the next window. The plan writer accepts any file inside the checkout as the allowance's
   source (`plan.py:388-427`). Rule: a resized allowance is written to a new untracked file outside `joulewise/`,
   `scripts/` and the pack (for example under the ignored `runs/` directory), never by editing `sizing_b5.json`.

## 8. Worked example: the procedure run on a disposable clone

`proof-landing.sh` (this directory; log `proof-landing.log`) ran steps 2 to 7 with the real generator and the real
collectors on a clone at `/private/tmp/w1007-seal-land/proof/clone`, with the lane head standing in for C. (An
earlier run with the lane's first commit as C is kept as `proof-landing-at-6f9daa3c3.log`; same results.)

- C = `2737ef88c92754fe20c8417f66dc62edc7d0ae8c`. The inventory generated from it lists 682 files: 150 under
  `joulewise/`, 165 under `scripts/`, 123, 123 and 120 in the three packs, and the catalog. Its SHA-256 was
  `1315cd57017a0257ba433debe0271ba1e22c7a320cecf8531f4fc3195ef9695c`.
- S changed exactly three paths. The inventory regenerated at S had the same `files` map. The git-object checker
  (`tests/test_b5_seal_landing.py` `seal_landing_problems`) returned `('sealed', [])`.
- After a records commit (two paths) and a pin-only commit, the collectors, given `--h-claim C`, raised no flag for
  any of the three packs. Their record: `{'pin_only': 1, 'seal_document': 3, 'window_input': 0, 'record_only': 2}`;
  executed files 438 of 682 sealed for each floor pack (150 + 165 + 123) and 435 for the contrast pack, 0 changed,
  0 missing, 0 added.
- Counterfactuals, each one commit on top: an edit to `joulewise/b5/harvest.py` was flagged by both the per-file and
  the head check; an edit to `docs/phase_2/window_runbook.md` and an edit to `identity_pins.json` were flagged by the
  head check alone; an edit to one file of the contrast pack was flagged by the head check for a floor-pack window
  and by both checks for the contrast-pack window.

The harvest's side is proven in `tests/test_harvest_b5_window.py` `IdentityReplayTests`, including one test that
turns the fixture's measurement checkout into a real repository with C, S and R and runs the real `git diff`.

**The change alters nothing else, checked on real bytes.** The 2026-10-06 real-model rehearsal window (ALPHA pack, 13
members; a rehearsal, not a claim window) was harvested twice into new archive roots, once with the int5 base code
`9b0c680ed` and once with the lane head `2737ef88c` (`run_ab.sh`, `compare_ab.py`, `ab-compare.log` in this
directory). Both: verdict COLLECTED, 186 flags, 13 members assessed. The flags are the same multiset of (code,
scope, observed, expected); `exclusions.json` is equal; 19 of 20 withheld files and 11 of 13 derived files are
byte-identical, and the others differ only in the `emitted` time of each flag and in the archive root's own name.
The one new output is `derived/code-identity.json`. On that window it reads: `comparison` `compared`,
`h_claim_source` `plan` (the rehearsal's inventory has `head` null), one `pin_only` path, and a `driver_checkout`
at `/Users/edr/code/JouleWise-wt-real-reh` with 304 code files, none differing from the sealed inventory.

## 9. Where this departs from the orchestrator's ruling

The ruling's scope for "still caught" was `joulewise/`, `scripts/`, the window's own pack and the flag catalog. The
lane kept that and added the rest of `configs/` and the chain-source runbook, for one reason: for the identity pins,
the sizing output and the runbook, the head comparison is the only code check there is. They are not in the sealed
inventory and not pinned by a plan tree; the seal record pins them, and no code reads the seal record. Dropping them
from the comparison would have removed the one existing check on bytes a window reads.

One consequence differs from the ruling: a change confined to another pack's directory is flagged for a window of a
different pack (last counterfactual above). The lane judged this acceptable because a cure to any sealed file must
re-issue the inventory anyway, which moves `head` and clears the comparison for every pack. If the orchestrator or
the seal gate prefers the ruling's narrower scope, the change is: in both `head_change_class` functions, class a
path under `configs/campaigns/<directory>/` as `record_only` when the directory is neither the window's pack nor
`v5_claim_25g83`; the files a pack reads from other campaign directories (references, spares, the NEG-8 corpus) are
pinned by its plan tree and compared by the pack-identity check. The arm collector would also need the window's
pack, which `scripts/collect_window_flags.py:88` does not pass to `checkout_identity` today (one line).
