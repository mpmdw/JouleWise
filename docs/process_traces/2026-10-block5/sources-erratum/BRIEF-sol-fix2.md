SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5/harvest.py", "joulewise/whole_window.py", "scripts/harvest_b5_window.py", "tests/**", ".scratch-fix/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn after writing the report. Start no background task. Commit nothing; leave your changes uncommitted in the working tree.

# Round 2: bring the harvest's catalog recovery into exact agreement with the admitted text of Erratum 2

You work in `/Users/edr/code/JouleWise-wt-harvest-sources`, branch `lane/2026-10-10-harvest-screen-sources`, head
`0b23cf491c928c7d6fb38aa4e5674550d0700dce` (round 1's fix, committed). A cold judge admitted the erratum with
corrections and wrote the complete rule. **The rule is frozen: the program must implement it exactly, item by
item; you may not change the rule.** If you find that an item cannot be implemented exactly as written, do not
approximate it: implement everything else, and say in your report which item, why, and what the nearest exact
behaviour would be.

## Hard rules

- Write only inside WRITE_SCOPE. Outside `tests/`, the lane may differ from the claim head in exactly three
  files: `joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `scripts/harvest_b5_window.py`
  (registration section 11 item 4). The verdict writer that a harvest starts is the measurement clone's own
  sealed copy of `scripts/run_campaign.py` and `joulewise/whole_window.py`; it is not changed by this lane
  and its stored verdict bytes stay as they are. The desk copy of `joulewise/whole_window.py` is used only
  by the harvest. Never edit the four pinned estimator files (`joulewise/reduce.py`,
  `joulewise/uncertainty_evidence.py`, `joulewise/powermetrics_fiducial.py`,
  `joulewise/adapters/powermetrics.py`) or `scripts/prewindow_check.sh`.
- Run only targeted tests (the test modules for the harvest and the whole-window screen that you touch or
  add). Do not run `unittest discover` or `shard_tests.py`. Use `/opt/homebrew/bin/python3.13` or the
  repository's documented interpreter; no Homebrew command of any kind; no package install.
- No measurement work; nothing that loads the machine for more than a few minutes. Do not start another
  agent and do not call Claude or Codex by any route. No network access is needed.
- The owner's address and name go into no network request made by you (no URL, header, payload, `gh` call
  or `git config` line) and into no file.
- Scratch files go under `.scratch-fix/` in your working directory (create it; it is inside WRITE_SCOPE), never
  under `/private/tmp` and never inside a custody root, runs root or harvest archive. Point `TMPDIR` and
  `tempfile.tempdir` there for tests. Delete `.scratch-fix/` before you end.
- Blinding. The block is blinded until its release event: nobody may learn a measured energy, power or
  duration of a claim window. The passage below says which files of a claim window may be opened. It binds
  you word for word. Your report carries structure only.

### The passage (from the magistrate brief, section 6; "you" is the magistrate, and it binds the seat the same way)

**What you may open before the release event** (the orchestrator's decision O-7 of 2026-10-07). The
registration's custody map (its section 8) lists the paths nobody may open before the release event and
calls the rest releasable. Decision O-7 gives you less than the map releases, on purpose: every file you do
not open is one that cannot leak a value into a record, an email or a repair. Where the two differ, follow
this list. Of everything a window and its harvest produce, you open only:

- `harvest.json` in a harvest's archive root: `verdict`, `claim_usable` and `exclude_window_reasons`, and
  also its member counts (`yield`), its list of failed collectors by name (`faults`) and `harvest_checkout`.
  You read them through the reading block of 4.5.
- `derived/code-identity.json` in the archive root (which paths differ between H_claim and the commit the
  window ran from).
- `night/hazard_result.json` in the window's custody root (the driver's verdict, the arm's verdict for each
  hazard, the yield counts for each stage, the reason codes the driver raised, the fault reasons), and the
  one word `result` of `night/g10.json`.
- `hazards/arm.json` in the window's custody root, the **arm record**: what the arm measured for each of the
  six hazards, its verdict for each, and so which hazard modules refused. Registration section 7.3 builds the
  **cause key** of an attempt that started no chain from this file (the cause key is what rule 1 below
  compares between two attempts of a pack: the hazard modules that refused, or the families of the
  window-removing codes), and the registration's custody map lists the file as a hazard measurement that may
  be read during the block (the orchestrator's decision of 2026-10-07 23:55 adds it to this list).

A consult seat that you convene may also read the monitor's contention journal,
`<custody root>/hazards/monitor/contention.jsonl` (process names and CPU shares). **Nobody opens
`derived/flags.jsonl`, `derived/exclusions.json` or `derived/window_flags.json`** (seal gate ruling SG-12):
they name, member by member, a reason code whose presence says something about a measured energy. The
harvest program reads them to compute `claim_usable`; you read `claim_usable` from `harvest.json`. Nobody
opens anything else under a custody root's `hazards/`, `flags/`, `operator-logs/` or `night/transcript/`, its
`night.log` or chain logs, a runs root, or an archive's `sources/` or `withheld/`, except a program that
prints structure only (the END STATE count below is one). Plan-time files written at the desk before t0 (the
plan, `window.env`, the staging directory) are not restricted. Testing that a file exists is not opening it.
Every brief you write for a seat carries this passage whole, from "What you may open" to here.


For this task: the claim windows are every `v5-b5-*` custody root under `/Users/edr/night-custody/`, every
runs root under `/Users/edr/night-b5/`, and every archive `/Users/edr/night-archive/harvest-v5-b5-*`. You
open none of their restricted files and run no program over them. Everything you need from them is in
"Facts" below. If one more structural fact from a claim window would settle something, write the exact
program in your report under "Counts I would want" (it prints fixed labels, words from closed lists in the
code, and integer counts only) and the magistrate decides whether to run it.

Rehearsals are not claim windows and are open to you, read-only:
`/Users/edr/night-archive/gate-prune/rehearsal-real/` (`alpha-1`, `gamma-1`, `gamma-2`, and the three
`corpus18-*` bases of the second seal; `corpus18-20261009T1949Z` is the one that completed, with all 18
corpus members). Copy what you need into your scratch directory and work on the copy.


## Read first

1. `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/sources-erratum/RULING.md`,
   section D ("THE ADMITTED TEXT": items 0 to 9, Unchanged, the worked example, section 5 Mechanics, and the
   closing paragraph "What the present diff does not yet implement"). Section D is the specification. Sections
   A to C and E give the reasons.
2. `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/sources-erratum/REFUTATION.md`
   (the refuter's findings, with code citations; MINOR 9 lists text/implementation disagreements).
3. Your own round-1 report: `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/sources-erratum/sol-fix.md`.

## What to build

Everything the ruling's closing paragraph lists as not yet implemented, with a test for each:

- Item 0 conditions (b) to (f) with their closed words, tested in the stated order
  (`runs_root_not_hazard`, `membership_condition_not_unresolved`, `no_absent_invoked_member`,
  `invoked_member_ambiguous`, `occurrence_supersession_present`); when (a) does not hold the recovery is never
  entered.
- Item 1: every catalog manifest schema v2, else `source_manifest_schema_v1`; nothing returned is
  `source_manifest_unauthenticated`; an empty list is `source_manifests_unrecorded`.
- Item 3: the roster check (`reference_not_in_roster`): every reference found must be a planned reference or a
  spare of the sealed roster at the same slot.
- Item 7(b): the basis-membership check (`reference_not_in_verdict_basis`): every surviving reference must be a
  `member_occurrences` entry of the stored verdict's validated evaluation basis whose three SHA-256s equal fresh
  hashes of the bundle's `config.json`, `metadata.json` and `summary_metrics.json`. A lost reference need not be
  in the basis.
- Item 6: `midpoint_lost` is the realised value (true exactly when no midpoint survives), not a constant.
- Item 8: `reference_source` in `derived/neg8-allowance.json` as well; the exact objects of item 8 in
  `derived/neg8-screen.json` and in `observed.reference_source`; `campaign_sources_problem` and
  `rescreen.problems` carry the closed word.
- The program gate of section 5: a module constant in `joulewise/b5/harvest.py`,
  `ERRATUM_2_ADMITTED_AT = "2026-10-10T16:30:00Z"` and `ERRATUM_2_ADMITTED_AT_EPOCH_S = 1791649800`; the recovery
  is refused when the window plan's `t0_epoch_s` is not later than it: "cannot run" with
  `campaign_sources_problem` `recovery_predates_erratum`. Find how the harvest already reads the plan
  (`hazard_window`, `t0_epoch_s`); if the plan's t0 cannot be read, that is also `recovery_predates_erratum`
  (fail closed). Say exactly where in the order of item 0 you test it: it must be tested after (a) and before
  (b), so that an ungoverned attempt never enters the recovery; say so in the report.
- Item 9 (the claim consumer) is NOT yours; it belongs to a later lane. Do not build it.
- Tests for the cases the refuter lists as untested: an ambiguous second directory, a v1 manifest, a non-hazard
  root, a reference outside the roster, a reference outside the basis, a basis hash mismatch, an ungoverned t0,
  an occurrence-supersession row, a stored row whose membership condition is `..._ambiguous`.
- Keep: a verdict with recorded sources must behave byte for byte as under the pinned program `224a264c5`, and a
  verdict whose recorded sources do not authenticate exactly as before.

## The check on real rehearsal bytes (round 1 could not run it)

The completed rehearsal `/Users/edr/night-archive/gate-prune/rehearsal-real/corpus18-20261009T1949Z` is not a
claim window and is open to you read-only. Find how it was harvested (its harvest archive and the command are
described in `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/second-clone.md`).
Show that the harvest's derived screen outputs for it are byte-identical and the emitted flags equal between the
pinned program (`git worktree` is not available to you; use `git show 224a264c5:<path>` into `.scratch-fix/` or
the read-only checkout `/Users/edr/code/JouleWise-wt-harvest-cap`, which is at `224a264c5`) and your working
tree. If a full harvest of the rehearsal would run for more than about ten minutes or would write inside the
rehearsal's directories, do not run it: instead call the screen functions (`neg8_corpus_physics`, `neg8_screen`
and what they need) over the rehearsal's existing archive in memory under both programs and compare the
results; say exactly what you compared. If neither is possible, say NOT EXECUTED and why.

The rule every lane on this path carries:

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



## What to return

Sections: Item-by-item table (each item 0(a) to 0(f), 1 to 8 and the program gate: file and line where it is
implemented, the test that covers it, and "exact" or the deviation); Tests (commands and result lines); Rehearsal
comparison (what ran, result); Anything in the admitted text that is ambiguous or that you could not implement
exactly; Residual risk. No energy, power or duration values, no member names from a claim window.
