# Independent executing review of lane SEAL-LAND

Reviewer: Opus 5.5 review seat (not the author). 2026-10-07, 21:24 to 22:40 PDT.
Reviewed head: `2737ef88c92754fe20c8417f66dc62edc7d0ae8c` (branch `lane/2026-10-07-seal-landing`, base int5 `9b0c680ed`).
The lane worktree was only read (`git -C`); its HEAD and status are unchanged.
Scratch: `/private/tmp/w1007-sealreview/` (a clone of the lane worktree detached at the reviewed head; a clean clone
left there at 16:38 by an earlier review run that the usage pause cut off was verified clean and reused).
Interpreter `/opt/homebrew/bin/python3.13 -B`; `TMPDIR` under `/private/tmp/w1007-sealreview/`.

## Verdict

**DEFECTS: one MAJOR (F1), which the lane itself raised as an open question and which predates the lane.**
Everything the lane was briefed to change behaves as it says: all sixteen changed-window-input counterfactuals
are still excluded, none of the permitted commit kinds excludes, the case rule lets nothing through, the procedure
can be carried out and is internally consistent, the tests pass. F1 needs the orchestrator's ruling and, if the
ruling is "flag it", about six lines before H_claim. F2 and F3 are MINOR and optional; the rest are notes for the
registration writer and the magistrate brief.

| id | severity | class | one line |
|---|---|---|---|
| F1 | MAJOR (pre-existing; lane recorded it and asked the seal gate) | NUMBER_INTEGRITY | A launch agent installed from a checkout other than the measurement clone runs that checkout's driver, hazard modules, monitor and collectors; when those files differ from the sealed inventory no flag is raised, only a record. |
| F2 | MINOR | NUMBER_INTEGRITY | `record_only` is "every path not listed", so a tracked root-level Python module (the repository root is first on `sys.path`), `env/mac-measurement-lock.txt`, `pyproject.toml`, `.gitignore` and `.gitattributes` can change after H_claim with no flag. |
| F3 | MINOR (pre-existing) | NUMBER_INTEGRITY | A sealed inventory that has `files` but no `head` makes the head comparison compare the executed head with itself; the record says `identical`, no flag. |
| F4 | NOTE | PROCEDURE | A second commit to the registration or analysis plan after the seal commit is silent in code and in the landing test; only the seal record's digests bind them. |
| F5 | NOTE | PROCEDURE | After a re-issued seal, a re-harvest of an earlier window is excluded unless it is given the inventory in force at its arm; with the lane's wider scope this also holds for a cure confined to another pack's directory. |
| F6 | NOTE | REPRESENTATION | The harvest's `git diff -z` output is decoded strictly: a changed path that is not UTF-8 is a harvest fault, where the arm collector decodes with replacement. |
| F7 | NOTE | PROCEDURE | Three window inputs carry draft labels at H_claim (`flag_catalog.json`, `identity_pins.json`, `sizing_b5.json`); they cannot be relabelled at or after the seal commit, and a hand relabel fails the generators' `--check`. |
| F8 | NOTE | PROCEDURE | The suite is not green at the seal commit if the seal-time edit moves line 354 of the analysis plan; the fix is a `tests/` fixture, which belongs in the record commit. |
| F9 | NOTE | REPRESENTATION | The harvest records nothing about its own program; the inventory generator is an untracked file. |

Rule applied (pasted from `/Users/edr/night-archive/gate-prune/REVIEW_BRIEF_RULE.md`):

> **Physics refuses; everything else is a flag (Ed, 2026-10-05).** A *refusal* here means any code
> path that stops collection or removes data from a claim: a raise that a caller turns into a
> failed member, stage or window; a nonzero exit; a stop, kill or hold; or a flag code whose catalog
> effect is EXCLUDE_WINDOW. Only two conditions may refuse. PHYSICS: a physical hazard measured
> directly (clock step or drift, battery charge or discharge, thermal pressure, a contending
> process, free disk, the instrument not sampling, elapsed time against a calibration horizon or a
> hung-process cap). NUMBER_INTEGRITY: a number would be wrong or could not be attributed (bytes
> that differ from their recorded hash, a member from another window, an executed pack, model or
> code that differs from the sealed one). Every other condition (a missing or malformed record, a
> string or label that differs, a path layout, a pin or ledger shape, a probe that failed, a record
> that could not be written) is written as a flag and collection goes on; the pre-registered
> analysis plan decides later what the flag excludes. A reviewer's "fail closed" recommendation on
> such a condition is dispositioned **"flag, not refuse"**, never sent to a fix round. Any new
> refusal must add an entry to `configs/gates/hazard_refusals.json` (category PHYSICS or
> NUMBER_INTEGRITY, and a `protects` text naming the physical quantity measured or the number
> protected); `tests/hazards/test_refusal_allowlist.py` fails until it does, and the entry's diff is
> part of the review. A new EXCLUDE_WINDOW or EXCLUDE_MEMBER code needs the same entry under
> `window_exclusions` or `member_exclusions`. Never mark a new or changed site BASELINE and never
> add a line to `tests/hazards/refusal_baseline_frozen.txt`. The test cannot see two shapes, so the
> reviewer checks them by hand: a refusal written as `return False`, `return None` or `continue` in
> an admission or selection function, and a new call to an existing function that raises.

How the rule was applied to my own findings: F1, F2 and F3 are about executed code that differs from the sealed
code, or a comparison with the seal that was not made, which the rule names as NUMBER_INTEGRITY; each proposed fix
uses an existing code that is already in the allowlist and the catalog. F6 is representation only, and its fix
removes a fault, it adds none. Nothing else here recommends failing closed.

## Findings

### F1. MAJOR, NUMBER_INTEGRITY: a driver checkout whose code differs from the sealed code raises no flag
- **What.** The launch agent runs `<installer's checkout>/scripts/run_night.py`; the driver, the hazard modules, the
  monitor, the collectors, the G10 program and the meter program are that checkout's files
  (`scripts/run_night.py:3964`, `joulewise/b5/driver.py:676`). When that checkout is not the measurement clone the
  driver inventories it as `driver_checkout` (`driver.py:1833`). Commit `2737ef88c` copies that block into
  `derived/code-identity.json` with the list of code files that differ from the sealed inventory, and raises no flag
  (`harvest.py:5716-5732`; the lane's test `test_a_separate_driver_checkout_is_recorded_and_raises_no_flag` asserts
  it). No other code compares it: `grep driver_checkout` finds only the writer and this record.
- **Probe.** `x7`: a second checkout with one appended line in `joulewise/b5/driver.py`,
  `joulewise/hazards/clock.py` and `scripts/hazard_monitor.py`, committed, clean. The arm-time record written by
  that checkout's own `executed_inventory` for the landed clone at P1; then the real harvest head check and the
  real collectors started the way the driver starts them (script from the driver checkout, `--repo` the clone).
  Harvest flags: none. Collector flags: none. Record: `files_differing_from_sealed: ["joulewise/b5/driver.py",
  "joulewise/hazards/clock.py", "scripts/hazard_monitor.py"]`, `files_differing_from_sealed_count: 3`.
- **Why it is not only theory.** The 2026-10-06 rehearsal ran exactly this way (driver in
  `/Users/edr/code/JouleWise-wt-real-reh`, `status_clean: false`; `ab-lane-code-identity.json`). After the seal,
  main will hold fixes the clone must not hold, and the watchdog already runs from the canonical root at main.
- **Why the lane's own principle covers it.** The orchestrator's ruling: "the bytes of every file a window executed
  equal the sealed bytes" and "a changed path inside the executed scope must still be caught".
- **Smallest fix (before H_claim; `joulewise/` is a window input).** In `code_identity`, compute the
  `driver_checkout` block before the two `emit` calls, and when it lists at least one differing code file append
  `{"check": "driver_checkout", ...}` to `differences`. For parity with the measurement checkout, replay on the
  block's `status_porcelain` the two checks that checkout already gets (tracked edits; untracked files under
  `joulewise/` or `scripts/`); other untracked files stay a record, so the rehearsal's driver checkout (dirty, no
  differing file) is judged by what its porcelain lists, not by "not clean". That reuses
  `code.executed_differs_from_sealed`, already in `configs/gates/hazard_refusals.json` ("the executed measurement
  code differs from the sealed code") and in the catalog; no new code. A separate checkout with identical bytes
  stays a record. Flip the lane's test. The alternative the rule forbids is refusing the install because of where
  the checkout lives (a path layout).
- If the orchestrator rules "record only", the registration must say that the agents are installed from the
  measurement clone and that the analysis admits a window only when `driver_checkout` is null or lists no file.

### F2. MINOR, NUMBER_INTEGRITY: `record_only` is the complement of a short list
- **What.** `head_change_class` (both copies) returns `window_input` for `joulewise/`, `scripts/`, `configs/` and
  the runbook, and `record_only` for every other path. The registration's own class (iii) is a positive list
  (`docs/`, `tests/`, `RUN_STATE.md`, `TASK_QUEUE.md`). Five kinds of path fall between the two.
- **Probes** (`p1/result-cases4.json`, `result-cases2.json` case 2f):
  - 4a. A tracked root-level `hashlib.py`, committed after the seal commit. Every script inserts the repository root
    at `sys.path[0]`, ahead of the standard library. Marker file: the module was executed by the real
    `scripts/collect_window_flags.py --stage ...` process and by both of its `--run-collector` children. Harvest
    flags: none. Arm flags: none. Class: `record_only: ['hashlib.py']`. The per-file inventory does not list it
    either (roots are `joulewise`, `scripts`, the pack).
  - 2f. `env/mac-measurement-lock.txt` and `pyproject.toml`: `record_only`, no flag. Registration section 2 item 5
    has the measurement environment "relocked"; `env/README.md` builds it with
    `pip install -c env/mac-measurement-lock.txt -e ".[mac]"`. The identity pins check seven packages only.
    The lane's notes list the lock among files "the head check is the only code check on", then leave it out.
    SEAL_LANDING step 5's check (no path under `joulewise/`, `scripts/`, `configs/`, not the runbook) lets a record
    commit change it.
  - 4c. `.gitignore` gains `joulewise/zz_stray.py`, then that untracked file appears: `git status` is clean, no flag.
  - 4b. `.gitattributes` with `eol=crlf` for the runbook and `identity_pins.json`, then a re-checkout: bytes on disk
    change (runbook `c4e8bf41...` to `9a768b73...`), `git status` clean, no flag. Effect here is nil: the plan writer
    reads the runbook with universal newlines (`chain.runbook_screen` equal) and the JSON parses the same.
- **Why MINOR.** No tracked file is in such a position today (zero root-level `.py`, no `.gitattributes`), sealed
  code imports nothing from `tests/`, `analysis/` or `docs/`, and the procedure puts only pin-only commits in the
  clone. 4a needs a commit nobody makes by accident (D-161: no forger seats). The lock and `pyproject.toml` are the
  realistic ones. By kind 4a is an executed byte that escapes; the orchestrator may regrade.
- **Smallest fix (before H_claim), if taken.** Make `record_only` the positive list and `window_input` the rest:
  record-only when the path starts with `docs/` (not the runbook), `tests/`, or a dot-directory (`.github/`,
  `.claude/`, `.codex/`, `.agents/`), or is a root-level `*.md`. About six lines in each function plus rows in the
  existing parametrized test. Cheaper variant: add `"env/"` to `WINDOW_INPUT_PREFIXES` and `pyproject.toml`,
  `.gitignore`, `.gitattributes` to `WINDOW_INPUT_FILES`, and class any root-level `*.py` as a window input.

### F3. MINOR (pre-existing), NUMBER_INTEGRITY: an inventory with no `head` is compared with nothing, silently
- **Probe** (`p1/pj`). The landed inventory with `head` set to null, and a clone that holds a changed
  `identity_pins.json` committed after the seal: harvest flags none, `comparison: identical`,
  `h_claim_source: plan`, and `identity_checks.checkout_identity.head: true`. The same window with the real
  inventory: `code.executed_differs_from_sealed`, EXCLUDE_WINDOW.
- **Why it matters.** SEAL_LANDING fact 3 says the harvest's comparison is the only one that ties a window to the
  seal and that it needs a non-null `head`. The code does not require one. `identity_checks...head: true` also
  lets the harvest supersede an arm-time `code.identity_unmeasured`.
- **What already covers the seal.** `tests.test_b5_seal_landing` rejects a committed inventory whose `head` is not a
  commit. The gap is an inventory handed in by `--sealed-inventory-path`, and `scripts/rehearse_b5_real.py`, which
  still writes `head: null`.
- **Smallest fix.** In `code_identity`, when the sealed inventory was read and names no head, append
  `{"check": "head", "missing_input": "sealed_inventory_head"}` to `unmeasured` (`code.identity_unmeasured`, already
  allowlisted: "which code produced the numbers could not be established") and do not set
  `identity_checks["checkout_identity"]["head"]`. Two lines; the rehearsal generator then has to write a head.
  Or leave the code and state in the registration that `h_claim_source` must read `sealed_inventory`.

### F4. NOTE, PROCEDURE: commits to the seal documents after the seal commit are silent
- **Probe.** 2a: a commit after S that edits the registration and the analysis plan: no flag from the harvest or the
  collectors, and the record cannot show it (`seal_document` already lists the three paths because of S). `p3` n3:
  the landing checker stays `('sealed', [])` after a later registration-only commit. A later edit of the inventory
  is caught (n4).
- This follows the ruling. What binds the registration is (a) the plan's recorded digest, which the harvest faults
  on (`harvest.py:1414`), and (b) the seal record. (a) only helps if the plan's digest is copied from the seal
  record, as SEAL_LANDING step 8 says; a plan written from the clone's current file carries whatever is there.
- **Smallest fix (tests only, can land in the record commit).** In `seal_landing_problems`, also report any commit
  in `<seal commit>..<ref>` that changes `registration_block5.md`. The registration writer needs fact 17 as written.

### F5. NOTE, PROCEDURE: a re-harvest after a re-issued seal needs the old inventory
- **Probes** (`p2`). 5d: ALPHA-1 ran at P1; a GAMMA-pack-only cure C' and its seal commit S' follow; the re-harvest
  reads the inventory from the clone's working tree (the default): EXCLUDE_WINDOW, head check only,
  `window_input` = the GAMMA file. 5e: the same re-harvest with `--sealed-inventory-path` = the inventory in force
  at ALPHA-1's arm: clean. 5c: BETA and GAMMA windows armed at S' are clean.
- The lane states the rule (SEAL_LANDING section 6 (iv), fact 23). It must reach the magistrate brief: registration
  7.5 says such a cure "does not supersede completed windows", and 7.5's third bullet makes re-harvests routine.
- Alternative fix, not needed for the seal: the harvest reads the inventory as committed at the executed head
  (`git show <executed head>:<path>`) and falls back to the working tree.

### F6. NOTE, REPRESENTATION: a changed path that is not UTF-8 faults the harvest
- **Probe** 7a: an index entry `docs/review-\xff.md` committed after the seal. The harvest's `_changed_paths` raises
  `UnicodeDecodeError` (`text=True` with `-z`; the `except` names `OSError` and `SubprocessError` only), which
  `step()` turns into a harvest fault. The arm collector decodes with `"replace"` and classes the path. Before the
  lane git quoted such a path and nothing raised. Such a path cannot be checked out on APFS, so this is remote.
- **Fix.** One line: pass `encoding="utf-8", errors="replace"` to the runner call. By the rule a path string must
  not fault.
- Related, correct: 7d, a path containing a newline (`docs/x\njoulewise/y.py`), is classed `record_only` as one
  path; without `-z` its second line would have read as `joulewise/y.py`.

### F7. NOTE, PROCEDURE: draft labels are part of the sealed bytes of three window inputs
- **Probe.** At the lane head `flag_catalog.json` `notes.status` reads "DRAFT, NOT SEALED. Revision 9";
  `identity_pins.json` and `sizing_b5.json` read `"status": "UNSEALED_DRAFT"`, `"sealed": false`, and the sizing
  note holds the literal `FILL[B5-SIZING-OUTPUTS]`. Changing either generated file by hand makes its generator's
  `--check` exit 1 (run), and any byte change to any of the three after H_claim excludes every later window (1f,
  1g, 1h). The generators say "until the seal replaces it" (`scripts/write_b5_identity_pins.py:63`); the seal
  commit may not touch them.
- No program reads these labels. Either the two generators and the catalog text change before H_claim, or the
  registration says the labels stay and that the seal record's digests are what seals the files. The catalog's
  status sentence also cannot name H_claim (the catalog is inside it); it can name H_claim's parent. SEAL_LANDING
  step 1 and REGISTRATION_FACTS fact 4 should say this. The false catalog note (line 344) is the same kind: before
  H_claim or never.

### F8. NOTE, PROCEDURE: the record commit must carry the test fixtures the seal commit forces
- **Probe** (`p3`). `tests/fixtures/d165_rationale_allowlist.json` pins three phrases at line 354 of the analysis
  plan. One line inserted near the top of the analysis plan: `tests.test_d165_rationale_census` fails (2 errors).
  The fixture is under `tests/`, so correcting it in R raises no flag (2c). SEAL_LANDING step 4 should say that
  the whole suite is green at R, not necessarily at S, and step 5 should list `tests/` fixtures among R's paths.

### F9. NOTE, REPRESENTATION: two identities that are not recorded
- The harvest archive holds no path, head or digest of the harvest program (checked on the fixture archive
  produced from the second checkout). Registration 11 item 4 is therefore procedural only, as the lane says
  (fact 18). A record in `harvest.json` (root, head, clean, one digest over `joulewise/` and `scripts/`) would make
  the addendum checkable; a record, never a flag.
- `make_sealed_inventory.py` (SHA-256 `617554f5...d92de0`) is not tracked. That is safe: the landing test recomputes
  every digest from git objects. The seal record should carry its digest or the file should be committed.

## Probes by brief item

### Harness (`/private/tmp/w1007-sealreview/harness/`)
- `build_landing.sh`: full clone of the lane head; C = `2737ef88c` (stand-in for H_claim); the lane's
  `make_sealed_inventory.py` generates the inventory; S = seal commit (three seal documents); R = a seal record
  under `docs/`; P1 = one pin-only commit. Probe repo `/private/tmp/w1007-sealreview/p1/repo`
  (S `56d7048d6`, R `1f0d6f1cb`, P1 `4e81af411`).
- `mk_executed.py`: the real `joulewise.b5.driver.executed_inventory` (the arm-time record).
- `run_code_identity.py`: the real `joulewise.b5.harvest._Harvest.code_identity` body on that record, the probe
  repo's sealed inventory and the real `git diff`; flags mapped to the effect in the repo's `flag_catalog.json`.
- `run_collectors.py`: the real `scripts/collect_window_flags.py --stage desk --h-claim C` with the
  `checkout_identity` and `executed_code` collectors.
- `cf.py`, `batch.py`: one commit on top of P1 per counterfactual, the three programs, then reset.
- `build_fixture_window.py`, `summarize_archive.py`: the harvest test fixture landed in real git, harvested by the
  real command line `scripts/harvest_b5_window.py`; summaries read `derived/` only.

### Baseline (the landing as the procedure describes it, executed head P1)
- The generator reproduced the lane's inventory byte for byte: 682 files, SHA-256 `1315cd57...9695c`.
- Harvest: `comparison: compared`, `h_claim_source: sealed_inventory`, seal_document 3, pin_only 1, record_only 1,
  window_input 0; no flag. Arm collectors: no flag; 438 of 438 sealed files in the window's roots.
- End to end through the real exclusion function: fixture window, a file of another pack directory added after
  the seal, harvested by the command line: `exclude_window` gains `code.executed_differs_from_sealed` (34 flags
  against 33).

### (1) one changed byte in a window input after H_claim: every case EXCLUDE_WINDOW, harvest and arm collector
`p1/result-cases1.json`, `result-cases2.json`; ALPHA window.
| case | changed path | harvest checks that fired | arm collector checks |
|---|---|---|---|
| 1a | `joulewise/whole_window.py` (+1 byte) | per-file, head | head, per-file |
| 1b | `scripts/run_campaign.py` | per-file, head | head, per-file |
| 1c | `scripts/prewindow_check.sh` | per-file, head | head, per-file |
| 1d | own pack `plan_tree.json` | per-file, head | head, per-file |
| 1e | own pack member config | per-file, head | head, per-file |
| 1f | `identity_pins.json` | head only | head only |
| 1g | `sizing_b5.json` | head only | head only |
| 1h | `flag_catalog.json` | head only | head only |
| 1i | `docs/phase_2/window_runbook.md` | head only | head only |
| 1j | `configs/gates/hazard_refusals.json` | head only | head only |
| 1k | new file `joulewise/zz_new_module.py` | per-file, head | head, per-file |
| 1l | deleted `scripts/size_b5_window.py` | per-file, head | head, per-file |
| 1m | `joulewise/external/km003c_parse.py` moved to `attic/` | per-file, head (old path listed) | head, per-file |
| 1n | mode change only (`chmod +x joulewise/b5/chain.py`) | head only | head only |
| 1o | file replaced by a symlink to identical bytes outside the roots | head only | head only |
| 1p | a file of an unrelated campaign under `configs/campaigns/exploratory_2026_07_17/` | head only | head only |

1h: the catalog is listed in the sealed inventory, but neither per-file check compares it, because it lies outside
every window's executed roots. The lane's fact 16 is right that the head comparison is its only code check.
In production the arm collector is given the plan's `measurement_head`, which the installer forces to equal HEAD
(`night_agent_install.py:1235`), so the arm column above is what a desk run with `--h-claim C` shows; at a real arm
only the per-file rows fire. The lane says so (fact 15).

### (2) commits that must not exclude: none did; each is listed
| case | commit touches | harvest flags | arm flags | where recorded |
|---|---|---|---|---|
| 2a | registration and analysis plan again, after S | none | none | `seal_document` (already 3 because of S; F4) |
| 2b | `docs/decision_log.md`, `README.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, a new `docs/phase_2/` note | none | none | `record_only` (5 paths) |
| 2c | three files under `tests/` | none | none | `record_only` (3 paths) |
| 2d | second pin-only commit, ALPHA window | none | none | `pin_only` |
| 2g, 2h | pin-only commit, GAMMA window and BETA window | none | none | `pin_only` |
| 2e | pin, docs, tests and analysis plan in one commit | none | none | each in its class |
| 2f | `pyproject.toml`, `.gitignore`, `env/mac-measurement-lock.txt`, `.github/workflows/ci.yml`, `analysis/` | none | none | `record_only` (F2) |
Also clean: executed head = the seal commit's merge commit M (below).

### (3) letter case (the volume is case-insensitive APFS: a file made as `CaseProbe` opens as `caseprobe`)
What is compared without regard to case: in both `head_change_class` functions, only the question "is this path a
window input": `path.casefold().startswith(("joulewise/", "scripts/", "configs/"))` or
`path.casefold() == "docs/phase_2/window_runbook.md"`. The pin path and the three seal-document paths are compared
by exact string, and those two tests run first. No digest and no commit name is compared without regard to case.
`p1/result-cases3.json`: each case adds a git index entry whose name differs only in case, commits it and
re-materializes the working tree, as a pull of such a commit would.
| case | index path added | on disk | harvest | arm |
|---|---|---|---|---|
| 3a | `Joulewise/zz_case.py` (new) | lands in `joulewise/`; the per-file inventory does not list it | EXCLUDE (head only) | EXCLUDE (head only) |
| 3b | `Scripts/run_campaign.py` with other bytes | overwrites `scripts/run_campaign.py` | EXCLUDE (per-file, head, tracked edits) | EXCLUDE |
| 3c | `.../v5_claim_25g83/Registration_block5.md` | overwrites the registration | EXCLUDE (head, tracked edits) | EXCLUDE |
| 3d | `Docs/Phase_2/Window_Runbook.md` | overwrites the runbook | EXCLUDE (head, tracked edits) | EXCLUDE |
| 3e | `configs/calibration/Calibration_ledger_head.json` | overwrites the pin | EXCLUDE (head, tracked edits) | EXCLUDE |
| 3f | `Configs/campaigns/v5_claim_25g83/identity_pins.json` | overwrites the identity pins | EXCLUDE (head, tracked edits) | EXCLUDE |
| 3g | `docs/phase_2/window_runboo<U+212A KELVIN SIGN>.md` | overwrites the runbook | EXCLUDE (head, tracked edits) | EXCLUDE |
No case variant escaped. 3a shows the fold doing real work: without it that file is importable and unlisted.
The fold only widens the excluded class; the two exact-match classes cannot be reached by a case variant.
- U-1, digests and `head` in upper case (`p1/u1`, `u1c`). Every digest upper case: harvest 438 differences, arm 50
  listed, EXCLUDE. One digest upper case: one difference, EXCLUDE. `head` upper case: git resolves it, the
  comparison runs, no flag on the clean landing. An upper-case digest can only make a false difference. One corner
  by reading: the harvest drops a malformed digest from the sealed map, so a sealed file with a malformed digest
  that is also missing from the checkout is not reported per file; the deletion is still listed by the head
  comparison or by tracked edits, and the landing test rejects the inventory.
- The two classifier functions agree on 111,837 paths (every tracked path and nine variants of each).

### (4) the procedure, step by step
- Step 1, stub state: `tests.test_b5_seal_landing` 9 OK at the lane head. Generators' `--check`
  (`size_b5_window.py`, `write_b5_identity_pins.py`) exit 0. Neither output embeds a repository commit name.
- Step 2, generator: refuses a checkout with an untracked file and writes nothing (run); output accepted by the
  harvest, both collectors and the landing checker.
- Step 4, checks 1 to 3: `git diff --name-only --no-renames C S` = the three paths; landing test 9 OK at S; the
  generator on a clean checkout of S gives the same `files` map (682).
- Step 5: landing test 9 OK at R. CI fence commands at C and at R: `scripts/repin.py --check` "PASS 16 pin families
  current", `scripts/gen_state.py --check` exit 0, `tests.test_docs_freshness` 31 OK,
  `scripts/digest_pin_census.py` exit 0 and leaves `configs/pins/registry.json` untouched (the 682 new digests do
  not force a change to a window input).
- Step 6: merge commit M (first parent `7cd23b914` = today's main, second parent R): `git diff R M` empty; landing
  test 9 OK; a window run from M: no flag. CI checks out with `fetch-depth: 0`, so the landing test runs there.
  Squash (`p3`): the checker reports the parent and the extra path; in a transport clone of the squashed branch C
  is absent, the checker says "head ... is not a commit", the harvest says `code.identity_unmeasured`
  (`git_diff_unavailable`, EXCLUDE_WINDOW), the desk collector `code.executed_differs_from_sealed` (descends
  false). "Never squash" is a real constraint and fails toward exclusion.
- Step 7: landing test 9 OK at P1; collectors clean; a shallow clone at S makes the repository test skip.
- Step 8: `plan._locator` accepts the right digest of `sizing_b5.json` and raises `WindowPlanError` on a wrong one
  (run). Installer citation read: `plan.measurement_head` must equal the measurement checkout's HEAD.
- Step 9: `advance_ledger_pin` commits with `git commit --only -- <pin>` and raises unless the changed paths are
  exactly the pin (`plan.py:717-721`), read not run.
- Negative cases (`p3`): a seal commit that also changes `identity_pins.json`: reported. A later edit of the
  inventory: reported. A later class (ii) fix on main: checker still clean (it reads C and S from git objects).
- The lane's `proof-landing.sh`, unchanged except the scratch path: exit 0; its log equals `proof-landing.log`
  line for line once commit names are masked (`logs/proof-landing-review.log`).
- Self-reference: none. The inventory names C, its parent. The registration at S prints C, digests of files at C
  (`FILL[B5-FINAL-HASHES]`, for example the identity pins digest `a0865895...` at line 1471, which is the file in
  the lane head) and the seal record's path. The seal record prints S and the digests at S. Nothing prints R.
  No tracked file under `joulewise/`, `scripts/`, `configs/` or `tests/` holds the SHA-256 that the registration,
  the analysis plan or the stub has at C (searched with `git grep`: 0, 0, 0), so the seal commit breaks no pin.
- Citations: 24 `file:line` citations in SEAL_LANDING.md checked at the reviewed head, all correct.
- **The procedure is internally consistent and can be carried out.** It needs three additions to be complete: F7
  (labels final before C), F8 (R carries test fixtures), F5 (the re-harvest rule in the magistrate brief).

### (5) the dissent: all of `configs/` and the runbook stay caught
- 5a (`p2`). BETA armed from a clone that holds a GAMMA-pack-only change and the old inventory: EXCLUDE_WINDOW,
  head check only. Under the ruling's narrower scope this window would be clean.
- **Can it exclude a clean window in the registered sequence (three packs sealed together, pin-only commits
  between windows)? No.** Between windows the only committer in the clone is the pin advance, which refuses a
  commit that is not the pin alone; pin-only commits raise nothing for ALPHA, BETA or GAMMA (2d, 2g, 2h); a window
  of each of the three packs run from S and from R is clean in the harvest and in the collectors (run; six windows, no flag),
  and so is one run from M. No registered step writes a tracked file under `configs/` (window plan inputs are
  untracked files given by `--inputs`).
- **Pin-only commits to `configs/calibration/calibration_ledger_head.json` are exempt**, by exact match tested
  before the `configs/` prefix; a case variant of that name is not exempt (3e).
- Where the dissent does cost something: the registered contingency of registration 7.5, first bullet (F5), and
  F7 for `identity_pins.json` and `sizing_b5.json`. Under the narrower scope a GAMMA-pack-only cure would need no
  old-inventory rule for ALPHA and BETA re-harvests, but a cure to GAMMA-only code under `joulewise/` or `scripts/`
  needs it in either scope, because every window inventories all of both directories. So the rule is needed anyway.
- My reading: the dissent is right. For `identity_pins.json`, `sizing_b5.json`, the catalog and the runbook the
  head comparison is the only code check (1f to 1i fire on the head check alone); the narrower scope would have
  left the first two and the runbook with none.

### (6) where the harvest and the analysis may run
- 6a (`x6`). The real `code_identity` imported from a second checkout at another head (one commit that changes
  `joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/__init__.py`), on the window
  collected at P1 in the clone: no flag; `comparison: compared`, window_input 0.
- 6b. The harvest test fixture, measurement checkout landed in real git (H_claim, seal commit), harvested twice by
  the real command line `scripts/harvest_b5_window.py`: once from the lane-head checkout, once from that second
  checkout. Both exit 0, COLLECTED, 33 flags; the flag multiset (code, scope, observed) is equal; no `code.*`
  flag; `exclusions` equal; `code-identity.json` equal. (`--skip-g3`; the fixture's own exclusions are calibration
  and NEG-8 artifacts of a synthetic window.)
- **So yes: `harvest_b5_window.py` can run from a checkout other than the measurement clone, at a different head,
  on a window collected at the seal commit, without flagging the window.** By reading, nothing in the harvest
  compares its own checkout with anything: it takes the pack, ledger, pin, inventory, catalog, identity pins and
  registration from the plan's `measurement_root` (`resolve_inputs`), the acceptance from the measurement root
  first (`_acceptance_path`), runs `git diff` in the measurement root, and with `--prepare-desk` runs
  `<measurement root>/scripts/run_campaign.py` under `<measurement root>/.venv/bin/python` (`harvest.py:5199-5201`).
  The G3 checker runs from the harvest's own checkout with `--repo-root` the measurement root.
- The lane's limits on this claim are also true: no code reads a seal-record addendum, and the harvest records
  nothing about itself (F9).
- What the magistrate must never do, confirmed by 1a: bring a class (ii) commit into the clone (both checks, both
  programs, EXCLUDE).

### (7) tests, allowlist, pinned files
- The lane's log `tests-run3-final-head-2737ef88c.log` holds the count (739 OK) but no module list, so I chose the
  list: every test module that names the changed functions, the collectors, the harvest, or the seal directory.
  23 modules, 675 tests, all OK at the reviewed head:
  `tests.test_harvest_b5_window` (182, 600 s); `tests.test_harvest_b5_p2harv`, `tests.test_harvest_b5_p3harv`,
  `tests.flags.test_flags_collect`, `.test_flags_fx_regressions`, `.test_flags_review_regressions`,
  `.test_flags_catalog`, `.test_flags_core`, `.test_flags_exclusions`, `.test_flags_identity_pins`,
  `.test_flags_import_graph`, `.test_flags_schema`, `tests.test_b5_seal_landing`,
  `tests.hazards.test_refusal_allowlist`, `tests.test_gate_prune_integration`, `tests.test_neg8_survivors`,
  `tests.test_hazard_neg8_mint_verdicts`, `tests.test_write_b5_identity_pins`, `tests.test_size_b5_window`,
  `tests.test_d165_rationale_census`, `tests.test_digest_pin_census`, `tests.test_b5_chain_static_check`,
  `tests.test_b5_chain_prune2` (493, 310 s). Logs: `logs/tests-A-harvest.log`, `logs/tests-B-others.log`.
  Two tests skipped because my clone had the design branch only as a remote ref; with the local ref
  (`1d97f0a60`) both pass, and `tests.hazards.test_refusal_allowlist` is 23 OK with no skip. No load failure.
- No new refusal or EXCLUDE code. Files changed base to head: `joulewise/b5/harvest.py`,
  `joulewise/flags/collect.py` and three test files. `configs/gates/hazard_refusals.json`,
  `tests/hazards/refusal_baseline_frozen.txt`, the catalog, `joulewise/flags/catalog.py` and `core.py` are
  untouched. The added lines hold no `raise`, no `return False` or `None`, no `continue`, no new `emit` code and no
  new flag-code literal.
- By hand, the shape the test cannot see: one new call to an existing function that raises, `write_json_once` for
  `derived/code-identity.json`. Run: with the file already present it raises `FileExistsError` after the flag was
  emitted (`['code.executed_differs_from_sealed']`), and `step()` records a harvest fault. That is the convention
  of every derived output (re-harvest on identical bytes, never a science outcome); it stops no collection and
  removes no data through the catalog. No defect.
- The four pinned estimator files and `scripts/prewindow_check.sh` have the same git blob at `9b0c680ed` and at
  `2737ef88c` (`82449d58`, `202acfcb`, `d1bd5d4b`, `8fa6db3c`, `0e622e94`); the script's SHA-256 begins `d8458eea`,
  the value the registration quotes.

## What I could not verify
- The lane's exact 739-test list (not in its log).
- The analysis half of point 6 (extraction, mint, `analysis_engine` run from another checkout): not executed; I
  verified the harvest only.
- A real window: every harvest-side probe used the real functions on a real repository with a real arm-time
  inventory, or the synthetic fixture window end to end. I did not rerun the lane's A/B on the rehearsal archive;
  I read its output (`ab-compare.log`).
- The G3 checker under a second checkout (I passed `--skip-g3`); by reading it takes no identity from its own
  checkout.
- The pin-advance program and the installer were read, not run.
- The real seal-time text of the registration and analysis plan does not exist yet; my seal commit appended one
  line to each.

## Scratch left behind
`/private/tmp/w1007-sealreview/` (1.2 GB): `harness/`, `logs/`, `p1/` (probe repo and result files), small result
files in `p2/`, `x6/`, `x7/`. Disposable clones were removed. No process is left running.
