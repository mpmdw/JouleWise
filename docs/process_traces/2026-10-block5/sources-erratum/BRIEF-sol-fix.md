SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5/harvest.py", "joulewise/whole_window.py", "scripts/harvest_b5_window.py", "tests/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn after writing the report. Start no background task. Commit nothing; leave your changes uncommitted in the working tree.

# Root cause and harvest fix: a block-5 window was removed by `neg8.screen_failed` because the stored verdict names no source campaign manifest, although enough references survive

You work in `/Users/edr/code/JouleWise-wt-harvest-sources`, branch `lane/2026-10-10-harvest-screen-sources`,
created from `224a264c5faaae90cdf56118df37e773a932700b`, the commit the block-5 harvest program is pinned
at. That tree contains the sealed tree of the second seal (claim head
`c27485347c9629b857df81665b5b1b8d10dcd36a`). You are asked for your own engineering and design judgment
and have explicit license to disagree with the hypothesis and the fix shape suggested here.

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
- Scratch files go under `/Users/edr/night-archive/b5-consults/beta-a1/fix/scratch/` (create it), never
  under `/private/tmp` and never inside a custody root, runs root or harvest archive.
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

## Facts (established by the magistrate with count programs; structure only)

The window is BETA attempt 1 of the second seal, plan `v5-b5-beta-a1-20261010T0742Z`. Its chain ran its
whole span from the sealed clone; the harvest (commit `224a264c5`) exited 0 with verdict `COLLECTED`,
`claim_usable` false, one window reason `neg8.screen_failed`, no collector fault.

- Run time: start references 3 of 3 succeeded, midpoint 1 of 1, end references 2 of 3. After the end
  stage the chain's spares decision returned 0 and the stage `beta-reference-end.spares` ran and returned
  rc 1 within roughly ten seconds. The harvest's yield shows 125 planned, 125 present and no `.spares`
  roster stage, so the spare left no bundle directory.
- Corpus: 18 collected, 1 dropped at the harvest, 12 kept, clean bound validated
  (`bound_used` is `corpus_physics_clean`).
- `derived/neg8-screen.json`, by closed-list words: `stored.decision` `failed`; stored conditions beyond
  the two underived codes: `neg8_bracket_missing`, `neg8_bracket_reference_invalid`; `rescreen.evaluated`
  false; `rescreen.problems` exactly `['source_manifests_unrecorded']`; no survivor record;
  `harvest_reference_losses` has two entries: one `member.admission_aborted` at the end endpoint and one
  `contention.request_overlap` at the start endpoint. So the surviving references are 2 at the start, 1 at
  the midpoint, 2 at the end, a shape the registration's screen is defined for.
- The stored `whole-window-verdict.json` (key names and list lengths only): same keys as the verdict of
  the claim-usable ALPHA attempt 1. ALPHA's has `source_campaign_manifests` with 9 entries (top level and
  under `row_provenance`), `bundle_ids` 105, `neg8_bracket.claim_families` with 2 entries. BETA's has both
  `source_campaign_manifests` lists **empty**, `bundle_ids` 99, `evaluation_basis.member_occurrences` 99,
  `excluded_bundles` 8, `member_failures` 8, `neg8_bracket.claim_families` empty and the bracket's numeric
  fields null, `neg8_bracket.conditions` with 4 entries, `idle_admission_core.conditions` with 6.
- The claim runs root's `campaign_manifests/` directory: ALPHA attempt 1 has 9 files, BETA attempt 1 has
  10. With the desk root's `campaign_provenance` functions, every file authenticates pointwise
  (`load_authenticated_campaign_manifest`: 9 of 9 and 10 of 10) and `load_authenticated_campaign_catalog`
  returns 9 and 10 records. The first seal's ALPHA attempt 3, which also ran a spare stage that returned
  rc 1, also has 10 files, all authentic.
- `harvest.py` `verdict_neg8_sources` returns `source_manifests_unrecorded` when
  `row_provenance.source_campaign_manifests` is missing or empty (near lines 1104 to 1170).

Working hypothesis (prove or refute it from the code): a spare invocation that writes a campaign manifest
and leaves no bundle makes the sealed verdict writer record an empty source list (and so a bracket with no
references), and the harvest then refuses to re-run the screen. If true, every window that loses a
reference at run time and whose spare leaves no bundle is removed whatever its physics.

## What to do

1. **Root cause.** From the sealed code (`scripts/run_campaign.py`, `joulewise/whole_window.py`,
   `joulewise/campaign_provenance.py`, `joulewise/b5/chain.py`, `joulewise/b5/reference_spares.py`), find
   exactly why the writer stored an empty `source_campaign_manifests` and a missing bracket for a runs
   root with 10 authentic manifests, and why the spare invocation returned 1 without a bundle (name the
   return site if you can; that code is window-executed and is NOT to be changed here, only explained).
   Reproduce the empty source list on a scratch copy of a rehearsal runs root by constructing the state
   the facts describe (for instance by adding the manifest and campaign-log rows a bundle-less spare
   invocation leaves, using the repository's own functions), and show the reproduction's commands.
2. **Is a harvest-side fix inside the sealed registration?** Read
   `configs/campaigns/v5_claim_25g83/registration_block5.md` sections 0.12, 6.5, 7.2 and 11 item 4, and the
   passages near lines 1100 to 1215, 2905 to 2925, 4040 to 4120 (the harvest's re-screen, "verdict sources
   that do not authenticate", `observed.reference_source`, `_claim_campaign_manifests_as_written`). State,
   with line citations, whether the registration (a) already says the harvest re-derives the reference set
   from the authenticated campaign manifests when the verdict's own source list cannot be used, so the
   present behaviour is a program defect against the text; or (b) says a window whose verdict records no
   usable sources is removed, so changing that needs a prospective cold erratum (registration section 10).
   Do not stretch the text. If it is (b), say so plainly, still build the fix, and mark it as needing the
   erratum.
3. **Fix**, in the three permitted files only. The intended behaviour: when the stored verdict names no
   usable source manifests, the harvest's re-screen takes the window's reference set from the runs root's
   campaign manifests, each authenticated by the same `campaign_provenance` functions against the campaign
   log, with the same policy check, and applies the same loss rules it applies today (run-time failures,
   harvest physics drops, strict validation, the custody triangle), then evaluates the registered screen
   with the count-adjusted clean bound. A manifest member with no bundle (the spare) is a lost reference,
   not a reason to discard every manifest. Nothing may make the screen easier to pass: a window whose
   surviving references are fewer than 2 at an endpoint, or whose statistic exceeds the bound, or whose
   manifests do not authenticate, must still be removed. The harvest record must say which source named
   the references (the existing `observed.reference_source` idea) so the path taken is disclosed. Keep the
   change as small as the defect allows; no refactor.
4. **Tests** under `tests/`: the regression (a runs root with a bundle-less spare manifest and a verdict
   with empty sources now evaluates the screen on the survivors); the negative controls (fewer than 2
   survivors at an endpoint is still `neg8.screen_failed` with `references_insufficient`; an
   unauthenticated manifest is still a failure; a window with recorded sources behaves byte-for-byte as
   before). Run the touched test modules and report the commands and their result lines.
5. **Check on real rehearsal bytes**: harvest logic on the completed `corpus18-20261009T1949Z` rehearsal
   must give the same screen result before and after your change (it has recorded sources). Say how you
   checked.

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

Sections: Root cause (with file and line citations, and the reproduction); Registration reading ((a) or
(b), with line citations); The fix (what changed, per file, and why it cannot let a physically failing
window pass); Tests (commands and result lines); Residual risk; Counts I would want (optional). Plain
findings and code facts; no prose for outside readers. No energy, power or duration values, no member
names from a claim window.
